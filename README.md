# SweatStack MCP Server


> [!IMPORTANT]  
> The SweatStack MCP Server is highly experimental. The code in this repository is distributed as-is and comes with no warranty, support, or promise of future updates. Use at your own risk!


## Local install for Claude Desktop

This requires [uv](https://docs.astral.sh/uv/) to be installed.

Clone the repository and install the dependencies:

```bash
git clone https://github.com/sweatstack/sweatstack-mcp.git
cd sweatstack-mcp
```

Copy the `.env.example` file to `.env` and set the `SWEATSTACK_API_KEY` (get it [here](https://app.sweatstack.no/settings/api)).

Install the server for Claude Desktop:

```bash
uv run mcp install src/sweatstack_mcp/server.py --name "SweatStack" --with-editable . --env-file .env
```