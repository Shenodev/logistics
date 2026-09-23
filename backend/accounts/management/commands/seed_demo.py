import random
import string
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Faker

User = get_user_model()

# Hardcoded demo accounts per task spec
DEMO_ACCOUNTS = [
    {
        "email": "user@shenodev.tech",
        "username": "user@shenodev.tech",
        "password": "user123",
        "role": "user",
        "first_name": "Demo Shipper",
        "last_name": "User",
        "is_staff": False,
    },
    {
        "email": "admin@shenodev.tech",
        "username": "admin@shenodev.tech",
        "password": "admin123",
        "role": "admin",
        "first_name": "Demo Admin",
        "last_name": "Admin",
        "is_staff": True,
    },
    {
        "email": "delivery@shenodev.tech",
        "username": "delivery@shenodev.tech",
        "password": "delivery123",
        "role": "driver",
        "first_name": "Demo Driver",
        "last_name": "Delivery",
        "is_staff": False,
    },
]


class Command(BaseCommand):
    help = "Seed demo accounts (hardcoded) + rich interconnected Faker data: 50+ orders, 20+ invoices, vehicles, active alerts"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Clear existing DEMO data before seeding")
        parser.add_argument("--orders", type=int, default=57, help="Number of fake orders to generate (default 57)")
        parser.add_argument("--invoices", type=int, default=24, help="Number of invoices to generate (default 24)")

    def handle(self, *args, **options):
        fake = Faker()
        Faker.seed(1337)
        random.seed(1337)

        clear = options["clear"]
        num_orders = options["orders"]
        num_invoices = options["invoices"]

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding demo accounts..."))
        demo_users = {}
        for acc in DEMO_ACCOUNTS:
            user, created = User.objects.get_or_create(
                username=acc["username"],
                defaults={
                    "email": acc["email"],
                    "first_name": acc["first_name"],
                    "last_name": acc["last_name"],
                    "role": acc["role"],
                    "is_staff": acc["is_staff"],
                },
            )
            # Ensure fields are exactly as spec even if existed
            user.email = acc["email"]
            user.first_name = acc["first_name"]
            user.last_name = acc["last_name"]
            user.role = acc["role"]
            user.is_staff = acc["is_staff"] or acc["role"] == "admin"
            user.is_active = True
            user.set_password(acc["password"])
            user.save()
            demo_users[acc["role"]] = user
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"  {action} {acc['email']} (role={acc['role']})"))

        shipper = demo_users["user"]
        admin = demo_users["admin"]
        driver = demo_users["driver"]

        # Lazy import to avoid circular import at module load
        from fleet.models import DriverProfile
        from invoices.models import Invoice
        from notifications.models import Notification
        from orders.models import Order

        # Clean previous DEMO data if requested or by default for idempotency on order numbers
        # We delete DEMO-prefixed objects so re-running does not duplicate
        demo_order_qs = Order.objects.filter(order_number__startswith="SHP-DEMO-")
        demo_invoice_qs = Invoice.objects.filter(invoice_number__startswith="INV-DEMO-")
        # Notifications tied to demo orders or demo users with DEMO tag
        # For safety, delete notifications where order is demo order OR message contains DEMO marker
        demo_notif_qs = Notification.objects.filter(order__order_number__startswith="SHP-DEMO-")
        # Also clear system alerts with DEMO tag for these users
        system_notif_qs = Notification.objects.filter(user__in=[shipper.id, admin.id, driver.id], title__startswith="[DEMO]")

        if clear or demo_order_qs.exists():
            count_o = demo_order_qs.count()
            count_i = demo_invoice_qs.count()
            count_n = demo_notif_qs.count() + system_notif_qs.count()
            if count_o or count_i or count_n:
                self.stdout.write(f"  Clearing previous DEMO data: {count_o} orders, {count_i} invoices, {count_n} alerts")
            # Delete notifications first (FK)
            demo_notif_qs.delete()
            system_notif_qs.delete()
            demo_invoice_qs.delete()
            demo_order_qs.delete()
            # Reset driver profile counters
            DriverProfile.objects.filter(user=driver).update(current_orders_count=0)

        # ------------------------------------------------------------------
        # Vehicles: ensure delivery driver has a rich DriverProfile
        # ------------------------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding vehicles (DriverProfile)..."))
        vehicle_types = [c[0] for c in DriverProfile.VehicleType.choices]
        availabilities = [c[0] for c in DriverProfile.Availability.choices]

        def fake_plate():
            return f"{fake.lexify(text='??').upper()}-{fake.numerify(text='###')}-{fake.lexify(text='???').upper()}"

        def fake_license():
            return f"{fake.lexify(text='????').upper()}-{fake.numerify(text='########')}"

        profile, created = DriverProfile.objects.get_or_create(
            user=driver,
            defaults={
                "license_number": fake_license(),
                "vehicle_type": random.choice(vehicle_types),
                "vehicle_plate": fake_plate(),
                "phone": fake.phone_number()[:20],
                "availability": "available",
                "is_available": True,
                "rating": round(random.uniform(4.2, 5.0), 1),
                "total_deliveries": random.randint(80, 450),
                "acceptance_rate": round(random.uniform(86.0, 99.5), 1),
                "current_orders_count": 0,
                "max_orders": 6,
            },
        )
        if not created:
            # Refresh Faker data on re-seed but keep valid unique fields
            profile.vehicle_type = random.choice(vehicle_types)
            profile.availability = random.choice(["available", "on_duty"])
            profile.is_available = True
            profile.rating = round(random.uniform(4.2, 5.0), 1)
            profile.total_deliveries = random.randint(80, 450)
            profile.acceptance_rate = round(random.uniform(86.0, 99.5), 1)
            profile.phone = fake.phone_number()[:20]
            # Regenerate if needed to avoid unique clashes on update
            try:
                profile.save()
            except Exception:
                profile.license_number = fake_license()
                profile.vehicle_plate = fake_plate()
                profile.save()
        else:
            # Ensure uniqueness already handled
            pass
        self.stdout.write(self.style.SUCCESS(f"  Vehicle: {profile.get_vehicle_type_display()} {profile.vehicle_plate} -> {driver.email}"))

        # ------------------------------------------------------------------
        # Orders: 50+ interconnected orders in various stages, strictly tied to shipper owner
        # ------------------------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING(f"Seeding {num_orders} orders (various stages, Faker)..."))

        # Weighted distribution across stages
        status_weights = [
            (Order.Status.PROCESSING, 8),
            (Order.Status.RECEIVED, 8),
            (Order.Status.RECEIVED_BY_DRIVER, 6),
            (Order.Status.PICKED_UP, 7),
            (Order.Status.IN_TRANSIT, 7),
            (Order.Status.OUT_FOR_DELIVERY, 6),
            (Order.Status.DELIVERED, 10),
            (Order.Status.CANCELLED, 5),
        ]
        # Flatten to list then shuffle
        status_pool = []
        for status, weight in status_weights:
            status_pool.extend([status] * weight)
        # If num_orders differs from 57, extend or trim pool
        while len(status_pool) < num_orders:
            status_pool.extend(status_pool)
        status_pool = status_pool[:num_orders]
        random.shuffle(status_pool)

        modes = ["Ocean Freight", "Air Freight", "Road Freight", "Rail Freight", "Express"]
        priorities = ["Standard Freight", "Priority Air", "Express", "Economy", "Critical"]
        delivery_map = {
            Order.Status.PROCESSING: "assigned",
            Order.Status.RECEIVED: "assigned",
            Order.Status.RECEIVED_BY_DRIVER: "assigned",
            Order.Status.CANCELLED: "assigned",
            Order.Status.PICKED_UP: "picked_up",
            Order.Status.IN_TRANSIT: "on_the_way",
            Order.Status.OUT_FOR_DELIVERY: "on_the_way",
            Order.Status.DELIVERED: "delivered",
        }

        created_orders = []
        now = timezone.now()
        base_seq = fake.random_int(min=1000, max=9000)

        for idx, status in enumerate(status_pool):
            seq = base_seq + idx
            order_number = f"SHP-DEMO-{seq:05d}-ORD"
            # Ensure unique even on re-run with different seq base - get_or_create
            origin = fake.city()
            destination = fake.city()
            # Avoid same city
            while destination == origin:
                destination = fake.city()
            origin_code = fake.lexify(text="???").upper()
            destination_code = fake.lexify(text="???").upper()
            mode = random.choice(modes)
            priority = random.choice(priorities)
            gross_weight = f"{fake.random_int(min=500, max=28000):,} kg"
            customer_phone = fake.phone_number()[:20]
            restaurant_name = fake.company() + " " + random.choice(["Hub", "Kitchen", "Depot", "Logistics Center"])
            restaurant_address = fake.address().replace("\n", ", ")[:200]
            delivery_status = delivery_map.get(status, "assigned")

            # Driver assignment logic - strictly delivery@shenodev.tech for assigned stages
            driver_fk = None
            is_locked = False
            dispatch_status = Order.DispatchStatus.IDLE
            dispatch_queue = []
            dispatch_in_progress = False
            assigned_name = ""
            assigned_phone = profile.phone if profile.phone else fake.phone_number()[:20]

            if status in (Order.Status.RECEIVED_BY_DRIVER, Order.Status.PICKED_UP, Order.Status.IN_TRANSIT, Order.Status.OUT_FOR_DELIVERY, Order.Status.DELIVERED):
                driver_fk = driver
                if status == Order.Status.RECEIVED_BY_DRIVER:
                    is_locked = True
                    dispatch_status = Order.DispatchStatus.ASSIGNED
                    assigned_name = f"{driver.first_name} {driver.last_name}".strip() or driver.email
                    assigned_phone = profile.phone
                elif status == Order.Status.DELIVERED:
                    dispatch_status = Order.DispatchStatus.COMPLETED
                    is_locked = True
                    assigned_name = f"{driver.first_name} {driver.last_name}".strip() or driver.email
                    assigned_phone = profile.phone
                else:
                    dispatch_status = Order.DispatchStatus.ASSIGNED
            elif status == Order.Status.PROCESSING and random.random() < 0.3:
                # Simulate active dispatch
                dispatch_status = Order.DispatchStatus.DISPATCHING
                dispatch_queue = [driver.id]
                dispatch_in_progress = True
            elif status == Order.Status.RECEIVED and random.random() < 0.2:
                dispatch_status = Order.DispatchStatus.DISPATCHING
                dispatch_queue = [driver.id]
                dispatch_in_progress = True

            # Create order - bypass transition checks by direct creation with desired status
            order = Order.objects.create(
                order_number=order_number,
                owner=shipper,
                driver=driver_fk,
                status=status,
                dispatch_status=dispatch_status,
                dispatch_queue=dispatch_queue,
                dispatch_current_index=0,
                dispatch_in_progress=dispatch_in_progress,
                is_locked=is_locked,
                assigned_driver_name=assigned_name,
                assigned_driver_phone=assigned_phone,
                origin=origin,
                origin_code=origin_code,
                destination=destination,
                destination_code=destination_code,
                mode=mode,
                priority=priority,
                gross_weight=gross_weight,
                customer_phone=customer_phone,
                restaurant_name=restaurant_name,
                restaurant_address=restaurant_address,
                delivery_status=delivery_status,
            )
            # Backdate created_at/updated_at for realism (past 60 days, but keep stage recency)
            # Delivered = older (completed), processing = recent
            age_weights = {
                Order.Status.DELIVERED: (20, 60),
                Order.Status.OUT_FOR_DELIVERY: (2, 10),
                Order.Status.IN_TRANSIT: (3, 15),
                Order.Status.PICKED_UP: (1, 8),
                Order.Status.RECEIVED_BY_DRIVER: (0, 5),
                Order.Status.RECEIVED: (0, 7),
                Order.Status.PROCESSING: (0, 3),
                Order.Status.CANCELLED: (5, 45),
            }
            low, high = age_weights.get(status, (0, 30))
            days_ago = random.randint(low, high)
            hours_ago = random.randint(0, 23)
            fake_created = now - timedelta(days=days_ago, hours=hours_ago, minutes=random.randint(0, 59))
            # Direct update to avoid auto_now
            Order.objects.filter(pk=order.pk).update(created_at=fake_created, updated_at=fake_created)
            if delivery_status != "assigned":
                Order.objects.filter(pk=order.pk).update(delivery_updated_at=fake_created + timedelta(hours=random.randint(1, 12)))
            if status == Order.Status.CANCELLED:
                Order.objects.filter(pk=order.pk).update(cancelled_at=fake_created + timedelta(hours=2), refund_status="pending")

            created_orders.append(order)

        self.stdout.write(self.style.SUCCESS(f"  Created {len(created_orders)} orders"))

        # ------------------------------------------------------------------
        # Invoices: 20+ past invoices strictly tied to shipper + orders
        # ------------------------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING(f"Seeding {num_invoices} invoices..."))
        # Pick random orders to invoice - prefer delivered/in_transit but include variety
        eligible = [o for o in created_orders if o.status != Order.Status.CANCELLED]
        # Also include some cancelled for refunded invoices
        cancelled_orders = [o for o in created_orders if o.status == Order.Status.CANCELLED]
        invoice_targets = random.sample(eligible, min(len(eligible), num_invoices - min(4, len(cancelled_orders))))
        # Add cancelled ones for refunded flow
        invoice_targets += random.sample(cancelled_orders, min(len(cancelled_orders), num_invoices - len(invoice_targets)))
        # If still short, pad with eligible
        while len(invoice_targets) < num_invoices and eligible:
            invoice_targets.append(random.choice(eligible))
        random.shuffle(invoice_targets)
        invoice_targets = invoice_targets[:num_invoices]

        statuses = [Invoice.Status.PAID, Invoice.Status.OVERDUE, Invoice.Status.PENDING, Invoice.Status.REFUNDED, Invoice.Status.CANCELLED]
        # Weight: mostly paid
        status_pool_inv = (
            [Invoice.Status.PAID] * 10
            + [Invoice.Status.PENDING] * 4
            + [Invoice.Status.OVERDUE] * 3
            + [Invoice.Status.REFUNDED] * 4
            + [Invoice.Status.CANCELLED] * 1
        )

        created_invoices = []
        for idx, order in enumerate(invoice_targets):
            seq = base_seq + 5000 + idx
            invoice_number = f"INV-DEMO-{seq:05d}"
            amount = round(random.uniform(85.0, 4200.0), 2)
            # Force description to tie to order
            description = f"{order.mode} · {order.order_number} · {order.origin} -> {order.destination}"
            # Status logic: cancelled order -> refunded/cancelled, delivered -> paid
            if order.status == Order.Status.CANCELLED:
                status = random.choice([Invoice.Status.REFUNDED, Invoice.Status.CANCELLED])
            elif order.status == Order.Status.DELIVERED:
                status = random.choice([Invoice.Status.PAID, Invoice.Status.PAID, Invoice.Status.PAID, Invoice.Status.OVERDUE])
            else:
                status = random.choice(status_pool_inv)

            due_date = (now - timedelta(days=random.randint(5, 60))).date() if status in (Invoice.Status.OVERDUE, Invoice.Status.PAID, Invoice.Status.REFUNDED) else (now + timedelta(days=random.randint(5, 25))).date()
            paid_at = None
            refund_id = None
            if status == Invoice.Status.PAID:
                paid_at = now - timedelta(days=random.randint(1, 30), hours=random.randint(1, 12))
            if status == Invoice.Status.REFUNDED:
                refund_id = f"re_{fake.lexify(text='????????????').lower()}_{random.randint(1000,9999)}"
                paid_at = now - timedelta(days=random.randint(2, 35))

            # Keep stripe PI in sync with order for refundability
            stripe_pi = order.stripe_payment_intent_id

            inv = Invoice.objects.create(
                invoice_number=invoice_number,
                order=order,
                user=shipper,
                amount=amount,
                currency="USD",
                status=status,
                due_date=due_date,
                paid_at=paid_at,
                refund_id=refund_id,
                stripe_payment_intent_id=stripe_pi,
                description=description[:200],
            )
            # Backdate
            fake_inv_created = now - timedelta(days=random.randint(3, 65), hours=random.randint(0, 23))
            Invoice.objects.filter(pk=inv.pk).update(created_at=fake_inv_created, updated_at=fake_inv_created)
            created_invoices.append(inv)

        self.stdout.write(self.style.SUCCESS(f"  Created {len(created_invoices)} invoices"))

        # ------------------------------------------------------------------
        # Active alerts (Notifications): rich interconnected alerts for shipper + admin + driver
        # ------------------------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding active alerts (notifications)..."))

        # Helper to create notification
        def create_alert(user, order, kind, title, message, stage_from="", stage_to="", is_read=False):
            return Notification.objects.create(
                user=user,
                order=order,
                kind=kind,
                title=title,
                message=message,
                stage_from=stage_from,
                stage_to=stage_to,
                is_read=is_read,
            )

        alerts_created = 0
        # 1) Order transition alerts for recent orders (unread, active)
        recent_orders = sorted(created_orders, key=lambda o: o.order_number, reverse=True)[:15]
        for order in recent_orders:
            # Create 1-2 alerts per order
            title_map = {
                Order.Status.PROCESSING: "Order Processing",
                Order.Status.RECEIVED: "Order Received",
                Order.Status.RECEIVED_BY_DRIVER: "Driver Accepted Order",
                Order.Status.PICKED_UP: "Order Picked Up",
                Order.Status.IN_TRANSIT: "Order In Transit",
                Order.Status.OUT_FOR_DELIVERY: "Out for Delivery",
                Order.Status.DELIVERED: "Order Delivered",
                Order.Status.CANCELLED: "Order Cancelled",
            }
            title = title_map.get(order.status, f"Order {order.status}")
            msg = f"[DEMO] {order.order_number} {title} · {order.origin} ({order.origin_code}) -> {order.destination} ({order.destination_code}) · {order.mode} · {order.gross_weight}"
            # Shipper alert (unread for active feel)
            create_alert(shipper, order, Notification.Kind.ORDER_STATUS, f"[DEMO] {title}", msg, stage_from="processing", stage_to=order.status, is_read=random.random() < 0.25)
            alerts_created += 1
            # Admin alert
            create_alert(admin, order, Notification.Kind.ORDER_STATUS, f"[DEMO] {title}", msg, stage_from="processing", stage_to=order.status, is_read=random.random() < 0.35)
            alerts_created += 1
            # Driver alert if assigned
            if order.driver_id == driver.id:
                dtitle = f"[DEMO] Assigned: {order.order_number}"
                dmsg = f"[DEMO] You are assigned to {order.order_number} · {order.restaurant_name} · {order.restaurant_address} · Customer {order.customer_phone}"
                create_alert(driver, order, Notification.Kind.ASSIGNMENT, dtitle, dmsg, stage_from="assigned", stage_to=order.delivery_status, is_read=random.random() < 0.4)
                alerts_created += 1

        # 2) System / fleet alerts for admin
        system_alerts = [
            ("[DEMO] Fleet at capacity", f"[DEMO] Driver {driver.email} is approaching max capacity ({profile.current_orders_count}/{profile.max_orders})", Notification.Kind.SYSTEM),
            ("[DEMO] High priority shipment", f"[DEMO] {random.choice(created_orders).order_number} flagged as Critical priority · {fake.address().replace(chr(10), ', ')[:120]}", Notification.Kind.SYSTEM),
            ("[DEMO] Vehicle maintenance due", f"[DEMO] {profile.get_vehicle_type_display()} {profile.vehicle_plate} scheduled maintenance in 3 days", Notification.Kind.SYSTEM),
            ("[DEMO] New shipper onboarded", f"[DEMO] {shipper.email} created {len(created_orders)} demo orders", Notification.Kind.SYSTEM),
            ("[DEMO] Refund pending", f"[DEMO] Invoice {random.choice(created_invoices).invoice_number} refund pending review", Notification.Kind.REFUND),
        ]
        for title, msg, kind in system_alerts:
            create_alert(admin, None, kind, title, msg, is_read=False)
            alerts_created += 1

        # 3) Refund alerts for shipper
        refund_invoices = [inv for inv in created_invoices if inv.status == Invoice.Status.REFUNDED]
        for inv in refund_invoices[:5]:
            create_alert(shipper, inv.order, Notification.Kind.REFUND, "[DEMO] Refund Processed", f"[DEMO] {inv.invoice_number} refunded ${inv.amount} · {inv.order.order_number} via Visa ending via {inv.stripe_payment_intent_id[:12]}...", is_read=False)
            create_alert(admin, inv.order, Notification.Kind.REFUND, "[DEMO] Refund Processed", f"[DEMO] {inv.invoice_number} refunded ${inv.amount} -> {shipper.email}", is_read=random.random() < 0.3)
            alerts_created += 2

        self.stdout.write(self.style.SUCCESS(f"  Created {alerts_created} active alerts"))

        # Summary
        self.stdout.write(self.style.MIGRATE_HEADING("Demo seed complete"))
        self.stdout.write(f"  Accounts: 3 (shipper/admin/driver)")
        self.stdout.write(f"  Orders: {Order.objects.filter(order_number__startswith='SHP-DEMO-').count()} (processing/received/received_by_driver/picked_up/in_transit/out_for_delivery/delivered/cancelled)")
        self.stdout.write(f"  Invoices: {Invoice.objects.filter(invoice_number__startswith='INV-DEMO-').count()}")
        self.stdout.write(f"  Vehicles: 1 profile for {driver.email} ({profile.vehicle_plate})")
        self.stdout.write(f"  Alerts: {Notification.objects.filter(title__startswith='[DEMO]').count()} ([DEMO] tagged)")
        self.stdout.write(self.style.SUCCESS("Login with: user@shenodev.tech / user123 | admin@shenodev.tech / admin123 | delivery@shenodev.tech / delivery123"))
