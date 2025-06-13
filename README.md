# SweatStack MCP Server


> [!IMPORTANT]  
> The SweatStack MCP Server is highly experimental. The code in this repository is distributed as-is and comes with no warranty, support, or promise of future updates. Use at your own risk!


## Local install for Claude Desktop

This requires [uv](https://docs.astral.sh/uv/) to be installed.

Clone the repository:

```bash
git clone https://github.com/sweatstack/sweatstack-mcp.git
cd sweatstack-mcp
```

Copy the `.env.example` file to `.env` and set the `SWEATSTACK_API_KEY` (get it [here](https://app.sweatstack.no/settings/api)).

Install the server for Claude Desktop:

```bash
uv run mcp install src/sweatstack_mcp/server.py --name "SweatStack" --with-editable . --env-file .env
```

You might need to restart Claude Desktop for the server to be available.
After that, you can use the server directly in Claude Desktop.

![Claude Desktop demo](./media/sweatstack-mcp-claude-desktop.gif)



## CLI chat with llm

The repository also contains a cli tool that can be used to chat interactively with the server.

```
make chat
```

This is built on top of [llm](https://llm.datasette.io/en/stable/index.html) and uses the [llm-tools-mcp](https://github.com/VirtusLab/llm-tools-mcp) plugin.

This tool requires an API key for an LLM provider to be present.
Please refer to the [llm documentation](https://llm.datasette.io/en/stable/index.html) for more information.

![CLI demo](./media/sweatstack-mcp-llm.gif)


## Development

Claude Desktop logs are availabe here:
- MacOS: `~/Library/Logs/Claude/`
- Windows: `C:\Users\{username}\AppData\Local\Claude\Logs\`