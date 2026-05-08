# middleware.py
import time
from django.conf import settings
from django.contrib.auth import logout


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
