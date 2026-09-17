
from pydantic import BaseModel
class RAGQueryRequest(BaseModel):
    query: str
    document_ids: list[int] | None = None   # optionally scope to specific uploaded docs

class RAGSource(BaseModel):
    document_id: int
    filename: str
    chunk_text: str

class RAGQueryResponse(BaseModel):
    answer: str
    sources: list[RAGSource]
    
    
