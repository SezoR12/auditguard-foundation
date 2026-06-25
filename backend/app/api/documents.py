import os
import uuid
import json
import hashlib
import aiofiles
import magic
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ..db import get_session
from ..models.user import User
from ..models.document import Document, FileType, DocCategory, DocStatus
from ..schemas.document import DocumentOut
from ..deps import get_current_user, require_role
from ..config import settings

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

ALLOWED_MIMES = {
    ".xlsx": ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/octet-stream", "application/zip"],
    ".csv": ["text/csv", "text/plain"],
    ".docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/octet-stream", "application/zip"],
    ".jpg": ["image/jpeg"],
    ".jpeg": ["image/jpeg"],
    ".png": ["image/png"],
    ".tiff": ["image/tiff"],
    ".pdf": ["application/pdf"],
    ".json": ["application/json", "text/plain"]
}

def derive_key(company_id: str, file_uuid: str) -> bytes:
    key_material = f"{settings.ENCRYPTION_MASTER_KEY}:{company_id}:{file_uuid}".encode("utf-8")
    return hashlib.sha256(key_material).digest()

def encrypt_data(key: bytes, plaintext: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ciphertext

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_category: str = Form(...),
    branch_id: str | None = Form(None),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="حجم الملف يتجاوز الحد المسموح به (50 ميغابايت)")

    filename = file.filename or "untitled"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_MIMES:
        raise HTTPException(status_code=400, detail="امتداد الملف غير مدعوم")

    # Virus scan simulation via MIME type matching
    mime_type = magic.from_buffer(content[:2048], mime=True)
    if not any(mime_type.startswith(allowed) or allowed in mime_type for allowed in ALLOWED_MIMES[ext]):
        raise HTTPException(status_code=400, detail="نوع الملف ومحتواه غير متطابقين (اشتباه بوجود برمجيات خبيثة)")

    try:
        category_enum = DocCategory(doc_category)
    except ValueError:
        category_enum = DocCategory.other

    file_uuid = uuid.uuid4()
    now = datetime.now()
    year_str = now.strftime("%Y")
    month_str = now.strftime("%m")
    company_id_str = str(user.company_id)
    
    # Target directory: /data/uploads/company_{id}/{year}/{month}
    dir_path = f"/data/uploads/company_{company_id_str}/{year_str}/{month_str}"
    os.makedirs(dir_path, exist_ok=True)
    
    safe_filename = filename.replace("/", "_").replace("\\", "_")
    file_path = f"{dir_path}/{file_uuid}_{safe_filename}"

    # Encrypted JSON Special Pipeline
    if ext == ".json" and (category_enum == DocCategory.encrypted_report or doc_category == "encrypted_json" or category_enum == DocCategory.other):
        try:
            data_json = json.loads(content.decode("utf-8"))
            if not isinstance(data_json, dict) or "metadata" not in data_json or "encrypted_payload" not in data_json:
                raise HTTPException(status_code=400, detail="بنية ملف JSON المشفر غير صالحة")
        except Exception:
            raise HTTPException(status_code=400, detail="بنية ملف JSON المشفر غير صالحة")
        
        file_type = FileType.encrypted_json
        data_to_write = content
    else:
        if ext == ".xlsx": file_type = FileType.excel
        elif ext == ".csv": file_type = FileType.csv
        elif ext == ".docx": file_type = FileType.word
        elif ext in (".jpg", ".jpeg", ".png", ".tiff"): file_type = FileType.image
        elif ext == ".pdf": file_type = FileType.pdf
        elif ext == ".json": file_type = FileType.encrypted_json
        else: file_type = FileType.word

        # Encrypt file at rest using AES-256-GCM
        key = derive_key(company_id_str, str(file_uuid))
        data_to_write = encrypt_data(key, content)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(data_to_write)

    branch_uuid = None
    if branch_id and branch_id.strip():
        try:
            branch_uuid = uuid.UUID(branch_id.strip())
        except ValueError:
            branch_uuid = None
    else:
        branch_uuid = user.branch_id

    doc = Document(
        id=file_uuid,
        file_path=file_path,
        original_filename=filename,
        file_type=file_type,
        doc_category=category_enum,
        status=DocStatus.pending,
        uploaded_by=user.id,
        company_id=user.company_id,
        branch_id=branch_uuid,
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)

    return {"document_id": str(doc.id), "status": doc.status.value, "message": "تم الرفع بنجاح"}

@router.get("/my-uploads", response_model=list[DocumentOut])
async def get_my_uploads(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    stmt = select(Document).where(Document.uploaded_by == user.id).order_by(Document.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/pending-certification", response_model=list[DocumentOut])
async def get_pending_certification(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    stmt = select(Document).where(
        Document.company_id == user.company_id,
        Document.status.in_([DocStatus.pending, DocStatus.ocr_processing])
    ).order_by(Document.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()

@router.get("/company-documents", response_model=list[DocumentOut])
async def get_company_documents(user: User = Depends(require_role("owner", "gm", "manager")), session: AsyncSession = Depends(get_session)):
    stmt = select(Document).where(Document.company_id == user.company_id).order_by(Document.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()
