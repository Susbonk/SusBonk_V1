<script lang="ts">
  import { authState, chatsState, uiState } from '../stores/index.js';
  import { login, getMe } from '../api/auth.js';
  import { listChats } from '../api/chats.js';

  interface Props {
    onSwitchToRegister: () => void;
  }

  let { onSwitchToRegister }: Props = $props();

  let email = $state('');
  let password = $state('');
  let error = $state('');
  let isLoading = $state(false);

  async function handleLogin() {
    if (!email || !password) {
      error = 'Please fill in all fields';
      return;
    }

    error = '';
    isLoading = true;

    try {
      await login({ email, password });
      const user = await getMe();
      
      authState.update(state => ({
        ...state,
        user,
        token: localStorage.getItem('susbonk_token'),
        isAuthenticated: true,
        isLoading: false
      }));

      // Fetch chats
      const chats = await listChats();
      chatsState.update(state => ({
        ...state,
        chats,
        activeChat: chats.length > 0 ? chats[0] : null,
        isLoading: false
      }));

      // Show onboarding if no chats
      if (chats.length === 0) {
        uiState.update(state => ({ ...state, showOnboarding: true }));
      }
    } catch (err: any) {
      error = err.message || 'Login failed';
      isLoading = false;
    }
  }
</script>

<div class="min-h-screen bg-white p-4 flex flex-col justify-center">
  <div class="max-w-md mx-auto w-full">
    <div class="card p-6">
      <h1 class="text-2xl font-black mb-6 text-center">Login to SusBonk</h1>
      
      {#if error}
        <div class="p-3 bg-red-100 border-3 border-red-500 text-red-700 font-bold text-sm mb-4">
          {error}
        </div>
      {/if}

      <form onsubmit={(e) => { e.preventDefault(); handleLogin(); }} class="space-y-4">
        <div>
          <label for="email" class="block font-bold mb-2">Email</label>
          <input
            id="email"
            type="email"
            bind:value={email}
            class="w-full p-3 border-3 border-black font-bold"
            placeholder="your@email.com"
            required
          />
        </div>

        <div>
          <label for="password" class="block font-bold mb-2">Password</label>
          <input
            id="password"
            type="password"
            bind:value={password}
            class="w-full p-3 border-3 border-black font-bold"
            placeholder="••••••••"
            required
          />
        </div>

        <button type="submit" class="w-full btn btn-primary py-3 text-lg font-black" disabled={isLoading}>
          {isLoading ? 'LOGGING IN...' : 'LOGIN'}
        </button>
      </form>

      <div class="mt-6 text-center">
        <button onclick={onSwitchToRegister} class="font-bold underline">
          Don't have an account? Register
        </button>
      </div>
    </div>
  </div>
</div>
