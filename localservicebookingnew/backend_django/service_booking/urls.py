from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT token refresh
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Google OAuth / allauth
    path('accounts/', include('allauth.urls')),

    # All app routes
    path('', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
