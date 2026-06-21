"""
progress/views.py

Session lifecycle and progress-tracking API views.
All views require authentication (session cookie).

Session flow:
  POST /sessions/              → create session, get session id
  GET  /sessions/<id>/next/    → receive next question
  POST /sessions/<id>/answers/ → submit answer, receive hint/explanation
  POST /sessions/<id>/complete/ → mark session finished
  GET  /sessions/<id>/results/ → fetch final score

Progress queries:
  GET /progress/            → overall stats (seen, mastered, due)
  GET /progress/domains/    → per-domain accuracy
  GET /progress/objectives/ → per-objective coverage
"""

import logging

from django.db import IntegrityError, transaction
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ExamSession, SessionAnswer, UserQuestionProgress, UserDomainProgress
from .serializers import (
    AnswerSubmitSerializer,
    ExamSessionSerializer,
    SessionAnswerSerializer,
    UserDomainProgressSerializer,
)
from questions.models import Objective, Question
from questions.serializers import QuestionSerializer

logger = logging.getLogger(__name__)


class SessionCreateView(generics.CreateAPIView):
    """
    POST /api/v1/sessions/

    Creates a new exam/study/pbq session for the authenticated user.

    Request body:
        session_type  (str, required) -- 'study' | 'exam' | 'pbq'
        domain_filter (int, optional) -- Domain pk; limits questions to one domain

    Response: {id, session_type, domain_filter, started_at, completed_at}
    """
    serializer_class = ExamSessionSerializer

    def perform_create(self, serializer):
        # Inject the authenticated user; client cannot set this field directly.
        serializer.save(user=self.request.user)


class SessionNextQuestionView(APIView):
    """
    GET /api/v1/sessions/<pk>/next/

    Returns the next question for the session, chosen by ExamSession.get_next_question().
    Study mode uses SM-2 ordering; exam mode uses random ordering.

    Path params:
        pk -- ExamSession primary key (integer)

    Response:
        200 -- question object {id, objective, question_text, question_type,
               difficulty, answer_choices[]}
        204 -- {'detail': 'No more questions.'} when the session queue is exhausted
    """
    def get(self, request, pk):
        session = get_object_or_404(ExamSession, pk=pk, user=request.user)
        question = session.get_next_question()
        if not question:
            return Response({'detail': 'No more questions.'}, status=status.HTTP_204_NO_CONTENT)
        return Response(QuestionSerializer(question).data)


class SessionAnswerView(APIView):
    """
    POST /api/v1/sessions/<pk>/answers/

    Submits an answer for a question within a session. Implements the
    two-strike feedback rule: hint on first wrong, explanation on second wrong
    or after a correct answer. Updates SM-2 state in study mode.

    Path params:
        pk -- ExamSession primary key (integer)

    Request body:
        question_id (int)  -- pk of the question being answered
        answer      (dict) -- shape depends on question_type; see Question.check_answer()

    Response:
        correct        (bool)      -- whether the submission was right
        attempt_number (int)       -- 1 or 2 (two-strike max)
        hint           (str|null)  -- populated only on first wrong attempt
        explanation    (str|null)  -- populated on correct answer or second wrong attempt
        correct_ids    (int[])     -- choice types only; correct AnswerChoice pks.
                                      Present ONLY once the question is resolved
                                      (correct, 2nd attempt, or exam session), so the
                                      answer can't be read before the second attempt.
        correct_order  (int[])     -- ordering type only; correct AnswerChoice pk
                                      sequence. Same resolved-only gating as correct_ids.
    """
    def post(self, request, pk):
        # Session must exist and belong to the caller → 404, not 500 (BE-02).
        session = get_object_or_404(ExamSession, pk=pk, user=request.user)

        # Request-shape validation → 400 on missing/non-int question_id or a
        # non-dict answer, rather than a downstream 500 (BE-03). Per Contract
        # Decision A1 this validates shape only, never per-type answer contents.
        serializer = AnswerSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question_id = serializer.validated_data['question_id']
        submitted = serializer.validated_data['answer']

        question = get_object_or_404(Question, pk=question_id)
        is_correct = question.check_answer(submitted)

        # Everything that writes (the SessionAnswer, the SM-2 card, and the
        # denormalised domain counter) happens atomically so a failure can't
        # leave them desynced (BE-01). select_for_update serialises concurrent
        # submits for the same (session, question) so attempt_number can't race;
        # the unique_together still backstops it via IntegrityError → 409.
        try:
            with transaction.atomic():
                prior = (
                    SessionAnswer.objects
                    .select_for_update()
                    .filter(session=session, question=question)
                )
                attempt_number = prior.count() + 1

                # First-ever answer to this question by this user (across all
                # their sessions) → count it once toward domain "seen" (W5/BE-05
                # persisted counter). Checked before the insert below.
                is_first_ever = not SessionAnswer.objects.filter(
                    session__user=request.user, question=question
                ).exists()

                SessionAnswer.objects.create(
                    session=session,
                    question=question,
                    submitted_answer=submitted,
                    is_correct=is_correct,
                    attempt_number=attempt_number,
                )

                # SM-2 update only happens in study mode (not exam/pbq).
                if session.session_type == 'study':
                    rating = 2 if is_correct else 0  # Good (2) or Again (0)
                    progress, _ = UserQuestionProgress.objects.get_or_create(
                        user=request.user, question=question,
                    )
                    progress.update_sm2(rating)

                # Denormalised per-domain accuracy: total_seen counts distinct
                # questions ever answered; total_correct counts those right on
                # the first attempt. F() expressions keep the increment atomic.
                if is_first_ever:
                    dp, _ = UserDomainProgress.objects.get_or_create(
                        user=request.user,
                        domain=question.objective.domain,
                        is_pbq=(session.session_type == 'pbq'),
                    )
                    dp.total_seen = F('total_seen') + 1
                    if is_correct:
                        dp.total_correct = F('total_correct') + 1
                    dp.save(update_fields=['total_seen', 'total_correct'])
        except IntegrityError:
            # A concurrent/duplicate submit hit the (session, question,
            # attempt_number) uniqueness constraint. Treat as a conflict rather
            # than a 500 — the earlier write already recorded the attempt.
            logger.warning(
                'Duplicate answer submit for session=%s question=%s user=%s',
                session.pk, question_id, request.user.pk,
            )
            return Response(
                {'detail': 'Answer already submitted for this attempt.'},
                status=status.HTTP_409_CONFLICT,
            )

        logger.info(
            'Answer submitted: user=%s session=%s question=%s attempt=%s correct=%s',
            request.user.pk, session.pk, question_id, attempt_number, is_correct,
        )

        response_data = {
            'correct': is_correct,
            'attempt_number': attempt_number,
            'hint': None,
            'explanation': None,
        }

        # Two-strike rule: hint on first miss, explanation once resolved
        if not is_correct and attempt_number == 1:
            response_data['hint'] = question.get_hint()
        elif is_correct or attempt_number >= 2:
            response_data['explanation'] = question.get_answer_explanation()

        # Correct-answer reveal — only once the question is RESOLVED, so a
        # study/pbq user can't read the answer off the network response before
        # their second attempt. Exam sessions are single-attempt, so always
        # resolved. The frontend highlights the correct option(s) green from
        # this data; its mere presence is the gate (absent → no reveal).
        resolved = is_correct or attempt_number >= 2 or session.session_type == 'exam'
        if resolved:
            key = question.get_answer_key()
            if question.question_type in ('multiple_choice', 'multi_select', 'true_false'):
                response_data['correct_ids'] = key.get('correct_ids', [])
            elif question.question_type == 'ordering':
                response_data['correct_order'] = key.get('ordered_ids', [])

        return Response(response_data)


class SessionResultsView(APIView):
    """
    GET /api/v1/sessions/<pk>/results/

    Returns the aggregated score for a completed (or in-progress) session.

    Path params:
        pk -- ExamSession primary key (integer)

    Response: output of ExamSession.calculate_score()
        {correct, total, percent, by_domain: {domain_id: {correct, total}}}
    """
    def get(self, request, pk):
        session = get_object_or_404(ExamSession, pk=pk, user=request.user)
        return Response(session.calculate_score())


class SessionCompleteView(APIView):
    """
    POST /api/v1/sessions/<pk>/complete/

    Marks the session as finished by setting completed_at to now.
    Should be called when the user clicks 'Submit Exam' or leaves the session.

    Path params:
        pk -- ExamSession primary key (integer)

    Response: {'detail': 'Session completed.'}
    """
    def post(self, request, pk):
        session = get_object_or_404(ExamSession, pk=pk, user=request.user)
        session.completed_at = timezone.now()
        session.save()
        return Response({'detail': 'Session completed.'})


class ProgressOverviewView(APIView):
    """
    GET /api/v1/progress/

    Returns high-level stats for the authenticated user. Powers the Dashboard
    summary cards and milestone tracker.

    Response:
        total_questions (int) -- total questions in the database
        total_seen      (int) -- questions the user has answered at least once
        total_mastered  (int) -- questions with card_state == 'mastered'
        due_count       (int) -- SM-2 cards due today or overdue
    """
    def get(self, request):
        user = request.user
        progress_qs = UserQuestionProgress.objects.filter(user=user)
        total_questions = Question.objects.count()
        total_seen = progress_qs.count()
        total_mastered = progress_qs.filter(card_state='mastered').count()
        due_count = progress_qs.filter(due_date__lte=timezone.now().date()).count()

        return Response({
            'total_questions': total_questions,
            'total_seen': total_seen,
            'total_mastered': total_mastered,
            'due_count': due_count,
        })


class DomainProgressView(generics.ListAPIView):
    """
    GET /api/v1/progress/domains/

    Returns per-domain accuracy for standard (non-PBQ) questions.
    Used by the domain radar chart and domain detail pages.

    Response: list of {domain, total_seen, total_correct, is_pbq}
    """
    serializer_class = UserDomainProgressSerializer

    def get_queryset(self):
        return UserDomainProgress.objects.filter(user=self.request.user, is_pbq=False)


class ObjectiveProgressView(APIView):
    """
    GET /api/v1/progress/objectives/

    Returns per-objective coverage and accuracy for the authenticated user.
    Used by the objective heatmap on the Dashboard.

    Response: list of dicts:
        objective_code  (str) -- e.g. '4.8'
        objective_title (str) -- full title
        total_questions (int) -- questions available under this objective
        seen            (int) -- how many the user has answered at least once
        correct         (int) -- how many are in 'review' or 'mastered' state
    """
    def get(self, request):
        user = request.user

        # Three aggregated queries total instead of 2-per-objective (BE-04):
        #   1. per-objective question counts
        #   2+3. the user's progress rows grouped by objective (seen / correct)
        # assembled in Python below.
        question_counts = dict(
            Objective.objects
            .annotate(n=Count('questions'))
            .values_list('id', 'n')
        )
        progress_rows = (
            UserQuestionProgress.objects
            .filter(user=user)
            .values('question__objective_id')
            .annotate(
                seen=Count('id'),
                correct=Count('id', filter=Q(card_state__in=['review', 'mastered'])),
            )
        )
        progress_by_obj = {
            row['question__objective_id']: (row['seen'], row['correct'])
            for row in progress_rows
        }

        data = []
        for obj in Objective.objects.all():
            seen, correct = progress_by_obj.get(obj.id, (0, 0))
            data.append({
                'objective_code': obj.code,
                'objective_title': obj.title,
                'total_questions': question_counts.get(obj.id, 0),
                'seen': seen,
                'correct': correct,
            })
        return Response(data)
