from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..engine import AgentEngine
from ..tts import speak


class AgentWindow(QWidget):
    def __init__(self, engine: AgentEngine) -> None:
        super().__init__()
        self.engine = engine
        self.setWindowTitle("AI Agent Text RO")
        self.resize(700, 420)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Scrie o intrebare...")
        self.input.returnPressed.connect(self.on_send)

        self.send_btn = QPushButton("Trimite")
        self.send_btn.clicked.connect(self.on_send)

        self.voice_checkbox = QCheckBox("Voice (TTS)")
        self.voice_checkbox.setChecked(self.engine.config.enable_voice)

        top = QHBoxLayout()
        top.addWidget(QLabel("Agent status:"))
        top.addWidget(QLabel("ready"))
        top.addStretch(1)
        top.addWidget(self.voice_checkbox)

        bottom = QHBoxLayout()
        bottom.addWidget(self.input, 1)
        bottom.addWidget(self.send_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.chat, 1)
        layout.addLayout(bottom)

    def on_send(self) -> None:
        text = self.input.text().strip()
        if not text:
            return
        self.append_message("Tu", text)
        self.input.clear()

        reply = self.engine.respond(text)
        self.append_message("Agent", reply)

        if self.voice_checkbox.isChecked():
            try:
                speak(reply)
            except Exception as exc:
                self.append_message("TTS", f"Eroare: {exc}")

    def append_message(self, role: str, content: str) -> None:
        self.chat.append(f"<b>{role}:</b> {content}")
