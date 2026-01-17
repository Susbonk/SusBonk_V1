import { api } from './client.js';
import type { Chat } from '../types/api.js';

interface ChatListResponse {
  items: Chat[];
  total: number;
  page: number;
  page_size: number;
}

interface ChatUpdateRequest {
  enable_ai_check?: boolean;
  prompts_threshold?: number;
  custom_prompt_threshold?: number;
  cleanup_mentions?: boolean;
  cleanup_emojis?: boolean;
  cleanup_links?: boolean;
  allowed_link_domains?: Record<string, unknown>;
}

export async function listChats(): Promise<Chat[]> {
  const response = await api.get<ChatListResponse>('/chats');
  return response.items;
}

export async function getChat(chatId: string): Promise<Chat> {
  return api.get<Chat>(`/chats/${chatId}`);
}

export async function updateChat(chatId: string, data: ChatUpdateRequest): Promise<Chat> {
  return api.patch<Chat>(`/chats/${chatId}`, data);
}
