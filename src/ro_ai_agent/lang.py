from __future__ import annotations

"""RO: Detectare simpla de limba pentru routing RO/EN.
EN: Simple language detection for RO/EN routing.
"""


def detect_lang(text: str) -> str | None:
    """RO: Returneaza 'ro' sau 'en' cand e suficient de sigur.
    EN: Return 'ro' or 'en' when reasonably confident.
    """
    text_norm = " ".join(text.strip().lower().split())
    if not text_norm:
        return None

    ro_markers = {
        "salut",
        "buna",
        "bună",
        "multumesc",
        "mulțumesc",
        "te rog",
        "va rog",
        "cum",
        "ce",
        "sunt",
        "esti",
        "ești",
        "vreau",
        "ajutor",
    }
    en_markers = {
        "hi",
        "hello",
        "thanks",
        "please",
        "hey",
        "how",
        "are",
        "you",
        "what",
        "can",
        "help",
    }
    if any(m in text_norm for m in en_markers):
        return "en"
    if any(m in text_norm for m in ro_markers):
        return "ro"
    if len(text_norm) < 12:
        return "ro"

    try:
        from langdetect import DetectorFactory, detect_langs  # type: ignore

        DetectorFactory.seed = 0
        guesses = detect_langs(text_norm)
        if not guesses:
            return None
        best = guesses[0]
        if any(ch in text_norm for ch in "ăâîșţșț"):
            return "ro"
        if best.lang in {"ro", "en"}:
            return best.lang
    except Exception:
        return None
    return None
