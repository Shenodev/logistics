import { reactive } from 'vue'
import type { DeliveryStatus, Shipment } from '~/data/shipments'
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
    const key = id.trim().toUpperCase()
    const item = state.items.find((s) => s.id === key)
    if (!item) return false
    if (item.status !== 'order_received' && item.status !== 'booked') return false
    if (item.status === 'cancelled') return false
    item.status = 'cancelled'
    item.cancelledAt = new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) + ' • ' + new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) + ' UTC'
    item.cancelledBy = 'current_user'
    item.refundStatus = 'pending'
    item.refundId = null
    item.eta = 'Cancelled — refund pending'
    item.nextCheckpoint = 'Order cancelled — awaiting admin Visa refund'
    item.nextCheckpointIn = 'Refund pending'
    item.currentPhase = 'Cancelled'
    item.timelineFillPct = 0
    // milestones will reflect cancelled on next computed if needed, but keep existing for now
    return true
  }

  function issueRefund(id: string): { ok: boolean; refundId?: string } {
    const key = id.trim().toUpperCase()
    const item = state.items.find((s) => s.id === key)
    if (!item) return { ok: false }
    if (item.status !== 'cancelled') return { ok: false }
    if (item.refundStatus === 'refunded') return { ok: false }
    // Mock Stripe refund
    const refundId = `re_${Math.random().toString(36).slice(2, 10)}_${Date.now().toString(36)}`
    item.refundStatus = 'refunded'
    item.refundId = refundId
    item.nextCheckpointIn = 'Refunded to Visa'
    return { ok: true, refundId }
  }

  function updateDeliveryStatus(id: string, next: DeliveryStatus): boolean {
    const key = id.trim().toUpperCase()
    const item = state.items.find((s) => s.id === key)
    if (!item) return false
    // enforce sequential flow: assigned -> picked_up -> on_the_way -> delivered
    const order: DeliveryStatus[] = ['assigned', 'picked_up', 'on_the_way', 'delivered']
    const curIdx = order.indexOf(item.deliveryStatus)
    const nextIdx = order.indexOf(next)
    if (nextIdx !== curIdx + 1) return false
    item.deliveryStatus = next
    item.deliveryUpdatedAt = new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' }) + ' UTC'
    if (next === 'picked_up') {
      item.nextCheckpoint = 'Picked Up — en route to customer'
      item.nextCheckpointIn = 'On the way'
    } else if (next === 'on_the_way') {
      item.nextCheckpoint = 'On the way — navigating to dropoff'
      item.nextCheckpointIn = 'ETA 12 min'
    } else if (next === 'delivered') {
      item.status = 'delivered'
      item.currentPhase = 'Delivered'
      item.timelineFillPct = 100
      item.eta = 'Delivered'
      item.nextCheckpoint = 'Delivered — awaiting customer signature'
      item.nextCheckpointIn = 'Completed'
    }
    return true
  }

  return { list, get, remove, cancelOrder, issueRefund, updateDeliveryStatus }
}