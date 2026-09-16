from groq import Groq
from app.core.config import settings
from sentence_transformers import SentenceTransformer
from datetime import datetime
import json

client = Groq(api_key=settings.GROQ_API_KEY)


MODEL = "openai/gpt-oss-120b"


# =========================
# NORMAL CHAT
# =========================
def chat_completion(message: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": message
            }
        ],
    )

    return response.choices[0].message.content


# =========================
# STREAMING CHAT (SSE)
# =========================
async def stream_chat_completion(message: str):
    stream = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": message
            }
        ],
        stream=True,
    )

    for chunk in stream:
        try:
            content = chunk.choices[0].delta.content

            if content:
                yield f"data: {content}\n\n"

        except Exception:
            continue

    yield "data: [DONE]\n\n"


# =========================
# EMBEDDINGS
# =========================
_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str) -> list[float]:
    return _embedding_model.encode(text).tolist()


# =========================
# FUNCTION CALLING
# =========================
FUNCTIONS = [
    {
        "name": "get_current_time",
        "description": "Get current UTC time",
        "parameters": {
            "type": "object",
            "properties": {}
        },
    },
    {
        "name": "calculate",
        "description": "Evaluate a math expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string"
                }
            },
            "required": ["expression"]
        },
    },
]


def execute_function(name: str, args: dict) -> str:

    if name == "get_current_time":
        return datetime.utcnow().isoformat()

    if name == "calculate":
        try:
            return str(
                eval(
                    args["expression"],
                    {"__builtins__": {}}
                )
            )
        except Exception as e:
            return str(e)

    return "Unknown function"


def chat_with_tools(message: str) -> str:

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": message
            }
        ],
        tools=[
            {
                "type": "function",
                "function": func
            }
            for func in FUNCTIONS
        ],
    )

    msg = response.choices[0].message

    if getattr(msg, "tool_calls", None):

        call = msg.tool_calls[0]

        args = json.loads(call.function.arguments)

        result = execute_function(
            call.function.name,
            args
        )

        followup = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": message
                },
                {
                    "role": "assistant",
                    "tool_calls": [call]
                },
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result
                },
            ],
        )

        return followup.choices[0].message.content

    return msg.content  