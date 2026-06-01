"""
Provisioning service — ask the MCP server to create the schema + run the alembic migration for a new user.

The auth server has no direct access to the `envel_managed` DB (separation of concerns).
The MCP owns models.py + alembic migrations for the user schema.
"""

import httpx

from .config import settings


class ProvisioningError(Exception):
    pass


async def provision_managed_user(username: str) -> str:
    """Call the MCP internal endpoint to create the schema + migrate. Return db_url."""
    url = f"{settings.mcp_internal_url.rstrip('/')}/internal/provision"
    headers = {"Authorization": f"Bearer {settings.internal_api_key}"}
    payload = {"username": username}

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=payload, headers=headers)

    if resp.status_code != 200:
        raise ProvisioningError(
            f"MCP provisioning failed: {resp.status_code} {resp.text}"
        )

    data = resp.json()
    db_url = data.get("db_url")
    if not db_url:
        raise ProvisioningError(f"MCP response missing db_url: {data}")
    return db_url
