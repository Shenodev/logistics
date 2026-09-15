<script setup lang="ts">
import { billingSummary, invoices, invoiceStatusTone, savedCards, type SavedCard } from '~~/app/data/billing'

definePageMeta({ layout: 'user', middleware: 'auth' })

useSeoMeta({
  title: 'Billing & Invoices',
  description: 'Monitor your freight spend — invoices, payment methods, and automatic settlement at ShenoFlow.',
})

const cards = ref<SavedCard[]>([...savedCards])
const autoPay = ref(true)
const addOpen = ref(false)
const savingCard = ref(false)
const cardError = ref<string | null>(null)
const cardSuccess = ref<string | null>(null)
const cardHostRef = ref<HTMLDivElement | null>(null)

const stripe = useStripe()

function openAddCard() {
  addOpen.value = true
  cardError.value = null
  cardSuccess.value = null
  if (stripe.enabled.value && !stripe.ready.value) {
    stripe.init().then(() => {
      if (stripe.card.value && cardHostRef.value) {
        nextTick(() => stripe.mountCard(cardHostRef.value))
      }
    })
  }
  nextTick(() => stripe.mountCard(cardHostRef.value))
}

function closeAddCard() {
  addOpen.value = false
  stripe.unmountCard()
  cardError.value = null
  cardSuccess.value = null
}

async function submitCard() {
  if (!stripe.stripe.value || !stripe.card.value) {
    cardError.value = 'Stripe is not ready yet. Please try again.'
    return
  }
  savingCard.value = true
  cardError.value = null
  cardSuccess.value = null
  try {
    const { paymentMethod, error } = await stripe.stripe.value.createPaymentMethod({
      type: 'card',
      card: stripe.card.value,
    })
    if (error) {
      cardError.value = error.message
      return
    }
    const cardData = paymentMethod.card
    cards.value.unshift({
      id: paymentMethod.id,
      brand: cardData.brand,
      last4: cardData.last4 ?? '0000',
      exp: `${String(cardData.exp_month).padStart(2, '0')} / ${String(cardData.exp_year).slice(-2)}`,
      isDefault: cards.value.length === 0,
    })
    cardSuccess.value = `Card ${cardData.brand?.toUpperCase()} •••• ${cardData.last4} added in Stripe test mode.`
    addOpen.value = false
    stripe.unmountCard()
  }
  catch (error) {
    cardError.value = error instanceof Error ? error.message : 'Unable to save card.'
  }
  finally {
    savingCard.value = false
  }
}

function setDefault(id: string) {
  cards.value = cards.value.map((card) => ({ ...card, isDefault: card.id === id }))
}

function removeCard(id: string) {
  if (cards.value.length <= 1) {
    cardError.value = 'You must keep at least one payment method on file.'
    return
  }
  const removing = cards.value.find((card) => card.id === id)
  cards.value = cards.value.filter((card) => card.id !== id)
  if (removing?.isDefault) {
    const next = cards.value[0]
    if (next) setDefault(next.id)
  }
}

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
          <p class="text-body-sm text-on-surface-variant">Settlement batches, invoice history, and payment methods</p>
        </div>
        <Button class="gap-1.5 rounded-lg bg-secondary-container px-4 py-2 font-label-md font-semibold text-on-secondary-container hover:opacity-90" size="sm" @click="downloadStatement">
          <MIcon name="download" class="text-[18px]" />
          Download Statement (CSV)
        </Button>
      </section>

      <!-- Summary row -->
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
        <div class="flex items-center justify-between rounded-xl border border-outline-variant bg-surface-container p-4">
          <div>
            <p class="text-label-sm uppercase tracking-wider text-on-surface-variant">Automatic Payments</p>
            <p class="mt-1 font-heading text-headline-sm font-semibold text-on-surface">{{ autoPay ? 'Enabled' : 'Paused' }}</p>
            <p class="mt-1 text-body-sm text-on-surface-variant">Settle open invoices on {{ billingSummary.nextBatch }}</p>
          </div>
          <Switch v-model:checked="autoPay" aria-label="Toggle automatic payments" />
        </div>
      </section>

      <!-- Payment methods -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <section class="rounded-xl border border-outline-variant bg-surface-container p-6 lg:col-span-8">
          <div class="flex items-center justify-between border-b border-outline-variant pb-3">
            <div class="flex items-center gap-2">
              <MIcon name="credit_card" class="text-[22px] text-primary" />
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Payment Methods</h2>
            </div>
            <span class="rounded-lg border border-outline-variant bg-surface-container-high px-2 py-0.5 text-label-sm text-on-surface-variant">
              Secured by <span class="font-semibold text-primary">Stripe</span>
            </span>
          </div>

          <p v-if="cardError" class="mt-3 rounded-lg border border-destructive/30 bg-destructive/10 p-2.5 text-body-sm text-destructive">{{ cardError }}</p>
          <p v-if="cardSuccess" class="mt-3 rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-2.5 text-body-sm text-emerald-400">{{ cardSuccess }}</p>

          <ul class="divide-y divide-outline-variant/60">
            <li v-for="card in cards" :key="card.id" class="flex items-center justify-between gap-3 py-3">
              <div class="flex items-center gap-3">
                <div class="flex size-10 items-center justify-center rounded-lg border border-outline-variant bg-surface-low text-primary">
                  <MIcon :name="card.brand === 'visa' ? 'contactless' : card.brand === 'mastercard' ? 'credit_card' : 'credit_card'" class="text-[20px]" />
                </div>
                <div>
                  <div class="flex items-center gap-2">
                    <span class="font-label-md font-semibold text-on-surface">{{ brandLabel[card.brand] ?? card.brand.toUpperCase() }}</span>
                    <span class="font-telemetry-numeric text-on-surface">•••• {{ card.last4 }}</span>
                    <span v-if="card.isDefault" class="rounded border border-primary/30 bg-primary-container/10 px-1.5 py-0.5 text-label-sm font-semibold text-primary">Default</span>
                  </div>
                  <p class="mt-0.5 text-label-sm text-on-surface-variant">Expires {{ card.exp }}</p>
                </div>
              </div>
              <div class="flex items-center gap-1">
                <button
                  v-if="!card.isDefault"
                  class="rounded-lg px-2 py-1 text-label-sm text-on-surface-variant transition-colors hover:bg-surface-container-high hover:text-primary"
                  @click="setDefault(card.id)"
                >
                  Set default
                </button>
                <button class="rounded-lg px-2 py-1 text-label-sm text-on-surface-variant transition-colors hover:bg-surface-container-high hover:text-destructive" @click="removeCard(card.id)">
                  Remove
                </button>
              </div>
            </li>
          </ul>

          <!-- Stripe card entry -->
          <template v-if="stripe.enabled.value">
            <button
              v-if="!addOpen"
              class="mt-2 flex w-full items-center justify-center gap-1.5 rounded-lg border border-dashed border-outline-variant py-3 text-label-md font-semibold text-primary transition-colors hover:border-primary/60 hover:bg-surface-container-high"
              @click="openAddCard"
            >
              <MIcon name="add" class="text-[18px]" />
              Add Payment Method
            </button>
            <div v-else class="mt-3 space-y-3">
              <div class="rounded-lg border border-outline-variant bg-surface p-3">
                <div ref="cardHostRef" class="min-h-12" />
              </div>
              <p class="text-label-sm text-on-surface-variant">
                Test mode — use card number 4242 4242 4242 4242 with any future expiry.
              </p>
              <div class="flex items-center justify-end gap-2">
                <Button variant="ghost" class="text-label-md text-on-surface-variant hover:bg-surface-container-high" @click="closeAddCard">
                  Cancel
                </Button>
                <Button class="gap-1 rounded-lg bg-primary-container font-label-md font-bold text-on-primary-container hover:bg-primary" :disabled="savingCard || !stripe.ready.value" @click="submitCard">
                  <MIcon name="lock" class="text-[16px]" />
                  {{ savingCard ? 'Saving…' : 'Save Card' }}
                </Button>
              </div>
            </div>
          </template>
          <div v-else class="mt-3 rounded-lg border border-outline-variant bg-surface-low p-3 text-body-sm text-on-surface-variant">
            Connect a Stripe publishable key via <code class="font-mono text-primary">NUXT_PUBLIC_STRIPE_PK</code> to enter new cards with Stripe&nbsp;Elements. Existing payment methods are listed above for reference.
          </div>
        </section>

        <!-- Auto-pay details -->
        <aside class="flex flex-col justify-between rounded-xl border border-outline-variant bg-surface-container p-6 lg:col-span-4">
          <div>
            <div class="flex items-center gap-2">
              <MIcon name="autorenew" class="text-[22px] text-secondary" />
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Settlement Profile</h2>
            </div>
            <p class="mt-2 text-body-sm leading-relaxed text-on-surface-variant">
              Automatic settlement charges your default card for all <strong class="text-on-surface">open invoices</strong> on <strong class="text-on-surface">{{ billingSummary.nextBatch }}</strong>. One consolidated batch, no per-invoice friction.
            </p>
            <div class="mt-4 space-y-2">
              <div class="flex items-center justify-between rounded-lg border border-outline-variant bg-surface-low p-2.5">
                <span class="text-label-md text-on-surface-variant">Net 15 terms</span>
                <span class="text-label-sm font-semibold text-primary">Active</span>
              </div>
              <div class="flex items-center justify-between rounded-lg border border-outline-variant bg-surface-low p-2.5">
                <span class="text-label-md text-on-surface-variant">Default card</span>
                <span class="font-telemetry-numeric text-label-sm text-on-surface">{{ cards.find((card) => card.isDefault)?.brand.toUpperCase() }} •••• {{ cards.find((card) => card.isDefault)?.last4 }}</span>
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

      <!-- Invoices table -->
      <section class="overflow-hidden rounded-xl border border-outline-variant bg-surface-container">
        <div class="flex items-center justify-between border-b border-outline-variant p-4">
          <div class="flex items-center gap-2">
            <MIcon name="receipt_long" class="text-[22px] text-primary" />
            <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Invoice History</h2>
          </div>
          <span class="text-label-sm text-on-surface-variant">{{ invoices.length }} invoices · FY 2024</span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left">
            <thead>
              <tr class="border-b border-outline-variant text-label-sm uppercase tracking-wider text-on-surface-variant">
                <th class="px-4 py-3 font-semibold">Invoice #</th>
                <th class="px-4 py-3 font-semibold">Date</th>
                <th class="px-4 py-3 font-semibold">Description</th>
                <th class="px-4 py-3 text-right font-semibold">Amount</th>
                <th class="px-4 py-3 font-semibold">Status</th>
                <th class="px-4 py-3 text-right font-semibold">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-outline-variant/60">
              <tr v-for="invoice in invoices" :key="invoice.id" class="transition-colors hover:bg-surface-container-high">
                <td class="px-4 py-3 font-telemetry-numeric text-on-surface">{{ invoice.id }}</td>
                <td class="px-4 py-3 text-body-sm text-on-surface-variant">{{ invoice.date }}</td>
                <td class="px-4 py-3 text-body-sm text-on-surface">{{ invoice.description }}</td>
                <td class="px-4 py-3 text-right font-telemetry-numeric text-on-surface">{{ invoice.amount }}</td>
                <td class="px-4 py-3">
                  <span class="rounded border px-2 py-0.5 text-label-sm font-semibold capitalize" :class="invoiceStatusTone[invoice.status]">
                    {{ invoice.status }}
                  </span>
                </td>
                <td class="px-4 py-3 text-right">
                  <button class="inline-flex items-center gap-1 text-label-sm font-medium text-primary transition-colors hover:text-on-surface">
                    <MIcon name="picture_as_pdf" class="text-[16px]" />
                    PDF
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </main>
</template>