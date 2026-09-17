from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.services import llm_service
from app.schemas.chat import ChatRequest, ChatResponse, EmbedRequest, EmbedResponse
from app.core.dependencies import get_current_user
from app.core.limiter import limiter

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
def chat(request: Request, body: ChatRequest, user=Depends(get_current_user)):
    return {"response": llm_service.chat_completion(body.message)}

@router.post("/chat/stream")
@limiter.limit("10/minute")
async def chat_stream(request: Request, body: ChatRequest, user=Depends(get_current_user)):
    return StreamingResponse(llm_service.stream_chat_completion(body.message), media_type="text/event-stream")

@router.post("/embed", response_model=EmbedResponse)
@limiter.limit("20/minute")
def embed(request: Request, body: EmbedRequest, user=Depends(get_current_user)):
    return {"embedding": llm_service.get_embedding(body.text)}

@router.post("/function-call", response_model=ChatResponse)
@limiter.limit("10/minute")
def function_call(request: Request, body: ChatRequest, user=Depends(get_current_user)):
    return {"response": llm_service.chat_with_tools(body.message)}