from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from ..models.document import FileType, DocCategory, DocStatus, OcrStatus

class DocumentOut(BaseModel):
    id: UUID
    file_path: str
    original_filename: str
    file_type: FileType
    doc_category: DocCategory
    status: DocStatus
    uploaded_by: UUID | None = None
    company_id: UUID
    branch_id: UUID | None = None
    ocr_status: OcrStatus
    confidence_score: float | None = None
    extracted_data: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True
