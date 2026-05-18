from django.contrib import admin
from .models import Domain, Objective, Question, AnswerChoice, AnswerKey


class AnswerChoiceInline(admin.TabularInline):
    model = AnswerChoice
    extra = 4


class AnswerKeyInline(admin.StackedInline):
    model = AnswerKey
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'objective', 'question_type', 'difficulty', 'short_text']
    list_filter = ['question_type', 'difficulty', 'objective__domain']
    search_fields = ['question_text']
    inlines = [AnswerChoiceInline, AnswerKeyInline]

    def short_text(self, obj):
        return obj.question_text[:80]
    short_text.short_description = 'Question'


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['number', 'name', 'weight_pct']


@admin.register(Objective)
class ObjectiveAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'domain']
    list_filter = ['domain']
