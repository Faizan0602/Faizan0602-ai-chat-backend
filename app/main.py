from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth, ai, chat, system
from app.routers.system import REQUEST_COUNT
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Chat Backend")


    
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://frontend-psi-three-kw4r0bg8r2.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# rate limiter setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# request counting middleware
@app.middleware("http")
async def count_requests(request, call_next):
    REQUEST_COUNT["total"] += 1
    return await call_next(request)

# routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
# app.include_router(rag.router, prefix="/api/v1")
# app.include_router(documents.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(system.router)   # unversioned - /health and /metrics