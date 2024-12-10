from django.shortcuts import redirect
from django.conf import settings
from survey.models import *
from .views import *
from django.contrib.auth.models import User


from django.utils.deprecation import MiddlewareMixin

class NoCacheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
