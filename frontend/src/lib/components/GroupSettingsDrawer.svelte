<script lang="ts">
  import { X, Settings, Sliders, Users, MessageSquare, Save } from 'lucide-svelte';
  import { slide, fly } from 'svelte/transition';
  import { updateChat } from '../api/chats.js';
  import type { Chat } from '../types/api.js';

  interface Props {
    chat: Chat;
    isOpen: boolean;
    onClose: () => void;
  }

  let { chat, isOpen, onClose }: Props = $props();

  let isSaving = $state(false);
  let activeSection = $state<'detection' | 'cleanup'>('detection');

  // Group settings (reactive from chat prop)
  let enableAiCheck = $state(chat.enable_ai_check);
  let promptsThreshold = $state(chat.prompts_threshold);
  let customPromptThreshold = $state(chat.custom_prompt_threshold);
  let cleanupMentions = $state(chat.cleanup_mentions);
  let cleanupEmojis = $state(chat.cleanup_emojis);
  let cleanupLinks = $state(chat.cleanup_links);
  let cleanupEmails = $state(chat.cleanup_emails);
  let maxEmojiCount = $state(chat.max_emoji_count);
  let allowedLinkDomains = $state(chat.allowed_link_domains?.join(', ') || '');
  let allowedMentions = $state(chat.allowed_mentions?.join(', ') || '');

  // Sync state when chat changes
  $effect(() => {
    enableAiCheck = chat.enable_ai_check;
    promptsThreshold = chat.prompts_threshold;
    customPromptThreshold = chat.custom_prompt_threshold;
    cleanupMentions = chat.cleanup_mentions;
    cleanupEmojis = chat.cleanup_emojis;
    cleanupLinks = chat.cleanup_links;
    cleanupEmails = chat.cleanup_emails;
    maxEmojiCount = chat.max_emoji_count;
    allowedLinkDomains = chat.allowed_link_domains?.join(', ') || '';
    allowedMentions = chat.allowed_mentions?.join(', ') || '';
  });

  async function saveSettings() {
    isSaving = true;
    try {
      const updateData = {
        enable_ai_check: enableAiCheck,
        prompts_threshold: promptsThreshold,
        custom_prompt_threshold: customPromptThreshold,
        cleanup_mentions: cleanupMentions,
        cleanup_emojis: cleanupEmojis,
        cleanup_links: cleanupLinks,
        cleanup_emails: cleanupEmails,
        max_emoji_count: maxEmojiCount,
        allowed_link_domains: allowedLinkDomains
          .split(',')
          .map((d) => d.trim())
          .filter((d) => d),
        allowed_mentions: allowedMentions
          .split(',')
          .map((m) => m.trim())
          .filter((m) => m),
      };

      await updateChat(chat.id, updateData);
      Object.assign(chat, updateData);
      onClose();
    } catch (err) {
      console.error('Failed to save group settings:', err);
      alert('Failed to save settings');
    } finally {
      isSaving = false;
    }
  }

  function getThresholdLabel(value: number): string {
    if (value < 0.3) return 'Low';
    if (value < 0.6) return 'Medium';
    if (value < 0.8) return 'High';
    return 'Strict';
  }

  function getThresholdColor(value: number): string {
    if (value < 0.3) return 'text-green-600';
    if (value < 0.6) return 'text-yellow-600';
    if (value < 0.8) return 'text-orange-600';
    return 'text-red-600';
  }
</script>

{#if isOpen}
  <!-- Backdrop -->
  <div
    class="fixed inset-0 bg-black/50 z-50"
    onclick={onClose}
    onkeydown={(e) => e.key === 'Escape' && onClose()}
    role="button"
    tabindex="0"
    transition:fly={{ duration: 200 }}
  ></div>

  <!-- Drawer -->
  <div
    class="fixed bottom-0 left-0 right-0 max-h-[85vh] bg-white border-t-4 border-black z-50 overflow-hidden flex flex-col"
    transition:slide={{ duration: 300 }}
    role="dialog"
    aria-modal="true"
    aria-labelledby="drawer-title"
  >
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b-3 border-black bg-[#CCFF00]">
      <div class="flex items-center gap-2">
        <Settings class="w-5 h-5" />
        <h2 id="drawer-title" class="font-black text-lg">Edit {chat.title || 'Group'}</h2>
      </div>
      <button
        onclick={onClose}
        class="p-2 hover:bg-black/10 transition-colors border-2 border-black"
        aria-label="Close drawer"
      >
        <X class="w-5 h-5" />
      </button>
    </div>

    <!-- Section Tabs -->
    <div class="flex border-b-3 border-black">
      <button
        onclick={() => (activeSection = 'detection')}
        class="flex-1 py-3 px-4 font-bold text-sm flex items-center justify-center gap-2 transition-colors {activeSection ===
        'detection'
          ? 'bg-[#FF8A00]'
          : 'bg-white hover:bg-gray-50'}"
      >
        <Sliders class="w-4 h-4" />
        AI Detection
      </button>
      <button
        onclick={() => (activeSection = 'cleanup')}
        class="flex-1 py-3 px-4 font-bold text-sm flex items-center justify-center gap-2 border-l-3 border-black transition-colors {activeSection ===
        'cleanup'
          ? 'bg-[#FF8A00]'
          : 'bg-white hover:bg-gray-50'}"
      >
        <MessageSquare class="w-4 h-4" />
        Cleanup Rules
      </button>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-4">
      {#if activeSection === 'detection'}
        <div class="space-y-5" transition:slide>
          <!-- AI Detection Toggle -->
          <label class="flex items-center justify-between p-3 border-3 border-black bg-gray-50">
            <div>
              <span class="font-bold block">Enable AI Spam Detection</span>
              <span class="text-sm text-gray-600">Use AI to analyze messages</span>
            </div>
            <input type="checkbox" bind:checked={enableAiCheck} class="w-6 h-6 accent-[#CCFF00]" />
          </label>

          {#if enableAiCheck}
            <!-- System Prompts Threshold -->
            <div class="p-3 border-3 border-black">
              <div class="flex items-center justify-between mb-2">
                <span class="font-bold">System Prompts Threshold</span>
                <span class="font-black {getThresholdColor(promptsThreshold)}">
                  {getThresholdLabel(promptsThreshold)} ({promptsThreshold.toFixed(2)})
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                bind:value={promptsThreshold}
                class="w-full h-2 accent-[#FF8A00]"
              />
              <div class="flex justify-between text-xs text-gray-500 mt-1">
                <span>Lenient</span>
                <span>Strict</span>
              </div>
            </div>

            <!-- Custom Prompts Threshold -->
            <div class="p-3 border-3 border-black">
              <div class="flex items-center justify-between mb-2">
                <span class="font-bold">Custom Prompts Threshold</span>
                <span class="font-black {getThresholdColor(customPromptThreshold)}">
                  {getThresholdLabel(customPromptThreshold)} ({customPromptThreshold.toFixed(2)})
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                bind:value={customPromptThreshold}
                class="w-full h-2 accent-[#FF8A00]"
              />
              <div class="flex justify-between text-xs text-gray-500 mt-1">
                <span>Lenient</span>
                <span>Strict</span>
              </div>
            </div>
          {/if}
        </div>
      {:else}
        <div class="space-y-4" transition:slide>
          <!-- Cleanup Mentions -->
          <div class="border-3 border-black">
            <label class="flex items-center justify-between p-3 bg-gray-50">
              <span class="font-bold">Clean up excessive mentions</span>
              <input
                type="checkbox"
                bind:checked={cleanupMentions}
                class="w-5 h-5 accent-[#CCFF00]"
              />
            </label>
            {#if cleanupMentions}
              <div class="p-3 border-t-2 border-black">
                <label class="block text-sm font-medium mb-1"
                  >Allowed mentions (comma-separated)</label
                >
                <input
                  type="text"
                  bind:value={allowedMentions}
                  placeholder="@admin, @moderator"
                  class="w-full border-2 border-black px-3 py-2 focus:outline-none focus:border-[#CCFF00]"
                />
              </div>
            {/if}
          </div>

          <!-- Cleanup Emojis -->
          <div class="border-3 border-black">
            <label class="flex items-center justify-between p-3 bg-gray-50">
              <span class="font-bold">Clean up excessive emojis</span>
              <input
                type="checkbox"
                bind:checked={cleanupEmojis}
                class="w-5 h-5 accent-[#CCFF00]"
              />
            </label>
            {#if cleanupEmojis}
              <div class="p-3 border-t-2 border-black">
                <label class="block text-sm font-medium mb-1">Maximum emoji count</label>
                <input
                  type="number"
                  min="0"
                  max="50"
                  bind:value={maxEmojiCount}
                  class="w-24 border-2 border-black px-3 py-2 focus:outline-none focus:border-[#CCFF00]"
                />
              </div>
            {/if}
          </div>

          <!-- Cleanup Links -->
          <div class="border-3 border-black">
            <label class="flex items-center justify-between p-3 bg-gray-50">
              <span class="font-bold">Clean up suspicious links</span>
              <input type="checkbox" bind:checked={cleanupLinks} class="w-5 h-5 accent-[#CCFF00]" />
            </label>
            {#if cleanupLinks}
              <div class="p-3 border-t-2 border-black">
                <label class="block text-sm font-medium mb-1"
                  >Allowed domains (comma-separated)</label
                >
                <input
                  type="text"
                  bind:value={allowedLinkDomains}
                  placeholder="example.com, trusted-site.org"
                  class="w-full border-2 border-black px-3 py-2 focus:outline-none focus:border-[#CCFF00]"
                />
              </div>
            {/if}
          </div>

          <!-- Cleanup Emails -->
          <label class="flex items-center justify-between p-3 border-3 border-black bg-gray-50">
            <span class="font-bold">Clean up email addresses</span>
            <input type="checkbox" bind:checked={cleanupEmails} class="w-5 h-5 accent-[#CCFF00]" />
          </label>
        </div>
      {/if}
    </div>

    <!-- Footer with Save -->
    <div class="p-4 border-t-3 border-black bg-gray-50">
      <button
        onclick={saveSettings}
        disabled={isSaving}
        class="w-full bg-[#CCFF00] border-3 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] py-3 font-black flex items-center justify-center gap-2 transition-all active:shadow-none active:translate-x-[4px] active:translate-y-[4px] disabled:opacity-50"
      >
        <Save class="w-5 h-5" />
        {isSaving ? 'SAVING...' : 'SAVE CHANGES'}
      </button>
    </div>
  </div>
{/if}

<style>
  /* Ensure smooth transitions */
  .overflow-y-auto {
    scrollbar-width: thin;
    scrollbar-color: #000 #e5e7eb;
  }
</style>
