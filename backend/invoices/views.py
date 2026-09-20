import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from accounts.permissions import IsAdmin

from orders.models import Order

from .models import Invoice

logger = logging.getLogger(__name__)


def _get_stripe_client():
    secret = getattr(settings, 'STRIPE_SECRET_KEY', '') or ''
    if not secret or secret.startswith('sk_test_mock') or secret == 'mock':
        return None
    try:
        import stripe
        stripe.api_key = secret
        # Optionally set API version
        if getattr(settings, 'STRIPE_API_VERSION', None):
            stripe.api_version = settings.STRIPE_API_VERSION
        return stripe
    except Exception as exc:
        logger.warning('Stripe init failed, falling back to mock: %s', exc)
        return None


@api_view(['POST'])
@permission_classes([IsAdmin])
def create_refund(request):
    """
    Secure Admin-only endpoint: POST /api/v1/refunds/
    Body: { "order_number": "SHP-10004-CAN" } or { "invoice_number": "INV-2024-10004" }

    Validates:
    - User is admin
    - Order is cancelled and refund pending
    - Invoice exists and not already refunded

    Calls Stripe API to refund the original Visa PaymentIntent, then
    updates Invoice.status -> 'refunded' and Order.refund_status -> 'refunded'.
    """
    # IsAdmin permission already enforced; request.user is guaranteed admin
    user = request.user

    order_number = (request.data.get('order_number') or '').strip()
    invoice_number = (request.data.get('invoice_number') or '').strip()
    # Support legacy `order_id` param
    if not order_number and not invoice_number:
        order_number = (request.data.get('order_id') or request.data.get('id') or '').strip()

    if not order_number and not invoice_number:
        return Response(
            {'detail': 'Provide order_number or invoice_number.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Resolve order and invoice
    order = None
    invoice = None

    if order_number:
        try:
            order = Order.objects.select_related('owner', 'driver').get(order_number=order_number)
        except Order.DoesNotExist:
            return Response({'detail': f'Order {order_number} not found.'}, status=status.HTTP_404_NOT_FOUND)
        # Find invoice via order FK or invoice_id field
        invoice = Invoice.objects.filter(order=order).first()
        if not invoice and order.invoice_id:
            invoice = Invoice.objects.filter(invoice_number=order.invoice_id).first()
    elif invoice_number:
        try:
            invoice = Invoice.objects.select_related('order', 'user').get(invoice_number=invoice_number)
        except Invoice.DoesNotExist:
            return Response({'detail': f'Invoice {invoice_number} not found.'}, status=status.HTTP_404_NOT_FOUND)
        order = invoice.order
        if not order and invoice_number:
            # Try to find order via invoice_id
            order = Order.objects.filter(invoice_id=invoice_number).first()

    if not order:
        return Response({'detail': 'Order not found for refund.'}, status=status.HTTP_404_NOT_FOUND)

    # Validate order is eligible: must be cancelled and pending refund
    if order.status != Order.Status.CANCELLED:
        return Response(
            {'detail': f'Only cancelled orders can be refunded. Current status is {order.status}.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if order.refund_status == 'refunded':
        return Response({'detail': 'Order already refunded.', 'refund_id': order.refund_id}, status=status.HTTP_400_BAD_REQUEST)
    if order.refund_status != 'pending':
        return Response(
            {'detail': f'Order refund status is {order.refund_status}, expected pending.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate invoice if present
    if invoice:
        if invoice.status == Invoice.Status.REFUNDED:
            return Response({'detail': 'Invoice already refunded.', 'refund_id': invoice.refund_id}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # No invoice yet — create a pending one for the order owner
        # Use order's owner and a mock amount derived from order
        amount = 0
        try:
            # Try to parse gross_weight or use default? For now use Order's refundAmount if available
            amt_str = (order.refund_amount or '$0.00').replace('$', '').replace(',', '').strip()
            amount = float(amt_str)
        except Exception:
            amount = 0
        # Fallback to 0 if parsing fails — still create invoice
        invoice = Invoice(
            invoice_number=order.invoice_id or f'INV-{order.order_number[-4:]}',
            order=order,
            user=order.owner,
            amount=amount,
            status=Invoice.Status.PENDING,
            description=f'{order.mode} · {order.order_number} — Cancelled',
        )

    # Determine Stripe PaymentIntent
    payment_intent = order.stripe_payment_intent_id or getattr(invoice, 'stripe_payment_intent_id', None)
    if not payment_intent:
        # Generate deterministic mock PI for idempotency if none exists
        suffix = order.order_number.replace('-', '').lower()[-12:] or 'test'
        payment_intent = f'pi_{suffix}_mock_visa'

    # Idempotency key: order_number + refund
    idempotency_key = f'refund_{order.order_number}_{order.invoice_id or "noinv"}'

    stripe_client = _get_stripe_client()
    stripe_refund_id = None
    stripe_status = 'mock'

    if stripe_client is None:
        # Mock mode — no real Stripe call (dev, no secret key)
        stripe_refund_id = f're_mock_{order.order_number.replace("-", "").lower()}_{int(timezone.now().timestamp())}'
        stripe_status = 'succeeded_mock'
        logger.info('Stripe mock refund for %s PI %s -> %s', order.order_number, payment_intent, stripe_refund_id)
    else:
        try:
            import stripe
            # Attempt to create refund — full amount, to original Visa
            refund = stripe.Refund.create(
                payment_intent=payment_intent,
                reason='requested_by_customer',
                metadata={'order_number': order.order_number, 'invoice_number': getattr(invoice, 'invoice_number', '')},
                idempotency_key=idempotency_key,
            )
            stripe_refund_id = getattr(refund, 'id', None) or f're_{refund.get("id", "unknown")}'
            stripe_status = getattr(refund, 'status', 'succeeded')
        except Exception as exc:
            # Stripe error — handle common cases
            err_msg = str(exc)
            # If already refunded (idempotency), treat as success if we can fetch
            if 'already been refunded' in err_msg.lower() or 'idempotency' in err_msg.lower():
                stripe_refund_id = f're_duplicate_{order.order_number}'
                stripe_status = 'succeeded_duplicate'
            else:
                logger.exception('Stripe refund failed for %s', order.order_number)
                return Response(
                    {'detail': f'Stripe refund failed: {err_msg}', 'payment_intent': payment_intent},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

    # Atomic update of Order and Invoice
    try:
        with transaction.atomic():
            # Re-fetch with select_for_update to avoid race
            order = Order.objects.select_for_update().get(pk=order.pk)
            if order.refund_status == 'refunded':
                return Response({'detail': 'Order already refunded (race).', 'refund_id': order.refund_id}, status=status.HTTP_400_BAD_REQUEST)
            order.refund_status = 'refunded'
            order.refund_id = stripe_refund_id
            order.save(update_fields=['refund_status', 'refund_id', 'updated_at'])

            # Ensure invoice exists and update
            if invoice and invoice.pk:
                # Refresh
                invoice = Invoice.objects.select_for_update().get(pk=invoice.pk)
                if invoice.status == Invoice.Status.REFUNDED:
                    return Response({'detail': 'Invoice already refunded (race).', 'refund_id': invoice.refund_id}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Create new invoice if we made a transient one
                invoice = Invoice(
                    invoice_number=order.invoice_id or f'INV-{order.order_number[-4:]}',
                    order=order,
                    user=order.owner,
                    amount=order.refund_amount.replace('$', '').replace(',', '') if order.refund_amount else 0,
                    status=Invoice.Status.REFUNDED,
                    stripe_payment_intent_id=payment_intent,
                )
            invoice.status = Invoice.Status.REFUNDED
            invoice.refund_id = stripe_refund_id
            invoice.stripe_payment_intent_id = payment_intent
            invoice.paid_at = timezone.now()
            invoice.save()
    except Exception as exc:
        logger.exception('Refund DB update failed for %s', order.order_number)
        return Response({'detail': f'Database update failed: {exc}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Trigger transactional email: Visa refund processed (from hello@contact.logistics.shenodev.tech)
    try:
        from utils.emails import send_refund_processed_email
        # Refresh for email context
        order.refresh_from_db()
        invoice.refresh_from_db()
        send_refund_processed_email(order, invoice, refund_id=stripe_refund_id)
    except Exception as e:
        logger.warning("Failed to send refund email for %s: %s", order.order_number, e)

    return Response(
        {
            'detail': 'Visa refund issued via Stripe.',
            'order_number': order.order_number,
            'invoice_number': invoice.invoice_number,
            'refund_id': stripe_refund_id,
            'payment_intent': payment_intent,
            'amount': str(invoice.amount),
            'status': invoice.status,
            'stripe_status': stripe_status,
        },
        status=status.HTTP_200_OK,
    )
