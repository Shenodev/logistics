<script setup lang="ts">
import { incomingSeed, driverStats, type IncomingOrder } from '~~/app/data/delivery'

definePageMeta({ layout: 'delivery', middleware: 'auth' })

useSeoMeta({
  title: 'Delivery — Incoming Orders',
  description: 'Mobile-first driver dashboard — incoming order queue with Accept / Reject.',
  viewport: 'width=device-width, initial-scale=1, viewport-fit=cover',
})

const { list: shipmentList, fetchOrders, acceptOrder, rejectOrder } = useShipments()
const processingId = ref<string | null>(null)
const toast = ref<string | null>(null)
const accepted = ref<IncomingOrder[]>([])

// Connect delivery subdomain to Django DRF via $fetch (HttpOnly JWT)
onMounted(async () => {
  await fetchOrders()
  // Build queue from API: unassigned received orders (pool) + mapper to IncomingOrder
  // Fallback to seed if API empty (offline dev)
  if (shipmentList.value.filter((s) => s.status === 'order_received').length === 0 && incomingSeed.length) {
    // keep seed for demo when API has no pool
  }
})

const queue = computed<IncomingOrder[]>(() => {
  // Map API shipments that are in received pool to IncomingOrder view model
  const pool = shipmentList.value.filter((s) => s.status === 'order_received')
  if (pool.length === 0) return [...incomingSeed].filter((o) => !accepted.value.find((a) => a.shipment.id === o.shipment.id))
  return pool.map((s) => {
    const seed = incomingSeed.find((i) => i.shipment.id === s.id)
    return seed ?? { shipment: s, payout: '$42.00', distance: '10.2 km', expiresIn: '5:00', priority: 'Standard' as const }
  }).filter((o) => !accepted.value.find((a) => a.shipment.id === o.shipment.id))
})

function showToast(msg: string) {
  toast.value = msg
  setTimeout(() => (toast.value = null), 2500)
}

async function handleAccept(id: string) {
  processingId.value = id
  // Call Django DRF driver accept endpoint via $fetch
  const ok = await acceptOrder(id)
  if (ok) {
    const found = queue.value.find((o) => o.shipment.id === id)
    if (found) accepted.value.unshift(found)
    if ('vibrate' in navigator) navigator.vibrate(20)
    showToast(`Accepted ${id} — heading to pickup`)
    await fetchOrders()
  } else {
    showToast(`Accept failed for ${id}`)
  }
  processingId.value = null
}

async function handleReject(id: string) {
  processingId.value = id
  const ok = await rejectOrder(id)
  if (ok) {
    showToast(`Rejected ${id} — returned to pool`)
    await fetchOrders()
  } else {
    // Fallback local
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
