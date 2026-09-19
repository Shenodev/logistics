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

  function remove(id: string): boolean {
    const key = id.trim().toUpperCase()
    const idx = state.items.findIndex((item) => item.id === key)
    if (idx === -1) return false
    state.items.splice(idx, 1)
    return true
  }

  function cancelOrder(id: string): boolean {
    // Business rule: cancellation is only a soft remove in UI;
    // backend would flag for Stripe refund. Here we remove from the reactive list.
    return remove(id)
  }

  return { list, get, remove, cancelOrder }
}