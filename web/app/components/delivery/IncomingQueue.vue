<script setup lang="ts">
import type { IncomingOrder } from '~~/app/data/delivery'

interface Props {
  orders: IncomingOrder[]
  processingId?: string | null
}

defineProps<Props>()

const emit = defineEmits<{
  accept: [id: string]
  reject: [id: string]
}>()
</script>

<template>
  <section class="space-y-3">
    <div class="flex items-center justify-between">
      <h2 class="font-heading text-headline-sm font-bold text-on-surface">Incoming Orders Queue</h2>
      <span class="rounded-full border border-primary/30 bg-primary/10 px-2.5 py-1 text-label-sm font-bold text-primary">{{ orders.length }} pending</span>
    </div>
    <p class="text-body-sm leading-relaxed text-on-surface-variant">New automated assignments — tap Accept to claim or Reject to return to pool. Large touch targets for outdoor use.</p>

    <div v-if="orders.length === 0" class="rounded-xl border border-dashed border-outline-variant bg-surface-container p-6 text-center">
      <div class="mx-auto flex size-12 items-center justify-center rounded-full bg-surface-container-high text-primary">
        <MIcon name="inbox" class="text-[24px]" />
      </div>
      <p class="mt-2 font-label-md font-semibold text-on-surface">No incoming orders</p>
      <p class="text-body-sm text-on-surface-variant">New assignments will appear here with haptic alert.</p>
    </div>

    <div v-else class="space-y-3">
      <article
        v-for="order in orders"
        :key="order.shipment.id"
        class="rounded-xl border border-outline-variant bg-surface-container p-3 shadow-sm"
      >
        <div class="flex items-start justify-between gap-2">
          <div class="flex items-center gap-2">
            <div class="flex size-9 items-center justify-center rounded-lg bg-primary-container text-on-primary-container">
              <MIcon name="local_shipping" class="text-[20px]" />
            </div>
            <div>
              <div class="flex items-center gap-1.5">
                <span class="font-mono text-body-md font-bold text-on-surface">{{ order.shipment.id }}</span>
                <span
                  class="rounded-full border px-2 py-0.5 text-[11px] font-bold"
                  :class="order.priority==='Urgent' ? 'border-destructive/40 bg-destructive/10 text-destructive' : order.priority==='Express' ? 'border-primary/30 bg-primary/10 text-primary' : 'border-outline-variant bg-surface-container-high text-on-surface-variant'"
                >
                  {{ order.priority }}
                </span>
              </div>
              <div class="font-mono text-label-sm text-on-surface-variant">Expires in {{ order.expiresIn }}</div>
            </div>
          </div>
          <div class="text-right">
            <div class="font-telemetry-numeric text-lg font-bold text-primary">{{ order.payout }}</div>
            <div class="text-label-sm text-on-surface-variant">{{ order.distance }}</div>
          </div>
        </div>

        <div class="mt-2 space-y-1 rounded-lg bg-surface-low p-2">
          <div class="flex items-center gap-1.5 text-body-sm font-medium text-on-surface">
            <MIcon name="location_on" class="text-[16px] text-primary" />
            <span class="truncate">{{ order.shipment.origin }} ({{ order.shipment.originCode }}) → {{ order.shipment.destination }} ({{ order.shipment.destinationCode }})</span>
          </div>
          <div class="flex items-center gap-3 text-label-sm text-on-surface-variant">
            <span class="flex items-center gap-1"><MIcon name="inventory_2" class="text-[14px]" /> {{ order.shipment.grossWeight }} • {{ order.shipment.pallets }}</span>
            <span class="h-3 w-px bg-outline-variant" />
            <span class="flex items-center gap-1"><MIcon name="schedule" class="text-[14px]" /> {{ order.shipment.nextCheckpointIn }}</span>
          </div>
        </div>

        <!-- Large touch targets: min-h-12 (48px) for outdoor use -->
        <div class="mt-3 grid grid-cols-2 gap-2">
          <button
            type="button"
            class="inline-flex min-h-12 items-center justify-center gap-1.5 rounded-xl border border-outline-variant bg-surface-container-high px-4 text-label-md font-bold text-on-surface-variant transition-colors hover:bg-surface-container hover:text-destructive active:scale-[0.98]"
            :disabled="processingId===order.shipment.id"
            @click="emit('reject', order.shipment.id)"
          >
            <MIcon name="close" class="text-[20px]" />
            Reject
          </button>
          <button
            type="button"
            class="inline-flex min-h-12 items-center justify-center gap-1.5 rounded-xl bg-primary px-4 text-label-md font-bold text-on-primary shadow-sm transition-colors hover:bg-primary/90 active:scale-[0.98] disabled:opacity-50"
            :disabled="processingId===order.shipment.id"
            @click="emit('accept', order.shipment.id)"
          >
            <MIcon v-if="processingId!==order.shipment.id" name="check" class="text-[20px]" />
            <span v-if="processingId===order.shipment.id" class="h-4 w-4 animate-spin rounded-full border-2 border-on-primary border-t-transparent" />
            Accept
          </button>
        </div>
      </article>
    </div>
  </section>
</template>
