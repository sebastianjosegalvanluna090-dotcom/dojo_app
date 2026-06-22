"""
views/instructors_view.py
Vista de gestión de instructores — se embebe en SettingsView (página Instructores).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QMessageBox, QDialog,
    QListWidget, QListWidgetItem, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QColor

from repositories.instructors_repository import InstructorsRepository

# ─── PALETA ───────────────────────────────────────────────────────────
BG_MAIN  = "#0D0D0D"
BG_CARD  = "#161616"
BG_TABLE = "#121212"
BG_INPUT = "#1C1C1C"
BORDER   = "#2A2A2A"
RED      = "#C8102E"
RED_H    = "#E8152F"
RED_DARK = "#7A0A1C"
TEXT_PRI = "#F0F0F0"
TEXT_SEC = "#888888"
TEXT_MUT = "#444444"
GREEN    = "#22C55E"
BLUE     = "#3B82F6"
ORANGE   = "#F97316"

FIELD_STYLE = f"""
    QLineEdit {{
        background-color: {BG_INPUT}; color: {TEXT_PRI};
        border: 1.5px solid {BORDER}; border-radius: 8px;
        padding: 0 12px; font-size: 13px;
        min-height: 38px; max-height: 38px;
    }}
    QLineEdit:focus {{ border-color: {RED}; background-color: #1A0A0C; }}
"""


def _lbl(text):
    l = QLabel(text)
    l.setStyleSheet(
        f"color: {TEXT_SEC}; font-size: 10px; font-weight: 700; letter-spacing: 0.8px;"
    )
    return l


def _make_card(accent=None):
    card = QFrame()
    bl = f"border-left: 3px solid {accent};" if accent else ""
    card.setStyleSheet(f"""
        QFrame {{
            background-color: {BG_CARD}; border: 1px solid {BORDER};
            {bl} border-radius: 10px;
        }}
        QFrame * {{ border: none; background: transparent; }}
    """)
    return card


# ─── Worker ───────────────────────────────────────────────────────────
class LoadWorker(QThread):
    done = pyqtSignal(list)

    def __init__(self, repo, search=""):
        super().__init__()
        self.repo   = repo
        self.search = search

    def run(self):
        try:
            self.done.emit(self.repo.get_all(self.search))
        except Exception as e:
            print(f"[Instructors error] {e}")
            self.done.emit([])


# ─── FORMULARIO CREAR / EDITAR ────────────────────────────────────────
class InstructorFormDialog(QDialog):
    def __init__(self, repo, instructor_id=None, parent=None):
        super().__init__(parent)
        self.repo          = repo
        self.instructor_id = instructor_id
        self.is_edit       = instructor_id is not None

        self.setWindowTitle("Editar Instructor" if self.is_edit else "Nuevo Instructor")
        self.setFixedSize(500, 320 if self.is_edit else 440)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: #111111; color: {TEXT_PRI};")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        if self.is_edit:
            self._build_edit_ui(root)
        else:
            self._build_create_ui(root)

    # ── Modo crear ────────────────────────────────────────────────────
    def _build_create_ui(self, root):
        # Toggle existente / nueva persona
        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(0)
        self.btn_existing   = QPushButton("Persona existente")
        self.btn_new_person = QPushButton("Nueva persona")
        for btn in [self.btn_existing, self.btn_new_person]:
            btn.setFixedHeight(36)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_existing.setChecked(True)
        self._style_toggle(self.btn_existing, True)
        self._style_toggle(self.btn_new_person, False)
        self.btn_existing.clicked.connect(lambda: self._switch_mode(True))
        self.btn_new_person.clicked.connect(lambda: self._switch_mode(False))
        toggle_row.addWidget(self.btn_existing)
        toggle_row.addWidget(self.btn_new_person)
        root.addLayout(toggle_row)

        # ── Panel: persona existente
        self.panel_existing = QWidget()
        self.panel_existing.setStyleSheet("background: transparent;")
        pe = QVBoxLayout(self.panel_existing)
        pe.setContentsMargins(0, 8, 0, 0)
        pe.setSpacing(8)

        pe.addWidget(_lbl("BUSCAR PERSONA"))
        self.search_person = QLineEdit()
        self.search_person.setPlaceholderText("🔍  Nombre, email o teléfono...")
        self.search_person.setStyleSheet(FIELD_STYLE)
        self.search_person.textChanged.connect(self._filter_people)
        pe.addWidget(self.search_person)

        self.people_list = QListWidget()
        self.people_list.setMinimumHeight(180)
        self.people_list.setStyleSheet(f"""
            QListWidget {{
                background: #1A1A1A; border: 1.5px solid {BORDER};
                border-radius: 8px; color: {TEXT_PRI}; font-size: 13px;
            }}
            QListWidget::item {{ padding: 8px 12px; border-bottom: 1px solid {BORDER}; }}
            QListWidget::item:selected {{ background: #2A0A0C; color: {TEXT_PRI}; border-left: 3px solid {RED}; }}
            QListWidget::item:hover {{ background: #222222; }}
        """)
        pe.addWidget(self.people_list)
        root.addWidget(self.panel_existing)

        self._all_people = self.repo.get_people_not_instructors()
        self._populate_people(self._all_people)

        # ── Panel: nueva persona
        self.panel_new = QWidget()
        self.panel_new.setStyleSheet("background: transparent;")
        pn = QVBoxLayout(self.panel_new)
        pn.setContentsMargins(0, 8, 0, 0)
        pn.setSpacing(8)

        name_row = QHBoxLayout()
        name_row.setSpacing(12)
        c1 = QVBoxLayout(); c1.addWidget(_lbl("NOMBRE *"))
        self.inp_first = QLineEdit(); self.inp_first.setPlaceholderText("Nombre")
        self.inp_first.setStyleSheet(FIELD_STYLE); c1.addWidget(self.inp_first)
        c2 = QVBoxLayout(); c2.addWidget(_lbl("APELLIDO *"))
        self.inp_last = QLineEdit(); self.inp_last.setPlaceholderText("Apellido")
        self.inp_last.setStyleSheet(FIELD_STYLE); c2.addWidget(self.inp_last)
        name_row.addLayout(c1); name_row.addLayout(c2)
        pn.addLayout(name_row)

        pn.addWidget(_lbl("EMAIL"))
        self.inp_email = QLineEdit()
        self.inp_email.setPlaceholderText("correo@ejemplo.com")
        self.inp_email.setStyleSheet(FIELD_STYLE)
        pn.addWidget(self.inp_email)

        pn.addWidget(_lbl("TELÉFONO"))
        self.inp_phone = QLineEdit()
        self.inp_phone.setPlaceholderText("+57 300 000 0000")
        self.inp_phone.setStyleSheet(FIELD_STYLE)
        pn.addWidget(self.inp_phone)

        self.panel_new.setVisible(False)
        root.addWidget(self.panel_new)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #FF4444; font-size: 11px;")
        root.addWidget(self.lbl_error)
        root.addStretch()
        root.addLayout(self._btn_row("Crear Instructor", self._save_create))

    # ── Modo editar ───────────────────────────────────────────────────
    def _build_edit_ui(self, root):
        name_row = QHBoxLayout(); name_row.setSpacing(12)
        c1 = QVBoxLayout(); c1.addWidget(_lbl("NOMBRE *"))
        self.inp_first = QLineEdit(); self.inp_first.setStyleSheet(FIELD_STYLE)
        c1.addWidget(self.inp_first)
        c2 = QVBoxLayout(); c2.addWidget(_lbl("APELLIDO *"))
        self.inp_last = QLineEdit(); self.inp_last.setStyleSheet(FIELD_STYLE)
        c2.addWidget(self.inp_last)
        name_row.addLayout(c1); name_row.addLayout(c2)
        root.addLayout(name_row)

        root.addWidget(_lbl("EMAIL"))
        self.inp_email = QLineEdit(); self.inp_email.setStyleSheet(FIELD_STYLE)
        root.addWidget(self.inp_email)

        root.addWidget(_lbl("TELÉFONO"))
        self.inp_phone = QLineEdit(); self.inp_phone.setStyleSheet(FIELD_STYLE)
        root.addWidget(self.inp_phone)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #FF4444; font-size: 11px;")
        root.addWidget(self.lbl_error)
        root.addStretch()
        root.addLayout(self._btn_row("Guardar Cambios", self._save_edit))
        self._load_edit_data()

    def _load_edit_data(self):
        data = self.repo.get_by_id(self.instructor_id)
        if data:
            self.inp_first.setText(data.get("first_name") or "")
            self.inp_last.setText(data.get("last_name") or "")
            self.inp_email.setText(data.get("email") or "")
            self.inp_phone.setText(data.get("phone") or "")

    # ── Helpers ───────────────────────────────────────────────────────
    def _btn_row(self, save_label, save_fn):
        row = QHBoxLayout(); row.setSpacing(10)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 8px; font-size: 13px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; }}
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton(save_label)
        btn_save.setFixedHeight(38)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white; border: none;
                border-radius: 8px; font-size: 13px; font-weight: 700; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        btn_save.clicked.connect(save_fn)
        row.addWidget(btn_cancel); row.addWidget(btn_save)
        return row

    def _style_toggle(self, btn, active):
        if active:
            btn.setStyleSheet(f"""
                QPushButton {{ background: {RED}; color: white; border: none;
                    border-radius: 8px; font-size: 13px; font-weight: 700; }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{ background: #1E1E1E; color: {TEXT_SEC};
                    border: 1.5px solid {BORDER}; border-radius: 8px; font-size: 13px; }}
                QPushButton:hover {{ color: {TEXT_PRI}; }}
            """)

    def _switch_mode(self, existing: bool):
        self._style_toggle(self.btn_existing, existing)
        self._style_toggle(self.btn_new_person, not existing)
        self.panel_existing.setVisible(existing)
        self.panel_new.setVisible(not existing)

    def _populate_people(self, people):
        self.people_list.clear()
        if not people:
            item = QListWidgetItem("Sin personas disponibles para asignar")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setForeground(QColor(TEXT_MUT))
            self.people_list.addItem(item)
            return
        for p in people:
            item = QListWidgetItem(f"👤  {p['nombre']}  —  {p['email']}")
            item.setData(Qt.ItemDataRole.UserRole, p)
            self.people_list.addItem(item)

    def _filter_people(self, text):
        text = text.lower()
        filtered = [
            p for p in self._all_people
            if text in p["nombre"].lower()
            or text in p["email"].lower()
            or text in p["telefono"].lower()
        ]
        self._populate_people(filtered)

    def _save_create(self):
        self.lbl_error.setText("")
        if self.panel_existing.isVisible():
            item = self.people_list.currentItem()
            if not item or not item.data(Qt.ItemDataRole.UserRole):
                self.lbl_error.setText("⚠ Selecciona una persona de la lista.")
                return
            person = item.data(Qt.ItemDataRole.UserRole)
            try:
                self.repo.create_from_person(person["id"])
                self.accept()
            except Exception as e:
                self.lbl_error.setText(f"Error: {e}")
            return

        first = self.inp_first.text().strip()
        last  = self.inp_last.text().strip()
        if not first or not last:
            self.lbl_error.setText("⚠ Nombre y apellido son obligatorios.")
            return
        try:
            self.repo.create_person_and_instructor({
                "first_name": first, "last_name": last,
                "email":      self.inp_email.text().strip() or None,
                "phone":      self.inp_phone.text().strip() or None,
                "birthdate":  None,
            })
            self.accept()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")

    def _save_edit(self):
        self.lbl_error.setText("")
        first = self.inp_first.text().strip()
        last  = self.inp_last.text().strip()
        if not first or not last:
            self.lbl_error.setText("⚠ Nombre y apellido son obligatorios.")
            return
        try:
            self.repo.update(self.instructor_id, {
                "first_name": first, "last_name": last,
                "email":      self.inp_email.text().strip() or None,
                "phone":      self.inp_phone.text().strip() or None,
                "birthdate":  None,
            })
            self.accept()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")


# ─── GESTIÓN DE ARTES MARCIALES DEL INSTRUCTOR ───────────────────────
class MartialArtsDialog(QDialog):
    def __init__(self, repo, instructor_id, parent=None):
        super().__init__(parent)
        self.repo          = repo
        self.instructor_id = instructor_id
        self.setWindowTitle("Artes Marciales del Instructor")
        self.setFixedSize(460, 420)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: #111111; color: {TEXT_PRI};")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(10)

        root.addWidget(self._slbl("ASIGNADAS"))
        self.assigned_list = QListWidget()
        self.assigned_list.setMinimumHeight(110)
        self.assigned_list.setStyleSheet(f"""
            QListWidget {{ background: #1A1A1A; border: 1.5px solid {BORDER};
                border-radius: 8px; color: {TEXT_PRI}; font-size: 13px; }}
            QListWidget::item {{ padding: 7px 12px; border-bottom: 1px solid {BORDER}; }}
            QListWidget::item:selected {{ background: #2A0A0C; border-left: 3px solid {RED}; }}
            QListWidget::item:hover {{ background: #222; }}
        """)
        root.addWidget(self.assigned_list)

        btn_remove = QPushButton("🗑  Quitar seleccionada")
        btn_remove.setFixedHeight(32)
        btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_remove.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: #FF4444;
                border: 1px solid #FF4444; border-radius: 7px; font-size: 12px; }}
            QPushButton:hover {{ background: #2A0A0A; }}
        """)
        btn_remove.clicked.connect(self._remove_ma)
        root.addWidget(btn_remove)

        sep = QFrame(); sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER};")
        root.addWidget(sep)

        root.addWidget(self._slbl("AGREGAR ARTE MARCIAL"))
        self.cmb_ma = QListWidget()
        self.cmb_ma.setMaximumHeight(100)
        self.cmb_ma.setStyleSheet(f"""
            QListWidget {{ background: #1A1A1A; border: 1.5px solid {BORDER};
                border-radius: 8px; color: {TEXT_PRI}; font-size: 13px; }}
            QListWidget::item {{ padding: 6px 12px; border-bottom: 1px solid {BORDER}; }}
            QListWidget::item:selected {{ background: #2A0A0C; border-left: 3px solid {RED}; }}
            QListWidget::item:hover {{ background: #222; }}
        """)
        root.addWidget(self.cmb_ma)

        self.chk_promote = QCheckBox("Puede promover estudiantes")
        self.chk_promote.setStyleSheet(f"""
            QCheckBox {{ color: {TEXT_PRI}; font-size: 13px; }}
            QCheckBox::indicator {{ width: 16px; height: 16px;
                border: 1.5px solid {BORDER}; border-radius: 4px; background: {BG_INPUT}; }}
            QCheckBox::indicator:checked {{ background: {RED}; border-color: {RED}; }}
        """)
        root.addWidget(self.chk_promote)

        btn_add = QPushButton("＋  Agregar arte marcial")
        btn_add.setFixedHeight(38)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white; border: none;
                border-radius: 8px; font-size: 13px; font-weight: 700; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        btn_add.clicked.connect(self._add_ma)
        root.addWidget(btn_add)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #FF4444; font-size: 11px;")
        root.addWidget(self.lbl_error)

        btn_close = QPushButton("Cerrar")
        btn_close.setFixedHeight(34)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 7px; font-size: 13px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; }}
        """)
        btn_close.clicked.connect(self.accept)
        root.addWidget(btn_close)

        self._load_data()

    def _slbl(self, text):
        l = QLabel(text)
        l.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; font-weight: 700; letter-spacing: 0.8px;")
        return l

    def _load_data(self):
        self.assigned_list.clear()
        assigned = self.repo.get_instructor_martial_arts(self.instructor_id)
        assigned_ids = set()
        for a in assigned:
            promo = "  ★ Puede promover" if a["can_promote"] else ""
            item = QListWidgetItem(f"🥋  {a['ma_name']}{promo}")
            item.setData(Qt.ItemDataRole.UserRole, a)
            self.assigned_list.addItem(item)
            assigned_ids.add(a["ma_id"])

        self.cmb_ma.clear()
        for ma in self.repo.get_martial_arts():
            if ma["id"] not in assigned_ids:
                item = QListWidgetItem(ma["name"])
                item.setData(Qt.ItemDataRole.UserRole, ma)
                self.cmb_ma.addItem(item)

    def _add_ma(self):
        self.lbl_error.setText("")
        item = self.cmb_ma.currentItem()
        if not item:
            self.lbl_error.setText("⚠ Selecciona un arte marcial.")
            return
        ma = item.data(Qt.ItemDataRole.UserRole)
        try:
            self.repo.assign_instructor_martial_art(
                self.instructor_id, ma["id"], self.chk_promote.isChecked()
            )
            self.chk_promote.setChecked(False)
            self._load_data()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")

    def _remove_ma(self):
        self.lbl_error.setText("")
        item = self.assigned_list.currentItem()
        if not item:
            self.lbl_error.setText("⚠ Selecciona una asignación para quitar.")
            return
        a = item.data(Qt.ItemDataRole.UserRole)
        try:
            self.repo.remove_instructor_martial_art(a["id"])
            self._load_data()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")


# ─── DETALLE DEL INSTRUCTOR ───────────────────────────────────────────
class InstructorDetail(QDialog):
    def __init__(self, instructor_id, repo, parent=None):
        super().__init__(parent)
        self.instructor_id = instructor_id
        self.repo          = repo
        self.setWindowTitle("Detalle del Instructor")
        self.setFixedSize(660, 520)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet("background-color: #111111; color: #F0F0F0;")

        data    = repo.get_by_id(instructor_id)
        classes = repo.get_recent_classes(instructor_id)
        total_c = repo.get_class_count(instructor_id)
        mas     = repo.get_instructor_martial_arts(instructor_id)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 20)
        root.setSpacing(14)

        # ── Cabecera
        hdr = QHBoxLayout(); hdr.setSpacing(16)
        nombre = f"{(data or {}).get('first_name','')} {(data or {}).get('last_name','')}".strip()
        initials = "".join(p[0].upper() for p in nombre.split()[:2] if p)
        avatar = QLabel(initials or "?")
        avatar.setFixedSize(64, 64)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(
            "background-color: #1A1A1A; color: #C8102E; font-size: 20px; "
            "font-weight: 700; border-radius: 32px; border: 2px solid #2A2A2A;"
        )
        info_col = QVBoxLayout(); info_col.setSpacing(4)
        lbl_name = QLabel(nombre or "—")
        lbl_name.setStyleSheet("font-size: 17px; font-weight: 700; color: #F0F0F0;")
        lbl_sub = QLabel(
            f"Instructor  ·  ID: {(data or {}).get('id','—')}  ·  "
            f"{total_c} clase{'s' if total_c != 1 else ''} impartida{'s' if total_c != 1 else ''}"
        )
        lbl_sub.setStyleSheet("font-size: 11px; color: #666;")
        info_col.addWidget(lbl_name); info_col.addWidget(lbl_sub)
        badge = QLabel("🥋  Instructor")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter); badge.setFixedHeight(26)
        badge.setStyleSheet(f"""
            background-color: #1A1000; color: {ORANGE};
            border: 1px solid {ORANGE}; border-radius: 6px;
            font-size: 11px; font-weight: 600; padding: 0 12px;
        """)
        hdr.addWidget(avatar); hdr.addLayout(info_col, 1)
        hdr.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)
        root.addLayout(hdr)

        sep = QFrame(); sep.setFixedHeight(2)
        sep.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #C8102E, stop:0.4 #C8102E, stop:1 transparent); border: none;
        """)
        root.addWidget(sep)

        # ── Tarjetas
        cards_row = QHBoxLayout(); cards_row.setSpacing(12)

        personal = _make_card()
        pl = QVBoxLayout(personal)
        pl.setContentsMargins(14, 14, 14, 14); pl.setSpacing(6)
        pl.addWidget(self._slbl("DATOS PERSONALES"))
        pl.addLayout(self._drow("Email",    (data or {}).get("email") or "—"))
        pl.addLayout(self._drow("Teléfono", (data or {}).get("phone") or "—"))
        pl.addWidget(self._slbl("ARTES MARCIALES"))
        if mas:
            for m in mas:
                r = QHBoxLayout()
                dot = QLabel("●"); dot.setStyleSheet(f"color: {RED}; font-size: 10px;"); dot.setFixedWidth(14)
                lbl_ma = QLabel(m["ma_name"]); lbl_ma.setStyleSheet("color: #F0F0F0; font-size: 12px;")
                promo = QLabel("★ Puede promover" if m["can_promote"] else "")
                promo.setStyleSheet(f"color: {ORANGE}; font-size: 10px;")
                r.addWidget(dot); r.addWidget(lbl_ma, 1); r.addWidget(promo)
                pl.addLayout(r)
        else:
            none_ma = QLabel("Sin artes marciales asignadas")
            none_ma.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px;")
            pl.addWidget(none_ma)
        pl.addStretch()
        cards_row.addWidget(personal)

        classes_card = _make_card()
        cl = QVBoxLayout(classes_card)
        cl.setContentsMargins(14, 14, 14, 14); cl.setSpacing(6)
        cl.addWidget(self._slbl("ÚLTIMAS CLASES"))
        if classes:
            for fecha, clase, arte in classes:
                r = QHBoxLayout()
                dot = QLabel("●"); dot.setStyleSheet(f"color: {BLUE}; font-size: 10px;"); dot.setFixedWidth(14)
                lbl_c = QLabel(str(clase)); lbl_c.setStyleSheet("color: #F0F0F0; font-size: 12px;")
                lbl_d = QLabel(str(fecha)); lbl_d.setStyleSheet("color: #555; font-size: 11px;")
                lbl_d.setAlignment(Qt.AlignmentFlag.AlignRight)
                r.addWidget(dot); r.addWidget(lbl_c, 1); r.addWidget(lbl_d)
                cl.addLayout(r)
        else:
            none_c = QLabel("Sin clases registradas")
            none_c.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px;")
            cl.addWidget(none_c)
        cl.addStretch()
        cards_row.addWidget(classes_card)
        root.addLayout(cards_row, 1)

        # ── Botones
        btn_row = QHBoxLayout(); btn_row.setSpacing(10)
        btn_ma = QPushButton("🥋  Artes Marciales")
        btn_ma.setFixedHeight(38); btn_ma.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ma.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {ORANGE};
                border: 1px solid {ORANGE}; border-radius: 7px; font-size: 13px; }}
            QPushButton:hover {{ background: #1A1000; }}
        """)
        btn_ma.clicked.connect(self._manage_martial_arts)

        btn_edit = QPushButton("✎  Editar")
        btn_edit.setFixedHeight(38); btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 7px; font-size: 13px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; }}
        """)
        btn_edit.clicked.connect(self._open_edit)

        btn_close = QPushButton("Cerrar")
        btn_close.setFixedHeight(38); btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white; border: none;
                border-radius: 7px; font-size: 13px; font-weight: 700; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        btn_close.clicked.connect(self.reject)

        btn_row.addWidget(btn_ma); btn_row.addStretch()
        btn_row.addWidget(btn_edit); btn_row.addWidget(btn_close)
        root.addLayout(btn_row)

    def _slbl(self, text):
        l = QLabel(text)
        l.setStyleSheet("font-size: 10px; font-weight: 700; letter-spacing: 1px; color: #555; padding: 6px 0 4px 0;")
        return l

    def _drow(self, key, val, val_color="#F0F0F0"):
        k = QLabel(key); k.setStyleSheet("color: #555; font-size: 12px;")
        v = QLabel(str(val)); v.setStyleSheet(f"color: {val_color}; font-size: 12px;")
        v.setAlignment(Qt.AlignmentFlag.AlignRight)
        r = QHBoxLayout(); r.addWidget(k); r.addWidget(v, 1)
        return r

    def _open_edit(self):
        dlg = InstructorFormDialog(self.repo, instructor_id=self.instructor_id, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.accept()

    def _manage_martial_arts(self):
        dlg = MartialArtsDialog(self.repo, self.instructor_id, parent=self)
        dlg.exec()
        self.accept()


# ─── VISTA PRINCIPAL ──────────────────────────────────────────────────
class InstructorsView(QWidget):
    def __init__(self):
        super().__init__()
        self.repo  = InstructorsRepository()
        self._rows = []
        self._build_ui()
        self._load()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {BG_MAIN};")
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # Encabezado
        hdr = QHBoxLayout()
        title = QLabel("🥋  Instructores")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_PRI};")

        self.btn_delete = QPushButton("🗑  Eliminar")
        self.btn_delete.setFixedHeight(38)
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: #FF4444;
                border: 1px solid #FF4444; border-radius: 7px;
                font-size: 13px; font-weight: 600; padding: 0 18px; }}
            QPushButton:hover {{ background: #2A0A0A; }}
        """)
        self.btn_delete.clicked.connect(self._delete_instructor)

        self.btn_new = QPushButton("＋  Nuevo Instructor")
        self.btn_new.setFixedHeight(38)
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white; border: none;
                border-radius: 7px; font-size: 13px; font-weight: 600; padding: 0 18px; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        self.btn_new.clicked.connect(self._create_instructor)

        hdr.addWidget(title); hdr.addStretch()
        hdr.addWidget(self.btn_delete); hdr.addWidget(self.btn_new)
        root.addLayout(hdr)

        sep = QFrame(); sep.setFixedHeight(2)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.4 {RED}, stop:1 transparent); border: none;
        """)
        root.addWidget(sep)

        # Barra de herramientas
        toolbar = QHBoxLayout(); toolbar.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Buscar por nombre, email o teléfono...")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{ background: #1E1E1E; color: {TEXT_PRI};
                border: 1.5px solid #333; border-radius: 7px;
                padding: 0 14px; font-size: 13px; }}
            QLineEdit:focus {{ border-color: {RED}; }}
        """)
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._load)
        self.search_input.textChanged.connect(lambda: self._search_timer.start(400))

        btn_refresh = QPushButton("↻  Actualizar")
        btn_refresh.setFixedHeight(38); btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 7px;
                font-size: 12px; padding: 0 14px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; }}
        """)
        btn_refresh.clicked.connect(self._load)

        btn_edit = QPushButton("✎  Editar")
        btn_edit.setFixedHeight(38); btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 7px;
                font-size: 12px; padding: 0 14px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; }}
        """)
        btn_edit.clicked.connect(self._edit_instructor)

        toolbar.addWidget(self.search_input, 1)
        toolbar.addWidget(btn_refresh); toolbar.addWidget(btn_edit)
        root.addLayout(toolbar)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Email", "Teléfono"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 60)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{ background-color: {BG_TABLE}; alternate-background-color: #141414;
                color: {TEXT_PRI}; border: 1px solid {BORDER};
                border-radius: 10px; font-size: 13px; }}
            QHeaderView::section {{ background-color: {BG_CARD}; color: {TEXT_SEC};
                border: none; border-bottom: 1px solid {BORDER};
                padding: 8px 10px; font-size: 11px; font-weight: 600; letter-spacing: 1px; }}
            QTableWidget::item {{ padding: 8px 10px; border-bottom: 1px solid #1A1A1A; }}
            QTableWidget::item:selected {{ background-color: {RED_DARK}; color: white; }}
        """)
        self.table.doubleClicked.connect(self._view_detail)
        root.addWidget(self.table, 1)

        self.lbl_count = QLabel("Cargando...")
        self.lbl_count.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px;")
        root.addWidget(self.lbl_count)

    def _load(self):
        self.lbl_count.setText("Cargando...")
        self._worker = LoadWorker(self.repo, self.search_input.text().strip())
        self._worker.done.connect(self._on_data)
        self._worker.start()

    def _on_data(self, rows):
        self._rows = rows
        self.table.setRowCount(0)
        if not rows:
            self.lbl_count.setText("No se encontraron instructores.")
            return
        self.table.setRowCount(len(rows))
        # Tupla: (id, nombre, telefono, email, fecha_registro, id_person, ...)
        for i, r in enumerate(rows):
            # Columnas: ID, Nombre, Email (índice 3), Teléfono (índice 2)
            for j, val in enumerate([r[0], r[1], r[3], r[2]]):
                item = QTableWidgetItem(str(val) if val else "—")
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter |
                    (Qt.AlignmentFlag.AlignHCenter if j == 0 else Qt.AlignmentFlag.AlignLeft)
                )
                self.table.setItem(i, j, item)
            self.table.setRowHeight(i, 44)
        total = len(rows)
        self.lbl_count.setText(
            f"{total} instructor{'es' if total != 1 else ''} encontrado{'s' if total != 1 else ''}"
        )

    def _get_selected(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._rows):
            return None
        return self._rows[row]

    def _view_detail(self):
        r = self._get_selected()
        if not r:
            return
        dlg = InstructorDetail(r[0], self.repo, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load()

    def _create_instructor(self):
        dlg = InstructorFormDialog(self.repo, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load()

    def _edit_instructor(self):
        r = self._get_selected()
        if not r:
            QMessageBox.information(self, "Aviso", "Selecciona un instructor primero.")
            return
        dlg = InstructorFormDialog(self.repo, instructor_id=r[0], parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load()

    def _delete_instructor(self):
        r = self._get_selected()
        if not r:
            QMessageBox.information(self, "Aviso", "Selecciona un instructor primero.")
            return
        confirm = QMessageBox(self)
        confirm.setWindowTitle("Confirmar eliminación")
        confirm.setText(f"¿Eliminar a {r[1]} como instructor?")
        confirm.setInformativeText(
            "No se puede eliminar si tiene clases asignadas.\n"
            "El registro de persona también se eliminará."
        )
        confirm.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        confirm.setDefaultButton(QMessageBox.StandardButton.Cancel)
        confirm.setStyleSheet("background-color: #161616; color: #F0F0F0;")
        if confirm.exec() == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete(r[0])
                self._load()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{e}")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._view_detail()
        elif event.key() == Qt.Key.Key_E:
            self._edit_instructor()
        super().keyPressEvent(event)