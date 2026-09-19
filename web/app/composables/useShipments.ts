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

  return { list, get, remove, cancelOrder, issueRefund }
}