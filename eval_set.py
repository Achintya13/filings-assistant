"""Read the evaluation questions from markdown into structured cases."""

import re
from pathlib import Path

QUESTIONS_FILE = Path("data/eval_questions.md")

FIELD_PATTERN = re.compile(r"\*\*(\w+):\*\*\s*(.+?)(?=\n\*\*|\Z)", re.DOTALL)


def load_cases(path: Path = QUESTIONS_FILE) -> list[dict]:
    """Return one dict per question, with its id, text, expected answer and type."""
    text = path.read_text()
    blocks = re.split(r"\n##\s+", text)
    cases = []

    for block in blocks[1:]:
        lines = block.split("\n", 1)
        case_id = lines[0].strip()
        body = lines[1] if len(lines) > 1 else ""

        fields = {
            key.lower(): value.strip() for key, value in FIELD_PATTERN.findall(body)
        }

        if "question" not in fields:
            continue

        cases.append(
            {
                "id": case_id,
                "question": fields.get("question", ""),
                "expected": fields.get("expected", ""),
                "source": fields.get("source", ""),
                "type": fields.get("type", "unspecified"),
            }
        )

    return cases


def expected_documents(source_field: str) -> list[str]:
    """Pull PDF filenames out of a source line, for the retrieval check."""
    return re.findall(r"[\w\-]+\.pdf", source_field)


if __name__ == "__main__":
    cases = load_cases()
    print(f"Parsed {len(cases)} cases from {QUESTIONS_FILE}\n")

    for case in cases:
        docs = expected_documents(case["source"]) or ["(none)"]
        print(f"{case['id']:<4} {case['type']}")
        print(f"     Q: {case['question'][:70]}")
        print(f"     Expects: {', '.join(docs)}")
        if not case["expected"]:
            print("     WARNING: no expected answer recorded")
        print()
