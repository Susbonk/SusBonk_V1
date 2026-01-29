use anyhow::{Context, Result};

/// Parse email recipients from environment variable
/// Supports both CSV ("a@x.com,b@y.com") and JSON array (["a@x.com","b@y.com"])
pub fn parse_email_recipients(input: &str) -> Result<Vec<String>> {
    let trimmed = input.trim();
    
    if trimmed.starts_with('[') {
        serde_json::from_str(trimmed).context("Failed to parse JSON array")
    } else {
        Ok(trimmed.split(',').map(|s| s.trim().to_string()).collect())
    }
}

/// Convert bytes to gigabytes
pub fn bytes_to_gb(bytes: u64) -> f64 {
    bytes as f64 / 1_073_741_824.0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_csv_recipients() {
        let result = parse_email_recipients("admin@example.com,ops@example.com").unwrap();
        assert_eq!(result, vec!["admin@example.com", "ops@example.com"]);
    }

    #[test]
    fn test_parse_json_recipients() {
        let result = parse_email_recipients(r#"["admin@example.com","ops@example.com"]"#).unwrap();
        assert_eq!(result, vec!["admin@example.com", "ops@example.com"]);
    }

    #[test]
    fn test_parse_single_recipient() {
        let result = parse_email_recipients("admin@example.com").unwrap();
        assert_eq!(result, vec!["admin@example.com"]);
    }

    #[test]
    fn test_bytes_to_gb() {
        assert_eq!(bytes_to_gb(1_073_741_824), 1.0);
        assert_eq!(bytes_to_gb(2_147_483_648), 2.0);
        assert!((bytes_to_gb(536_870_912) - 0.5).abs() < 0.001);
    }
}
