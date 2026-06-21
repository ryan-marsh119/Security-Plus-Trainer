"""
Tests for the session / progress app.

The happy-path smoke test exercises the real authenticated flow over the
same-origin session + CSRF setup that production uses. The remaining classes add
the negative-path, reveal-gate, SM-2, isolation, and counter coverage that the
CI `needs: test` gate relies on (BE-14).
"""

import json

from django.contrib.auth.models import User
from django.test import TestCase

from questions.models import Domain, Objective, Question, AnswerChoice, AnswerKey
from progress.models import ExamSession, SessionAnswer, UserQuestionProgress, UserDomainProgress


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
            explanation='A firewall blocks traffic before it reaches the asset.',
        )

    def _csrf(self):
        """Seed the csrftoken cookie (as the SPA does) and return its value."""
        self.client.get('/api/v1/auth/csrf/')
        return self.client.cookies['csrftoken'].value

    def test_login_session_submit_happy_path(self):
        token = self._csrf()

        resp = self.client.post(
            '/api/v1/auth/login/',
            data=json.dumps({'username': 'smoke', 'password': 'smoke-pass-123'}),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(resp.status_code, 200, resp.content)

        resp = self.client.post(
            '/api/v1/sessions/',
            data=json.dumps({'session_type': 'study'}),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        session_id = resp.json()['id']

        resp = self.client.get(f'/api/v1/sessions/{session_id}/next/')
        self.assertEqual(resp.status_code, 200, resp.content)
        self.assertEqual(resp.json()['id'], self.question.id)

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


class SM2ModelTests(TestCase):
    """Unit tests for UserQuestionProgress.update_sm2 (W4/BE-07 + transitions)."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='sm2', password='x')
        domain = Domain.objects.create(number=1, name='D1', weight_pct=12)
        obj = Objective.objects.create(domain=domain, code='1.1', title='o')
        cls.q = Question.objects.create(objective=obj, question_text='q', question_type='multiple_choice')

    def _progress(self):
        return UserQuestionProgress.objects.create(user=self.user, question=self.q)

    def test_good_ratings_grow_interval_and_state(self):
        p = self._progress()
        p.update_sm2(2)          # reps 0 -> interval 1, reps 1
        self.assertEqual(p.interval_days, 1)
        self.assertEqual(p.repetitions, 1)
        self.assertEqual(p.card_state, 'review')
        p.update_sm2(2)          # reps 1 -> interval 6
        self.assertEqual(p.interval_days, 6)
        p.update_sm2(2)          # reps>=2 -> round(6 * 2.5) = 15
        self.assertEqual(p.interval_days, 15)
        p.update_sm2(2)          # round(15 * 2.5) = 38 -> mastered (>=21)
        self.assertEqual(p.interval_days, 38)
        self.assertEqual(p.card_state, 'mastered')

    def test_again_resets_repetitions_and_interval(self):
        p = self._progress()
        p.update_sm2(2)
        p.update_sm2(2)
        p.update_sm2(0)
        self.assertEqual(p.repetitions, 0)
        self.assertEqual(p.interval_days, 1)
        self.assertEqual(p.card_state, 'learning')

    def test_ease_factor_floor_is_1_3(self):
        p = self._progress()
        for _ in range(20):
            p.update_sm2(0)
        self.assertGreaterEqual(p.ease_factor, 1.3)

    def test_out_of_range_rating_raises(self):
        p = self._progress()
        with self.assertRaises(ValueError):
            p.update_sm2(4)
        with self.assertRaises(ValueError):
            p.update_sm2(-1)


class _AnswerFlowBase(TestCase):
    """Shared fixtures: a user with a 2-choice MC question and answer key."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='flow', password='x')
        cls.other = User.objects.create_user(username='intruder', password='x')
        cls.domain = Domain.objects.create(number=1, name='D1', weight_pct=12)
        obj = Objective.objects.create(domain=cls.domain, code='1.1', title='o')
        cls.q = Question.objects.create(objective=obj, question_text='q', question_type='multiple_choice')
        cls.correct = AnswerChoice.objects.create(question=cls.q, text='right', order=1)
        cls.wrong = AnswerChoice.objects.create(question=cls.q, text='wrong', order=2)
        AnswerKey.objects.create(
            question=cls.q,
            answer_data={'correct_ids': [cls.correct.id]},
            hint='a hint', explanation='an explanation',
        )

    def _session(self, user, session_type='study'):
        return ExamSession.objects.create(user=user, session_type=session_type)

    def _submit(self, session_id, choice_id, question_id=None):
        return self.client.post(
            f'/api/v1/sessions/{session_id}/answers/',
            data=json.dumps({
                'question_id': question_id or self.q.id,
                'answer': {'selected_id': choice_id},
            }),
            content_type='application/json',
        )


class RevealGateTests(_AnswerFlowBase):
    """Contract B — correct_ids/correct_order present ONLY once resolved."""

    def setUp(self):
        self.client.force_login(self.user)

    def test_first_wrong_hides_reveal_shows_hint(self):
        session = self._session(self.user)
        resp = self._submit(session.id, self.wrong.id)
        self.assertEqual(resp.status_code, 200, resp.content)
        body = resp.json()
        self.assertFalse(body['correct'])
        self.assertEqual(body['hint'], 'a hint')
        self.assertIsNone(body['explanation'])
        self.assertNotIn('correct_ids', body)     # gate: not leaked early
        self.assertNotIn('correct_order', body)

    def test_second_wrong_reveals_and_explains(self):
        session = self._session(self.user)
        self._submit(session.id, self.wrong.id)
        resp = self._submit(session.id, self.wrong.id)
        body = resp.json()
        self.assertEqual(body['attempt_number'], 2)
        self.assertEqual(body['explanation'], 'an explanation')
        self.assertEqual(body['correct_ids'], [self.correct.id])

    def test_exam_reveals_immediately_and_skips_sm2(self):
        session = self._session(self.user, session_type='exam')
        resp = self._submit(session.id, self.wrong.id)
        body = resp.json()
        self.assertFalse(body['correct'])
        self.assertEqual(body['correct_ids'], [self.correct.id])   # exam reveals always
        self.assertFalse(
            UserQuestionProgress.objects.filter(user=self.user, question=self.q).exists()
        )


class AnswerValidationTests(_AnswerFlowBase):
    """W1/BE-02/BE-03 — 404 and 400 instead of 500."""

    def setUp(self):
        self.client.force_login(self.user)

    def test_missing_question_id_is_400(self):
        session = self._session(self.user)
        resp = self.client.post(
            f'/api/v1/sessions/{session.id}/answers/',
            data=json.dumps({'answer': {'selected_id': self.correct.id}}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400, resp.content)

    def test_non_int_question_id_is_400(self):
        session = self._session(self.user)
        resp = self.client.post(
            f'/api/v1/sessions/{session.id}/answers/',
            data=json.dumps({'question_id': 'abc', 'answer': {}}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400, resp.content)

    def test_answer_as_list_is_400(self):
        session = self._session(self.user)
        resp = self.client.post(
            f'/api/v1/sessions/{session.id}/answers/',
            data=json.dumps({'question_id': self.q.id, 'answer': [1, 2]}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400, resp.content)

    def test_nonexistent_session_is_404(self):
        resp = self._submit(999999, self.correct.id)
        self.assertEqual(resp.status_code, 404, resp.content)

    def test_nonexistent_question_is_404(self):
        session = self._session(self.user)
        resp = self._submit(session.id, self.correct.id, question_id=999999)
        self.assertEqual(resp.status_code, 404, resp.content)


class UserIsolationTests(_AnswerFlowBase):
    """W1/BE-02 — a user cannot touch a session owned by someone else."""

    def test_other_user_cannot_read_or_post_session(self):
        session = self._session(self.user)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(f'/api/v1/sessions/{session.id}/next/').status_code, 404)
        self.assertEqual(self._submit(session.id, self.correct.id).status_code, 404)
        self.assertEqual(self.client.get(f'/api/v1/sessions/{session.id}/results/').status_code, 404)


class DomainProgressCounterTests(_AnswerFlowBase):
    """W5/BE-05 — /progress/domains/ reflects the persisted counter."""

    def setUp(self):
        self.client.force_login(self.user)

    def test_counter_increments_on_first_correct_answer(self):
        session = self._session(self.user)
        self._submit(session.id, self.correct.id)
        resp = self.client.get('/api/v1/progress/domains/')
        self.assertEqual(resp.status_code, 200, resp.content)
        rows = resp.json()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['domain'], self.domain.id)
        self.assertEqual(rows[0]['total_seen'], 1)
        self.assertEqual(rows[0]['total_correct'], 1)

    def test_seen_counts_question_once_across_sessions(self):
        # Wrong in session 1, then session 2: total_seen stays 1 (distinct
        # question), total_correct 0 (first-ever attempt was wrong).
        s1 = self._session(self.user)
        self._submit(s1.id, self.wrong.id)
        s2 = self._session(self.user)
        self._submit(s2.id, self.correct.id)
        row = UserDomainProgress.objects.get(user=self.user, domain=self.domain, is_pbq=False)
        self.assertEqual(row.total_seen, 1)
        self.assertEqual(row.total_correct, 0)


class CalculateScoreTests(_AnswerFlowBase):
    """W15/BE-13 — first-attempt, distinct-question accuracy."""

    def test_retry_does_not_inflate_total(self):
        session = self._session(self.user)
        SessionAnswer.objects.create(session=session, question=self.q, submitted_answer={}, is_correct=False, attempt_number=1)
        SessionAnswer.objects.create(session=session, question=self.q, submitted_answer={}, is_correct=True, attempt_number=2)
        score = session.calculate_score()
        self.assertEqual(score['total'], 1)       # distinct question
        self.assertEqual(score['correct'], 0)     # first attempt was wrong
        self.assertEqual(score['percent'], 0)


class ObjectiveProgressTests(_AnswerFlowBase):
    """W6/BE-04 — objective coverage correctness after the N+1 collapse."""

    def setUp(self):
        self.client.force_login(self.user)

    def test_counts_match_fixture(self):
        UserQuestionProgress.objects.create(user=self.user, question=self.q, card_state='review')
        resp = self.client.get('/api/v1/progress/objectives/')
        self.assertEqual(resp.status_code, 200, resp.content)
        row = next(r for r in resp.json() if r['objective_code'] == '1.1')
        self.assertEqual(row['total_questions'], 1)
        self.assertEqual(row['seen'], 1)
        self.assertEqual(row['correct'], 1)
