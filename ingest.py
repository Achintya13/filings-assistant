"""Read PDFs, split into chunks, save as JSON."""

import json
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

DOCS_DIR = Path("data/documents")
OUTPUT = Path("data/chunks.json")
MIN_CHUNK_CHARS = 100

splitter = RecursiveCharacterTextSplitter(
    chunk_size=900,
    chunk_overlap=150,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def chunk_document(path: Path) -> list[dict]:
    """Return one dict per chunk, carrying its source and page."""
    reader = PdfReader(path)
    chunks = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if not text:
            continue

        for piece in splitter.split_text(text):
            if len(piece) < MIN_CHUNK_CHARS:
                continue
            chunks.append(
                {
                    "source": path.name,
                    "page": page_number,
                    "text": piece,
                }
            )

    return chunks


if __name__ == "__main__":
    all_chunks = []

    for path in sorted(DOCS_DIR.glob("*.pdf")):
        chunks = chunk_document(path)
        all_chunks.extend(chunks)
        print(f"{path.name}: {len(chunks)} chunks")

    OUTPUT.write_text(json.dumps(all_chunks, indent=2))
    print(f"\nTotal: {len(all_chunks)} chunks -> {OUTPUT}")
