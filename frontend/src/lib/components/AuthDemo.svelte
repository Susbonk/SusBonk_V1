<script lang="ts">
  import Login from './Login.svelte';
  import Register from './Register.svelte';

  let currentView = $state<'login' | 'register'>('login');
</script>

{#if currentView === 'login'}
  <Login onSwitchToRegister={() => currentView = 'register'} />
{:else}
  <Register onSwitchToLogin={() => currentView = 'login'} />
{/if}
