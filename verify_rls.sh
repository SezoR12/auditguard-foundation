#!/usr/bin/env bash
set -euo pipefail

echo "================================================================="
echo "       AuditCore RLS (Row-Level Security) Direct SQL Test       "
echo "================================================================="
echo

# Ensure containers are running
if ! docker compose ps postgres | grep -q "Up"; then
    echo "[error] PostgreSQL container is not running. Please run ./setup.sh first."
    exit 1
fi

echo "[1/4] Seeding test sample data into analytics_outputs (as superuser/owner)..."
docker compose exec -T postgres psql -U auditcore -d auditcore -c "
DO \$\$
DECLARE
    cid uuid;
BEGIN
    -- Ensure at least one company exists
    SELECT id INTO cid FROM companies LIMIT 1;
    IF cid IS NULL THEN
        INSERT INTO companies (name, sector, tier) VALUES ('شركة التقنية العراقية', 'تجارة', 'advanced') RETURNING id INTO cid;
    END IF;

    -- Insert sample analytics output if table is empty
    IF NOT EXISTS (SELECT 1 FROM analytics_outputs) THEN
        INSERT INTO analytics_outputs (company_id, output_type, data, trust_index) 
        VALUES (cid, 'trust_index', '{\"metrics\": \"highly_confidential\"}'::jsonb, 95);
    END IF;
END \$\$;
" > /dev/null

echo "[2/4] Running direct SQL SELECT on analytics_outputs as 'auditor' role..."
AUDITOR_COUNT=$(docker compose exec -T postgres psql -U auditcore -d auditcore -t -A -c "
    SELECT set_user_role('auditor');
    SELECT count(*) FROM analytics_outputs;
")

echo "--> Auditor row count result: ${AUDITOR_COUNT}"
if [ "${AUDITOR_COUNT}" -eq 0 ]; then
    echo "    [SUCCESS] Auditor is successfully blocked by RLS (0 rows returned)."
else
    echo "    [FAILURE] Auditor saw ${AUDITOR_COUNT} rows!"
    exit 1
fi
echo

echo "[3/4] Running direct SQL SELECT on analytics_outputs as 'owner' role..."
OWNER_COUNT=$(docker compose exec -T postgres psql -U auditcore -d auditcore -t -A -c "
    SELECT set_user_role('owner');
    SELECT count(*) FROM analytics_outputs;
")

echo "--> Owner row count result: ${OWNER_COUNT}"
if [ "${OWNER_COUNT}" -ge 1 ]; then
    echo "    [SUCCESS] Owner successfully accessed analytics_outputs (${OWNER_COUNT} rows returned)."
else
    echo "    [FAILURE] Owner saw 0 rows!"
    exit 1
fi
echo

echo "[4/4] Direct SQL Test Complete."
echo "================================================================="
echo " All RLS Acceptance Criteria Verified Successfully!              "
echo "================================================================="
