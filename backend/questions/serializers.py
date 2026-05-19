"""
questions/serializers.py

DRF serializers for read-only content exposure.
Answer keys are deliberately excluded from all serializers — correct answer
data lives only in AnswerKey.answer_data and is accessed server-side through
Question.check_answer(), never sent to the client.
"""

from rest_framework import serializers
from .models import Domain, Objective, Question, AnswerChoice


class DomainSerializer(serializers.ModelSerializer):
    """
    Serializes a Domain for the /domains/ list endpoint.

    Output fields:
        id          -- database pk
        number      -- domain number 1–5
        name        -- full domain name
        weight_pct  -- percentage of exam questions from this domain
    """
    class Meta:
        model = Domain
        fields = ['id', 'number', 'name', 'weight_pct']


class ObjectiveSerializer(serializers.ModelSerializer):
    """
    Serializes an Objective for the /domains/<pk>/objectives/ endpoint.

    Output fields:
        id           -- database pk
        code         -- dot-notation code (e.g. '4.8')
        title        -- full objective title
        concept_card -- short explanation shown after pretest attempt (may be empty)
    """
    class Meta:
        model = Objective
        fields = ['id', 'code', 'title', 'concept_card']


class AnswerChoiceSerializer(serializers.ModelSerializer):
    """
    Serializes a single answer choice. Intentionally omits any is_correct field
    so the client cannot determine the right answer before submitting.

    Output fields:
        id    -- database pk (used in submitted answers, e.g. {'selected_id': 42})
        text  -- display text of this choice
        order -- display order (1-indexed)
    """
    class Meta:
        model = AnswerChoice
        fields = ['id', 'text', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializes a Question with its answer choices nested inline.
    Used by QuestionDetailView, QuestionListView, and SessionNextQuestionView.

    Output fields:
        id             -- database pk
        objective      -- objective pk (FK reference, not nested)
        question_text  -- full question prompt
        question_type  -- one of: multiple_choice, multi_select, true_false,
                          ordering, drag_drop, fill_blank, pbq_simulation
        difficulty     -- 'easy' | 'medium' | 'hard'
        answer_choices -- list of AnswerChoiceSerializer objects (ordered by `order`)
    """
    answer_choices = AnswerChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'objective', 'question_text', 'question_type', 'difficulty', 'answer_choices']
