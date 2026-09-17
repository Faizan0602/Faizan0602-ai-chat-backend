from pydantic import BaseModel
from datetime import datetime

class ConversationCreate(BaseModel):
    title: str | None = None

class ConversationOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str

class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    class Config:
        from_attributes = True