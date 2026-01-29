use serde_json::{json, Value as JsonValue};
use thiserror::Error;

#[derive(Clone)]
pub struct LlmClient {
    pub base_url: String,
    pub model: String,
    pub api_key: Option<String>,
    pub http: reqwest::Client,
}

#[derive(Debug, Error)]
pub enum RuntimeError {
    #[error("Redis error: {0}")]
    Redis(#[from] redis::RedisError),
    #[error("HTTP error: {0}")]
    Http(#[from] reqwest::Error),
    #[error("Bad response: {0}")]
    BadResponse(String),
    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),
}

impl LlmClient {
    fn looks_like_ollama(&self) -> bool {
        let s = self.base_url.to_lowercase();
        s.contains("11434") || s.contains("ollama") || s.ends_with("/api/chat")
    }

    fn normalize_url(base: &str) -> String {
        base.trim().trim_end_matches('/').to_string()
    }

    pub async fn one_shot(
        &self,
        user_text: &str,
        extra: Option<JsonValue>,
    ) -> Result<String, RuntimeError> {
        if self.looks_like_ollama() {
            self.ollama_chat(user_text, extra).await
        } else {
            self.openai_chat_completions(user_text, extra).await
        }
    }

    async fn openai_chat_completions(
        &self,
        user_text: &str,
        extra: Option<JsonValue>,
    ) -> Result<String, RuntimeError> {
        let base = Self::normalize_url(&self.base_url);
        let url = if base.ends_with("/v1/chat/completions") {
            base
        } else if base.ends_with("/v1") {
            format!("{base}/chat/completions")
        } else {
            format!("{base}/v1/chat/completions")
        };

        let mut payload = json!({
            "model": self.model,
            "messages": [{"role": "user", "content": user_text}],
        });

        if let Some(ex) = extra {
            if let (Some(obj), Some(ex_obj)) = (payload.as_object_mut(), ex.as_object()) {
                for (k, v) in ex_obj {
                    obj.insert(k.clone(), v.clone());
                }
            }
        }

        let mut req = self.http.post(url).header("Content-Type", "application/json");

        if let Some(key) = self.api_key.as_ref().filter(|s| !s.trim().is_empty()) {
            req = req.header("Authorization", format!("Bearer {key}"));
        }

        let resp = req.json(&payload).send().await?;

        if !resp.status().is_success() {
            let status = resp.status();
            let body = resp.text().await.unwrap_or_default();
            return Err(RuntimeError::BadResponse(format!(
                "HTTP {}: {}",
                status,
                &body[..body.len().min(2000)]
            )));
        }

        let data: JsonValue = resp.json().await?;
        let text = data
            .get("choices")
            .and_then(|v| v.get(0))
            .and_then(|v| v.get("message"))
            .and_then(|v| v.get("content"))
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .trim()
            .to_string();

        if text.is_empty() {
            return Err(RuntimeError::BadResponse("Empty model output".into()));
        }
        Ok(text)
    }

    async fn ollama_chat(
        &self,
        user_text: &str,
        extra: Option<JsonValue>,
    ) -> Result<String, RuntimeError> {
        let base = Self::normalize_url(&self.base_url);
        let url = if base.ends_with("/api/chat") {
            base
        } else {
            format!("{base}/api/chat")
        };

        let mut payload = json!({
            "model": self.model,
            "messages": [{"role": "user", "content": user_text}],
            "stream": false,
            "keep_alive": "5m",
        });

        if let Some(ex) = extra {
            if let (Some(obj), Some(ex_obj)) = (payload.as_object_mut(), ex.as_object()) {
                for (k, v) in ex_obj {
                    obj.insert(k.clone(), v.clone());
                }
            }
        }

        let resp = self
            .http
            .post(url)
            .header("Content-Type", "application/json")
            .json(&payload)
            .send()
            .await?;

        if !resp.status().is_success() {
            let status = resp.status();
            let body = resp.text().await.unwrap_or_default();
            return Err(RuntimeError::BadResponse(format!(
                "HTTP {}: {}",
                status,
                &body[..body.len().min(2000)]
            )));
        }

        let data: JsonValue = resp.json().await?;
        let text = data
            .get("message")
            .and_then(|v| v.get("content"))
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .trim()
            .to_string();

        if text.is_empty() {
            return Err(RuntimeError::BadResponse("Empty model output".into()));
        }
        Ok(text)
    }
}
