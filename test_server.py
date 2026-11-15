"""Check the library desk works, without Claude.

Starts mcp_server.py the way an AI app would, connects to it over MCP,
lists its tools and tries each one. One search uses one Voyage call.
"""

import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])


def show(result) -> None:
    """Print what a tool sent back, or its error."""
    if result.isError:
        print("   ERROR:", result.content[0].text)
        return
    data = result.structuredContent
    if data is None:
        print("  ", result.content[0].text[:300])
        return
    print("  ", json.dumps(data, indent=2)[:600])


async def main() -> None:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools on offer:")
            for tool in tools.tools:
                first_line = (tool.description or "").strip().splitlines()[0]
                print(f"  - {tool.name}: {first_line}")

            print("\n1. list_documents")
            show(await session.call_tool("list_documents", {}))

            print("\n2. calculate '(2005 - 1532) / 1532 * 100'")
            show(
                await session.call_tool(
                    "calculate", {"expression": "(2005 - 1532) / 1532 * 100"}
                )
            )

            print("\n3. calculate something unsafe (should be refused)")
            show(
                await session.call_tool(
                    "calculate", {"expression": "__import__('os').system('ls')"}
                )
            )

            print("\n4. search_filings 'Q1 2026 underlying profit', year 2026")
            show(
                await session.call_tool(
                    "search_filings",
                    {"query": "Q1 2026 underlying profit", "year": 2026, "top_k": 2},
                )
            )


if __name__ == "__main__":
    asyncio.run(main())
