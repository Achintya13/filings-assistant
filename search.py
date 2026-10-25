"""Find the chunks most relevant to a question, favouring a given period."""

import json
import os
from pathlib import Path

import numpy as np
import voyageai
from dotenv import load_dotenv

load_dotenv()

MODEL = "voyage-3.5"

# Added to a chunk's score when its document is exactly the period asked
# about; half of it when the document merely covers that period. Scores
# sit around 0.55, so 0.10 is a decisive nudge without being absolute.
EXACT_BOOST = 0.10
COVERS_BOOST = 0.05
EXCLUDED = -1.0

client = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"])

chunks = json.loads(Path("data/chunks.json").read_text())
vectors = np.load("data/vectors.npy")

# Normalise once at load time, so similarity becomes a plain dot product.
vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def embed_query(question: str) -> np.ndarray:
    """Turn a question into a unit-length vector."""
    response = client.embed([question], model=MODEL, input_type="query")
    vector = np.array(response.embeddings[0], dtype=np.float32)
    return vector / np.linalg.norm(vector)


def adjust_scores(
    scores: np.ndarray, year: int | None, period: str | None
) -> np.ndarray:
    """Exclude the wrong year outright; nudge the right period upward.

    The year is a hard filter because a 2026 document cannot answer a
    question about 2025. The period is only a boost: a question about Q2
    has no Q2 document to find, so the half-year report must stay
    reachable, just ranked below an exact match when one exists.
    """
    adjusted = scores.copy()

    for i, chunk in enumerate(chunks):
        if year is not None and chunk.get("year") != year:
            adjusted[i] = EXCLUDED
            continue

        if period is None:
            continue

        if chunk.get("period") == period:
            adjusted[i] += EXACT_BOOST
        elif period in chunk.get("covers", []):
            adjusted[i] += COVERS_BOOST

    return adjusted


def search(
    question: str,
    top_k: int = 5,
    year: int | None = None,
    period: str | None = None,
) -> list[dict]:
    """Return the top_k chunks most similar to the question."""
    query_vector = embed_query(question)
    raw = vectors @ query_vector
    scores = adjust_scores(raw, year, period)

    if np.max(scores) == EXCLUDED:
        raise ValueError(f"No chunks match year={year}")

    best = np.argsort(scores)[::-1][:top_k]

    results = []
    for index in best:
        chunk = chunks[index]
        results.append(
            {
                "source": chunk["source"],
                "page": chunk["page"],
                "text": chunk["text"],
                "score": float(scores[index]),
                "raw_score": float(raw[index]),
            }
        )

    return results


if __name__ == "__main__":
    question = "What drove the increase in the impairment charge in Q1 2025?"

    for label, filters in [
        ("no filter", {}),
        ("year=2025, period=Q1", {"year": 2025, "period": "Q1"}),
    ]:
        print("=" * 70)
        print(f"{label}\n")

        for result in search(question, **filters):
            boost = result["score"] - result["raw_score"]
            mark = f" (+{boost:.2f})" if boost > 0 else ""
            print(f"[{result['score']:.3f}{mark}] {result['source']} p{result['page']}")
            print(f"{result['text'][:180]}\n")
