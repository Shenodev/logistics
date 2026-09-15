<script setup lang="ts">
defineProps<{
  suffix?: string
}>()
</script>

<template>
  <div class="flex items-center gap-2.5">
    <img
      src="/logo-icon.png"
      alt="ShenoFlow logo"
      class="h-8 w-8 shrink-0 object-contain"
    />
    <span class="font-heading text-lg font-semibold tracking-tight text-foreground">
      ShenoFlow
      <span v-if="suffix" class="text-primary">{{ suffix }}</span>
    </span>
  </div>
</template>