# ─── EVENT_POST_DIALOG ──────────────────────────────────────────────

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QFrame, QCheckBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor

from core.debug import debug_log
from views.events.event_widgets import (
    BG_MAIN, BG_CARD, BG_CARD2, BG_HOVER, BORDER, BORDER2,
    RED, RED_H, TEXT_PRI, TEXT_SEC, TEXT_MUT, TEXT_DIM, GREEN,
)


class EventPostDialog(QDialog):
    """Dialog to create a post on an event."""

    def __init__(self, repo, event_id, current_user, post_id=None, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.event_id = event_id
        self.current_user = current_user
        self.current_user_id = current_user.get("id") if current_user else None
        self._post_id = post_id
        self._is_edit = post_id is not None

        self.setWindowTitle("Editar publicación" if self._is_edit else "Nueva publicación")
        self.setFixedSize(480, 380)
        self.setStyleSheet(f"QDialog {{ background-color: {BG_MAIN}; }}")

        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        header = QHBoxLayout()
        lbl_title = QLabel("Editar publicación" if self._is_edit else "Nueva publicación")
        lbl_title.setStyleSheet(f"color: {TEXT_PRI}; font-size: 15px; font-weight: 800; font-family: 'Inter','Segoe UI',sans-serif;")
        header.addWidget(lbl_title)
        header.addStretch()
        root.addLayout(header)

        content_lbl = QLabel("Contenido")
        content_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 600; font-family: 'Inter','Segoe UI',sans-serif;")
        root.addWidget(content_lbl)

        self._content_edit = QTextEdit()
        self._content_edit.setPlaceholderText("Escribe tu publicación aquí...")
        self._content_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {BG_CARD2}; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 10px;
                padding: 12px; font-size: 13px; font-weight: 500;
                font-family: 'Inter','Segoe UI',sans-serif;
                line-height: 1.4;
            }}
            QTextEdit:focus {{ border-color: {BORDER2}; }}
        """)
        root.addWidget(self._content_edit)

        self._pinned_check = QCheckBox("Publicación fijada")
        self._pinned_check.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 600; font-family: 'Inter','Segoe UI',sans-serif;")
        root.addWidget(self._pinned_check)

        root.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setMinimumWidth(100)
        btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_CARD2}; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 8px;
                font-size: 11px; font-weight: 600;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QPushButton:hover {{ background-color: {BG_HOVER}; color: {TEXT_PRI}; }}
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_publish = QPushButton("Publicar")
        btn_publish.setFixedHeight(36)
        btn_publish.setMinimumWidth(100)
        btn_publish.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_publish.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED}; color: white;
                border: 1px solid {RED_H}; border-radius: 8px;
                font-size: 11px; font-weight: 700;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QPushButton:hover {{ background-color: {RED_H}; }}
        """)
        btn_publish.clicked.connect(self._publish)
        btn_row.addWidget(btn_publish)

        root.addLayout(btn_row)

    def _publish(self):
        content = self._content_edit.toPlainText().strip()
        if not content:
            self._content_edit.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {BG_CARD2}; color: {TEXT_SEC};
                    border: 1px solid {RED}; border-radius: 10px;
                    padding: 12px; font-size: 13px; font-weight: 500;
                    font-family: 'Inter','Segoe UI',sans-serif;
                }}
            """)
            return

        is_pinned = self._pinned_check.isChecked()

        try:
            if self._is_edit:
                ok = self.repo.update_event_post(self._post_id, self.current_user_id, {
                    "content": content,
                    "is_pinned": is_pinned,
                    "image_path": None,
                })
            else:
                post_id = self.repo.create_event_post(
                    self.event_id,
                    self.current_user_id,
                    content,
                    image_path=None,
                    is_pinned=is_pinned,
                )
                ok = post_id is not None

            if ok:
                self.accept()
        except Exception as e:
            debug_log(f"[EventPost] Error publicando: {e}")
