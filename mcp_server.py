"""The library desk: an MCP server that offers three tools over the filings.

Any AI app that speaks MCP can connect to this and use the tools. It runs
over stdio, meaning the app starts it as a background program on this
computer and talks to it through its input and output.

Never use print() in this file: stdout carries the MCP messages, and a
stray print would corrupt them. Use the logger, which writes to stderr.
"""

import ast
import logging
import operator

from mcp.server.fastmcp import FastMCP

from search import chunks, search

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("filings-server")

mcp = FastMCP("lloyds-filings")

VALID_PERIODS = {"Q1", "Q2", "Q3", "Q4", "HY", "FY"}
MAX_TOP_K = 10


@mcp.tool()
def list_documents() -> list[dict]:
    """List the Lloyds Banking Group reports available to search.

    Returns one entry per report: its file name, year, reporting period
    (Q1, Q3, HY = half year, FY = full year), the quarters it covers,
    and its last page number. Use this first when a question spans
    several periods, or to check whether a period exists before
    searching for it.
    """
    documents: dict[str, dict] = {}
    for chunk in chunks:
        entry = documents.setdefault(
            chunk["source"],
            {
                "source": chunk["source"],
                "year": chunk.get("year"),
                "period": chunk.get("period"),
                "covers": chunk.get("covers", []),
                "last_page": 0,
            },
        )
        entry["last_page"] = max(entry["last_page"], chunk["page"])

    return sorted(documents.values(), key=lambda d: (d["year"] or 0, d["source"]))


@mcp.tool()
def search_filings(
    query: str,
    year: int | None = None,
    period: str | None = None,
    top_k: int = 5,
) -> list[dict]:
    """Search the Lloyds Banking Group reports for passages relevant to a query.

    Returns the most relevant excerpts, each with its file name and page so
    it can be cited. Call this several times with different queries when a
    question needs facts from more than one period.

    Args:
        query: what to look for, in plain words, e.g. "Q1 2026 underlying profit".
        year: optional. Only search reports from this year.
        period: optional. One of Q1, Q2, Q3, Q4, HY, FY. Favours reports for
            that period without excluding the others.
        top_k: how many excerpts to return, 1 to 10. Default 5.
    """
    if not query.strip():
        raise ValueError("query must not be empty")
    if period is not None and period not in VALID_PERIODS:
        raise ValueError(f"period must be one of {sorted(VALID_PERIODS)}")
    top_k = max(1, min(top_k, MAX_TOP_K))

    log.info("search_filings query=%r year=%s period=%s", query, year, period)
    results = search(query, top_k=top_k, year=year, period=period)

    return [
        {
            "source": r["source"],
            "page": r["page"],
            "text": r["text"],
            "score": round(r["score"], 3),
        }
        for r in results
    ]


# The calculator only understands numbers, brackets and + - * /.
# It never runs text as Python code, so a model cannot slip in commands.
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _evaluate(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
        return OPERATORS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
        return OPERATORS[type(node.op)](_evaluate(node.operand))
    raise ValueError("only numbers, brackets and + - * / are allowed")


@mcp.tool()
def calculate(expression: str) -> float:
    """Work out an arithmetic expression exactly.

    Use this for every sum, difference, percentage or comparison instead of
    working it out yourself. Supports numbers, brackets and + - * /.
    Example: "(2005 - 1532) / 1532 * 100".
    """
    if len(expression) > 200:
        raise ValueError("expression is too long")
    cleaned = expression.replace(",", "").replace("£", "")
    try:
        tree = ast.parse(cleaned, mode="eval")
    except SyntaxError as error:
        raise ValueError("not a valid arithmetic expression") from error
    try:
        result = _evaluate(tree)
    except ZeroDivisionError as error:
        raise ValueError("division by zero") from error
    return round(result, 6)


if __name__ == "__main__":
    mcp.run()
