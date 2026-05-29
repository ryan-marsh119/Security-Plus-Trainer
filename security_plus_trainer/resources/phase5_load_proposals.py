"""
Phase 5 helper: convert a researcher's new-question proposal JSON into CSV
rows and append them to the appropriate domain_<N>_*.csv.

Handles the four format variants the parallel researcher agents produced:

  A) `new_questions` wrapper; choices as [{"text":"..."}];
     answer in correct_choice_texts / correct_choice_text / ordered_choice_texts.
  B) `new_questions` wrapper; choices as ["str", ...]; same answer keys as A.
  C) `new_questions` wrapper; choices as [{"order": N, "text": "...", "is_correct": bool}];
     correctness derived from `is_correct`; ordering implied by `order`.
  D) `proposals` wrapper with change_type=add_question; proposed.choices as
     [{"order": N, "text": "..."}]; answer in correct_choice_orders (the order ints).

Usage (from repo root):

    ./venv/Scripts/python.exe security_plus_trainer/resources/phase5_load_proposals.py \\
        --proposal security_plus_trainer/resources/audit_proposals_5_d4.json

Target CSV is inferred from the first digit of objective_code; pass --csv to
override.

After append:

    cd backend && ../venv/Scripts/python.exe manage.py import_questions

CSV columns:
    objective_code,question_text,question_type,difficulty,answer_choices_json,
    correct_answer_key_json,hint,explanation,source
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

CSV_COLUMNS = [
    "objective_code",
    "question_text",
    "question_type",
    "difficulty",
    "answer_choices_json",
    "correct_answer_key_json",
    "hint",
    "explanation",
    "source",
]

DOMAIN_CSV = {
    "1": "security_plus_trainer/resources/domain_1_general_security.csv",
    "2": "security_plus_trainer/resources/domain_2_threats_vulnerabilities.csv",
    "3": "security_plus_trainer/resources/domain_3_security_architecture.csv",
    "4": "security_plus_trainer/resources/domain_4_security_operations.csv",
    "5": "security_plus_trainer/resources/domain_5_program_management.csv",
}


def normalize_question(raw: dict) -> dict:
    # Strip the audit-style `proposed` wrapper (Format D) if present.
    q = raw.get("proposed", raw)

    qtype = q["question_type"]
    choices_raw = q["choices"]

    # Normalize each choice to (text, is_correct_or_None).
    pairs: list[tuple[str, object]] = []
    for c in choices_raw:
        if isinstance(c, str):
            pairs.append((c, None))
        else:
            pairs.append((c["text"], c.get("is_correct")))

    enriched = [
        {"id": i + 1, "text": t, "order": i + 1} for i, (t, _) in enumerate(pairs)
    ]
    text_to_id = {t: i + 1 for i, (t, _) in enumerate(pairs)}
    is_correct = [f for _, f in pairs]

    # Resolve the answer key for each question type by checking which fields
    # the researcher actually supplied.
    if qtype == "ordering":
        if "ordered_choice_texts" in q:
            ids = [text_to_id[t] for t in q["ordered_choice_texts"]]
        elif "correct_choice_orders" in q:
            ids = list(q["correct_choice_orders"])
        else:
            # Format C: ordering choices were emitted in the correct sequence.
            ids = [c["id"] for c in enriched]
        answer_data = {"ordered_ids": ids}

    elif qtype in ("multi_select", "multiple_choice", "true_false"):
        if "correct_choice_texts" in q:
            ids = [text_to_id[t] for t in q["correct_choice_texts"]]
        elif "correct_choice_text" in q:
            ids = [text_to_id[q["correct_choice_text"]]]
        elif "correct_choice_orders" in q:
            ids = list(q["correct_choice_orders"])
        elif any(is_correct):
            ids = [i + 1 for i, f in enumerate(is_correct) if f]
        else:
            raise ValueError(
                f"No answer key derivable for {qtype}: {q['question_text'][:80]!r}"
            )
        answer_data = {"correct_ids": ids}

    else:
        raise ValueError(f"Unsupported question_type: {qtype}")

    # Source can be a string ("source") or a list ("sources").
    if "source" in q:
        source = q["source"]
    elif "sources" in q:
        source = "; ".join(q["sources"])
    else:
        source = ""

    return {
        "objective_code": q["objective_code"],
        "question_text": q["question_text"],
        "question_type": qtype,
        "difficulty": q["difficulty"],
        "answer_choices_json": json.dumps(enriched, ensure_ascii=False),
        "correct_answer_key_json": json.dumps(answer_data, ensure_ascii=False),
        "hint": q.get("hint", ""),
        "explanation": q.get("explanation", ""),
        "source": source,
    }


def iter_raw_questions(proposal: dict):
    if "new_questions" in proposal:
        yield from proposal["new_questions"]
    elif "proposals" in proposal:
        for item in proposal["proposals"]:
            if item.get("change_type") != "add_question":
                continue
            yield item
    else:
        raise ValueError("Proposal must have 'new_questions' or 'proposals' wrapper")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal", required=True, type=Path)
    parser.add_argument(
        "--csv",
        type=Path,
        help="Target CSV. If omitted, inferred from first digit of objective_code.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    proposal = json.loads(args.proposal.read_text(encoding="utf-8"))
    rows = [normalize_question(q) for q in iter_raw_questions(proposal)]

    # Sanity: every row should belong to the same domain.
    domains = Counter(r["objective_code"].split(".")[0] for r in rows)
    if not domains:
        print("No questions to load.")
        return 0
    if len(domains) > 1:
        sys.stderr.write(
            f"Mixed domain proposal — refusing to load. Counts: {dict(domains)}\n"
        )
        return 3

    domain = next(iter(domains))
    csv_path = args.csv or Path(DOMAIN_CSV[domain])

    if args.dry_run:
        print(f"Would append {len(rows)} rows to {csv_path}")
        type_counts = Counter(r["question_type"] for r in rows)
        obj_counts = Counter(r["objective_code"] for r in rows)
        print(f"  by_type: {dict(type_counts)}")
        print(f"  by_obj:  {dict(obj_counts)}")
        return 0

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        header = next(csv.reader(f))
    if header != CSV_COLUMNS:
        sys.stderr.write(
            f"CSV header mismatch in {csv_path}.\n  got: {header}\n  expected: {CSV_COLUMNS}\n"
        )
        return 2

    with csv_path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, quoting=csv.QUOTE_MINIMAL)
        for r in rows:
            writer.writerow(r)

    print(f"Appended {len(rows)} rows to {csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
