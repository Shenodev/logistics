from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models


class DriverProfile(models.Model):
    class Availability(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        ON_DUTY = 'on_duty', 'On Duty'
        OFF_DUTY = 'off_duty', 'Off Duty'
        ON_BREAK = 'on_break', 'On Break'

    class VehicleType(models.TextChoices):
        SPRINTER_VAN = 'sprinter_van', 'Sprinter Van'
        BOX_TRUCK_5T = 'box_truck_5t', '5 Ton Box Truck'
        BOX_TRUCK_10T = 'box_truck_10t', '10 Ton Freight Rig'
        HEAVY_TRACTOR = 'heavy_tractor', 'Heavy Freight Tractor'
        EV_SPRINTER = 'ev_sprinter', 'EV Sprinter 350'
        VOLVO_FH_ELECTRIC = 'volvo_fh_electric', 'Volvo FH Electric 40T'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='driver_profile',
        limit_choices_to={'role': 'driver'},
        primary_key=True,
        help_text='Driver user (role=driver)',
    )
    license_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(r'^[A-Z0-9-]{5,20}$', 'Invalid license number')],
        help_text='CDL or local license',
    )
    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
        default=VehicleType.SPRINTER_VAN,
    )
    vehicle_plate = models.CharField(
        max_length=20,
        unique=True,
        help_text='License plate e.g. NY-784-KLP',
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r'^\+?[0-9\s().-]{7,25}$', 'Invalid phone')],
    )
    availability = models.CharField(
        max_length=10,
        choices=Availability.choices,
        default=Availability.AVAILABLE,
        db_index=True,
    )
    is_available = models.BooleanField(default=True, help_text='Quick toggle for dispatch board')
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=5.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text='Driver rating 0.0–5.0',
    )
    total_deliveries = models.PositiveIntegerField(default=0)
    acceptance_rate = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=100.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Acceptance rate %',
    )
    current_orders_count = models.PositiveSmallIntegerField(default=0)
    max_orders = models.PositiveSmallIntegerField(default=5, help_text='Max concurrent orders for capacity check')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__email']
        verbose_name = 'driver profile'
        verbose_name_plural = 'driver profiles'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=0) & models.Q(rating__lte=5),
                name='driver_rating_range',
            ),
            models.CheckConstraint(
                condition=models.Q(current_orders_count__lte=models.F('max_orders')),
                name='driver_capacity_check',
                violation_error_message='Driver is at max capacity',
            ),
        ]
        indexes = [
            models.Index(fields=['availability', 'is_available']),
        ]

    def __str__(self) -> str:
        return f'{self.user.email} — {self.get_vehicle_type_display()} ({self.vehicle_plate})'

    def clean(self):
        # Enforce linked user is driver role
        if self.user_id and hasattr(self.user, 'role') and self.user.role != 'driver':
            raise ValidationError({'user': 'DriverProfile user must have role=driver'})
        if self.current_orders_count > self.max_orders:
            raise ValidationError({'current_orders_count': 'Exceeds max_orders capacity'})

    @property
    def is_at_capacity(self) -> bool:
        return self.current_orders_count >= self.max_orders
