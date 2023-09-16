from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from cvgezgini.api import urls as api_urls
urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include(api_urls, namespace='api')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        'api/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),
]

