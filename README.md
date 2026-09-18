# 🤖 AI Chat Platform

A full-stack, production-grade AI chat application — built from the ground up with a versioned REST API, JWT authentication with refresh-token rotation, persistent multi-turn conversations, document ingestion with background processing, and a clean React frontend.

**Not a notebook demo. Not a LangChain tutorial clone.** This is an authenticated, deployed, real backend service that happens to be powered by an LLM — built the way AI features actually ship at product companies.

🔗 **Live Demo:** [https://frontend-psi-three-kw4r0bg8r2.vercel.app/](#)
📄 **API Docs:** [https://orbitchat-b3ku.onrender.com](#)

---

## 📸 Screenshots

| Login | Register |
|---|---|
| ![Login](./screenshots/Login.png) | ![Register](./screenshots/Register.png) |

| Chat Dashboard | Conversation View |
|---|---|
| ![Dashboard](./screenshots/Dashboard.png) | ![Chat](./screenshots/Chat.png) |


---

## ✨ Features

- 🔐 **Secure Authentication** — JWT access tokens + rotating refresh tokens with revocation on logout, password hashing via bcrypt
- 💬 **Persistent, Multi-Turn Chat** — conversations and message history stored per-user in PostgreSQL, with full context passed to the LLM on every turn
- ⚡ **Real Token Streaming** — responses stream back via Server-Sent Events (SSE), rendered live in the UI exactly like ChatGPT
- 🧠 **Function/Tool Calling** — the LLM can invoke real backend functions (e.g. calculations, live data) rather than guessing
- 🚦 **Rate Limiting** — protects upstream LLM API usage from abuse
- 📊 **Health & Metrics Endpoints** — `/health` and `/metrics` for observability
- 🧩 **Provider-Agnostic LLM Layer** — swap the underlying model provider via config, no route changes needed
- 🎨 **Modern React Frontend** — clean, responsive chat UI 

---

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│   React     │  HTTPS  │     FastAPI       │         │  PostgreSQL │
│  Frontend   │────────▶│  /api/v1/*        │────────▶│   (Neon)    │
│  (Vite)     │◀────SSE─│  routers          │         └─────────────┘
└─────────────┘         │                   │
                         │  ┌─────────────┐  │         ┌─────────────┐
                         │  │ LLM Service │──┼────────▶│  Groq API   │
                         │  │   Layer     │  │         └─────────────┘
                         │  └─────────────┘  │
                         └──────────────────┘
```

**Request flow for a chat message:**
`Client → JWT auth check → conversation lookup → history built from DB → LLM service (streamed) → response streamed to client → full reply persisted to DB`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI (Python) |
| Database | PostgreSQL (Neon) via SQLAlchemy ORM |
| Auth | JWT (access + refresh rotation), bcrypt password hashing |
| LLM Provider | Groq API (swappable via service layer) |
| Embeddings | `sentence-transformers` (local, MiniLM) |
| Frontend | React (Vite), React Router, Axios, Tailwind CSS |
| Rate Limiting | SlowAPI |
| Deployment | Render (backend), Vercel (frontend) |

---

## 📁 Project Structure

```
ai-chat-backend/
├── backend/
│   ├── app/
│   │   ├── core/          # config, security, JWT, dependencies, rate limiter
│   │   ├── models/         # SQLAlchemy models (User, Conversation, Message, Document, RefreshToken)
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── routers/        # auth, ai, chat, documents, rag, system
│   │   ├── services/       # llm_service.py, ingestion_service.py
│   │   └── main.py
│   └── requirements.txt
└── frontend/
    └── src/
        ├── pages/           # Login, Register, Chat
        └── api.js           # centralized Axios client
```

---

## 🚀 API Overview

All routes are versioned under `/api/v1`.

| Endpoint | Method | Description |
|---|---|---|
| `/auth/register` | POST | Create a new user |
| `/auth/login` | POST | Get access + refresh token pair |
| `/auth/refresh` | POST | Rotate refresh token, issue new access token |
| `/auth/logout` | POST | Revoke a refresh token |
| `/chat/conversations` | GET / POST | List / create conversations |
| `/chat/conversations/{id}/messages` | GET / POST | Fetch history / send message (streamed) |
| `/documents/upload` | POST | Upload a document for background ingestion |
| `/documents/{id}/status` | GET | Poll processing status |
| `/ai/chat` | POST | Stateless single-turn chat |
| `/ai/embed` | POST | Generate text embeddings |
| `/ai/function-call` | POST | LLM tool-calling demo |
| `/health` | GET | Liveness + DB connectivity check |
| `/metrics` | GET | Basic request metrics |

Full interactive docs available at `/docs` (Swagger UI) once running.

---

## ⚙️ Local Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:
```
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
GROQ_API_KEY=your-groq-api-key
```

Run it:
```bash
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`.

---

## 🎯 Design Decisions

- **Refresh token rotation over long-lived single tokens** — every refresh issues a new token and invalidates the old one, so a leaked/stolen refresh token can be detected via reuse rather than silently trusted until natural expiry.
- **Provider-agnostic LLM service layer** — all model calls are isolated in `llm_service.py`; swapping Groq for OpenAI or Anthropic means editing one file, not every route.
- **Background processing for uploads** — document ingestion (extraction, chunking, embeddings) runs after the HTTP response is sent, so users aren't blocked waiting on a multi-second pipeline for large files.
- **Deliberately deferred for this iteration:** Docker/Compose, Redis-backed caching, and Celery-based background workers. The current scope prioritized a working, deployed, authenticated API over infrastructure that doesn't yet have a scale problem to solve. These are the clear next additions if traffic or team size grows.

---

## 🗺️ Roadmap / What's Next

- [ ] Retrieval-Augmented Generation (RAG) — wire the existing document embeddings into `/rag/query`
- [ ] Multi-agent orchestration via LangGraph
- [ ] MCP server exposing chat/document tools to external clients
- [ ] Redis-backed response caching
- [ ] Dockerized deployment

---

## 📬 Contact

Built by **Faizan** — [LinkedIn](#) · [GitHub](#)