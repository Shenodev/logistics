import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = 'Create or update the seeded development users'

    def handle(self, *args, **options):
        users = [
            {
                'username': os.environ.get('DJANGO_DEV_ADMIN_EMAIL', 'admin@sheno.dev'),
                'email': os.environ.get('DJANGO_DEV_ADMIN_EMAIL', 'admin@sheno.dev'),
                'first_name': 'Sheno Admin',
                'password': os.environ.get('DJANGO_DEV_ADMIN_PASSWORD', 'admin123'),
                'is_staff': True,
            },
            {
                'username': os.environ.get('DJANGO_DEV_USER_EMAIL', 'user@sheno.dev'),
                'email': os.environ.get('DJANGO_DEV_USER_EMAIL', 'user@sheno.dev'),
                'first_name': 'Sheno User',
                'password': os.environ.get('DJANGO_DEV_USER_PASSWORD', 'user123'),
                'is_staff': False,
            },
        ]

        for data in users:
            password = data.pop('password')
            is_staff = data.pop('is_staff')
            user, created = User.objects.get_or_create(username=data['username'], defaults=data)
            if not created:
                for key, value in data.items():
                    setattr(user, key, value)
            user.is_staff = is_staff
            user.set_password(password)
            user.save()

            action = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f'{action} {data["username"]} (role: {"admin" if is_staff else "user"})'))