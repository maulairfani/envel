from pathlib import Path

from fastmcp import FastMCP
from fastmcp.apps.generative import GenerativeUI
from fastmcp.server.providers import FileSystemProvider

from .apps import register_apps
from .auth import auth
from .routes import register_routes

COMPONENTS_DIR = Path(__file__).resolve().parent / "components"

# GenerativeUI: the LLM writes its own Prefab code, executed in a Pyodide sandbox
# (via a Deno subprocess — see Dockerfile). Data is visualized by having the LLM
# call our data tools (get_workspace/read_transactions) and then pass the
# results to the `data` parameter of generate_prefab_ui (isolated sandbox, can't
# access the DB itself).
mcp = FastMCP(
    "Envel",
    auth=auth,
    providers=[FileSystemProvider(COMPONENTS_DIR), GenerativeUI(tool_name="visualize")],
)
register_routes(mcp)
register_apps(mcp)

app = mcp.http_app()
