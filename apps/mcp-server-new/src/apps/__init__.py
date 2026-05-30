"""
MCP Apps — tools yang return interactive UI (Prefab) bukan teks.

Beda dengan `components/tools/` (auto-discovered via FileSystemProvider pakai
standalone `@tool`): app butuh `@mcp.tool(app=True)`, yang cuma ada di
server-bound decorator. Jadi tiap app expose `register(mcp)` dan didaftarkan
di sini, persis pola `routes/` (lihat src/routes/__init__.py).

Tambah app baru:
  1. Bikin file src/apps/<nama>.py dengan `def register(mcp): ...`
  2. Import + panggil di register_apps() bawah.
"""

from fastmcp import FastMCP

from . import transactions


def register_apps(mcp: FastMCP) -> None:
    """Daftarkan semua interactive app ke instance FastMCP."""
    transactions.register(mcp)
