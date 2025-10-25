import logging
import time
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from projects.models import Project

logger = logging.getLogger(__name__)


def home_view(request):
    """
    Smart home page that shows different content based on user state:
    - Not authenticated: Landing page with sign up/login
    - Authenticated but no projects: Create project prompt
    - Authenticated with projects but no active project: Project selection
    - Authenticated with active project: Log new visit prompt
    """
    logger.info(
        f"Home view accessed by user: {request.user.email if request.user.is_authenticated else 'anonymous'}"
    )

    if not request.user.is_authenticated:
        # User not logged in - show landing page
        return render(
            request,
            "home.html",
            {
                "user_state": "anonymous",
                "primary_action": "signup",
                "secondary_action": "login",
            },
        )

    # User is authenticated - check their project status
    user_projects = Project.objects.filter(
        Q(owner=request.user) | Q(collaborators=request.user)
    ).distinct()

    active_projects = user_projects.filter(status="active")

    if not user_projects.exists():
        # User has no projects - prompt to create one
        return render(
            request,
            "home.html",
            {"user_state": "no_projects", "primary_action": "create_project"},
        )

    if not active_projects.exists():
        # User has projects but none are active - show project list
        finished_projects = user_projects.filter(status="finished")
        return render(
            request,
            "home.html",
            {
                "user_state": "no_active_projects",
                "finished_projects": finished_projects,
                "primary_action": "create_project",
                "secondary_action": "view_projects",
            },
        )

    # User has active projects
    if active_projects.count() == 1:
        # Single active project - show visit logging prompt
        active_project = active_projects.first()
        recent_visits = active_project.visits.all()[:3]

        return render(
            request,
            "home.html",
            {
                "user_state": "single_active_project",
                "active_project": active_project,
                "recent_visits": recent_visits,
                "primary_action": "log_visit",
                "secondary_action": "view_project",
            },
        )
    else:
        # Multiple active projects - show project selection
        return render(
            request,
            "home.html",
            {
                "user_state": "multiple_active_projects",
                "active_projects": active_projects,
                "primary_action": "view_projects",
                "secondary_action": "create_project",
            },
        )


@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    Returns HTTP 200 if the application is healthy, 503 if not.
    """
    start_time = time.time()
    health_status = {"status": "healthy", "timestamp": int(time.time()), "checks": {}}

    overall_healthy = True

    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful",
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
        }
        overall_healthy = False

    # Check cache (if configured) - don't fail overall health for cache issues
    try:
        cache.set("health_check_test", "ok", 10)
        cache_result = cache.get("health_check_test")
        if cache_result == "ok":
            health_status["checks"]["cache"] = {
                "status": "healthy",
                "message": "Cache is working",
            }
        else:
            health_status["checks"]["cache"] = {
                "status": "unhealthy",
                "message": "Cache read/write test failed",
            }
            # Don't fail overall health for cache issues
    except Exception as e:
        health_status["checks"]["cache"] = {
            "status": "unhealthy",
            "message": f"Cache error: {str(e)}",
        }
        # Don't fail overall health for cache issues

    # Check static files directory
    try:
        static_root = Path(settings.STATIC_ROOT)
        if static_root.exists() and static_root.is_dir():
            health_status["checks"]["static_files"] = {
                "status": "healthy",
                "message": "Static files directory accessible",
            }
        else:
            health_status["checks"]["static_files"] = {
                "status": "unhealthy",
                "message": "Static files directory not accessible",
            }
            overall_healthy = False
    except Exception as e:
        health_status["checks"]["static_files"] = {
            "status": "unhealthy",
            "message": f"Static files check failed: {str(e)}",
        }
        overall_healthy = False

    # Calculate response time
    response_time = round((time.time() - start_time) * 1000, 2)
    health_status["response_time_ms"] = response_time

    # Set overall status
    if not overall_healthy:
        health_status["status"] = "unhealthy"

    # Return appropriate HTTP status code
    status_code = 200 if overall_healthy else 503

    return JsonResponse(health_status, status=status_code)


@require_http_methods(["GET", "HEAD"])
def basic_health_check(request):
    """
    Basic health check endpoint for Docker healthcheck.
    Only checks database connectivity for fast response.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=503)


def terms_of_service(request):
    """Terms of Service page."""
    logger.info(
        f"Terms of Service accessed by user: {request.user.email if request.user.is_authenticated else 'anonymous'}"
    )
    return render(request, "legal/terms_of_service.html")


def privacy_policy(request):
    """Privacy Policy page."""
    logger.info(
        f"Privacy Policy accessed by user: {request.user.email if request.user.is_authenticated else 'anonymous'}"
    )
    return render(request, "legal/privacy_policy.html")
