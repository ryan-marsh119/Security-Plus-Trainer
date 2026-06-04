"""
securityplus/urls.py

Root URL configuration. All application routes live under /api/v1/.
The Django admin is mounted at /admin/ for development convenience.

URL layout:
    /admin/              -- Django admin interface
    /api/v1/healthz      -- unauthenticated health check
    /api/v1/auth/        -- users.urls  (login, logout, register, me)
    /api/v1/             -- questions.urls  (domains, objectives, questions)
    /api/v1/             -- progress.urls   (sessions, answers, results, progress)
    everything else      -- React SPA index.html (client-side routing)
"""

from django.contrib import admin
from django.urls import path, re_path, include
from .views import healthz, spa_index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/healthz', healthz, name='healthz'),
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/', include('questions.urls')),
    path('api/v1/', include('progress.urls')),
    # SPA fallback — must be LAST. Excludes api/, admin/, static/ so those route
    # normally (whitenoise also serves /static/ before URL resolution anyway).
    re_path(r'^(?!api/|admin/|static/).*$', spa_index, name='spa-index'),
]
