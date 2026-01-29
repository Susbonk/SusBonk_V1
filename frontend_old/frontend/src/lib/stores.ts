import { writable } from 'svelte/store';
import type { User, Chat, CustomPrompt, TabType } from './types.js';

// Auth State
export interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
}

const initialAuthState: AuthState = {
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: false
};

export const authState = writable<AuthState>(initialAuthState);

// Chats State
export interface ChatsState {
    chats: Chat[];
    activeChat: Chat | null;
    isLoading: boolean;
}

const initialChatsState: ChatsState = {
    chats: [],
    activeChat: null,
    isLoading: false
};

export const chatsState = writable<ChatsState>(initialChatsState);

// Prompts State
export interface PromptsState {
    systemPrompts: CustomPrompt[];
    customPrompts: CustomPrompt[];
    isLoading: boolean;
}

const initialPromptsState: PromptsState = {
    systemPrompts: [],
    customPrompts: [],
    isLoading: false
};

export const promptsState = writable<PromptsState>(initialPromptsState);

// UI State
export interface UIState {
    activeTab: TabType;
    showOnboarding: boolean;
}

const initialUIState: UIState = {
    activeTab: 'dashboard',
    showOnboarding: false
};

export const uiState = writable<UIState>(initialUIState);
