#!/usr/bin/env bash
# Runs Alembic migrations against the target environment's database.
# DATABASE_URL is injected as a masked/protected CI/CD variable per environment.
set -euo pipefail

echo ">> Running database migrations against ${ENVIRONMENT:-unknown}"
alembic upgrade head
echo ">> Migrations complete"
