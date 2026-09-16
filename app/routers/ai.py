from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.services import llm_service
from app.schemas.chat import ChatRequest, ChatResponse, EmbedRequest, EmbedResponse
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest, user=Depends(get_current_user)):
    return {"response": llm_service.chat_completion(body.message)}

@router.post("/chat/stream")
async def chat_stream(body: ChatRequest, user=Depends(get_current_user)):
    return StreamingResponse(llm_service.stream_chat_completion(body.message), media_type="text/event-stream")

@router.post("/embed", response_model=EmbedResponse)
def embed(body: EmbedRequest, user=Depends(get_current_user)):
    return {"embedding": llm_service.get_embedding(body.text)}

@router.post("/function-call", response_model=ChatResponse)
def function_call(body: ChatRequest, user=Depends(get_current_user)):
    return {"response": llm_service.chat_with_tools(body.message)}