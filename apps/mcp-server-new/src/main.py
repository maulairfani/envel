from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.providers import FileSystemProvider
from pydantic import AnyHttpUrl
from starlette.requests import Request
from starlette.responses import JSONResponse

from . import provisioning
from .config import settings

COMPONENTS_DIR = Path(__file__).resolve().parent / "components"

verifier = JWTVerifier(public_key=settings.jwt_secret, algorithm="HS256")
auth = RemoteAuthProvider(
    token_verifier=verifier,
    authorization_servers=[AnyHttpUrl(settings.auth_base_url)],
    base_url=AnyHttpUrl(settings.mcp_base_url),
)

mcp = FastMCP(
    "Envel",
    auth=auth,
    providers=[FileSystemProvider(COMPONENTS_DIR)],
)


@mcp.custom_route("/internal/provision", methods=["POST"])
async def provision_endpoint(request: Request):
    # Shared-secret auth
    expected = f"Bearer {settings.internal_api_key}"
    if request.headers.get("authorization") != expected:
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


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
