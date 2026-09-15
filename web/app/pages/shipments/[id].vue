<script setup lang="ts">
import { STATUS_FLOW } from '~~/app/data/shipments'

definePageMeta({ layout: 'user', middleware: 'auth' })

const route = useRoute()
const { get: findShipment } = useShipments()

const shipment = computed(() => findShipment(String(route.params.id ?? '')))

useSeoMeta({
  title: () => shipment.value ? `${shipment.value.id} · Tracking` : 'Shipment not found',
  description: () => shipment.value
    ? `Live tracking and chain of custody for ${shipment.value.id} — ${shipment.value.origin} to ${shipment.value.destination}.`
    : 'The requested shipment could not be found.',
})

const statusLabel = computed(() => shipment.value ? STATUS_FLOW[shipment.value.status].label : '')

const activeIndex = computed(() => (shipment.value ? STATUS_FLOW[shipment.value.status].index : 0))
</script>

<template>
  <main class="bg-background">
    <template v-if="shipment">
      <div class="mx-auto max-w-[1600px] space-y-6 p-6">
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

            <div class="flex items-center gap-2 self-start lg:self-center">
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

        <!-- 3. Milestone timeline -->
        <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
          <div class="mb-6 flex items-center justify-between">
            <div>
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Consignment Progress &amp; Chain of Custody</h2>
              <p class="mt-0.5 text-body-sm text-on-surface-variant">Automated timestamp verification recorded on carrier ledger</p>
            </div>
            <div class="flex items-center gap-2">
              <span class="rounded border border-outline-variant bg-surface-container-high px-2.5 py-1 text-label-sm text-on-surface-variant">
                Current Phase: <strong class="font-medium text-primary">{{ shipment.currentPhase }}</strong>
              </span>
            </div>
          </div>

          <div class="relative py-2">
            <div class="absolute top-[26px] right-[5%] left-[5%] z-0 h-0.5 -translate-y-1/2 bg-outline-variant">
              <div class="h-full bg-primary" :style="{ width: `${shipment.timelineFillPct}%` }" />
            </div>

            <div class="relative z-10 grid grid-cols-5 gap-2 text-center">
              <div
                v-for="milestone in shipment.milestones"
                :key="milestone.label"
                class="flex flex-col items-center"
                :class="milestone.state === 'upcoming' ? 'opacity-40' : milestone.state === 'active' ? '' : 'opacity-100'"
              >
                <div v-if="milestone.state === 'active'" class="relative mb-2">
                  <div class="flex size-12 items-center justify-center rounded-full border-2 border-primary bg-primary-container font-bold text-on-primary-container">
                    <MIcon :name="milestone.icon" class="text-[24px]" />
                  </div>
                  <span class="radar-pulse pointer-events-none absolute -inset-1 rounded-full border border-primary" />
                </div>
                <div
                  v-else
                  class="mb-2 flex size-12 items-center justify-center rounded-full border-2 bg-surface-container-highest"
                  :class="milestone.state === 'done' ? 'border-primary text-primary' : 'border-outline-variant bg-surface-low text-outline'"
                >
                  <MIcon :name="milestone.icon" class="text-[22px]" />
                </div>
                <div class="text-label-md font-semibold" :class="milestone.state === 'active' ? 'font-bold text-primary' : 'text-on-surface'">
                  {{ milestone.label }}
                </div>
                <div class="mt-0.5 text-body-sm" :class="milestone.state === 'active' ? 'font-medium text-on-surface' : 'text-on-surface-variant'">
                  {{ milestone.detail }}
                </div>
                <div class="mt-0.5 font-mono text-label-sm text-outline">{{ milestone.time }}</div>
              </div>
            </div>
          </div>
        </section>

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