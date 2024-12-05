from django.contrib import admin
from django.apps import apps


app_models = apps.get_app_config('survey').get_models()  # Replace 'myapp' with your app's name


for model in app_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        # Skip already registered models to avoid errors
        pass

