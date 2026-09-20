import logging
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)

FROM_EMAIL = "hello@contact.logistics.shenodev.tech"
FROM_NAME = "Sheno Logistics"


def _get_resend_client():
    api_key = getattr(settings, "RESEND_API_KEY", "") or ""
    # Treat placeholder and empty as mock mode
    if not api_key or api_key.startswith("re_mock") or api_key == "test":
        return None
    try:
        import resend  # type: ignore
        resend.api_key = api_key
        return resend
    except Exception as exc:
        logger.warning("Resend init failed, falling back to console: %s", exc)
        return None


def _send_email(to: str, subject: str, html: str, text: Optional[str] = None) -> dict:
    """
    Sends email via Resend Python SDK from hello@contact.logistics.shenodev.tech.
    Falls back to console/log when RESEND_API_KEY is not configured (dev).
    Returns dict with id and status.
    """
    from_email = getattr(settings, "RESEND_FROM_EMAIL", FROM_EMAIL) or FROM_EMAIL
    from_name = getattr(settings, "RESEND_FROM_NAME", FROM_NAME) or FROM_NAME
    sender = f"{from_name} <{from_email}>"

    resend_client = _get_resend_client()
    if resend_client is None:
        # Mock mode — log and return mock id
        mock_id = f"mock_{to.replace('@','_').replace('.','_')}_{hash(subject) % 100000:05d}"
        logger.info(
            "[email] Mock send via %s to %s | subject: %s | id: %s",
            sender,
            to,
            subject,
            mock_id,
        )
        # Also print to console for dev visibility
        print(f"[Resend Mock] From: {sender} To: {to} Subject: {subject} | id: {mock_id}")
        return {"id": mock_id, "status": "mock_sent", "to": to, "subject": subject}

    try:
        import resend  # type: ignore

        params = {
            "from": sender,
            "to": [to],
            "subject": subject,
            "html": html,
        }
        if text:
            params["text"] = text

        result = resend.Emails.send(params)
        # Resend returns {"id": "..."}
        email_id = result.get("id") if isinstance(result, dict) else str(result)
        logger.info("[email] Sent via Resend to %s | subject: %s | id: %s", to, subject, email_id)
        return {"id": email_id, "status": "sent", "to": to, "subject": subject}
    except Exception as exc:
        logger.exception("Resend send failed to %s subject %s: %s", to, subject, exc)
        # Don't raise — email failure should not block order flow
        return {"id": None, "status": "failed", "error": str(exc), "to": to, "subject": subject}


def send_order_cancelled_email(order, recipient_email: Optional[str] = None) -> dict:
    """
    Triggered when an order is cancelled (Stage 1 only).
    Sends to order.owner.email.
    """
    to = recipient_email or getattr(getattr(order, "owner", None), "email", None) or getattr(order, "owner_email", None)
    if not to:
        logger.warning("No recipient for cancelled email for order %s", getattr(order, "order_number", "unknown"))
        return {"id": None, "status": "skipped", "reason": "no recipient"}

    subject = f"Order {order.order_number} Cancelled - Refund Pending"
    html = f"""
    <div style="font-family: Inter, sans-serif; color: #0f172a; max-width: 600px; margin: 0 auto;">
      <div style="background: #0f172a; color: #e2e8f0; padding: 20px; border-radius: 12px 12px 0 0;">
        <h1 style="margin: 0; font-size: 20px;">Sheno Logistics</h1>
        <p style="margin: 4px 0 0; color: #94a3b8; font-size: 13px;">Order Update • {order.order_number}</p>
      </div>
      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 0; padding: 24px; border-radius: 0 0 12px 12px;">
        <h2 style="margin: 0 0 8px; font-size: 18px; color: #0f172a;">Your order has been cancelled</h2>
        <p style="margin: 0 0 16px; color: #475569; line-height: 1.5;">
          Order <strong>{order.order_number}</strong> ({order.origin} → {order.destination}) was cancelled in Stage 1 (Order Received).
          It has been flagged for a Visa refund via Stripe. An admin will process the refund shortly.
        </p>
        <div style="background: #f1f5f9; border-radius: 8px; padding: 12px; margin: 0 0 16px;">
          <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">Order Details</div>
          <div style="margin-top: 6px; font-size: 14px; color: #0f172a;">
            <div><strong>Order:</strong> {order.order_number}</div>
            <div><strong>Route:</strong> {order.origin} ({order.origin_code}) → {order.destination} ({order.destination_code})</div>
            <div><strong>Cancelled at:</strong> {getattr(order, 'cancelled_at', '') or 'just now'}</div>
            <div><strong>Refund amount:</strong> {getattr(order, 'refund_amount', '') or 'TBD'}</div>
            <div><strong>Invoice:</strong> {getattr(order, 'invoice_id', '') or 'pending'}</div>
          </div>
        </div>
        <p style="margin: 0 0 16px; color: #475569; font-size: 14px;">
          No action is required. The refund will be issued to your original Visa via Stripe and will appear within 5–10 business days.
        </p>
        <a href="https://logistics.shenodev.tech/shipments/{order.order_number}" style="display: inline-block; background: #06b6d4; color: #083344; text-decoration: none; padding: 10px 18px; border-radius: 8px; font-weight: 600; font-size: 14px;">View Order</a>
        <p style="margin: 16px 0 0; color: #94a3b8; font-size: 12px;">If you did not request this cancellation, please contact support@sheno.dev.</p>
      </div>
      <p style="text-align: center; color: #94a3b8; font-size: 11px; margin-top: 12px;">Sent from {FROM_EMAIL} • Sheno Logistics • B2B Logistics Platform</p>
    </div>
    """
    text = (
        f"Order {order.order_number} Cancelled — Refund Pending\n"
        f"Order {order.order_number} ({order.origin} -> {order.destination}) was cancelled in Stage 1. "
        f"Refund amount {getattr(order, 'refund_amount', '')} will be issued to your Visa via Stripe.\n"
        f"Cancelled at: {getattr(order, 'cancelled_at', '')}\n"
        f"View: https://logistics.shenodev.tech/shipments/{order.order_number}\n"
    )
    return _send_email(to, subject, html, text)


def send_refund_processed_email(order, invoice, recipient_email: Optional[str] = None, refund_id: Optional[str] = None) -> dict:
    """
    Triggered when a Visa refund is successfully processed (admin issues refund).
    Sends to order.owner.email.
    """
    to = recipient_email or getattr(getattr(order, "owner", None), "email", None) or getattr(order, "owner_email", None)
    if not to:
        # Fallback to invoice user
        to = getattr(getattr(invoice, "user", None), "email", None) if invoice else None
    if not to:
        logger.warning("No recipient for refund email for order %s", getattr(order, "order_number", "unknown"))
        return {"id": None, "status": "skipped", "reason": "no recipient"}

    refund_display = refund_id or getattr(order, "refund_id", "") or getattr(invoice, "refund_id", "") or "pending"
    amount = getattr(order, "refund_amount", None) or (f"${invoice.amount}" if invoice and getattr(invoice, "amount", None) else "TBD")
    invoice_num = getattr(invoice, "invoice_number", None) or getattr(order, "invoice_id", "") or order.order_number

    subject = f"Refund Processed: Visa Refund for Order {order.order_number} - {amount}"
    html = f"""
    <div style="font-family: Inter, sans-serif; color: #0f172a; max-width: 600px; margin: 0 auto;">
      <div style="background: #0f172a; color: #e2e8f0; padding: 20px; border-radius: 12px 12px 0 0;">
        <h1 style="margin: 0; font-size: 20px;">Sheno Logistics</h1>
        <p style="margin: 4px 0 0; color: #94a3b8; font-size: 13px;">Refund Confirmation • {order.order_number}</p>
      </div>
      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 0; padding: 24px; border-radius: 0 0 12px 12px;">
        <div style="background: #f0fdf4; border: 1px solid #86efac; color: #166534; padding: 12px; border-radius: 8px; margin: 0 0 16px; display: flex; align-items: center; gap: 8px;">
          <span style="font-weight: 700;">✓ Visa refund successfully processed via Stripe</span>
        </div>
        <h2 style="margin: 0 0 8px; font-size: 18px; color: #0f172a;">Your Visa has been refunded</h2>
        <p style="margin: 0 0 16px; color: #475569; line-height: 1.5;">
          The cancelled order <strong>{order.order_number}</strong> has been refunded to your original Visa ending in <strong>4242</strong> via Stripe.
          The amount will appear within 5–10 business days.
        </p>
        <div style="background: #f1f5f9; border-radius: 8px; padding: 12px; margin: 0 0 16px;">
          <div style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">Refund Details</div>
          <div style="margin-top: 6px; font-size: 14px; color: #0f172a;">
            <div><strong>Order:</strong> {order.order_number}</div>
            <div><strong>Invoice:</strong> {invoice_num}</div>
            <div><strong>Refund ID:</strong> <span style="font-family: monospace;">{refund_display}</span></div>
            <div><strong>Amount:</strong> {amount}</div>
            <div><strong>Destination:</strong> Visa •••• 4242 via Stripe</div>
          </div>
        </div>
        <a href="https://logistics.shenodev.tech/shipments/{order.order_number}" style="display: inline-block; background: #06b6d4; color: #083344; text-decoration: none; padding: 10px 18px; border-radius: 8px; font-weight: 600; font-size: 14px;">View Order &amp; Invoice</a>
        <p style="margin: 16px 0 0; color: #94a3b8; font-size: 12px;">Questions? Contact support@sheno.dev or your admin dispatcher.</p>
      </div>
      <p style="text-align: center; color: #94a3b8; font-size: 11px; margin-top: 12px;">Sent from {FROM_EMAIL} • Sheno Logistics • B2B Logistics Platform</p>
    </div>
    """
    text = (
        f"Refund Processed: Visa Refund for Order {order.order_number}\n"
        f"Your cancelled order {order.order_number} has been refunded {amount} to Visa **** 4242 via Stripe.\n"
        f"Refund ID: {refund_display}\n"
        f"Invoice: {invoice_num}\n"
        f"View: https://logistics.shenodev.tech/shipments/{order.order_number}\n"
    )
    return _send_email(to, subject, html, text)
