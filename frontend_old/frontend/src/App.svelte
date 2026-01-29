<script lang="ts">
  import { getToken, setToken } from "./api";
  import Auth from "./Auth.svelte";
  import Settings from "./Settings.svelte";
  import CustomPrompts from "./CustomPrompts.svelte";
  import ChatList from "./ChatList.svelte";
  import ChatSettings from "./ChatSettings.svelte";
  import DeletedMessages from "./DeletedMessages.svelte";
  import UserStates from "./UserStates.svelte";

  let isAuthenticated = !!getToken();
  let view: "chats" | "settings" | "prompts" | "chat-detail" = "chats";
  let selectedChatId: string | null = null;
  let showUserStates = false;

  const logout = () => {
    setToken(null);
    window.location.reload();
  };

  const selectChat = (chatId: string) => {
    selectedChatId = chatId;
    view = "chat-detail";
    showUserStates = false;
  };
</script>

{#if !isAuthenticated}
  <Auth />
{:else}
  <nav>
    <button on:click={() => (view = "chats")}>Chats</button>
    <button on:click={() => (view = "prompts")}>Custom Prompts</button>
    <button on:click={() => (view = "settings")}>Settings</button>
    <button on:click={logout}>Logout</button>
  </nav>

  {#if view === "chats"}
    <ChatList onSelectChat={selectChat} />
  {:else if view === "prompts"}
    <CustomPrompts />
  {:else if view === "settings"}
    <Settings />
  {:else if view === "chat-detail" && selectedChatId}
    <div class="container">
      <div class="chat-header">
        <button on:click={() => (view = "chats")}>← Back</button>
        <button on:click={() => (showUserStates = !showUserStates)}>
          {showUserStates ? "Hide" : "Show"} User States
        </button>
      </div>
      {#if showUserStates}
        <UserStates chatId={selectedChatId} />
      {/if}
    </div>
    <ChatSettings chatId={selectedChatId} />
    <DeletedMessages chatId={selectedChatId} />
  {/if}
{/if}

<style>
  nav {
    padding: var(--spacing-md);
    background: linear-gradient(
      135deg,
      var(--color-surface) 0%,
      rgba(26, 26, 26, 0.9) 100%
    );
    border-bottom: 3px solid var(--color-primary);
    display: flex;
    gap: var(--spacing-sm);
    position: relative;
    overflow: hidden;
  }

  nav::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
      90deg,
      transparent 0%,
      rgba(0, 255, 136, 0.1) 25%,
      rgba(255, 107, 53, 0.1) 75%,
      transparent 100%
    );
    animation: pulse 3s ease-in-out infinite;
  }

  @keyframes pulse {
    0%,
    100% {
      opacity: 0.3;
    }
    50% {
      opacity: 0.7;
    }
  }

  .chat-header {
    display: flex;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
    padding: var(--spacing-md);
    border: 2px solid var(--color-border);
    border-radius: var(--border-radius);
    background: var(--color-surface);
    position: relative;
  }

  .chat-header::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(
      90deg,
      var(--color-primary),
      var(--color-secondary)
    );
  }
</style>
