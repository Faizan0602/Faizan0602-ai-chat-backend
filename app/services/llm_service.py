from groq import AsyncGroq, Groq
from app.core.config import settings

from datetime import datetime
import json

client = Groq(api_key=settings.GROQ_API_KEY)
async_client = AsyncGroq(api_key=settings.GROQ_API_KEY)


MODEL = "openai/gpt-oss-120b"
MAX_COMPLETION_TOKENS = 500
SYSTEM_PROMPT = (
    "You are Orbit, a concise and helpful AI assistant. "
    "Answer directly in a few paragraphs or a short list. "
    "Give detailed explanations only when the user explicitly asks for detail."
)


def build_chat_messages(messages: list[dict]) -> list[dict]:
    return [{"role": "system", "content": SYSTEM_PROMPT}, *messages]


# =========================
# NORMAL CHAT
# =========================
def chat_completion(message: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_COMPLETION_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
    )

    return response.choices[0].message.content


# =========================
# STREAMING CHAT (SSE)
# =========================
async def stream_chat_completion(message: str):
    stream = async_client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_COMPLETION_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        stream=True,
    )

    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content




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

def chat_completion_with_history(messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_COMPLETION_TOKENS,
        messages=build_chat_messages(messages),
    )
    return response.choices[0].message.content

async def stream_chat_completion_with_history(messages: list[dict]):
    stream = await async_client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_COMPLETION_TOKENS,
        messages=build_chat_messages(messages),
        stream=True,
    )
    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content