use std::env;
use std::net::SocketAddr;
use std::str::FromStr;
use std::time::Duration;

/// Get environment variable as string with a default value
pub fn env_string(name: &str, default: &str) -> String {
    env::var(name).unwrap_or_else(|_| default.to_string())
}

/// Get optional environment variable as string (None if not set)
pub fn env_opt_string(name: &str) -> Option<String> {
    env::var(name).ok().filter(|v| !v.is_empty())
}

/// Parse environment variable using FromStr trait with a default value
pub fn env_parse<T>(name: &str, default: T) -> T
where
    T: FromStr + std::fmt::Display,
{
    env::var(name)
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or_else(|| {
            tracing::debug!(
                "Environment variable {} not set or invalid, using default: {}",
                name,
                default
            );
            default
        })
}

/// Get environment variable as boolean with a default value
pub fn env_bool(name: &str, default: bool) -> bool {
    env::var(name)
        .ok()
        .map(|v| matches!(v.as_str(), "1" | "true" | "yes" | "on"))
        .unwrap_or(default)
}

/// Get environment variable as duration in seconds with a default value
pub fn env_duration_secs(name: &str, default_secs: u64) -> Duration {
    let secs = env_parse(name, default_secs);
    Duration::from_secs(secs)
}

/// Get environment variable as SocketAddr with a default value
pub fn env_socketaddr(name: &str, default: &str) -> SocketAddr {
    env::var(name)
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or_else(|| {
            let addr = default.parse().expect("Invalid default socket address");
            tracing::debug!(
                "Environment variable {} not set, using default: {}",
                name,
                default
            );
            addr
        })
}
