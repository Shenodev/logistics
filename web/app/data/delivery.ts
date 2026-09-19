import type { Shipment } from '~~/app/data/shipments'
import { shipments } from '~~/app/data/shipments'

export interface IncomingOrder {
  shipment: Shipment
  payout: string
  distance: string
  expiresIn: string
  priority: 'Standard' | 'Express' | 'Urgent'
}

export const incomingSeed: IncomingOrder[] = [
  {
    shipment: shipments.find((s) => s.id === 'SHP-10002-ORD')!,
    payout: '$47.50',
    distance: '12.4 km',
    expiresIn: '4:32',
    priority: 'Express',
  },
  {
    shipment: shipments.find((s) => s.id === 'SHP-10003-ORD')!,
    payout: '$28.00',
    distance: '6.8 km',
    expiresIn: '3:15',
    priority: 'Urgent',
  },
  {
    shipment: shipments.find((s) => s.id === 'SHP-10001-ORD')!,
    payout: '$124.00',
    distance: '18.2 km',
    expiresIn: '5:00',
    priority: 'Standard',
  },
]

export const driverStats = {
  earningsToday: '$214.80',
  deliveriesToday: 6,
  acceptanceRate: '96%',
  onlineHours: '4h 22m',
}
