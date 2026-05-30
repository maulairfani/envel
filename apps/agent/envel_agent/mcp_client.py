"""
MCP client + per-request token passthrough.

The agent talks to the Envel MCP server over streamable-http. Each user's JWT
must ride along as a Bearer header so the MCP server resolves the right user
schema. We carry the token in a ContextVar and inject it via an httpx.Auth so
the (process-wide) MultiServerMCPClient stays a singleton.

Set the token per request with `set_user_token(...)`; when unset, we fall back
to ENVEL_DEV_TOKEN so `langgraph dev` works end-to-end with a dev token.
"""

import contextvars

import httpx
from langchain_mcp_adapters.client import MultiServerMCPClient

from envel_agent import config

# Per-request user token (set by the auth bridge; see auth.py / agent runtime).
_user_token: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "envel_user_token", default=None
)


def set_user_token(token: str | None) -> None:
    _user_token.set(token)


class _BearerFromContext(httpx.Auth):
    """Inject `Authorization: Bearer <token>` from the ContextVar (or dev token)."""

    def auth_flow(self, request):
        token = _user_token.get() or config.ENVEL_DEV_TOKEN
        if token:
            request.headers["Authorization"] = f"Bearer {token}"
        yield request


_client = MultiServerMCPClient(
    {
        "envel": {
            "transport": "streamable_http",
            "url": config.MCP_URL,
            "auth": _BearerFromContext(),
        }
    }
)


async def get_mcp_tools():
    """Discover the Envel finance tools from the MCP server."""
    return await _client.get_tools()
