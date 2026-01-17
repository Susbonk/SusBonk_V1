import { writable } from 'svelte/store';
import type { User } from '../types/api.js';

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false
};

export const authState = writable<AuthState>(initialState);
