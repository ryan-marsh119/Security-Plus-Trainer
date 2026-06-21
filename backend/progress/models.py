"""
progress/models.py

Tracks everything that happens after a user starts studying:
  - ExamSession        -- a single study or exam run
  - SessionAnswer      -- one answer submission within a session
  - UserQuestionProgress -- SM-2 spaced-repetition state per user/question pair
  - UserDomainProgress -- aggregated accuracy per user/domain (for dashboard)
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ExamSession(models.Model):
    """
    Represents one sitting: study mode, full practice exam, or PBQ-only practice.

    Fields:
        user          -- The authenticated user (FK, CASCADE delete).
        session_type  -- 'study' | 'exam' | 'pbq'. Controls question ordering
                         and whether SM-2 updates are applied.
        started_at    -- Auto-set when the session is created.
        completed_at  -- Set by SessionCompleteView when the user finishes.
                         Null means the session is still in progress.
        domain_filter -- Optional Domain FK. When set, only questions from that
                         domain are served. Used by PBQSession and domain-focused study.
    """

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
        """
        Aggregates the session into a per-question accuracy summary.

        Scores DISTINCT questions on their FIRST attempt only (BE-13). A study
        question missed then re-answered correctly counts once, as wrong — so
        `percent` is a true accuracy rather than a fraction-of-attempts diluted
        by two-strike retries. Exam sessions are single-attempt, so this is
        identical to counting all rows for them. The first attempt is always
        attempt_number == 1 (assigned as prior_count + 1 at submission), and
        there is exactly one such row per question.

        Returns:
            dict with keys:
                correct  (int)   -- distinct questions correct on first attempt
                total    (int)   -- distinct questions attempted
                percent  (float) -- correct / total * 100, rounded to 1 dp; 0 if none
                by_domain (dict) -- {domain_id: {'correct': int, 'total': int}}
        """
        first_attempts = (
            self.session_answers
            .filter(attempt_number=1)
            .select_related('question__objective__domain')
        )
        total = first_attempts.count()
        correct = first_attempts.filter(is_correct=True).count()

        by_domain: dict = {}
        for ans in first_attempts:
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
        """
        Selects the next question to serve based on session type.

        Exam mode:  random question not yet answered in this session, optionally
                    filtered by domain_filter.
        Study mode: priority order —
                    1. SM-2 due cards (earliest due_date first)
                    2. New questions the user has never seen (random)
                    Returns None when all eligible questions are exhausted.

        Returns:
            Question instance or None
        """
        from questions.models import Question
        answered_ids = self.session_answers.values_list('question_id', flat=True)

        if self.session_type == 'exam':
            qs = Question.objects.exclude(id__in=answered_ids)
            if self.domain_filter:
                qs = qs.filter(objective__domain=self.domain_filter)
            return qs.order_by('?').first()

        # Study / PBQ mode: SM-2 due-date priority
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

        # Fall back to unseen questions
        seen_ids = UserQuestionProgress.objects.filter(user=self.user).values_list('question_id', flat=True)
        return qs.exclude(id__in=seen_ids).order_by('?').first()


class SessionAnswer(models.Model):
    """
    Records one answer submission for a question within a session.
    Multiple rows can exist for the same (session, question) pair because the
    two-strike system allows a second attempt after a wrong answer.

    Fields:
        session          -- Parent ExamSession (FK, CASCADE delete).
        question         -- The question that was answered (FK).
        submitted_answer -- JSONB matching the question_type shape (see Question.check_answer).
        is_correct       -- Result of Question.check_answer() at submission time.
        attempt_number   -- 1 for first attempt, 2 for second (two-strike max).
        answered_at      -- Auto-set timestamp.

    Constraints:
        unique_together on (session, question, attempt_number) — prevents duplicate attempts.
    """

    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='session_answers')
    question = models.ForeignKey('questions.Question', on_delete=models.CASCADE)
    submitted_answer = models.JSONField()
    is_correct = models.BooleanField()
    attempt_number = models.PositiveSmallIntegerField(default=1)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('session', 'question', 'attempt_number')]
        indexes = [
            # Hot path: attempt_number lookups and first-ever-answer checks
            # filter on (session, question); the answer counter joins on these.
            models.Index(fields=['session', 'question']),
        ]

    def __str__(self):
        return f'Session {self.session_id} Q{self.question_id} attempt {self.attempt_number}'


class UserQuestionProgress(models.Model):
    """
    Stores the SM-2 spaced-repetition state for one (user, question) pair.
    Created the first time a user answers a question in study mode.

    Fields:
        user          -- The learner (FK, CASCADE delete).
        question      -- The question being tracked (FK).
        card_state    -- 'new' → 'learning' → 'review' → 'mastered'.
                         Driven by interval_days thresholds in update_sm2().
        ease_factor   -- SM-2 E-Factor; starts at 2.5, floor 1.3. Higher means
                         longer intervals.
        interval_days -- Days until the card is due again. Grows with repetitions.
        repetitions   -- Count of consecutive correct answers (resets on Again/Hard).
        due_date      -- Date the card should be shown again. Compared against
                         today in get_next_question().
        last_seen     -- Auto-updated on every save() call.

    Constraints:
        unique_together on (user, question).
    """

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
        indexes = [
            # SM-2 due-card lookup (get_next_question) filters user + due_date;
            # dashboard counts filter user + card_state.
            models.Index(fields=['user', 'due_date']),
            models.Index(fields=['user', 'card_state']),
        ]

    def update_sm2(self, rating: int) -> None:
        """
        Applies the SM-2 algorithm and saves the updated state.

        Args:
            rating: int in 0–3
                0 = Again  (complete blackout — reset repetitions)
                1 = Hard   (correct but difficult — reset repetitions)
                2 = Good   (correct with effort — grow interval normally)
                3 = Easy   (correct with no effort — grow interval faster)

        Side effects:
            Updates ease_factor, interval_days, repetitions, due_date,
            card_state, then calls self.save().

        Card state thresholds:
            interval_days >= 21 → 'mastered'
            repetitions > 0     → 'review'
            otherwise           → 'learning'

        Raises:
            ValueError: if rating is outside the supported 0–3 range. The SM-2
                ease-factor formula is only defined for 0–3; an out-of-range
                value would silently corrupt the card's scheduling.
        """
        if not isinstance(rating, int) or not 0 <= rating <= 3:
            raise ValueError(f'rating must be an int in 0..3, got {rating!r}')

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

        # Standard SM-2 ease-factor update formula
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
    """
    Denormalised accuracy summary per user/domain pair. Updated by the app
    after each answer to keep dashboard queries fast (no live aggregation needed).

    Fields:
        user          -- The learner (FK, CASCADE delete).
        domain        -- The Domain being tracked (FK).
        total_seen    -- Number of distinct questions answered at least once.
        total_correct -- Number answered correctly on the first attempt.
        is_pbq        -- True when this row tracks PBQ-type questions separately
                         from standard MC questions in the same domain.

    Constraints:
        unique_together on (user, domain, is_pbq).
    """

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
