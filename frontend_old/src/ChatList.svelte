<script lang="ts">
  import { onMount } from "svelte";
  import { chats } from "./api";
  import { ChevronRight, MessageSquare } from "lucide-svelte";

  interface Props {
    onSelectChat: (chatId: string) => void;
  }

  let { onSelectChat }: Props = $props();

  let chatList = $state<any[]>([]);
  let isLoading = $state(true);

  onMount(async () => {
    try {
      const res = await chats.list();
      chatList = res.chats || [];
    } finally {
      isLoading = false;
    }
  });
</script>

<div class="space-y-4">
  <h2 class="text-2xl font-black tracking-tight">Your Chats</h2>

  {#if isLoading}
    <div class="text-center py-8 text-gray-500">Loading chats...</div>
  {:else if chatList.length === 0}
    <div class="card text-center py-8 bg-[#CCFF00]/20">
      <MessageSquare class="w-12 h-12 mx-auto text-gray-400 mb-4" />
      <p class="font-bold text-lg mb-2">No chats yet</p>
      <p class="text-gray-600">
        Connect your Telegram account in Settings to get started.
      </p>
    </div>
  {:else}
    <div class="space-y-2">
      {#each chatList as chat}
        <button
          onclick={() => onSelectChat(chat.id)}
          class="w-full card flex items-center justify-between hover:bg-[#CCFF00]/20 transition-colors cursor-pointer"
        >
          <div class="text-left">
            <strong class="font-bold"
              >{chat.title || `Chat ${chat.platform_chat_id}`}</strong
            >
            <span class="block text-sm text-gray-500 mt-1"
              >Type: {chat.type}</span
            >
          </div>
          <ChevronRight class="w-5 h-5 text-gray-400" />
        </button>
      {/each}
    </div>
  {/if}
</div>
