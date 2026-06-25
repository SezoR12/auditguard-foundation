from pydantic import BaseModel, EmailStr
from uuid import UUID
from ..models.user import UserRole

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshIn(BaseModel):
    refresh_token: str

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: UserRole
    company_id: UUID
    branch_id: UUID | None = None
    is_active: bool

    class Config:
        from_attributes = True