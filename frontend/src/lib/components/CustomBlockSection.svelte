<script lang="ts">
  import { Plus, Trash2, X } from 'lucide-svelte';

  interface CustomBlock {
    id: string;
    name: string;
    instructions: string;
  }

  let blocks = $state<CustomBlock[]>([
    { id: "1", name: "Competitor Mentions", instructions: "Block any mention of 'SafeMoon' or 'DogeCoin'. Only allow Bitcoin and Ethereum discussions." },
    { id: "2", name: "No FUD", instructions: "Bonk messages that contain 'rug pull', 'scam', or 'honey pot' without evidence." }
  ]);
  let isModalOpen = $state(false);
  let newName = $state("");
  let newInstructions = $state("");

  function saveBlock() {
    if (!newName || !newInstructions) return;
    blocks = [...blocks, { id: Date.now().toString(), name: newName, instructions: newInstructions }];
    closeModal();
  }

  function deleteBlock(id: string, name: string) {
    if (confirm(`Delete "${name}"? This cannot be undone.`)) {
      blocks = blocks.filter(b => b.id !== id);
    }
  }

  function closeModal() {
    isModalOpen = false;
    newName = "";
    newInstructions = "";
  }
</script>

<div class="card">
  <div class="flex items-center justify-between mb-4">
    <h3 class="font-extrabold">Custom Blocks</h3>
    <button onclick={() => isModalOpen = true} class="bg-[#FF8A00] border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] px-3 py-1 text-sm font-bold flex items-center gap-1 transition-all active:shadow-none active:translate-x-[2px] active:translate-y-[2px]">
      <Plus class="w-4 h-4" />
      NEW
    </button>
  </div>

  <div class="space-y-3">
    {#if blocks.length === 0}
      <div class="text-center py-8 text-gray-500 italic border-2 border-dashed border-gray-300">No custom rules yet.</div>
    {:else}
      {#each blocks as block (block.id)}
        <div class="border-3 border-black p-3 bg-gray-50 hover:bg-[#fff9e6] transition-colors">
          <div class="flex justify-between items-start mb-2">
            <h4 class="font-bold text-lg leading-tight">{block.name}</h4>
            <button onclick={() => deleteBlock(block.id, block.name)} class="text-gray-400 hover:text-red-600 transition-colors">
              <Trash2 class="w-5 h-5" />
            </button>
          </div>
          <p class="text-sm text-gray-600 font-medium line-clamp-2">"{block.instructions}"</p>
        </div>
      {/each}
    {/if}
  </div>
</div>

<!-- Modal -->
{#if isModalOpen}
  <div class="modal-backdrop" onclick={closeModal} onkeydown={(e) => e.key === 'Escape' && closeModal()} role="button" tabindex="0">
    <div class="modal-content" onclick={(e) => e.stopPropagation()} role="dialog" tabindex="-1">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-extrabold">New Custom Block</h2>
        <button onclick={closeModal} class="p-1 hover:bg-gray-100"><X class="w-6 h-6" /></button>
      </div>
      <p class="text-gray-600 mb-4">Define a new rule for SusBonk using natural language.</p>
      
      <div class="space-y-4 mb-6">
        <div>
          <label for="block-name" class="font-bold mb-2 block">Name</label>
          <input id="block-name" type="text" bind:value={newName} placeholder="e.g. No Competitors" class="w-full border-3 border-black px-3 py-2 focus:outline-none focus:border-[#CCFF00]" />
        </div>
        <div>
          <label for="block-instructions" class="font-bold mb-2 block">LLM Instructions</label>
          <textarea id="block-instructions" bind:value={newInstructions} placeholder="Describe what the bot should look for..." class="w-full border-3 border-black px-3 py-2 min-h-[100px] focus:outline-none focus:border-[#CCFF00]"></textarea>
        </div>
      </div>
      
      <button onclick={saveBlock} class="btn btn-primary w-full py-3 text-lg font-black">SAVE RULE</button>
    </div>
  </div>
{/if}
