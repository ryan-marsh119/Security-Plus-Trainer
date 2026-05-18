# Security+ Trainer — Application Architecture
Phase 3 output | AppArchitect | 2026-05-18

---

## 1. Directory Structure

```
security_plus_trainer/          ← git root
├── backend/                    ← Django project root
│   ├── manage.py
│   ├── requirements.txt
│   ├── securityplus/           ← Django project package
│   │   ├── settings/
│   │   │   ├── base.py         ← shared settings
│   │   │   ├── development.py  ← DEBUG=True, SQLite fallback
│   │   │   └── production.py   ← env-var driven, no DEBUG
│   │   ├── urls.py             ← root URL conf
│   │   └── wsgi.py
│   ├── questions/              ← Domain, Objective, Question, AnswerChoice, AnswerKey
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── management/
│   │       └── commands/
│   │           └── import_questions.py   ← loads Phase 2 CSVs into DB
│   ├── progress/               ← UserQuestionProgress, ExamSession, SessionAnswer, UserDomainProgress
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   └── users/                  ← Auth (extends Django User)
│       ├── models.py
│       ├── views.py
│       └── urls.py
├── frontend/                   ← React (Vite)
│   ├── src/
│   │   ├── App.jsx             ← Router setup
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── StudySession.jsx
│   │   │   ├── PracticeExam.jsx
│   │   │   ├── DomainDetail.jsx
│   │   │   ├── PBQHub.jsx      ← /pbq landing — 5 domain cards
│   │   │   ├── PBQSession.jsx  ← /pbq/:domainId practice
│   │   │   └── Results.jsx
│   │   ├── components/
│   │   │   ├── questions/
│   │   │   │   ├── QuestionWrapper.jsx   ← renders correct component by question_type
│   │   │   │   ├── MultipleChoice.jsx
│   │   │   │   ├── MultiSelect.jsx
│   │   │   │   ├── TrueFalse.jsx
│   │   │   │   ├── OrderingQuestion.jsx  ← drag-and-drop sortable list (PBQ)
│   │   │   │   ├── DragDropQuestion.jsx  ← drag items to labeled zones (PBQ)
│   │   │   │   ├── PBQSimulation.jsx     ← scenario card + sub-questions (PBQ)
│   │   │   │   └── FillBlank.jsx         ← inline text inputs (PBQ)
│   │   │   ├── progress/
│   │   │   │   ├── DomainProgressBar.jsx
│   │   │   │   ├── ObjectiveHeatmap.jsx
│   │   │   │   └── MilestoneTracker.jsx
│   │   │   ├── feedback/
│   │   │   │   ├── HintPanel.jsx         ← two-strike hint (shown on 1st wrong)
│   │   │   │   ├── ExplanationPanel.jsx  ← shown on 2nd wrong or after correct
│   │   │   │   └── ConceptCard.jsx       ← shown after pretest attempt
│   │   │   └── common/
│   │   │       ├── Header.jsx
│   │   │       ├── Button.jsx
│   │   │       └── ProgressRing.jsx
│   │   ├── hooks/
│   │   │   ├── useSession.js
│   │   │   └── useProgress.js
│   │   ├── store/
│   │   │   ├── sessionStore.js   ← Zustand: current question, attempt count, session progress
│   │   │   └── userStore.js      ← Zustand: auth state, overall progress stats
│   │   └── api/
│   │       └── client.js         ← Axios instance + CSRF interceptor
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── package.json
├── mcp_server/                 ← Phase 4.5
├── security_plus_trainer/
│   └── resources/              ← all agent outputs + PDFs
├── CLAUDE.md
├── docker-compose.yml
└── plan.md
```

---

## 2. Django Apps

| App | Models | Responsibility |
|-----|--------|----------------|
| `questions` | Domain, Objective, Question, AnswerChoice, AnswerKey | Content; answer-key logic; CSV import command |
| `progress` | UserQuestionProgress, ExamSession, SessionAnswer, UserDomainProgress | SM-2 state; session builder; scoring |
| `users` | (extends Django User) | Registration, login, logout, profile |

---

## 3. PostgreSQL Schema

Full DDL is in `edu_platform_research.md`. Summary of key decisions:

| Table | Key fields | Notes |
|-------|-----------|-------|
| `domains` | name, number, weight_pct | 5 SY0-701 domains |
| `objectives` | domain_fk, code, title, concept_card | concept_card shown after pretest attempt |
| `questions` | objective_fk, question_text, question_type, difficulty | question_type enum below |
| `answer_choices` | question_fk, text, order, is_correct | MC/multi-select rows |
| `answer_keys` | question_fk, answer_data (JSONB), hint, explanation | canonical answer for all types |
| `users` | Django built-in | extended by users app |
| `user_question_progress` | user_fk, question_fk, ease_factor, interval_days, repetitions, due_date, card_state | SM-2 state |
| `exam_sessions` | user_fk, session_type, started_at, completed_at | study \| exam |
| `session_answers` | session_fk, question_fk, submitted_answer, is_correct, attempt_number | per-question response |
| `user_domain_progress` | user_fk, domain_fk, total_seen, total_correct, is_pbq | denormalized for dashboard |

**question_type enum values:**
`multiple_choice`, `multi_select`, `true_false`, `ordering`, `drag_drop`, `fill_blank`, `pbq_simulation`

**answer_data JSONB shapes by type:**
```json
// multiple_choice / multi_select
{"correct_ids": [2]}
{"correct_ids": [1, 3]}

// ordering
{"ordered_ids": [3, 1, 4, 2]}

// drag_drop
{"matches": {"item_1": "zone_A", "item_2": "zone_B"}}

// fill_blank
{"answers": ["AES", "256"]}

// pbq_simulation
{"steps": [{"step": 1, "expected": "deny tcp any host 10.0.0.1 eq 3389"}]}
```

---

## 4. Django Model Method Signatures

```python
# questions/models.py

class Question(models.Model):
    def get_answer_key(self) -> dict:
        """Returns answer_data dict from related AnswerKey."""

    def get_answer_explanation(self) -> str:
        """Returns full explanation string."""

    def get_hint(self) -> str:
        """Returns hint string — shown on first wrong attempt (Brilliant two-strike)."""

    def show_correct_answers(self) -> list[str]:
        """Returns list of correct answer choice texts (human-readable)."""

    def check_answer(self, submitted: dict) -> bool:
        """Returns True if submitted answer dict matches answer_key."""


# progress/models.py

class ExamSession(models.Model):
    def calculate_score(self) -> dict:
        """Returns:
        {
            'correct': int,
            'total': int,
            'percent': float,
            'by_domain': {domain_id: {'correct': int, 'total': int}}
        }
        """

    def get_next_question(self) -> Optional["Question"]:
        """Study mode: SM-2 due-date ordered, interleaved by objective.
        Exam mode: random, no repeats.
        Never serves 2 consecutive questions from the same objective."""


class UserQuestionProgress(models.Model):
    def update_sm2(self, rating: int) -> None:
        """Update SM-2 fields after a review.
        rating: 0=Again, 1=Hard, 2=Good, 3=Easy
        Updates: ease_factor, interval_days, repetitions, due_date, card_state."""
```

---

## 5. API Specification

**Base URL:** `/api/v1/`
**Auth:** Django session-based (cookies + CSRF token). No JWT — single-domain SPA, no mobile client needed yet.

### Auth endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login/` | Set session cookie |
| POST | `/auth/logout/` | Clear session |
| POST | `/auth/register/` | Create account |
| GET | `/auth/me/` | Current user info |

### Content endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/domains/` | All 5 domains with user accuracy % |
| GET | `/domains/{id}/objectives/` | Objectives + per-objective stats for user |
| GET | `/questions/{id}/` | Single question (answer_key never exposed) |
| GET | `/questions/?domain=1&objective=1.1&question_type=ordering&limit=10` | Filtered list |

### Session endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | `/sessions/` | Create session — body: `{"type": "study" | "exam"}` |
| GET | `/sessions/{id}/next/` | Next question for this session |
| POST | `/sessions/{id}/answers/` | Submit answer |
| GET | `/sessions/{id}/results/` | Full session summary |
| POST | `/sessions/{id}/complete/` | Mark session done |

### Progress endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/progress/` | Overall: streak, mastered count, due count, milestone |
| GET | `/progress/domains/` | Per-domain accuracy + coverage |
| GET | `/progress/objectives/` | Per-objective stats |

### Answer submission — request & response
```json
// POST /sessions/{id}/answers/
// Request:
{
  "question_id": 42,
  "submitted_answer": {"correct_ids": [2]}
}

// Response — first wrong attempt:
{
  "correct": false,
  "attempt_number": 1,
  "hint": "Think about what attacker motivation...",
  "explanation": null
}

// Response — second wrong OR correct:
{
  "correct": true,
  "attempt_number": 2,
  "hint": null,
  "explanation": "Ransomware encrypts or locks files..."
}
```

---

## 6. Pages & User Journey

| Route | Page | Description |
|-------|------|-------------|
| `/login` | Login | Auth form |
| `/register` | Register | Create account |
| `/dashboard` | Dashboard | Milestone tracker, domain heatmap, "Start Studying" CTA |
| `/study` | StudySession | SM-2 queue, concept cards, two-strike hints |
| `/exam` | PracticeExam | 90 q, 90-min timer, no hints, exam simulation |
| `/domains/:id` | DomainDetail | Objective list + accuracy per objective |
| `/pbq` | PBQHub | 5 domain cards with PBQ counts + accuracy |
| `/pbq/:domainId` | PBQSession | Domain-filtered PBQ practice |
| `/results/:sessionId` | Results | Score, wrong answers, full explanations |

---

## 7. PBQ Practice Page

PBQs appear first on the real exam (3–6 questions) and are the hardest type.

**`/pbq` hub:** 5 domain cards showing available PBQ count and user's PBQ accuracy %. "Start All" button for cross-domain mix.

**`/pbq/:domainId` session:** renders interaction component based on `question_type`:

| question_type | Component | Example scenario |
|--------------|-----------|-----------------|
| `ordering` | OrderingQuestion | Arrange incident response steps in correct order |
| `drag_drop` | DragDropQuestion | Match IoC to malware type; place IDS/firewall in network diagram |
| `pbq_simulation` | PBQSimulation | Configure ACL rules; analyze a SIEM log |
| `fill_blank` | FillBlank | Complete nmap command syntax; fill in cipher name |

Rules: no timer in practice mode, two-strike hints apply, PBQ accuracy tracked separately via `user_domain_progress.is_pbq`.

**Content gap:** Phase 5 must add ≥ 5 PBQ questions per domain (25 total) using `pbq_resources.md` archetypes.

---

## 8. Dashboard — 5 Milestones

| Level | Name | Criteria |
|-------|------|---------|
| 1 | Novice | < 20% of questions seen |
| 2 | Apprentice | ≥ 20% seen, ≥ 60% accuracy |
| 3 | Practitioner | ≥ 40% seen, ≥ 70% accuracy |
| 4 | Professional | ≥ 60% seen, ≥ 80% accuracy |
| 5 | Expert | ≥ 80% seen, ≥ 85% accuracy |

**Dashboard widgets:** domain radar chart, objective heatmap grid, streak counter, "X questions due for review" badge, weak-areas callout (objectives with < 60% accuracy).

---

## 9. Session Builder Rules

1. Never serve 2 consecutive questions from the same objective (interleaving — Brilliant pattern)
2. Study mode: SM-2 due date drives priority; overdue questions first
3. New user: serve 1 pretest question per objective → show `concept_card` after attempt
4. Exam mode: 90 random questions, 90-min countdown, no hints, SM-2 not updated until session completes

---

## 10. Frontend Tech Stack

| Tool | Role |
|------|------|
| Vite | Build tool (faster than CRA) |
| React 18 + React Router v6 | UI + client-side routing |
| Zustand | Lightweight state management (2 stores: sessionStore, userStore) |
| Axios | API client with CSRF interceptor |
| Tailwind CSS | Utility-first styling |
| recharts (TBD) | Domain radar chart + objective heatmap |

---

## 11. Auth Strategy

**Session-based (Django sessions + CSRF)**

Rationale:
- Single-domain SPA — no cross-origin auth needed
- No mobile client planned for MVP
- Django's session framework is battle-tested
- CSRF protection built in
- Simpler than JWT (no token refresh, no storage XSS risk)

Flow: `POST /auth/login/` → Django sets `sessionid` cookie → all subsequent requests include cookie + `X-CSRFToken` header (Axios interceptor handles this automatically).

---

## 12. Gaps Requiring Phase 5 Action

No `requests.txt` needed — Phase 2 CSV schema fully covers the DB schema. However Phase 5 must:
- Add ≥ 5 PBQ questions per domain (25 total) — currently sparse
- Validate all 248 existing questions against SY0-701 objectives
- Add more `ordering` and `drag_drop` question types
