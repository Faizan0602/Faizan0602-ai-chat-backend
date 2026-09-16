from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth, ai

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Chat Backend")
app.include_router(auth.router)
app.include_router(ai.router)