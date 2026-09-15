<script setup lang="ts">
definePageMeta({ layout: 'user', middleware: 'auth' })

useSeoMeta({
  title: 'Support & Help Center',
  description: 'Contact the ShenoFlow operations desk, read the FAQs, and check carrier network status.',
})

const openFaq = ref<string | null>('track')

const faqs = [
  {
    id: 'track',
    question: 'How do I track a shipment in real time?',
    answer: 'Open My Shipments, select any active consignment, and the live radar vector telemetry surfaces ETA, next checkpoint, and vessel/handling status. You can also use the search bar in the top navigation with your booking reference (e.g. SHP-89421-US).',
  },
  {
    id: 'pod',
    question: 'When is a Proof of Delivery (POD) available?',
    answer: 'PODs are published within 4 hours of the delivered milestone. They appear in the shipment detail page under Proof of Delivery, including the consignee signature and scan timestamp.',
  },
  {
    id: 'billing',
    question: 'Why does my outstanding balance not match my latest invoice?',
    answer: 'The dashboard total aggregates open invoices plus pending cost-recovery adjustments that settle on the next batch date. Your Billing page lists every invoice individually with its status.',
  },
  {
    id: 'customs',
    question: 'Who handles customs documentation for my lanes?',
    answer: 'ShenoFlow files and manages customs documents for all enterprise lanes. Watch for clearance notifications under shipment milestones and your notification preferences.',
  },
]

const ticket = ref({ subject: '', category: 'Support', priority: 'Normal', message: '' })
const ticketSent = ref(false)

function submitTicket() {
  if (!ticket.value.subject || !ticket.value.message) return
  ticketSent.value = true
  ticket.value = { subject: '', category: 'Support', priority: 'Normal', message: '' }
  setTimeout(() => (ticketSent.value = false), 5000)
}

const services = [
  { name: 'Tracking API', status: 'Operational', tone: 'text-primary' },
  { name: 'Customs Gateway', status: 'Operational', tone: 'text-primary' },
  { name: 'Billing Engine', status: 'Operational', tone: 'text-primary' },
  { name: 'Carrier Mesh', status: 'Degraded', tone: 'text-tertiary' },
]

const guides = [
  { label: 'Quickstart: first shipment', icon: 'rocket_launch' },
  { label: 'Intermodal handoff guide', icon: 'sync_alt' },
  { label: 'Customs & compliance', icon: 'fact_check' },
  { label: 'Stripe billing walkthrough', icon: 'payments' },
]
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
            <span class="text-primary font-medium">Support</span>
          </div>
          <h1 class="mt-1 font-heading text-headline-lg font-bold tracking-tight text-on-surface">Support &amp; Help Center</h1>
          <p class="text-body-sm text-on-surface-variant">Talk to the operations desk, read the FAQs, or check carrier network status</p>
        </div>
        <span class="inline-flex items-center gap-2 self-start rounded-lg border border-primary/30 bg-surface-container px-3 py-2 text-label-sm font-semibold text-primary sm:self-auto">
          <MIcon name="bolt" class="text-[16px]" />
          Avg response &lt; 3 min
        </span>
      </section>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <!-- Left column -->
        <div class="space-y-6 lg:col-span-8">
          <!-- Contact / ticket -->
          <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
            <div class="flex items-center gap-2 border-b border-outline-variant pb-3">
              <MIcon name="support_agent" class="text-[22px] text-primary" />
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Contact the Operations Desk</h2>
            </div>

            <div class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
              <a class="rounded-lg border border-outline-variant bg-surface-low p-3 transition-colors hover:border-primary/50" href="mailto:support@sheno.dev">
                <p class="flex items-center gap-1.5 text-label-sm font-semibold text-on-surface">
                  <MIcon name="mail" class="text-[16px] text-primary" />
                  Email
                </p>
                <p class="mt-1 text-label-md text-on-surface-variant">support@sheno.dev</p>
              </a>
              <a class="rounded-lg border border-outline-variant bg-surface-low p-3 transition-colors hover:border-primary/50" href="tel:+12125550148">
                <p class="flex items-center gap-1.5 text-label-sm font-semibold text-on-surface">
                  <MIcon name="call" class="text-[16px] text-primary" />
                  Phone
                </p>
                <p class="mt-1 text-label-md text-on-surface-variant">+1 (212) 555-0148</p>
              </a>
              <div class="rounded-lg border border-outline-variant bg-surface-low p-3">
                <p class="flex items-center gap-1.5 text-label-sm font-semibold text-on-surface">
                  <MIcon name="chat" class="text-[16px] text-primary" />
                  Track &amp; trace
                </p>
                <p class="mt-1 text-label-md text-on-surface-variant">24/7 escalation lane</p>
              </div>
            </div>

            <p v-if="ticketSent" class="mt-4 rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-2.5 text-body-sm text-emerald-400">
              Ticket submitted. The operations desk will reply within 3 minutes during business hours.
            </p>

            <form class="mt-4 space-y-3" @submit.prevent="submitTicket">
              <input
                v-model="ticket.subject"
                placeholder="What do you need help with?"
                class="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface placeholder:text-outline focus:border-primary focus:outline-none"
              />
              <div class="grid grid-cols-2 gap-3">
                <select v-model="ticket.category" class="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface focus:border-primary focus:outline-none">
                  <option>Support</option>
                  <option>Customs</option>
                  <option>Billing</option>
                  <option>Carrier escalation</option>
                </select>
                <select v-model="ticket.priority" class="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface focus:border-primary focus:outline-none">
                  <option>Normal</option>
                  <option>High</option>
                  <option>Critical</option>
                </select>
              </div>
              <textarea
                v-model="ticket.message"
                rows="4"
                placeholder="Describe the issue — include shipment references where relevant."
                class="w-full resize-none rounded-lg border border-outline-variant bg-surface px-3 py-2 font-body-md text-body-md text-on-surface placeholder:text-outline focus:border-primary focus:outline-none"
              />
              <div class="flex items-center justify-end">
                <Button class="gap-1.5 rounded-lg bg-primary-container px-4 py-2 font-label-md font-bold text-on-primary-container hover:bg-primary" :disabled="!ticket.subject || !ticket.message">
                  <MIcon name="send" class="text-[18px]" />
                  Submit Ticket
                </Button>
              </div>
            </form>
          </section>

          <!-- FAQ -->
          <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
            <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Frequently Asked Questions</h2>
            <ul class="mt-3 space-y-2">
              <li v-for="faq in faqs" :key="faq.id" class="rounded-lg border border-outline-variant bg-surface-low">
                <button class="flex w-full items-center justify-between gap-3 p-3 text-left" @click="openFaq = openFaq === faq.id ? null : faq.id">
                  <span class="font-label-md font-semibold text-on-surface">{{ faq.question }}</span>
                  <MIcon :name="openFaq === faq.id ? 'expand_less' : 'expand_more'" class="shrink-0 text-[20px] text-on-surface-variant" />
                </button>
                <p v-if="openFaq === faq.id" class="px-3 pb-3 text-body-sm leading-relaxed text-on-surface-variant">
                  {{ faq.answer }}
                </p>
              </li>
            </ul>
          </section>
        </div>

        <!-- Right column -->
        <div class="space-y-6 lg:col-span-4">
          <!-- System status -->
          <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <MIcon name="radar" class="text-[22px] text-primary" />
                <h2 class="font-heading text-headline-sm font-semibold text-on-surface">System Status</h2>
              </div>
              <span class="rounded border border-primary/30 bg-primary-container/10 px-1.5 py-0.5 font-mono text-label-sm font-semibold text-primary">99.98%</span>
            </div>
            <ul class="mt-4 space-y-2">
              <li v-for="service in services" :key="service.name" class="flex items-center justify-between rounded-lg border border-outline-variant bg-surface-low px-3 py-2">
                <span class="text-label-md text-on-surface">{{ service.name }}</span>
                <span class="flex items-center gap-1.5 text-label-sm" :class="service.tone">
                  <span class="h-1.5 w-1.5 rounded-full bg-current" />
                  {{ service.status }}
                </span>
              </li>
            </ul>
          </section>

          <!-- Documentation -->
          <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
            <div class="flex items-center gap-2">
              <MIcon name="terminal" class="text-[22px] text-tertiary" />
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Documentation &amp; Guides</h2>
            </div>
            <ul class="mt-4 space-y-1">
              <li v-for="guide in guides" :key="guide.label">
                <a class="flex items-center justify-between rounded-lg px-2 py-1.5 text-label-md text-on-surface-variant transition-colors hover:bg-surface-container-high hover:text-on-surface" href="#">
                  <span class="flex items-center gap-2">
                    <MIcon :name="guide.icon" class="text-[18px] text-primary" />
                    {{ guide.label }}
                  </span>
                  <MIcon name="arrow_outward" class="text-[16px] text-outline" />
                </a>
              </li>
            </ul>
          </section>

          <!-- Escalation -->
          <section class="rounded-xl border border-outline-variant bg-surface-container p-6">
            <div class="flex items-center gap-2">
              <MIcon name="warning" class="text-[22px] text-secondary" />
              <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Escalation Path</h2>
            </div>
            <ol class="mt-4 space-y-2">
              <li class="flex items-center gap-2 text-body-sm text-on-surface-variant">
                <span class="rounded-full border border-outline-variant bg-surface-low px-2 py-0.5 font-mono text-label-sm text-primary">L1</span>
                Operations desk · instant
              </li>
              <li class="flex items-center gap-2 text-body-sm text-on-surface-variant">
                <span class="rounded-full border border-outline-variant bg-surface-low px-2 py-0.5 font-mono text-label-sm text-primary">L2</span>
                Lane specialist · 30 min
              </li>
              <li class="flex items-center gap-2 text-body-sm text-on-surface-variant">
                <span class="rounded-full border border-outline-variant bg-surface-low px-2 py-0.5 font-mono text-label-sm text-primary">L3</span>
                Enterprise TAM · same day
              </li>
            </ol>
          </section>
        </div>
      </div>
    </div>
  </main>
</template>