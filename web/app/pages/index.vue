<script setup lang="ts">
import { activityFeed, recentQueries } from '~~/app/data/shipments'
import { incomingSeed } from '~~/app/data/delivery'

definePageMeta({ layout: 'user', middleware: 'auth' })

const appRole = useAppRole()
const isDelivery = computed(() => appRole === 'delivery')

// Delivery dashboard state (mobile-first, re-used on / for delivery PWA)
const deliveryQueue = ref([...incomingSeed])
const deliveryProcessing = ref<string | null>(null)
const deliveryToast = ref<string | null>(null)
function onDeliveryAccept(id: string) {
  deliveryProcessing.value = id
  setTimeout(() => {
    deliveryQueue.value = deliveryQueue.value.filter((o) => o.shipment.id !== id)
    deliveryProcessing.value = null
    deliveryToast.value = `Accepted ${id}`
    setTimeout(() => (deliveryToast.value = null), 2000)
    if ('vibrate' in navigator) navigator.vibrate(20)
  }, 500)
}
function onDeliveryReject(id: string) {
  deliveryProcessing.value = id
  setTimeout(() => {
    deliveryQueue.value = deliveryQueue.value.filter((o) => o.shipment.id !== id)
    deliveryProcessing.value = null
    deliveryToast.value = `Rejected ${id}`
    setTimeout(() => (deliveryToast.value = null), 2000)
  }, 300)
}

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

const stats = [
  {
    label: 'Active Shipments',
    badge: '+12% MoM',
    badgeTone: 'primary' as const,
    badgeIcon: 'trending_up',
    value: '24',
    valueCaption: 'In-Transit',
    footnote: '+3 scheduled for carrier release today',
    footerLabel: 'Network Saturation',
    footerValue: '82%',
    footerKind: 'bar' as const,
    barPct: 82,
  },
  {
    label: 'Pending Deliveries',
    badge: '2 Pending Customs',
    badgeTone: 'tertiary' as const,
    badgeIcon: 'warning',
    value: '6',
    valueCaption: 'Arriving Today',
    footnote: '4 on schedule for final warehouse intake',
    footerLabel: 'Gate Clearance',
    footerValue: '2 Holds · Rotterdam',
    footerKind: 'stepper' as const,
  },
  {
    label: 'Total Spent This Month',
    badge: '-4.5% vs Forecast',
    badgeTone: 'primary' as const,
    value: '$148,290.00',
    valueCaption: 'USD',
    footnote: '19 Invoices reconciled · 3 draft',
    footerLabel: 'Next Settlement Batch:',
    footerValue: 'Nov 28, 2024',
    footerKind: 'text' as const,
  },
]
</script>

<template>
  <!-- Delivery PWA: mobile-first dashboard at root -->
  <main v-if="isDelivery" class="bg-background">
    <div class="mx-auto w-full max-w-md space-y-4 p-4 pb-6">
      <div class="rounded-xl border border-outline-variant bg-surface-container p-3">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="font-heading text-headline-md font-bold text-on-surface">Delivery Dashboard</h1>
            <p class="text-body-sm text-on-surface-variant">Mobile • Large touch targets</p>
          </div>
          <span class="rounded-full bg-primary px-2.5 py-1 text-label-sm font-bold text-on-primary">Online</span>
        </div>
        <div class="mt-3 grid grid-cols-3 gap-2 text-center">
          <div class="rounded-lg bg-surface-low p-2"><div class="font-telemetry-numeric text-lg font-bold text-primary">3</div><div class="text-[11px] uppercase tracking-wider text-on-surface-variant">Incoming</div></div>
          <div class="rounded-lg bg-surface-low p-2"><div class="font-telemetry-numeric text-lg font-bold text-on-surface">1</div><div class="text-[11px] uppercase tracking-wider text-on-surface-variant">Active</div></div>
          <div class="rounded-lg bg-surface-low p-2"><div class="font-telemetry-numeric text-lg font-bold text-tertiary">96%</div><div class="text-[11px] uppercase tracking-wider text-on-surface-variant">Rate</div></div>
        </div>
      </div>
      <div v-if="deliveryToast" class="rounded-xl border border-primary/30 bg-primary/10 px-3 py-2 text-center text-body-sm font-medium text-primary">{{ deliveryToast }}</div>
      <DeliveryIncomingQueue :orders="deliveryQueue" :processing-id="deliveryProcessing" @accept="onDeliveryAccept" @reject="onDeliveryReject" />
      <NuxtLink to="/incoming" class="flex min-h-12 w-full items-center justify-center gap-1 rounded-xl border border-outline-variant bg-surface-container px-4 text-label-md font-bold text-primary hover:bg-surface-container-high">
        <MIcon name="inbox" class="text-[20px]" /> Go to Incoming Queue
      </NuxtLink>
    </div>
  </main>
  <main v-else class="bg-background">
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
        <DashboardStatCard
          v-for="stat in stats"
          :key="stat.label"
          v-bind="stat"
        />
      </section>

      <!-- Main Content Split -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <!-- Left: Activity Feed -->
        <div class="lg:col-span-8">
          <DashboardActivityFeed :items="activityFeed" />
        </div>

        <!-- Right: Live Tracking + Fleet Advisory -->
        <div class="space-y-6 lg:col-span-4">
          <DashboardFleetSnapshot />

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