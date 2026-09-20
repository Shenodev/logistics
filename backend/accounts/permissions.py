from rest_framework.permissions import BasePermission


def _get_role(user):
    # Prefer explicit role, fallback to is_staff
    role = getattr(user, 'role', None)
    if role in ('user', 'admin', 'driver'):
        return role
    if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
        return 'admin'
    return 'user'


class IsAdmin(BasePermission):
    """Only users with role=admin (or is_staff) can access."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and _get_role(request.user) == 'admin'
        )


class IsDriver(BasePermission):
    """Only users with role=driver."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and _get_role(request.user) == 'driver'
        )


class IsAdminOrDriver(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and _get_role(request.user) in ('admin', 'driver')
        )


class IsOrderOwnerOrAdmin(BasePermission):
    """Object-level: owner of the order or admin."""

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if _get_role(request.user) == 'admin':
            return True
        # obj is Order
        return getattr(obj, 'owner_id', None) == request.user.id


class IsAssignedDriver(BasePermission):
    """
    Object-level: driver can only operate on orders assigned to them.
    Used for driver status updates (picked_up → delivered).
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if _get_role(request.user) != 'driver':
            return False
        # obj is Order
        return getattr(obj, 'driver_id', None) == request.user.id


class IsAssignedDriverOrAdmin(BasePermission):
    """Allow admin or the assigned driver of the order."""

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        role = _get_role(request.user)
        if role == 'admin':
            return True
        if role == 'driver' and getattr(obj, 'driver_id', None) == request.user.id:
            return True
        return False


class IsDriverAssignedOrUnassignedPool(BasePermission):
    """
    For accept: driver may accept an unassigned received order (pool)
    OR an order already assigned to them. Used as object-level gate for accept/reject.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if _get_role(request.user) != 'driver':
            return False
        # Unassigned pool: status received and no driver
        if getattr(obj, 'driver_id', None) is None and getattr(obj, 'status', None) == 'received':
            return True
        # Already assigned to this driver
        if getattr(obj, 'driver_id', None) == request.user.id:
            return True
        return False
