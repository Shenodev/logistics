from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.models import Order
from orders.views import OrderViewSet
from invoices.models import Invoice
from invoices.views import create_refund

User = get_user_model()


class BusinessConstraintsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        # Clean
        Order.objects.filter(order_number__startswith='SHP-TEST-').delete()
        Invoice.objects.filter(invoice_number__startswith='INV-TEST-').delete()
        # Users: get_or_create for test isolation (role field)
        self.user, _ = User.objects.get_or_create(username='test_user_constraint@sheno.dev', defaults={'email': 'test_user_constraint@sheno.dev', 'role': 'user'})
        self.user.set_password('test12345')
        self.user.role = 'user'
        self.user.save()
        self.admin, _ = User.objects.get_or_create(username='test_admin_constraint@sheno.dev', defaults={'email': 'test_admin_constraint@sheno.dev', 'role': 'admin', 'is_staff': True})
        self.admin.set_password('test12345')
        self.admin.role = 'admin'
        self.admin.is_staff = True
        self.admin.save()
        self.driver, _ = User.objects.get_or_create(username='test_driver_constraint@sheno.dev', defaults={'email': 'test_driver_constraint@sheno.dev', 'role': 'driver'})
        self.driver.set_password('test12345')
        self.driver.role = 'driver'
        self.driver.save()

    def tearDown(self):
        Order.objects.filter(order_number__startswith='SHP-TEST-').delete()
        Invoice.objects.filter(invoice_number__startswith='INV-TEST-').delete()

    def test_1_users_cannot_create_orders(self):
        """Users cannot create orders via POST /api/orders/ without external ingest — must be 403"""
        view = OrderViewSet.as_view({'post': 'create'})
        # User without external header should be blocked
        req = self.factory.post('/api/orders/', {'order_number': 'SHP-TEST-CREATE-001', 'origin': 'A', 'destination': 'B'}, format='json')
        force_authenticate(req, user=self.user)
        resp = view(req)
        self.assertEqual(resp.status_code, 403)
        self.assertIn('Manual order creation is disabled', str(resp.data))

        # Admin can create (or external ingest)
        req2 = self.factory.post('/api/orders/', {'order_number': 'SHP-TEST-CREATE-002', 'origin': 'A', 'destination': 'B'}, format='json', HTTP_X_EXTERNAL_INGEST='true')
        force_authenticate(req2, user=self.user)
        resp2 = view(req2)
        # With external header, user can create (simulating external API)
        self.assertEqual(resp2.status_code, 201)

        # Admin without header can also create
        req3 = self.factory.post('/api/orders/', {'order_number': 'SHP-TEST-CREATE-003', 'origin': 'A', 'destination': 'B'}, format='json')
        force_authenticate(req3, user=self.admin)
        resp3 = view(req3)
        self.assertEqual(resp3.status_code, 201)

    def test_2_cancellation_strictly_fails_after_stage1(self):
        """Cancellation strictly fails after Stage 1 — only received can be cancelled, else 400"""
        view = OrderViewSet.as_view({'post': 'cancel'})
        # Create received order
        order = Order.objects.create(order_number='SHP-TEST-CANCEL-001', owner=self.user, status='received', origin='A', destination='B')
        # Should succeed
        req = self.factory.post(f'/api/orders/{order.order_number}/cancel')
        force_authenticate(req, user=self.user)
        resp = view(req, order_number=order.order_number)
        self.assertEqual(resp.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, 'cancelled')
        self.assertEqual(order.refund_status, 'pending')

        # Create orders in later stages and ensure cancel fails with 400
        for idx, status in enumerate(['picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'cancelled']):
            order2 = Order.objects.create(order_number=f'SHP-TEST-TC{idx}', owner=self.user, status=status, origin='A', destination='B')
            # For cancelled, need to set refund_status to avoid auto-pending? It's already pending from save
            req2 = self.factory.post(f'/api/orders/{order2.order_number}/cancel')
            force_authenticate(req2, user=self.user)
            resp2 = view(req2, order_number=order2.order_number)
            self.assertEqual(resp2.status_code, 400, msg=f"Cancel should fail for {status}, got {resp2.status_code} {resp2.data}")
            self.assertIn('Only orders in Stage 1', str(resp2.data))

    def test_3_refunds_only_admin(self):
        """Refunds can only be triggered by Admins — user/driver 403, admin 200, second refund 400"""
        # Create cancelled pending order + invoice
        order = Order.objects.create(order_number='SHP-TEST-REFUND-001', owner=self.user, status='received', origin='A', destination='B')
        order.status = 'cancelled'
        order.save()
        order.refresh_from_db()
        # Ensure invoice exists
        inv = Invoice.objects.create(invoice_number='INV-TEST-REFUND-001', order=order, user=self.user, amount=100, status='pending', stripe_payment_intent_id=order.stripe_payment_intent_id)
        # User should be 403
        req = self.factory.post('/api/v1/refunds/', {'order_number': order.order_number}, format='json')
        force_authenticate(req, user=self.user)
        resp = create_refund(req)
        self.assertEqual(resp.status_code, 403)
        # Driver should be 403
        req2 = self.factory.post('/api/v1/refunds/', {'order_number': order.order_number}, format='json')
        force_authenticate(req2, user=self.driver)
        resp2 = create_refund(req2)
        self.assertEqual(resp2.status_code, 403)
        # Admin should succeed 200
        req3 = self.factory.post('/api/v1/refunds/', {'order_number': order.order_number}, format='json')
        force_authenticate(req3, user=self.admin)
        resp3 = create_refund(req3)
        self.assertEqual(resp3.status_code, 200)
        self.assertIn('Visa refund issued', str(resp3.data))
        # Second refund should be 400 (already refunded)
        req4 = self.factory.post('/api/v1/refunds/', {'order_number': order.order_number}, format='json')
        force_authenticate(req4, user=self.admin)
        resp4 = create_refund(req4)
        self.assertEqual(resp4.status_code, 400)
        self.assertIn('already refunded', str(resp4.data).lower())
