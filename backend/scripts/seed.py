import asyncio
from decimal import Decimal
from sqlalchemy import select
from app.db import SessionLocal
from app.models import (
    Company, Branch, User, UserRole, AuditTask, TaskType, TaskStatus,
    AnalyticsOutput, OutputType, WasteMapItem, WasteCategory, RiskAlert, RiskSeverity
)
from app.models.company import CompanyTier
from app.security import hash_password

USERS = [
    ("owner@auditcore.local", "Owner123!", "المالك", UserRole.owner),
    ("auditor@auditcore.local", "Auditor123!", "المدقق", UserRole.auditor),
    ("manager@auditcore.local", "Manager123!", "المدير", UserRole.manager),
    ("gm@auditcore.local", "Gm123!", "المدير العام", UserRole.gm),
]

async def main():
    async with SessionLocal() as s:
        # Idempotent: skip if owner exists
        existing = (await s.execute(select(User).where(User.email == "owner@auditcore.local"))).scalar_one_or_none()
        if existing:
            print("Seed: already present, skipping.")
            return

        company = Company(name="شركة التقنية العراقية", sector="تجارة", tier=CompanyTier.advanced)
        s.add(company)
        await s.flush()

        branch = Branch(company_id=company.id, name="الرئيسي - بغداد", location="بغداد")
        s.add(branch)
        await s.flush()

        users_dict = {}
        for email, pw, name, role in USERS:
            u = User(
                email=email,
                hashed_password=hash_password(pw),
                full_name=name,
                role=role,
                company_id=company.id,
                branch_id=branch.id,
                is_active=True,
            )
            s.add(u)
            users_dict[role] = u
        await s.flush()

        # Seed real Audit Tasks for Auditor
        auditor_user = users_dict[UserRole.auditor]
        s.add(AuditTask(
            auditor_id=auditor_user.id,
            title="تدقيق الفواتير الشهرية للفرع الرئيسي",
            task_type=TaskType.monthly,
            status=TaskStatus.in_progress,
            demerit_points=0
        ))
        s.add(AuditTask(
            auditor_id=auditor_user.id,
            title="مراجعة كشوفات الحسابات البنكية ومطابقتها",
            task_type=TaskType.weekly,
            status=TaskStatus.pending,
            demerit_points=0
        ))

        # Seed real Analytics Outputs (hidden from auditor)
        s.add(AnalyticsOutput(
            company_id=company.id,
            output_type=OutputType.trust_index,
            data={"score": 94, "trend": "positive", "details": "مؤشر الثقة المالي والإداري مستقر وممتاز."},
            trust_index=94
        ))
        s.add(AnalyticsOutput(
            company_id=company.id,
            output_type=OutputType.summary,
            data={"cash_flow_health": "Optimal", "anomaly_detection_rate": "0.02%"},
            trust_index=90
        ))

        # Seed real Waste Map Items (hidden from auditor)
        s.add(WasteMapItem(
            company_id=company.id,
            category=WasteCategory.financial,
            amount_iqd=Decimal("2500000.00"),
            department="قسم المشتريات",
            description="فروقات في تسعير المواد الأولية مقارنة بالسوق المحلي.",
            status="open"
        ))
        s.add(WasteMapItem(
            company_id=company.id,
            category=WasteCategory.operational,
            amount_iqd=Decimal("1200000.00"),
            department="إدارة المخازن",
            description="تكدس المخزون وبطء دورة التوريد في الفرع الرئيسي.",
            status="under_review"
        ))

        # Seed real Risk Alerts (hidden from auditor)
        s.add(RiskAlert(
            company_id=company.id,
            severity=RiskSeverity.high,
            title="ثغرة في توثيق سندات الصرف",
            description="تم اكتشاف غياب التواقيع المعتمدة على 5 سندات صرف في قسم الحسابات.",
            financial_impact=Decimal("4500000.00"),
            status="investigating"
        ))
        s.add(RiskAlert(
            company_id=company.id,
            severity=RiskSeverity.medium,
            title="تأخر في مطابقة الحسابات الختامية",
            description="تأخر قسم المالي في إغلاق الحسابات الشهرية بمقدار 5 أيام.",
            financial_impact=Decimal("1000000.00"),
            status="open"
        ))

        await s.commit()
        print("Seed: created company, branch, 4 users, audit tasks, analytics, waste map items, and risk alerts.")

if __name__ == "__main__":
    asyncio.run(main())
