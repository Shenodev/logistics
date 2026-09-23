"""Vercel serverless entry point for the ShenoFlow Django API (WSGI)."""
import logging
import os
import sys

# Make the backend project root importable when this file runs as ``api/index.py``.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.management import call_command  # noqa: E402
import django  # noqa: E402

django.setup()

logger = logging.getLogger(__name__)

if os.environ.get('DJANGO_AUTO_MIGRATE', 'true').lower() == 'true':
    try:
        call_command('migrate', interactive=False)
    except Exception as exc:  # noqa: BLE001
        # Never crash Vercel import on migration failure — log and continue.
        # Most common: InconsistentMigrationHistory when admin.0001 was recorded
        # before accounts.0001 on an old Supabase DB (custom AUTH_USER_MODEL
        # requires 'accounts' before 'django.contrib.admin' in INSTALLED_APPS).
        # The app can still serve reads; heal via one-off SQL below.
        logger.warning("Auto-migrate skipped due to %s: %s", type(exc).__name__, exc)
        # Optional auto-heal attempt for the known swapped-user case.
        # Delete the early admin entry so the next deploy can re-apply in correct order.
        # Safe: admin tables already exist; --fake re-records history without DDL.
        try:
            from django.db import connection
            from django.db.migrations.exceptions import InconsistentMigrationHistory

            if isinstance(exc, InconsistentMigrationHistory) and 'accounts.0001_initial' in str(exc):
                with connection.cursor() as cur:
                    cur.execute("DELETE FROM django_migrations WHERE app='admin' AND name='0001_initial'")
                    # contenttypes/admin ordering sometimes also inconsistent
                    cur.execute("DELETE FROM django_migrations WHERE app='admin' AND name='0002_logentry_remove_auto_add'")
                    cur.execute("DELETE FROM django_migrations WHERE app='admin' AND name='0003_logentry_add_action_flag_choices'")
                call_command('migrate', '--fake-initial', interactive=False, verbosity=0)
                logger.warning("Auto-heal: re-faked admin migrations after clearing early rows")
        except Exception as heal_exc:  # noqa: BLE001
            logger.warning("Auto-heal failed: %s", heal_exc)

# Ensure demo accounts exist on production (Supabase) so logins never show invalid credentials.
# Lightweight: only creates 3 hardcoded users if missing; no Faker data on cold start.
# Rich data (57 orders/24 invoices) seeded via ./setup.sh or manual `python manage.py seed_demo --clear`
# on Supabase. This block fixes the "invalid credentials" seen on user/admin portals.
if os.environ.get('DJANGO_AUTO_SEED_DEMO', 'true').lower() == 'true':
    try:
        from django.contrib.auth import get_user_model

        User = get_user_model()
        demo_seed = [
            ('user@shenodev.tech', 'user123', 'user', 'Demo Shipper', False),
            ('admin@shenodev.tech', 'admin123', 'admin', 'Demo Admin', True),
            ('delivery@shenodev.tech', 'delivery123', 'driver', 'Demo Driver', False),
        ]
        for email, pwd, role, first_name, is_staff in demo_seed:
            u, created = User.objects.get_or_create(
                username=email, defaults={'email': email, 'first_name': first_name, 'role': role, 'is_staff': is_staff}
            )
            # Heal existing: ensure email/role/password correct even if created earlier with wrong domain
            needs_save = False
            if u.email != email:
                u.email = email
                needs_save = True
            if getattr(u, 'role', None) != role:
                u.role = role
                needs_save = True
            if u.is_staff != is_staff and role == 'admin':
                u.is_staff = is_staff
                needs_save = True
            if not u.is_active:
                u.is_active = True
                needs_save = True
            # Always reset password to demo value so stakeholder one-click works
            # (cheap: set_password hashes; only when missing or on every cold start to self-heal)
            try:
                if not u.check_password(pwd):
                    u.set_password(pwd)
                    needs_save = True
            except Exception:
                u.set_password(pwd)
                needs_save = True
            if created or needs_save:
                u.save()
                logger.warning("Auto-seed demo user %s (created=%s)", email, created)
    except Exception as seed_exc:  # noqa: BLE001
        logger.warning("Auto-seed demo accounts skipped: %s", seed_exc)

# Vercel Python expects a WSGI app exposed as ``app``.
from config.wsgi import application as app  # noqa: E402
