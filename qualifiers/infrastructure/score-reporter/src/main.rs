use common::models::ScoringParameters;
use diesel::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::error::Error;
use uuid::Uuid;

#[derive(Serialize)]
struct NautilusScoreRequest<'a> {
    auth: &'a String,
    ticket: &'a common::models::TeamToken,
    score: i32,
    shortname: &'a String,
}

impl<'a> NautilusScoreRequest<'a> {
    pub fn new(
        auth: &'a String,
        ticket: &'a common::models::TeamToken,
        score: i32,
        shortname: &'a String,
    ) -> Self {
        Self {
            auth,
            ticket,
            score,
            shortname,
        }
    }
}

#[derive(Deserialize)]
#[serde(untagged)]
enum NautilusScoreResponse {
    Error {
        error: String,
    },
    Score {
        success: bool,
        score: i32,
        solution_id: i32,
        challenge: NautilusChallengeInfo,
    },
}

#[derive(Deserialize)]
struct NautilusChallengeInfo {
    name: String,
    shortname: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    dotenv::dotenv().ok();
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));

    let auth_server_key = std::env::var("AUTH_KEY").expect("AUTH_KEY");
    let auth_server_url = std::env::var("AUTH_URL").expect("AUTH_URL");

    log::debug!("Setting up database pool");
    let db_pool = common::setup_database_pool()
        .map_err(|err| std::io::Error::new(std::io::ErrorKind::ConnectionRefused, err))?;

    let scoring_parameters = ScoringParameters::quals2023();

    log::debug!("Getting database connection");
    let mut conn = db_pool.get()?;

    log::debug!("Getting challenges");
    let all_challenges = {
        use common::schema::challenges::dsl::*;
        challenges.load::<common::models::Challenge>(&mut conn)?
    };

    for challenge in all_challenges.iter() {
        log::debug!("Processing challenge {}", challenge.challenge_id());
        // TODO (P2): have a flag for the challenge whether it scores or not
        let is_test_challenge =
            *challenge.challenge_id() == common::models::ChallengeId::from_i32(7);

        let is_special_challenge1 =
            *challenge.challenge_id() == common::models::ChallengeId::from_i32(4);

        let mut scoring_teams = HashSet::new();

        let challenge_scores =
            common::get_challenge_scores(&mut conn, *challenge.challenge_id(), &scoring_parameters)
                .await
                .expect("Failed to get challenge scores");

        log::debug!("Got {} solves for challenge {}", challenge_scores.solves.len(), challenge.challenge_id());
        for solve in challenge_scores.solves.iter() {
            let solve_score = match solve.score_awarded {
                Some(score) => score,
                None => {
                    log::debug!("No points awarded for solve {} for team {} on challenge {}", solve.team_id, solve.team_id, challenge.challenge_id());
                    continue;
                }
            };

            if scoring_teams.contains(&solve.team_id) {
                log::debug!("Already processed team {} for challenge {}", solve.team_id, challenge.challenge_id());
                continue;
            }
            scoring_teams.insert(&solve.team_id);

            let solve_exploit_id = solve.exploit_id;
            let exploit_res = {
                use common::schema::exploits::dsl::*;
                match exploits
                    .filter(exploit_id.eq(solve_exploit_id))
                    .first::<common::models::Exploit>(&mut conn)
                    .optional()
                {
                    Ok(exploit_res) => exploit_res,
                    Err(_) => {
                        log::warn!("Failed to fetch exploit {solve_exploit_id} from the database");
                        continue;
                    }
                }
            };

            let exploit = match exploit_res {
                Some(exploit) => exploit,
                None => {
                    log::warn!("No exploit with ID {solve_exploit_id} found in the database");
                    continue;
                }
            };

            if exploit.score_awarded().is_some() {
                continue;
            }

            let score = if is_test_challenge { 1 } else if is_special_challenge1 { 50 } else { solve_score };

            log::info!("Going to submit {score} points to team {} for explioit {solve_exploit_id}", solve.team_id);

            let http_client = reqwest::Client::new();
            let report_response = http_client
                .patch(format!("{auth_server_url}/livectf/ticket/score"))
                .json(&NautilusScoreRequest::new(
                    &auth_server_key,
                    exploit.team_token(),
                    score,
                    &challenge.challenge_short_name().to_string(),
                ))
                .send()
                .await?
                .json::<NautilusScoreResponse>()
                .await?;

            match report_response {
                NautilusScoreResponse::Error { error } => {
                    log::warn!(
                        "Failed to submit score for exploit {solve_exploit_id}, error: {error}"
                    );
                    continue;
                }
                NautilusScoreResponse::Score {
                    success,
                    score,
                    solution_id,
                    challenge,
                } => {
                    if !success {
                        log::warn!("Score submission rejected for exploit {solve_exploit_id}");
                        continue;
                    }

                    {
                        use common::schema::exploits::dsl::*;
                        if let Err(err) = diesel::update(&exploit)
                            .set(score_awarded.eq(score))
                            .execute(&mut conn)
                        {
                            log::warn!(
                                "Failed to store score in database for exploit {solve_exploit_id}"
                            );
                            continue;
                        }
                    }

                    log::info!(
                        "Successfully submitted {score} points to team {} for explioit {solve_exploit_id}", solve.team_id
                    );
                }
            }
        }
    }

    Ok(())
}
