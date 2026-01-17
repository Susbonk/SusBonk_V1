import { api, setToken, clearToken } from './client.js';
import type { User } from '../types/api.js';

interface RegisterRequest {
  email: string;
  password: string;
  username?: string;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export async function register(data: RegisterRequest): Promise<User> {
  return api.post<User>('/auth/register', data);
}

export async function login(data: LoginRequest): Promise<string> {
  const response = await api.post<TokenResponse>('/auth/login', data);
  setToken(response.access_token);
  return response.access_token;
}

export async function getMe(): Promise<User> {
  return api.get<User>('/auth/me');
}

export function logout(): void {
  clearToken();
}
