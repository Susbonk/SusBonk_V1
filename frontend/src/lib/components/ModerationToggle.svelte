<script lang="ts">
  import type { ComponentType } from 'svelte';
  import type { StrengthLevel } from '../types';

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

  function setLevel(newLevel: StrengthLevel) {
    level = newLevel;
    wobble = true;
    setTimeout(() => wobble = false, 300);
  }

  const levels: StrengthLevel[] = ["Chill", "Normal", "Bonkers"];
</script>

<div class="card transition-transform {wobble ? 'animate-wobble' : ''}">
  <div class="flex items-center gap-3 mb-4">
    <Icon class="w-6 h-6" />
    <span class="font-extrabold">{category}</span>
  </div>

  <div class="grid grid-cols-3 gap-2">
    {#each levels as lvl}
      <button
        onclick={() => setLevel(lvl)}
        class="py-3 px-2 border-3 border-black transition-all font-bold text-sm {level === lvl ? 'bg-[#CCFF00] shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]' : 'bg-gray-100 hover:bg-gray-200'}"
      >
        {lvl}
      </button>
    {/each}
  </div>
</div>
