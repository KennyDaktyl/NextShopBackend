from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import include, path

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from web.accounts.views import UserLoginView, UserRegistrationViewSet


schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="API documentation for the Product app",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'users', UserRegistrationViewSet, basename='user')

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('sentry-debug/', trigger_error),
    path("anymail/", include("anymail.urls")),
    path("admin/", admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # User
    path('auth/', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.social.urls')),
    
    # path('login/', UserLoginView.as_view(), name='user-login'),
    # path('register/', UserRegistrationViewSet, name='user-registration'),

    # CMS
    path("cms/", include("web.cms.urls")),
    # Categories
    path("api/categories/", include("web.categories.urls")),
    # Carts
    path('api/carts/', include("web.carts.urls")),
    # Products
    path("api/products/", include("web.products.urls")),
    path("api/orders/", include("web.orders.urls")),
    path("api/accounts/", include("web.accounts.urls")),
    path("api/front/", include("web.front.urls")),
    path("api/deliveries/", include("web.deliveries.urls")),
    path("api/payments/", include("web.payments.urls")),
    path("api/articles/", include("web.articles.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
