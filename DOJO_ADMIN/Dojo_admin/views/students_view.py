from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QMessageBox, QDialog,
    QFormLayout, QScrollArea, QSizePolicy, QFileDialog   # ← QFileDialog agregado
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap                  # ← QPixmap agregado

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

    def __init__(self, repo, search=""):
        super().__init__()
        self.repo   = repo
        self.search = search

    def run(self):
        try:
            data = self.repo.get_all(self.search)
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
        self._build_ui()
        self._load()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {BG_MAIN};")
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        root.addWidget(self._make_header())

        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.4 {RED}, stop:1 transparent);
            border: none;
        """)
        root.addWidget(sep)

        root.addWidget(self._make_toolbar())

        self.table = self._make_table()
        root.addWidget(self.table, 1)

        self.lbl_count = QLabel("Cargando...")
        self.lbl_count.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px;")
        root.addWidget(self.lbl_count)

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
                background-color: transparent; color: #FF4444;
                border: 1px solid #FF4444; border-radius: 7px;
                font-size: 13px; font-weight: 600; padding: 0 18px;
            }}
            QPushButton:hover {{ background-color: #2A0A0A; }}
        """)
        self.btn_delete.clicked.connect(self._delete_student)

        self.btn_new = QPushButton("＋  Nuevo Estudiante")
        self.btn_new.setFixedHeight(38)
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED}; color: white;
                border: none; border-radius: 7px;
                font-size: 13px; font-weight: 600; padding: 0 18px;
            }}
            QPushButton:hover {{ background-color: #E8152F; }}
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
                background-color: #1E1E1E; color: {TEXT_PRI};
                border: 1.5px solid #333; border-radius: 7px;
                padding: 0 14px; font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {RED}; }}
        """)
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._load)
        self.search_input.textChanged.connect(lambda: self._search_timer.start(400))

        btn_refresh = QPushButton("↻  Actualizar")
        btn_refresh.setFixedHeight(38)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 7px;
                font-size: 12px; padding: 0 14px;
            }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; }}
        """)
        btn_refresh.clicked.connect(self._load)

        btn_edit = QPushButton("✎  Editar")
        btn_edit.setFixedHeight(38)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 7px;
                font-size: 12px; padding: 0 14px;
            }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; }}
        """)
        btn_edit.clicked.connect(self._edit_student)

        h.addWidget(self.search_input, 1)
        h.addWidget(btn_refresh)
        h.addWidget(btn_edit)
        return w

    def _make_table(self):
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Documento", "Teléfono",
            "Email", "Estado", "Categoría", "Cinturón"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 50)
        table.setColumnWidth(6, 100)
        table.setColumnWidth(7, 180)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_TABLE};
                alternate-background-color: #141414;
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 10px;
                font-size: 13px;
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
        return table

    def _load(self):
        self.lbl_count.setText("Cargando...")
        search = self.search_input.text().strip()
        self._worker = LoadWorker(self.repo, search)
        self._worker.done.connect(self._on_data)
        self._worker.start()

    def _on_data(self, rows):
        self._rows = rows
        self.table.setRowCount(0)
        if not rows:
            self.lbl_count.setText("No se encontraron estudiantes.")
            return

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            # índices: 0=id, 1=nombre, 2=doc, 3=phone, 4=email,
            #          5=estado, 6=categoria, 7=fecha, 8=id_person,
            #          9=fname, 10=lname, 11=birth, 12=doc_num,
            #          13=id_type_doc, 14=id_status, 15=cat_id,
            #          16=cinturon, 17=belt_color, 18=belt_pre_color,
            #          19=arte_marcial

            values = [
                row[0],        # ID
                row[1],        # Nombre
                row[2],        # Documento
                row[3] or "—", # Teléfono
                row[4] or "—", # Email
                row[5],        # Estado
                row[6] or "—", # Categoría
            ]

            for j, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

                if j == 5:  # Estado
                    estado = str(val).lower()
                    if "activo" in estado or "active" in estado:
                        item.setForeground(QColor(GREEN))
                    elif "inactivo" in estado or "suspendido" in estado or "inactive" in estado:
                        item.setForeground(QColor("#FF4444"))
                    else:
                        item.setForeground(QColor(YELLOW))

                self.table.setItem(i, j, item)

            # ── Col 7: barra visual del cinturón + nombre arte marcial
            belt_name      = str(row[16]) if len(row) > 16 else "Sin cinturón"
            belt_color     = str(row[17]) if len(row) > 17 and row[17] else "#888888"
            belt_pre_color = str(row[18]) if len(row) > 18 and row[18] else None
            art_name       = str(row[19]) if len(row) > 19 else ""

            belt_widget = self._make_belt_cell(belt_name, belt_color, belt_pre_color, art_name)
            self.table.setCellWidget(i, 7, belt_widget)
            self.table.setRowHeight(i, 44)

        total = len(rows)
        self.lbl_count.setText(
            f"{total} estudiante{'s' if total != 1 else ''} encontrado{'s' if total != 1 else ''}"
        )

    def _make_belt_cell(self, name: str, color: str, pre_color: str = None, art_name: str = "") -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        hl = QHBoxLayout(w)
        hl.setContentsMargins(8, 4, 8, 4)
        hl.setSpacing(8)

        light_colors = {"#FFFFFF", "#FFD700", "#FF8C00", "#FFFF00", "#FFA500", "#FFFACD"}
        belt_color = color or "#888888"
        border_c = "#999999" if belt_color.upper() in light_colors else belt_color

        # Contenedor de la barra
        bar_container = QWidget()
        bar_container.setFixedSize(44, 18)
        bar_layout = QHBoxLayout(bar_container)
        bar_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.setSpacing(0)

        if pre_color and pre_color != "None":
            bar_left = QFrame()
            bar_left.setStyleSheet(f"""
                QFrame {{
                    background-color: {belt_color};
                    border-top-left-radius: 3px;
                    border-bottom-left-radius: 3px;
                    border: 1.5px solid {border_c};
                    border-right: none;
                }}
            """)
            bar_stripe = QFrame()
            bar_stripe.setFixedWidth(7)
            bar_stripe.setStyleSheet(f"""
                QFrame {{
                    background-color: {pre_color};
                    border-radius: 0px;
                }}
            """)
            bar_right = QFrame()
            bar_right.setStyleSheet(f"""
                QFrame {{
                    background-color: {belt_color};
                    border-top-right-radius: 3px;
                    border-bottom-right-radius: 3px;
                    border: 1.5px solid {border_c};
                    border-left: none;
                }}
            """)
            bar_layout.addWidget(bar_left, 2)
            bar_layout.addWidget(bar_stripe)
            bar_layout.addWidget(bar_right, 2)
        else:
            bar_full = QFrame()
            bar_full.setStyleSheet(f"""
                QFrame {{
                    background-color: {belt_color};
                    border-radius: 3px;
                    border: 1.5px solid {border_c};
                }}
            """)
            bar_layout.addWidget(bar_full, 1)

        # Texto: arte marcial (no el nombre del cinturón)
        display = art_name if art_name and art_name != "Sin arte" else name
        lbl = QLabel(display)
        lbl.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px; background: transparent;")

        hl.addWidget(bar_container)
        hl.addWidget(lbl, 1)
        return w

    def _get_selected_id(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._rows):
            return None
        return self._rows[row][0]

    def _view_detail(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._rows):
            return
        student_id = self._rows[row][0]
        dlg = StudentDetail(student_id, self.repo, self)
        dlg.exec()

    def _create_student(self):
        dlg = StudentForm(self.repo, parent=self)
        if dlg.exec() == StudentForm.DialogCode.Accepted:
            self._load()

    def _edit_student(self):
        sid = self._get_selected_id()
        if sid is None:
            QMessageBox.information(self, "Aviso", "Selecciona un estudiante primero.")
            return
        dlg = StudentForm(self.repo, student_id=sid, parent=self)
        if dlg.exec() == StudentForm.DialogCode.Accepted:
            self._load()

    def _delete_student(self):
        sid = self._get_selected_id()
        if sid is None:
            QMessageBox.information(self, "Aviso", "Selecciona un estudiante primero.")
            return
        row = self.table.currentRow()
        nombre = self._rows[row][1] if row >= 0 else "este estudiante"
        confirm = QMessageBox(self)
        confirm.setWindowTitle("Confirmar eliminación")
        confirm.setText(f"¿Eliminar a {nombre}?")
        confirm.setInformativeText(
            "Se eliminarán sus membresías, cinturones e historial.\n"
            "Esta acción no se puede deshacer."
        )
        confirm.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        confirm.setDefaultButton(QMessageBox.StandardButton.Cancel)
        confirm.setStyleSheet("background-color: #161616; color: #F0F0F0;")
        if confirm.exec() == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete(sid)
                self._load()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{e}")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._view_detail()
        elif event.key() == Qt.Key.Key_E:
            self._edit_student()
        super().keyPressEvent(event)