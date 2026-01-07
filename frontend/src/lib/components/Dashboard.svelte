<script lang="ts">
  import { Zap, Heart, DollarSign, Briefcase, Pencil, User } from 'lucide-svelte';
  import DashboardHeader from './DashboardHeader.svelte';
  import ModerationToggle from './ModerationToggle.svelte';
  import WhitelistSection from './WhitelistSection.svelte';
  import RecentBonks from './RecentBonks.svelte';
  import BottomNav from './BottomNav.svelte';
  import CustomBlockSection from './CustomBlockSection.svelte';
  import { appState, togglePlayPause, changeGroup } from '../stores.js';

  interface Props {
    onEmergencyStop: () => void;
    onAddGroup: () => void;
  }

  let { onEmergencyStop, onAddGroup }: Props = $props();

  type TabType = 'dashboard' | 'logs' | 'settings';
  let activeTab = $state<TabType>('dashboard');

  function handleGroupChange(value: string) {
    if (value === "add_new") {
      onAddGroup();
    } else {
      changeGroup(value);
    }
  }

  function handleTabChange(tab: TabType) {
    activeTab = tab;
  }

  function handleTogglePlay() {
    togglePlayPause();
  }
</script>

<div class="min-h-screen bg-white pb-24">
  <div class="max-w-md mx-auto">
    
    <!-- DASHBOARD TAB -->
    {#if activeTab === 'dashboard'}
      <div class="p-4 space-y-4 animate-in fade-in duration-300">
        <!-- Header Section -->
        <DashboardHeader 
          bonkCount={$appState.bonkCount}
          isPlaying={$appState.isPlaying}
          onTogglePlay={handleTogglePlay}
          groups={$appState.groups}
          activeGroup={$appState.activeGroup}
          onGroupChange={handleGroupChange}
        />

        <!-- Moderation Toggles Section -->
        <div>
          <h2 class="mb-3" style="font-family: Poppins, sans-serif; font-weight: 800; font-size: 18px;">
            Moderation Strength
          </h2>
          <div class="space-y-3">
            <ModerationToggle icon={Zap} category="Crypto Scams" initialLevel="Normal" />
            <ModerationToggle icon={Heart} category="Dating/Romance" initialLevel="Bonkers" />
            <ModerationToggle icon={DollarSign} category="Money Schemes" initialLevel="Normal" />
            <ModerationToggle icon={Briefcase} category="Job Offers" initialLevel="Chill" />
            <ModerationToggle icon={Pencil} category="Spam Links" initialLevel="Normal" />
            <ModerationToggle icon={User} category="Fake Accounts" initialLevel="Normal" />
          </div>
        </div>


      </div>
    {/if}

    <!-- LOGS TAB -->
    {#if activeTab === 'logs'}
      <div class="p-4 space-y-4 animate-in fade-in duration-300">
        <h2 class="text-2xl mb-4" style="font-family: Poppins, sans-serif; font-weight: 900;">
          Activity Logs
        </h2>
        <!-- Recent Bonks -->
        <RecentBonks />
      </div>
    {/if}

    <!-- SETTINGS TAB -->
    {#if activeTab === 'settings'}
      <div class="p-4 space-y-4 animate-in fade-in duration-300">
        <h2 class="text-2xl mb-4" style="font-family: Poppins, sans-serif; font-weight: 900;">
          Settings
        </h2>
        
        <!-- Whitelist Section -->
        <WhitelistSection />

        <!-- Custom Blocks -->
        <CustomBlockSection />
      </div>
    {/if}
  </div>

  <!-- Bottom Navigation -->
  <BottomNav {activeTab} onTabChange={handleTabChange} />
</div>
