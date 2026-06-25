"""enable RLS on hidden tables

Revision ID: 002_enable_rls
Revises: 001_initial
Create Date: 2026-06-25
"""
from alembic import op
import sqlalchemy as sa

revision = "002_enable_rls"
down_revision = "001_initial"
branch_labels = None
depends_on = None

HIDDEN = ["analytics_outputs", "waste_map_items", "risk_alerts"]
POLICIES = {
    "analytics_outputs": "auditor_no_access_analytics",
    "waste_map_items": "auditor_no_access_waste",
    "risk_alerts": "auditor_no_access_risk",
}


def upgrade():
    op.execute("""
        CREATE OR REPLACE FUNCTION set_user_role(role text) RETURNS void
        LANGUAGE plpgsql AS $$
        BEGIN
            PERFORM set_config('app.current_user_role', role, false);
        END;
        $$;
    """)

    for t in HIDDEN:
        op.execute(f"ALTER TABLE {t} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {t} FORCE ROW LEVEL SECURITY")
        policy = POLICIES[t]
        op.execute(f"""
            CREATE POLICY {policy} ON {t}
            FOR ALL
            USING (current_setting('app.current_user_role', true) != 'auditor')
            WITH CHECK (current_setting('app.current_user_role', true) != 'auditor')
        """)

    # Verification: insert a row bypassing RLS (superuser session here ignores FORCE? No: FORCE applies to table owners too.)
    # We need to insert as a role exempt from RLS. Use SET LOCAL role to a temp superuser-ish path: use SECURITY DEFINER trick.
    op.execute("""
        DO $$
        DECLARE
            cid uuid;
            cnt_auditor int;
            cnt_owner int;
        BEGIN
            -- Insert a company and a hidden row with RLS temporarily disabled
            ALTER TABLE companies DISABLE ROW LEVEL SECURITY;
            ALTER TABLE analytics_outputs DISABLE ROW LEVEL SECURITY;
            INSERT INTO companies (name, sector, tier) VALUES ('__rls_probe__', 'test', 'essential') RETURNING id INTO cid;
            INSERT INTO analytics_outputs (company_id, output_type, data, trust_index)
              VALUES (cid, 'trust_index', '{}'::jsonb, 50);
            ALTER TABLE analytics_outputs ENABLE ROW LEVEL SECURITY;

            PERFORM set_user_role('auditor');
            SELECT count(*) INTO cnt_auditor FROM analytics_outputs;
            PERFORM set_user_role('owner');
            SELECT count(*) INTO cnt_owner FROM analytics_outputs;

            IF cnt_auditor <> 0 THEN
                RAISE EXCEPTION 'RLS verification failed: auditor saw % rows in analytics_outputs', cnt_auditor;
            END IF;
            IF cnt_owner < 1 THEN
                RAISE EXCEPTION 'RLS verification failed: owner saw % rows in analytics_outputs', cnt_owner;
            END IF;

            -- Cleanup probe
            ALTER TABLE analytics_outputs DISABLE ROW LEVEL SECURITY;
            DELETE FROM analytics_outputs WHERE company_id = cid;
            DELETE FROM companies WHERE id = cid;
            ALTER TABLE analytics_outputs ENABLE ROW LEVEL SECURITY;
            ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
            ALTER TABLE companies DISABLE ROW LEVEL SECURITY;
        END $$;
    """)


def downgrade():
    for t, policy in POLICIES.items():
        op.execute(f"DROP POLICY IF EXISTS {policy} ON {t}")
        op.execute(f"ALTER TABLE {t} DISABLE ROW LEVEL SECURITY")
    op.execute("DROP FUNCTION IF EXISTS set_user_role(text)")