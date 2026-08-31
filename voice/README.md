# Voice

Handles listening and transcribing for JARVIS — the "ears." Talks to the
[Brain project](../brain/README.md) over its `/chat` API; doesn't do any
reasoning or tool calling itself. See `02_voice_todo.md` for the full
roadmap.

## Status

- [x] Toggle-to-record (press SPACE to start/stop) — `record.py`
- [x] Speech-to-text via Groq's Whisper endpoint — `stt.py`
- [ ] Send transcribed text to the Brain's `/chat` endpoint
- [ ] Text-to-speech (speak the Brain's response back)
- [ ] Wake-word detection (hybrid: wake word + push-to-talk as fallback)

## Important: runs on native Windows, not WSL

This project needs real microphone access, and WSL2 doesn't reliably
pass audio hardware through to the Linux side — `sounddevice`/PortAudio
can't see the mic at all from inside WSL. Everything in this folder
should be run from a native Windows Python install (PowerShell or cmd),
not from a WSL terminal. The Brain project can keep running in WSL as
usual — WSL2 forwards `localhost` ports to Windows automatically, so
this project will still be able to reach `http://localhost:8000/chat`
from the Windows side without extra setup.

## Setup

From a Windows terminal, inside this folder:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with:

```
GROQ_API_KEY=your_key_here
STT_MODEL=whisper-large-v3-turbo
```

(`STT_MODEL` is optional — defaults to `whisper-large-v3-turbo` if omitted.)

## Files

- `record.py` — mic/toggle mechanics only. Press SPACE to start recording,
  press again to stop; saves to `recording.wav` and calls into `stt.py`
  to transcribe it. Uses `sounddevice` for audio capture and `pynput` for
  the global hotkey.
- `stt.py` — owns the Groq connection for transcription specifically.
  Exposes one function, `transcribe(path)`, that takes a WAV file path
  and returns the transcribed text. Kept separate from `record.py` so
  the mic/toggle logic doesn't need to know Groq exists.

## Running it

```
python record.py
```

Press SPACE, speak, press SPACE again. You should see the transcript
printed as "You said: ...". Ctrl+C to quit.

## Design notes

- Toggle-to-talk (press to start, press again to stop), not hold-to-talk
  or auto-silence-detection — simplest option to get right first, and a
  legitimate permanent choice on its own.
- The eventual hybrid interaction model is wake-word detection as the
  primary trigger, with the SPACE toggle staying available as a manual
  fallback — both would start the same underlying record → transcribe →
  send-to-Brain → speak pipeline.
- This project deliberately knows nothing about tools, skills, or
  conversation memory — all of that lives in the Brain. Voice's only job
  is turning speech into text, sending it off, and turning the response
  back into speech.