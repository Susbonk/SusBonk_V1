pub mod opensearch;

use std::sync::Arc;
use tokio::sync::mpsc;
use tracing::error;
use uuid::Uuid;
use chrono::Utc;
use crate::models::{LogEvent, LogLevel, SpamDetectionEvent, MonitoringEvent};
use opensearch::OpenSearchLogger;

pub struct LoggingService {
    sender: mpsc::UnboundedSender<LogMessage>,
    shutdown_tx: tokio::sync::watch::Sender<bool>,
}

#[derive(Debug)]
enum LogMessage {
    Event(LogEvent),
    SpamDetection(SpamDetectionEvent),
    Monitoring(MonitoringEvent),
}

impl LoggingService {
    pub fn new(opensearch_logger: Arc<OpenSearchLogger>) -> Self {
        let (sender, mut receiver) = mpsc::unbounded_channel::<LogMessage>();
        let (shutdown_tx, mut shutdown_rx) = tokio::sync::watch::channel(false);
        
        tokio::spawn(async move {
            loop {
                tokio::select! {
                    Some(message) = receiver.recv() => {
                        match message {
                            LogMessage::Event(event) => {
                                if let Err(e) = opensearch_logger.log_event(&event).await {
                                    error!("Failed to log event: {}", e);
                                }
                            }
                            LogMessage::SpamDetection(event) => {
                                if let Err(e) = opensearch_logger.log_spam_detection(&event).await {
                                    error!("Failed to log spam detection: {}", e);
                                }
                            }
                            LogMessage::Monitoring(event) => {
                                if let Err(e) = opensearch_logger.log_monitoring(&event).await {
                                    error!("Failed to log monitoring event: {}", e);
                                }
                            }
                        }
                    }
                    _ = shutdown_rx.changed() => {
                        if *shutdown_rx.borrow() {
                            break;
                        }
                    }
                }
            }
        });

        Self { sender, shutdown_tx }
    }

    pub fn log(&self, level: LogLevel, service: &str, message: &str, metadata: serde_json::Value) {
        let event = LogEvent {
            id: Uuid::new_v4(),
            timestamp: Utc::now(),
            level,
            service: service.to_string(),
            message: message.to_string(),
            metadata,
        };

        if let Err(e) = self.sender.send(LogMessage::Event(event)) {
            error!("Failed to send log event: {}", e);
        }
    }

    pub fn log_spam_detection(&self, event: SpamDetectionEvent) {
        if let Err(e) = self.sender.send(LogMessage::SpamDetection(event)) {
            error!("Failed to send spam detection event: {}", e);
        }
    }

    pub fn log_monitoring(&self, event: MonitoringEvent) {
        if let Err(e) = self.sender.send(LogMessage::Monitoring(event)) {
            error!("Failed to send monitoring event: {}", e);
        }
    }

    pub async fn shutdown(&self) {
        let _ = self.shutdown_tx.send(true);
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
    }
}
