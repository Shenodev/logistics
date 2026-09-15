"""Vercel serverless entry point for the ShenoFlow Django API (WSGI)."""
import os
import sys

# Make the backend project root importable when this file runs as ``api/index.py``.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.management import call_command  # noqa: E402
import django  # noqa: E402

django.setup()

if os.environ.get('DJANGO_AUTO_MIGRATE', 'true').lower() == 'true':
    call_command('migrate', interactive=False)

# Vercel Python expects a WSGI app exposed as ``app``.
from config.wsgi import application as app  # noqa: E402