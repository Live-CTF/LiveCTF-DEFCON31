use std::io::Read;
use std::io::{Error, ErrorKind};
use std::sync::Arc;

use actix_multipart_extract::File;
use bytes::Bytes;
use chrono::Utc;
use diesel::prelude::*;
use flate2::read::GzDecoder;
use log::info;
use object_store::ObjectStore;
use redis::AsyncCommands;
use tar::Archive;
use uuid::Uuid;

use common::models::ExploitStatus;
use common::models::{ChallengeId, TeamId};

pub type DbError = Box<dyn std::error::Error + Send + Sync>;

pub enum CreateExploitError {
    DbError(DbError),
    ExploitAlreadyQueued {
        team_id: TeamId,
        challenge_id: ChallengeId,
    },
}
impl From<DbError> for CreateExploitError {
    fn from(error: DbError) -> Self {
        Self::DbError(error)
    }
}

pub enum GetChallengeError {
    NotFound { challenge_id: ChallengeId },
    NotReleased { challenge_id: ChallengeId },
    Closed { challenge_id: ChallengeId },
    Database(DbError),
}

pub fn get_open_challenges(
    conn: &mut PgConnection,
) -> Result<Vec<common::models::Challenge>, DbError> {
    use common::schema::challenges::dsl::*;

    use diesel::dsl::now;
    let released_challenges = challenges
        .filter(now.gt(releases_at).and(now.lt(closes_at)))
        .load::<common::models::Challenge>(conn)?;

    Ok(released_challenges)
}

pub fn get_released_challenges(
    conn: &mut PgConnection,
) -> Result<Vec<common::models::Challenge>, DbError> {
    use common::schema::challenges::dsl::*;

    use diesel::dsl::now;
    let released_challenges = challenges
        .filter(now.gt(releases_at))
        .load::<common::models::Challenge>(conn)?;

    Ok(released_challenges)
}

pub fn admin_get_exploits(conn: &mut PgConnection) -> Result<Vec<common::models::Exploit>, DbError> {
    use common::schema::exploits::dsl::*;

    let all_exploits = exploits.load::<common::models::Exploit>(conn)?;

    Ok(all_exploits)
}

pub fn get_released_challenge(
    conn: &mut PgConnection,
    id: common::models::ChallengeId,
) -> Result<common::models::Challenge, GetChallengeError> {
    use common::schema::challenges::dsl::*;

    let challenge = challenges
        .filter(challenge_id.eq(id))
        .first::<common::models::Challenge>(conn)
        .optional()
        .map_err(|db_err| GetChallengeError::Database(Box::new(db_err)))?;

    let now = Utc::now().naive_utc();
    match challenge {
        None => Err(GetChallengeError::NotFound { challenge_id: id }),
        Some(challenge) => match challenge {
            _ if now < *challenge.releases_at() => Err(GetChallengeError::NotReleased {
                challenge_id: *challenge.challenge_id(),
            }),
            _ if now > *challenge.closes_at() => Err(GetChallengeError::Closed {
                challenge_id: *challenge.challenge_id(),
            }),
            _ => Ok(challenge),
        },
    }
}

pub fn create_exploit_submission(
    conn: &mut PgConnection,
    exploit_challenge: &common::models::Challenge,
    exploit_team_info: &common::models::TeamInfo,
    exploit_file_uuid: Uuid,
    overwrite: bool,
) -> Result<common::models::Exploit, CreateExploitError> {
    use common::schema::exploits::dsl::*;

    let new_exploit = common::models::Exploit::new(
        *exploit_team_info.team_id(),
        exploit_team_info.team_token().clone(),
        *exploit_challenge.challenge_id(),
        exploit_file_uuid,
    );

    if overwrite {
        info!(
            "Cancelling pending exploit for team {}",
            *exploit_team_info.team_id()
        );

        diesel::update(exploits)
            .filter(
                team_id
                    .eq(*exploit_team_info.team_id())
                    .and(pending.eq(Some(true))),
            )
            .set((
                status.eq(ExploitStatus::Cancelled),
                pending.eq(None::<bool>),
            ))
            .execute(conn)
            .map_err(|err| CreateExploitError::DbError(Box::new(err)))?;
    }

    let rows_inserted = diesel::insert_into(exploits)
        .values(&new_exploit)
        .on_conflict((team_id, challenge_id, pending))
        .do_nothing()
        .execute(conn)
        .map_err(|err| CreateExploitError::DbError(Box::new(err)))?;
    info!("Inserted {} rows", rows_inserted);
    if rows_inserted == 1 {
        Ok(new_exploit)
    } else {
        Err(CreateExploitError::ExploitAlreadyQueued {
            team_id: *exploit_team_info.team_id(),
            challenge_id: *exploit_challenge.challenge_id(),
        })
    }
}

fn get_rate_limit_bucket(team_id: common::models::TeamId, rate_limit: chrono::Duration) -> String {
    let bucket_ts = chrono::Utc::now().timestamp() / rate_limit.num_seconds();
    let bucket = format!("rate-limit:{team_id}:{bucket_ts}");

    bucket
}

fn expire_bucket<'a, T: redis::FromRedisValue>(
    redis_con: &'a mut redis::aio::Connection,
    bucket: &'a str,
    rate_limit: chrono::Duration,
) -> redis::RedisFuture<'a, T> {
    redis_con.expire(
        bucket,
        (2 * rate_limit.num_seconds())
            .try_into()
            .expect("Failed to convert rate limit timeout to usize"),
    )
}

pub async fn revert_rate_limit(
    redis_client: &redis::Client,
    team_id: common::models::TeamId,
    rate_limit: chrono::Duration,
) -> Result<bool, redis::RedisError> {
    let mut redis_con = redis_client.get_tokio_connection().await?;
    let bucket = get_rate_limit_bucket(team_id, rate_limit);

    // TODO (P2): Could this leave a key without an expiry?
    let num_submissions_bucket: i64 = redis_con.decr(&bucket, 1).await?;
    expire_bucket(&mut redis_con, &bucket, rate_limit).await?;

    Ok(num_submissions_bucket == 0)
}

pub async fn check_rate_limit(
    redis_client: &redis::Client,
    team_id: common::models::TeamId,
    rate_limit: chrono::Duration,
) -> Result<bool, redis::RedisError> {
    let mut redis_con = redis_client.get_tokio_connection().await?;
    let bucket = get_rate_limit_bucket(team_id, rate_limit);

    // TODO (P2): Could this leave a key without an expiry?
    let num_submissions_bucket: i64 = redis_con.incr(&bucket, 1).await?;
    expire_bucket(&mut redis_con, &bucket, rate_limit).await?;

    Ok(num_submissions_bucket == 1)
}

pub fn validate_submission_file(exploit_archive: &File, max_size: usize) -> Result<&[u8], Error> {
    let gzip_stream = GzDecoder::new(&exploit_archive.bytes[..]);
    let capped_stream = gzip_stream.take(max_size.try_into().map_err(|_| {
        Error::new(
            ErrorKind::InvalidInput,
            "Could not convert max_size into an u64",
        )
    })?);
    let mut archive = Archive::new(capped_stream);

    for entry in archive.entries()? {
        let entry = entry?;
        let entry_path = entry.path()?;

        let prefix = std::path::PathBuf::from("./");
        if entry_path.strip_prefix(prefix).unwrap_or(&entry_path)
            == std::path::Path::new("Dockerfile")
        {
            return Ok(&exploit_archive.bytes[..]);
        }
    }

    Err(Error::new(
        ErrorKind::InvalidInput,
        "No Dockerfile found in tar-gz archive.",
    ))
}

pub async fn save_exploit_file(
    exploit_archive: &[u8],
    object_store: &Arc<dyn ObjectStore>,
) -> Result<Uuid, Error> {
    let archive_uuid = Uuid::new_v4();
    let archive_path = object_store::path::Path::from(format!("{archive_uuid}.tar.gz"));

    object_store
        .put(&archive_path, Bytes::copy_from_slice(exploit_archive))
        .await
        .map_err(|err| {
            Error::new(
                ErrorKind::InvalidInput,
                format!("Unable to create exploit archive object: {err}"),
            )
        })?;

    Ok(archive_uuid)
}

pub fn get_exploit(
    conn: &mut PgConnection,
    id: Uuid,
) -> Result<Option<common::models::Exploit>, DbError> {
    use common::schema::exploits::dsl::*;

    let exploit = exploits
        .filter(exploit_id.eq(id))
        .first::<common::models::Exploit>(conn)
        .optional()?;

    Ok(exploit)
}
