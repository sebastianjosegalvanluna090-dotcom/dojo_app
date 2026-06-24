# ─── ESTUDENTS_VIEW ─────────────────────────────────────────────

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QMessageBox, QDialog,
    QFormLayout, QScrollArea, QSizePolicy, QFileDialog,
    QGraphicsOpacityEffect, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QPixmap, QPainter, QPainterPath

from repositories.student_repository import StudentRepository
from views.student_form import StudentForm

# ─── PALETA ───────────────────────────────────────────────────────────
BG_MAIN    = "#0D0D0D"
BG_CARD    = "#161616"
BG_TABLE   = "#121212"
BORDER     = "#2A2A2A"
RED        = "#C8102E"
RED_DARK   = "#7A0A1C"
TEXT_PRI   = "#F0F0F0"
TEXT_SEC   = "#888888"
TEXT_MUT   = "#444444"
GREEN      = "#22C55E"
BLUE       = "#3B82F6"
YELLOW     = "#EAB308"


# ─── Worker ───────────────────────────────────────────────────────────
class LoadWorker(QThread):
    done = pyqtSignal(list)

    def __init__(self, repo, search="", filters=None):
        super().__init__()
        self.repo = repo
        self.search = search
        self.filters = filters or {}

    def run(self):
        try:
            data = self.repo.get_all(self.search, self.filters)
            self.done.emit(data)
        except Exception as e:
            print(f"[Students error] {e}")
            self.done.emit([])

# ─── DETALLE AMPLIADO ─────────────────────────────────────────────────
class StudentDetail(QDialog):
    def __init__(self, student_id, repo, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.repo = repo
        self.setWindowTitle("Detalle del Estudiante")
        self.setFixedSize(700, 620)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet("background-color: #111111; color: #F0F0F0;")

        data = repo.get_detail(student_id)
        belt_history = repo.get_belt_history(student_id)
        last_classes = repo.get_last_classes(student_id)
        photo_path = repo.get_photo(student_id)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        # ── Cabecera con avatar / foto + nombre
        header = QHBoxLayout()
        header.setSpacing(16)

        self.lbl_photo = QLabel()
        self.lbl_photo.setFixedSize(72, 72)
        self.lbl_photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_photo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_photo.setToolTip("Clic para cambiar foto")
        self._set_photo(photo_path, data.get("nombre", "?"))
        self.lbl_photo.mousePressEvent = lambda _: self._change_photo()

        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        lbl_name = QLabel(data.get("nombre", "—"))
        lbl_name.setStyleSheet("font-size: 17px; font-weight: 700; color: #F0F0F0;")
        lbl_sub = QLabel(
            f"ID: {data.get('id', '—')}  ·  "
            f"{data.get('tipo_doc', '—')}: {data.get('documento', '—')}  ·  "
            f"{data.get('categoria', '—')}"
        )
        lbl_sub.setStyleSheet("font-size: 11px; color: #666666;")
        name_col.addWidget(lbl_name)
        name_col.addWidget(lbl_sub)

        estado = data.get("estado", "—")
        badge_color = "#22C55E" if "activo" in estado.lower() else "#FF4444"
        badge_bg = "#0A2A0A" if "activo" in estado.lower() else "#2A0A0A"
        lbl_badge = QLabel(estado.capitalize())
        lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_badge.setFixedHeight(26)
        lbl_badge.setStyleSheet(f"""
            background-color: {badge_bg};
            color: {badge_color};
            border: 1px solid {badge_color};
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            padding: 0 12px;
        """)

        header.addWidget(self.lbl_photo)
        header.addLayout(name_col, 1)
        header.addWidget(lbl_badge, 0, Qt.AlignmentFlag.AlignTop)
        root.addLayout(header)

        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #C8102E, stop:0.4 #C8102E, stop:1 transparent);
            border: none;
        """)
        root.addWidget(sep)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        left_card = self._make_card()
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(4)
        left_layout.addWidget(self._section_label("DATOS PERSONALES"))
        left_layout.addLayout(self._data_row("Teléfono", data.get("telefono", "—")))
        left_layout.addLayout(self._data_row("Email", data.get("email", "—")))
        left_layout.addLayout(self._data_row("Nacimiento", data.get("nacimiento", "—")))
        left_layout.addLayout(self._data_row("Ingreso", data.get("fecha_ingreso", "—")))
        left_layout.addStretch()

        right_card = self._make_card()
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(14, 14, 14, 14)
        right_layout.setSpacing(4)
        right_layout.addWidget(self._section_label("MEMBRESÍA"))
        right_layout.addLayout(self._data_row("Plan", data.get("membresia", "—")))
        cuota = data.get("cuota")
        right_layout.addLayout(self._data_row("Cuota", f"${cuota}" if cuota and cuota != "—" else "—", "#22C55E"))
        right_layout.addLayout(self._data_row("Inicio", data.get("inicio_mem", "—")))
        right_layout.addLayout(self._data_row("Vence", data.get("fin_mem", "—"), "#EAB308"))

        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet("background: #2A2A2A; border: none; margin: 4px 0;")
        right_layout.addWidget(sep2)
        right_layout.addWidget(self._section_label("CINTURÓN"))
        right_layout.addLayout(self._data_row("Arte marcial", data.get("arte_marcial", "—")))
        right_layout.addLayout(self._data_row("Cinturón", data.get("cinturon", "—")))
        right_layout.addStretch()

        top_row.addWidget(left_card)
        top_row.addWidget(right_card)
        root.addLayout(top_row)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)

        belt_card = self._make_card()
        belt_layout = QVBoxLayout(belt_card)
        belt_layout.setContentsMargins(14, 12, 14, 12)
        belt_layout.setSpacing(6)
        belt_layout.addWidget(self._section_label("HISTORIAL DE CINTURONES"))

        if belt_history:
            for cinturon, arte, action, fecha in belt_history:
                row = QHBoxLayout()
                dot = QLabel("●")
                dot.setStyleSheet("color: #C8102E; font-size: 10px;")
                dot.setFixedWidth(14)
                lbl_belt = QLabel(f"{cinturon}  ({arte})")
                lbl_belt.setStyleSheet("color: #F0F0F0; font-size: 12px;")
                lbl_date = QLabel(str(fecha))
                lbl_date.setStyleSheet("color: #555555; font-size: 11px;")
                lbl_date.setAlignment(Qt.AlignmentFlag.AlignRight)
                row.addWidget(dot)
                row.addWidget(lbl_belt, 1)
                row.addWidget(lbl_date)
                belt_layout.addLayout(row)
        else:
            none_lbl = QLabel("Sin historial")
            none_lbl.setStyleSheet("color: #555555; font-size: 12px;")
            belt_layout.addWidget(none_lbl)

        belt_layout.addStretch()

        class_card = self._make_card()
        class_layout = QVBoxLayout(class_card)
        class_layout.setContentsMargins(14, 12, 14, 12)
        class_layout.setSpacing(6)
        class_layout.addWidget(self._section_label("ÚLTIMAS CLASES"))

        if last_classes:
            for fecha, clase, arte in last_classes:
                row = QHBoxLayout()
                dot = QLabel("●")
                dot.setStyleSheet("color: #3B82F6; font-size: 10px;")
                dot.setFixedWidth(14)
                lbl_class = QLabel(str(clase))
                lbl_class.setStyleSheet("color: #F0F0F0; font-size: 12px;")
                lbl_date = QLabel(str(fecha))
                lbl_date.setStyleSheet("color: #555555; font-size: 11px;")
                lbl_date.setAlignment(Qt.AlignmentFlag.AlignRight)
                row.addWidget(dot)
                row.addWidget(lbl_class, 1)
                row.addWidget(lbl_date)
                class_layout.addLayout(row)
        else:
            none_lbl = QLabel("Sin clases registradas")
            none_lbl.setStyleSheet("color: #555555; font-size: 12px;")
            class_layout.addWidget(none_lbl)

        class_layout.addStretch()

        bottom_row.addWidget(belt_card)
        bottom_row.addWidget(class_card)
        root.addLayout(bottom_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_edit = QPushButton("✎  Editar")
        btn_edit.setFixedHeight(38)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet("""
            QPushButton {
                background: transparent; color: #888888;
                border: 1px solid #2A2A2A; border-radius: 7px; font-size: 13px;
            }
            QPushButton:hover { color: #F0F0F0; border-color: #555; }
        """)
        btn_edit.clicked.connect(self._open_edit)

        btn_close = QPushButton("Cerrar")
        btn_close.setFixedHeight(38)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #C8102E; color: white;
                border: none; border-radius: 7px; font-size: 13px; font-weight: 700;
            }
            QPushButton:hover { background-color: #E8152F; }
        """)
        btn_close.clicked.connect(self.reject)

        btn_row.addWidget(btn_edit)
        btn_row.addWidget(btn_close)
        root.addLayout(btn_row)

    def _make_card(self):
        card = QFrame()
        card.setStyleSheet("""
        QFrame {
            background-color: #161616;
            border: 1px solid #2A2A2A;
            border-radius: 10px;
        }
        QFrame * {
            border: none;
        }
    """)
        return card

    def _section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "font-size: 10px; font-weight: 700; letter-spacing: 1px; "
            "color: #555555; padding-bottom: 6px;"
        )
        return lbl

    def _data_row(self, key, val, val_color="#F0F0F0"):
        k = QLabel(key)
        k.setStyleSheet("color: #555555; font-size: 12px;")
        v = QLabel(str(val) if val else "—")
        v.setAlignment(Qt.AlignmentFlag.AlignRight)
        v.setStyleSheet(f"color: {val_color}; font-size: 12px;")
        v.setWordWrap(True)
        row = QHBoxLayout()
        row.addWidget(k)
        row.addWidget(v, 1)
        return row

    def _set_photo(self, path, name):
        if path:
            pixmap = QPixmap(path).scaled(72, 72, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.lbl_photo.setPixmap(pixmap)
        else:
            initials = "".join(part[0].upper() for part in name.split()[:2] if part)
            self.lbl_photo.setText(initials or "?")
            self.lbl_photo.setStyleSheet(
                "background-color: #1A1A1A; color: #C8102E; font-size: 20px; font-weight: 700; border-radius: 36px;"
            )

    def _change_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar foto", "", "Imágenes (*.png *.jpg *.jpeg)")
        if path:
            self.repo.update_photo(self.student_id, path)
            self._set_photo(path, self.repo.get_detail(self.student_id).get("nombre", "?"))

    def _open_edit(self):
        from views.student_form import StudentForm

        dlg = StudentForm(self.repo, student_id=self.student_id, parent=self)
        if dlg.exec() == StudentForm.DialogCode.Accepted:
            self.accept()  # cierra el detalle también para que la tabla se recargue


# ─── VISTA PRINCIPAL ──────────────────────────────────────────────────
class StudentsView(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = StudentRepository()
        self._rows = []
        self._display_rows = []

        # Animaciones
        self._animations = []
        self._loading_anim = None
        self._loading_effect = None
        self._row_timer = None
        self._row_insert_index = 0

        self._build_ui()

        QTimer.singleShot(80, self._animate_initial_entrance)

        self._load()

    # ─────────────────────────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(f"background-color: {BG_MAIN};")

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(12)

        self.header_widget = self._make_header()
        root.addWidget(self.header_widget)

        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.4 {RED}, stop:1 transparent);
            border: none;
        """)
        root.addWidget(sep)

        self.toolbar_widget = self._make_toolbar()
        self.filter_widget = self._make_filter_bar()

        root.addWidget(self.toolbar_widget)
        root.addWidget(self.filter_widget)

        content = QHBoxLayout()
        content.setSpacing(14)

        self.table = self._make_table()
        self.quick_panel = self._make_quick_panel()

        content.addWidget(self.table, 4)
        content.addWidget(self.quick_panel, 1)

        root.addLayout(content, 1)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)

        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet(f"color: {GREEN}; font-size: 11px;")

        self.lbl_count = QLabel("Cargando...")
        self.lbl_count.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px;")
        self.lbl_count.setAlignment(Qt.AlignmentFlag.AlignRight)

        footer.addWidget(self.lbl_status)
        footer.addStretch()
        footer.addWidget(self.lbl_count)

        root.addLayout(footer)

        self._load_filter_options()

    def _make_header(self):
        w = QWidget()
        w.setStyleSheet("background: transparent;")

        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)

        title = QLabel("👥  Estudiantes")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_PRI};")

        self.btn_delete = QPushButton("🗑  Eliminar")
        self.btn_delete.setFixedHeight(38)
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: #FF4444;
                border: 1px solid #FF4444;
                border-radius: 7px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 18px;
            }}
            QPushButton:hover {{
                background-color: #2A0A0A;
            }}
        """)
        self.btn_delete.clicked.connect(self._delete_student)

        self.btn_new = QPushButton("＋  Nuevo Estudiante")
        self.btn_new.setFixedHeight(38)
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED};
                color: white;
                border: none;
                border-radius: 7px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 18px;
            }}
            QPushButton:hover {{
                background-color: #E8152F;
            }}
        """)
        self.btn_new.clicked.connect(self._create_student)

        h.addWidget(title)
        h.addStretch()
        h.addWidget(self.btn_delete)
        h.addWidget(self.btn_new)

        return w

    def _make_toolbar(self):
        w = QWidget()
        w.setStyleSheet("background: transparent;")

        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Buscar por nombre, documento, email o teléfono...")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #1E1E1E;
                color: {TEXT_PRI};
                border: 1.5px solid #333;
                border-radius: 7px;
                padding: 0 14px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {RED};
            }}
        """)

        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._load)
        self.search_input.textChanged.connect(lambda: self._search_timer.start(400))

        btn_refresh = QPushButton("↻  Actualizar")
        btn_refresh.setFixedHeight(38)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet(self._secondary_button_style())
        btn_refresh.clicked.connect(self._load)

        btn_edit = QPushButton("✎  Editar")
        btn_edit.setFixedHeight(38)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet(self._secondary_button_style())
        btn_edit.clicked.connect(self._edit_student)

        h.addWidget(self.search_input, 1)
        h.addWidget(btn_refresh)
        h.addWidget(btn_edit)

        return w

    def _make_filter_bar(self):
        w = QWidget()
        w.setStyleSheet("background: transparent;")

        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        combo_style = f"""
            QComboBox {{
                background-color: #1A1A1A;
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 0 10px;
                font-size: 12px;
                min-height: 32px;
            }}
            QComboBox:focus {{
                border-color: {RED};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background: #1A1A1A;
                color: {TEXT_PRI};
                selection-background-color: {RED};
                border: 1px solid {BORDER};
            }}
        """

        lbl = QLabel("Filtros:")
        lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; font-weight: 600;")
        h.addWidget(lbl)

        self.cmb_filter_status = QComboBox()
        self.cmb_filter_status.setFixedHeight(32)
        self.cmb_filter_status.setMinimumWidth(120)
        self.cmb_filter_status.setStyleSheet(combo_style)
        self.cmb_filter_status.addItem("Estado: todos", None)
        self.cmb_filter_status.currentIndexChanged.connect(self._apply_filters)
        h.addWidget(self.cmb_filter_status)

        self.cmb_filter_category = QComboBox()
        self.cmb_filter_category.setFixedHeight(32)
        self.cmb_filter_category.setMinimumWidth(130)
        self.cmb_filter_category.setStyleSheet(combo_style)
        self.cmb_filter_category.addItem("Categoría: todas", None)
        self.cmb_filter_category.currentIndexChanged.connect(self._apply_filters)
        h.addWidget(self.cmb_filter_category)

        self.cmb_filter_doctype = QComboBox()
        self.cmb_filter_doctype.setFixedHeight(32)
        self.cmb_filter_doctype.setMinimumWidth(140)
        self.cmb_filter_doctype.setStyleSheet(combo_style)
        self.cmb_filter_doctype.addItem("Tipo doc: todos", None)
        self.cmb_filter_doctype.currentIndexChanged.connect(self._apply_filters)
        h.addWidget(self.cmb_filter_doctype)

        self.cmb_filter_ma = QComboBox()
        self.cmb_filter_ma.setFixedHeight(32)
        self.cmb_filter_ma.setMinimumWidth(160)
        self.cmb_filter_ma.setStyleSheet(combo_style)
        self.cmb_filter_ma.addItem("Arte marcial: todas", None)
        self.cmb_filter_ma.currentIndexChanged.connect(self._apply_filters)
        h.addWidget(self.cmb_filter_ma)

        # Filtro cliente para cinturón
        self.cmb_filter_belt = QComboBox()
        self.cmb_filter_belt.setFixedHeight(32)
        self.cmb_filter_belt.setMinimumWidth(135)
        self.cmb_filter_belt.setStyleSheet(combo_style)
        self.cmb_filter_belt.addItem("Cinturón: todos", "all")
        self.cmb_filter_belt.addItem("Con cinturón", "with_belt")
        self.cmb_filter_belt.addItem("Sin cinturón", "no_belt")
        self.cmb_filter_belt.addItem("Con grados", "with_grades")
        self.cmb_filter_belt.currentIndexChanged.connect(self._apply_filters)
        h.addWidget(self.cmb_filter_belt)

        btn_clear = QPushButton("✕ Limpiar")
        btn_clear.setFixedHeight(32)
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_MUT};
                border: 1px solid {BORDER};
                border-radius: 6px;
                font-size: 11px;
                padding: 0 10px;
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
                border-color: #555;
            }}
        """)
        btn_clear.clicked.connect(self._clear_filters)

        h.addWidget(btn_clear)
        h.addStretch()

        return w

    def _make_table(self):
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Documento", "Teléfono", "Email", "Estado", "Cinturón"
        ])

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)

        table.setColumnWidth(0, 50)
        table.setColumnWidth(2, 125)
        table.setColumnWidth(3, 135)
        table.setColumnWidth(5, 115)
        table.setColumnWidth(6, 370)

        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)

        # OJO:
        # Como hay widgets en Estado/Cinturón, sorting visual puede romper relación row->data.
        # Mejor dejar el orden desde el repository.
        table.setSortingEnabled(False)

        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_TABLE};
                alternate-background-color: #141414;
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 10px;
                font-size: 13px;
                outline: none;
            }}
            QHeaderView::section {{
                background-color: {BG_CARD};
                color: {TEXT_SEC};
                border: none;
                border-bottom: 1px solid {BORDER};
                padding: 8px 10px;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
            }}
            QTableWidget::item {{
                padding: 8px 10px;
                border-bottom: 1px solid #1A1A1A;
            }}
            QTableWidget::item:selected {{
                background-color: {RED_DARK};
                color: white;
            }}
        """)

        table.doubleClicked.connect(self._view_detail)
        table.itemSelectionChanged.connect(self._update_quick_panel_from_selection)

        return table

    def _make_quick_panel(self):
        panel = QFrame()
        panel.setMinimumWidth(230)
        panel.setMaximumWidth(280)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
            QFrame * {{
                border: none;
                background: transparent;
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("DETALLE RÁPIDO")
        title.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 700; letter-spacing: 1px;")

        self.quick_avatar = QLabel("👤")
        self.quick_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quick_avatar.setFixedSize(58, 58)
        self.quick_avatar.setStyleSheet(f"""
            QLabel {{
                background-color: #1A1A1A;
                color: {RED};
                border-radius: 29px;
                font-size: 22px;
                font-weight: 700;
            }}
        """)

        self.quick_name = QLabel("Selecciona un estudiante")
        self.quick_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quick_name.setWordWrap(True)
        self.quick_name.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 700;")

        self.quick_doc = QLabel("—")
        self.quick_doc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quick_doc.setWordWrap(True)
        self.quick_doc.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px;")

        self.quick_status = QLabel("—")
        self.quick_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quick_status.setFixedHeight(26)
        self.quick_status.setStyleSheet(self._badge_style("#333333", TEXT_SEC))

        self.quick_belt = QLabel("🥋 Sin cinturón")
        self.quick_belt.setWordWrap(True)
        self.quick_belt.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px;")

        self.quick_art = QLabel("Sin arte")
        self.quick_art.setWordWrap(True)
        self.quick_art.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px;")

        self.quick_phone = QLabel("📞 —")
        self.quick_phone.setWordWrap(True)
        self.quick_phone.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")

        self.quick_email = QLabel("✉ —")
        self.quick_email.setWordWrap(True)
        self.quick_email.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")

        btn_view = QPushButton("👁  Ver detalle")
        btn_view.setFixedHeight(34)
        btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_view.setStyleSheet(self._secondary_button_style())
        btn_view.clicked.connect(self._view_detail)

        btn_edit = QPushButton("✎  Editar")
        btn_edit.setFixedHeight(34)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet(self._secondary_button_style())
        btn_edit.clicked.connect(self._edit_student)

        layout.addWidget(title)
        layout.addSpacing(8)
        layout.addWidget(self.quick_avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.quick_name)
        layout.addWidget(self.quick_doc)
        layout.addWidget(self.quick_status)
        layout.addSpacing(8)
        layout.addWidget(self._mini_separator())
        layout.addWidget(self.quick_belt)
        layout.addWidget(self.quick_art)
        layout.addSpacing(8)
        layout.addWidget(self._mini_separator())
        layout.addWidget(self.quick_phone)
        layout.addWidget(self.quick_email)
        layout.addStretch()
        layout.addWidget(btn_view)
        layout.addWidget(btn_edit)

        return panel

    # ─────────────────────────────────────────────────────────────
    # Carga y filtros
    # ─────────────────────────────────────────────────────────────
    def _load_filter_options(self):
        try:
            opts = self.repo.get_filter_options()

            for st_id, st_name in opts["statuses"]:
                self.cmb_filter_status.addItem(st_name, st_id)

            for cat_id, cat_name in opts["categories"]:
                self.cmb_filter_category.addItem(cat_name, cat_id)

            for dt_id, dt_name in opts["doc_types"]:
                self.cmb_filter_doctype.addItem(dt_name, dt_id)

            for ma_id, ma_name in opts["martial_arts"]:
                self.cmb_filter_ma.addItem(f"🥋 {ma_name}", ma_id)

        except Exception as e:
            print(f"[Filter options error] {e}")

    def _get_filters(self):
        return {
            "id_status": self.cmb_filter_status.currentData(),
            "category_id": self.cmb_filter_category.currentData(),
            "id_type_document": self.cmb_filter_doctype.currentData(),
            "martial_art_id": self.cmb_filter_ma.currentData(),
        }

    def _apply_filters(self):
        self._load()

    def _clear_filters(self):
        combos = [
            self.cmb_filter_status,
            self.cmb_filter_category,
            self.cmb_filter_doctype,
            self.cmb_filter_ma,
            self.cmb_filter_belt,
        ]

        for cmb in combos:
            cmb.blockSignals(True)
            cmb.setCurrentIndex(0)
            cmb.blockSignals(False)

        self.search_input.clear()
        self._load()

    def _load(self):
        self.lbl_count.setText("Cargando...")
        self.lbl_status.setText("")
        self._start_loading_animation()

        self.table.setEnabled(False)
        self._show_skeleton_rows()

        search = self.search_input.text().strip()
        self._worker = LoadWorker(self.repo, search, self._get_filters())
        self._worker.done.connect(self._on_data)
        self._worker.start()

    def _on_data(self, rows):
        self._stop_loading_animation()
        self.table.setEnabled(True)

        self._rows = rows
        self._display_rows = self._apply_client_filters(rows)

        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        if not self._display_rows:
            self.lbl_count.setText("No se encontraron estudiantes.")
            self._clear_quick_panel()
            self._fade_in_widget(self.lbl_count, 220, 0.0, 1.0)
            return

        self._row_insert_index = 0

        if self._row_timer:
            self._row_timer.stop()

        self._row_timer = QTimer(self)
        self._row_timer.timeout.connect(self._insert_next_row_animated)
        self._row_timer.start(18)

    def _apply_client_filters(self, rows):
        belt_filter = self.cmb_filter_belt.currentData()

        if belt_filter == "all":
            return rows

        result = []

        for row in rows:
            belt_name = str(row[16]) if len(row) > 16 and row[16] else "Sin cinturón"
            grades = int(row[20]) if len(row) > 20 and row[20] else 0

            has_belt = belt_name.lower() != "sin cinturón"

            if belt_filter == "with_belt" and has_belt:
                result.append(row)
            elif belt_filter == "no_belt" and not has_belt:
                result.append(row)
            elif belt_filter == "with_grades" and grades > 0:
                result.append(row)

        return result

    def _insert_next_row_animated(self):
        if self._row_insert_index >= len(self._display_rows):
            if self._row_timer:
                self._row_timer.stop()

            total = len(self._display_rows)
            self.lbl_count.setText(
                f"{total} estudiante{'s' if total != 1 else ''} encontrado{'s' if total != 1 else ''}"
            )

            self._animate_table_loaded()
            return

        row_data = self._display_rows[self._row_insert_index]

        table_row = self.table.rowCount()
        self.table.insertRow(table_row)

        self._populate_table_row(table_row, row_data)
        self.table.setRowHeight(table_row, 56)

        self._row_insert_index += 1


    def _show_skeleton_rows(self):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        for i in range(6):
            self.table.insertRow(i)
            self.table.setRowHeight(i, 56)

            for j in range(7):
                item = QTableWidgetItem("████████")
                item.setForeground(QColor("#2A2A2A"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(i, j, item)

    # ─────────────────────────────────────────────────────────────
    # Tabla
    # ─────────────────────────────────────────────────────────────
    def _populate_table_row(self, i, row):
        values = [
            row[0],
            row[1],
            row[2],
            row[3] or "—",
            row[4] or "—",
        ]

        for j, val in enumerate(values):
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(i, j, item)

        # ── Estado visual
        status_widget = self._make_status_badge(str(row[5] or "—"))
        self.table.setCellWidget(i, 5, status_widget)

        # Item vacío para evitar texto montado encima del widget
        status_item = QTableWidgetItem("")
        status_item.setData(Qt.ItemDataRole.UserRole, str(row[5] or "—"))
        self.table.setItem(i, 5, status_item)

        # ── Cinturón visual
        belt_name = str(row[16]) if len(row) > 16 and row[16] else "Sin cinturón"
        belt_color = str(row[17]) if len(row) > 17 and row[17] else "#888888"
        belt_pre_color = str(row[18]) if len(row) > 18 and row[18] else None
        art_name = str(row[19]) if len(row) > 19 and row[19] else "Sin arte"
        belt_grades = int(row[20]) if len(row) > 20 and row[20] else 0
        belt_grade_color = str(row[21]) if len(row) > 21 and row[21] else "#FFFFFF"

        belt_widget = self._make_belt_cell_full(
            belt_name,
            belt_color,
            belt_pre_color,
            art_name,
            belt_grades,
            belt_grade_color,
        )

        self.table.setCellWidget(i, 6, belt_widget)

        # Item vacío para evitar texto montado encima del widget
        belt_item = QTableWidgetItem("")
        belt_item.setData(Qt.ItemDataRole.UserRole, f"{art_name} {belt_name}")
        self.table.setItem(i, 6, belt_item)

    def _make_status_badge(self, status):
        status_text = status.capitalize()
        status_lower = status.lower()

        if "inactivo" in status_lower or "inactive" in status_lower or "suspendido" in status_lower:
            color = "#FF4444"
            bg = "#2A0A0A"

        elif "activo" in status_lower or "active" in status_lower:
            color = GREEN
            bg = "#0A2A0A"

        else:
            color = YELLOW
            bg = "#2A260A"

        w = QWidget()
        w.setStyleSheet("background: transparent;")

        hl = QHBoxLayout(w)
        hl.setContentsMargins(6, 8, 6, 8)

        lbl = QLabel(status_text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setFixedHeight(24)
        lbl.setStyleSheet(self._badge_style(bg, color))

        hl.addWidget(lbl)

        return w


    # ─────────────────────────────────────────────────────────────
    # Cinturón visual
    # ─────────────────────────────────────────────────────────────
    def _make_belt_cell_full(self, name, color, pre_color, art_name, grades=0, grade_color="#FFFFFF"):
        w = QWidget()
        w.setStyleSheet("background: transparent;")

        hl = QHBoxLayout(w)
        hl.setContentsMargins(10, 4, 10, 4)
        hl.setSpacing(12)

        if not name or name == "None":
            name = "Sin cinturón"

        if not art_name or art_name == "None":
            art_name = "Sin arte"

        no_belt = name.lower() == "sin cinturón"

        light = {"#FFFFFF", "#FFD700", "#FF8C00", "#FFFF00", "#FFA500", "#FFFACD"}
        belt_color = color or "#888888"
        border_c = "#777777" if no_belt else ("#999999" if belt_color.upper() in light else belt_color)

        is_bjj = art_name.strip().lower() in {
            "brazilian jiu-jitsu",
            "bjj",
            "jiu-jitsu brasileño",
            "jiu jitsu brasileño",
        }

        bar = QFrame()
        bar.setFixedSize(98, 20)

        if no_belt:
            bar.setStyleSheet("""
                QFrame {
                    background-color: #202020;
                    border-radius: 5px;
                    border: 1.5px dashed #555555;
                }
            """)
        else:
            bar.setStyleSheet(f"""
                QFrame {{
                    background-color: {belt_color};
                    border-radius: 5px;
                    border: 1.5px solid {border_c};
                }}
            """)

        if not no_belt:
            if is_bjj:
                grados = max(0, min(4, int(grades or 0)))
                stripe_color = "red" if belt_color.upper() == "#000000" else "black"

                inner = QHBoxLayout(bar)
                inner.setContentsMargins(0, 0, 4, 0)
                inner.setSpacing(0)
                inner.addStretch()

                stripe_box = QFrame()
                stripe_box.setFixedSize(42, 18)
                stripe_box.setStyleSheet(f"""
                    QFrame {{
                        background-color: {stripe_color};
                        border-top-left-radius: 0px;
                        border-bottom-left-radius: 0px;
                        border-top-right-radius: 4px;
                        border-bottom-right-radius: 4px;
                        border: none;
                    }}
                """)

                stripe_hl = QHBoxLayout(stripe_box)
                stripe_hl.setContentsMargins(3, 0, 3, 0)
                stripe_hl.setSpacing(3)
                stripe_hl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                for idx in range(4):
                    s = QFrame()
                    s.setFixedSize(4, 13)

                    if idx >= 4 - grados:
                        s.setStyleSheet("QFrame { background: white; border-radius: 1px; border: none; }")
                    else:
                        s.setStyleSheet("QFrame { background: transparent; border: none; }")

                    stripe_hl.addWidget(s)

                inner.addWidget(stripe_box, 0, Qt.AlignmentFlag.AlignVCenter)

            elif pre_color and pre_color != "None":
                inner = QHBoxLayout(bar)
                inner.setContentsMargins(0, 0, 0, 0)
                inner.setSpacing(0)

                left = QFrame()
                left.setStyleSheet("background: transparent; border: none;")

                stripe = QFrame()
                stripe.setFixedWidth(8)
                stripe.setStyleSheet(f"QFrame {{ background-color: {pre_color}; border: none; }}")

                right = QFrame()
                right.setStyleSheet("background: transparent; border: none;")

                inner.addWidget(left, 3)
                inner.addWidget(stripe)
                inner.addWidget(right, 1)

            else:
                grados = max(0, min(10, int(grades or 0)))

                if grados > 0:
                    inner = QHBoxLayout(bar)
                    inner.setContentsMargins(0, 0, 5, 0)
                    inner.setSpacing(0)
                    inner.addStretch()

                    grade_box = QFrame()
                    grade_box.setFixedSize(62, 18)
                    grade_box.setStyleSheet("QFrame { background: transparent; border: none; }")

                    grade_hl = QHBoxLayout(grade_box)
                    grade_hl.setContentsMargins(0, 0, 0, 0)
                    grade_hl.setSpacing(2)
                    grade_hl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                    for idx in range(10):
                        s = QFrame()
                        s.setFixedSize(3, 13)

                        if idx >= 10 - grados:
                            s.setStyleSheet(f"QFrame {{ background: {grade_color}; border-radius: 1px; border: none; }}")
                        else:
                            s.setStyleSheet("QFrame { background: transparent; border: none; }")

                        grade_hl.addWidget(s)

                    inner.addWidget(grade_box, 0, Qt.AlignmentFlag.AlignVCenter)

        info_w = QWidget()
        info_w.setStyleSheet("background: transparent;")

        info = QVBoxLayout(info_w)
        info.setSpacing(0)
        info.setContentsMargins(0, 0, 0, 0)

        lbl_belt = QLabel("🥋 Sin cinturón" if no_belt else name)
        lbl_belt.setToolTip(name)
        lbl_belt.setMinimumWidth(0)
        lbl_belt.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        lbl_belt.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_MUT if no_belt else TEXT_PRI};
                font-size: 12px;
                font-weight: 600;
                background: transparent;
            }}
        """)

        lbl_art = QLabel("" if art_name == "Sin arte" else art_name)
        lbl_art.setToolTip(art_name)
        lbl_art.setMinimumWidth(0)
        lbl_art.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        lbl_art.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_MUT};
                font-size: 10px;
                background: transparent;
            }}
        """)

        info.addWidget(lbl_belt)
        if art_name and art_name != "Sin arte":
            info.addWidget(lbl_art)

        hl.addWidget(bar, 0, Qt.AlignmentFlag.AlignVCenter)
        hl.addWidget(info_w, 1)

        return w
    
    def _rounded_pixmap(self, path, size=58):
        pixmap = QPixmap(path)

        if pixmap.isNull():
            return None

        pixmap = pixmap.scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        rounded = QPixmap(size, size)
        rounded.fill(Qt.GlobalColor.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path_clip = QPainterPath()
        path_clip.addEllipse(0, 0, size, size)

        painter.setClipPath(path_clip)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return rounded


    def _set_quick_avatar(self, student_id, name):
        photo_path = None

        try:
            photo_path = self.repo.get_photo(student_id)
        except Exception:
            photo_path = None

        if photo_path:
            rounded = self._rounded_pixmap(photo_path, 58)

            if rounded:
                self.quick_avatar.setPixmap(rounded)
                self.quick_avatar.setText("")
                self.quick_avatar.setStyleSheet("""
                    QLabel {
                        background-color: #1A1A1A;
                        border-radius: 29px;
                    }
                """)
                return

        initials = "".join(part[0].upper() for part in name.split()[:2] if part)

        self.quick_avatar.setPixmap(QPixmap())
        self.quick_avatar.setText(initials or "👤")
        self.quick_avatar.setStyleSheet(f"""
            QLabel {{
                background-color: #1A1A1A;
                color: {RED};
                border-radius: 29px;
                font-size: 22px;
                font-weight: 700;
            }}
        """)

    # ─────────────────────────────────────────────────────────────
    # Panel rápido
    # ─────────────────────────────────────────────────────────────
    def _update_quick_panel_from_selection(self):
        row_index = self.table.currentRow()

        if row_index < 0 or row_index >= len(self._display_rows):
            self._clear_quick_panel()
            return

        row = self._display_rows[row_index]

        student_id = row[0]
        name = str(row[1] or "—")
        doc = str(row[2] or "—")
        phone = str(row[3] or "—")
        email = str(row[4] or "—")
        status = str(row[5] or "—")
        belt = str(row[16]) if len(row) > 16 and row[16] else "Sin cinturón"
        art = str(row[19]) if len(row) > 19 and row[19] else "Sin arte"

        self._set_quick_avatar(student_id, name)

        self.quick_name.setText(name)
        self.quick_doc.setText(doc)

        status_lower = status.lower()
        if "inactivo" in status_lower or "inactive" in status_lower or "suspendido" in status_lower:
            self.quick_status.setStyleSheet(self._badge_style("#2A0A0A", "#FF4444"))

        elif "activo" in status_lower or "active" in status_lower:
            self.quick_status.setStyleSheet(self._badge_style("#0A2A0A", GREEN))

        else:
            self.quick_status.setStyleSheet(self._badge_style("#2A260A", YELLOW))


        self.quick_status.setText(status.capitalize())
        self.quick_belt.setText(f"🥋 {belt}")
        self.quick_art.setText(art)
        self.quick_phone.setText(f"📞 {phone}")
        self.quick_email.setText(f"✉ {email}")

        self._fade_in_widget(self.quick_panel, 160, 0.75, 1.0)


    def _clear_quick_panel(self):
        self.quick_avatar.setPixmap(QPixmap())
        self.quick_avatar.setText("👤")
        self.quick_avatar.setStyleSheet(f"""
            QLabel {{
                background-color: #1A1A1A;
                color: {RED};
                border-radius: 29px;
                font-size: 22px;
                font-weight: 700;
            }}
        """)

        self.quick_name.setText("Selecciona un estudiante")
        self.quick_doc.setText("—")
        self.quick_status.setText("—")
        self.quick_status.setStyleSheet(self._badge_style("#333333", TEXT_SEC))
        self.quick_belt.setText("🥋 Sin cinturón")
        self.quick_art.setText("Sin arte")
        self.quick_phone.setText("📞 —")
        self.quick_email.setText("✉ —")


    # ─────────────────────────────────────────────────────────────
    # Acciones
    # ─────────────────────────────────────────────────────────────
    def _get_selected_id(self):
        row = self.table.currentRow()

        if row < 0 or row >= len(self._display_rows):
            return None

        return self._display_rows[row][0]

    def _view_detail(self):
        sid = self._get_selected_id()

        if sid is None:
            self._pulse_widget(self.table)
            return

        self._view_detail_by_id(sid)

    def _view_detail_by_id(self, student_id):
        dlg = StudentDetail(student_id, self.repo, self)
        dlg.exec()

    def _create_student(self):
        dlg = StudentForm(self.repo, parent=self)

        if dlg.exec() == StudentForm.DialogCode.Accepted:
            credentials = getattr(dlg, "created_credentials", None)

            self._load()
            self._set_status("✓ Estudiante creado correctamente")

            if credentials:
                username = credentials.get("username", "—")
                password = credentials.get("password", "—")

                msg = QMessageBox(self)
                msg.setWindowTitle("Usuario creado")
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setText("El estudiante fue creado correctamente.")
                msg.setInformativeText(
                    f"Usuario: {username}\n"
                    f"Contraseña temporal: {password}\n\n"
                    "Guarda esta información. La contraseña no se podrá ver nuevamente."
                )
                msg.setStyleSheet(self._messagebox_style())
                msg.exec()

    def _edit_student(self):
        sid = self._get_selected_id()

        if sid is None:
            self._pulse_widget(self.table)
            QMessageBox.information(self, "Aviso", "Selecciona un estudiante primero.")
            return

        self._edit_student_by_id(sid)

    def _edit_student_by_id(self, student_id):
        dlg = StudentForm(self.repo, student_id=student_id, parent=self)

        if dlg.exec() == StudentForm.DialogCode.Accepted:
            self._load()
            self._set_status("✓ Cambios guardados correctamente")

    def _delete_student(self):
        sid = self._get_selected_id()

        if sid is None:
            self._pulse_widget(self.table)
            QMessageBox.information(self, "Aviso", "Selecciona un estudiante primero.")
            return

        row = self.table.currentRow()
        name = self._display_rows[row][1] if row >= 0 else "este estudiante"

        self._delete_student_by_id(sid, name)

    def _delete_student_by_id(self, student_id, name):
        confirm = QMessageBox(self)
        confirm.setWindowTitle("Confirmar eliminación")
        confirm.setText(f"¿Eliminar a {name}?")
        confirm.setInformativeText(
            "Se eliminarán sus membresías, cinturones e historial.\n"
            "Esta acción no se puede deshacer."
        )
        confirm.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        confirm.setDefaultButton(QMessageBox.StandardButton.Cancel)
        confirm.setStyleSheet(self._messagebox_style())

        if confirm.exec() == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete(student_id)
                self._load()
                self._set_status("✓ Estudiante eliminado correctamente")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{e}")

    # ─────────────────────────────────────────────────────────────
    # Animaciones
    # ─────────────────────────────────────────────────────────────
    def _fade_in_widget(self, widget, duration=260, start=0.0, end=1.0):
        if widget is None:
            return

        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(duration)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._animations.append(anim)

        def cleanup():
            if anim in self._animations:
                self._animations.remove(anim)

        anim.finished.connect(cleanup)
        anim.start()

    def _animate_initial_entrance(self):
        self._fade_in_widget(self.header_widget, 320, 0.0, 1.0)
        QTimer.singleShot(80, lambda: self._fade_in_widget(self.toolbar_widget, 320, 0.0, 1.0))
        QTimer.singleShot(140, lambda: self._fade_in_widget(self.filter_widget, 320, 0.0, 1.0))
        QTimer.singleShot(200, lambda: self._fade_in_widget(self.table, 360, 0.0, 1.0))
        QTimer.singleShot(240, lambda: self._fade_in_widget(self.quick_panel, 360, 0.0, 1.0))

    def _start_loading_animation(self):
        if not hasattr(self, "lbl_count"):
            return

        self._loading_effect = QGraphicsOpacityEffect(self.lbl_count)
        self.lbl_count.setGraphicsEffect(self._loading_effect)

        self._loading_anim = QPropertyAnimation(self._loading_effect, b"opacity", self)
        self._loading_anim.setDuration(650)
        self._loading_anim.setStartValue(0.35)
        self._loading_anim.setEndValue(1.0)
        self._loading_anim.setLoopCount(-1)
        self._loading_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._loading_anim.start()

    def _stop_loading_animation(self):
        if self._loading_anim:
            self._loading_anim.stop()
            self._loading_anim = None

        if hasattr(self, "lbl_count") and self.lbl_count:
            self.lbl_count.setGraphicsEffect(None)

        self._loading_effect = None

    def _animate_table_loaded(self):
        self._fade_in_widget(self.table, 220, 0.0, 1.0)

    def _pulse_widget(self, widget):
        if widget is None:
            return

        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(180)
        anim.setStartValue(0.45)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._animations.append(anim)

        def cleanup():
            widget.setGraphicsEffect(None)

            if anim in self._animations:
                self._animations.remove(anim)

        anim.finished.connect(cleanup)
        anim.start()

    # ─────────────────────────────────────────────────────────────
    # Helpers visuales
    # ─────────────────────────────────────────────────────────────
    def _set_status(self, text):
        self.lbl_status.setText(text)
        self._fade_in_widget(self.lbl_status, 180, 0.0, 1.0)

        QTimer.singleShot(3000, self._clear_status_safe)

    def _clear_status_safe(self):
        try:
            self.lbl_status.setText("")
        except RuntimeError:
            pass

    def _badge_style(self, bg, color):
        return f"""
            QLabel {{
                background-color: {bg};
                color: {color};
                border: 1px solid {color};
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                padding: 0 10px;
            }}
        """

    def _secondary_button_style(self):
        return f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SEC};
                border: 1px solid {BORDER};
                border-radius: 7px;
                font-size: 12px;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
                border-color: #555;
            }}
        """

    def _messagebox_style(self):
        return """
            QMessageBox {
                background-color: #161616;
                color: #F0F0F0;
            }
            QLabel {
                color: #F0F0F0;
            }
            QPushButton {
                background-color: #C8102E;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #E8152F;
            }
        """

    def _mini_separator(self):
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER}; border: none;")
        return sep

    # ─────────────────────────────────────────────────────────────
    # Teclado
    # ─────────────────────────────────────────────────────────────
    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()

        if modifiers == Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_N:
            self._create_student()
            return

        if modifiers == Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_R:
            self._load()
            return

        if modifiers == Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_F:
            self.search_input.setFocus()
            self.search_input.selectAll()
            return

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._view_detail()
            return

        if key == Qt.Key.Key_E:
            self._edit_student()
            return

        if key == Qt.Key.Key_Delete:
            self._delete_student()
            return

        if key == Qt.Key.Key_Escape:
            self.table.clearSelection()
            self._clear_quick_panel()
            return

        super().keyPressEvent(event)