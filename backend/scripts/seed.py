import asyncio
from sqlalchemy import select
from app.db import SessionLocal
from app.models import Company, Branch, User, UserRole
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

        for email, pw, name, role in USERS:
            s.add(User(
                email=email,
                hashed_password=hash_password(pw),
                full_name=name,
                role=role,
                company_id=company.id,
                branch_id=branch.id,
                is_active=True,
            ))
        await s.commit()
        print("Seed: created company, branch, and 4 users.")


if __name__ == "__main__":
    asyncio.run(main())