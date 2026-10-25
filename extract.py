"""Read the reporting period out of a question, so retrieval can favour it."""

import json
import os
import re

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Haiku is enough for this: it is a short structured extraction, not
# reasoning, and it runs on every query so cost and latency matter.
MODEL = "claude-haiku-4-5"

VALID_PERIODS = {"Q1", "Q2", "Q3", "Q4", "HY", "FY"}
VALID_YEARS = range(2020, 2031)

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """You extract the reporting period a question is asking about.

Return only a JSON object, no other text, with these keys:
- "year": a four-digit integer, or null if the question names no year
- "period": one of "Q1", "Q2", "Q3", "Q4", "HY", "FY", or null

Guidance:
- "the first quarter of 2025" is Q1, 2025
- "half year 2026", "H1 2026", "interim" is HY
- "full year", "annual", "FY25" is FY
- A question spanning periods ("between 2025 and Q1 2026") names more than
  one; return the later of them, since that document usually carries both.
- A question with no period at all gets null for both. 
- A question tracking how something changed across several reports ("how did
  guidance change through the year", "how has X evolved") needs all of them;
  return null for both so nothing is excluded.Do not guess.

Examples:
{"year": 2025, "period": "Q1"}
{"year": 2026, "period": "HY"}
{"year": null, "period": null}"""


def parse_response(text: str) -> dict:
    """Pull the JSON object out of the reply and sanity-check its values."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {"year": None, "period": None}

    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"year": None, "period": None}

    year = data.get("year")
    period = data.get("period")

    if year not in VALID_YEARS:
        year = None
    if period not in VALID_PERIODS:
        period = None

    return {"year": year, "period": period}


def extract_period(question: str) -> dict:
    """Return {"year": int|None, "period": str|None} for a question."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=100,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": question}],
    )
    return parse_response(response.content[0].text)


QUESTIONS = [
    "What was the CET1 ratio at the end of 2025?",
    "How did the 2026 net interest income guidance change through the year?",
    "What drove the increase in the impairment charge in Q1 2025?",
    "What interim dividend did Lloyds declare for H1 2026?",
    "How did the CET1 ratio move between the end of 2025 and the end of Q1 2026?",
    "What is the total motor finance provision?",
    "What were Lloyds' Q3 2026 results?",
]


if __name__ == "__main__":
    for question in QUESTIONS:
        result = extract_period(question)
        print(f"{result['year']} {result['period'] or '--':<3}  {question}")
