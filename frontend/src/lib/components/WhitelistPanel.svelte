<script lang="ts">
  import { onMount } from 'svelte';
  import {
    ChevronDown,
    Users,
    AtSign,
    Link,
    Plus,
    X,
    Search,
    Shield,
    ShieldOff,
  } from 'lucide-svelte';
  import { chatsState } from '../stores/index.js';
  import { updateChat } from '../api/chats.js';
  import { listUserStates, updateUserState } from '../api/userStates.js';
  import type { Chat, UserState } from '../types/api.js';

  // State
  let selectedChatId = $state<string | null>(null);
  let isDropdownOpen = $state(false);
  let isSaving = $state(false);

  // Whitelist sections
  let activeSection = $state<'members' | 'mentions' | 'urls'>('members');

  // Members state
  let allMembers = $state<UserState[]>([]);
  let trustedMembers = $state<UserState[]>([]);
  let isLoadingMembers = $state(false);
  let showMemberModal = $state(false);
  let memberSearchQuery = $state('');

  // Whitelists from selected chat
  let allowedMentions = $state<string[]>([]);
  let allowedUrls = $state<string[]>([]);
  let newMention = $state('');
  let newUrl = $state('');

  // Load initial data
  onMount(() => {
    if ($chatsState.activeChat) {
      selectedChatId = $chatsState.activeChat.id;
      loadWhitelists($chatsState.activeChat);
    }
  });

  // Get the selected chat object
  const selectedChat = $derived($chatsState.chats.find((c) => c.id === selectedChatId) || null);

  // Filter untrusted members for adding
  const untrustedMembers = $derived(
    allMembers.filter(
      (m) =>
        !m.trusted &&
        (memberSearchQuery === '' || String(m.external_user_id).includes(memberSearchQuery))
    )
  );

  function handleChatChange(chatId: string) {
    selectedChatId = chatId;
    isDropdownOpen = false;
    const chat = $chatsState.chats.find((c) => c.id === chatId);
    if (chat) {
      loadWhitelists(chat);
    }
  }

  function loadWhitelists(chat: Chat) {
    // Load allowed mentions and URLs from chat
    allowedMentions = chat.allowed_mentions || [];
    allowedUrls = chat.allowed_link_domains || [];
    // Load members
    loadMembers();
  }

  async function loadMembers() {
    if (!selectedChatId) return;

    isLoadingMembers = true;
    try {
      const members = await listUserStates(selectedChatId);
      allMembers = members;
      trustedMembers = members.filter((m) => m.trusted);
    } catch (err) {
      console.error('Failed to load members:', err);
    } finally {
      isLoadingMembers = false;
    }
  }

  async function addTrustedMember(member: UserState) {
    if (!selectedChatId) return;

    try {
      await updateUserState(selectedChatId, member.id, { trusted: true });
      // Update local state
      allMembers = allMembers.map((m) => (m.id === member.id ? { ...m, trusted: true } : m));
      trustedMembers = allMembers.filter((m) => m.trusted);
    } catch (err) {
      console.error('Failed to trust member:', err);
      alert('Failed to add member to whitelist');
    }
  }

  async function removeTrustedMember(member: UserState) {
    if (!selectedChatId) return;

    try {
      await updateUserState(selectedChatId, member.id, { trusted: false });
      // Update local state
      allMembers = allMembers.map((m) => (m.id === member.id ? { ...m, trusted: false } : m));
      trustedMembers = allMembers.filter((m) => m.trusted);
    } catch (err) {
      console.error('Failed to untrust member:', err);
      alert('Failed to remove member from whitelist');
    }
  }

  async function saveMentions() {
    if (!selectedChatId) return;

    isSaving = true;
    try {
      await updateChat(selectedChatId, { allowed_mentions: allowedMentions });
      // Update local chats state
      chatsState.update((state) => ({
        ...state,
        chats: state.chats.map((c) =>
          c.id === selectedChatId ? { ...c, allowed_mentions: allowedMentions } : c
        ),
      }));
    } catch (err) {
      console.error('Failed to save mentions:', err);
      alert('Failed to save allowed mentions');
    } finally {
      isSaving = false;
    }
  }

  async function saveUrls() {
    if (!selectedChatId) return;

    isSaving = true;
    try {
      await updateChat(selectedChatId, { allowed_link_domains: allowedUrls });
      // Update local chats state
      chatsState.update((state) => ({
        ...state,
        chats: state.chats.map((c) =>
          c.id === selectedChatId ? { ...c, allowed_link_domains: allowedUrls } : c
        ),
      }));
    } catch (err) {
      console.error('Failed to save URLs:', err);
      alert('Failed to save allowed URLs');
    } finally {
      isSaving = false;
    }
  }

  function addMention() {
    const mention = newMention.trim().replace('@', '');
    if (mention && !allowedMentions.includes(mention)) {
      allowedMentions = [...allowedMentions, mention];
      newMention = '';
      saveMentions();
    }
  }

  function removeMention(mention: string) {
    allowedMentions = allowedMentions.filter((m) => m !== mention);
    saveMentions();
  }

  function addUrl() {
    const url = newUrl
      .trim()
      .toLowerCase()
      .replace(/^https?:\/\//, '')
      .replace(/\/$/, '');
    if (url && !allowedUrls.includes(url)) {
      allowedUrls = [...allowedUrls, url];
      newUrl = '';
      saveUrls();
    }
  }

  function removeUrl(url: string) {
    allowedUrls = allowedUrls.filter((u) => u !== url);
    saveUrls();
  }
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
    <!-- Section Tabs -->
    <div class="flex border-3 border-black overflow-hidden">
      <button
        onclick={() => (activeSection = 'members')}
        class="flex-1 py-3 px-2 font-bold text-xs flex items-center justify-center gap-1 transition-colors {activeSection ===
        'members'
          ? 'bg-[#FF8A00]'
          : 'bg-white hover:bg-gray-50'}"
      >
        <Users class="w-4 h-4" />
        Members
      </button>
      <button
        onclick={() => (activeSection = 'mentions')}
        class="flex-1 py-3 px-2 font-bold text-xs flex items-center justify-center gap-1 border-l-2 border-black transition-colors {activeSection ===
        'mentions'
          ? 'bg-[#FF8A00]'
          : 'bg-white hover:bg-gray-50'}"
      >
        <AtSign class="w-4 h-4" />
        Mentions
      </button>
      <button
        onclick={() => (activeSection = 'urls')}
        class="flex-1 py-3 px-2 font-bold text-xs flex items-center justify-center gap-1 border-l-2 border-black transition-colors {activeSection ===
        'urls'
          ? 'bg-[#FF8A00]'
          : 'bg-white hover:bg-gray-50'}"
      >
        <Link class="w-4 h-4" />
        URLs
      </button>
    </div>

    <!-- Content Area -->
    <div class="border-3 border-black p-4 bg-white">
      {#if activeSection === 'members'}
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="font-black">Trusted Members ({trustedMembers.length})</h3>
            <button
              onclick={() => {
                memberSearchQuery = '';
                showMemberModal = true;
              }}
              class="flex items-center gap-2 px-4 py-2 bg-[#CCFF00] border-3 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] font-bold text-sm hover:bg-[#d4ff33] transition-colors active:shadow-none active:translate-x-[3px] active:translate-y-[3px]"
            >
              <Plus class="w-4 h-4" />
              Add
            </button>
          </div>

          {#if isLoadingMembers}
            <div class="text-center py-6 text-gray-500">Loading members...</div>
          {:else if trustedMembers.length === 0}
            <div
              class="text-center py-6 text-gray-500 italic border-2 border-dashed border-gray-300"
            >
              No trusted members yet. Add members to whitelist them.
            </div>
          {:else}
            <div class="space-y-2 max-h-64 overflow-y-auto">
              {#each trustedMembers as member (member.id)}
                <div
                  class="flex items-center justify-between p-3 bg-green-50 border-2 border-green-300"
                >
                  <div class="flex items-center gap-2">
                    <Shield class="w-5 h-5 text-green-600" />
                    <span class="font-bold">User {member.external_user_id}</span>
                    <span class="text-sm text-gray-500">({member.valid_messages} msgs)</span>
                  </div>
                  <button
                    onclick={() => removeTrustedMember(member)}
                    class="p-2 hover:bg-red-100 transition-colors"
                    title="Remove from whitelist"
                  >
                    <X class="w-4 h-4 text-red-600" />
                  </button>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {:else if activeSection === 'mentions'}
        <div class="space-y-4">
          <h3 class="font-black">Allowed Mentions ({allowedMentions.length})</h3>
          <p class="text-sm text-gray-600">
            Usernames that are allowed to be mentioned without triggering cleanup.
          </p>

          <!-- Add Mention Input -->
          <div class="flex gap-2">
            <div class="flex-1 relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">@</span>
              <input
                type="text"
                bind:value={newMention}
                onkeydown={(e) => e.key === 'Enter' && addMention()}
                placeholder="username"
                class="w-full pl-8 pr-4 py-3 border-3 border-black font-medium"
              />
            </div>
            <button
              onclick={addMention}
              disabled={!newMention.trim()}
              class="px-4 py-3 bg-[#CCFF00] border-3 border-black font-bold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Plus class="w-5 h-5" />
            </button>
          </div>

          <!-- Mentions List -->
          {#if allowedMentions.length === 0}
            <div
              class="text-center py-6 text-gray-500 italic border-2 border-dashed border-gray-300"
            >
              No allowed mentions. Add usernames to whitelist them.
            </div>
          {:else}
            <div class="flex flex-wrap gap-2">
              {#each allowedMentions as mention}
                <div
                  class="flex items-center gap-2 px-3 py-2 bg-blue-50 border-2 border-blue-300 font-medium"
                >
                  <span>@{mention}</span>
                  <button
                    onclick={() => removeMention(mention)}
                    class="hover:text-red-600 transition-colors"
                  >
                    <X class="w-4 h-4" />
                  </button>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {:else if activeSection === 'urls'}
        <div class="space-y-4">
          <h3 class="font-black">Allowed URLs ({allowedUrls.length})</h3>
          <p class="text-sm text-gray-600">
            Domains that are allowed without triggering link cleanup.
          </p>

          <!-- Add URL Input -->
          <div class="flex gap-2">
            <input
              type="text"
              bind:value={newUrl}
              onkeydown={(e) => e.key === 'Enter' && addUrl()}
              placeholder="example.com"
              class="flex-1 px-4 py-3 border-3 border-black font-medium"
            />
            <button
              onclick={addUrl}
              disabled={!newUrl.trim()}
              class="px-4 py-3 bg-[#CCFF00] border-3 border-black font-bold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Plus class="w-5 h-5" />
            </button>
          </div>

          <!-- URLs List -->
          {#if allowedUrls.length === 0}
            <div
              class="text-center py-6 text-gray-500 italic border-2 border-dashed border-gray-300"
            >
              No allowed URLs. Add domains to whitelist them.
            </div>
          {:else}
            <div class="space-y-2">
              {#each allowedUrls as url}
                <div
                  class="flex items-center justify-between p-3 bg-purple-50 border-2 border-purple-300"
                >
                  <div class="flex items-center gap-2">
                    <Link class="w-4 h-4 text-purple-600" />
                    <span class="font-medium">{url}</span>
                  </div>
                  <button
                    onclick={() => removeUrl(url)}
                    class="p-2 hover:bg-red-100 transition-colors"
                  >
                    <X class="w-4 h-4 text-red-600" />
                  </button>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {/if}
    </div>
  {:else}
    <div class="text-center py-8 text-gray-500 italic border-3 border-dashed border-gray-300">
      Please select a group to manage whitelists.
    </div>
  {/if}
</div>

<!-- Member Selection Modal -->
{#if showMemberModal}
  <div class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
    <div
      class="bg-white border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] w-full max-w-md max-h-[80vh] flex flex-col"
    >
      <!-- Modal Header -->
      <div class="flex items-center justify-between p-4 border-b-3 border-black bg-[#CCFF00]">
        <h3 class="font-black text-lg">Add Trusted Member</h3>
        <button
          onclick={() => (showMemberModal = false)}
          class="p-2 hover:bg-black/10 transition-colors"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Search -->
      <div class="p-4 border-b-2 border-black/20">
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            bind:value={memberSearchQuery}
            placeholder="Search by user ID..."
            class="w-full pl-10 pr-4 py-3 border-3 border-black font-medium"
          />
        </div>
      </div>

      <!-- Members List -->
      <div class="flex-1 overflow-y-auto p-4">
        {#if untrustedMembers.length === 0}
          <div class="text-center py-6 text-gray-500 italic">
            {allMembers.length === trustedMembers.length
              ? 'All members are already trusted!'
              : 'No members match your search.'}
          </div>
        {:else}
          <div class="space-y-2">
            {#each untrustedMembers as member (member.id)}
              <button
                onclick={() => {
                  addTrustedMember(member);
                  showMemberModal = false;
                }}
                class="w-full flex items-center justify-between p-3 bg-gray-50 border-2 border-gray-200 hover:bg-green-50 hover:border-green-300 transition-colors"
              >
                <div class="flex items-center gap-2">
                  <ShieldOff class="w-5 h-5 text-gray-400" />
                  <span class="font-bold">User {member.external_user_id}</span>
                  <span class="text-sm text-gray-500">({member.valid_messages} msgs)</span>
                </div>
                <Plus class="w-5 h-5 text-green-600" />
              </button>
            {/each}
          </div>
        {/if}
      </div>

      <!-- Footer -->
      <div class="p-4 border-t-3 border-black bg-gray-50">
        <button
          onclick={() => (showMemberModal = false)}
          class="w-full py-3 border-3 border-black font-bold bg-white hover:bg-gray-100 transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
{/if}
