"""
URL configuration for Housing Evaluation System.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.views.decorators.cache import cache_control

@cache_control(max_age=86400)  # Cache for 24 hours
def service_worker(request):
    """Serve the service worker file."""
    with open(settings.BASE_DIR / 'static' / 'sw.js', 'r') as f:
        content = f.read()
    return HttpResponse(content, content_type='application/javascript')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('projects/', include('projects.urls')),
    path('user/', include('accounts.urls')),
    path('sw.js', service_worker, name='service_worker'),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
