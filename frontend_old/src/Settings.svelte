<script lang="ts">
  import { onMount } from "svelte";
  import { auth, setToken } from "./api";
  import Modal from "./Modal.svelte"; // Updated import
  import {
    ExternalLink,
    MessageCircle,
    CheckCircle,
    AlertCircle,
    User,
    LogOut, // Added import
  } from "lucide-svelte";

  let user = $state<any>(null);
  let telegramData = $state<any>(null);
  let loading = $state(false);
  let connectionStatus = $state<"checking" | "connected" | "pending" | "error">(
    "checking",
  );
  let errorMessage = $state("");
  let showLogoutModal = $state(false);

  import { authState, chatsState } from "./lib/stores.js"; // Updated import

  onMount(async () => {
    try {
      user = await auth.me();
    } catch (err) {
      // DEV MODE: Use mock data from store
      console.warn("API unavailable, using mock data:", err);
      user = $authState.user || {
        id: "dev-user-1",
        email: "dev@test.com",
        username: "DevUser",
        telegram_user_id: null,
      };
    }
    await checkTelegramConnection();
  });

  async function checkTelegramConnection() {
    connectionStatus = "checking";
    try {
      const data = await auth.connectTelegram();
      if (data.status === "already_connected" || user?.telegram_user_id) {
        connectionStatus = "connected";
      } else {
        connectionStatus = "pending";
        telegramData = data;
      }
    } catch (err) {
      // DEV MODE: Show pending status for demo
      connectionStatus = "pending";
      telegramData = {
        bot_link: "https://t.me/SusBonkBot?start=demo",
        code: "DEMO123",
      };
    }
  }

  function openTelegramBot() {
    if (telegramData?.bot_link) {
      window.open(telegramData.bot_link, "_blank");
    }
  }

  function confirmLogout() {
    showLogoutModal = true;
  }

  function logout() {
    setToken(null);
    authState.update((s) => ({
      ...s,
      user: null,
      token: null,
      isAuthenticated: false,
    }));
    chatsState.set({
      chats: [],
      activeChat: null,
      isLoading: false,
    });
    showLogoutModal = false;
  }
</script>

<div class="space-y-4">
  {#if user}
    <!-- Profile Card -->
    <div class="card">
      <div class="flex items-center gap-3 mb-4">
        <div
          class="w-12 h-12 bg-[#CCFF00] border-3 border-black flex items-center justify-center"
        >
          <User class="w-6 h-6" />
        </div>
        <div>
          <h3 class="font-black text-lg tracking-tight">
            {user.username || "User"}
          </h3>
        </div>
      </div>
    </div>

    <!-- Telegram Connection Card -->
    <div class="card">
      <div class="flex items-center gap-2 mb-4">
        <MessageCircle class="w-5 h-5 text-blue-500" />
        <h3 class="font-extrabold">Telegram Connection</h3>
      </div>

      <div class="space-y-4">
        {#if connectionStatus === "checking"}
          <div
            class="flex items-center gap-3 p-4 bg-gray-50 border-3 border-gray-300"
          >
            <div
              class="animate-spin w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full"
            ></div>
            <span class="font-medium">Checking connection status...</span>
          </div>
        {:else if connectionStatus === "connected" || user.telegram_user_id}
          <div
            class="flex items-center gap-3 p-4 bg-[#CCFF00] border-3 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
          >
            <img
              src="/doggo_thumbs_up.jpg"
              alt="Doggo Thumbs Up"
              class="w-16 h-16 object-cover border-2 border-black bg-white"
            />
            <div>
              <div class="font-black text-xl leading-tight text-black">
                Your Telegram got a Doggo
              </div>
              <div
                class="text-xs font-bold uppercase tracking-wide text-black mt-1"
              >
                Doggo is ready to fight bots!
              </div>
            </div>
          </div>
        {:else if connectionStatus === "pending"}
          <div class="space-y-4">
            <div
              class="flex items-center gap-3 p-4 bg-yellow-50 border-3 border-yellow-400"
            >
              <AlertCircle class="w-5 h-5 text-yellow-600" />
              <div>
                <div class="font-bold text-yellow-800">Connection Pending</div>
                <div class="text-sm text-yellow-600">
                  Click the button below to connect with SusBonk bot
                </div>
              </div>
            </div>

            <div class="space-y-3 p-4 bg-gray-50 border-3 border-black">
              <h4 class="font-bold">How to connect:</h4>
              <ol class="list-decimal list-inside space-y-2 text-sm">
                <li>Click "Connect to Telegram" button below</li>
                <li>Telegram will open automatically</li>
                <li>
                  Click the <strong>Start</strong> button at the bottom
                </li>
                <li>Your account will be linked instantly</li>
              </ol>
            </div>

            <button
              onclick={openTelegramBot}
              class="w-full bg-blue-500 hover:bg-blue-600 text-white border-3 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] py-3 font-bold flex items-center justify-center gap-2 transition-all active:shadow-none active:translate-x-[4px] active:translate-y-[4px]"
            >
              <ExternalLink class="w-5 h-5" />
              Connect to Telegram
            </button>

            <button
              onclick={checkTelegramConnection}
              class="w-full bg-gray-200 hover:bg-gray-300 border-3 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] py-3 font-bold transition-all active:shadow-none active:translate-x-[4px] active:translate-y-[4px]"
            >
              Check Connection Status
            </button>
          </div>
        {:else if connectionStatus === "error"}
          <div
            class="flex items-center gap-3 p-4 bg-red-50 border-3 border-red-400"
          >
            <AlertCircle class="w-5 h-5 text-red-600" />
            <div>
              <div class="font-bold text-red-800">Connection Error</div>
              <div class="text-sm text-red-600">{errorMessage}</div>
            </div>
          </div>

          <button
            onclick={checkTelegramConnection}
            class="w-full bg-gray-200 hover:bg-gray-300 border-3 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] py-3 font-bold transition-all active:shadow-none active:translate-x-[4px] active:translate-y-[4px]"
          >
            Retry Connection Check
          </button>
        {/if}
      </div>
    </div>

    <!-- Discord Connection Card -->
    <div class="card">
      <div class="flex items-center gap-2 mb-4">
        <MessageCircle class="w-5 h-5 text-indigo-500" />
        <h3 class="font-extrabold">Discord Connection (Work in progress)</h3>
      </div>

      <div
        class="flex items-center gap-3 p-4 bg-gray-50 border-3 border-gray-300 border-dashed"
      >
        <img
          src="/discord_wip_doggo.jpg"
          alt="Work in Progress"
          class="w-16 h-16 object-cover border-2 border-black bg-white"
        />
        <div>
          <div class="font-black text-xl leading-tight text-gray-500">
            Coming Soon
          </div>
          <div
            class="text-xs font-bold uppercase tracking-wide text-gray-400 mt-1"
          >
            Doggo is working hard on this!
          </div>
        </div>
      </div>
    </div>

    <!-- Logout Button -->
    <button
      onclick={confirmLogout}
      class="w-full btn bg-[#FF8A00] hover:bg-[#E67C00] py-3 font-black flex items-center justify-center gap-2"
    >
      <LogOut class="w-5 h-5" />
      LOGOUT
    </button>
  {:else}
    <div class="card text-center py-8">
      <div class="animate-pulse">Loading profile...</div>
    </div>
  {/if}
</div>

{#if showLogoutModal}
  <Modal
    title="Confirm Logout"
    message="Are you sure you want to log out?"
    confirmText="Logout"
    onConfirm={logout}
    onCancel={() => (showLogoutModal = false)}
  />
{/if}
