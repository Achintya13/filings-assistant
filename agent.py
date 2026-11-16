"""The real pupil: Claude answers questions using the library desk over MCP.

Claude is given the desk's menu, decides which tools to use, and keeps going
round until it has enough to answer, up to a fixed number of rounds.

    uv run python agent.py                      # runs question 10
    uv run python agent.py "your own question"
"""

import asyncio
import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

MODEL = "claude-sonnet-4-6"

# Guard rail: the most times Claude may go round the loop for one question.
MAX_ROUNDS = 8

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
SERVER = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])

SYSTEM_PROMPT = """You answer questions about Lloyds Banking Group using the tools provided.

How to work:
- Plan first. If the question spans several periods, call list_documents, then search each period separately.
- Search with the words a results announcement would use, such as "underlying profit" or "CET1 ratio", plus the period.
- Use calculate for every sum, difference or comparison.

Rules for the answer:
- Use only what the tools return. Never use outside knowledge.
- Cite the source document and page for every figure, like [2025-lbg-fy-results.pdf p5].
- Check the period carefully. If the reports do not cover the period asked about, say so plainly rather than giving figures for a different period.
- If the tools do not give you the answer, say "The documents provided do not contain this information."
- Give a cause or reason only if the excerpts state it.
- Be concise."""


def to_claude_tools(mcp_tools) -> list[dict]:
    """Copy the desk's menu into the format Claude's API expects."""
    return [
        {
            "name": tool.name,
            "description": tool.description or "",
            "input_schema": tool.inputSchema,
        }
        for tool in mcp_tools
    ]


def result_text(outcome) -> str:
    """A tool can send back several pieces of text; join them into one."""
    return "\n".join(item.text for item in outcome.content if item.type == "text")


async def run_agent(question: str) -> dict:
    """Answer one question, letting Claude use the desk's tools."""
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = to_claude_tools((await session.list_tools()).tools)

            # The conversation so far. Every round adds Claude's request and
            # the desk's reply, and the whole thing is sent again next round.
            messages = [{"role": "user", "content": question}]
            tool_calls = []
            sources = {}
            input_tokens = 0
            output_tokens = 0

            for round_number in range(1, MAX_ROUNDS + 1):
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=1500,
                    system=SYSTEM_PROMPT,
                    tools=tools,
                    messages=messages,
                )
                input_tokens += response.usage.input_tokens
                output_tokens += response.usage.output_tokens

                if response.stop_reason != "tool_use":
                    answer_text = "".join(
                        block.text for block in response.content if block.type == "text"
                    )
                    return {
                        "answer": answer_text,
                        "sources": list(sources.values()),
                        "filters": tool_calls,
                        "rounds": round_number,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                    }

                messages.append({"role": "assistant", "content": response.content})

                replies = []
                for block in response.content:
                    if block.type != "tool_use":
                        continue
                    tool_calls.append({"tool": block.name, "input": block.input})
                    outcome = await session.call_tool(block.name, block.input)

                    if block.name == "search_filings" and not outcome.isError:
                        found = (outcome.structuredContent or {}).get("result", [])
                        for item in found:
                            sources[(item["source"], item["page"])] = {
                                "source": item["source"],
                                "page": item["page"],
                            }

                    replies.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_text(outcome),
                            "is_error": outcome.isError,
                        }
                    )

                messages.append({"role": "user", "content": replies})

            return {
                "answer": f"Stopped after {MAX_ROUNDS} rounds without a final answer.",
                "sources": list(sources.values()),
                "filters": tool_calls,
                "rounds": MAX_ROUNDS,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            }


def answer(question: str) -> dict:
    """Same shape as answer.py's answer(), so the marker can test either."""
    return asyncio.run(run_agent(question))


if __name__ == "__main__":
    question = (
        " ".join(sys.argv[1:])
        if len(sys.argv) > 1
        else "Which quarter was the most profitable?"
    )
    print(f"Q: {question}\n")

    result = answer(question)

    print("Tools used:")
    for number, call in enumerate(result["filters"], start=1):
        print(f"  {number}. {call['tool']} {call['input']}")

    print(f"\n{result['answer']}\n")
    print(
        f"[{result['rounds']} rounds, "
        f"{result['input_tokens']} tokens in, {result['output_tokens']} out]"
    )
