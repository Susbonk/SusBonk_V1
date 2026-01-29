<script lang="ts">
  import { onMount } from "svelte";
  import { customPrompts } from "./api";
  import Modal from "./Modal.svelte";

  let prompts: any[] = [];
  let editing: string | null = null;
  let creating = false;
  let deleteModal: { show: boolean; prompt: any } = {
    show: false,
    prompt: null,
  };

  let form = { title: "", text: "", is_active: true };

  onMount(async () => {
    await loadPrompts();
  });

  const loadPrompts = async () => {
    const res = await customPrompts.list();
    prompts = res.prompts;
  };

  const startCreate = () => {
    form = { title: "", text: "", is_active: true };
    creating = true;
  };

  const startEdit = (prompt: any) => {
    form = { ...prompt };
    editing = prompt.id;
  };

  const save = async () => {
    if (creating) {
      await customPrompts.create(form);
      creating = false;
    } else if (editing) {
      await customPrompts.update(editing, form);
      editing = null;
    }
    await loadPrompts();
  };

  const cancel = () => {
    creating = false;
    editing = null;
    form = { title: "", text: "", is_active: true };
  };

  const confirmDelete = (prompt: any) => {
    deleteModal = { show: true, prompt };
  };

  const deletePrompt = async () => {
    await customPrompts.delete(deleteModal.prompt.id);
    deleteModal = { show: false, prompt: null };
    await loadPrompts();
  };
</script>

<div class="container">
  <div class="card">
    <div class="header">
      <h2>Custom Prompts</h2>
      <button class="btn-primary" on:click={startCreate}>Create New</button>
    </div>

    {#if creating || editing}
      <div class="form-card">
        <h3>{creating ? "Create" : "Edit"} Custom Prompt</h3>
        <div class="form-group">
          <label for="title">Title (optional)</label>
          <input
            id="title"
            type="text"
            bind:value={form.title}
            placeholder="Enter title"
          />
        </div>
        <div class="form-group">
          <label for="prompt-text">Prompt Text</label>
          <textarea
            id="prompt-text"
            bind:value={form.text}
            placeholder="Enter prompt text"
            rows="6"
            required
          ></textarea>
        </div>
        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" bind:checked={form.is_active} />
            Active
          </label>
        </div>
        <div class="button-group">
          <button
            class="btn-primary"
            on:click={save}
            disabled={!form.text.trim()}>Save</button
          >
          <button type="button" on:click={cancel}>Cancel</button>
        </div>
      </div>
    {/if}

    <div class="prompts-list">
      {#each prompts as prompt}
        <div class="prompt-item card">
          <div class="prompt-header">
            <div>
              <h4>{prompt.title || "Untitled"}</h4>
              <span
                class="status-badge {prompt.is_active ? 'active' : 'inactive'}"
              >
                {prompt.is_active ? "Active" : "Inactive"}
              </span>
            </div>
            <div class="actions">
              <button on:click={() => startEdit(prompt)}>Edit</button>
              <button class="btn-danger" on:click={() => confirmDelete(prompt)}
                >Delete</button
              >
            </div>
          </div>
          <p class="prompt-text">{prompt.text}</p>
          <small class="timestamp"
            >Created: {new Date(prompt.created_at).toLocaleString()}</small
          >
        </div>
      {/each}
    </div>
  </div>
</div>

{#if deleteModal.show}
  <Modal
    message="Delete prompt '{deleteModal.prompt.title || 'Untitled'}'?"
    onConfirm={deletePrompt}
    onCancel={() => (deleteModal = { show: false, prompt: null })}
  />
{/if}

<style>
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
  }

  .form-card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    padding: var(--spacing-lg);
    margin-bottom: var(--spacing-lg);
  }

  .form-card h3 {
    margin-bottom: var(--spacing-md);
  }

  textarea {
    width: 100%;
    min-height: 120px;
    resize: vertical;
  }

  .prompts-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .prompt-item {
    background: var(--color-surface);
  }

  .prompt-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--spacing-sm);
  }

  .prompt-header h4 {
    margin: 0 0 var(--spacing-xs) 0;
  }

  .status-badge {
    font-size: var(--font-size-sm);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--border-radius);
    font-weight: 500;
  }

  .status-badge.active {
    background: #dcfce7;
    color: #166534;
  }

  .status-badge.inactive {
    background: #fef2f2;
    color: #991b1b;
  }

  .actions {
    display: flex;
    gap: var(--spacing-xs);
  }

  .actions button {
    font-size: var(--font-size-sm);
    padding: var(--spacing-xs) var(--spacing-sm);
  }

  .btn-danger {
    background: var(--color-error);
    color: white;
    border-color: var(--color-error);
  }

  .btn-danger:hover {
    background: #b91c1c;
    border-color: #b91c1c;
  }

  .prompt-text {
    margin-bottom: var(--spacing-sm);
    line-height: 1.6;
    white-space: pre-wrap;
  }

  .timestamp {
    color: var(--color-text-muted);
    font-size: var(--font-size-sm);
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-weight: 500;
  }
</style>
