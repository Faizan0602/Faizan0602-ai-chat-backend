from fastapi import APIRouter, Depends, HTTPException
import json

from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat_history import ConversationCreate, ConversationOut, MessageCreate, MessageOut
from app.services import llm_service

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/conversations", response_model=ConversationOut)
def create_conversation(body: ConversationCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    convo = Conversation(user_id=user.id, title=body.title or "New Conversation")
    db.add(convo); db.commit(); db.refresh(convo)
    return convo

@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )
    
@router.get("/conversations/{id}/messages", response_model=list[MessageOut])
def get_messages(id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    convo = db.query(Conversation).filter(Conversation.id == id, Conversation.user_id == user.id).first()
    if not convo:
        raise HTTPException(404, "Conversation not found")
    return convo.messages

@router.post("/conversations/{id}/messages")
async def send_message(id: int, body: MessageCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    convo = db.query(Conversation).filter(Conversation.id == id, Conversation.user_id == user.id).first()
    if not convo:
        raise HTTPException(404, "Conversation not found")

    # save the user's message first
    user_msg = Message(conversation_id=convo.id, role="user", content=body.content)
    db.add(user_msg); db.commit()

    # build full history for context
    history = [{"role": m.role, "content": m.content} for m in convo.messages]

    async def generate_and_save():
        full_reply = ""
        async for chunk in llm_service.stream_chat_completion_with_history(history):
            full_reply += chunk
            yield f"data: {json.dumps(chunk)}\n\n"
        # after streaming finishes, save the assistant's full reply
        assistant_msg = Message(conversation_id=convo.id, role="assistant", content=full_reply)
        db.add(assistant_msg)
        db.commit()
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_and_save(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@router.delete("/conversations/{id}")
def delete_conversation(id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    convo = db.query(Conversation).filter(Conversation.id == id, Conversation.user_id == user.id).first()
    if not convo:
        raise HTTPException(404, "Conversation not found")
    db.delete(convo); db.commit()
    return {"detail": "deleted"}