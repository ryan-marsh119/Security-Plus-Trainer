from django.db import models


class Domain(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)
    name = models.CharField(max_length=200)
    weight_pct = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f'{self.number}. {self.name}'


class Objective(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='objectives')
    code = models.CharField(max_length=10, unique=True)  # e.g. "1.1", "3.4"
    title = models.CharField(max_length=300)
    concept_card = models.TextField(blank=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f'{self.code} {self.title}'


class Question(models.Model):
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

    def get_answer_key(self) -> dict:
        return self.answer_key.answer_data

    def get_hint(self) -> str:
        return self.answer_key.hint

    def get_answer_explanation(self) -> str:
        return self.answer_key.explanation

    def show_correct_answers(self) -> list[str]:
        key = self.get_answer_key()
        correct_ids = key.get('correct_ids', [])
        return list(
            self.answer_choices.filter(id__in=correct_ids).values_list('text', flat=True)
        )

    def check_answer(self, submitted: dict) -> bool:
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
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_choices')
    text = models.TextField()
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text[:60]


class AnswerKey(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answer_key')
    answer_data = models.JSONField()
    hint = models.TextField(blank=True)
    explanation = models.TextField(blank=True)

    def __str__(self):
        return f'Key for Q#{self.question_id}'
