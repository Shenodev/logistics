import os

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

User = get_user_model()


def user_payload(user):
    # Prefer explicit role field; fall back to is_staff for legacy data
    raw_role = getattr(user, 'role', None)
    if raw_role in ('user', 'admin', 'driver'):
        role = raw_role
    else:
        role = 'admin' if getattr(user, 'is_staff', False) else 'user'
    return {
        'id': str(user.id),
        'email': user.email,
        'name': user.first_name or user.email,
        'role': role,
    }


def set_session_cookie(response, user):
    token = AccessToken.for_user(user)
    response.set_cookie(
        settings.AUTH_COOKIE_NAME,
        str(token),
        max_age=settings.AUTH_COOKIE_MAX_AGE,
        domain=settings.AUTH_COOKIE_DOMAIN,
        path='/',
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=True,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )


def set_refresh_cookie(response, user):
    token = RefreshToken.for_user(user)
    response.set_cookie(
        settings.AUTH_REFRESH_COOKIE_NAME,
        str(token),
        max_age=settings.AUTH_REFRESH_COOKIE_MAX_AGE,
        domain=settings.AUTH_COOKIE_DOMAIN,
        path='/',
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=True,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )


def clear_session_cookie(response):
    response.set_cookie(
        settings.AUTH_COOKIE_NAME,
        '',
        max_age=0,
        domain=settings.AUTH_COOKIE_DOMAIN,
        path='/',
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=True,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )


def clear_refresh_cookie(response):
    response.set_cookie(
        settings.AUTH_REFRESH_COOKIE_NAME,
        '',
        max_age=0,
        domain=settings.AUTH_COOKIE_DOMAIN,
        path='/',
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=True,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = str(request.data.get('email') or '').strip().lower()
    password = str(request.data.get('password') or '')

    if not email or not password:
        return Response(
            {'statusMessage': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=email, password=password)
    if user is None:
        return Response(
            {'statusMessage': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    response = Response({'user': user_payload(user)})
    set_session_cookie(response, user)
    set_refresh_cookie(response, user)
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    name = str(request.data.get('name') or '').strip()
    email = str(request.data.get('email') or '').strip().lower()
    password = str(request.data.get('password') or '')
    # Role-aware signup: delivery PWA posts driver role, portal defaults to user
    requested_role = str(request.data.get('role') or '').strip().lower()
    # Also support legacy `delivery` hint from client
    if not requested_role and 'driver' in request.headers.get('X-Portal', '').lower():
        requested_role = 'driver'
    role = requested_role if requested_role in ('user', 'driver') else 'user'
    # Never allow public signup to create admin
    if role == 'admin':
        role = 'user'

    if not name or not email or not password:
        return Response(
            {'statusMessage': 'Name, email and password are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if len(password) < 8:
        return Response(
            {'statusMessage': 'Password must be at least 8 characters'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    reserved = {
        os.environ.get('DJANGO_DEV_ADMIN_EMAIL', 'admin@sheno.dev'),
        os.environ.get('DJANGO_DEV_USER_EMAIL', 'user@sheno.dev'),
        os.environ.get('DJANGO_DEV_DRIVER_EMAIL', 'driver@sheno.dev'),
    }
    if email in reserved or User.objects.filter(email=email).exists():
        return Response(
            {'statusMessage': 'An account with this email already exists'},
            status=status.HTTP_409_CONFLICT,
        )

    try:
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name,
            role=role,
        )
    except Exception:
        return Response(
            {'statusMessage': 'An account with this email already exists'},
            status=status.HTTP_409_CONFLICT,
        )

    response = Response({'user': user_payload(user)}, status=status.HTTP_201_CREATED)
    set_session_cookie(response, user)
    set_refresh_cookie(response, user)
    return response


@api_view(['GET'])
def me_view(request):
    return Response({'user': user_payload(request.user)})


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_view(request):
    raw_token = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)
    if not raw_token:
        return Response(
            {'statusMessage': 'Refresh token missing'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        refresh = RefreshToken(raw_token)
        user = User.objects.get(pk=refresh['user_id'])
    except (TokenError, TypeError, KeyError, User.DoesNotExist):
        return Response(
            {'statusMessage': 'Refresh session expired, please sign in again'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    response = Response({'ok': True})
    set_session_cookie(response, user)
    set_refresh_cookie(response, user)
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    response = Response({'ok': True})
    clear_session_cookie(response)
    clear_refresh_cookie(response)
    return response