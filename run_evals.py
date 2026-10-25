"""Run every evaluation question through the pipeline and save the output.

Grading is manual for now: read answers.md against data/eval_questions.md
and mark each one pass, partial or fail.
"""

import time


from pathlib import Path

from answer import answer

OUTPUT = Path("data/answers.md")

QUESTIONS = [
    ("Q1", "What was the CET1 ratio at the end of 2025?"),
    ("Q2", "How did underlying net interest income change year on year in 2025?"),
    ("Q3", "What is the total motor finance provision?"),
    ("Q4", "What drove the increase in the impairment charge in Q1 2025?"),
    (
        "Q5",
        "What interim dividend did Lloyds declare for H1 2026, and what other "
        "capital return came with it?",
    ),
    ("Q6", "In which quarter of 2025 was return on tangible equity lowest, and why?"),
    (
        "Q7",
        "How did the CET1 ratio move between the end of 2025 and the end of Q1 2026?",
    ),
    ("Q8", "How did the 2026 net interest income guidance change through the year?"),
    ("Q9", "What were Lloyds' Q3 2026 results?"),
    ("Q10", "which quater was the most profitable?"),
]


if __name__ == "__main__":
    lines = ["# Evaluation run\n"]
    total_in = 0
    total_out = 0

    for label, question in QUESTIONS:
        print(f"Running {label}...")
        result = answer(question)

        total_in += result["input_tokens"]
        total_out += result["output_tokens"]

        lines.append(f"\n## {label}\n")
        lines.append(f"**Question:** {question}\n")
        lines.append(f"**Answer:**\n\n{result['answer']}\n")
        lines.append("**Chunks retrieved:**\n")
        for source in result["sources"]:
            lines.append(
                f"- [{source['score']:.3f}] {source['source']} p{source['page']}"
            )
        lines.append(
            f"\n**Tokens:** {result['input_tokens']} in, "
            f"{result['output_tokens']} out\n"
        )
        lines.append("**Grade:** _(pass / partial / fail)_\n")
        time.sleep(21)

    lines.append(f"\n---\n\n**Total tokens:** {total_in} in, {total_out} out\n")

    OUTPUT.write_text("\n".join(lines))
    print(f"\nWrote {OUTPUT}")
    print(f"Total: {total_in} in, {total_out} out")
