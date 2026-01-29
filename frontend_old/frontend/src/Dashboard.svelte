<script lang="ts">
    import { ChevronDown, LogOut } from "lucide-svelte";
    import { chatsState } from "./lib/stores.js";
    import type { TabType } from "./lib/types.js";
    import ChatSettings from "./ChatSettings.svelte";
    import UserStates from "./UserStates.svelte";
    import DeletedMessages from "./DeletedMessages.svelte";
    import SettingsPanel from "./Settings.svelte";

    interface Props {
        activeTab: TabType;
        onLogout: () => void;
    }

    let { activeTab, onLogout }: Props = $props();

    // Group selector state
    let isGroupDropdownOpen = $state(false);

    function handleGroupChange(chatId: string) {
        const chat = $chatsState.chats.find((c) => c.id === chatId);
        if (chat) {
            chatsState.update((state) => ({ ...state, activeChat: chat }));
        }
        isGroupDropdownOpen = false;
    }
</script>

<div class="min-h-full bg-white pb-safe">
    <div class="max-w-4xl mx-auto h-full">
        {#if activeTab === "dashboard"}
            <div class="p-4 space-y-4">
                <!-- Header -->
                <div class="flex items-center justify-between">
                    <div class="flex-1 flex items-center gap-4">
                        <img
                            src="/bonk_dog.jpg"
                            alt="SusBonk"
                            class="w-16 h-16 border-3 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] rounded-lg object-cover"
                        />
                        <div>
                            <h1 class="text-2xl font-black tracking-tight">
                                SusBonk Dashboard
                            </h1>
                            <p class="text-gray-600">Manage your groups</p>
                        </div>
                    </div>
                </div>

                <!-- Group Selector -->
                <div class="relative border-3 border-black bg-gray-50 p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                    <h2 class="text-lg font-black mb-1">Select Your Group</h2>
                    <p class="text-sm text-gray-500 mb-3">
                        Pick a group to manage its settings and view logs.
                    </p>
                    <button
                        onclick={() =>
                            (isGroupDropdownOpen = !isGroupDropdownOpen)}
                        class="w-full bg-white hover:bg-gray-50 border-3 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] h-14 px-4 flex items-center justify-between font-bold text-lg transition-all active:translate-x-[2px] active:translate-y-[2px] active:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)]"
                    >
                        <span class="flex items-center gap-2">
                            {#if $chatsState.activeChat}
                                <span
                                    class="w-3 h-3 rounded-full bg-[#CCFF00] border-2 border-black"
                                ></span>
                                {$chatsState.activeChat.title}
                            {:else}
                                <span class="text-gray-400">Tap to choose a group...</span>
                            {/if}
                        </span>
                        <ChevronDown
                            class="w-6 h-6 transition-transform {isGroupDropdownOpen
                                ? 'rotate-180'
                                : ''}"
                        />
                    </button>

                    {#if isGroupDropdownOpen}
                        <div
                            class="absolute z-20 left-0 right-0 mt-2 mx-4 bg-white border-3 border-black shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] max-h-60 overflow-y-auto"
                        >
                            {#each $chatsState.chats as chat (chat.id)}
                                <button
                                    onclick={() => handleGroupChange(chat.id)}
                                    class="w-full px-4 py-3 text-left hover:bg-[#CCFF00] font-medium border-b border-black/20 last:border-b-0 transition-colors"
                                >
                                    {chat.title || "Unnamed Group"}
                                </button>
                            {/each}
                            {#if $chatsState.chats.length === 0}
                                <div class="px-4 py-3 text-gray-500 italic">
                                    No groups available. Connect Telegram in
                                    Settings.
                                </div>
                            {/if}
                        </div>
                    {/if}
                </div>

                {#if $chatsState.activeChat}
                    <!-- Chat Settings -->
                    <ChatSettings chatId={$chatsState.activeChat.id} />
                {:else}
                    <div class="card text-center py-8">
                        <p class="text-gray-500 italic">
                            Select a group to view settings.
                        </p>
                    </div>
                {/if}
            </div>
        {/if}

        {#if activeTab === "logs"}
            <div class="p-4 space-y-4">
                <h2 class="text-2xl font-black">
                    Logs for {$chatsState.activeChat?.title ||
                        "No Group Selected"}
                </h2>
                {#if $chatsState.activeChat}
                    <DeletedMessages chatId={$chatsState.activeChat.id} />
                    <UserStates chatId={$chatsState.activeChat.id} />
                {:else}
                    <div class="card text-center py-8">
                        <p class="text-gray-500 italic">
                            Select a group on Dashboard to view logs.
                        </p>
                    </div>
                {/if}
            </div>
        {/if}

        {#if activeTab === "settings"}
            <div class="p-4 space-y-4">
                <h2 class="text-2xl font-black">Account Settings</h2>
                <p class="text-gray-600 -mt-2">
                    Manage your account connections
                </p>

                <!-- Settings Content -->
                <div class="mt-4">
                    <SettingsPanel />
                </div>
            </div>
        {/if}
    </div>
</div>
