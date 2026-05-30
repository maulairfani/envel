"""
Internal routes — dipanggil service-to-service (auth-server ↔ mcp-server),
bukan untuk client publik. Dilindungi shared secret (INTERNAL_API_KEY).
"""

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from .. import provisioning
from ..config import settings


def _check_internal_auth(request: Request) -> bool:
    return request.headers.get("authorization") == f"Bearer {settings.internal_api_key}"


def register(mcp: FastMCP) -> None:
    @mcp.custom_route("/internal/provision", methods=["POST"])
    async def provision_endpoint(request: Request):
        if not _check_internal_auth(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)

        body = await request.json()
        username = body.get("username")
        if not username:
            return JSONResponse({"error": "missing_username"}, status_code=400)

        try:
            db_url = provisioning.provision(username)
        except ValueError as e:
            return JSONResponse({"error": str(e)}, status_code=400)
        except Exception as e:
            return JSONResponse({"error": f"provisioning_failed: {e}"}, status_code=500)

        return JSONResponse({"db_url": db_url})
