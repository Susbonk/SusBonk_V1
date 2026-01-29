<script lang="ts">
  import { auth, setToken } from "./api";

  let email = "";
  let password = "";
  let username = "";
  let isLogin = true;
  let error = "";

  const handleSubmit = async () => {
    error = "";
    try {
      if (isLogin) {
        await auth.login(email, password);
        window.location.reload();
      } else {
        await auth.register(email, password, username || undefined);
        isLogin = true;
      }
    } catch (e: any) {
      error = e.message;
    }
  };
</script>

<div class="auth-container">
  <div class="auth-form">
    <h2>{isLogin ? "Login" : "Register"}</h2>
    <form on:submit|preventDefault={handleSubmit}>
      <div class="form-group">
        <input type="email" bind:value={email} placeholder="Email" required />
      </div>
      <div class="form-group">
        <input
          type="password"
          bind:value={password}
          placeholder="Password"
          required
        />
      </div>
      {#if !isLogin}
        <div class="form-group">
          <input
            type="text"
            bind:value={username}
            placeholder="Username (optional)"
          />
        </div>
      {/if}
      <div class="btn-group">
        <button type="submit" class="btn-primary">{isLogin ? "Login" : "Register"}</button>
        <button type="button" on:click={() => (isLogin = !isLogin)}>
          {isLogin ? "Need to register?" : "Already have account?"}
        </button>
      </div>
    </form>
    {#if error}<p class="text-error">{error}</p>{/if}
  </div>
</div>

<style>
  .auth-container {
    max-width: 400px;
    margin: var(--spacing-xl) auto;
    padding: var(--spacing-lg);
  }
  
  .auth-form {
    background: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius);
    padding: var(--spacing-xl);
  }
  
  h2 {
    margin-bottom: var(--spacing-lg);
    text-align: center;
    color: var(--color-text);
  }
  
  .form-group {
    margin-bottom: var(--spacing-md);
  }
  
  input {
    width: 100%;
  }
  
  .btn-group {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
    margin-top: var(--spacing-lg);
  }
</style>
