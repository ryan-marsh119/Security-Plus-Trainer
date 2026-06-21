"""
Auth endpoint tests (BE-14 #13). Covers register (happy + validation), login
(bad credentials), the /auth/me/ session gate, and logout clearing the session.
"""

import json

from django.contrib.auth.models import User
from django.test import TestCase


class AuthTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.existing = User.objects.create_user(username='existing', password='good-pass-123')

    def _csrf(self):
        self.client.get('/api/v1/auth/csrf/')
        return self.client.cookies['csrftoken'].value

    def _post(self, path, payload, token=None):
        return self.client.post(
            path,
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=token or self._csrf(),
        )

    def test_register_happy_path_logs_in(self):
        resp = self._post('/api/v1/auth/register/', {
            'username': 'newuser', 'email': 'n@e.com', 'password': 'strong-pass-9',
        })
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json()['username'], 'newuser')
        # Session established → /auth/me/ now returns the user.
        me = self.client.get('/api/v1/auth/me/')
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()['username'], 'newuser')

    def test_register_duplicate_username_is_400(self):
        resp = self._post('/api/v1/auth/register/', {
            'username': 'existing', 'password': 'strong-pass-9',
        })
        self.assertEqual(resp.status_code, 400, resp.content)

    def test_register_short_password_is_400(self):
        resp = self._post('/api/v1/auth/register/', {
            'username': 'shorty', 'password': 'abc',
        })
        self.assertEqual(resp.status_code, 400, resp.content)

    def test_login_bad_credentials_is_401(self):
        resp = self._post('/api/v1/auth/login/', {
            'username': 'existing', 'password': 'wrong',
        })
        self.assertEqual(resp.status_code, 401, resp.content)

    def test_me_requires_auth(self):
        resp = self.client.get('/api/v1/auth/me/')
        self.assertIn(resp.status_code, (401, 403))

    def test_logout_clears_session(self):
        token = self._csrf()
        self._post('/api/v1/auth/login/', {'username': 'existing', 'password': 'good-pass-123'}, token=token)
        self.assertEqual(self.client.get('/api/v1/auth/me/').status_code, 200)
        self._post('/api/v1/auth/logout/', {}, token=token)
        self.assertIn(self.client.get('/api/v1/auth/me/').status_code, (401, 403))
