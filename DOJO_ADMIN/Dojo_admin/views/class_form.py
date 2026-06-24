# ─── CLASS_FORM ─────────────────────────────────────────────

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QComboBox,
    QSpinBox, QTimeEdit, QMessageBox, QColorDialog
)
from PyQt6.QtCore import Qt, QTime


BG_MAIN  = "#111111"
BG_CARD  = "#161616"
BORDER   = "#2A2A2A"
RED      = "#C8102E"
TEXT_PRI = "#F0F0F0"
TEXT_SEC = "#888888"
TEXT_MUT = "#555555"
BLUE     = "#3B82F6"


class ClassForm(QDialog):
    def __init__(
        self,
        repo,
        schedule_id=None,
        default_day=None,
        default_hour=None,
        parent=None
    ):
        super().__init__(parent)

        self.repo = repo
        self.schedule_id = schedule_id
        self.default_day = default_day
        self.default_hour = default_hour
        self.selected_color = BLUE

        self.setWindowTitle("Clase")
        self.setFixedSize(520, 560)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_MAIN}; color: {TEXT_PRI};")

        self._build_ui()
        self._load_options()

        if self.schedule_id:
            self._load_data()
        else:
            self._apply_defaults()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("🗓️  Datos de la clase")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {TEXT_PRI};")
        root.addWidget(title)

        form_wrap = QLabel()
        form_wrap.setStyleSheet("background: transparent;")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(12)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ej: BJJ Adultos")

        self.cmb_martial_art = QComboBox()
        self.cmb_instructor = QComboBox()

        self.cmb_day = QComboBox()
        for idx, name in enumerate([
            "Lunes", "Martes", "Miércoles", "Jueves",
            "Viernes", "Sábado", "Domingo"
        ]):
            self.cmb_day.addItem(name, idx)

        self.time_start = QTimeEdit()
        self.time_start.setDisplayFormat("HH:mm")

        self.time_end = QTimeEdit()
        self.time_end.setDisplayFormat("HH:mm")

        self.spin_capacity = QSpinBox()
        self.spin_capacity.setRange(0, 999)
        self.spin_capacity.setSpecialValueText("Sin cupo")
        self.spin_capacity.setValue(0)

        self.input_location = QLineEdit()
        self.input_location.setPlaceholderText("Ej: Tatami principal")

        self.cmb_status = QComboBox()
        self.cmb_status.addItem("Activa", "active")
        self.cmb_status.addItem("Inactiva", "inactive")
        self.cmb_status.addItem("Cancelada", "canceled")

        self.cmb_repeat = QComboBox()
        self.cmb_repeat.addItem("Semanal", "weekly")

        self.btn_color = QPushButton("Seleccionar color")
        self.btn_color.setFixedHeight(34)
        self.btn_color.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_color.clicked.connect(self._select_color)

        for widget in [
            self.input_name,
            self.cmb_martial_art,
            self.cmb_instructor,
            self.cmb_day,
            self.time_start,
            self.time_end,
            self.spin_capacity,
            self.input_location,
            self.cmb_status,
            self.cmb_repeat,
            self.btn_color,
        ]:
            widget.setStyleSheet(self._input_style())

        form.addRow(self._label("Nombre"), self.input_name)
        form.addRow(self._label("Arte marcial"), self.cmb_martial_art)
        form.addRow(self._label("Instructor"), self.cmb_instructor)
        form.addRow(self._label("Día"), self.cmb_day)
        form.addRow(self._label("Hora inicio"), self.time_start)
        form.addRow(self._label("Hora fin"), self.time_end)
        form.addRow(self._label("Capacidad"), self.spin_capacity)
        form.addRow(self._label("Ubicación"), self.input_location)
        form.addRow(self._label("Estado"), self.cmb_status)
        form.addRow(self._label("Repetición"), self.cmb_repeat)
        form.addRow(self._label("Color"), self.btn_color)

        root.addLayout(form)

        root.addStretch()

        actions = QHBoxLayout()
        actions.setSpacing(10)

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

    def _load_options(self):
        try:
            opts = self.repo.get_form_options()

            self.cmb_martial_art.clear()
            self.cmb_martial_art.addItem("Seleccionar...", None)
            for ma_id, ma_name in opts.get("martial_arts", []):
                self.cmb_martial_art.addItem(ma_name, ma_id)

            self.cmb_instructor.clear()
            self.cmb_instructor.addItem("Seleccionar...", None)
            for ins_id, ins_name in opts.get("instructors", []):
                self.cmb_instructor.addItem(ins_name, ins_id)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar opciones:\n{e}")

    def _apply_defaults(self):
        if self.default_day is not None:
            index = self.cmb_day.findData(self.default_day)
            if index >= 0:
                self.cmb_day.setCurrentIndex(index)

        hour = int(self.default_hour or 18)
        self.time_start.setTime(QTime(hour, 0))
        self.time_end.setTime(QTime(min(hour + 1, 23), 0))
        self._update_color_button()

    def _load_data(self):
        data = self.repo.get_by_id(self.schedule_id)

        if not data:
            QMessageBox.warning(self, "Aviso", "No se encontró la clase.")
            self.reject()
            return

        self.input_name.setText(data.get("name") or "")

        self._set_combo_value(self.cmb_martial_art, data.get("id_martial_art"))
        self._set_combo_value(self.cmb_instructor, data.get("id_instructor"))
        self._set_combo_value(self.cmb_day, data.get("day_of_week"))
        self._set_combo_value(self.cmb_status, data.get("status") or "active")
        self._set_combo_value(self.cmb_repeat, data.get("repeat_type") or "weekly")

        if data.get("start_time"):
            self.time_start.setTime(QTime(data["start_time"].hour, data["start_time"].minute))

        if data.get("end_time"):
            self.time_end.setTime(QTime(data["end_time"].hour, data["end_time"].minute))

        self.spin_capacity.setValue(int(data.get("capacity") or 0))
        self.input_location.setText(data.get("location") or "")

        self.selected_color = data.get("color") or BLUE
        self._update_color_button()

    def _save(self):
        name = self.input_name.text().strip()

        if not name:
            QMessageBox.information(self, "Aviso", "Escribe el nombre de la clase.")
            return

        if self.cmb_martial_art.currentData() is None:
            QMessageBox.information(self, "Aviso", "Selecciona un arte marcial.")
            return

        if self.cmb_instructor.currentData() is None:
            QMessageBox.information(self, "Aviso", "Selecciona un instructor.")
            return

        if self.time_end.time() <= self.time_start.time():
            QMessageBox.information(self, "Aviso", "La hora fin debe ser mayor que la hora inicio.")
            return

        capacity = self.spin_capacity.value()
        data = {
            "name": name,
            "id_martial_art": self.cmb_martial_art.currentData(),
            "id_instructor": self.cmb_instructor.currentData(),
            "day_of_week": self.cmb_day.currentData(),
            "start_time": self.time_start.time().toString("HH:mm"),
            "end_time": self.time_end.time().toString("HH:mm"),
            "capacity": capacity if capacity > 0 else None,
            "location": self.input_location.text().strip() or None,
            "color": self.selected_color,
            "status": self.cmb_status.currentData(),
            "repeat_type": self.cmb_repeat.currentData(),
        }

        try:
            if self.schedule_id:
                self.repo.update_schedule(self.schedule_id, data)
            else:
                self.repo.create_schedule(data)

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")

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
            QLineEdit, QComboBox, QTimeEdit, QSpinBox {{
                background-color: #1E1E1E;
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 7px;
                min-height: 34px;
                padding: 0 10px;
                font-size: 12px;
            }}
            QLineEdit:focus, QComboBox:focus, QTimeEdit:focus, QSpinBox:focus {{
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
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
                border-color: #555;
            }}
        """