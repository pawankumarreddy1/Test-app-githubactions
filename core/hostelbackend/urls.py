"""
URL configuration for hostelbackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Hostel Management API",
        default_version="v1",
        description="API documentation for Hostel Management CRUD operations",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    url="http://34.207.251.160",
)


urlpatterns = [
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("admin/", admin.site.urls),
    path("api/", include("apps.hostelinfo.urls")),
    path("api/", include("apps.hostelmanagement.urls")),
    path("api/", include("apps.roomallocate.urls")),
    path("api/", include("apps.feemanagement.urls")),
    path("api/", include("apps.reports.urls")),
    path("api/", include("apps.messmanagement.urls")),
    path("api/", include("apps.expenses.urls")),
]

# Serve static files in production
# Note: In production, we need to serve static files manually since DEBUG=False
from django.views.static import serve
from django.urls import re_path

# Add static file serving for production
urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
