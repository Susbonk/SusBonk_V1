<script lang="ts">
  import { onMount } from "svelte";
  import { prompts, customPrompts, chatPrompts, chats } from "./api";
  import Modal from "./Modal.svelte";

  export let chatId: string;

  let availablePrompts: any[] = [];
  let availableCustomPrompts: any[] = [];
  let linkedPrompts: any[] = [];
  let linkedCustomPrompts: any[] = [];
  let loading = false;
  let expandedPrompts: Set<string> = new Set();
  let addModal: { show: boolean; prompt: any; type: 'system' | 'custom'; threshold: number } = { 
    show: false, prompt: null, type: 'system', threshold: 0.3 
  };

  onMount(async () => {
    await loadData();
  });

  const loadData = async () => {
    loading = true;
    try {
      const [promptsRes, customPromptsRes, linksRes] = await Promise.all([
        prompts.list(),
        customPrompts.list(),
        chats.getLinks(chatId)
      ]);
      
      availablePrompts = promptsRes.prompts;
      availableCustomPrompts = customPromptsRes.prompts;
      linkedPrompts = linksRes.prompts;
      linkedCustomPrompts = linksRes.custom_prompts;
    } finally {
      loading = false;
    }
  };

  const toggleExpanded = (id: string) => {
    if (expandedPrompts.has(id)) {
      expandedPrompts.delete(id);
    } else {
      expandedPrompts.add(id);
    }
    expandedPrompts = expandedPrompts;
  };

  const showAddModal = (prompt: any, type: 'system' | 'custom') => {
    addModal = { show: true, prompt, type, threshold: 0.3 };
  };

  const confirmAdd = async () => {
    if (addModal.type === 'system') {
      await chatPrompts.linkPrompt(chatId, { 
        prompt_id: addModal.prompt.id, 
        threshold: addModal.threshold 
      });
    } else {
      await chatPrompts.linkCustomPrompt(chatId, { 
        custom_prompt_id: addModal.prompt.id, 
        threshold: addModal.threshold 
      });
    }
    addModal = { show: false, prompt: null, type: 'system', threshold: 0.3 };
    await loadData();
  };

  const unlinkPrompt = async (promptId: string) => {
    await chatPrompts.unlinkPrompt(chatId, promptId);
    await loadData();
  };

  const unlinkCustomPrompt = async (customPromptId: string) => {
    await chatPrompts.unlinkCustomPrompt(chatId, customPromptId);
    await loadData();
  };

  const getPromptById = (id: string) => availablePrompts.find(p => p.id === id);
  const getCustomPromptById = (id: string) => availableCustomPrompts.find(p => p.id === id);
  const isPromptLinked = (id: string) => linkedPrompts.some(p => p.prompt_id === id);
  const isCustomPromptLinked = (id: string) => linkedCustomPrompts.some(p => p.custom_prompt_id === id);
</script>

<div class="card">
  <h3>Linked Prompts</h3>
  
  {#if loading}
    <p>Loading...</p>
  {:else}
    <div class="prompts-section">
      <h4>System Prompts</h4>
      <div class="linked-list">
        {#each linkedPrompts as link}
          {@const prompt = getPromptById(link.prompt_id)}
          {#if prompt}
            <div class="prompt-item">
              <div class="prompt-info">
                <div class="prompt-header-row">
                  <strong>{prompt.title || "Untitled"}</strong>
                  <div class="prompt-actions">
                    <button class="btn-text" on:click={() => toggleExpanded(prompt.id)}>
                      {expandedPrompts.has(prompt.id) ? "Hide" : "View"} Full Text
                    </button>
                    <button class="btn-danger" on:click={() => unlinkPrompt(link.prompt_id)}>Remove</button>
                  </div>
                </div>
                <small>Threshold: {link.threshold}</small>
                {#if expandedPrompts.has(prompt.id)}
                  <div class="prompt-full-text">{prompt.text}</div>
                {/if}
              </div>
            </div>
          {/if}
        {/each}
      </div>
      
      <div class="available-list">
        <h5>Available System Prompts</h5>
        {#each availablePrompts.filter(p => p.is_active && !isPromptLinked(p.id)) as prompt}
          <div class="prompt-item">
            <div class="prompt-info">
              <div class="prompt-header-row">
                <strong>{prompt.title || "Untitled"}</strong>
                <div class="prompt-actions">
                  <button class="btn-text" on:click={() => toggleExpanded(prompt.id)}>
                    {expandedPrompts.has(prompt.id) ? "Hide" : "View"} Full Text
                  </button>
                  <button class="btn-primary" on:click={() => showAddModal(prompt, 'system')}>Add</button>
                </div>
              </div>
              {#if expandedPrompts.has(prompt.id)}
                <div class="prompt-full-text">{prompt.text}</div>
              {:else}
                <p class="prompt-preview">{prompt.text.substring(0, 100)}...</p>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    </div>

    <div class="prompts-section">
      <h4>Custom Prompts</h4>
      <div class="linked-list">
        {#each linkedCustomPrompts as link}
          {@const prompt = getCustomPromptById(link.custom_prompt_id)}
          {#if prompt}
            <div class="prompt-item">
              <div class="prompt-info">
                <div class="prompt-header-row">
                  <strong>{prompt.title || "Untitled"}</strong>
                  <div class="prompt-actions">
                    <button class="btn-text" on:click={() => toggleExpanded(prompt.id)}>
                      {expandedPrompts.has(prompt.id) ? "Hide" : "View"} Full Text
                    </button>
                    <button class="btn-danger" on:click={() => unlinkCustomPrompt(link.custom_prompt_id)}>Remove</button>
                  </div>
                </div>
                <small>Threshold: {link.threshold}</small>
                {#if expandedPrompts.has(prompt.id)}
                  <div class="prompt-full-text">{prompt.text}</div>
                {/if}
              </div>
            </div>
          {/if}
        {/each}
      </div>
      
      <div class="available-list">
        <h5>Available Custom Prompts</h5>
        {#each availableCustomPrompts.filter(p => p.is_active && !isCustomPromptLinked(p.id)) as prompt}
          <div class="prompt-item">
            <div class="prompt-info">
              <div class="prompt-header-row">
                <strong>{prompt.title || "Untitled"}</strong>
                <div class="prompt-actions">
                  <button class="btn-text" on:click={() => toggleExpanded(prompt.id)}>
                    {expandedPrompts.has(prompt.id) ? "Hide" : "View"} Full Text
                  </button>
                  <button class="btn-primary" on:click={() => showAddModal(prompt, 'custom')}>Add</button>
                </div>
              </div>
              {#if expandedPrompts.has(prompt.id)}
                <div class="prompt-full-text">{prompt.text}</div>
              {:else}
                <p class="prompt-preview">{prompt.text.substring(0, 100)}...</p>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>

{#if addModal.show}
  <Modal
    message="Add prompt '{addModal.prompt.title || 'Untitled'}' to chat?"
    onConfirm={confirmAdd}
    onCancel={() => (addModal = { show: false, prompt: null, type: 'system', threshold: 0.3 })}
  >
    <div class="threshold-input">
      <label>
        Threshold (0.0 - 1.0):
        <input 
          type="number" 
          bind:value={addModal.threshold} 
          min="0" 
          max="1" 
          step="0.1"
        />
      </label>
    </div>
  </Modal>
{/if}

<style>
  h3, h4, h5 {
    margin-bottom: var(--spacing-md);
    color: var(--color-text);
  }

  h4 {
    border-bottom: 1px solid var(--color-border);
    padding-bottom: var(--spacing-sm);
  }

  h5 {
    font-size: var(--font-size-base);
    margin-top: var(--spacing-lg);
    margin-bottom: var(--spacing-sm);
  }

  .prompts-section {
    margin-bottom: var(--spacing-xl);
  }

  .linked-list, .available-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .prompt-item {
    display: flex;
    flex-direction: column;
    padding: var(--spacing-md);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    background: var(--color-background);
  }

  .prompt-header-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--spacing-sm);
  }

  .prompt-actions {
    display: flex;
    gap: var(--spacing-xs);
  }

  .prompt-info {
    flex: 1;
  }

  .prompt-info strong {
    display: block;
    margin-bottom: var(--spacing-xs);
  }

  .prompt-info small {
    color: var(--color-text-muted);
    font-size: var(--font-size-sm);
  }

  .prompt-preview {
    color: var(--color-text-muted);
    font-size: var(--font-size-sm);
    margin: var(--spacing-xs) 0;
    line-height: 1.4;
  }

  .prompt-full-text {
    background: var(--color-surface);
    padding: var(--spacing-md);
    border-radius: var(--border-radius);
    margin-top: var(--spacing-sm);
    white-space: pre-wrap;
    font-family: monospace;
    font-size: var(--font-size-sm);
    line-height: 1.5;
    max-height: 300px;
    overflow-y: auto;
  }

  .btn-text {
    background: none;
    border: none;
    color: var(--color-primary);
    padding: var(--spacing-xs);
    font-size: var(--font-size-sm);
    text-decoration: underline;
  }

  .btn-text:hover {
    background: var(--color-surface);
  }

  .btn-danger {
    background: var(--color-error);
    color: white;
    border-color: var(--color-error);
    font-size: var(--font-size-sm);
    padding: var(--spacing-xs) var(--spacing-sm);
  }

  .btn-danger:hover {
    background: #b91c1c;
    border-color: #b91c1c;
  }

  .threshold-input {
    margin-top: var(--spacing-md);
  }

  .threshold-input label {
    display: block;
    margin-bottom: var(--spacing-xs);
    font-weight: 500;
  }

  .threshold-input input {
    width: 100px;
    margin-top: var(--spacing-xs);
  }
</style>
