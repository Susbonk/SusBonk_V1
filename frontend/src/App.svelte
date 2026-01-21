<script lang="ts">
  import { onMount } from 'svelte';
  import Onboarding from './lib/components/Onboarding.svelte';
  import Dashboard from './lib/components/Dashboard.svelte';
  import BottomNav from './lib/components/BottomNav.svelte';
  import AuthDemo from './lib/components/AuthDemo.svelte';
  import { uiState, authState, chatsState } from './lib/stores/index.js';
  import { getMe } from './lib/api/auth.js';
  import { listChats } from './lib/api/chats.js';
  import { getToken } from './lib/api/client.js';
  import type { TabType } from './lib/types';
  import './app.css';

  let activeTab = $state<TabType>($uiState.activeTab);

  onMount(async () => {
    // DEV MODE: Skip auth for UI testing when ?dev=true
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('dev') === 'true') {
      authState.update((state) => ({
        ...state,
        user: { id: 'dev-user', email: 'dev@test.com', created_at: new Date().toISOString() },
        token: 'dev-token',
        isAuthenticated: true,
        isLoading: false,
      }));
      chatsState.update((state) => ({
        ...state,
        chats: [
          {
            id: 'dev-chat-1',
            title: 'MyTestGroup',
            telegram_id: 12345,
            spam_detected: 42,
            enable_ai_check: true,
            prompts_threshold: 0.5,
            custom_prompt_threshold: 0.5,
            cleanup_mentions: false,
            cleanup_emojis: true,
            cleanup_links: true,
            cleanup_emails: false,
            max_emoji_count: 10,
            allowed_link_domains: ['example.com'],
            allowed_mentions: [],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ],
        activeChat: null,
        isLoading: false,
      }));
      // Set active chat after a tick
      setTimeout(() => {
        chatsState.update((state) => ({
          ...state,
          activeChat: state.chats[0] || null,
        }));
      }, 100);
      return;
    }

    const token = getToken();
    if (token) {
      try {
        const user = await getMe();
        authState.update((state) => ({
          ...state,
          user,
          token,
          isAuthenticated: true,
          isLoading: false,
        }));

        // Fetch chats after successful auth
        const chats = await listChats();
        chatsState.update((state) => ({
          ...state,
          chats,
          activeChat: chats.length > 0 ? chats[0] : null,
          isLoading: false,
        }));

        // Show onboarding if no chats
        if (chats.length === 0) {
          uiState.update((state) => ({ ...state, showOnboarding: true }));
        }
      } catch {
        // Token invalid, stay logged out
      }
    }
  });

  function handleSummon() {
    uiState.update((state) => ({ ...state, showOnboarding: false }));
  }

  function handleAddGroup() {
    uiState.update((state) => ({ ...state, showOnboarding: true }));
  }

  function handleEmergencyStop() {
    if (confirm('Are you sure you want to stop SusBonk? Your group will be unprotected!')) {
      uiState.update((state) => ({ ...state, showOnboarding: true }));
    }
  }

  function handleTabChange(tab: TabType) {
    activeTab = tab;
    uiState.update((state) => ({ ...state, activeTab: tab }));
  }
</script>

<div class="size-full pb-24">
  {#if !$authState.isAuthenticated}
    <AuthDemo />
  {:else if $uiState.showOnboarding}
    <Onboarding onSummon={handleSummon} />
  {:else}
    <Dashboard onEmergencyStop={handleEmergencyStop} onAddGroup={handleAddGroup} {activeTab} />
  {/if}
</div>

{#if $authState.isAuthenticated}
  <BottomNav {activeTab} onTabChange={handleTabChange} />
{/if}
