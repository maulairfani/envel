from pathlib import Path

from fastmcp import FastMCP
from fastmcp.apps.generative import GenerativeUI
from fastmcp.server.providers import FileSystemProvider

from .apps import register_apps
from .auth import auth
from .routes import register_routes

COMPONENTS_DIR = Path(__file__).resolve().parent / "components"

# GenerativeUI: LLM menulis kode Prefab sendiri, dijalankan di sandbox Pyodide
# (via subprocess Deno — lihat Dockerfile). Data divisualkan dengan cara LLM
# memanggil tool data kita (get_workspace/read_transactions) lalu meneruskan
# hasilnya ke parameter `data` generate_prefab_ui (sandbox terisolasi, tidak
# bisa akses DB sendiri).
mcp = FastMCP(
    "Envel",
    auth=auth,
    providers=[FileSystemProvider(COMPONENTS_DIR), GenerativeUI(tool_name="visualize")],
)
register_routes(mcp)
register_apps(mcp)

app = mcp.http_app()
