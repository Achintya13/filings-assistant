"""Mark one answer against the answer key, using a model as judge.

The judge fills in a checklist: one line per key point in the expected
answer, ticked if the system's answer states it. Plain code then turns the
ticks into a grade, so the same checklist always gives the same grade.
"""

import json
import os
import re

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Sonnet, not Haiku: marking needs careful reading of two answers.
MODEL = "claude-sonnet-4-6"

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

JUDGE_PROMPT = """You check answers from a financial document question-answering system against an answer key.

You get a question, the expected answer written by a human from the filings, and the system's answer.

Step 1. Split the expected answer into its key points: each separate figure or fact it states. Usually one to five points.
Step 2. For each key point, decide whether the system's answer states it. Different wording is fine. Figures must match.
Step 3. Decide whether the system's answer contradicts the expected answer: a different figure for the same thing, or a figure for a different period presented as the one asked about.

If the expected answer says the documents do not contain the information, there is one key point: the system says so.

Return only JSON, no other text:
{"points": [{"point": "short description", "present": true}], "contradiction": false, "reason": "one short sentence"}"""


def decide_grade(points: list[dict], contradiction: bool) -> str:
    """Turn the checklist into a grade. No judgement here, just counting."""
    if contradiction or not points:
        return "fail"
    present = sum(1 for point in points if point.get("present") is True)
    if present == len(points):
        return "pass"
    if present == 0:
        return "fail"
    return "partial"


def parse_response(text: str) -> dict:
    """Read the judge's JSON and check it has the shape we asked for."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {
            "grade": "fail",
            "score": "",
            "points": [],
            "reason": "judge returned no JSON",
        }

    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {
            "grade": "fail",
            "score": "",
            "points": [],
            "reason": "judge returned malformed JSON",
        }

    points = data.get("points")
    if not isinstance(points, list) or not all(isinstance(p, dict) for p in points):
        return {
            "grade": "fail",
            "score": "",
            "points": [],
            "reason": "judge returned no checklist",
        }

    contradiction = data.get("contradiction") is True
    present = sum(1 for point in points if point.get("present") is True)

    return {
        "grade": decide_grade(points, contradiction),
        "score": f"{present}/{len(points)}",
        "points": points,
        "reason": data.get("reason", ""),
    }


def grade_answer(question: str, expected: str, actual: str) -> dict:
    """Return the grade, the checklist score and the judge's reason."""
    content = (
        f"Question:\n{question}\n\n"
        f"Expected answer:\n{expected}\n\n"
        f"System's answer:\n{actual}"
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=600,
        system=JUDGE_PROMPT,
        messages=[{"role": "user", "content": content}],
    )

    return parse_response(response.content[0].text)
