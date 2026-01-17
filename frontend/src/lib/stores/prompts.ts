import { writable } from 'svelte/store';
import type { CustomPrompt } from '../types/api.js';

export interface PromptsState {
  systemPrompts: CustomPrompt[];
  customPrompts: CustomPrompt[];
  isLoading: boolean;
}

const initialState: PromptsState = {
  systemPrompts: [],
  customPrompts: [],
  isLoading: false
};

export const promptsState = writable<PromptsState>(initialState);
