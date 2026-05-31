#!/usr/bin/env bash
# VM-side deploy for Envel (run by CI over SSH, or by hand).
#
#   ENVEL_TAG=<git-sha> bash scripts/deploy.sh
#
# Pulls the images for ENVEL_TAG, runs MCP DB migrations for every user schema,
# (re)starts the stack, and health-checks. Idempotent — re-run with an older
# ENVEL_TAG to roll back. Uses `-f docker-compose.yml` so the dev override
# (source mounts / --reload) is NEVER applied in production.
set -euo pipefail

cd "$(dirname "$0")/.."  # repo root (holds the root docker-compose.yml)

export ENVEL_TAG="${ENVEL_TAG:-latest}"
PG_USER="${POSTGRES_USER:-envel}"
PG_DB="${POSTGRES_DB:-envel_managed}"
COMPOSE="docker compose -f docker-compose.yml"  # prod only — ignore override

echo ">> Deploying Envel @ tag=${ENVEL_TAG}"

echo ">> Pulling images"
$COMPOSE pull

echo ">> Starting datastores"
$COMPOSE up -d --no-build postgres-managed postgres-auth agent-postgres agent-redis

echo ">> Waiting for managed Postgres"
until docker exec envel-postgres-managed pg_isready -U "${PG_USER}" -d "${PG_DB}" >/dev/null 2>&1; do
  sleep 1
done

echo ">> Migrating MCP schema for each user"
schemas=$(docker exec envel-postgres-managed psql -U "${PG_USER}" -d "${PG_DB}" -tAc \
  "SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'user\\_%'")
if [ -z "${schemas}" ]; then
  echo "   (no user schemas yet — skipping)"
else
  for s in ${schemas}; do
    echo "   - alembic upgrade head [schema=${s}]"
    $COMPOSE run --rm mcp-server alembic -x schema="${s}" upgrade head
  done
fi

echo ">> Starting all services"
$COMPOSE up -d --no-build --remove-orphans

echo ">> Health check"
sleep 5
$COMPOSE ps
if curl -fsS http://localhost:8002/ok >/dev/null; then
  echo "   agent /ok OK"
else
  echo "   agent health FAILED" >&2
  exit 1
fi

echo ">> Deploy done @ tag=${ENVEL_TAG}"
