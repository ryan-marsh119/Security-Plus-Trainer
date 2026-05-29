"""
Read a Claude tool-result persisted file (which wraps agent output as
[{"type": "text", "text": "..."}]) and extract the first ```json ... ```
code block as a clean JSON file.

Usage:
    python phase5_extract_persisted.py <persisted.json> <output.json>
"""

import json
import re
import sys
from pathlib import Path


def main() -> int:
    persisted_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    data = json.loads(persisted_path.read_text(encoding="utf-8"))
    text_chunks = [item["text"] for item in data if item.get("type") == "text"]
    combined = "\n".join(text_chunks)

    m = re.search(r"```json\s*\n(.*?)```", combined, re.DOTALL)
    if not m:
        sys.stderr.write("No ```json block found in persisted text.\n")
        return 2

    payload = json.loads(m.group(1))
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    # Try to count questions in any of the known wrappers.
    if "new_questions" in payload:
        count = len(payload["new_questions"])
    elif "proposals" in payload:
        count = len(payload["proposals"])
    else:
        count = "?"
    print(f"Extracted {count} questions to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
