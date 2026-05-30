"""
Envel Deep Agent.

Graph factory wired into langgraph.json (`./envel_agent/agent.py:make_graph`). It:
  1. discovers the Envel finance tools from the MCP server,
  2. applies this agent's own system prompt (see prompts.py),
  3. loads the portable `envel` skill on-demand via the skills middleware,
  4. gives each user persistent, isolated long-term memory under /memories/,
  5. handles tool-call failures (retry transient read-only calls; turn any other
     failure into a readable message instead of crashing the run), and
  6. builds a Deep Agent over OpenAI (gpt-5.4-nano by default).

Persistence (checkpointer/store) is provided by the LangGraph server at
runtime — we don't construct one here. The /memories/ StoreBackend uses that
platform-provided store.

Per-request user token → MCP passthrough: `inject_user_token` runs once per
invocation, reads the authenticated user (populated by src/auth.py) from the
run config, and stashes the raw JWT so MCP calls go out as that user. Falls
back to ENVEL_DEV_TOKEN when there is no authenticated user (local dev).
"""

import httpx
from langchain.agents.middleware import (
    ToolRetryMiddleware,
    before_agent,
    wrap_tool_call,
)
from langchain.messages import ToolMessage
from langgraph.config import get_config

from deepagents import create_deep_agent
from deepagents.backends import (
    CompositeBackend,
    FilesystemBackend,
    StateBackend,
    StoreBackend,
)

from envel_agent import config
from envel_agent.mcp_client import get_mcp_tools, set_user_token
from envel_agent.prompts import SYSTEM_PROMPT

# /skills/   → on-disk skill dir (read-only mount in the container)
# /memories/ → per-user long-term memory in the platform store (isolated by the
#              authenticated user's identity), persists across threads
# everything else (internal agent files, offloaded results) → ephemeral
#              StateBackend, so nothing is written to the read-only skill mount
SKILLS_NAMESPACE = "/skills/"
MEMORIES_NAMESPACE = "/memories/"
MEMORY_FILE = "/memories/preferences.md"


def _backend(rt):
    return CompositeBackend(
        default=StateBackend(rt),
        routes={
            SKILLS_NAMESPACE: FilesystemBackend(
                root_dir=str(config.SKILLS_DIR), virtual_mode=True
            ),
            MEMORIES_NAMESPACE: StoreBackend(
                rt, namespace=lambda rt: (rt.server_info.user.identity,)
            ),
        },
    )


@before_agent
def inject_user_token(state, runtime):
    """Forward the authenticated user's JWT to MCP for this invocation."""
    try:
        cfg = get_config()
        user = (cfg.get("configurable") or {}).get("langgraph_auth_user") or {}
        token = user.get("token")
        if token:
            set_user_token(token)
    except Exception:
        # No active run config / no custom auth → rely on ENVEL_DEV_TOKEN.
        pass
    return None


# Read-only MCP tools are safe to auto-retry on transient network blips. Writes
# (plan_action / write_transactions / *_crud) are intentionally NOT retried: a
# mutation whose response was merely lost could be double-applied.
RETRYABLE_TOOLS = ["get_workspace", "read_transactions"]
_TRANSIENT = (TimeoutError, ConnectionError, httpx.TransportError)


@wrap_tool_call
async def handle_tool_errors(request, handler):
    """Turn any tool exception into a readable ToolMessage so the run never
    crashes — the model sees the failure and can recover or tell the user."""
    try:
        return await handler(request)
    except Exception as e:  # noqa: BLE001 — surface every failure to the model
        return ToolMessage(
            content=(
                f"Tool '{request.tool_call['name']}' failed: {e}. "
                "Tell the user plainly what went wrong and suggest a next step; "
                "do not retry blindly."
            ),
            tool_call_id=request.tool_call["id"],
        )


async def make_graph():
    tools = await get_mcp_tools()
    return create_deep_agent(
        name="envel",
        model=config.MODEL,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        skills=[SKILLS_NAMESPACE],
        memory=[MEMORY_FILE],
        backend=_backend,
        middleware=[
            inject_user_token,
            # outer: convert any leftover tool exception into a ToolMessage
            handle_tool_errors,
            # inner: retry only read-only tools on transient network errors
            ToolRetryMiddleware(
                max_retries=2,
                tools=RETRYABLE_TOOLS,
                retry_on=_TRANSIENT,
            ),
        ],
    )
