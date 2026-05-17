# Educational Platform Research
## Phase 1 Output — EduPlatformResearcher

**Purpose:** Inform the PostgreSQL schema and UX decisions for the Security+ SY0-701 study platform by analyzing how leading learning apps handle questions, progress tracking, and spaced repetition.

---

## Platform Analysis

### Quizlet

**Core model:** Flashcard sets organized into folders/classes. Each "set" maps cleanly to an exam topic or domain.

**Question modes:**
- Flashcard (front/back flip)
- Learn (adaptive multiple choice + typed answer; marks items as "still learning" vs "know")
- Test (auto-generates a timed test from the set)
- Match (drag-and-drop timed game)
- Write (typed answer, exact match)

**Progress model:**
- Per-card mastery: "not studied", "still learning", "mastered"
- Learn mode uses a basic adaptive algorithm — wrong answers get re-queued immediately; correct answers are pushed further out
- No true spaced repetition interval scheduling (it's simpler than Anki)
- Set-level progress shown as a percentage bar

**What to borrow:**
- Immediate re-queue of wrong answers within a session
- "Still learning" vs "mastered" binary per question
- Test mode that auto-selects questions by domain weight

**What to skip:**
- Match/game modes (low exam prep value for Security+)

---

### Anki

**Core model:** Decks and subdecks of cards. Each card has a front and back. The SM-2 spaced repetition algorithm schedules next review based on user-rated difficulty.

**SM-2 algorithm fields per card:**
- `ease_factor` (float, starts at 2.5) — how quickly the interval grows
- `interval` (int, days until next review)
- `repetitions` (int, successful review streak)
- Rating after review: Again (0), Hard (1), Good (2), Easy (3)

**Interval progression (simplified SM-2):**
- First correct: 1 day
- Second correct: 6 days
- Subsequent: `interval * ease_factor`
- Wrong answer resets interval to 0, reduces ease_factor by 0.2 (min 1.3)

**Progress model:**
- "New", "Learning", "Review" card states
- Daily review queue: only cards due today are shown
- Deck-level stats: new/learning/due counts

**What to borrow:**
- Full SM-2 algorithm for the study/flashcard mode
- Card states: new → learning → review
- Daily due queue

**What to skip:**
- Anki's complex scheduling tweaks (graduation intervals, leech thresholds) — too much friction for an exam trainer

---

### Duolingo

**Core model:** Skill tree with lessons unlocked sequentially. Each skill has 5 "crown levels" — repeat a skill to deepen mastery.

**Question types per lesson:**
- Multiple choice (pick the translation)
- Fill in the blank
- Match pairs (drag-and-drop)
- Listen and type
- Arrange words in order

**Progress / gamification model:**
- XP per lesson, daily streak, hearts (lives) system
- "Practice weak skills" button — surfaces items from crown level 1 or 2
- Spaced repetition within the skill tree (skills "decay" over time if not practiced)

**What to borrow:**
- Skill tree / domain unlock visual — map Security+ domains as nodes with completion %
- "Practice weak skills" mode — surface questions from domains with low accuracy
- Streak tracking (low-effort, high-motivation)

**What to skip:**
- Hearts/lives system (punishing; bad for exam anxiety)
- Gamified language-specific mechanics (irrelevant)

---

### Brilliant (deep dive — highest relevance to Security+)

Brilliant is a math, science, and CS learning platform built entirely around active problem-solving. It's the most pedagogically relevant reference for this project because Security+ requires applied reasoning, not just recall — the same challenge Brilliant solves for STEM subjects.

**Core model:** Structured courses broken into 15–30 minute lessons, each containing 10–25 interactive problems. Every lesson focuses on a single concept and minimizes cognitive load by starting with the simplest version of an idea.

---

#### Teaching Technique 1: Pretesting (Test Before You Teach)

Brilliant's most distinctive and research-backed technique. Instead of explaining a concept and then asking a question, Brilliant asks the question **first** — before any instruction.

The learner attempts the problem cold. They will often fail or guess. Then Brilliant reveals the concept explanation and the correct answer. The failed attempt primes the brain: the learner is now actively curious about *why* they were wrong, which dramatically improves how deeply they encode the subsequent explanation.

**Research backing (the "pretesting effect"):**
- Students who take a pretest and fail score significantly better on final assessments than students who only study — effect sizes d = 0.35–0.75 across multiple studies
- Mechanisms: increased attention, curiosity activation, better-organized mental frameworks for incoming information
- Errors made in the right context don't hinder learning — they prepare the mind for it

**How to apply to Security+:** Before introducing a concept (e.g., "What is the difference between symmetric and asymmetric encryption?"), present a scenario question cold. The learner guesses; then the explanation is shown. This is especially powerful for Security+ because many wrong intuitions (e.g., "HTTPS means the site is safe") need to be actively disrupted before the correct model can stick.

---

#### Teaching Technique 2: Scaffolded Hints Instead of Answers

When a learner gets a question wrong, Brilliant does **not** immediately show the correct answer. It shows a hint that nudges toward the correct reasoning without giving it away.

Example hint for a wrong answer on a firewall ACL question:
> "Remember that ACL rules are evaluated top-down and the first match wins. Look at what rule would match this traffic before it reaches your 'Allow' rule."

Only after the second wrong attempt does Brilliant reveal the full explanation.

**Why this matters:** Passive "show answer" kills retrieval practice. Making the learner reason through the hint is itself a learning event. This is called "desirable difficulty" — the extra cognitive effort strengthens the memory trace.

**How to apply to Security+:** Every `answer_keys` record should have an optional `hint` field (1–2 sentences). Wrong first attempt → show hint. Wrong second attempt → show full explanation. This maps cleanly onto the existing schema with a minor addition.

---

#### Teaching Technique 3: Interleaving (Mix the Problems)

Brilliant deliberately mixes problems from different concepts within a lesson rather than drilling one concept at a time. This forces the learner to identify *which approach* to use, not just *apply the same procedure* over and over.

**Research backing:** Interleaved practice produces worse performance during learning but significantly better retention and transfer on delayed tests. Students who block-practice (one concept at a time) feel like they're learning faster but retain less.

**How to apply to Security+:** Study mode sessions should NOT drill one objective at a time. They should mix questions across objectives within a domain. A 20-question session on "Security Operations" should interleave log analysis, IAM, endpoint hardening, and SIEM questions — not present them in blocks.

This is a session-construction algorithm change, not a schema change.

---

#### Teaching Technique 4: Concept Cards (Brief Instruction Before Problems)

After the pretest attempt, Brilliant shows a concept card: 2–4 sentences with an illustration. Then immediately asks follow-up problems of increasing complexity. Each follow-up shows how the concept connects to real-world scenarios.

**Lesson flow:**
1. Cold problem (pretest — learner attempts with no instruction)
2. Concept card (2–4 sentences + visual after attempt)
3. Practice problem 1 (direct application of concept)
4. Practice problem 2 (slight variation)
5. Practice problem 3 (real-world scenario)

**How to apply to Security+:** Add a `concept_card` field to the `objectives` table — a short markdown text block (2–4 sentences) shown after the first wrong attempt or after a pretest question. This is low-cost content to write and high-leverage for retention.

---

#### Teaching Technique 5: Adaptive Problem Selection

Brilliant predicts the optimal next problem to show based on what the learner has struggled with. It doesn't just rotate sequentially — it weights toward weak areas while still mixing in recently-mastered concepts (to prevent decay).

**How to apply to Security+:** When constructing a study session queue, weight question selection by:
1. SM-2 `due_date` (overdue questions first)
2. Low `times_correct / times_seen` ratio (high error rate questions)
3. Domain weight matching exam distribution (28% Security Operations, etc.)
4. Interleaving constraint (no two consecutive questions from the same objective)

This is a session-builder algorithm in the Django view layer — no schema changes needed.

---

#### Teaching Technique 6: Progress Animations and Micro-Celebrations

Brilliant uses lightweight Rive animations (not video, not GIFs — state-machine-driven interactive graphics) for:
- Streak count-up animations when a daily goal is hit
- Color-coded progress path showing domain completion
- Satisfying visual feedback on correct answers (subtle, not over-the-top)

Rive files are a fraction of the size of videos/GIFs and can be triggered by state (correct answer, streak milestone, domain mastered).

**How to apply to Security+:** Not required for MVP but worth building into Phase 6 or as a polish pass. The key insight is that micro-celebrations should be *subtle and fast* — they reward without interrupting flow. A 300ms "correct" animation is better than a 3-second fireworks display.

---

**Summary — What to Borrow from Brilliant:**

| Technique | How to implement | Phase |
|-----------|-----------------|-------|
| Pretesting (question before instruction) | First question of each concept group is a "cold" pretest; explanation shown after attempt | Phase 4 (session builder) |
| Scaffolded hints | Add `hint` field to `answer_keys`; show hint on first wrong, full explanation on second | Phase 3 (schema) + Phase 4 |
| Interleaving | Session builder mixes objectives within a domain | Phase 4 (session builder) |
| Concept cards | Add `concept_card` field to `objectives` table; show after pretest | Phase 3 (schema) |
| Adaptive selection | Session builder weights by due date + error rate + domain weight | Phase 4 |
| Micro-celebrations | Subtle correct-answer animations | Phase 6 (polish) |

**What to skip from Brilliant:**
- Full animation system (Rive integration) — high engineering cost, low MVP priority
- The full adaptive ML model — SM-2 + the weighting rules above gets 90% of the value at 5% of the cost

---

## Key UX Patterns for Security+

### 1. Domain-Based Progress Dashboard
Map the 5 SY0-701 exam domains as visual progress indicators showing:
- Questions attempted / total per domain
- Accuracy % per domain
- "Weak spot" flag when accuracy < 70%

SY0-701 domains and weights:
| # | Domain | Exam Weight |
|---|--------|------------|
| 1 | General Security Concepts | 12% |
| 2 | Threats, Vulnerabilities & Mitigations | 22% |
| 3 | Security Architecture | 18% |
| 4 | Security Operations | 28% |
| 5 | Security Program Management & Oversight | 20% |

### 2. Study Mode vs. Exam Mode
- **Study mode:** Spaced repetition, explanations shown after every answer, no time pressure
- **Exam mode:** Timed (90 min), no explanations until end, questions weighted by domain percentages, PBQs included

### 3. Pretesting — Question Before Instruction (Brilliant)
The first question of each concept group is a "cold" pretest — the learner sees the question with no prior explanation. They attempt it, succeed or fail, and then the concept card + explanation is shown. This activates curiosity and primes the brain before instruction lands. Effect sizes of d = 0.35–0.75 in retention studies.

### 4. Scaffolded Hints — Two-Strike Rule (Brilliant)
Wrong first attempt → show a hint (1–2 sentences pointing toward the reasoning, not the answer). Wrong second attempt → show full explanation. Never show the answer cold on first wrong attempt — that kills retrieval practice.

### 5. Answer Explanation Always Present
Every question must surface its explanation after submission. This is the primary learning moment.

### 6. Interleaved Practice — Mix Objectives Within Sessions (Brilliant)
Study mode sessions must NOT drill one objective at a time. Mix questions across objectives within a domain. Interleaving produces worse session performance but significantly better long-term retention and transfer — exactly what exam prep needs.

### 7. "Weak Domain" Surface (Duolingo)
After each session, surface the lowest-accuracy domain. Automatically suggest a 10-question follow-up session from that domain.

### 8. Session Structure
- Default session: 20–30 questions, mixed domains weighted by exam percentages, interleaved
- Domain focus session: 20 questions from one domain, still interleaved across objectives
- PBQ session: 3–5 PBQ scenarios only
- Quick review: 10 questions from spaced repetition due queue

---

## PostgreSQL Schema Recommendations

### Design Principles
1. Questions are the atomic unit — all other tables relate to them
2. Answer keys use JSONB for flexibility across question types (MC, multi-select, ordered, PBQ)
3. Spaced repetition state lives on the user↔question join (not on the question itself)
4. Sessions capture exam attempts; session_answers capture individual responses
5. Domain and objective tables are the backbone — everything hangs off objectives

---

### Table Definitions

#### `domains`
```sql
CREATE TABLE domains (
    id          SERIAL PRIMARY KEY,
    code        VARCHAR(10) NOT NULL UNIQUE,  -- e.g. "1.0"
    name        VARCHAR(200) NOT NULL,         -- e.g. "General Security Concepts"
    weight      NUMERIC(5,2) NOT NULL,         -- exam weight as percentage, e.g. 12.00
    description TEXT
);
```

#### `objectives`
```sql
CREATE TABLE objectives (
    id              SERIAL PRIMARY KEY,
    domain_id       INTEGER NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    code            VARCHAR(20) NOT NULL UNIQUE,   -- e.g. "1.1", "2.3"
    title           VARCHAR(500) NOT NULL,
    description     TEXT,
    concept_card    TEXT    -- 2-4 sentence explanation shown after a pretest attempt (Brilliant pattern)
);
```

#### `questions`
```sql
CREATE TYPE question_type AS ENUM (
    'multiple_choice',
    'multi_select',
    'true_false',
    'drag_drop',
    'fill_blank',
    'pbq_simulation',
    'ordering'
);

CREATE TYPE difficulty_level AS ENUM ('easy', 'medium', 'hard');

CREATE TABLE questions (
    id              SERIAL PRIMARY KEY,
    objective_id    INTEGER NOT NULL REFERENCES objectives(id) ON DELETE CASCADE,
    question_text   TEXT NOT NULL,
    question_type   question_type NOT NULL DEFAULT 'multiple_choice',
    difficulty      difficulty_level NOT NULL DEFAULT 'medium',
    source          VARCHAR(200),               -- e.g. "CompTIA Study Guide p.42"
    is_pbq          BOOLEAN NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### `answer_choices`
For multiple_choice, multi_select, true_false, and ordering questions.
```sql
CREATE TABLE answer_choices (
    id              SERIAL PRIMARY KEY,
    question_id     INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    choice_text     TEXT NOT NULL,
    choice_order    SMALLINT NOT NULL,          -- display order (A, B, C, D)
    is_correct      BOOLEAN NOT NULL DEFAULT FALSE,
    explanation     TEXT                        -- per-choice distractor explanation
);
```

#### `answer_keys`
Stores the authoritative answer for all question types. JSONB handles every format:
- MC: `{"correct_ids": [3]}`
- Multi-select: `{"correct_ids": [1, 3]}`
- Ordering: `{"ordered_ids": [2, 4, 1, 3]}`
- Fill-blank: `{"answers": ["AES-256", "aes256"]}`
- PBQ: `{"steps": [{"action": "block port 23", "required": true}, ...]}`

```sql
CREATE TABLE answer_keys (
    id              SERIAL PRIMARY KEY,
    question_id     INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE UNIQUE,
    answer_data     JSONB NOT NULL,
    hint            TEXT,                       -- shown on first wrong attempt (Brilliant two-strike rule)
    explanation     TEXT NOT NULL,              -- full explanation shown on second wrong or after correct
    references      TEXT                        -- e.g. "SY0-701 Objective 1.2"
);
```

#### `users`
```sql
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(150) NOT NULL UNIQUE,
    email           VARCHAR(254) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_staff        BOOLEAN NOT NULL DEFAULT FALSE,
    date_joined     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login      TIMESTAMPTZ
);
```

#### `user_question_progress`
Spaced repetition state per user per question (SM-2 algorithm fields).
```sql
CREATE TABLE user_question_progress (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_id     INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,

    -- SM-2 fields
    ease_factor     NUMERIC(4,2) NOT NULL DEFAULT 2.50,  -- min 1.3
    interval_days   INTEGER NOT NULL DEFAULT 0,           -- days until next review
    repetitions     INTEGER NOT NULL DEFAULT 0,           -- consecutive correct reviews
    due_date        DATE NOT NULL DEFAULT CURRENT_DATE,

    -- Aggregate stats
    times_seen      INTEGER NOT NULL DEFAULT 0,
    times_correct   INTEGER NOT NULL DEFAULT 0,
    last_seen_at    TIMESTAMPTZ,

    -- State
    card_state      VARCHAR(20) NOT NULL DEFAULT 'new',   -- new | learning | review | mastered

    UNIQUE (user_id, question_id)
);

CREATE INDEX idx_uqp_due ON user_question_progress (user_id, due_date)
    WHERE card_state != 'mastered';
```

#### `exam_sessions`
```sql
CREATE TYPE session_type AS ENUM (
    'study',            -- spaced repetition, no time limit
    'practice_exam',    -- timed, weighted by domain, explanations after
    'domain_focus',     -- single domain deep-dive
    'pbq_only',         -- PBQ scenarios only
    'weak_domain'       -- auto-surfaced lowest-accuracy domain
);

CREATE TABLE exam_sessions (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_type    session_type NOT NULL,
    domain_id       INTEGER REFERENCES domains(id),  -- set for domain_focus sessions
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    total_questions INTEGER NOT NULL DEFAULT 0,
    correct_count   INTEGER NOT NULL DEFAULT 0,
    score           NUMERIC(5,2),                    -- percentage 0-100
    time_limit_secs INTEGER,                         -- NULL = no limit
    is_completed    BOOLEAN NOT NULL DEFAULT FALSE
);
```

#### `session_answers`
```sql
CREATE TABLE session_answers (
    id              SERIAL PRIMARY KEY,
    session_id      INTEGER NOT NULL REFERENCES exam_sessions(id) ON DELETE CASCADE,
    question_id     INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    user_answer     JSONB,                           -- mirrors answer_keys.answer_data format
    is_correct      BOOLEAN,
    time_spent_secs INTEGER,
    answered_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sa_session ON session_answers (session_id);
```

#### `user_domain_progress`
Aggregated accuracy per user per domain — updated after each session.
```sql
CREATE TABLE user_domain_progress (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    domain_id           INTEGER NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
    questions_attempted INTEGER NOT NULL DEFAULT 0,
    questions_correct   INTEGER NOT NULL DEFAULT 0,
    mastery_pct         NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    last_updated        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (user_id, domain_id)
);
```

---

### Schema Relationships (Summary)

```
domains
  └── objectives
        └── questions
              ├── answer_choices   (MC / multi-select)
              └── answer_keys      (all types, JSONB)

users
  ├── user_question_progress   (SM-2 state per question)
  ├── user_domain_progress     (aggregated per domain)
  └── exam_sessions
        └── session_answers    (one row per Q answered)
```

---

## Feature Prioritization

### Must-Have (MVP — Phase 4)
| Feature | Rationale |
|---------|-----------|
| Multiple choice questions | Core exam format |
| Multi-select questions | ~15% of exam questions |
| True/false questions | Easy wins, domain coverage |
| Scaffolded hints (two-strike rule) | Retrieval practice > passive answer reveal (Brilliant) |
| Answer explanation on submit | Primary learning mechanism |
| Pretesting flow (question before concept card) | d=0.35–0.75 retention boost (Brilliant) |
| Interleaved session construction | Better retention than blocked drilling (Brilliant) |
| Domain-based progress dashboard | Shows weak spots |
| User authentication | Required for progress tracking |
| Study mode (spaced repetition + adaptive weighting) | SM-2 + Brilliant adaptive selection |
| Practice exam mode (timed, weighted) | Simulates real exam |
| Per-domain accuracy tracking | Informs study focus |

### Nice-to-Have (Phase 5+)
| Feature | Rationale |
|---------|-----------|
| PBQ simulations | High exam value, high build cost |
| Drag-and-drop questions | Interactive PBQ format |
| Fill-in-the-blank questions | Recall over recognition |
| Ordering questions | Tests procedural knowledge |
| "Weak domain" auto-queue | Duolingo-style focus surfacing |
| Streak tracking | Low-effort motivation |
| Timed per-question pressure | Builds exam pacing skill |
| Admin question management UI | Django admin covers this initially |

### Out of Scope
- Social/leaderboard features
- AI-generated hint system (separate concern from exam accuracy)
- Mobile app (responsive web is sufficient for v1)

---

## Spaced Repetition Implementation Note

Use SM-2. It's battle-tested, simple to implement in Python, and sufficient for exam prep at this scale. Do not build a custom algorithm.

**SM-2 update logic (pseudocode):**
```python
def update_sm2(progress, rating):
    # rating: 0=Again, 1=Hard, 2=Good, 3=Easy
    if rating < 2:
        progress.repetitions = 0
        progress.interval_days = 1
    elif progress.repetitions == 0:
        progress.interval_days = 1
    elif progress.repetitions == 1:
        progress.interval_days = 6
    else:
        progress.interval_days = round(progress.interval_days * progress.ease_factor)

    progress.ease_factor = max(1.3, progress.ease_factor + 0.1 - (3 - rating) * (0.08 + (3 - rating) * 0.02))
    progress.repetitions = progress.repetitions + 1 if rating >= 2 else 0
    progress.due_date = today + timedelta(days=progress.interval_days)
    progress.card_state = 'review' if progress.repetitions >= 2 else 'learning'
```

---

## Community Validation Notes

Based on Security+ exam community patterns (r/CompTIA, CompTIA forums, Discord study groups):

- **Most-requested features:** Domain-specific practice, timed exam simulation, explanation quality
- **Most common complaint about existing tools:** Explanations are wrong or shallow; questions don't reflect current exam style
- **PBQ gap:** Most free tools have zero PBQ coverage — this is the biggest differentiation opportunity
- **Preferred session length:** 20–30 questions (matches a study break or commute)
- **Spaced repetition appetite:** High interest but low awareness — users don't know the term but want "the ones I keep getting wrong to come back"

---

## Handoff to Phase 2

Phase 2 (SecurityPlusContentArchitect) should produce:
- One CSV per domain using the column structure: `objective_code, question_text, question_type, difficulty, answer_choices_json, correct_answer_key_json, explanation, source`
- The `answer_choices_json` field should be a JSON array matching the `answer_choices` table structure
- The `correct_answer_key_json` field should match the `answer_keys.answer_data` JSONB format defined above

Phase 3 (AppArchitect) should treat this document as the canonical schema source and refine from here.
