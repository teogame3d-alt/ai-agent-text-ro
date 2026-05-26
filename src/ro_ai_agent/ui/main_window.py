"""RO: UI PyQt6 pentru chat si modul de invatare (Teach).
EN: PyQt6 UI for chat and the Teach workflow.
"""

from __future__ import annotations

from datetime import UTC

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..engine import AgentEngine
from ..lang import detect_lang
from ..memory import (
    add_learned_faq,
    append_learned_json,
    list_learning_queue,
    mark_learning,
)
from ..tts import speak

AGENT_STYLE = """
QWidget {
    background: #eef2f6;
    color: #172033;
}
QTabWidget::pane {
    border: 1px solid #cdd6e0;
    border-radius: 8px;
    background: #ffffff;
}
QTabBar::tab {
    background: #dce6ef;
    color: #263549;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 700;
}
QTabBar::tab:selected {
    background: #ffffff;
}
QTextEdit, QLineEdit, QListWidget {
    background: #ffffff;
    border: 1px solid #c7d2df;
    border-radius: 7px;
    padding: 9px;
}
QPushButton {
    background: #ffffff;
    color: #172033;
    border: 1px solid #c7d2df;
    border-radius: 6px;
    padding: 8px 12px;
    font-weight: 800;
}
QPushButton:hover {
    background: #e8fff7;
    border-color: #10b981;
}
QPushButton#primary {
    background: #134e4a;
    color: #ffffff;
    border-color: #134e4a;
}
QFrame#hero {
    background: #172033;
    border-radius: 8px;
}
QFrame#signalCard {
    background: #ffffff;
    border: 1px solid #cad5df;
    border-radius: 8px;
}
QLabel#heroTitle {
    background: transparent;
    color: #ffffff;
    font-size: 22px;
    font-weight: 900;
}
QLabel#heroSubtitle {
    background: transparent;
    color: #c8d7e5;
}
QLabel#signalLabel {
    color: #6b7787;
    font-size: 11px;
    font-weight: 800;
}
QLabel#signalValue {
    color: #172033;
    font-size: 17px;
    font-weight: 900;
}
"""


class AgentWindow(QWidget):
    """RO: Fereastra principala cu tab-uri Chat si Teach.
    EN: Main window with Chat and Teach tabs.
    """

    def __init__(self, engine: AgentEngine) -> None:
        super().__init__()
        self.engine = engine
        self.setWindowTitle("AI Agent Text RO Studio")
        self.resize(920, 620)
        self.setStyleSheet(AGENT_STYLE)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_chat_tab(), "Chat")
        self.tabs.addTab(self._build_teach_tab(), "Teach")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        layout.addWidget(self._build_hero())
        layout.addWidget(self.tabs)
        self.append_message(
            "System",
            "Deterministic NLP ready: intent match, FAQ fallback, policy rules, and SQLite memory.",
        )

    def on_send(self) -> None:
        """RO: Trimite mesajul, afiseaza raspunsul si optional TTS.
        EN: Send message, show reply, and optionally run TTS.
        """
        text = self.input.text().strip()
        if not text:
            return
        self.append_message("Tu", text)
        self.input.clear()

        reply, score = self.engine.respond(text)
        self.append_message("Agent", reply)
        self.conf_label.setText(f"confidence: {score:.2f}")
        self.status_label.setText("processed")

        if self.voice_checkbox.isChecked():
            try:
                speak(reply)
            except Exception:
                # RO: TTS ramane silent daca nu exista voce RO.
                # EN: Keep TTS silent if no Romanian voice is available.
                pass

    def append_message(self, role: str, content: str) -> None:
        """RO: Adauga o linie in zona de chat.
        EN: Append a line to the chat area.
        """
        self.chat.append(f"<b>{role}:</b> {content}")

    def _build_chat_tab(self) -> QWidget:
        """RO: Construieste tab-ul de chat.
        EN: Build the chat tab UI.
        """
        tab = QWidget()

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Scrie o intrebare...")
        self.input.returnPressed.connect(self.on_send)

        self.send_btn = QPushButton("Trimite")
        self.send_btn.setObjectName("primary")
        self.send_btn.clicked.connect(self.on_send)

        self.voice_checkbox = QCheckBox("Voice (TTS)")
        self.voice_checkbox.setChecked(self.engine.config.enable_voice)

        top = QHBoxLayout()
        top.addWidget(QLabel("Agent status:"))
        self.status_label = QLabel("ready")
        top.addWidget(self.status_label)
        self.conf_label = QLabel("confidence: -")
        top.addWidget(self.conf_label)
        top.addStretch(1)
        top.addWidget(self.voice_checkbox)

        bottom = QHBoxLayout()
        bottom.addWidget(self.input, 1)
        bottom.addWidget(self.send_btn)

        layout = QVBoxLayout(tab)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)
        layout.addLayout(top)
        layout.addLayout(self._quick_prompt_row())
        layout.addWidget(self.chat, 1)
        layout.addLayout(bottom)
        return tab

    def _build_hero(self) -> QFrame:
        """Build a visual summary that explains the project at a glance."""

        hero = QFrame()
        hero.setObjectName("hero")

        title = QLabel("AI Agent Text RO Studio")
        title.setObjectName("heroTitle")
        subtitle = QLabel(
            "RO/EN intent matching, FAQ fallback, policy rules, "
            "human-in-the-loop learning, and SQLite memory."
        )
        subtitle.setObjectName("heroSubtitle")

        copy = QVBoxLayout()
        copy.addWidget(title)
        copy.addWidget(subtitle)
        copy.addStretch(1)

        signals = QGridLayout()
        signals.addWidget(self._signal_card("PIPELINE", "TF-IDF style"), 0, 0)
        signals.addWidget(self._signal_card("MEMORY", "SQLite"), 0, 1)
        signals.addWidget(self._signal_card("CONTROL", "Policy gates"), 0, 2)
        signals.addWidget(self._signal_card("LEARNING", "Human review"), 0, 3)

        row = QHBoxLayout(hero)
        row.setContentsMargins(18, 16, 18, 16)
        row.addLayout(copy, 2)
        row.addLayout(signals, 3)
        return hero

    def _signal_card(self, label: str, value: str) -> QFrame:
        """Create one compact status card for the top project summary."""

        card = QFrame()
        card.setObjectName("signalCard")
        label_widget = QLabel(label)
        label_widget.setObjectName("signalLabel")
        value_widget = QLabel(value)
        value_widget.setObjectName("signalValue")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.addWidget(label_widget)
        layout.addWidget(value_widget)
        return card

    def _quick_prompt_row(self) -> QHBoxLayout:
        """Offer repeatable demo prompts so screenshots show real behavior."""

        row = QHBoxLayout()
        for prompt in ["salut", "ce poti face?", "help me"]:
            button = QPushButton(prompt)
            button.clicked.connect(lambda _checked=False, value=prompt: self._use_prompt(value))
            row.addWidget(button)
        row.addStretch(1)
        return row

    def _use_prompt(self, text: str) -> None:
        """Insert a demo prompt and send it through the same production path."""

        self.input.setText(text)
        self.on_send()

    def _build_teach_tab(self) -> QWidget:
        """RO: Construieste tab-ul de invatare manuala.
        EN: Build the manual learning tab.
        """
        tab = QWidget()

        self.queue_list = QListWidget()
        self.queue_list.itemSelectionChanged.connect(self._on_select_queue)

        self.response_box = QTextEdit()
        self.response_box.setPlaceholderText("Scrie raspunsul corect pentru intrebare.")

        self.approve_btn = QPushButton("Approve")
        self.approve_btn.clicked.connect(self._approve_selected)

        self.deny_btn = QPushButton("Deny (policy)")
        self.deny_btn.clicked.connect(self._deny_selected)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._refresh_queue)

        buttons = QHBoxLayout()
        buttons.addWidget(self.approve_btn)
        buttons.addWidget(self.deny_btn)
        buttons.addStretch(1)
        buttons.addWidget(self.refresh_btn)

        layout = QVBoxLayout(tab)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)
        layout.addWidget(QLabel("Learning queue (pending questions)"))
        layout.addWidget(self.queue_list, 1)
        layout.addWidget(QLabel("Approved response"))
        layout.addWidget(self.response_box, 1)
        layout.addLayout(buttons)

        self._refresh_queue()
        return tab

    def _refresh_queue(self) -> None:
        """RO: Reincarca lista de intrebari pending.
        EN: Reload the pending learning queue.
        """
        self.queue_list.clear()
        for item_id, question, status, created_at in list_learning_queue(self.engine.memory_db):
            if status != "pending":
                continue
            entry = QListWidgetItem(f"[{item_id}] {question}")
            entry.setData(Qt.ItemDataRole.UserRole, (item_id, question, created_at))
            self.queue_list.addItem(entry)

    def _on_select_queue(self) -> None:
        """RO: Populeaza zona de raspuns cand se selecteaza o intrebare.
        EN: Fill the response area when a question is selected.
        """
        items = self.queue_list.selectedItems()
        if not items:
            return
        item_id, question, _created = items[0].data(Qt.ItemDataRole.UserRole)
        self.response_box.setPlainText("")
        self.append_message("Teach", f"Selected: {question} (id={item_id})")

    def _approve_selected(self) -> None:
        """RO: Salveaza raspunsul aprobat si marcheaza itemul ca approved.
        EN: Save approved response and mark the item approved.
        """
        items = self.queue_list.selectedItems()
        if not items:
            return
        item_id, question, _created = items[0].data(Qt.ItemDataRole.UserRole)
        response = self.response_box.toPlainText().strip()
        if not response:
            return
        created = self._now()
        add_learned_faq(self.engine.memory_db, question, response, created)
        lang = detect_lang(question) or "ro"
        append_learned_json(self.engine.memory_db, question, response, created, lang)
        mark_learning(self.engine.memory_db, item_id, "approved")
        self._refresh_queue()
        self.append_message("Teach", "Approved and learned.")

    def _deny_selected(self) -> None:
        """RO: Adauga un keyword de blocare si marcheaza itemul denied.
        EN: Add a deny keyword and mark the item denied.
        """
        items = self.queue_list.selectedItems()
        if not items:
            return
        item_id, question, _created = items[0].data(Qt.ItemDataRole.UserRole)
        keyword, ok = QInputDialog.getText(self, "Deny rule", "Keyword to block")
        if ok and keyword.strip():
            self.engine.add_policy_keyword(keyword.strip(), "deny")
            mark_learning(self.engine.memory_db, item_id, "denied")
            self._refresh_queue()
            self.append_message("Teach", f"Denied by policy keyword: {keyword.strip()}")

    def _now(self) -> str:
        """RO: Timestamp UTC pentru consistenta in DB.
        EN: UTC timestamp for DB consistency.
        """
        from datetime import datetime

        return datetime.now(UTC).isoformat()
