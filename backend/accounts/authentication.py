from django.conf import settings

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class SessionCookieJWTAuthentication(JWTAuthentication):
    """Accepts a JWT from the ``shenoflow_session`` cookie as a fallback
    to the standard ``Authorization: Bearer`` header."""

    def authenticate(self, request):
        header = self.get_header(request)
        raw_token = self.get_raw_token(header) if header is not None else None
        cookie_token = request.COOKIES.get(settings.AUTH_COOKIE_NAME)

        token = raw_token or cookie_token
        if token is None:
            return None

        try:
            validated_token = self.get_validated_token(token)
        except Exception as exc:
            raise AuthenticationFailed('Invalid or expired session') from exc

        return self.get_user(validated_token), validated_token