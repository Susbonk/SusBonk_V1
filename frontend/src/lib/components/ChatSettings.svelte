<script lang="ts">
  import { onMount } from 'svelte';
  import { Save, Settings } from 'lucide-svelte';
  import { updateChat } from '../api/chats.js';
  import type { Chat } from '../types/api.js';

  interface Props {
    chat: Chat;
  }

  let { chat }: Props = $props();

  let isLoading = $state(false);
  let isSaving = $state(false);
  
  // Chat settings
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

  async function saveSettings() {
    if (!chat) return;

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
        allowed_link_domains: allowedLinkDomains.split(',').map(d => d.trim()).filter(d => d),
        allowed_mentions: allowedMentions.split(',').map(m => m.trim()).filter(m => m)
      };

      await updateChat(chat.id, updateData);
      
      // Update local chat object
      Object.assign(chat, updateData);
      
      alert('Settings saved successfully!');
    } catch (err) {
      console.error('Failed to save chat settings:', err);
      alert('Failed to save settings');
    } finally {
      isSaving = false;
    }
  }
</script>

<div class="card">
  <div class="flex items-center gap-2 mb-4">
    <Settings class="w-5 h-5" />
    <h3 class="font-extrabold">Chat Settings</h3>
  </div>

  <div class="space-y-6">
    <!-- AI Detection -->
    <div class="space-y-3">
      <h4 class="font-bold text-lg">AI Detection</h4>
      
      <label class="flex items-center gap-3">
        <input
          type="checkbox"
          bind:checked={enableAiCheck}
          class="w-4 h-4"
        />
        <span class="font-medium">Enable AI spam detection</span>
      </label>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block font-medium mb-1">System Prompts Threshold</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            bind:value={promptsThreshold}
            class="w-full"
          />
          <span class="text-sm text-gray-600">{promptsThreshold.toFixed(2)}</span>
        </div>
        
        <div>
          <label class="block font-medium mb-1">Custom Prompts Threshold</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            bind:value={customPromptThreshold}
            class="w-full"
          />
          <span class="text-sm text-gray-600">{customPromptThreshold.toFixed(2)}</span>
        </div>
      </div>
    </div>

    <!-- Cleanup Settings -->
    <div class="space-y-3">
      <h4 class="font-bold text-lg">Cleanup Rules</h4>
      
      <div class="space-y-3">
        <label class="flex items-center gap-3">
          <input
            type="checkbox"
            bind:checked={cleanupMentions}
            class="w-4 h-4"
          />
          <span class="font-medium">Clean up excessive mentions</span>
        </label>

        {#if cleanupMentions}
          <div class="ml-7">
            <label class="block font-medium mb-1">Allowed mentions (comma-separated)</label>
            <input
              type="text"
              bind:value={allowedMentions}
              placeholder="@admin, @moderator"
              class="w-full border-2 border-black px-3 py-2 focus:outline-none focus:border-[#CCFF00]"
            />
          </div>
        {/if}

        <label class="flex items-center gap-3">
          <input
            type="checkbox"
            bind:checked={cleanupEmojis}
            class="w-4 h-4"
          />
          <span class="font-medium">Clean up excessive emojis</span>
        </label>

        {#if cleanupEmojis}
          <div class="ml-7">
            <label class="block font-medium mb-1">Max emoji count</label>
            <input
              type="number"
              min="0"
              max="50"
              bind:value={maxEmojiCount}
              class="w-24 border-2 border-black px-3 py-2 focus:outline-none focus:border-[#CCFF00]"
            />
          </div>
        {/if}

        <label class="flex items-center gap-3">
          <input
            type="checkbox"
            bind:checked={cleanupLinks}
            class="w-4 h-4"
          />
          <span class="font-medium">Clean up suspicious links</span>
        </label>

        {#if cleanupLinks}
          <div class="ml-7">
            <label class="block font-medium mb-1">Allowed domains (comma-separated)</label>
            <input
              type="text"
              bind:value={allowedLinkDomains}
              placeholder="example.com, trusted-site.org"
              class="w-full border-2 border-black px-3 py-2 focus:outline-none focus:border-[#CCFF00]"
            />
          </div>
        {/if}

        <label class="flex items-center gap-3">
          <input
            type="checkbox"
            bind:checked={cleanupEmails}
            class="w-4 h-4"
          />
          <span class="font-medium">Clean up email addresses</span>
        </label>
      </div>
    </div>

    <!-- Save Button -->
    <div class="pt-4 border-t-2 border-gray-200">
      <button
        onclick={saveSettings}
        disabled={isSaving}
        class="bg-[#CCFF00] border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] px-4 py-2 font-bold flex items-center gap-2 transition-all active:shadow-none active:translate-x-[2px] active:translate-y-[2px] disabled:opacity-50"
      >
        <Save class="w-4 h-4" />
        {isSaving ? 'Saving...' : 'Save Settings'}
      </button>
    </div>
  </div>
</div>
