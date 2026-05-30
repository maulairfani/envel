"""Environment-driven settings for the Envel agent."""

import os
from pathlib import Path

# provider:model string passed to deepagents (init_chat_model under the hood).
MODEL = os.environ.get("ENVEL_MODEL", "openai:gpt-5.4-nano")

# MCP server exposing the Envel finance tools (streamable-http transport).
MCP_URL = os.environ.get("MCP_URL", "http://localhost:8001/mcp")

# Shared HS256 secret — same value used by auth-server (to sign) and
# mcp-server (to verify). The agent verifies incoming tokens with it.
JWT_SECRET = os.environ.get("JWT_SECRET", "")

# Dev-only bearer used for MCP calls when no per-request user token is set.
ENVEL_DEV_TOKEN = os.environ.get("ENVEL_DEV_TOKEN") or None

# Directory holding the portable Envel skill(s) — one folder per skill, each
# with a SKILL.md (Agent Skills spec). Loaded on-demand by the deep agent's
# skills middleware. Defaults to repo-root /skills; in the container it's the
# read-only mount at /skills (set ENVEL_SKILLS_DIR).
_REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = Path(os.environ.get("ENVEL_SKILLS_DIR", _REPO_ROOT / "skills"))
