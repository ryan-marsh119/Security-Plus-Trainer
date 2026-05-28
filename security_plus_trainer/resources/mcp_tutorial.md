# Building an MCP Server for the Security+ Trainer Question Bank

**Goal of this tutorial:** Build a small Python MCP server that exposes the trainer's question bank — including the canonical answer keys — to another Claude agent so it can audit whether the "correct" answers are actually correct.

**Who this is for:** You (Ryan), as part of the Phase 4.5 milestone in `plan.md`. The audience is someone who knows Python, has a working Django project at `backend/`, and wants to learn the MCP pattern by building a small, useful one.

**What you'll have at the end:**

- A `mcp_server/` directory with a working stdio MCP server.
- Three audit-focused tools an agent can call:
  - `list_domains()` — picks a starting point.
  - `list_questions(...)` — enumerate questions in a domain/objective.
  - `audit_question(question_id)` — returns the question, choices, the answer the DB says is correct, the explanation, and the hint — everything an auditor needs in one shot.
- Connection instructions for both Claude Code and Claude Desktop.
- A worked audit workflow you can paste into the auditor agent.

> **Project rule reminder:** All agent outputs (including this tutorial) live in `security_plus_trainer/resources/`. The MCP code itself goes in `mcp_server/` per the directory layout in `CLAUDE.md`.

---

## 1. What MCP actually is (the short version)

**Model Context Protocol (MCP)** is a small spec that lets an LLM-driven agent (Claude Code, Claude Desktop, etc.) discover and call functions in an external process. Think of it as a standard plug for "tools the model can use."

The pieces:

- **MCP server** — a process you write that exposes tools, resources, and/or prompts. It speaks the MCP protocol over a transport.
- **MCP client** — the agent runtime (Claude Code, Claude Desktop, the Agent SDK) that talks to your server.
- **Transport** — how they talk. Two common ones:
  - **stdio** — server is launched as a subprocess; client talks to it over stdin/stdout. Best for local tools. **We'll use this.**
  - **HTTP/SSE** — server runs as an HTTP service. Best for remote tools or sharing across machines.

For this project — a local question bank, a local Django app, an agent running on the same laptop — stdio is the right choice. No ports to open, no auth to configure, the agent launches the server when it needs it and shuts it down when it's done.

### Why MCP instead of just calling the Django API?

You *could* point an auditor agent at `/api/v1/...` and let it figure out the endpoints. MCP is better here because:

1. **Tool definitions are typed and self-describing.** The agent sees tool names, descriptions, and JSON schemas — no guessing, no hallucinated endpoints.
2. **You don't have to expose audit-only data over HTTP.** The MCP server reads the Django ORM directly in-process; nothing new gets added to your public API surface.
3. **It's exactly the skill the project plan calls out** ("Claude integration: MCP server (Phase 4.5 milestone)").

---

## 2. Architecture

```
+--------------------+      MCP / stdio       +------------------+      Django ORM        +--------------+
|  Auditor agent     | <--------------------> |  mcp_server      | <--------------------> |  PostgreSQL  |
|  (Claude Code or   |   list_questions       |  (this tutorial) |   Question.objects     |  (your DB)   |
|   Claude Desktop)  |   audit_question       |  Python process  |   .get_answer_key()    |              |
+--------------------+                        +------------------+                        +--------------+
```

Key points:

- The MCP server is a normal Python process. It imports your Django apps and calls models directly — same as a `manage.py` command would.
- The auditor agent runs in a separate conversation/process (could even be a different Claude window). It only sees the tools, not the database.
- Read-only by design. We expose *no* write tools. The auditor can read; if it finds a bad answer, it tells the user — humans decide what to fix.

---

## 3. Prereqs

Inside your existing venv (`venv/`), confirm Python ≥ 3.10 (MCP SDK requires it):

```bash
venv/Scripts/python --version
```

Install the official MCP Python SDK:

```bash
venv/Scripts/pip install "mcp[cli]"
```

The `[cli]` extra gives you the `mcp` CLI which is useful for debugging (`mcp dev path/to/server.py` opens an inspector).

You already have `django`, `psycopg2`, `python-dotenv` installed from the main project — the MCP server will reuse all of them.

---

## 4. Project layout

Create this structure at the project root:

```
mcp_server/
├── __init__.py
├── server.py          # The MCP server itself
├── django_bootstrap.py  # Sets up Django so we can import models
└── README.md          # How to run it (optional, can copy from this tutorial)
```

The split between `server.py` and `django_bootstrap.py` is deliberate — Django *must* be set up before any model import happens, and isolating that into one tiny module keeps `server.py` readable.

---

## 5. Step 1 — Bootstrap Django outside of `manage.py`

Your `manage.py` does the Django setup dance for you. An MCP server is a long-running Python process that needs to do the same dance manually.

Create `mcp_server/django_bootstrap.py`:

```python
"""
Sets up Django so the MCP server can import models from the `questions`,
`progress`, and `users` apps. Must be imported BEFORE any model import.

This is the same setup `manage.py` does behind the scenes — we just do it
explicitly because we don't have `manage.py` as our entry point.
"""

import os
import sys
from pathlib import Path

# Add backend/ to PYTHONPATH so `import questions.models` resolves.
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# Point Django at the same settings module manage.py uses.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "securityplus.settings")

import django  # noqa: E402  (must come after sys.path/env tweaks)

django.setup()
```

That's it. Once `django.setup()` returns, you can `from questions.models import Question` anywhere in the process.

> **Gotcha:** if you `import` model classes at the top of `server.py` *before* `from . import django_bootstrap`, you'll get `django.core.exceptions.AppRegistryNotReady`. Always import the bootstrap module first.

---

## 6. Step 2 — Sketch the MCP server skeleton

The official Python SDK ships a high-level helper called `FastMCP` that takes the boilerplate away. You define tools as plain Python functions decorated with `@mcp.tool()`, and the SDK turns docstrings and type hints into the tool schema the agent sees.

Create `mcp_server/server.py`:

```python
"""
MCP server exposing the Security+ trainer question bank for audit.

Tools:
    list_domains()                          -> list of 5 SY0-701 domains
    list_questions(domain_number, ...)      -> enumerate questions for audit
    audit_question(question_id)             -> full audit payload for one question

Run directly:
    python -m mcp_server.server

Or wire it into Claude Code / Claude Desktop (see resources/mcp_tutorial.md).
"""

import sys
from pathlib import Path

# Add this file's directory to sys.path so absolute imports resolve whether
# the file is loaded via `python -m mcp_server.server` (package mode) or via
# `mcp dev mcp_server/server.py` (file mode). See gotcha below.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import django_bootstrap  # noqa: F401  MUST be first — sets up Django

from mcp.server.fastmcp import FastMCP

# IMPORTANT: importing models has to happen AFTER django_bootstrap above.
from questions.models import Domain, Objective, Question  # noqa: E402

mcp = FastMCP("security-plus-trainer")


# --- Tools go here (next section) ---


if __name__ == "__main__":
    # FastMCP.run() defaults to stdio transport, which is what we want.
    mcp.run()
```

The `# noqa: F401` is there so linters don't flag the bootstrap import as "unused" — it has the side effect of configuring Django, which is the whole point.

> **Gotcha #1 — why not `from . import django_bootstrap`?** Relative imports (with the dot) only work when Python loads the file as part of a package. `python -m mcp_server.server` does load it as a package member, so `from . import django_bootstrap` *would* work in that mode. But the MCP inspector (`mcp dev mcp_server/server.py`) loads the file directly via `importlib.util.spec_from_file_location`, which doesn't establish a package context — you'd get `ImportError: attempted relative import with no known parent package`. The `sys.path` tweak plus an absolute `import django_bootstrap` works in both execution modes; the directory just gets added twice in package mode, which is harmless.

> **Gotcha #2 — Django setup ordering.** If you `import` model classes at the top of `server.py` *before* `import django_bootstrap`, you'll get `django.core.exceptions.AppRegistryNotReady`. Always import the bootstrap module first; model imports go below it.

---

## 7. Step 3 — Tool 1: `list_domains`

Easy warm-up. The auditor agent needs to know what's in the bank before it can audit anything. This tool also doubles as a "connection works" smoke test.

Add inside `server.py`:

```python
@mcp.tool()
def list_domains() -> list[dict]:
    """
    Return the five SY0-701 exam domains, each with its question count.

    The auditor agent typically calls this first to choose a domain to audit.

    Returns:
        A list of {number, name, weight_pct, question_count} dicts,
        ordered by domain number 1..5.
    """
    out = []
    for domain in Domain.objects.all().order_by("number"):
        question_count = Question.objects.filter(
            objective__domain=domain
        ).count()
        out.append({
            "number": domain.number,
            "name": domain.name,
            "weight_pct": float(domain.weight_pct),
            "question_count": question_count,
        })
    return out
```

A few things to notice:

- **Docstring quality matters.** The agent sees this docstring as the tool's description. Tell it what the tool is for and when to call it. The "auditor agent typically calls this first" hint is real signal.
- **Return primitives.** MCP tools serialise to JSON, so return `dict`, `list`, `str`, `int`, `float`, `bool`, or `None`. `Decimal` is *not* JSON-serialisable — note the `float(domain.weight_pct)` cast.
- **No `request` object, no auth.** Direct ORM access. The same Postgres connection your dev server uses.

---

## 8. Step 4 — Tool 2: `list_questions`

The auditor needs a way to enumerate questions without dumping all 248 at once. Filters + pagination:

```python
@mcp.tool()
def list_questions(
    domain_number: int | None = None,
    objective_code: str | None = None,
    question_type: str | None = None,
    limit: int = 25,
    offset: int = 0,
) -> dict:
    """
    Enumerate questions for auditing, with optional filters.

    Args:
        domain_number: Filter to a single domain (1-5). Omit for all domains.
        objective_code: Filter by objective code like '1.1' or '3.4'.
        question_type: One of 'multiple_choice', 'multi_select', 'true_false',
            'ordering', 'drag_drop', 'fill_blank', 'pbq_simulation'.
        limit: Page size, max 100. Default 25.
        offset: How many to skip (for paging). Default 0.

    Returns:
        {
            "total": <int>,           # matching questions across all pages
            "offset": <int>,
            "limit": <int>,
            "items": [
                {
                    "id": <int>,                    # use with audit_question()
                    "objective_code": "3.4",
                    "domain_number": 3,
                    "question_type": "multiple_choice",
                    "difficulty": "medium",
                    "preview": "<first 120 chars of question_text>"
                },
                ...
            ]
        }
    """
    limit = max(1, min(int(limit), 100))
    offset = max(0, int(offset))

    qs = Question.objects.select_related("objective__domain").order_by("id")

    if domain_number is not None:
        qs = qs.filter(objective__domain__number=domain_number)
    if objective_code:
        qs = qs.filter(objective__code=objective_code)
    if question_type:
        qs = qs.filter(question_type=question_type)

    total = qs.count()
    page = qs[offset:offset + limit]

    items = [
        {
            "id": q.id,
            "objective_code": q.objective.code,
            "domain_number": q.objective.domain.number,
            "question_type": q.question_type,
            "difficulty": q.difficulty,
            "preview": q.question_text[:120],
        }
        for q in page
    ]

    return {"total": total, "offset": offset, "limit": limit, "items": items}
```

Why `preview` and not full text? Token economy. The auditor will pull full text via `audit_question` only for IDs it actually wants to inspect.

---

## 9. Step 5 — Tool 3: `audit_question` (the main event)

This is the tool that earns the project its keep. One call returns everything the auditor needs to decide *"is the stored correct answer actually correct?"*

```python
@mcp.tool()
def audit_question(question_id: int) -> dict:
    """
    Return everything needed to audit a single question's answer key.

    The auditor agent should:
      1. Read `question_text` and any `choices`.
      2. Decide independently which option(s) it believes are correct.
      3. Compare its answer to `correct_answer_texts` (human-readable) or
         `answer_key` (raw machine form).
      4. If they disagree, summarise the disagreement to the user — DO NOT
         modify the database. A human reviews flagged items.

    Args:
        question_id: PK of the Question to audit. Get IDs from list_questions().

    Returns:
        {
            "id": <int>,
            "domain": {"number": 3, "name": "Security Architecture"},
            "objective": {"code": "3.4", "title": "..."},
            "question_type": "multiple_choice",
            "difficulty": "medium",
            "question_text": "...",
            "choices": [
                {"id": 17, "order": 1, "text": "Least privilege"},
                ...
            ],
            "answer_key": {"correct_ids": [17]},   # raw JSONB shape
            "correct_answer_texts": ["Least privilege"],
            "hint": "Think about which principle minimises blast radius.",
            "explanation": "Least privilege limits each account to the..."
        }
    """
    try:
        q = (
            Question.objects
            .select_related("objective__domain", "answer_key")
            .prefetch_related("answer_choices")
            .get(pk=question_id)
        )
    except Question.DoesNotExist:
        return {"error": f"No question with id={question_id}"}

    return {
        "id": q.id,
        "domain": {
            "number": q.objective.domain.number,
            "name": q.objective.domain.name,
        },
        "objective": {
            "code": q.objective.code,
            "title": q.objective.title,
        },
        "question_type": q.question_type,
        "difficulty": q.difficulty,
        "question_text": q.question_text,
        "choices": [
            {"id": c.id, "order": c.order, "text": c.text}
            for c in q.answer_choices.all()
        ],
        # These four lines are the whole reason this MCP exists:
        "answer_key": q.get_answer_key(),
        "correct_answer_texts": q.show_correct_answers(),
        "hint": q.get_hint(),
        "explanation": q.get_answer_explanation(),
    }
```

Notice we go through the helper methods `get_answer_key()`, `show_correct_answers()`, `get_hint()`, and `get_answer_explanation()` rather than reading `q.answer_key.answer_data` directly. Per the convention in `CLAUDE.md` ("All answer-key logic goes through `get_answer_key()`"), the MCP follows the same rule — if the helpers ever change shape, this tool stays correct for free.

> **PBQ / drag-drop note:** `show_correct_answers()` returns `[]` for non-choice types (ordering, drag_drop, fill_blank). The auditor should fall back to `answer_key` for those — the raw JSONB tells it everything (e.g. `{"ordered_ids": [...]}`).

---

## 10. Step 6 — Run it standalone

You can — and should — run the server outside of any agent first, just to confirm it boots and the Django bootstrap works.

From the project root, with Postgres running:

```bash
venv/Scripts/python -m mcp_server.server
```

It'll appear to hang. That's correct — stdio servers wait for a client. Hit Ctrl-C to exit.

Better: use the inspector that ships with the SDK. It gives you a UI for clicking through your tools manually:

```bash
venv/Scripts/mcp dev mcp_server/server.py
```

> **Gotcha #3 — invoke `mcp` directly, not via `python -m mcp`.** The `mcp` package doesn't ship a `__main__.py`, so `python -m mcp ...` fails with `No module named mcp.__main__; 'mcp' is a package and cannot be directly executed`. The `mcp[cli]` install drops a standalone `mcp` executable into `venv/Scripts/` — call that directly. (Or activate the venv first, then plain `mcp dev ...` works.)

The inspector opens a browser tab, shows your three tools, and lets you call each one. **Do this before plugging it into an agent.** It'll catch any Django-setup or serialisation errors in seconds.

---

## 11. Step 7 — Wire it into Claude Code

In a terminal where `claude` is installed, register the server. The CLI signature is `claude mcp add [options] <name> <commandOrUrl> [args...]` — positional command and args, with `--` as a separator so your flags don't get interpreted as `claude mcp add` options:

```bash
claude mcp add security-plus-trainer -- \
  "C:/Users/rmars/security_plus_trainer/venv/Scripts/python.exe" \
  "C:/Users/rmars/security_plus_trainer/mcp_server/server.py"
```

Verify it registered:

```bash
claude mcp list
```

Then in a Claude Code session, check it loaded:

```
/mcp
```

You should see `security-plus-trainer` listed with three tools.

> **Gotcha #4 — use the absolute path to `server.py`, not `-m mcp_server.server`.** `python -m foo` only finds `foo` if its parent directory is on Python's path, which by default is the cwd. `claude mcp add` has no `--cwd` flag, so the server is launched from whatever directory Claude Code happens to be in — `python -m mcp_server.server` would fail with `No module named mcp_server`. Pointing Python at `server.py` by absolute path sidesteps cwd entirely: Python loads the file by path, the `sys.path.insert(...)` inside `server.py` makes `import django_bootstrap` resolve, and `django_bootstrap.py` uses `Path(__file__)` to find the backend directory. Nothing depends on cwd.

> Flag names vary slightly across `claude` versions — `claude mcp add --help` is the source of truth on your install.

### Wiring into Claude Desktop instead

Edit `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) and add:

```json
{
  "mcpServers": {
    "security-plus-trainer": {
      "command": "C:/Users/rmars/security_plus_trainer/venv/Scripts/python.exe",
      "args": ["-m", "mcp_server.server"],
      "cwd": "C:/Users/rmars/security_plus_trainer"
    }
  }
}
```

Restart Claude Desktop. The tools become available to any new conversation.

---

## 12. Step 8 — The auditor agent

This is the second agent — a *different* Claude session that uses your MCP to look at questions and form an independent opinion. Open a fresh session (Claude Code is ideal) and paste a prompt like this:

```
You are an independent Security+ SY0-701 subject matter expert. You have access
to an MCP server called `security-plus-trainer` exposing three tools:
list_domains, list_questions, and audit_question.

Your job: audit the stored answer keys in the question bank. For every question
you audit:

1. Read the question_text and choices in isolation.
2. Decide which answer(s) you believe are correct based on Security+ SY0-701
   exam objectives — do NOT look at `correct_answer_texts` or `explanation`
   until after you've made your own choice.
3. Compare your answer to `correct_answer_texts`.
4. Mark each question as one of:
     AGREE       — your answer matches the stored key, explanation is sound.
     UNSURE      — your answer matches but the explanation is weak/misleading.
     DISAGREE    — you believe the stored key is wrong; explain why and cite
                   the relevant SY0-701 concept.

Audit all questions in all domains.
Produce a markdown table:
| ID | Verdict | Stored answer | Your answer | Notes |

Do not modify anything. The MCP is read-only by design.
```

That prompt forces the auditor to commit to an answer *before* peeking at the stored key — which is what makes the audit meaningful. If you let it see the answer first, it'll almost always rationalise agreement.

---

## 13. Worked example — a tiny end-to-end run

What you'd see in a working session, abbreviated:

1. **Auditor**: *calls `list_domains()`* → picks Domain 3.
2. **Auditor**: *calls `list_questions(domain_number=3, objective_code="3.4", limit=10)`* → gets 10 IDs and previews.
3. For each ID, *calls `audit_question(question_id=...)`*, reads question + choices, picks its own answer, then compares.
4. Posts a final table back to you:

   ```
   | ID  | Verdict   | Stored                 | Mine                   | Notes                                |
   |-----|-----------|------------------------|------------------------|--------------------------------------|
   | 142 | AGREE     | TLS 1.3                | TLS 1.3                | Explanation cites PFS correctly.     |
   | 147 | DISAGREE  | Symmetric encryption   | Asymmetric encryption  | Question asks about key exchange...  |
   | 151 | UNSURE    | Hash collision         | Hash collision         | Right answer, but explanation        |
   |     |           |                        |                        | conflates collision with preimage.   |
   ```

5. **You** review the DISAGREE / UNSURE rows by hand. Real bugs go into a fix list; false alarms are noted (and might inform a better auditor prompt next round).

---

## 14. Safety & conventions

- **Read-only.** This tutorial deliberately exposes zero write tools. If you later add a `flag_question(question_id, reason)` tool, route it through a *new* model (e.g. `QuestionAuditFlag`) rather than mutating `AnswerKey` directly — keeps the human in the loop.
- **No live user data.** None of these tools touch `User`, `ExamSession`, or `SessionAnswer`. The audit MCP is content-only.
- **Helper methods, always.** The MCP uses `get_answer_key()` / `show_correct_answers()` / `get_hint()` / `get_answer_explanation()` — the same convention `CLAUDE.md` enforces for the rest of the codebase.
- **Django connections.** A long-running MCP process can hold stale Postgres connections. If you start seeing `OperationalError: server closed the connection unexpectedly`, wrap each tool in `connection.close_if_unusable_or_obsolete()` from `django.db`. Not needed for short audit sessions.

---

## 15. What to extend next

Natural follow-ons once this works:

- **`compare_question_to_pdf(question_id, objective_code)`** — pulls the relevant section of `resources/CompTIA Security+ (SY0-701) Study Guide 2.pdf` and includes it in the audit payload so the auditor cites official material directly.
- **`list_questions_with_no_explanation()`** — quick triage for content gaps.
- **A second MCP server `progress_inspector`** — exposes anonymised aggregate stats (which questions are most-missed) so an agent can correlate "agents disagree with this key" against "users get this one wrong constantly." Strong signal for real errors vs. agent confusion.
- **HTTP transport for remote audits** — switch to `mcp.run(transport="streamable-http", port=3333)` if you ever want a teammate's Claude to audit your local DB over a tunnel.

---

## 16. Quick reference — full `server.py`

For copy-paste convenience, here's the complete file with all three tools:

```python
"""
MCP server exposing the Security+ trainer question bank for audit.

Run via the inspector (recommended for first-time testing):
    venv/Scripts/mcp dev mcp_server/server.py

Or run standalone (waits for an MCP client over stdio):
    venv/Scripts/python -m mcp_server.server
"""

import sys
from pathlib import Path

# Make absolute imports resolve in both `python -m` mode and `mcp dev` mode.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import django_bootstrap  # noqa: F401  MUST be first — sets up Django

from mcp.server.fastmcp import FastMCP
from questions.models import Domain, Question  # noqa: E402

mcp = FastMCP("security-plus-trainer")


@mcp.tool()
def list_domains() -> list[dict]:
    """Return the five SY0-701 exam domains, each with its question count."""
    out = []
    for domain in Domain.objects.all().order_by("number"):
        question_count = Question.objects.filter(
            objective__domain=domain
        ).count()
        out.append({
            "number": domain.number,
            "name": domain.name,
            "weight_pct": float(domain.weight_pct),
            "question_count": question_count,
        })
    return out


@mcp.tool()
def list_questions(
    domain_number: int | None = None,
    objective_code: str | None = None,
    question_type: str | None = None,
    limit: int = 25,
    offset: int = 0,
) -> dict:
    """Enumerate questions for auditing, with optional filters and paging."""
    limit = max(1, min(int(limit), 100))
    offset = max(0, int(offset))

    qs = Question.objects.select_related("objective__domain").order_by("id")
    if domain_number is not None:
        qs = qs.filter(objective__domain__number=domain_number)
    if objective_code:
        qs = qs.filter(objective__code=objective_code)
    if question_type:
        qs = qs.filter(question_type=question_type)

    total = qs.count()
    page = qs[offset:offset + limit]
    items = [
        {
            "id": q.id,
            "objective_code": q.objective.code,
            "domain_number": q.objective.domain.number,
            "question_type": q.question_type,
            "difficulty": q.difficulty,
            "preview": q.question_text[:120],
        }
        for q in page
    ]
    return {"total": total, "offset": offset, "limit": limit, "items": items}


@mcp.tool()
def audit_question(question_id: int) -> dict:
    """Return everything needed to audit one question's answer key."""
    try:
        q = (
            Question.objects
            .select_related("objective__domain", "answer_key")
            .prefetch_related("answer_choices")
            .get(pk=question_id)
        )
    except Question.DoesNotExist:
        return {"error": f"No question with id={question_id}"}

    return {
        "id": q.id,
        "domain": {
            "number": q.objective.domain.number,
            "name": q.objective.domain.name,
        },
        "objective": {
            "code": q.objective.code,
            "title": q.objective.title,
        },
        "question_type": q.question_type,
        "difficulty": q.difficulty,
        "question_text": q.question_text,
        "choices": [
            {"id": c.id, "order": c.order, "text": c.text}
            for c in q.answer_choices.all()
        ],
        "answer_key": q.get_answer_key(),
        "correct_answer_texts": q.show_correct_answers(),
        "hint": q.get_hint(),
        "explanation": q.get_answer_explanation(),
    }


if __name__ == "__main__":
    mcp.run()
```

And `django_bootstrap.py`:

```python
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "securityplus.settings")

import django  # noqa: E402
django.setup()
```

---

## 17. What you've learned (Claude Code angle)

Beyond the working MCP, this exercise reinforces a few transferable Claude Code skills:

- **Tool authoring as a documentation exercise.** The agent only ever sees your docstrings and signatures — clear naming and crisp descriptions matter more than implementation cleverness.
- **Read-only by default.** Most agentic mistakes happen on write paths. Designing a tool surface that *cannot* corrupt state is half the safety story.
- **Separating bootstrap from logic.** `django_bootstrap.py` is the kind of "small ugly module" that keeps the rest of the codebase clean. Same pattern reappears in any project where you import a framework's ORM outside its CLI.
- **One MCP per concern.** This server is "question bank, read-only." If you later need write access for a flagging workflow, that's a *different* MCP — different name, different permissions story, easier to reason about.

When you're ready, log this as Phase 4.5 in `CLAUDE.md` (per the convention in your phase log) and capture any surprises in the "Known Issues & Workarounds" section.
