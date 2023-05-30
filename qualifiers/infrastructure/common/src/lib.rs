pub mod models;
pub mod schema;

use diesel::PgConnection;
use diesel_migrations::MigrationHarness;

use object_store::aws::AmazonS3Builder;
use object_store::azure::MicrosoftAzureBuilder;
use object_store::gcp::GoogleCloudStorageBuilder;
use object_store::local::LocalFileSystem;
use object_store::ObjectStore;

use std::sync::Arc;

use crate::models::ScoringParameters;
use crate::models::{ChallengeId, Exploit, ExploitStatus};
use chrono::Utc;
use diesel::prelude::*;
use diesel::ExpressionMethods;

fn calculate_score(
    scoring_parameters: &ScoringParameters,
    first_solve: chrono::NaiveDateTime,
    scoring_time: chrono::NaiveDateTime,
) -> i32 {
    let elpased = scoring_time - first_solve;
    let elpased_periods: i32 = (elpased.num_seconds()
        / scoring_parameters.score_dropoff_period.num_seconds())
    .try_into()
    .unwrap_or(0);

    scoring_parameters.max_score - elpased_periods * scoring_parameters.score_dropoff
}

pub type DbError = Box<dyn std::error::Error + Send + Sync>;
pub async fn get_challenge_scores(
    conn: &mut PgConnection,
    scores_challenge_id: ChallengeId,
    scoring_parameters: &ScoringParameters,
) -> Result<models::ChallengeScores, DbError> {
    use crate::schema::exploits::dsl::*;

    let potential_solves = exploits
        .filter(
            challenge_id.eq(scores_challenge_id).and(
                status
                    .eq(ExploitStatus::RunSolved)
                    .or(pending.eq(Some(true))),
            ),
        )
        .order(submission_time.asc())
        .load::<Exploit>(conn)?;

    let (next_score, solves) = match potential_solves.first() {
        None => (scoring_parameters.max_score, vec![]),
        Some(first_submission) => {
            let solves = potential_solves
                .iter()
                .filter(|exploit| *exploit.status() == ExploitStatus::RunSolved);
            if *first_submission.status() == ExploitStatus::RunSolved {
                let now = Utc::now().naive_utc();
                let score =
                    calculate_score(scoring_parameters, *first_submission.submission_time(), now);
                let challenge_solves = solves
                    .map(|exploit| {
                        let score = calculate_score(
                            scoring_parameters,
                            *first_submission.submission_time(),
                            *exploit.submission_time(),
                        );
                        models::ChallengeSolve::new(
                            *exploit.exploit_id(),
                            *exploit.team_id(),
                            *exploit.submission_time(),
                            Some(score),
                            exploit.score_awarded().is_some(),
                        )
                    })
                    .collect();

                (score, challenge_solves)
            } else {
                let score = scoring_parameters.max_score;
                let challenge_solves = solves
                    .map(|exploit| {
                        models::ChallengeSolve::new(
                            *exploit.exploit_id(),
                            *exploit.team_id(),
                            *exploit.submission_time(),
                            None,
                            exploit.score_awarded().is_some(),
                        )
                    })
                    .collect();

                (score, challenge_solves)
            }
        }
    };

    Ok(models::ChallengeScores::new(
        scores_challenge_id,
        next_score,
        solves,
    ))
}

pub fn get_object_store_url_prefix() -> Result<String, object_store::Error> {
    let storage_type = std::env::var("EXPLOITS_STORAGE").expect("EXPLOITS_STORAGE not set");
    let exploits_path = std::env::var("EXPLOITS_PATH").expect("EXPLOITS_PATH not set");
    match storage_type.as_ref() {
        "local" => Ok(exploits_path),
        "aws" => Ok(format!("s3://{exploits_path}/")),
        "azure" => Ok(format!("az://{exploits_path}/")),
        "gcp" => Ok(format!("gs://{exploits_path}/")),
        _ => {
            log::error!(
                "ObjectStore of type {} not supported. Must be one of: local, aws, azure or gcp",
                storage_type
            );
            Err(object_store::Error::NotImplemented)
        }
    }
}

pub fn get_object_store() -> object_store::Result<Arc<dyn ObjectStore>> {
    let storage_type = std::env::var("EXPLOITS_STORAGE").expect("EXPLOITS_STORAGE not set");
    let exploits_path = std::env::var("EXPLOITS_PATH").expect("EXPLOITS_PATH not set");

    let store: Arc<dyn ObjectStore> = match storage_type.as_ref() {
        "local" => Arc::new(LocalFileSystem::new_with_prefix(exploits_path)?),
        "aws" => Arc::new(
            AmazonS3Builder::from_env()
                .with_bucket_name(exploits_path)
                .build()?,
        ),
        "azure" => Arc::new(
            MicrosoftAzureBuilder::from_env()
                .with_container_name(exploits_path)
                .build()?,
        ),
        "gcp" => Arc::new(
            GoogleCloudStorageBuilder::from_env()
                .with_bucket_name(exploits_path)
                .build()?,
        ),
        _ => {
            log::error!(
                "ObjectStore of type {} not supported. Must be one of: local, aws, azure or gcp",
                storage_type
            );
            return Err(object_store::Error::NotImplemented);
        }
    };

    Ok(store)
}

pub fn setup_database_pool(
) -> Result<diesel::r2d2::Pool<diesel::r2d2::ConnectionManager<PgConnection>>, r2d2::Error> {
    // set up database connection pool
    let conn_spec = std::env::var("DATABASE_URL").expect("DATABASE_URL");
    let manager = diesel::r2d2::ConnectionManager::<PgConnection>::new(conn_spec);
    let pool = diesel::r2d2::Pool::builder()
        .build(manager)
        .expect("Failed to create pool.");
    let mut conn = match pool.get() {
        Ok(conn) => conn,
        Err(err) => return Err(err),
    };
    run_migration(&mut conn);
    Ok(pool)
}

pub const MIGRATIONS: diesel_migrations::EmbeddedMigrations =
    diesel_migrations::embed_migrations!();
fn run_migration(conn: &mut PgConnection) {
    conn.run_pending_migrations(MIGRATIONS)
        .expect("Failed to run migrations. Please investigate and try again.");
}

#[cfg(test)]
mod tests {

    // TODO (P2): tests?
}
