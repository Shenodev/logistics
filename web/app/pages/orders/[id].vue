<script setup lang="ts">
import type { DeliveryStatus } from '~~/app/data/shipments'

definePageMeta({ layout: 'delivery', middleware: 'auth' })

const route = useRoute()
const router = useRouter()
const { get, updateDeliveryStatus } = useShipments()

const shipment = computed(() => get(String(route.params.id ?? '')))

useSeoMeta({
  title: () => shipment.value ? `${shipment.value.id} — Active Order` : 'Order not found',
  description: () => shipment.value ? `Delivery active order ${shipment.value.id} — pickup and dropoff with status updates.` : 'Order not found',
})

const deliveryLabel: Record<DeliveryStatus, string> = {
  assigned: 'Ready for Pickup',
  picked_up: 'Picked Up',
  on_the_way: 'On the Way',
  delivered: 'Delivered',
}

const nextAction = computed(() => {
  if (!shipment.value) return null
  const s = shipment.value.deliveryStatus
  if (s === 'assigned') return { next: 'picked_up' as const, label: 'Picked Up', icon: 'inventory', desc: 'Confirm you have collected the order from the restaurant' }
  if (s === 'picked_up') return { next: 'on_the_way' as const, label: 'On the Way', icon: 'local_shipping', desc: 'Heading to customer — share live ETA' }
  if (s === 'on_the_way') return { next: 'delivered' as const, label: 'Delivered', icon: 'verified', desc: 'Confirm handover and signature' }
  return null
})

const updating = ref(false)
const toast = ref<string | null>(null)
const callToast = ref(false)

function showToast(msg: string) {
  toast.value = msg
  setTimeout(() => (toast.value = null), 3000)
}

async function advanceStatus() {
  if (!shipment.value || !nextAction.value || updating.value) return
  updating.value = true
  await new Promise((r) => setTimeout(r, 400))
  const ok = updateDeliveryStatus(shipment.value!.id, nextAction.value!.next)
  updating.value = false
  if (ok) {
    if ('vibrate' in navigator) navigator.vibrate(30)
    showToast(`Status: ${deliveryLabel[nextAction.value!.next as DeliveryStatus]}`)
  }
}

function onCall() {
  callToast.value = true
  if ('vibrate' in navigator) navigator.vibrate(15)
  setTimeout(() => (callToast.value = false), 2000)
}

const isDelivered = computed(() => shipment.value?.deliveryStatus === 'delivered')
</script>

<template>
  <div class="space-y-4">
    <div v-if="toast" class="rounded-xl border border-primary/30 bg-primary/10 px-3 py-2 text-center text-body-sm font-medium text-primary">
      {{ toast }}
    </div>

    <template v-if="shipment">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <button class="inline-flex min-h-10 items-center gap-1 rounded-lg border border-outline-variant bg-surface-container px-3 text-label-md font-medium text-on-surface" @click="router.back()">
          <MIcon name="arrow_back" class="text-[18px]" /> Back
        </button>
        <span class="rounded-full border px-2.5 py-1 text-label-sm font-bold" :class="isDelivered ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400' : 'border-primary/30 bg-primary/10 text-primary'">
          {{ deliveryLabel[shipment.deliveryStatus] }}
        </span>
      </div>

      <div class="rounded-xl border border-outline-variant bg-surface-container p-3">
        <div class="flex items-center gap-2">
          <MIcon name="receipt_long" class="text-[20px] text-primary" />
          <h1 class="font-heading text-headline-sm font-bold text-on-surface">{{ shipment.id }}</h1>
          <span class="ml-auto font-mono text-label-sm text-on-surface-variant">{{ shipment.mode }}</span>
        </div>
        <div class="mt-1 flex items-center gap-2 text-body-sm text-on-surface-variant">
          <span class="rounded bg-surface-low px-1.5 py-0.5 font-mono text-label-sm">{{ shipment.grossWeight }}</span>
          <span>{{ shipment.pallets }}</span>
          <span class="h-3 w-px bg-outline-variant" />
          <span class="text-primary font-medium">{{ shipment.priority }}</span>
        </div>
      </div>

      <!-- Pickup — Restaurant -->
      <section class="rounded-xl border border-outline-variant bg-surface-container p-3">
        <div class="flex items-center gap-2">
          <div class="flex size-9 items-center justify-center rounded-lg bg-tertiary-container/20 text-tertiary border border-tertiary/20">
            <MIcon name="restaurant" class="text-[20px]" />
          </div>
          <div>
            <h2 class="font-heading text-label-md font-bold text-on-surface">Pickup — Restaurant</h2>
            <p class="text-body-sm font-medium text-on-surface">{{ shipment.restaurantName }}</p>
          </div>
          <span class="ml-auto rounded-full bg-surface-low px-2 py-0.5 text-label-sm font-semibold text-on-surface-variant">Step 1</span>
        </div>
        <div class="mt-2 space-y-1 rounded-lg bg-surface-low p-2.5">
          <div class="flex items-start gap-1.5 text-body-sm text-on-surface">
            <MIcon name="location_on" class="mt-0.5 text-[16px] text-primary" />
            <span>{{ shipment.restaurantAddress }}</span>
          </div>
          <div class="flex items-center gap-1.5 text-body-sm text-on-surface-variant">
            <MIcon name="storefront" class="text-[16px] text-outline" />
            <span>{{ shipment.origin }} ({{ shipment.originCode }})</span>
          </div>
        </div>
        <a
          href="https://maps.google.com/?q=Restaurant"
          target="_blank"
          rel="noopener"
          class="mt-2 inline-flex min-h-12 w-full items-center justify-center gap-1.5 rounded-xl border border-outline-variant bg-surface-container-high px-4 text-label-md font-bold text-on-surface hover:bg-surface-low"
        >
          <MIcon name="navigation" class="text-[18px] text-primary" /> Navigate to Pickup
        </a>
      </section>

      <!-- Dropoff — Customer -->
      <section class="rounded-xl border border-primary/20 bg-surface-container p-3">
        <div class="flex items-center gap-2">
          <div class="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary border border-primary/20">
            <MIcon name="person_pin_circle" class="text-[20px]" />
          </div>
          <div>
            <h2 class="font-heading text-label-md font-bold text-on-surface">Dropoff — Customer</h2>
            <p class="text-body-sm font-medium text-on-surface">{{ shipment.consigneeName }}</p>
          </div>
          <span class="ml-auto rounded-full bg-primary/10 border border-primary/30 px-2 py-0.5 text-label-sm font-bold text-primary">Step 2</span>
        </div>
        <div class="mt-2 space-y-1 rounded-lg bg-surface-low p-2.5">
          <div class="flex items-start gap-1.5 text-body-sm text-on-surface">
            <MIcon name="location_on" class="mt-0.5 text-[16px] text-primary" />
            <span>{{ shipment.consigneeAddress }}</span>
          </div>
          <div class="flex items-center gap-1.5 text-body-sm text-on-surface">
            <MIcon name="person" class="text-[16px] text-outline" />
            <span>{{ shipment.receiver }} • {{ shipment.receiverRole }}</span>
          </div>
          <div class="flex items-center gap-1.5 text-body-sm text-on-surface-variant">
            <MIcon name="badge" class="text-[16px] text-outline" />
            <span>Badge {{ shipment.receiverBadge }}</span>
          </div>
        </div>

        <!-- Prominent Call Customer button — tel: link, large touch target -->
        <a
          :href="`tel:${shipment.customerPhone.replace(/\s|\(|\)|-/g, '')}`"
          class="mt-3 inline-flex min-h-14 w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 text-headline-sm font-bold text-on-primary shadow-sm hover:bg-primary/90 active:scale-[0.98] transition-transform"
          @click="onCall"
        >
          <MIcon name="call" class="text-[22px]" />
          Call Customer
          <span class="ml-1 font-mono text-body-sm font-medium opacity-90">{{ shipment.customerPhone }}</span>
        </a>
        <p v-if="callToast" class="mt-2 text-center text-body-sm font-medium text-primary">Opening phone dialer…</p>
        <p class="mt-1 text-center text-label-sm text-on-surface-variant">Tap to call via device dialer — hands-free for driving</p>
      </section>

      <!-- Status update — large sequential buttons -->
      <section class="rounded-xl border border-outline-variant bg-surface-container p-3">
        <div class="flex items-center gap-2">
          <MIcon name="update" class="text-[20px] text-primary" />
          <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Status Update</h2>
          <span class="ml-auto text-label-sm text-on-surface-variant">Sequential</span>
        </div>

        <div class="mt-3 flex items-center justify-between rounded-lg bg-surface-low p-2">
          <div class="flex items-center gap-1.5">
            <span class="h-2 w-2 rounded-full" :class="isDelivered ? 'bg-emerald-400' : 'bg-primary animate-pulse'" />
            <span class="font-label-md font-semibold" :class="isDelivered ? 'text-emerald-400' : 'text-primary'">{{ deliveryLabel[shipment.deliveryStatus] }}</span>
          </div>
          <span v-if="shipment.deliveryUpdatedAt" class="font-mono text-label-sm text-on-surface-variant">{{ shipment.deliveryUpdatedAt }}</span>
          <span v-else class="text-label-sm text-outline">Not started</span>
        </div>

        <!-- Progress stepper -->
        <div class="mt-3 grid grid-cols-3 gap-1">
          <div
            v-for="step in (['picked_up','on_the_way','delivered'] as const)"
            :key="step"
            class="h-1.5 rounded-full"
            :class="(['picked_up','on_the_way','delivered'].indexOf(shipment.deliveryStatus) >= ['picked_up','on_the_way','delivered'].indexOf(step)) ? 'bg-primary' : 'bg-surface-low'"
          />
        </div>
        <div class="mt-1 flex justify-between text-[11px] font-medium uppercase tracking-wider" :class="isDelivered ? 'text-emerald-400' : 'text-on-surface-variant'">
          <span>Picked Up</span><span>On the Way</span><span>Delivered</span>
        </div>

        <div class="mt-4 space-y-2">
          <button
            v-if="nextAction"
            type="button"
            class="inline-flex min-h-14 w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 text-headline-sm font-bold text-on-primary shadow-sm hover:bg-primary/90 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none"
            :disabled="updating"
            @click="advanceStatus"
          >
            <MIcon :name="nextAction.icon" class="text-[22px]" />
            <span>{{ nextAction.label }}</span>
            <span v-if="updating" class="ml-2 h-4 w-4 animate-spin rounded-full border-2 border-on-primary border-t-transparent" />
          </button>
          <div v-else class="flex min-h-14 items-center justify-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-400">
            <MIcon name="verified" class="text-[22px]" />
            <span class="font-heading text-headline-sm font-bold">Delivered — Completed</span>
          </div>
          <p v-if="nextAction" class="text-center text-body-sm text-on-surface-variant">{{ nextAction.desc }}</p>
          <p v-else class="text-center text-body-sm text-emerald-400">Order delivered. Awaiting customer signature sync.</p>
        </div>

        <div class="mt-3 grid grid-cols-3 gap-2 text-center">
          <div class="rounded-lg border px-2 py-1" :class="shipment.deliveryStatus==='picked_up' || shipment.deliveryStatus==='on_the_way' || shipment.deliveryStatus==='delivered' ? 'border-primary/30 bg-primary/10 text-primary' : 'border-outline-variant bg-surface-low text-outline'">Picked Up</div>
          <div class="rounded-lg border px-2 py-1" :class="shipment.deliveryStatus==='on_the_way' || shipment.deliveryStatus==='delivered' ? 'border-primary/30 bg-primary/10 text-primary' : 'border-outline-variant bg-surface-low text-outline'">On the Way</div>
          <div class="rounded-lg border px-2 py-1" :class="shipment.deliveryStatus==='delivered' ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400' : 'border-outline-variant bg-surface-low text-outline'">Delivered</div>
        </div>
      </section>

      <div class="pb-2 text-center text-label-sm text-outline">Large touch targets • 48px+ • Outdoor readable • PWA offline-ready</div>
    </template>

    <div v-else class="mx-auto max-w-md rounded-xl border border-dashed border-outline-variant bg-surface-container p-8 text-center">
      <MIcon name="search_off" class="text-[32px] text-outline" />
      <h1 class="mt-2 font-heading text-headline-sm font-bold text-on-surface">Order not found</h1>
      <p class="mt-1 text-body-sm text-on-surface-variant">Check the order ID or return to incoming queue.</p>
      <NuxtLink to="/incoming" class="mt-4 inline-flex min-h-12 items-center justify-center rounded-xl bg-primary px-6 text-label-md font-bold text-on-primary">Back to Incoming</NuxtLink>
    </div>
  </div>
</template>
