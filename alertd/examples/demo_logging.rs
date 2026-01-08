// Example: How to use the alertd logging service
//
// Run with: cargo run --example demo_logging

use std::sync::Arc;
use alertd::logging::{LoggingService, opensearch::OpenSearchLogger};
use alertd::models::{LogLevel, SpamDetectionEvent, MonitoringEvent};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize OpenSearch logger
    let opensearch_url = "http://localhost:9200".to_string();
    let index_prefix = "demo".to_string();
    let opensearch_logger = Arc::new(OpenSearchLogger::new(opensearch_url, index_prefix));
    
    // Initialize logging service
    let logging_service = LoggingService::new(opensearch_logger);

    // Example 1: Log a general event
    logging_service.log(
        LogLevel::Info,
        "demo-service",
        "Service started successfully",
        serde_json::json!({"version": "0.1.0"})
    );

    // Example 2: Log a spam detection event
    let spam_event = SpamDetectionEvent {
        message_id: "msg_123".to_string(),
        chat_id: "chat_456".to_string(),
        user_id: "user_789".to_string(),
        content: "Buy crypto now!".to_string(),
        spam_score: 0.95,
        blocked: true,
        detection_rules: vec!["crypto_spam".to_string(), "urgency_keywords".to_string()],
    };
    logging_service.log_spam_detection(spam_event);

    // Example 3: Log a monitoring event
    let monitoring_event = MonitoringEvent {
        metric_name: "messages_processed".to_string(),
        value: 1.0,
        unit: "count".to_string(),
        tags: std::collections::HashMap::from([
            ("service".to_string(), "demo-service".to_string()),
            ("environment".to_string(), "development".to_string()),
        ]),
    };
    logging_service.log_monitoring(monitoring_event);

    println!("Demo events logged! Check OpenSearch at http://localhost:9200/demo-*/_search");

    // Give time for async logging to complete
    tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
    logging_service.shutdown().await;

    Ok(())
}
