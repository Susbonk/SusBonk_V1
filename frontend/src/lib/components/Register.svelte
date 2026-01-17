<script lang="ts">
  import { register } from '../api/auth.js';

  interface Props {
    onSwitchToLogin: () => void;
  }

  let { onSwitchToLogin }: Props = $props();

  let email = $state('');
  let password = $state('');
  let username = $state('');
  let error = $state('');
  let success = $state('');
  let isLoading = $state(false);

  async function handleRegister() {
    if (!email || !password) {
      error = 'Please fill in email and password';
      return;
    }

    error = '';
    success = '';
    isLoading = true;

    try {
      await register({ email, password, username: username || undefined });
      success = 'Account created! Please login.';
      setTimeout(() => onSwitchToLogin(), 2000);
    } catch (err: any) {
      error = err.message || 'Registration failed';
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="min-h-screen bg-white p-4 flex flex-col justify-center">
  <div class="max-w-md mx-auto w-full">
    <div class="card p-6">
      <h1 class="text-2xl font-black mb-6 text-center">Join SusBonk</h1>
      
      {#if error}
        <div class="p-3 bg-red-100 border-3 border-red-500 text-red-700 font-bold text-sm mb-4">
          {error}
        </div>
      {/if}

      {#if success}
        <div class="p-3 bg-green-100 border-3 border-green-500 text-green-700 font-bold text-sm mb-4">
          {success}
        </div>
      {/if}

      <form onsubmit={(e) => { e.preventDefault(); handleRegister(); }} class="space-y-4">
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
          <label for="username" class="block font-bold mb-2">Username <span class="text-gray-500">(optional)</span></label>
          <input
            id="username"
            type="text"
            bind:value={username}
            class="w-full p-3 border-3 border-black font-bold"
            placeholder="cooluser123"
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

        <button type="submit" class="w-full btn btn-secondary py-3 text-lg font-black" disabled={isLoading}>
          {isLoading ? 'CREATING ACCOUNT...' : 'REGISTER'}
        </button>
      </form>

      <div class="mt-6 text-center">
        <button onclick={onSwitchToLogin} class="font-bold underline">
          Already have an account? Login
        </button>
      </div>
    </div>
  </div>
</div>
