# ─── EVENT_REGISTRATION_DIALOG ──────────────────────────────────────

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTextEdit, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor

from core.debug import debug_log
from views.events.event_widgets import (
    BG_MAIN, BG_CARD, BG_CARD2, BG_HOVER, BORDER, BORDER2,
    RED, RED_H, TEXT_PRI, TEXT_SEC, TEXT_MUT, TEXT_DIM, GREEN,
)


class EventRegistrationDialog(QDialog):
    """Dialog to register a student for an event."""

    def __init__(self, repo, event_id, current_user, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.event_id = event_id
        self.current_user = current_user
        self.current_user_id = current_user.get("id") if current_user else None
        self._students = []
        self._selected_student_id = None

        self.setWindowTitle("Inscribir participante")
        self.setFixedSize(440, 380)
        self.setStyleSheet(f"QDialog {{ background-color: {BG_MAIN}; }}")

        self._build_ui()
        self._load_students()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        header = QHBoxLayout()
        lbl_title = QLabel("Inscribir participante")
        lbl_title.setStyleSheet(f"color: {TEXT_PRI}; font-size: 15px; font-weight: 800; font-family: 'Inter','Segoe UI',sans-serif;")
        header.addWidget(lbl_title)
        header.addStretch()
        root.addLayout(header)

        student_lbl = QLabel("Seleccionar estudiante")
        student_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 600; font-family: 'Inter','Segoe UI',sans-serif;")
        root.addWidget(student_lbl)

        self._student_combo = QComboBox()
        self._student_combo.setFixedHeight(38)
        self._student_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {BG_CARD2}; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 10px;
                padding: 0 12px; font-size: 12px; font-weight: 600;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QComboBox:focus {{ border-color: {BORDER2}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox QAbstractItemView {{
                background-color: {BG_CARD}; color: {TEXT_SEC};
                border: 1px solid {BORDER}; selection-background-color: {BG_HOVER};
                selection-color: {TEXT_PRI};
            }}
        """)
        self._student_combo.currentIndexChanged.connect(self._on_student_changed)
        root.addWidget(self._student_combo)

        notes_lbl = QLabel("Notas (opcional)")
        notes_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 600; font-family: 'Inter','Segoe UI',sans-serif;")
        root.addWidget(notes_lbl)

        self._notes_edit = QTextEdit()
        self._notes_edit.setFixedHeight(80)
        self._notes_edit.setPlaceholderText("Notas sobre la inscripción...")
        self._notes_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {BG_CARD2}; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 10px;
                padding: 8px; font-size: 12px; font-weight: 500;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QTextEdit:focus {{ border-color: {BORDER2}; }}
        """)
        root.addWidget(self._notes_edit)

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

        btn_register = QPushButton("Inscribir")
        btn_register.setFixedHeight(36)
        btn_register.setMinimumWidth(110)
        btn_register.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_register.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED}; color: white;
                border: 1px solid {RED_H}; border-radius: 8px;
                font-size: 11px; font-weight: 700;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QPushButton:hover {{ background-color: {RED_H}; }}
        """)
        btn_register.clicked.connect(self._register)
        btn_row.addWidget(btn_register)

        root.addLayout(btn_row)

    def _load_students(self):
        try:
            self._students = self.repo.get_available_students_for_user(self.current_user_id)
            self._student_combo.addItem("— Seleccionar —", None)
            for s in self._students:
                name = f"{s.get('first_name', '')} {s.get('last_name', '')}".strip()
                self._student_combo.addItem(name or "Sin nombre", s.get("id"))
        except Exception as e:
            debug_log(f"[EventRegistration] Error cargando estudiantes: {e}")

    def _on_student_changed(self, index):
        self._selected_student_id = self._student_combo.currentData()

    def _register(self):
        if not self._selected_student_id:
            return
        try:
            notes = self._notes_edit.toPlainText().strip()
            result = self.repo.register_student(
                self.event_id,
                self.current_user_id,
                self._selected_student_id,
                notes,
            )
            if result:
                self.accept()
        except Exception as e:
            debug_log(f"[EventRegistration] Error inscribiendo: {e}")
