<script lang="ts">
  import { User } from 'lucide-svelte';

  interface BonkLog {
    id: string;
    username: string;
    timestamp: string;
    snippet: string;
  }

  const logs: BonkLog[] = [
    { id: "1", username: "cryptoking420", timestamp: "2m ago", snippet: "🚨 DOUBLE YOUR CRYPTO IN 24HRS! CLICK HERE..." },
    { id: "2", username: "workfromhome", timestamp: "5m ago", snippet: "Make $5000/week working from home! No experience..." },
    { id: "3", username: "sususer123", timestamp: "12m ago", snippet: "Send me your wallet address and I'll send you..." },
    { id: "4", username: "totallylegit", timestamp: "18m ago", snippet: "Free iPhone giveaway! Just click this link..." },
    { id: "5", username: "scammer_v2", timestamp: "23m ago", snippet: "Admin here, we need to verify your account..." },
    { id: "6", username: "phisherman", timestamp: "31m ago", snippet: "Your account will be deleted unless you..." },
    { id: "7", username: "spambot9000", timestamp: "45m ago", snippet: "Join our premium group for exclusive signals..." },
    { id: "8", username: "fakeadmin", timestamp: "1h ago", snippet: "This is official Telegram support. Please..." },
    { id: "9", username: "mlm_master", timestamp: "1h ago", snippet: "Be your own boss! Join my team and earn..." },
    { id: "10", username: "nft_scam", timestamp: "2h ago", snippet: "Rare NFT airdrop! Connect your wallet to..." },
  ];
</script>

<div class="card">
  <div class="flex items-center justify-between mb-4">
    <h3 class="font-extrabold">Recent Bonks</h3>
    <span class="text-xs bg-yellow-200 px-2 py-1 border-2 border-black font-bold">Sample Data - Real logs coming soon</span>
  </div>

  <div class="space-y-3">
    {#each logs as log (log.id)}
      <div class="border-3 border-black p-3 bg-gray-50 hover:bg-gray-100 transition-colors">
        <div class="flex gap-3">
          <div class="w-10 h-10 bg-black border-2 border-black flex items-center justify-center flex-shrink-0">
            <User class="w-6 h-6 text-white" />
          </div>

          <div class="flex-1 min-w-0">
            <div class="flex items-baseline gap-2 mb-1">
              <span class="font-bold text-sm">@{log.username}</span>
              <span class="text-xs text-gray-500 font-semibold">{log.timestamp}</span>
            </div>
            <p class="text-gray-400 truncate blur-[3px] select-none text-xs font-semibold">{log.snippet}</p>
          </div>

          <button class="bg-white border-2 border-black px-3 py-1 h-fit shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all active:shadow-none active:translate-x-[2px] active:translate-y-[2px] hover:bg-[#CCFF00] flex-shrink-0 text-[10px] font-bold -rotate-1">
            NOT SUS
          </button>
        </div>
      </div>
    {/each}
  </div>
</div>
