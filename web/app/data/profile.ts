export interface BillingAddress {
  id: string
  label: string
  line1: string
  line2: string
  city: string
  zip: string
  country: string
  isDefault: boolean
}

export const billingAddresses: BillingAddress[] = [
  {
    id: 'addr_hq',
    label: 'Headquarters',
    line1: '1000 Dockside Avenue',
    line2: 'Suite 400, Pier 9',
    city: 'Newark, NJ',
    zip: '07114',
    country: 'United States',
    isDefault: true,
  },
  {
    id: 'addr_nl',
    label: 'Rotterdam Office',
    line1: 'Waalhaven Z.z. 8',
    line2: 'Port of Rotterdam',
    city: 'Rotterdam',
    zip: '3089 JH',
    country: 'Netherlands',
    isDefault: false,
  },
  {
    id: 'addr_sg',
    label: 'APAC Hub',
    line1: '18 Pasir Panjang Road',
    line2: '#07-28 Mapletree HQ',
    city: 'Singapore',
    zip: '117420',
    country: 'Singapore',
    isDefault: false,
  },
]

export interface NotificationPref {
  id: string
  title: string
  description: string
  enabled: boolean
}

export const notificationPrefs: NotificationPref[] = [
  { id: 'status', title: 'Shipment status alerts', description: 'Milestone updates for tracked shipments', enabled: true },
  { id: 'delay', title: 'Delay & exception warnings', description: 'Earliest possible flag on route deviations', enabled: true },
  { id: 'billing', title: 'Invoice & payment alerts', description: 'New invoices, settlement batch reminders', enabled: false },
  { id: 'customs', title: 'Customs clearance notices', description: 'Document-feed and inspection requests', enabled: true },
]

export const timezones = [
  'America/New_York (UTC-05:00)',
  'Europe/Amsterdam (UTC+01:00)',
  'Asia/Singapore (UTC+08:00)',
]

export const activeSessions = [
  { device: 'Chrome · Windows', location: 'Newark, NJ, US', current: true },
  { device: 'Safari · iPhone 15', location: 'Newark, NJ, US', current: false },
  { device: 'Edge · Windows', location: 'Amsterdam, NL', current: false },
]