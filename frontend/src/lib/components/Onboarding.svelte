<script lang="ts">
  import { Play } from 'lucide-svelte';

  interface Props {
    onSummon: () => void;
  }

  let { onSummon }: Props = $props();

  const steps = [
    "Add @SusBonkBot to your Telegram group",
    "Grant admin permissions (Delete Messages)",
    "Type /start to initialize SusBonk"
  ];
</script>

<div class="min-h-screen bg-white p-4 flex flex-col">
  <div class="mt-8 card p-6 mb-6">
    <h1 class="text-2xl font-black mb-4">How to Summon SusBonk</h1>
    
    <!-- Video Placeholder -->
    <div class="aspect-video bg-gray-100 border-3 border-black flex items-center justify-center mb-6 relative">
      <div class="absolute inset-0 flex items-center justify-center">
        <div class="w-16 h-16 bg-black rounded-full flex items-center justify-center">
          <Play class="w-8 h-8 text-white fill-white" />
        </div>
      </div>
      <div class="absolute bottom-3 left-3 bg-white border-2 border-black px-2 py-1 text-xs font-bold">2:34</div>
    </div>

    <!-- Steps -->
    <div class="space-y-4">
      {#each steps as step, i}
        <div class="flex items-start gap-3">
          <div class="w-8 h-8 bg-[#CCFF00] border-3 border-black flex items-center justify-center flex-shrink-0 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] font-black">
            {i + 1}
          </div>
          <p class="pt-1 font-bold">{step}</p>
        </div>
      {/each}
    </div>
  </div>

  <div class="mt-auto pb-8">
    <button onclick={onSummon} class="w-full btn btn-secondary py-5 px-6 text-xl font-black -rotate-2 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] border-4">
      SUMMON SUSBONK 🔨
    </button>
  </div>
</div>
