from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ExamSession, SessionAnswer, UserQuestionProgress, UserDomainProgress
from .serializers import ExamSessionSerializer, SessionAnswerSerializer, UserDomainProgressSerializer
from questions.serializers import QuestionSerializer


class SessionCreateView(generics.CreateAPIView):
    serializer_class = ExamSessionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SessionNextQuestionView(APIView):
    def get(self, request, pk):
        session = ExamSession.objects.get(pk=pk, user=request.user)
        question = session.get_next_question()
        if not question:
            return Response({'detail': 'No more questions.'}, status=status.HTTP_204_NO_CONTENT)
        return Response(QuestionSerializer(question).data)


class SessionAnswerView(APIView):
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

        if not is_correct and attempt_number == 1:
            response_data['hint'] = question.get_hint()
        elif is_correct or attempt_number >= 2:
            response_data['explanation'] = question.get_answer_explanation()

        # Update SM-2 if study mode
        if session.session_type == 'study':
            rating = 2 if is_correct else 0
            progress, _ = UserQuestionProgress.objects.get_or_create(
                user=request.user, question=question,
            )
            progress.update_sm2(rating)

        return Response(response_data)


class SessionResultsView(APIView):
    def get(self, request, pk):
        session = ExamSession.objects.get(pk=pk, user=request.user)
        return Response(session.calculate_score())


class SessionCompleteView(APIView):
    def post(self, request, pk):
        session = ExamSession.objects.get(pk=pk, user=request.user)
        session.completed_at = timezone.now()
        session.save()
        return Response({'detail': 'Session completed.'})


class ProgressOverviewView(APIView):
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
    serializer_class = UserDomainProgressSerializer

    def get_queryset(self):
        return UserDomainProgress.objects.filter(user=self.request.user, is_pbq=False)


class ObjectiveProgressView(APIView):
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
