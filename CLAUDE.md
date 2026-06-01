# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Envel** is an AI-powered envelope budgeting platform. It implements envelope
budgeting methodology — every rupiah (IDR) is assigned to a specific category —
exposed over the Model Context Protocol (MCP) and driven by a conversational
LangGraph agent.

This is a monorepo of **four independently deployed services** that communicate
**only over HTTP** (no shared Python imports between apps):

- `apps/mcp-server/` — FastMCP server exposing finance tools & prompts (host port **8001**, container 8000)
- `apps/auth-server/` — OAuth 2.1 / JWT authentication server (host port **9000**)
- `apps/agent/` — LangGraph Deep Agent that drives the tools (host port **8002**, container 8000)
- `apps/web/` — Next.js 16 chat UI (host port **3000**)

Each app has its own `README.md`, `.env.example`, `Dockerfile`, and
`docker-compose.yml` (included from the root `docker-compose.yml`). The agent's
behavior is defined by the canonical skill at `skills/envel/SKILL.md`.

## Commands

The whole stack runs via Docker Compose from the repo root.

### Run (Docker Compose)

```bash
# Dev: bare command auto-applies docker-compose.override.yml
# (source mounts + hot reload for the Python services)
docker compose up -d --build

# Prod: images only, no override (this is what scripts/deploy.sh uses)
docker compose -f docker-compose.yml up -d --no-build
```

Ports: web `:3000`, mcp `:8001`, auth `:9000`, agent `:8002`.

### Configure `.env` per app

Secrets live **per app** — each `.env` is the interpolation source for that
app's compose file. Copy from each `.env.example`. Cross-app invariants:

- `JWT_SECRET` — **identical** across auth-server, mcp-server, and agent (HS256).
- `INTERNAL_API_KEY` — **identical** across auth-server and mcp-server.
- `AUTH_DATA_KEY` — Fernet key in auth-server (encrypts each user's `db_url` at rest).
- `OPENAI_API_KEY` + `LANGSMITH_API_KEY` in agent (the containerized LangGraph
  server verifies a Self-Hosted Lite license on startup).

### Agent dev loop

The agent has a faster non-Docker loop via `langgraph dev` (http://localhost:2024).
See `apps/agent/README.md`.

## Architecture

### Service topology

```text
Browser ─▶ web (:3000) ──Bearer JWT──▶ agent (:8002)
                                          │ verify JWT (HS256), forward token
                                          ▼
   auth-server (:9000) ◀──introspect/db-url──── mcp-server (:8001)
        │                                            │
 Postgres (envel_auth)              Postgres (envel_managed, schema=user_<id>)

MCP clients (Claude/ChatGPT) ── OAuth 2.1 ─▶ auth-server ─▶ mcp-server
```

### Per-user data isolation (Postgres schemas)

Each user's financial data lives in its **own Postgres schema** (`user_<id>`)
inside the `envel_managed` database. The auth server stores each user's
`db_url` **encrypted at rest with Fernet** (`AUTH_DATA_KEY`).

On each request the MCP server (`apps/mcp-server/src/deps.py`):

1. `current_user()` reads the verified JWT's `sub`, then fetches the user's
   `db_url` from the auth server's `/internal/db-url` endpoint (authorized with
   `INTERNAL_API_KEY`, cached 5 min per username).
2. `user_session(db_url)` yields a SQLAlchemy session bound to that user's
   schema. Engines are cached per `db_url` to avoid reconnecting each request.

### Authentication

- Login & token issuance happen in `apps/auth-server`. Tokens are **JWTs signed
  HS256** with the shared `JWT_SECRET`.
- The **agent** verifies incoming JWTs locally (`apps/agent/envel_agent/auth.py`)
  and forwards them to MCP per request; it also scopes LangGraph threads to their
  owner.
- The **MCP server** trusts JWTs verified by FastMCP and resolves them to a DB
  URL via the auth server's internal API. MCP clients authenticate via the full
  OAuth 2.1 flow against the auth server.
- `/internal/*` endpoints on the auth server are protected by `INTERNAL_API_KEY`
  and must not be exposed publicly.

### MCP server internals (`apps/mcp-server/src/`)

- `main.py` — builds the `FastMCP("Envel")` app, registers routes & sub-apps,
  and mounts a `GenerativeUI` provider (LLM writes Prefab UI code, run in a
  Pyodide/Deno sandbox; it cannot touch the DB and is fed data only via tools).
- `components/tools/` — the finance tools: `account_crud`, `envelope_crud`,
  `envelope_group_crud`, `get_workspace`, `plan_action`, `read_transactions`,
  `write_transactions`.
- `apps/` — higher-level interactive app surfaces (`envelopes`, `transactions`).
- `config.py` — `pydantic-settings`; builds `managed_database_url` from
  `POSTGRES_*` parts. `deps.py` — request-scoped user/session helpers.
- `models.py` — SQLAlchemy models. Schema changes are managed by **Alembic**
  (`alembic/versions/`).

### Database migrations (Alembic)

Both `apps/mcp-server` and `apps/auth-server` use Alembic. The MCP server runs
migrations **per user schema** (`alembic -x schema=user_<id> upgrade head`) —
`scripts/deploy.sh` iterates every `user_*` schema on deploy. Add a new
migration for any schema change; never edit a merged migration.

### Agent (`apps/agent/`)

A standalone LangGraph **Deep Agent** (`envel_agent/`). It connects to the MCP
server for all finance tools/data and loads `skills/envel/SKILL.md` as its
system prompt. The Web client talks to this LangGraph server directly (no BFF).
It has its **own** Postgres (pgvector) + Redis for chat history, checkpoints,
and long-term memory — it never touches `envel_managed`. The package can't be
named `src` (reserved by langgraph). The Dockerfile/compose are generated via
`langgraph dockerfile`.

### Web (`apps/web/`)

Next.js **16** (React 19) — **breaking changes from earlier Next versions**.
Read `apps/web/AGENTS.md` and the bundled docs in `node_modules/next/dist/docs/`
before writing UI code. It needs no `.env` in Docker (service URLs are set inline
in its compose file).

## Deployment

Single VM, Docker Compose, GHCR images. CI builds each service image and pushes
to `ghcr.io/maulairfani/envel-{mcp,auth,agent,web}:<git-sha>`; the VM pulls and
restarts (the VM never builds). `scripts/deploy.sh` pulls images, migrates the
auth DB + every user schema, starts the stack, and health-checks (agent `/ok`,
web `/login`). Rollback = re-run with an older `ENVEL_TAG`. Full guide:
[`docs/deployment.md`](docs/deployment.md). CI/CD: `.github/workflows/ci-cd.yml`.

## Logging

- **MCP server**: FastMCP `Context` logging (`ctx.info()`, `ctx.error()`) sent
  to the MCP client as notifications.
- **Auth server**: JSON structured logging (login attempts, token issuance/
  revocation, introspection).

## GitHub workflow (best practice)

Every change follows an issue-first, PR-based flow — never commit straight to `main`:

1. **Open an issue first.** Bug, feature, or docs — describe context, the change,
   and acceptance criteria. **Always apply at least one label** (`bug`,
   `enhancement`, `documentation`, etc.; see `gh label list`).
2. **Branch from `main`** with a prefix matching the work:
   `fix/*`, `feat/*`, `docs/*`, `chore/*` (e.g. `fix/web-proxy-redirect-500`).
3. **Commit** using [Conventional Commits](https://www.conventionalcommits.org/)
   (`fix(web): …`, `feat(agent): …`, `docs: …`). Keep commits focused — don't mix
   an unrelated refactor or docs change into a bug fix.
   - **Update `CHANGELOG.md`** when the change is user-/operator-facing: add a
     line under `## [Unreleased]` in the right group (`Added`/`Changed`/`Fixed`/
     `Removed`/`Security`). Skip for internal-only refactors, chores, or CI/docs
     tweaks no user would notice.
4. **Open a PR** to `main` that references the issue with `Closes #<n>` so the
   issue auto-closes and its card on the **Envel Roadmap** project board
   (<https://github.com/users/maulairfani/projects/2>) moves to Done on merge.
   Fill in the PR template; CI (build of every service image) must pass.
5. **Track work on the board** — new issues go to the board in `Todo`, move to
   `In Progress` when started.

> Assistant note: when asked to "commit", the assistant only **stages the
> relevant files and proposes a one-line commit message** — the human runs the
> actual `git commit`/`push`.

## Key Design Decisions

- Apps communicate **only over HTTP** — no shared Python packages.
- Per-user isolation is a **Postgres schema per user**, with each user's DB URL
  **Fernet-encrypted** in the auth DB.
- `JWT_SECRET` must be identical across auth/mcp/agent; `INTERNAL_API_KEY` across
  auth/mcp. These and all real secrets live only in per-app `.env` files (never
  in git — only `.env.example` is committed).
- The project is licensed **AGPL-3.0** (see `LICENSE`); contributions are subject
  to the CLA terms in `CONTRIBUTING.md`.
