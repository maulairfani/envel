from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server.providers import FileSystemProvider

from .auth import auth
from .routes import register_routes

COMPONENTS_DIR = Path(__file__).resolve().parent / "components"

mcp = FastMCP(
    "Envel",
    auth=auth,
    providers=[FileSystemProvider(COMPONENTS_DIR)],
)
register_routes(mcp)

app = mcp.http_app()
