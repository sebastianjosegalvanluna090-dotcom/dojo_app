"""
views/instructor_form.py
Formulario crear / editar instructor + permisos por arte marcial.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QPushButton, QLabel, QFrame,
    QWidget, QCalendarWidget, QScrollArea, QComboBox,
    QCheckBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QTextCharFormat

# ─── PALETA ───────────────────────────────────────────────────────────
BG_DARK   = "#0D0D0D"
BG_INPUT  = "#1C1C1C"
BG_ROW    = "#161616"
BG_ROW_H  = "#1E1E1E"
BORDER    = "#2A2A2A"
RED       = "#C8102E"
RED_H     = "#E8152F"
TEXT_PRI  = "#F0F0F0"
TEXT_SEC  = "#666666"
TEXT_MUT  = "#444444"
ERROR_C   = "#FF4444"
GREEN     = "#22C55E"
ORANGE    = "#F97316"

PHONE_PREFIXES = [
    ("🇨🇴", "+57",  "Colombia"),
    ("🇺🇸", "+1",   "Estados Unidos"),
    ("🇲🇽", "+52",  "México"),
    ("🇦🇷", "+54",  "Argentina"),
    ("🇨🇱", "+56",  "Chile"),
    ("🇵🇪", "+51",  "Perú"),
    ("🇻🇪", "+58",  "Venezuela"),
    ("🇪🇨", "+593", "Ecuador"),
    ("🇧🇷", "+55",  "Brasil"),
    ("🇪🇸", "+34",  "España"),
    ("🇬🇧", "+44",  "Reino Unido"),
    ("🇫🇷", "+33",  "Francia"),
    ("🇩🇪", "+49",  "Alemania"),
    ("🇯🇵", "+81",  "Japón"),
]

FIELD_STYLE = f"""
    QLineEdit, QComboBox {{
        background-color: {BG_INPUT}; color: {TEXT_PRI};
        border: 1.5px solid {BORDER}; border-radius: 8px;
        padding: 0 12px; font-size: 13px;
        min-height: 40px; max-height: 40px;
    }}
    QLineEdit:focus, QComboBox:focus {{ border-color: {RED}; background: #1A0A0C; }}
    QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox QAbstractItemView {{
        background: #1C1C1C; color: {TEXT_PRI};
        selection-background-color: {RED};
        border: 1px solid {BORDER}; border-radius: 6px;
    }}
"""

CAL_STYLE = f"""
    QCalendarWidget {{ background: #141414; color: {TEXT_PRI}; border: none; }}
    QCalendarWidget QAbstractItemView {{
        background: #141414; color: {TEXT_PRI};
        selection-background-color: {RED}; selection-color: white; font-size: 13px;
    }}
    QCalendarWidget QAbstractItemView:disabled {{ color: #333; }}
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background: #1C1C1C; border-radius: 8px; padding: 4px; min-height: 44px;
    }}
    QCalendarWidget QToolButton {{
        background: transparent; color: {TEXT_PRI}; font-size: 13px; font-weight: 600;
        border: none; border-radius: 6px; padding: 4px 8px;
    }}
    QCalendarWidget QToolButton:hover {{ background: #2A2A2A; }}
    QCalendarWidget QToolButton::menu-indicator {{ image: none; }}
    QCalendarWidget QSpinBox {{
        background: #1C1C1C; color: {TEXT_PRI}; border: 1px solid {BORDER};
        border-radius: 6px; font-size: 13px; padding: 2px 6px;
    }}
"""

CHECK_STYLE = """
    QCheckBox {
        color: #F0F0F0;
        font-size: 13px;
        spacing: 8px;
        background: transparent;
        border: none;
    }
    QCheckBox::indicator {
        width: 18px; height: 18px;
        border-radius: 5px;
        border: 1.5px solid #444;
        background: #1C1C1C;
    }
    QCheckBox::indicator:checked {
        background: #C8102E;
        border-color: #C8102E;
        image: none;
    }
    QCheckBox::indicator:hover { border-color: #C8102E; }
"""

CHECK_PROMOTE_STYLE = """
    QCheckBox {
        color: #F97316;
        font-size: 13px;
        spacing: 8px;
        background: transparent;
        border: none;
    }
    QCheckBox::indicator {
        width: 18px; height: 18px;
        border-radius: 5px;
        border: 1.5px solid #444;
        background: #1C1C1C;
    }
    QCheckBox::indicator:checked {
        background: #F97316;
        border-color: #F97316;
    }
    QCheckBox::indicator:hover { border-color: #F97316; }
"""


def _lbl(text, color=None):
    l = QLabel(text)
    c = color or TEXT_SEC
    l.setStyleSheet(f"color: {c}; font-size: 11px; font-weight: 600; letter-spacing: 0.5px;")
    return l


# ── Widget de permisos por arte marcial ───────────────────────────────
class MartialArtsPermissionsWidget(QWidget):
    """
    Muestra una fila por arte marcial con dos checkboxes:
      ✅ Puede dictar clases   🥋 Puede dar ascensos
    La regla can_promote se deshabilita si can_teach está desmarcado.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self._rows: list[dict] = []   # {"id_martial_art", "chk_teach", "chk_promote"}
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)

    def load(self, permissions: list):
        """
        permissions: lista de dicts del repo.get_permissions()
        [{"id_martial_art", "name", "can_teach", "can_promote"}]
        """
        # Limpiar
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._rows.clear()

        if not permissions:
            lbl = QLabel("No hay artes marciales registradas.")
            lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px;")
            self._layout.addWidget(lbl)
            return

        # Cabecera
        hdr = QWidget()
        hdr.setStyleSheet("background: transparent;")
        hdr_l = QHBoxLayout(hdr)
        hdr_l.setContentsMargins(12, 4, 12, 4)
        hdr_l.setSpacing(0)
        lbl_art = QLabel("ARTE MARCIAL")
        lbl_art.setStyleSheet(f"font-size: 10px; font-weight: 700; letter-spacing: 1px; color: {TEXT_MUT};")
        lbl_teach = QLabel("CLASES")
        lbl_teach.setStyleSheet(f"font-size: 10px; font-weight: 700; letter-spacing: 1px; color: {TEXT_MUT};")
        lbl_teach.setFixedWidth(100)
        lbl_teach.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_prom = QLabel("ASCENSOS")
        lbl_prom.setStyleSheet(f"font-size: 10px; font-weight: 700; letter-spacing: 1px; color: {TEXT_MUT};")
        lbl_prom.setFixedWidth(110)
        lbl_prom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr_l.addWidget(lbl_art, 1)
        hdr_l.addWidget(lbl_teach)
        hdr_l.addWidget(lbl_prom)
        self._layout.addWidget(hdr)

        sep = QFrame(); sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        self._layout.addWidget(sep)

        # Filas
        for i, perm in enumerate(permissions):
            row_w = QWidget()
            bg = BG_ROW if i % 2 == 0 else BG_ROW_H
            row_w.setStyleSheet(f"background-color: {bg}; border-radius: 8px;")
            row_l = QHBoxLayout(row_w)
            row_l.setContentsMargins(12, 10, 12, 10)
            row_l.setSpacing(0)

            # Nombre del arte marcial
            lbl_name = QLabel(f"🥋  {perm['name']}")
            lbl_name.setStyleSheet(f"color: {TEXT_PRI}; font-size: 13px; font-weight: 500;")

            # Checkbox dictar clases
            chk_teach = QCheckBox("Sí")
            chk_teach.setStyleSheet(CHECK_STYLE)
            chk_teach.setChecked(perm["can_teach"])
            chk_teach.setFixedWidth(100)

            # Checkbox dar ascensos
            chk_promote = QCheckBox("Sí")
            chk_promote.setStyleSheet(CHECK_PROMOTE_STYLE)
            chk_promote.setChecked(perm["can_promote"])
            chk_promote.setFixedWidth(110)
            chk_promote.setEnabled(perm["can_teach"])  # solo activo si puede dictar

            # Regla: al desmarcar can_teach → desmarcar y deshabilitar can_promote
            def _on_teach_changed(state, cp=chk_promote):
                enabled = (state == Qt.CheckState.Checked.value or state == 2)
                cp.setEnabled(enabled)
                if not enabled:
                    cp.setChecked(False)

            chk_teach.stateChanged.connect(_on_teach_changed)

            row_l.addWidget(lbl_name, 1)
            row_l.addWidget(chk_teach)
            row_l.addWidget(chk_promote)

            self._layout.addWidget(row_w)
            self._rows.append({
                "id_martial_art": perm["id_martial_art"],
                "chk_teach":      chk_teach,
                "chk_promote":    chk_promote,
            })

    def get_permissions(self) -> list:
        """Devuelve la lista de permisos lista para guardar en el repo."""
        return [
            {
                "id_martial_art": r["id_martial_art"],
                "can_teach":      r["chk_teach"].isChecked(),
                "can_promote":    r["chk_promote"].isChecked(),
            }
            for r in self._rows
        ]


# ── Formulario principal ──────────────────────────────────────────────
class InstructorForm(QDialog):
    def __init__(self, repo, instructor_id: int = None, parent=None):
        super().__init__(parent)
        self.repo          = repo
        self.instructor_id = instructor_id
        self.is_edit       = instructor_id is not None
        self._birth_date   = QDate.currentDate().addYears(-25)

        self.setWindowTitle("Editar Instructor" if self.is_edit else "Nuevo Instructor")
        self.setFixedSize(600, 680)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DARK}; color: {TEXT_PRI};")

        self._build_ui()
        if self.is_edit:
            self._load_data()
        self._load_permissions()

    # ── UI ────────────────────────────────────────────────────────────
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container.setStyleSheet(f"background-color: {BG_DARK};")
        root = QVBoxLayout(container)
        root.setContentsMargins(32, 28, 32, 20)
        root.setSpacing(0)

        # ── Encabezado
        hdr = QHBoxLayout()
        icon = QLabel("✏️" if self.is_edit else "➕")
        icon.setStyleSheet("font-size: 18px;")
        title = QLabel("Editar Instructor" if self.is_edit else "Nuevo Instructor")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT_PRI};")
        hdr.addWidget(icon); hdr.addSpacing(8); hdr.addWidget(title); hdr.addStretch()
        root.addLayout(hdr)
        root.addSpacing(12)

        sep = QFrame(); sep.setFixedHeight(2)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.4 {RED}, stop:1 transparent); border: none;
        """)
        root.addWidget(sep)
        root.addSpacing(22)

        # ── Sección datos personales
        root.addWidget(self._sec_hdr("DATOS PERSONALES"))
        root.addSpacing(12)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14); grid.setVerticalSpacing(12)
        grid.setColumnStretch(0, 1); grid.setColumnStretch(1, 1)

        self.inp_first = QLineEdit(); self.inp_first.setPlaceholderText("Nombre"); self.inp_first.setStyleSheet(FIELD_STYLE)
        self.inp_last  = QLineEdit(); self.inp_last.setPlaceholderText("Apellido"); self.inp_last.setStyleSheet(FIELD_STYLE)
        grid.addWidget(_lbl("Nombre *"),   0, 0); grid.addWidget(_lbl("Apellido *"), 0, 1)
        grid.addWidget(self.inp_first,     1, 0); grid.addWidget(self.inp_last,      1, 1)

        self.inp_email = QLineEdit(); self.inp_email.setPlaceholderText("correo@ejemplo.com"); self.inp_email.setStyleSheet(FIELD_STYLE)
        grid.addWidget(_lbl("Email"), 2, 0, 1, 2)
        grid.addWidget(self.inp_email, 3, 0, 1, 2)

        self.cmb_prefix = QComboBox(); self.cmb_prefix.setFixedWidth(140); self.cmb_prefix.setStyleSheet(FIELD_STYLE)
        for flag, code, _ in PHONE_PREFIXES:
            self.cmb_prefix.addItem(f"{flag}  {code}", code)

        self.inp_phone = QLineEdit(); self.inp_phone.setPlaceholderText("Número sin prefijo"); self.inp_phone.setStyleSheet(FIELD_STYLE)
        phone_w = QWidget(); phone_w.setStyleSheet("background: transparent; border: none;")
        phone_hl = QHBoxLayout(phone_w); phone_hl.setContentsMargins(0,0,0,0); phone_hl.setSpacing(8)
        phone_hl.addWidget(self.cmb_prefix); phone_hl.addWidget(self.inp_phone, 1)
        grid.addWidget(_lbl("Teléfono"), 4, 0, 1, 2)
        grid.addWidget(phone_w, 5, 0, 1, 2)

        self.inp_birth = QLineEdit(); self.inp_birth.setReadOnly(True)
        self.inp_birth.setText(self._birth_date.toString("dd / MM / yyyy"))
        self.inp_birth.setStyleSheet(FIELD_STYLE)
        btn_cal = QPushButton("📅"); btn_cal.setFixedSize(44, 42)
        btn_cal.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cal.setStyleSheet(f"""
            QPushButton {{ background: #222; border: 1.5px solid {BORDER};
                border-radius: 8px; font-size: 16px; }}
            QPushButton:hover {{ border-color: {RED}; }}
        """)
        btn_cal.clicked.connect(self._show_calendar)
        birth_w = QWidget(); birth_w.setStyleSheet("background: transparent; border: none;")
        birth_hl = QHBoxLayout(birth_w); birth_hl.setContentsMargins(0,0,0,0); birth_hl.setSpacing(8)
        birth_hl.addWidget(self.inp_birth, 1); birth_hl.addWidget(btn_cal)
        grid.addWidget(_lbl("Fecha de nacimiento"), 6, 0, 1, 2)
        grid.addWidget(birth_w, 7, 0, 1, 2)

        root.addLayout(grid)
        root.addSpacing(28)

        # ── Separador
        div = QFrame(); div.setFixedHeight(1)
        div.setStyleSheet(f"background: {BORDER}; border: none;")
        root.addWidget(div)
        root.addSpacing(22)

        # ── Sección permisos
        perm_hdr = QHBoxLayout()
        perm_hdr.addWidget(self._sec_hdr("PERMISOS POR ARTE MARCIAL"))
        perm_hdr.addStretch()
        tip = QLabel("🔴 Clases  🟠 Ascensos")
        tip.setStyleSheet(f"font-size: 11px; color: {TEXT_MUT};")
        perm_hdr.addWidget(tip)
        root.addLayout(perm_hdr)
        root.addSpacing(10)

        # Leyenda
        legend = QHBoxLayout(); legend.setSpacing(20)
        for color, icon, text in [
            (GREEN,  "✅", "Puede dictar clases en ese arte"),
            (ORANGE, "🥋", "Puede dar ascensos de cinturón"),
        ]:
            dot = QLabel(icon); dot.setStyleSheet("font-size: 13px;")
            lbl = QLabel(text); lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px;")
            legend.addWidget(dot); legend.addWidget(lbl)
        legend.addStretch()
        root.addLayout(legend)
        root.addSpacing(10)

        # Widget de permisos
        self.perms_widget = MartialArtsPermissionsWidget()
        root.addWidget(self.perms_widget)
        root.addSpacing(12)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(f"color: {ERROR_C}; font-size: 12px;")
        self.lbl_error.setWordWrap(True)
        root.addWidget(self.lbl_error)
        root.addStretch()

        scroll.setWidget(container)
        outer.addWidget(scroll)

        # ── Botones fijos
        btn_area = QWidget()
        btn_area.setStyleSheet(f"background-color: {BG_DARK}; border-top: 1px solid {BORDER};")
        btn_hl = QHBoxLayout(btn_area)
        btn_hl.setContentsMargins(32, 14, 32, 14); btn_hl.setSpacing(10)

        btn_cancel = QPushButton("Cancelar"); btn_cancel.setFixedHeight(42)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 8px; font-size: 13px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Guardar Cambios" if self.is_edit else "Crear Instructor")
        self.btn_save.setFixedHeight(42)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white; border: none;
                border-radius: 8px; font-size: 13px; font-weight: 700; }}
            QPushButton:hover {{ background: {RED_H}; }}
            QPushButton:disabled {{ background: #3A1A1A; color: #666; }}
        """)
        self.btn_save.clicked.connect(self._save)

        btn_hl.addWidget(btn_cancel); btn_hl.addWidget(self.btn_save)
        outer.addWidget(btn_area)

    def _sec_hdr(self, text):
        l = QLabel(text)
        l.setStyleSheet(f"font-size: 10px; font-weight: 700; letter-spacing: 1.5px; color: {TEXT_SEC};")
        return l

    # ── Calendario ────────────────────────────────────────────────────
    def _show_calendar(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Fecha de nacimiento")
        dlg.setFixedSize(320, 280)
        dlg.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        dlg.setStyleSheet("background-color: #141414;")
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(12, 12, 12, 12); layout.setSpacing(10)

        cal = QCalendarWidget()
        cal.setStyleSheet(CAL_STYLE); cal.setGridVisible(False)
        cal.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        cal.setMaximumDate(QDate.currentDate())
        cal.setSelectedDate(self._birth_date)
        fmt = QTextCharFormat(); fmt.setForeground(QColor(RED))
        cal.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, fmt)
        cal.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, fmt)

        btn_ok = QPushButton("Confirmar"); btn_ok.setFixedHeight(38)
        btn_ok.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white; border: none;
                border-radius: 8px; font-size: 13px; font-weight: 700; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)

        def confirm():
            self._birth_date = cal.selectedDate()
            self.inp_birth.setText(self._birth_date.toString("dd / MM / yyyy"))
            dlg.accept()

        btn_ok.clicked.connect(confirm)
        cal.activated.connect(lambda _: confirm())
        layout.addWidget(cal); layout.addWidget(btn_ok)
        dlg.exec()

    # ── Cargar datos ──────────────────────────────────────────────────
    def _load_data(self):
        data = self.repo.get_by_id(self.instructor_id)
        if not data:
            return
        self.inp_first.setText(data["first_name"] or "")
        self.inp_last.setText(data["last_name"] or "")
        self.inp_email.setText(data["email"] or "")

        phone = data.get("phone") or ""
        for i, (_, code, _) in enumerate(PHONE_PREFIXES):
            if phone.startswith(code):
                self.cmb_prefix.setCurrentIndex(i)
                self.inp_phone.setText(phone[len(code):].strip())
                break
        else:
            self.inp_phone.setText(phone)

        if data["birthdate"]:
            d = data["birthdate"]
            self._birth_date = QDate(d.year, d.month, d.day)
            self.inp_birth.setText(self._birth_date.toString("dd / MM / yyyy"))

    def _load_permissions(self):
        """Carga permisos si es edición; si es nuevo, carga todas las artes con False."""
        if self.is_edit:
            perms = self.repo.get_permissions(self.instructor_id)
        else:
            # Nuevo: todas las artes marciales sin permisos
            perms = [
                {"id_martial_art": ma["id"], "name": ma["name"],
                 "can_teach": False, "can_promote": False}
                for ma in self.repo.get_martial_arts()
            ]
        self.perms_widget.load(perms)

    # ── Guardar ───────────────────────────────────────────────────────
    def _save(self):
        self.lbl_error.setText("")
        first = self.inp_first.text().strip()
        last  = self.inp_last.text().strip()

        if not first or not last:
            self.lbl_error.setText("⚠  Nombre y apellido son obligatorios.")
            return

        email = self.inp_email.text().strip() or None
        if email:
            exclude_pid = None
            if self.is_edit:
                current = self.repo.get_by_id(self.instructor_id)
                exclude_pid = current["id_person"] if current else None
            if self.repo.email_exists(email, exclude_pid):
                self.lbl_error.setText("⚠  Este email ya está registrado.")
                return

        prefix = self.cmb_prefix.currentData()
        number = self.inp_phone.text().strip()
        phone  = f"{prefix}{number}" if number else None

        data = {
            "first_name": first, "last_name": last,
            "phone": phone, "email": email,
            "birthdate": self._birth_date.toPyDate(),
        }

        self.btn_save.setEnabled(False)
        self.btn_save.setText("Guardando...")
        try:
            if self.is_edit:
                self.repo.update(self.instructor_id, data)
                instructor_id = self.instructor_id
            else:
                instructor_id = self.repo.create(data)

            # Guardar permisos
            self.repo.save_permissions(instructor_id, self.perms_widget.get_permissions())
            self.accept()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")
            self.btn_save.setEnabled(True)
            self.btn_save.setText("Guardar Cambios" if self.is_edit else "Crear Instructor")