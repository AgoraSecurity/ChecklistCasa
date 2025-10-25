import logging
import time

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Middleware to log all incoming requests."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        # Log the incoming request
        logger.info(
            f"Request: {request.method} {request.path} "
            f"from {self.get_client_ip(request)} "
            f"User: {request.user.email if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous'}"
        )

        response = self.get_response(request)

        # Log the response
        duration = round((time.time() - start_time) * 1000, 2)
        logger.info(
            f"Response: {response.status_code} for {request.method} {request.path} "
            f"in {duration}ms"
        )

        return response

    def get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
