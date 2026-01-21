export interface User {
  id: string;
  email: string;
  username?: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  telegram_user_id?: number;
  discord_user_id?: number;
}

export interface Chat {
  id: string;
  title: string | null;
  chat_link?: string | null;
  type: string;
  platform_chat_id: number;
  user_id: string;
  enable_ai_check: boolean;
  prompts_threshold: number;
  custom_prompt_threshold: number;
  cleanup_mentions: boolean;
  allowed_mentions?: string[] | null;
  cleanup_emojis: boolean;
  max_emoji_count: number;
  cleanup_links: boolean;
  allowed_link_domains?: string[] | null;
  cleanup_emails: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  // Legacy fields for backward compatibility
  spam_detected?: number;
  processed_messages?: number;
}

// Uses 'title' and 'text' with validation aliases from name/prompt_text
export interface SystemPrompt {
  id: string;
  title: string | null;
  text: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CustomPrompt {
  id: string;
  user_id: string;
  title: string | null;
  text: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserState {
  id: string;
  external_user_id: number;
  trusted: boolean;
  valid_messages: number;
  created_at: string;
  updated_at: string;
}

export interface LogEntry {
  id: string;
  chat_id: string;
  user_id: string;
  message: string;
  spam_detected: boolean;
  timestamp: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
}
