# Store Usage Guide

## Quick Reference

### Import Stores
```typescript
import { authState, chatsState, promptsState, uiState } from '$lib/stores/index.js';
```

### Auth Store
```typescript
// Read
$authState.isAuthenticated
$authState.user
$authState.token

// Update (for API integration)
authState.update(state => ({
  ...state,
  user: apiUser,
  token: apiToken,
  isAuthenticated: true
}));
```

### Chats Store
```typescript
// Read
$chatsState.chats
$chatsState.activeChat
$chatsState.isLoading

// Update (for API integration)
chatsState.update(state => ({
  ...state,
  chats: apiChats,
  activeChat: apiChats[0] || null
}));
```

### Prompts Store
```typescript
// Read
$promptsState.systemPrompts
$promptsState.customPrompts
$promptsState.isLoading

// Update (for API integration)
promptsState.update(state => ({
  ...state,
  customPrompts: apiPrompts
}));
```

### UI Store
```typescript
// Read
$uiState.activeTab
$uiState.showOnboarding

// Update
uiState.update(state => ({
  ...state,
  activeTab: 'logs',
  showOnboarding: false
}));
```

## API Types Reference

### User
```typescript
interface User {
  id: string;
  email: string;
  username?: string;
  created_at: string;
}
```

### Chat
```typescript
interface Chat {
  id: string;
  title: string;
  type: 'telegram' | 'discord';
  enable_ai_check: boolean;
  prompts_threshold: number;
  custom_prompt_threshold: number;
  spam_detected: number;
  processed_messages: number;
  created_at: string;
  updated_at: string;
}
```

### CustomPrompt
```typescript
interface CustomPrompt {
  id: string;
  title: string;
  text: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

### UserState
```typescript
interface UserState {
  id: string;
  external_user_id: number;
  trusted: boolean;
  valid_messages: number;
  created_at: string;
  updated_at: string;
}
```

## Component Integration Examples

### Login Component (Future API Integration)
```typescript
async function handleLogin() {
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    
    authState.update(state => ({
      ...state,
      user: data.user,
      token: data.token,
      isAuthenticated: true
    }));
  } catch (error) {
    console.error('Login failed:', error);
  }
}
```

### Dashboard Component (Future API Integration)
```typescript
async function loadChats() {
  chatsState.update(state => ({ ...state, isLoading: true }));
  
  try {
    const response = await fetch('/api/chats', {
      headers: { 'Authorization': `Bearer ${$authState.token}` }
    });
    
    const chats = await response.json();
    
    chatsState.update(state => ({
      ...state,
      chats,
      activeChat: chats[0] || null,
      isLoading: false
    }));
  } catch (error) {
    console.error('Failed to load chats:', error);
    chatsState.update(state => ({ ...state, isLoading: false }));
  }
}
```
