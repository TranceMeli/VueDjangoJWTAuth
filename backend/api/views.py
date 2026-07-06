from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # type: ignore[import]
from rest_framework_simplejwt.tokens import AccessToken  # type: ignore[import]
from rest_framework.views import APIView  # type: ignore[import]
from rest_framework.response import Response  # type: ignore[import]
from rest_framework.decorators import api_view, permission_classes  # type: ignore[import]
from rest_framework.permissions import IsAuthenticated  # type: ignore[import]
from django.conf import settings  # type: ignore[import]
from django.contrib.auth import get_user_model  # type: ignore[import]
from api.serializers import CustomTokenObtainPairSerializer

User = get_user_model()

REFRESH_COOKIE_NAME = 'refresh_token'
REFRESH_COOKIE_PATH = '/api/token/refresh/'


def _set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
        path=REFRESH_COOKIE_PATH,
    )


class CookieTokenObtainPairView(TokenObtainPairView):
    """Logs the user in and moves the refresh token into an HttpOnly cookie."""

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh_token = response.data.pop('refresh', None)
            if refresh_token:
                _set_refresh_cookie(response, refresh_token)
        return response


class CookieTokenRefreshView(TokenRefreshView):
    """Reads the refresh token from the cookie, rotates it, and re-attaches the user's role."""

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(REFRESH_COOKIE_NAME)
        if refresh_token:
            request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            new_refresh = response.data.pop('refresh', None)
            if new_refresh:
                _set_refresh_cookie(response, new_refresh)

            # Determine the role from the freshly issued access token instead of
            # decoding the (soon to be blacklisted) refresh token separately —
            # simpler and avoids relying on rotation timing.
            is_admin = False
            new_access = response.data.get('access')
            if new_access:
                try:
                    user_id = AccessToken(new_access)['user_id']
                    user = User.objects.get(id=user_id)
                    is_admin = user.is_staff
                except (User.DoesNotExist, KeyError):
                    is_admin = False
            response.data['isAdmin'] = is_admin

        return response


class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "Logged out successfully"})
        response.delete_cookie(REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)
        return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({
        "message": "Success! You have access to this protected data.",
        "user": request.user.username,
    })