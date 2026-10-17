"""Answer a question using retrieved chunks."""

import os

from anthropic import Anthropic
from dotenv import load_dotenv

from search import search

load_dotenv()

MODEL = "claude-sonnet-4-6"

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM_PROMPT = """You answer questions about Lloyds Banking Group using only the excerpts provided.

Rules:
- Use only the excerpts. Never use outside knowledge.
- Cite the source document and page for every figure.
- Check the period carefully. If the question asks about a period the excerpts do not cover, say so plainly.
- If the excerpts do not answer the question, say "The documents provided do not contain this information."
- Be concise."""


def format_context(results):
    parts = []
    for result in results:
        label = "[" + result["source"] + " p" + str(result["page"]) + "]"
        parts.append(label + "\n" + result["text"])
    return "\n\n---\n\n".join(parts)


def answer(question, top_k=5):
    results = search(question, top_k=top_k)
    context = format_context(results)

    response = client.messages.create(
        model=MODEL,
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Excerpts:\\n\\n{context}\\n\\nQuestion: {question}",
            }
        ],
    )

    return {
        "answer": response.content[0].text,
        "sources": results,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
