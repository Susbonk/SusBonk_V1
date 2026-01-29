<script lang="ts">
  import { auth, setToken } from "./api";
  import { authState, chatsState } from "./lib/stores.js";
  import { chats } from "./api";

  let email = $state("");
  let password = $state("");
  let confirmPassword = $state("");
  let username = $state("");
  let isLogin = $state(true);
  let error = $state("");
  let isLoading = $state(false);

  // Real-time password validation for registration
  let passwordError = $derived(
    !isLogin && confirmPassword && password !== confirmPassword
      ? "Passwords do not match"
      : ""
  );

  async function handleSubmit() {
    error = "";
    isLoading = true;

    try {
      if (isLogin) {
        const response = await auth.login(email, password);
        const user = await auth.me();

        authState.update((state) => ({
          ...state,
          user,
          token: response.access_token,
          isAuthenticated: true,
          isLoading: false,
        }));

        // Fetch chats after login
        const chatList = await chats.list();
        chatsState.update((state) => ({
          ...state,
          chats: chatList.chats || [],
          activeChat: chatList.chats?.length > 0 ? chatList.chats[0] : null,
        }));
      } else {
        // Validate password match for registration
        if (password !== confirmPassword) {
          error = "Passwords do not match";
          isLoading = false;
          return;
        }

        await auth.register(email, password, username || undefined);
        isLogin = true;
        error = "";
        alert("Registration successful! Please log in.");
      }
    } catch (e: any) {
      error = e.message || "Something went wrong";
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="min-h-screen bg-[#CCFF00] p-4 flex flex-col justify-center">
  <div class="max-w-md mx-auto w-full">
    <!-- Logo/Header -->
    <div class="text-center mb-8">
      <img
        src="/bonk_dog.jpg"
        alt="SusBonk Doggo"
        class="w-32 h-32 mx-auto mb-4 border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-xl object-cover"
      />
      <h1 class="text-5xl font-black mb-2">SusBonk</h1>
      <p class="text-lg font-bold">Anti-Spam Bot Dashboard</p>
    </div>

    <div class="card">
      <h2 class="text-2xl font-black mb-6 text-center">
        {isLogin ? "Login" : "Register"}
      </h2>

      {#if error}
        <div
          class="p-3 bg-red-100 border-3 border-red-500 text-red-700 font-bold text-sm mb-4"
        >
          {error}
        </div>
      {/if}

      <form
        onsubmit={(e) => {
          e.preventDefault();
          handleSubmit();
        }}
        class="space-y-4"
      >
        <div>
          <label for="email" class="block font-bold mb-2">Email</label>
          <input
            id="email"
            type="email"
            bind:value={email}
            class="w-full"
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
            class="w-full"
            placeholder="••••••••"
            required
          />
        </div>

        {#if !isLogin}
          <div>
            <label for="confirmPassword" class="block font-bold mb-2"
              >Confirm Password</label
            >
            <input
              id="confirmPassword"
              type="password"
              bind:value={confirmPassword}
              class="w-full"
              placeholder="••••••••"
              required
            />
            {#if passwordError}
              <p class="text-red-600 text-sm font-bold mt-1">{passwordError}</p>
            {/if}
          </div>

          <div>
            <label for="username" class="block font-bold mb-2"
              >Username (optional)</label
            >
            <input
              id="username"
              type="text"
              bind:value={username}
              class="w-full"
              placeholder="cooluser123"
            />
          </div>
        {/if}

        <button
          type="submit"
          class="w-full btn btn-primary py-3 text-lg font-black"
          disabled={isLoading || !!passwordError}
        >
          {isLoading ? "LOADING..." : isLogin ? "LOGIN" : "REGISTER"}
        </button>
      </form>

      <div class="mt-6 text-center">
        <button
          onclick={() => (isLogin = !isLogin)}
          class="font-bold underline hover:text-[#FF8A00] transition-colors"
        >
          {isLogin
            ? "Don't have an account? Register"
            : "Already have an account? Login"}
        </button>
      </div>

    </div>

    <p class="text-center mt-6 font-medium text-sm">
      Protect your Telegram groups from spam 🛡️
    </p>
  </div>
</div>
