export interface User {
  id: string;
  email: string;
  username?: string;
  created_at: string;
}

export interface Chat {
  id: string;
  title: string;
  type: 'telegram' | 'discord';
  enable_ai_check: boolean;
  prompts_threshold: number;
  custom_prompt_threshold: number;
  spam_detected: number;
  processed_messages: number;
  created_at: string;
  updated_at: string;
}

export interface CustomPrompt {
  id: string;
  user_id: string;
  name: string;
  prompt_text: string;
  is_active: boolean;
  created_at: string;
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
