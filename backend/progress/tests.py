"""
End-to-end happy-path smoke test (Phase 6).

Exercises the real authenticated flow over the same-origin session + CSRF setup
that production uses: seed CSRF cookie -> login -> create session -> fetch next
question -> submit the correct answer and get a scored response. This is the
single most important guard that a deploy hasn't broken auth or answer-checking.
"""

import json

from django.contrib.auth.models import User
from django.test import TestCase

from questions.models import Domain, Objective, Question, AnswerChoice, AnswerKey


class StudyFlowSmokeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='smoke', password='smoke-pass-123')

        domain = Domain.objects.create(number=1, name='General Security Concepts', weight_pct=12)
        objective = Objective.objects.create(domain=domain, code='1.1', title='Test objective')
        cls.question = Question.objects.create(
            objective=objective,
            question_text='Which control type is a firewall?',
            question_type='multiple_choice',
        )
        cls.correct = AnswerChoice.objects.create(question=cls.question, text='Preventive', order=1)
        AnswerChoice.objects.create(question=cls.question, text='Detective', order=2)
        AnswerKey.objects.create(
            question=cls.question,
            answer_data={'correct_ids': [cls.correct.id]},
            hint='Think about what a firewall does before an attack.',
            explanation='A firewall blocks traffic before it reaches the asset — preventive.',
        )

    def _csrf(self):
        """Seed the csrftoken cookie (as the SPA does) and return its value."""
        self.client.get('/api/v1/auth/csrf/')
        return self.client.cookies['csrftoken'].value

    def test_login_session_submit_happy_path(self):
        token = self._csrf()

        # Login (anonymous POST — no CSRF enforced by DRF SessionAuthentication).
        resp = self.client.post(
            '/api/v1/auth/login/',
            data=json.dumps({'username': 'smoke', 'password': 'smoke-pass-123'}),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(resp.status_code, 200, resp.content)

        # Create a study session (authenticated POST — CSRF header required).
        resp = self.client.post(
            '/api/v1/sessions/',
            data=json.dumps({'session_type': 'study'}),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        session_id = resp.json()['id']

        # Fetch the next question — only one exists, so we should get it back.
        resp = self.client.get(f'/api/v1/sessions/{session_id}/next/')
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.json()['id'], self.question.id)

        # Submit the correct answer and confirm it scores as correct.
        resp = self.client.post(
            f'/api/v1/sessions/{session_id}/answers/',
            data=json.dumps({
                'question_id': self.question.id,
                'answer': {'selected_id': self.correct.id},
            }),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(resp.status_code, 200, resp.content)
        body = resp.json()
        self.assertTrue(body['correct'])
        self.assertEqual(body['correct_ids'], [self.correct.id])
