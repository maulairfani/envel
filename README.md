# Envel

**Budget with the AI you already use.** Envel is an envelope-budgeting engine
exposed over the [Model Context Protocol](https://modelcontextprotocol.io), so
you can manage your money straight from **Claude, ChatGPT, or any MCP client** —
no new app to learn. Connect it once and just talk: *"log my groceries,"* *"how
much is left this month?"*, *"help me plan my paycheck."*

Don't have a favorite AI client, or want a ready-made experience? Envel also
**ships its own agent and chat web app** — the same engine, with a finance-tuned
assistant and UI included. Either way, your data stays isolated behind OAuth 2.1.

[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License: AGPL v3](https://img.shields.io/badge/license-AGPL--3.0-blue)](LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](CONTRIBUTING.md)

---

## Why AI-first?

A normal budgeting app is a filing cabinet: *you* invent the categories, *you*
decide how much goes where, *you* figure out why you overspent and how to do
better next month. The app just stores what you typed.

Envel flips that. Because you budget *together* with an AI, it understands your
situation and thinks alongside you:

- **You talk, it does the bookkeeping.** No forms, no category dropdowns — say
  what happened and Envel records, categorizes, and updates the budget.
- **It reasons about your money, not just stores it.** Ask "can I afford this?"
  or "where did my money go?" and get a real answer grounded in your actual data.
- **It coaches, not just tracks.** Envel spots overspending, unassigned money,
  and off-track goals, then suggests concrete next steps — the part traditional
  apps leave entirely to you.

The result: the hard part of budgeting — *thinking* — gets shared with the AI.

---

## What you can do

- **Manage money by chatting.** Tell Envel *"just spent 75k at the convenience store with my BCA card"* and it records the expense, categorizes it, and updates your budget — all in plain language, in rupiah.
- **See all your accounts in one place.** Bank, e-wallet, cash, and credit card — Envel tracks each balance so you always know your real total.
- **Plan where your money goes.** Sort your money into envelopes (Needs, Wants, Savings) and set goals like *"save Rp 5jt by December"* or *"spend max Rp 1jt on groceries this month."*
- **Log spending in seconds.** Drop in a whole receipt and each line becomes a transaction in one go; transfers between accounts are handled too.
- **Know exactly where you stand.** Ask for a budget review and Envel surfaces what's still unassigned, what's overspent, and what's on track.
- **See it, not just read it.** Inside AI clients that support rich UI, Envel renders live interactive views — an envelope snapshot with progress bars that highlights overspending, a transactions browser — and generates custom charts on demand.
- **Keep your finances private.** Every user gets their own isolated database with credentials encrypted at rest — your money data is never mixed with anyone else's.

---

## Budgeting method

Envel follows **envelope budgeting**: instead of a single pool of money you hope
lasts the month, you decide what each part of your money is for, up front. The
idea is simple —

1. **Money lives in accounts.** Your real balances: bank, e-wallet, cash, cards.
2. **Envelopes are jobs for that money.** Groceries, rent, an emergency fund, a
   trip — each is an envelope you assign money to.
3. **Ready to Assign (RTA)** is money you own but haven't given a job yet. When
   income comes in, it lands here until you assign it to envelopes.
4. **The goal is RTA = 0.** Not zero in your bank — zero *unassigned*. Every
   rupiah you have is already pointed at something on purpose.

As you spend, an envelope's available amount goes down; leftover money rolls over
to next month. If you overspend an envelope it goes negative, and Envel nudges
you to cover it — by moving money from another envelope or assigning fresh RTA.
Nothing is estimated: every balance and budget figure is derived from your actual
transactions and assignments.

### Envelope goals

Give an envelope a target so Envel can track progress and tell you what to fund:

| Target | Meaning | Example |
| ------ | ------- | ------- |
| **Spend monthly** | Spend up to X each month; refills toward X every month | Groceries — Rp 1.500.000 / month |
| **Save monthly** | Set aside X every month; keeps accumulating | Emergency fund — Rp 500.000 / month |
| **Save total** | Save up to X once, no deadline | New laptop — Rp 15.000.000 |
| **Save by date** | Have X ready by a specific date | Year-end trip — Rp 6.000.000 by Dec 2026 |

All amounts are in Indonesian rupiah (IDR), whole numbers, no cents.

---

## Architecture

Envel is a monorepo of **four independently deployed services** that communicate
only over HTTP — there are no shared Python imports between apps.

| App | Stack | Host port | Responsibility |
| --- | ----- | --------- | -------------- |
| [`apps/mcp-server`](apps/mcp-server) | FastMCP · Postgres · Alembic | `8001` | Finance tools & data, one Postgres **schema per user** |
| [`apps/auth-server`](apps/auth-server) | FastAPI · OAuth 2.1 / JWT · Postgres | `9000` | Login, token issuance, per-user DB-URL resolution (Fernet-encrypted) |
| [`apps/agent`](apps/agent) | LangGraph Deep Agent · Postgres · Redis | `8002` | The conversational agent; verifies JWTs and calls MCP per user |
| [`apps/web`](apps/web) | Next.js 16 chat UI | `3000` | Browser front end at `chat.envel.dev` |

```text
Browser ─▶ web (Next.js, :3000)
                │  Authorization: Bearer <JWT>
                ▼
            agent (LangGraph, :8002) ──verify JWT (HS256)──▶ forwards token
                │                                                   │
                ▼                                                   ▼
        auth-server (:9000) ◀── token introspection ──── mcp-server (:8001)
                │                                                   │
       Postgres (envel_auth)                          Postgres (envel_managed,
                                                          schema = user_<id>)

MCP clients (Claude, ChatGPT) ─── OAuth 2.1 ──▶ auth-server ──▶ mcp-server
```

**How a request flows:** the web app logs the user in via the auth server and
receives a JWT. It calls the LangGraph agent with that bearer token; the agent
verifies the JWT locally (shared `JWT_SECRET`, HS256) and forwards it to the MCP
server on the user's behalf. The MCP server resolves the token to that user's
Postgres schema and reads/writes only their data.

---

## Getting started

The whole stack runs via Docker Compose from the repo root. Rather than duplicate
setup steps here, follow the guide that matches what you want to do:

| I want to… | Read |
| ---------- | ---- |
| Run Envel locally / contribute | [CONTRIBUTING.md](CONTRIBUTING.md) — setup, conventions, PR process |
| Work on a specific service | the app folder: [mcp-server](apps/mcp-server) · [auth-server](apps/auth-server) · [agent](apps/agent/README.md) · [web](apps/web) |
| Deploy to a VM | [docs/deployment.md](docs/deployment.md) — GHCR, secrets, nginx, migrations, rollback |
| Configure an app | that app's `.env.example` (the per-app `.env` is the single source for its compose file) |

> Cross-app invariants: `JWT_SECRET` must be identical across auth/mcp/agent, and
> `INTERNAL_API_KEY` across auth/mcp. See each `.env.example` for the rest.

---

## Repository structure

```text
apps/
├── mcp-server/    FastMCP finance tools & prompts + Alembic (Postgres, :8001)
├── auth-server/   OAuth 2.1 / JWT auth + per-user DB-URL store (Postgres, :9000)
├── agent/         LangGraph Deep Agent (Postgres + Redis, :8002)
└── web/           Next.js 16 chat UI (:3000)
skills/
└── envel/         Canonical agent behavior skill (SKILL.md)
docs/
└── deployment.md  VM / Docker Compose deployment guide
scripts/
└── deploy.sh      VM-side pull · migrate · up · health-check
```

Each app has its own `README.md`, `.env.example`, `Dockerfile`, and
`docker-compose.yml`, included from the root `docker-compose.yml`.

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for the
development setup, conventions, and the contributor license terms. Bugs and
feature ideas go through the [issue templates](.github/ISSUE_TEMPLATE).

---

## License

Envel is licensed under the **GNU Affero General Public License v3.0** — see
[LICENSE](LICENSE). In short: you're free to use, modify, and self-host it, but
if you run a modified version as a network service you must make your source
available under the same license. For commercial licensing that isn't subject to
the AGPL's network-copyleft terms, contact <maulairfani15@gmail.com>.
