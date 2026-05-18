from django.contrib import admin
from .models import ExamSession, SessionAnswer, UserQuestionProgress, UserDomainProgress


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_type', 'started_at', 'completed_at']
    list_filter = ['session_type']


@admin.register(SessionAnswer)
class SessionAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'question', 'is_correct', 'attempt_number']
    list_filter = ['is_correct']


@admin.register(UserQuestionProgress)
class UserQuestionProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'card_state', 'ease_factor', 'interval_days', 'due_date']
    list_filter = ['card_state']


@admin.register(UserDomainProgress)
class UserDomainProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'domain', 'total_seen', 'total_correct', 'is_pbq']
