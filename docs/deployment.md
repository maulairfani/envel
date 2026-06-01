# Deployment (single VM, Docker Compose)

CI builds each service image, pushes to GHCR tagged with the commit SHA, then
the VM pulls and restarts. The VM never builds.

```
push main → build (envel-mcp / envel-auth / envel-agent) → push ghcr.io
          → ssh VM → git reset --hard → scripts/deploy.sh (pull · migrate · up · health)
```

Images: `ghcr.io/maulairfani/envel-{mcp,auth,agent}:<git-sha>`.

## GitHub repo secrets

| Secret | What |
| ------ | ---- |
| `SSH_PRIVATE_KEY` | private key whose public half is in the VM user's `authorized_keys` |
| `VM_HOST` | VM hostname/IP |
| `VM_USER` | SSH user on the VM |
| `VM_REPO_DIR` | absolute path to the cloned repo on the VM |

GHCR push uses the built-in `GITHUB_TOKEN` (no secret needed).

## VM one-time setup

1. Install Docker Engine + Compose plugin.
2. **Authenticate to GHCR** (images are private by default). Create a classic PAT
   with `read:packages` and log in once — it persists in `~/.docker/config.json`:
   ```bash
   echo "<PAT>" | docker login ghcr.io -u maulairfani --password-stdin
   ```
   (Alternatively make the three packages public and skip this.)
3. Clone the repo to `VM_REPO_DIR` and check out `main`.
4. Create one `.env` per app (NOT in git — secrets live only on the VM). Each
   app's `.env` is self-contained (it's the interpolation source for that app's
   compose, via `include: env_file:`). See each `.env.example` for the keys.
   - `apps/auth-server/.env`, `apps/mcp-server/.env`, `apps/agent/.env`.
   - Each Python app's `.env` holds its own `POSTGRES_*` (sets a strong password
     before the first `up`).
   - Keep `JWT_SECRET` identical across auth + mcp + agent, and
     `INTERNAL_API_KEY` identical across auth + mcp.
   - `apps/agent/.env` needs `OPENAI_API_KEY` and `LANGSMITH_API_KEY` (Self-Hosted
     Lite license); `MCP_URL` is overridden to the internal address by compose.
5. First deploy:
   ```bash
   ENVEL_TAG=latest bash scripts/deploy.sh
   ```
6. Point nginx (host) at the published ports: mcp `:8001`, auth `:9000`,
   agent `:8002`, web `:3000` (e.g. `envel.dev/mcp`, `envel.dev/auth`, a subdomain
   for the agent, and **`chat.envel.dev` → `:3000`** for the web app). The
   containers join the shared `envel` network internally.
   - The web app needs no `.env`: its config is fixed internal URLs set inline in
     `apps/web/docker-compose.yml` (`AUTH_URL=http://auth-server:9000`,
     `AGENT_URL=http://agent:8000`, `MCP_URL=http://mcp-server:8000/mcp`).
   - For native login to work behind the proxy, forward the real host headers
     (`Host`/`X-Forwarded-Host`/`X-Forwarded-Proto`) so the server-side OAuth
     `redirect_uri` resolves to `https://chat.envel.dev/`, and **whitelist that
     redirect_uri on the auth-server**.

> Migrating from the old systemd setup: stop/disable `envel-auth`, `envel-mcp`,
> `envel-platform` services first so they don't fight for the ports.

## Deploy & rollback

- **Deploy** happens automatically on push to `main`.
- **Manual deploy / rollback** — SSH to the VM and run with any pushed tag:
  ```bash
  ENVEL_TAG=<git-sha> bash scripts/deploy.sh
  ```
  Rolling back is just re-running with an older SHA (images are immutable).

`scripts/deploy.sh` pulls images, runs MCP Alembic migrations for every
`user_*` schema, starts the stack, and fails the deploy if the agent `/ok`
or web `/login` health check doesn't pass. The web image is a Next.js
standalone build (no DB, no migrations) — it just gets pulled and restarted.

## Dev vs prod compose

- **Prod** (`docker compose -f docker-compose.yml …`): images only, no source
  mounts, no `--reload`. This is what `scripts/deploy.sh` uses.
- **Dev** (bare `docker compose …`): auto-applies `docker-compose.override.yml`,
  which adds source mounts + hot reload for the Python services. The agent's dev
  loop uses `langgraph dev` (see `apps/agent/README.md`).
