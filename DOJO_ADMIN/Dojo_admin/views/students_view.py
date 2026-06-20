from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QMessageBox, QDialog,
    QFormLayout, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QColor

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
        self.setWindowTitle("Detalle del Estudiante")
        self.setFixedSize(460, 560)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: #161616; color: {TEXT_PRI};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        title = QLabel("👤  Detalle del Estudiante")
        title.setStyleSheet("font-size: 15px; font-weight: 700;")
        layout.addWidget(title)

        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.4 {RED}, stop:1 transparent);
            border: none;
        """)
        layout.addWidget(sep)

        # Cargar datos
        data = repo.get_detail(student_id)

        def section(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"""
                font-size: 10px; font-weight: 700;
                letter-spacing: 1px; color: {TEXT_SEC};
                padding-top: 8px;
            """)
            return lbl

        def row(key, val, color=None):
            k = QLabel(key + ":")
            k.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-weight: 600;")
            v = QLabel(str(val))
            v.setStyleSheet(f"color: {color or TEXT_PRI}; font-size: 13px;")
            v.setWordWrap(True)
            return k, v

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # ── Datos personales
        form.addRow(section("DATOS PERSONALES"), QLabel(""))
        k, v = row("ID", data.get("id", "—")); form.addRow(k, v)
        k, v = row("Nombre", data.get("nombre", "—")); form.addRow(k, v)
        k, v = row("Tipo Doc.", data.get("tipo_doc", "—")); form.addRow(k, v)
        k, v = row("Documento", data.get("documento", "—")); form.addRow(k, v)
        k, v = row("Teléfono", data.get("telefono", "—")); form.addRow(k, v)
        k, v = row("Email", data.get("email", "—")); form.addRow(k, v)
        k, v = row("Nacimiento", data.get("nacimiento", "—")); form.addRow(k, v)

        estado = data.get("estado", "—")
        color_estado = GREEN if "activo" in estado.lower() else "#FF4444"
        k, v = row("Estado", estado, color_estado); form.addRow(k, v)
        k, v = row("Ingreso", data.get("fecha_ingreso", "—")); form.addRow(k, v)

        # ── Membresía
        form.addRow(section("MEMBRESÍA"), QLabel(""))
        k, v = row("Plan", data.get("membresia", "—")); form.addRow(k, v)
        k, v = row("Cuota", f"${data.get('cuota', '—')}" if data.get('cuota') not in ('—', None) else "—"); form.addRow(k, v)
        k, v = row("Inicio", data.get("inicio_mem", "—")); form.addRow(k, v)
        k, v = row("Vence", data.get("fin_mem", "—")); form.addRow(k, v)

        # ── Cinturón
        form.addRow(section("CINTURÓN"), QLabel(""))
        k, v = row("Arte Marcial", data.get("arte_marcial", "—")); form.addRow(k, v)
        k, v = row("Cinturón", data.get("cinturon", "—")); form.addRow(k, v)

        layout.addLayout(form)
        layout.addStretch()

        btn_close = QPushButton("Cerrar")
        btn_close.setFixedHeight(38)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED}; color: white;
                border: none; border-radius: 7px; font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #E8152F; }}
        """)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)


# ─── VISTA PRINCIPAL ──────────────────────────────────────────────────
class StudentsView(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = StudentRepository()
        self._rows = []
        self._build_ui()
        self._load()

    # ── UI ────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(f"background-color: {BG_MAIN};")
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # Encabezado
        root.addWidget(self._make_header())

        # Separador
        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.4 {RED}, stop:1 transparent);
            border: none;
        """)
        root.addWidget(sep)

        # Barra de herramientas
        root.addWidget(self._make_toolbar())

        # Tabla
        self.table = self._make_table()
        root.addWidget(self.table, 1)

        # Footer con conteo
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
                font-size: 13px; font-weight: 600;
                padding: 0 18px;
            }}
            QPushButton:hover {{ background-color: #2A0A0A; }}
            QPushButton:pressed {{ background-color: #3A0000; }}
        """)
        self.btn_delete.clicked.connect(self._delete_student)

        self.btn_new = QPushButton("＋  Nuevo Estudiante")
        self.btn_new.setFixedHeight(38)
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED}; color: white;
                border: none; border-radius: 7px;
                font-size: 13px; font-weight: 600;
                padding: 0 18px;
            }}
            QPushButton:hover {{ background-color: #E8152F; }}
            QPushButton:pressed {{ background-color: #A00C24; }}
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
        # Búsqueda con debounce 400ms
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._load)
        self.search_input.textChanged.connect(
            lambda: self._search_timer.start(400)
        )

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
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Documento", "Teléfono",
            "Email", "Estado", "Arte Marcial"
        ])

        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 50)
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
                gridline-color: transparent;
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

        # Doble click → detalle
        table.doubleClicked.connect(self._view_detail)

        # Menú contextual con botones de acción en cada fila
        table.cellClicked.connect(self._on_cell_click)

        return table

    # ── Cargar datos ──────────────────────────────────────────────────
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
            # Columnas: id, nombre, documento, teléfono, email, estado, arte
            values = [row[0], row[1], row[2], row[3] or "—",
                      row[4] or "—", row[5], row[6]]
            for j, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

                # Color del estado
                if j == 5:
                    estado = str(val).lower()
                    if "activo" in estado:
                        item.setForeground(QColor(GREEN))
                    elif "inactivo" in estado or "suspendido" in estado:
                        item.setForeground(QColor("#FF4444"))
                    else:
                        item.setForeground(QColor(YELLOW))

                self.table.setItem(i, j, item)
            self.table.setRowHeight(i, 44)

        total = len(rows)
        self.lbl_count.setText(
            f"{total} estudiante{'s' if total != 1 else ''} encontrado{'s' if total != 1 else ''}"
        )

    # ── Acciones ──────────────────────────────────────────────────────
    def _get_selected_id(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._rows):
            return None
        return self._rows[row][0]

    def _on_cell_click(self, row, col):
        pass  # selección normal, doble click para detalle

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

        # Nombre del estudiante seleccionado
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

    # Botón editar accesible desde la barra de herramientas también
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self._view_detail()
        elif event.key() == Qt.Key.Key_E:
            self._edit_student()
        super().keyPressEvent(event)