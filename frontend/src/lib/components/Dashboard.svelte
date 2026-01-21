<script lang="ts">
  import { onMount } from 'svelte';
  import {
    Zap,
    Heart,
    DollarSign,
    Briefcase,
    Pencil,
    User,
    ChevronDown,
    ChevronUp,
    Sparkles,
    Plus,
    X,
  } from 'lucide-svelte';
  import DashboardHeader from './DashboardHeader.svelte';
  import ModerationToggle from './ModerationToggle.svelte';
  import RecentBonks from './RecentBonks.svelte';
  import CustomBlockSection from './CustomBlockSection.svelte';
  import MembersPanel from './MembersPanel.svelte';
  import ChatSettings from './ChatSettings.svelte';
  import TelegramConnection from './TelegramConnection.svelte';
  import GroupSettingsDrawer from './GroupSettingsDrawer.svelte';
  import WhitelistPanel from './WhitelistPanel.svelte';
  import { chatsState, promptsState } from '../stores/index.js';
  import {
    listSystemPrompts,
    listCustomPrompts,
    createPrompt,
    updatePrompt,
    deletePrompt,
  } from '../api/prompts.js';
  import type { SystemPrompt, CustomPrompt } from '../types/api.js';
  import type { TabType, SettingsTabType } from '../types';

  interface Props {
    onEmergencyStop: () => void;
    onAddGroup: () => void;
    activeTab: TabType;
  }

  let { onEmergencyStop, onAddGroup, activeTab }: Props = $props();

  // Moderation section state
  let promptsExpanded = $state(true);
  let customExpanded = $state(true);
  let systemPrompts = $state<SystemPrompt[]>([]);
  let isLoadingPrompts = $state(false);

  // Group settings drawer state
  let isGroupSettingsOpen = $state(false);

  // Settings sub-tab state (now Account-focused)
  let settingsTab = $state<SettingsTabType>('telegram');
  const settingsTabs: { id: SettingsTabType; label: string }[] = [
    { id: 'telegram', label: 'Telegram' },
    { id: 'members', label: 'Members Mgmt' },
    { id: 'whitelist', label: 'Whitelist' },
  ];

  // Modal state for creating/editing custom prompts
  let isModalOpen = $state(false);
  let editingPrompt = $state<CustomPrompt | null>(null);
  let newName = $state('');
  let newInstructions = $state('');
  let isSaving = $state(false);

  // Icon mapping for system prompts
  const promptIcons: Record<string, typeof Zap> = {
    crypto_scam: Zap,
    spam_links: Pencil,
    adult_content: Heart,
    harassment: User,
    commercial_spam: DollarSign,
  };

  onMount(async () => {
    await loadPrompts();
  });

  async function loadPrompts() {
    isLoadingPrompts = true;
    try {
      const [system, custom] = await Promise.all([listSystemPrompts(), listCustomPrompts()]);
      systemPrompts = system;
      promptsState.update((state) => ({ ...state, customPrompts: custom }));
    } catch (err) {
      console.error('Failed to load prompts:', err);
    } finally {
      isLoadingPrompts = false;
    }
  }

  function handleGroupChange(value: string) {
    if (value === 'add_new') {
      onAddGroup();
    } else {
      chatsState.update((state) => ({
        ...state,
        activeChat: state.chats.find((chat) => chat.title === value) || null,
      }));
    }
  }

  function togglePlayPause() {
    // TODO: Implement with API integration
  }

  // Custom prompt CRUD
  function openCreateModal() {
    editingPrompt = null;
    newName = '';
    newInstructions = '';
    isModalOpen = true;
  }

  function openEditModal(prompt: CustomPrompt) {
    editingPrompt = prompt;
    newName = prompt.title || '';
    newInstructions = prompt.text;
    isModalOpen = true;
  }

  function closeModal() {
    isModalOpen = false;
    editingPrompt = null;
    newName = '';
    newInstructions = '';
  }

  async function savePrompt() {
    if (!newName || !newInstructions) return;

    isSaving = true;
    try {
      if (editingPrompt) {
        await updatePrompt(editingPrompt.id, { title: newName, text: newInstructions });
      } else {
        await createPrompt({ title: newName, text: newInstructions });
      }
      await loadPrompts();
      closeModal();
    } catch (err) {
      console.error('Failed to save prompt:', err);
      alert('Failed to save custom prompt');
    } finally {
      isSaving = false;
    }
  }

  async function handleDeletePrompt(prompt: CustomPrompt) {
    if (confirm(`Delete "${prompt.title}"? This cannot be undone.`)) {
      try {
        await deletePrompt(prompt.id);
        await loadPrompts();
      } catch (err) {
        console.error('Failed to delete prompt:', err);
        alert('Failed to delete custom prompt');
      }
    }
  }

  function getPromptIcon(promptName: string | null) {
    return promptIcons[promptName || ''] || Briefcase;
  }

  function formatPromptName(name: string | null): string {
    if (!name) return 'Unnamed';
    return name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }
</script>

<div class="min-h-screen bg-white">
  <div class="max-w-md mx-auto">
    {#if activeTab === 'dashboard'}
      <div class="p-4 space-y-4">
        <DashboardHeader
          bonkCount={$chatsState.activeChat?.spam_detected || 0}
          isPlaying={false}
          onTogglePlay={togglePlayPause}
          groups={$chatsState.chats
            .map((chat) => chat.title)
            .filter((t): t is string => t !== null)}
          activeGroup={$chatsState.activeChat?.title || ''}
          onGroupChange={handleGroupChange}
          onEditGroup={() => (isGroupSettingsOpen = true)}
        />

        <div>
          <h2 class="mb-3 text-lg font-extrabold">Moderation Strength</h2>

          <!-- System Prompts (formerly Built-in Rules) -->
          <div class="mb-4">
            <button
              onclick={() => (promptsExpanded = !promptsExpanded)}
              class="w-full flex items-center justify-between py-2 px-3 bg-gray-100 border-3 border-black mb-2 font-bold text-sm"
            >
              <span>Prompts ({systemPrompts.length})</span>
              {#if promptsExpanded}<ChevronUp class="w-5 h-5" />{:else}<ChevronDown
                  class="w-5 h-5"
                />{/if}
            </button>

            {#if promptsExpanded}
              <div class="space-y-3">
                {#if isLoadingPrompts}
                  <div class="text-center py-6 text-gray-500">Loading prompts...</div>
                {:else if systemPrompts.length === 0}
                  <div
                    class="text-center py-6 text-gray-500 italic border-2 border-dashed border-gray-300"
                  >
                    No system prompts available.
                  </div>
                {:else}
                  {#each systemPrompts as prompt (prompt.id)}
                    <ModerationToggle
                      icon={getPromptIcon(prompt.title)}
                      category={formatPromptName(prompt.title)}
                      promptText={prompt.text}
                      initialLevel="Normal"
                    />
                  {/each}
                {/if}
              </div>
            {/if}
          </div>

          <!-- Custom Rules -->
          <div>
            <div
              class="flex items-center justify-between py-2 px-3 bg-[#FF8A00]/20 border-3 border-black mb-2"
            >
              <button
                onclick={() => (customExpanded = !customExpanded)}
                class="flex items-center gap-2 font-bold text-sm"
              >
                <span>Custom Rules ({$promptsState.customPrompts.length})</span>
                {#if customExpanded}<ChevronUp class="w-5 h-5" />{:else}<ChevronDown
                    class="w-5 h-5"
                  />{/if}
              </button>
              <button
                onclick={openCreateModal}
                class="bg-[#FF8A00] border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] px-3 py-1 text-sm font-bold flex items-center gap-1 transition-all active:shadow-none active:translate-x-[2px] active:translate-y-[2px]"
              >
                <Plus class="w-4 h-4" />
                NEW
              </button>
            </div>

            {#if customExpanded}
              <div class="space-y-3">
                {#if $promptsState.customPrompts.length === 0}
                  <div
                    class="text-center py-6 text-gray-500 italic border-2 border-dashed border-gray-300"
                  >
                    No custom rules yet. Click NEW to create one.
                  </div>
                {:else}
                  {#each $promptsState.customPrompts as prompt (prompt.id)}
                    <ModerationToggle
                      icon={Sparkles}
                      category={prompt.title || 'Unnamed'}
                      promptText={prompt.text}
                      initialLevel="Normal"
                      isCustom={true}
                      onEdit={() => openEditModal(prompt)}
                      onDelete={() => handleDeletePrompt(prompt)}
                    />
                  {/each}
                {/if}
              </div>
            {/if}
          </div>
        </div>
      </div>
    {/if}

    {#if activeTab === 'logs'}
      <div class="p-4 space-y-4">
        <h2 class="text-2xl font-black">
          Logs for {$chatsState.activeChat?.title || 'No Group Selected'}
        </h2>
        <RecentBonks />
      </div>
    {/if}

    {#if activeTab === 'settings'}
      <div class="p-4 space-y-4">
        <h2 class="text-2xl font-black">Account</h2>
        <p class="text-gray-600 -mt-2">Manage your account and connections</p>

        <!-- Account Sub-tabs -->
        <div class="flex border-3 border-black">
          {#each settingsTabs as tab, index}
            <button
              onclick={() => (settingsTab = tab.id)}
              class="flex-1 py-3 font-bold text-sm transition-colors {settingsTab === tab.id
                ? 'bg-[#FF8A00] text-black'
                : 'bg-white hover:bg-gray-50'} {index !== settingsTabs.length - 1
                ? 'border-r-3 border-black'
                : ''}"
            >
              {tab.label}
            </button>
          {/each}
        </div>

        <!-- Account Content -->
        <div class="mt-4">
          {#if settingsTab === 'telegram'}
            <TelegramConnection />
          {/if}

          {#if settingsTab === 'members'}
            <MembersPanel />
          {/if}

          {#if settingsTab === 'whitelist'}
            <WhitelistPanel />
          {/if}
        </div>

        <!-- Group Settings Hint -->
        <div class="mt-6 p-4 bg-gray-50 border-3 border-black border-dashed">
          <p class="text-sm text-gray-600">
            <strong>Looking for group settings?</strong> Select a group on the Dashboard and click
            the
            <span
              class="inline-flex items-center gap-1 px-2 py-0.5 bg-[#FF8A00] border-2 border-black text-xs font-bold"
            >
              Edit
            </span>
            button to configure AI detection, cleanup rules, and more.
          </p>
        </div>
      </div>
    {/if}
  </div>
</div>

<!-- Group Settings Drawer -->
{#if $chatsState.activeChat}
  <GroupSettingsDrawer
    chat={$chatsState.activeChat}
    isOpen={isGroupSettingsOpen}
    onClose={() => (isGroupSettingsOpen = false)}
  />
{/if}

<!-- Create/Edit Custom Prompt Modal -->
{#if isModalOpen}
  <div
    class="modal-backdrop"
    onclick={closeModal}
    onkeydown={(e) => e.key === 'Escape' && closeModal()}
    role="button"
    tabindex="0"
  >
    <div
      class="modal-content"
      onclick={(e) => e.stopPropagation()}
      onkeydown={(e) => e.key === 'Enter' && e.stopPropagation()}
      role="dialog"
      tabindex="-1"
    >
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-extrabold">{editingPrompt ? 'Edit' : 'New'} Custom Rule</h2>
        <button onclick={closeModal} class="p-1 hover:bg-gray-100"><X class="w-6 h-6" /></button>
      </div>
      <p class="text-gray-600 mb-4">
        Define a moderation rule using natural language instructions for the AI.
      </p>

      <div class="space-y-4 mb-6">
        <div>
          <label for="prompt-name" class="font-bold mb-2 block">Rule Name</label>
          <input
            id="prompt-name"
            type="text"
            bind:value={newName}
            placeholder="e.g. No Competitor Mentions"
            class="w-full border-3 border-black px-3 py-2 focus:outline-none focus:border-[#CCFF00]"
          />
        </div>
        <div>
          <label for="prompt-text" class="font-bold mb-2 block">AI Instructions</label>
          <textarea
            id="prompt-text"
            bind:value={newInstructions}
            placeholder="Describe what the AI should look for in messages..."
            class="w-full border-3 border-black px-3 py-2 min-h-[120px] focus:outline-none focus:border-[#CCFF00]"
          ></textarea>
        </div>
      </div>

      <button
        onclick={savePrompt}
        class="btn btn-primary w-full py-3 text-lg font-black"
        disabled={isSaving || !newName || !newInstructions}
      >
        {isSaving ? 'SAVING...' : editingPrompt ? 'UPDATE RULE' : 'CREATE RULE'}
      </button>
    </div>
  </div>
{/if}
