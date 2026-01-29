export interface User {
    id: string;
    email: string;
    username?: string;
    created_at: string;
    updated_at?: string;
    is_active?: boolean;
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
    prompts_threshold?: number;
    custom_prompt_threshold?: number;
    cleanup_mentions: boolean;
    allowed_mentions?: string[] | null;
    cleanup_emojis: boolean;
    max_emoji_count: number;
    cleanup_links: boolean;
    allowed_link_domains?: string[] | null;
    cleanup_emails: boolean;
    min_messages_required?: number;
    min_observation_minutes?: number;
    is_active?: boolean;
    created_at: string;
    updated_at?: string;
    // Legacy fields for backward compatibility
    spam_detected?: number;
    processed_messages?: number;
}

export interface SystemPrompt {
    id: string;
    title: string | null;
    text: string;
    is_active: boolean;
    created_at: string;
    updated_at?: string;
}

export interface CustomPrompt {
    id: string;
    user_id: string;
    title: string | null;
    text: string;
    is_active: boolean;
    created_at: string;
    updated_at?: string;
}

export interface ChatPromptLink {
    prompt_id: string;
    threshold: number;
    priority?: number;
    is_active?: boolean;
}

export interface ChatCustomPromptLink {
    custom_prompt_id: string;
    threshold: number;
    priority?: number;
    is_active?: boolean;
}

export interface UserState {
    id: string;
    external_user_id: number;
    trusted: boolean;
    valid_messages: number;
    joined_at?: string;
    created_at: string;
    updated_at?: string;
}

export interface DeletedMessage {
    id: string;
    chat_id: string;
    user_id: string;
    message: string;
    reason?: string;
    timestamp: string;
}

export interface ApiResponse<T> {
    data: T;
    message?: string;
    error?: string;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    page_size: number;
}

// UI Types
export type TabType = 'dashboard' | 'logs' | 'settings';
export type SettingsTabType = 'telegram' | 'members' | 'whitelist';
export type StrengthLevel = 'Chill' | 'Normal' | 'Bonkers';

// Design tokens
export const colors = {
    primary: '#CCFF00',      // Lime green - active states
    secondary: '#FF8A00',    // Orange - CTAs
    black: '#000000',
    white: '#FFFFFF',
    gray: {
        50: '#f9fafb',
        100: '#f3f4f6',
        200: '#e5e7eb',
        400: '#9ca3af',
        500: '#6b7280',
        600: '#4b5563',
    },
    hover: {
        primary: '#d9ff33',
        secondary: '#ff9f2e',
        item: '#fff9e6',
    }
} as const;
