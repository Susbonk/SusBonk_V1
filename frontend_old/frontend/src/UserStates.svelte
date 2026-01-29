<script lang="ts">
  import { onMount } from "svelte";
  import { userStates } from "./api";
  import Modal from "./Modal.svelte";

  export let chatId: string;

  let states: any[] = [];
  let confirmModal: { show: boolean; state: any; action: "trust" | "untrust" } =
    { show: false, state: null, action: "trust" };

  const load = async () => {
    const res = await userStates.list(chatId);
    states = res.items;
  };

  onMount(load);

  const showConfirm = (state: any, action: "trust" | "untrust") => {
    confirmModal = { show: true, state, action };
  };

  const confirm = async () => {
    const { state, action } = confirmModal;
    confirmModal = { show: false, state: null, action: "trust" };

    if (action === "trust") {
      await userStates.update(chatId, state.id, { trusted: true });
    } else {
      await userStates.makeUntrusted(chatId, state.id);
    }
    await load();
  };
</script>

<div class="container">
  <div class="card">
    <h3>User States</h3>
    <p class="help-text">Messages count shows valid messages until reaching the minimum required for automatic trust.</p>
    <div class="table-container">
      <table class="user-states-table">
        <thead>
          <tr>
            <th>User ID</th>
            <th>Trusted</th>
            <th>Messages</th>
            <th>Joined</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each states as state}
            <tr>
              <td class="user-id">{state.external_user_id}</td>
              <td class="trust-status">
                <span class="status-badge {state.trusted ? 'trusted' : 'untrusted'}">
                  {state.trusted ? "✓" : "✗"}
                </span>
              </td>
              <td>{state.valid_messages}</td>
              <td class="join-date">
                {state.joined_at ? new Date(state.joined_at).toLocaleString() : "N/A"}
              </td>
              <td class="actions">
                {#if state.trusted}
                  <button class="btn-secondary" on:click={() => showConfirm(state, "untrust")}>
                    Make Untrusted
                  </button>
                {:else}
                  <button class="btn-primary" on:click={() => showConfirm(state, "trust")}>
                    Make Trusted
                  </button>
                  <button class="btn-secondary" on:click={() => showConfirm(state, "untrust")}>
                    Reset Stats
                  </button>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
</div>

{#if confirmModal.show}
  <Modal
    message={confirmModal.action === "trust"
      ? `Make user ${confirmModal.state.external_user_id} trusted?`
      : confirmModal.state.trusted
        ? `Make user ${confirmModal.state.external_user_id} untrusted?`
        : `Reset stats for user ${confirmModal.state.external_user_id}?`}
    onConfirm={confirm}
    onCancel={() =>
      (confirmModal = { show: false, state: null, action: "trust" })}
  />
{/if}

<style>
  h3 {
    margin-bottom: var(--spacing-md);
    color: var(--color-text);
  }
  
  .help-text {
    font-size: var(--font-size-sm);
    color: var(--color-text-muted);
    margin-bottom: var(--spacing-lg);
    font-style: italic;
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .user-states-table {
    width: 100%;
    border-collapse: collapse;
    background: var(--color-background);
  }
  
  .user-states-table th,
  .user-states-table td {
    border: 1px solid var(--color-border);
    padding: var(--spacing-sm);
    text-align: left;
  }
  
  .user-states-table th {
    background: var(--color-surface);
    font-weight: 600;
    color: var(--color-text);
  }
  
  .user-id {
    font-family: monospace;
    font-size: var(--font-size-sm);
  }
  
  .trust-status {
    text-align: center;
  }
  
  .status-badge {
    display: inline-block;
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--border-radius);
    font-weight: 600;
    font-size: var(--font-size-sm);
  }
  
  .status-badge.trusted {
    background: #dcfce7;
    color: #166534;
  }
  
  .status-badge.untrusted {
    background: #fef2f2;
    color: #991b1b;
  }
  
  .join-date {
    font-size: var(--font-size-sm);
    color: var(--color-text-muted);
  }
  
  .actions {
    white-space: nowrap;
  }
  
  .actions button {
    margin-right: var(--spacing-xs);
    font-size: var(--font-size-sm);
    padding: var(--spacing-xs) var(--spacing-sm);
  }
  
  .btn-secondary {
    background: var(--color-surface);
    border-color: var(--color-border);
    color: var(--color-text);
  }
  
  .btn-secondary:hover {
    background: var(--color-border);
  }
</style>
