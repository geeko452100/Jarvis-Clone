# Jarvis

A personal voice assistant written in Python — wake word → speech-to-text → LLM → text-to-speech, running locally where possible.

> **Status:** the text "brain" works. You can talk to JARVIS over an HTTP endpoint, and it can call skills (calculator, time, web search) while it answers. The voice pipeline around it — wake word, local STT, local TTS — isn't wired up yet; `record.py` is the first piece of that.

## Planned pipeline

```
🎤 mic input
   │
   ▼
[ openWakeWord ]   listen for a wake word (e.g. "Jarvis")        ── not wired up
   │
   ▼
[ faster-whisper ] transcribe speech to text (local STT)         ── not wired up
   │
   ▼
[ brain.py ]       send transcript to Groq, run tool calls,      ── ✅ working
                   return a reply
   │
   ▼
[ Piper ]          synthesize the response back to speech (TTS)  ── not wired up
   │
   ▼
🔊 speaker output
```

Right now the working path is: **text in → `brain.py` / `api.py` → text out**, with skills invoked along the way.

## Architecture

| File               | Role                                                                                     |
| ------------------ | ---------------------------------------------------------------------------------------- |
| `brain.py`         | Core logic: persona, conversation history, the tool-calling loop. Takes text in, returns text out. Doesn't care who's calling it. |
| `api.py`           | Thin FastAPI wrapper exposing `brain.py` over HTTP (`POST /chat`) so other projects (Voice, Gesture, Holo-Display) can share one brain. |
| `tools.py`         | Skill loader. Scans `skills/`, imports each file, and builds the tool registry + schemas sent to the model. |
| `skills/`          | One file per skill. Each follows the `NAME` / `DESCRIPTION` / `PARAMETERS` / `run()` convention. |
| `jarvis.md`        | The persona / system prompt. Required at startup.                                        |
| `record.py`        | Standalone toggle-to-record audio capture (press SPACE to start/stop → `recording.wav`). Proving the audio-capture mechanic before STT is added. |

### Skills

Currently included:

| Skill         | Description                                          | Requires                     |
| ------------- | --------------------------------------------------- | ---------------------------- |
| `calculator`  | Evaluate a basic math expression (via `simpleeval`) | —                            |
| `get_time`    | Return the current local time                        | —                            |
| `web_search`  | Search the web and return a short summary (Tavily)   | `TAVILY_API_KEY`             |

To add a skill, drop a `.py` file in `skills/` exposing four names — `NAME` (str), `DESCRIPTION` (str), `PARAMETERS` (JSON-schema dict), and `run(**kwargs)`. The loader picks it up automatically on the next start; files missing any of the four are skipped with a warning.

## Tech stack

| Concern            | Library                                                              |
| ------------------ | --------------------------------------------------------------------- |
| LLM inference      | [`groq`](https://github.com/groq/groq-python) (Groq API)             |
| HTTP API           | `fastapi`, `uvicorn`                                                 |
| Web search skill   | [`tavily`](https://tavily.com)                                      |
| Calculator skill   | `simpleeval`                                                         |
| Audio capture      | `sounddevice`, `soundfile`, `pynput`, `numpy`                       |
| Wake word detection| [`openwakeword`](https://github.com/dscripka/openWakeWord) — planned |
| Speech-to-text     | [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) — planned |
| Text-to-speech     | [`piper`](https://github.com/rhasspy/piper) — planned                |
| Config / validation| `pydantic`                                                           |
| CLI / output       | `typer`, `rich`                                                     |

Full pinned versions are in [requirements.txt](requirements.txt).

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure secrets
cp .env.example .env
# then fill in GROQ_API_KEY and MODEL_NAME (and TAVILY_API_KEY if you want web search)
```

### Environment variables

| Variable         | Required | Description                                                        |
| ---------------- | -------- | ----------------------------------------------------------------- |
| `GROQ_API_KEY`   | yes      | API key for Groq-hosted LLM inference (https://console.groq.com/keys) |
| `MODEL_NAME`     | yes      | Groq model id to use (e.g. `llama-3.3-70b-versatile`). `brain.py` exits if unset. |
| `TAVILY_API_KEY` | no       | Enables the `web_search` skill (free tier at https://tavily.com). Without it, `web_search` returns an unavailable message. |

## Usage

Start the API:

```bash
uvicorn api:app --reload
```

Then send it text:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "what is 12 * (4 + 3)?"}'
# {"response":"That's 84, sir."}
```

`brain.py` keeps a single global conversation (system prompt + last 20 messages) — it's a single-user hobby project, so there's no per-session state yet.

### Audio capture (standalone)

```bash
pip install sounddevice soundfile pynput numpy   # already in requirements.txt
python record.py
# press SPACE to start/stop recording → recording.wav
```

## Roadmap

- [x] LLM response generation (Groq), with conversation history
- [x] Skill/tool system with auto-loading (`calculator`, `get_time`, `web_search`)
- [x] HTTP API in front of the brain (`POST /chat`)
- [x] Audio capture proof of concept (`record.py`)
- [ ] Wake word listener loop (openWakeWord)
- [ ] Local STT transcription (faster-whisper) — feed `recording.wav` into the brain
- [ ] Local TTS playback (Piper)
- [ ] End-to-end voice loop tying the above together
- [ ] Config file for voice, model choice, and wake word
- [ ] More skills (timers, home automation, etc.)
- [ ] Tests

## License

TBD.
