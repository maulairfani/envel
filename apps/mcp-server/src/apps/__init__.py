"""
MCP Apps — tools that return an interactive UI (Prefab) instead of text.

Unlike `components/tools/` (auto-discovered via FileSystemProvider using a
standalone `@tool`): an app needs `@mcp.tool(app=True)`, which only exists on
the server-bound decorator. So each app exposes `register(mcp)` and is registered
here, exactly like the `routes/` pattern (see src/routes/__init__.py).

Add a new app:
  1. Create a file src/apps/<name>.py with `def register(mcp): ...`
  2. Import + call it in register_apps() below.
"""

from fastmcp import FastMCP

from . import envelopes, transactions


def register_apps(mcp: FastMCP) -> None:
    """Register all interactive apps onto the FastMCP instance."""
    transactions.register(mcp)
    envelopes.register(mcp)
