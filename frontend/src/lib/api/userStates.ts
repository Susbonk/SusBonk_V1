import { api } from './client.js';
import type { UserState } from '../types/api.js';

interface UserStateListResponse {
  items: UserState[];
  total: number;
  page: number;
  page_size: number;
}

interface UserStateUpdateRequest {
  trusted?: boolean;
}

export async function listUserStates(chatId: string): Promise<UserState[]> {
  const response = await api.get<UserStateListResponse>(`/chats/${chatId}/user-states`);
  return response.items;
}

export async function updateUserState(
  chatId: string,
  stateId: string,
  data: UserStateUpdateRequest
): Promise<UserState> {
  return api.patch<UserState>(`/chats/${chatId}/user-states/${stateId}`, data);
}

export async function makeUntrusted(chatId: string, stateId: string): Promise<UserState> {
  return api.post<UserState>(`/chats/${chatId}/user-states/${stateId}/make-untrusted`);
}
