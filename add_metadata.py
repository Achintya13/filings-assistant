"""Add year and period metadata to chunks.json, derived from filenames.

The chunk text does not change, so vectors.npy stays valid. Order is
preserved, which is what keeps chunks and vectors lined up.
"""

import json
import re
from pathlib import Path

CHUNKS = Path("data/chunks.json")

# Maps the period token in a filename to a readable label and the
# quarters it covers. Covering quarters matter for filtering: a question
# about Q2 should be able to reach a half-year document.
PERIODS = {
    "q1": ("Q1", ["Q1"]),
    "q2": ("Q2", ["Q2"]),
    "q3": ("Q3", ["Q3"]),
    "q4": ("Q4", ["Q4"]),
    "hy": ("HY", ["Q1", "Q2"]),
    "fy": ("FY", ["Q1", "Q2", "Q3", "Q4"]),
}


def parse_filename(filename: str) -> dict:
    """Pull year and period out of a name like 2025-lbg-q1-ims.pdf."""
    year_match = re.match(r"(\d{4})", filename)
    year = int(year_match.group(1)) if year_match else None

    period = None
    covers = []
    for token, (label, quarters) in PERIODS.items():
        if f"-{token}-" in filename.lower():
            period = label
            covers = quarters
            break

    return {"year": year, "period": period, "covers": covers}


if __name__ == "__main__":
    chunks = json.loads(CHUNKS.read_text())

    seen = {}
    for chunk in chunks:
        meta = parse_filename(chunk["source"])
        chunk["year"] = meta["year"]
        chunk["period"] = meta["period"]
        chunk["covers"] = meta["covers"]

        key = (chunk["source"], meta["year"], meta["period"])
        seen[key] = seen.get(key, 0) + 1

    CHUNKS.write_text(json.dumps(chunks, indent=2))

    print(f"Tagged {len(chunks)} chunks\n")
    for (source, year, period), count in sorted(seen.items()):
        print(f"  {source:<28} {year} {period:<3} {count:>4} chunks")

    untagged = [c for c in chunks if c["period"] is None]
    if untagged:
        print(f"\nWarning: {len(untagged)} chunks have no period")