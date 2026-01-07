<script lang="ts">
  import type { ComponentType } from 'svelte';

  type StrengthLevel = "Chill" | "Normal" | "Bonkers";

  interface Props {
    icon: ComponentType;
    category: string;
    initialLevel?: StrengthLevel;
  }

  let { icon: Icon, category, initialLevel = "Normal" }: Props = $props();
  let level = $state<StrengthLevel>("Normal");
  let wobble = $state(false);

  $effect(() => {
    level = initialLevel;
  });

  function handleLevelChange(newLevel: StrengthLevel) {
    level = newLevel;
    wobble = true;
    setTimeout(() => wobble = false, 300);
  }
</script>

<div 
  class="bg-white border-[4px] border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] p-4 transition-transform {wobble ? 'animate-wobble' : ''}"
>
  <!-- Category Header -->
  <div class="flex items-center gap-3 mb-4">
    <Icon class="w-6 h-6" />
    <span style="font-family: Poppins, sans-serif; font-weight: 800; font-size: 16px;">
      {category}
    </span>
  </div>

  <!-- 3-State Segmented Control -->
  <div class="grid grid-cols-3 gap-2">
    <button
      onclick={() => handleLevelChange("Chill")}
      class="py-3 px-2 border-[3px] border-black transition-all {level === 'Chill' ? 'bg-[#CCFF00] shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]' : 'bg-gray-100 hover:bg-gray-200'}"
      style="font-family: Poppins, sans-serif; font-weight: 700; font-size: 13px;"
    >
      Chill
    </button>
    <button
      onclick={() => handleLevelChange("Normal")}
      class="py-3 px-2 border-[3px] border-black transition-all {level === 'Normal' ? 'bg-[#CCFF00] shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]' : 'bg-gray-100 hover:bg-gray-200'}"
      style="font-family: Poppins, sans-serif; font-weight: 700; font-size: 13px;"
    >
      Normal
    </button>
    <button
      onclick={() => handleLevelChange("Bonkers")}
      class="py-3 px-2 border-[3px] border-black transition-all {level === 'Bonkers' ? 'bg-[#CCFF00] shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]' : 'bg-gray-100 hover:bg-gray-200'}"
      style="font-family: Poppins, sans-serif; font-weight: 700; font-size: 13px;"
    >
      Bonkers
    </button>
  </div>
</div>
