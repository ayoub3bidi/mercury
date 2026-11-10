from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    max_tokens: int | None = None


@app.post("/v1/chat/completions")
def chat_completion(payload: ChatRequest):
    prompt = payload.messages[-1].content if payload.messages else ""
    return {
        "id": "mercury-local-mock",
        "object": "chat.completion",
        "created": 0,
        "model": payload.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": f"Local mock response: {prompt[:100]}"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 1, "completion_tokens": 8, "total_tokens": 9},
    }
