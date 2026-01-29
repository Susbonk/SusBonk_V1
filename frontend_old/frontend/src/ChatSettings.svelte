<script lang="ts">
  import { onMount } from "svelte";
  import { chats } from "./api";
  import ChatPrompts from "./ChatPrompts.svelte";

  export let chatId: string;

  let settings: any = null;
  let editing = false;
  let newMention = "";
  let newDomain = "";
  let showPrompts = false;

  onMount(async () => {
    settings = await chats.get(chatId);
    if (!settings.allowed_mentions) settings.allowed_mentions = [];
    if (!settings.allowed_link_domains) settings.allowed_link_domains = [];
  });

  const save = async () => {
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
  };

  const addMention = () => {
    if (newMention) {
      settings.allowed_mentions = [...settings.allowed_mentions, newMention];
      newMention = "";
    }
  };

  const removeMention = (idx: number) => {
    settings.allowed_mentions = settings.allowed_mentions.filter(
      (_: any, i: number) => i !== idx,
    );
  };

  const addDomain = () => {
    if (newDomain) {
      settings.allowed_link_domains = [
        ...settings.allowed_link_domains,
        newDomain,
      ];
      newDomain = "";
    }
  };

  const removeDomain = (idx: number) => {
    settings.allowed_link_domains = settings.allowed_link_domains.filter(
      (_: any, i: number) => i !== idx,
    );
  };
</script>

{#if settings}
  <div class="container">
    <div class="card">
      <h3>Chat Settings</h3>
      <div class="chat-info">
        <p><strong>Title:</strong> {settings.title || "N/A"}</p>
        <p><strong>Type:</strong> {settings.type}</p>
      </div>

      <div class="section-tabs">
        <button
          class="tab-button {!showPrompts ? 'active' : ''}"
          on:click={() => (showPrompts = false)}
        >
          General Settings
        </button>
        <button
          class="tab-button {showPrompts ? 'active' : ''}"
          on:click={() => (showPrompts = true)}
        >
          Prompts
        </button>
      </div>

      {#if !showPrompts}
        {#if !editing}
          <div class="settings-preview">
            <div class="preview-item">
              <strong>AI Check:</strong>
              {settings.enable_ai_check ? "Enabled" : "Disabled"}
            </div>
            <div class="preview-item">
              <strong>Cleanup Mentions:</strong>
              {settings.cleanup_mentions ? "Enabled" : "Disabled"}
              {#if settings.cleanup_mentions && settings.allowed_mentions?.length}
                <small>({settings.allowed_mentions.length} allowed)</small>
              {/if}
            </div>
            <div class="preview-item">
              <strong>Cleanup Emojis:</strong>
              {settings.cleanup_emojis ? "Enabled" : "Disabled"}
              {#if settings.cleanup_emojis}
                <small>(max: {settings.max_emoji_count})</small>
              {/if}
            </div>
            <div class="preview-item">
              <strong>Cleanup Links:</strong>
              {settings.cleanup_links ? "Enabled" : "Disabled"}
              {#if settings.cleanup_links && settings.allowed_link_domains?.length}
                <small>({settings.allowed_link_domains.length} allowed)</small>
              {/if}
            </div>
            <div class="preview-item">
              <strong>Cleanup Emails:</strong>
              {settings.cleanup_emails ? "Enabled" : "Disabled"}
            </div>
          </div>
          <button class="btn-primary" on:click={() => (editing = true)}
            >Edit Settings</button
          >
        {:else}
          <div class="settings-form">
            <div class="form-group">
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  bind:checked={settings.enable_ai_check}
                />
                Enable AI Check
              </label>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  bind:checked={settings.cleanup_mentions}
                />
                Cleanup Mentions
              </label>
              {#if settings.cleanup_mentions}
                <div class="help-text">
                  When enabled, only mentions listed below will be allowed:
                </div>
                <div class="tag-list">
                  {#each settings.allowed_mentions as mention, i}
                    <span class="tag">
                      {mention}
                      <button
                        type="button"
                        class="tag-remove"
                        on:click={() => removeMention(i)}>×</button
                      >
                    </span>
                  {/each}
                  <div class="tag-input-group">
                    <input
                      type="text"
                      bind:value={newMention}
                      placeholder="Add allowed mention"
                    />
                    <button type="button" on:click={addMention}>Add</button>
                  </div>
                </div>
              {/if}
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" bind:checked={settings.cleanup_emojis} />
                Cleanup Emojis
              </label>
              <label class="number-label">
                Max Emoji Count:
                <input type="number" bind:value={settings.max_emoji_count} />
              </label>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" bind:checked={settings.cleanup_links} />
                Cleanup Links
              </label>
              {#if settings.cleanup_links}
                <div class="help-text">
                  When enabled, only links from domains listed below will be
                  allowed:
                </div>
                <div class="tag-list">
                  {#each settings.allowed_link_domains as domain, i}
                    <span class="tag">
                      {domain}
                      <button
                        type="button"
                        class="tag-remove"
                        on:click={() => removeDomain(i)}>×</button
                      >
                    </span>
                  {/each}
                  <div class="tag-input-group">
                    <input
                      type="text"
                      bind:value={newDomain}
                      placeholder="Add allowed domain"
                    />
                    <button type="button" on:click={addDomain}>Add</button>
                  </div>
                </div>
              {/if}
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" bind:checked={settings.cleanup_emails} />
                Cleanup Emails
              </label>
            </div>

            <div class="form-group">
              <label class="number-label">
                Min Messages Required:
                <input
                  type="number"
                  bind:value={settings.min_messages_required}
                />
              </label>
            </div>

            <div class="form-group">
              <label class="number-label">
                Min Observation Minutes:
                <input
                  type="number"
                  bind:value={settings.min_observation_minutes}
                />
              </label>
            </div>

            <div class="button-group">
              <button class="btn-primary" on:click={save}>Save</button>
              <button type="button" on:click={() => (editing = false)}
                >Cancel</button
              >
            </div>
          </div>
        {/if}
      {:else}
        <ChatPrompts {chatId} />
      {/if}
    </div>
  </div>
{/if}

<style>
  h3 {
    margin-bottom: var(--spacing-md);
    color: var(--color-text);
  }

  .chat-info {
    margin-bottom: var(--spacing-lg);
  }

  .chat-info p {
    margin-bottom: var(--spacing-xs);
  }

  .settings-form {
    margin-top: var(--spacing-lg);
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
    font-weight: 500;
  }

  .number-label {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-top: var(--spacing-sm);
    font-weight: 500;
  }

  .number-label input[type="number"] {
    width: 100px;
  }

  .tag-list {
    margin-left: var(--spacing-lg);
    margin-top: var(--spacing-sm);
  }

  .tag {
    display: inline-flex;
    align-items: center;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    padding: var(--spacing-xs) var(--spacing-sm);
    margin: var(--spacing-xs);
    font-size: var(--font-size-sm);
  }

  .tag-remove {
    background: none;
    border: none;
    color: var(--color-text-muted);
    padding: 0;
    margin-left: var(--spacing-xs);
    cursor: pointer;
    font-size: 16px;
    line-height: 1;
  }

  .tag-remove:hover {
    color: var(--color-error);
  }

  .tag-input-group {
    display: flex;
    gap: var(--spacing-sm);
    margin-top: var(--spacing-sm);
    align-items: center;
  }

  .tag-input-group input {
    width: 200px;
  }

  .button-group {
    display: flex;
    gap: var(--spacing-sm);
    margin-top: var(--spacing-lg);
  }

  .section-tabs {
    display: flex;
    gap: var(--spacing-xs);
    margin-bottom: var(--spacing-lg);
    border-bottom: 1px solid var(--color-border);
  }

  .tab-button {
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    padding: var(--spacing-sm) var(--spacing-md);
    cursor: pointer;
    font-weight: 500;
    color: var(--color-text-muted);
    transition: all 0.2s ease;
  }

  .tab-button:hover {
    color: var(--color-text);
    background: var(--color-surface);
  }

  .tab-button.active {
    color: var(--color-primary);
    border-bottom-color: var(--color-primary);
  }

  .help-text {
    font-size: var(--font-size-sm);
    color: var(--color-text-muted);
    margin: var(--spacing-xs) 0 var(--spacing-sm) 0;
    font-style: italic;
  }

  .settings-preview {
    margin-bottom: var(--spacing-lg);
  }

  .preview-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) 0;
    border-bottom: 1px solid var(--color-border);
  }

  .preview-item:last-child {
    border-bottom: none;
  }

  .preview-item small {
    color: var(--color-text-muted);
    font-style: italic;
  }
</style>
