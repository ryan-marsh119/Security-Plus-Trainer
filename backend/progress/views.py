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

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ExamSession, SessionAnswer, UserQuestionProgress, UserDomainProgress
from .serializers import ExamSessionSerializer, SessionAnswerSerializer, UserDomainProgressSerializer
from questions.serializers import QuestionSerializer


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
        session = ExamSession.objects.get(pk=pk, user=request.user)
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
        session = ExamSession.objects.get(pk=pk, user=request.user)
        question_id = request.data.get('question_id')
        submitted = request.data.get('answer', {})

        from questions.models import Question
        question = Question.objects.get(pk=question_id)

        prior_attempts = SessionAnswer.objects.filter(
            session=session, question=question
        ).count()
        attempt_number = prior_attempts + 1
        is_correct = question.check_answer(submitted)

        SessionAnswer.objects.create(
            session=session,
            question=question,
            submitted_answer=submitted,
            is_correct=is_correct,
            attempt_number=attempt_number,
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

        # SM-2 update only happens in study mode (not exam mode)
        if session.session_type == 'study':
            rating = 2 if is_correct else 0  # Good (2) or Again (0)
            progress, _ = UserQuestionProgress.objects.get_or_create(
                user=request.user, question=question,
            )
            progress.update_sm2(rating)

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
        session = ExamSession.objects.get(pk=pk, user=request.user)
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
        session = ExamSession.objects.get(pk=pk, user=request.user)
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
        from questions.models import Question
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
        from questions.models import Objective
        objectives = Objective.objects.prefetch_related('questions').all()
        user = request.user
        data = []
        for obj in objectives:
            q_ids = list(obj.questions.values_list('id', flat=True))
            seen = UserQuestionProgress.objects.filter(user=user, question_id__in=q_ids).count()
            correct = UserQuestionProgress.objects.filter(
                user=user, question_id__in=q_ids, card_state__in=['review', 'mastered']
            ).count()
            data.append({
                'objective_code': obj.code,
                'objective_title': obj.title,
                'total_questions': len(q_ids),
                'seen': seen,
                'correct': correct,
            })
        return Response(data)
