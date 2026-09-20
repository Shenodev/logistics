<script setup lang="ts">
import { STATUS_FLOW, type ShipmentStatus } from '~~/app/data/shipments'

definePageMeta({ layout: 'user', middleware: 'auth' })

useSeoMeta({
  title: 'My Shipments',
  description: 'Browse every consignment on your account — track shipments and view chain of custody.',
})

const { list, fetchOrders, isLoading } = useShipments()

// Connect user portal to Django DRF via $fetch (HttpOnly JWT cookie, credentials:include)
onMounted(() => {
  fetchOrders()
})

const statusFilter = ref<'all' | ShipmentStatus>('all')

const filteredList = computed(() => {
  if (statusFilter.value === 'all') return list.value
  return list.value.filter((shipment) => shipment.status === statusFilter.value)
})

const statusTabs: Array<{ key: 'all' | ShipmentStatus; label: string }> = [
  { key: 'all', label: 'All' },
  { key: 'order_received', label: 'Order Received' },
  { key: 'in_transit', label: 'In Transit' },
  { key: 'out_for_delivery', label: 'Out for Delivery' },
  { key: 'booked', label: 'Order Received' },
  { key: 'delivered', label: 'Delivered' },
]

const badgeTone: Record<ShipmentStatus, string> = {
  order_received: 'border-outline-variant bg-surface-container-high text-on-surface-variant',
  booked: 'border-outline-variant bg-surface-container-high text-on-surface-variant',
  in_transit: 'border-primary/30 bg-primary-container/10 text-primary',
  out_for_delivery: 'border-tertiary-container/30 bg-tertiary-container/15 text-tertiary',
  delivered: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
}
</script>

<template>
  <main class="bg-background">
    <div class="mx-auto max-w-[1600px] space-y-6 p-6">
      <!-- Header — read-only -->
      <section class="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div class="flex items-center gap-2 text-body-sm text-on-surface-variant">
            <span class="font-label-md uppercase tracking-wider text-on-surface-variant">Global Freight Portal</span>
            <span class="text-outline-variant">/</span>
            <span class="text-primary font-medium">Shipments</span>
          </div>
          <h1 class="mt-1 font-heading text-headline-lg font-bold tracking-tight text-on-surface">
            My Shipments
          </h1>
          <p class="text-body-sm text-on-surface-variant">{{ list.length }} consignments across your network — tracking only</p>
        </div>
      </section>

      <!-- Filters -->
      <section class="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div class="flex items-center gap-1 rounded-lg border border-outline-variant bg-surface-low p-1">
          <button
            v-for="tab in statusTabs"
            :key="tab.key"
            type="button"
            class="rounded px-2.5 py-1 text-label-sm transition-colors"
            :class="statusFilter === tab.key
              ? 'bg-surface-container-highest font-semibold text-primary'
              : 'text-on-surface-variant hover:text-on-surface'"
            @click="statusFilter = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>
        <span class="text-label-sm text-on-surface-variant">{{ filteredList.length }} shown</span>
      </section>

      <!-- Shipments list — read-only -->
      <section aria-label="Shipments" class="rounded-xl border border-outline-variant bg-surface-container">
        <ul class="divide-y divide-outline-variant/60">
          <li v-for="shipment in filteredList" :key="shipment.id">
            <NuxtLink
              :to="`/shipments/${shipment.id}`"
              class="flex flex-col gap-3 p-4 transition-colors hover:bg-surface-container-high md:flex-row md:items-center md:justify-between"
            >
              <div class="flex items-center gap-3">
                <div class="flex size-10 shrink-0 items-center justify-center rounded-lg border border-outline-variant bg-surface-low text-primary">
                  <MIcon
                    :name="shipment.status === 'delivered' ? 'verified' : shipment.status === 'in_transit' ? 'airplanemode_active' : 'local_shipping'"
                    class="text-[20px]"
                  />
                </div>
                <div>
                  <div class="flex items-center gap-2">
                    <span class="font-telemetry-numeric font-semibold text-on-surface">{{ shipment.id }}</span>
                    <span class="rounded border border-outline-variant bg-surface-container-high px-1.5 py-0.5 text-label-sm text-on-surface-variant">{{ shipment.mode }}</span>
                  </div>
                  <p class="mt-0.5 text-body-sm text-on-surface-variant">
                    {{ shipment.origin }} ({{ shipment.originCode }}) → {{ shipment.destination }} ({{ shipment.destinationCode }})
                  </p>
                </div>
              </div>
              <div class="flex items-center gap-4 pl-13 md:pl-0">
                <div class="text-right">
                  <p class="text-label-sm text-on-surface-variant">ETA</p>
                  <p class="font-heading text-label-md font-semibold text-on-surface">{{ shipment.eta }}</p>
                </div>
                <span class="rounded px-2 py-1 text-label-sm font-semibold" :class="badgeTone[shipment.status]">
                  {{ STATUS_FLOW[shipment.status].label }}
                </span>
                <MIcon name="chevron_right" class="text-[16px] text-outline" />
              </div>
            </NuxtLink>
          </li>
          <li v-if="filteredList.length === 0" class="px-4 py-10 text-center">
            <MIcon name="inventory_2" class="text-[28px] text-outline" />
            <p class="mt-2 text-body-sm text-on-surface-variant">No shipments match this filter yet.</p>
          </li>
        </ul>
      </section>

      <p class="text-center text-body-sm text-on-surface-variant">
        Need help? <NuxtLink to="/profile" class="text-primary hover:underline">Contact Support via Profile</NuxtLink>
      </p>
    </div>
  </main>
</template>
