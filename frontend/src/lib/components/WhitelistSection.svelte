<script lang="ts">
  import { Users, Trash2, X } from 'lucide-svelte';
  import { chatsState } from '../stores/index.js';
  import { listUserStates, updateUserState } from '../api/userStates.js';
  import type { UserState } from '../types/api.js';

  let isModalOpen = $state(false);
  let trustedUsers = $state<UserState[]>([]);
  let isLoading = $state(false);

  async function loadTrustedUsers() {
    const activeChat = $chatsState.activeChat;
    if (!activeChat) return;

    isLoading = true;
    try {
      const allUsers = await listUserStates(activeChat.id);
      trustedUsers = allUsers.filter(u => u.trusted);
    } catch (err) {
      console.error('Failed to load trusted users:', err);
    } finally {
      isLoading = false;
    }
  }

  async function removeUser(user: UserState) {
    const activeChat = $chatsState.activeChat;
    if (!activeChat) return;

    if (confirm(`Remove user ${user.external_user_id} from trusted members?`)) {
      try {
        await updateUserState(activeChat.id, user.id, { trusted: false });
        trustedUsers = trustedUsers.filter(u => u.id !== user.id);
      } catch (err) {
        console.error('Failed to remove user:', err);
        alert('Failed to remove user');
      }
    }
  }

  async function openModal() {
    isModalOpen = true;
    await loadTrustedUsers();
  }
</script>

<div class="card">
  <h3 class="mb-4 font-extrabold">Trusted Members</h3>

  <!-- Info Note -->
  <div class="mb-4 p-3 bg-gray-100 border-3 border-black">
    <p class="text-sm font-bold text-gray-700">Members appear here when they join your group</p>
  </div>

  <!-- View Trusted Members -->
  <button
    onclick={openModal}
    class="w-full px-4 py-2 border-3 border-black bg-gray-100 hover:bg-gray-200 transition-colors flex items-center justify-center gap-2 font-bold text-sm"
  >
    <Users class="w-4 h-4" />
    View Trusted Members ({trustedUsers.length})
  </button>
</div>

<!-- Modal -->
{#if isModalOpen}
  <div class="modal-backdrop" onclick={() => isModalOpen = false} onkeydown={(e) => e.key === 'Escape' && (isModalOpen = false)} role="button" tabindex="0">
    <div class="modal-content max-h-[80vh] flex flex-col" onclick={(e) => e.stopPropagation()} role="dialog" tabindex="-1">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-extrabold">Trusted Members</h2>
        <button onclick={() => isModalOpen = false} class="p-1 hover:bg-gray-100"><X class="w-6 h-6" /></button>
      </div>
      
      <div class="flex-1 overflow-y-auto space-y-2">
        {#if isLoading}
          <div class="text-center py-8 text-gray-500">Loading...</div>
        {:else if trustedUsers.length === 0}
          <div class="text-center py-8 text-gray-500 italic">No trusted members yet. Members will appear here when they join your group.</div>
        {:else}
          {#each trustedUsers as user (user.id)}
            <div class="flex items-center justify-between px-4 py-3 border-3 border-black bg-gray-50 hover:bg-[#fff9e6] transition-colors">
              <span class="font-semibold">User {user.external_user_id}</span>
              <button onclick={() => removeUser(user)} class="text-gray-400 hover:text-red-600 transition-colors p-1">
                <Trash2 class="w-5 h-5" />
              </button>
            </div>
          {/each}
        {/if}
      </div>
      
      <button onclick={() => isModalOpen = false} class="mt-4 btn btn-primary w-full py-3 font-black">DONE</button>
    </div>
  </div>
{/if}
