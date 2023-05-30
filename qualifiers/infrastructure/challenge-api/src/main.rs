use chrono::Duration;
use std::sync::Arc;

use actix_multipart_extract::Multipart;
use actix_web::{get, middleware, post, web, App, HttpResponse, HttpServer};
use backon::ConstantBuilder;
use backon::Retryable;
use celery::prelude::*;
use celery::Celery;
use diesel::prelude::*;
use diesel::r2d2::{self, ConnectionManager};
use exploit_builder::build_exploit;
use google_cloud_default::WithAuthExt;
use google_cloud_storage::client::{Client, ClientConfig};
use google_cloud_storage::sign::SignedURLOptions;
use hmac::{Hmac, Mac};
use object_store::ObjectStore;
use sha2::Sha256;
use uuid::Uuid;

mod actions;
mod error;
mod models;

use error::ApiError;

#[derive(Clone)]
struct AppState {
    celery: Arc<celery::Celery>,
    hmac_key: Hmac<Sha256>,
    admin_key: String,
    auth_server_url: String,
    auth_server_key: String,
    object_store: Arc<dyn ObjectStore>,
    exploit_rate_limit: Duration,
    max_exploit_size: usize,
    scoring_parameters: common::models::ScoringParameters,
}

type DbPool = r2d2::Pool<ConnectionManager<PgConnection>>;

#[get("/challenges")]
async fn get_challenges(pool: web::Data<DbPool>) -> Result<HttpResponse, ApiError> {
    let challenges = web::block(move || {
        let mut conn = pool.get()?;
        actions::get_released_challenges(&mut conn)
    })
    .await??;

    Ok(HttpResponse::Ok().json(challenges))
}

#[get("/challenges/{challenge_id}")]
async fn get_challenge(
    db_pool: web::Data<DbPool>,
    challenge_id: web::Path<common::models::ChallengeId>,
) -> Result<HttpResponse, ApiError> {
    let challenge_id = challenge_id.into_inner();

    let mut conn = db_pool.get()?;
    let challenge =
        web::block(move || actions::get_released_challenge(&mut conn, challenge_id)).await??;

    Ok(HttpResponse::Ok().json(challenge))
}

#[get("/challenges/{challenge_id}/download")]
async fn download_challenge(
    db_pool: web::Data<DbPool>,
    gcp_client: web::Data<google_cloud_storage::client::Client>,
    challenge_id: web::Path<common::models::ChallengeId>,
) -> Result<HttpResponse, ApiError> {
    let mut conn1 = db_pool.get()?;
    let challenge =
        web::block(move || actions::get_released_challenge(&mut conn1, *challenge_id)).await??;

    let url_for_download = gcp_client
        .signed_url(
            "livectf-challenges",
            &format!("{}.tgz", challenge.challenge_name()),
            None,
            None,
            SignedURLOptions::default(),
        )
        .await?;

    Ok(HttpResponse::Found()
        .insert_header(("Location", url_for_download))
        .finish())
}

#[get("/challenges/{challenge_id}/scores")]
async fn challenge_scores(
    db_pool: web::Data<DbPool>,
    challenge_id: web::Path<common::models::ChallengeId>,
    app_state: web::Data<AppState>,
) -> Result<HttpResponse, ApiError> {
    let app_state = app_state.into_inner();
    let mut conn = db_pool.get()?;
    let challenge_id = challenge_id.into_inner();
    let challenge_scores =
        common::get_challenge_scores(&mut conn, challenge_id, &app_state.scoring_parameters)
            .await?;

    Ok(HttpResponse::Ok().json(challenge_scores))
}

#[post("/challenges/{challenge_id}")]
async fn submit_exploit(
    db_pool: web::Data<DbPool>,
    redis: web::Data<redis::Client>,
    challenge_id: web::Path<common::models::ChallengeId>,
    app_state: web::Data<AppState>,
    team_token: web::Header<models::AuthenticationTokenHeader>,
    exploit_form: Multipart<models::NewExploit>,
) -> Result<HttpResponse, ApiError> {
    let challenge_id = challenge_id.into_inner();
    let team_token = team_token.into_inner();
    let app_state = app_state.into_inner();

    let mut conn1 = db_pool.get()?;
    let challenge =
        web::block(move || actions::get_released_challenge(&mut conn1, challenge_id)).await??;

    let team_info = team_token
        .validate(
            &redis,
            &app_state.auth_server_url,
            &app_state.auth_server_key,
            Some(challenge.challenge_short_name()),
        )
        .await?;

    let overwrite = exploit_form.overwrite.unwrap_or(false);

    let valid_exploit_file = match actions::validate_submission_file(
        &exploit_form.exploit,
        app_state.max_exploit_size,
    ) {
        Ok(file) => file,
        Err(_) => {
            return Err(ApiError::ExploitFile {
                max_file_size: app_state.max_exploit_size,
            });
        }
    };

    let mut conn2 = db_pool.get()?;
    // TODO (P2): Create some more elegant guard thing which releases rate limit unless disarmed before going out of scope
    if !actions::check_rate_limit(&redis, *team_info.team_id(), app_state.exploit_rate_limit)
        .await?
    {
        return Err(ApiError::RateLimit {
            limit: app_state.exploit_rate_limit.num_seconds(),
        });
    };

    let exploit_file_uuid =
        match actions::save_exploit_file(valid_exploit_file, &app_state.object_store).await {
            Err(err) => {
                actions::revert_rate_limit(
                    &redis,
                    *team_info.team_id(),
                    app_state.exploit_rate_limit,
                )
                .await?;
                return Err(err.into());
            }
            Ok(exploit_file_uuid) => exploit_file_uuid,
        };

    let team_info2 = team_info.clone();
    let exploit = match web::block(move || {
        actions::create_exploit_submission(
            &mut conn2,
            &challenge,
            &team_info2,
            exploit_file_uuid,
            overwrite,
        )
    })
    .await?
    .map_err(|error| match error {
        actions::CreateExploitError::DbError(error) => ApiError::Database {
            error: error.to_string(),
        },
        actions::CreateExploitError::ExploitAlreadyQueued {
            team_id,
            challenge_id,
        } => ApiError::ExploitAlreadyQueued {
            team_id,
            challenge_id,
        },
    }) {
        Err(err) => {
            actions::revert_rate_limit(&redis, *team_info.team_id(), app_state.exploit_rate_limit)
                .await?;
            return Err(err);
        }
        Ok(exploit) => exploit,
    };

    if let Err(err) = app_state
        .celery
        .send_task(build_exploit::new(*exploit.exploit_id()))
        .await
    {
        actions::revert_rate_limit(&redis, *team_info.team_id(), app_state.exploit_rate_limit)
            .await?;
        return Err(err.into());
    };

    Ok(HttpResponse::Ok().json(exploit))
}

#[get("/exploits/{exploit_id}")]
async fn get_exploit(
    pool: web::Data<DbPool>,
    redis: web::Data<redis::Client>,
    exploit_id: web::Path<Uuid>,
    app_state: web::Data<AppState>,
    team_token: web::Header<models::AuthenticationTokenHeader>,
) -> Result<HttpResponse, ApiError> {
    let exploit_id = exploit_id.into_inner();
    let team_token = team_token.into_inner();
    let app_state = app_state.into_inner();
    let team_info = team_token
        .validate(
            &redis,
            &app_state.auth_server_url,
            &app_state.auth_server_key,
            None,
        )
        .await?;

    let exploit = web::block(move || {
        let mut conn = pool.get()?;
        actions::get_exploit(&mut conn, exploit_id)
    })
    .await??;

    match exploit {
        Some(exploit) if *exploit.team_id() == *team_info.team_id() => {
            Ok(HttpResponse::Ok().json(exploit))
        }
        Some(exploit) => Err(ApiError::ExploitForbidden {
            team_id: *team_info.team_id(),
            exploit_id: *exploit.exploit_id(),
        }),
        None => Err(ApiError::ExploitNotFound { exploit_id }),
    }
}

#[get("/exploits")]
async fn get_exploits(
    pool: web::Data<DbPool>,
    admin_token: web::Header<models::AdminTokenHeader>,
    app_state: web::Data<AppState>,
) -> Result<HttpResponse, ApiError> {
    let admin_token = admin_token.into_inner();
    admin_token.validate(&app_state.admin_key)?;

    let exploits = web::block(move || {
        let mut conn = pool.get()?;
        actions::admin_get_exploits(&mut conn)
    })
    .await??;

    Ok(HttpResponse::Ok().json(exploits))
}

#[get("/exploits/{exploit_id}/rerun")]
async fn rerun_exploit(
    pool: web::Data<DbPool>,
    admin_token: web::Header<models::AdminTokenHeader>,
    exploit_id: web::Path<Uuid>,
    app_state: web::Data<AppState>,
) -> Result<HttpResponse, ApiError> {
    let exploit_id = exploit_id.into_inner();
    let admin_token = admin_token.into_inner();
    admin_token.validate(&app_state.admin_key)?;

    let exploit = web::block(move || {
        let mut conn = pool.get()?;
        actions::get_exploit(&mut conn, exploit_id)
    })
    .await??;

    match exploit {
        Some(exploit) => {
            app_state
                .celery
                .send_task(build_exploit::new(*exploit.exploit_id()))
                .await?;

            Ok(HttpResponse::Ok().json(exploit))
        },
        None => Err(ApiError::ExploitNotFound { exploit_id }),
    }
}


async fn connect_celery() -> Result<Arc<Celery>, CeleryError> {
    celery::app!(
        broker = AMQPBroker { std::env::var("AMQP_ADDR").expect("AMQP_ADDR not set") },
        tasks = [exploit_builder::build_exploit],
        task_routes = [ "build_exploit" => "build" ],
    )
    .await
}

async fn configure_celery_api() -> Result<Arc<Celery>, CeleryError> {
    let backon_settings = ConstantBuilder::default()
        .with_delay(std::time::Duration::from_secs(5))
        .with_max_times(12);
    connect_celery
        .retry(&backon_settings)
        .notify(|err: &CeleryError, dur: std::time::Duration| {
            log::info!(
                "Retrying connection to Celery in {:?}, error {:?}",
                dur,
                err
            );
        })
        .await
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv::dotenv().ok();
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));

    let common = configure_celery_api()
        .await
        .map_err(|err| std::io::Error::new(std::io::ErrorKind::ConnectionRefused, err))?;

    let db_pool = common::setup_database_pool()
        .map_err(|err| std::io::Error::new(std::io::ErrorKind::ConnectionRefused, err))?;

    let redis_client =
        redis::Client::open(std::env::var("REDIS_HOST").expect("REDIS_HOST not set"))
            .map_err(|err| std::io::Error::new(std::io::ErrorKind::ConnectionRefused, err))?;

    let host = std::env::var("API_HOST").unwrap_or_else(|_| "127.0.0.1".to_string());
    let port = std::env::var("API_PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse()
        .expect("API_PORT not set to an integer");

    log::info!("starting HTTP server at http://{}:{}", host, port);

    let object_store = common::get_object_store()?;

    let gcp_config = ClientConfig::default().with_auth().await.unwrap();
    let gcp_client = Client::new(gcp_config);
    let gcp_client = web::Data::new(gcp_client);

    // score = 50 - 1pt/6min => [10, 50]
    let scoring_parameters = common::models::ScoringParameters::quals2023();

    let db_pool_data = web::Data::new(db_pool);
    let redis_client_data = web::Data::new(redis_client);
    let app_state_data = web::Data::new(AppState {
        celery: common.clone(),
        hmac_key: Hmac::new_from_slice(std::env::var("HMAC_KEY").expect("HMAC_KEY").as_bytes())
            .expect("Failed to initialize HMAC from HMAC_KEY"),
        admin_key: std::env::var("ADMIN_KEY").expect("ADMIN_KEY"),
        auth_server_url: std::env::var("AUTH_URL").expect("AUTH_URL"),
        auth_server_key: std::env::var("AUTH_KEY").expect("AUTH_KEY"),
        object_store: object_store.clone(),
        exploit_rate_limit: Duration::seconds(60),
        max_exploit_size: 50_000_000, // 50mb,
        scoring_parameters,
    });

    // Start HTTP server
    HttpServer::new(move || {
        App::new()
            .app_data(db_pool_data.clone())
            .app_data(redis_client_data.clone())
            .app_data(gcp_client.clone())
            .app_data(app_state_data.clone())
            .wrap(middleware::Logger::default())
            .service(get_challenges)
            .service(get_challenge)
            .service(download_challenge)
            .service(challenge_scores)
            .service(get_exploits)
            .service(get_exploit)
            .service(rerun_exploit)
            .service(submit_exploit)
    })
    .bind((host, port))?
    .run()
    .await
}

#[cfg(test)]
mod tests {
    // TODO (P2): Tests?
}
