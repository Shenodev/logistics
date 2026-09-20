from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'User'
        ADMIN = 'admin', 'Admin'
        DRIVER = 'driver', 'Driver'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        db_index=True,
        help_text='User role for portal routing and permissions',
    )

    # Keep email unique for login; AbstractUser already has email field
    # Ensure email is required and unique at DB level for driver/user distinction
    email = models.EmailField(unique=True)

    class Meta:
        ordering = ['email']
        verbose_name = 'user'
        verbose_name_plural = 'users'

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN or self.is_staff

    @property
    def is_driver(self) -> bool:
        return self.role == self.Role.DRIVER

    def save(self, *args, **kwargs):
        # Keep is_staff in sync with admin role for Django admin access
        if self.role == self.Role.ADMIN and not self.is_staff:
            self.is_staff = True
        # Non-admins should not have staff flag unless explicitly set
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.email} ({self.get_role_display()})'
