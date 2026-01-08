use std::sync::Arc;
use std::time::Duration;
use tracing::{info, error, warn};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
use tokio_retry::strategy::{ExponentialBackoff, jitter};
use tokio_retry::Retry;

mod models;
mod logging;

use logging::{LoggingService, opensearch::OpenSearchLogger};
use models::{LogLevel, SpamDetectionEvent, MonitoringEvent};

async fn wait_for_opensearch(logger: &OpenSearchLogger, max_attempts: u32) -> anyhow::Result<()> {
    let retry_strategy = ExponentialBackoff::from_millis(1000)
        .map(jitter)
        .take(max_attempts as usize);

    Retry::spawn(retry_strategy, || async {
        match logger.health_check().await {
            Ok(_) => {
                info!("OpenSearch connection established");
                Ok(())
            }
            Err(e) => {
                warn!("Waiting for OpenSearch to be ready: {}", e);
                Err(e)
            }
        }
    })
    .await
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize tracing
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "alertd=debug,info".into()),
        )
        .with(tracing_subscriber::fmt::layer().json())
        .init();

    info!("Starting alertd service");

    // Initialize OpenSearch logger
    let opensearch_url = std::env::var("OPENSEARCH_URL")
        .unwrap_or_else(|_| "http://localhost:9200".to_string());
    let index_prefix = std::env::var("INDEX_PREFIX")
        .unwrap_or_else(|_| "susbonk".to_string());

    let opensearch_logger = Arc::new(OpenSearchLogger::new(opensearch_url, index_prefix));
    
    // Wait for OpenSearch to be ready
    if let Err(e) = wait_for_opensearch(&opensearch_logger, 10).await {
        error!("Failed to connect to OpenSearch after retries: {}", e);
        return Err(e);
    }

    // Create index templates
    if let Err(e) = opensearch_logger.create_index_templates().await {
        error!("Failed to create index templates: {}", e);
    }

    // Initialize logging service
    let logging_service = LoggingService::new(opensearch_logger);

    info!("alertd service running. Press Ctrl+C to stop.");
    
    // Keep the service running
    tokio::signal::ctrl_c().await?;
    info!("Shutting down alertd service");

    // Graceful shutdown
    logging_service.shutdown().await;
    tokio::time::sleep(Duration::from_millis(500)).await;

    Ok(())
}
