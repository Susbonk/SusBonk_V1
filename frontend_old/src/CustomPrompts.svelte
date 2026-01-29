<script lang="ts">
  import { onMount } from "svelte";
  import { customPrompts } from "./api";
  import Modal from "./Modal.svelte";
  import { Plus, Pencil, Trash2 } from "lucide-svelte";

  let promptsList = $state<any[]>([]);
  let editing = $state<string | null>(null);
  let creating = $state(false);
  let deleteModal = $state<{ show: boolean; prompt: any }>({
    show: false,
    prompt: null,
  });

  let form = $state({ title: "", text: "", is_active: true });

  onMount(async () => {
    await loadPrompts();
  });

  async function loadPrompts() {
    const res = await customPrompts.list();
    promptsList = res.prompts;
  }

  function startCreate() {
    form = { title: "", text: "", is_active: true };
    creating = true;
    editing = null;
  }

  function startEdit(prompt: any) {
    form = { ...prompt };
    editing = prompt.id;
    creating = false;
  }

  async function save() {
    if (creating) {
      await customPrompts.create(form);
      creating = false;
    } else if (editing) {
      await customPrompts.update(editing, form);
      editing = null;
    }
    await loadPrompts();
  }

  function cancel() {
    creating = false;
    editing = null;
    form = { title: "", text: "", is_active: true };
  }

  function confirmDelete(prompt: any) {
    deleteModal = { show: true, prompt };
  }

  async function deletePrompt() {
    await customPrompts.delete(deleteModal.prompt.id);
    deleteModal = { show: false, prompt: null };
    await loadPrompts();
  }
</script>

<div class="space-y-4">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <h3 class="font-black text-lg">Custom Prompts</h3>
    <button
      onclick={startCreate}
      class="btn btn-secondary px-4 py-2 flex items-center gap-2"
    >
      <Plus class="w-4 h-4" />
      NEW
    </button>
  </div>

  <!-- Prompts List -->
  <div class="space-y-3">
    {#if promptsList.length === 0}
      <div
        class="text-center py-8 text-gray-500 italic border-3 border-dashed border-gray-300"
      >
        No custom prompts yet. Click NEW to create one.
      </div>
    {:else}
      {#each promptsList as prompt}
        <div class="card">
          <div class="flex items-start justify-between mb-2">
            <div>
              <h4 class="font-bold">{prompt.title || "Untitled"}</h4>
              <span
                class="status-badge {prompt.is_active ? 'active' : 'inactive'}"
              >
                {prompt.is_active ? "Active" : "Inactive"}
              </span>
            </div>
            <div class="flex gap-2">
              <button
                onclick={() => startEdit(prompt)}
                class="p-2 border-2 border-black bg-white hover:bg-[#CCFF00] transition-all shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[2px] active:translate-y-[2px]"
                title="Edit prompt"
              >
                <Pencil class="w-4 h-4" />
              </button>
              <button
                onclick={() => confirmDelete(prompt)}
                class="p-2 border-2 border-black bg-white hover:bg-red-200 text-red-600 transition-all shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[2px] active:translate-y-[2px]"
                title="Delete prompt"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
          <p class="text-sm text-gray-600 whitespace-pre-wrap line-clamp-3">
            {prompt.text}
          </p>
          <p class="text-xs text-gray-400 mt-2">
            Created: {new Date(prompt.created_at).toLocaleString()}
          </p>
        </div>
      {/each}
    {/if}
  </div>
</div>

{#if creating || editing}
  <Modal
    title={creating ? "Create Custom Prompt" : "Edit Custom Prompt"}
    confirmText="Save"
    confirmDisabled={!form.text.trim()}
    onConfirm={save}
    onCancel={cancel}
  >
    <div class="space-y-4">
      <div>
        <label class="block font-bold mb-2">Title (optional)</label>
        <input
          type="text"
          bind:value={form.title}
          placeholder="Enter title"
          class="w-full"
        />
      </div>

      <div>
        <label class="block font-bold mb-2">Prompt Text</label>
        <textarea
          bind:value={form.text}
          placeholder="Enter the AI instructions for detecting spam..."
          class="w-full min-h-[120px]"
          required
        ></textarea>
      </div>

      <label class="flex items-center gap-2 font-medium">
        <input type="checkbox" bind:checked={form.is_active} class="w-5 h-5" />
        Active
      </label>
    </div>
  </Modal>
{/if}

{#if deleteModal.show}
  <Modal
    message="Delete prompt '{deleteModal.prompt.title || 'Untitled'}'?"
    onConfirm={deletePrompt}
    onCancel={() => (deleteModal = { show: false, prompt: null })}
  />
{/if}
