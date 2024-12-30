from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.timezone import now
from datetime import timedelta

# Middleware to monitor user activity and enforce session timeout
class SessionSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            timeout_seconds = 300  # Session timeout in seconds (e.g., 5 minutes)

            if last_activity:
                elapsed_time = (now() - last_activity).total_seconds()
                if elapsed_time > timeout_seconds:
                    del request.session['last_activity']
                    return redirect('logout')  # Redirect to logout or login page

            request.session['last_activity'] = now()

        response = self.get_response(request)
        return response
