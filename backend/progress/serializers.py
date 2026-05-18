from rest_framework import serializers
from .models import ExamSession, SessionAnswer, UserQuestionProgress, UserDomainProgress


class ExamSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSession
        fields = ['id', 'session_type', 'domain_filter', 'started_at', 'completed_at']
        read_only_fields = ['started_at', 'completed_at']


class SessionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionAnswer
        fields = ['id', 'question', 'submitted_answer', 'is_correct', 'attempt_number']


class UserDomainProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDomainProgress
        fields = ['domain', 'total_seen', 'total_correct', 'is_pbq']
