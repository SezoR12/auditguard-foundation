#!/usr/bin/env bash
set -euo pipefail

say() { printf "\033[1;36m[setup]\033[0m %s\n" "$*"; }
err() { printf "\033[1;31m[error]\033[0m %s\n" "$*" >&2; }

command -v docker >/dev/null 2>&1 || { err "Docker is not installed."; exit 1; }
docker compose version >/dev/null 2>&1 || { err "Docker Compose v2 is required."; exit 1; }

if [ ! -f .env ]; then
  say "Generating .env with random secrets..."
  POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -d '=+/' | cut -c1-24)
  SECRET_KEY=$(openssl rand -hex 32)
  JWT_SECRET=$(openssl rand -hex 32)
  ENCRYPTION_MASTER_KEY=$(openssl rand -hex 32)
  cat > .env <<EOF
POSTGRES_DB=auditcore
POSTGRES_USER=auditcore
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
SECRET_KEY=${SECRET_KEY}
JWT_SECRET=${JWT_SECRET}
ENCRYPTION_MASTER_KEY=${ENCRYPTION_MASTER_KEY}
EOF
else
  say ".env already exists, leaving as-is."
fi

say "Ensuring data upload directory exists with proper permissions..."
mkdir -p data/uploads
chmod -R 777 data

say "Building and starting containers..."
docker compose up -d --build

say "Waiting for Postgres to be healthy..."
for i in $(seq 1 60); do
  if docker compose ps postgres | grep -q "(healthy)"; then break; fi
  sleep 2
done

say "Running Alembic migrations..."
docker compose exec -T backend alembic upgrade head

say "Seeding database..."
docker compose exec -T backend python scripts/seed.py

say "Verifying that all containers are up and running..."
docker compose ps
for service in postgres redis backend frontend baileys-bridge; do
  if ! docker compose ps "$service" | grep -q "Up"; then
    err "Container for service '$service' failed to come up or exited."
    exit 1
  fi
done
say "All containers verified successfully!"

say "Running automated RBAC verification check (Auditor -> /owner 403 Arabic check)..."
docker compose exec -T backend python scripts/verify_rbac.py

cat <<MSG

AuditCore is up and fully verified!

Frontend: http://localhost:5173
Backend:  http://localhost:8000  (docs: /docs)

Login credentials:
  Owner   -> owner@auditcore.local   / Owner123!
  Auditor -> auditor@auditcore.local / Auditor123!
  Manager -> manager@auditcore.local / Manager123!
  GM      -> gm@auditcore.local      / Gm123!

MSG
