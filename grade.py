"""Grade one answer against its expected answer, using a model as judge."""

import json
import os
import re

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"

VALID_GRADES = {"pass", "partial", "fail"}

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

JUDGE_PROMPT = """You grade answers from a financial document question-answering system.

You are given a question, the expected answer written by a human from the source filings, and the answer the system produced. Decide how well the system's answer matches the expected one.

Grade strictly:
- "pass": every substantive figure and point in the expected answer appears in the system's answer. Extra correct detail is fine. Different wording is fine.
- "partial": the main point is right but specific figures or reasoning from the expected answer are missing, or the right conclusion was reached without the evidence that should support it.
- "fail": the answer is wrong, contradicts the expected answer, or invents figures.

For a question whose expected answer is that the documents do not contain the information, "pass" means the system refused. Giving figures for a different period is "fail", not "partial" — a confident wrong figure is the worst outcome.

Return only a JSON object, no other text:
{"grade": "pass" | "partial" | "fail", "reason": "one short sentence"}"""


def parse_response(text: str) -> dict:
    """Pull the JSON out of the reply and check the grade is one we allow."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {"grade": "fail", "reason": "judge returned no JSON"}

    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"grade": "fail", "reason": "judge returned malformed JSON"}

    grade = data.get("grade", "").lower()
    if grade not in VALID_GRADES:
        return {"grade": "fail", "reason": f"judge returned unknown grade: {grade}"}

    return {"grade": grade, "reason": data.get("reason", "")}


def grade_answer(question: str, expected: str, actual: str) -> dict:
    """Return {"grade": ..., "reason": ...} comparing actual against expected."""
    content = (
        f"Question:\n{question}\n\n"
        f"Expected answer:\n{expected}\n\n"
        f"System's answer:\n{actual}"
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=JUDGE_PROMPT,
        messages=[{"role": "user", "content": content}],
    )

    return parse_response(response.content[0].text)


def check_retrieval(expected_docs: list[str], sources: list[dict]) -> dict:
    """Did the documents the answer needs appear among the retrieved chunks?"""
    if not expected_docs:
        return {"hit": None, "found": [], "missing": []}

    retrieved = {source["source"] for source in sources}
    found = [doc for doc in expected_docs if doc in retrieved]
    missing = [doc for doc in expected_docs if doc not in retrieved]

    return {"hit": len(missing) == 0, "found": found, "missing": missing}


if __name__ == "__main__":
    result = grade_answer(
        question="What was the CET1 ratio at the end of 2025?",
        expected="14.0% at 31 December 2025.",
        actual="The CET1 ratio at 31 December 2025 was 14.0%.",
    )
    print(result)

    result = grade_answer(
        question="What was the CET1 ratio at the end of 2025?",
        expected="14.0% at 31 December 2025.",
        actual="The CET1 ratio was 13.4%.",
    )
    print(result)
