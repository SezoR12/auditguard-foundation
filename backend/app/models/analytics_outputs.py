import uuid
import enum
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, Enum as SAEnum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from ..db import Base

class OutputType(str, enum.Enum):
    trust_index = "trust_index"
    forecast = "forecast"
    summary = "summary"
    other = "other"

class AnalyticsOutput(Base):
    __tablename__ = "analytics_outputs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    output_type: Mapped[OutputType] = mapped_column(SAEnum(OutputType, name="analytics_output_type"), nullable=False)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    trust_index: Mapped[int | None] = mapped_column(Integer)