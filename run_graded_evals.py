"""Run every evaluation question and score it automatically.

Three checks per question:
- pages: did retrieval bring back the right document and page (no AI)
- citations: does the answer cite only documents that were retrieved (no AI)
- grade: does the answer match the expected one (Claude as judge)
"""

import json
import sys
import time
from datetime import date
from pathlib import Path

from answer import answer
from checks import check_citations, check_pages
from eval_set import load_cases
from grade import grade_answer

RESULTS_MD = Path("data/eval_results.md")
RESULTS_JSON = Path("data/eval_results.json")

# Voyage's free tier allows 3 requests a minute; each question uses one.
PAUSE_SECONDS = 21


def run_case(case: dict) -> dict:
    """Answer one question, then run all three checks on it."""
    result = answer(case["question"])

    pages = check_pages(case["source"], result["sources"])
    invented = check_citations(result["answer"], result["sources"])
    grade = grade_answer(case["question"], case["expected"], result["answer"])

    return {
        "id": case["id"],
        "type": case["type"],
        "question": case["question"],
        "answer": result["answer"],
        "filters": result["filters"],
        "sources": [f"{s['source']} p{s['page']}" for s in result["sources"]],
        "retrieval_hit": pages["hit"],
        "missing": pages["missing"],
        "invented_citations": invented,
        "grade": grade["grade"],
        "reason": grade["reason"],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
    }


def diagnose(row: dict) -> str:
    """Name the part of the pipeline responsible for a non-pass."""
    if row["grade"] == "pass":
        return "-"
    if row["retrieval_hit"] is False:
        return "retrieval"
    return "generation"


def count_grades(rows: list[dict]) -> dict:
    counts = {"pass": 0, "partial": 0, "fail": 0}
    for row in rows:
        counts[row["grade"]] += 1
    return counts


def load_previous() -> dict:
    """Grades from the last run, keyed by question id, for comparison."""
    if not RESULTS_JSON.exists():
        return {}
    previous = json.loads(RESULTS_JSON.read_text())
    return {row["id"]: row["grade"] for row in previous.get("rows", [])}


def write_report(rows: list[dict], previous: dict) -> None:
    counts = count_grades(rows)
    total_in = sum(row["input_tokens"] for row in rows)
    total_out = sum(row["output_tokens"] for row in rows)

    lines = [
        "# Evaluation results",
        "",
        f"Run {date.today().isoformat()} - "
        f"{counts['pass']} pass, {counts['partial']} partial, {counts['fail']} fail "
        f"of {len(rows)}",
        "",
        "| ID | Type | Grade | Pages | Citations | Cause | Note |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for row in rows:
        hit = {True: "found", False: "missed", None: "n/a"}[row["retrieval_hit"]]
        citations = "INVENTED" if row["invented_citations"] else "ok"
        change = ""
        if row["id"] in previous and previous[row["id"]] != row["grade"]:
            change = f" (was {previous[row['id']]})"
        lines.append(
            f"| {row['id']} | {row['type']} | {row['grade']}{change} | {hit} "
            f"| {citations} | {diagnose(row)} | {row['reason']} |"
        )

    lines += ["", f"Tokens: {total_in} in, {total_out} out", "", "## Answers", ""]

    for row in rows:
        lines += [
            f"### {row['id']} - {row['grade']}",
            "",
            f"**Question:** {row['question']}",
            "",
            f"**Filters:** {row['filters']}",
            "",
            f"**Answer:**\n\n{row['answer']}",
            "",
            "**Retrieved:**",
            "",
        ]
        lines += [f"- {source}" for source in row["sources"]]
        if row["missing"]:
            lines += ["", "**Missing:**", ""]
            lines += [f"- {item}" for item in row["missing"]]
        if row["invented_citations"]:
            lines += ["", "**Invented citations:**", ""]
            lines += [f"- {name}" for name in row["invented_citations"]]
        lines.append("")

    RESULTS_MD.write_text("\n".join(lines))
    RESULTS_JSON.write_text(
        json.dumps({"date": date.today().isoformat(), "rows": rows}, indent=2)
    )


if __name__ == "__main__":
    cases = load_cases()
    previous = load_previous()

    print(f"Running {len(cases)} cases\n")
    rows = []

    for index, case in enumerate(cases):
        print(f"  {case['id']}...", end="", flush=True)
        row = run_case(case)
        rows.append(row)
        flag = "  <-- invented citation" if row["invented_citations"] else ""
        print(f" {row['grade']}{flag}")

        if index < len(cases) - 1:
            time.sleep(PAUSE_SECONDS)

    write_report(rows, previous)

    counts = count_grades(rows)
    retrieval_failures = sum(1 for row in rows if diagnose(row) == "retrieval")
    generation_failures = sum(1 for row in rows if diagnose(row) == "generation")
    invented = sum(1 for row in rows if row["invented_citations"])

    print(
        f"\n{counts['pass']} pass, {counts['partial']} partial, "
        f"{counts['fail']} fail of {len(rows)}"
    )
    print(f"Caused by retrieval: {retrieval_failures}")
    print(f"Caused by generation: {generation_failures}")
    print(f"Answers with invented citations: {invented}")
    print(f"\nWrote {RESULTS_MD}")

    sys.exit(1 if counts["fail"] or invented else 0)
ß
