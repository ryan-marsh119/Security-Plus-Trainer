"""
Find Phase 5 batch researcher JSON outputs in the current Claude Code session
transcript and save each domain's payload as a clean JSON file.

Usage:
    python phase5_extract_session.py <session.jsonl>
"""

import json
import re
import sys
from pathlib import Path

DOMAINS = {
    "d2": [r'"objective_code": "2\.', r"Domain 2", r"Q-MS-01"],
    "d3": [r'"objective_code": "3\.', r"Domain 3"],
}

OUTPUT_DIR = Path("security_plus_trainer/resources")


def iter_text_chunks(jsonl_path: Path):
    """Yield every textual piece of content we can find in the transcript."""
    with jsonl_path.open(encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            # The transcript is heterogeneous. Walk it generically.
            yield from walk(rec)


def walk(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)
    elif isinstance(obj, str):
        yield obj


JSON_BLOCK_RE = re.compile(r"```json\s*\n(.*?)```", re.DOTALL)


def main() -> int:
    jsonl_path = Path(sys.argv[1])

    # Collect every ```json block we see, with the surrounding context that
    # decides which domain it belongs to.
    blocks_by_domain: dict[str, list[str]] = {k: [] for k in DOMAINS}

    for chunk in iter_text_chunks(jsonl_path):
        for m in JSON_BLOCK_RE.finditer(chunk):
            body = m.group(1)
            # We're only interested in payloads that wrap a new_questions
            # array (or audit-proposal style). Skip tiny example blocks.
            if '"new_questions"' not in body and '"proposals"' not in body:
                continue
            # Classify by which objective codes appear in the body.
            for dn, patterns in DOMAINS.items():
                # Look for matches in both the block and surrounding text.
                if any(re.search(p, body) for p in patterns):
                    blocks_by_domain[dn].append(body)
                    break

    for dn, blocks in blocks_by_domain.items():
        if not blocks:
            print(f"  {dn}: no block found")
            continue
        # Take the LARGEST block — that's the full proposal, not a partial one.
        body = max(blocks, key=len)
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as e:
            print(f"  {dn}: JSON decode error {e}")
            continue
        outpath = OUTPUT_DIR / f"audit_proposals_5_{dn}.json"
        outpath.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        count = (
            len(payload.get("new_questions", []))
            or len(payload.get("proposals", []))
        )
        print(f"  {dn}: extracted {count} questions to {outpath}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
