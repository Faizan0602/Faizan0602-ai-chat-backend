# app/routers/documents.py
import os
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.models.document import Document
from app.schemas.document import DocumentOut

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_TYPES = {"application/pdf", "text/plain"}
MAX_SIZE = 10 * 1024 * 1024  # 10 MB
UPLOAD_DIR = "uploads"

@router.post("/upload", response_model=DocumentOut)
async def upload_document(file: UploadFile, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Unsupported file type: {file.content_type}")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(400, "File too large (max 10MB)")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    save_path = os.path.join(UPLOAD_DIR, f"{user.id}_{file.filename}")
    with open(save_path, "wb") as f:
        f.write(contents)

    doc = Document(
        user_id=user.id,
        filename=file.filename,
        file_type=file.content_type,
        size_bytes=len(contents),
        status="uploaded",
    )
    db.add(doc); db.commit(); db.refresh(doc)
    return doc

@router.get("", response_model=list[DocumentOut])
def list_documents(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.user_id == user.id).all()

@router.get("/{doc_id}/status", response_model=DocumentOut)
def get_status(doc_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == user.id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc

@router.delete("/{doc_id}")
def delete_document(doc_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == user.id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    db.delete(doc); db.commit()
    return {"detail": "deleted"}