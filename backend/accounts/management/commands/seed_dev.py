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
                'role': 'admin',
                'is_staff': True,
            },
            {
                'username': os.environ.get('DJANGO_DEV_USER_EMAIL', 'user@sheno.dev'),
                'email': os.environ.get('DJANGO_DEV_USER_EMAIL', 'user@sheno.dev'),
                'first_name': 'Sheno User',
                'password': os.environ.get('DJANGO_DEV_USER_PASSWORD', 'user123'),
                'role': 'user',
                'is_staff': False,
            },
            {
                'username': os.environ.get('DJANGO_DEV_DRIVER_EMAIL', 'driver@sheno.dev'),
                'email': os.environ.get('DJANGO_DEV_DRIVER_EMAIL', 'driver@sheno.dev'),
                'first_name': 'Sheno Driver',
                'password': os.environ.get('DJANGO_DEV_DRIVER_PASSWORD', 'driver123'),
                'role': 'driver',
                'is_staff': False,
            },
        ]

        for data in users:
            password = data.pop('password')
            role = data.pop('role', 'user')
            is_staff = data.pop('is_staff', False)
            user, created = User.objects.get_or_create(username=data['username'], defaults={**data, 'role': role, 'is_staff': is_staff})
            if not created:
                for key, value in data.items():
                    setattr(user, key, value)
                user.role = role
            user.is_staff = is_staff or role == 'admin'
            user.set_password(password)
            user.save()

            action = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f'{action} {data["username"]} (role: {role})'))