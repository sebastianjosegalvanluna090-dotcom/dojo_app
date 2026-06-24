# ─── STUDENT_FORM ─────────────────────────────────────────────
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QComboBox, QDateEdit, QPushButton,
    QLabel, QFrame, QMessageBox, QWidget, QCalendarWidget,
    QSizePolicy, QToolButton, QScrollArea
)
from PyQt6.QtCore import Qt, QDate, QLocale
from PyQt6.QtGui import QColor, QTextCharFormat, QFont

# ─── PALETA ───────────────────────────────────────────────────────────
BG_DARK   = "#0D0D0D"
BG_CARD   = "#141414"
BG_INPUT  = "#1C1C1C"
BORDER    = "#2A2A2A"
BORDER_F  = "#C8102E"
RED       = "#C8102E"
RED_H     = "#E8152F"
TEXT_PRI  = "#F0F0F0"
TEXT_SEC  = "#666666"
TEXT_MUT  = "#3A3A3A"
GREEN     = "#22C55E"
ERROR_C   = "#FF4444"

# Prefijos telefónicos
PHONE_PREFIXES = [
    ("🇦🇫", "+93", "Afganistán"),
    ("🇦🇱", "+355", "Albania"),
    ("🇩🇿", "+213", "Argelia"),
    ("🇦🇩", "+376", "Andorra"),
    ("🇦🇴", "+244", "Angola"),
    ("🇦🇷", "+54", "Argentina"),
    ("🇦🇲", "+374", "Armenia"),
    ("🇦🇺", "+61", "Australia"),
    ("🇦🇹", "+43", "Austria"),
    ("🇦🇿", "+994", "Azerbaiyán"),

    ("🇧🇸", "+1", "Bahamas"),
    ("🇧🇭", "+973", "Bahréin"),
    ("🇧🇩", "+880", "Bangladesh"),
    ("🇧🇾", "+375", "Bielorrusia"),
    ("🇧🇪", "+32", "Bélgica"),
    ("🇧🇿", "+501", "Belice"),
    ("🇧🇴", "+591", "Bolivia"),
    ("🇧🇦", "+387", "Bosnia y Herzegovina"),
    ("🇧🇷", "+55", "Brasil"),
    ("🇧🇬", "+359", "Bulgaria"),

    ("🇨🇦", "+1", "Canadá"),
    ("🇨🇱", "+56", "Chile"),
    ("🇨🇳", "+86", "China"),
    ("🇨🇴", "+57", "Colombia"),
    ("🇨🇷", "+506", "Costa Rica"),
    ("🇭🇷", "+385", "Croacia"),
    ("🇨🇺", "+53", "Cuba"),

    ("🇩🇰", "+45", "Dinamarca"),
    ("🇩🇴", "+1", "República Dominicana"),

    ("🇪🇨", "+593", "Ecuador"),
    ("🇪🇬", "+20", "Egipto"),
    ("🇸🇻", "+503", "El Salvador"),
    ("🇪🇸", "+34", "España"),
    ("🇺🇸", "+1", "Estados Unidos"),

    ("🇪🇪", "+372", "Estonia"),
    ("🇪🇹", "+251", "Etiopía"),

    ("🇵🇭", "+63", "Filipinas"),
    ("🇫🇮", "+358", "Finlandia"),
    ("🇫🇷", "+33", "Francia"),

    ("🇬🇪", "+995", "Georgia"),
    ("🇩🇪", "+49", "Alemania"),
    ("🇬🇷", "+30", "Grecia"),
    ("🇬🇹", "+502", "Guatemala"),

    ("🇭🇳", "+504", "Honduras"),
    ("🇭🇰", "+852", "Hong Kong"),
    ("🇭🇺", "+36", "Hungría"),

    ("🇮🇳", "+91", "India"),
    ("🇮🇩", "+62", "Indonesia"),
    ("🇮🇷", "+98", "Irán"),
    ("🇮🇪", "+353", "Irlanda"),
    ("🇮🇱", "+972", "Israel"),
    ("🇮🇹", "+39", "Italia"),

    ("🇯🇵", "+81", "Japón"),
    ("🇯🇴", "+962", "Jordania"),

    ("🇰🇿", "+7", "Kazajistán"),
    ("🇰🇪", "+254", "Kenia"),
    ("🇰🇷", "+82", "Corea del Sur"),

    ("🇱🇧", "+961", "Líbano"),
    ("🇱🇹", "+370", "Lituania"),
    ("🇱🇺", "+352", "Luxemburgo"),

    ("🇲🇾", "+60", "Malasia"),
    ("🇲🇽", "+52", "México"),
    ("🇲🇦", "+212", "Marruecos"),

    ("🇳🇱", "+31", "Países Bajos"),
    ("🇳🇿", "+64", "Nueva Zelanda"),
    ("🇳🇮", "+505", "Nicaragua"),
    ("🇳🇬", "+234", "Nigeria"),
    ("🇳🇴", "+47", "Noruega"),

    ("🇵🇰", "+92", "Pakistán"),
    ("🇵🇦", "+507", "Panamá"),
    ("🇵🇾", "+595", "Paraguay"),
    ("🇵🇪", "+51", "Perú"),
    ("🇵🇱", "+48", "Polonia"),
    ("🇵🇹", "+351", "Portugal"),

    ("🇬🇧", "+44", "Reino Unido"),
    ("🇨🇿", "+420", "República Checa"),
    ("🇷🇴", "+40", "Rumania"),
    ("🇷🇺", "+7", "Rusia"),

    ("🇸🇦", "+966", "Arabia Saudita"),
    ("🇸🇬", "+65", "Singapur"),
    ("🇿🇦", "+27", "Sudáfrica"),
    ("🇸🇪", "+46", "Suecia"),
    ("🇨🇭", "+41", "Suiza"),

    ("🇹🇭", "+66", "Tailandia"),
    ("🇹🇷", "+90", "Turquía"),

    ("🇦🇪", "+971", "Emiratos Árabes Unidos"),
    ("🇺🇦", "+380", "Ucrania"),
    ("🇺🇾", "+598", "Uruguay"),

    ("🇻🇪", "+58", "Venezuela"),
    ("🇻🇳", "+84", "Vietnam"),
]

FIELD_STYLE = f"""
    QLineEdit, QComboBox {{
        background-color: {BG_INPUT};
        color: {TEXT_PRI};
        border: 1.5px solid {BORDER};
        border-radius: 8px;
        padding: 0 12px;
        font-size: 13px;
        min-height: 40px;
        max-height: 40px;
    }}
    QLineEdit:focus, QComboBox:focus {{
        border-color: {BORDER_F};
        background-color: #1A0A0C;
    }}
    QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox QAbstractItemView {{
        background-color: #1C1C1C;
        color: {TEXT_PRI};
        selection-background-color: {RED};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 4px;
        font-size: 13px;
    }}
"""

CAL_STYLE = f"""
    QCalendarWidget {{
        background-color: #141414;
        color: {TEXT_PRI};
        border: none;
    }}
    QCalendarWidget QAbstractItemView {{
        background-color: #141414;
        color: {TEXT_PRI};
        selection-background-color: {RED};
        selection-color: white;
        font-size: 13px;
    }}
    QCalendarWidget QAbstractItemView:disabled {{
        color: #333333;
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background-color: #1C1C1C;
        border-radius: 8px;
        padding: 4px;
        min-height: 44px;
    }}
    QCalendarWidget QToolButton {{
        background-color: transparent;
        color: {TEXT_PRI};
        font-size: 13px;
        font-weight: 600;
        border: none;
        border-radius: 6px;
        padding: 4px 8px;
        min-width: 28px;
        min-height: 28px;
    }}
    QCalendarWidget QToolButton:hover {{
        background-color: #2A2A2A;
    }}
    QCalendarWidget QToolButton::menu-indicator {{ image: none; }}
    QCalendarWidget QSpinBox {{
        background-color: #1C1C1C;
        color: {TEXT_PRI};
        border: 1px solid {BORDER};
        border-radius: 6px;
        font-size: 13px;
        padding: 2px 6px;
    }}
    QCalendarWidget QMenu {{
        background-color: #1C1C1C;
        color: {TEXT_PRI};
        border: 1px solid {BORDER};
        border-radius: 8px;
        font-size: 13px;
    }}
    QCalendarWidget QMenu::item:selected {{
        background-color: {RED};
    }}
"""


def _lbl(text):
    l = QLabel(text)
    l.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 600; letter-spacing: 0.5px;")
    return l


def _divider():
    f = QFrame()
    f.setFixedHeight(1)
    f.setStyleSheet(f"background: {BORDER}; border: none;")
    return f


class StudentForm(QDialog):
    def __init__(self, repo, student_id: int = None, parent=None):
        super().__init__(parent)
        self.repo       = repo
        self.student_id = student_id
        self.is_edit    = student_id is not None
        self.created_credentials = None

        self.setWindowTitle("Editar Estudiante" if self.is_edit else "Nuevo Estudiante")
        self.setFixedSize(620, 720)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DARK}; color: {TEXT_PRI};")

        self._build_ui()
        self._load_combos()
        if self.is_edit:
            self._load_student()

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
        root.setContentsMargins(32, 28, 32, 24)
        root.setSpacing(0)

        hdr = QHBoxLayout()
        icon = QLabel("✏️" if self.is_edit else "➕")
        icon.setStyleSheet("font-size: 18px;")
        title = QLabel("Editar Estudiante" if self.is_edit else "Nuevo Estudiante")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT_PRI};")
        hdr.addWidget(icon)
        hdr.addSpacing(8)
        hdr.addWidget(title)
        hdr.addStretch()
        root.addLayout(hdr)
        root.addSpacing(12)

        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.4 {RED}, stop:1 transparent);
            border: none;
        """)
        root.addWidget(sep)
        root.addSpacing(24)

        root.addWidget(self._section_header("DATOS PERSONALES"))
        root.addSpacing(12)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(12)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        self.inp_first = QLineEdit()
        self.inp_first.setPlaceholderText("Nombre")
        self.inp_first.setStyleSheet(FIELD_STYLE)

        self.inp_last = QLineEdit()
        self.inp_last.setPlaceholderText("Apellido")
        self.inp_last.setStyleSheet(FIELD_STYLE)

        grid.addWidget(_lbl("Nombre *"),   0, 0)
        grid.addWidget(_lbl("Apellido *"), 0, 1)
        grid.addWidget(self.inp_first,     1, 0)
        grid.addWidget(self.inp_last,      1, 1)

        self.inp_email = QLineEdit()
        self.inp_email.setPlaceholderText("correo@ejemplo.com")
        self.inp_email.setStyleSheet(FIELD_STYLE)
        grid.addWidget(_lbl("Email"), 2, 0, 1, 2)
        grid.addWidget(self.inp_email, 3, 0, 1, 2)

        self.cmb_prefix = QComboBox()
        self.cmb_prefix.setFixedWidth(150)
        self.cmb_prefix.setStyleSheet(FIELD_STYLE)
        for flag, code, country in PHONE_PREFIXES:
            self.cmb_prefix.addItem(f"{flag}  {code}", code)
            self.cmb_prefix.setItemData(
                self.cmb_prefix.count() - 1, country, Qt.ItemDataRole.ToolTipRole
            )

        self.inp_phone = QLineEdit()
        self.inp_phone.setPlaceholderText("Número sin prefijo")
        self.inp_phone.setStyleSheet(FIELD_STYLE)

        phone_container = QWidget()
        phone_container.setStyleSheet("QWidget { background: transparent; border: none; }")
        phone_layout = QHBoxLayout(phone_container)
        phone_layout.setContentsMargins(0, 0, 0, 0)
        phone_layout.setSpacing(8)
        phone_layout.addWidget(self.cmb_prefix)
        phone_layout.addWidget(self.inp_phone, 1)

        grid.addWidget(_lbl("Teléfono"), 4, 0, 1, 2)
        grid.addWidget(phone_container,  5, 0, 1, 2)

        self._birth_date = QDate.currentDate().addYears(-18)
        self.inp_birth = QLineEdit()
        self.inp_birth.setReadOnly(True)
        self.inp_birth.setText(self._birth_date.toString("dd / MM / yyyy"))
        self.inp_birth.setStyleSheet(FIELD_STYLE)

        btn_cal_birth = QPushButton("📅")
        btn_cal_birth.setFixedSize(44, 42)
        btn_cal_birth.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cal_birth.setStyleSheet(f"""
            QPushButton {{
                background-color: #222; border: 1.5px solid {BORDER};
                border-radius: 8px; font-size: 16px;
            }}
            QPushButton:hover {{ border-color: {RED}; background-color: #2A2A2A; }}
        """)
        btn_cal_birth.clicked.connect(self._show_calendar)

        birth_row = QWidget()
        birth_row.setStyleSheet("QWidget { background: transparent; border: none; }")
        birth_hl = QHBoxLayout(birth_row)
        birth_hl.setContentsMargins(0, 0, 0, 0)
        birth_hl.setSpacing(8)
        birth_hl.addWidget(self.inp_birth, 1)
        birth_hl.addWidget(btn_cal_birth)

        self._joined_date = QDate.currentDate()
        self.inp_joined = QLineEdit()
        self.inp_joined.setReadOnly(True)
        self.inp_joined.setText(self._joined_date.toString("dd / MM / yyyy"))
        self.inp_joined.setStyleSheet(FIELD_STYLE)

        btn_cal_joined = QPushButton("📅")
        btn_cal_joined.setFixedSize(44, 42)
        btn_cal_joined.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cal_joined.setStyleSheet(f"""
            QPushButton {{
                background-color: #222; border: 1.5px solid {BORDER};
                border-radius: 8px; font-size: 16px;
            }}
            QPushButton:hover {{ border-color: {RED}; background-color: #2A2A2A; }}
        """)
        btn_cal_joined.clicked.connect(self._show_calendar_joined)

        joined_row = QWidget()
        joined_row.setStyleSheet("QWidget { background: transparent; border: none; }")
        joined_hl = QHBoxLayout(joined_row)
        joined_hl.setContentsMargins(0, 0, 0, 0)
        joined_hl.setSpacing(8)
        joined_hl.addWidget(self.inp_joined, 1)
        joined_hl.addWidget(btn_cal_joined)

        grid.addWidget(_lbl("Fecha de nacimiento"), 6, 0)
        grid.addWidget(_lbl("Fecha de ingreso al dojo"), 6, 1)
        grid.addWidget(birth_row,  7, 0)
        grid.addWidget(joined_row, 7, 1)

        root.addLayout(grid)
        root.addSpacing(24)

        root.addWidget(_divider())
        root.addSpacing(20)
        root.addWidget(self._section_header("INFORMACIÓN ACADÉMICA"))
        root.addSpacing(12)

        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(14)
        grid2.setVerticalSpacing(12)
        grid2.setColumnStretch(0, 1)
        grid2.setColumnStretch(1, 1)

        self.cmb_doctype  = QComboBox(); self.cmb_doctype.setStyleSheet(FIELD_STYLE)
        self.inp_doc      = QLineEdit(); self.inp_doc.setPlaceholderText("Número"); self.inp_doc.setStyleSheet(FIELD_STYLE)
        self.cmb_status   = QComboBox(); self.cmb_status.setStyleSheet(FIELD_STYLE)
        self.cmb_category = QComboBox(); self.cmb_category.setStyleSheet(FIELD_STYLE)

        grid2.addWidget(_lbl("Tipo documento"), 0, 0)
        grid2.addWidget(_lbl("Nº Documento"),   0, 1)
        grid2.addWidget(self.cmb_doctype,        1, 0)
        grid2.addWidget(self.inp_doc,            1, 1)
        grid2.addWidget(_lbl("Estado"),          2, 0)
        grid2.addWidget(_lbl("Categoría"),       2, 1)
        grid2.addWidget(self.cmb_status,         3, 0)
        grid2.addWidget(self.cmb_category,       3, 1)

        root.addLayout(grid2)
        root.addSpacing(12)
        root.addSpacing(20)
        root.addWidget(_divider())
        root.addSpacing(20)
        root.addWidget(self._section_header("ACCESO DEL ESTUDIANTE"))
        root.addSpacing(12)

        access_grid = QGridLayout()
        access_grid.setHorizontalSpacing(14)
        access_grid.setVerticalSpacing(12)
        access_grid.setColumnStretch(0, 1)
        access_grid.setColumnStretch(1, 1)

        self.inp_username = QLineEdit()
        self.inp_username.setPlaceholderText("Opcional. Si queda vacío se genera automático")
        self.inp_username.setStyleSheet(FIELD_STYLE)

        self.inp_password = QLineEdit()
        self.inp_password.setPlaceholderText(
            "Opcional. Si queda vacío usa el documento" if not self.is_edit else "Dejar vacío para no cambiar"
        )
        self.inp_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_password.setStyleSheet(FIELD_STYLE)

        access_grid.addWidget(_lbl("Usuario de acceso"), 0, 0)
        access_grid.addWidget(_lbl("Contraseña"), 0, 1)
        access_grid.addWidget(self.inp_username, 1, 0)
        access_grid.addWidget(self.inp_password, 1, 1)

        root.addLayout(access_grid)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(f"color: {ERROR_C}; font-size: 12px;")
        self.lbl_error.setWordWrap(True)
        root.addWidget(self.lbl_error)
        root.addStretch()

        scroll.setWidget(container)
        outer.addWidget(scroll)

        btn_area = QWidget()
        btn_area.setStyleSheet(f"background-color: {BG_DARK}; border-top: 1px solid {BORDER};")
        btn_hl = QHBoxLayout(btn_area)
        btn_hl.setContentsMargins(32, 14, 32, 14)
        btn_hl.setSpacing(10)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(42)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 8px; font-size: 13px;
            }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Guardar Cambios" if self.is_edit else "Crear Estudiante")
        self.btn_save.setFixedHeight(42)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED}; color: white;
                border: none; border-radius: 8px;
                font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: {RED_H}; }}
            QPushButton:pressed {{ background-color: #A00C24; }}
            QPushButton:disabled {{ background-color: #3A1A1A; color: #666; }}
        """)
        self.btn_save.clicked.connect(self._save)

        btn_hl.addWidget(btn_cancel)
        btn_hl.addWidget(self.btn_save)
        outer.addWidget(btn_area)

    def _section_header(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            font-size: 10px; font-weight: 700;
            letter-spacing: 1.5px; color: {TEXT_SEC};
        """)
        return lbl

    # ── Combos ────────────────────────────────────────────────────────
    def _load_combos(self):
        self.cmb_doctype.addItem("Seleccionar...", None)
        for doc_id, doc_name in self.repo.get_type_documents():
            self.cmb_doctype.addItem(doc_name, doc_id)

        self.cmb_status.addItem("Seleccionar...", None)
        for st_id, st_name in self.repo.get_statuses():
            self.cmb_status.addItem(st_name, st_id)

        self.cmb_category.addItem("Seleccionar...", None)
        for cat_id, cat_name in self.repo.get_categories():
            self.cmb_category.addItem(cat_name, cat_id)

    def _show_calendar(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Seleccionar fecha")
        dlg.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        dlg.setStyleSheet(f"background-color: #141414; color: {TEXT_PRI};")
        dlg.setFixedSize(320, 280)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        cal = QCalendarWidget()
        cal.setStyleSheet(CAL_STYLE)
        cal.setGridVisible(False)
        cal.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        cal.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        cal.setMaximumDate(QDate.currentDate())
        cal.setSelectedDate(self._birth_date)

        fmt_weekend = QTextCharFormat()
        fmt_weekend.setForeground(QColor(RED))
        cal.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, fmt_weekend)
        cal.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, fmt_weekend)

        btn_ok = QPushButton("Confirmar")
        btn_ok.setFixedHeight(38)
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED}; color: white;
                border: none; border-radius: 8px;
                font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: {RED_H}; }}
        """)

        def confirm():
            self._birth_date = cal.selectedDate()
            self.inp_birth.setText(self._birth_date.toString("dd / MM / yyyy"))
            dlg.accept()

        btn_ok.clicked.connect(confirm)
        cal.activated.connect(lambda _: confirm())

        layout.addWidget(cal)
        layout.addWidget(btn_ok)
        dlg.exec()

    def _show_calendar_joined(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Fecha de ingreso")
        dlg.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        dlg.setStyleSheet(f"background-color: #141414; color: {TEXT_PRI};")
        dlg.setFixedSize(320, 280)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        cal = QCalendarWidget()
        cal.setStyleSheet(CAL_STYLE)
        cal.setGridVisible(False)
        cal.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        cal.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        cal.setSelectedDate(self._joined_date)

        fmt_weekend = QTextCharFormat()
        fmt_weekend.setForeground(QColor(RED))
        cal.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, fmt_weekend)
        cal.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, fmt_weekend)

        btn_ok = QPushButton("Confirmar")
        btn_ok.setFixedHeight(38)
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED}; color: white;
                border: none; border-radius: 8px;
                font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: {RED_H}; }}
        """)

        def confirm():
            self._joined_date = cal.selectedDate()
            self.inp_joined.setText(self._joined_date.toString("dd / MM / yyyy"))
            dlg.accept()

        btn_ok.clicked.connect(confirm)
        cal.activated.connect(lambda _: confirm())

        layout.addWidget(cal)
        layout.addWidget(btn_ok)
        dlg.exec()

    # ── Cargar datos (edición) ─────────────────────────────────────────
    def _load_student(self):
        data = self.repo.get_by_id(self.student_id)
        if not data:
            return

        self.inp_first.setText(data["first_name"] or "")
        self.inp_last.setText(data["last_name"] or "")
        self.inp_email.setText(data["email"] or "")

        # Teléfono: separar prefijo y número
        phone = data.get("phone") or ""
        matched = False
        for i, (_, code, _) in enumerate(PHONE_PREFIXES):
            if phone.startswith(code):
                self.cmb_prefix.setCurrentIndex(i)
                self.inp_phone.setText(phone[len(code):].strip())
                matched = True
                break
        if not matched:
            self.inp_phone.setText(phone)

        if data["birthdate"]:
            d = data["birthdate"]
            self._birth_date = QDate(d.year, d.month, d.day)
            self.inp_birth.setText(self._birth_date.toString("dd / MM / yyyy"))

        if data.get("joined_date"):
            d = data["joined_date"]
            self._joined_date = QDate(d.year, d.month, d.day)
            self.inp_joined.setText(self._joined_date.toString("dd / MM / yyyy"))

        self.inp_doc.setText(data["document"] or "")

        for i in range(self.cmb_doctype.count()):
            if self.cmb_doctype.itemData(i) == data["id_type_document"]:
                self.cmb_doctype.setCurrentIndex(i); break

        for i in range(self.cmb_status.count()):
            if self.cmb_status.itemData(i) == data["id_status"]:
                self.cmb_status.setCurrentIndex(i); break

        for i in range(self.cmb_category.count()):
            if self.cmb_category.itemData(i) == data["category_id"]:
                self.cmb_category.setCurrentIndex(i); break

        user = self.repo.get_user_by_student_id(self.student_id)

        if user:
            self.inp_username.setText(user.get("username") or "")

    # ── Guardar ───────────────────────────────────────────────────────
    def _save(self):
        self.lbl_error.setText("")

        first = self.inp_first.text().strip()
        last  = self.inp_last.text().strip()

        if not first or not last:
            self.lbl_error.setText("⚠  Nombre y apellido son obligatorios.")
            return

        # Combinar prefijo + número
        prefix = self.cmb_prefix.currentData()
        number = self.inp_phone.text().strip()
        phone  = f"{prefix}{number}" if number else None

        birth = self._birth_date
        data = {
            "first_name":       first,
            "last_name":        last,
            "phone":            phone,
            "email":            self.inp_email.text().strip() or None,
            "birthdate":        birth.toPyDate(),
            "joined_date":      self._joined_date.toPyDate(),
            "document":         self.inp_doc.text().strip() or None,
            "id_type_document": self.cmb_doctype.currentData(),
            "id_status":        self.cmb_status.currentData(),
            "category_id":      self.cmb_category.currentData(),
            "username":         self.inp_username.text().strip(),
            "password":         self.inp_password.text().strip(),
        }

        self.btn_save.setEnabled(False)
        self.btn_save.setText("Guardando...")
        try:
            if self.is_edit:
                self.repo.update(self.student_id, data)
            else:
                result = self.repo.create(data)
                self.created_credentials = result

            self.accept()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")
            self.btn_save.setEnabled(True)
            self.btn_save.setText("Guardar Cambios" if self.is_edit else "Crear Estudiante")