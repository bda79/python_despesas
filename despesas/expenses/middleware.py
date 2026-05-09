# middleware.py
import time
from django.conf import settings
from django.contrib.auth import logout
import logging

logger = logging.getLogger(__name__)


class SessionIdleTimeout:
    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = getattr(settings, "SESSION_COOKIE_AGE", 300)

    def __call__(self, request):
        if request.user.is_authenticated:
            current_time = time.time()
            last_activity = request.session.get("last_activity", current_time)

            if current_time - last_activity > self.timeout:
                logout(request)
            else:
                request.session["last_activity"] = current_time

        return self.get_response(request)


class SlowRequestMiddleware:
    """
    Detecta requests lentas e registra no terminal.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        # Tempo em segundos
        if duration > 1.5:
            logger.warning(
                f"[SLOW REQUEST] {request.method} {request.path} "
                f"levou {duration:.2f}s"
            )

        # Header opcional
        response["X-Request-Duration"] = f"{duration:.2f}s"

        return response
