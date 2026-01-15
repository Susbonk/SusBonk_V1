use axum::{
    extract::State,
    http::StatusCode,
    response::IntoResponse,
    routing::post,
    Json, Router,
};
use reqwest::Client;
use serde_json::json;
use std::sync::Arc;
use tracing::{info, error};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

use ingestd::{IngestPayload, IngestResponse, LogEvent};

struct AppState {
    client: Client,
    opensearch_url: String,
}

async fn ingest_handler(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<IngestPayload>,
) -> Result<Json<IngestResponse>, StatusCode> {
    let events = payload.into_vec();
    let count = events.len();

    if let Err(e) = bulk_index(&state, events).await {
        error!("Failed to bulk index: {}", e);
        return Err(StatusCode::INTERNAL_SERVER_ERROR);
    }

    Ok(Json(IngestResponse { indexed: count }))
}

async fn bulk_index(state: &AppState, events: Vec<LogEvent>) -> anyhow::Result<()> {
    let mut bulk_body = String::new();
    
    for event in events {
        let timestamp = event.timestamp.unwrap_or_else(chrono::Utc::now);
        let service_name = event.service
            .as_ref()
            .and_then(|s| Some(s.name.as_str()))
            .unwrap_or("unknown");
        let index = format!("logs-{}-{}", service_name, timestamp.format("%Y.%m.%d"));
        
        let action = json!({
            "index": {
                "_index": index
            }
        });
        
        bulk_body.push_str(&serde_json::to_string(&action)?);
        bulk_body.push('\n');
        bulk_body.push_str(&serde_json::to_string(&event)?);
        bulk_body.push('\n');
    }

    let url = format!("{}/_bulk", state.opensearch_url);
    let response = state.client
        .post(&url)
        .header("Content-Type", "application/x-ndjson")
        .body(bulk_body)
        .send()
        .await?;

    if !response.status().is_success() {
        error!("Bulk index failed: {}", response.status());
        return Err(anyhow::anyhow!("Bulk index failed"));
    }

    Ok(())
}

async fn health_handler() -> impl IntoResponse {
    Json(json!({"status": "ok"}))
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

    let opensearch_url = std::env::var("OS_URL")
        .unwrap_or_else(|_| "http://localhost:9200".to_string());
    let port = std::env::var("PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse::<u16>()?;

    let state = Arc::new(AppState {
        client: Client::new(),
        opensearch_url,
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
