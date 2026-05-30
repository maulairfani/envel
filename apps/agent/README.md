# Envel Agent

Standalone **LangGraph Deep Agent** for Envel. It connects to the Envel MCP
server for all finance tools/data, and loads the canonical `envel` behavior
skill (`../../skills/envel/SKILL.md`) as its system prompt.

No BFF: the Web client talks to this LangGraph server directly. Auth lives here
(`envel_agent/auth.py`) — incoming Envel JWTs are verified locally (HS256,
shared `JWT_SECRET`) and forwarded to MCP on the user's behalf.

## Layout

```
apps/agent/
├─ langgraph.json     # graph: envel -> envel_agent/agent.py:make_graph ; auth -> envel_agent/auth.py:auth
├─ requirements.txt   # runtime deps (matches mcp-server / auth-server convention)
├─ Dockerfile         # generated FROM langchain/langgraph-api:3.12 (langgraph dockerfile)
├─ docker-compose.yml # agent + agent-postgres (pgvector) + agent-redis
├─ .env.example
└─ envel_agent/       # package name can't be "src" (reserved by langgraph)
   ├─ config.py       # env-driven settings (model, MCP_URL, JWT_SECRET, skill path)
   ├─ mcp_client.py   # MultiServerMCPClient + per-request Bearer passthrough
   ├─ auth.py         # @auth.authenticate (verify JWT) + @auth.on (scope threads by owner)
   └─ agent.py        # create_deep_agent + token-injection middleware
```

## Run locally (dev, no Docker)

```bash
pip install -r requirements.txt "langgraph-cli[inmem]"
cp .env.example .env           # set OPENAI_API_KEY, JWT_SECRET, MCP_URL, ENVEL_DEV_TOKEN
langgraph dev                  # http://localhost:2024  (Studio auto-opens)
```

- Make sure the MCP server is up and reachable at `MCP_URL` (default
  `http://localhost:8001/mcp`).
- For a quick single-user smoke test, set `ENVEL_DEV_TOKEN` to a JWT signed
  with the shared `JWT_SECRET` (`sub` = an existing username, e.g. `admin`).
  Real per-user auth flows through the `Authorization: Bearer` header instead.

## Run in Docker (container parity)

> **Requires a LangSmith API key.** The `langchain/langgraph-api` image is the
> licensed self-hosted server and verifies a license on startup. Set
> `LANGSMITH_API_KEY` in `.env` (a free LangSmith account enables the
> Self-Hosted Lite tier). Without it the container crash-loops with
> `License verification failed`. The local `langgraph dev` workflow needs no key.

From the repo root (root compose `include`s this app):

```bash
docker compose up -d --build agent
```

- Exposed on host port **8002** → container 8000.
- Brings up its own `agent-postgres` (pgvector) and `agent-redis` — LangGraph's
  persistence + queue. Independent of `envel_managed`.
- Joins the shared `envel` network so it reaches `mcp-server` at
  `http://mcp-server:8000/mcp` (overridden in compose).
- The skill is **mounted** read-only (`../../skills:/skills:ro`) rather than
  baked, since it lives at repo-root outside the build context. For a
  self-contained prod image, copy the skill into the build context instead.

The Dockerfile/compose are generated via
`langgraph dockerfile ./Dockerfile --add-docker-compose` and committed (so
`docker compose build` needs no CLI). Regenerate if `langgraph.json` changes —
note the generator emits a Windows-backslash path in `LANGGRAPH_AUTH` that must
be fixed to a forward slash.

## Persistence

Chat history + checkpoints are managed by the LangGraph server's own Postgres
(isolated by `thread_id`; threads scoped to their owner via custom auth). The
agent never touches `envel_managed` — financial data stays behind MCP.
