<script lang="ts">
  import { Play } from 'lucide-svelte';

  interface Props {
    onSummon: () => void;
  }

  let { onSummon }: Props = $props();
</script>

<div class="min-h-screen bg-white p-4 flex flex-col">
  <!-- Hero Card -->
  <div class="mt-8 bg-white border-[4px] border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] p-6 mb-6">
    <h1 class="text-2xl mb-4" style="font-family: Poppins, sans-serif; font-weight: 900;">
      How to Summon SusBonk
    </h1>
    
    <!-- Video Placeholder -->
    <div class="aspect-video bg-gray-100 border-[3px] border-black flex items-center justify-center mb-6 relative">
      <div class="absolute inset-0 flex items-center justify-center">
        <div class="w-16 h-16 bg-black rounded-full flex items-center justify-center">
          <Play class="w-8 h-8 text-white fill-white" />
        </div>
      </div>
      <div class="absolute bottom-3 left-3 bg-white border-[2px] border-black px-2 py-1 text-xs" style="font-family: Poppins, sans-serif; font-weight: 700;">
        2:34
      </div>
    </div>

    <!-- Instruction List -->
    <div class="space-y-4">
      <div class="flex items-start gap-3">
        <div class="w-8 h-8 bg-[#CCFF00] border-[3px] border-black flex items-center justify-center flex-shrink-0 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]" style="font-family: Poppins, sans-serif; font-weight: 900;">
          1
        </div>
        <p class="pt-1" style="font-family: Poppins, sans-serif; font-weight: 700;">
          Add @SusBonkBot to your Telegram group
        </p>
      </div>
      
      <div class="flex items-start gap-3">
        <div class="w-8 h-8 bg-[#CCFF00] border-[3px] border-black flex items-center justify-center flex-shrink-0 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]" style="font-family: Poppins, sans-serif; font-weight: 900;">
          2
        </div>
        <p class="pt-1" style="font-family: Poppins, sans-serif; font-weight: 700;">
          Grant admin permissions (Delete Messages)
        </p>
      </div>
      
      <div class="flex items-start gap-3">
        <div class="w-8 h-8 bg-[#CCFF00] border-[3px] border-black flex items-center justify-center flex-shrink-0 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]" style="font-family: Poppins, sans-serif; font-weight: 900;">
          3
        </div>
        <p class="pt-1" style="font-family: Poppins, sans-serif; font-weight: 700;">
          Type /start to initialize SusBonk
        </p>
      </div>
    </div>
  </div>

  <!-- Main Action Button - Sticky at bottom -->
  <div class="mt-auto pb-8">
    <button
      onclick={onSummon}
      class="w-full bg-[#FF8A00] border-[4px] border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] py-5 px-6 transition-all active:shadow-none active:translate-x-[6px] active:translate-y-[6px] hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]"
      style="font-family: Poppins, sans-serif; font-weight: 900; font-size: 20px; transform: rotate(-2deg);"
    >
      SUMMON SUSBONK 🔨
    </button>
  </div>
</div>
