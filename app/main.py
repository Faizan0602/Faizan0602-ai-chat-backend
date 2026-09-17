from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth, ai
from app.routers import auth, ai, rag, documents,chat


Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Chat Backend")
app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(rag.router)
app.include_router(documents.router)
app.include_router(chat.router)