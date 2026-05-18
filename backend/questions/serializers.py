from rest_framework import serializers
from .models import Domain, Objective, Question, AnswerChoice


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ['id', 'number', 'name', 'weight_pct']


class ObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Objective
        fields = ['id', 'code', 'title', 'concept_card']


class AnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = ['id', 'text', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    answer_choices = AnswerChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'objective', 'question_text', 'question_type', 'difficulty', 'answer_choices']
