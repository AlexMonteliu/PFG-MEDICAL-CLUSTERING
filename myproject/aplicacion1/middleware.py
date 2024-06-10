from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            current_url = resolve(request.path_info).url_name
            if current_url not in ['login', 'admin', 'static']:
                return redirect(settings.LOGIN_URL)
        response = self.get_response(request)
        return response
