<script setup lang="ts">
import { shipments as seedShipments, canCancelOrder } from '~~/app/data/shipments'
import type { Shipment } from '~~/app/data/shipments'
import { drivers } from '~~/app/data/drivers'

definePageMeta({ middleware: 'admin', layout: 'admin' })

useSeoMeta({
  title: 'Admin — Route Planning',
  description: 'Route Planning & Dispatch Engine — drag incoming automated orders to drivers. Cancel restricted to Stage 1 Order Received only.',
})

const { cancelOrder } = useShipments()

// Local dispatch board state — incoming automated orders are order_received only
const unassigned = ref<Shipment[]>(seedShipments.filter((s) => s.status === 'order_received').slice(0, 4))
const assignments = reactive<Record<string, Shipment[]>>({
  'TR-402': [],
  'VN-108': [],
  'TR-510': [],
  'VN-304': [],
})

const draggedId = ref<string | null>(null)
const dragOverDriver = ref<string | null>(null)
const dragOverPool = ref(false)
const toast = ref<string | null>(null)
const cancellingId = ref<string | null>(null)

function showToast(msg: string) {
  toast.value = msg
  setTimeout(() => (toast.value = null), 3000)
}

function findShipment(id: string): { shipment: Shipment | undefined; from: 'pool' | string | null; idx: number } {
  const poolIdx = unassigned.value.findIndex((s) => s.id === id)
  if (poolIdx !== -1) return { shipment: unassigned.value[poolIdx], from: 'pool', idx: poolIdx }
  for (const dId of Object.keys(assignments)) {
    const idx = assignments[dId]!.findIndex((s) => s.id === id)
    if (idx !== -1) return { shipment: assignments[dId]![idx], from: dId, idx }
  }
  return { shipment: undefined, from: null, idx: -1 }
}

function onDragStart(e: DragEvent, id: string) {
  draggedId.value = id
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', id)
    e.dataTransfer.setData('application/x-shipment', id)
  }
}

function onDragEnd() {
  draggedId.value = null
  dragOverDriver.value = null
  dragOverPool.value = false
}

function onDropToDriver(e: DragEvent, driverId: string) {
  e.preventDefault()
  const id = (e.dataTransfer?.getData('text/plain') || draggedId.value || '').trim().toUpperCase()
  if (!id) return
  const found = findShipment(id)
  if (!found.shipment) return
  const driver = drivers.find((d) => d.id === driverId)
  if (!driver) return
  if (assignments[driverId]!.length >= driver.capacity) {
    showToast(`${driver.name} is at capacity (${driver.capacity})`)
    draggedId.value = null
    dragOverDriver.value = null
    return
  }
  // remove from previous
  if (found.from === 'pool') unassigned.value.splice(found.idx, 1)
  else if (found.from) assignments[found.from]!.splice(found.idx, 1)
  assignments[driverId]!.push(found.shipment!)
  showToast(`Assigned ${id} → ${driver.name} (${driverId})`)
  draggedId.value = null
  dragOverDriver.value = null
}

function onDropToPool(e: DragEvent) {
  e.preventDefault()
  const id = (e.dataTransfer?.getData('text/plain') || draggedId.value || '').trim().toUpperCase()
  if (!id) return
  const found = findShipment(id)
  if (!found.shipment || found.from === 'pool') {
    dragOverPool.value = false
    draggedId.value = null
    return
  }
  assignments[found.from!]!.splice(found.idx, 1)
  unassigned.value.unshift(found.shipment!)
  showToast(`Returned ${id} to Unassigned Pool`)
  dragOverPool.value = false
  draggedId.value = null
}

function handleCancel(id: string) {
  const shipment = findShipment(id).shipment
  if (!shipment) return
  if (!canCancelOrder(shipment)) return
  cancellingId.value = id
  setTimeout(() => {
    // remove from board
    const found = findShipment(id)
    if (found.from === 'pool') unassigned.value.splice(found.idx, 1)
    else if (found.from) assignments[found.from]!.splice(found.idx, 1)
    cancelOrder(id)
    cancellingId.value = null
    showToast(`Cancelled ${id} — flagged for Visa refund via Stripe`)
  }, 400)
}

// Quick assign via button (keyboard / mobile fallback)
function assignViaButton(id: string, driverId: string) {
  const found = findShipment(id)
  if (!found.shipment) return
  const driver = drivers.find((d) => d.id === driverId)!
  if (assignments[driverId]!.length >= driver.capacity) {
    showToast(`${driver.name} is at capacity`)
    return
  }
  if (found.from === 'pool') unassigned.value.splice(found.idx, 1)
  else if (found.from) assignments[found.from]!.splice(found.idx, 1)
  assignments[driverId]!.push(found.shipment!)
  showToast(`Assigned ${id} → ${driver.name}`)
}

const allAssignedCount = computed(() => Object.values(assignments).reduce((acc, arr) => acc + arr.length, 0))
</script>

<template>
  <main class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 rounded-xl border border-outline-variant/60 bg-surface-container-low p-4">
      <div>
        <div class="flex items-center gap-2">
          <h1 class="font-heading text-headline-md font-bold tracking-tight text-on-surface">Route Planning &amp; Dispatch Engine</h1>
          <span class="rounded-full border border-primary-container/30 bg-primary-container/10 px-2 py-0.5 text-label-sm font-semibold text-primary">v4.18 Real-time Solvers</span>
          <span class="rounded border border-outline-variant bg-surface-container px-2 py-0.5 text-label-sm text-on-surface-variant">Admin Route Planning</span>
        </div>
        <p class="mt-1 text-body-sm text-on-surface-variant">Drag incoming automated orders from the unassigned pool to specific drivers. Cancel restricted to Stage 1 <strong class="text-on-surface">Order Received</strong> only — no manual order creation.</p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <button class="rounded-xl border border-outline-variant bg-surface-container-high px-4 py-2 text-label-md font-medium text-on-surface hover:border-primary flex items-center gap-1.5">
          <MIcon name="history_toggle_off" class="text-[18px] text-tertiary" /> Simulate Delays
        </button>
        <button class="rounded-xl border border-secondary/30 bg-secondary-container px-4 py-2 text-label-md font-semibold text-white hover:bg-secondary-container/80 flex items-center gap-1.5">
          <MIcon name="send" class="text-[18px]" /> Publish Dispatches ({{ allAssignedCount }})
        </button>
      </div>
    </div>

    <div v-if="toast" class="rounded-lg border border-primary/30 bg-primary-container/10 px-4 py-2 text-body-sm font-medium text-primary">
      {{ toast }}
    </div>

    <!-- Split: Pool vs Tactical Map -->
    <section class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
      <!-- Unassigned Pool — Vue drag-and-drop source -->
      <div
        class="lg:col-span-4 flex flex-col rounded-xl border bg-surface-container overflow-hidden"
        :class="dragOverPool ? 'border-primary ring-1 ring-primary/30' : 'border-outline-variant/60'"
        @dragover.prevent="dragOverPool = true"
        @dragleave="dragOverPool = false"
        @drop="onDropToPool"
      >
        <div class="flex items-center justify-between border-b border-outline-variant bg-surface-container-low p-4">
          <div class="flex items-center gap-2">
            <MIcon name="move_to_inbox" class="text-[20px] text-primary" />
            <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Unassigned Order Pool</h2>
          </div>
          <span class="rounded-full border border-tertiary/30 bg-tertiary-container/20 px-2 py-0.5 text-label-sm font-semibold text-tertiary">{{ unassigned.length }} Orders Pending</span>
        </div>
        <div class="p-2 border-b border-outline-variant bg-surface-container-high/40">
          <p class="text-label-sm text-on-surface-variant">Incoming automated orders — drag to a driver lane. Orders are ingested via external API.</p>
        </div>
        <div class="flex-1 overflow-y-auto p-2 space-y-2 min-h-[380px]" :class="dragOverPool ? 'bg-primary/5' : ''">
          <p v-if="unassigned.length === 0" class="py-8 text-center text-body-sm text-on-surface-variant">All incoming orders dispatched. Drop here to return an order.</p>
          <div
            v-for="order in unassigned"
            :key="order.id"
            draggable="true"
            @dragstart="onDragStart($event, order.id)"
            @dragend="onDragEnd"
            class="group cursor-grab active:cursor-grabbing rounded-xl border bg-surface-low p-3 hover:border-primary/60 transition-colors"
            :class="draggedId===order.id ? 'opacity-50 ring-1 ring-primary' : 'border-outline-variant'"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1.5">
                <MIcon name="drag_indicator" class="text-[18px] text-outline group-hover:text-primary" />
                <span class="font-mono text-body-md font-bold text-on-surface">{{ order.id }}</span>
                <span class="text-label-sm text-on-surface-variant">{{ order.grossWeight }}</span>
              </div>
              <span class="rounded border px-2 py-0.5 text-label-sm font-medium" :class="order.status==='order_received' ? 'bg-primary-container/10 border-primary/30 text-primary' : 'bg-surface-variant border-outline-variant text-on-surface-variant'">{{ order.status==='order_received' ? 'Order Received' : order.status }}</span>
            </div>
            <div class="mt-1.5 space-y-1 pl-6 text-body-sm">
              <div class="flex items-center gap-1.5 text-on-surface-variant">
                <span class="h-1.5 w-1.5 rounded-full bg-primary" />
                <span class="truncate">{{ order.origin }} → {{ order.destination }}</span>
              </div>
              <div class="flex items-center gap-2 text-label-sm">
                <span class="flex items-center gap-1 text-primary"><MIcon name="ac_unit" class="text-[14px]" />{{ order.mode }}</span>
                <span class="text-outline">•</span>
                <span class="text-on-surface-variant">{{ order.pallets }}</span>
              </div>
            </div>
            <div class="mt-2 flex items-center gap-1.5 pl-6">
              <!-- Cancel Order — Stage 1 only -->
              <ShipmentCancelOrderButton :shipment="order" :loading="cancellingId===order.id" @cancel="handleCancel(order.id)" />
              <span v-if="!canCancelOrder(order)" class="text-label-sm text-outline">Cancel locked — past Stage 1</span>
              <!-- Fallback assign buttons for mobile / keyboard -->
              <div class="ml-auto flex items-center gap-1">
                <select class="rounded border border-outline-variant bg-surface px-1 py-1 text-label-sm text-on-surface" :value="''" @change="assignViaButton(order.id, ($event.target as HTMLSelectElement).value); ($event.target as HTMLSelectElement).value=''">
                  <option value="" disabled>Assign to…</option>
                  <option v-for="d in drivers" :key="d.id" :value="d.id">{{ d.name }} ({{ d.id }})</option>
                </select>
              </div>
            </div>
          </div>
        </div>
        <div class="border-t border-outline-variant bg-surface-container-low p-2 flex items-center justify-between text-label-sm">
          <span class="text-on-surface-variant">{{ unassigned.length }} pending • Drag to driver lane →</span>
          <span class="text-primary">No manual creation</span>
        </div>
      </div>

      <!-- Tactical GIS Map -->
      <div class="lg:col-span-8 flex flex-col rounded-xl border border-outline-variant/60 bg-surface-container overflow-hidden">
        <div class="flex items-center justify-between border-b border-outline-variant bg-surface-container-low p-3">
          <div class="flex items-center gap-2">
            <MIcon name="public" class="text-[18px] text-primary" />
            <span class="font-heading text-label-md font-semibold text-on-surface">Tactical GIS — Fleet Positions</span>
            <span class="hidden xl:inline rounded bg-primary/10 border border-primary/20 px-2 py-0.5 text-label-sm text-primary">Zone Alpha: Metro Central</span>
          </div>
          <span class="text-label-sm text-on-surface-variant">{{ allAssignedCount }} dispatched • {{ unassigned.length }} unassigned</span>
        </div>
        <div class="flex-1 min-h-[380px] bg-[#091122] relative overflow-hidden">
          <svg class="absolute inset-0 h-full w-full opacity-20" xmlns="http://www.w3.org/2000/svg">
            <defs><pattern id="gridRoute" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 L 0 0 0 40" fill="none" stroke="#3d494c" stroke-width="0.75" /></pattern></defs>
            <rect width="100%" height="100%" fill="url(#gridRoute)" />
          </svg>
          <svg class="absolute inset-0 h-full w-full pointer-events-none" viewBox="0 0 800 500" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M 120 40 Q 220 180 190 320 T 310 480" stroke="#1e293b" stroke-width="40" stroke-linecap="round" opacity="0.6" />
            <path d="M 450 20 Q 480 150 580 260 T 700 450" stroke="#1e293b" stroke-width="60" stroke-linecap="round" opacity="0.4" />
            <path d="M 160 210 L 260 140 L 370 190 L 490 130" stroke="#06B6D4" stroke-width="2.5" stroke-dasharray="4 3" opacity="0.9" />
            <path d="M 190 350 L 310 320 L 440 370" stroke="#2861FF" stroke-width="2" stroke-dasharray="3 3" opacity="0.8" />
            <circle cx="160" cy="210" r="14" fill="#131B2E" stroke="#06B6D4" stroke-width="2" /><text x="160" y="214" text-anchor="middle" fill="#06B6D4" font-size="11" font-weight="700">#1</text>
            <circle cx="260" cy="140" r="14" fill="#131B2E" stroke="#06B6D4" stroke-width="2" /><text x="260" y="144" text-anchor="middle" fill="#06B6D4" font-size="11" font-weight="700">#2</text>
            <circle cx="370" cy="190" r="14" fill="#131B2E" stroke="#06B6D4" stroke-width="2" /><text x="370" y="194" text-anchor="middle" fill="#06B6D4" font-size="11" font-weight="700">#3</text>
            <circle cx="490" cy="130" r="14" fill="#131B2E" stroke="#06B6D4" stroke-width="2" /><text x="490" y="134" text-anchor="middle" fill="#06B6D4" font-size="11" font-weight="700">#4</text>
            <circle cx="210" cy="175" r="5" fill="#4CD7F6" /><circle cx="210" cy="175" r="10" stroke="#4CD7F6" stroke-width="1" opacity="0.6" />
            <circle cx="250" cy="335" r="5" fill="#2861FF" />
            <circle cx="495" cy="255" r="5" fill="#FFB873" />
          </svg>
          <div class="absolute bottom-3 left-3 rounded-lg border border-outline-variant bg-surface-container-low/90 px-3 py-1.5 text-label-sm backdrop-blur">
            <div class="flex items-center gap-1.5 font-semibold text-on-surface"><span class="h-2 w-2 animate-ping rounded-full bg-primary" /> Active Telemetry Solver</div>
            <div class="font-mono text-[11px] text-on-surface-variant">SOLVER: AntColony-V3 • FEASIBLE: YES</div>
          </div>
          <div class="absolute bottom-3 right-3 flex items-center gap-2 rounded-xl border border-outline-variant/80 bg-surface-container-low/95 px-3 py-1.5 text-body-sm">
            <MIcon name="analytics" class="text-[18px] text-primary" />
            <span class="font-mono text-label-sm text-on-surface">Total Distance: <strong class="text-primary">342 km</strong> • Fuel: <strong class="text-tertiary">$184.20</strong></span>
          </div>
        </div>
      </div>
    </section>

    <!-- Driver Assignment Lanes — drop targets -->
    <section class="rounded-xl border border-outline-variant/60 bg-surface-container p-4 flex flex-col gap-4">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-outline-variant pb-3">
        <div>
          <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Active Driver Assignment Lanes</h2>
          <p class="text-body-sm text-on-surface-variant">Drag unassigned order tokens into a driver lane. Cancel is restricted to Stage 1 <strong class="text-on-surface">Order Received</strong> only.</p>
        </div>
        <div class="flex items-center gap-2">
          <button class="rounded-xl border border-outline-variant bg-surface-container-high px-3 py-1.5 text-label-md font-medium text-on-surface hover:border-primary flex items-center gap-1.5">
            <MIcon name="balance" class="text-[18px] text-primary" /> Auto-Balance Workload
          </button>
        </div>
      </div>

      <div class="grid grid-cols-12 gap-1 px-2 text-label-sm font-mono text-on-surface-variant border-b border-outline-variant/40 pb-1.5">
        <div class="col-span-3">DRIVER PROFILE &amp; VEHICLE</div>
        <div class="col-span-9 grid grid-cols-10 text-center"><span>08:00</span><span>09:00</span><span>10:00</span><span>11:00</span><span>12:00</span><span>13:00</span><span>14:00</span><span>15:00</span><span>16:00</span><span>17:00</span></div>
      </div>

      <div class="space-y-3">
        <div
          v-for="driver in drivers"
          :key="driver.id"
          class="grid grid-cols-12 gap-2 rounded-xl border bg-surface-low p-3 items-center transition-colors"
          :class="dragOverDriver===driver.id ? 'border-primary ring-1 ring-primary/40 bg-primary/5' : 'border-outline-variant hover:border-outline-variant/80'"
          @dragover.prevent="dragOverDriver = driver.id"
          @dragleave="dragOverDriver = null"
          @drop="onDropToDriver($event, driver.id)"
        >
          <div class="col-span-3 border-r border-outline-variant/50 pr-2">
            <div class="flex items-center justify-between">
              <span class="font-bold text-on-surface truncate">{{ driver.name }}</span>
              <span class="font-mono text-label-sm text-primary">{{ driver.id }}</span>
            </div>
            <div class="text-label-sm text-on-surface-variant truncate">{{ driver.vehicle }}</div>
            <div class="mt-1 flex items-center justify-between text-[11px] font-mono">
              <span :class="(assignments[driver.id] || []).length >= driver.capacity ? 'text-destructive font-bold' : 'text-on-surface'">Cap: <strong :class="(assignments[driver.id] || []).length >= driver.capacity ? 'text-destructive' : 'text-primary'">{{ (assignments[driver.id] || []).length }}/{{ driver.capacity }} ({{ Math.round((assignments[driver.id] || []).length / driver.capacity * 100) }}%)</strong></span>
              <span class="text-on-surface-variant">{{ driver.status }}</span>
            </div>
            <div class="mt-1 h-1 w-full overflow-hidden rounded-full bg-surface-container-highest">
              <div class="h-full" :class="(assignments[driver.id] || []).length >= driver.capacity ? 'bg-destructive' : 'bg-primary-container'" :style="{ width: ((assignments[driver.id] || []).length / driver.capacity * 100) + '%' }" />
            </div>
          </div>
          <div class="col-span-9 grid grid-cols-10 gap-1.5 py-1 items-center min-h-[56px]">
            <template v-if="(assignments[driver.id] || []).length === 0">
              <div class="col-span-10 flex items-center justify-center gap-1.5 rounded border-2 border-dashed py-3 text-center transition-colors" :class="dragOverDriver===driver.id ? 'border-primary bg-primary/10 text-primary' : 'border-primary/40 bg-primary/5 text-primary'">
                <MIcon name="add_circle" class="text-[18px]" />
                <span class="text-label-sm font-medium">DROP ZONE: Drag Unassigned Order Here — {{ driver.name }}</span>
              </div>
            </template>
            <template v-else>
              <div
                v-for="order in (assignments[driver.id] || [])"
                :key="order.id"
                draggable="true"
                @dragstart="onDragStart($event, order.id)"
                @dragend="onDragEnd"
                class="col-span-5 sm:col-span-3 md:col-span-2 rounded border bg-surface-container-high p-1.5 text-label-sm hover:border-primary transition-colors cursor-grab active:cursor-grabbing flex flex-col gap-1"
                :class="draggedId===order.id ? 'opacity-50' : 'border-outline-variant'"
              >
                <div class="flex items-center justify-between">
                  <span class="font-mono font-bold text-on-surface">{{ order.id }}</span>
                  <button class="rounded px-1 py-0.5 text-[10px] border border-outline-variant hover:bg-surface-low" @click="() => { const idx = (assignments[driver.id] || []).findIndex(s=>s.id===order.id); if(idx!==-1){ const [mv]=(assignments[driver.id] || []).splice(idx,1); unassigned.unshift(mv); showToast(`Returned ${order.id} to pool`) } }" title="Return to pool"><MIcon name="undo" class="text-[12px]" /></button>
                </div>
                <div class="truncate text-[11px] text-on-surface-variant">{{ order.origin }} → {{ order.destination }}</div>
                <ShipmentCancelOrderButton :shipment="order" :loading="cancellingId===order.id" @cancel="handleCancel(order.id)" />
              </div>
              <div
                v-if="(assignments[driver.id] || []).length < driver.capacity"
                class="col-span-5 sm:col-span-3 md:col-span-2 flex items-center justify-center gap-1 rounded border-2 border-dashed py-3 text-center"
                :class="dragOverDriver===driver.id ? 'border-primary bg-primary/10 text-primary' : 'border-primary/30 bg-primary/5 text-primary'"
              >
                <MIcon name="add" class="text-[16px]" /> Drop more
              </div>
            </template>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-2 rounded-lg border border-outline-variant bg-surface-low px-3 py-2 text-label-sm text-on-surface-variant">
        <MIcon name="info" class="text-[16px] text-primary" />
        <span>Orders are ingested via external APIs only — this board dispatches, not creates. Cancel is Stage 1 only.</span>
        <span class="ml-auto hidden sm:inline">Total dispatched: {{ allAssignedCount }} • Unassigned: {{ unassigned.length }}</span>
      </div>
    </section>
  </main>
</template>
