# Production-style backend image: Django served by gunicorn, static via whitenoise.
# Build context is the repository root (see docker-compose.yml) so the question
# CSVs under security_plus_trainer/resources/ are available where the
# import_questions command expects them (../security_plus_trainer/resources).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app/backend

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ /app/backend/
COPY security_plus_trainer/resources/ /app/security_plus_trainer/resources/

# Normalize line endings (in case of CRLF from Windows) and make executable.
RUN sed -i 's/\r$//' /app/backend/entrypoint.sh \
    && chmod +x /app/backend/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/backend/entrypoint.sh"]
