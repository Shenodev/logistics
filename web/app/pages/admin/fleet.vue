<script setup lang="ts">
import {
  createColumnHelper,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useVueTable,
  FlexRender,
} from '@tanstack/vue-table'
import { fleetRoster, type FleetDriver } from '~~/app/data/fleet'

definePageMeta({ layout: 'admin', middleware: 'admin' })

useSeoMeta({
  title: 'Admin — Fleet Management',
  description: 'Fleet & Driver Management — roster, telemetry, compliance, and performance via TanStack Table.',
})

const search = ref('')
const statusFilter = ref<'all' | FleetDriver['status']>('all')
const sorting = ref<any[]>([])

const columnHelper = createColumnHelper<FleetDriver>()

const columns = [
  columnHelper.accessor('name', {
    header: 'Driver Personnel',
    cell: (info) => info.getValue(),
    enableSorting: true,
  }),
  columnHelper.accessor('statusLabel', {
    header: 'Status Badge',
    cell: (info) => info.getValue(),
    enableSorting: false,
  }),
  columnHelper.accessor('email', {
    header: 'Contact Details',
    cell: (info) => info.getValue(),
    enableSorting: false,
  }),
  columnHelper.accessor('vehicle', {
    header: 'Assigned Vehicle',
    cell: (info) => info.getValue(),
  }),
  columnHelper.accessor('route', {
    header: 'Current Mission Route',
    cell: (info) => info.getValue(),
  }),
  columnHelper.accessor('hosHours', {
    header: 'Hours of Service (HOS)',
    cell: (info) => info.getValue(),
  }),
  columnHelper.accessor('performance', {
    header: 'Performance',
    cell: (info) => info.getValue(),
  }),
]

const data = computed(() => {
  let rows = [...fleetRoster]
  if (statusFilter.value !== 'all') rows = rows.filter((r) => r.status === statusFilter.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    rows = rows.filter((r) => `${r.name} ${r.id} ${r.email} ${r.plate}`.toLowerCase().includes(q))
  }
  return rows
})

const table = useVueTable({
  get data() { return data.value },
  columns,
  state: {
    get sorting() { return sorting.value },
    get globalFilter() { return search.value },
  },
  onSortingChange: (updater: any) => {
    sorting.value = typeof updater === 'function' ? updater(sorting.value) : updater
  },
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
})

function statusTone(status: FleetDriver['status']) {
  if (status === 'en_route') return 'bg-primary/10 border-primary/30 text-primary'
  if (status === 'on_break') return 'bg-tertiary-container/15 border-tertiary/30 text-tertiary'
  if (status === 'compliance') return 'bg-error/10 border-error/30 text-error'
  return 'bg-surface-container-highest border-outline-variant text-on-surface-variant'
}
</script>

<template>
  <main class="space-y-6">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-outline-variant pb-4">
      <div>
        <div class="flex items-center gap-2">
          <h1 class="font-heading text-headline-lg font-semibold tracking-tight text-on-surface">Fleet &amp; Driver Management</h1>
          <span class="rounded border border-primary/25 bg-primary/10 px-2 py-0.5 text-label-sm font-semibold text-primary">LIVE RADAR</span>
        </div>
        <p class="text-body-md text-on-surface-variant mt-1">Real-time personnel telemetry, active vehicle pairing, compliance status, and performance tracking — TanStack Table.</p>
      </div>
      <div class="flex items-center gap-2">
        <button class="rounded border border-outline-variant bg-surface-container px-3.5 py-2 text-label-md font-medium text-on-surface hover:border-primary flex items-center gap-2">
          <MIcon name="file_download" class="text-[18px]" /> Export Roster (CSV)
        </button>
        <span class="hidden sm:inline-flex items-center gap-1 rounded bg-amber-500/10 border border-amber-500/30 px-2 py-1 text-label-sm font-semibold text-amber-400">
          <MIcon name="warning" class="text-[14px]" /> 2 Compliance
        </span>
      </div>
    </div>

    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3 rounded-xl border border-outline-variant/60 bg-surface-container/50 p-2.5">
      <div class="flex items-center gap-2">
        <span class="flex items-center gap-1 rounded bg-primary/10 border border-primary/25 px-2.5 py-1 text-label-sm font-semibold text-primary">
          <span class="h-2 w-2 animate-ping rounded-full bg-primary" /> Driver Roster ({{ data.length }} Active)
        </span>
        <span class="hidden sm:inline-flex items-center gap-1 rounded bg-surface-container px-2.5 py-1 text-label-sm text-on-surface-variant">Vehicle Inventory (210 Assets)</span>
      </div>
      <div class="flex flex-wrap items-center gap-2 text-label-sm">
        <span class="flex items-center gap-1 rounded bg-primary/10 border border-primary/25 px-2 py-1"><span class="h-2 w-2 rounded-full bg-primary animate-ping" /> Active on Road: <strong class="text-primary">94</strong></span>
        <span class="flex items-center gap-1 rounded bg-tertiary-container/10 border border-tertiary/25 px-2 py-1">Rest / Break: <strong class="text-tertiary">28</strong></span>
        <span class="flex items-center gap-1 rounded bg-surface-container-highest border border-outline-variant px-2 py-1">Off Duty: <strong>26</strong></span>
      </div>
    </div>

    <div class="rounded-xl border border-outline-variant bg-surface-container p-3 flex flex-col gap-3">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
        <div class="md:col-span-2 relative">
          <MIcon name="filter_alt" class="absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[18px]" />
          <input v-model="search" placeholder="Search by driver name, ID, phone, or license plate..." class="w-full rounded border border-outline-variant bg-surface-container-lowest py-2 pl-9 pr-3 text-body-sm text-on-surface placeholder:text-outline focus:border-primary focus:outline-none" />
        </div>
        <select v-model="statusFilter" class="rounded border border-outline-variant bg-surface-container-lowest px-3 py-2 text-body-sm text-on-surface">
          <option value="all">Duty Status: All</option>
          <option value="en_route">On-Duty / En Route</option>
          <option value="on_break">On Break / Rest Period</option>
          <option value="off_duty">Off-Duty / Standby</option>
          <option value="compliance">Compliance Warning</option>
        </select>
        <select class="rounded border border-outline-variant bg-surface-container-lowest px-3 py-2 text-body-sm text-on-surface">
          <option>Vehicle Class: All</option>
          <option>5-Ton Box Truck</option>
          <option>Sprinter Van</option>
          <option>Heavy Freight Tractor</option>
        </select>
      </div>
    </div>

    <div class="overflow-hidden rounded-xl border border-outline-variant bg-surface-container">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[1100px] border-collapse text-left">
          <thead>
            <tr class="border-b border-outline-variant bg-surface-container-high/60 text-label-sm uppercase tracking-wider text-outline">
              <th v-for="header in table.getHeaderGroups()[0]?.headers" :key="header.id" class="px-4 py-3 font-semibold">
                <div v-if="!header.isPlaceholder" class="flex items-center gap-1 cursor-pointer select-none" @click="header.column.getToggleSortingHandler()?.($event)">
                  <FlexRender :render="header.column.columnDef.header" :props="header.getContext()" />
                  <MIcon v-if="header.column.getIsSorted() === 'asc'" name="arrow_upward" class="text-[14px]" />
                  <MIcon v-else-if="header.column.getIsSorted() === 'desc'" name="arrow_downward" class="text-[14px]" />
                  <MIcon v-else name="unfold_more" class="text-[14px] opacity-50" />
                </div>
              </th>
              <th class="px-4 py-3 font-semibold text-center">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-outline-variant/60">
            <tr v-for="row in table.getRowModel().rows" :key="row.id" class="hover:bg-surface-container-high/40 transition-colors group">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-outline-variant bg-surface-container-highest text-primary font-bold">
                    {{ row.original.name.split(' ').map(n=>n[0]).join('').slice(0,2) }}
                  </div>
                  <div>
                    <div class="font-medium text-on-surface group-hover:text-primary">{{ row.original.name }}</div>
                    <div class="flex items-center gap-1.5">
                      <span class="font-mono text-label-sm text-outline">{{ row.original.id }}</span>
                      <span class="rounded border border-outline-variant bg-surface-container-lowest px-1.5 py-0.5 text-[10px] font-mono text-on-surface-variant">{{ row.original.cdl }}</span>
                      <span v-if="row.original.complianceWarning" class="rounded bg-error-container/20 border border-error/30 px-1.5 py-0.5 text-[10px] font-mono text-error">{{ row.original.complianceWarning }}</span>
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-3 py-3">
                <span class="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-label-sm font-medium" :class="statusTone(row.original.status)">
                  <span class="h-1.5 w-1.5 rounded-full" :class="row.original.status==='en_route' ? 'bg-primary animate-pulse' : row.original.status==='on_break' ? 'bg-tertiary' : row.original.status==='compliance' ? 'bg-error' : 'bg-outline'" />
                  {{ row.original.statusLabel }}
                </span>
              </td>
              <td class="px-3 py-3 font-mono text-body-sm text-on-surface-variant">
                <div class="flex items-center gap-1.5"><MIcon name="mail" class="text-[14px]" />{{ row.original.email }}</div>
                <div class="flex items-center gap-1.5 mt-0.5"><MIcon name="call" class="text-[14px]" />{{ row.original.phone }}</div>
              </td>
              <td class="px-3 py-3">
                <div class="flex items-center gap-2">
                  <div class="rounded border border-outline-variant bg-surface-container-lowest p-1.5 text-on-surface-variant"><MIcon name="local_shipping" class="text-[18px]" /></div>
                  <div>
                    <div class="text-body-sm font-medium text-on-surface">{{ row.original.vehicle }}</div>
                    <div class="font-mono text-label-sm tracking-wider text-primary">{{ row.original.plate }}</div>
                  </div>
                </div>
              </td>
              <td class="px-3 py-3">
                <div class="font-medium text-on-surface text-body-sm">{{ row.original.route }}</div>
                <div class="flex items-center gap-1 text-label-sm text-outline"><MIcon name="schedule" class="text-[13px]" />{{ row.original.routeMeta }}</div>
              </td>
              <td class="px-3 py-3">
                <div class="w-36">
                  <div class="flex justify-between font-mono text-label-sm"><span class="font-semibold" :class="row.original.hosHours>7 ? 'text-error' : 'text-on-surface'">{{ row.original.hosHours }} hrs</span><span class="text-outline">/ {{ row.original.hosMax }} Max</span></div>
                  <div class="mt-1 h-1.5 w-full overflow-hidden rounded-full border border-outline-variant/60 bg-surface-container-lowest"><div class="h-full rounded-full" :class="row.original.hosHours>7 ? 'bg-error' : row.original.status==='on_break' ? 'bg-tertiary' : 'bg-primary'" :style="{ width: (row.original.hosHours/row.original.hosMax*100)+'%' }" /></div>
                </div>
              </td>
              <td class="px-3 py-3 text-right">
                <div class="inline-flex flex-col items-end">
                  <div class="flex items-center gap-2">
                    <svg class="h-5 w-16 overflow-visible" viewBox="0 0 64 20"><polyline :points="row.original.sparkline.map((v,i)=> `${i*12},${20-v}`).join(' ')" fill="none" :stroke="row.original.performance>97 ? '#06b6d4' : row.original.performance>93 ? '#ffb873' : '#64748b'" stroke-width="2" /></svg>
                    <span class="font-telemetry-numeric font-bold text-on-surface">{{ row.original.performance }}%</span>
                  </div>
                  <span class="text-label-sm" :class="row.original.performance>97 ? 'text-primary' : row.original.performance>94 ? 'text-tertiary' : 'text-outline'">{{ row.original.tier }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-1">
                  <button class="rounded p-1.5 text-outline hover:bg-surface-container-lowest hover:text-primary"><MIcon name="chat" /></button>
                  <button class="rounded p-1.5 text-outline hover:bg-surface-container-lowest hover:text-primary"><MIcon name="more_vert" /></button>
                </div>
              </td>
            </tr>
            <tr v-if="table.getRowModel().rows.length===0"><td colspan="8" class="py-10 text-center text-body-sm text-on-surface-variant">No drivers match your filters.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </main>
</template>
