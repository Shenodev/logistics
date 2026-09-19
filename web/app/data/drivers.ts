export interface Driver {
  id: string
  name: string
  vehicle: string
  plate: string
  capacity: number // max orders
  status: 'en_route' | 'depot' | 'available'
}

export const drivers: Driver[] = [
  { id: 'TR-402', name: 'Marcus Vance', vehicle: '5 Ton Box Truck', plate: 'TR-402', capacity: 6, status: 'en_route' },
  { id: 'VN-108', name: 'Sarah Jenkins', vehicle: 'High Roof Sprinter', plate: 'VN-108', capacity: 5, status: 'available' },
  { id: 'TR-510', name: 'David Kalu', vehicle: '10 Ton Freight Rig', plate: 'TR-510', capacity: 5, status: 'en_route' },
  { id: 'VN-304', name: 'Aisha Cohen', vehicle: 'Sprinter Van', plate: 'VN-304', capacity: 4, status: 'depot' },
]
