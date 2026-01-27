from __future__ import annotations

from pathlib import Path


def speak(text: str, output_path: Path | None = None) -> None:
    """Try Google TTS (gTTS). If not available, fallback to pyttsx3.

    If output_path is provided, gTTS will save an mp3. pyttsx3 ignores output_path.
    """
    try:
        from gtts import gTTS  # type: ignore

        tts = gTTS(text=text, lang="ro")
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            tts.save(str(output_path))
        else:
            temp_path = Path("tts_output.mp3")
            tts.save(str(temp_path))
        return
    except Exception:
        pass

    try:
        import pyttsx3  # type: ignore

        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return
    except Exception:
        raise RuntimeError("No TTS backend available. Install gTTS or pyttsx3.")
