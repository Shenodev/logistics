<script setup lang="ts">
const { toasts } = useNotifications()
</script>

<template>
  <div
    v-if="toasts.length"
    class="pointer-events-none fixed bottom-20 right-4 z-[60] flex w-80 max-w-[90vw] flex-col gap-2 sm:bottom-6 sm:right-6"
    aria-live="polite"
  >
    <div
      v-for="t in toasts"
      :key="t.id"
      class="pointer-events-auto flex gap-2 rounded-xl border border-primary/30 bg-surface-container p-3 shadow-xl"
    >
      <div class="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
        <MIcon name="notifications_active" class="text-[18px]" />
      </div>
      <div class="min-w-0 flex-1">
        <p class="font-label-md font-bold text-on-surface">{{ t.title }}</p>
        <p class="mt-0.5 line-clamp-2 text-body-sm text-on-surface-variant">{{ t.message }}</p>
        <p v-if="t.order_number" class="mt-1 font-mono text-label-sm text-primary">{{ t.order_number }}</p>
      </div>
      <MIcon name="close" class="text-[16px] text-outline" />
    </div>
  </div>
</template>
