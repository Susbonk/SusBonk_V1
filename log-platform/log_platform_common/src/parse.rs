use serde_json::Value;

/// Parse email list from string - supports both CSV format and JSON array
pub fn parse_email_list(raw: &str) -> Vec<String> {
    let s = raw.trim();
    if s.is_empty() {
        return vec![];
    }

    // JSON array support
    if s.starts_with('[') {
        if let Ok(v) = serde_json::from_str::<Value>(s) {
            if let Some(arr) = v.as_array() {
                let out: Vec<String> = arr
                    .iter()
                    .filter_map(|x| x.as_str())
                    .map(|x| x.trim())
                    .filter(|x| !x.is_empty())
                    .map(|x| x.to_string())
                    .collect();
                if !out.is_empty() {
                    return out;
                }
            }
        }
        // fallthrough to CSV parsing
    }

    // Split ONLY by comma/semicolon to allow: "Ivan <a@b.com>"
    s.split(|c: char| c == ',' || c == ';')
        .map(|x| x.trim())
        .filter(|x| !x.is_empty())
        .map(|x| x.to_string())
        .collect()
}

pub fn bytes_to_gb(b: f64) -> f64 {
    b / (1024.0_f64.powi(3))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_email_list_csv() {
        assert_eq!(
            parse_email_list("a@b.com,c@d.com"),
            vec!["a@b.com", "c@d.com"]
        );
    }

    #[test]
    fn test_parse_email_list_json() {
        assert_eq!(
            parse_email_list(r#"["a@b.com", "c@d.com"]"#),
            vec!["a@b.com", "c@d.com"]
        );
    }

    #[test]
    fn test_bytes_to_gb() {
        assert_eq!(bytes_to_gb(1024.0_f64.powi(3)), 1.0);
    }
}
