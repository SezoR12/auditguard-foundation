from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..db import get_session
from ..models.user import User
from ..models.company import Company
from ..models.branch import Branch
from ..models.audit_task import AuditTask
from ..models.document import Document, DocStatus
from ..models.analytics_outputs import AnalyticsOutput
from ..models.waste_map_items import WasteMapItem
from ..models.risk_alerts import RiskAlert
from ..deps import get_current_user, require_role

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/owner")
async def get_owner_dashboard(user: User = Depends(require_role("owner", "gm", "manager")), session: AsyncSession = Depends(get_session)):
    # Fetch real company data
    comp_res = await session.execute(select(Company).where(Company.id == user.company_id))
    company = comp_res.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="الشركة غير موجودة")

    # Fetch branches
    branches_res = await session.execute(select(Branch).where(Branch.company_id == user.company_id))
    branches = branches_res.scalars().all()

    # Users count
    users_cnt = await session.scalar(select(func.count()).select_from(User).where(User.company_id == user.company_id))

    # Real Analytics Outputs (RLS allows owner)
    analytics_res = await session.execute(select(AnalyticsOutput).where(AnalyticsOutput.company_id == user.company_id))
    analytics = analytics_res.scalars().all()

    # Real Waste Map Items
    waste_res = await session.execute(select(WasteMapItem).where(WasteMapItem.company_id == user.company_id))
    waste_items = waste_res.scalars().all()

    # Real Risk Alerts
    risk_res = await session.execute(select(RiskAlert).where(RiskAlert.company_id == user.company_id))
    risk_alerts = risk_res.scalars().all()

    # Recent Audit Tasks
    tasks_res = await session.execute(select(AuditTask).order_by(AuditTask.created_at.desc()).limit(5))
    tasks = tasks_res.scalars().all()

    return {
        "company": {
            "id": str(company.id),
            "name": company.name,
            "sector": company.sector,
            "tier": company.tier.value,
        },
        "branches": [{"id": str(b.id), "name": b.name, "location": b.location} for b in branches],
        "stats": {
            "total_users": users_cnt,
            "total_waste_iqd": sum(float(w.amount_iqd) for w in waste_items),
            "total_risk_impact_iqd": sum(float(r.financial_impact) for r in risk_alerts),
            "trust_index": analytics[0].trust_index if analytics and analytics[0].trust_index else 90,
        },
        "analytics": [{"id": str(a.id), "output_type": a.output_type.value, "data": a.data, "trust_index": a.trust_index} for a in analytics],
        "waste_items": [{"id": str(w.id), "category": w.category.value, "amount_iqd": float(w.amount_iqd), "department": w.department, "description": w.description, "status": w.status} for w in waste_items],
        "risk_alerts": [{"id": str(r.id), "severity": r.severity.value, "title": r.title, "description": r.description, "financial_impact": float(r.financial_impact), "status": r.status} for r in risk_alerts],
        "recent_tasks": [{"id": str(t.id), "title": t.title, "task_type": t.task_type.value, "status": t.status.value, "demerit_points": t.demerit_points} for t in tasks],
    }

@router.get("/auditor")
async def get_auditor_dashboard(user: User = Depends(require_role("auditor")), session: AsyncSession = Depends(get_session)):
    # Fetch real company data
    comp_res = await session.execute(select(Company).where(Company.id == user.company_id))
    company = comp_res.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="الشركة غير موجودة")

    # Fetch branches
    branches_res = await session.execute(select(Branch).where(Branch.company_id == user.company_id))
    branches = branches_res.scalars().all()

    # Auditor's assigned tasks
    tasks_res = await session.execute(select(AuditTask).where(AuditTask.auditor_id == user.id).order_by(AuditTask.created_at.desc()))
    tasks = tasks_res.scalars().all()

    # Uploads stats
    my_uploads_cnt = await session.scalar(select(func.count()).select_from(Document).where(Document.uploaded_by == user.id))
    pending_docs_cnt = await session.scalar(select(func.count()).select_from(Document).where(
        Document.company_id == user.company_id,
        Document.status.in_([DocStatus.pending, DocStatus.ocr_processing])
    ))

    return {
        "company": {
            "id": str(company.id),
            "name": company.name,
            "sector": company.sector,
            "tier": company.tier.value,
        },
        "branches": [{"id": str(b.id), "name": b.name, "location": b.location} for b in branches],
        "stats": {
            "assigned_tasks": len(tasks),
            "my_uploads": my_uploads_cnt,
            "pending_certification": pending_docs_cnt,
        },
        "tasks": [{"id": str(t.id), "title": t.title, "task_type": t.task_type.value, "status": t.status.value, "demerit_points": t.demerit_points} for t in tasks],
    }
