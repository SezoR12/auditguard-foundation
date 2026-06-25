# AuditCore — Phase 1 Foundation

On-premise audit intelligence platform. Phase 1 ships the Dockerized stack,
PostgreSQL schema with Row-Level Security (RLS), JWT auth, role-based access,
and a minimal Arabic/RTL React frontend.

## Stack

- **postgres** 15-alpine (internal only) — main DB, `pgcrypto` for UUIDs.
- **redis** 7-alpine (internal only) — reserved for Celery in a later phase.
- **backend** — FastAPI (Python 3.11), SQLAlchemy 2.0 async, asyncpg, Alembic.
- **frontend** — React 18 + Vite + TypeScript + TailwindCSS, fully RTL.
- **baileys-bridge** — Node 20 placeholder for WhatsApp Web (later phase).

## Quick start

```bash
chmod +x setup.sh
./setup.sh
```

`setup.sh` checks Docker, generates a `.env` with random secrets, builds the
stack, runs migrations, and seeds demo users.

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs

### Seed credentials

| Role    | Email                       | Password    |
| ------- | --------------------------- | ----------- |
| Owner   | owner@auditcore.local       | Owner123!   |
| Auditor | auditor@auditcore.local     | Auditor123! |
| Manager | manager@auditcore.local     | Manager123! |
| GM      | gm@auditcore.local          | Gm123!      |

## Row-Level Security

Three tables are hidden from the `auditor` role at the DB layer:
`analytics_outputs`, `waste_map_items`, `risk_alerts`. Each has RLS enabled
and FORCED, with a policy filtering on the session GUC
`app.current_user_role`. The helper function `set_user_role(text)` sets that
GUC, and every authenticated request calls it inside `get_current_user` so
the auditor role can never read or write these tables — even if application
code forgets to filter.

The migration `002_enable_rls.py` includes a self-verifying `DO $$ ... $$;`
block that fails the migration if an auditor can see rows.

### Manually verify

```bash
docker compose exec postgres psql -U auditcore -d auditcore -c \
  "SELECT set_user_role('auditor'); SELECT count(*) FROM analytics_outputs;"
# -> 0

docker compose exec postgres psql -U auditcore -d auditcore -c \
  "SELECT set_user_role('owner'); SELECT count(*) FROM analytics_outputs;"
# -> (any rows present)
```

## API

- `POST /auth/login` — OAuth2 password form (used by Swagger).
- `POST /auth/login-json` — JSON `{email, password}` (used by the frontend).
- `POST /auth/refresh` — refresh-token rotation.
- `GET  /auth/me` — current user.
- `GET  /owner/ping` — sample role-guarded endpoint; returns Arabic 403 for non-owners.

All error responses set `detail` in Arabic.

## Frontend

- `<html dir="rtl" lang="ar">` and Tajawal font by default.
- `/login` → role-based redirect: owner → `/owner`, auditor → `/auditor`,
  manager → `/manager`, gm → `/gm`. Each role page shows `مرحباً {full_name}`.
- JWT stored in `localStorage` and attached via an axios interceptor.

## Out of scope in Phase 1

Document upload/OCR, audit task workflows, analytics generation, Celery
workers, and the real Baileys/WhatsApp bridge.
