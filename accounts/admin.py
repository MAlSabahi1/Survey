from django.contrib import admin
from django.apps import apps
from django.contrib.auth.models import User, Group


app_models = apps.get_app_config('survey').get_models()  # Replace 'myapp' with your app's name

