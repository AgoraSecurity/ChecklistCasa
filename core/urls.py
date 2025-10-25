"""
URL configuration for Housing Evaluation System.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("projects/", include("projects.urls")),
    path("user/", include("accounts.urls")),
    path('health/', views.health_check, name='health_check'),
    path('health/basic/', views.basic_health_check, name='basic_health_check'),
    path("tos/", views.terms_of_service, name="terms_of_service"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("", views.home_view, name="home"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
