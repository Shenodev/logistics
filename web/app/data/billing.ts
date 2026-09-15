export type InvoiceStatus = 'paid' | 'open' | 'overdue'

export interface Invoice {
  id: string
  date: string
  description: string
  amount: string
  status: InvoiceStatus
}

export const invoices: Invoice[] = [
  { id: 'INV-2024-1187', date: 'Nov 12, 2024', description: 'Ocean Freight · SHP-89421-US', amount: '$4,820.00', status: 'open' },
  { id: 'INV-2024-1182', date: 'Nov 05, 2024', description: 'Air Cargo · SHP-90214-DE', amount: '$3,150.00', status: 'paid' },
  { id: 'INV-2024-1176', date: 'Oct 29, 2024', description: 'Intermodal · MSKU-993214-4', amount: '$6,740.00', status: 'paid' },
  { id: 'INV-2024-1171', date: 'Oct 22, 2024', description: 'Ground Fleet · SHP-88201-US', amount: '$1,180.00', status: 'paid' },
  { id: 'INV-2024-1165', date: 'Oct 15, 2024', description: 'Ocean Freight · SHP-77219-SG', amount: '$9,460.00', status: 'paid' },
  { id: 'INV-2024-1158', date: 'Oct 08, 2024', description: 'Intermodal LCL · SHP-74812-AU', amount: '$2,940.00', status: 'overdue' },
  { id: 'INV-2024-1141', date: 'Sep 25, 2024', description: 'Air Cargo Express · SHP-69033-FR', amount: '$5,620.00', status: 'paid' },
  { id: 'INV-2024-1132', date: 'Sep 12, 2024', description: 'Temp Controlled · MSKU-45520-BR', amount: '$7,890.00', status: 'paid' },
]

export interface SavedCard {
  id: string
  brand: string
  last4: string
  exp: string
  isDefault: boolean
}

export const savedCards: SavedCard[] = [
  { id: 'pm_business_visa', brand: 'visa', last4: '4242', exp: '12 / 28', isDefault: true },
  { id: 'pm_business_mc', brand: 'mastercard', last4: '5100', exp: '08 / 27', isDefault: false },
]

export const billingSummary = {
  outstanding: '$4,820.00',
  outstandingNote: '2 invoices due before Nov 28, 2024',
  paidThisMonth: '$42,150.00',
  paidNote: '19 invoices reconciled this month',
  nextBatch: 'Nov 28, 2024',
}

export const invoiceStatusTone: Record<InvoiceStatus, string> = {
  paid: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
  open: 'border-tertiary-container/30 bg-tertiary-container/15 text-tertiary',
  overdue: 'border-destructive/30 bg-destructive/10 text-destructive',
}