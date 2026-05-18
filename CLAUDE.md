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

## Schema Notes (from Phase 1)

Core tables and their purpose — see `security_plus_trainer/resources/edu_platform_research.md` for full DDL.

| Table | Purpose |
|-------|---------|
| `domains` | 5 SY0-701 exam domains with weight % |
| `objectives` | Sub-objectives within each domain (e.g. 1.1, 2.3) |
| `questions` | All question content; `question_type` enum covers MC, multi-select, true_false, drag_drop, fill_blank, pbq_simulation, ordering |
| `answer_choices` | Choice rows for MC/multi-select; `is_correct` flag |
| `answer_keys` | JSONB `answer_data` — canonical answer for all types |
| `users` | Auth; handled by Django's built-in User model |
| `user_question_progress` | SM-2 spaced repetition state per user per question |
| `exam_sessions` | Practice exam or study session records |
| `session_answers` | Per-question responses within a session |
| `user_domain_progress` | Aggregated accuracy per user per domain |

**Key design decisions:**
- Answer keys use JSONB to support all question types without a polymorphic mess
- SM-2 algorithm for spaced repetition (`ease_factor`, `interval_days`, `repetitions`, `due_date`)
- `user_question_progress.card_state`: new → learning → review → mastered
- `answer_keys.hint` — shown on first wrong attempt; full `explanation` on second (Brilliant two-strike rule)
- `objectives.concept_card` — 2–4 sentence explanation shown after a pretest question attempt
- Session builder must interleave objectives within a domain (no blocked drilling)

## Phase Log

> Record loops back to earlier phases here so future-Claude understands the history.

- **Phase 0** (2026-05-17): Project initialized. Git repo created. Virtualenv: `venv/`. Docker Compose for Postgres configured.
- **Phase 1** (2026-05-17): Platform research complete. Schema design finalized. SM-2 spaced repetition chosen. See `security_plus_trainer/resources/edu_platform_research.md`.
- **Phase 2** (2026-05-18): 100 questions generated across all 5 domains and 19 SY0-701 objectives. CSVs at `security_plus_trainer/resources/domain_*.csv`. Source method: knowledge-based (SY0-701 objectives v7 used as structure reference; study guide PDF skipped due to size). See `extraction_log.txt` and `coverage_map.md`. Domain 4 objectives 4.7–4.9 are low-coverage — expansion priority in Phase 5.

## Security+ Domain Tracker (Objectives Touched)

> Update at end of each phase.

| Phase | Domains Touched |
|-------|----------------|
| Phase 0 | — |
| Phase 1 | All 5 domains (schema design maps to all) |
| Phase 2 | All 5 domains — 100 questions total; 24/23/14/24/15 by domain |
