use crate::types::SpamEvent;
use redis::{Client, aio::Connection, RedisResult};
use serde_json;
use tracing::{info, error};

pub struct RedisStreamsClient {
    client: Client,
}

impl RedisStreamsClient {
    pub fn new(redis_url: &str) -> RedisResult<Self> {
        let client = Client::open(redis_url)?;
        Ok(Self { client })
    }

    pub async fn get_connection(&self) -> RedisResult<Connection> {
        self.client.get_async_connection().await
    }

    pub async fn log_spam_event(&self, event: &SpamEvent) -> RedisResult<()> {
        let mut conn = self.get_connection().await?;
        
        let event_json = serde_json::to_string(event)
            .map_err(|e| redis::RedisError::from((redis::ErrorKind::TypeError, "JSON serialization failed", e.to_string())))?;
        
        let stream_key = format!("spam_events:{}", event.chat_id);
        
        let _: String = redis::cmd("XADD")
            .arg(&stream_key)
            .arg("*")
            .arg("event")
            .arg(&event_json)
            .query_async(&mut conn)
            .await?;
        
        info!("Logged spam event to Redis stream: {}", stream_key);
        Ok(())
    }

    pub async fn create_consumer_group(&self, stream_key: &str, group_name: &str) -> RedisResult<()> {
        let mut conn = self.get_connection().await?;
        
        let result: RedisResult<String> = redis::cmd("XGROUP")
            .arg("CREATE")
            .arg(stream_key)
            .arg(group_name)
            .arg("0")
            .arg("MKSTREAM")
            .query_async(&mut conn)
            .await;
        
        match result {
            Ok(_) => {
                info!("Created consumer group {} for stream {}", group_name, stream_key);
                Ok(())
            }
            Err(e) => {
                // Group might already exist, which is fine
                if e.to_string().contains("BUSYGROUP") {
                    info!("Consumer group {} already exists for stream {}", group_name, stream_key);
                    Ok(())
                } else {
                    error!("Failed to create consumer group: {}", e);
                    Err(e)
                }
            }
        }
    }
}
