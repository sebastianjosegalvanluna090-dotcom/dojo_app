from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QPushButton,
    QLabel, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor

# ─── PALETA ───────────────────────────────────────────────────────────
BG_DARK    = "#0D0D0D"
BG_CARD    = "#161616"
BORDER     = "#2A2A2A"
INPUT_BG   = "#1E1E1E"
INPUT_BDR  = "#333333"
RED        = "#C8102E"
TEXT_PRI   = "#F0F0F0"
TEXT_SEC   = "#888888"
GREEN      = "#22C55E"
ERROR_C    = "#FF4444"

INPUT_STYLE = f"""
    QLineEdit, QComboBox, QDateEdit {{
        background-color: {INPUT_BG};
        color: {TEXT_PRI};
        border: 1.5px solid {INPUT_BDR};
        border-radius: 7px;
        padding: 6px 12px;
        font-size: 13px;
        min-height: 34px;
    }}
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
        border: 1.5px solid {RED};
    }}
    QComboBox::drop-down {{ border: none; padding-right: 8px; }}
    QComboBox QAbstractItemView {{
        background-color: {INPUT_BG};
        color: {TEXT_PRI};
        selection-background-color: {RED};
        border: 1px solid {BORDER};
    }}
    QDateEdit::up-button, QDateEdit::down-button {{ width: 0; }}
"""


class StudentForm(QDialog):
    def __init__(self, repo, student_id: int = None, parent=None):
        super().__init__(parent)
        self.repo       = repo
        self.student_id = student_id
        self.is_edit    = student_id is not None

        self.setWindowTitle("Editar Estudiante" if self.is_edit else "Nuevo Estudiante")
        self.setFixedSize(480, 560)
        self.setStyleSheet(f"background-color: {BG_DARK}; color: {TEXT_PRI};")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        self._build_ui()
        self._load_combos()
        if self.is_edit:
            self._load_student()

    # ── UI ────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # Título
        title = QLabel("✏️  Editar Estudiante" if self.is_edit else "➕  Nuevo Estudiante")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT_PRI};")
        root.addWidget(title)

        # Separador
        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.4 {RED}, stop:1 transparent);
            border: none;
        """)
        root.addWidget(sep)

        # Formulario
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        label_style = f"color: {TEXT_SEC}; font-size: 12px; font-weight: 600;"

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet(label_style)
            return l

        self.inp_first  = QLineEdit()
        self.inp_last   = QLineEdit()
        self.inp_phone  = QLineEdit()
        self.inp_email  = QLineEdit()
        self.inp_birth  = QDateEdit()
        self.inp_birth.setCalendarPopup(True)
        self.inp_birth.setDate(QDate.currentDate().addYears(-18))
        self.inp_doc    = QLineEdit()
        self.cmb_doctype = QComboBox()
        self.cmb_status  = QComboBox()

        for w in [self.inp_first, self.inp_last, self.inp_phone,
                  self.inp_email, self.inp_birth, self.inp_doc,
                  self.cmb_doctype, self.cmb_status]:
            w.setStyleSheet(INPUT_STYLE)

        form.addRow(lbl("Nombre *"),      self.inp_first)
        form.addRow(lbl("Apellido *"),     self.inp_last)
        form.addRow(lbl("Teléfono"),       self.inp_phone)
        form.addRow(lbl("Email"),          self.inp_email)
        form.addRow(lbl("Nacimiento"),     self.inp_birth)
        form.addRow(lbl("Tipo Doc."),      self.cmb_doctype)
        form.addRow(lbl("Nº Documento"),   self.inp_doc)
        form.addRow(lbl("Estado"),         self.cmb_status)

        root.addLayout(form)

        # Mensaje de error
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(f"color: {ERROR_C}; font-size: 12px;")
        self.lbl_error.setWordWrap(True)
        root.addWidget(self.lbl_error)

        root.addStretch()

        # Botones
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(40)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 7px; font-size: 13px;
            }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Guardar Cambios" if self.is_edit else "Crear Estudiante")
        self.btn_save.setFixedHeight(40)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED}; color: white;
                border: none; border-radius: 7px;
                font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: #E8152F; }}
            QPushButton:pressed {{ background-color: #A00C24; }}
        """)
        self.btn_save.clicked.connect(self._save)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self.btn_save)
        root.addLayout(btn_row)

    # ── Cargar combos ─────────────────────────────────────────────────
    def _load_combos(self):
        # Tipo de documento
        self.cmb_doctype.addItem("Seleccionar...", None)
        for doc_id, doc_name in self.repo.get_type_documents():
            self.cmb_doctype.addItem(doc_name, doc_id)

        # Estado
        self.cmb_status.addItem("Seleccionar...", None)
        for st_id, st_name in self.repo.get_statuses():
            self.cmb_status.addItem(st_name, st_id)

    # ── Cargar datos del estudiante (modo edición) ────────────────────
    def _load_student(self):
        data = self.repo.get_by_id(self.student_id)
        if not data:
            return
        self.inp_first.setText(data["first_name"] or "")
        self.inp_last.setText(data["last_name"] or "")
        self.inp_phone.setText(data["phone"] or "")
        self.inp_email.setText(data["email"] or "")
        if data["birthdate"]:
            d = data["birthdate"]
            self.inp_birth.setDate(QDate(d.year, d.month, d.day))
        self.inp_doc.setText(data["document"] or "")

        # Seleccionar combo tipo doc
        for i in range(self.cmb_doctype.count()):
            if self.cmb_doctype.itemData(i) == data["id_type_document"]:
                self.cmb_doctype.setCurrentIndex(i)
                break

        # Seleccionar combo estado
        for i in range(self.cmb_status.count()):
            if self.cmb_status.itemData(i) == data["id_status"]:
                self.cmb_status.setCurrentIndex(i)
                break

    # ── Guardar ───────────────────────────────────────────────────────
    def _save(self):
        self.lbl_error.setText("")

        first = self.inp_first.text().strip()
        last  = self.inp_last.text().strip()

        if not first or not last:
            self.lbl_error.setText("⚠  Nombre y apellido son obligatorios.")
            return

        birth = self.inp_birth.date()
        data = {
            "first_name":       first,
            "last_name":        last,
            "phone":            self.inp_phone.text().strip() or None,
            "email":            self.inp_email.text().strip() or None,
            "birthdate":        birth.toPyDate(),
            "document":         self.inp_doc.text().strip() or None,
            "id_type_document": self.cmb_doctype.currentData(),
            "id_status":        self.cmb_status.currentData(),
            "category_id":      None,
        }

        self.btn_save.setEnabled(False)
        self.btn_save.setText("Guardando...")
        try:
            if self.is_edit:
                self.repo.update(self.student_id, data)
            else:
                self.repo.create(data)
            self.accept()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")
            self.btn_save.setEnabled(True)
            self.btn_save.setText("Guardar Cambios" if self.is_edit else "Crear Estudiante")