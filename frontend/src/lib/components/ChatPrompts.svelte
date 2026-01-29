<script lang="ts">
  import { onMount } from 'svelte';
  import { chatPromptsApi, type LinkedPrompt, type LinkedCustomPrompt } from '../api/chatPrompts';
  import { Plus, Trash2, Settings } from 'lucide-svelte';

  interface Props {
    chatId: number;
    availablePrompts: Array<{ id: number; name: string }>;
    availableCustomPrompts: Array<{ id: number; text: string }>;
  }

  let { chatId, availablePrompts, availableCustomPrompts }: Props = $props();

  let linkedPrompts = $state<LinkedPrompt[]>([]);
  let linkedCustomPrompts = $state<LinkedCustomPrompt[]>([]);
  let loading = $state(true);
  let showAddPrompt = $state(false);
  let showAddCustom = $state(false);
  let selectedPromptId = $state<number | null>(null);
  let selectedCustomId = $state<number | null>(null);
  let threshold = $state(0.7);
  let priority = $state(1);

  onMount(async () => {
    await loadLinkedPrompts();
  });

  async function loadLinkedPrompts() {
    try {
      const data = await chatPromptsApi.getLinkedPrompts(chatId);
      linkedPrompts = data.system_prompts;
      linkedCustomPrompts = data.custom_prompts;
    } catch (error) {
      console.error('Failed to load linked prompts:', error);
    } finally {
      loading = false;
    }
  }

  async function linkPrompt() {
    if (!selectedPromptId) return;
    try {
      await chatPromptsApi.linkPrompt(chatId, {
        prompt_id: selectedPromptId,
        threshold,
        priority,
        is_active: true,
      });
      await loadLinkedPrompts();
      showAddPrompt = false;
      selectedPromptId = null;
      threshold = 0.7;
      priority = 1;
    } catch (error) {
      console.error('Failed to link prompt:', error);
    }
  }

  async function unlinkPrompt(promptId: number) {
    try {
      await chatPromptsApi.unlinkPrompt(chatId, promptId);
      await loadLinkedPrompts();
    } catch (error) {
      console.error('Failed to unlink prompt:', error);
    }
  }

  async function linkCustomPrompt() {
    if (!selectedCustomId) return;
    try {
      await chatPromptsApi.linkCustomPrompt(chatId, {
        custom_prompt_id: selectedCustomId,
        threshold,
        priority,
        is_active: true,
      });
      await loadLinkedPrompts();
      showAddCustom = false;
      selectedCustomId = null;
      threshold = 0.7;
      priority = 1;
    } catch (error) {
      console.error('Failed to link custom prompt:', error);
    }
  }

  async function unlinkCustomPrompt(customPromptId: number) {
    try {
      await chatPromptsApi.unlinkCustomPrompt(chatId, customPromptId);
      await loadLinkedPrompts();
    } catch (error) {
      console.error('Failed to unlink custom prompt:', error);
    }
  }

  const unlinkedPrompts = $derived(
    availablePrompts.filter(p => !linkedPrompts.some(lp => lp.prompt_id === p.id))
  );

  const unlinkedCustomPrompts = $derived(
    availableCustomPrompts.filter(cp => !linkedCustomPrompts.some(lcp => lcp.custom_prompt_id === cp.id))
  );
</script>

<div class="chat-prompts">
  {#if loading}
    <p class="text-gray-500">Loading prompts...</p>
  {:else}
    <div class="section">
      <div class="section-header">
        <h3>System Prompts</h3>
        <button class="btn-icon" onclick={() => (showAddPrompt = !showAddPrompt)}>
          <Plus size={16} />
        </button>
      </div>

      {#if showAddPrompt && unlinkedPrompts.length > 0}
        <div class="add-form">
          <select bind:value={selectedPromptId}>
            <option value={null}>Select prompt...</option>
            {#each unlinkedPrompts as prompt}
              <option value={prompt.id}>{prompt.name}</option>
            {/each}
          </select>
          <label>
            Threshold:
            <input type="number" bind:value={threshold} min="0" max="1" step="0.1" />
          </label>
          <label>
            Priority:
            <input type="number" bind:value={priority} min="1" />
          </label>
          <button class="btn-primary" onclick={linkPrompt}>Add</button>
          <button class="btn-secondary" onclick={() => (showAddPrompt = false)}>Cancel</button>
        </div>
      {/if}

      <div class="prompts-list">
        {#each linkedPrompts as prompt}
          <div class="prompt-item">
            <div class="prompt-info">
              <span class="prompt-name">{prompt.prompt_name}</span>
              <span class="prompt-meta">Threshold: {prompt.threshold} | Priority: {prompt.priority}</span>
            </div>
            <button class="btn-icon" onclick={() => unlinkPrompt(prompt.prompt_id)}>
              <Trash2 size={16} />
            </button>
          </div>
        {/each}
      </div>
    </div>

    <div class="section">
      <div class="section-header">
        <h3>Custom Prompts</h3>
        <button class="btn-icon" onclick={() => (showAddCustom = !showAddCustom)}>
          <Plus size={16} />
        </button>
      </div>

      {#if showAddCustom && unlinkedCustomPrompts.length > 0}
        <div class="add-form">
          <select bind:value={selectedCustomId}>
            <option value={null}>Select custom prompt...</option>
            {#each unlinkedCustomPrompts as custom}
              <option value={custom.id}>{custom.text.slice(0, 50)}...</option>
            {/each}
          </select>
          <label>
            Threshold:
            <input type="number" bind:value={threshold} min="0" max="1" step="0.1" />
          </label>
          <label>
            Priority:
            <input type="number" bind:value={priority} min="1" />
          </label>
          <button class="btn-primary" onclick={linkCustomPrompt}>Add</button>
          <button class="btn-secondary" onclick={() => (showAddCustom = false)}>Cancel</button>
        </div>
      {/if}

      <div class="prompts-list">
        {#each linkedCustomPrompts as custom}
          <div class="prompt-item">
            <div class="prompt-info">
              <span class="prompt-name">{custom.custom_prompt_text.slice(0, 60)}...</span>
              <span class="prompt-meta">Threshold: {custom.threshold} | Priority: {custom.priority}</span>
            </div>
            <button class="btn-icon" onclick={() => unlinkCustomPrompt(custom.custom_prompt_id)}>
              <Trash2 size={16} />
            </button>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .chat-prompts {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .section {
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  h3 {
    font-size: 1rem;
    font-weight: 600;
    margin: 0;
  }

  .add-form {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding: 1rem;
    background: var(--bg-secondary);
    border-radius: 6px;
    margin-bottom: 1rem;
  }

  .add-form label {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    font-size: 0.875rem;
  }

  .prompts-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .prompt-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: var(--bg-secondary);
    border-radius: 6px;
  }

  .prompt-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .prompt-name {
    font-weight: 500;
  }

  .prompt-meta {
    font-size: 0.75rem;
    color: var(--text-secondary);
  }

  .btn-icon {
    padding: 0.5rem;
    background: transparent;
    border: none;
    cursor: pointer;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .btn-icon:hover {
    background: var(--bg-hover);
  }

  .btn-primary,
  .btn-secondary {
    padding: 0.5rem 1rem;
    border-radius: 6px;
    border: none;
    cursor: pointer;
    font-size: 0.875rem;
  }

  .btn-primary {
    background: var(--primary-color);
    color: white;
  }

  .btn-secondary {
    background: var(--bg-secondary);
    color: var(--text-primary);
  }

  select,
  input {
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-primary);
    color: var(--text-primary);
  }
</style>
