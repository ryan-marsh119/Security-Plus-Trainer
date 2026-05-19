# Security+ Trainer — Project Documentation

A full-stack Security+ SY0-701 study platform built with Django, React, and PostgreSQL.
This document explains how the project works end-to-end: data model, API, frontend, and
the learning mechanics that drive the study experience.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [How to Run](#how-to-run)
3. [Data Model](#data-model)
4. [Answer Key System](#answer-key-system)
5. [SM-2 Spaced Repetition](#sm-2-spaced-repetition)
6. [Two-Strike Hint System](#two-strike-hint-system)
7. [API Reference](#api-reference)
8. [Frontend Architecture](#frontend-architecture)
9. [Session Lifecycle](#session-lifecycle)
10. [Authentication](#authentication)
11. [Management Commands](#management-commands)
12. [Dashboard Milestones](#dashboard-milestones)

---

## Project Structure

```
security_plus_trainer/          ← git root
├── backend/                    ← Django project
│   ├── manage.py
│   ├── requirements.txt
│   ├── securityplus/           ← Django project package (settings, urls, wsgi)
│   ├── questions/              ← Content models: Domain, Objective, Question, AnswerKey
│   ├── progress/               ← Progress models: ExamSession, UserQuestionProgress
│   └── users/                  ← Auth views: login, logout, register, me
├── frontend/                   ← Vite + React app
│   └── src/
│       ├── api/client.js       ← Axios instance with CSRF interceptor
│       ├── store/              ← Zustand stores (userStore, sessionStore)
│       ├── pages/              ← Route-level page components
│       └── components/         ← Shared UI components
├── security_plus_trainer/
│   └── resources/              ← All agent outputs, CSVs, and this file
├── docker-compose.yml          ← PostgreSQL container
├── start_dev.ps1               ← One-command dev startup script
└── CLAUDE.md                   ← Claude Code companion guide
```

---

## How to Run

**Prerequisites:** Docker Desktop, Node.js (v18+), Python 3.11+ virtualenv at `venv/`

```powershell
# One command starts everything
.\start_dev.ps1
```

That script:
1. Starts the PostgreSQL container via Docker Compose
2. Polls until the DB accepts connections
3. Runs any pending Django migrations
4. Opens the Django backend server in a new terminal window
5. Opens the Vite frontend dev server in a new terminal window

**Service URLs:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/v1/
- Django Admin: http://localhost:8000/admin/ (dev credentials: `admin` / `admin1234`)

**First-time setup only** (already done if DB container has data):
```powershell
cd backend
..\venv\Scripts\python manage.py migrate
..\venv\Scripts\python manage.py seed_domains
..\venv\Scripts\python manage.py import_questions
```

---

## Data Model

### Content Layer (questions app)

```
Domain (5 rows)
  └── Objective (28 rows — one per SY0-701 sub-objective)
        └── Question (248 rows)
              ├── AnswerChoice (4 rows per MC question)
              └── AnswerKey    (1 row per question — JSONB answer_data)
```

**Domain** — One of the five SY0-701 exam domains.

| Field      | Type    | Notes                          |
|------------|---------|--------------------------------|
| number     | int     | 1–5, used for ordering         |
| name       | str     | e.g. "Security Operations"     |
| weight_pct | decimal | e.g. 28.00 (28% of the exam)   |

**Objective** — A sub-objective like "4.8 Explain appropriate incident response activities."

| Field       | Type | Notes                                                  |
|-------------|------|--------------------------------------------------------|
| code        | str  | Dot-notation, unique: '1.1' through '5.6'              |
| title       | str  | Full objective title from CompTIA exam objectives doc  |
| concept_card| text | 2–4 sentence explanation shown after pretest attempt   |

**Question** — One exam question. `question_type` determines how the UI renders it and
how the server evaluates the submitted answer.

| question_type  | Description                         | UI component needed        |
|----------------|-------------------------------------|----------------------------|
| multiple_choice| One correct answer from 4 choices   | MultipleChoice (done)      |
| multi_select   | Multiple correct answers            | MultiSelect (TODO)         |
| true_false     | True or False                       | TrueFalse (TODO)           |
| ordering       | Drag items into correct order       | OrderingQuestion (TODO)    |
| drag_drop      | Drag items to matching drop zones   | DragDropQuestion (TODO)    |
| fill_blank     | Type command/syntax answers         | FillBlank (TODO)           |
| pbq_simulation | Scenario card + sub-questions       | PBQSimulation (TODO)       |

**AnswerKey** — One-to-one with Question. The `answer_data` JSONB field shape varies:

```json
// multiple_choice / true_false
{ "correct_ids": [42] }

// multi_select
{ "correct_ids": [42, 57] }

// ordering
{ "ordered_ids": [10, 20, 30, 40] }

// drag_drop
{ "matches": { "Firewall": "Perimeter", "IDS": "Internal" } }

// fill_blank
{ "answers": ["nmap", "-sV"] }
```

### Progress Layer (progress app)

**ExamSession** — One study sitting. Tracks which questions have been answered so
`get_next_question()` never serves a duplicate within the same session.

**SessionAnswer** — One answer submission. Multiple rows per question are allowed
because the two-strike system lets the user try again after a wrong answer.

**UserQuestionProgress** — The SM-2 card for one (user, question) pair. Created on
first answer; updated after every study-mode submission. See SM-2 section below.

**UserDomainProgress** — Aggregated accuracy per user/domain. Kept denormalised for
fast dashboard queries (no live COUNT() aggregation on every page load).

---

## Answer Key System

All answer-key logic is funnelled through methods on the `Question` model. Views and
management commands never read `answer_key.answer_data` directly.

```python
question.get_answer_key()        # → raw dict from JSONB
question.get_hint()              # → hint string (may be empty)
question.get_answer_explanation() # → full explanation string
question.show_correct_answers()  # → ['Least privilege', ...]
question.check_answer(submitted) # → True | False
```

The `AnswerKey` model intentionally has no `is_correct` flag on `AnswerChoice`. This
prevents the QuestionSerializer from accidentally leaking correct answers to the client —
choice IDs are just opaque integers to the frontend until the user submits.

---

## SM-2 Spaced Repetition

Study mode uses the SM-2 algorithm (the same algorithm behind Anki) to schedule when
each question should be reviewed.

**Key fields on UserQuestionProgress:**

| Field         | Default | Meaning                                              |
|---------------|---------|------------------------------------------------------|
| ease_factor   | 2.5     | Multiplier for interval growth. Floor: 1.3           |
| interval_days | 1       | Days until the card is due again                     |
| repetitions   | 0       | Consecutive correct answers. Resets on wrong answer  |
| due_date      | today   | Date the card should be shown again                  |
| card_state    | 'new'   | new → learning → review → mastered                  |

**Ratings used in the app** (simplified from the full SM-2 four-grade scale):

| Outcome        | Rating | Effect                           |
|----------------|--------|----------------------------------|
| Correct answer | 2 (Good) | Interval grows normally        |
| Wrong answer   | 0 (Again) | Repetitions reset to 0, interval back to 1 day |

**Card state thresholds:**
- `interval_days >= 21` → mastered
- `repetitions > 0` → review
- otherwise → learning

**Question priority in study mode:**
1. SM-2 due cards (earliest `due_date` first)
2. New questions never seen before (random order)

---

## Two-Strike Hint System

Inspired by Brilliant.org's teaching approach. Every question answer goes through
`SessionAnswerView` which applies this rule:

```
First wrong attempt  → return hint (from answer_key.hint)
Second wrong attempt → return explanation (from answer_key.explanation)
Correct answer       → return explanation immediately
Exam mode            → never return hint or explanation
```

This forces active recall before giving away the answer, which research shows improves
retention compared to immediately showing explanations.

---

## API Reference

**Base URL:** `http://localhost:8000/api/v1/`
**Auth:** Session cookie. All endpoints require authentication except login and register.
**CSRF:** Required on POST/PUT/PATCH/DELETE. Read from the `csrftoken` cookie.

### Auth

| Method | Path             | Description                             |
|--------|------------------|-----------------------------------------|
| POST   | /auth/login/     | Authenticate. Body: {username, password}|
| POST   | /auth/logout/    | Destroy session                         |
| POST   | /auth/register/  | Create account. Body: {username, email, password} |
| GET    | /auth/me/        | Current user info                       |

### Content

| Method | Path                          | Description                          |
|--------|-------------------------------|--------------------------------------|
| GET    | /domains/                     | All 5 domains                        |
| GET    | /domains/<id>/objectives/     | Objectives for a domain              |
| GET    | /questions/<id>/              | Single question with answer choices  |
| GET    | /questions/                   | Filtered question list (see params)  |

`/questions/` query params:
- `?question_type=ordering,drag_drop` — comma-separated type filter
- `?domain=4` — filter by domain pk

### Sessions

| Method | Path                       | Description                            |
|--------|----------------------------|----------------------------------------|
| POST   | /sessions/                 | Create session. Body: {session_type, domain_filter?} |
| GET    | /sessions/<id>/next/       | Next question for this session         |
| POST   | /sessions/<id>/answers/    | Submit answer. Body: {question_id, answer} |
| GET    | /sessions/<id>/results/    | Score summary                          |
| POST   | /sessions/<id>/complete/   | Mark session finished                  |

Answer submission response shape:
```json
{
  "correct": false,
  "attempt_number": 1,
  "hint": "Think about the principle of least privilege...",
  "explanation": null
}
```

### Progress

| Method | Path                    | Description                          |
|--------|-------------------------|--------------------------------------|
| GET    | /progress/              | Overall stats (seen, mastered, due)  |
| GET    | /progress/domains/      | Per-domain accuracy                  |
| GET    | /progress/objectives/   | Per-objective coverage               |

---

## Frontend Architecture

```
src/
├── api/
│   └── client.js           Axios instance; CSRF interceptor
├── store/
│   ├── userStore.js         Auth state (user, isLoading) + actions
│   └── sessionStore.js      Active session state + actions
├── pages/
│   ├── Login.jsx            /login
│   ├── Register.jsx         /register
│   ├── Dashboard.jsx        /dashboard — stats + navigation
│   ├── StudySession.jsx     /study — SM-2 study mode
│   ├── PracticeExam.jsx     /exam — timed 90-question exam
│   ├── PBQHub.jsx           /pbq — domain selector for PBQ practice
│   ├── PBQSession.jsx       /pbq/:domainId — PBQ practice session
│   └── Results.jsx          /results — post-session score
└── components/
    └── questions/
        └── QuestionWrapper.jsx  Question card + answer + feedback
```

**State management:** Zustand (two stores).
- `userStore` — who is logged in. Persists as long as the session cookie is valid.
- `sessionStore` — the active study/exam session. Cleared when the session completes.

**Routing:** React Router v6 with a `RequireAuth` wrapper that redirects unauthenticated
users to `/login`.

**Styling:** Tailwind CSS v4 via `@tailwindcss/vite` plugin. No separate config file needed.

**Dev proxy:** Vite proxies `/api` requests to `http://localhost:8000`, so the frontend
and backend run on different ports without CORS issues in development.

---

## Session Lifecycle

```
User clicks "Study Mode"
        ↓
StudySession mounts → sessionStore.startSession('study')
        ↓
POST /sessions/  →  returns {id: 5, session_type: 'study', ...}
        ↓
GET /sessions/5/next/  →  returns question object
        ↓
QuestionWrapper renders question + choices
        ↓
User selects answer + clicks Submit
        ↓
POST /sessions/5/answers/ {question_id: 12, answer: {selected_id: 42}}
        ↓
Server: check_answer() → SM-2 update → return {correct, hint/explanation}
        ↓
QuestionWrapper shows feedback panel
        ↓
User clicks "Next Question" → fetchNextQuestion() → GET /sessions/5/next/
        ↓
... repeat until GET /sessions/5/next/ returns 204 No Content
        ↓
User clicks "End Session" → completeSession()
        ↓
POST /sessions/5/complete/  +  GET /sessions/5/results/
        ↓
navigate('/results', {state: {results}})  →  Results page
```

---

## Authentication

Session-based using Django's built-in session framework.

**Why not JWT?**
This is a single-domain SPA with no mobile client. Session cookies are simpler,
stored server-side (no token expiry logic), and HttpOnly cookies cannot be read by
JavaScript (XSS-resistant). JWTs would add complexity with no benefit here.

**CSRF protection:**
Django's `CsrfViewMiddleware` requires an `X-CSRFToken` header on all state-changing
requests. Django sets a `csrftoken` cookie on the first response. The Axios interceptor
in `api/client.js` reads this cookie and attaches the header automatically.

**Session cookie settings (settings.py):**
- `SESSION_COOKIE_HTTPONLY = True` — JS cannot read the session cookie
- `SESSION_COOKIE_SAMESITE = 'Lax'` — protects against CSRF from other origins
- `CSRF_COOKIE_SAMESITE = 'Lax'` — same protection for the CSRF cookie

---

## Management Commands

All commands run from the `backend/` directory:

```powershell
# Seed the 5 SY0-701 domains and 28 objectives (idempotent)
..\venv\Scripts\python manage.py seed_domains

# Import all questions from resources/domain_*.csv (idempotent — skips duplicates)
..\venv\Scripts\python manage.py import_questions

# Import a single CSV file
..\venv\Scripts\python manage.py import_questions --csv path/to/file.csv

# Validate CSV rows without writing to the database
..\venv\Scripts\python manage.py import_questions --dry-run

# Standard Django commands
..\venv\Scripts\python manage.py makemigrations
..\venv\Scripts\python manage.py migrate
..\venv\Scripts\python manage.py createsuperuser
```

**CSV format** (required columns for `import_questions`):

| Column                  | Description                                      |
|-------------------------|--------------------------------------------------|
| objective_code          | Must match an existing Objective.code (e.g. '4.8') |
| question_text           | Full question prompt                             |
| question_type           | One of the Question.QUESTION_TYPES values        |
| difficulty              | 'easy' \| 'medium' \| 'hard'                    |
| answer_choices_json     | JSON array: `[{"text": "Option A"}, ...]`        |
| correct_answer_key_json | JSON dict matching Question.check_answer() shape |
| hint                    | (optional) Shown on first wrong attempt          |
| explanation             | (optional) Shown on correct or second wrong      |

---

## Dashboard Milestones

The dashboard tracks progress toward five milestones based on questions seen and
overall accuracy:

| Milestone    | Trigger                              |
|--------------|--------------------------------------|
| Novice       | < 20% of questions seen              |
| Apprentice   | ≥ 20% seen, ≥ 60% accuracy          |
| Practitioner | ≥ 40% seen, ≥ 70% accuracy          |
| Professional | ≥ 60% seen, ≥ 80% accuracy          |
| Expert       | ≥ 80% seen, ≥ 85% accuracy          |

Milestone logic is implemented in the frontend Dashboard component using data from
`GET /progress/` (total_seen, total_questions) and `GET /progress/domains/`
(accuracy per domain).
