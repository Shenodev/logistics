<script setup lang="ts">
import { invoiceStatusTone, type Invoice } from '~~/app/data/billing'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

interface Props {
  invoices: Invoice[]
}

defineProps<Props>()

const refundedCount = computed(() => 0) // placeholder to avoid unused, actual computed in template via filter if needed
</script>

<template>
  <div class="overflow-hidden rounded-xl border border-outline-variant bg-surface-container">
    <div class="flex flex-col gap-2 border-b border-outline-variant p-4 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex items-center gap-2">
        <MIcon name="receipt_long" class="text-[22px] text-primary" />
        <h2 class="font-heading text-headline-sm font-semibold text-on-surface">Invoice History</h2>
        <span class="rounded-full bg-amber-500/10 px-2 py-0.5 text-label-sm font-semibold text-amber-400">
          {{ invoices.filter((i) => i.status === 'refunded').length }} Refunded
        </span>
      </div>
      <span class="text-label-sm text-on-surface-variant">{{ invoices.length }} invoices · FY 2024 · Read-only</span>
    </div>

    <!-- Refunded legend -->
    <div class="flex flex-wrap items-center gap-2 border-b border-outline-variant bg-amber-500/5 px-4 py-2 text-label-sm">
      <span class="flex items-center gap-1.5 text-amber-400">
        <MIcon name="undo" class="text-[16px]" />
        <span class="font-semibold">Refunded</span>
      </span>
      <span class="text-on-surface-variant">— cancelled orders refunded to Visa via Stripe. Highlighted in amber.</span>
    </div>

    <Table>
      <TableHeader>
        <TableRow class="border-outline-variant hover:bg-transparent">
          <TableHead class="text-label-sm uppercase tracking-wider text-on-surface-variant">Invoice #</TableHead>
          <TableHead class="text-label-sm uppercase tracking-wider text-on-surface-variant">Date</TableHead>
          <TableHead class="text-label-sm uppercase tracking-wider text-on-surface-variant">Description</TableHead>
          <TableHead class="text-right text-label-sm uppercase tracking-wider text-on-surface-variant">Amount</TableHead>
          <TableHead class="text-label-sm uppercase tracking-wider text-on-surface-variant">Status</TableHead>
          <TableHead class="text-right text-label-sm uppercase tracking-wider text-on-surface-variant">Receipt</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow
          v-for="invoice in invoices"
          :key="invoice.id"
          class="border-outline-variant/60 transition-colors hover:bg-surface-container-high"
          :class="invoice.status === 'refunded' ? 'bg-amber-500/5 hover:bg-amber-500/10 border-l-2 border-l-amber-500' : ''"
        >
          <TableCell class="font-telemetry-numeric font-medium text-on-surface">{{ invoice.id }}</TableCell>
          <TableCell class="text-body-sm text-on-surface-variant">{{ invoice.date }}</TableCell>
          <TableCell class="max-w-[280px] truncate text-body-sm text-on-surface">{{ invoice.description }}</TableCell>
          <TableCell class="text-right font-telemetry-numeric font-semibold" :class="invoice.status === 'refunded' ? 'text-amber-400' : 'text-on-surface'">
            {{ invoice.amount }}
          </TableCell>
          <TableCell>
            <span class="inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-label-sm font-semibold capitalize" :class="invoiceStatusTone[invoice.status]">
              <MIcon v-if="invoice.status === 'refunded'" name="undo" class="text-[14px]" />
              <MIcon v-else-if="invoice.status === 'paid'" name="check_circle" class="text-[14px]" />
              <MIcon v-else-if="invoice.status === 'overdue'" name="warning" class="text-[14px]" />
              <MIcon v-else name="schedule" class="text-[14px]" />
              {{ invoice.status }}
            </span>
          </TableCell>
          <TableCell class="text-right">
            <button class="inline-flex items-center gap-1 text-label-sm font-medium text-primary transition-colors hover:text-on-surface">
              <MIcon name="picture_as_pdf" class="text-[16px]" />
              PDF
            </button>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>

    <div class="border-t border-outline-variant bg-surface-low px-4 py-2.5 text-label-sm text-on-surface-variant">
      <span class="font-medium text-on-surface">No payments are taken here.</span> Invoices are logged automatically from your freight activity. Refunds for cancelled orders are issued by Admin to your Visa via Stripe and appear as <span class="font-semibold text-amber-400">Refunded</span>.
    </div>
  </div>
</template>
