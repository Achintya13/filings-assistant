"""Re-mark the saved answers from the last run, without asking the system again.

Only the judge runs, so there is no Voyage call and no waiting. Each answer
is marked several times; a question whose marks differ shows the judge is
unsteady on it.

    uv run python regrade.py        # mark each answer twice
    uv run python regrade.py 3      # mark each answer three times
"""

import json
import sys
from pathlib import Path

from eval_set import load_cases
from grade import grade_answer

RESULTS_JSON = Path("data/eval_results.json")


if __name__ == "__main__":
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    saved = json.loads(RESULTS_JSON.read_text())["rows"]
    cases = {case["id"]: case for case in load_cases()}

    print(f"Re-marking {len(saved)} saved answers, {rounds} times each\n")
    unsteady = 0

    for row in saved:
        case = cases[row["id"]]
        marks = []
        for _ in range(rounds):
            result = grade_answer(case["question"], case["expected"], row["answer"])
            marks.append(f"{result['grade']} {result.get('score', '')}".strip())

        steady = len(set(marks)) == 1
        if not steady:
            unsteady += 1
        flag = "" if steady else "  <-- marks differ"
        print(f"  {row['id']:<4} {' | '.join(marks)}{flag}")

    print(f"\n{unsteady} of {len(saved)} questions got different marks")
