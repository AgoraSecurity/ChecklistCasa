import logging
import time

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Intelligent middleware to log important requests and errors."""

    def __init__(self, get_response):
        self.get_response = get_response

        # Paths to always log (important business operations)
        self.important_paths = {
            "/accounts/login/",
            "/accounts/logout/",
            "/accounts/signup/",
            "/accounts/confirm-email/",
            "/accounts/password/reset/",
            "/projects/",
        }

        # Paths to never log (noise)
        self.ignore_paths = {
            "/health/",
            "/health/basic/",
            "/static/",
            "/media/",
            "/favicon.ico",
        }

    def __call__(self, request):
        start_time = time.time()
        should_log = self._should_log_request(request)

        if should_log:
            user_info = self._get_user_info(request)
            logger.info(
                f"→ {request.method} {request.path} | {user_info} | IP: {self._get_client_ip(request)}"
            )

        response = self.get_response(request)

        # Always log errors, slow requests, or important operations
        duration = round((time.time() - start_time) * 1000, 2)

        if (
            response.status_code >= 400
            or duration > 1000
            or should_log  # Slow requests (>1s)
        ):

            status_emoji = "✅" if response.status_code < 400 else "❌"
            user_info = self._get_user_info(request)

            logger.info(
                f"{status_emoji} {response.status_code} {request.method} {request.path} | "
                f"{user_info} | {duration}ms"
            )

            # Log additional context for errors
            if response.status_code >= 400:
                logger.warning(
                    f"Error details: {request.method} {request.path} returned {response.status_code}"
                )

        return response

    def _should_log_request(self, request):
        """Determine if this request should be logged."""
        path = request.path

        # Skip health checks and static files
        if any(path.startswith(ignore) for ignore in self.ignore_paths):
            return False

        # Always log important authentication/business operations
        if any(path.startswith(important) for important in self.important_paths):
            return True

        # Log POST requests (form submissions, API calls)
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            return True

        return False

    def _get_user_info(self, request):
        """Get meaningful user information."""
        if not hasattr(request, "user"):
            return "No user context"

        if request.user.is_authenticated:
            return f"User: {request.user.email}"
        else:
            return "Anonymous"

    def _get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")
