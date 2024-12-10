from django.contrib import admin
from django.http import Http404
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),  # new
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include('survey.urls')),
    path("survey/", include("survey.urls")),


]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
