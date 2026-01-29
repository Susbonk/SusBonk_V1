use redis::{aio::MultiplexedConnection, AsyncCommands, RedisError, RedisResult};
use std::time::Duration;
use tokio::time::sleep;
use tracing::{debug, warn};

/// Maximum number of retry attempts for transient Redis failures
const MAX_RETRIES: u32 = 3;

/// Base delay for exponential backoff (milliseconds)
const BASE_DELAY_MS: u64 = 100;

/// Ensure a consumer group exists for a stream
/// Creates the stream if it doesn't exist (MKSTREAM)
/// Handles BUSYGROUP error gracefully (group already exists)
pub async fn ensure_consumer_group(
    conn: &mut MultiplexedConnection,
    stream: &str,
    group: &str,
) -> RedisResult<()> {
    let result: RedisResult<String> = redis::cmd("XGROUP")
        .arg("CREATE")
        .arg(stream)
        .arg(group)
        .arg("0")
        .arg("MKSTREAM")
        .query_async(conn)
        .await;

    match result {
        Ok(_) => {
            debug!("Created consumer group '{}' for stream '{}'", group, stream);
            Ok(())
        }
        Err(e) => {
            let err_msg = e.to_string();
            if err_msg.contains("BUSYGROUP") {
                debug!("Consumer group '{}' already exists for stream '{}'", group, stream);
                Ok(())
            } else {
                warn!("Failed to create consumer group: {}", err_msg);
                Err(e)
            }
        }
    }
}

/// Acknowledge and delete a message from a stream
/// This prevents message leaks and keeps streams clean
pub async fn ack_and_delete(
    conn: &mut MultiplexedConnection,
    stream: &str,
    group: &str,
    message_id: &str,
) -> RedisResult<()> {
    // Acknowledge the message
    let _: i64 = conn.xack(stream, group, &[message_id]).await?;
    
    // Delete the message from the stream
    let _: i64 = conn.xdel(stream, &[message_id]).await?;
    
    debug!("Acked and deleted message {} from stream {}", message_id, stream);
    Ok(())
}

/// Execute a Redis operation with exponential backoff retry
/// Retries on transient failures (connection errors, timeouts)
pub async fn with_retry<F, Fut, T>(mut operation: F) -> RedisResult<T>
where
    F: FnMut() -> Fut,
    Fut: std::future::Future<Output = RedisResult<T>>,
{
    let mut attempts = 0;
    
    loop {
        match operation().await {
            Ok(result) => return Ok(result),
            Err(e) => {
                attempts += 1;
                
                if attempts >= MAX_RETRIES {
                    warn!("Redis operation failed after {} attempts: {}", MAX_RETRIES, e);
                    return Err(e);
                }
                
                if is_transient_error(&e) {
                    let delay = BASE_DELAY_MS * 2_u64.pow(attempts - 1);
                    debug!("Transient Redis error, retrying in {}ms (attempt {}/{})", 
                           delay, attempts, MAX_RETRIES);
                    sleep(Duration::from_millis(delay)).await;
                } else {
                    // Non-transient error, fail immediately
                    return Err(e);
                }
            }
        }
    }
}

/// Check if a Redis error is transient and worth retrying
fn is_transient_error(error: &RedisError) -> bool {
    let err_msg = error.to_string().to_lowercase();
    
    // Connection errors
    if err_msg.contains("connection") 
        || err_msg.contains("timeout")
        || err_msg.contains("broken pipe")
        || err_msg.contains("connection reset")
        || err_msg.contains("io error") {
        return true;
    }
    
    // Cluster errors
    if err_msg.contains("moved") 
        || err_msg.contains("ask")
        || err_msg.contains("clusterdown") {
        return true;
    }
    
    false
}

/// Read messages from a stream using consumer group
/// Returns (message_id, fields) tuples
pub async fn read_group(
    conn: &mut MultiplexedConnection,
    stream: &str,
    group: &str,
    consumer: &str,
    count: usize,
    block_ms: usize,
) -> RedisResult<Vec<(String, Vec<(String, String)>)>> {
    let result: redis::streams::StreamReadReply = conn
        .xread_options(
            &[stream],
            &[">"],
            &redis::streams::StreamReadOptions::default()
                .group(group, consumer)
                .count(count)
                .block(block_ms),
        )
        .await?;

    let mut messages = Vec::new();
    
    for stream_key in result.keys {
        for stream_id in stream_key.ids {
            let id = stream_id.id;
            let fields: Vec<(String, String)> = stream_id
                .map
                .into_iter()
                .map(|(k, v)| {
                    let value = match v {
                        redis::Value::BulkString(bytes) => String::from_utf8_lossy(&bytes).to_string(),
                        redis::Value::SimpleString(s) => s,
                        redis::Value::Int(i) => i.to_string(),
                        _ => String::new(),
                    };
                    (k, value)
                })
                .collect();
            
            messages.push((id, fields));
        }
    }
    
    Ok(messages)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_is_transient_error() {
        // Connection errors should be transient
        let err = RedisError::from((redis::ErrorKind::IoError, "connection refused"));
        assert!(is_transient_error(&err));
        
        // Timeout errors should be transient
        let err = RedisError::from((redis::ErrorKind::IoError, "timeout"));
        assert!(is_transient_error(&err));
        
        // Type errors should not be transient
        let err = RedisError::from((redis::ErrorKind::TypeError, "wrong type"));
        assert!(!is_transient_error(&err));
    }

    #[test]
    fn test_retry_constants() {
        assert_eq!(MAX_RETRIES, 3);
        assert_eq!(BASE_DELAY_MS, 100);
        
        // Verify exponential backoff delays
        assert_eq!(BASE_DELAY_MS * 2_u64.pow(0), 100); // First retry: 100ms
        assert_eq!(BASE_DELAY_MS * 2_u64.pow(1), 200); // Second retry: 200ms
        assert_eq!(BASE_DELAY_MS * 2_u64.pow(2), 400); // Third retry: 400ms
    }
}
