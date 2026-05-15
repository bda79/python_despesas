# middleware.py
import time
import logging

logger = logging.getLogger(__name__)


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
