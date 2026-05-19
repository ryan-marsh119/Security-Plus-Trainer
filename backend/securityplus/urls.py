"""
securityplus/urls.py

Root URL configuration. All application routes live under /api/v1/.
The Django admin is mounted at /admin/ for development convenience.

URL layout:
    /admin/              -- Django admin interface
    /api/v1/auth/        -- users.urls  (login, logout, register, me)
    /api/v1/             -- questions.urls  (domains, objectives, questions)
    /api/v1/             -- progress.urls   (sessions, answers, results, progress)
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/', include('questions.urls')),
    path('api/v1/', include('progress.urls')),
]
