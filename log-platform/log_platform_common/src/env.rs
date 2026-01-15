use std::env;
use std::str::FromStr;

pub fn get_env(key: &str, default: &str) -> String {
    env::var(key).unwrap_or_else(|_| default.to_string())
}

pub fn env_parse<T: FromStr>(key: &str, default: T) -> T {
    env::var(key)
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(default)
}

pub fn env_bool(key: &str, default: bool) -> bool {
    env::var(key)
        .map(|v| matches!(v.to_lowercase().as_str(), "true" | "1" | "yes"))
        .unwrap_or(default)
}

pub fn get_opensearch_url() -> String {
    get_env("OPENSEARCH_URL", "http://localhost:9200")
}

pub fn get_ingest_url() -> String {
    get_env("INGEST_URL", "http://localhost:8080")
}

pub fn get_port() -> u16 {
    env_parse("PORT", 8080)
}

pub fn get_smtp_host() -> String {
    get_env("SMTP_SERVER", "localhost")
}

pub fn get_smtp_port() -> u16 {
    env_parse("SMTP_PORT", 587)
}

pub fn get_smtp_user() -> Option<String> {
    env::var("SMTP_USER").ok().filter(|s| !s.is_empty())
}

pub fn get_smtp_password() -> Option<String> {
    env::var("SMTP_PASSWORD").ok().filter(|s| !s.is_empty())
}

pub fn get_alert_email_from() -> String {
    get_env("ALERT_EMAIL_FROM", "alerts@localhost")
}

pub fn get_alert_email_to() -> String {
    get_env("ALERT_EMAIL_TO", "admin@example.com")
}

#[derive(Debug, Clone)]
pub struct Cfg {
    pub opensearch_url: String,
    pub ingest_url: String,
    pub smtp_host: String,
    pub smtp_port: u16,
    pub smtp_user: Option<String>,
    pub smtp_password: Option<String>,
    pub alert_email_from: String,
    pub alert_email_to: String,
    pub disk_threshold_gb: f64,
    pub warn_threshold: usize,
    pub error_threshold: usize,
    pub check_interval_secs: u64,
}

impl Default for Cfg {
    fn default() -> Self {
        Self::from_env()
    }
}

impl Cfg {
    pub fn from_env() -> Self {
        Self {
            opensearch_url: get_opensearch_url(),
            ingest_url: get_ingest_url(),
            smtp_host: get_smtp_host(),
            smtp_port: get_smtp_port(),
            smtp_user: get_smtp_user(),
            smtp_password: get_smtp_password(),
            alert_email_from: get_alert_email_from(),
            alert_email_to: get_alert_email_to(),
            disk_threshold_gb: env_parse("DISK_THRESHOLD_GB", 50.0),
            warn_threshold: env_parse("WARNING_THRESHOLD", 100),
            error_threshold: env_parse("ERROR_THRESHOLD", 50),
            check_interval_secs: env_parse("CHECK_INTERVAL_SECS", 60),
        }
    }
}
