"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views.
See: https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path
from app.views.upload import upload_file
from app.views.generate import generate_regex_tasks
from app.views.replace import replace_tasks
from app.views.download import download_file
from app.views.csrf import get_csrf_token
from app.views.preview_data import preview_data
from app.views.preview_replace import preview_replace_tasks

urlpatterns = [
    path("admin", admin.site.urls),
    path("api/upload", upload_file),
    path("api/preview_data", preview_data),
    path("api/generate-tasks", generate_regex_tasks),
    path("api/preview_replace", preview_replace_tasks),
    path("api/replace", replace_tasks),
    path("api/download", download_file),
    path("api/get-csrf", get_csrf_token),
]
