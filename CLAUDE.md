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

```bash
# Start PostgreSQL via Docker Compose
docker compose up -d db

# Backend (Django dev server)
cd backend
../venv/Scripts/python manage.py migrate
../venv/Scripts/python manage.py runserver

# Import questions from CSVs (after migrations)
../venv/Scripts/python manage.py import_questions

# Frontend (Vite dev server — http://localhost:5173)
cd frontend
npm run dev
```

## Auth Strategy

Session-based (Django sessions + CSRF). Rationale: single-domain SPA, no mobile client, simpler than JWT. CSRF token sent in cookie, React reads it via `document.cookie` and attaches as `X-CSRFToken` header on mutating requests.

## API

**Base URL:** `/api/v1/`

All endpoints require authentication (session cookie) except `POST /auth/login/` and `POST /auth/register/`.

## Frontend Stack

| Tool | Role |
|------|------|
| Vite + React | Build tool + UI framework |
| React Router v6 | Client-side routing |
| Zustand | State (sessionStore, userStore) |
| Axios | API client with CSRF interceptor |
| Tailwind CSS v4 | Utility-first styling |

## Dashboard Milestones

| Milestone | Trigger |
|-----------|---------|
| Novice | < 20% of questions seen |
| Apprentice | ≥ 20% seen, ≥ 60% accuracy |
| Practitioner | ≥ 40% seen, ≥ 70% accuracy |
| Professional | ≥ 60% seen, ≥ 80% accuracy |
| Expert | ≥ 80% seen, ≥ 85% accuracy |

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
- **Phase 2** (2026-05-18): 248 questions total across all 5 domains. Initial 100 knowledge-based + 148 web-sourced (CompTIA official site + lognpacific.com free practice tests). Domain 4 grew from 24 → 118 questions (major gap filled). CSVs at `security_plus_trainer/resources/domain_*.csv`. See `extraction_log.txt`, `coverage_map.md`, `generate_questions.py`, `generate_web_questions.py`.
- **Phase 3** (2026-05-18): Full-stack scaffold complete. Django backend: questions/progress/users apps with models, views, serializers, URLs, and import_questions management command. Frontend: Vite + React + Tailwind v4 + React Router v6 + Zustand + Axios. All stub pages (Login, Register, Dashboard, StudySession, PracticeExam, PBQHub, PBQSession, Results) wired in App.jsx. `python manage.py check` passes. Frontend builds cleanly. See `resources/architecture.md` for full design doc.
- **Phase 4** (2026-05-18): Database live. Migrations applied (19 total). `seed_domains` command creates 5 domains + 28 SY0-701 objectives. `import_questions` loads all 248 questions (41/29/21/118/39 by domain). Admin registered for all models. API endpoints verified end-to-end: login → session → next question → submit answer (two-strike hint system confirmed). Local superuser: admin / admin1234 (dev only).
- **Phase 4.1** (2026-05-18 – 2026-05-27): Hardening + dev ergonomics. Fixed answer scoring bug, auth/session persistence, and CSRF cookie flow. Added Domains page (objective-level browse). Inline documentation pass + `resources/doc.md` reference guide. `start_dev.ps1` one-command dev startup. Full stack containerized with Docker Compose (backend, frontend, db). Commits: `d6994fb`, `13b1305`, `d1a3e09`, `7b91af7`.
- **Phase 4.5** (2026-05-27 – 2026-05-28): MCP integration + full question-bank audit. Built `mcp_server/` exposing the question bank to Claude Code via three tools: `list_domains`, `list_questions`, `audit_question`. Authored two specialized subagents — `question-researcher` (read-only SY0-701 SME, cites the SY0-701 PDF / NIST / RFCs) and `question-db-admin` (applies structured JSON proposals to source CSV + Postgres in lockstep). Ran a 5-parallel-agent audit across all 248 questions → `resources/audit_summary.md`: 242/248 (97.6%) stored answer keys verified correct on the merits. Applied all 73 derived changes via the agent pipeline — 1 answer-key correction (Q212 Decentralized → Committee-based), 3 stem rewrites (Q65, Q70, Q80), 1 choice text edit (Q70), 68 `objective_code` re-tags including the cross-domain move of Q192–194 (Domain 4 → Domain 1, since honeypot/honeynet/honeyfile live under SY0-701 §1.2 "Deception and disruption technology"). Two cosmetic follow-ups (Q212 explanation, Q65 hint) also applied. Every change independently verified via MCP `audit_question`. **New per-domain question counts: 44/29/21/115/39** (Q192–194 moved from D4 to D1). Artifacts: `resources/audit_proposals.json`, `resources/audit_proposals_summary.md`, `resources/audit_summary.md`, `resources/mcp_tutorial.md`, `.claude/agents/question-researcher.md`, `.claude/agents/question-db-admin.md`.
- **Phase 5 — first pass** (2026-05-28): Content type diversification + § 3.4 gap fill. Plan staged at user's direction: lift every (domain × {multi_select, true_false, ordering}) cell to **≥ 10** before attempting the original plan.md target of ≥ 20. Workflow followed the Phase 4.5 pipeline but in *authoring* mode: `question-researcher` agents emitted structured JSON proposals; a new `resources/phase5_load_proposals.py` helper normalized four parallel-agent format variants and appended rows to the right `domain_<N>_*.csv`; `import_questions` loaded them. **Batch 0** was a 7-question § 3.4 dry run (IDs 250–256) covering HA, site types, platform diversity, capacity planning, DR testing, backups, and power — verified end-to-end before scaling up. **Batch 1** ran 5 researcher agents in parallel, one per domain, producing 136 new questions across all objective codes. Every new question cites the SY0-701 Objectives PDF and at least one named NIST publication / RFC / vendor spec. v2 audit on the new content (5 parallel SME passes, scoped to id ≥ 250): **138/143 AGREE, 5 UNSURE, 0 DISAGREE — 96.5 % pass rate**, within 1.1 pp of the Phase 4.5 baseline (97.6 %). The 5 UNSURE flags (Q282, Q283, Q291, Q309, Q325) were stem-wording / attribution issues; **all 5 were resolved 2026-05-29** via a 10-change-record proposal applied through `question-db-admin` and re-verified via MCP — sign/verify framing on the digital-signature steps, AIA/CRLDP + CT-logs replacement for the OCSP/CRL "publish" language, stem qualifier drops on Q291, pathway-to-violence reattribution on Q309, and a firewall-before-IPS sequence change on Q325. Post-fix pass rate: **143/143 AGREE**. **New per-domain question counts: 71/59/51/142/69 = 392 total** (up from 249). Per-(domain × type) for the three non-MC types is now 10/10/10 in every domain. Per-type distribution: MC 242 / multi_select 50 / true_false 50 / ordering 50. Artifacts: `resources/question_type_gaps.md`, `resources/audit_proposals_5_3_4.json`, `resources/audit_proposals_5_d{1..5}.json`, `resources/audit_summary_v2.md` + per-domain `audit_summary_v2_d{1..5}.md`, `resources/phase5_load_proposals.py`, `resources/phase5_extract_persisted.py`, `resources/phase5_extract_session.py`, `resources/phase5_extract_audit_reports.py`. **Outstanding (Phase 5.1):** lift every (domain × non-MC type) cell from 10 → 20 (~150 more questions).

## Known Issues & Workarounds

- Vite dev server proxy (`/api → localhost:8000`) handles CSRF correctly in dev; Django admin must be hit first in raw HTTP clients to seed the CSRF cookie (API clients like Axios handle this automatically via the CSRF interceptor in `src/api/client.js`).
- Cross-domain `objective_code` re-tags require physically moving the row between `domain_*.csv` files (the CSVs are partitioned by domain). The `question-db-admin` agent will normally refuse a cross-domain retag and bounce it back — explicit authorization in the prompt is required to perform the move. See the Q192–194 precedent in Phase 4.5.
- Direct `AnswerKey.explanation` edits via inline Python can introduce stray escape artifacts (observed: extra trailing apostrophe on Q212 during the answer-key change). Always read the row back and verify via MCP `audit_question` after a content edit.
- Phase 5 surfaced four distinct JSON output formats from parallel `question-researcher` runs (mixing `new_questions` vs. `proposals` wrappers; `choices` as strings vs. `{text}` vs. `{text, order, is_correct}`; correctness in `correct_choice_texts` vs. `correct_choice_text` vs. `correct_choice_orders` vs. inline `is_correct`). `resources/phase5_load_proposals.py` normalizes all four into the CSV importer's canonical shape — extend that normalizer if a sixth variant shows up rather than asking agents to retry.

## Security+ Domain Tracker (Objectives Touched)

> Update at end of each phase.

| Phase | Domains Touched |
|-------|----------------|
| Phase 0 | — |
| Phase 1 | All 5 domains (schema design maps to all) |
| Phase 2 | All 5 domains — 248 questions total; 41/29/21/118/39 by domain |
| Phase 4 | All 5 domains — full API confirmed (login, session, question, answer, progress) |
| Phase 4.5 | All 5 domains — full content audit; 73 fixes applied (1 answer key, 3 stems, 1 choice, 68 retags); counts now 44/29/21/115/39 |
| Phase 5 (first pass) | All 5 domains — content type diversification + § 3.4 gap fill. +143 new questions (7 § 3.4 dry run + 136 bulk). Every (domain × non-MC type) cell now ≥ 10. Counts now 71/59/51/142/69 = 392 total. v2 audit: 96.5 % AGREE, 0 stored-key inversions. |
