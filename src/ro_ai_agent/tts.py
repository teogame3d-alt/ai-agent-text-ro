from __future__ import annotations

from pathlib import Path
import os
import time


def speak(text: str, output_path: Path | None = None) -> None:
    """Try pyttsx3 for live speech. If not available, use gTTS and play mp3.

    If output_path is provided, gTTS will save an mp3 and open it with default player.
    """
    try:
        import pyttsx3  # type: ignore

        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return
    except Exception:
        pass

    try:
        from gtts import gTTS  # type: ignore

        tts = gTTS(text=text, lang="ro")
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            mp3_path = output_path
        else:
            mp3_path = Path("tts_output.mp3")
        tts.save(str(mp3_path))
        os.startfile(str(mp3_path))
        time.sleep(0.2)
        return
    except Exception:
        raise RuntimeError("No TTS backend available. Install gTTS or pyttsx3.")
