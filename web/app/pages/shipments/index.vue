<script setup lang="ts">
import { createBookedShipment, STATUS_FLOW, type ShipmentStatus } from '~~/app/data/shipments'

definePageMeta({ layout: 'user', middleware: 'auth' })

useSeoMeta({
  title: 'My Shipments',
  description: 'Browse every consignment on your account — track shipments, request quotes, and create new bookings.',
})

const router = useRouter()
const route = useRoute()
const { list, add } = useShipments()

const bookOpen = ref(route.query.new === '1' || !route.query.new)
const quoteOpen = ref(route.query.new === 'quote')

const statusFilter = ref<'all' | ShipmentStatus>('all')

const filteredList = computed(() => {
  if (statusFilter.value === 'all') return list.value
  return list.value.filter((shipment) => shipment.status === statusFilter.value)
})

const statusTabs: Array<{ key: 'all' | ShipmentStatus; label: string }> = [
  { key: 'all', label: 'All' },
  { key: 'order_received', label: 'Order Received' },
  { key: 'in_transit', label: 'In Transit' },
  { key: 'out_for_delivery', label: 'Out for Delivery' },
  { key: 'booked', label: 'Order Received' },
  { key: 'delivered', label: 'Delivered' },
]

const badgeTone: Record<ShipmentStatus, string> = {
  order_received: 'border-outline-variant bg-surface-container-high text-on-surface-variant',
  booked: 'border-outline-variant bg-surface-container-high text-on-surface-variant',
  in_transit: 'border-primary/30 bg-primary-container/10 text-primary',
  out_for_delivery: 'border-tertiary-container/30 bg-tertiary-container/15 text-tertiary',
  delivered: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
}

const form = reactive({
  origin: '',
  destination: '',
  mode: 'Ocean Freight',
  priority: 'Standard Freight',
  grossWeight: '12000 kg',
})

const bookingError = ref('')

function submitBooking() {
  if (!form.origin.trim() || !form.destination.trim()) {
    bookingError.value = 'Please fill in both origin and destination.'
    return
  }
  const shipment = createBookedShipment({ ...form })
  add(shipment)
  router.push(`/shipments/${shipment.id}`)
}

const quoteForm = reactive({
  name: '',
  email: '',
  origin: '',
  destination: '',
  cargo: '',
  weight: '',
})
const quoteSent = ref(false)

function submitQuote() {
  quoteSent.value = true
}

function openQuote() {
  bookOpen.value = false
  quoteOpen.value = true
  quoteSent.value = false
}

function openBooking() {
  bookOpen.value = true
  quoteOpen.value = false
}
</script>

<template>
  <main class="bg-background">
    <div class="mx-auto max-w-[1600px] space-y-6 p-6">
      <!-- Header -->
      <section class="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div class="flex items-center gap-2 text-body-sm text-on-surface-variant">
            <span class="font-label-md uppercase tracking-wider text-on-surface-variant">Global Freight Portal</span>
            <span class="text-outline-variant">/</span>
            <span class="text-primary font-medium">Shipments</span>
          </div>
          <h1 class="mt-1 font-heading text-headline-lg font-bold tracking-tight text-on-surface">
            My Shipments
          </h1>
          <p class="text-body-sm text-on-surface-variant">{{ list.length }} consignments across your network</p>
        </div>
        <div class="flex items-center gap-2">
          <Button
            class="flex items-center gap-1 rounded-lg bg-secondary-container px-4 py-2 font-label-md font-semibold text-on-secondary-container transition-colors hover:opacity-90 active:scale-[0.98]"
            size="sm"
            @click="openBooking"
          >
            <MIcon name="add" class="text-[18px]" />
            New Shipment
          </Button>
          <Button
            class="flex items-center gap-1 rounded-lg border border-outline-variant bg-surface-low px-4 py-2 font-label-md text-on-surface transition-colors hover:border-primary hover:bg-surface-container-high"
            size="sm"
            @click="openQuote"
          >
            <MIcon name="request_quote" class="text-[18px] text-primary" />
            Request Quote
          </Button>
        </div>
      </section>

      <!-- Create / Quote forms -->
      <section v-if="bookOpen || quoteOpen" class="rounded-xl border border-outline-variant bg-surface-container p-6">
        <form v-if="bookOpen" novalidate class="space-y-4" @submit.prevent="submitBooking">
          <div class="flex items-center gap-2">
            <div class="flex size-9 items-center justify-center rounded-lg bg-primary-container/15 text-primary">
              <MIcon name="add_circle_outline" class="text-[20px]" />
            </div>
            <div>
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Create New Shipment</h2>
              <p class="text-body-sm text-on-surface-variant">Book a consignment and receive a tracking number immediately</p>
            </div>
          </div>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div class="space-y-1.5">
              <Label class="text-label-sm text-on-surface-variant">Origin</Label>
              <Input v-model="form.origin" placeholder="e.g. Rotterdam, NL" class="border-outline-variant bg-surface" />
            </div>
            <div class="space-y-1.5">
              <Label class="text-label-sm text-on-surface-variant">Destination</Label>
              <Input v-model="form.destination" placeholder="e.g. Chicago, US" class="border-outline-variant bg-surface" />
            </div>
            <div class="space-y-1.5">
              <Label class="text-label-sm text-on-surface-variant">Freight Mode</Label>
              <select v-model="form.mode" class="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface focus:border-primary focus:outline-none">
                <option>Ocean Freight</option>
                <option>Air Cargo</option>
                <option>Intermodal</option>
                <option>Ground Fleet</option>
              </select>
            </div>
            <div class="space-y-1.5">
              <Label class="text-label-sm text-on-surface-variant">Service Level</Label>
              <select v-model="form.priority" class="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface focus:border-primary focus:outline-none">
                <option>Standard Freight</option>
                <option>Express &amp; Priority</option>
                <option>Temp Controlled</option>
                <option>Last-Mile Express</option>
              </select>
            </div>
            <div class="space-y-1.5">
              <Label class="text-label-sm text-on-surface-variant">Estimated Gross Weight</Label>
              <Input v-model="form.grossWeight" inputmode="numeric" class="border-outline-variant bg-surface" />
            </div>
          </div>
          <p v-if="bookingError" class="text-body-sm text-destructive">{{ bookingError }}</p>
          <div class="flex items-center justify-end gap-2 border-t border-outline-variant pt-4">
            <Button type="button" variant="ghost" class="text-label-md text-on-surface-variant hover:bg-surface-container-high" @click="bookOpen = false">
              Cancel
            </Button>
            <Button type="submit" class="gap-1 rounded-lg bg-primary-container font-label-md font-bold text-on-primary-container hover:bg-primary">
              <MIcon name="local_shipping" class="text-[18px]" />
              Book Shipment
            </Button>
          </div>
        </form>

        <form v-else novalidate class="space-y-4" @submit.prevent="submitQuote">
          <div class="flex items-center gap-2">
            <div class="flex size-9 items-center justify-center rounded-lg bg-secondary-container/20 text-secondary">
              <MIcon name="request_quote" class="text-[20px]" />
            </div>
            <div>
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Request Freight Quote</h2>
              <p class="text-body-sm text-on-surface-variant">A freight specialist will respond within 2 business hours</p>
            </div>
          </div>
          <div v-if="quoteSent" class="rounded-lg border border-primary/30 bg-primary-container/10 p-3 text-body-sm text-on-surface">
            <span class="font-semibold text-primary">Quote request received.</span>
            <span class="text-on-surface-variant"> Our team is pricing lanes across your carrier network — expect a response shortly.</span>
          </div>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div class="space-y-1.5">
              <Label class="text-label-sm text-on-surface-variant">Contact Name</Label>
              <Input v-model="quoteForm.name" placeholder="Full name" class="border-outline-variant bg-surface" />
            </div>
            <div class="space-y-1.5">
              <Label class="text-label-sm text-on-surface-variant">Work Email</Label>
              <Input v-model="quoteForm.email" type="email" placeholder="you@company.com" class="border-outline-variant bg-surface" />
            </div>
            <div class="space-y-1.5">
              <Label class="text-label-sm text-on-surface-variant">Origin</Label>
              <Input v-model="quoteForm.origin" placeholder="City or port of departure" class="border-outline-variant bg-surface" />
            </div>
            <div class="space-y-1.5">
              <Label class="text-label-sm text-on-surface-variant">Destination</Label>
              <Input v-model="quoteForm.destination" placeholder="City or port of arrival" class="border-outline-variant bg-surface" />
            </div>
            <div class="space-y-1.5">
              <Label class="text-label-sm text-on-surface-variant">Cargo Description</Label>
              <Input v-model="quoteForm.cargo" placeholder="e.g. Integrated electronics, 22 pallets" class="border-outline-variant bg-surface" />
            </div>
            <div class="space-y-1.5">
              <Label class="text-label-sm text-on-surface-variant">Estimated Weight</Label>
              <Input v-model="quoteForm.weight" placeholder="e.g. 14,850 kg" class="border-outline-variant bg-surface" />
            </div>
          </div>
          <div class="flex items-center justify-end gap-2 border-t border-outline-variant pt-4">
            <Button type="button" variant="ghost" class="text-label-md text-on-surface-variant hover:bg-surface-container-high" @click="quoteOpen = false; quoteSent = false">
              Cancel
            </Button>
            <Button type="submit" class="gap-1 rounded-lg bg-secondary-container font-label-md font-semibold text-on-secondary-container hover:opacity-90">
              <MIcon name="send" class="text-[18px]" />
              Request Quote
            </Button>
          </div>
        </form>
      </section>

      <!-- Filters -->
      <section class="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div class="flex items-center gap-1 rounded-lg border border-outline-variant bg-surface-low p-1">
          <button
            v-for="tab in statusTabs"
            :key="tab.key"
            type="button"
            class="rounded px-2.5 py-1 text-label-sm transition-colors"
            :class="statusFilter === tab.key
              ? 'bg-surface-container-highest font-semibold text-primary'
              : 'text-on-surface-variant hover:text-on-surface'"
            @click="statusFilter = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>
        <span class="text-label-sm text-on-surface-variant">{{ filteredList.length }} shown</span>
      </section>

      <!-- Shipments list -->
      <section aria-label="Shipments" class="rounded-xl border border-outline-variant bg-surface-container">
        <ul class="divide-y divide-outline-variant/60">
          <li v-for="shipment in filteredList" :key="shipment.id">
            <NuxtLink
              :to="`/shipments/${shipment.id}`"
              class="flex flex-col gap-3 p-4 transition-colors hover:bg-surface-container-high md:flex-row md:items-center md:justify-between"
            >
              <div class="flex items-center gap-3">
                <div class="flex size-10 shrink-0 items-center justify-center rounded-lg border border-outline-variant bg-surface-low text-primary">
                  <MIcon
                    :name="shipment.status === 'delivered' ? 'verified' : shipment.status === 'in_transit' ? 'airplanemode_active' : 'local_shipping'"
                    class="text-[20px]"
                  />
                </div>
                <div>
                  <div class="flex items-center gap-2">
                    <span class="font-telemetry-numeric font-semibold text-on-surface">{{ shipment.id }}</span>
                    <span class="rounded border border-outline-variant bg-surface-container-high px-1.5 py-0.5 text-label-sm text-on-surface-variant">{{ shipment.mode }}</span>
                  </div>
                  <p class="mt-0.5 text-body-sm text-on-surface-variant">
                    {{ shipment.origin }} ({{ shipment.originCode }}) → {{ shipment.destination }} ({{ shipment.destinationCode }})
                  </p>
                </div>
              </div>
              <div class="flex items-center gap-4 pl-13 md:pl-0">
                <div class="text-right">
                  <p class="text-label-sm text-on-surface-variant">ETA</p>
                  <p class="font-heading text-label-md font-semibold text-on-surface">{{ shipment.eta }}</p>
                </div>
                <span class="rounded px-2 py-1 text-label-sm font-semibold" :class="badgeTone[shipment.status]">
                  {{ STATUS_FLOW[shipment.status].label }}
                </span>
                <MIcon name="chevron_right" class="text-[16px] text-outline" />
              </div>
            </NuxtLink>
          </li>
          <li v-if="filteredList.length === 0" class="px-4 py-10 text-center">
            <MIcon name="inventory_2" class="text-[28px] text-outline" />
            <p class="mt-2 text-body-sm text-on-surface-variant">No shipments match this filter yet.</p>
          </li>
        </ul>
      </section>

      <p class="text-center text-body-sm text-on-surface-variant">
        Need help? <NuxtLink to="/profile" class="text-primary hover:underline">Contact Support</NuxtLink>
      </p>
    </div>
  </main>
</template>