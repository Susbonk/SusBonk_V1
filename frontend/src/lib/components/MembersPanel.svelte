<script lang="ts">
  import { onMount } from 'svelte';
  import { RefreshCw, Shield, ShieldOff, RotateCcw, ChevronDown } from 'lucide-svelte';
  import { chatsState } from '../stores/index.js';
  import { listUserStates, updateUserState, makeUntrusted } from '../api/userStates.js';
  import type { UserState } from '../types/api.js';

  let selectedChatId = $state<string | null>(null);
  let isDropdownOpen = $state(false);
  let userStates = $state<UserState[]>([]);
  let isLoading = $state(false);
  let isUpdating = $state<string | null>(null);

  // Get the selected chat object
  const selectedChat = $derived($chatsState.chats.find((c) => c.id === selectedChatId) || null);

  onMount(() => {
    // Default to active chat if available
    if ($chatsState.activeChat) {
      selectedChatId = $chatsState.activeChat.id;
      loadUserStates();
    }
  });

  function handleChatChange(chatId: string) {
    selectedChatId = chatId;
    isDropdownOpen = false;
    loadUserStates();
  }

  async function loadUserStates() {
    if (!selectedChatId) return;

    isLoading = true;
    try {
      userStates = await listUserStates(selectedChatId);
    } catch (err) {
      console.error('Failed to load user states:', err);
    } finally {
      isLoading = false;
    }
  }

  async function toggleTrust(user: UserState) {
    if (!selectedChatId) return;

    isUpdating = user.id;
    try {
      const updated = await updateUserState(selectedChatId, user.id, { trusted: !user.trusted });
      userStates = userStates.map((u) => (u.id === user.id ? updated : u));
    } catch (err) {
      console.error('Failed to update trust status:', err);
      alert('Failed to update trust status');
    } finally {
      isUpdating = null;
    }
  }

  async function resetUser(user: UserState) {
    if (!selectedChatId) return;

    if (
      !confirm(
        `Reset user ${user.external_user_id}? This will mark them as untrusted and reset their message count.`
      )
    ) {
      return;
    }

    isUpdating = user.id;
    try {
      const updated = await makeUntrusted(selectedChatId, user.id);
      userStates = userStates.map((u) => (u.id === user.id ? updated : u));
    } catch (err) {
      console.error('Failed to reset user:', err);
      alert('Failed to reset user');
    } finally {
      isUpdating = null;
    }
  }

  function formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  const trustedCount = $derived(userStates.filter((u) => u.trusted).length);
  const untrustedCount = $derived(userStates.filter((u) => !u.trusted).length);
</script>

<div class="space-y-4">
  <!-- Group Selector -->
  <div class="relative">
    <label class="block text-sm font-bold mb-2">Select Group</label>
    <button
      onclick={() => (isDropdownOpen = !isDropdownOpen)}
      class="w-full bg-white border-3 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] h-12 px-4 flex items-center justify-between font-bold"
    >
      <span>{selectedChat?.title || 'Select a group...'}</span>
      <ChevronDown class="w-5 h-5" />
    </button>

    {#if isDropdownOpen}
      <div
        class="absolute z-20 w-full mt-2 bg-white border-3 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] max-h-48 overflow-y-auto"
      >
        {#each $chatsState.chats as chat (chat.id)}
          <button
            onclick={() => handleChatChange(chat.id)}
            class="w-full px-4 py-3 text-left hover:bg-[#CCFF00] font-medium border-b border-black/20 last:border-b-0 transition-colors"
          >
            {chat.title || 'Unnamed Group'}
          </button>
        {/each}
        {#if $chatsState.chats.length === 0}
          <div class="px-4 py-3 text-gray-500 italic">No groups available</div>
        {/if}
      </div>
    {/if}
  </div>

  {#if selectedChat}
    <!-- Stats Bar -->
    <div class="flex gap-3">
      <div class="flex-1 p-3 border-3 border-black bg-green-100">
        <div class="text-2xl font-black text-green-700">{trustedCount}</div>
        <div class="text-xs font-bold text-green-600">Trusted</div>
      </div>
      <div class="flex-1 p-3 border-3 border-black bg-red-100">
        <div class="text-2xl font-black text-red-700">{untrustedCount}</div>
        <div class="text-xs font-bold text-red-600">Untrusted</div>
      </div>
      <button
        onclick={loadUserStates}
        class="p-3 border-3 border-black bg-gray-100 hover:bg-gray-200 transition-colors"
        disabled={isLoading}
      >
        <RefreshCw class="w-6 h-6 {isLoading ? 'animate-spin' : ''}" />
      </button>
    </div>

    <!-- Members List -->
    <div class="space-y-3">
      {#if isLoading}
        <div class="text-center py-8 text-gray-500">Loading members...</div>
      {:else if userStates.length === 0}
        <div class="text-center py-8 text-gray-500 italic border-2 border-dashed border-gray-300">
          No members yet. Members will appear when they join your group.
        </div>
      {:else}
        {#each userStates as user (user.id)}
          {@const isBeingUpdated = isUpdating === user.id}
          <div
            class="border-3 border-black p-4 bg-white hover:bg-[#fff9e6] transition-colors {isBeingUpdated
              ? 'opacity-50'
              : ''}"
          >
            <!-- User Info Row -->
            <div class="flex items-start justify-between mb-3">
              <div>
                <div class="font-bold text-lg">User {user.external_user_id}</div>
                <div class="flex gap-4 text-sm text-gray-600 mt-1">
                  <span>📊 {user.valid_messages} msgs</span>
                  <span>⏰ {formatDate(user.created_at)}</span>
                </div>
              </div>
              <!-- Trust Badge -->
              <div
                class="px-3 py-1 border-2 border-black font-bold text-sm {user.trusted
                  ? 'bg-green-400'
                  : 'bg-red-400'}"
              >
                {user.trusted ? '✓ Trusted' : '✗ Untrusted'}
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex gap-2">
              <button
                onclick={() => toggleTrust(user)}
                class="flex-1 flex items-center justify-center gap-2 py-2 border-3 border-black font-bold text-sm transition-all active:shadow-none active:translate-x-[1px] active:translate-y-[1px] {user.trusted
                  ? 'bg-red-100 hover:bg-red-200'
                  : 'bg-green-100 hover:bg-green-200'} shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                disabled={isBeingUpdated}
              >
                {#if user.trusted}
                  <ShieldOff class="w-4 h-4" />
                  Remove Trust
                {:else}
                  <Shield class="w-4 h-4" />
                  Make Trusted
                {/if}
              </button>
              <button
                onclick={() => resetUser(user)}
                class="px-4 py-2 border-3 border-black bg-gray-100 hover:bg-gray-200 font-bold text-sm transition-all active:shadow-none active:translate-x-[1px] active:translate-y-[1px] shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                disabled={isBeingUpdated}
                title="Reset user stats"
              >
                <RotateCcw class="w-4 h-4" />
              </button>
            </div>
          </div>
        {/each}
      {/if}
    </div>
  {:else}
    <div class="text-center py-8 text-gray-500 italic border-3 border-dashed border-gray-300">
      Please select a group to manage members.
    </div>
  {/if}
</div>
