"""
Tests for the questions app: deployment smoke checks, the answer-checking logic
per question type, and query-param validation.
"""

from django.contrib.auth.models import User
from django.test import TestCase

from questions.models import Domain, Objective, Question, AnswerChoice, AnswerKey


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


class CheckAnswerTests(TestCase):
    """Question.check_answer across every supported type (BE-14 #4)."""

    @classmethod
    def setUpTestData(cls):
        cls.domain = Domain.objects.create(number=1, name='D1', weight_pct=12)
        cls.obj = Objective.objects.create(domain=cls.domain, code='1.1', title='o')

    def _q(self, qtype, answer_data):
        q = Question.objects.create(objective=self.obj, question_text='q', question_type=qtype)
        AnswerKey.objects.create(question=q, answer_data=answer_data)
        return q

    def test_multiple_choice(self):
        q = self._q('multiple_choice', {'correct_ids': [5]})
        self.assertTrue(q.check_answer({'selected_id': 5}))
        self.assertFalse(q.check_answer({'selected_id': 6}))

    def test_true_false(self):
        q = self._q('true_false', {'correct_ids': [1]})
        self.assertTrue(q.check_answer({'selected_id': 1}))
        self.assertFalse(q.check_answer({'selected_id': 2}))

    def test_multi_select_is_order_independent(self):
        q = self._q('multi_select', {'correct_ids': [1, 2, 3]})
        self.assertTrue(q.check_answer({'selected_ids': [3, 1, 2]}))
        self.assertFalse(q.check_answer({'selected_ids': [1, 2]}))

    def test_ordering_is_order_sensitive(self):
        q = self._q('ordering', {'ordered_ids': [1, 2, 3]})
        self.assertTrue(q.check_answer({'ordered_ids': [1, 2, 3]}))
        self.assertFalse(q.check_answer({'ordered_ids': [1, 3, 2]}))

    def test_drag_drop(self):
        q = self._q('drag_drop', {'matches': {'a': 'x', 'b': 'y'}})
        self.assertTrue(q.check_answer({'matches': {'a': 'x', 'b': 'y'}}))
        self.assertFalse(q.check_answer({'matches': {'a': 'y', 'b': 'x'}}))

    def test_fill_blank_is_case_and_space_insensitive(self):
        q = self._q('fill_blank', {'answers': ['Least Privilege']})
        self.assertTrue(q.check_answer({'answers': ['  least privilege ']}))
        self.assertFalse(q.check_answer({'answers': ['need to know']}))

    def test_pbq_simulation_is_unscorable(self):
        q = self._q('pbq_simulation', {})
        self.assertFalse(q.check_answer({'anything': True}))

    def test_missing_keys_do_not_raise(self):
        q = self._q('multiple_choice', {'correct_ids': [5]})
        self.assertFalse(q.check_answer({}))  # tolerant of an empty payload


class QuestionFilterValidationTests(TestCase):
    """W7/BE-08 — query-param validation on the questions list."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='filter', password='x')
        domain = Domain.objects.create(number=1, name='D1', weight_pct=12)
        obj = Objective.objects.create(domain=domain, code='1.1', title='o')
        Question.objects.create(objective=obj, question_text='q', question_type='ordering')

    def setUp(self):
        self.client.force_login(self.user)

    def test_bad_domain_is_400(self):
        resp = self.client.get('/api/v1/questions/?domain=abc')
        self.assertEqual(resp.status_code, 400, resp.content)

    def test_unknown_question_type_returns_empty_not_500(self):
        resp = self.client.get('/api/v1/questions/?question_type=bogus')
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.json(), [])

    def test_valid_filters_ok(self):
        resp = self.client.get('/api/v1/questions/?question_type=ordering')
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(len(resp.json()), 1)
