import uuid
from datetime import datetime
from sqlalchemy import String, Enum as SAEnum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import enum
from ..db import Base

class CompanyTier(str, enum.Enum):
    essential = "essential"
    advanced = "advanced"
    elite = "elite"

class Company(Base):
    __tablename__ = "companies"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sector: Mapped[str] = mapped_column(String(120), nullable=False)
    tier: Mapped[CompanyTier] = mapped_column(SAEnum(CompanyTier, name="company_tier"), nullable=False, default=CompanyTier.essential)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())