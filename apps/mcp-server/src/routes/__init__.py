from fastmcp import FastMCP

from . import internal


def register_routes(mcp: FastMCP) -> None:
    """Register all custom HTTP routes onto the FastMCP instance."""
    internal.register(mcp)
