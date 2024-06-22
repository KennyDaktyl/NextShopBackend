from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import include, path

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from web.accounts.views import UserLoginView, UserRegistrationView


schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API documentation for the Product app",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # User
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.social.urls')),
    
    # path('login/', UserLoginView.as_view(), name='user-login'),
    # path('register/', UserRegistrationView.as_view(), name='user-registration'),

    # Products
    path("api/products/", include("web.products.urls")),
    path("api/orders/", include("web.orders.urls")),
    path("api/accounts/", include("web.accounts.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
