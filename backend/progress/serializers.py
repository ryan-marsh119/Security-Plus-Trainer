"""
progress/serializers.py

DRF serializers for session and progress data.
"""

from rest_framework import serializers
from .models import ExamSession, SessionAnswer, UserQuestionProgress, UserDomainProgress


class AnswerSubmitSerializer(serializers.Serializer):
    """
    Validates the SHAPE of an answer-submission request body
    (POST /sessions/<id>/answers/). Request-shape validation only — it does NOT
    validate per-question-type answer contents, because Question.check_answer()
    already tolerates missing/extra keys via .get(default). Adding per-type
    validation here could reject a payload the frontend legitimately emits and
    would couple this serializer to the answer-key shapes; keep it generic.

    Fields:
        question_id (int)  -- pk of the question being answered (required).
        answer      (dict) -- the type-specific answer payload; defaults to {}
                              so a malformed/absent body fails cleanly at
                              check_answer rather than 500-ing.
    """
    question_id = serializers.IntegerField()
    answer = serializers.DictField(required=False, default=dict)


class ExamSessionSerializer(serializers.ModelSerializer):
    """
    Used for both creating sessions (POST /sessions/) and returning session data.

    Input fields (on POST):
        session_type  (str, required) -- 'study' | 'exam' | 'pbq'
        domain_filter (int, optional) -- Domain pk; limits questions to one domain

    Output fields:
        id            -- database pk, used in subsequent session API calls
        session_type  -- as submitted
        domain_filter -- Domain pk or null
        started_at    -- ISO 8601 timestamp (read-only, auto-set)
        completed_at  -- ISO 8601 timestamp or null (read-only, set by complete endpoint)
    """
    class Meta:
        model = ExamSession
        fields = ['id', 'session_type', 'domain_filter', 'started_at', 'completed_at']
        read_only_fields = ['started_at', 'completed_at']


class SessionAnswerSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for individual answer records.
    Not currently exposed via an endpoint but available for future history views.

    Output fields:
        id               -- database pk
        question         -- Question pk
        submitted_answer -- raw JSONB dict as submitted by the user
        is_correct       -- bool
        attempt_number   -- 1 or 2
    """
    class Meta:
        model = SessionAnswer
        fields = ['id', 'question', 'submitted_answer', 'is_correct', 'attempt_number']


class UserDomainProgressSerializer(serializers.ModelSerializer):
    """
    Serializes per-domain accuracy for the /progress/domains/ endpoint.

    Output fields:
        domain        -- Domain pk
        total_seen    -- distinct questions answered at least once
        total_correct -- questions answered correctly on first attempt
        is_pbq        -- False for standard questions, True for PBQ-only rows
    """
    class Meta:
        model = UserDomainProgress
        fields = ['domain', 'total_seen', 'total_correct', 'is_pbq']
