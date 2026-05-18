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
        resources_dir = Path(__file__).resolve().parents[5] / 'resources'

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

    def _import_csv(self, csv_path, dry_run):
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
                for i, choice in enumerate(answer_choices_raw):
                    AnswerChoice.objects.create(
                        question=question,
                        text=choice['text'],
                        order=i + 1,
                    )

                AnswerKey.objects.create(
                    question=question,
                    answer_data=json.loads(row['correct_answer_key_json']),
                    hint=row.get('hint', ''),
                    explanation=row.get('explanation', ''),
                )

                created += 1

        return created, skipped
