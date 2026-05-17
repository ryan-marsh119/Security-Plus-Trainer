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

**Goal:** Extract SY0-701 objectives, official CompTIA questions (or PBQs), YouTube resources, and practice tests from the PDFs in `/resources/`. Map to the 6 exam domains. Flag hallucinations and coverage gaps.

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
- Complete list of pages and user journey
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

**Deliverables** (all saved to `security_plus_trainer/resources/`):
- [ ] `architecture.md` — Django app structure, React component tree, API spec, dashboard design, answer-key strategy
- [ ] `requests.txt` — any gaps that need Phase 2 to re-extract (if applicable)
- [ ] Updated CLAUDE.md with schema diagram, API base URL, auth flow

**Security+ tie-in:** Designing authentication (session vs JWT), authorization (user vs admin views), and data integrity directly touches Domain 1 and Domain 4.

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

## Phase 5: Content Import & Validation

**Agent Name:** `SecurityPlusExaminer`

**Goal:** Import extracted questions from Phase 2 CSVs into the Django app. Validate all questions against exam standards and objectives. Flag issues; add corrected versions. Identify coverage gaps.

**Starting Prompt:**
```
Activate as SecurityPlusExaminer.

You are a senior cybersecurity professional and former CompTIA exam item writer. You are
extremely strict about accuracy and alignment with SY0-701 standards.

Review all questions in the database using the built-in get_answer_key(), show_correct_answers(),
and get_answer_explanation() methods.

For each question:
- Validate both the answer_key and the answer_explanation against industry standards, official
  objectives, best practices, and provided resources.
- Flag any issues with answers or explanations.
- Provide corrected versions with improved answer_key and detailed answer_explanation.

Also identify coverage gaps and add new high-quality questions (especially PBQs) with complete
answer_key and answer_explanation fields where needed.
```

**Validation Checklist:**
- [ ] All multiple-choice questions have exactly one correct answer and plausible distractors
- [ ] Multi-select questions are clearly marked; answers validated
- [ ] PBQ descriptions are actionable (not just generic scenarios)
- [ ] Explanations are accurate and reference domain objectives
- [ ] Coverage: no single objective has fewer than 3 questions

**Deliverables:**
- [ ] All Phase 2 questions imported into Django
- [ ] `security_plus_trainer/resources/validation_report.md` — questions flagged, corrections applied, updated coverage map
- [ ] Updated CLAUDE.md with question count and coverage stats

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
