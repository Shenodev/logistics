<script setup lang="ts">
definePageMeta({ layout: 'delivery', middleware: 'auth' })
useSeoMeta({ title: 'My Orders — Delivery' })
</script>

<template>
  <div class="space-y-4 lg:space-y-6">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 class="font-heading text-headline-md font-bold text-on-surface lg:text-2xl">Active Orders</h1>
        <p class="text-body-sm text-on-surface-variant lg:text-sm">Orders you accepted from Incoming Queue — desktop grid, mobile list</p>
      </div>
      <NuxtLink to="/incoming" class="hidden lg:inline-flex min-h-9 items-center gap-1.5 rounded-xl border border-outline-variant bg-surface-container px-3 text-sm font-semibold text-on-surface-variant hover:text-primary">
        <MIcon name="inbox" class="text-[16px]" /> Incoming Queue
      </NuxtLink>
    </div>
    <div class="rounded-xl border border-dashed border-outline-variant bg-surface-container p-6 text-center lg:p-8">
      <MIcon name="local_shipping" class="text-[28px] text-outline" />
      <p class="mt-2 text-body-sm text-on-surface-variant">No active orders yet. Accept an order from <NuxtLink to="/incoming" class="text-primary underline">Incoming</NuxtLink>.</p>
      <NuxtLink to="/incoming" class="mt-3 inline-flex min-h-12 items-center justify-center rounded-xl bg-primary px-6 text-label-md font-bold text-on-primary">Go to Incoming Queue</NuxtLink>
    </div>
  </div>
</template>
