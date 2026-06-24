# ─── EVENT_FORM ─────────────────────────────────────────────

from datetime import date

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit,
    QComboBox, QDateEdit, QTimeEdit, QMessageBox,
    QColorDialog, QCheckBox
)
from PyQt6.QtCore import Qt, QDate, QTime


BG_MAIN  = "#111111"
BORDER   = "#2A2A2A"
RED      = "#C8102E"
TEXT_PRI = "#F0F0F0"
TEXT_SEC = "#888888"
BLUE     = "#3B82F6"


class EventForm(QDialog):
    def __init__(
        self,
        repo,
        event_id=None,
        default_date=None,
        parent=None
    ):
        super().__init__(parent)

        self.repo = repo
        self.event_id = event_id
        self.default_date = default_date or date.today()
        self.selected_color = BLUE

        self.setWindowTitle("Evento")
        self.setFixedSize(540, 620)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_MAIN}; color: {TEXT_PRI};")

        self._build_ui()

        if self.event_id:
            self._load_data()
        else:
            self._apply_defaults()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("🎯  Datos del evento")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT_PRI};")
        root.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(12)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ej: Examen de grado")

        self.date_event = QDateEdit()
        self.date_event.setCalendarPopup(True)
        self.date_event.setDisplayFormat("dd/MM/yyyy")

        self.cmb_type = QComboBox()
        self.cmb_type.addItem("Torneo", "torneo")
        self.cmb_type.addItem("Examen de grado", "examen")
        self.cmb_type.addItem("Seminario", "seminario")
        self.cmb_type.addItem("Festivo", "festivo")
        self.cmb_type.addItem("Otro", "otro")

        self.input_location = QLineEdit()
        self.input_location.setPlaceholderText("Ej: Dojo principal")

        self.time_start = QTimeEdit()
        self.time_start.setDisplayFormat("HH:mm")
        self.time_start.setTime(QTime(0, 0))

        self.time_end = QTimeEdit()
        self.time_end.setDisplayFormat("HH:mm")
        self.time_end.setTime(QTime(0, 0))

        self.chk_has_time = QCheckBox("Usar hora")
        self.chk_has_time.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px;")
        self.chk_has_time.stateChanged.connect(self._toggle_time_inputs)

        self.chk_important = QCheckBox("Marcar como importante")
        self.chk_important.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px;")

        self.input_description = QTextEdit()
        self.input_description.setPlaceholderText("Descripción del evento...")
        self.input_description.setFixedHeight(100)

        self.btn_color = QPushButton("Seleccionar color")
        self.btn_color.setFixedHeight(34)
        self.btn_color.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_color.clicked.connect(self._select_color)

        for widget in [
            self.input_name,
            self.date_event,
            self.cmb_type,
            self.input_location,
            self.time_start,
            self.time_end,
            self.input_description,
            self.btn_color,
        ]:
            widget.setStyleSheet(self._input_style())

        form.addRow(self._label("Nombre"), self.input_name)
        form.addRow(self._label("Fecha"), self.date_event)
        form.addRow(self._label("Tipo"), self.cmb_type)
        form.addRow(self._label("Ubicación"), self.input_location)
        form.addRow(self._label("Horario"), self.chk_has_time)
        form.addRow(self._label("Hora inicio"), self.time_start)
        form.addRow(self._label("Hora fin"), self.time_end)
        form.addRow(self._label("Importante"), self.chk_important)
        form.addRow(self._label("Color"), self.btn_color)
        form.addRow(self._label("Descripción"), self.input_description)

        root.addLayout(form)
        root.addStretch()

        actions = QHBoxLayout()
        actions.setSpacing(10)

        if self.event_id:
            btn_delete = QPushButton("Eliminar")
            btn_delete.setFixedHeight(38)
            btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_delete.setStyleSheet(self._danger_button_style())
            btn_delete.clicked.connect(self._delete)
            actions.addWidget(btn_delete)

        actions.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(self._secondary_button_style())
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Guardar")
        btn_save.setFixedHeight(38)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(self._primary_button_style())
        btn_save.clicked.connect(self._save)

        actions.addWidget(btn_cancel)
        actions.addWidget(btn_save)

        root.addLayout(actions)

        self._toggle_time_inputs()
        self._update_color_button()

    def _apply_defaults(self):
        self.date_event.setDate(QDate(
            self.default_date.year,
            self.default_date.month,
            self.default_date.day
        ))
        self._update_color_button()

    def _load_data(self):
        data = self.repo.get_by_id(self.event_id)

        if not data:
            QMessageBox.warning(self, "Aviso", "No se encontró el evento.")
            self.reject()
            return

        self.input_name.setText(data.get("name") or "")

        event_date = data.get("event_date") or date.today()
        self.date_event.setDate(QDate(event_date.year, event_date.month, event_date.day))

        self._set_combo_value(self.cmb_type, data.get("event_type") or "otro")

        self.input_location.setText(data.get("location") or "")
        self.input_description.setPlainText(data.get("description") or "")

        self.selected_color = data.get("color") or BLUE

        if data.get("start_time") or data.get("end_time"):
            self.chk_has_time.setChecked(True)

        if data.get("start_time"):
            self.time_start.setTime(QTime(data["start_time"].hour, data["start_time"].minute))

        if data.get("end_time"):
            self.time_end.setTime(QTime(data["end_time"].hour, data["end_time"].minute))

        self.chk_important.setChecked(bool(data.get("is_important")))
        self._toggle_time_inputs()
        self._update_color_button()

    def _save(self):
        name = self.input_name.text().strip()

        if not name:
            QMessageBox.information(self, "Aviso", "Escribe el nombre del evento.")
            return

        use_time = self.chk_has_time.isChecked()

        if use_time and self.time_end.time() <= self.time_start.time():
            QMessageBox.information(self, "Aviso", "La hora fin debe ser mayor que la hora inicio.")
            return

        qdate = self.date_event.date()

        data = {
            "name": name,
            "event_date": qdate.toPyDate(),
            "event_type": self.cmb_type.currentData(),
            "description": self.input_description.toPlainText().strip() or None,
            "color": self.selected_color,
            "start_time": self.time_start.time().toString("HH:mm") if use_time else None,
            "end_time": self.time_end.time().toString("HH:mm") if use_time else None,
            "location": self.input_location.text().strip() or None,
            "is_important": self.chk_important.isChecked(),
        }

        try:
            if self.event_id:
                self.repo.update(self.event_id, data)
            else:
                self.repo.create(data)

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")

    def _delete(self):
        confirm = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Eliminar este evento?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete(self.event_id)
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{e}")

    def _toggle_time_inputs(self):
        enabled = self.chk_has_time.isChecked()
        self.time_start.setEnabled(enabled)
        self.time_end.setEnabled(enabled)

    def _select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()
            self._update_color_button()

    def _update_color_button(self):
        self.btn_color.setText(self.selected_color)
        self.btn_color.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.selected_color};
                color: white;
                border: none;
                border-radius: 7px;
                font-size: 12px;
                font-weight: 700;
            }}
        """)

    def _set_combo_value(self, combo, value):
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px;")
        return lbl

    def _input_style(self):
        return f"""
            QLineEdit, QComboBox, QDateEdit, QTimeEdit, QTextEdit {{
                background-color: #1E1E1E;
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 7px;
                min-height: 34px;
                padding: 0 10px;
                font-size: 12px;
            }}
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, QTextEdit:focus {{
                border-color: {RED};
            }}
        """

    def _primary_button_style(self):
        return f"""
            QPushButton {{
                background-color: {RED};
                color: white;
                border: none;
                border-radius: 7px;
                font-size: 13px;
                font-weight: 700;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background-color: #E8152F;
            }}
        """

    def _secondary_button_style(self):
        return f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SEC};
                border: 1px solid {BORDER};
                border-radius: 7px;
                font-size: 13px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
                border-color: #555;
            }}
        """

    def _danger_button_style(self):
        return """
            QPushButton {
                background: transparent;
                color: #FF4444;
                border: 1px solid #FF4444;
                border-radius: 7px;
                font-size: 13px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #2A0A0A;
            }
        """