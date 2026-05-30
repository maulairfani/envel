from fastmcp import FastMCP

from . import internal


def register_routes(mcp: FastMCP) -> None:
    """Daftarkan semua custom HTTP route ke instance FastMCP."""
    internal.register(mcp)
