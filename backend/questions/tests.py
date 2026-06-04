"""
Smoke tests for deployment safety (Phase 6).

These are intentionally minimal end-to-end checks that the wiring works:
the health probe answers, and the API is closed to anonymous users. The full
login -> session -> submit-answer happy path lives in progress/tests.py.
"""

from django.test import TestCase


class HealthCheckTests(TestCase):
    def test_healthz_ok_without_auth(self):
        """The Railway/CI health probe must return 200 with no session."""
        resp = self.client.get('/api/v1/healthz')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {'status': 'ok'})


class ApiAuthGateTests(TestCase):
    def test_questions_list_rejects_anonymous(self):
        """The questions API must reject unauthenticated callers (401/403)."""
        resp = self.client.get('/api/v1/questions/')
        self.assertIn(resp.status_code, (401, 403))
