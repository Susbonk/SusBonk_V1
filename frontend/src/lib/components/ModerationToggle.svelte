<script lang="ts">
  import type { ComponentType } from 'svelte';
  import type { StrengthLevel } from '../types';
  import { Trash2, Pencil } from 'lucide-svelte';

  interface Props {
    icon: ComponentType;
    category: string;
    promptText?: string;
    initialLevel?: StrengthLevel;
    isCustom?: boolean;
    onEdit?: () => void;
    onDelete?: () => void;
  }

  let {
    icon: Icon,
    category,
    promptText,
    initialLevel = 'Normal',
    isCustom = false,
    onEdit,
    onDelete,
  }: Props = $props();
  let level = $state<StrengthLevel>('Normal');
  let wobble = $state(false);
  let showDetails = $state(false);

  $effect(() => {
    level = initialLevel;
  });

  function setLevel(newLevel: StrengthLevel) {
    level = newLevel;
    wobble = true;
    setTimeout(() => (wobble = false), 300);
  }

  const levels: StrengthLevel[] = ['Chill', 'Normal', 'Bonkers'];
</script>

<div class="card transition-transform {wobble ? 'animate-wobble' : ''}">
  <div class="flex items-center justify-between mb-4">
    <button
      class="flex items-center gap-3 text-left"
      onclick={() => promptText && (showDetails = !showDetails)}
    >
      <Icon class="w-6 h-6" />
      <span class="font-extrabold">{category}</span>
    </button>

    {#if isCustom}
      <div class="flex items-center gap-1">
        {#if onEdit}
          <button
            onclick={onEdit}
            class="p-1.5 hover:bg-gray-100 rounded transition-colors text-gray-500 hover:text-gray-700"
            title="Edit"
          >
            <Pencil class="w-4 h-4" />
          </button>
        {/if}
        {#if onDelete}
          <button
            onclick={onDelete}
            class="p-1.5 hover:bg-red-50 rounded transition-colors text-gray-400 hover:text-red-600"
            title="Delete"
          >
            <Trash2 class="w-4 h-4" />
          </button>
        {/if}
      </div>
    {/if}
  </div>

  {#if showDetails && promptText}
    <div class="mb-4 p-3 bg-gray-50 border-2 border-gray-200 text-sm text-gray-600 rounded">
      {promptText}
    </div>
  {/if}

  <div class="grid grid-cols-3 gap-2">
    {#each levels as lvl}
      <button
        onclick={() => setLevel(lvl)}
        class="py-3 px-2 border-3 border-black transition-all font-bold text-sm {level === lvl
          ? 'bg-[#CCFF00] shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]'
          : 'bg-gray-100 hover:bg-gray-200'}"
      >
        {lvl}
      </button>
    {/each}
  </div>
</div>
