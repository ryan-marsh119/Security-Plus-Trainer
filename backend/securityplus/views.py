"""
securityplus/views.py

Project-level views that don't belong to a specific app:

    healthz    -- unauthenticated liveness probe for Railway / CI health checks.
    spa_index  -- serves the built React index.html for any non-API/admin/static
                  path so React Router can handle client-side deep links.

Both are plain Django views (not DRF) so the global DRF IsAuthenticated default
does not apply to them.
"""

from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound


def healthz(request):
    """GET /api/v1/healthz -> 200 {"status": "ok"}. No auth, no DB access."""
    return JsonResponse({'status': 'ok'})


def spa_index(request):
    """
    Catch-all that returns the React app's index.html so client-side routes
    (e.g. /dashboard, /study) resolve on a hard refresh or direct link.

    The combined production image builds the SPA into FRONTEND_BUILD_DIR. In a
    pure-backend dev setup (no build present) this returns a 404 with a hint,
    since the SPA is served by the Vite dev server instead.
    """
    index_file = settings.FRONTEND_BUILD_DIR / 'index.html'
    if not index_file.exists():
        return HttpResponseNotFound(
            'SPA build not found. Run the Vite dev server, or build the '
            'combined image which bundles the frontend.'
        )
    return HttpResponse(index_file.read_text(encoding='utf-8'), content_type='text/html')
