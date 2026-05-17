# Security+ Trainer — Claude Code Companion

## Project Goal

Build a full-stack Security+ SY0-701 study platform + learn Claude Code agentic workflows.
Dual goal: ship working software AND become AI-literate.

## Tech Stack

- **Backend:** Django + PostgreSQL
- **Frontend:** React
- **Deployment:** Docker → Railway
- **Claude integration:** MCP server (Phase 4.5 milestone)

## Directory Structure

```
security_plus_trainer/
├── backend/           # Django project root
├── frontend/          # React app
├── mcp_server/        # MCP server exposing question bank to Claude Code
├── resources/         # CompTIA PDFs, pbq_resources.md, AND all agent outputs
│   ├── *.pdf          # Official CompTIA study materials (read-only inputs)
│   ├── pbq_resources.md
│   └── <agent outputs> # Reports, CSVs, logs, architecture docs written here
├── CLAUDE.md          # This file — update every phase
├── plan.md            # Development roadmap
└── README.md          # Public-facing docs
```

## How to Run

> Fill in as Phase 0 progresses.

```bash
# Start PostgreSQL via Docker Compose
docker compose up -d db

# Backend (Django)
cd backend
python manage.py runserver

# Frontend (React)
cd frontend
npm start
```

## Conventions & Rules

- Enter plan mode (Shift+Tab twice in terminal Claude) before each phase
- No `git commit` or `git push` without explicit user approval
- Ask permission before running terminal commands (except: runserver, makemigrations, migrate, pytest)
- Pause after each milestone for review
- Helper methods for answer handling: `get_answer_key()`, `get_answer_explanation()`, `show_correct_answers()`, `calculate_score()`
- All answer-key logic goes through `get_answer_key()`
- **All agent outputs go in `security_plus_trainer/resources/`** — this includes research reports, schema docs, CSVs, extraction logs, architecture docs, validation reports, and eval results. This is also where agents look first when they need context from a previous phase.

## Known Issues & Workarounds

> Emerge as you work — keep this updated.

## Phase Log

> Record loops back to earlier phases here so future-Claude understands the history.

- **Phase 0** (2026-05-17): Project initialized. Git repo created. Virtualenv: `venv/`. Docker Compose for Postgres configured.

## Security+ Domain Tracker (Objectives Touched)

> Update at end of each phase.

| Phase | Domains Touched |
|-------|----------------|
| Phase 0 | — |
