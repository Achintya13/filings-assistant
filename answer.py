"""Answer a question using retrieved chunks, scoped to the period it names."""

import os

from anthropic import Anthropic
from dotenv import load_dotenv

from extract import extract_period
from search import search

load_dotenv()

MODEL = "claude-sonnet-4-6"

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """You answer questions about Lloyds Banking Group using only the excerpts provided.

Rules:
- Use only the excerpts. Never use outside knowledge.
- Cite the source document and page for every figure, like [2025-lbg-fy-results.pdf p5].
- Check the period carefully. If the question asks about a period the excerpts do not cover, say so plainly rather than giving figures for a different period.
- If the excerpts do not answer the question, say "The documents provided do not contain this information."
- Be concise."""


def format_context(results: list[dict]) -> str:
    """Lay the retrieved chunks out for the model, each with its citation."""
    parts = []
    for result in results:
        label = "[" + result["source"] + " p" + str(result["page"]) + "]"
        parts.append(label + "\n" + result["text"])
    return "\n\n---\n\n".join(parts)


def answer(question: str, top_k: int = 5) -> dict:
    """Extract the period, retrieve within it, then generate a grounded answer."""
    filters = extract_period(question)
    results = search(question, top_k=top_k, **filters)
    context = format_context(results)

    response = client.messages.create(
        model=MODEL,
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Excerpts:\n\n{context}\n\nQuestion: {question}",
            }
        ],
    )

    return {
        "answer": response.content[0].text,
        "sources": results,
        "filters": filters,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }


if __name__ == "__main__":
    question = "What drove the increase in the impairment charge in Q1 2025?"
    result = answer(question)

    print(f"Q: {question}")
    print(f"Filters: {result['filters']}\n")
    print(result["answer"])
    print(f"\n[{result['input_tokens']} in, {result['output_tokens']} out]")
