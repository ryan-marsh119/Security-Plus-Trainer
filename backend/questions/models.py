"""
questions/models.py

Core content models for the Security+ trainer.
Hierarchy: Domain → Objective → Question → AnswerChoice + AnswerKey

All answer-key logic is funnelled through Question helper methods so views
and management commands never need to inspect answer_data directly.
"""

from django.db import models


class Domain(models.Model):
    """
    One of the five SY0-701 exam domains (e.g. 'Security Operations').

    Fields:
        number      -- Official domain number 1–5, used for ordering.
        name        -- Full domain name as published by CompTIA.
        weight_pct  -- Percentage of exam questions drawn from this domain.
    """

    number = models.PositiveSmallIntegerField(unique=True)
    name = models.CharField(max_length=200)
    weight_pct = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f'{self.number}. {self.name}'


class Objective(models.Model):
    """
    A sub-objective within a Domain (e.g. code='4.8', title='Explain appropriate
    incident response activities').

    Fields:
        domain       -- Parent Domain (FK, CASCADE delete).
        code         -- Dot-notation code like '1.1' or '3.4'. Unique across all domains.
        title        -- Full objective title from the official CompTIA exam objectives doc.
        concept_card -- Short 2–4 sentence explanation shown to users after a pretest
                        attempt on a question tied to this objective. Optional.
    """

    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='objectives')
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=300)
    concept_card = models.TextField(blank=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f'{self.code} {self.title}'


class Question(models.Model):
    """
    A single exam question. Supports seven question types to cover all CompTIA
    SY0-701 formats, including Performance-Based Questions (PBQs).

    Fields:
        objective      -- The SY0-701 objective this question tests (FK).
        question_text  -- The full question prompt shown to the user.
        question_type  -- One of QUESTION_TYPES; determines how the UI renders
                          the question and how check_answer() evaluates submissions.
        difficulty     -- 'easy' | 'medium' | 'hard'. Used for filtering and stats.
        created_at     -- Auto-set on creation; used for audit trail.

    Related objects:
        answer_choices -- AnswerChoice rows (for MC / multi-select / true_false).
        answer_key     -- Single AnswerKey row with JSONB answer_data.
    """

    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('multi_select', 'Multi-Select'),
        ('true_false', 'True/False'),
        ('ordering', 'Ordering'),
        ('drag_drop', 'Drag and Drop'),
        ('fill_blank', 'Fill in the Blank'),
        ('pbq_simulation', 'PBQ Simulation'),
    ]
    DIFFICULTIES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    objective = models.ForeignKey(Objective, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTIES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text[:80]

    # ------------------------------------------------------------------
    # Answer-key accessors — always use these; never read answer_key directly
    # ------------------------------------------------------------------

    def get_answer_key(self) -> dict:
        """
        Returns the raw JSONB answer_data dict for this question.

        Shape varies by question_type:
            multiple_choice / true_false  -> {'correct_ids': [<choice_id>]}
            multi_select                  -> {'correct_ids': [<id>, ...]}
            ordering                      -> {'ordered_ids': [<id>, ...]}
            drag_drop                     -> {'matches': {'<item>': '<zone>', ...}}
            fill_blank                    -> {'answers': ['<text>', ...]}
        """
        return self.answer_key.answer_data

    def get_hint(self) -> str:
        """
        Returns the two-strike hint string. Shown to the user only on their
        first wrong attempt (the 'Brilliant two-strike' rule).
        May be empty string if no hint was authored for this question.
        """
        return self.answer_key.hint

    def get_answer_explanation(self) -> str:
        """
        Returns the full explanation string. Shown after a correct answer or
        after the user's second wrong attempt.
        """
        return self.answer_key.explanation

    def show_correct_answers(self) -> list[str]:
        """
        Returns a list of human-readable correct answer texts.
        Only meaningful for choice-based types (multiple_choice, multi_select,
        true_false). Returns an empty list for ordering/drag_drop/fill_blank.

        Returns:
            list[str] -- e.g. ['Least privilege', 'Need to know']
        """
        key = self.get_answer_key()
        correct_ids = key.get('correct_ids', [])
        return list(
            self.answer_choices.filter(id__in=correct_ids).values_list('text', flat=True)
        )

    def check_answer(self, submitted: dict) -> bool:
        """
        Evaluates a submitted answer against the stored answer key.

        Args:
            submitted: dict whose shape must match the question_type:
                multiple_choice / true_false  -> {'selected_id': <int>}
                multi_select                  -> {'selected_ids': [<int>, ...]}
                ordering                      -> {'ordered_ids': [<int>, ...]}
                drag_drop                     -> {'matches': {'<item>': '<zone>'}}
                fill_blank                    -> {'answers': ['<str>', ...]}

        Returns:
            bool -- True if the submission exactly matches the answer key.
                    fill_blank comparison is case- and whitespace-insensitive.
        """
        key = self.get_answer_key()
        q_type = self.question_type

        if q_type in ('multiple_choice', 'true_false'):
            return submitted.get('selected_id') == key.get('correct_ids', [None])[0]
        if q_type == 'multi_select':
            return set(submitted.get('selected_ids', [])) == set(key.get('correct_ids', []))
        if q_type == 'ordering':
            return submitted.get('ordered_ids', []) == key.get('ordered_ids', [])
        if q_type == 'drag_drop':
            return submitted.get('matches', {}) == key.get('matches', {})
        if q_type == 'fill_blank':
            submitted_answers = [a.strip().lower() for a in submitted.get('answers', [])]
            correct_answers = [a.strip().lower() for a in key.get('answers', [])]
            return submitted_answers == correct_answers
        return False


class AnswerChoice(models.Model):
    """
    One selectable option for a choice-based question (multiple_choice,
    multi_select, true_false). Correct choices are identified in AnswerKey,
    not here — this keeps the UI from leaking the answer in the serializer.

    Fields:
        question -- Parent Question (FK, CASCADE delete).
        text     -- The displayed choice text.
        order    -- Display order (1-indexed, set during CSV import).
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_choices')
    text = models.TextField()
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text[:60]


class AnswerKey(models.Model):
    """
    The authoritative answer record for a Question. One-to-one with Question.

    Fields:
        question    -- Parent Question (OneToOne, CASCADE delete).
        answer_data -- JSONB dict. Shape depends on question_type; see
                       Question.get_answer_key() docstring for full shape spec.
        hint        -- Shown to the user on their FIRST wrong attempt only.
                       Empty string means no hint is provided.
        explanation -- Shown after a correct answer or after the second wrong
                       attempt. Should cite the relevant SY0-701 concept.
    """

    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answer_key')
    answer_data = models.JSONField()
    hint = models.TextField(blank=True)
    explanation = models.TextField(blank=True)

    def __str__(self):
        return f'Key for Q#{self.question_id}'
