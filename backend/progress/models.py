from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ExamSession(models.Model):
    SESSION_TYPES = [
        ('study', 'Study'),
        ('exam', 'Exam'),
        ('pbq', 'PBQ Practice'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_sessions')
    session_type = models.CharField(max_length=10, choices=SESSION_TYPES)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    domain_filter = models.ForeignKey(
        'questions.Domain', null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f'{self.user.username} {self.session_type} #{self.pk}'

    def calculate_score(self) -> dict:
        answers = self.session_answers.select_related('question__objective__domain')
        total = answers.count()
        correct = answers.filter(is_correct=True).count()

        by_domain: dict = {}
        for ans in answers:
            domain_id = ans.question.objective.domain_id
            bucket = by_domain.setdefault(domain_id, {'correct': 0, 'total': 0})
            bucket['total'] += 1
            if ans.is_correct:
                bucket['correct'] += 1

        return {
            'correct': correct,
            'total': total,
            'percent': round(correct / total * 100, 1) if total else 0,
            'by_domain': by_domain,
        }

    def get_next_question(self):
        from questions.models import Question
        answered_ids = self.session_answers.values_list('question_id', flat=True)

        if self.session_type == 'exam':
            return (
                Question.objects
                .filter(domain_filter=self.domain_filter)
                .exclude(id__in=answered_ids)
                .order_by('?')
                .first()
            )

        # Study mode: SM-2 due-date priority
        qs = Question.objects.exclude(id__in=answered_ids)
        if self.domain_filter:
            qs = qs.filter(objective__domain=self.domain_filter)

        due = (
            UserQuestionProgress.objects
            .filter(user=self.user, due_date__lte=timezone.now().date(), question__in=qs)
            .order_by('due_date')
            .select_related('question')
            .first()
        )
        if due:
            return due.question

        # New questions not yet seen
        seen_ids = UserQuestionProgress.objects.filter(user=self.user).values_list('question_id', flat=True)
        return qs.exclude(id__in=seen_ids).order_by('?').first()


class SessionAnswer(models.Model):
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='session_answers')
    question = models.ForeignKey('questions.Question', on_delete=models.CASCADE)
    submitted_answer = models.JSONField()
    is_correct = models.BooleanField()
    attempt_number = models.PositiveSmallIntegerField(default=1)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('session', 'question', 'attempt_number')]

    def __str__(self):
        return f'Session {self.session_id} Q{self.question_id} attempt {self.attempt_number}'


class UserQuestionProgress(models.Model):
    CARD_STATES = [
        ('new', 'New'),
        ('learning', 'Learning'),
        ('review', 'Review'),
        ('mastered', 'Mastered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_progress')
    question = models.ForeignKey('questions.Question', on_delete=models.CASCADE)
    card_state = models.CharField(max_length=10, choices=CARD_STATES, default='new')
    ease_factor = models.FloatField(default=2.5)
    interval_days = models.PositiveIntegerField(default=1)
    repetitions = models.PositiveIntegerField(default=0)
    due_date = models.DateField(default=timezone.now)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('user', 'question')]

    def update_sm2(self, rating: int) -> None:
        """Update SM-2 state. rating: 0=Again, 1=Hard, 2=Good, 3=Easy."""
        if rating < 2:
            self.repetitions = 0
            self.interval_days = 1
        else:
            if self.repetitions == 0:
                self.interval_days = 1
            elif self.repetitions == 1:
                self.interval_days = 6
            else:
                self.interval_days = round(self.interval_days * self.ease_factor)
            self.repetitions += 1

        self.ease_factor = max(1.3, self.ease_factor + 0.1 - (3 - rating) * (0.08 + (3 - rating) * 0.02))

        from datetime import date, timedelta
        self.due_date = date.today() + timedelta(days=self.interval_days)

        if self.interval_days >= 21:
            self.card_state = 'mastered'
        elif self.repetitions > 0:
            self.card_state = 'review'
        else:
            self.card_state = 'learning'

        self.save()


class UserDomainProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='domain_progress')
    domain = models.ForeignKey('questions.Domain', on_delete=models.CASCADE)
    total_seen = models.PositiveIntegerField(default=0)
    total_correct = models.PositiveIntegerField(default=0)
    is_pbq = models.BooleanField(default=False)

    class Meta:
        unique_together = [('user', 'domain', 'is_pbq')]

    def __str__(self):
        label = 'PBQ' if self.is_pbq else 'standard'
        return f'{self.user.username} domain {self.domain_id} {label}'
