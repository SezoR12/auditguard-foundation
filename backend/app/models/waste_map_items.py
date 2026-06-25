import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Numeric, ForeignKey, Enum as SAEnum, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from ..db import Base

class WasteCategory(str, enum.Enum):
    financial = "financial"
    operational = "operational"
    human = "human"
    opportunity = "opportunity"

class WasteMapItem(Base):
    __tablename__ = "waste_map_items"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[WasteCategory] = mapped_column(SAEnum(WasteCategory, name="waste_category"), nullable=False)
    amount_iqd: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    department: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(64), default="open", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())