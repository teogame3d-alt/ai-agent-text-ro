from __future__ import annotations

from pathlib import Path
import os
import time


def _find_ro_voice(engine) -> str | None:
    voices = engine.getProperty("voices")
    for v in voices:
        name = (getattr(v, "name", "") or "").lower()
        langs = getattr(v, "languages", [])
        lang_text = " ".join(
            [l.decode("utf-8", "ignore").lower() if isinstance(l, bytes) else str(l).lower() for l in langs]
        )
        if "ro" in lang_text or "romanian" in name or "romana" in name:
            return v.id
    return None


def speak(text: str, output_path: Path | None = None) -> None:
    """Prefer Romanian TTS. Try pyttsx3 with RO voice, then gTTS. If gTTS fails,
    fallback to pyttsx3 default voice to avoid silence.
    """
    try:
        import pyttsx3  # type: ignore

        engine = pyttsx3.init()
        ro_voice = _find_ro_voice(engine)
        if ro_voice:
            engine.setProperty("voice", ro_voice)
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
        try:
            from playsound import playsound  # type: ignore

            playsound(str(mp3_path))
        except Exception:
            os.startfile(str(mp3_path))
            time.sleep(0.2)
        return
    except Exception:
        try:
            import pyttsx3  # type: ignore

            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            return
        except Exception:
            raise RuntimeError("No TTS backend available. Install gTTS or pyttsx3.")
