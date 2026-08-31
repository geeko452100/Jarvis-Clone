"""Toggle-to-record: press SPACE to start recording, press again to stop
and transcribe it. Recording/toggle mechanics only — actual Groq calls
live in stt.py, kept separate on purpose.

Requires: pip install sounddevice soundfile pynput numpy
(stt.py has its own requirements: groq, python-dotenv)
"""

import queue
import numpy as np
import sounddevice as sd
import soundfile as sf
from pynput import keyboard

from stt import transcribe

SAMPLE_RATE = 16000  # Whisper expects 16kHz mono audio
CHANNELS = 1
OUTPUT_FILE = "recording.wav"

recording = False
key_held = False  # Prevents OS key-repeat from toggling multiple times
                   # while SPACE is held down — without this, holding
                   # the key would fire on_press repeatedly and rapidly
                   # flip recording on/off/on/off.
audio_queue = queue.Queue()


def audio_callback(indata, frames, time, status):
    """Called continuously by sounddevice for every audio chunk, whether
    we're "recording" or not. Only actually queue it while `recording`
    is True — this is what makes the toggle meaningful."""
    if recording:
        audio_queue.put(indata.copy())


def start_recording():
    global recording
    print("Recording... press SPACE again to stop.")
    recording = True


def stop_recording():
    global recording
    recording = False
    print("Stopped. Saving...")

    frames = []
    while not audio_queue.empty():
        frames.append(audio_queue.get())

    if not frames:
        print("Nothing recorded.\n")
        return

    audio_data = np.concatenate(frames, axis=0)
    sf.write(OUTPUT_FILE, audio_data, SAMPLE_RATE)

    print("Transcribing...")
    try:
        text = transcribe(OUTPUT_FILE)
        print(f"You said: {text}\n")
    except Exception as e:
        print(f"Transcription failed: {e}\n")


def on_press(key):
    global key_held
    if key == keyboard.Key.space and not key_held:
        key_held = True
        if not recording:
            start_recording()
        else:
            stop_recording()


def on_release(key):
    global key_held
    if key == keyboard.Key.space:
        key_held = False


print("Ready. Press SPACE to start/stop recording. Ctrl+C to quit.\n")

# The audio stream runs continuously in the background the whole time
# this script is alive — audio_callback() decides moment-to-moment
# whether what it's hearing actually gets kept.
stream = sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    callback=audio_callback,
)
stream.start()

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()