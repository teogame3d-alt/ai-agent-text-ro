from __future__ import annotations

"""RO: TTS cu fallback-uri (pyttsx3 -> gTTS -> pyttsx3 default).
EN: TTS with fallbacks (pyttsx3 -> gTTS -> pyttsx3 default).
"""

from pathlib import Path
import os
import tempfile
import time

from .lang import detect_lang


_ENGINE = None
_RO_VOICE_ID: str | None = None
_EN_VOICE_ID: str | None = None


def _find_ro_voice(engine) -> str | None:
    """RO: Cauta o voce romana instalata in engine.
    EN: Look for a Romanian voice installed in the engine.
    """
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


def _find_en_voice(engine) -> str | None:
    voices = engine.getProperty("voices")
    for v in voices:
        name = (getattr(v, "name", "") or "").lower()
        langs = getattr(v, "languages", [])
        lang_text = " ".join(
            [l.decode("utf-8", "ignore").lower() if isinstance(l, bytes) else str(l).lower() for l in langs]
        )
        if "en" in lang_text or "english" in name:
            return v.id
    return None


def _play_mp3(path: Path) -> None:
    try:
        from playsound import playsound  # type: ignore

        playsound(str(path))
    except Exception:
        os.startfile(str(path))
        time.sleep(0.2)


def _gtts_speak(text: str, lang: str, output_path: Path | None) -> bool:
    try:
        from gtts import gTTS  # type: ignore

        tts = gTTS(text=text, lang=lang)
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            mp3_path = output_path
        else:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tmp.close()
            mp3_path = Path(tmp.name)

        tts.save(str(mp3_path))
        try:
            _play_mp3(mp3_path)
        finally:
            if output_path is None:
                try:
                    mp3_path.unlink(missing_ok=True)
                except Exception:
                    pass
        return True
    except Exception:
        return False


def _pyttsx3_ro(text: str) -> bool:
    global _ENGINE, _RO_VOICE_ID
    try:
        import pyttsx3  # type: ignore

        if _ENGINE is None:
            _ENGINE = pyttsx3.init()
        if _RO_VOICE_ID is None:
            _RO_VOICE_ID = _find_ro_voice(_ENGINE)

        if _RO_VOICE_ID:
            _ENGINE.setProperty("voice", _RO_VOICE_ID)
            _ENGINE.say(text)
            _ENGINE.runAndWait()
            return True
    except Exception:
        return False
    return False


def _pyttsx3_en(text: str) -> bool:
    global _ENGINE, _EN_VOICE_ID
    try:
        import pyttsx3  # type: ignore

        if _ENGINE is None:
            _ENGINE = pyttsx3.init()
        if _EN_VOICE_ID is None:
            _EN_VOICE_ID = _find_en_voice(_ENGINE)

        if _EN_VOICE_ID:
            _ENGINE.setProperty("voice", _EN_VOICE_ID)
            _ENGINE.say(text)
            _ENGINE.runAndWait()
            return True
    except Exception:
        return False
    return False


def speak(text: str, output_path: Path | None = None) -> bool:
    """RO: RO prioritar; EN doar daca detectat; altfel tace.
    EN: RO first; EN only if detected; otherwise stay silent.
    """
    lang = detect_lang(text)
    if lang == "ro":
        return _gtts_speak(text, "ro", output_path) or _pyttsx3_ro(text)
    if lang == "en":
        return _gtts_speak(text, "en", output_path) or _pyttsx3_en(text)
    return False
