<script lang="ts">
  import { onMount } from 'svelte';
  import { Plus, Trash2, X } from 'lucide-svelte';
  import { promptsState } from '../stores/index.js';
  import { listCustomPrompts, createPrompt, deletePrompt } from '../api/prompts.js';
  import type { CustomPrompt } from '../types/api.js';

  let isModalOpen = $state(false);
  let newName = $state('');
  let newInstructions = $state('');
  let isLoading = $state(false);
  let isSaving = $state(false);

  onMount(async () => {
    await loadPrompts();
  });

  async function loadPrompts() {
    isLoading = true;
    try {
      const prompts = await listCustomPrompts();
      promptsState.update((state) => ({ ...state, customPrompts: prompts }));
    } catch (err) {
      console.error('Failed to load custom prompts:', err);
    } finally {
      isLoading = false;
    }
  }

  async function saveBlock() {
    if (!newName || !newInstructions) return;

    isSaving = true;
    try {
      await createPrompt({ title: newName, text: newInstructions });
      await loadPrompts();
      closeModal();
    } catch (err) {
      console.error('Failed to create prompt:', err);
      alert('Failed to create custom rule');
    } finally {
      isSaving = false;
    }
  }

  async function deleteBlock(prompt: CustomPrompt) {
    if (confirm(`Delete "${prompt.title}"? This cannot be undone.`)) {
      try {
        await deletePrompt(prompt.id);
        await loadPrompts();
      } catch (err) {
        console.error('Failed to delete prompt:', err);
        alert('Failed to delete custom rule');
      }
    }
  }

  function closeModal() {
    isModalOpen = false;
    newName = '';
    newInstructions = '';
  }
</script>

<div class="card">
  <div class="flex items-center justify-between mb-4">
    <h3 class="font-extrabold">Custom Blocks</h3>
    <button
      onclick={() => (isModalOpen = true)}
      class="bg-[#FF8A00] border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] px-3 py-1 text-sm font-bold flex items-center gap-1 transition-all active:shadow-none active:translate-x-[2px] active:translate-y-[2px]"
    >
      <Plus class="w-4 h-4" />
      NEW
    </button>
  </div>

  <div class="space-y-3">
    {#if isLoading}
      <div class="text-center py-8 text-gray-500">Loading...</div>
    {:else if $promptsState.customPrompts.length === 0}
      <div class="text-center py-8 text-gray-500 italic border-2 border-dashed border-gray-300">
        No custom rules yet.
      </div>
    {:else}
      {#each $promptsState.customPrompts as prompt (prompt.id)}
        <div class="border-3 border-black p-3 bg-gray-50 hover:bg-[#fff9e6] transition-colors">
          <div class="flex justify-between items-start mb-2">
            <h4 class="font-bold text-lg leading-tight">{prompt.title}</h4>
            <button
              onclick={() => deleteBlock(prompt)}
              class="text-gray-400 hover:text-red-600 transition-colors"
            >
              <Trash2 class="w-5 h-5" />
            </button>
          </div>
          <p class="text-sm text-gray-600 font-medium line-clamp-2">"{prompt.text}"</p>
        </div>
      {/each}
    {/if}
  </div>
</div>

<!-- Modal -->
{#if isModalOpen}
  <div
    class="modal-backdrop"
    onclick={closeModal}
    onkeydown={(e) => e.key === 'Escape' && closeModal()}
    role="button"
    tabindex="0"
  >
    <div class="modal-content" onclick={(e) => e.stopPropagation()} role="dialog" tabindex="-1">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-extrabold">New Custom Block</h2>
        <button onclick={closeModal} class="p-1 hover:bg-gray-100"><X class="w-6 h-6" /></button>
      </div>
      <p class="text-gray-600 mb-4">Define a new rule for SusBonk using natural language.</p>

      <div class="space-y-4 mb-6">
        <div>
          <label for="block-name" class="font-bold mb-2 block">Name</label>
          <input
            id="block-name"
            type="text"
            bind:value={newName}
            placeholder="e.g. No Competitors"
            class="w-full border-3 border-black px-3 py-2 focus:outline-none focus:border-[#CCFF00]"
          />
        </div>
        <div>
          <label for="block-instructions" class="font-bold mb-2 block">LLM Instructions</label>
          <textarea
            id="block-instructions"
            bind:value={newInstructions}
            placeholder="Describe what the bot should look for..."
            class="w-full border-3 border-black px-3 py-2 min-h-[100px] focus:outline-none focus:border-[#CCFF00]"
          ></textarea>
        </div>
      </div>

      <button
        onclick={saveBlock}
        class="btn btn-primary w-full py-3 text-lg font-black"
        disabled={isSaving}
      >
        {isSaving ? 'SAVING...' : 'SAVE RULE'}
      </button>
    </div>
  </div>
{/if}
