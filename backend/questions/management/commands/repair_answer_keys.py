"""
management/commands/repair_answer_keys.py

One-time, idempotent repair for answer keys imported before the import_questions
fix. Early imports stored CSV-local choice ids (1-based positions) in
answer_data['correct_ids'] / ['ordered_ids'] instead of the real AnswerChoice
primary keys, so Question.check_answer() compared the submitted PK against a
positional id and marked correct answers wrong.

This command treats each id N in those fields as a 1-based position and remaps it
to the PK of the choice with order == N for that question.

Idempotency: if every id in a key is already a valid AnswerChoice PK for its
question, the key is left untouched — safe to re-run.

Usage:
    python manage.py repair_answer_keys --dry-run   # report only
    python manage.py repair_answer_keys             # apply
"""

from django.core.management.base import BaseCommand
from questions.models import AnswerKey


class Command(BaseCommand):
    help = 'Remap answer-key id lists from CSV-local positions to real AnswerChoice PKs.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Show what would change without writing to the database.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        repaired = skipped = 0

        for key in AnswerKey.objects.select_related('question').all():
            question = key.question
            choices = list(question.answer_choices.order_by('order'))
            valid_pks = {c.pk for c in choices}
            order_to_pk = {c.order: c.pk for c in choices}

            data = key.answer_data
            before = {}
            after = {}
            changed = False

            for field in ('correct_ids', 'ordered_ids'):
                ids = data.get(field)
                if not ids:
                    continue
                # Already real PKs for this question -> leave alone (idempotent).
                if all(i in valid_pks for i in ids):
                    continue
                new_ids = [order_to_pk.get(i, i) for i in ids]
                if new_ids != ids:
                    before[field] = ids
                    after[field] = new_ids
                    data[field] = new_ids
                    changed = True

            if changed:
                repaired += 1
                self.stdout.write(
                    f'Q{question.id} ({question.question_type}): {before} -> {after}'
                )
                if not dry_run:
                    key.answer_data = data
                    key.save(update_fields=['answer_data'])
            else:
                skipped += 1

        verb = 'would repair' if dry_run else 'repaired'
        self.stdout.write(self.style.SUCCESS(
            f'Done: {verb} {repaired} answer keys, {skipped} already correct.'
        ))
