import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Float, ForeignKey, Enum as SAEnum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from ..db import Base

class FileType(str, enum.Enum):
    excel = "excel"
    csv = "csv"
    word = "word"
    image = "image"
    pdf = "pdf"
    encrypted_json = "encrypted_json"

class DocCategory(str, enum.Enum):
    invoice = "invoice"
    contract = "contract"
    report = "report"
    receipt = "receipt"
    bank_statement = "bank_statement"
    inventory_report = "inventory_report"
    encrypted_report = "encrypted_report"
    other = "other"

class DocStatus(str, enum.Enum):
    pending = "pending"
    ocr_processing = "ocr_processing"
    certified = "certified"

class OcrStatus(str, enum.Enum):
    not_started = "not_started"
    running = "running"
    done = "done"
    failed = "failed"

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    file_type: Mapped[FileType] = mapped_column(SAEnum(FileType, name="file_type"), nullable=False)
    doc_category: Mapped[DocCategory] = mapped_column(SAEnum(DocCategory, name="doc_category"), nullable=False, default=DocCategory.other)
    status: Mapped[DocStatus] = mapped_column(SAEnum(DocStatus, name="doc_status"), nullable=False, default=DocStatus.pending)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    branch_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("branches.id", ondelete="SET NULL"))
    ocr_status: Mapped[OcrStatus] = mapped_column(SAEnum(OcrStatus, name="ocr_status"), nullable=False, default=OcrStatus.not_started)
    confidence_score: Mapped[float | None] = mapped_column(Float)
    extracted_data: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())