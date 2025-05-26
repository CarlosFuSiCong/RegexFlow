"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from app.views.upload import upload_file
from app.views.generate import generate_regex_tasks
from app.views.replace import replace_tasks
from app.views.download import download_file
from app.views.csrf import get_csrf_token


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/upload/", upload_file),
    path("api/generate-tasks/", generate_regex_tasks),
    path("api/replace/", replace_tasks),
    path("api/download/", download_file),
    path("api/get-csrf/", get_csrf_token),
]
