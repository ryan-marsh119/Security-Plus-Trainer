# Security+ SY0-701 Study Platform

A full-stack interactive study platform for the CompTIA Security+ SY0-701 exam.

## Features

- Multiple question types: multiple choice, multi-select, true/false, drag-and-drop, PBQs
- Practice exams and performance-based question simulators
- Detailed answer keys and explanations
- Progress dashboard tied to official SY0-701 exam domains

## Tech Stack

- **Backend:** Django + PostgreSQL
- **Frontend:** React
- **Deployment:** Docker → Railway

## Requirements

- Python 3.12
- Node 20
- Docker & Docker Compose

## Run locally (Docker — production-style)

The local stack runs the **same combined image we deploy to Railway**: one `web`
container (gunicorn → Django) serves the API/admin **and** the pre-built React SPA,
plus a Postgres `db` container. On boot the `web` container migrates, collects
static, seeds domains, and imports questions (all idempotent).

```bash
docker compose up -d --build      # build + start db + web
# app:    http://localhost:8000/
# admin:  http://localhost:8000/admin/
# health: http://localhost:8000/api/v1/healthz
docker compose logs -f web        # follow boot/app logs
docker compose down               # stop (add -v to wipe the database volume)
```

Create a local admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

## Run locally (frontend hot-reload dev)

For frontend work, run the Vite dev server against a backend. Start `db` (and
optionally `web`) with Compose, then:

```bash
cd frontend && npm install && npm run dev   # http://localhost:5173 (proxies /api → :8000)
```

## Tests

```bash
cd backend && ../venv/Scripts/python manage.py test     # Windows venv
# or inside the container:
docker compose exec web python manage.py test
```

## Deployment (Railway via GitHub Actions)

Push to `main` → GitHub Actions runs the `test` job (Postgres service, migrate,
`manage.py test`, `npm run build`). Only if it passes does the `deploy` job run
`railway up` (gated by `needs: test`). See `.github/workflows/ci.yml` and
`railway.json` (Dockerfile builder, healthcheck `/api/v1/healthz`).

**One-time setup (Railway):**
1. Create a Railway project → add the **PostgreSQL** plugin.
2. Create the web service from this repo (Dockerfile builder).
3. Service env vars: `SECRET_KEY` (generate one), `DEBUG=False`, and reference the
   Postgres `DATABASE_URL`. `RAILWAY_PUBLIC_DOMAIN` is injected automatically and is
   added to `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` by `settings.py`.
4. Account → Tokens → create a token → add it to the GitHub repo as the
   `RAILWAY_TOKEN` secret. (If your service isn't named `web`, set a repo
   **variable** `RAILWAY_SERVICE` to its name.)
5. After the first deploy: `railway run python manage.py createsuperuser`.

## Ops

- **Read logs:** `docker compose logs -f web` locally; `railway logs` in prod.
- **Restart:** `docker compose restart web` / Railway dashboard → service → Restart.
- **Rollback:** Railway dashboard → service → Deployments → redeploy a previous build
  (or `git revert` and push — CI redeploys the reverted state).
- **Backend code changes** require an image rebuild to persist:
  `docker compose up -d --build web`. The backend is not volume-mounted.

## Project Structure

```
security_plus_trainer/
├── Dockerfile        # combined prod image (React build → Django/gunicorn)
├── railway.json      # Railway builder + healthcheck config
├── docker-compose.yml# local: db + combined web service
├── backend/          # Django project
├── frontend/         # React project (Vite)
├── mcp_server/       # MCP server for Claude Code integration
├── resources/        # CompTIA study materials + agent outputs
└── plan.md           # Development plan
```

## Development Phases

See [plan.md](./plan.md) for the full development roadmap.
