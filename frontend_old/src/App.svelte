<script lang="ts">
  import { onMount } from "svelte";
  import { getToken, setToken, auth, chats } from "./api";
  import { authState, chatsState, uiState } from "./lib/stores.js";
  import type { TabType } from "./lib/types.js";
  import Auth from "./Auth.svelte";
  import Dashboard from "./Dashboard.svelte";
  import BottomNav from "./BottomNav.svelte";
  import "./app.css";
  import "./scrollbar.css";

  let activeTab = $state<TabType>("dashboard");

  onMount(async () => {
    const token = getToken();
    if (token) {
      try {
        const user = await auth.me();
        authState.update((state) => ({
          ...state,
          user,
          token,
          isAuthenticated: true,
          isLoading: false,
        }));

        // Fetch chats after successful auth
        const chatList = await chats.list();
        chatsState.update((state) => ({
          ...state,
          chats: chatList.chats || [],
          activeChat: chatList.chats?.length > 0 ? chatList.chats[0] : null,
          isLoading: false,
        }));
      } catch {
        // Token invalid, stay logged out
        setToken(null);
      }
    }
  });

  function handleTabChange(tab: TabType) {
    activeTab = tab;
    uiState.update((state) => ({ ...state, activeTab: tab }));
  }

  function handleLogout() {
    setToken(null);
    authState.update((state) => ({
      ...state,
      user: null,
      token: null,
      isAuthenticated: false,
    }));
    window.location.reload();
  }
</script>

<div class="size-full {$authState.isAuthenticated ? 'pb-24' : ''}">
  {#if !$authState.isAuthenticated}
    <Auth />
  {:else}
    <Dashboard {activeTab} onLogout={handleLogout} />
  {/if}
</div>

{#if $authState.isAuthenticated}
  <BottomNav {activeTab} onTabChange={handleTabChange} />
{/if}
