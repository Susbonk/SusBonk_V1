import { api } from './client.js';
import type { CustomPrompt } from '../types/api.js';

interface CustomPromptListResponse {
  items: CustomPrompt[];
  total: number;
  page: number;
  page_size: number;
}

interface CustomPromptCreateRequest {
  name: string;
  prompt_text: string;
}

interface CustomPromptUpdateRequest {
  name?: string;
  prompt_text?: string;
  is_active?: boolean;
}

export async function listCustomPrompts(): Promise<CustomPrompt[]> {
  const response = await api.get<CustomPromptListResponse>('/prompts/custom');
  return response.items;
}

export async function createPrompt(data: CustomPromptCreateRequest): Promise<CustomPrompt> {
  return api.post<CustomPrompt>('/prompts/custom', data);
}

export async function updatePrompt(
  promptId: string,
  data: CustomPromptUpdateRequest
): Promise<CustomPrompt> {
  return api.patch<CustomPrompt>(`/prompts/custom/${promptId}`, data);
}

export async function deletePrompt(promptId: string): Promise<void> {
  await api.delete(`/prompts/custom/${promptId}`);
}
