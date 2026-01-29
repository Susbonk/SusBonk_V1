<script lang="ts">
  import { User, Shield } from 'lucide-svelte';
</script>

<div class="card">
  <div class="flex items-center justify-between mb-4">
    <h3 class="font-extrabold">Recent Bonks</h3>
  </div>

  <div class="border-3 border-black p-4 bg-gray-50">
    <div class="flex gap-3 items-start">
      <div class="w-10 h-10 bg-black border-2 border-black flex items-center justify-center flex-shrink-0">
        <Shield class="w-6 h-6 text-white" />
      </div>
      <div class="flex-1">
        <p class="font-bold text-sm mb-1">No bonks yet</p>
        <p class="text-xs text-gray-600 font-semibold leading-relaxed">
          This view will populate with real moderation events once the Telegram bot is connected and deleting messages.
        </p>
        <div class="mt-3 flex items-center gap-2 text-[10px] text-gray-600 font-bold">
          <User class="w-4 h-4" />
          <span>Tip: check OpenSearch Dashboards for logs at http://localhost:5601</span>
        </div>
      </div>
    </div>
  </div>
</div>
