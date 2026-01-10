<script lang="ts">
  import Onboarding from './lib/components/Onboarding.svelte';
  import Dashboard from './lib/components/Dashboard.svelte';
  import BottomNav from './lib/components/BottomNav.svelte';
  import { appState, summonBot, stopBot } from './lib/stores.js';
  import type { TabType } from './lib/types';
  import './app.css';

  let activeTab = $state<TabType>('dashboard');

  function handleSummon() {
    summonBot();
  }

  function handleAddGroup() {
    stopBot();
  }

  function handleEmergencyStop() {
    if (confirm("Are you sure you want to stop SusBonk? Your group will be unprotected!")) {
      stopBot();
    }
  }

  function handleTabChange(tab: TabType) {
    activeTab = tab;
    if (!$appState.isActive) {
      summonBot();
    }
  }
</script>

<div class="size-full pb-24">
  {#if !$appState.isActive}
    <Onboarding onSummon={handleSummon} />
  {:else}
    <Dashboard 
      onEmergencyStop={handleEmergencyStop}
      onAddGroup={handleAddGroup}
      {activeTab}
    />
  {/if}
</div>

<BottomNav {activeTab} onTabChange={handleTabChange} />
