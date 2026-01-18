<script lang="ts">
  import { onMount } from 'svelte';
  import { ExternalLink, MessageCircle, CheckCircle, AlertCircle } from 'lucide-svelte';
  import { api } from '../api/client.js';
  
  let connectionStatus = $state<'checking' | 'connected' | 'pending' | 'error'>('checking');
  let botLink = $state('');
  let errorMessage = $state('');

  onMount(async () => {
    await checkTelegramConnection();
  });

  async function checkTelegramConnection() {
    connectionStatus = 'checking';
    try {
      const data = await api.get('/auth/me/connect_telegram');
      if (data.status === 'already_connected') {
        connectionStatus = 'connected';
      } else {
        connectionStatus = 'pending';
        botLink = data.bot_link || 'https://t.me/SusBonkBot';
      }
    } catch (err) {
      console.error('Failed to check Telegram connection:', err);
      connectionStatus = 'error';
      errorMessage = 'Failed to check connection status';
    }
  }

  function openTelegramBot() {
    if (botLink) {
      window.open(botLink, '_blank');
    }
  }
</script>

<div class="card">
  <div class="flex items-center gap-2 mb-4">
    <MessageCircle class="w-5 h-5 text-blue-500" />
    <h3 class="font-extrabold">Telegram Connection</h3>
  </div>

  <div class="space-y-4">
    {#if connectionStatus === 'checking'}
      <div class="flex items-center gap-3 p-4 bg-gray-50 border-2 border-gray-300">
        <div class="animate-spin w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full"></div>
        <span class="font-medium">Checking connection status...</span>
      </div>
    
    {:else if connectionStatus === 'connected'}
      <div class="flex items-center gap-3 p-4 bg-green-50 border-2 border-green-300">
        <CheckCircle class="w-5 h-5 text-green-600" />
        <div>
          <div class="font-bold text-green-800">Connected to Telegram</div>
          <div class="text-sm text-green-600">Your account is linked to SusBonk bot</div>
        </div>
      </div>
    
    {:else if connectionStatus === 'pending'}
      <div class="space-y-4">
        <div class="flex items-center gap-3 p-4 bg-yellow-50 border-2 border-yellow-300">
          <AlertCircle class="w-5 h-5 text-yellow-600" />
          <div>
            <div class="font-bold text-yellow-800">Connection Pending</div>
            <div class="text-sm text-yellow-600">Click the button below to connect with SusBonk bot</div>
          </div>
        </div>

        <div class="space-y-3">
          <h4 class="font-bold">How to connect:</h4>
          <ol class="list-decimal list-inside space-y-2 text-sm">
            <li>Click "Connect to Telegram" button below</li>
            <li>Start a conversation with @SusBonkBot</li>
            <li>Send the command <code class="bg-gray-100 px-1 rounded">/start</code></li>
            <li>Your account will be automatically linked</li>
          </ol>
        </div>

        <button
          onclick={openTelegramBot}
          class="bg-blue-500 hover:bg-blue-600 text-white border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] px-4 py-2 font-bold flex items-center gap-2 transition-all active:shadow-none active:translate-x-[2px] active:translate-y-[2px]"
        >
          <ExternalLink class="w-4 h-4" />
          Connect to Telegram
        </button>

        <button
          onclick={checkTelegramConnection}
          class="bg-gray-200 hover:bg-gray-300 border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] px-4 py-2 font-bold transition-all active:shadow-none active:translate-x-[2px] active:translate-y-[2px]"
        >
          Check Connection Status
        </button>
      </div>
    
    {:else if connectionStatus === 'error'}
      <div class="flex items-center gap-3 p-4 bg-red-50 border-2 border-red-300">
        <AlertCircle class="w-5 h-5 text-red-600" />
        <div>
          <div class="font-bold text-red-800">Connection Error</div>
          <div class="text-sm text-red-600">{errorMessage}</div>
        </div>
      </div>

      <button
        onclick={checkTelegramConnection}
        class="bg-gray-200 hover:bg-gray-300 border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] px-4 py-2 font-bold transition-all active:shadow-none active:translate-x-[2px] active:translate-y-[2px]"
      >
        Retry Connection Check
      </button>
    {/if}
  </div>
</div>
