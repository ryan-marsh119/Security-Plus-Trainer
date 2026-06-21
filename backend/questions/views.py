"""
questions/views.py

Read-only API views for browsing content. All views require authentication
(enforced globally by DEFAULT_PERMISSION_CLASSES in settings.py).

URL prefix: /api/v1/   (see securityplus/urls.py)
"""

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from .models import Domain, Objective, Question
from .serializers import DomainSerializer, ObjectiveSerializer, QuestionSerializer


class DomainListView(generics.ListAPIView):
    """
    GET /api/v1/domains/

    Returns all five SY0-701 domains ordered by number.

    Response: list of {id, number, name, weight_pct}
    """
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


class ObjectiveListView(generics.ListAPIView):
    """
    GET /api/v1/domains/<pk>/objectives/

    Returns all objectives that belong to the given domain.

    Path params:
        pk -- Domain primary key (integer)

    Response: list of {id, code, title, concept_card}
    """
    serializer_class = ObjectiveSerializer

    def get_queryset(self):
        return Objective.objects.filter(domain_id=self.kwargs['pk'])


class QuestionDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/questions/<pk>/

    Returns a single question with its answer choices.
    Answer key (correct answers) is intentionally excluded from the serializer
    so the frontend cannot leak answers before the user submits.

    Path params:
        pk -- Question primary key (integer)

    Response: {id, objective, question_text, question_type, difficulty, answer_choices[]}
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class QuestionListView(generics.ListAPIView):
    """
    GET /api/v1/questions/

    Returns questions with optional filters. Used by the PBQ Hub to load
    domain-specific PBQ question sets.

    Query params:
        question_type -- Comma-separated list of types to include.
                         e.g. ?question_type=ordering,drag_drop,pbq_simulation,fill_blank
        domain        -- Domain primary key (integer).
                         e.g. ?domain=4

    Response: list of question objects (same shape as QuestionDetailView)
    """
    serializer_class = QuestionSerializer

    def get_queryset(self):
        qs = Question.objects.all()
        q_type = self.request.query_params.get('question_type')
        domain = self.request.query_params.get('domain')
        if q_type:
            # Unknown types simply match nothing (→ empty list), so no error is
            # raised here; only a non-integer domain is a hard client error.
            types = [t for t in q_type.split(',') if t]
            qs = qs.filter(question_type__in=types)
        if domain:
            try:
                domain_id = int(domain)
            except (TypeError, ValueError):
                raise ValidationError({'domain': 'Must be an integer domain id.'})
            qs = qs.filter(objective__domain_id=domain_id)
        return qs
