"""Look at what pypdf actually extracts from a filing."""

from pathlib import Path

from pypdf import PdfReader

path = Path("data/documents/2025-lbg-q1-ims.pdf")
reader = PdfReader(path)

print(f"File: {path.name}")
print(f"Pages: {len(reader.pages)}")
print("-" * 60)

for page_number in [0, 1, 2]:
    text = reader.pages[page_number].extract_text()
    print(f"\n=== PAGE {page_number + 1} ===")
    print(text[:800])
