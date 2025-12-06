from django.shortcuts import redirect
from django.urls import resolve
import datetime
from django.contrib.auth import logout
from django.utils import timezone


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            # Check if the current URL is not the login page
            current_url = resolve(request.path_info).url_name
            if current_url != 'login':
                # Redirect to the login page
                return self.logout(request)

        response = self.get_response(request)
        return response

    def logout(self, request):
        logout(request)
        return redirect('Auth:login')


class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            last_activity_str = request.session.get('last_activity')

            if last_activity_str:
                last_activity = datetime.datetime.strptime(last_activity_str, '%Y-%m-%dT%H:%M:%S.%f%z')
                idle_duration = (timezone.now() - last_activity).seconds

                if idle_duration > 60 * 15:
                    return self.logout(request)

            request.session['last_activity'] = timezone.now().isoformat()

        return response

    def logout(self, request):
        logout(request)
        return redirect('Auth:login')