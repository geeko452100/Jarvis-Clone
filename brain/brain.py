"""Core JARVIS logic: persona, tool-calling loop, conversation history.

This is the "brain" — it doesn't know or care whether it's being called
from a terminal script or a FastAPI endpoint. It just takes text in and
returns text out, running tool calls as needed along the way.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Loaded first — tools.py loads every skill file immediately on import,
# and a skill that reads an env var (like an API key) at import time
# would otherwise find .env not yet read.
load_dotenv()

from groq import Groq
from tools import AVAILABLE_TOOLS, TOOL_SCHEMAS

MODEL = os.getenv("MODEL_NAME")

if not MODEL:
    print("Error: Invalid or missing env variables.")
    sys.exit(1)

client = Groq()

try:
    with open("jarvis.md", "r", encoding="utf-8") as f:
        persona = f.read()
except FileNotFoundError:
    print("Error: jarvis.md not found — persona file is required to start.")
    sys.exit(1)

# One global conversation, same as the terminal version — this is a
# single-user hobby project, so there's no need for per-session state
# yet. Every call to get_jarvis_response() reads and appends here.
messages = [{"role": "system", "content": persona}]

MAX_TOOL_ROUNDS = 5


def get_jarvis_response(user_text: str) -> str:
    """Run one full turn: send user_text to the model, handle any tool
    calls it requests, and return JARVIS's final plain-text reply."""

    # Declared up front (Python requires `global` before the name is
    # used in the function) since this function both reads and
    # reassigns the module-level `messages` list.
    global messages

    messages.append({"role": "user", "content": user_text})

    response_message = None

    for _ in range(MAX_TOOL_ROUNDS):
        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
        )

        response_message = completion.choices[0].message

        if not response_message.tool_calls:
            break  # Final answer — no more tools requested.

        messages.append(
            {
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in response_message.tool_calls
                ],
            }
        )

        for tool_call in response_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments or "{}")

            tool_function = AVAILABLE_TOOLS.get(tool_name)
            if tool_function:
                result = tool_function(**tool_args)
            else:
                result = f"Error: unknown tool '{tool_name}'"

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                }
            )
    else:
        # Hit MAX_TOOL_ROUNDS without a final plain-text answer.
        return "Apologies, sir — I got stuck deciding how to answer that."

    full_response = response_message.content

    messages.append({"role": "assistant", "content": full_response})

    # Keep history bounded: system prompt + last 20 messages after it.
    messages = [messages[0]] + messages[1:][-20:]

    return full_response