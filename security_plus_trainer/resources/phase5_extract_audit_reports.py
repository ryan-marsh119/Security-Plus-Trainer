"""
Find the five per-domain Phase 5 v2 audit reports in the session jsonl and
save each as a clean markdown file.

Usage:
    python phase5_extract_audit_reports.py <session.jsonl>
"""

import json
import re
import sys
from pathlib import Path

DOMAIN_RE = re.compile(
    r"(# Phase 5 v2 Audit\s*[—-]\s*Domain (\d).*?)(?=\n# |\Z)",
    re.DOTALL,
)


def walk(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)
    elif isinstance(o, str):
        yield o


def main() -> int:
    jsonl = Path(sys.argv[1])
    best_per_domain: dict[str, tuple[int, str]] = {}

    with jsonl.open(encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            for chunk in walk(rec):
                for m in DOMAIN_RE.finditer(chunk):
                    body, dn = m.group(1), m.group(2)
                    cur = best_per_domain.get(dn)
                    if cur is None or len(body) > cur[0]:
                        best_per_domain[dn] = (len(body), body)

    for dn, (_, body) in sorted(best_per_domain.items()):
        outpath = Path(f"security_plus_trainer/resources/audit_summary_v2_d{dn}.md")
        outpath.write_text(body.rstrip() + "\n", encoding="utf-8")
        print(f"d{dn}: wrote {len(body):,} bytes to {outpath}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
