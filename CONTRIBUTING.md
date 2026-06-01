# Contributing to Envel

Thanks for your interest in contributing! Envel is an AI-powered envelope
budgeting platform built around the Model Context Protocol. This guide explains
how to get a working setup and how to land a change.

## Ways to contribute

- **Report bugs** — open an issue using the bug template.
- **Request features** — open an issue using the feature template.
- **Improve docs** — fixes to the README, per-app READMEs, or `docs/` are very welcome.
- **Write code** — pick up an open issue, or discuss a larger change in an issue first.

For anything non-trivial, please open an issue to discuss the approach before you
start coding. It saves everyone time.

## Repository layout

Envel is a monorepo of four independently deployed services that communicate
only over HTTP:

| App | Stack | Host port |
| --- | ----- | --------- |
| `apps/mcp-server` | FastMCP + Postgres (per-user schema) + Alembic | 8001 |
| `apps/auth-server` | FastAPI OAuth 2.1 / JWT + Postgres | 9000 |
| `apps/agent` | LangGraph Deep Agent + Postgres + Redis | 8002 |
| `apps/web` | Next.js 16 chat UI | 3000 |

Each app has its own `README.md`, `.env.example`, `Dockerfile`, and
`docker-compose.yml`. Read the relevant app README before changing it.

## Local development

The whole stack runs via Docker Compose from the repo root:

```bash
# 1. Create one .env per Python app (copy from each .env.example)
cp apps/auth-server/.env.example apps/auth-server/.env
cp apps/mcp-server/.env.example  apps/mcp-server/.env
cp apps/agent/.env.example       apps/agent/.env

# 2. Keep JWT_SECRET identical across auth + mcp + agent,
#    and INTERNAL_API_KEY identical across auth + mcp.

# 3. Bring the stack up (dev override adds source mounts + hot reload)
docker compose up -d --build
```

See [`docs/deployment.md`](docs/deployment.md) for the full topology and the
prod vs. dev compose distinction. For the agent's faster `langgraph dev` loop,
see [`apps/agent/README.md`](apps/agent/README.md).

## Database migrations

The MCP and auth servers use Alembic. If your change touches the schema, add a
migration in the app's `alembic/versions/` and make sure `alembic upgrade head`
runs cleanly. Never edit an already-merged migration — add a new one.

## Coding conventions

- **Python**: type hints, `pydantic-settings` for config, FastMCP `Context`
  logging in MCP tools. Match the style of the surrounding code.
- **Web**: this is **Next.js 16** with breaking changes from earlier versions —
  read `apps/web/AGENTS.md` and the bundled docs before writing UI code.
- Keep secrets out of git. Only `.env.example` files are committed.
- Follow [Conventional Commits](https://www.conventionalcommits.org/) for commit
  messages (e.g. `feat(web): ...`, `fix(agent): ...`, `docs: ...`).

## Pull request process

1. Fork the repo and create a branch off `main`.
2. Make your change with clear, focused commits.
3. Ensure the stack builds (`docker compose build`) and any migrations apply.
4. Open a PR against `main` and fill out the PR template. Link the issue it closes.
5. A maintainer will review. CI must pass (it builds every service image).

## Contributor License Agreement (CLA)

Envel is licensed under **AGPL-3.0**. To keep the option of offering commercial
licenses (dual-licensing) open, the project requires that contributors grant the
maintainer the right to relicense their contributions.

By submitting a pull request, you agree that:

- Your contribution is your original work (or you have the right to submit it), and
- You grant **Mohammad Maulana Irfani** a perpetual, worldwide, royalty-free
  license to use, modify, and **relicense** your contribution, including under
  commercial terms, in addition to the project's AGPL-3.0 license.

If your employer has rights to work you create, make sure you have permission to
contribute under these terms. If you cannot agree to this, please open an issue
to discuss before contributing.

## Questions

Open a [discussion or issue](https://github.com/maulairfani/envel/issues),
or email <maulairfani15@gmail.com>.
