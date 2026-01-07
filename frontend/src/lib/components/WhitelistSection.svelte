<script lang="ts">
  import { Plus } from 'lucide-svelte';

  let inputValue = $state("");
  let trustAdmins = $state(true);
  let trustVeterans = $state(true);
  let allowBots = $state(false);
</script>

<div class="bg-white border-[4px] border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] p-4">
  <h3 class="mb-4" style="font-family: Poppins, sans-serif; font-weight: 800; font-size: 16px;">
    Whitelist & Safety
  </h3>

  <!-- Quick Add -->
  <div class="mb-4 flex gap-2">
    <input
      type="text"
      bind:value={inputValue}
      placeholder="@username or user ID"
      class="flex-1 px-3 py-2 border-[3px] border-black focus:outline-none focus:ring-2 focus:ring-[#CCFF00]"
      style="font-family: Poppins, sans-serif; font-weight: 600;"
    />
    <button
      class="bg-[#FF8A00] border-[3px] border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] px-4 py-2 transition-all active:shadow-none active:translate-x-[4px] active:translate-y-[4px]"
      style="font-family: Poppins, sans-serif; font-weight: 700; transform: rotate(-2deg);"
    >
      <Plus class="w-5 h-5" />
    </button>
  </div>

  <!-- Toggle Pills -->
  <div class="space-y-2">
    <button
      onclick={() => trustAdmins = !trustAdmins}
      class="w-full px-4 py-3 border-[3px] border-black transition-all text-left flex items-center justify-between {trustAdmins ? 'bg-[#CCFF00] shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]' : 'bg-white hover:bg-gray-50'}"
      style="font-family: Poppins, sans-serif; font-weight: 700; font-size: 14px;"
    >
      Trust Group Admins
      <div class="w-5 h-5 border-[2px] border-black flex items-center justify-center {trustAdmins ? 'bg-black' : 'bg-white'}">
        {#if trustAdmins}
          <div class="w-2 h-2 bg-[#CCFF00]"></div>
        {/if}
      </div>
    </button>
    
    <button
      onclick={() => trustVeterans = !trustVeterans}
      class="w-full px-4 py-3 border-[3px] border-black transition-all text-left flex items-center justify-between {trustVeterans ? 'bg-[#CCFF00] shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]' : 'bg-white hover:bg-gray-50'}"
      style="font-family: Poppins, sans-serif; font-weight: 700; font-size: 14px;"
    >
      Trust 30-Day Veterans
      <div class="w-5 h-5 border-[2px] border-black flex items-center justify-center {trustVeterans ? 'bg-black' : 'bg-white'}">
        {#if trustVeterans}
          <div class="w-2 h-2 bg-[#CCFF00]"></div>
        {/if}
      </div>
    </button>
    
    <button
      onclick={() => allowBots = !allowBots}
      class="w-full px-4 py-3 border-[3px] border-black transition-all text-left flex items-center justify-between {allowBots ? 'bg-[#CCFF00] shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]' : 'bg-white hover:bg-gray-50'}"
      style="font-family: Poppins, sans-serif; font-weight: 700; font-size: 14px;"
    >
      Allow Verified Bots
      <div class="w-5 h-5 border-[2px] border-black flex items-center justify-center {allowBots ? 'bg-black' : 'bg-white'}">
        {#if allowBots}
          <div class="w-2 h-2 bg-[#CCFF00]"></div>
        {/if}
      </div>
    </button>
  </div>
</div>
