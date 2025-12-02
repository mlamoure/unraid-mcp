# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
MCP server for Unraid GraphQL API built with FastMCP 2. Modular architecture with separate packages for config, core, subscriptions, and tools.

## Development Commands

### Setup
```bash
uv sync                  # Install dependencies
uv sync --group dev      # Include dev dependencies
```

### Running the Server
```bash
./dev.sh                      # Development mode with auto-restart and log tailing
./dev.sh --kill               # Stop server
./dev.sh --status             # Check server status
./dev.sh --tail               # Follow logs
uv run unraid-mcp-server      # Direct run
uv run -m unraid_mcp.main     # Module execution
```

### Code Quality
```bash
uv run black unraid_mcp/      # Format
uv run ruff check unraid_mcp/ # Lint
uv run mypy unraid_mcp/       # Type check
```

### Testing
```bash
uv run pytest                           # Run all tests
uv run pytest tests/test_foo.py         # Run single file
uv run pytest -k "test_name"            # Run by name pattern
uv run pytest -m "not slow"             # Skip slow tests
uv run pytest -m "not integration"      # Skip integration tests
uv run pytest --no-cov                  # Skip coverage
```

### Docker
```bash
docker build -t unraid-mcp-server .
docker-compose up -d
docker-compose logs -f unraid-mcp
```

### Environment Variables
Copy `.env.example` to `.env`:
- `UNRAID_API_URL`: GraphQL endpoint (required)
- `UNRAID_API_KEY`: API key (required)
- `UNRAID_MCP_TRANSPORT`: `streamable-http` (default), `sse` (deprecated), `stdio`
- `UNRAID_MCP_PORT`: Server port (default: 6970)
- `UNRAID_MCP_HOST`: Server host (default: 0.0.0.0)
- `UNRAID_MCP_LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR

## Architecture

### Module Structure
```
unraid_mcp/
├── main.py              # Entry point
├── server.py            # FastMCP server setup, module registration
├── config/
│   ├── settings.py      # Environment loading, configuration constants
│   └── logging.py       # Rich logging with file rotation
├── core/
│   ├── client.py        # GraphQL client with timeout management
│   ├── exceptions.py    # ToolError for user-facing errors
│   └── types.py         # Shared type definitions
├── subscriptions/
│   ├── manager.py       # WebSocket subscription lifecycle
│   ├── resources.py     # MCP resource registration
│   └── diagnostics.py   # Subscription testing tools
└── tools/               # Domain-specific tools (26 total)
    ├── docker.py        # Container management
    ├── system.py        # System info
    ├── storage.py       # Disks, shares, logs, notifications
    ├── health.py        # Health checks
    ├── virtualization.py# VM management
    └── rclone.py        # Cloud storage remotes
```

### Tool Registration Pattern
Each tool module exports a `register_*_tools(mcp: FastMCP)` function. Tools are decorated with `@mcp.tool()` and use `make_graphql_request()` for API calls. Example:
```python
def register_docker_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_docker_containers() -> list[dict[str, Any]]:
        response = await make_graphql_request(query)
        # Process and return data
```

### Key Patterns
- **Error Handling**: Raise `ToolError` for user-facing errors; exceptions are logged with context
- **Idempotent Operations**: `is_idempotent_error()` in client.py treats "already started/stopped" as success
- **Timeout Tiers**: Default 30s, disk operations 90s (configurable in settings.py)
- **Environment Loading**: Cascading .env files - container mount → project root → local

### Transport Endpoints
- `streamable-http`: HTTP on `/mcp` (recommended)
- `sse`: Server-Sent Events on `/mcp` (deprecated)
- `stdio`: Standard I/O for direct integration