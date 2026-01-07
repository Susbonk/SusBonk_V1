<script lang="ts">
  import { onMount } from 'svelte';
  import { CheckCircle, AlertCircle, X } from 'lucide-svelte';

  interface Props {
    type: 'success' | 'error' | 'info';
    message: string;
    onClose: () => void;
    duration?: number;
  }

  let { type, message, onClose, duration = 3000 }: Props = $props();
  let visible = $state(true);

  onMount(() => {
    const timer = setTimeout(() => {
      visible = false;
      setTimeout(onClose, 300); // Wait for fade out animation
    }, duration);

    return () => clearTimeout(timer);
  });

  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    info: AlertCircle
  };

  const colors = {
    success: 'bg-[#CCFF00] border-green-600',
    error: 'bg-red-100 border-red-600',
    info: 'bg-blue-100 border-blue-600'
  };

  const Icon = icons[type];
</script>

<div 
  class="fixed top-4 right-4 z-50 transition-all duration-300 {visible ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-2'}"
>
  <div class="border-[3px] border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] p-4 max-w-sm {colors[type]}">
    <div class="flex items-start gap-3">
      <Icon class="w-5 h-5 flex-shrink-0 mt-0.5" />
      <p class="flex-1 text-sm font-semibold" style="font-family: Poppins, sans-serif;">
        {message}
      </p>
      <button 
        onclick={() => { visible = false; setTimeout(onClose, 300); }}
        class="flex-shrink-0 hover:bg-black/10 p-1 rounded transition-colors"
      >
        <X class="w-4 h-4" />
      </button>
    </div>
  </div>
</div>