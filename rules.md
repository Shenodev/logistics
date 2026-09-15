# Development Rules & Guardrails

## 1. UI & Design System (Stitch UI)
*   Typography: 'Sora' (Headings), 'Inter' (Body).
*   Colors: Deep Slate (`#0F172A`), Surfaces (`#1E293B`), Electric Cyan (`#06B6D4`).
*   No 3D elements, rounded-xl corners, clean negative space.

## 2. Django Backend & API Standards
*   **DRF Serializers:** Strict validation and sanitization for all incoming request payloads.
*   **Database Optimization:** Use `select_related` and `prefetch_related` in Django ORM to prevent N+1 query problems (critical for 100k users).
*   **Security:** Enforce CSRF protection, CORS headers restricted to official subdomains, and secure password hashing (Argon2/PBKDF2).

## 3. Middleware & Routing Rules
*   Nuxt frontend must implement route middleware to intercept unauthenticated users and redirect to `/login`.
*   Admin subdomain (`admin.logistics.shenodev.tech`) must reject tokens lacking admin privileges at the layout/middleware level.