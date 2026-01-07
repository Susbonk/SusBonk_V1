<script lang="ts">
  import Onboarding from './lib/components/Onboarding.svelte';
  import Dashboard from './lib/components/Dashboard.svelte';
  import { appState, summonBot, stopBot } from './lib/stores.js';
  import './app.css';

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
</script>

<div class="size-full" style="font-family: Poppins, sans-serif;">
  {#if !$appState.isActive}
    <Onboarding onSummon={handleSummon} />
  {:else}
    <Dashboard 
      onEmergencyStop={handleEmergencyStop}
      onAddGroup={handleAddGroup}
    />
  {/if}
</div>
