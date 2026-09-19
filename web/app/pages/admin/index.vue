<script setup lang="ts">
import { shipments } from '~~/app/data/shipments'

definePageMeta({ middleware: 'admin', layout: 'admin' })

useSeoMeta({
  title: 'Admin — Command Center',
  description: 'Dispatcher command center — global live fleet telemetry, network velocity, and critical exceptions queue. Read-only operations.',
})

const auth = useAuthStore()

type AlertLevel = 'critical' | 'warning'
interface AlertItem {
  id: string
  level: AlertLevel
  category: 'critical' | 'vehicle' | 'delay'
  icon: string
  title: string
  location: string
  description: string
  actions: Array<{ label: string; icon: string; variant: 'primary' | 'danger' | 'ghost' }>
}

const alerts: AlertItem[] = [
  {
    id: 'A1',
    level: 'critical',
    category: 'vehicle',
    icon: 'fmd_bad',
    title: 'Vehicle Breakdown: Truck TR-1092',
    location: 'Interstate 80 Mile 142',
    description: 'Diagnostic Alert: Severe Engine Overheat detected. Cargo: Pharma Cold Chain 4°C at risk of temperature threshold breach in 38 minutes.',
    actions: [
      { label: 'Contact Driver', icon: 'phone_in_talk', variant: 'ghost' },
      { label: 'Dispatch Tow & Transfer', icon: 'emergency', variant: 'danger' },
    ],
  },
  {
    id: 'A2',
    level: 'warning',
    category: 'delay',
    icon: 'schedule',
    title: 'Driver Delayed (+45 min): Route NY-BOS #44',
    location: 'Traffic Congestion I-95 North',
    description: 'Major congestion near New Haven corridor. 12 timed enterprise delivery windows now marked as High Risk.',
    actions: [
      { label: 'Notify Receivers', icon: 'mail', variant: 'ghost' },
      { label: 'Dynamic Re-optimize', icon: 'alt_route', variant: 'primary' },
    ],
  },
  {
    id: 'A3',
    level: 'critical',
    category: 'delay',
    icon: 'cancel',
    title: 'Missed Delivery Window: Order SHP-10001-ORD',
    location: 'Frankfurt Depot Cargo Hub',
    description: 'Consignee receiving dock closed at 14:00 CET without signature handover. Container staged in temporary bay 14. Order remains in Stage 1 — eligible for cancel/refund triage.',
    actions: [
      { label: 'Log Deviation', icon: 'history', variant: 'ghost' },
      { label: 'Reschedule Next Shift', icon: 'event_repeat', variant: 'ghost' },
    ],
  },
  {
    id: 'A4',
    level: 'warning',
    category: 'vehicle',
    icon: 'wrong_location',
    title: 'Geofence Deviation: Van VN-304',
    location: 'Sector 7B Perimeter Breach',
    description: 'Vehicle exited designated delivery corridor without authorized manifest override. Telemetry heartbeats active.',
    actions: [
      { label: 'Review Route', icon: 'map', variant: 'ghost' },
      { label: 'Ping Driver', icon: 'sensors', variant: 'ghost' },
    ],
  },
]

const activeFilter = ref<'all' | 'critical' | 'vehicle' | 'delay'>('all')

const filteredAlerts = computed(() => {
  if (activeFilter.value === 'all') return alerts
  if (activeFilter.value === 'critical') return alerts.filter((a) => a.level === 'critical')
  return alerts.filter((a) => a.category === activeFilter.value)
})

const stats = [
  { label: 'Revenue Today', value: '$842,950.00', sub: '+8.4% vs daily target', icon: 'payments', footerLabel: 'Gross Margin', footerValue: '22.4%' },
  { label: 'Delivery Fulfillment', value: '1,842', caption: '/ 14 Failed', progress: 99.2, icon: 'task_alt', footerLabel: 'Success Rate', footerValue: '99.2%' },
  { label: 'Active Fleet Assets', value: '444 Assets', sub2: '384 En Route · 42 Depot', icon: 'badge', footerLabel: 'Off Duty Standby', footerValue: '18 Drivers' },
  { label: 'Network Velocity', value: '58.2', caption: 'km/h avg', sub: 'Corridor Flow Optimal', icon: 'speed', footerLabel: 'Fuel Efficiency Index', footerValue: '94.1%' },
]
</script>

<template>
  <main class="space-y-6">
    <!-- Title bar -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <div class="flex items-center gap-2">
          <h1 class="font-heading text-headline-md font-bold text-on-surface">Command Center Live Overview</h1>
          <span class="rounded border border-primary/30 bg-primary-container/10 px-2 py-0.5 text-label-sm font-semibold text-primary">Admin console</span>
        </div>
        <p class="text-body-sm text-on-surface-variant">Global multi-modal fleet status, active corridor tracking, and dispatch exception handling — read-only.</p>
      </div>
      <div class="flex items-center gap-2 self-start sm:self-auto">
        <button class="h-8 rounded border border-outline-variant bg-surface-container px-3 text-label-sm font-medium text-on-surface hover:border-primary flex items-center gap-1.5 transition-colors">
          <MIcon name="alt_route" class="text-[16px]" /> Emergency Re-route
        </button>
        <button class="h-8 rounded border border-outline-variant bg-surface-container px-3 text-label-sm font-medium text-on-surface hover:border-primary flex items-center gap-1.5 transition-colors">
          <MIcon name="file_download" class="text-[16px]" /> Export Telemetry
        </button>
      </div>
    </div>

    <!-- Global Live Map — dashboard mapping over shipments -->
    <AdminGlobalLiveMap :shipments="shipments" />

    <!-- Quick stats row -->
    <section class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
      <div v-for="s in stats" :key="s.label" class="rounded-xl border border-outline-variant bg-surface-container p-4 flex flex-col justify-between hover:border-primary/30 transition-colors">
        <div class="flex items-center justify-between">
          <span class="text-label-sm uppercase tracking-wider text-on-surface-variant">{{ s.label }}</span>
          <MIcon :name="s.icon" class="text-[18px] text-outline" />
        </div>
        <div class="my-2">
          <div class="flex items-baseline gap-1">
            <span class="font-telemetry-numeric text-headline-md font-bold tracking-tight text-on-surface">{{ s.value }}</span>
            <span v-if="s.caption" class="text-body-sm text-on-surface-variant">{{ s.caption }}</span>
          </div>
          <div v-if="s.sub" class="mt-1 flex items-center gap-1 text-label-sm" :class="s.label==='Network Velocity' ? 'text-primary' : 'text-primary'">
            <MIcon v-if="s.label==='Revenue Today'" name="trending_up" class="text-[14px]" />
            <MIcon v-if="s.label==='Network Velocity'" name="check_circle" class="text-[14px]" />
            {{ s.sub }}
          </div>
          <div v-if="s.sub2" class="mt-1 text-label-sm text-on-surface-variant">{{ s.sub2 }}</div>
          <div v-if="s.progress" class="mt-2 flex h-2 overflow-hidden rounded-full bg-surface-lowest">
            <div class="h-full bg-primary" :style="{ width: s.progress + '%' }" />
            <div class="h-full bg-destructive" :style="{ width: (100 - s.progress) + '%' }" />
          </div>
        </div>
        <div class="flex items-center justify-between border-t border-outline-variant pt-2 text-label-sm">
          <span class="text-on-surface-variant">{{ s.footerLabel }}</span>
          <span class="font-medium" :class="s.footerValue==='99.2%' ? 'text-primary' : 'text-on-surface'">{{ s.footerValue }}</span>
        </div>
      </div>
    </section>

    <!-- Critical Alerts & Exceptions Queue — read-only triage, no order creation -->
    <section class="overflow-hidden rounded-xl border border-outline-variant bg-surface-container">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-outline-variant p-4">
        <div class="flex items-center gap-2">
          <MIcon name="warning" class="text-[20px] text-destructive" />
          <div>
            <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Critical Alerts &amp; Exceptions Queue</h2>
            <p class="text-body-sm text-on-surface-variant">Autonomous telemetry violations and route delays requiring triage — no manual order creation.</p>
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <div class="flex items-center gap-1 rounded-lg border border-outline-variant bg-surface-lowest p-1">
            <button class="rounded px-2.5 py-1 text-label-sm font-medium transition-colors" :class="activeFilter==='all' ? 'bg-surface-container-high text-primary border border-outline-variant' : 'text-on-surface-variant hover:text-on-surface'" @click="activeFilter='all'">All Exceptions (14)</button>
            <button class="rounded px-2.5 py-1 text-label-sm transition-colors" :class="activeFilter==='critical' ? 'bg-surface-container-high text-primary border border-outline-variant font-medium' : 'text-on-surface-variant hover:text-on-surface'" @click="activeFilter='critical'">Critical (4)</button>
            <button class="rounded px-2.5 py-1 text-label-sm transition-colors" :class="activeFilter==='vehicle' ? 'bg-surface-container-high text-primary border border-outline-variant font-medium' : 'text-on-surface-variant hover:text-on-surface'" @click="activeFilter='vehicle'">Vehicle Issues (3)</button>
            <button class="rounded px-2.5 py-1 text-label-sm transition-colors" :class="activeFilter==='delay' ? 'bg-surface-container-high text-primary border border-outline-variant font-medium' : 'text-on-surface-variant hover:text-on-surface'" @click="activeFilter='delay'">Schedule Delays (7)</button>
          </div>
          <button class="h-8 rounded border border-outline-variant bg-surface-container-high px-3 text-label-sm font-medium text-on-surface hover:border-primary flex items-center gap-1">
            <MIcon name="done_all" class="text-[16px]" /> Batch Acknowledge
          </button>
        </div>
      </div>

      <div class="space-y-2 p-4">
        <div
          v-for="alert in filteredAlerts"
          :key="alert.id"
          class="flex flex-col lg:flex-row lg:items-center justify-between gap-3 rounded-lg border p-4 transition-colors"
          :class="alert.level==='critical' ? 'bg-surface-low border-destructive/50 hover:border-destructive' : 'bg-surface-low border-tertiary-container/50 hover:border-tertiary'"
        >
          <div class="flex items-start gap-3">
            <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded border mt-0.5" :class="alert.level==='critical' ? 'bg-destructive/10 border-destructive text-destructive' : 'bg-tertiary-container/20 border-tertiary text-tertiary'">
              <MIcon :name="alert.icon" class="text-[18px]" />
            </div>
            <div class="space-y-1">
              <div class="flex flex-wrap items-center gap-2">
                <span class="rounded border px-2 py-0.5 text-label-sm font-bold uppercase tracking-wide" :class="alert.level==='critical' ? 'bg-destructive/10 text-destructive border-destructive/40' : 'bg-tertiary-container/20 text-tertiary border-tertiary/40'">{{ alert.level==='critical' ? 'Critical Exception' : 'Warning' }}</span>
                <span class="font-heading text-label-md font-semibold text-on-surface">{{ alert.title }}</span>
                <span class="text-body-sm text-outline-variant">•</span>
                <span class="text-body-sm text-on-surface-variant">{{ alert.location }}</span>
              </div>
              <p class="text-body-sm leading-relaxed text-on-surface-variant">{{ alert.description }}</p>
            </div>
          </div>
          <div class="flex items-center gap-1.5 shrink-0 self-end lg:self-center">
            <button
              v-for="action in alert.actions"
              :key="action.label"
              class="h-8 rounded px-3 text-label-sm font-medium flex items-center gap-1 transition-colors"
              :class="action.variant==='danger' ? 'bg-destructive text-destructive-foreground hover:bg-destructive/90' : action.variant==='primary' ? 'bg-primary-container text-on-primary hover:bg-primary' : 'bg-surface-container-high border border-outline-variant text-on-surface hover:border-primary'"
            >
              <MIcon :name="action.icon" class="text-[14px]" /> {{ action.label }}
            </button>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-between border-t border-outline-variant bg-surface-lowest px-4 py-2 text-label-sm text-on-surface-variant">
        <div class="flex items-center gap-2">
          <span>Showing {{ filteredAlerts.length }} of 14 active telemetry exceptions</span>
          <span>•</span>
          <span class="font-medium text-primary">Automatic SLA auto-escalation active (15m window)</span>
        </div>
        <span class="hidden sm:inline-flex items-center gap-1 text-primary">View All Exception Logs <MIcon name="chevron_right" class="text-[16px]" /></span>
      </div>
    </section>

    <!-- No manual order creation — read-only notice -->
    <div class="flex items-center gap-2 rounded-lg border border-outline-variant bg-surface-container px-4 py-2 text-label-sm text-on-surface-variant">
      <MIcon name="block" class="text-[16px] text-outline" />
      <span>Orders are ingested via external APIs only — no manual creation tools are exposed in this command center.</span>
      <span class="ml-auto hidden sm:inline text-label-sm text-outline">Dispatcher: {{ auth.user?.email }}</span>
    </div>
  </main>
</template>
