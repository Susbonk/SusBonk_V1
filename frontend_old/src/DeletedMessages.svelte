<script lang="ts">
  import { onMount } from "svelte";
  import { deletedMessages, userStates } from "./api";
  import Modal from "./Modal.svelte";
  import { Trash2, Shield, User as UserIcon, ChevronDown } from "lucide-svelte";

  interface Props {
    chatId: string;
  }

  let { chatId }: Props = $props();

  const PAGE_SIZE = 10;

  let messages = $state<any[]>([]);
  let states = $state<any[]>([]);
  let isLoading = $state(false);
  let isExpanded = $state(true);
  let visibleCount = $state(PAGE_SIZE);

  const visibleMessages = $derived(messages.slice(0, visibleCount));
  const hasMore = $derived(visibleCount < messages.length);

  let sentinelEl: HTMLDivElement | undefined = $state();

  $effect(() => {
    if (!sentinelEl) return;
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore) {
          visibleCount += PAGE_SIZE;
        }
      },
      { rootMargin: "200px" },
    );
    observer.observe(sentinelEl);
    return () => observer.disconnect();
  });
  let confirmModal = $state<{
    show: boolean;
    stateId: string;
    userId: string;
  }>({
    show: false,
    stateId: "",
    userId: "",
  });

  // Helper to find state
  function findState(userId: string) {
    // Try matching by user_id or external_user_id
    return states.find(
      (s) =>
        s.user_id === userId ||
        s.external_user_id?.toString() === userId?.toString(),
    );
  }

  onMount(async () => {
    await load();
  });

  $effect(() => {
    if (chatId) {
      load();
    }
  });

  async function load() {
    isLoading = true;
    try {
      const [msgsRes, statesRes] = await Promise.all([
        deletedMessages.list(chatId),
        userStates.list(chatId),
      ]);
      messages = msgsRes.messages || msgsRes.items || [];
      states = statesRes.items || [];
    } catch (err) {
      console.error("Failed to load deleted messages:", err);
      messages = [];
    } finally {
      isLoading = false;
    }
  }

  function formatDate(ts: number | string): string {
    const num = typeof ts === "string" ? Number(ts) : ts;
    // If timestamp is in seconds (< 1e12), convert to ms
    const ms = num < 1e12 ? num * 1000 : num;
    return new Date(ms).toLocaleString();
  }

  async function makeTrusted() {
    try {
      await userStates.update(chatId, confirmModal.stateId, { trusted: true });
      // Reload
      await load();
    } catch (err) {
      alert("Failed to update user trust state");
    } finally {
      confirmModal.show = false;
    }
  }
</script>

<div class="space-y-4">
  <button
    onclick={() => (isExpanded = !isExpanded)}
    class="w-full flex items-center justify-between cursor-pointer"
  >
    <div class="flex items-center gap-3">
      <div
        class="w-10 h-10 border-3 border-black bg-[#CCFF00] flex items-center justify-center shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
      >
        <Trash2 class="w-6 h-6 text-black" />
      </div>
      <div class="text-left">
        <h3 class="font-black text-xl tracking-tight">Deleted Messages</h3>
        <span class="text-sm font-bold bg-black text-white px-2 py-0.5"
          >{messages.length} blocked</span
        >
      </div>
    </div>
    <ChevronDown
      class="w-6 h-6 transition-transform {isExpanded ? 'rotate-180' : ''}"
    />
  </button>

  {#if isExpanded}
    {#if isLoading}
      <div class="text-center py-6 text-gray-500">Loading...</div>
    {:else if messages.length === 0}
      <div
        class="text-center py-8 bg-gray-50 border-3 border-dashed border-gray-300 flex flex-col items-center"
      >
        <img
          src="/bonk_chilling.jpg"
          alt="Chilling Doggo"
          class="w-48 h-auto mb-4 object-contain drop-shadow-md"
        />
        <p class="text-gray-500 italic font-bold">No deleted messages yet.</p>
        <p class="text-xs text-gray-400 mt-1">
          Spam messages will appear here when detected.
        </p>
      </div>
    {:else}
      <div class="space-y-2">
        {#each visibleMessages as msg}
          {@const state = findState(msg.platform_user_id?.toString())}
          <div
            class="border-3 border-black p-3 bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] transition-all"
          >
            <div
              class="flex items-start justify-between mb-3 border-b-2 border-dashed border-gray-200 pb-2"
            >
              <div class="flex items-center gap-2">
                <div>
                  <div class="font-bold text-sm">
                    {msg.nickname ||
                      state?.user?.username ||
                      state?.external_user_id ||
                      msg.platform_user_id ||
                      "Unknown"}
                  </div>
                  <div class="text-xs text-gray-500 font-mono">
                    {formatDate(msg.timestamp)}
                  </div>
                </div>
              </div>

              {#if state && !state.trusted}
                <button
                  onclick={() =>
                    (confirmModal = {
                      show: true,
                      stateId: state.id,
                      userId: msg.platform_user_id?.toString(),
                    })}
                  class="bg-[#CCFF00] hover:bg-[#d9ff33] border-2 border-black px-3 py-1 text-xs font-black flex items-center gap-1 transition-all shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[2px] active:translate-y-[2px]"
                >
                  <Shield class="w-3 h-3" />
                  TRUST
                </button>
              {/if}
            </div>
            <div class="relative pl-3 border-l-4 border-red-500 my-2">
              <p
                class="text-sm font-medium whitespace-pre-wrap break-words italic text-gray-800"
              >
                "{msg.message_text || "No content"}"
              </p>
            </div>

            {#if msg.reason}
              <div class="mt-3 flex justify-end">
                <span
                  class="inline-flex items-center px-2 py-1 bg-red-100 border-2 border-red-500 text-red-700 text-xs font-bold uppercase gap-1"
                >
                  <Trash2 class="w-3 h-3" />
                  {msg.reason}
                </span>
              </div>
            {/if}
          </div>
        {/each}
      </div>

      {#if hasMore}
        <div
          bind:this={sentinelEl}
          class="py-4 text-center text-sm text-gray-400 font-bold"
        >
          Loading more...
        </div>
      {/if}
    {/if}
  {/if}
</div>

{#if confirmModal.show}
  <Modal
    message={`Make user ${confirmModal.userId} trusted?`}
    onConfirm={makeTrusted}
    onCancel={() => (confirmModal = { show: false, stateId: "", userId: "" })}
  />
{/if}
