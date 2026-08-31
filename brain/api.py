"""FastAPI entry point for JARVIS.

Thin on purpose — all the actual chatbot logic lives in brain.py. This
file's only job is to expose it over HTTP so other projects (Voice,
Gesture, Holo-Display) can send text and get a response back, instead
of each of them needing to talk to Groq directly.

Run with: uvicorn api:app --reload
"""

from fastapi import FastAPI
from pydantic import BaseModel

from brain import get_jarvis_response

app = FastAPI()


class ChatRequest(BaseModel):
    text: str


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    reply = get_jarvis_response(request.text)
    return ChatResponse(response=reply)