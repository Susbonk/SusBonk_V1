use axum::{Json, Router, extract::State, http::StatusCode, routing::post};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::time::Duration;

use log_platform_domain::LogEvent;
use tracing::{error, info, warn};

use log_platform_common::env;
use log_platform_common::opensearch;

#[derive(Clone)]
struct Cfg {
    os_url: String,
    bind_addr: std::net::SocketAddr,
}

impl Cfg {
    fn from_env() -> Self {
        Self {
            os_url: env::env_string("OPENSEARCH_URL", "http://localhost:9200"),
            bind_addr: env::env_socketaddr("INGEST_BIND", "0.0.0.0:8080"),
        }
    }
}

#[derive(Clone)]
struct AppState {
    os_url: String,
    http: Client,
}

#[derive(Debug, Deserialize)]
#[serde(untagged)]
enum IngestPayload {
    One(LogEvent),
    Many(Vec<LogEvent>),
}

#[derive(Debug, Serialize)]
struct IngestResponse {
    indexed: usize,
}

async fn ingest(
    State(st): State<AppState>,
    Json(payload): Json<IngestPayload>,
) -> Result<Json<IngestResponse>, (StatusCode, String)> {
    let events: Vec<LogEvent> = match payload {
        IngestPayload::One(e) => vec![e],
        IngestPayload::Many(v) => v,
    };

    if events.is_empty() {
        warn!("received empty payload");
        return Err((StatusCode::BAD_REQUEST, "empty payload".into()));
    }

    info!("received {} log events for ingest", events.len());

    let (body, count) = opensearch::to_bulk_ndjson(&events).map_err(|e: anyhow::Error| {
        error!("failed to convert events to bulk format: {}", e);
        (StatusCode::BAD_REQUEST, e.to_string())
    })?;

    let url = format!("{}/_bulk", st.os_url.trim_end_matches('/'));

    info!("sending bulk request to opensearch: {} events", count);

    let resp = st
        .http
        .post(&url)
        .header("Content-Type", "application/x-ndjson")
        .body(body)
        .send()
        .await
        .map_err(|e| {
            error!("failed to send request to opensearch: {}", e);
            (StatusCode::BAD_GATEWAY, e.to_string())
        })?;

    let status = resp.status();
    let text = resp.text().await.unwrap_or_default();

    if !status.is_success() {
        error!("opensearch bulk request failed: {} - {}", status, text);
        return Err((
            StatusCode::BAD_GATEWAY,
            format!("opensearch bulk error: {} {}", status, text),
        ));
    }

    let v: serde_json::Value = serde_json::from_str(&text).unwrap_or_else(|_| json!({"raw": text}));
    if v.get("errors").and_then(|x| x.as_bool()) == Some(true) {
        error!("opensearch bulk response contains errors: {}", v);
        return Err((
            StatusCode::BAD_GATEWAY,
            format!("bulk returned errors: {}", v),
        ));
    }

    info!("successfully indexed {} events", count);

    Ok(Json(IngestResponse { indexed: count }))
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO) // Use INFO as default, but can be overridden by RUST_LOG
        .with_target(false)
        .init();

    let cfg = Cfg::from_env();
    let http = log_platform_common::http::client(Duration::from_secs(10));

    let st = AppState {
        os_url: cfg.os_url.clone(),
        http,
    };

    let addr = cfg.bind_addr;

    let app = Router::new().route("/ingest", post(ingest)).with_state(st);

    info!("ingest service starting on http://{}", addr);
    info!("opensearch url: {}", cfg.os_url);

    axum::serve(tokio::net::TcpListener::bind(addr).await?, app).await?;
    Ok(())
}
