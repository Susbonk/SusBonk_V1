use regex::Regex;
use std::collections::HashSet;
use tracing::info;
use crate::database::ChatConfig;
use crate::types::DetectionType;

pub struct LinkDetector {
    url_regex: Regex,
    shortened_domains: HashSet<String>,
    suspicious_patterns: Vec<Regex>,
}

#[derive(Debug, Clone)]
pub struct LinkDetection {
    pub detection_type: DetectionType,
    pub detected_url: String,
    pub confidence: f32,
    pub reason: String,
}

impl LinkDetector {
    pub fn new() -> Self {
        let url_regex = Regex::new(
            r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?",
        ).expect("Invalid URL regex");

        let shortened_domains = [
            "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "short.link",
            "tiny.cc", "is.gd", "buff.ly", "adf.ly", "bl.ink", "lnkd.in",
            "s.id", "cutt.ly", "rebrand.ly", "clickme.net", "v.gd"
        ].iter().map(|s| s.to_string()).collect();

        let suspicious_patterns = vec![
            Regex::new(r"(?i)(free|win|prize|money|cash|bitcoin|crypto)").unwrap(),
            Regex::new(r"(?i)(urgent|limited|act\s+now|click\s+here)").unwrap(),
            Regex::new(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}").unwrap(), // IP addresses
            Regex::new(r"(?i)\.tk$|\.ml$|\.ga$|\.cf$").unwrap(), // Suspicious TLDs
        ];

        Self {
            url_regex,
            shortened_domains,
            suspicious_patterns,
        }
    }

    pub fn detect_links(&self, text: &str, config: Option<&ChatConfig>) -> Vec<LinkDetection> {
        let mut detections = Vec::new();
        
        // Extract whitelisted domains from config
        let whitelisted_domains: Vec<String> = config
            .and_then(|c| c.allowed_link_domains.as_ref())
            .and_then(|v| v.as_array())
            .map(|arr| {
                arr.iter()
                    .filter_map(|v| v.as_str().map(|s| s.to_string()))
                    .collect()
            })
            .unwrap_or_default();

        // Extract all URLs from the message
        for url_match in self.url_regex.find_iter(text) {
            let url = url_match.as_str();
            
            // Check if domain is whitelisted
            let is_whitelisted = whitelisted_domains.iter().any(|domain| url.contains(domain));
            if is_whitelisted {
                continue; // Skip whitelisted domains
            }
            
            // Check for shortened URLs
            if let Some(detection) = self.check_shortened_url(url) {
                detections.push(detection);
                continue;
            }

            // Check for suspicious patterns in URL
            if let Some(detection) = self.check_suspicious_patterns(url) {
                detections.push(detection);
                continue;
            }

            // Check for unknown/suspicious domains
            if let Some(detection) = self.check_unknown_domain(url) {
                detections.push(detection);
            }
        }

        if !detections.is_empty() {
            info!("Detected {} suspicious links in message", detections.len());
        }

        detections
    }

    fn check_shortened_url(&self, url: &str) -> Option<LinkDetection> {
        for domain in &self.shortened_domains {
            if url.contains(domain) {
                return Some(LinkDetection {
                    detection_type: DetectionType::ShortenedUrl,
                    detected_url: url.to_string(),
                    confidence: 0.7,
                    reason: format!("Shortened URL from {}", domain),
                });
            }
        }
        None
    }

    fn check_suspicious_patterns(&self, url: &str) -> Option<LinkDetection> {
        for (i, pattern) in self.suspicious_patterns.iter().enumerate() {
            if pattern.is_match(url) {
                let reason = match i {
                    0 => "Contains money/prize keywords",
                    1 => "Contains urgency keywords",
                    2 => "Uses IP address instead of domain",
                    3 => "Uses suspicious TLD",
                    _ => "Matches suspicious pattern",
                };

                return Some(LinkDetection {
                    detection_type: DetectionType::SuspiciousLink,
                    detected_url: url.to_string(),
                    confidence: 0.8,
                    reason: reason.to_string(),
                });
            }
        }
        None
    }

    fn check_unknown_domain(&self, url: &str) -> Option<LinkDetection> {
        // Extract domain from URL
        if let Some(domain) = self.extract_domain(url) {
            // Simple heuristic: domains with unusual patterns
            if domain.len() > 30 || domain.chars().filter(|c| c.is_numeric()).count() > domain.len() / 2 {
                return Some(LinkDetection {
                    detection_type: DetectionType::UnknownDomain,
                    detected_url: url.to_string(),
                    confidence: 0.6,
                    reason: format!("Suspicious domain pattern: {}", domain),
                });
            }
        }
        None
    }

    fn extract_domain(&self, url: &str) -> Option<String> {
        if let Some(start) = url.find("://") {
            let after_protocol = &url[start + 3..];
            if let Some(end) = after_protocol.find('/') {
                Some(after_protocol[..end].to_string())
            } else if let Some(end) = after_protocol.find('?') {
                Some(after_protocol[..end].to_string())
            } else {
                Some(after_protocol.to_string())
            }
        } else {
            None
        }
    }

    #[allow(dead_code)]
    pub fn extract_all_urls(&self, text: &str) -> Vec<String> {
        self.url_regex
            .find_iter(text)
            .map(|m| m.as_str().to_string())
            .collect()
    }
}
