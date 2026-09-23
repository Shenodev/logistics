# Development Rules & Guardrails

## 1. UI & Design System (Stitch UI)
*   **Theme:** Deep Slate (`#0F172A`), Surfaces (`#1E293B`), Electric Cyan (`#06B6D4`).
*   **Delivery App Specifics:** MUST be Mobile-First. Use large touch targets (min 48px height), bottom navigation bars, and simplified typography for outdoor readability.

## 2. Business Logic Guardrails (CRITICAL)
*   **No Order Creation:** Remove ALL forms, buttons, and API endpoints related to users or admins manually creating shipments. Orders are assumed to be ingested via external APIs.
*   **Cancellation State Machine:** The "Cancel Order" button in User and Admin dashboards MUST be disabled and hidden if the order status progresses past "Order Received".
*   **Billing/Refunds:** Users do not pay manually within the app. Billing details are kept strictly to log previous transactions and allow Admins to issue Visa refunds for cancelled orders.

## 3. Django Backend & API Standards
*   Use `select_related` for performance.
*   Enforce CSRF and strict DRF permissions across all 3 roles (`User`, `Admin`, `Driver`).