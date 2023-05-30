use actix_multipart_extract::{File, MultipartForm};
use actix_web::error::ParseError;
use actix_web::http::header::{
    Header, HeaderName, HeaderValue, InvalidHeaderValue, TryIntoHeaderValue,
};
use actix_web::HttpMessage;
use redis::AsyncCommands;
use serde::Deserialize;

use common::models::TeamId;
use common::models::TeamToken;

#[derive(Deserialize, MultipartForm, Debug)]
pub struct NewExploit {
    #[multipart(max_size = 10MB)]
    pub exploit: File,
    pub overwrite: Option<bool>,
}

#[derive(Deserialize)]
#[serde(untagged)]
pub enum NautilusAuthResponse {
    Error {
        error: String,
    },
    Info {
        challenge: NautilusChallengeInfo,
        score: Option<u64>,
        slug: String,
        success: bool,
        team: NautilusTeamInfo,
    },
}

#[derive(Deserialize)]
pub struct NautilusChallengeInfo {
    name: String,
    shortname: String,
}

#[derive(Deserialize)]
pub struct NautilusTeamInfo {
    display_name: String,
    id: i32,
    name: String,
    name_punycode: String,
}

pub enum AuthenticationError {
    InvalidToken { token: String },
    IncorrectChallenge { token: String },
    Redis(redis::RedisError),
    Reqwest(reqwest::Error),
}
impl From<redis::RedisError> for AuthenticationError {
    fn from(error: redis::RedisError) -> Self {
        Self::Redis(error)
    }
}
impl From<reqwest::Error> for AuthenticationError {
    fn from(error: reqwest::Error) -> Self {
        Self::Reqwest(error)
    }
}

pub struct AuthenticationTokenHeader(String);
pub struct AdminTokenHeader(String);

impl AuthenticationTokenHeader {
    pub async fn validate(
        self,
        redis_client: &redis::Client,
        auth_server_url: &str,
        auth_server_key: &str,
        challenge_shortname: Option<&String>,
    ) -> Result<common::models::TeamInfo, AuthenticationError> {
        let mut redis_con = redis_client.get_tokio_connection().await?;
        let redis_key_team = format!("team:{}", self.0);
        let redis_key_challenge = format!("challenge:{}", self.0);
        if let (Ok(token_team_id), Ok(token_challenge_shortname)) = (
            redis_con.get(&redis_key_team).await,
            redis_con.get(&redis_key_challenge).await,
        ) {
            if let Some(challenge_shortname) = challenge_shortname {
                if *challenge_shortname != token_challenge_shortname {
                    return Err(AuthenticationError::IncorrectChallenge { token: self.0 });
                }
            }
            return Ok(common::models::TeamInfo::new(
                TeamToken(self.0),
                TeamId(token_team_id),
                token_challenge_shortname,
            ));
        }

        let http_client = reqwest::Client::new();
        let auth_response = http_client
            .get(format!("{auth_server_url}/livectf/ticket"))
            .query(&[("auth", auth_server_key), ("ticket", &self.0)])
            .send()
            .await?
            .json::<NautilusAuthResponse>()
            .await?;

        match auth_response {
            NautilusAuthResponse::Error { .. } => {
                Err(AuthenticationError::InvalidToken { token: self.0 })
            }
            NautilusAuthResponse::Info {
                challenge,
                score: _,
                slug: _,
                success: _,
                team,
            } => {
                let team_id = team.id;
                redis_con.set(&redis_key_team, team_id).await?;
                redis_con.expire(&redis_key_team, 15 * 60).await?;
                redis_con
                    .set(&redis_key_challenge, challenge.shortname.clone())
                    .await?;
                redis_con.expire(&redis_key_challenge, 15 * 60).await?;

                if let Some(challenge_shortname) = challenge_shortname {
                    if *challenge_shortname != challenge.shortname {
                        return Err(AuthenticationError::IncorrectChallenge { token: self.0 });
                    }
                }

                Ok(common::models::TeamInfo::new(
                    TeamToken(self.0),
                    TeamId(team_id),
                    challenge.shortname,
                ))
            }
        }
    }
}

impl AdminTokenHeader {
    pub fn validate(self, admin_key: &str) -> Result<(), AuthenticationError> {
        if self.0 == *admin_key {
            Ok(())
        } else {
            Err(AuthenticationError::InvalidToken { token: self.0 })
        }
    }
}

impl Header for AdminTokenHeader {
    fn name() -> HeaderName {
        HeaderName::from_static("x-livectf-admin")
    }
    fn parse<M>(msg: &M) -> Result<Self, ParseError>
    where
        M: HttpMessage,
    {
        Ok(Self(
            msg.headers()
                .get(Self::name())
                .ok_or(ParseError::Header)?
                .to_str()
                .map_err(|_| ParseError::Header)?
                .to_string(),
        ))
    }
}

impl Header for AuthenticationTokenHeader {
    fn name() -> HeaderName {
        HeaderName::from_static("x-livectf-token")
    }
    fn parse<M>(msg: &M) -> Result<Self, ParseError>
    where
        M: HttpMessage,
    {
        Ok(Self(
            msg.headers()
                .get(Self::name())
                .ok_or(ParseError::Header)?
                .to_str()
                .map_err(|_| ParseError::Header)?
                .to_string(),
        ))
    }
}

impl TryIntoHeaderValue for AuthenticationTokenHeader {
    type Error = InvalidHeaderValue;

    fn try_into_value(self) -> Result<HeaderValue, Self::Error> {
        HeaderValue::from_str(&self.0)
    }
}

impl TryIntoHeaderValue for AdminTokenHeader {
    type Error = InvalidHeaderValue;

    fn try_into_value(self) -> Result<HeaderValue, Self::Error> {
        HeaderValue::from_str(&self.0)
    }
}
