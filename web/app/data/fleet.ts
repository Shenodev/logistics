export type DutyStatus = 'en_route' | 'on_break' | 'off_duty' | 'compliance'

export interface FleetDriver {
  id: string
  name: string
  cdl: string
  status: DutyStatus
  statusLabel: string
  email: string
  phone: string
  vehicle: string
  plate: string
  route: string
  routeMeta: string
  hosHours: number
  hosMax: number
  performance: number
  tier: string
  sparkline: number[]
  complianceWarning?: string
}

export const fleetRoster: FleetDriver[] = [
  {
    id: '#DRV-1049',
    name: 'Marcus Vance',
    cdl: 'CDL-A',
    status: 'en_route',
    statusLabel: 'On-Duty / En Route',
    email: 'm.vance@orbital.net',
    phone: '+1 (555) 392-4819',
    vehicle: '5 Ton Box Truck',
    plate: 'NY-784-KLP',
    route: 'ORD-4081 → Midtown Depot',
    routeMeta: 'ETA 14:15 EST (On Schedule)',
    hosHours: 5.4,
    hosMax: 8.0,
    performance: 98.4,
    tier: 'Top 5% Tier',
    sparkline: [15, 12, 14, 8, 10, 4],
  },
  {
    id: '#DRV-2204',
    name: 'Sarah Jenkins',
    cdl: 'CDL-A',
    status: 'on_break',
    statusLabel: 'On Break (32m remaining)',
    email: 's.jenkins@orbital.net',
    phone: '+1 (555) 744-1903',
    vehicle: 'Heavy Freight Tractor',
    plate: 'IL-991-XTR',
    route: 'CHI-West → Rest Haven #04',
    routeMeta: 'Mandatory DOT 30m Rest',
    hosHours: 3.8,
    hosMax: 8.0,
    performance: 94.2,
    tier: 'Fleet Standard',
    sparkline: [6, 8, 5, 12, 9, 7],
  },
  {
    id: '#DRV-3108',
    name: 'David Kalu',
    cdl: 'CDL-B',
    status: 'off_duty',
    statusLabel: 'Off-Duty / Scheduled 18:00',
    email: 'd.kalu@orbital.net',
    phone: '+1 (555) 602-9931',
    vehicle: 'Sprinter EV 350',
    plate: 'NJ-404-EVX',
    route: 'Standby → Depot Newark-01',
    routeMeta: 'Shift starts in 3h 40m',
    hosHours: 0.0,
    hosMax: 8.0,
    performance: 96.0,
    tier: 'Reliable Shift',
    sparkline: [10, 12, 9, 11, 10, 10],
  },
  {
    id: '#DRV-4419',
    name: 'Elena Rostova',
    cdl: 'CDL-A',
    status: 'compliance',
    statusLabel: 'On-Duty / En Route',
    email: 'e.rostova@orbital.net',
    phone: '+49 (171) 882-9014',
    vehicle: 'Volvo FH Electric 40T',
    plate: 'FRA-882-EU',
    route: 'FRA-Cargo → Stuttgart Orbital',
    routeMeta: 'ETA 16:40 CET (+12m Customs Delay)',
    hosHours: 7.2,
    hosMax: 8.0,
    performance: 89.0,
    tier: 'Route Disruption',
    sparkline: [5, 9, 11, 13, 15, 16],
    complianceWarning: 'MED CERT DUE',
  },
  {
    id: '#DRV-5091',
    name: 'Tariq Mansour',
    cdl: 'CDL-A',
    status: 'en_route',
    statusLabel: 'On-Duty / En Route',
    email: 't.mansour@orbital.net',
    phone: '+1 (555) 819-2045',
    vehicle: 'Sprinter High-Cube',
    plate: 'TX-501-MNS',
    route: 'AUS-Gateway → San Antonio Express',
    routeMeta: 'ETA 15:30 CST (Fast Transit)',
    hosHours: 2.1,
    hosMax: 8.0,
    performance: 99.1,
    tier: 'Fleet Leader',
    sparkline: [14, 11, 9, 5, 4, 3],
  },
  {
    id: '#DRV-8821',
    name: 'Chloe Bennett',
    cdl: 'CDL-B',
    status: 'on_break',
    statusLabel: 'On Break (18m remaining)',
    email: 'c.bennett@orbital.net',
    phone: '+1 (555) 210-3371',
    vehicle: 'Sprinter Van',
    plate: 'CA-221-BNT',
    route: 'LAX Depot → Rest Area 12',
    routeMeta: 'DOT Break • 18m left',
    hosHours: 4.2,
    hosMax: 8.0,
    performance: 92.7,
    tier: 'Standard',
    sparkline: [9, 7, 8, 6, 9, 11],
  },
]

export const analyticsKpis = [
  { label: 'Gross Fleet Revenue', value: '$1.42M', change: '+14.2% MoM', note: 'vs $1.24M scheduled baseline', icon: 'payments', tone: 'primary' },
  { label: 'Avg Cost Per Freight Mile', value: '$2.18', change: '-4.1% vs target', note: 'Optimal margin threshold: <$2.25', icon: 'straighten', tone: 'secondary' },
  { label: 'Fleet Utilization Rate', value: '91.4%', change: '+2.8%', note: '148 of 162 orbital carriers active', icon: 'alt_route', tone: 'tertiary' },
  { label: 'Mean On-Time Fulfillment', value: '98.7%', change: 'Optimal', note: '99.2% required on Tier-1 SLA', icon: 'verified', tone: 'primary' },
]

export const financialPerformance = [
  { week: 'Week 1', label: 'Oct 1-7', revenue: 290, cost: 192, margin: 12 },
  { week: 'Week 2', label: 'Oct 8-14', revenue: 335, cost: 208, margin: 15 },
  { week: 'Week 3', label: 'Oct 15-21', revenue: 360, cost: 224, margin: 18 },
  { week: 'Week 4', label: 'Oct 22-28', revenue: 435, cost: 236, margin: 22 },
]

export const heatmapData = [
  { day: 'Mon', values: [12, 34, 71, 88, 54, 18] },
  { day: 'Tue', values: [10, 42, 85, 91, 62, 21] },
  { day: 'Wed', values: [15, 50, 89, 94, 78, 25] },
  { day: 'Thu', values: [18, 58, 92, 99, 96, 32] },
  { day: 'Fri', values: [14, 45, 82, 87, 65, 28] },
  { day: 'Sat', values: [8, 18, 36, 42, 30, 12] },
  { day: 'Sun', values: [5, 12, 22, 28, 25, 9] },
]
export const heatmapHours = ['00-04', '04-08', '08-12', '12-16', '16-20', '20-24']
