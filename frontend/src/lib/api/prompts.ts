import { api } from './client.js';
import type { CustomPrompt, SystemPrompt } from '../types/api.js';

// Senior backend response structures
interface SystemPromptListResponse {
  prompts: SystemPrompt[];
}

interface CustomPromptListResponse {
  prompts: CustomPrompt[];
}

interface CustomPromptCreateRequest {
  title: string;
  text: string;
}

interface CustomPromptUpdateRequest {
  title?: string;
  text?: string;
  is_active?: boolean;
}

export async function listSystemPrompts(): Promise<SystemPrompt[]> {
  const response = await api.get<SystemPromptListResponse>('/prompts');
  return response.prompts;
}

export async function listCustomPrompts(): Promise<CustomPrompt[]> {
  const response = await api.get<CustomPromptListResponse>('/prompts/custom');
  return response.prompts;
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
