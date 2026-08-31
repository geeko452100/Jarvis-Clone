"""Speech-to-text via Groq's Whisper endpoint.

Owns the Groq connection for transcription specifically — kept separate
from record.py (which only handles mic/toggle mechanics) and from
brain.py's own Groq client (which handles chat, a different kind of
model entirely).
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq()
STT_MODEL = os.getenv("STT_MODEL", "whisper-large-v3-turbo")


def transcribe(path):
    """Send a WAV file to Groq's Whisper endpoint and return the
    transcribed text."""
    with open(path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            file=f,
            model=STT_MODEL,
        )
    return transcript.text