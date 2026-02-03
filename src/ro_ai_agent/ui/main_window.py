from __future__ import annotations

"""RO: UI PyQt6 pentru chat si modul de invatare (Teach).
EN: PyQt6 UI for chat and the Teach workflow.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QInputDialog,
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


class AgentWindow(QWidget):
    """RO: Fereastra principala cu tab-uri Chat si Teach.
    EN: Main window with Chat and Teach tabs.
    """
    def __init__(self, engine: AgentEngine) -> None:
        super().__init__()
        self.engine = engine
        self.setWindowTitle("AI Agent Text RO")
        self.resize(700, 420)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_chat_tab(), "Chat")
        self.tabs.addTab(self._build_teach_tab(), "Teach")

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)

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
        layout.addLayout(top)
        layout.addWidget(self.chat, 1)
        layout.addLayout(bottom)
        return tab

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
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()
