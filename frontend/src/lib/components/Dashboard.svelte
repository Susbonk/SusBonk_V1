<script lang="ts">
  import { Zap, Heart, DollarSign, Briefcase, Pencil, User, ChevronDown, ChevronUp, Sparkles } from 'lucide-svelte';
  import DashboardHeader from './DashboardHeader.svelte';
  import ModerationToggle from './ModerationToggle.svelte';
  import WhitelistSection from './WhitelistSection.svelte';
  import RecentBonks from './RecentBonks.svelte';
  import CustomBlockSection from './CustomBlockSection.svelte';
  import { appState, togglePlayPause, changeGroup } from '../stores.js';
  import type { TabType } from '../types';

  interface Props {
    onEmergencyStop: () => void;
    onAddGroup: () => void;
    activeTab: TabType;
  }

  let { onEmergencyStop, onAddGroup, activeTab }: Props = $props();

  let builtInExpanded = $state(true);
  let customExpanded = $state(true);

  const customBlocks = [
    { id: "1", name: "Competitor Mentions", level: "Normal" },
    { id: "2", name: "No FUD", level: "Bonkers" }
  ];

  function handleGroupChange(value: string) {
    if (value === "add_new") {
      onAddGroup();
    } else {
      changeGroup(value);
    }
  }
</script>

<div class="min-h-screen bg-white">
  <div class="max-w-md mx-auto">
    
    {#if activeTab === 'dashboard'}
      <div class="p-4 space-y-4">
        <DashboardHeader 
          bonkCount={$appState.bonkCount}
          isPlaying={$appState.isPlaying}
          onTogglePlay={togglePlayPause}
          groups={$appState.groups}
          activeGroup={$appState.activeGroup}
          onGroupChange={handleGroupChange}
        />

        <div>
          <h2 class="mb-3 text-lg font-extrabold">Moderation Strength</h2>
          
          <!-- Built-in Rules -->
          <div class="mb-4">
            <button 
              onclick={() => builtInExpanded = !builtInExpanded}
              class="w-full flex items-center justify-between py-2 px-3 bg-gray-100 border-3 border-black mb-2 font-bold text-sm"
            >
              <span>Built-in Rules</span>
              {#if builtInExpanded}<ChevronUp class="w-5 h-5" />{:else}<ChevronDown class="w-5 h-5" />{/if}
            </button>
            
            {#if builtInExpanded}
              <div class="space-y-3">
                <ModerationToggle icon={Zap} category="Crypto Scams" initialLevel="Normal" />
                <ModerationToggle icon={Heart} category="Dating/Romance" initialLevel="Bonkers" />
                <ModerationToggle icon={DollarSign} category="Money Schemes" initialLevel="Normal" />
                <ModerationToggle icon={Briefcase} category="Job Offers" initialLevel="Chill" />
                <ModerationToggle icon={Pencil} category="Spam Links" initialLevel="Normal" />
                <ModerationToggle icon={User} category="Fake Accounts" initialLevel="Normal" />
              </div>
            {/if}
          </div>

          <!-- Custom Rules -->
          <div>
            <button 
              onclick={() => customExpanded = !customExpanded}
              class="w-full flex items-center justify-between py-2 px-3 bg-[#FF8A00]/20 border-3 border-black mb-2 font-bold text-sm"
            >
              <span>Custom Rules ({customBlocks.length})</span>
              {#if customExpanded}<ChevronUp class="w-5 h-5" />{:else}<ChevronDown class="w-5 h-5" />{/if}
            </button>
            
            {#if customExpanded}
              <div class="space-y-3">
                {#if customBlocks.length === 0}
                  <div class="text-center py-6 text-gray-500 italic border-2 border-dashed border-gray-300">
                    No custom rules. Add them in Settings.
                  </div>
                {:else}
                  {#each customBlocks as block (block.id)}
                    <ModerationToggle icon={Sparkles} category={block.name} initialLevel={block.level} />
                  {/each}
                {/if}
              </div>
            {/if}
          </div>
        </div>
      </div>
    {/if}

    {#if activeTab === 'logs'}
      <div class="p-4 space-y-4">
        <h2 class="text-2xl font-black">Logs for {$appState.activeGroup}</h2>
        <RecentBonks />
      </div>
    {/if}

    {#if activeTab === 'settings'}
      <div class="p-4 space-y-4">
        <h2 class="text-2xl font-black">Settings for {$appState.activeGroup}</h2>
        <WhitelistSection />
        <CustomBlockSection />
      </div>
    {/if}
  </div>
</div>
