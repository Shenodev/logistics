# System Architecture: B2B Logistics Platform

## 1. Tech Stack Overview
*   **Frontend:** Nuxt 3, TypeScript, shadcn-vue, Tailwind CSS, Vite PWA (For Delivery App).
*   **Backend:** Python 3.11+, Django REST Framework (DRF).
*   **Database:** PostgreSQL.
*   **Gateway:** Cloudflare (Subdomain Routing).
*   **Payments:** Stripe (For processing refunds).
*   **Email:** Resend SDK.

## 2. Triple-Subdomain Architecture
*   **User Portal (`logistics.shenodev.tech`):** Read-only dashboard for customers to track automated orders, view history, and cancel *only* in Stage 1 ("Order Received"). No manual order creation.
*   **Admin Portal (`admin.logistics.shenodev.tech`):** Command center for dispatchers to manage fleet, track orders, process Visa refunds for cancelled orders, and view analytics. No manual order creation.
*   **Delivery PWA (`delivery.logistics.shenodev.tech`):** Mobile-first Progressive Web App for drivers. Includes Login/Signup, incoming order alerts (Accept/Reject), navigation details, status updates (Picked Up -> On the Way -> Delivered), and a direct "Call Customer" action.

## 3. Order Lifecycle & Cancellation Logic
*   **Cancellation Rule:** Users and Admins can ONLY cancel an order if its status is exactly Stage 1 (`Order Received` / `استلام الطلب`).
*   **Refund Logic:** If an order is cancelled, the system flags it for a refund. Admins process the refund directly back to the customer's Visa via Stripe API.