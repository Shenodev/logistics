<template>
  <main class="flex-1">
    <div class="mx-auto w-full max-w-6xl px-4 py-8 lg:px-6 lg:py-10">
      <div class="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p class="font-heading text-xs font-semibold uppercase tracking-widest text-cyan-400">
            Fleet overview
          </p>
          <h1 class="mt-2 font-heading text-3xl font-bold tracking-tight text-foreground">
            Welcome back, {{ firstName }} <span v-if="today" class="font-normal text-muted-foreground">· {{ today }}</span>
          </h1>
          <p class="mt-1.5 text-sm text-muted-foreground">
            {{ greetingLine }}
          </p>
        </div>
        <Button variant="secondary" size="sm" class="bg-secondary text-secondary-foreground" @click="scrollToTracking">
          Track a shipment
        </Button>
      </div>

      <section aria-label="Quick stats" class="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Card class="gap-0 border-border bg-card/50">
          <CardHeader class="flex-row items-center justify-between px-5 py-4">
            <p class="text-sm text-muted-foreground">In transit</p>
            <span class="flex size-9 items-center justify-center rounded-lg bg-cyan-500/15 text-cyan-400">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="size-5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 6h10l2 4v6h-2M8 6 6 10H2a1 1 0 0 0-1 1v5h2" />
                <circle cx="6" cy="17.5" r="1.8" />
                <circle cx="16" cy="17.5" r="1.8" />
              </svg>
            </span>
          </CardHeader>
          <CardContent class="px-5 pb-4">
            <p class="font-mono text-3xl font-semibold tracking-tight text-foreground">24</p>
            <p class="mt-1 flex items-center gap-1.5 text-xs text-muted-foreground">
              <span class="text-emerald-400">+4</span> vs. yesterday
            </p>
          </CardContent>
        </Card>

        <Card class="gap-0 border-border bg-card/50">
          <CardHeader class="flex-row items-center justify-between px-5 py-4">
            <p class="text-sm text-muted-foreground">Pickups today</p>
            <span class="flex size-9 items-center justify-center rounded-lg bg-cyan-500/15 text-cyan-400">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="size-5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 8h11v8H4zM15 10h3l2 2v4h-5z" />
              </svg>
            </span>
          </CardHeader>
          <CardContent class="px-5 pb-4">
            <p class="font-mono text-3xl font-semibold tracking-tight text-foreground">12</p>
            <p class="mt-1 flex items-center gap-1.5 text-xs text-muted-foreground">
              <span class="text-amber-400">3 due</span> by 14:00
            </p>
          </CardContent>
        </Card>

        <Card class="gap-0 border-border bg-card/50">
          <CardHeader class="flex-row items-center justify-between px-5 py-4">
            <p class="text-sm text-muted-foreground">Delivered this month</p>
            <span class="flex size-9 items-center justify-center rounded-lg bg-cyan-500/15 text-cyan-400">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="size-5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 7h16v10H4zM8 7V4h8v3" />
                <path stroke-linecap="round" stroke-linejoin="round" d="m8.5 14.5 2.4 2.4 4.6-4.6" />
              </svg>
            </span>
          </CardHeader>
          <CardContent class="px-5 pb-4">
            <p class="font-mono text-3xl font-semibold tracking-tight text-foreground">186</p>
            <p class="mt-1 flex items-center gap-1.5 text-xs text-muted-foreground">
              <span class="text-emerald-400">+12%</span> vs. last month
            </p>
          </CardContent>
        </Card>

        <Card class="gap-0 border-border bg-card/50">
          <CardHeader class="flex-row items-center justify-between px-5 py-4">
            <p class="text-sm text-muted-foreground">On-time rate</p>
            <span class="flex size-9 items-center justify-center rounded-lg bg-cyan-500/15 text-cyan-400">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="size-5" aria-hidden="true">
                <circle cx="12" cy="12" r="8.5" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 7.5V12l3 2" />
              </svg>
            </span>
          </CardHeader>
          <CardContent class="px-5 pb-4">
            <p class="font-mono text-3xl font-semibold tracking-tight text-foreground">93%</p>
            <Progress :model-value="93" class="mt-2" />
            <p class="mt-1.5 text-xs text-muted-foreground">Last 30 days</p>
          </CardContent>
        </Card>
      </section>

      <div class="mt-6 grid gap-6 lg:grid-cols-[1.55fr_1fr]">
        <Card id="tracking" class="border-border bg-card/50">
          <CardHeader>
            <CardTitle class="font-heading text-lg font-semibold tracking-tight">
              Track a shipment
            </CardTitle>
            <CardDescription>
              Enter a consignment reference to see live status and estimated delivery.
            </CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <form class="flex flex-col gap-3 sm:flex-row" novalidate @submit.prevent="trackShipment">
              <Input
                v-model="trackingInput"
                placeholder="e.g. SN-2026-0118"
                inputmode="text"
                aria-label="Shipment reference"
                class="bg-secondary border-border h-10 font-mono"
                @keyup.enter="trackShipment"
              />
              <Button type="submit" class="gap-1.5 h-10 shrink-0" :disabled="searchState === 'loading'">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="size-4" aria-hidden="true">
                  <circle cx="11" cy="11" r="7" />
                  <path stroke-linecap="round" d="m20 20-3.5-3.5" />
                </svg>
                Track
              </Button>
            </form>

            <p v-if="searchState === 'empty'" class="text-sm text-destructive">
              Enter a shipment reference to track it.
            </p>
            <p v-else-if="searchState === 'not_found'" class="text-sm text-destructive">
              No shipment found for <code class="font-mono">{{ trackingInput }}</code>. Double-check the reference and try again.
            </p>

            <Transition name="track-result" mode="out-in">
              <div v-if="searchState === 'loading'" key="loading" class="space-y-3">
                <Skeleton class="h-4 w-2/3 bg-secondary" />
                <Skeleton class="h-10 w-full bg-secondary" />
                <Skeleton class="h-3 w-1/2 bg-secondary" />
              </div>

              <div v-else-if="searchState === 'found' && result" key="result" class="rounded-xl border border-border bg-secondary/40 p-4">
                <div class="flex flex-wrap items-center justify-between gap-2">
                  <code class="font-mono text-sm font-semibold text-cyan-300">{{ result.id }}</code>
                  <Badge class="bg-cyan-500/15 text-cyan-300">
                    {{ STATUS_FLOW[result.status].label }}
                  </Badge>
                </div>

                <div class="mt-4">
                  <div class="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{{ result.origin }}</span>
                    <span>{{ result.destination }}</span>
                  </div>
                  <div class="mt-2 flex items-center gap-2">
                    <template v-for="(stage, i) in STATUS_STAGES" :key="stage">
                      <span
                        class="size-2 shrink-0 rounded-full transition-colors"
                        :class="i <= currentStageIndex ? 'bg-cyan-400' : 'bg-border'"
                      />
                      <span
                        v-if="i < STATUS_STAGES.length - 1"
                        :key="`connector-${i}`"
                        class="h-0.5 flex-1 rounded-full"
                        :class="i < currentStageIndex ? 'bg-cyan-400/70' : 'bg-border'"
                      />
                    </template>
                  </div>
                  <div class="mt-2 flex items-center justify-between gap-1 text-[10px] uppercase tracking-wide text-muted-foreground">
                    <template v-for="(stage, i) in STATUS_STAGES" :key="stage">
                      <span class="whitespace-nowrap" :class="i <= currentStageIndex ? 'text-cyan-300' : ''">{{ stage }}</span>
                    </template>
                  </div>
                </div>

                <div class="mt-4 grid grid-cols-2 gap-3 border-t border-border/60 pt-3 text-sm">
                  <div>
                    <p class="text-xs text-muted-foreground">ETA</p>
                    <p class="font-mono font-medium text-foreground">{{ result.eta }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-muted-foreground">Carrier</p>
                    <p class="font-medium text-foreground">{{ result.carrier }}</p>
                  </div>
                </div>
              </div>
            </Transition>
          </CardContent>
        </Card>

        <Card class="border-border bg-card/50">
          <CardHeader class="flex-row items-center justify-between">
            <div class="space-y-1">
              <CardTitle class="font-heading text-lg font-semibold tracking-tight">
                Recent activity
              </CardTitle>
              <CardDescription class="text-sm">
                Latest movements across your network.
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent class="pt-0">
            <Tabs v-model="activityFilter" default-value="all" class="mb-4">
              <TabsList class="w-full bg-secondary/60">
                <TabsTrigger value="all" class="flex-1">All</TabsTrigger>
                <TabsTrigger value="shipment" class="flex-1">Shipments</TabsTrigger>
                <TabsTrigger value="system" class="flex-1">System</TabsTrigger>
              </TabsList>
            </Tabs>

            <ol class="space-y-1">
              <li
                v-for="item in filteredActivity"
                :key="item.id"
                class="flex gap-3 rounded-lg px-2 py-2.5 transition-colors hover:bg-secondary/40"
              >
                <span
                  class="mt-0.5 size-8 shrink-0 rounded-lg border border-border bg-secondary/60 flex items-center justify-center"
                  :class="item.kind === 'system' ? 'text-muted-foreground' : 'text-cyan-400'"
                >
                  <svg v-if="item.kind === 'shipment'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="size-4" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8 6h10l2 4v6h-2M8 6 6 10H2a1 1 0 0 0-1 1v5h2" />
                    <circle cx="6" cy="17.5" r="1.8" />
                    <circle cx="16" cy="17.5" r="1.8" />
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="size-4" aria-hidden="true">
                    <circle cx="12" cy="12" r="3.2" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 3.2v2.4M12 18.4v2.4M3.2 12h2.4M18.4 12h2.4" />
                  </svg>
                </span>
                <div class="min-w-0 flex-1">
                  <div class="flex items-baseline justify-between gap-2">
                    <p class="truncate text-sm font-medium text-foreground">{{ item.title }}</p>
                    <span class="shrink-0 text-xs text-muted-foreground">{{ item.time }}</span>
                  </div>
                  <p class="truncate text-xs text-muted-foreground">{{ item.body }}</p>
                </div>
              </li>
              <li v-if="filteredActivity.length === 0" class="px-2 py-4 text-sm text-muted-foreground">
                No activity in this category yet.
              </li>
            </ol>
          </CardContent>
        </Card>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

useSeoMeta({
  title: 'Dashboard',
  description: 'Overview of your freight network — quick stats, recent activity, and shipment tracking.',
})

const auth = useAuthStore()

const firstName = computed(() => auth.user?.name?.split(' ')[0] || 'there')
const greetingLine = computed(() =>
  auth.isAdmin
    ? 'Network-wide dispatch view for assigned freight and fleet.'
    : "Here's what's moving across your network today.",
)

const today = ref('')
onMounted(() => {
  today.value = new Date().toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
  })
})

type TrackingStatus = 'booked' | 'pickup' | 'in_transit' | 'out_for_delivery' | 'delivered'

interface Shipment {
  id: string
  origin: string
  destination: string
  status: TrackingStatus
  eta: string
  carrier: string
}

const STATUS_STAGES = ['Booked', 'Pickup', 'In transit', 'Out for delivery', 'Delivered']

const STATUS_FLOW: Record<TrackingStatus, { label: string; index: number }> = {
  booked: { label: 'Booked', index: 0 },
  pickup: { label: 'Picked up', index: 1 },
  in_transit: { label: 'In transit', index: 2 },
  out_for_delivery: { label: 'Out for delivery', index: 3 },
  delivered: { label: 'Delivered', index: 4 },
}

const shipments: Shipment[] = [
  {
    id: 'SN-2026-0118',
    origin: 'Port Said',
    destination: 'Cairo Distribution Hub',
    status: 'in_transit',
    eta: 'Thu, 14:30',
    carrier: 'Truck EG-8841',
  },
  {
    id: 'SN-2026-0097',
    origin: 'Alexandria',
    destination: 'Tanta Depot',
    status: 'out_for_delivery',
    eta: 'Today, 16:00',
    carrier: 'Truck EG-5520',
  },
  {
    id: 'SN-2026-0124',
    origin: 'Cairo Hub',
    destination: 'Giza Gateway',
    status: 'booked',
    eta: 'Fri, 09:00',
    carrier: 'Assigned shortly',
  },
]

const trackingInput = ref('')
const searchState = ref<'idle' | 'loading' | 'empty' | 'found' | 'not_found'>('idle')
const result = ref<Shipment | null>(null)
let searchTimer: ReturnType<typeof setTimeout> | undefined

function trackShipment() {
  const query = trackingInput.value.trim()
  if (!query) {
    searchState.value = 'empty'
    result.value = null
    return
  }
  searchState.value = 'loading'
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    const found = shipments.find((shipment) => shipment.id === query.toUpperCase())
    if (found) {
      result.value = found
      searchState.value = 'found'
    }
    else {
      result.value = null
      searchState.value = 'not_found'
    }
  }, 600)
}

const currentStageIndex = computed(() => (result.value ? STATUS_FLOW[result.value.status].index : 0))

function scrollToTracking() {
  if (import.meta.client) {
    document.getElementById('tracking')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

interface ActivityItem {
  id: number
  kind: 'shipment' | 'system'
  title: string
  body: string
  time: string
}

const activity: ActivityItem[] = [
  { id: 1, kind: 'shipment', title: 'SN-2026-0118 departed Port Said', body: 'En route to Cairo Distribution Hub · ETA Thu, 14:30', time: '12m ago' },
  { id: 2, kind: 'shipment', title: 'SN-2026-0097 delivered', body: 'Proof of delivery captured at Tanta Depot', time: '1h ago' },
  { id: 3, kind: 'system', title: 'Rates refreshed', body: '14 lanes updated for the upcoming week', time: '3h ago' },
  { id: 4, kind: 'shipment', title: 'SN-2026-0124 booked', body: 'Pickup window confirmed for Fri, 08:00–10:00', time: '6h ago' },
  { id: 5, kind: 'system', title: 'Fleet check completed', body: 'All 31 vehicles passed the morning inspection', time: '9h ago' },
  { id: 6, kind: 'shipment', title: 'SN-2026-0084 damaged on arrival', body: 'Claim filed against carrier · review pending', time: '1d ago' },
]

const activityFilter = ref<'all' | 'shipment' | 'system'>('all')
const filteredActivity = computed(() => {
  if (activityFilter.value === 'all') {
    return activity
  }
  return activity.filter((item) => item.kind === activityFilter.value)
})

onUnmounted(() => clearTimeout(searchTimer))
</script>

<style scoped>
.track-result-enter-active,
.track-result-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.track-result-enter-from,
.track-result-leave-to {
  opacity: 0;
  transform: translateY(4px);
}
</style>