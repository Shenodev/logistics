<script setup lang="ts">
import type { ActivityCategory, ActivityItem } from '~~/app/data/shipments'

interface Props {
  items: ActivityItem[]
}

const props = defineProps<Props>()

const filterTabs: Array<{ key: ActivityCategory | 'updates'; label: string }> = [
  { key: 'updates', label: 'All Updates' },
  { key: 'alerts', label: 'Exceptions & Alerts' },
  { key: 'customs', label: 'Customs' },
  { key: 'delivered', label: 'Delivered' },
]

const activeFilter = ref<ActivityCategory | 'updates'>('updates')

const filteredActivity = computed(() => {
  if (activeFilter.value === 'updates') return props.items
  return props.items.filter((item) => item.category === activeFilter.value)
})
</script>

<template>
  <section class="flex flex-col rounded-xl border border-outline-variant bg-surface-container p-4">
    <div class="flex flex-col justify-between gap-2 border-b border-outline-variant pb-4 sm:flex-row sm:items-center">
      <div>
        <h3 class="font-heading text-headline-sm font-bold text-on-surface">Recent Activity Feed</h3>
        <p class="text-body-sm text-on-surface-variant">Continuous telemetry stream from freight corridors</p>
      </div>
      <div class="flex items-center gap-1 rounded-lg border border-outline-variant bg-surface-low p-1">
        <button
          v-for="tab in filterTabs"
          :key="tab.key"
          type="button"
          class="rounded px-2.5 py-1 text-label-sm transition-colors"
          :class="activeFilter === tab.key
            ? 'bg-surface-container-highest font-semibold text-primary'
            : 'font-label-sm text-on-surface-variant hover:text-on-surface'"
          @click="activeFilter = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <ol class="flex-1 space-y-4 py-4">
      <li v-for="item in filteredActivity" :key="item.id" class="flex gap-4">
        <div class="flex flex-col items-center">
          <div class="z-10 flex size-8 items-center justify-center rounded-full border border-outline-variant bg-surface-container-high text-primary">
            <MIcon :name="item.icon" class="text-[16px]" />
          </div>
          <div class="mt-1 h-full w-px bg-outline-variant" />
        </div>
        <div class="flex-1 pb-2">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-1">
              <NuxtLink
                :to="`/shipments/${item.shipmentId}`"
                class="text-body-md font-semibold text-primary hover:underline"
              >
                {{ item.shipmentId }}
              </NuxtLink>
              <span class="rounded border border-outline-variant bg-surface-container-high px-1.5 py-0.5 text-label-sm text-on-surface-variant">
                {{ item.mode }}
              </span>
            </div>
            <span class="font-telemetry-numeric text-label-sm text-outline">{{ item.time }}</span>
          </div>
          <p class="mt-1 text-body-md text-on-surface">{{ item.title }}</p>
          <div class="mt-2 flex items-center gap-4 text-label-sm text-on-surface-variant">
            <span class="flex items-center gap-1">
              <MIcon name="location_on" class="text-[14px]" />
              {{ item.location }}
            </span>
            <span class="flex items-center gap-1">
              <MIcon name="directions_boat" class="text-[14px]" />
              {{ item.carrier }}
            </span>
          </div>
        </div>
      </li>
      <li v-if="filteredActivity.length === 0" class="py-4 text-center text-body-sm text-on-surface-variant">
        No events in this category right now.
      </li>
    </ol>

    <div class="flex justify-center border-t border-outline-variant pt-2">
      <NuxtLink to="/shipments" class="flex items-center gap-1 text-label-md text-primary transition-colors hover:text-on-surface">
        <span>View Full Manifest History</span>
        <MIcon name="arrow_forward" class="text-[16px]" />
      </NuxtLink>
    </div>
  </section>
</template>