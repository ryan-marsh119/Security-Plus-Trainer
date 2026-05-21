"""
management/commands/import_questions.py

Imports Security+ questions from the domain CSV files in resources/.
Must be run after seed_domains has populated Domain and Objective rows.

Usage:
    python manage.py import_questions                  # all domain_*.csv files
    python manage.py import_questions --csv path/to/file.csv
    python manage.py import_questions --dry-run        # validate without writing

CSV columns required:
    objective_code          -- dot-notation code matching an existing Objective (e.g. '4.8')
    question_text           -- full question prompt
    question_type           -- one of the Question.QUESTION_TYPES values
    difficulty              -- 'easy' | 'medium' | 'hard'
    answer_choices_json     -- JSON array of {"text": "..."} objects
    correct_answer_key_json -- JSON dict matching Question.check_answer() shape
    hint                    -- (optional) shown on first wrong attempt
    explanation             -- (optional) shown on correct answer or second wrong attempt

Idempotency: rows are skipped if a question with the same (objective, question_text)
already exists, so the command is safe to re-run.
"""

import csv
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from questions.models import Domain, Objective, Question, AnswerChoice, AnswerKey


class Command(BaseCommand):
    help = 'Import questions from domain CSV files in resources/'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv', type=str,
            help='Path to a specific CSV file (default: all domain_*.csv in resources/)',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Parse and validate without writing to the database',
        )

    def handle(self, *args, **options):
        # Resolve path: backend/questions/management/commands/ → project root → resources/
        resources_dir = Path(__file__).resolve().parents[4] / 'security_plus_trainer' / 'resources'

        if options['csv']:
            csv_files = [Path(options['csv'])]
        else:
            csv_files = sorted(resources_dir.glob('domain_*.csv'))

        if not csv_files:
            self.stderr.write('No CSV files found.')
            return

        total_created = 0
        total_skipped = 0

        for csv_path in csv_files:
            self.stdout.write(f'Processing {csv_path.name}...')
            created, skipped = self._import_csv(csv_path, options['dry_run'])
            total_created += created
            total_skipped += skipped
            self.stdout.write(f'  {created} created, {skipped} skipped')

        self.stdout.write(self.style.SUCCESS(
            f'Done: {total_created} questions created, {total_skipped} skipped'
        ))

    def _import_csv(self, csv_path: Path, dry_run: bool) -> tuple[int, int]:
        """
        Processes a single CSV file.

        Args:
            csv_path -- absolute Path to the CSV file
            dry_run  -- if True, count rows but do not write to the database

        Returns:
            (created, skipped) -- tuple of integer counts
        """
        created = skipped = 0

        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                objective_code = row['objective_code'].strip()
                try:
                    objective = Objective.objects.get(code=objective_code)
                except Objective.DoesNotExist:
                    self.stderr.write(f'  Objective {objective_code} not found — skipping row')
                    skipped += 1
                    continue

                question_text = row['question_text'].strip()
                # Skip duplicates — safe to re-run without creating doubles
                if Question.objects.filter(objective=objective, question_text=question_text).exists():
                    skipped += 1
                    continue

                if dry_run:
                    created += 1
                    continue

                question = Question.objects.create(
                    objective=objective,
                    question_text=question_text,
                    question_type=row['question_type'].strip(),
                    difficulty=row['difficulty'].strip(),
                )

                answer_choices_raw = json.loads(row['answer_choices_json'])
                # Map each CSV-local choice id to the real DB primary key so the
                # answer key references actual AnswerChoice PKs, not CSV ids.
                csv_id_to_pk = {}
                for i, choice in enumerate(answer_choices_raw):
                    created_choice = AnswerChoice.objects.create(
                        question=question,
                        text=choice['text'],
                        order=i + 1,
                    )
                    csv_id_to_pk[choice.get('id', i + 1)] = created_choice.pk

                answer_data = json.loads(row['correct_answer_key_json'])
                for id_field in ('correct_ids', 'ordered_ids'):
                    if id_field in answer_data:
                        answer_data[id_field] = [
                            csv_id_to_pk.get(cid, cid) for cid in answer_data[id_field]
                        ]

                AnswerKey.objects.create(
                    question=question,
                    answer_data=answer_data,
                    hint=row.get('hint', ''),
                    explanation=row.get('explanation', ''),
                )

                created += 1

        return created, skipped
