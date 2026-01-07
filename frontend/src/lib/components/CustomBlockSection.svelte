<script lang="ts">
  import { Plus, Trash2 } from 'lucide-svelte';

  interface CustomBlock {
    id: string;
    name: string;
    instructions: string;
  }

  let blocks = $state<CustomBlock[]>([
    { id: "1", name: "Competitor Mentions", instructions: "Block any mention of 'SafeMoon' or 'DogeCoin'. Only allow Bitcoin and Ethereum discussions." },
    { id: "2", name: "No FUD", instructions: "Bonk messages that contain 'rug pull', 'scam', or 'honey pot' without evidence." }
  ]);
  let isOpen = $state(false);
  let newName = $state("");
  let newInstructions = $state("");

  function handleSave() {
    if (!newName || !newInstructions) return;
    
    const newBlock: CustomBlock = {
      id: Date.now().toString(),
      name: newName,
      instructions: newInstructions
    };
    
    blocks = [...blocks, newBlock];
    isOpen = false;
    newName = "";
    newInstructions = "";
  }

  function handleDelete(id: string) {
    blocks = blocks.filter(b => b.id !== id);
  }
</script>

<div class="bg-white border-[4px] border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] p-4">
  <div class="flex items-center justify-between mb-4">
    <h3 style="font-family: Poppins, sans-serif; font-weight: 800; font-size: 16px;">
      Custom Blocks
    </h3>
    
    <button
      onclick={() => isOpen = true}
      class="bg-[#FF8A00] border-[2px] border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] px-3 py-1 text-sm font-bold flex items-center gap-1 transition-all active:shadow-none active:translate-x-[2px] active:translate-y-[2px]"
      style="font-family: Poppins, sans-serif;"
    >
      <Plus class="w-4 h-4" />
      NEW
    </button>
  </div>

  <div class="space-y-3">
    {#if blocks.length === 0}
      <div class="text-center py-8 text-gray-500 italic border-[2px] border-dashed border-gray-300">
        No custom rules yet.
      </div>
    {:else}
      {#each blocks as block (block.id)}
        <div class="border-[3px] border-black p-3 bg-gray-50 group hover:bg-[#fff9e6] transition-colors relative">
          <div class="flex justify-between items-start mb-2">
            <h4 class="font-bold text-lg leading-tight">{block.name}</h4>
            <button 
              onclick={() => handleDelete(block.id)}
              class="text-gray-400 hover:text-red-600 transition-colors"
            >
              <Trash2 class="w-5 h-5" />
            </button>
          </div>
          <p class="text-sm text-gray-600 font-medium line-clamp-2">
            "{block.instructions}"
          </p>
        </div>
      {/each}
    {/if}
  </div>
</div>

<!-- Simple Modal -->
{#if isOpen}
  <div 
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" 
    onclick={() => isOpen = false}
    onkeydown={(e) => e.key === 'Escape' && (isOpen = false)}
    role="button"
    tabindex="0"
  >
    <div class="bg-white border-[4px] border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] max-w-md w-full p-6" onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()} role="dialog" tabindex="-1">
      <h2 style="font-family: Poppins, sans-serif; font-weight: 800; font-size: 24px;" class="mb-2">
        New Custom Block
      </h2>
      <p style="font-family: Poppins, sans-serif;" class="text-gray-600 mb-4">
        Define a new rule for SusBonk using natural language.
      </p>
      
      <div class="space-y-4 mb-6">
        <div>
          <label for="block-name" class="font-bold mb-2 block">Name</label>
          <input
            id="block-name"
            type="text"
            bind:value={newName}
            placeholder="e.g. No Competitors"
            class="w-full border-[3px] border-black px-3 py-2 focus:outline-none focus:border-[#CCFF00]"
          />
        </div>
        <div>
          <label for="block-instructions" class="font-bold mb-2 block">LLM Instructions</label>
          <textarea
            id="block-instructions"
            bind:value={newInstructions}
            placeholder="Describe what the bot should look for..."
            class="w-full border-[3px] border-black px-3 py-2 min-h-[100px] focus:outline-none focus:border-[#CCFF00]"
          ></textarea>
        </div>
      </div>
      
      <button
        onclick={handleSave}
        class="bg-[#CCFF00] w-full border-[3px] border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] py-3 px-4 font-black text-lg transition-all active:shadow-none active:translate-x-[4px] active:translate-y-[4px] hover:bg-[#d9ff33]"
        style="font-family: Poppins, sans-serif;"
      >
        SAVE RULE
      </button>
    </div>
  </div>
{/if}
