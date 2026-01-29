<script lang="ts">
  import { onMount } from "svelte";
  import { chats } from "./api";

  export let onSelectChat: (chatId: string) => void;

  let chatList: any[] = [];

  onMount(async () => {
    const res = await chats.list();
    chatList = res.chats;
  });
</script>

<div class="container">
  <h2>Chats</h2>
  <div class="chat-list">
    {#each chatList as chat}
      <div
        class="chat-item card"
        role="button"
        tabindex="0"
        on:click={() => onSelectChat(chat.id)}
        on:keydown={(e) => e.key === "Enter" && onSelectChat(chat.id)}
      >
        <strong>{chat.title || `Chat ${chat.platform_chat_id}`}</strong>
        <small class="chat-type">Type: {chat.type}</small>
      </div>
    {:else}
      <p class="no-chats">
        No chats yet. Connect your Telegram account in Settings to get started.
      </p>
    {/each}
  </div>
</div>

<style>
  .chat-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .chat-item {
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .chat-item:hover {
    background: var(--color-surface);
    border-color: var(--color-secondary);
  }

  .chat-type {
    color: var(--color-text-muted);
    display: block;
    margin-top: var(--spacing-xs);
  }

  .no-chats {
    text-align: center;
    color: var(--color-text-muted);
    font-style: italic;
    padding: var(--spacing-xl);
  }
</style>
