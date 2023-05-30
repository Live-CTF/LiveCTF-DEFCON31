use std::fmt;

use chrono::Utc;
use diesel::prelude::*;
use diesel_derive_newtype::DieselNewType;
use serde::{Deserialize, Serialize};
use std::hash::Hash;
use uuid::Uuid;

use crate::schema::{challenges, exploit_outputs, exploits};

#[derive(Serialize)]
pub struct ChallengeSolve {
    #[serde(skip_serializing)]
    pub exploit_id: Uuid,
    pub team_id: TeamId,
    pub submission_time: chrono::NaiveDateTime,
    pub score_awarded: Option<i32>,
    #[serde(skip_serializing)]
    pub is_reported: bool,
}

impl ChallengeSolve {
    pub fn new(
        exploit_id: Uuid,
        team_id: TeamId,
        submission_time: chrono::NaiveDateTime,
        score_awarded: Option<i32>,
        is_reported: bool,
    ) -> Self {
        Self {
            exploit_id,
            team_id,
            submission_time,
            score_awarded,
            is_reported,
        }
    }
}

#[derive(Serialize)]
pub struct ChallengeScores {
    pub challenge_id: ChallengeId,
    pub current_score: i32,
    pub solves: Vec<ChallengeSolve>,
}

impl ChallengeScores {
    pub fn new(challenge_id: ChallengeId, current_score: i32, solves: Vec<ChallengeSolve>) -> Self {
        Self {
            challenge_id,
            current_score,
            solves,
        }
    }
}

#[derive(Clone)]
pub struct ScoringParameters {
    pub max_score: i32,
    pub score_dropoff: i32,
    pub score_dropoff_period: chrono::Duration,
}

impl ScoringParameters {
    pub fn quals2023() -> Self {
        Self {
            max_score: 50,
            score_dropoff: 1,
            score_dropoff_period: chrono::Duration::seconds(6 * 60), // 6min
        }
    }
}

#[derive(diesel_derive_enum::DbEnum)]
#[ExistingTypePath = "crate::schema::sql_types::ExploitStatus"]
#[derive(Debug, Clone, Copy, Serialize, PartialEq, Eq)]
pub enum ExploitStatus {
    Submitted,
    Building,
    BuildOk,
    BuildFailed,
    Cancelled,
    Running,
    RunSolved,
    RunFailed,
}

#[derive(Hash, Debug, PartialEq, Eq, Copy, Clone, Serialize, Deserialize, DieselNewType)]
pub struct TeamId(pub i32);

#[derive(Hash, Debug, PartialEq, Eq, Clone, Serialize, Deserialize, DieselNewType)]
pub struct TeamToken(pub String);

#[derive(Hash, Debug, PartialEq, Eq, Clone)]
pub struct TeamInfo {
    team_token: TeamToken,
    team_id: TeamId,
    challenge_shortname: String,
}

impl TeamInfo {
    pub fn new(team_token: TeamToken, team_id: TeamId, challenge_shortname: String) -> Self {
        Self {
            team_token,
            team_id,
            challenge_shortname,
        }
    }

    pub fn team_token(&self) -> &TeamToken {
        &self.team_token
    }

    pub fn team_id(&self) -> &TeamId {
        &self.team_id
    }

    pub fn challenge_shortname(&self) -> &str {
        &self.challenge_shortname
    }
}

impl fmt::Display for TeamId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.0.fmt(f)
    }
}

#[derive(Hash, Debug, PartialEq, Eq, Copy, Clone, Serialize, Deserialize, DieselNewType)]
pub struct ChallengeId(i32);

impl ChallengeId {
    pub fn from_i32(id: i32) -> Self {
        Self(id)
    }
}

impl fmt::Display for ChallengeId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.0.fmt(f)
    }
}

#[derive(Debug, Clone, Serialize, Queryable, Insertable, AsChangeset, Identifiable)]
#[diesel(table_name = exploits)]
#[diesel(primary_key(exploit_id))]
pub struct Exploit {
    exploit_id: Uuid,
    team_id: TeamId,
    team_token: TeamToken,
    challenge_id: ChallengeId,
    archive_id: Uuid,
    #[serde(skip_serializing)]
    pending: Option<bool>,
    status: ExploitStatus,
    score_awarded: Option<i32>,
    submission_time: chrono::NaiveDateTime,
    run_duration: Option<i32>, // TODO (P2): use duration
}

#[derive(Debug, Clone, Serialize, Queryable, Insertable, AsChangeset, Identifiable)]
#[diesel(table_name = exploit_outputs)]
#[diesel(primary_key(output_id))]
pub struct ExploitOutput {
    output_id: Uuid,
    exploit_id: Uuid,
    stdout: String,
    stderr: String,
    created_at: chrono::NaiveDateTime,
}

impl ExploitOutput {
    pub fn new(exploit_id: Uuid, stdout: String, stderr: String) -> Self {
        Self {
            output_id: Uuid::new_v4(),
            exploit_id,
            stdout,
            stderr,
            created_at: Utc::now().naive_utc(),
        }
    }
}

impl Exploit {
    pub fn team_id(&self) -> &TeamId {
        &self.team_id
    }

    pub fn exploit_id(&self) -> &Uuid {
        &self.exploit_id
    }

    pub fn team_token(&self) -> &TeamToken {
        &self.team_token
    }

    pub fn archive_id(&self) -> &Uuid {
        &self.archive_id
    }

    pub fn challenge_id(&self) -> &ChallengeId {
        &self.challenge_id
    }

    pub fn status(&self) -> &ExploitStatus {
        &self.status
    }

    pub fn score_awarded(&self) -> &Option<i32> {
        &self.score_awarded
    }

    pub fn submission_time(&self) -> &chrono::NaiveDateTime {
        &self.submission_time
    }

    pub fn set_status(&mut self, status: ExploitStatus) -> &Self {
        self.status = status;
        self
    }

    pub fn new(
        exploit_team_id: TeamId,
        exploit_team_token: TeamToken,
        exploit_challenge_id: ChallengeId,
        exploit_file_uuid: Uuid,
    ) -> Self {
        Self {
            exploit_id: Uuid::new_v4(),
            team_id: exploit_team_id,
            team_token: exploit_team_token,
            challenge_id: exploit_challenge_id,
            archive_id: exploit_file_uuid,
            pending: Some(true),
            status: ExploitStatus::Submitted,
            score_awarded: None,
            submission_time: Utc::now().naive_utc(),
            run_duration: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Queryable, Insertable, AsChangeset, Identifiable)]
#[diesel(table_name = challenges)]
#[diesel(primary_key(challenge_id))]
pub struct Challenge {
    challenge_id: ChallengeId,
    challenge_short_name: String,
    challenge_name: String,
    #[serde(skip_serializing)]
    uses_nsjail: bool,
    releases_at: chrono::NaiveDateTime,
    closes_at: chrono::NaiveDateTime,
}

impl Challenge {
    pub fn challenge_name(&self) -> &String {
        &self.challenge_name
    }

    pub fn challenge_short_name(&self) -> &String {
        &self.challenge_short_name
    }

    pub fn challenge_id(&self) -> &ChallengeId {
        &self.challenge_id
    }

    pub fn uses_nsjail(&self) -> &bool {
        &self.uses_nsjail
    }

    pub fn releases_at(&self) -> &chrono::NaiveDateTime {
        &self.releases_at
    }

    pub fn closes_at(&self) -> &chrono::NaiveDateTime {
        &self.closes_at
    }
}
