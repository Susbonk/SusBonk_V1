<script lang="ts">
  import { onMount } from "svelte";
  import { userStates, deletedMessages } from "./api";
  import Modal from "./Modal.svelte";
  import {
    Shield,
    ShieldOff,
    RefreshCw,
    MessageSquare,
    Calendar,
    ChevronDown,
  } from "lucide-svelte";

  interface Props {
    chatId: string;
  }

  let { chatId }: Props = $props();

  const PAGE_SIZE = 10;

  let states = $state<any[]>([]);
  let nicknameMap = $state<Record<string, string>>({});
  let isLoading = $state(false);
  let isExpanded = $state(true);
  let visibleCount = $state(PAGE_SIZE);

  const visibleStates = $derived(states.slice(0, visibleCount));
  const hasMore = $derived(visibleCount < states.length);

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

  let isUpdating = $state<string | null>(null);
  let confirmModal = $state<{
    show: boolean;
    state: any;
    action: "trust" | "untrust";
  }>({
    show: false,
    state: null,
    action: "trust",
  });

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
      const [statesRes, msgsRes] = await Promise.all([
        userStates.list(chatId),
        deletedMessages.list(chatId),
      ]);
      states = statesRes.items;
      // Build nickname lookup from deleted messages
      const msgs = msgsRes.items || [];
      const map: Record<string, string> = {};
      for (const m of msgs) {
        if (m.nickname && m.platform_user_id) {
          map[String(m.platform_user_id)] = m.nickname;
        }
      }
      nicknameMap = map;
    } finally {
      isLoading = false;
    }
  }

  function showConfirm(state: any, action: "trust" | "untrust") {
    confirmModal = { show: true, state, action };
  }

  async function confirm() {
    const { state, action } = confirmModal;
    confirmModal = { show: false, state: null, action: "trust" };
    isUpdating = state.id;

    try {
      if (action === "trust") {
        await userStates.update(chatId, state.id, { trusted: true });
      } else {
        await userStates.makeUntrusted(chatId, state.id);
      }
      await load();
    } finally {
      isUpdating = null;
    }
  }

  function formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  }

  const trustedCount = $derived(states.filter((u) => u.trusted).length);
  const untrustedCount = $derived(states.filter((u) => !u.trusted).length);
</script>

<div class="space-y-4">
  <div class="flex items-center justify-between">
    <button
      onclick={() => (isExpanded = !isExpanded)}
      class="flex items-center gap-2 cursor-pointer"
    >
      <h3 class="font-black text-lg tracking-tight">User States</h3>
      <span class="text-sm font-bold bg-black text-white px-2 py-0.5"
        >{states.length} members</span
      >
      <ChevronDown
        class="w-5 h-5 transition-transform {isExpanded ? 'rotate-180' : ''}"
      />
    </button>
    <button
      onclick={load}
      class="p-2 border-3 border-black bg-white hover:bg-[#CCFF00] transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[4px] active:translate-y-[4px]"
      disabled={isLoading}
    >
      <RefreshCw class="w-5 h-5 {isLoading ? 'animate-spin' : ''}" />
    </button>
  </div>

  {#if isExpanded}
    <!-- Stats Bar -->
    <div class="flex gap-3">
      <div
        class="flex-1 p-3 border-3 border-black bg-white shadow-[4px_4px_0px_0px_#CCFF00] relative overflow-hidden"
      >
        <div class="absolute right-[-10px] top-[-10px] opacity-10 rotate-12">
          <Shield class="w-24 h-24 text-[#CCFF00]" />
        </div>
        <div class="text-3xl font-black text-black">{trustedCount}</div>
        <div class="text-sm font-bold text-black flex items-center gap-1">
          <Shield class="w-4 h-4" /> Good Hooman
        </div>
      </div>
      <div
        class="flex-1 p-3 border-3 border-black bg-white shadow-[4px_4px_0px_0px_rgba(239,68,68,1)] relative overflow-hidden"
      >
        <div class="absolute right-[-10px] top-[-10px] opacity-10 rotate-12">
          <ShieldOff class="w-24 h-24 text-red-600" />
        </div>
        <div class="text-3xl font-black text-red-600">{untrustedCount}</div>
        <div class="text-sm font-bold text-black flex items-center gap-1">
          <ShieldOff class="w-4 h-4" /> Bad Robots
        </div>
      </div>
    </div>

    <p class="text-sm text-gray-500 italic">
      Messages count shows valid messages until reaching the minimum required
      for automatic trust.
    </p>

    <!-- Members List -->
    <div class="space-y-3">
      {#if isLoading}
        <div class="text-center py-8 text-gray-500">Loading members...</div>
      {:else if states.length === 0}
        <div
          class="text-center py-8 text-gray-500 italic border-3 border-dashed border-gray-300"
        >
          No members yet. Members will appear when they join your group.
        </div>
      {:else}
        {#each visibleStates as state}
          {@const isBeingUpdated = isUpdating === state.id}
          <div
            class="border-3 border-black bg-white transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] {isBeingUpdated
              ? 'opacity-50'
              : ''}"
          >
            <div
              class="flex items-center justify-between p-3 gap-4 overflow-x-auto scrollbar-hide"
            >
              <!-- Left: Name & Badges -->
              <div class="flex items-center gap-3 min-w-max">
                {#if state.trusted}
                  <div
                    class="w-8 h-8 bg-[#CCFF00] border-2 border-black flex items-center justify-center"
                  >
                    <Shield class="w-4 h-4 text-black" />
                  </div>
                {:else}
                  <div
                    class="w-8 h-8 bg-red-400 border-2 border-black flex items-center justify-center"
                  >
                    <ShieldOff class="w-4 h-4 text-black" />
                  </div>
                {/if}

                <div>
                  <div class="font-black text-lg">
                    {nicknameMap[String(state.external_user_id)] ||
                      `User ${state.external_user_id}`}
                  </div>
                  <div
                    class="flex items-center gap-2 text-xs font-bold text-gray-500"
                  >
                    <span class="flex items-center gap-1"
                      ><MessageSquare class="w-3 h-3" />
                      {state.valid_messages}</span
                    >
                    <span>•</span>
                    <span class="flex items-center gap-1"
                      ><Calendar class="w-3 h-3" />
                      {formatDate(state.joined_at || state.created_at)}</span
                    >
                  </div>
                </div>
              </div>

              <!-- Right: Whitelist / Blacklist Buttons -->
              <div class="flex items-center gap-2">
                {#if !state.trusted}
                  <button
                    onclick={(e) => {
                      e.stopPropagation();
                      showConfirm(state, "trust");
                    }}
                    class="h-8 px-3 flex items-center gap-1 border-2 border-black bg-[#CCFF00] hover:bg-[#d9ff33] font-black text-xs uppercase transition-all active:shadow-none active:translate-x-[2px] active:translate-y-[2px] shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                    disabled={isBeingUpdated}
                  >
                    <Shield class="w-3.5 h-3.5" />
                    Whitelist
                  </button>
                {:else}
                  <button
                    onclick={(e) => {
                      e.stopPropagation();
                      showConfirm(state, "untrust");
                    }}
                    class="h-8 px-3 flex items-center gap-1 border-2 border-black bg-red-400 hover:bg-red-500 text-white font-black text-xs uppercase transition-all active:shadow-none active:translate-x-[2px] active:translate-y-[2px] shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                    disabled={isBeingUpdated}
                  >
                    <ShieldOff class="w-3.5 h-3.5" />
                    Blacklist
                  </button>
                {/if}
              </div>
            </div>
          </div>
        {/each}

        {#if hasMore}
          <div bind:this={sentinelEl} class="py-4 text-center text-sm text-gray-400 font-bold">
            Loading more...
          </div>
        {/if}
      {/if}
    </div>
  {/if}
</div>

{#if confirmModal.show}
  <Modal
    message={confirmModal.action === "trust"
      ? `Whitelist ${nicknameMap[String(confirmModal.state.external_user_id)] || `user ${confirmModal.state.external_user_id}`}?`
      : `Blacklist ${nicknameMap[String(confirmModal.state.external_user_id)] || `user ${confirmModal.state.external_user_id}`}?`}
    onConfirm={confirm}
    onCancel={() =>
      (confirmModal = { show: false, state: null, action: "trust" })}
  />
{/if}
