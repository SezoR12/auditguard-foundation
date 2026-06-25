
# AuditCore Phase 1 — Foundation

This builds a standalone dockerized stack at the repo root. The existing TanStack Start template files are unrelated to this deliverable and will be left in place but not used; the new app lives under `backend/`, `frontend/`, and `baileys-bridge/` with its own `docker-compose.yml` and `setup.sh`. If you'd rather I delete the template files, say the word.

## Repo layout

```text
.
├── docker-compose.yml
├── setup.sh
├── README.md
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       ├── 001_initial.py
│   │       └── 002_enable_rls.py
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── security.py
│   │   ├── deps.py
│   │   ├── models/        # company, branch, user, audit_task,
│   │   │                  # document, document_certification,
│   │   │                  # audit_ledger, analytics_outputs,
│   │   │                  # waste_map_items, risk_alerts
│   │   ├── schemas/       # pydantic auth schemas
│   │   └── api/auth.py
│   └── scripts/seed.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css
│       ├── api.ts
│       ├── auth.tsx          # context + ProtectedRoute
│       └── pages/
│           ├── Login.tsx
│           ├── Owner.tsx
│           ├── Auditor.tsx
│           ├── Manager.tsx
│           └── GM.tsx
└── baileys-bridge/
    ├── Dockerfile
    └── package.json          # placeholder
```

## Services (docker-compose)

- `postgres` — `postgres:15-alpine`, named volume `postgres_data`, port not published (internal only).
- `redis` — `redis:7-alpine`, internal only.
- `backend` — FastAPI/uvicorn `--reload`, mounts `./backend`, exposes 8000.
- `frontend` — Vite dev server, mounts `./frontend`, exposes 5173, proxies `/api` → backend.
- `baileys-bridge` — Node 20 alpine, placeholder `index.js` that just `console.log`s and sleeps.

## Database & RLS

SQLAlchemy 2.0 async (asyncpg). Enums via PG enum types. UUID PKs via `gen_random_uuid()` (enable `pgcrypto`).

`002_enable_rls.py`:
- `CREATE OR REPLACE FUNCTION set_user_role(role text) ...` sets `app.current_user_role` for the session.
- `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` + `FORCE ROW LEVEL SECURITY` on the three hidden tables.
- Three `USING (current_setting('app.current_user_role', true) <> 'auditor')` policies.
- Verification block: `SELECT set_user_role('auditor')` then `INSERT` a dummy row as superuser bypassed, then in a non-superuser context confirm `SELECT count(*) FROM analytics_outputs = 0`. (App user must be non-superuser; we create `auditcore_app` role granted on tables, used as DB user.)

`get_current_user` calls `await conn.execute(text("SELECT set_user_role(:r)"), {"r": role})` on each request's session before any query.

## Auth

- `python-jose` HS256, 30-min access, 7-day refresh (rotation: refresh endpoint issues new pair, old refresh's `jti` tracked in-memory dict for Phase 1 — flagged as TODO for Redis later).
- `passlib[bcrypt]` for hashing.
- `require_role(*roles)` raises `HTTPException(403, detail="ليس لديك صلاحية الوصول إلى هذا المورد")`.
- Login error: `"البريد الإلكتروني أو كلمة المرور غير صحيحة"`.

## Frontend

- React 18 + Vite + TS + Tailwind. `index.html` has `<html dir="rtl" lang="ar">`.
- Tailwind config with default font stack including a system Arabic fallback.
- `AuthContext` stores JWT in `localStorage` (httpOnly cookies need backend cookie auth — out of scope here; localStorage flagged as the chosen tradeoff in README).
- `axios` instance attaches `Authorization: Bearer`.
- `ProtectedRoute` redirects unauthenticated to `/login`; role pages show `مرحباً {full_name}` plus role-specific heading.

## Seed

`scripts/seed.py` runs against the async engine, idempotent (skip if owner email exists), creates company/branch and the four users with the specified bcrypt-hashed passwords.

## setup.sh

Bash: checks `docker` + `docker compose`, writes `.env` (only if missing) with `openssl rand -hex 32` for SECRET_KEY/JWT_SECRET and `openssl rand -base64 24` for POSTGRES_PASSWORD, `docker compose up -d --build`, waits for Postgres healthcheck, runs `alembic upgrade head`, runs `seed.py`, prints the four credentials and URLs.

## Acceptance check mapping

- Containers come up via `setup.sh`.
- `/auth/login` + role-based redirect verified by Login → role page.
- RLS verified inside migration (raises if hidden tables visible as auditor).
- `require_role` returns Arabic 403 for cross-role access (no `/owner` endpoint is added yet beyond `/auth/me`; I will add a stub `GET /api/owner/ping` guarded by `require_role("owner")` so the acceptance test is exercisable).

## Out of scope (Phase 1)

No real Baileys/WhatsApp logic, no Celery worker yet (Redis is up but unused), no document upload endpoints, no analytics generation. The hidden tables exist empty so RLS is testable.
