<script lang="ts">
  import { LayoutGrid, Scroll, Settings } from 'lucide-svelte';

  type TabType = 'dashboard' | 'logs' | 'settings';

  interface Props {
    activeTab: TabType;
    onTabChange: (tab: TabType) => void;
  }

  let { activeTab, onTabChange }: Props = $props();

  const tabs = [
    { id: 'dashboard' as const, label: 'Dashboard', icon: LayoutGrid },
    { id: 'logs' as const, label: 'Logs', icon: Scroll },
    { id: 'settings' as const, label: 'Settings', icon: Settings },
  ];
</script>

<div class="fixed bottom-0 left-0 right-0 border-t-[4px] border-black bg-white z-50 pb-safe">
  <div class="flex items-stretch h-20">
    {#each tabs as tab, index}
      {@const isActive = activeTab === tab.id}
      {@const Icon = tab.icon}
      
      <button
        onclick={() => onTabChange(tab.id)}
        class="flex-1 flex flex-col items-center justify-center gap-1 transition-colors relative {isActive ? 'bg-[#CCFF00]' : 'bg-white hover:bg-gray-50'} {index !== tabs.length - 1 ? 'border-r-[4px] border-black' : ''}"
      >
        <Icon class="w-6 h-6 {isActive ? 'stroke-[2.5px]' : 'stroke-2'}" />
        <span 
          style="font-family: Poppins, sans-serif; font-weight: {isActive ? 800 : 600}; font-size: 12px;"
        >
          {tab.label}
        </span>
        {#if isActive}
          <div class="absolute top-0 left-0 right-0 h-[4px] bg-black"></div>
        {/if}
      </button>
    {/each}
  </div>
</div>
