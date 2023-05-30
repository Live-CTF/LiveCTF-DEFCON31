use actix_web::http::header::ContentType;
use actix_web::http::StatusCode;
use actix_web::HttpResponse;
use common::models::{ChallengeId, TeamId};
use derive_more::{Display, Error};
use serde::Serialize;
use uuid::Uuid;

use crate::actions::DbError;
use crate::actions::GetChallengeError;
use crate::models::AuthenticationError;

#[derive(Serialize)]
struct ApiErrorMessage {
    error: String,
}
impl ApiErrorMessage {
    fn new(error: String) -> Self {
        Self { error }
    }
}

#[derive(Debug, Display, Error)]
pub enum ApiError {
    Database {
        error: String,
    },

    #[display(fmt = "ChallengeNotFound: challenge: {challenge_id}")]
    ChallengeNotFound {
        challenge_id: ChallengeId,
    },
    #[display(fmt = "ChallengeClosed: challenge: {challenge_id}")]
    ChallengeClosed {
        challenge_id: ChallengeId,
    },
    #[display(fmt = "ChallengeNotReleased: challenge: {challenge_id}")]
    ChallengeNotReleased {
        challenge_id: ChallengeId,
    },
    #[display(fmt = "ExploitNotFound: exploit: {exploit_id}")]
    ExploitNotFound {
        exploit_id: Uuid,
    },
    #[display(fmt = "ExploitForbidden: team: {team_id}, exploit: {exploit_id}")]
    ExploitForbidden {
        team_id: TeamId,
        exploit_id: Uuid,
    },

    Unauthenticated,
    InvalidAuthenticationToken {
        token: String,
    },
    IncorrectChallengeToken {
        token: String,
    },

    ExploitFile {
        max_file_size: usize,
    },

    #[display(fmt = "ExploitAlreadyQueued: team: {team_id}, challenge: {challenge_id}")]
    ExploitAlreadyQueued {
        team_id: TeamId,
        challenge_id: ChallengeId,
    },

    RateLimit {
        limit: i64,
    },

    Internal {
        error: String,
    },
}

impl From<actix_web::error::BlockingError> for ApiError {
    fn from(error: actix_web::error::BlockingError) -> Self {
        Self::Internal {
            error: format!("Block error: {error}"),
        }
    }
}

impl From<DbError> for ApiError {
    fn from(error: DbError) -> Self {
        Self::Database {
            error: format!("Postgres error: {error}"),
        }
    }
}

impl From<redis::RedisError> for ApiError {
    fn from(error: redis::RedisError) -> Self {
        Self::Database {
            error: format!("Redis error: {error}"),
        }
    }
}

impl From<celery::error::CeleryError> for ApiError {
    fn from(error: celery::error::CeleryError) -> Self {
        Self::Internal {
            error: format!("Celery error: {error}"),
        }
    }
}

impl From<std::io::Error> for ApiError {
    fn from(error: std::io::Error) -> Self {
        Self::Internal {
            error: format!("IO error: {error}"),
        }
    }
}

impl From<reqwest::Error> for ApiError {
    fn from(error: reqwest::Error) -> Self {
        Self::Internal {
            error: format!("Reqwuest error: {error}"),
        }
    }
}

impl From<r2d2::Error> for ApiError {
    fn from(error: r2d2::Error) -> Self {
        Self::Internal {
            error: format!("R2D2 error: {error}"),
        }
    }
}

impl From<google_cloud_storage::sign::SignedURLError> for ApiError {
    fn from(error: google_cloud_storage::sign::SignedURLError) -> Self {
        Self::Internal {
            error: format!("GCS error: {error}"),
        }
    }
}

impl From<AuthenticationError> for ApiError {
    fn from(error: AuthenticationError) -> Self {
        match error {
            AuthenticationError::InvalidToken { token } => {
                Self::InvalidAuthenticationToken { token }
            }
            AuthenticationError::IncorrectChallenge { token } => {
                Self::IncorrectChallengeToken { token }
            }
            AuthenticationError::Redis(error) => error.into(),
            AuthenticationError::Reqwest(error) => error.into(),
        }
    }
}

impl From<GetChallengeError> for ApiError {
    fn from(error: GetChallengeError) -> Self {
        match error {
            GetChallengeError::NotFound { challenge_id } => {
                Self::ChallengeNotFound { challenge_id }
            }
            GetChallengeError::NotReleased { challenge_id } => {
                Self::ChallengeNotReleased { challenge_id }
            }
            GetChallengeError::Closed { challenge_id } => Self::ChallengeClosed { challenge_id },
            GetChallengeError::Database(error) => error.into(),
        }
    }
}

impl actix_web::error::ResponseError for ApiError {
    fn error_response(&self) -> HttpResponse {
        let error_body = match self {
            Self::ChallengeNotFound { challenge_id } => {
                ApiErrorMessage::new(format!("Challenge with id {challenge_id} not found"))
            }
            Self::ChallengeClosed { challenge_id } => ApiErrorMessage::new(format!(
                "Challenge with id {challenge_id} is no longer open for submissions"
            )),
            Self::ChallengeNotReleased { challenge_id } => ApiErrorMessage::new(format!(
                "Challenge with id {challenge_id} is not yet released"
            )),
            Self::ExploitNotFound { exploit_id } => {
                ApiErrorMessage::new(format!("Exploit with id {exploit_id} not found"))
            }
            Self::ExploitForbidden {
                team_id,
                exploit_id,
            } => ApiErrorMessage::new(format!(
                "Team with id {team_id} is not allowed to view exploit with id {exploit_id}"
            )),
            Self::Database { .. } => ApiErrorMessage::new("Internal server error".to_string()),

            Self::RateLimit { limit } => ApiErrorMessage::new(format!(
                "Rate limit exceeded: can only submit once every {limit} seconds"
            )),

            // TODO (P2): map to specific errors
            Self::ExploitFile { max_file_size } => ApiErrorMessage::new(format!("Exploit archive invalid, did not contain a Dockerfile or decompressed size exceeded max limit of {max_file_size} bytes")),

            Self::ExploitAlreadyQueued { team_id, challenge_id } => ApiErrorMessage::new(format!("A pending exploit for team id {team_id} and challenge id {challenge_id} is already in the queue. Retry with \"overwrite=true\" if you want to cancel the currently pending exploit. Warning: this can not be undone.")),

            Self::Unauthenticated => ApiErrorMessage::new("You are not authenticated".to_string()),
            Self::InvalidAuthenticationToken { token } => ApiErrorMessage::new(format!("The token {token} is not a valid authentication token")),
            Self::IncorrectChallengeToken { token } => ApiErrorMessage::new(format!("The token {token} is valid for a different challenge")),

            Self::Internal { .. } => ApiErrorMessage::new("Internal server error".to_string()),
        };

        HttpResponse::build(self.status_code())
            .insert_header(ContentType::json())
            .json(error_body)
    }
    fn status_code(&self) -> StatusCode {
        match self {
            Self::Database { .. } => StatusCode::INTERNAL_SERVER_ERROR,
            Self::ChallengeNotFound { .. } => StatusCode::NOT_FOUND,
            Self::ChallengeClosed { .. } => StatusCode::FORBIDDEN,
            Self::ChallengeNotReleased { .. } => StatusCode::FORBIDDEN,
            Self::ExploitNotFound { .. } => StatusCode::NOT_FOUND,
            Self::ExploitForbidden { .. } => StatusCode::FORBIDDEN,
            Self::RateLimit { .. } => StatusCode::TOO_MANY_REQUESTS,
            Self::Internal { .. } => StatusCode::INTERNAL_SERVER_ERROR,
            Self::ExploitFile { .. } => StatusCode::UNPROCESSABLE_ENTITY,
            Self::Unauthenticated => StatusCode::FORBIDDEN,
            Self::ExploitAlreadyQueued { .. } => StatusCode::FORBIDDEN,
            Self::InvalidAuthenticationToken { .. } => StatusCode::FORBIDDEN,
            Self::IncorrectChallengeToken { .. } => StatusCode::FORBIDDEN,
        }
    }
}
