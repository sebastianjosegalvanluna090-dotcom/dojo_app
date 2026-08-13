from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox,
)
from PyQt6.QtCore import Qt

from core.i18n import tr

BG_DIALOG = "#111111"
BG_INPUT  = "#1C1C1C"
BORDER    = "#2A2A2A"
RED       = "#C8102E"
RED_H     = "#E8152F"
TEXT_PRI  = "#F0F0F0"
TEXT_MUT  = "#666666"


class TypeProductDialog(QDialog):
    def __init__(self, repo, category=None, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.category = category
        self.setWindowTitle(tr("management.category.create_title") if category is None else tr("management.category.edit_title"))
        self.setFixedSize(420, 210)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")
        self._build_ui()
        if category is not None:
            self.input_name.setText(category["name"])

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        card = QLabel()
        card.setStyleSheet(f"""
            background-color: #161616;
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 20px;
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)

        card_layout.addWidget(self._label(tr("management.category.name")))
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText(tr("management.category.name_placeholder"))
        self.input_name.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 8px;
                padding: 0 12px; font-size: 13px; min-height: 36px;
            }}
            QLineEdit:focus {{ border-color: {RED}; }}
        """)
        card_layout.addWidget(self.input_name)

        root.addWidget(card)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton(tr("management.category.cancel"))
        btn_cancel.setFixedHeight(36)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUT};
                border: 1px solid {BORDER}; border-radius: 7px; font-size: 13px;
            }}
            QPushButton:hover {{ color: {TEXT_PRI}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton(tr("management.category.save"))
        self.btn_save.setFixedHeight(36)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background: {RED}; color: white;
                border: none; border-radius: 7px; font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        self.btn_save.clicked.connect(self._save)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self.btn_save)
        root.addLayout(btn_row)

    def _label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px; font-weight: 600;")
        return lbl

    def _save(self):
        name = self.input_name.text().strip()
        if not name:
            QMessageBox.warning(self, tr("management.category.create_title"), tr("management.category.required"))
            return
        if len(name) < 2:
            QMessageBox.warning(self, tr("management.category.create_title"), tr("management.category.too_short"))
            return

        try:
            if self.category is None:
                self.repo.create(name)
            else:
                self.repo.update(self.category["id"], name)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, tr("common.error"), str(e))
