from fastapi import APIRouter, Depends, HTTPException
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/rag", tags=["RAG"])

@router.post("/rag/query", response_model=RAGQueryResponse)
def rag_query(body: RAGQueryRequest, user=Depends(get_current_user)):
    raise HTTPException(501, "Not implemented yet — built in Phase 4")