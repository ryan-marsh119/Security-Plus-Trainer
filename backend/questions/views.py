from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Domain, Objective, Question
from .serializers import DomainSerializer, ObjectiveSerializer, QuestionSerializer


class DomainListView(generics.ListAPIView):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


class ObjectiveListView(generics.ListAPIView):
    serializer_class = ObjectiveSerializer

    def get_queryset(self):
        return Objective.objects.filter(domain_id=self.kwargs['pk'])


class QuestionDetailView(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class QuestionListView(generics.ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        qs = Question.objects.all()
        q_type = self.request.query_params.get('question_type')
        domain = self.request.query_params.get('domain')
        if q_type:
            types = q_type.split(',')
            qs = qs.filter(question_type__in=types)
        if domain:
            qs = qs.filter(objective__domain_id=domain)
        return qs
