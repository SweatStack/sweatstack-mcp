# /// script
# dependencies = [
#   "mcp",
# ]
# ///

import asyncio

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import (
    InitializeResult,
    TextContent,
)


url = "http://localhost:8001/mcp/"


async def main():
    async with streamablehttp_client(url) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            result = await session.initialize()
            assert isinstance(result, InitializeResult)
            assert result.serverInfo.name == "StatelessServer"
            tool_result = await session.call_tool("echo", {"message": "hello"})
            assert len(tool_result.content) == 1
            assert isinstance(tool_result.content[0], TextContent)
            assert tool_result.content[0].text == "Echo: hello"

            for i in range(3):
                tool_result = await session.call_tool("echo", {"message": f"test_{i}"})
                assert len(tool_result.content) == 1
                assert isinstance(tool_result.content[0], TextContent)
                assert tool_result.content[0].text == f"Echo: test_{i}"


if __name__ == "__main__":
    asyncio.run(main())