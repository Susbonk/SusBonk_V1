use axum::{
    extract::State,
    http::StatusCode,
    response::IntoResponse,
    routing::post,
    Json, Router,
};
use std::sync::Arc;
use tracing::{info, error};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

use log_platform_common::{IngestPayload, IngestResponse, opensearch::OpenSearchClient, env};

struct AppState {
    opensearch: OpenSearchClient,
}

async fn ingest_handler(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<IngestPayload>,
) -> Result<Json<IngestResponse>, StatusCode> {
    let events = payload.into_vec();

    match state.opensearch.bulk_index(events).await {
        Ok(indexed) => Ok(Json(IngestResponse { indexed })),
        Err(e) => {
            error!("Failed to bulk index: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

async fn health_handler() -> impl IntoResponse {
    Json(serde_json::json!({"status": "ok"}))
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "ingestd=debug,info".into()),
        )
        .with(tracing_subscriber::fmt::layer().json())
        .init();

    info!("Starting ingestd service");

    let opensearch_url = env::get_opensearch_url();
    let port = env::get_port();

    let state = Arc::new(AppState {
        opensearch: OpenSearchClient::new(opensearch_url),
    });

    let app = Router::new()
        .route("/ingest", post(ingest_handler))
        .route("/health", axum::routing::get(health_handler))
        .with_state(state);

    let addr = format!("0.0.0.0:{}", port);
    info!("ingestd listening on {}", addr);

    let listener = tokio::net::TcpListener::bind(&addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}
