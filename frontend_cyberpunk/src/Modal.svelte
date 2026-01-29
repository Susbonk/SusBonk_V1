<script lang="ts">
  export let message: string;
  export let onConfirm: () => void;
  export let onCancel: () => void;
</script>

<div
  class="overlay"
  role="button"
  tabindex="0"
  on:click={onCancel}
  on:keydown={(e) => e.key === "Escape" && onCancel()}
>
  <div
    class="modal"
    role="dialog"
    tabindex="-1"
    on:click|stopPropagation
    on:keydown|stopPropagation
  >
    <p>{message}</p>
    <slot></slot>
    <div class="button-row">
      <button class="btn-primary" on:click={onConfirm}>Confirm</button>
      <button on:click={onCancel}>Cancel</button>
    </div>
  </div>
</div>

<style>
  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  .modal {
    background: var(--color-background);
    padding: var(--spacing-lg);
    border-radius: var(--border-radius);
    min-width: 300px;
    max-width: 500px;
  }

  .modal p {
    margin-bottom: var(--spacing-md);
  }

  .button-row {
    display: flex;
    gap: var(--spacing-sm);
    justify-content: flex-end;
    margin-top: var(--spacing-md);
  }
</style>
