<script lang="ts">
  import { X } from "lucide-svelte";
  import { fly } from "svelte/transition";

  interface Props {
    title?: string;
    message?: string;
    confirmText?: string;
    confirmDisabled?: boolean;
    onConfirm: () => void;
    onCancel: () => void;
    children?: any;
  }

  let {
    title = "Confirm",
    message = "",
    confirmText = "Confirm",
    confirmDisabled = false,
    onConfirm,
    onCancel,
    children,
  }: Props = $props();
</script>

<div
  class="modal-backdrop"
  onclick={onCancel}
  onkeydown={(e) => e.key === "Escape" && onCancel()}
  role="button"
  tabindex="0"
>
  <div
    class="modal-content"
    onclick={(e) => e.stopPropagation()}
    onkeydown={(e) => e.stopPropagation()}
    role="dialog"
    tabindex="-1"
    transition:fly={{ y: 50, duration: 200 }}
  >
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-black text-lg">{title}</h3>
      <button
        onclick={onCancel}
        class="p-1 border-2 border-black hover:bg-red-200 transition-all shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[2px] active:translate-y-[2px]"
      >
        <X class="w-5 h-5" />
      </button>
    </div>

    {#if message}
      <p class="text-gray-700 mb-4">{message}</p>
    {/if}

    {#if children}
      {@render children()}
    {/if}

    <div class="flex gap-3 mt-6">
      <button onclick={onCancel} class="flex-1 btn py-2"> Cancel </button>
      <button
        onclick={onConfirm}
        disabled={confirmDisabled}
        class="flex-1 btn btn-primary py-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {confirmText}
      </button>
    </div>
  </div>
</div>
