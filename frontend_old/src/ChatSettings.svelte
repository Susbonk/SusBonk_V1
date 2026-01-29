<script lang="ts">
  import { onMount } from "svelte";
  import { chats } from "./api";
  import { slide } from "svelte/transition";
  import {
    Settings,
    Sliders,
    MessageSquare,
    Save,
    X,
    Plus,
    Trash2,
  } from "lucide-svelte";
  import ChatPrompts from "./ChatPrompts.svelte";

  interface Props {
    chatId: string;
  }

  let { chatId }: Props = $props();

  let settings = $state<any>(null);
  let editing = $state(false);
  let isSaving = $state(false);
  let activeSection = $state<"detection" | "cleanup" | "prompts">("detection");
  let newMention = $state("");
  let newDomain = $state("");

  import { chatsState } from "./lib/stores.js";

  onMount(async () => {
    await loadSettings();
  });

  $effect(() => {
    // Reload when chatId changes
    if (chatId) {
      loadSettings();
    }
  });

  async function loadSettings() {
    try {
      settings = await chats.get(chatId);
    } catch (err) {
      // DEV MODE: Use mock data from store if API fails
      console.warn("API unavailable, using mock data:", err);
      const chatFromStore = $chatsState.chats.find((c) => c.id === chatId);
      settings = chatFromStore || {
        id: chatId,
        title: "Mock Chat",
        type: "supergroup",
        enable_ai_check: true,
        cleanup_mentions: false,
        cleanup_emojis: false,
        cleanup_links: true,
        cleanup_emails: false,
        max_emoji_count: 5,
        min_messages_required: 5,
        min_observation_minutes: 60,
      };
    }
    if (!settings.allowed_mentions) settings.allowed_mentions = [];
    if (!settings.allowed_link_domains) settings.allowed_link_domains = [];
  }

  async function save() {
    isSaving = true;
    try {
      await chats.update(chatId, {
        enable_ai_check: settings.enable_ai_check,
        cleanup_mentions: settings.cleanup_mentions,
        allowed_mentions: settings.allowed_mentions,
        cleanup_emojis: settings.cleanup_emojis,
        max_emoji_count: settings.max_emoji_count,
        cleanup_links: settings.cleanup_links,
        allowed_link_domains: settings.allowed_link_domains,
        cleanup_emails: settings.cleanup_emails,
        min_messages_required: settings.min_messages_required,
        min_observation_minutes: settings.min_observation_minutes,
      });
      editing = false;
    } catch (err) {
      alert("Failed to save settings");
    } finally {
      isSaving = false;
    }
  }

  function addMention() {
    if (newMention) {
      settings.allowed_mentions = [...settings.allowed_mentions, newMention];
      newMention = "";
    }
  }

  function removeMention(idx: number) {
    settings.allowed_mentions = settings.allowed_mentions.filter(
      (_: any, i: number) => i !== idx,
    );
  }

  function addDomain() {
    if (newDomain) {
      settings.allowed_link_domains = [
        ...settings.allowed_link_domains,
        newDomain,
      ];
      newDomain = "";
    }
  }

  function removeDomain(idx: number) {
    settings.allowed_link_domains = settings.allowed_link_domains.filter(
      (_: any, i: number) => i !== idx,
    );
  }
</script>

{#if settings}
  <div class="card">
    <!-- Header removed as per user request (redundant group name) -->

    <!-- Section Tabs -->
    <div class="flex border-3 border-black mb-4">
      <button
        onclick={() => (activeSection = "detection")}
        class="flex-1 py-2 px-3 font-bold text-sm flex items-center justify-center gap-1 transition-colors {activeSection ===
        'detection'
          ? 'bg-[#CCFF00]'
          : 'bg-white hover:bg-gray-50'}"
      >
        <Sliders class="w-4 h-4" />
        Detection
      </button>
      <button
        onclick={() => (activeSection = "cleanup")}
        class="flex-1 py-2 px-3 font-bold text-sm flex items-center justify-center gap-1 border-l-3 border-black transition-colors {activeSection ===
        'cleanup'
          ? 'bg-[#CCFF00]'
          : 'bg-white hover:bg-gray-50'}"
      >
        <MessageSquare class="w-4 h-4" />
        Cleanup
      </button>
      <button
        onclick={() => (activeSection = "prompts")}
        class="flex-1 py-2 px-3 font-bold text-sm flex items-center justify-center gap-1 border-l-3 border-black transition-colors {activeSection ===
        'prompts'
          ? 'bg-[#CCFF00]'
          : 'bg-white hover:bg-gray-50'}"
      >
        <MessageSquare class="w-4 h-4" />
        Prompts
      </button>
    </div>

    {#if activeSection === "detection"}
      <div class="space-y-4" transition:slide>
        <!-- AI Detection Toggle -->
        <label
          class="flex items-center justify-between p-3 border-3 border-black bg-gray-50"
        >
          <div>
            <span class="font-bold block">Enable AI Spam Detection</span>
            <span class="text-sm text-gray-600">Use AI to analyze messages</span
            >
          </div>
          <input
            type="checkbox"
            bind:checked={settings.enable_ai_check}
            class="w-6 h-6"
          />
        </label>

        <!-- Min Messages Required -->
        <div class="p-3 border-3 border-black">
          <div class="flex items-center justify-between mb-2">
            <span class="font-bold">Min Messages Required</span>
            <span class="font-black text-[#FF8A00]"
              >{settings.min_messages_required || 5}</span
            >
          </div>
          <input
            type="range"
            min="1"
            max="50"
            step="1"
            bind:value={settings.min_messages_required}
            class="w-full"
          />
          <p class="text-xs text-gray-500 mt-1">
            Messages before user is auto-trusted
          </p>
        </div>

        <!-- Min Observation Minutes -->
        <div class="p-3 border-3 border-black">
          <div class="flex flex-col gap-1 mb-2">
            <span class="font-bold">Observation Period (minutes)</span>
            <span class="text-xs text-gray-500">
              How long a user must be present before being trusted.
            </span>
          </div>
          <input
            type="number"
            min="1"
            bind:value={settings.min_observation_minutes}
            class="w-full border-2 border-black p-2 font-bold"
          />
        </div>
      </div>
    {:else if activeSection === "cleanup"}
      <div class="space-y-4" transition:slide>
        <!-- Cleanup Mentions -->
        <div class="border-3 border-black">
          <label class="flex items-center justify-between p-3 bg-gray-50">
            <span class="font-bold">Clean up excessive mentions</span>
            <input
              type="checkbox"
              bind:checked={settings.cleanup_mentions}
              class="w-5 h-5"
            />
          </label>
          {#if settings.cleanup_mentions}
            <div class="p-3 border-t-2 border-black">
              <label class="block text-sm font-medium mb-2"
                >Allowed mentions</label
              >
              <div class="flex flex-wrap gap-1 mb-2">
                {#each settings.allowed_mentions as mention, i}
                  <span class="tag flex items-center gap-1">
                    {mention}
                    <button
                      onclick={() => removeMention(i)}
                      class="p-0.5 hover:bg-red-200 border border-black transition-colors rounded-none"
                    >
                      <X class="w-3 h-3" />
                    </button>
                  </span>
                {/each}
              </div>
              <div class="flex gap-2">
                <input
                  type="text"
                  bind:value={newMention}
                  placeholder="@username"
                  class="flex-1"
                />
                <button
                  onclick={addMention}
                  class="btn btn-secondary px-3 flex items-center justify-center active:translate-x-[2px] active:translate-y-[2px] active:shadow-none shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] border-2"
                >
                  <Plus class="w-4 h-4" />
                </button>
              </div>
            </div>
          {/if}
        </div>

        <!-- Cleanup Emojis -->
        <div class="border-3 border-black">
          <label class="flex items-center justify-between p-3 bg-gray-50">
            <span class="font-bold">Clean up excessive emojis</span>
            <input
              type="checkbox"
              bind:checked={settings.cleanup_emojis}
              class="w-5 h-5"
            />
          </label>
          {#if settings.cleanup_emojis}
            <div class="p-3 border-t-2 border-black">
              <label class="block text-sm font-medium mb-1"
                >Maximum emoji count</label
              >
              <input
                type="number"
                min="0"
                max="50"
                bind:value={settings.max_emoji_count}
                class="w-24"
              />
            </div>
          {/if}
        </div>

        <!-- Cleanup Links -->
        <div class="border-3 border-black">
          <label class="flex items-center justify-between p-3 bg-gray-50">
            <span class="font-bold">Clean up suspicious links</span>
            <input
              type="checkbox"
              bind:checked={settings.cleanup_links}
              class="w-5 h-5"
            />
          </label>
          {#if settings.cleanup_links}
            <div class="p-3 border-t-2 border-black">
              <label class="block text-sm font-medium mb-2"
                >Allowed domains</label
              >
              <div class="flex flex-wrap gap-1 mb-2">
                {#each settings.allowed_link_domains as domain, i}
                  <span class="tag flex items-center gap-1">
                    {domain}
                    <button
                      onclick={() => removeDomain(i)}
                      class="p-0.5 hover:bg-red-200 border border-black transition-colors rounded-none"
                    >
                      <X class="w-3 h-3" />
                    </button>
                  </span>
                {/each}
              </div>
              <div class="flex gap-2">
                <input
                  type="text"
                  bind:value={newDomain}
                  placeholder="example.com"
                  class="flex-1"
                />
                <button
                  onclick={addDomain}
                  class="btn btn-secondary px-3 flex items-center justify-center active:translate-x-[2px] active:translate-y-[2px] active:shadow-none shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] border-2"
                >
                  <Plus class="w-4 h-4" />
                </button>
              </div>
            </div>
          {/if}
        </div>

        <!-- Cleanup Emails -->
        <label
          class="flex items-center justify-between p-3 border-3 border-black bg-gray-50"
        >
          <span class="font-bold">Clean up email addresses</span>
          <input
            type="checkbox"
            bind:checked={settings.cleanup_emails}
            class="w-5 h-5"
          />
        </label>
      </div>
    {:else}
      <ChatPrompts {chatId} />
    {/if}

    <!-- Save Button -->
    {#if activeSection !== "prompts"}
      <div class="mt-4 pt-4 border-t-3 border-black">
        <button
          onclick={save}
          disabled={isSaving}
          class="w-full btn btn-primary py-3 font-black flex items-center justify-center gap-2"
        >
          <Save class="w-5 h-5" />
          {isSaving ? "SAVING..." : "SAVE CHANGES"}
        </button>
      </div>
    {/if}
  </div>
{:else}
  <div class="card text-center py-8">
    <div class="animate-pulse">Loading settings...</div>
  </div>
{/if}
