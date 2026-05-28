"""
MCP server exposing the Security+ trainer question bank for audit.

Tools:
    list_domains()                          -> list of 5 SY0-701 domains
    list_questions(domain_number, ...)      -> enumerate questions for audit
    audit_questions(question_id)            -> full audit payload for one quesion

Run directly:
    python -m mcp_server.server

Or wire it into Claude Code / Claude Desktop (see resources/mcp_tutorial.md)
"""

import sys
from pathlib import Path

# Make absolute imports resolve whether the file is loaded vai
# `python -m mcp_server.server` OR via `mcp dev mcp_server/server.py`

sys.path.insert(0, str(Path(__file__).resolve().parent))

import django_bootstrap # noqa: F401 MUST be first - sets up Django
from asgiref.sync import sync_to_async
from mcp.server.fastmcp import FastMCP

# IMPORTANT: importing modules has to happen AFTER django_bootstrap above!
from questions.models import Domain, Objective, Question # noqa: E402

mcp = FastMCP("security-plus-trainer")

# Tools here!
#
# FastMCP runs tool handlers inside an asyncio event loop. Django's ORM is
# synchronous and refuses to be called from an async context, so each tool is
# defined as `async def` and delegates to a private `_*_sync` helper via
# `sync_to_async`. `thread_sensitive=True` keeps all ORM calls on the same
# worker thread so Django's per-thread DB connection is reused safely.

def _list_domains_sync() -> list[dict]:
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
async def list_domains() -> list[dict]:
    """
    Return the five SY0-701 exam domains, each with its question count.
    The auditor agent typically calls this first to choose a domain to
    audit.

    Returns:
        A list of {number, name, weight_pct, question_count} dicts,
        ordered by domain number 1..5.
    """
    return await sync_to_async(_list_domains_sync, thread_sensitive=True)()


def _list_questions_sync(
    domain_number: int | None,
    objective_code: str | None,
    question_type: str | None,
    limit: int,
    offset: int,
) -> dict:
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
async def list_questions(
    domain_number: int | None = None,
    objective_code: str | None = None,
    question_type: str | None = None,
    limit: int = 25,
    offset: int = 0,
) -> dict:
    """
    Enumerate questions for auditing, with optional filters.

    Args:
        domain_number: Filter to a single domain (1-5). Omit for all domains
        objective_code: Filter by objective code like '1.1' or '3.4'.
        question_type: One of 'multiple_choice', 'multi_select', 'true_false',
        'ordering', 'drag_drop', 'fill_blank', 'pbq_simulation'.
        limit: Page size, max 100, Default 25.
        offset: How many to skip (for paging). Default 0.

    Returns:
        {
            "total": <int>,
            "offset": <int>,
            "limit": <int>,
            "items": [
                {
                    "id": <int>,    # use with audit_question()
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
    return await sync_to_async(_list_questions_sync, thread_sensitive=True)(
        domain_number, objective_code, question_type, limit, offset
    )


def _audit_question_sync(question_id: int) -> dict:
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


@mcp.tool()
async def audit_question(question_id: int) -> dict:
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
    return await sync_to_async(_audit_question_sync, thread_sensitive=True)(
        question_id
    )

if __name__ == "__main__":
    # FastMCP.run() defaults to stdio transport, which is what we want.
    mcp.run()