.PHONY: chat

chat:
	uv run llm chat --ta -T 'MCP("./llm-tools-mcp-config.json")'