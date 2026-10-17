"""Find the chunks most relevant to a question."""

import json
import os
from pathlib import Path

import numpy as np
import voyageai
from dotenv import load_dotenv

load_dotenv()

MODEL = "voyage-3.5"

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


def search(question: str, top_k: int = 5) -> list[dict]:
    """Return the top_k chunks most similar to the question."""
    query_vector = embed_query(question)
    scores = vectors @ query_vector

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
            }
        )

    return results


QUESTIONS = [
    "What drove the increase in the impairment charge in Q1 2025?",
    "What were Lloyds' Q3 2026 results?",
]


if __name__ == "__main__":
    for question in QUESTIONS:
        print("=" * 70)
        print(f"Q: {question}\n")

        for result in search(question):
            print(f"[{result['score']:.3f}] {result['source']} p{result['page']}")
            print(f"{result['text'][:250]}\n")
