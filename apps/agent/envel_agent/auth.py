"""
LangGraph custom auth.

Because the Web client talks to this LangGraph server directly (no BFF), auth
lives here. We validate the incoming Envel JWT locally with the SAME HS256
secret the auth-server signs with (and the mcp-server verifies with), use its
`sub` claim as the user identity, and scope every resource (threads, etc.) to
that owner so users can't see each other's conversations.

The raw token is stashed on the auth-user object so the graph can forward it to
the MCP server as the user's bearer (see mcp_client.set_user_token).
"""

import jwt
from langgraph_sdk import Auth

from envel_agent import config

auth = Auth()


@auth.authenticate
async def authenticate(authorization: str | None) -> Auth.types.MinimalUserDict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise Auth.exceptions.HTTPException(
            status_code=401, detail="Missing bearer token"
        )
    token = authorization.split(" ", 1)[1].strip()
    try:
        claims = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except jwt.PyJWTError:
        raise Auth.exceptions.HTTPException(status_code=401, detail="Invalid token")

    username = claims.get("sub")
    if not username:
        raise Auth.exceptions.HTTPException(status_code=401, detail="Token missing sub")

    # Custom fields (identity + raw token) land in
    # config["configurable"]["langgraph_auth_user"] for the graph to use.
    return {"identity": username, "token": token}


@auth.on.threads
async def threads_owner(ctx: Auth.types.AuthContext, value: dict) -> dict:
    """Scope conversations to their owner: tag on write, filter on read.

    Only threads are owner-scoped — assistants (the shared graph definition)
    stay accessible to any authenticated user, otherwise the auto-created
    default assistant would be filtered out ("No assistants found").
    """
    filters = {"owner": ctx.user.identity}
    metadata = value.setdefault("metadata", {})
    metadata.update(filters)
    return filters
