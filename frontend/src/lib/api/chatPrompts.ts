import { api } from './client';

export interface LinkedPrompt {
  id: number;
  prompt_id: number;
  prompt_name: string;
  threshold: number;
  priority: number;
  is_active: boolean;
}

export interface LinkedCustomPrompt {
  id: number;
  custom_prompt_id: number;
  custom_prompt_text: string;
  threshold: number;
  priority: number;
  is_active: boolean;
}

export interface ChatPromptsResponse {
  system_prompts: LinkedPrompt[];
  custom_prompts: LinkedCustomPrompt[];
}

export interface LinkPromptRequest {
  prompt_id: number;
  threshold?: number;
  priority?: number;
  is_active?: boolean;
}

export interface LinkCustomPromptRequest {
  custom_prompt_id: number;
  threshold?: number;
  priority?: number;
  is_active?: boolean;
}

export const chatPromptsApi = {
  getLinkedPrompts: (chatId: number) =>
    api.get<ChatPromptsResponse>(`/chats/${chatId}/linked_prompts`),

  linkPrompt: (chatId: number, data: LinkPromptRequest) =>
    api.post<LinkedPrompt>(`/chats/${chatId}/prompts`, data),

  unlinkPrompt: (chatId: number, promptId: number) =>
    api.delete(`/chats/${chatId}/prompts/${promptId}`),

  linkCustomPrompt: (chatId: number, data: LinkCustomPromptRequest) =>
    api.post<LinkedCustomPrompt>(`/chats/${chatId}/custom-prompts`, data),

  unlinkCustomPrompt: (chatId: number, customPromptId: number) =>
    api.delete(`/chats/${chatId}/custom-prompts/${customPromptId}`),
};
