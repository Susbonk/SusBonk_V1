use once_cell::sync::Lazy;
use regex::Regex;
use url::Url;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Trigger {
    MentionEntity,
    MentionRegex,
    LinkEntityUrl,
    LinkEntityTextLink,
    LinkRegex,
    EmailRegex,
    EmojiOverflow,
}

pub fn count_emojis(text: &str) -> usize {
    text.chars()
        .filter(|c| {
            let code = *c as u32;
            matches!(code,
                0x1F600..=0x1F64F | // Emoticons
                0x1F300..=0x1F5FF | // Misc Symbols and Pictographs
                0x1F680..=0x1F6FF | // Transport and Map
                0x1F1E6..=0x1F1FF | // Regional indicators (flags)
                0x2600..=0x26FF |   // Misc symbols
                0x2700..=0x27BF |   // Dingbats
                0x1F900..=0x1F9FF | // Supplemental Symbols and Pictographs
                0x1F018..=0x1F270 | // Various symbols
                0x203C | 0x2049 | 0x2122 | 0x2139 | // Exclamation, TM, info
                0x2194..=0x2199 | // Arrows
                0x21A9..=0x21AA | // Arrows
                0x231A..=0x231B | // Watch, hourglass
                0x2328 | 0x23CF | // Keyboard, eject
                0x23E9..=0x23F3 | // Media controls
                0x25AA..=0x25AB | // Squares
                0x25B6 | 0x25C0 | // Triangles
                0x25FB..=0x25FE | // Squares
                0x2B05..=0x2B07 | // Arrows
                0x2B1B..=0x2B1C | // Squares
                0x2B50 | 0x2B55   // Star, circle
            )
        })
        .count()
}

pub fn extract_mention_from_entity(
    text: &str,
    entity: &teloxide::types::MessageEntity,
) -> Option<String> {
    let start = entity.offset as usize;
    let end = start + entity.length as usize;
    if let Some(mention_text) = text.get(start..end) {
        // Remove @ prefix and convert to lowercase for consistent comparison
        let username = mention_text.trim_start_matches('@').to_lowercase();
        if !username.is_empty() {
            return Some(username);
        }
    }
    None
}

pub fn extract_url_from_entity(
    text: &str,
    entity: &teloxide::types::MessageEntity,
) -> Option<String> {
    match &entity.kind {
        teloxide::types::MessageEntityKind::Url => {
            let start = entity.offset as usize;
            let end = start + entity.length as usize;
            text.get(start..end).map(|s| s.to_string())
        }
        teloxide::types::MessageEntityKind::TextLink { url } => Some(url.to_string()),
        _ => None,
    }
}

pub fn normalize_domain(url_str: &str) -> Option<String> {
    let url_with_scheme = if url_str.starts_with("http://")
        || url_str.starts_with("https://")
        || url_str.starts_with("tg://")
    {
        url_str.to_string()
    } else {
        format!("http://{}", url_str)
    };

    if let Ok(url) = Url::parse(&url_with_scheme) {
        if let Some(host) = url.host_str() {
            let normalized = if host.starts_with("www.") {
                &host[4..]
            } else {
                host
            };
            return Some(normalized.to_lowercase());
        }
    }
    None
}

// Mention fallback:
// - no look-around
// - requires a non-word char (and NOT '.') or start before '@'
// - prevents matching emails like "a@b.com" because left side is a word char ('a')
pub static RE_MENTION: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)(^|[^a-z0-9_.])@[a-z0-9_]{5,32}($|[^a-z0-9_])").unwrap());

// Link fallback patterns
pub static RE_LINK_FALLBACK: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)[a-z][a-z0-9+.-]*://|www\.|t\.me/").unwrap());

// Email detection (separate trigger)
// "Good enough" moderation regex: catches typical emails.
pub static RE_EMAIL: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b").unwrap());

/// Extract message text with all links from entities appended
pub fn extract_message_with_links(
    text: &str,
    entities: &[teloxide::types::MessageEntity],
) -> String {
    let mut result = text.to_string();
    let mut links = Vec::new();

    for entity in entities {
        if let Some(url) = extract_url_from_entity(text, entity) {
            links.push(url);
        }
    }

    if !links.is_empty() {
        result.push_str(" [Links: ");
        result.push_str(&links.join(", "));
        result.push(']');
    }

    result
}
