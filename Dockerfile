# Combined production image (Railway target).
#
# One container runs gunicorn -> Django, which serves the API/admin AND the
# pre-built React SPA (via whitenoise) from the same origin. Build context is the
# repository root so both frontend/ and backend/ (plus the question CSVs under
# security_plus_trainer/resources/) are available.
#
#   Stage 1 (node)   build the Vite SPA  -> /app/dist
#   Stage 2 (python) install backend, copy the built SPA, run gunicorn

# ---- Stage 1: build the React SPA ---------------------------------------
FROM node:20-alpine AS frontend
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Django + gunicorn -----------------------------------------
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app/backend

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ /app/backend/
COPY security_plus_trainer/resources/ /app/security_plus_trainer/resources/

# The built SPA lands at /app/frontend_build, which settings.py adds to
# STATICFILES_DIRS (assets served via whitenoise) and reads index.html from
# (SPA fallback view).
COPY --from=frontend /app/dist /app/frontend_build

# Normalize line endings (in case of CRLF from Windows) and make executable.
RUN sed -i 's/\r$//' /app/backend/entrypoint.sh \
    && chmod +x /app/backend/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/backend/entrypoint.sh"]
