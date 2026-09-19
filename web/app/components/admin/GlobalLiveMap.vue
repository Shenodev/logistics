<script setup lang="ts">
import type { Shipment } from '~~/app/data/shipments'

interface Props {
  shipments: Shipment[]
}

const props = defineProps<Props>()

// Map shipment IDs to fixed global positions for demo — dashboard mapping exercise
const positions = [
  { x: 240, y: 220, mode: 'ground' },
  { x: 570, y: 118, mode: 'air' },
  { x: 620, y: 190, mode: 'ocean' },
  { x: 980, y: 340, mode: 'intermodal' },
  { x: 180, y: 250, mode: 'air' },
  { x: 640, y: 200, mode: 'ocean' },
]

const markers = computed(() =>
  props.shipments.slice(0, 6).map((s, i) => ({
    shipment: s,
    pos: positions[i % positions.length]!,
    label: s.id,
    sub: s.status === 'delivered' ? 'Delivered' : s.status === 'in_transit' ? 'En Route' : s.status === 'out_for_delivery' ? 'Final Mile' : 'Order Received',
  })),
)

const activeCount = computed(() => props.shipments.length)
</script>

<template>
  <section class="relative flex h-[460px] flex-col justify-between overflow-hidden rounded-xl border border-outline-variant bg-surface-container">
    <!-- Synthetic Vector Map Canvas -->
    <div class="absolute inset-0 pointer-events-none">
      <svg class="h-full w-full opacity-35" preserveAspectRatio="none" viewBox="0 0 1200 600" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="gridPatternAdmin" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#3d494c" stroke-width="0.75" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#gridPatternAdmin)" />
        <!-- Trajectories -->
        <path d="M 240 220 Q 420 120 620 190" fill="none" stroke="#06b6d4" stroke-dasharray="6,4" stroke-width="2" opacity="0.8" />
        <path d="M 280 260 Q 460 320 620 230" fill="none" stroke="#2861ff" stroke-dasharray="4,4" stroke-width="1.5" opacity="0.7" />
        <path d="M 200 240 Q 60 200 20 280" fill="none" stroke="#06b6d4" stroke-width="1.75" opacity="0.6" />
        <path d="M 640 190 Q 820 180 980 340" fill="none" stroke="#06b6d4" stroke-width="2" opacity="0.8" />
        <path d="M 620 230 Q 750 360 960 380" fill="none" stroke="#06b6d4" stroke-dasharray="6,3" stroke-width="1.5" opacity="0.7" />
        <path d="M 610 200 L 640 190" fill="none" stroke="#ffb873" stroke-width="2" />
        <!-- Hub rings -->
        <circle cx="240" cy="220" r="14" fill="none" stroke="#06b6d4" stroke-width="1" opacity="0.4" />
        <circle cx="240" cy="220" r="4" fill="#06b6d4" />
        <circle cx="620" cy="190" r="14" fill="none" stroke="#06b6d4" stroke-width="1" opacity="0.4" />
        <circle cx="620" cy="190" r="4" fill="#06b6d4" />
        <circle cx="980" cy="340" r="14" fill="none" stroke="#06b6d4" stroke-width="1" opacity="0.4" />
        <circle cx="980" cy="340" r="4" fill="#06b6d4" />
        <circle cx="180" cy="250" r="12" fill="none" stroke="#06b6d4" stroke-width="1" opacity="0.3" />
        <circle cx="180" cy="250" r="3" fill="#06b6d4" />
      </svg>
    </div>

    <!-- Top HUD -->
    <div class="relative z-10 flex flex-wrap items-center justify-between gap-4 border-b border-outline-variant bg-surface-container/80 p-4 backdrop-blur-sm">
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2">
          <span class="h-2.5 w-2.5 animate-ping rounded-full bg-primary" />
          <span class="text-label-md font-medium text-on-surface">Global Telemetry Stream</span>
        </div>
        <div class="h-4 w-px bg-outline-variant" />
        <div class="flex items-center gap-2">
          <span class="text-label-sm text-on-surface-variant">Active Assets Worldwide:</span>
          <span class="font-telemetry-numeric text-headline-sm font-bold tracking-tight text-primary">{{ activeCount }}</span>
        </div>
      </div>
      <div class="flex items-center gap-1 rounded-lg border border-outline-variant bg-surface-lowest p-1">
        <span class="flex items-center gap-1 rounded bg-surface-container-high px-2 py-1 text-label-sm font-medium text-primary border border-outline-variant">
          <MIcon name="flight" class="text-[16px]" /> Air ({{ shipments.filter(s=>s.mode==='Air Cargo').length }})
        </span>
        <span class="flex items-center gap-1 px-2 py-1 text-label-sm text-on-surface-variant">
          <MIcon name="directions_boat" class="text-[16px]" /> Ocean ({{ shipments.filter(s=>s.mode==='Ocean Freight').length }})
        </span>
        <span class="flex items-center gap-1 px-2 py-1 text-label-sm text-on-surface-variant">
          <MIcon name="local_shipping" class="text-[16px]" /> Road ({{ shipments.filter(s=>s.mode==='Ground Fleet').length }})
        </span>
      </div>
    </div>

    <!-- Markers — dashboard mapping: v-for over shipments -->
    <div class="relative z-10 flex-1 w-full pointer-events-none">
      <div
        v-for="m in markers"
        :key="m.label"
        class="absolute -translate-x-1/2 -translate-y-1/2 pointer-events-auto cursor-pointer group"
        :style="{ left: m.pos.x / 12 + '%', top: m.pos.y / 6 + '%' }"
      >
        <div class="flex items-center gap-1.5 rounded border bg-surface-container-high px-2 py-1 shadow-sm" :class="m.shipment.status==='delivered' ? 'border-emerald-500/30' : m.pos.mode==='air' ? 'border-primary-container' : 'border-outline-variant'">
          <MIcon :name="m.pos.mode==='air' ? 'flight' : m.pos.mode==='ocean' ? 'directions_boat' : 'local_shipping'" class="text-sm" :class="m.shipment.status==='delivered' ? 'text-emerald-400' : 'text-primary'" />
          <span class="text-label-sm font-bold" :class="m.shipment.status==='delivered' ? 'text-emerald-400' : 'text-primary'">{{ m.label }}</span>
          <span class="text-label-sm text-on-surface">{{ m.sub }}</span>
        </div>
        <div class="mx-auto -mt-0.5 h-2 w-2 animate-pulse rounded-full" :class="m.shipment.status==='delivered' ? 'bg-emerald-400' : 'bg-primary'" />
      </div>

      <div class="absolute bottom-2 left-4 text-label-sm font-semibold tracking-wider text-outline uppercase">Hub // Rotterdam</div>
      <div class="absolute bottom-2 right-1/4 text-label-sm font-semibold tracking-wider text-outline uppercase">Hub // Singapore</div>
    </div>

    <!-- Bottom legend -->
    <div class="relative z-10 flex items-center justify-between border-t border-outline-variant bg-surface-container/80 p-3 backdrop-blur-sm">
      <div class="flex items-center gap-4 text-label-sm text-on-surface-variant">
        <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-primary" /> Air Priority</span>
        <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-secondary" /> Maritime Bulk</span>
        <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-tertiary" /> Ground Freight</span>
        <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-destructive" /> Corridor Hold</span>
      </div>
      <div class="flex items-center gap-1 rounded border border-outline-variant bg-surface-lowest p-0.5">
        <button class="flex h-7 w-7 items-center justify-center rounded text-on-surface-variant hover:bg-surface-container hover:text-on-surface" title="Zoom In"><MIcon name="add" class="text-[18px]" /></button>
        <button class="flex h-7 w-7 items-center justify-center rounded text-on-surface-variant hover:bg-surface-container hover:text-on-surface" title="Zoom Out"><MIcon name="remove" class="text-[18px]" /></button>
        <button class="flex h-7 w-7 items-center justify-center rounded text-on-surface-variant hover:bg-surface-container hover:text-on-surface" title="Reset"><MIcon name="filter_center_focus" class="text-[18px]" /></button>
      </div>
    </div>
  </section>
</template>
