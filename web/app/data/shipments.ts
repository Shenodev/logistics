export type ShipmentStatus = 'order_received' | 'booked' | 'in_transit' | 'out_for_delivery' | 'delivered' | 'cancelled'

/**
 * Stage 1 canonical status is `order_received` ("Order Received" / "استلام الطلب").
 * `booked` is kept as a legacy alias for backward compatibility — both map to Stage 1.
 */
export function isCancellableStatus(status: ShipmentStatus): boolean {
  return status === 'order_received' || status === 'booked'
}

export function canCancelOrder(shipment: { status: ShipmentStatus }): boolean {
  return isCancellableStatus(shipment.status)
}

export function isRefundEligible(shipment: Pick<Shipment, 'status' | 'refundStatus'>): boolean {
  return shipment.status === 'cancelled' && shipment.refundStatus === 'pending'
}

export function isRefunded(shipment: Pick<Shipment, 'refundStatus'>): boolean {
  return shipment.refundStatus === 'refunded'
}

export interface Milestone {
  label: string
  detail: string
  time: string
  state: 'done' | 'active' | 'upcoming'
  icon: string
}

export interface MapWaypoint {
  label: string
  kind: 'origin' | 'current' | 'checkpoint' | 'destination'
}

export type DeliveryStatus = 'assigned' | 'picked_up' | 'on_the_way' | 'delivered'

export interface Shipment {
  id: string
  mode: string
  status: ShipmentStatus
  priority: string
  origin: string
  originCode: string
  destination: string
  destinationCode: string
  bookedAt: string
  masterAwb: string
  eta: string
  etaTz: string
  carrier: string
  lat: string
  lon: string
  spd: string
  alt: string
  nextCheckpoint: string
  nextCheckpointIn: string
  weather: string
  cargoTemp: string
  waypoints: MapWaypoint[]
  grossWeight: string
  grossWeightLbs: string
  totalVolume: string
  totalVolumeCu: string
  pallets: string
  palletType: string
  containerSpec: string
  containerSpecDetail: string
  dimensions: string
  tare: string
  hsCode: string
  hsDesc: string
  handling: Array<{ icon: string; label: string; kind: 'primary' | 'tertiary' | 'neutral' }>
  consigneeName: string
  consigneeAddress: string
  receiver: string
  receiverRole: string
  receiverBadge: string
  milestones: Milestone[]
  currentPhase: string
  timelineFillPct: number
  // financial / cancellation
  cancelledAt?: string | null
  cancelledBy?: string | null
  refundStatus?: 'none' | 'pending' | 'refunded'
  refundId?: string | null
  refundAmount?: string
  invoiceId?: string
  // delivery
  customerPhone: string
  restaurantName: string
  restaurantAddress: string
  deliveryStatus: DeliveryStatus
  deliveryUpdatedAt?: string | null
}

export const STATUS_FLOW: Record<ShipmentStatus, { label: string; index: number }> = {
  order_received: { label: 'Order Received', index: 0 },
  booked: { label: 'Order Received', index: 0 },
  in_transit: { label: 'In Transit', index: 2 },
  out_for_delivery: { label: 'Out for Delivery', index: 3 },
  delivered: { label: 'Delivered', index: 4 },
  cancelled: { label: 'Cancelled', index: 0 },
}

const STEP_LABELS = [
  { label: 'Order Received', icon: 'receipt_long' },
  { label: 'Picked Up & Origin Hub', icon: 'check' },
  { label: 'In Transit', icon: 'airplanemode_active' },
  { label: 'Out for Delivery', icon: 'local_shipping' },
  { label: 'Delivered', icon: 'verified' },
]

const STEP_DETAILS: Record<ShipmentStatus, { detail: string[]; time: string[] }> = {
  order_received: {
    detail: ['Booking Confirmed', 'Carrier Assigned', 'Expected Soon', 'Upcoming', 'Consignee Sign-off'],
    time: ['Oct 24 • 14:32', 'Oct 25 • 08:15', 'Est. Oct 28', 'Est. Oct 29 • 09:00', 'Est. Oct 29 • 16:30'],
  },
  booked: {
    detail: ['Booking Confirmed', 'Carrier Assigned', 'Expected Soon', 'Upcoming', 'Consignee Sign-off'],
    time: ['Oct 24 • 14:32', 'Oct 25 • 08:15', 'Est. Oct 28', 'Est. Oct 29 • 09:00', 'Est. Oct 29 • 16:30'],
  },
  cancelled: {
    detail: ['Order Cancelled — Refund Pending', 'Carrier Released', 'Refund Queued', 'Awaiting Admin Visa Refund', 'Closed'],
    time: ['Oct 24 • 14:32', 'Oct 24 • 14:35', 'Oct 24 • 14:35', 'Pending Admin Action', '—'],
  },
  in_transit: {
    detail: ['Completed', 'Rotterdam Port Depot', 'Expected Oct 28', 'Upcoming', 'Consignee Sign-off'],
    time: ['Oct 24 • 14:32', 'Oct 25 • 08:15', 'Oct 26 • 06:10', 'Est. Oct 29 • 09:00', 'Est. Oct 29 • 16:30'],
  },
  out_for_delivery: {
    detail: ['Completed', 'Rotterdam Port Depot', 'Departed Origin Hub', 'ETA 09:00', 'Consignee Sign-off'],
    time: ['Oct 24 • 14:32', 'Oct 25 • 08:15', 'Oct 27 • 14:02', 'Est. Oct 29 • 09:00', 'Est. Oct 29 • 16:30'],
  },
  delivered: {
    detail: ['Completed', 'Rotterdam Port Depot', 'Departed Origin Hub', 'Final Mile Dispatch', 'Signed by Consignee'],
    time: ['Oct 24 • 14:32', 'Oct 25 • 08:15', 'Oct 27 • 14:02', 'Oct 29 • 09:12', 'Jun 30 • 14:47'],
  },
}

function milestonesFor(status: ShipmentStatus): Milestone[] {
  const idx = STATUS_FLOW[status].index
  return STEP_LABELS.map((step, i) => ({
    label: step.label,
    icon: step.icon,
    detail: STEP_DETAILS[status].detail[i],
    time: STEP_DETAILS[status].time[i],
    state: i < idx ? 'done' : i === idx ? 'active' : 'upcoming',
  }))
}

function timelineFillPct(status: ShipmentStatus): number {
  const idx = STATUS_FLOW[status].index
  return Math.round((idx / 4) * 100)
}

interface ShipmentSeed {
  id: string
  mode: string
  status: ShipmentStatus
  priority: string
  origin: string
  originCode: string
  destination: string
  destinationCode: string
  carrier: string
  eta: string
  nextCheckpoint: string
  nextCheckpointIn: string
  grossWeight: string
  grossWeightLbs: string
  totalVolume: string
  totalVolumeCu: string
  pallets: string
  palletType: string
  containerSpec: string
  containerSpecDetail: string
  dimensions: string
  tare: string
  hsCode: string
  hsDesc: string
  consigneeName: string
  consigneeAddress: string
  receiver: string
  receiverRole: string
  receiverBadge: string
}

const DEFAULT_HANDLING = [
  {
    icon: 'device_thermostat',
    label: 'Class 2 Temp Controlled (Ambient 15°C - 25°C)',
    kind: 'primary' as const,
  },
  {
    icon: 'warning',
    label: 'Fragile Integrated Electronics',
    kind: 'tertiary' as const,
  },
  {
    icon: 'layers_clear',
    label: 'Do Not Double Stack',
    kind: 'neutral' as const,
  },
]

function buildShipment(seed: ShipmentSeed & Partial<Pick<Shipment, 'cancelledAt' | 'cancelledBy' | 'refundStatus' | 'refundId' | 'refundAmount' | 'invoiceId' | 'customerPhone' | 'restaurantName' | 'restaurantAddress' | 'deliveryStatus' | 'deliveryUpdatedAt'>>): Shipment {
  const isCancelled = seed.status === 'cancelled'
  const digits = seed.id.replace(/\D/g, '').slice(-4).padStart(4, '0') || '0148'
  return {
    id: seed.id,
    mode: seed.mode,
    status: seed.status,
    priority: seed.priority,
    origin: seed.origin,
    originCode: seed.originCode,
    destination: seed.destination,
    destinationCode: seed.destinationCode,
    bookedAt: 'Oct 24, 2024 • 14:32 UTC',
    masterAwb: '724-81920194',
    eta: isCancelled ? 'Cancelled — refund pending' : seed.eta,
    etaTz: 'CDT',
    carrier: seed.carrier,
    lat: seed.id === 'SHP-89421-US' ? '48.219° N' : '41.500° N',
    lon: seed.id === 'SHP-89421-US' ? '34.810° W' : '72.100° W',
    spd: '480 kts',
    alt: '36,000 ft',
    nextCheckpoint: seed.nextCheckpoint,
    nextCheckpointIn: seed.nextCheckpointIn,
    weather: 'Clear skies • 4°C Ext',
    cargoTemp: 'Cargo Hold Temp: 18°C Stable (Regulated)',
    waypoints: [
      { label: `${seed.originCode} • ${seed.origin}`, kind: 'origin' },
      { label: 'FLIGHT ATLAS 921', kind: 'current' },
      { label: 'EWR (Transfer)', kind: 'checkpoint' },
      { label: `${seed.destinationCode} • ${seed.destination}`, kind: 'destination' },
    ],
    grossWeight: seed.grossWeight,
    grossWeightLbs: seed.grossWeightLbs,
    totalVolume: seed.totalVolume,
    totalVolumeCu: seed.totalVolumeCu,
    pallets: seed.pallets,
    palletType: seed.palletType,
    containerSpec: seed.containerSpec,
    containerSpecDetail: seed.containerSpecDetail,
    dimensions: seed.dimensions,
    tare: seed.tare,
    hsCode: seed.hsCode,
    hsDesc: seed.hsDesc,
    handling: DEFAULT_HANDLING,
    consigneeName: seed.consigneeName,
    consigneeAddress: seed.consigneeAddress,
    receiver: seed.receiver,
    receiverRole: seed.receiverRole,
    receiverBadge: seed.receiverBadge,
    milestones: milestonesFor(seed.status),
    currentPhase: STATUS_FLOW[seed.status].label,
    timelineFillPct: timelineFillPct(seed.status),
    cancelledAt: seed.cancelledAt ?? (isCancelled ? 'Oct 24, 2024 • 14:35 UTC' : null),
    cancelledBy: seed.cancelledBy ?? (isCancelled ? 'user@sheno.dev' : null),
    refundStatus: seed.refundStatus ?? (isCancelled ? 'pending' : 'none'),
    refundId: seed.refundId ?? null,
    refundAmount: seed.refundAmount ?? (isCancelled ? '$12,400.00' : '$0.00'),
    invoiceId: seed.invoiceId ?? `INV-2024-${seed.id.slice(-4)}`,
    customerPhone: seed.customerPhone ?? `+1 (212) 555-${digits}`,
    restaurantName: seed.restaurantName ?? `${seed.origin} Hub Kitchen`,
    restaurantAddress: seed.restaurantAddress ?? `${seed.origin}, ${seed.originCode} • Bay ${seed.id.slice(-2)} • Pickup Dock 4`,
    deliveryStatus: seed.deliveryStatus ?? (isCancelled ? 'assigned' : 'assigned'),
    deliveryUpdatedAt: seed.deliveryUpdatedAt ?? null,
  }
}

export const shipments: Shipment[] = [
  buildShipment({
    id: 'SHP-10001-ORD',
    mode: 'Ocean Freight',
    status: 'order_received',
    priority: 'Standard Freight',
    origin: 'Rotterdam',
    originCode: 'RTM',
    destination: 'Chicago',
    destinationCode: 'ORD',
    carrier: 'Carrier assignment pending',
    eta: 'TBD — awaiting carrier confirmation',
    nextCheckpoint: 'Order Received — awaiting pickup',
    nextCheckpointIn: 'TBD',
    grossWeight: '12,400 kg',
    grossWeightLbs: '27,337 lbs',
    totalVolume: '62.0 m³',
    totalVolumeCu: '2,189 cu ft',
    pallets: '18 Units',
    palletType: 'Euro Pallets (EPAL 1)',
    containerSpec: '40ft HC',
    containerSpecDetail: 'High Cube Intermodal',
    dimensions: "12.19m × 2.44m × 2.89m (40'0\" × 8'0\" × 9'6\")",
    tare: '3,980 kg (Standard Cor-Ten Steel)',
    hsCode: '8542.31',
    hsDesc: 'Electronic Integrated Circuits (Processors & Controllers)',
    consigneeName: 'Apex Global Distribution Center, Bay 14',
    consigneeAddress: '1040 Logistics Blvd, Bensenville, IL 60106, United States',
    receiver: 'Robert Chen',
    receiverRole: 'Lead Logistics Manager',
    receiverBadge: 'APX-9941',
  }),
  buildShipment({
    id: 'SHP-10002-ORD',
    mode: 'Intermodal',
    status: 'order_received',
    priority: 'Express Air & Intermodal',
    origin: 'Jersey City Port',
    originCode: 'JCP',
    destination: 'Brooklyn Terminal',
    destinationCode: 'BKL',
    carrier: 'Carrier assignment pending',
    eta: 'TBD — awaiting carrier confirmation',
    nextCheckpoint: 'Order Received — awaiting pickup',
    nextCheckpointIn: 'TBD',
    grossWeight: '1,200 kg',
    grossWeightLbs: '2,645 lbs',
    totalVolume: '18.5 m³',
    totalVolumeCu: '653 cu ft',
    pallets: '4 Units',
    palletType: 'Standard Pallets',
    containerSpec: '20ft',
    containerSpecDetail: 'General Freight',
    dimensions: "6.06m × 2.44m × 2.59m",
    tare: '2,280 kg',
    hsCode: '8473.30',
    hsDesc: 'General Freight — Palletized',
    consigneeName: 'Brooklyn Terminal Hub',
    consigneeAddress: '12 Harbor Way, Brooklyn, NY 11201, United States',
    receiver: 'Alex Rivera',
    receiverRole: 'Warehouse Lead',
    receiverBadge: 'BKL-201',
  }),
  buildShipment({
    id: 'SHP-10003-ORD',
    mode: 'Ground Fleet',
    status: 'order_received',
    priority: 'Standard Freight',
    origin: 'Newark Airport Hub',
    originCode: 'EWR',
    destination: 'Midtown Manhattan',
    destinationCode: 'MTM',
    carrier: 'Carrier assignment pending',
    eta: 'TBD — awaiting carrier confirmation',
    nextCheckpoint: 'Order Received — awaiting pickup',
    nextCheckpointIn: 'TBD',
    grossWeight: '280 kg',
    grossWeightLbs: '617 lbs',
    totalVolume: '4.2 m³',
    totalVolumeCu: '148 cu ft',
    pallets: '1 Unit',
    palletType: 'Small Pallet',
    containerSpec: 'LTL',
    containerSpecDetail: 'Cold Chain',
    dimensions: "1.2m × 0.8m × 1.0m",
    tare: '120 kg',
    hsCode: '3004.90',
    hsDesc: 'Pharma — Cold Chain 4°C',
    consigneeName: 'Midtown Medical Depot',
    consigneeAddress: '450 7th Ave, New York, NY 10123, United States',
    receiver: 'Dr. Maya Patel',
    receiverRole: 'Cold Chain Supervisor',
    receiverBadge: 'MTM-88',
  }),
  buildShipment({
    id: 'SHP-10004-CAN',
    mode: 'Ocean Freight',
    status: 'cancelled',
    priority: 'Standard Freight',
    origin: 'Rotterdam',
    originCode: 'RTM',
    destination: 'Chicago',
    destinationCode: 'ORD',
    carrier: 'Carrier released — order cancelled',
    eta: 'Cancelled — refund pending',
    nextCheckpoint: 'Order Received — cancelled by user',
    nextCheckpointIn: 'Refund pending admin action',
    grossWeight: '8,900 kg',
    grossWeightLbs: '19,621 lbs',
    totalVolume: '42.0 m³',
    totalVolumeCu: '1,483 cu ft',
    pallets: '12 Units',
    palletType: 'Euro Pallets (EPAL 1)',
    containerSpec: '40ft HC',
    containerSpecDetail: 'High Cube Intermodal',
    dimensions: "12.19m × 2.44m × 2.89m (40'0\" × 8'0\" × 9'6\")",
    tare: '3,980 kg (Standard Cor-Ten Steel)',
    hsCode: '8542.31',
    hsDesc: 'Electronic Integrated Circuits (Processors & Controllers)',
    consigneeName: 'Apex Global Distribution Center, Bay 14',
    consigneeAddress: '1040 Logistics Blvd, Bensenville, IL 60106, United States',
    receiver: 'Robert Chen',
    receiverRole: 'Lead Logistics Manager',
    receiverBadge: 'APX-9941',
    cancelledAt: 'Oct 24, 2024 • 14:35 UTC',
    cancelledBy: 'user@sheno.dev',
    refundStatus: 'pending',
    refundAmount: '$8,900.00',
    invoiceId: 'INV-2024-10004',
  }),
  buildShipment({
    id: 'SHP-89421-US',
    mode: 'Ocean Freight',
    status: 'in_transit',
    priority: 'Express Air & Intermodal',
    origin: 'Rotterdam',
    originCode: 'RTM',
    destination: "Chicago O'Hare",
    destinationCode: 'ORD',
    carrier: 'Atlas Air 921 / Maersk Intermodal',
    eta: 'Tomorrow, 11:30 AM',
    nextCheckpoint: 'Newark Transfer Hub (EWR)',
    nextCheckpointIn: '4 hrs 15 mins',
    grossWeight: '14,850 kg',
    grossWeightLbs: '32,738 lbs',
    totalVolume: '76.2 m³',
    totalVolumeCu: '2,691 cu ft',
    pallets: '22 Units',
    palletType: 'Euro Pallets (EPAL 1)',
    containerSpec: '40ft HC',
    containerSpecDetail: 'High Cube Intermodal',
    dimensions: "12.19m × 2.44m × 2.89m (40'0\" × 8'0\" × 9'6\")",
    tare: '3,980 kg (Standard Cor-Ten Steel)',
    hsCode: '8542.31',
    hsDesc: 'Electronic Integrated Circuits (Processors & Controllers)',
    consigneeName: 'Apex Global Distribution Center, Bay 14',
    consigneeAddress: '1040 Logistics Blvd, Bensenville, IL 60106, United States',
    receiver: 'Robert Chen',
    receiverRole: 'Lead Logistics Manager',
    receiverBadge: 'APX-9941',
  }),
  buildShipment({
    id: 'SHP-20940-NL',
    mode: 'Ocean Freight',
    status: 'in_transit',
    priority: 'Standard Container',
    origin: 'Rotterdam',
    originCode: 'RTM',
    destination: "Chicago O'Hare",
    destinationCode: 'ORD',
    carrier: 'Maersk Mc-Kinney Møller',
    eta: 'Wed, 2:00 PM',
    nextCheckpoint: 'Customs Hub 4',
    nextCheckpointIn: 'On hold review',
    grossWeight: '21,300 kg',
    grossWeightLbs: '46,958 lbs',
    totalVolume: '88.5 m³',
    totalVolumeCu: '3,125 cu ft',
    pallets: '26 Units',
    palletType: 'Standard Pallets',
    containerSpec: '40ft HC',
    containerSpecDetail: 'High Cube Intermodal',
    dimensions: "12.19m × 2.44m × 2.89m (40'0\" × 8'0\" × 9'6\")",
    tare: '3,980 kg (Standard Cor-Ten Steel)',
    hsCode: '8473.30',
    hsDesc: 'Parts & Accessories of Electronic Machines',
    consigneeName: 'Windy City Distribution LLC',
    consigneeAddress: '2301 Commerce Drive, Elk Grove Village, IL 60007, United States',
    receiver: 'Alma Reyes',
    receiverRole: 'Warehouse Supervisor',
    receiverBadge: 'WCD-2208',
  }),
  buildShipment({
    id: 'MSKU-993214-4',
    mode: 'Intermodal',
    status: 'out_for_delivery',
    priority: 'Reefer Intermodal',
    origin: 'Singapore',
    originCode: 'SIN',
    destination: 'Los Angeles',
    destinationCode: 'LAX',
    carrier: 'CMA CGM Jacques Saadé',
    eta: 'Today, 6:45 PM',
    nextCheckpoint: 'Los Angeles Gateway',
    nextCheckpointIn: 'Final mile dispatch',
    grossWeight: '11,040 kg',
    grossWeightLbs: '24,339 lbs',
    totalVolume: '54.8 m³',
    totalVolumeCu: '1,935 cu ft',
    pallets: '18 Units',
    palletType: 'GMP Compliant Pallets',
    containerSpec: '20ft RF',
    containerSpecDetail: 'Reefer / Temp Controlled',
    dimensions: "6.06m × 2.44m × 2.59m (20'0\" × 8'0\" × 8'6\")",
    tare: '2,280 kg (Reefer Cor-Ten Steel)',
    hsCode: '3004.90',
    hsDesc: 'Pharmaceutical Preparations (Refrigerated)',
    consigneeName: 'Pacific Biologics Warehouse',
    consigneeAddress: '4455 Goodwin Ave, Commerce, CA 90040, United States',
    receiver: 'Daniel Okafor',
    receiverRole: 'Pharma Logistics Lead',
    receiverBadge: 'PB-7712',
  }),
  buildShipment({
    id: 'SHP-90214-DE',
    mode: 'Air Cargo',
    status: 'in_transit',
    priority: 'Express Air Freight',
    origin: 'Frankfurt',
    originCode: 'FRA',
    destination: 'New York',
    destinationCode: 'JFK',
    carrier: 'Lufthansa Cargo / BA-2490',
    eta: 'Tomorrow, 7:15 AM',
    nextCheckpoint: 'John F. Kennedy Hub',
    nextCheckpointIn: '6 hrs 40 mins',
    grossWeight: '9,220 kg',
    grossWeightLbs: '20,326 lbs',
    totalVolume: '41.7 m³',
    totalVolumeCu: '1,472 cu ft',
    pallets: '14 Units',
    palletType: 'Airline ULD Pallets',
    containerSpec: 'AKE-ULD',
    containerSpecDetail: 'Air Cargo Unit Load Device',
    dimensions: '3.18m × 1.53m × 1.63m (ULD-6 Profile)',
    tare: '910 kg (Aluminum ULD Frame)',
    hsCode: '8471.80',
    hsDesc: 'Automatic Data Processing Machines & Units',
    consigneeName: 'Manhattan Tech Fulfillment',
    consigneeAddress: '900 Terminal Road, Jamaica, NY 11430, United States',
    receiver: 'Priya Nair',
    receiverRole: 'Operations Manager',
    receiverBadge: 'MTF-4409',
  }),
  buildShipment({
    id: 'SHP-77219-SG',
    mode: 'Intermodal',
    status: 'in_transit',
    priority: 'Rail & Sea Intermodal',
    origin: 'Singapore',
    originCode: 'SIN',
    destination: 'Sydney',
    destinationCode: 'SYD',
    carrier: 'CMA CGM Jacques Saadé',
    eta: 'Fri, 10:30 AM',
    nextCheckpoint: 'Sydney Intermodal Terminal',
    nextCheckpointIn: '38 hrs 05 mins',
    grossWeight: '17,660 kg',
    grossWeightLbs: '38,934 lbs',
    totalVolume: '66.4 m³',
    totalVolumeCu: '2,345 cu ft',
    pallets: '20 Units',
    palletType: 'EPAL 2 Pallets',
    containerSpec: '40ft HC',
    containerSpecDetail: 'High Cube Intermodal',
    dimensions: "12.19m × 2.44m × 2.89m (40'0\" × 8'0\" × 9'6\")",
    tare: '3,980 kg (Standard Cor-Ten Steel)',
    hsCode: '8802.11',
    hsDesc: 'Helicopters & Light Aircraft Parts',
    consigneeName: 'Harbourside Aviation Services',
    consigneeAddress: '12 Airport Drive, Mascot, NSW 2020, Australia',
    receiver: 'Thomas Whitfield',
    receiverRole: 'Aviation Parts Lead',
    receiverBadge: 'HAS-6620',
  }),
  buildShipment({
    id: 'SHP-88201-US',
    mode: 'Ground Fleet',
    status: 'out_for_delivery',
    priority: 'Final Mile Express',
    origin: 'Chicago',
    originCode: 'CHI',
    destination: 'Chicago Loop',
    destinationCode: 'CLP',
    carrier: 'Swift Logistics Driver #489',
    eta: 'Today, 4:30 PM',
    nextCheckpoint: 'Midwest Fulfillment Center 02',
    nextCheckpointIn: 'Final mile in progress',
    grossWeight: '2,410 kg',
    grossWeightLbs: '5,313 lbs',
    totalVolume: '12.8 m³',
    totalVolumeCu: '452 cu ft',
    pallets: '6 Units',
    palletType: 'Half-Pallets',
    containerSpec: 'LTL',
    containerSpecDetail: 'Less-than-Truckload',
    dimensions: '4.2m × 1.8m × 2.1m (Trailer Section)',
    tare: '540 kg (Box Truck)',
    hsCode: '9403.60',
    hsDesc: 'Furniture of Wood / Office Systems',
    consigneeName: 'Loop Office Interiors',
    consigneeAddress: '100 W Lake Street, Chicago, IL 60601, United States',
    receiver: 'Gary Simmons',
    receiverRole: 'Facilities Contact',
    receiverBadge: 'LOI-1822',
  }),
]

export function getShipment(id: string): Shipment | undefined {
  const normalized = id.trim().toUpperCase()
  return shipments.find((shipment) => shipment.id === normalized)
}

export type ActivityCategory = 'updates' | 'alerts' | 'customs' | 'delivered'

export interface ActivityItem {
  id: number
  shipmentId: string
  mode: string
  title: string
  location: string
  carrier: string
  time: string
  icon: string
  category: ActivityCategory
}

export const activityFeed: ActivityItem[] = [
  {
    id: 1,
    shipmentId: 'SHP-89421-US',
    mode: 'Ocean Freight',
    title: 'Cleared Rotterdam Customs Hub 4',
    location: 'Port of Rotterdam, NL',
    carrier: 'Maersk Mc-Kinney Møller',
    time: '12 mins ago',
    icon: 'verified_user',
    category: 'customs',
  },
  {
    id: 2,
    shipmentId: 'SHP-20940-NL',
    mode: 'Ocean Freight',
    title: 'Customs hold raised on manifest HS group 8473',
    location: 'Rotterdam Clearance Desk',
    carrier: 'Maersk Mc-Kinney Møller',
    time: '34 mins ago',
    icon: 'warning',
    category: 'alerts',
  },
  {
    id: 3,
    shipmentId: 'SHP-90214-DE',
    mode: 'Air Cargo',
    title: 'Loaded on Flight BA-2490 at Frankfurt Airport',
    location: 'Frankfurt Main (FRA), DE',
    carrier: 'Lufthansa Cargo / BA-2490',
    time: '48 mins ago',
    icon: 'flight_takeoff',
    category: 'updates',
  },
  {
    id: 4,
    shipmentId: 'SHP-77219-SG',
    mode: 'Intermodal',
    title: 'Departed Port of Singapore - Berth 12',
    location: 'PSA Singapore Terminal',
    carrier: 'CMA CGM Jacques Saadé',
    time: '2 hrs ago',
    icon: 'anchor',
    category: 'updates',
  },
  {
    id: 5,
    shipmentId: 'SHP-88201-US',
    mode: 'Ground Fleet',
    title: 'Out for Final Mile Delivery in Chicago, IL',
    location: 'Midwest Fulfillment Center 02',
    carrier: 'Swift Logistics Driver #489',
    time: '3 hrs ago',
    icon: 'local_shipping',
    category: 'delivered',
  },
]

export const recentQueries = ['SHP-89421-US', 'SHP-20940-NL', 'MSKU-993214-4']