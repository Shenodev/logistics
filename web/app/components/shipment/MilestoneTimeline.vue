<script setup lang="ts">
import type { Shipment } from '~~/app/data/shipments'

interface Props {
  shipment: Shipment
}

defineProps<Props>()
</script>

<template>
  <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Consignment Progress &amp; Chain of Custody</h2>
        <p class="mt-0.5 text-body-sm text-on-surface-variant">Automated timestamp verification recorded on carrier ledger</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="rounded border border-outline-variant bg-surface-container-high px-2.5 py-1 text-label-sm text-on-surface-variant">
          Current Phase: <strong class="font-medium text-primary">{{ shipment.currentPhase }}</strong>
        </span>
      </div>
    </div>

    <div class="relative py-2">
      <div class="absolute top-[26px] right-[5%] left-[5%] z-0 h-0.5 -translate-y-1/2 bg-outline-variant">
        <div class="h-full bg-primary" :style="{ width: `${shipment.timelineFillPct}%` }" />
      </div>

      <div class="relative z-10 grid grid-cols-6 gap-2 text-center">
        <div
          v-for="milestone in shipment.milestones"
          :key="milestone.label"
          class="flex flex-col items-center"
          :class="milestone.state === 'upcoming' ? 'opacity-40' : milestone.state === 'active' ? '' : 'opacity-100'"
        >
          <!-- Vue conditional rendering: active vs done vs upcoming -->
          <div v-if="milestone.state === 'active'" class="relative mb-2">
            <div class="flex size-12 items-center justify-center rounded-full border-2 border-primary bg-primary-container font-bold text-on-primary-container">
              <MIcon :name="milestone.icon" class="text-[24px]" />
            </div>
            <span class="radar-pulse pointer-events-none absolute -inset-1 rounded-full border border-primary" />
          </div>
          <div
            v-else
            class="mb-2 flex size-12 items-center justify-center rounded-full border-2 bg-surface-container-highest"
            :class="milestone.state === 'done' ? 'border-primary text-primary' : 'border-outline-variant bg-surface-low text-outline'"
          >
            <MIcon :name="milestone.icon" class="text-[22px]" />
          </div>
          <div class="text-label-md font-semibold" :class="milestone.state === 'active' ? 'font-bold text-primary' : 'text-on-surface'">
            {{ milestone.label }}
          </div>
          <div class="mt-0.5 text-body-sm" :class="milestone.state === 'active' ? 'font-medium text-on-surface' : 'text-on-surface-variant'">
            {{ milestone.detail }}
          </div>
          <div class="mt-0.5 font-mono text-label-sm text-outline">{{ milestone.time }}</div>
        </div>
      </div>
    </div>
  </section>
</template>
