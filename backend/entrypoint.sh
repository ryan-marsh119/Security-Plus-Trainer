#!/bin/sh
# Backend container entrypoint. All steps below are idempotent, so it is safe
# to run on every container start (fresh or existing database).
set -e

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Seeding domains and objectives..."
python manage.py seed_domains

echo "Importing questions..."
python manage.py import_questions

echo "Starting gunicorn..."
exec gunicorn securityplus.wsgi:application --bind 0.0.0.0:8000 --workers 3
