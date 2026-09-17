from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth, ai, rag, documents, chat, system
from app.routers.system import REQUEST_COUNT
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Chat Backend")

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
app.include_router(rag.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(system.router)   # unversioned - /health and /metrics