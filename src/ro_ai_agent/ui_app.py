from __future__ import annotations

"""RO: Entry point pentru UI PyQt6 (usor de rulat din IDE).
EN: PyQt6 UI entry point (easy to run from IDE).
"""

from pathlib import Path

from PyQt6.QtWidgets import QApplication

from .engine import AgentEngine
from .ui.main_window import AgentWindow


def main() -> None:
    """RO: Bootstrapeaza engine-ul si porneste fereastra UI.
    EN: Bootstrap the engine and launch the UI window.
    """
    base = Path(__file__).resolve().parents[2]
    data_path = base / "data" / "intents_ro.json"
    cfg_path = base / "data" / "config.json"
    memory_db = base / "data" / "memory.db"

    engine = AgentEngine.from_paths(data_path, cfg_path, memory_db)
    app = QApplication([])
    win = AgentWindow(engine)
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
