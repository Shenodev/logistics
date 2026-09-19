<script setup lang="ts">
import { incomingSeed, driverStats, type IncomingOrder } from '~~/app/data/delivery'

definePageMeta({ layout: 'delivery', middleware: 'auth' })

useSeoMeta({
  title: 'Delivery — Incoming Orders',
  description: 'Mobile-first driver dashboard — incoming order queue with Accept / Reject.',
  viewport: 'width=device-width, initial-scale=1, viewport-fit=cover',
})

const queue = ref<IncomingOrder[]>([...incomingSeed])
const processingId = ref<string | null>(null)
const toast = ref<string | null>(null)
const accepted = ref<IncomingOrder[]>([])

function showToast(msg: string) {
  toast.value = msg
  setTimeout(() => (toast.value = null), 2500)
}

async function handleAccept(id: string) {
  processingId.value = id
  await new Promise((r) => setTimeout(r, 500))
  const idx = queue.value.findIndex((o) => o.shipment.id === id)
  if (idx !== -1) {
    const [order] = queue.value.splice(idx, 1)
    accepted.value.unshift(order!)
    // haptic feedback if available
    if ('vibrate' in navigator) navigator.vibrate(20)
    showToast(`Accepted ${id} — heading to pickup`)
  }
  processingId.value = null
}

async function handleReject(id: string) {
  processingId.value = id
  await new Promise((r) => setTimeout(r, 300))
  const idx = queue.value.findIndex((o) => o.shipment.id === id)
  if (idx !== -1) {
    queue.value.splice(idx, 1)
    showToast(`Rejected ${id} — returned to pool`)
  }
  processingId.value = null
}
</script>

<template>
  <div class="space-y-4">
    <!-- Driver header stats — large text for outdoor readability -->
    <section class="rounded-xl border border-outline-variant bg-surface-container p-3">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="font-heading text-headline-md font-bold leading-tight text-on-surface">Delivery Dashboard</h1>
          <p class="text-body-sm text-on-surface-variant">Mobile • Large touch targets • Outdoor readable</p>
        </div>
        <span class="rounded-full bg-primary px-2.5 py-1 text-label-sm font-bold text-on-primary">Driver</span>
      </div>
      <div class="mt-3 grid grid-cols-3 gap-2">
        <div class="rounded-lg bg-surface-low p-2 text-center">
          <div class="font-telemetry-numeric text-lg font-bold text-primary">{{ driverStats.earningsToday }}</div>
          <div class="text-[11px] uppercase tracking-wider text-on-surface-variant">Today</div>
        </div>
        <div class="rounded-lg bg-surface-low p-2 text-center">
          <div class="font-telemetry-numeric text-lg font-bold text-on-surface">{{ driverStats.deliveriesToday }}</div>
          <div class="text-[11px] uppercase tracking-wider text-on-surface-variant">Deliveries</div>
        </div>
        <div class="rounded-lg bg-surface-low p-2 text-center">
          <div class="font-telemetry-numeric text-lg font-bold text-tertiary">{{ driverStats.acceptanceRate }}</div>
          <div class="text-[11px] uppercase tracking-wider text-on-surface-variant">Accept Rate</div>
        </div>
      </div>
    </section>

    <div v-if="toast" class="rounded-xl border border-primary/30 bg-primary/10 px-3 py-2 text-center text-body-sm font-medium text-primary">
      {{ toast }}
    </div>

    <!-- Incoming Orders Queue — core component -->
    <DeliveryIncomingQueue :orders="queue" :processing-id="processingId" @accept="handleAccept" @reject="handleReject" />

    <!-- Accepted preview — shows dispatch result -->
    <section v-if="accepted.length" class="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3">
      <h3 class="flex items-center gap-1.5 font-heading text-label-md font-bold text-emerald-400">
        <MIcon name="task_alt" class="text-[18px]" /> Accepted ({{ accepted.length }})
      </h3>
      <ul class="mt-2 space-y-1">
        <li v-for="o in accepted" :key="o.shipment.id" class="flex items-center justify-between rounded-lg bg-surface-container px-2.5 py-2 text-body-sm">
          <span class="font-mono font-semibold text-on-surface">{{ o.shipment.id }}</span>
          <span class="text-on-surface-variant">{{ o.shipment.origin }} → {{ o.shipment.destination }}</span>
          <MIcon name="check_circle" class="text-[16px] text-emerald-400" />
        </li>
      </ul>
      <NuxtLink to="/orders" class="mt-2 inline-flex min-h-12 w-full items-center justify-center rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 text-label-md font-bold text-emerald-400 hover:bg-emerald-500/20">
        View Active Orders
      </NuxtLink>
    </section>

    <p class="pb-2 text-center text-label-sm text-outline">PWA: standalone • portrait • offline-ready • Install from browser menu</p>
  </div>
</template>
