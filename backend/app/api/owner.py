from fastapi import APIRouter, Depends
from ..deps import require_role
from ..models.user import User

router = APIRouter(prefix="/owner", tags=["owner"])

@router.get("/ping")
async def owner_ping(user: User = Depends(require_role("owner"))):
    return {"ok": True, "user": user.email}