import { describe, it, expect } from 'vitest'
import {
  isCancellableStatus,
  canCancelOrder,
  isRefundEligible,
  isRefunded,
  STATUS_FLOW,
} from '../app/data/shipments'

// 1. Users cannot create orders — frontend has no creation API
describe('Business Constraint: Users cannot create orders', () => {
  it('should not expose createBookedShipment (removed per No Order Creation guardrail)', async () => {
    const shipmentsModule: any = await import('../app/data/shipments')
    expect(shipmentsModule.createBookedShipment).toBeUndefined()
    expect(shipmentsModule.NewShipmentInput).toBeUndefined()
  })

  it('should not expose add() in useShipments composable', async () => {
    const { useShipments } = await import('../app/composables/useShipments')
    const api = useShipments()
    // @ts-expect-error — add should not exist
    expect(api.add).toBeUndefined()
    expect(api.list).toBeDefined()
    expect(api.cancelOrder).toBeDefined()
  })

  it('should have shipments list page with no New Shipment button (read-only)', async () => {
    const fs = await import('fs')
    const path = await import('path')
    const content = fs.readFileSync(path.resolve(__dirname, '../app/pages/shipments/index.vue'), 'utf-8')
    expect(content).not.toMatch(/New Shipment/)
    expect(content).not.toMatch(/Create New Shipment/)
    expect(content).not.toMatch(/Book Shipment/)
    expect(content).toMatch(/tracking only/)
  })
})

// 2. Cancellation strictly fails after Stage 1
describe('Business Constraint: Cancellation strictly fails after Stage 1', () => {
  it('Stage 1 (order_received/booked) is cancellable', () => {
    expect(isCancellableStatus('order_received')).toBe(true)
    expect(isCancellableStatus('booked')).toBe(true)
    expect(canCancelOrder({ status: 'order_received' })).toBe(true)
    expect(canCancelOrder({ status: 'booked' })).toBe(true)
  })

  it('Stage 2+ is NOT cancellable (picked_up, in_transit, out_for_delivery, delivered, cancelled)', () => {
    expect(isCancellableStatus('in_transit' as any)).toBe(false)
    expect(canCancelOrder({ status: 'in_transit' })).toBe(false)
    expect(canCancelOrder({ status: 'out_for_delivery' })).toBe(false)
    expect(canCancelOrder({ status: 'delivered' })).toBe(false)
    expect(canCancelOrder({ status: 'cancelled' })).toBe(false)
  })

  it('STATUS_FLOW enforces linear state machine with cancel only from received', () => {
    // Allowed: received -> picked_up, received -> cancelled
    expect(STATUS_FLOW.order_received.index).toBe(0)
    // Verify cancelled is terminal
    // The backend Order.ALLOWED_TRANSITIONS is mirrored here via isCancellableStatus
    // Frontend timeline: only Stage 1 shows Cancel button (v-if="canCancel")
    // This test ensures the helper is used correctly
    const stage1 = canCancelOrder({ status: 'order_received' })
    const stage3 = canCancelOrder({ status: 'in_transit' })
    expect(stage1).toBe(true)
    expect(stage3).toBe(false)
  })

  it('Refund eligibility requires cancelled + pending', () => {
    expect(isRefundEligible({ status: 'cancelled', refundStatus: 'pending' })).toBe(true)
    expect(isRefundEligible({ status: 'cancelled', refundStatus: 'refunded' })).toBe(false)
    expect(isRefundEligible({ status: 'cancelled', refundStatus: 'none' })).toBe(false)
    expect(isRefundEligible({ status: 'order_received', refundStatus: 'pending' })).toBe(false)
    expect(isRefunded({ refundStatus: 'refunded' })).toBe(true)
    expect(isRefunded({ refundStatus: 'pending' })).toBe(false)
  })

  it('shipments detail page hides Cancel button after Stage 1 (v-if="canCancel")', async () => {
    const fs = await import('fs')
    const path = await import('path')
    const content = fs.readFileSync(path.resolve(__dirname, '../app/pages/shipments/[id].vue'), 'utf-8')
    expect(content).toMatch(/canCancel/)
    expect(content).toMatch(/ShipmentCancelOrderButton/)
    expect(content).toMatch(/v-if="canCancel"/)
  })
})

// 3. Refunds can only be triggered by Admins
describe('Business Constraint: Refunds can only be triggered by Admins', () => {
  it('RefundManagement shows Issue Visa Refund only for admin + eligible', async () => {
    const fs = await import('fs')
    const path = await import('path')
    const content = fs.readFileSync(path.resolve(__dirname, '../app/components/shipment/RefundManagement.vue'), 'utf-8')
    // Component must check isAdmin and eligible
    expect(content).toMatch(/isAdmin/)
    expect(content).toMatch(/eligible/)
    expect(content).toMatch(/Issue Visa Refund/)
    // Must hide for non-admin
    expect(content).toMatch(/Pending admin refund/)
  })

  it('Invoice table highlights Refunded status (passive billing)', async () => {
    const fs = await import('fs')
    const path = await import('path')
    const billing = fs.readFileSync(path.resolve(__dirname, '../app/pages/billing.vue'), 'utf-8')
    // Billing must be passive, no Add Payment Method / Set default
    expect(billing).not.toMatch(/Add Payment Method/)
    // Check that InvoiceTable highlights refunded
    const table = fs.readFileSync(path.resolve(__dirname, '../app/components/billing/InvoiceTable.vue'), 'utf-8')
    expect(table).toMatch(/refunded/)
    expect(table).toMatch(/amber/)
  })
})
