import { computed, reactive, ref } from 'vue'
import type { DeliveryStatus, Shipment, ShipmentStatus } from '~/data/shipments'
import { shipments as seed, STATUS_FLOW } from '~/data/shipments'

// --- API helper (mirrors useAuthStore authRequest) ---
function orderRequest<T>(url: string, options: Record<string, unknown> = {}): Promise<T> {
  const base = String(useRuntimeConfig().public.apiBase ?? '').replace(/\/+$/, '')
  const target = base ? url : `/api${url}`
  const fetcher = import.meta.server ? useRequestFetch() : $fetch
  return fetcher<T>(target, {
    baseURL: base || undefined,
    credentials: base ? 'include' : 'same-origin',
    ...options,
  } as any)
}

// Map backend Order (received/picked_up/...) to frontend ShipmentStatus (order_received etc)
function mapBackendStatus(s: string): ShipmentStatus {
  if (s === 'received') return 'order_received'
  if (s === 'picked_up') return 'order_received' // legacy alias, keep as received for timeline until in_transit
  return s as ShipmentStatus
}

function mapShipmentFromOrder(order: any, fallback?: Shipment): Shipment | null {
  const base = fallback ?? seed.find((s) => s.id === order.order_number) as Shipment | undefined
  if (!base) {
    // Minimal fallback if no seed matches (e.g. newly created order)
    return null
  }
  // Backend order has: order_number, status, delivery_status, customer_phone, restaurantName, etc.
  const mappedStatus = mapBackendStatus(order.status)
  // For delivery_status driven orders, reflect on timeline: if backend is picked_up, show in_transit etc.
  // Keep seed milestones but override status-related fields
  const next: Shipment = {
    ...base,
    id: order.order_number,
    status: mappedStatus,
    // Map backend delivery_status to frontend deliveryStatus
    deliveryStatus: (order.delivery_status as DeliveryStatus) ?? base.deliveryStatus,
    deliveryUpdatedAt: order.delivery_updated_at ?? base.deliveryUpdatedAt,
    customerPhone: order.customer_phone ?? base.customerPhone,
    restaurantName: order.restaurant_name ?? base.restaurantName,
    restaurantAddress: order.restaurant_address ?? base.restaurantAddress,
    // Keep other fields from backend if present
    origin: order.origin ?? base.origin,
    originCode: order.origin_code ?? base.originCode,
    destination: order.destination ?? base.destination,
    destinationCode: order.destination_code ?? base.destinationCode,
    // For cancelled, reflect backend fields
    ...(order.status === 'cancelled' ? {
      cancelledAt: order.cancelled_at ?? base.cancelledAt,
      refundStatus: order.refund_status ?? base.refundStatus,
      refundId: order.refund_id ?? base.refundId,
      invoiceId: order.invoice_id ?? base.invoiceId,
    } : {}),
  }
  // Recompute derived timeline fields if status changed
  if (mappedStatus !== base.status) {
    // Re-derive milestones and phase from new status if needed — keep simple for now
    // The frontend's milestonesFor is not exported, so we keep base milestones but update currentPhase
    const flow = STATUS_FLOW[mappedStatus as ShipmentStatus]
    if (flow) {
      next.currentPhase = flow.label
      next.timelineFillPct = Math.round((flow.index / 4) * 100)
    }
    if (order.status === 'cancelled') {
      next.currentPhase = 'Cancelled'
      next.timelineFillPct = 0
      next.eta = 'Cancelled — refund pending'
      next.nextCheckpoint = 'Order cancelled — awaiting admin Visa refund'
    } else if (order.status === 'picked_up') {
      next.currentPhase = 'Picked Up'
      next.nextCheckpoint = 'Picked Up — en route to customer'
    }
  }
  return next
}

const state = reactive<{ items: Shipment[] }>({ items: [...seed] })
const isLoading = ref(false)
const lastError = ref<string | null>(null)

export function useShipments() {
  const list = computed(() => state.items)

  function get(id: string): Shipment | undefined {
    const key = id.trim().toUpperCase()
    return state.items.find((item) => item.id === key)
  }

  // --- $fetch integration for 3 subdomains (user/admin/delivery) ---
  async function fetchOrders(): Promise<Shipment[]> {
    isLoading.value = true
    lastError.value = null
    try {
      const data = await orderRequest<any>('/api/orders/', { method: 'GET' })
      // DRF may return paginated {results: []} or plain array
      const orders: any[] = Array.isArray(data) ? data : (data.results ?? data)
      if (Array.isArray(orders) && orders.length >= 0) {
        // Merge backend orders into state
        for (const o of orders) {
          const existing = state.items.find((s) => s.id === o.order_number)
          const mapped = mapShipmentFromOrder(o, existing)
          if (mapped && existing) {
            Object.assign(existing, mapped)
          } else if (mapped) {
            state.items.unshift(mapped)
          } else if (o.order_number && !existing) {
            // Create minimal shipment from backend order if no seed
            const minimal: Shipment = {
              id: o.order_number,
              mode: o.mode ?? 'Ground Fleet',
              status: mapBackendStatus(o.status),
              priority: o.priority ?? 'Standard',
              origin: o.origin ?? 'Unknown',
              originCode: o.origin_code ?? 'UNK',
              destination: o.destination ?? 'Unknown',
              destinationCode: o.destination_code ?? 'UNK',
              bookedAt: o.created_at ?? new Date().toLocaleString(),
              masterAwb: 'N/A',
              eta: o.status === 'cancelled' ? 'Cancelled' : 'TBD',
              etaTz: 'UTC',
              carrier: 'Pending',
              lat: '0',
              lon: '0',
              spd: '0',
              alt: '0',
              nextCheckpoint: 'Pending',
              nextCheckpointIn: 'TBD',
              weather: 'N/A',
              cargoTemp: 'N/A',
              waypoints: [],
              grossWeight: o.gross_weight ?? '0 kg',
              grossWeightLbs: '0 lbs',
              totalVolume: '0',
              totalVolumeCu: '0',
              pallets: '0',
              palletType: '',
              containerSpec: '',
              containerSpecDetail: '',
              dimensions: '',
              tare: '',
              hsCode: '',
              hsDesc: '',
              handling: [],
              consigneeName: o.destination ?? 'Unknown',
              consigneeAddress: '',
              receiver: '',
              receiverRole: '',
              receiverBadge: '',
              milestones: [],
              currentPhase: o.status ?? 'Unknown',
              timelineFillPct: 0,
              customerPhone: o.customer_phone ?? '+1 (212) 555-0148',
              restaurantName: o.restaurant_name ?? o.origin ?? 'Hub',
              restaurantAddress: o.restaurant_address ?? '',
              deliveryStatus: (o.delivery_status as DeliveryStatus) ?? 'assigned',
              deliveryUpdatedAt: o.delivery_updated_at ?? null,
              cancelledAt: o.cancelled_at ?? null,
              refundStatus: o.refund_status ?? 'none',
              refundId: o.refund_id ?? null,
              invoiceId: o.invoice_id ?? null,
            }
            state.items.unshift(minimal)
          }
        }
      }
      return state.items
    } catch (e: any) {
      lastError.value = e?.data?.detail || e?.message || 'Failed to fetch orders'
      // Fallback to seed (already in state) for offline/dev
      return state.items
    } finally {
      isLoading.value = false
    }
  }

  async function fetchOrder(id: string): Promise<Shipment | undefined> {
    const key = id.trim().toUpperCase()
    try {
      const o = await orderRequest<any>(`/api/orders/${encodeURIComponent(key)}/`, { method: 'GET' })
      const orderData = o.order_number ? o : (o as any)
      const existing = state.items.find((s) => s.id === key)
      const mapped = mapShipmentFromOrder(orderData, existing)
      if (mapped && existing) {
        Object.assign(existing, mapped)
        return existing
      } else if (mapped) {
        state.items.unshift(mapped)
        return mapped
      }
      return mapped ?? undefined
    } catch {
      // Fallback to local
      return get(key)
    }
  }

  function remove(id: string): boolean {
    const key = id.trim().toUpperCase()
    const idx = state.items.findIndex((item) => item.id === key)
    if (idx === -1) return false
    state.items.splice(idx, 1)
    return true
  }

  async function cancelOrder(id: string): Promise<boolean> {
    const key = id.trim().toUpperCase()
    const local = state.items.find((s) => s.id === key)
    // Try API first
    try {
      const res = await orderRequest<any>(`/api/orders/${encodeURIComponent(key)}/cancel/`, { method: 'POST' })
      const updated = res.order_number ? res : res
      if (local) {
        const mapped = mapShipmentFromOrder(updated, local)
        if (mapped) Object.assign(local, mapped)
        // Fallback ensure cancelled fields
        local.status = 'cancelled' as ShipmentStatus
        local.refundStatus = 'pending'
      }
      return true
    } catch (e: any) {
      // If API fails (offline or 400), fallback to local logic for Stage 1 check
      if (local) {
        if (local.status !== 'order_received' && local.status !== 'booked') return false
        if (local.status === 'cancelled') return false
        local.status = 'cancelled'
        local.cancelledAt = new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) + ' • ' + new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) + ' UTC'
        local.cancelledBy = 'current_user'
        local.refundStatus = 'pending'
        local.refundId = null
        local.eta = 'Cancelled — refund pending'
        local.nextCheckpoint = 'Order cancelled — awaiting admin Visa refund'
        local.nextCheckpointIn = 'Refund pending'
        local.currentPhase = 'Cancelled'
        local.timelineFillPct = 0
        return true
      }
      return false
    }
  }

  async function issueRefund(id: string): Promise<{ ok: boolean; refundId?: string }> {
    const key = id.trim().toUpperCase()
    const local = state.items.find((s) => s.id === key)
    try {
      // Try via dedicated refunds endpoint
      const res = await orderRequest<any>('/api/v1/refunds/', { method: 'POST', body: { order_number: key } })
      const refundId = res.refund_id || res.id || `re_${Date.now()}`
      if (local) {
        local.refundStatus = 'refunded'
        local.refundId = refundId
        local.nextCheckpointIn = 'Refunded to Visa'
      }
      // Also try to update local via fetchOrder
      await fetchOrder(key)
      return { ok: true, refundId }
    } catch {
      if (!local) return { ok: false }
      if (local.status !== 'cancelled') return { ok: false }
      if (local.refundStatus === 'refunded') return { ok: false }
      const refundId = `re_${Math.random().toString(36).slice(2, 10)}_${Date.now().toString(36)}`
      local.refundStatus = 'refunded'
      local.refundId = refundId
      local.nextCheckpointIn = 'Refunded to Visa'
      return { ok: true, refundId }
    }
  }

  async function updateDeliveryStatus(id: string, next: DeliveryStatus): Promise<boolean> {
    const key = id.trim().toUpperCase()
    const local = state.items.find((s) => s.id === key)
    // Try API: PATCH /api/orders/{id}/ with delivery_status
    try {
      const res = await orderRequest<any>(`/api/orders/${encodeURIComponent(key)}/`, {
        method: 'PATCH',
        body: { delivery_status: next },
      })
      const updated = res.delivery_status ? res : res
      const newStatus = updated.delivery_status as DeliveryStatus
      if (local) {
        // Update local from API response
        const mapped = mapShipmentFromOrder(updated, local)
        if (mapped) Object.assign(local, mapped)
        else local.deliveryStatus = newStatus
        local.deliveryUpdatedAt = updated.delivery_updated_at ?? new Date().toLocaleString()
        // Sync main status if delivered
        if (newStatus === 'delivered') {
          local.status = 'delivered' as ShipmentStatus
          local.currentPhase = 'Delivered'
          local.timelineFillPct = 100
        }
      }
      return true
    } catch (e: any) {
      // Fallback to local state machine for offline/dev
      if (!local) return false
      const order: DeliveryStatus[] = ['assigned', 'picked_up', 'on_the_way', 'delivered']
      const curIdx = order.indexOf(local.deliveryStatus)
      const nextIdx = order.indexOf(next)
      if (nextIdx !== curIdx + 1) return false
      local.deliveryStatus = next
      local.deliveryUpdatedAt = new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' }) + ' UTC'
      if (next === 'picked_up') {
        local.nextCheckpoint = 'Picked Up — en route to customer'
        local.nextCheckpointIn = 'On the way'
      } else if (next === 'on_the_way') {
        local.nextCheckpoint = 'On the way — navigating to dropoff'
        local.nextCheckpointIn = 'ETA 12 min'
      } else if (next === 'delivered') {
        local.status = 'delivered'
        local.currentPhase = 'Delivered'
        local.timelineFillPct = 100
        local.eta = 'Delivered'
        local.nextCheckpoint = 'Delivered — awaiting customer signature'
        local.nextCheckpointIn = 'Completed'
      }
      return true
    }
  }

  // Helpers for driver accept/reject via API
  async function acceptOrder(id: string): Promise<boolean> {
    const key = id.trim().toUpperCase()
    try {
      const res = await orderRequest<any>(`/api/orders/${encodeURIComponent(key)}/accept/`, { method: 'POST' })
      const mapped = mapShipmentFromOrder(res, get(key))
      if (mapped && get(key)) Object.assign(get(key)!, mapped)
      return true
    } catch {
      // Fallback local: move to assigned
      const local = get(key)
      if (local && local.status === 'order_received') {
        local.deliveryStatus = 'picked_up'
        return true
      }
      return false
    }
  }

  async function rejectOrder(id: string): Promise<boolean> {
    const key = id.trim().toUpperCase()
    try {
      const res = await orderRequest<any>(`/api/orders/${encodeURIComponent(key)}/reject/`, { method: 'POST' })
      const mapped = mapShipmentFromOrder(res, get(key))
      if (mapped && get(key)) Object.assign(get(key)!, mapped)
      return true
    } catch {
      return false
    }
  }

  return {
    list, get, remove, cancelOrder, issueRefund, updateDeliveryStatus, acceptOrder, rejectOrder,
    fetchOrders, fetchOrder,
    isLoading, lastError,
  }
}
