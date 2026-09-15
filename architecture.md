# System Architecture: B2B Logistics Platform (Enterprise & Cost-Optimized)

## 1. Tech Stack Overview
*   **Frontend:** Nuxt 3 (Vue 3 Composition API), TypeScript, shadcn-vue, Tailwind CSS.
*   **Backend:** Python 3.11+, Django REST Framework (DRF), Django JWT (SimpleJWT).
*   **Database:** PostgreSQL (Hosted on Supabase/Neon Free Tier).
*   **Caching & Performance:** Upstash Redis (Free Tier) / Django LocMem Cache.
*   **Infrastructure / Gateway:** Cloudflare (Free WAF, CDN, Rate Limiting, Subdomain Routing).
*   **Email Provider:** Resend SDK.
*   **Project name in logo:** ShenoFlow
*   **Project logo url:** /Logo Icon.png
*   **Project icon url:** /Logo Icon.png (but fix it's size)

## 2. Subdomain Routing & Multi-Tenant Architecture
*   **User/Customer Portal:** `logistics.shenodev.tech` (Nuxt App - User Dashboard, Tracking, Billing).
*   **Admin/Dispatcher Portal:** `admin.logistics.shenodev.tech` (Nuxt App - Command Center, Fleet, Analytics).
*   **Backend API Service:** `api.logistics.shenodev.tech` (Django REST API).

## 3. Communication & Security Flow
*   **Auth:** JWT stored in Secure, HttpOnly, SameSite Cookies.
*   **RBAC Middleware:** Django permission classes enforcing strict separation between `Shipper` (User) and `Dispatcher/Admin` roles.