
from pydantic import BaseModel
class DocumentOut(BaseModel):
    id: int
    filename: str
    file_type: str
    size_bytes: int
    status: str
    class Config:
        from_attributes = True