<script lang="ts">
  import { onMount } from "svelte";
  import { prompts, customPrompts, chatPrompts, chats } from "./api";
  import Modal from "./Modal.svelte";
  import { Plus, Trash2, Eye, EyeOff } from "lucide-svelte";

  interface Props {
    chatId: string;
  }

  let { chatId }: Props = $props();

  let availablePrompts = $state<any[]>([]);
  let availableCustomPrompts = $state<any[]>([]);
  let linkedPrompts = $state<any[]>([]);
  let linkedCustomPrompts = $state<any[]>([]);
  let loading = $state(false);
  let expandedPrompts = $state<Set<string>>(new Set());
  let addModal = $state<{
    show: boolean;
    prompt: any;
    type: "system" | "custom";
    threshold: number;
  }>({
    show: false,
    prompt: null,
    type: "system",
    threshold: 0.3,
  });

  // Create new prompt state
  let showCreateForm = $state(false);
  let createForm = $state({ title: "", text: "", threshold: 0.3 });
  let isCreating = $state(false);

  onMount(async () => {
    await loadData();
  });

  async function loadData() {
    loading = true;
    try {
      const [promptsRes, customPromptsRes, linksRes] = await Promise.all([
        prompts.list(),
        customPrompts.list(),
        chats.getLinks(chatId),
      ]);

      availablePrompts = promptsRes.prompts;
      availableCustomPrompts = customPromptsRes.prompts;
      linkedPrompts = linksRes.prompts;
      linkedCustomPrompts = linksRes.custom_prompts;
    } finally {
      loading = false;
    }
  }

  function toggleExpanded(id: string) {
    const newSet = new Set(expandedPrompts);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    expandedPrompts = newSet;
  }

  function showAddModal(prompt: any, type: "system" | "custom") {
    addModal = { show: true, prompt, type, threshold: 0.3 };
  }

  async function confirmAdd() {
    if (addModal.type === "system") {
      await chatPrompts.linkPrompt(chatId, {
        prompt_id: addModal.prompt.id,
        threshold: addModal.threshold,
      });
    } else {
      await chatPrompts.linkCustomPrompt(chatId, {
        custom_prompt_id: addModal.prompt.id,
        threshold: addModal.threshold,
      });
    }
    addModal = { show: false, prompt: null, type: "system", threshold: 0.3 };
    await loadData();
  }

  async function unlinkPrompt(promptId: string) {
    if (confirm("Remove this prompt from the chat?")) {
      await chatPrompts.unlinkPrompt(chatId, promptId);
      await loadData();
    }
  }

  async function unlinkCustomPrompt(customPromptId: string) {
    if (confirm("Remove this custom prompt from the chat?")) {
      await chatPrompts.unlinkCustomPrompt(chatId, customPromptId);
      await loadData();
    }
  }

  const getPromptById = (id: string) =>
    availablePrompts.find((p) => p.id === id);
  const getCustomPromptById = (id: string) =>
    availableCustomPrompts.find((p) => p.id === id);
  const isPromptLinked = (id: string) =>
    linkedPrompts.some((p) => p.prompt_id === id);
  const isCustomPromptLinked = (id: string) =>
    linkedCustomPrompts.some((p) => p.custom_prompt_id === id);

  // Create new prompt and auto-link to this chat
  async function createAndLink() {
    if (!createForm.text.trim()) return;
    isCreating = true;
    try {
      // Create the custom prompt
      const newPrompt = await customPrompts.create({
        title: createForm.title || undefined,
        text: createForm.text,
        is_active: true,
      });
      // Auto-link it to this chat
      await chatPrompts.linkCustomPrompt(chatId, {
        custom_prompt_id: newPrompt.id,
        threshold: createForm.threshold,
      });
      // Reset form and reload
      createForm = { title: "", text: "", threshold: 0.3 };
      showCreateForm = false;
      await loadData();
    } catch (err) {
      console.error("Failed to create prompt:", err);
      alert("Failed to create prompt");
    } finally {
      isCreating = false;
    }
  }

  function cancelCreate() {
    showCreateForm = false;
    createForm = { title: "", text: "", threshold: 0.3 };
  }
</script>

<div class="space-y-4">
  <h4 class="font-bold text-lg">Linked Prompts</h4>

  {#if loading}
    <div class="text-center py-6 text-gray-500">Loading prompts...</div>
  {:else}
    <!-- System Prompts Section -->
    <div>
      <h5 class="font-bold mb-2 text-sm text-gray-600">System Prompts</h5>
      {#if linkedPrompts.length === 0}
        <p class="text-gray-400 italic text-sm">No system prompts linked</p>
      {:else}
        <div class="space-y-2">
          {#each linkedPrompts as link}
            {@const prompt = getPromptById(link.prompt_id)}
            {#if prompt}
              <div class="border-3 border-black p-3 bg-gray-50">
                <div class="flex items-center justify-between">
                  <div class="flex items-center flex-wrap gap-2">
                    <span class="font-bold">{prompt.title || "Untitled"}</span>
                    <span
                      class="text-xs px-2 py-0.5 bg-[#CCFF00] border border-black font-bold whitespace-nowrap"
                    >
                      Threshold: {link.threshold}
                    </span>
                  </div>
                  <div class="flex gap-2">
                    <button
                      onclick={() => toggleExpanded(prompt.id)}
                      class="p-1.5 border-2 border-black bg-white hover:bg-[#CCFF00] transition-all shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[2px] active:translate-y-[2px]"
                      title={expandedPrompts.has(prompt.id)
                        ? "Hide content"
                        : "Show content"}
                    >
                      {#if expandedPrompts.has(prompt.id)}
                        <EyeOff class="w-4 h-4" />
                      {:else}
                        <Eye class="w-4 h-4" />
                      {/if}
                    </button>
                    <button
                      onclick={() => unlinkPrompt(link.prompt_id)}
                      class="p-1.5 border-2 border-black bg-white hover:bg-red-200 text-red-600 transition-all shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[2px] active:translate-y-[2px]"
                      title="Unlink prompt"
                    >
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>
                </div>
                {#if expandedPrompts.has(prompt.id)}
                  <pre
                    class="mt-2 p-2 bg-white border-2 border-black text-xs overflow-x-auto whitespace-pre-wrap">{prompt.text}</pre>
                {/if}
              </div>
            {/if}
          {/each}
        </div>
      {/if}

      <!-- Available System Prompts -->
      <div class="mt-3">
        <h6 class="font-medium text-xs text-gray-500 mb-2">
          Available to Add:
        </h6>
        <div class="flex flex-wrap gap-2">
          {#each availablePrompts.filter((p) => p.is_active && !isPromptLinked(p.id)) as prompt}
            <button
              onclick={() => showAddModal(prompt, "system")}
              class="px-3 py-1 border-2 border-black bg-white hover:bg-[#CCFF00] text-sm font-medium transition-colors flex items-center gap-1"
            >
              <Plus class="w-3 h-3" />
              {prompt.title || "Untitled"}
            </button>
          {/each}
        </div>
      </div>
    </div>

    <!-- Custom Prompts Section -->
    <div class="mt-6">
      <div class="flex items-center justify-between mb-2">
        <h5 class="font-bold text-sm text-gray-600">Custom Prompts</h5>
        <button
          onclick={() => (showCreateForm = true)}
          class="px-3 py-1 border-2 border-[#FF8A00] bg-[#FF8A00] hover:bg-[#FF8A00]/80 text-sm font-bold transition-colors flex items-center gap-1"
        >
          <Plus class="w-4 h-4" />
          NEW
        </button>
      </div>

      {#if linkedCustomPrompts.length === 0}
        <p class="text-gray-400 italic text-sm">No custom prompts linked</p>
      {:else}
        <div class="space-y-2">
          {#each linkedCustomPrompts as link}
            {@const prompt = getCustomPromptById(link.custom_prompt_id)}
            {#if prompt}
              <div class="border-3 border-black p-3 bg-[#FF8A00]/10">
                <div class="flex items-center justify-between">
                  <div class="flex items-center flex-wrap gap-2">
                    <span class="font-bold">{prompt.title || "Untitled"}</span>
                    <span
                      class="text-xs px-2 py-0.5 bg-[#FF8A00] border border-black font-bold whitespace-nowrap"
                    >
                      Threshold: {link.threshold}
                    </span>
                  </div>
                  <div class="flex gap-2">
                    <button
                      onclick={() => toggleExpanded(prompt.id)}
                      class="p-1.5 border-2 border-black bg-white hover:bg-[#FF8A00] transition-all shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[2px] active:translate-y-[2px]"
                      title={expandedPrompts.has(prompt.id)
                        ? "Hide content"
                        : "Show content"}
                    >
                      {#if expandedPrompts.has(prompt.id)}
                        <EyeOff class="w-4 h-4" />
                      {:else}
                        <Eye class="w-4 h-4" />
                      {/if}
                    </button>
                    <button
                      onclick={() => unlinkCustomPrompt(link.custom_prompt_id)}
                      class="p-1.5 border-2 border-black bg-white hover:bg-red-200 text-red-600 transition-all shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[2px] active:translate-y-[2px]"
                      title="Unlink prompt"
                    >
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>
                </div>
                {#if expandedPrompts.has(prompt.id)}
                  <pre
                    class="mt-2 p-2 bg-white border-2 border-black text-xs overflow-x-auto whitespace-pre-wrap">{prompt.text}</pre>
                {/if}
              </div>
            {/if}
          {/each}
        </div>
      {/if}

      <!-- Available Custom Prompts -->
      <div class="mt-3">
        <h6 class="font-medium text-xs text-gray-500 mb-2">
          Available to Add:
        </h6>
        <div class="flex flex-wrap gap-2">
          {#each availableCustomPrompts.filter((p) => p.is_active && !isCustomPromptLinked(p.id)) as prompt}
            <button
              onclick={() => showAddModal(prompt, "custom")}
              class="px-3 py-1 border-2 border-[#FF8A00] bg-white hover:bg-[#FF8A00]/20 text-sm font-medium transition-colors flex items-center gap-1"
            >
              <Plus class="w-3 h-3" />
              {prompt.title || "Untitled"}
            </button>
          {/each}
        </div>
      </div>
    </div>
  {/if}
</div>

{#if addModal.show}
  <Modal
    message="Add prompt '{addModal.prompt.title || 'Untitled'}' to chat?"
    onConfirm={confirmAdd}
    onCancel={() =>
      (addModal = {
        show: false,
        prompt: null,
        type: "system",
        threshold: 0.3,
      })}
  >
    <div class="mt-4">
      <label class="font-bold block mb-2">Threshold (0.0 - 1.0)</label>
      <input
        type="number"
        bind:value={addModal.threshold}
        min="0"
        max="1"
        step="0.1"
        class="w-24 p-2 border-2 border-black"
      />
      <p class="text-xs text-gray-500 mt-1">Higher = stricter detection</p>
    </div>
  </Modal>
{/if}

{#if showCreateForm}
  <Modal
    title="Create New Prompt"
    confirmText={isCreating ? "Creating..." : "Create & Add"}
    confirmDisabled={!createForm.text.trim() || isCreating}
    onConfirm={createAndLink}
    onCancel={cancelCreate}
  >
    <div class="space-y-3">
      <div>
        <label class="block text-sm font-medium mb-1">Title (optional)</label>
        <input
          type="text"
          bind:value={createForm.title}
          placeholder="e.g., NFT Scam Detector"
          class="w-full border-2 border-black p-2"
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">Prompt Text</label>
        <textarea
          bind:value={createForm.text}
          placeholder="Describe what the AI should detect..."
          class="w-full border-2 border-black p-2 min-h-[100px]"
          required
        ></textarea>
      </div>

      <div>
        <label class="block text-sm font-medium mb-1"
          >Threshold (0.0 - 1.0)</label
        >
        <input
          type="number"
          bind:value={createForm.threshold}
          min="0"
          max="1"
          step="0.1"
          class="w-24 border-2 border-black p-2"
        />
        <p class="text-xs text-gray-500 mt-1">Higher = stricter detection</p>
      </div>
    </div>
  </Modal>
{/if}
