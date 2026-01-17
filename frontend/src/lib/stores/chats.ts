import { writable } from 'svelte/store';
import type { Chat } from '../types/api.js';

export interface ChatsState {
  chats: Chat[];
  activeChat: Chat | null;
  isLoading: boolean;
}

const initialState: ChatsState = {
  chats: [],
  activeChat: null,
  isLoading: false
};

export const chatsState = writable<ChatsState>(initialState);
