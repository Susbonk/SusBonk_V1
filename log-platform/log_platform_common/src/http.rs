use reqwest::Client;
use std::time::Duration;

/// Create a shared HTTP client with common configuration
pub fn client(timeout: Duration) -> Client {
    Client::builder()
        .timeout(timeout)
        .user_agent("log-platform-client/1.0")
        .build()
        .expect("Failed to build HTTP client")
}
