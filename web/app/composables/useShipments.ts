import { reactive } from 'vue'
import type { Shipment } from '~/data/shipments'
import { shipments as seed } from '~/data/shipments'

const state = reactive<{ items: Shipment[] }>({ items: [...seed] })

export function useShipments() {
  const list = computed(() => state.items)

  function get(id: string): Shipment | undefined {
    const key = id.trim().toUpperCase()
    return state.items.find((item) => item.id === key)
  }

  function add(shipment: Shipment): void {
    state.items.unshift(shipment)
  }

  return { list, get, add }
}