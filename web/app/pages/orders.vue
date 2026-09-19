<script setup lang="ts">
definePageMeta({ layout: 'delivery', middleware: 'auth' })
useSeoMeta({ title: 'My Orders — Delivery' })
</script>

<template>
  <div class="space-y-4">
    <h1 class="font-heading text-headline-md font-bold text-on-surface">Active Orders</h1>
    <p class="text-body-sm text-on-surface-variant">Orders you accepted from the Incoming Queue appear here. Tap to start navigation and update status.</p>
    <div class="rounded-xl border border-dashed border-outline-variant bg-surface-container p-6 text-center">
      <MIcon name="local_shipping" class="text-[28px] text-outline" />
      <p class="mt-2 text-body-sm text-on-surface-variant">No active orders yet. Accept an order from <NuxtLink to="/incoming" class="text-primary underline">Incoming</NuxtLink>.</p>
      <NuxtLink to="/incoming" class="mt-3 inline-flex min-h-12 items-center justify-center rounded-xl bg-primary px-6 text-label-md font-bold text-on-primary">Go to Incoming Queue</NuxtLink>
    </div>
  </div>
</template>
