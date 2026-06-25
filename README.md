# AuditCore — Foundation & Phase 2 Ingestion Pipeline

On-premise audit intelligence platform. Phase 1 & 2 ship the Dockerized stack,
PostgreSQL schema with Row-Level Security (RLS), JWT auth, role-based access,
secure document upload pipeline with AES-256-GCM encryption at rest, malware scan
simulation via MIME type verification, and a fully Arabic/RTL React frontend.

## Stack

- **postgres** 15-alpine (internal only) — main DB, `pgcrypto` for UUIDs.
- **redis** 7-alpine (internal only) — reserved for Celery in a later phase.
- **backend** — FastAPI (Python 3.11), SQLAlchemy 2.0 async, asyncpg, Alembic, cryptography, python-magic.
- **frontend** — React 18 + Vite + TypeScript + TailwindCSS + react-dropzone, fully RTL.
- **baileys-bridge** — Node 20 placeholder for WhatsApp Web (later phase).

## Quick start

```bash
chmod +x setup.sh
./setup.sh
```

`setup.sh` checks Docker, generates a `.env` with random secrets (`ENCRYPTION_MASTER_KEY`, `SECRET_KEY`, etc.), builds the
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
- `POST /documents/upload` — secure document upload with AES-256-GCM encryption & MIME validation.
- `GET  /documents/my-uploads` — documents uploaded by current auditor.
- `GET  /documents/pending-certification` — documents pending certification for auditor's company.
- `GET  /documents/company-documents` — entire company document listing (Owner/GM/Manager).

All error responses set `detail` in Arabic.

## Secure Ingestion & Encryption at Rest

- All uploaded documents are validated against allowed extensions and MIME types (`python-magic`). Mismatches (e.g. `.exe` renamed to `.pdf`) are rejected immediately.
- Files are saved to `/data/uploads/company_{id}/{year}/{month}/{uuid}_{filename}`.
- Non-JSON files are encrypted at rest using **AES-256-GCM**. Keys are derived dynamically using `ENCRYPTION_MASTER_KEY` + `company_id` + `file_uuid`. Keys are **never** stored in the database.
- `.json` files flagged as `encrypted_json` or `encrypted_report` are validated against their required schema (`metadata`, `encrypted_payload`) and stored as-is for downstream AI decryption.

## Frontend

- `<html dir="rtl" lang="ar">` and Tajawal font by default.
- `/login` → role-based redirect: owner → `/owner`, auditor → `/auditor`,
  manager → `/manager`, gm → `/gm`. Each role page shows `مرحباً {full_name}`.
- Auditor dashboard contains a drag-and-drop interface (`react-dropzone`) with progress bars and listing tables.
- Owner dashboard provides an overarching view of all uploaded company documents.
- JWT stored in `localStorage` and attached via an axios interceptor.

## Out of scope in Phase 2

OCR processing engine, AI decryption engine, audit task workflows, analytics generation, Celery
workers, and the real Baileys/WhatsApp bridge.
