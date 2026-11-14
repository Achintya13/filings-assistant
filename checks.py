"""Plain checks that need no AI: right pages retrieved, and no made-up citations."""

import re

PDF_NAME = re.compile(r"[\w\-]+\.pdf")
PAGE_NUMBER = re.compile(r"\bp(\d+)")


def expected_locations(source_field: str) -> dict[str, set[int]]:
    """Map each PDF in a source line to the pages listed for it.

    An empty set means the line names the document but no page, so any
    page of that document counts.
    """
    locations: dict[str, set[int]] = {}
    for part in source_field.split(";"):
        match = PDF_NAME.search(part)
        if not match:
            continue
        pages = {int(number) for number in PAGE_NUMBER.findall(part)}
        locations.setdefault(match.group(0), set()).update(pages)
    return locations


def check_pages(source_field: str, sources: list[dict]) -> dict:
    """Did retrieval bring back the right document AND one of the right pages?"""
    locations = expected_locations(source_field)
    if not locations:
        return {"hit": None, "missing": []}

    retrieved: dict[str, set[int]] = {}
    for source in sources:
        retrieved.setdefault(source["source"], set()).add(source["page"])

    missing = []
    for document, pages in locations.items():
        got = retrieved.get(document)
        if got is None:
            missing.append(f"{document} (not retrieved)")
        elif pages and not (pages & got):
            wanted = ", ".join(f"p{page}" for page in sorted(pages))
            found = ", ".join(f"p{page}" for page in sorted(got))
            missing.append(f"{document} (wanted {wanted}, got {found})")

    return {"hit": not missing, "missing": missing}


def check_citations(answer_text: str, sources: list[dict]) -> list[str]:
    """Return any PDF the answer cites that was never retrieved."""
    retrieved = {source["source"] for source in sources}
    cited = set(PDF_NAME.findall(answer_text))
    return sorted(cited - retrieved)
