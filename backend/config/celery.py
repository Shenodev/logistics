import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
# Use Django settings for Celery config (CELERY_ prefix)
app.config_from_object('django.conf:settings', namespace='CELERY')
# Autodiscover tasks in all installed apps
app.autodiscover_tasks()

# Optional: ensure Upstash Redis uses TLS (rediss)
# Celery will use CELERY_BROKER_URL from settings
