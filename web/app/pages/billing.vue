<script setup lang="ts">
import { billingSummary, invoices, savedCards } from '~~/app/data/billing'

definePageMeta({ layout: 'user', middleware: 'auth' })

useSeoMeta({
  title: 'Billing & Invoices',
  description: 'Monitor your freight spend — invoices, payment methods, and automatic settlement at ShenoFlow.',
})

function downloadStatement() {
  if (!import.meta.client) return
  const rows = [
    ['Invoice #', 'Date', 'Description', 'Amount', 'Status'],
    ...invoices.map((invoice) => [invoice.id, invoice.date, invoice.description, invoice.amount, invoice.status]),
  ]
  const csv = '\uFEFF' + rows.map((row) => row.map((cell) => `"${cell}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'shenoflow-statement.csv'
  link.click()
  URL.revokeObjectURL(url)
}

const brandLabel: Record<string, string> = {
  visa: 'Visa',
  mastercard: 'Mastercard',
  amex: 'Amex',
  discover: 'Discover',
}
</script>

<template>
  <main class="bg-background">
    <div class="mx-auto max-w-[1600px] space-y-6 p-6">
      <!-- Header -->
      <section class="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <div class="flex items-center gap-2 text-body-sm text-on-surface-variant">
            <span class="font-label-md uppercase tracking-wider text-on-surface-variant">Global Freight Portal</span>
            <span class="text-outline-variant">/</span>
            <span class="text-primary font-medium">Billing</span>
          </div>
          <h1 class="mt-1 font-heading text-headline-lg font-bold tracking-tight text-on-surface">Billing &amp; Invoices</h1>
          <p class="text-body-sm text-on-surface-variant">Past invoices and settlement history — no manual payment required</p>
        </div>
        <Button class="gap-1.5 rounded-lg bg-secondary-container px-4 py-2 font-label-md font-semibold text-on-secondary-container hover:opacity-90" size="sm" @click="downloadStatement">
          <MIcon name="download" class="text-[18px]" />
          Download Statement (CSV)
        </Button>
      </section>

      <!-- Passive notice -->
      <div class="flex items-start gap-2 rounded-xl border border-primary/20 bg-primary-container/10 px-4 py-3 text-body-sm">
        <MIcon name="info" class="mt-0.5 text-[18px] text-primary" />
        <p class="leading-relaxed text-on-surface-variant">
          <span class="font-semibold text-on-surface">No payments are taken here.</span>
          Invoices are generated automatically from your freight activity. Refunds for orders cancelled in Stage 1 are issued by an Admin back to your Visa via Stripe and appear below as <span class="font-semibold text-amber-400">Refunded</span>.
        </p>
      </div>

      <!-- Summary row — passive -->
      <section aria-label="Billing summary" class="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
          <p class="text-label-sm uppercase tracking-wider text-on-surface-variant">Outstanding Balance</p>
          <p class="mt-1 font-heading font-telemetry-numeric text-3xl font-bold text-on-surface">{{ billingSummary.outstanding }}</p>
          <p class="mt-1 text-body-sm text-on-surface-variant">{{ billingSummary.outstandingNote }}</p>
        </div>
        <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
          <p class="text-label-sm uppercase tracking-wider text-on-surface-variant">Paid This Month</p>
          <p class="mt-1 font-heading font-telemetry-numeric text-3xl font-bold text-primary">{{ billingSummary.paidThisMonth }}</p>
          <p class="mt-1 text-body-sm text-on-surface-variant">{{ billingSummary.paidNote }}</p>
        </div>
        <div class="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
          <p class="flex items-center gap-1.5 text-label-sm uppercase tracking-wider text-amber-400">
            <MIcon name="undo" class="text-[14px]" />
            Refunded to Visa
          </p>
          <p class="mt-1 font-heading font-telemetry-numeric text-3xl font-bold text-amber-400">{{ billingSummary.refundedTotal }}</p>
          <p class="mt-1 text-body-sm text-on-surface-variant">{{ billingSummary.refundedNote }}</p>
        </div>
      </section>

      <!-- Payment methods — read-only -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <section class="rounded-xl border border-outline-variant bg-surface-container p-6 lg:col-span-8">
          <div class="flex items-center justify-between border-b border-outline-variant pb-3">
            <div class="flex items-center gap-2">
              <MIcon name="credit_card" class="text-[22px] text-primary" />
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Payment Methods on File</h2>
            </div>
            <span class="rounded-lg border border-outline-variant bg-surface-container-high px-2 py-0.5 text-label-sm text-on-surface-variant">
              Reference only · Secured by <span class="font-semibold text-primary">Stripe</span>
            </span>
          </div>

          <p class="mt-3 rounded-lg border border-outline-variant bg-surface-low px-3 py-2 text-body-sm leading-relaxed text-on-surface-variant">
            Cards are listed for reference and for refunds. No manual payment is taken in this portal — settlement is automatic. To update a card, contact support.
          </p>

          <ul class="mt-3 divide-y divide-outline-variant/60">
            <li v-for="card in savedCards" :key="card.id" class="flex items-center justify-between gap-3 py-3">
              <div class="flex items-center gap-3">
                <div class="flex size-10 items-center justify-center rounded-lg border border-outline-variant bg-surface-low text-primary">
                  <MIcon :name="card.brand === 'visa' ? 'contactless' : card.brand === 'mastercard' ? 'credit_card' : 'credit_card'" class="text-[20px]" />
                </div>
                <div>
                  <div class="flex items-center gap-2">
                    <span class="font-label-md font-semibold text-on-surface">{{ brandLabel[card.brand] ?? card.brand.toUpperCase() }}</span>
                    <span class="font-telemetry-numeric text-on-surface">•••• {{ card.last4 }}</span>
                    <span v-if="card.isDefault" class="rounded border border-primary/30 bg-primary-container/10 px-1.5 py-0.5 text-label-sm font-semibold text-primary">Default for refunds</span>
                  </div>
                  <p class="mt-0.5 text-label-sm text-on-surface-variant">Expires {{ card.exp }}</p>
                </div>
              </div>
              <span class="rounded-lg bg-surface-low px-2 py-1 text-label-sm text-on-surface-variant">Read-only</span>
            </li>
          </ul>

          <p class="mt-3 rounded-lg border border-outline-variant bg-surface-low px-3 py-2 text-label-sm leading-relaxed text-on-surface-variant">
            Reference mode — Stripe Elements disabled. Set <code class="font-mono text-primary">NUXT_PUBLIC_STRIPE_PK</code> for live admin refund processing.
          </p>
        </section>

        <!-- Settlement Profile — passive -->
        <aside class="flex flex-col justify-between rounded-xl border border-outline-variant bg-surface-container p-6 lg:col-span-4">
          <div>
            <div class="flex items-center gap-2">
              <MIcon name="autorenew" class="text-[22px] text-secondary" />
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Settlement Profile</h2>
            </div>
            <p class="mt-2 text-body-sm leading-relaxed text-on-surface-variant">
              Automatic settlement charges your default card for all <strong class="text-on-surface">open invoices</strong> on <strong class="text-on-surface">{{ billingSummary.nextBatch }}</strong>. One consolidated batch — no per-invoice action needed.
            </p>
            <div class="mt-4 space-y-2">
              <div class="flex items-center justify-between rounded-lg border border-outline-variant bg-surface-low p-2.5">
                <span class="text-label-md text-on-surface-variant">Net 15 terms</span>
                <span class="text-label-sm font-semibold text-primary">Active</span>
              </div>
              <div class="flex items-center justify-between rounded-lg border border-outline-variant bg-surface-low p-2.5">
                <span class="text-label-md text-on-surface-variant">Default card</span>
                <span class="font-telemetry-numeric text-label-sm text-on-surface">{{ savedCards.find((card) => card.isDefault)?.brand.toUpperCase() }} •••• {{ savedCards.find((card) => card.isDefault)?.last4 }}</span>
              </div>
              <div class="flex items-center justify-between rounded-lg border border-amber-500/20 bg-amber-500/5 p-2.5">
                <span class="text-label-md text-on-surface-variant">Refunds</span>
                <span class="text-label-sm font-semibold text-amber-400">Admin → Visa via Stripe</span>
              </div>
            </div>
          </div>
          <div class="mt-4 rounded-lg border border-tertiary-container/30 bg-tertiary-container/10 p-3 text-label-sm text-on-surface-variant">
            <span class="flex items-center gap-1.5 font-semibold text-tertiary">
              <MIcon name="schedule_send" class="text-[16px]" />
              Early settlement bonus
            </span>
            <p class="mt-1">Paying invoices before the batch date unlocks a 1.5% tariff credit applied to your next statement.</p>
          </div>
        </aside>
      </div>

      <!-- Invoices — shadcn Data Table -->
      <BillingInvoiceTable :invoices="invoices" />
    </div>
  </main>
</template>
