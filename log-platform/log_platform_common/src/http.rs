use reqwest::Client;
use std::time::Duration;

pub fn create_client() -> Client {
    Client::builder()
        .timeout(Duration::from_secs(30))
        .build()
        .unwrap_or_else(|_| Client::new())
}
