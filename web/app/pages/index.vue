<script setup lang="ts">
import { activityFeed, recentQueries, type ActivityCategory } from '~~/app/data/shipments'

definePageMeta({ layout: 'user', middleware: 'auth' })

useSeoMeta({
  title: 'Dashboard',
  description: 'Overview of your freight network — live tracking, quick stats, and recent activity across the Sheno logistics grid.',
})

const router = useRouter()
const auth = useAuthStore()

const firstName = computed(() => auth.user?.name?.split(' ')[0] || 'there')

const today = ref('')
const nowUtc = ref('')
onMounted(() => {
  const now = new Date()
  today.value = now.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' })
  nowUtc.value = now.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short',
    hour12: false,
  })
})

const trackingInput = ref('')
const emptyQuery = ref(false)

function trackShipment() {
  const query = trackingInput.value.trim()
  if (!query) {
    emptyQuery.value = true
    return
  }
  router.push(`/shipments/${encodeURIComponent(query)}`)
}

function trackRecent(id: string) {
  trackingInput.value = id
  router.push(`/shipments/${encodeURIComponent(id)}`)
}

type Stat = {
  label: string
  badge: string
  badgeTone: 'primary' | 'tertiary'
  badgeIcon?: string
  value: string
  valueCaption: string
  footnote: string
  footerLabel: string
  footerValue: string
  footerKind: 'bar' | 'stepper' | 'text'
  barPct?: number
  barTone?: 'primary' | 'tertiary'
}

const stats: Stat[] = [
  {
    label: 'Active Shipments',
    badge: '+12% MoM',
    badgeTone: 'primary',
    badgeIcon: 'trending_up',
    value: '24',
    valueCaption: 'In-Transit',
    footnote: '+3 scheduled for carrier release today',
    footerLabel: 'Network Saturation',
    footerValue: '82%',
    footerKind: 'bar',
    barPct: 82,
    barTone: 'primary',
  },
  {
    label: 'Pending Deliveries',
    badge: '2 Pending Customs',
    badgeTone: 'tertiary',
    badgeIcon: 'warning',
    value: '6',
    valueCaption: 'Arriving Today',
    footnote: '4 on schedule for final warehouse intake',
    footerLabel: 'Gate Clearance',
    footerValue: '2 Holds · Rotterdam',
    footerKind: 'stepper',
  },
  {
    label: 'Total Spent This Month',
    badge: '-4.5% vs Forecast',
    badgeTone: 'primary',
    value: '$148,290.00',
    valueCaption: 'USD',
    footnote: '19 Invoices reconciled · 3 draft',
    footerLabel: 'Next Settlement Batch:',
    footerValue: 'Nov 28, 2024',
    footerKind: 'text',
  },
]

const filterTabs: Array<{ key: ActivityCategory | 'updates'; label: string }> = [
  { key: 'updates', label: 'All Updates' },
  { key: 'alerts', label: 'Exceptions & Alerts' },
  { key: 'customs', label: 'Customs' },
  { key: 'delivered', label: 'Delivered' },
]

const activeFilter = ref<ActivityCategory | 'updates'>('updates')

const filteredActivity = computed(() => {
  if (activeFilter.value === 'updates') return activityFeed
  return activityFeed.filter((item) => item.category === activeFilter.value)
})
</script>

<template>
  <main class="bg-background">
    <div class="mx-auto max-w-[1600px] space-y-6 p-6">
      <!-- Track Shipment Command Surface -->
      <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
        <div class="mb-4 flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <div class="flex items-center gap-1 text-label-sm text-on-surface-variant">
              <MIcon name="schedule" class="text-[14px]" />
              <span v-if="today">{{ today }} · Global Telemetry Live</span>
              <span v-else>{{ nowUtc }} · Global Telemetry Live</span>
            </div>
            <h2 class="mt-1 font-heading text-headline-lg font-bold text-on-surface">
              Welcome back, {{ firstName }}
            </h2>
          </div>
          <div class="flex items-center gap-1">
            <span class="flex items-center gap-1 rounded border border-outline-variant bg-surface-container-high px-2.5 py-1 text-label-sm text-on-surface-variant">
              <MIcon name="check_circle" class="text-[14px] text-primary" />
              Port Status: Normal
            </span>
            <span class="flex items-center gap-1 rounded border border-outline-variant bg-surface-container-high px-2.5 py-1 text-label-sm text-on-surface-variant">
              <MIcon name="airplanemode_active" class="text-[14px] text-primary" />
              Air Corridors: Clear
            </span>
          </div>
        </div>

        <form novalidate class="space-y-1" @submit.prevent="trackShipment">
          <div class="flex flex-col gap-1 sm:flex-row">
            <div class="relative flex-1">
              <MIcon name="qr_code_scanner" class="absolute top-1/2 left-3.5 -translate-y-1/2 text-primary" />
              <input
                v-model="trackingInput"
                class="w-full rounded-lg border border-outline-variant bg-surface py-3 pr-4 pl-11 font-body-md font-telemetry-numeric text-body-md text-on-surface transition-colors placeholder:text-outline focus:border-primary focus:outline-none"
                type="text"
                placeholder="Enter Carrier Tracking Number, Container ID, or Waybill (e.g. SHP-89421-US)..."
                aria-label="Tracking number"
                @keyup.enter="trackShipment"
              />
            </div>
            <Button
              type="submit"
              class="flex items-center justify-center gap-1 rounded-lg bg-primary-container px-8 py-3 font-label-md font-bold text-on-primary-container transition-colors duration-150 hover:bg-primary active:scale-[0.98]"
            >
              <MIcon name="travel_explore" class="text-[18px]" />
              <span>Track</span>
            </Button>
          </div>

          <p v-if="emptyQuery" class="text-body-sm text-destructive">
            Enter a tracking number, container ID, or waybill to continue.
          </p>

          <div class="flex flex-wrap items-center gap-1 pt-1">
            <span class="text-label-sm text-outline">Recent Queries:</span>
            <button
              v-for="id in recentQueries"
              :key="id"
              type="button"
              class="rounded border border-outline-variant bg-surface-container-high px-2 py-0.5 font-label-sm font-telemetry-numeric text-primary transition-colors hover:bg-surface-container-highest"
              @click="trackRecent(id)"
            >
              {{ id }}
            </button>
          </div>
        </form>
      </section>

      <!-- Quick Stats Row -->
      <section aria-label="Quick stats" class="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div
          v-for="stat in stats"
          :key="stat.label"
          class="relative flex flex-col justify-between overflow-hidden rounded-xl border border-outline-variant bg-surface-container p-4"
        >
          <div>
            <div class="mb-1 flex items-center justify-between">
              <span class="text-label-sm uppercase tracking-wider text-on-surface-variant">{{ stat.label }}</span>
              <span
                class="flex items-center gap-0.5 rounded border px-1.5 py-0.5 text-label-sm font-semibold"
                :class="stat.badgeTone === 'primary'
                  ? 'border-primary/20 bg-primary/10 text-primary'
                  : 'border-tertiary-container/30 bg-tertiary-container/20 text-tertiary'"
              >
                <MIcon v-if="stat.badgeIcon" :name="stat.badgeIcon" class="text-[12px]" />
                {{ stat.badge }}
              </span>
            </div>
            <div class="mb-1 flex items-baseline gap-1">
              <span class="font-heading font-telemetry-numeric text-3xl leading-tight font-bold text-on-surface">{{ stat.value }}</span>
              <span class="text-body-sm font-semibold" :class="stat.badgeTone === 'tertiary' ? 'text-tertiary' : 'text-primary'">
                {{ stat.valueCaption }}
              </span>
            </div>
            <p class="text-body-sm text-on-surface-variant">{{ stat.footnote }}</p>
          </div>

          <div class="mt-4 border-t border-outline-variant/60 pt-4">
            <template v-if="stat.footerKind === 'bar'">
              <div class="mb-1 flex items-center justify-between font-label-sm text-on-surface-variant">
                <span>{{ stat.footerLabel }}</span>
                <span class="font-telemetry-numeric text-on-surface">{{ stat.footerValue }}</span>
              </div>
              <div class="h-1.5 w-full overflow-hidden rounded-full bg-surface-container-high">
                <div class="h-full rounded-full bg-primary" :style="{ width: `${stat.barPct}%` }" />
              </div>
            </template>
            <template v-else-if="stat.footerKind === 'stepper'">
              <div class="flex items-center justify-between font-label-sm">
                <span class="text-on-surface-variant">{{ stat.footerLabel }}</span>
                <span class="font-telemetry-numeric text-tertiary">{{ stat.footerValue }}</span>
              </div>
              <div class="mt-1.5 grid grid-cols-6 gap-1">
                <div v-for="n in 4" :key="`done-${n}`" class="h-1.5 rounded bg-primary" />
                <div v-for="n in 2" :key="`hold-${n}`" class="h-1.5 rounded bg-tertiary" />
              </div>
            </template>
            <template v-else>
              <div class="flex items-center justify-between font-label-sm">
                <span class="text-on-surface-variant">{{ stat.footerLabel }}</span>
                <span class="font-telemetry-numeric font-medium text-on-surface">{{ stat.footerValue }}</span>
              </div>
            </template>
          </div>
        </div>
      </section>

      <!-- Main Content Split -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <!-- Left: Activity Feed -->
        <section class="flex flex-col rounded-xl border border-outline-variant bg-surface-container p-4 lg:col-span-8">
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

        <!-- Right: Quick Actions + Fleet Advisory -->
        <div class="space-y-6 lg:col-span-4">
          <section class="space-y-4 rounded-xl border border-outline-variant bg-surface-container p-4">
            <div>
              <h3 class="font-heading text-headline-sm font-bold text-on-surface">Quick Actions</h3>
              <p class="text-body-sm text-on-surface-variant">Instant logistics orchestration controls</p>
            </div>
            <div class="space-y-1">
              <Button class="w-full items-center justify-between rounded-lg bg-primary-container py-3 font-label-md font-bold text-on-primary-container transition-colors duration-150 hover:bg-primary active:scale-[0.98]" as-child>
                <NuxtLink to="/shipments">
                  <span>Create New Shipment</span>
                  <MIcon name="arrow_forward" class="text-[18px]" />
                </NuxtLink>
              </Button>
              <Button class="w-full items-center justify-between rounded-lg bg-secondary-container py-3 font-label-md font-semibold text-on-secondary-container transition-colors duration-150 hover:opacity-90 active:scale-[0.98]" as-child>
                <NuxtLink to="/shipments?new=quote">
                  <span>Request Freight Quote</span>
                  <MIcon name="request_quote" class="text-[18px]" />
                </NuxtLink>
              </Button>
            </div>
            <div class="space-y-1 border-t border-outline-variant pt-1">
              <span class="block py-1 text-label-sm uppercase tracking-wider text-outline">Operational Shortcuts</span>
              <NuxtLink to="/shipments" class="flex items-center justify-between rounded-lg p-2 text-body-sm text-on-surface-variant transition-colors hover:bg-surface-container-high hover:text-on-surface">
                <span class="flex items-center gap-1">
                  <MIcon name="download" class="text-[16px] text-primary" />
                  <span>Download Monthly Manifest (CSV)</span>
                </span>
                <MIcon name="chevron_right" class="text-[14px] text-outline" />
              </NuxtLink>
              <NuxtLink to="/profile" class="flex items-center justify-between rounded-lg p-2 text-body-sm text-on-surface-variant transition-colors hover:bg-surface-container-high hover:text-on-surface">
                <span class="flex items-center gap-1">
                  <MIcon name="eco" class="text-[16px] text-primary" />
                  <span>Carbon Offset Report</span>
                </span>
                <MIcon name="chevron_right" class="text-[14px] text-outline" />
              </NuxtLink>
              <NuxtLink to="/shipments?new=quote" class="flex items-center justify-between rounded-lg p-2 text-body-sm text-on-surface-variant transition-colors hover:bg-surface-container-high hover:text-on-surface">
                <span class="flex items-center gap-1">
                  <MIcon name="schedule_send" class="text-[16px] text-primary" />
                  <span>Schedule Carrier Pickup</span>
                </span>
                <MIcon name="chevron_right" class="text-[14px] text-outline" />
              </NuxtLink>
            </div>
          </section>

          <section class="relative overflow-hidden rounded-xl border border-outline-variant bg-surface-container p-4">
            <div class="flex items-start gap-2">
              <div class="rounded-lg border border-tertiary-container/30 bg-tertiary-container/20 p-2 text-tertiary">
                <MIcon name="warning_amber" class="text-[20px]" />
              </div>
              <div>
                <div class="flex items-center gap-1">
                  <h4 class="font-heading text-[15px] font-semibold text-on-surface">Fleet Advisory: North Atlantic</h4>
                  <span class="rounded border border-tertiary-container/30 bg-surface-container-high px-1.5 py-0.5 text-[10px] font-semibold uppercase text-tertiary">Caution</span>
                </div>
                <p class="mt-1.5 text-body-sm leading-relaxed text-on-surface-variant">
                  Severe meteorological depression active across Corridor NA-4. Routing algorithms have automatically offset deep-draft container vessels 45 nautical miles south.
                </p>
                <div class="mt-3 flex items-center justify-between border-t border-outline-variant/60 pt-2 text-label-sm text-on-surface-variant">
                  <span class="font-medium text-primary">Zero system downtime detected</span>
                  <NuxtLink to="/shipments" class="underline transition-colors hover:text-primary">Details</NuxtLink>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  </main>
</template>