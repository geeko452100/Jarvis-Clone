# brain

The text "brain" of JARVIS: text in → LLM reply out, with skills (tool calls)
invoked along the way. It has no idea whether it's being driven by a terminal
script, an HTTP client, or an eventual voice pipeline — it just takes a string
and returns a string.

## Layout

| File          | Role                                                                                                   |
| ------------- | ------------------------------------------------------------------------------------------------------ |
| `brain.py`    | Core logic: loads the persona, keeps one global conversation, runs the tool-calling loop, returns the final reply. Exposes `get_jarvis_response(text) -> str`. |
| `api.py`      | Thin FastAPI wrapper over `brain.py` — `POST /chat` so other projects can share one brain instead of each talking to Groq directly. |
| `tools.py`    | Skill loader. Scans `skills/`, imports each file, and builds `AVAILABLE_TOOLS` (name → function) and `TOOL_SCHEMAS` (sent to the model). Runs on import. |
| `skills/`     | One file per skill, each following the `NAME` / `DESCRIPTION` / `PARAMETERS` / `run()` convention.      |
| `jarvis.md`   | The persona / system prompt. Required at startup — `brain.py` exits if it's missing.                    |

## How a turn works

1. `get_jarvis_response(text)` appends the user message to the shared history.
2. It calls the Groq chat API with the full history and the tool schemas.
3. If the model requests tool calls, each is dispatched through `AVAILABLE_TOOLS`,
   the results are appended as `tool` messages, and the loop repeats.
4. Once the model returns plain text (or after `MAX_TOOL_ROUNDS = 5`), that reply
   is appended and returned.
5. History is trimmed to the system prompt + the last 20 messages.

There is one global conversation — this is a single-user hobby project, so there's
no per-session state yet.

## Skills

| Skill        | Description                                          | Requires         |
| ------------ | -------------------------------------------------- | ---------------- |
| `calculator` | Evaluate a basic math expression (via `simpleeval`) | —                |
| `get_time`   | Return the current local time                        | —                |
| `web_search` | Search the web and return a short summary (Tavily)   | `TAVILY_API_KEY` |

To add one, drop a `.py` file in `skills/` exposing four names:

- `NAME` — `str`, the tool name the model calls
- `DESCRIPTION` — `str`, shown to the model
- `PARAMETERS` — JSON-schema `dict` describing the arguments
- `run(**kwargs)` — the function that does the work and returns a result

The loader picks it up on the next start. Files missing any of the four are
skipped with a printed warning rather than crashing startup. Read API keys
lazily inside `run()`, not at import time — skills are imported before `.env`
is guaranteed to have been read.

## Setup

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then fill in the values below
```

### Environment variables

| Variable         | Required | Description                                                                     |
| ---------------- | -------- | ----------------------------------------------------------------------------- |
| `GROQ_API_KEY`   | yes      | API key for Groq-hosted LLM inference — https://console.groq.com/keys          |
| `MODEL_NAME`     | yes      | Groq model id, e.g. `llama-3.3-70b-versatile`. `brain.py` exits if unset.       |
| `TAVILY_API_KEY` | no       | Enables the `web_search` skill (free tier at https://tavily.com). Without it, `web_search` returns an "unavailable" message. |

## Usage

Start the API:

```bash
uvicorn api:app --reload
```

Send it text:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "what is 12 * (4 + 3)?"}'
# {"response":"That's 84, sir."}
```

Or call the brain directly from Python:

```python
from brain import get_jarvis_response

print(get_jarvis_response("what time is it?"))
```

> Both entry points run from this directory — `jarvis.md` and `skills/` are
> resolved as relative paths.

## Tech stack

| Concern       | Library                    |
| ------------- | -------------------------- |
| LLM inference | `groq`                    |
| HTTP API      | `fastapi`, `uvicorn`      |
| Web search    | `tavily`                  |
| Calculator    | `simpleeval`              |
| Config        | `python-dotenv`, `pydantic` |

Full pinned versions are in [requirements.txt](requirements.txt).
