<script lang="ts">
  import { Plus, X, Users, Trash2 } from 'lucide-svelte';

  interface WhitelistedUser {
    id: string;
    username: string;
  }

  let inputValue = $state("");
  let trustAdmins = $state(true);
  let trustVeterans = $state(true);
  let allowBots = $state(false);
  let isModalOpen = $state(false);
  let whitelistedUsers = $state<WhitelistedUser[]>([
    { id: "1", username: "@cryptoking" },
    { id: "2", username: "@moongirl" },
    { id: "3", username: "123456789" }
  ]);

  function addUser() {
    if (!inputValue.trim()) return;
    whitelistedUsers = [...whitelistedUsers, { id: Date.now().toString(), username: inputValue.trim() }];
    inputValue = "";
  }

  function removeUser(id: string, username: string) {
    if (confirm(`Remove ${username} from whitelist?`)) {
      whitelistedUsers = whitelistedUsers.filter(u => u.id !== id);
    }
  }

  const toggleOptions = [
    { key: 'trustAdmins', label: 'Trust Group Admins' },
    { key: 'trustVeterans', label: 'Trust 30-Day Veterans' },
    { key: 'allowBots', label: 'Allow Verified Bots' },
  ];

  function getToggleValue(key: string): boolean {
    if (key === 'trustAdmins') return trustAdmins;
    if (key === 'trustVeterans') return trustVeterans;
    return allowBots;
  }

  function toggleValue(key: string) {
    if (key === 'trustAdmins') trustAdmins = !trustAdmins;
    else if (key === 'trustVeterans') trustVeterans = !trustVeterans;
    else allowBots = !allowBots;
  }
</script>

<div class="card">
  <h3 class="mb-4 font-extrabold">Whitelist & Safety</h3>

  <!-- Quick Add -->
  <div class="mb-3 flex gap-2">
    <input
      type="text"
      bind:value={inputValue}
      placeholder="@username or user ID"
      class="flex-1 px-3 py-2 border-3 border-black focus:outline-none focus:ring-2 focus:ring-[#CCFF00] font-semibold"
      onkeydown={(e) => e.key === 'Enter' && addUser()}
    />
    <button onclick={addUser} class="btn btn-secondary px-4 py-2 -rotate-2">
      <Plus class="w-5 h-5" />
    </button>
  </div>

  <!-- View Whitelist -->
  <button
    onclick={() => isModalOpen = true}
    class="w-full mb-4 px-4 py-2 border-3 border-black bg-gray-100 hover:bg-gray-200 transition-colors flex items-center justify-center gap-2 font-bold text-sm"
  >
    <Users class="w-4 h-4" />
    View Whitelisted ({whitelistedUsers.length})
  </button>

  <!-- Toggle Options -->
  <div class="space-y-2">
    {#each toggleOptions as opt}
      {@const isActive = getToggleValue(opt.key)}
      <button
        onclick={() => toggleValue(opt.key)}
        class="w-full px-4 py-3 border-3 border-black transition-all text-left flex items-center justify-between font-bold text-sm {isActive ? 'bg-[#CCFF00] shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]' : 'bg-white hover:bg-gray-50'}"
      >
        {opt.label}
        <div class="w-5 h-5 border-2 border-black flex items-center justify-center {isActive ? 'bg-black' : 'bg-white'}">
          {#if isActive}<div class="w-2 h-2 bg-[#CCFF00]"></div>{/if}
        </div>
      </button>
    {/each}
  </div>
</div>

<!-- Modal -->
{#if isModalOpen}
  <div class="modal-backdrop" onclick={() => isModalOpen = false} onkeydown={(e) => e.key === 'Escape' && (isModalOpen = false)} role="button" tabindex="0">
    <div class="modal-content max-h-[80vh] flex flex-col" onclick={(e) => e.stopPropagation()} role="dialog" tabindex="-1">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-extrabold">Whitelisted Users</h2>
        <button onclick={() => isModalOpen = false} class="p-1 hover:bg-gray-100"><X class="w-6 h-6" /></button>
      </div>
      
      <div class="flex-1 overflow-y-auto space-y-2">
        {#if whitelistedUsers.length === 0}
          <div class="text-center py-8 text-gray-500 italic">No whitelisted users yet.</div>
        {:else}
          {#each whitelistedUsers as user (user.id)}
            <div class="flex items-center justify-between px-4 py-3 border-3 border-black bg-gray-50 hover:bg-[#fff9e6] transition-colors">
              <span class="font-semibold">{user.username}</span>
              <button onclick={() => removeUser(user.id, user.username)} class="text-gray-400 hover:text-red-600 transition-colors p-1">
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
