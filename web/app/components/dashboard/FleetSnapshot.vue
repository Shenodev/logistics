<script setup lang="ts">
import { shipments, STATUS_FLOW } from '~~/app/data/shipments'

const MODE_ICONS: Record<string, string> = {
  'Ocean Freight': 'directions_boat',
  'Air Cargo': 'flight',
  Intermodal: 'railway_alert',
  'Ground Fleet': 'local_shipping',
}

const active = computed(() => shipments.filter((shipment) => shipment.status !== 'delivered').slice(0, 4))
</script>

<template>
  <section class="rounded-xl border border-outline-variant bg-surface-container p-4">
    <div>
      <h3 class="font-heading text-headline-sm font-bold text-on-surface">Live Fleet Snapshot</h3>
      <p class="text-body-sm text-on-surface-variant">Active bookings under automated tracking</p>
    </div>

    <ul class="mt-2 space-y-1 border-t border-outline-variant pt-2">
      <li v-for="shipment in active" :key="shipment.id" class="rounded-lg p-2 transition-colors hover:bg-surface-container-high">
        <div class="flex items-start gap-3">
          <div class="flex size-9 shrink-0 items-center justify-center rounded-lg border border-outline-variant bg-surface-container-high text-primary">
            <MIcon :name="MODE_ICONS[shipment.mode] ?? 'local_shipping'" class="text-[18px]" />
          </div>
          <div class="min-w-0 flex-1">
            <div class="flex items-center justify-between gap-2">
              <NuxtLink :to="`/shipments/${shipment.id}`" class="truncate text-body-sm font-semibold text-primary hover:underline">
                {{ shipment.id }}
              </NuxtLink>
              <span class="shrink-0 rounded border px-1.5 py-0.5 text-[11px] font-semibold"
                :class="shipment.status === 'out_for_delivery'
                  ? 'border-primary/20 bg-primary/10 text-primary'
                  : 'border-outline-variant bg-surface-container-high text-on-surface-variant'"
              >
                {{ STATUS_FLOW[shipment.status].label }}
              </span>
            </div>
            <p class="mt-0.5 truncate text-label-sm text-on-surface-variant">
              {{ shipment.originCode }} → {{ shipment.destinationCode }}
            </p>
            <div class="mt-2 flex items-center justify-between gap-2">
              <span class="text-label-sm font-medium text-on-surface-variant">ETA {{ shipment.eta }}</span>
              <span class="font-telemetry-numeric text-label-sm text-outline">{{ shipment.mode }}</span>
            </div>
            <div class="mt-1.5 h-1 w-full overflow-hidden rounded-full bg-surface-container-high">
              <div class="h-full rounded-full bg-primary" :style="{ width: `${shipment.timelineFillPct}%` }" />
            </div>
          </div>
        </div>
      </li>
    </ul>

    <NuxtLink to="/shipments" class="mt-2 flex items-center justify-center gap-1 border-t border-outline-variant pt-2 text-label-md text-primary transition-colors hover:text-on-surface">
      <span>Track All Shipments</span>
      <MIcon name="arrow_forward" class="text-[16px]" />
    </NuxtLink>
  </section>
</template>