# Security+ SY0-701 Study Platform: Development Plan
## Dual Learning Goals: Claude Code Mastery + Security+ Exam Prep

**Project Goal:** Build a full-stack Security+ SY0-701 study platform using Claude Code as your primary development tool, treating this as an opportunity to become "AI-literate" rather than just AI-assisted. By shipping real code to production while practicing agentic collaboration patterns, you'll emerge with both a working exam trainer AND practical mastery of Claude Code workflows that transfer to any future project.

**Tech Stack:** Django + React + PostgreSQL → Docker → Railway

**Timeline:** 1–2 weeks for MVP + MCP server; 3–4 weeks with Phase 6/7 + documentation

---

## Core Philosophy: Phases as Scaffolding, Not Strict Gates

These phases are your *starting scaffold*, not a waterfall gate. You'll bounce between them—discovering the schema is wrong during Phase 4, refactoring Phase 2 content extraction, adding new questions from Phase 5 feedback. That's not a failure; it's real Claude Code work. **Update CLAUDE.md and relevant artifacts each time you loop back**, then continue forward.

---

## Phase 0: Project Setup & Environment Validation

**Goal:** Sweep the workshop. Ensure dev environment is working, repo is initialized, Claude Code is comfortable in your terminal/VS Code, and CLAUDE.md is started.

**Deliverables:**
- [ ] GitHub repo created with `.gitignore` (Python, Django, Node, Docker volumes, secrets, `.env`)
- [ ] First version of `CLAUDE.md` in project root (see template below)
- [ ] `README.md` stub (expand as you go)
- [ ] Python virtualenv created and confirmed working
- [ ] PostgreSQL or Docker Compose for Postgres verified running locally
- [ ] **Claude Code test:** open the repo in terminal via `claude`, then in VS Code extension. Verify both can read/write files.

**CLAUDE.md Starter Template:**
```markdown
# Security+ Trainer Project Companion

## Project Goal
Build a full-stack Security+ SY0-701 study platform + learn Claude Code agentic workflows.

## Tech Stack
- Backend: Django + PostgreSQL
- Frontend: React
- Deployment: Docker → Railway
- Claude integration: MCP server (Phase 4.5 milestone)

## Directory Structure
- /backend/        — Django project
- /frontend/       — React project
- /resources/      — CompTIA official study materials
- /mcp_server/     — MCP server for live exam data (Phase 4.5)

## How to Run
[Fill in as Phase 0 progresses]

## Conventions & Rules
[Add as they emerge]

## Known Issues & Workarounds
[Emerge as you work; keep updated]

## Objectives Touched (Security+ Domain Tracker)
[Update at end of each phase]
```

**How this teaches Claude Code:**
- CLAUDE.md discipline is the single highest-leverage skill. Every phase ends with "what future-Claude needs to know that isn't in the code."
- Testing Claude in two environments (terminal + VS Code) surfaces the difference: terminal shows agentic loops most clearly; VS Code feels smoother but hides machinery.

---

## Phase 1: Educational Platform Research

**Agent Name:** `EduPlatformResearcher`

**Goal:** Understand how Quizlet, Anki, Duolingo, and similar platforms structure questions, progress tracking, and spaced repetition. Translate insights into PostgreSQL schema recommendations.

**Before Starting:** Enter plan mode (`Shift+Tab` twice in terminal Claude). Review the plan together, then let Claude execute.

**Starting Prompt:**
```
Activate as EduPlatformResearcher.

You are an expert in modern digital learning platforms. Analyze how Quizlet, Anki, Duolingo,
and similar education apps implement interactive learning.

Focus on:
- User learning flows and engagement techniques
- Implementation of different question formats: multiple choice, multi-select, true/false,
  drag-and-drop, and performance-based questions (PBQs)
- Progress tracking, spaced repetition, and dashboards
- How data for these question types is typically structured

Provide PostgreSQL-friendly schema suggestions and best practices tailored for a CompTIA
Security+ study application.
```

**Sub-agent suggestion:** While EduPlatformResearcher explores patterns, spawn a side sub-agent to search Security+ community platforms (Reddit, Discord) to validate your feature list against real user needs.

**Deliverables:**
- [ ] `security_plus_trainer/resources/edu_platform_research.md` — PostgreSQL schema suggestions, feature prioritization, educational UX patterns
- [ ] Updated CLAUDE.md with schema notes

---

## Phase 2: Security+ Content Extraction & Architecture

**Agent Name:** `SecurityPlusContentArchitect`

**Goal:** Extract SY0-701 objectives, official CompTIA questions (or PBQs), YouTube resources, and practice tests from the PDFs in `/resources/`. Map to the 6 exam domains. Flag hallucinations and coverage gaps. Links for YouTube resources and practice test sites can be found in the links.md file in the `/resources/`.

**Critical Note:** Claude can drop words from answers or pick the wrong correct choice. Don't over-trust this phase. Phase 7 (Evals) is what makes extraction trustworthy. For now, treat this as "structured extraction with manual spot-checking."

**Starting Prompt:**
```
Activate as SecurityPlusContentArchitect.

You are a certified CompTIA Security+ instructor and curriculum designer.

You will be provided with official CompTIA SY0-701 objectives, PDFs, YouTube links, free
practice test websites, and a report on free PBQ resources.

Your tasks:
1. Analyze all provided materials and map them to the official SY0-701 domains and objectives.
2. Identify coverage gaps.
3. Structure the content into clean, importable CSV files.
4. Extract questions from the provided resources. Use any existing explanations. Only generate
   an explanation if one is not provided in the source material.

Every question must include:
- A clear answer_key that supports single answers, multiple answers, ordered answers, and
  complex PBQ responses.
- A detailed answer_explanation field that explains why the answer is correct, including
  relevant concepts and best practices.

Focus on accurately aggregating and structuring the official and high-quality resources
provided.

Maintain a detailed log of all extracted questions, answer_keys, and answer_explanations for
potential later reference by Phase 3.

Store all output files in security_plus_trainer/resources/:
- question_answer_log.txt — full extraction log
- domain_<name>.csv — one CSV per domain
- coverage_map.md — domain/objective coverage summary
- extraction_log.txt — hallucinations, gaps, manual corrections
```

**Sub-agent for verification:** Spawn a sub-agent that spot-checks 5% of extracted questions against the source PDFs while the main phase continues.

**Deliverables** (all saved to `security_plus_trainer/resources/`):
- [ ] `domain_<name>.csv` — one per domain, columns: `[objective, question, answer_choices[], correct_choice, explanation]`
- [ ] `extraction_log.txt` — what worked, what Claude hallucinated, which PDFs had gaps, manual corrections applied
- [ ] `coverage_map.md` — which SY0-701 domains/objectives are represented, which are thin
- [ ] `question_answer_log.txt` — full log for Phase 3 reference

**CLAUDE.md Update:** Note "Explanations are Claude-generated from official material; validate before shipping to users"

---

## Phase 3: App Architecture & Database Design

**Agent Name:** `AppArchitect`

**Goal:** Design the complete stack: Django project structure, React component hierarchy, PostgreSQL schema (refined from Phase 1), API contract, answer-key strategy, authentication/authorization, progress dashboard.

**Before Starting:** Enter plan mode. This is the last high-level design pass before implementation — 30 minutes of review here saves hours of thrash in Phase 4.

**Starting Prompt:**
```
Activate as AppArchitect.

You are a senior full-stack software architect specializing in educational applications.

Using the research from EduPlatformResearcher and the content structure from
SecurityPlusContentArchitect, design the complete architecture for a Security+ study web app
using Django + React + PostgreSQL.

Deliverables must include:
- Recommended project/folder structure
- Detailed database schema with all relationships (PostgreSQL)
- Strategy for handling multiple question types with flexible answer_key and
  answer_explanation fields
- Django model method signatures: get_answer_key(), get_answer_explanation(),
  show_correct_answers(), and calculate_score()
- Complete list of pages and user journey, including a dedicated PBQ Practice page
  categorized by domain (see PBQ requirements below)
- Dashboard with progress tracking based on exam objectives, divided into at least 5
  clear milestones
- High-level API plan

If the CSVs from Phase 2 are missing any columns needed for the database schema, first check
security_plus_trainer/resources/question_answer_log.txt. Only if still missing, create a
clear request list for Phase 2 and save it to security_plus_trainer/resources/requests.txt.

Save all architecture output to security_plus_trainer/resources/:
- architecture.md — full design doc (schema, API spec, component tree, dashboard plan)
- requests.txt — any gaps that need Phase 2 to re-extract

Keep SQL queries simple and the overall design clean and maintainable.
```

**PBQ Practice Page Requirements:**
PBQs appear at the START of the real CompTIA exam (3–6 questions) and are the hardest
question type. The platform must include a dedicated `/pbq` practice area with:
- Domain selector — 5 cards (one per SY0-701 domain) showing available PBQ count
- Three PBQ interaction types (from `pbq_resources.md`):
  - **Interactive** — drag-and-drop matching/ordering (IoC matching, firewall rule ordering,
    device placement in a network diagram)
  - **Simulation** — simplified tool/dashboard interface (WAP config, ACL rule builder,
    log analysis)
  - **Fill-in-the-blank** — command syntax completion (nmap flags, ACL syntax, cipher names)
- Separate progress tracking for PBQs vs. standard MC questions
- No timer in practice mode; show domain objective tag after each attempt
- **PBQ work deferred** — the original ≥ 5-PBQ-per-domain go-live requirement is on hold.
  Phase 5 has been refocused on diversifying standard question types (multi-select, true/false,
  ordering) and closing objective-level coverage gaps. Revisit the PBQ requirement when PBQs
  are reactivated.

**Deliverables** (all saved to `security_plus_trainer/resources/`):
- [ ] `architecture.md` — Django app structure, React component tree (including PBQ components), API spec, dashboard design, answer-key strategy
- [ ] `requests.txt` — any gaps that need Phase 2 to re-extract (if applicable)
- [ ] Updated CLAUDE.md with schema diagram, API base URL, auth flow, PBQ page spec

**Security+ tie-in:** Designing authentication (session vs JWT), authorization (user vs admin views), and data integrity directly touches Domain 1 and Domain 4. Building PBQ drag-and-drop scenarios for firewall ACL configuration and network topology exercises directly reinforces Domains 3 and 4.

---

## Phase 4: Core Backend Implementation

**Agent Name:** `SecureStudyDeveloper`

**Goal:** Implement Django models, migrations, user auth, question endpoints, progress tracking, and answer-key service. Wire up to PostgreSQL.

**Before Starting:** Enter plan mode. Review architecture from Phase 3 before touching code.

**Starting Prompt:**
```
Activate as SecureStudyDeveloper.

We are building the Security+ study app using Django + React + PostgreSQL based on the
architecture from AppArchitect.

Core requirements:
- Implement flexible answer_key and answer_explanation fields for all question types.
- Create helper methods: get_answer_key(), get_answer_explanation(), show_correct_answers(),
  and calculate_score().

First task: Set up the initial Django project structure, database models, and basic user
authentication.

Follow all rules strictly. Show your detailed plan before writing any code.
```

**Rules (add to CLAUDE.md):**
- Work only inside the provided project root directory.
- Show a clear plan and get explicit approval before implementing major features.
- Use inline diffs for all code changes.
- No git commit or git push without explicit user approval.
- Ask permission before running terminal commands except safe ones (runserver, makemigrations, migrate, tests).
- Pause after each milestone for review.

**Hooks suggestion:** Set a post-tool-use hook that runs `pytest` after any edit to `models.py` or `views.py`. This teaches you that Claude Code is programmable — you're not just chatting, you're orchestrating.

**Sub-agent pattern:** After migrations are written, spawn a verification sub-agent that runs them against a test DB and reports errors without blocking your main flow.

**Deliverables:**
- [ ] Django models (Question, UserProgress, Domain, PracticeExam, etc.) fully implemented
- [ ] User authentication (session-based or JWT; document choice in CLAUDE.md)
- [ ] Admin interface for question management
- [ ] API endpoints: `/api/questions/`, `/api/submit_answer/`, `/api/progress/`, `/api/domains/`
- [ ] Database migrations and local test runs
- [ ] Helper methods: `get_answer_key()`, `calculate_score()`, etc.

**Security+ tie-in:** Implementing secure password storage, session management, and preventing unauthorized access = Domain 4 (Security Operations) + Domain 1 (General Security Concepts) applied to your own app.

---

## Phase 4.5 (Milestone): Build & Wire MCP Server

**Goal:** Build a small MCP server (50–100 lines Python) that exposes your question bank and SY0-701 objectives to Claude Code. This is where you shift from "Claude-assisted" to "Claude-extended."

**Why this matters:**
1. Companies are wrapping internal tools in MCP right now. Devs who build them are in demand.
2. Once Claude Code is wired to your MCP server, future Claude sessions can query live data instead of you pasting schemas into prompts.
3. It teaches you the protocol: extend, don't just use.

**Deliverables:**
- [ ] MCP server exposing:
  - `get_objectives()` — returns SY0-701 domain/objective list
  - `search_questions(domain, keyword)` — queries your question bank by domain or keyword
- [ ] MCP server configured in CLAUDE.md (how Claude Code connects)
- [ ] Test: next Claude Code session connects to the server and uses the tools to check question coverage

**Quickstart:** `modelcontextprotocol.io` has a 15-minute Python quickstart.

---

## Phase 5: Content Diversification & Gap-Fill

**Agent Name:** `SecurityPlusExaminer`

**Status of upstream phases:** Phase 4 imported all 248 questions; Phase 4.5 audited every key and applied 73 fixes — see `resources/audit_summary.md`. Phase 5 builds on that clean baseline.

**Goal:** Two parallel content efforts:
1. **Fill the Domain 3 § 3.4 coverage gap** flagged in the Phase 4.5 audit. Currently only 3 questions (Q82, Q83, Q84). Author additional items covering HA/clustering, geographic dispersion, replication modes, backup types (full/incremental/differential/snapshot), power resilience (UPS/generator/dual power), and the full exercise spectrum (walkthrough → tabletop → simulation → parallel → full failover). Target ≥ 10 questions on § 3.4.
2. **Diversify question types** across the entire bank. The existing 248 questions are almost entirely `multiple_choice`. Bring the question mix up to **at least 20 questions per type per domain** for these four types:
   - `multiple_choice`
   - `multi_select`
   - `true_false`
   - `ordering`

**PBQ work is on hold.** The original "≥ 5 PBQ per domain before go-live" requirement is deferred. `pbq_simulation`, `drag_drop`, and `fill_blank` are out of scope for this phase.

**Volume note:** 4 types × 5 domains × 20 questions = **400 minimum**. Current bank is 248 (and overwhelmingly MC). Expect Phase 5 to roughly double the question bank and rebalance the type distribution.

**Before Starting:** Enter plan mode. Use the `security-plus-trainer` MCP tools (`list_domains`, `list_questions`) to produce the baseline distribution table — that is the gap you are closing.

**Workflow (in order):**

1. **Survey current state.** Use `mcp__security-plus-trainer__list_questions` to count existing questions by `(domain, question_type)` and by `(objective_code, question_type)`. Output `resources/question_type_gaps.md` with three sections:
   - Current distribution table (rows = domain, columns = type, cell = count).
   - Target distribution (20 per cell for the four in-scope types).
   - Gap-per-cell = `max(0, 20 - current)` plus a callout for Domain 3 § 3.4.

2. **Mine local resources first.** Re-read the CompTIA materials in `resources/` (Exam Objectives 7.0 PDF, Study Guide PDF, Study Plan PDF) plus the existing `extraction_log.txt` and `coverage_map.md` for content that fits the non-MC formats but was previously extracted as MC or skipped entirely. Examples of what to look for:
   - **Ordering candidates:** sequenced lists in the source — IR lifecycle (Preparation → Detection → Analysis → Containment → Eradication → Recovery → Lessons Learned), RMF steps, NIST CSF function order, TCP three-way handshake, kill chain, change-management process.
   - **True/false candidates:** unambiguous declarative statements in the objectives ("Symmetric encryption uses the same key for encryption and decryption", "TLS 1.0 is deprecated by RFC 8996").
   - **Multi-select candidates:** any source bullet that lists multiple defenses for a single attack, multiple indicators for one threat, or multiple controls in a family (preventive/detective/corrective for a given risk).
   
   Append findings to `resources/question_type_gaps.md` under a "Local source candidates" section. **Be specific** — quote the source line and cite the page/objective. Report the count of candidates found per (type, domain) so we know what's left for step 3.

3. **External free sources + generation.** For any gap remaining after step 2:
   - First look at the CompTIA-aligned free sites already in scope (lognpacific.com, examcompass.com, comptia.org practice tests) for non-MC items. Cite the source URL on every imported question.
   - If still short, **generate** questions using the `question-researcher` agent against the SY0-701 Exam Objectives PDF. Researcher produces drafts with full citations; the `question-db-admin` agent applies them to CSV + DB. Same pipeline as Phase 4.5.

4. **Author and import.** New questions go into the existing `domain_<n>_*.csv` files following the established format. The `question_type` column supports `multiple_choice`, `multi_select`, `true_false`, `ordering`. Run `python manage.py import_questions` to load. (`import_questions` skips on `(objective, question_text)` match, so re-imports are safe.)

5. **Audit pass v2.** Once the new content is loaded, re-run the 5-parallel-agent audit (one per domain via the MCP) the same way Phase 4.5 did — but scoped to **only the new questions added in steps 2–4**. Produce `resources/audit_summary_v2.md`. Apply any flagged fixes via the `question-db-admin` agent.

**Validation Checklist:**
- [ ] All `multiple_choice` questions: exactly one correct answer, plausible distractors.
- [ ] All `multi_select` questions: stem explicitly says "Select all that apply" or "Select TWO/THREE"; `answer_data.correct_ids` contains every correct choice.
- [ ] All `true_false` questions: stem is an unambiguous declarative; not a trick negation or compound statement.
- [ ] All `ordering` questions: every step is necessary and order-dependent; explanation cites the canonical sequence source (NIST publication, CompTIA objective text, RFC).
- [ ] **Type coverage:** every (domain × {multiple_choice, multi_select, true_false, ordering}) cell has ≥ 20 questions.
- [ ] **Objective coverage:** every `objective_code` has ≥ 3 questions; Domain 3 § 3.4 lifted from 3 → ≥ 10.
- [ ] Every new explanation cites an authoritative source (SY0-701 objectives PDF section, NIST publication, RFC, vendor doc).

**Deliverables** (all saved to `security_plus_trainer/resources/`):
- [ ] `question_type_gaps.md` — baseline distribution, target, gap-per-cell, local source candidates with citations, and final sourcing plan.
- [ ] Updated `domain_<n>_*.csv` files containing the new questions.
- [ ] `audit_summary_v2.md` — v2 audit results scoped to the new content, with any fixes applied.
- [ ] Updated CLAUDE.md with: new total question count, new per-domain counts, and per-type distribution table.

---

## Phase 6: Shipping to Production

**Goal:** Containerize the app, set up CI/CD, deploy to Railway, and debug your first production issue live with Claude.

**Why this is essential:** Greenfield building and production debugging are different skills. This is also where security becomes real: TLS certs, secret management, container hardening, logging = all SY0-701 material applied to your own infrastructure.

**Deliverables:**
- [ ] Dockerfile for backend; Dockerfile for frontend (or Docker Compose)
- [ ] `docker-compose.yml` for local full-stack testing
- [ ] GitHub Actions workflow: `pytest` on every push, build Docker images, push to registry
- [ ] Deployment to Railway (simpler first production push)
- [ ] `.env` management and secrets handling (Claude can help set up GitHub Secrets)
- [ ] Production debugging: intentionally break something, then have Claude Code walk through logs and fixes
- [ ] `README.md` update: system requirements, install (Docker), how to run locally, how to deploy
- [ ] Add ops section to CLAUDE.md: how to read logs, restart services, rollback

**Security+ tie-in:** Deploying to production touches Domain 5 (Governance, Risk, and Compliance) and Domain 4 (Security Operations): secret rotation, audit logging, compliance with data residency.

### Agreed Phase 6 Plan (decided 2026-05-31)

**Decisions locked in:**
- **Topology: single combined service.** One Railway web service runs gunicorn → Django, which serves the API/admin **and** the pre-built React bundle (via whitenoise) from the same origin. Same-origin keeps the session-cookie + CSRF auth working with zero CORS config. Plus one Railway-managed Postgres. (The two-service nginx-proxy topology was considered and dropped.)
- **Deploy trigger: GitHub Actions runs the whole pipeline.** `pytest` + frontend build run first; **if any stage fails the deploy job never runs** (`deploy` job has `needs: test`). Deploy is `railway up` via the Railway CLI using a `RAILWAY_TOKEN` GitHub secret.

```
git push main ─► GitHub Actions
                   ├─ job: test   (postgres service, migrate, pytest, npm build)
                   └─ job: deploy (needs: test ✓) ─► railway up ─► Railway web service ─► Postgres
```

**Part A — Code & config changes (Claude does these):**
1. Fix blocking dependency gap: add `gunicorn`, `whitenoise`, `dj-database-url` to `backend/requirements.txt`. (Both gunicorn and whitenoise are referenced by entrypoint/settings today but are NOT installed — the committed prod image would crash on boot.)
2. Production-harden `backend/securityplus/settings.py`: parse `DATABASE_URL` (fallback to existing `DB_*` for local dev); `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO','https')`; `SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE = not DEBUG`; auto-add `RAILWAY_PUBLIC_DOMAIN` to `ALLOWED_HOSTS` + `CSRF_TRUSTED_ORIGINS`; whitenoise compressed/manifest static storage.
3. New combined `Dockerfile` (repo root), multi-stage: Stage 1 `node:20-alpine` builds React `dist/`; Stage 2 `python:3.12-slim` installs backend reqs, copies backend + `resources/` + `dist/`, runs `collectstatic`, starts gunicorn bound to `$PORT`.
4. SPA fallback route in Django so React Router deep links return `index.html` (while `/api/`, `/admin/`, `/static/` route normally).
5. `railway.json` pinning the Dockerfile builder + start command.
6. Unauthenticated `/api/v1/healthz` endpoint for Railway/CI health checks.
7. Real smoke tests (current `tests.py` files are empty stubs): health 200, questions API rejects anonymous, login→session→submit-answer happy path.
8. `.github/workflows/ci.yml`: `test` job (Postgres service container, migrate, run tests, `npm run build`) + `deploy` job with `needs: test` that runs `railway up` only on push to `main`.
9. Update combined entrypoint to bind `$PORT`; keep migrate/seed/import idempotent on boot.
10. Docs: README ops section (run locally, deploy, read logs, rollback) + CLAUDE.md Phase 6 log + ops notes.
11. Local verification: build the combined image, run against local Postgres, confirm app serves + login + questions load BEFORE any push.

**Part B — 🧑 User steps (only the user can do these):**
1. Create a Railway account at railway.app (sign in with GitHub).
2. Create a Railway project → Add PostgreSQL plugin.
3. Create the web service / link the repo (or via CLI on first deploy).
4. Generate a Railway API token (Account → Tokens) → add to GitHub repo Secrets as `RAILWAY_TOKEN`.
5. Set service env vars in Railway: `SECRET_KEY` (generated), `DEBUG=False`, reference Postgres `DATABASE_URL`.
6. Approve the commit & push (project rule: no commit/push without explicit approval).
7. After first deploy: create admin superuser via `railway run`, then smoke-test the live URL.

**Sequencing:** (A) Claude makes all Part-A changes + verifies image locally (no account needed) → (B) user does Part-B 1–5 → (C) approve push → CI runs → deploys → (D) user does Part-B 6–7; debug first prod issue together.

**Out of scope (deferred):** Phase 5.1 question expansion (10→20) paused until deployed; two-service/nginx topology dropped.

> **Blocker before Phase 6 starts:** a batch of cross-stack bugs was found during manual testing on 2026-05-31 (screenshots + notes in `security_plus_trainer/bugs/`). These must be fixed first — see the bug-fix plan / CLAUDE.md.

---

## Phase 7: Evals & Quality Assurance (Optional but High-Value)

**Goal:** Build an eval harness that programmatically tests whether Claude can correctly answer your extracted Security+ questions. This teaches eval-driven development — a skill almost no traditional devs have yet.

**Why:**
- It surfaces hallucination drift (did Claude drop a word in an explanation?).
- It validates your extraction process end-to-end.
- It's a skill that compounds in value across your career.

**Approach:** Feed your question bank to Claude (or Haiku for cost efficiency). Measure accuracy, flag mismatches. Iterate on extraction or explanation phrasing based on results.

**Deliverables:**
- [ ] Eval harness: Python script that loads questions, feeds them to Claude, checks answers
- [ ] `security_plus_trainer/resources/eval_report.md` — accuracy %, hallucination log, refinement notes

---

## Documentation Pass (Interwoven, Finalized in Phase 6)

By end of Phase 6, you should have:

- [ ] **README.md** (1–2 pages): system requirements, install, configuration, how to run locally, how to deploy, architecture overview
- [ ] **CONTRIBUTING.md** (½ page): how to add new questions, dev workflow, testing checklist
- [ ] **Architecture overview** (½ page or diagram): Django models, React components, MCP server connection, deployment target
- [ ] **CLAUDE.md finalized** with all discoveries, conventions, known workarounds

Have Claude Code generate the first draft from your code and CLAUDE.md, then you edit.

---

## Standing Rules Across All Phases

1. **Plan Mode Before Action:** Before each phase, enter plan mode (`Shift+Tab` twice in terminal Claude). Review the plan with Claude. Spot issues early.

2. **CLAUDE.md is a Living Document:** End every phase with "what does future-Claude need to know?" Add discoveries, conventions, workarounds, directory structure notes.

3. **One Agent at a Time + Parallel Sub-Agents:** Main agent drives the build. Spawn verification/research sub-agents for independent tasks (checking migrations, spot-checking PDFs, running evals). This keeps your mental model clean while using Claude's parallelism.

4. **Hooks & Automation:** Start small — one post-tool-use hook (e.g., run tests after model edits). This teaches you that Claude Code is programmable, not just a chat interface.

5. **Iterative, Not Waterfall:** If Phase 4 reveals schema issues, loop back to Phase 3, update CLAUDE.md, then continue. Mark the loop in CLAUDE.md so future-Claude knows what happened.

6. **All Agent Outputs Go in `security_plus_trainer/resources/`:** Every report, research doc, CSV, log, architecture doc, validation report, or eval result an agent produces must be saved to `security_plus_trainer/resources/`. This is also the first place agents should look when they need context from a previous phase — treat it as the shared memory layer between agents.

---

## Success Criteria

**Core MVP:**
- [ ] Full Django app running locally with PostgreSQL
- [ ] React frontend rendering questions
- [ ] User can take a practice test and get a score
- [ ] At least 50 SY0-701 questions imported and validated

**Claude Code Skills:**
- [ ] CLAUDE.md is detailed and lived-in
- [ ] Used plan mode at least 3 times
- [ ] Spawned a sub-agent for research or verification
- [ ] Wired the MCP server and used it in a Claude session

**Security+ Learning:**
- [ ] Can articulate the 6 exam domains and have touched all 6 through building
- [ ] Written explanations for at least 30 questions and can defend them from source material

**Shipping:**
- [ ] App deployed to Railway and publicly accessible
- [ ] GitHub Actions CI/CD working (tests run on push)
- [ ] README.md complete

---

## Timeline Estimate

| Phase | Hours |
|-------|-------|
| Phase 0: Setup | 1–2 |
| Phase 1: Research | 2–3 |
| Phase 2: Extraction | 3–4 |
| Phase 3: Architecture | 3–4 |
| Phase 4: Backend | 6–8 |
| Phase 4.5: MCP Server | 1–2 |
| Phase 5: Import & Validation | 2–3 |
| Phase 6: Production | 4–6 |
| Phase 7: Evals (optional) | 3–4 |
| Documentation | 1–2 |
| **Total** | **25–38 hours** |

Achievable in 1–2 weeks at 2–3 hours/day, or 3–4 weeks with lighter daily commitment.

---

## Resources Directory (`security_plus_trainer/resources/`)

This directory serves two purposes: **source inputs** (CompTIA PDFs, existing research) and **agent outputs** (reports, CSVs, logs). All agents read from and write to this directory.

**Source inputs (read-only):**
- `CompTIA Security+ (SY0-701) Exam Objectives 2.pdf`
- `CompTIA Security+ (SY0-701) Study Guide 2.pdf`
- `CompTIA Security+ (SY0-701) Study Plan 2.pdf`
- `CompTIA Security+ SY0-701 Exam Objectives (7.0).pdf`
- `pbq_resources.md` — comprehensive guide to PBQ types and open-access practice platforms

**Agent outputs (written during phases):**
- `edu_platform_research.md` — Phase 1 schema and UX research
- `domain_<name>.csv` — Phase 2 extracted questions per domain
- `extraction_log.txt` — Phase 2 hallucination and gap log
- `coverage_map.md` — Phase 2 domain/objective coverage
- `question_answer_log.txt` — Phase 2 full extraction log
- `architecture.md` — Phase 3 full design doc
- `requests.txt` — Phase 3 gaps needing Phase 2 re-extraction
- `validation_report.md` — Phase 5 question validation results
- `eval_report.md` — Phase 7 eval harness results

---

## First Step

1. Complete Phase 0 (repo setup, CLAUDE.md v1, Claude Code test in terminal + VS Code).
2. Open this plan in a Claude Code terminal session and enter plan mode (`Shift+Tab` twice).
3. Review the plan together, ask Claude for any clarifications, then move to Phase 1.
