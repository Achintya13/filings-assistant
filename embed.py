"""Embed every chunk and save the vectors.

Free-tier friendly: small batches, a pause between them, and progress
saved after every batch so an interruption costs at most one batch.
Re-running picks up where it left off.
"""

import json
import os
import time
from pathlib import Path

import numpy as np
import voyageai
from dotenv import load_dotenv

load_dotenv()

CHUNKS = Path("data/chunks.json")
OUTPUT = Path("data/vectors.npy")
PROGRESS = Path("data/vectors_partial.json")

MODEL = "voyage-3.5"
BATCH_SIZE = 8
PAUSE_SECONDS = 25

client = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"])

chunks = json.loads(CHUNKS.read_text())
texts = [chunk["text"] for chunk in chunks]

# Resume from a previous run if one was interrupted.
if PROGRESS.exists():
    vectors = json.loads(PROGRESS.read_text())
    print(f"Resuming: {len(vectors)} chunks already embedded")
else:
    vectors = []

remaining = len(texts) - len(vectors)
batch_count = (remaining + BATCH_SIZE - 1) // BATCH_SIZE
estimate = batch_count * PAUSE_SECONDS / 60

print(
    f"{remaining} chunks to go, {batch_count} batches, roughly {estimate:.0f} minutes"
)
print("Safe to interrupt with Ctrl+C - progress is saved after each batch.\n")

while len(vectors) < len(texts):
    start = len(vectors)
    batch = texts[start : start + BATCH_SIZE]

    try:
        result = client.embed(batch, model=MODEL, input_type="document")
    except Exception as error:
        print(f"  hit a limit at {start}: {type(error).__name__}")
        print("  waiting 60s before retrying...")
        time.sleep(60)
        continue

    vectors.extend(result.embeddings)
    PROGRESS.write_text(json.dumps(vectors))
    print(f"  {len(vectors)}/{len(texts)}")

    if len(vectors) < len(texts):
        time.sleep(PAUSE_SECONDS)

array = np.array(vectors, dtype=np.float32)
np.save(OUTPUT, array)
PROGRESS.unlink()

print(f"\nSaved {array.shape[0]} vectors of dimension {array.shape[1]} -> {OUTPUT}")
