<script lang="ts">
  import { onMount } from "svelte";
  import { deletedMessages, userStates } from "./api";
  import Modal from "./Modal.svelte";

  export let chatId: string;

  let messages: any[] = [];
  let confirmModal: { show: boolean; msg: any } = { show: false, msg: null };

  onMount(async () => {
    const res = await deletedMessages.list(chatId);
    messages = res.items;
  });

  const showConfirm = (msg: any) => {
    confirmModal = { show: true, msg };
  };

  const makeTrusted = async () => {
    const msg = confirmModal.msg;
    confirmModal = { show: false, msg: null };
    await userStates.update(chatId, msg.user_state_id, { trusted: true });
    // Reload messages after making user trusted
    const res = await deletedMessages.list(chatId);
    messages = res.items;
  };
</script>

<div class="container">
  <div class="card">
    <h3>Deleted Messages</h3>
    <div class="messages-list">
      {#each messages as msg}
        <div class="message card">
          <div class="message-header">
            <div>
              <strong>{msg.nickname || `User ${msg.platform_user_id}`}</strong>
              <small class="timestamp">{new Date(msg.timestamp * 1000).toLocaleString()}</small>
            </div>
            {#if msg.user_state_id}
              <button class="btn-primary" on:click={() => showConfirm(msg)}>Make Trusted</button>
            {/if}
          </div>
          <p class="message-text">{msg.message_text}</p>
        </div>
      {/each}
    </div>
  </div>
</div>

{#if confirmModal.show}
  <Modal
    message="Make user {confirmModal.msg.nickname ||
      confirmModal.msg.platform_user_id} trusted?"
    onConfirm={makeTrusted}
    onCancel={() => (confirmModal = { show: false, msg: null })}
  />
{/if}

<style>
  h3 {
    margin-bottom: var(--spacing-lg);
    color: var(--color-text);
  }
  
  .messages-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .message {
    background: var(--color-surface);
  }
  
  .message-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--spacing-sm);
  }
  
  .message-header > div {
    display: flex;
    flex-direction: column;
  }
  
  .message-text {
    margin-bottom: var(--spacing-md);
    line-height: 1.6;
  }
  
  .timestamp {
    color: var(--color-text-muted);
    font-size: var(--font-size-sm);
  }
</style>
