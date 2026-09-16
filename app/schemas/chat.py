from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class EmbedRequest(BaseModel):
    text: str

class EmbedResponse(BaseModel):
    embedding: list[float]