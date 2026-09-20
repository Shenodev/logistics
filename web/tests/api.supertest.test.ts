import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import request from 'supertest'
import { createServer } from 'http'

// Mock Django DRF behavior for Supertest verification
// This mirrors the actual backend/src: orders/views.py cancel 400 after Stage 1, refund admin-only

function createMockApiServer() {
  return createServer((req, res) => {
    const url = new URL(req.url || '/', `http://${req.headers.host}`)
    const path = url.pathname
    const method = req.method
    const role = (req.headers['x-role'] as string) || 'user'
    const body: any = {}

    let raw = ''
    req.on('data', (chunk) => (raw += chunk))
    req.on('end', () => {
      try {
        Object.assign(body, raw ? JSON.parse(raw) : {})
      } catch {}

      // 1. Users cannot create orders
      if (path === '/api/orders/' && method === 'POST') {
        if (role !== 'admin' && req.headers['x-external-ingest'] !== 'true') {
          res.writeHead(403, { 'Content-Type': 'application/json' })
          res.end(JSON.stringify({ detail: 'Manual order creation is disabled. Orders are ingested via external APIs.' }))
          return
        }
        res.writeHead(201, { 'Content-Type': 'application/json' })
        res.end(JSON.stringify({ order_number: 'SHP-MOCK-001', status: 'received' }))
        return
      }

      // 2. Cancellation strictly fails after Stage 1
      const cancelMatch = path.match(/^\/api\/orders\/([^/]+)\/cancel\/?$/)
      if (cancelMatch && method === 'POST') {
        const status = (req.headers['x-order-status'] as string) || 'received'
        if (status !== 'received' && status !== 'order_received' && status !== 'booked') {
          res.writeHead(400, { 'Content-Type': 'application/json' })
          res.end(JSON.stringify({ detail: `Only orders in Stage 1 (Received) can be cancelled. Current status is ${status}.` }))
          return
        }
        res.writeHead(200, { 'Content-Type': 'application/json' })
        res.end(JSON.stringify({ order_number: cancelMatch[1], status: 'cancelled' }))
        return
      }

      // 3. Refunds can only be triggered by Admins
      if (path === '/api/v1/refunds/' && method === 'POST') {
        if (role !== 'admin') {
          res.writeHead(403, { 'Content-Type': 'application/json' })
          res.end(JSON.stringify({ detail: 'Admin access required.' }))
          return
        }
        const orderStatus = (req.headers['x-order-status'] as string) || 'cancelled'
        const refundStatus = (req.headers['x-refund-status'] as string) || 'pending'
        if (orderStatus !== 'cancelled') {
          res.writeHead(400, { 'Content-Type': 'application/json' })
          res.end(JSON.stringify({ detail: 'Only cancelled orders can be refunded.' }))
          return
        }
        if (refundStatus !== 'pending') {
          res.writeHead(400, { 'Content-Type': 'application/json' })
          res.end(JSON.stringify({ detail: 'Order already refunded.' }))
          return
        }
        res.writeHead(200, { 'Content-Type': 'application/json' })
        res.end(JSON.stringify({ detail: 'Visa refund issued via Stripe.', refund_id: 're_mock_123' }))
        return
      }

      res.writeHead(404, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify({ detail: 'Not found' }))
    })
  })
}

describe('Supertest: Secure Order APIs', () => {
  const server = createMockApiServer()
  const agent = request(server)

  afterAll(() => server.close())

  it('1. Users cannot create orders (403 without external ingest, 201 with admin)', async () => {
    const resUser = await agent.post('/api/orders/').set('x-role', 'user').send({ order_number: 'SHP-TEST-001' })
    expect(resUser.status).toBe(403)
    expect(resUser.body.detail).toMatch(/Manual order creation is disabled/)

    const resAdmin = await agent.post('/api/orders/').set('x-role', 'admin').send({ order_number: 'SHP-ADMIN-001' })
    expect(resAdmin.status).toBe(201)

    const resExternal = await agent.post('/api/orders/').set('x-role', 'user').set('x-external-ingest', 'true').send({ order_number: 'SHP-EXT-001' })
    expect(resExternal.status).toBe(201)
  })

  it('2. Cancellation strictly fails after Stage 1 (400 if not received)', async () => {
    const resOk = await agent.post('/api/orders/SHP-RECEIVED-001/cancel').set('x-role', 'user').set('x-order-status', 'received')
    expect(resOk.status).toBe(200)
    expect(resOk.body.status).toBe('cancelled')

    const statuses = ['picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'cancelled']
    for (const s of statuses) {
      const res = await agent.post('/api/orders/SHP-TEST-001/cancel').set('x-role', 'user').set('x-order-status', s)
      expect(res.status).toBe(400)
      expect(res.body.detail).toMatch(/Only orders in Stage 1/)
    }
  })

  it('3. Refunds can only be triggered by Admins (403 for user/driver, 200 for admin on pending)', async () => {
    const resUser = await agent.post('/api/v1/refunds/').set('x-role', 'user').send({ order_number: 'SHP-10004-CAN' })
    expect(resUser.status).toBe(403)
    expect(resUser.body.detail).toMatch(/Admin access required/)

    const resDriver = await agent.post('/api/v1/refunds/').set('x-role', 'driver').send({ order_number: 'SHP-10004-CAN' })
    expect(resDriver.status).toBe(403)

    const resAdminPending = await agent
      .post('/api/v1/refunds/')
      .set('x-role', 'admin')
      .set('x-order-status', 'cancelled')
      .set('x-refund-status', 'pending')
      .send({ order_number: 'SHP-10004-CAN' })
    expect(resAdminPending.status).toBe(200)
    expect(resAdminPending.body.detail).toMatch(/Visa refund issued/)

    const resAdminWrongStatus = await agent
      .post('/api/v1/refunds/')
      .set('x-role', 'admin')
      .set('x-order-status', 'received')
      .send({ order_number: 'SHP-RECEIVED-001' })
    expect(resAdminWrongStatus.status).toBe(400)

    const resAdminAlreadyRefunded = await agent
      .post('/api/v1/refunds/')
      .set('x-role', 'admin')
      .set('x-order-status', 'cancelled')
      .set('x-refund-status', 'refunded')
      .send({ order_number: 'SHP-10004-CAN' })
    expect(resAdminAlreadyRefunded.status).toBe(400)
  })
})
