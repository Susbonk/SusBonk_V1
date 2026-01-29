use serde::{Deserialize, Serialize};

/// Redis stream names for AI task/result communication
pub mod streams {
    /// Stream for AI spam detection tasks (bot → AI service)
    pub const AI_TASKS: &str = "ai:tasks";
    
    /// Consumer group for AI service workers
    pub const AI_TASKS_GROUP: &str = "ai-workers";
    
    /// Stream for AI spam detection results (AI service → bot)
    pub const AI_RESULTS: &str = "ai:results";
    
    /// Consumer group for bot result processors
    pub const AI_RESULTS_GROUP: &str = "bot-processors";
}

/// AI spam detection task payload (bot → AI service)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AiTask {
    /// Unique task identifier
    pub task_id: String,
    
    /// Telegram chat ID
    pub chat_id: i64,
    
    /// Telegram message ID
    pub message_id: i32,
    
    /// Telegram user ID who sent the message
    pub user_id: i64,
    
    /// Message text to analyze
    pub message_text: String,
    
    /// List of prompt IDs to evaluate
    pub prompt_ids: Vec<i32>,
    
    /// Detection thresholds per prompt (optional, uses defaults if not provided)
    #[serde(default)]
    pub thresholds: Vec<f32>,
    
    /// Unix timestamp when task was created
    pub created_at: i64,
}

/// AI spam detection result payload (AI service → bot)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AiResult {
    /// Task ID this result corresponds to
    pub task_id: String,
    
    /// Whether processing succeeded
    pub ok: bool,
    
    /// Error message if ok=false
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
    
    /// Whether message is classified as spam
    pub is_spam: bool,
    
    /// Spam confidence score (0.0 - 1.0)
    pub score: f32,
    
    /// ID of the prompt that matched (if is_spam=true)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub matched_prompt_id: Option<i32>,
    
    /// Name of the prompt that matched
    #[serde(skip_serializing_if = "Option::is_none")]
    pub matched_prompt_name: Option<String>,
    
    /// Processing time in milliseconds
    pub elapsed_ms: u64,
    
    /// Message context fields (echoed back for correlation)
    pub chat_id: i64,
    pub message_id: i32,
    pub user_id: i64,
    
    /// Unix timestamp when result was generated
    pub completed_at: i64,
}

impl AiTask {
    /// Create a new AI task with current timestamp
    pub fn new(
        task_id: String,
        chat_id: i64,
        message_id: i32,
        user_id: i64,
        message_text: String,
        prompt_ids: Vec<i32>,
        thresholds: Vec<f32>,
    ) -> Self {
        Self {
            task_id,
            chat_id,
            message_id,
            user_id,
            message_text,
            prompt_ids,
            thresholds,
            created_at: chrono::Utc::now().timestamp(),
        }
    }
}

impl AiResult {
    /// Create a successful spam detection result
    pub fn spam(
        task_id: String,
        score: f32,
        matched_prompt_id: i32,
        matched_prompt_name: String,
        elapsed_ms: u64,
        chat_id: i64,
        message_id: i32,
        user_id: i64,
    ) -> Self {
        Self {
            task_id,
            ok: true,
            error: None,
            is_spam: true,
            score,
            matched_prompt_id: Some(matched_prompt_id),
            matched_prompt_name: Some(matched_prompt_name),
            elapsed_ms,
            chat_id,
            message_id,
            user_id,
            completed_at: chrono::Utc::now().timestamp(),
        }
    }
    
    /// Create a successful non-spam result
    pub fn not_spam(
        task_id: String,
        score: f32,
        elapsed_ms: u64,
        chat_id: i64,
        message_id: i32,
        user_id: i64,
    ) -> Self {
        Self {
            task_id,
            ok: true,
            error: None,
            is_spam: false,
            score,
            matched_prompt_id: None,
            matched_prompt_name: None,
            elapsed_ms,
            chat_id,
            message_id,
            user_id,
            completed_at: chrono::Utc::now().timestamp(),
        }
    }
    
    /// Create an error result
    pub fn error(
        task_id: String,
        error: String,
        chat_id: i64,
        message_id: i32,
        user_id: i64,
    ) -> Self {
        Self {
            task_id,
            ok: false,
            error: Some(error),
            is_spam: false,
            score: 0.0,
            matched_prompt_id: None,
            matched_prompt_name: None,
            elapsed_ms: 0,
            chat_id,
            message_id,
            user_id,
            completed_at: chrono::Utc::now().timestamp(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_task_serialization() {
        let task = AiTask::new(
            "task-123".to_string(),
            -1001234567890,
            42,
            987654321,
            "Buy crypto now!".to_string(),
            vec![1, 2, 3],
            vec![0.7, 0.8, 0.9],
        );
        
        let json = serde_json::to_string(&task).unwrap();
        let deserialized: AiTask = serde_json::from_str(&json).unwrap();
        
        assert_eq!(task.task_id, deserialized.task_id);
        assert_eq!(task.chat_id, deserialized.chat_id);
        assert_eq!(task.prompt_ids, deserialized.prompt_ids);
    }

    #[test]
    fn test_result_spam() {
        let result = AiResult::spam(
            "task-123".to_string(),
            0.95,
            1,
            "Crypto Scam".to_string(),
            150,
            -1001234567890,
            42,
            987654321,
        );
        
        assert!(result.ok);
        assert!(result.is_spam);
        assert_eq!(result.score, 0.95);
        assert_eq!(result.matched_prompt_id, Some(1));
    }

    #[test]
    fn test_result_not_spam() {
        let result = AiResult::not_spam(
            "task-123".to_string(),
            0.15,
            100,
            -1001234567890,
            42,
            987654321,
        );
        
        assert!(result.ok);
        assert!(!result.is_spam);
        assert_eq!(result.matched_prompt_id, None);
    }

    #[test]
    fn test_result_error() {
        let result = AiResult::error(
            "task-123".to_string(),
            "Model timeout".to_string(),
            -1001234567890,
            42,
            987654321,
        );
        
        assert!(!result.ok);
        assert_eq!(result.error, Some("Model timeout".to_string()));
    }
}
