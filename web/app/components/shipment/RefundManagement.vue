<script setup lang="ts">
import type { Shipment } from '~~/app/data/shipments'
import { isRefundEligible, isRefunded } from '~~/app/data/shipments'

interface Props {
  shipment: Shipment
  isAdmin: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{ refundIssued: [refundId: string] }>()

const { issueRefund } = useShipments()

const eligible = computed(() => isRefundEligible(props.shipment))
const refunded = computed(() => isRefunded(props.shipment))
const isCancelled = computed(() => props.shipment.status === 'cancelled')

const showConfirm = ref(false)
const processing = ref(false)
const error = ref<string | null>(null)

async function confirmRefund() {
  if (!eligible.value || !props.isAdmin || processing.value) return
  processing.value = true
  error.value = null
  // Simulate Stripe API latency
  await new Promise((r) => setTimeout(r, 700))
  const res = issueRefund(props.shipment.id)
  processing.value = false
  if (!res.ok || !res.refundId) {
    error.value = 'Refund failed — order not eligible or already refunded.'
    return
  }
  showConfirm.value = false
  emit('refundIssued', res.refundId)
}

function formatCard() {
  return 'Visa •••• 4242'
}
</script>

<template>
  <section class="rounded-xl border bg-surface-container p-6" :class="refunded ? 'border-emerald-500/30' : isCancelled ? 'border-amber-500/30' : 'border-outline-variant'">
    <div class="flex items-center gap-2 border-b pb-3" :class="refunded ? 'border-emerald-500/20' : isCancelled ? 'border-amber-500/20' : 'border-outline-variant'">
      <div class="flex size-8 items-center justify-center rounded-lg" :class="refunded ? 'bg-emerald-500/10 text-emerald-400' : isCancelled ? 'bg-amber-500/10 text-amber-400' : 'bg-surface-low text-on-surface-variant'">
        <MIcon :name="refunded ? 'check_circle' : isCancelled ? 'payments' : 'block'" class="text-[20px]" />
      </div>
      <div>
        <h2 class="font-heading text-headline-sm font-semibold" :class="refunded ? 'text-emerald-400' : isCancelled ? 'text-amber-400' : 'text-on-surface'">Refund Management</h2>
        <p class="text-body-sm" :class="refunded ? 'text-emerald-400/80' : 'text-on-surface-variant'">
          <span v-if="refunded">Visa refund issued via Stripe — financial action completed</span>
          <span v-else-if="isCancelled && isAdmin && eligible">Eligible cancelled order — admin can issue Visa refund</span>
          <span v-else-if="isCancelled && !isAdmin && eligible">Cancelled — flagged for admin Visa refund</span>
          <span v-else-if="isCancelled && refunded">Refund completed</span>
          <span v-else>Refunds are only available for orders cancelled in Stage 1 (Order Received)</span>
        </p>
      </div>
      <span v-if="refunded" class="ml-auto rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1 text-label-sm font-semibold text-emerald-400">Refunded</span>
      <span v-else-if="isCancelled && eligible" class="ml-auto rounded-full border border-amber-500/30 bg-amber-500/10 px-2.5 py-1 text-label-sm font-semibold text-amber-400">Pending Refund</span>
      <span v-else-if="isCancelled" class="ml-auto rounded-full border border-outline-variant bg-surface-low px-2 py-0.5 text-label-sm text-on-surface-variant">Cancelled</span>
    </div>

    <!-- Cancelled details -->
    <div v-if="isCancelled" class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
      <div class="rounded-lg border border-outline-variant bg-surface-low p-3">
        <div class="text-label-sm uppercase tracking-wider text-on-surface-variant">Invoice</div>
        <div class="mt-1 font-mono text-body-md font-semibold text-on-surface">{{ shipment.invoiceId }}</div>
        <div class="text-label-sm text-on-surface-variant">Order {{ shipment.id }}</div>
      </div>
      <div class="rounded-lg border border-outline-variant bg-surface-low p-3">
        <div class="text-label-sm uppercase tracking-wider text-on-surface-variant">Refund Amount</div>
        <div class="mt-1 font-telemetry-numeric text-xl font-bold" :class="refunded ? 'text-emerald-400' : 'text-amber-400'">{{ shipment.refundAmount }}</div>
        <div class="text-label-sm text-on-surface-variant">To {{ formatCard() }}</div>
      </div>
      <div class="rounded-lg border bg-surface-low p-3" :class="refunded ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-amber-500/30 bg-amber-500/5'">
        <div class="text-label-sm uppercase tracking-wider" :class="refunded ? 'text-emerald-400' : 'text-amber-400'">Refund Status</div>
        <div class="mt-1 font-label-md font-semibold" :class="refunded ? 'text-emerald-400' : 'text-amber-400'">
          {{ refunded ? 'Refunded via Stripe' : 'Pending admin action' }}
        </div>
        <div class="text-label-sm text-on-surface-variant">Cancelled {{ shipment.cancelledAt }}</div>
      </div>
    </div>

    <!-- Financial action -->
    <div class="mt-4 flex flex-col gap-3">
      <div v-if="refunded" class="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 flex items-center gap-3">
        <MIcon name="verified" class="text-[20px] text-emerald-400" />
        <div class="flex-1">
          <div class="text-label-md font-semibold text-emerald-400">Visa refund completed</div>
          <div class="font-mono text-body-sm text-on-surface-variant">Refund ID: {{ shipment.refundId }} • {{ formatCard() }} • Stripe</div>
        </div>
        <span class="rounded bg-emerald-500 px-2 py-1 text-label-sm font-bold text-white">Stripe</span>
      </div>

      <div v-else-if="isCancelled && eligible && isAdmin" class="rounded-lg border border-amber-500/30 bg-amber-500/5 p-3">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="flex items-center gap-2">
            <MIcon name="credit_card" class="text-[20px] text-amber-400" />
            <div>
              <div class="font-label-md font-semibold text-on-surface">Issue Visa Refund</div>
              <div class="text-body-sm text-on-surface-variant">Refund {{ shipment.refundAmount }} to {{ formatCard() }} via Stripe — eligible cancelled order</div>
            </div>
          </div>
          <button
            class="inline-flex items-center gap-1.5 rounded-lg bg-amber-500 px-4 py-2 text-label-md font-bold text-white hover:bg-amber-600 active:scale-[0.98] disabled:opacity-50"
            :disabled="processing"
            @click="showConfirm = true"
          >
            <MIcon name="payments" class="text-[18px]" />
            {{ processing ? 'Processing…' : 'Issue Visa Refund' }}
          </button>
        </div>
        <p v-if="error" class="mt-2 text-body-sm text-destructive">{{ error }}</p>
      </div>

      <div v-else-if="isCancelled && eligible && !isAdmin" class="rounded-lg border border-amber-500/30 bg-amber-500/5 p-3 flex items-center gap-2">
        <MIcon name="hourglass_top" class="text-[20px] text-amber-400" />
        <span class="text-body-sm text-on-surface-variant"><strong class="text-on-surface">Pending admin refund</strong> — your order was cancelled in Stage 1 and is queued for Visa refund via Stripe. An admin will issue it shortly. No action required.</span>
      </div>

      <div v-else-if="!isCancelled" class="rounded-lg border border-outline-variant bg-surface-low p-3 flex items-center gap-2">
        <MIcon name="info" class="text-[18px] text-outline" />
        <span class="text-body-sm text-on-surface-variant">Refund management is only available after an order is <strong class="text-on-surface">Cancelled</strong> in Stage 1 (Order Received). Active shipments must be cancelled first.</span>
      </div>
    </div>

    <!-- Confirm modal -->
    <div v-if="showConfirm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm" @click.self="showConfirm = false">
      <div class="w-full max-w-md rounded-xl border border-outline-variant bg-surface-container p-6 shadow-xl">
        <div class="flex items-start gap-3">
          <div class="flex size-10 shrink-0 items-center justify-center rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <MIcon name="payments" class="text-[22px]" />
          </div>
          <div>
            <h3 class="font-heading text-headline-sm font-semibold text-on-surface">Issue Visa refund for {{ shipment.id }}?</h3>
            <p class="mt-1 text-body-sm leading-relaxed text-on-surface-variant">
              You are about to refund <strong class="text-on-surface">{{ shipment.refundAmount }}</strong> to <strong class="text-on-surface">{{ formatCard() }}</strong> via Stripe. This financial action is for the eligible cancelled order <strong class="text-on-surface">{{ shipment.id }}</strong> (Invoice {{ shipment.invoiceId }}) and cannot be undone.
            </p>
            <div class="mt-3 rounded-lg border border-outline-variant bg-surface-low p-2.5 text-label-sm">
              <div class="flex justify-between"><span class="text-on-surface-variant">Order</span><span class="font-mono font-semibold text-on-surface">{{ shipment.id }}</span></div>
              <div class="flex justify-between"><span class="text-on-surface-variant">Invoice</span><span class="font-mono text-on-surface">{{ shipment.invoiceId }}</span></div>
              <div class="flex justify-between"><span class="text-on-surface-variant">Refund to</span><span class="text-on-surface">{{ formatCard() }} via Stripe</span></div>
              <div class="flex justify-between"><span class="text-on-surface-variant">Amount</span><span class="font-bold text-amber-400">{{ shipment.refundAmount }}</span></div>
            </div>
          </div>
        </div>
        <div class="mt-6 flex items-center justify-end gap-2">
          <button class="rounded-lg px-4 py-2 text-label-md font-medium text-on-surface-variant hover:bg-surface-container-high" :disabled="processing" @click="showConfirm = false">Cancel</button>
          <button class="inline-flex items-center gap-1.5 rounded-lg bg-amber-500 px-4 py-2 text-label-md font-bold text-white hover:bg-amber-600 disabled:opacity-50" :disabled="processing" @click="confirmRefund">
            <MIcon v-if="!processing" name="check_circle" class="text-[18px]" />
            {{ processing ? 'Issuing…' : 'Confirm — Issue Refund' }}
          </button>
        </div>
        <p v-if="error" class="mt-3 text-body-sm text-destructive">{{ error }}</p>
        <p class="mt-2 text-center text-label-sm text-outline">Financial action • Admin only • Stripe</p>
      </div>
    </div>
  </section>
</template>
