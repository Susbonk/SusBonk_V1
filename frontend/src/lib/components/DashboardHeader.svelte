<script lang="ts">
  import { Hammer, Play, Pause, ChevronDown, Plus } from 'lucide-svelte';
  import type { ComponentType } from 'svelte';

  interface Props {
    bonkCount: number;
    isPlaying: boolean;
    onTogglePlay: () => void;
    groups: string[];
    activeGroup: string;
    onGroupChange: (group: string) => void;
  }

  let { bonkCount, isPlaying, onTogglePlay, groups, activeGroup, onGroupChange }: Props = $props();
  let isOpen = $state(false);
</script>

<div class="space-y-4">
  <!-- Group Selection -->
  <div class="w-full relative">
    <button
      onclick={() => isOpen = !isOpen}
      class="w-full bg-white border-[3px] border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] h-12 px-4 flex items-center justify-between focus:ring-0 focus:ring-offset-0"
      style="font-family: Poppins, sans-serif; font-weight: 700; font-size: 16px;"
    >
      <span>{activeGroup}</span>
      <ChevronDown class="w-5 h-5" />
    </button>
    
    {#if isOpen}
      <div class="absolute top-full left-0 right-0 mt-1 bg-white border-[3px] border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] z-50" style="font-family: Poppins, sans-serif; font-weight: 600;">
        {#each groups as group}
          <button
            onclick={() => { onGroupChange(group); isOpen = false; }}
            class="w-full px-4 py-3 text-left hover:bg-[#CCFF00] transition-colors"
          >
            {group}
          </button>
        {/each}
        <button
          onclick={() => { onGroupChange('add_new'); isOpen = false; }}
          class="w-full px-4 py-3 text-left hover:bg-[#FF8A00] transition-colors border-t-[2px] border-black flex items-center gap-2 font-bold"
        >
          <Plus class="w-4 h-4" />
          Add New Group
        </button>
      </div>
    {/if}
  </div>

  <!-- Status Indicator & Play/Pause -->
  <div class="bg-white border-[4px] border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] p-4 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <div class="relative">
        <div class="w-4 h-4 rounded-full border-[2px] border-black {isPlaying ? 'bg-green-500 animate-pulse' : 'bg-red-500'}"></div>
        {#if isPlaying}
          <div class="absolute inset-0 w-4 h-4 bg-green-500 rounded-full animate-ping opacity-75"></div>
        {/if}
      </div>
      <span style="font-family: Poppins, sans-serif; font-weight: 800; font-size: 16px;">
        {isPlaying ? 'SUSBONK IS WATCHING' : 'SUSBONK IS SLEEPING'}
      </span>
    </div>
    
    <button
      onclick={onTogglePlay}
      class="border-[3px] border-black p-2 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all active:shadow-none active:translate-x-[2px] active:translate-y-[2px] {isPlaying ? 'bg-[#FF8A00] hover:bg-[#ff9f2e]' : 'bg-[#CCFF00] hover:bg-[#d9ff33]'}"
    >
      {#if isPlaying}
        <Pause class="w-6 h-6 fill-black" />
      {:else}
        <Play class="w-6 h-6 fill-black" />
      {/if}
    </button>
  </div>

  <!-- Bonk Counter -->
  <div class="bg-white border-[4px] border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] p-8 text-center relative overflow-hidden group">
    <div class="absolute top-0 right-0 p-2 opacity-10 group-hover:opacity-20 transition-opacity">
       <Hammer class="w-24 h-24 -rotate-12" />
    </div>
    
    <div class="flex items-center justify-center gap-3 mb-2 relative z-10">
      <Hammer class="w-12 h-12 {isPlaying ? 'animate-bounce' : ''}" />
      <div style="font-family: Poppins, sans-serif; font-weight: 900; font-size: 56px; line-height: 1;">
        {bonkCount.toLocaleString()}
      </div>
    </div>
    <div style="font-family: Poppins, sans-serif; font-weight: 700; font-size: 14px;" class="text-gray-600 relative z-10">
      Sus Messages Bonked
    </div>
  </div>
</div>
