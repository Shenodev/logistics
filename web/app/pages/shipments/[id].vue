<script setup lang="ts">
import { canCancelOrder, STATUS_FLOW } from '~~/app/data/shipments'

definePageMeta({ layout: 'user', middleware: 'auth' })

const route = useRoute()
const router = useRouter()
const { get: findShipment, cancelOrder } = useShipments()

const shipment = computed(() => findShipment(String(route.params.id ?? '')))

useSeoMeta({
  title: () => shipment.value ? `${shipment.value.id} · Tracking` : 'Shipment not found',
  description: () => shipment.value
    ? `Live tracking and chain of custody for ${shipment.value.id} — ${shipment.value.origin} to ${shipment.value.destination}.`
    : 'The requested shipment could not be found.',
})

const statusLabel = computed(() => shipment.value ? STATUS_FLOW[shipment.value.status].label : '')

// Vue conditional rendering: only Stage 1 "Order Received" is cancellable
const canCancel = computed(() => shipment.value ? canCancelOrder(shipment.value) : false)

const showCancelConfirm = ref(false)
const cancelling = ref(false)
const cancelSuccess = ref(false)

function requestCancel() {
  showCancelConfirm.value = true
}

function closeCancelDialog() {
  if (cancelling.value) return
  showCancelConfirm.value = false
}

async function confirmCancel() {
  if (!shipment.value || cancelling.value) return
  cancelling.value = true
  // Simulate async cancellation (would be Stripe refund flag on backend)
  await new Promise((resolve) => setTimeout(resolve, 500))
  cancelOrder(shipment.value.id)
  cancelling.value = false
  showCancelConfirm.value = false
  cancelSuccess.value = true
  // Brief success state then redirect to shipments list
  setTimeout(() => {
    router.push('/shipments')
  }, 900)
}
</script>

<template>
  <main class="bg-background">
    <template v-if="shipment">
      <div class="mx-auto max-w-[1600px] space-y-6 p-6">
        <!-- Cancel success banner (v-if conditional rendering) -->
        <div
          v-if="cancelSuccess"
          class="flex items-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-body-sm text-emerald-400"
        >
          <MIcon name="check_circle" class="text-[18px]" />
          <span class="font-medium">Order cancelled — flagged for Visa refund via Stripe. Redirecting…</span>
        </div>

        <!-- 1. Title & metadata -->
        <section class="rounded-xl border border-outline-variant bg-surface-container p-4">
          <div class="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
            <div class="flex flex-wrap items-center gap-4">
              <div>
                <div class="flex items-center gap-3">
                  <h1 class="font-heading font-telemetry-numeric text-headline-lg font-bold tracking-tight text-on-surface">
                    {{ shipment.id }}
                  </h1>
                  <div class="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary-container/15 px-3 py-1 text-primary">
                    <span class="relative flex h-2 w-2">
                      <span class="radar-pulse absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
                      <span class="relative inline-flex h-2 w-2 rounded-full bg-primary" />
                    </span>
                    <span class="text-label-sm font-semibold uppercase tracking-wider">{{ statusLabel }}</span>
                  </div>
                  <span class="rounded border border-outline-variant bg-surface-container-high px-2.5 py-0.5 text-label-sm text-on-surface-variant">
                    {{ shipment.priority }}
                  </span>
                </div>
                <div class="mt-1 flex flex-wrap items-center gap-4 text-body-sm text-on-surface-variant">
                  <span class="flex items-center gap-1 font-medium text-on-surface">
                    <MIcon name="flight_takeoff" class="text-[16px] text-primary" />
                    {{ shipment.origin }} ({{ shipment.originCode }})
                  </span>
                  <MIcon name="arrow_forward" class="text-[16px] text-outline" />
                  <span class="flex items-center gap-1 font-medium text-on-surface">
                    <MIcon name="flight_land" class="text-[16px] text-primary" />
                    {{ shipment.destination }} ({{ shipment.destinationCode }})
                  </span>
                  <span class="text-outline">•</span>
                  <span>Booked {{ shipment.bookedAt }}</span>
                  <span class="text-outline">•</span>
                  <span>Master AWB: <strong class="font-telemetry-numeric text-on-surface">{{ shipment.masterAwb }}</strong></span>
                </div>
              </div>
            </div>

            <div class="flex flex-wrap items-center gap-2 self-start lg:self-center">
              <!-- CRITICAL: Cancel Order — Vue conditional rendering (v-if) — only Stage 1 "Order Received" -->
              <ShipmentCancelOrderButton
                v-if="canCancel"
                :shipment="shipment"
                :loading="cancelling"
                @cancel="requestCancel"
              />
              <button class="flex items-center gap-1.5 rounded-lg border border-outline-variant bg-surface-low px-3 py-2 text-label-md text-on-surface transition-colors hover:border-primary hover:bg-surface-container-high active:scale-[0.98]">
                <MIcon name="picture_as_pdf" class="text-[18px] text-primary" />
                <span>Download Waybill (PDF)</span>
              </button>
              <button class="flex items-center gap-1.5 rounded-lg border border-outline-variant bg-surface-low px-3 py-2 text-label-md text-on-surface transition-colors hover:border-primary hover:bg-surface-container-high active:scale-[0.98]">
                <MIcon name="share" class="text-[18px] text-on-surface-variant" />
                <span>Share Tracking Link</span>
              </button>
              <button class="flex items-center gap-1.5 rounded-lg border border-outline-variant bg-surface-container-high px-3 py-2 text-label-md text-on-surface transition-colors hover:bg-surface-bright active:scale-[0.98]">
                <MIcon name="support_agent" class="text-[18px] text-secondary" />
                <span>Contact Freight Specialist</span>
              </button>
            </div>
          </div>
        </section>

        <!-- Cancel confirmation dialog (conditional rendering with v-if) -->
        <div
          v-if="showCancelConfirm"
          class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
          @click.self="closeCancelDialog"
        >
          <div class="w-full max-w-md rounded-xl border border-outline-variant bg-surface-container p-6 shadow-xl">
            <div class="flex items-start gap-3">
              <div class="flex size-10 shrink-0 items-center justify-center rounded-full bg-destructive/10 text-destructive">
                <MIcon name="warning" class="text-[22px]" />
              </div>
              <div>
                <h3 class="font-heading text-headline-sm font-semibold text-on-surface">Cancel order {{ shipment.id }}?</h3>
                <p class="mt-1 text-body-sm leading-relaxed text-on-surface-variant">
                  This order is still in <strong class="text-on-surface">Order Received</strong> (Stage 1) and can be cancelled. A refund will be flagged for processing back to your Visa via Stripe. This action cannot be undone after carrier pickup.
                </p>
              </div>
            </div>
            <div class="mt-6 flex items-center justify-end gap-2">
              <button
                class="rounded-lg px-4 py-2 text-label-md font-medium text-on-surface-variant hover:bg-surface-container-high"
                :disabled="cancelling"
                @click="closeCancelDialog"
              >
                Keep order
              </button>
              <button
                class="inline-flex items-center gap-1.5 rounded-lg bg-destructive px-4 py-2 text-label-md font-semibold text-destructive-foreground hover:bg-destructive/90 disabled:opacity-50"
                :disabled="cancelling"
                @click="confirmCancel"
              >
                <MIcon v-if="!cancelling" name="cancel" class="text-[16px]" />
                <span>{{ cancelling ? 'Cancelling…' : 'Confirm cancel' }}</span>
              </button>
            </div>
            <p class="mt-3 text-label-sm text-outline">Refund issued via Stripe to original Visa • Stage 1 only</p>
          </div>
        </div>

        <!-- 2. Live telemetry map -->
        <section class="relative overflow-hidden rounded-xl border border-outline-variant bg-surface-container">
          <div class="flex items-center justify-between border-b border-outline-variant bg-surface-low px-4 py-2.5 text-label-sm">
            <div class="flex flex-wrap items-center gap-4">
              <span class="flex items-center gap-1.5 font-medium text-primary">
                <MIcon name="radar" class="text-[16px]" />
                LIVE RADAR VECTOR TELEMETRY
              </span>
              <span class="hidden text-outline-variant md:inline">|</span>
              <span class="text-on-surface-variant">CARRIER: <span class="font-mono text-on-surface">{{ shipment.carrier }}</span></span>
              <span class="hidden text-outline-variant lg:inline">|</span>
              <span class="hidden text-on-surface-variant lg:inline">VESSEL/AIRCRAFT ID: <span class="font-mono text-on-surface">N782AT</span></span>
            </div>
            <div class="flex items-center gap-4 font-mono text-on-surface-variant">
              <span>LAT: <strong class="text-primary">{{ shipment.lat }}</strong></span>
              <span>LON: <strong class="text-primary">{{ shipment.lon }}</strong></span>
              <span>SPD: <strong class="text-on-surface">{{ shipment.spd }}</strong></span>
              <span class="hidden sm:inline">ALT: <strong class="text-on-surface">{{ shipment.alt }}</strong></span>
            </div>
          </div>

          <div class="relative h-[420px] w-full overflow-hidden bg-surface-lowest">
            <ShipmentMap :shipment="shipment" />

            <div class="absolute top-4 right-4 z-10 flex flex-col gap-1.5">
              <button class="flex size-8 items-center justify-center rounded border border-outline-variant bg-surface-low/90 text-on-surface transition-colors hover:bg-surface-container-high" title="Zoom In">
                <MIcon name="add" class="text-[18px]" />
              </button>
              <button class="flex size-8 items-center justify-center rounded border border-outline-variant bg-surface-low/90 text-on-surface transition-colors hover:bg-surface-container-high" title="Zoom Out">
                <MIcon name="remove" class="text-[18px]" />
              </button>
              <button class="flex size-8 items-center justify-center rounded border border-outline-variant bg-surface-low/90 text-primary transition-colors hover:bg-surface-container-high" title="Recenter on Vessel">
                <MIcon name="my_location" class="text-[18px]" />
              </button>
            </div>

            <div class="pointer-events-none absolute right-4 bottom-4 left-4 z-10 grid grid-cols-1 gap-4 md:grid-cols-3">
              <div class="pointer-events-auto flex items-center gap-2 rounded-xl border border-outline-variant bg-surface-low/95 p-2 backdrop-blur-sm">
                <div class="flex size-10 shrink-0 items-center justify-center rounded-lg border border-primary/20 bg-primary-container/10 text-primary">
                  <MIcon name="schedule" class="text-[22px]" />
                </div>
                <div>
                  <div class="text-label-sm uppercase tracking-wider text-on-surface-variant">Estimated Time of Arrival</div>
                  <div class="font-heading text-headline-sm font-bold text-on-surface">{{ shipment.eta }} <span class="text-label-md font-normal text-on-surface-variant">{{ shipment.etaTz }}</span></div>
                  <div class="mt-0.5 flex items-center gap-1 text-label-sm font-medium text-primary">
                    <MIcon name="check_circle" class="text-[14px]" />
                    Operational Status: On Schedule
                  </div>
                </div>
              </div>
              <div class="pointer-events-auto flex items-center gap-2 rounded-xl border border-outline-variant bg-surface-low/95 p-2 backdrop-blur-sm">
                <div class="flex size-10 shrink-0 items-center justify-center rounded-lg border border-outline-variant bg-surface-container-high text-secondary">
                  <MIcon name="transfer_within_a_station" class="text-[22px]" />
                </div>
                <div>
                  <div class="text-label-sm uppercase tracking-wider text-on-surface-variant">Next Transit Checkpoint</div>
                  <div class="font-heading text-headline-sm font-bold text-on-surface">{{ shipment.nextCheckpoint }}</div>
                  <div class="mt-0.5 flex items-center gap-1 font-mono text-label-sm text-on-surface-variant">
                    <MIcon name="timelapse" class="text-[14px] text-tertiary" />
                    Approaching in {{ shipment.nextCheckpointIn }}
                  </div>
                </div>
              </div>
              <div class="pointer-events-auto flex items-center gap-2 rounded-xl border border-outline-variant bg-surface-low/95 p-2 backdrop-blur-sm">
                <div class="flex size-10 shrink-0 items-center justify-center rounded-lg border border-outline-variant bg-surface-container-high text-primary">
                  <MIcon name="thermostat" class="text-[22px]" />
                </div>
                <div>
                  <div class="text-label-sm uppercase tracking-wider text-on-surface-variant">Atmospheric &amp; Cargo Telemetry</div>
                  <div class="font-heading text-headline-sm font-bold text-on-surface">{{ shipment.weather }}</div>
                  <div class="mt-0.5 flex items-center gap-1 text-label-sm font-medium text-primary">
                    <MIcon name="ac_unit" class="text-[14px]" />
                    {{ shipment.cargoTemp }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 3. Milestone timeline (extracted Vue component) -->
        <ShipmentMilestoneTimeline :shipment="shipment" />

        <!-- 4. Cargo details & POD -->
        <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <section class="flex flex-col justify-between rounded-xl border border-outline-variant bg-surface-container p-6">
            <div>
              <div class="mb-4 flex items-center justify-between border-b border-outline-variant pb-2">
                <div class="flex items-center gap-1">
                  <MIcon name="inventory_2" class="text-[22px] text-primary" />
                  <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Cargo &amp; Consignment Details</h2>
                </div>
                <span class="rounded border border-primary/20 bg-surface-container-high px-2 py-0.5 text-label-sm text-primary">Verified Manifest</span>
              </div>

              <div class="mb-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
                <div class="rounded-lg border border-outline-variant bg-surface-low p-2">
                  <div class="text-label-sm uppercase text-on-surface-variant">Gross Weight</div>
                  <div class="mt-1 font-telemetry-numeric font-bold text-on-surface">{{ shipment.grossWeight }}</div>
                  <div class="text-label-sm text-outline">{{ shipment.grossWeightLbs }}</div>
                </div>
                <div class="rounded-lg border border-outline-variant bg-surface-low p-2">
                  <div class="text-label-sm uppercase text-on-surface-variant">Total Volume</div>
                  <div class="mt-1 font-telemetry-numeric font-bold text-on-surface">{{ shipment.totalVolume }}</div>
                  <div class="text-label-sm text-outline">{{ shipment.totalVolumeCu }}</div>
                </div>
                <div class="rounded-lg border border-outline-variant bg-surface-low p-2">
                  <div class="text-label-sm uppercase text-on-surface-variant">Pallet Count</div>
                  <div class="mt-1 font-telemetry-numeric font-bold text-on-surface">{{ shipment.pallets }}</div>
                  <div class="text-label-sm text-outline">{{ shipment.palletType }}</div>
                </div>
                <div class="rounded-lg border border-outline-variant bg-surface-low p-2">
                  <div class="text-label-sm uppercase text-on-surface-variant">Container Spec</div>
                  <div class="mt-1 font-telemetry-numeric font-bold text-on-surface">{{ shipment.containerSpec }}</div>
                  <div class="text-label-sm text-outline">{{ shipment.containerSpecDetail }}</div>
                </div>
              </div>

              <div class="mb-4 rounded-lg border border-outline-variant bg-surface-low p-2">
                <div class="mb-1 flex items-center justify-between text-body-sm">
                  <span class="text-on-surface-variant">Container Dimensions (L × W × H):</span>
                  <span class="font-mono font-semibold text-on-surface">{{ shipment.dimensions }}</span>
                </div>
                <div class="flex items-center justify-between text-body-sm">
                  <span class="text-on-surface-variant">Payload Tare:</span>
                  <span class="font-mono text-on-surface">{{ shipment.tare }}</span>
                </div>
              </div>

              <div class="mb-4 space-y-1">
                <div class="text-label-sm font-semibold uppercase text-on-surface-variant">Handling Directives &amp; Sensitivities:</div>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="tag in shipment.handling"
                    :key="tag.label"
                    class="inline-flex items-center gap-1.5 rounded px-2.5 py-1 text-label-md"
                    :class="tag.kind === 'primary'
                      ? 'border border-primary/30 bg-primary-container/10 text-primary'
                      : tag.kind === 'tertiary'
                        ? 'border border-tertiary/30 bg-tertiary-container/15 text-tertiary'
                        : 'border border-outline-variant bg-surface-container-high text-on-surface'"
                  >
                    <MIcon :name="tag.icon" class="text-[16px]" />
                    {{ tag.label }}
                  </span>
                </div>
              </div>
            </div>

            <div class="flex items-center justify-between rounded-lg border border-outline-variant bg-surface-low p-2">
              <div class="flex items-center gap-2">
                <div class="flex size-8 items-center justify-center rounded bg-surface-container-highest text-primary">
                  <MIcon name="gavel" class="text-[20px]" />
                </div>
                <div>
                  <div class="text-body-sm font-semibold text-on-surface">Customs Declaration: HS Code {{ shipment.hsCode }}</div>
                  <div class="text-label-sm text-on-surface-variant">{{ shipment.hsDesc }}</div>
                </div>
              </div>
              <span class="inline-flex items-center gap-1 text-label-sm font-semibold text-primary">
                <MIcon name="task_alt" class="text-[16px]" />
                AMS/ISF Cleared
              </span>
            </div>
          </section>

          <section class="flex flex-col justify-between rounded-xl border border-outline-variant bg-surface-container p-6">
            <div>
              <div class="mb-4 flex items-center justify-between border-b border-outline-variant pb-2">
                <div class="flex items-center gap-1">
                  <MIcon name="fact_check" class="text-[22px] text-secondary" />
                  <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Proof of Delivery (POD) &amp; Verification</h2>
                </div>
                <span class="flex items-center gap-1 rounded border border-tertiary/25 bg-tertiary-container/15 px-2.5 py-0.5 text-label-sm font-medium text-tertiary">
                  <span class="size-1.5 rounded-full bg-tertiary" />
                  {{ shipment.status === 'delivered' ? 'Delivered & Verified' : 'Awaiting Delivery & Sign-off' }}
                </span>
              </div>

              <div class="mb-4 rounded-lg border border-outline-variant bg-surface-low p-2">
                <div class="flex items-start gap-2">
                  <MIcon name="domain" class="mt-0.5 text-[20px] text-outline" />
                  <div>
                    <div class="text-label-sm uppercase text-on-surface-variant">Designated Consignee Warehouse</div>
                    <div class="mt-0.5 font-body-md font-semibold text-on-surface">{{ shipment.consigneeName }}</div>
                    <div class="mt-0.5 text-body-sm text-on-surface-variant">{{ shipment.consigneeAddress }}</div>
                  </div>
                </div>
              </div>

              <div class="mb-4 flex items-center justify-between rounded-lg border border-outline-variant bg-surface-low p-2">
                <div class="flex items-center gap-2">
                  <div class="flex size-8 items-center justify-center rounded-full border border-secondary/30 bg-secondary-container/20 text-xs font-bold text-secondary">
                    {{ shipment.receiver.split(' ').map((part) => part[0]).slice(0, 2).join('') }}
                  </div>
                  <div>
                    <div class="text-body-sm font-semibold text-on-surface">{{ shipment.receiver }}</div>
                    <div class="text-label-sm text-on-surface-variant">{{ shipment.receiverRole }} • Badge ID: {{ shipment.receiverBadge }}</div>
                  </div>
                </div>
                <div class="text-right">
                  <span class="inline-flex items-center gap-1 rounded border border-outline-variant bg-surface-container-high px-2 py-0.5 text-label-sm text-on-surface-variant">
                    <MIcon name="badge" class="text-[14px] text-tertiary" />
                    Photo ID Required
                  </span>
                </div>
              </div>

              <div v-if="shipment.status === 'delivered'" class="mb-4 rounded-xl border border-primary/30 bg-primary-container/10 p-4 text-center">
                <MIcon name="verified" class="text-[32px] text-primary" />
                <div class="mt-2 text-label-md font-semibold text-primary">Signed &amp; verified</div>
                <p class="mt-1 text-body-sm text-on-surface-variant">
                  POD manifest synced from driver handheld on Oct 29 • 14:47 UTC. Seal images and inspection report archived.
                </p>
              </div>
              <div v-else class="group mb-4 cursor-pointer rounded-xl border-2 border-dashed border-outline-variant bg-surface-low/40 p-4 text-center transition-colors hover:border-primary/60">
                <div class="flex flex-col items-center justify-center">
                  <div class="mb-2 flex size-10 items-center justify-center rounded-full bg-surface-container-highest text-on-surface-variant transition-colors group-hover:bg-primary-container/20 group-hover:text-primary">
                    <MIcon name="draw" class="text-[24px]" />
                  </div>
                  <div class="text-label-md font-semibold text-on-surface transition-colors group-hover:text-primary">Digital Signature Capture &amp; Inspection Upload Zone</div>
                  <p class="mt-1 max-w-sm text-body-sm text-on-surface-variant">
                    Driver handheld terminal will sync signed bill of lading, seal verification photos, and cargo inspection report upon handover.
                  </p>
                  <div class="mt-2 flex items-center gap-4 text-label-sm text-outline">
                    <span class="flex items-center gap-1"><MIcon name="check" class="text-[14px]" /> e-Sign Ready</span>
                    <span class="flex items-center gap-1"><MIcon name="check" class="text-[14px]" /> Seal Image Upload</span>
                    <span class="flex items-center gap-1"><MIcon name="check" class="text-[14px]" /> Geofenced Validation</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="flex items-center justify-between border-t border-outline-variant pt-2">
              <div class="text-label-sm text-on-surface-variant">Pre-clearance valid for next 48 hours</div>
              <button class="flex items-center gap-2 rounded-lg border border-primary px-4 py-2 text-label-md font-semibold text-primary transition-colors duration-150 hover:bg-primary/10 active:scale-[0.98]">
                <MIcon name="fingerprint" class="text-[18px]" />
                <span>Pre-Authorize Digital Handover</span>
              </button>
            </div>
          </section>
        </div>
      </div>
    </template>

    <div v-else class="mx-auto flex min-h-[60vh] max-w-lg flex-col items-center justify-center px-6 text-center">
      <div class="flex size-14 items-center justify-center rounded-full border border-outline-variant bg-surface-container text-primary">
        <MIcon name="search_off" class="text-[28px]" />
      </div>
      <h1 class="mt-4 font-heading text-headline-md font-bold text-on-surface">Shipment &ldquo;{{ route.params.id }}&rdquo; not found</h1>
      <p class="mt-2 text-body-md text-on-surface-variant">
        Double-check the tracking number or waybill reference, or browse your active shipments below.
      </p>
      <div class="mt-6 flex items-center gap-2">
        <Button class="gap-1 rounded-lg bg-primary-container font-label-md font-bold text-on-primary-container hover:bg-primary" as-child>
          <NuxtLink to="/shipments">
            <MIcon name="local_shipping" class="text-[18px]" />
            My Shipments
          </NuxtLink>
        </Button>
        <Button variant="outline" class="rounded-lg border border-outline-variant text-on-surface" as-child>
          <NuxtLink to="/">
            Back to Overview
          </NuxtLink>
        </Button>
      </div>
    </div>
  </main>
</template>
