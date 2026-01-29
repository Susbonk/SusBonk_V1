<script lang="ts">
  import { onMount } from "svelte";
  import { auth } from "./api";

  let user: any = null;
  let telegramData: any = null;
  let loading = false;

  onMount(async () => {
    user = await auth.me();
  });

  const connectTelegram = async () => {
    loading = true;
    try {
      telegramData = await auth.connectTelegram();
    } catch (e) {
      alert("Error connecting Telegram");
    }
    loading = false;
  };
</script>

<div class="container">
  <h2>Settings</h2>
  {#if user}
    <div class="card">
      <h3>Profile</h3>
      <p><strong>Email:</strong> {user.email}</p>
      <p><strong>Username:</strong> {user.username || "N/A"}</p>
    </div>

    <div class="card">
      <h3>Connect Platforms</h3>
      <div class="platform-item">
        <strong>Telegram:</strong>
        {#if user.telegram_user_id}
          <span class="status-connected">Connected (ID: {user.telegram_user_id})</span>
        {:else}
          <button class="btn-primary" on:click={connectTelegram} disabled={loading}>
            Connect Telegram
          </button>
          {#if telegramData?.bot_link}
            <div class="telegram-info">
              <p>{telegramData.message}</p>
              <code class="bot-link">{telegramData.bot_link}</code>
            </div>
          {/if}
        {/if}
      </div>

      <div class="platform-item disabled">
        <strong>Discord:</strong> <span class="status-coming-soon">Coming soon</span>
      </div>
    </div>
  {/if}
</div>

<style>
  h3 {
    margin-bottom: var(--spacing-md);
    color: var(--color-text);
  }
  
  .platform-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-md);
    padding: var(--spacing-md);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
  }
  
  .platform-item.disabled {
    opacity: 0.5;
  }
  
  .status-connected {
    color: var(--color-primary);
    font-weight: 500;
  }
  
  .status-coming-soon {
    color: var(--color-text-muted);
  }
  
  .telegram-info {
    margin-top: var(--spacing-sm);
  }
  
  .bot-link {
    display: block;
    margin-top: var(--spacing-xs);
    padding: var(--spacing-sm);
    background: var(--color-surface);
    border-radius: var(--border-radius);
    font-family: monospace;
    font-size: var(--font-size-sm);
  }
</style>
