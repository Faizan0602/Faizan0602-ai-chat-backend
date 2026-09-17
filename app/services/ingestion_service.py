import json
from pypdf import PdfReader
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.llm_service import get_embedding

CHUNK_SIZE = 500       # characters per chunk
CHUNK_OVERLAP = 50     # overlap between chunks, so context isn't cut mid-thought

def extract_text(file_path: str, file_type: str) -> str:
    if file_type == "application/pdf":
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif file_type == "text/plain":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def chunk_text(text: str) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c for c in chunks if c.strip()]

def process_document(document_id: int, file_path: str, file_type: str):
    db: Session = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return

        doc.status = "processing"
        db.commit()

        text = extract_text(file_path, file_type)
        if not text.strip():
            doc.status = "failed"
            db.commit()
            return

        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            db_chunk = DocumentChunk(
                document_id=doc.id,
                chunk_index=i,
                chunk_text=chunk,
                embedding=json.dumps(embedding),
            )
            db.add(db_chunk)

        doc.status = "ready"
        db.commit()
    except Exception:
        doc.status = "failed"
        db.commit()
    finally:
        db.close()