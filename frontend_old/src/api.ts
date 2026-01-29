const API_URL = import.meta.env.VITE_API_URL || '';

let token: string | null = localStorage.getItem('token');

export const setToken = (t: string | null) => {
  token = t;
  if (t) localStorage.setItem('token', t);
  else localStorage.removeItem('token');
};

export const getToken = () => token;

const request = async (path: string, options: RequestInit = {}) => {
  const headers: HeadersInit = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) throw new Error(await res.text());
  return res.status === 204 ? null : res.json();
};

export const auth = {
  register: (email: string, password: string, username?: string) =>
    request('/auth/register', { method: 'POST', body: JSON.stringify({ email, password, username }) }),
  login: async (email: string, password: string) => {
    const data = await request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
    setToken(data.access_token);
    return data;
  },
  me: () => request('/auth/me'),
  connectTelegram: () => request('/auth/me/connect_telegram'),
};

export const chats = {
  list: () => request('/chats'),
  get: (id: string) => request(`/chats/${id}`),
  update: (id: string, data: any) => request(`/chats/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  getLinks: (id: string) => request(`/chats/${id}/linked_prompts`),
};

export const deletedMessages = {
  list: (chatId: string) => request(`/deleted-messages/${chatId}`),
};

export const userStates = {
  list: (chatId: string) => request(`/chats/${chatId}/user-states`),
  makeUntrusted: (chatId: string, stateId: string) =>
    request(`/chats/${chatId}/user-states/${stateId}/make-untrusted`, { method: 'POST' }),
  update: (chatId: string, stateId: string, data: any) =>
    request(`/chats/${chatId}/user-states/${stateId}`, { method: 'PATCH', body: JSON.stringify(data) }),
};

export const prompts = {
  list: () => request('/prompts'),
  get: (id: string) => request(`/prompts/${id}`),
};

export const customPrompts = {
  list: () => request('/prompts/custom'),
  create: (data: { title?: string; text: string; is_active?: boolean }) =>
    request('/prompts/custom', { method: 'POST', body: JSON.stringify(data) }),
  get: (id: string) => request(`/prompts/custom/${id}`),
  update: (id: string, data: { title?: string; text?: string; is_active?: boolean }) =>
    request(`/prompts/custom/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (id: string) => request(`/prompts/custom/${id}`, { method: 'DELETE' }),
};

export const chatPrompts = {
  linkPrompt: (chatId: string, data: { prompt_id: string; priority?: number; threshold?: number; is_active?: boolean }) =>
    request(`/chats/${chatId}/prompts`, { method: 'POST', body: JSON.stringify(data) }),
  unlinkPrompt: (chatId: string, promptId: string) =>
    request(`/chats/${chatId}/prompts/${promptId}`, { method: 'DELETE' }),
  linkCustomPrompt: (chatId: string, data: { custom_prompt_id: string; priority?: number; threshold?: number; is_active?: boolean }) =>
    request(`/chats/${chatId}/custom-prompts`, { method: 'POST', body: JSON.stringify(data) }),
  unlinkCustomPrompt: (chatId: string, customPromptId: string) =>
    request(`/chats/${chatId}/custom-prompts/${customPromptId}`, { method: 'DELETE' }),
};
