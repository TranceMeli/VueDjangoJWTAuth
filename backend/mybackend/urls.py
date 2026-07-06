from django.contrib import admin  # type: ignore
from django.urls import path  # type: ignore
from api.views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
    protected_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/protected/', protected_view, name='protected_view'),
]