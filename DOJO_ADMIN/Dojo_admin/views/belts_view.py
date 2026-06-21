from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QLineEdit, QComboBox, QMessageBox, QScrollArea,
    QSizePolicy, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from repositories.belts_repository import BeltsRepository

BG_MAIN  = "#0D0D0D"
BG_CARD  = "#161616"
BG_TABLE = "#121212"
BG_INPUT = "#1C1C1C"
BORDER   = "#2A2A2A"
RED      = "#C8102E"
RED_H    = "#E8152F"
TEXT_PRI = "#F0F0F0"
TEXT_SEC = "#888888"
TEXT_MUT = "#444444"
GREEN    = "#22C55E"
BLUE     = "#3B82F6"
YELLOW   = "#EAB308"

FIELD_STYLE = f"""
    QLineEdit, QComboBox {{
        background-color: {BG_INPUT};
        color: {TEXT_PRI};
        border: 1.5px solid {BORDER};
        border-radius: 8px;
        padding: 0 12px;
        font-size: 13px;
        min-height: 38px;
    }}
    QLineEdit:focus, QComboBox:focus {{ border-color: {RED}; }}
    QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox QAbstractItemView {{
        background-color: {BG_INPUT}; color: {TEXT_PRI};
        selection-background-color: {RED};
        border: 1px solid {BORDER}; border-radius: 6px;
    }}
"""


def make_card(accent=None):
    card = QFrame()
    border_left = f"border-left: 3px solid {accent};" if accent else ""
    card.setStyleSheet(f"""
        QFrame {{
            background-color: {BG_CARD};
            border: 1px solid {BORDER};
            {border_left}
            border-radius: 10px;
        }}
        QFrame * {{ border: none; background: transparent; }}
    """)
    return card


def _lbl(text):
    l = QLabel(text)
    l.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 600;")
    return l


class MartialArtDialog(QDialog):
    def __init__(self, repo, martial_art=None, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.martial_art = martial_art
        self.is_edit = martial_art is not None
        self.setWindowTitle("Editar Arte Marcial" if self.is_edit else "Nueva Arte Marcial")
        self.setFixedSize(380, 180)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: #111111; color: {TEXT_PRI};")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        root.addWidget(_lbl("NOMBRE DEL ARTE MARCIAL"))
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Ej: Karate, BJJ, Kickboxing...")
        self.inp_name.setStyleSheet(FIELD_STYLE)
        if self.is_edit:
            self.inp_name.setText(martial_art["name"])
        root.addWidget(self.inp_name)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #FF4444; font-size: 11px;")
        root.addWidget(self.lbl_error)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 8px; font-size: 13px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Guardar" if self.is_edit else "Crear")
        btn_save.setFixedHeight(38)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white;
                border: none; border-radius: 8px; font-size: 13px; font-weight: 700; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        btn_save.clicked.connect(self._save)
        self.inp_name.returnPressed.connect(self._save)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        root.addLayout(btn_row)

    def _save(self):
        name = self.inp_name.text().strip()
        if not name:
            self.lbl_error.setText("⚠ El nombre es obligatorio.")
            return
        try:
            if self.is_edit:
                self.repo.update_martial_art(self.martial_art["id"], name)
            else:
                self.repo.create_martial_art(name)
            self.accept()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")


class BeltDialog(QDialog):
    def __init__(self, repo, martial_art_id, belt=None, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.martial_art_id = martial_art_id
        self.belt = belt
        self.is_edit = belt is not None
        self.setWindowTitle("Editar Cinturón" if self.is_edit else "Nuevo Cinturón")
        self.setFixedSize(420, 220)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: #111111; color: {TEXT_PRI};")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        row = QHBoxLayout(); row.setSpacing(12)
        name_col = QVBoxLayout()
        name_col.addWidget(_lbl("NOMBRE"))
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Ej: Blanco, Amarillo...")
        self.inp_name.setStyleSheet(FIELD_STYLE)
        if self.is_edit:
            self.inp_name.setText(belt["name"])
        name_col.addWidget(self.inp_name)

        orden_col = QVBoxLayout()
        orden_col.addWidget(_lbl("ORDEN"))
        self.inp_orden = QLineEdit()
        self.inp_orden.setPlaceholderText("1, 2, 3...")
        self.inp_orden.setStyleSheet(FIELD_STYLE)
        self.inp_orden.setFixedWidth(80)
        if self.is_edit:
            self.inp_orden.setText(str(belt["orden"] or ""))
        orden_col.addWidget(self.inp_orden)

        row.addLayout(name_col, 1)
        row.addLayout(orden_col)
        root.addLayout(row)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #FF4444; font-size: 11px;")
        root.addWidget(self.lbl_error)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 8px; font-size: 13px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Guardar" if self.is_edit else "Crear")
        btn_save.setFixedHeight(38)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white;
                border: none; border-radius: 8px; font-size: 13px; font-weight: 700; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        btn_save.clicked.connect(self._save)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        root.addLayout(btn_row)

    def _save(self):
        name = self.inp_name.text().strip()
        if not name:
            self.lbl_error.setText("⚠ El nombre es obligatorio.")
            return
        try:
            orden = int(self.inp_orden.text().strip()) if self.inp_orden.text().strip() else None
        except ValueError:
            self.lbl_error.setText("⚠ El orden debe ser un número.")
            return
        try:
            if self.is_edit:
                self.repo.update_belt(self.belt["id"], name, orden)
            else:
                self.repo.create_belt(self.martial_art_id, name, orden)
            self.accept()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")


class RequirementDialog(QDialog):
    def __init__(self, repo, belt_id, req=None, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.belt_id = belt_id
        self.req = req
        self.is_edit = req is not None
        self.setWindowTitle("Editar Requisito" if self.is_edit else "Nuevo Requisito")
        self.setFixedSize(440, 220)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: #111111; color: {TEXT_PRI};")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        root.addWidget(_lbl("TIPO DE REQUISITO"))
        self.cmb_type = QComboBox()
        self.cmb_type.setStyleSheet(FIELD_STYLE)
        types = repo.get_requirement_types()
        self.cmb_type.addItem("Sin tipo", None)
        for tid, tname in types:
            self.cmb_type.addItem(tname, tid)
        if self.is_edit and req.get("id_type"):
            for i in range(self.cmb_type.count()):
                if self.cmb_type.itemData(i) == req["id_type"]:
                    self.cmb_type.setCurrentIndex(i); break
        root.addWidget(self.cmb_type)

        root.addWidget(_lbl("DESCRIPCIÓN DEL REQUISITO"))
        self.inp_req = QLineEdit()
        self.inp_req.setPlaceholderText("Ej: 20 clases asistidas, kata Heian Shodan...")
        self.inp_req.setStyleSheet(FIELD_STYLE)
        if self.is_edit:
            self.inp_req.setText(req["requirement"])
        root.addWidget(self.inp_req)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #FF4444; font-size: 11px;")
        root.addWidget(self.lbl_error)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 8px; font-size: 13px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Guardar" if self.is_edit else "Agregar")
        btn_save.setFixedHeight(38)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white;
                border: none; border-radius: 8px; font-size: 13px; font-weight: 700; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        btn_save.clicked.connect(self._save)
        self.inp_req.returnPressed.connect(self._save)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        root.addLayout(btn_row)

    def _save(self):
        req_text = self.inp_req.text().strip()
        if not req_text:
            self.lbl_error.setText("⚠ La descripción es obligatoria.")
            return
        tipo_id = self.cmb_type.currentData()
        try:
            if self.is_edit:
                self.repo.update_requirement(self.req["id"], req_text, tipo_id)
            else:
                self.repo.create_requirement(self.belt_id, req_text, tipo_id)
            self.accept()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")


class BeltsView(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = BeltsRepository()
        self._selected_ma = None
        self._selected_belt = None
        self._build_ui()
        self._load_martial_arts()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {BG_MAIN};")
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("🥋  Artes Marciales & Cinturones")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_PRI};")
        btn_new_ma = QPushButton("＋  Nueva Arte Marcial")
        btn_new_ma.setFixedHeight(38)
        btn_new_ma.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new_ma.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white;
                border: none; border-radius: 7px; font-size: 13px;
                font-weight: 600; padding: 0 18px; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        btn_new_ma.clicked.connect(self._create_martial_art)
        hdr.addWidget(title); hdr.addStretch(); hdr.addWidget(btn_new_ma)
        root.addLayout(hdr)

        sep = QFrame(); sep.setFixedHeight(2)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.4 {RED}, stop:1 transparent); border: none;
        """)
        root.addWidget(sep)

        # Tres columnas
        cols = QHBoxLayout(); cols.setSpacing(14)

        # ── Col 1: Artes Marciales
        ma_card = make_card(RED)
        ma_layout = QVBoxLayout(ma_card)
        ma_layout.setContentsMargins(14, 14, 14, 14)
        ma_layout.setSpacing(8)
        ma_hdr = QHBoxLayout()
        ma_lbl = QLabel("ARTES MARCIALES")
        ma_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; letter-spacing: 1px; color: {TEXT_MUT};")
        ma_hdr.addWidget(ma_lbl); ma_hdr.addStretch()
        ma_layout.addLayout(ma_hdr)

        self.ma_list = QListWidget()
        self.ma_list.setStyleSheet(f"""
            QListWidget {{ background: transparent; border: none; color: {TEXT_PRI}; font-size: 13px; }}
            QListWidget::item {{ padding: 10px 12px; border-radius: 6px; border-bottom: 1px solid {BORDER}; }}
            QListWidget::item:selected {{ background-color: #2A0A0C; color: {TEXT_PRI}; border-left: 3px solid {RED}; }}
            QListWidget::item:hover {{ background-color: #1A1A1A; }}
        """)
        self.ma_list.currentItemChanged.connect(self._on_ma_selected)
        ma_layout.addWidget(self.ma_list, 1)

        ma_btns = QHBoxLayout(); ma_btns.setSpacing(8)
        self.btn_edit_ma = QPushButton("✎ Editar")
        self.btn_del_ma  = QPushButton("🗑 Eliminar")
        for btn in [self.btn_edit_ma, self.btn_del_ma]:
            btn.setFixedHeight(32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit_ma.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 6px; font-size: 12px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; }}
        """)
        self.btn_del_ma.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: #FF4444;
                border: 1px solid #FF4444; border-radius: 6px; font-size: 12px; }}
            QPushButton:hover {{ background: #2A0A0A; }}
        """)
        self.btn_edit_ma.clicked.connect(self._edit_martial_art)
        self.btn_del_ma.clicked.connect(self._delete_martial_art)
        ma_btns.addWidget(self.btn_edit_ma); ma_btns.addWidget(self.btn_del_ma)
        ma_layout.addLayout(ma_btns)

        # ── Col 2: Cinturones
        belt_card = make_card(YELLOW)
        belt_layout = QVBoxLayout(belt_card)
        belt_layout.setContentsMargins(14, 14, 14, 14)
        belt_layout.setSpacing(8)
        belt_hdr = QHBoxLayout()
        self.belt_title = QLabel("CINTURONES")
        self.belt_title.setStyleSheet(f"font-size: 11px; font-weight: 700; letter-spacing: 1px; color: {TEXT_MUT};")
        btn_new_belt = QPushButton("＋")
        btn_new_belt.setFixedSize(26, 26)
        btn_new_belt.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new_belt.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white;
                border: none; border-radius: 6px; font-size: 14px; font-weight: 700; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        btn_new_belt.clicked.connect(self._create_belt)
        belt_hdr.addWidget(self.belt_title); belt_hdr.addStretch(); belt_hdr.addWidget(btn_new_belt)
        belt_layout.addLayout(belt_hdr)

        self.belt_table = QTableWidget()
        self.belt_table.setColumnCount(3)
        self.belt_table.setHorizontalHeaderLabels(["#", "Cinturón", ""])
        self.belt_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.belt_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.belt_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.belt_table.setColumnWidth(0, 40)
        self.belt_table.setColumnWidth(2, 80)
        self.belt_table.verticalHeader().setVisible(False)
        self.belt_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.belt_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.belt_table.setShowGrid(False)
        self.belt_table.setStyleSheet(f"""
            QTableWidget {{ background: transparent; color: {TEXT_PRI}; border: none; font-size: 13px; }}
            QHeaderView::section {{ background: {BG_CARD}; color: {TEXT_SEC}; border: none;
                border-bottom: 1px solid {BORDER}; padding: 6px 8px; font-size: 10px;
                font-weight: 700; letter-spacing: 1px; }}
            QTableWidget::item {{ padding: 6px 8px; border-bottom: 1px solid #1A1A1A; }}
            QTableWidget::item:selected {{ background: #1A0A0C; color: white; }}
        """)
        self.belt_table.currentItemChanged.connect(self._on_belt_selected)
        belt_layout.addWidget(self.belt_table, 1)

        # ── Col 3: Requisitos
        req_card = make_card(BLUE)
        req_layout = QVBoxLayout(req_card)
        req_layout.setContentsMargins(14, 14, 14, 14)
        req_layout.setSpacing(8)
        req_hdr = QHBoxLayout()
        self.req_title = QLabel("REQUISITOS")
        self.req_title.setStyleSheet(f"font-size: 11px; font-weight: 700; letter-spacing: 1px; color: {TEXT_MUT};")
        btn_new_req = QPushButton("＋")
        btn_new_req.setFixedSize(26, 26)
        btn_new_req.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new_req.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white;
                border: none; border-radius: 6px; font-size: 14px; font-weight: 700; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        btn_new_req.clicked.connect(self._create_requirement)
        req_hdr.addWidget(self.req_title); req_hdr.addStretch(); req_hdr.addWidget(btn_new_req)
        req_layout.addLayout(req_hdr)

        self.req_list = QListWidget()
        self.req_list.setStyleSheet(f"""
            QListWidget {{ background: transparent; border: none; color: {TEXT_PRI}; font-size: 12px; }}
            QListWidget::item {{ padding: 8px 10px; border-radius: 6px; border-bottom: 1px solid {BORDER}; }}
            QListWidget::item:selected {{ background: #0A1A2A; }}
            QListWidget::item:hover {{ background: #1A1A1A; }}
        """)
        req_layout.addWidget(self.req_list, 1)

        req_btns = QHBoxLayout(); req_btns.setSpacing(8)
        self.btn_edit_req = QPushButton("✎ Editar")
        self.btn_del_req  = QPushButton("🗑 Eliminar")
        for btn in [self.btn_edit_req, self.btn_del_req]:
            btn.setFixedHeight(32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit_req.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 6px; font-size: 12px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; }}
        """)
        self.btn_del_req.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: #FF4444;
                border: 1px solid #FF4444; border-radius: 6px; font-size: 12px; }}
            QPushButton:hover {{ background: #2A0A0A; }}
        """)
        self.btn_edit_req.clicked.connect(self._edit_requirement)
        self.btn_del_req.clicked.connect(self._delete_requirement)
        req_btns.addWidget(self.btn_edit_req); req_btns.addWidget(self.btn_del_req)
        req_layout.addLayout(req_btns)

        cols.addWidget(ma_card, 1)
        cols.addWidget(belt_card, 2)
        cols.addWidget(req_card, 2)
        root.addLayout(cols, 1)

        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px;")
        root.addWidget(self.lbl_status)

    def _load_martial_arts(self):
        self.ma_list.clear()
        arts = self.repo.get_martial_arts()
        for ma in arts:
            item = QListWidgetItem(f"🥋  {ma['name']}")
            item.setData(Qt.ItemDataRole.UserRole, ma)
            self.ma_list.addItem(item)
        self.lbl_status.setText(f"{len(arts)} arte(s) marcial(es)")

    def _on_ma_selected(self, current, previous):
        if not current:
            return
        self._selected_ma = current.data(Qt.ItemDataRole.UserRole)
        self.belt_title.setText(f"CINTURONES — {self._selected_ma['name'].upper()}")
        self._load_belts()
        self._clear_requirements()

    def _load_belts(self):
        if not self._selected_ma:
            return
        self.belt_table.setRowCount(0)
        belts = self.repo.get_belts(self._selected_ma["id"])
        self.belt_table.setRowCount(len(belts))
        for i, belt in enumerate(belts):
            orden_item = QTableWidgetItem(str(belt["orden"] or "—"))
            orden_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            orden_item.setForeground(QColor(TEXT_MUT))
            self.belt_table.setItem(i, 0, orden_item)

            name_item = QTableWidgetItem(belt["name"])
            name_item.setData(Qt.ItemDataRole.UserRole, belt)
            self.belt_table.setItem(i, 1, name_item)

            btn_w = QWidget()
            btn_w.setStyleSheet("background: transparent;")
            btn_hl = QHBoxLayout(btn_w)
            btn_hl.setContentsMargins(4, 2, 4, 2)
            btn_hl.setSpacing(4)

            btn_e = QPushButton("✎")
            btn_e.setFixedSize(28, 26)
            btn_e.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_e.setStyleSheet(f"""
                QPushButton {{ background: transparent; color: {TEXT_SEC};
                    border: 1px solid {BORDER}; border-radius: 5px; font-size: 11px; }}
                QPushButton:hover {{ color: {TEXT_PRI}; }}
            """)
            btn_e.clicked.connect(lambda _, b=belt: self._edit_belt(b))

            btn_d = QPushButton("✕")
            btn_d.setFixedSize(28, 26)
            btn_d.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_d.setStyleSheet(f"""
                QPushButton {{ background: transparent; color: #FF4444;
                    border: 1px solid #FF4444; border-radius: 5px; font-size: 11px; }}
                QPushButton:hover {{ background: #2A0A0A; }}
            """)
            btn_d.clicked.connect(lambda _, b=belt: self._delete_belt(b))

            btn_hl.addWidget(btn_e); btn_hl.addWidget(btn_d)
            self.belt_table.setCellWidget(i, 2, btn_w)
            self.belt_table.setRowHeight(i, 40)

        self._clear_requirements()

    def _on_belt_selected(self, current, previous):
        if not current:
            return
        row = self.belt_table.currentRow()
        if row < 0:
            return
        item = self.belt_table.item(row, 1)
        if item:
            self._selected_belt = item.data(Qt.ItemDataRole.UserRole)
            self._load_requirements()

    def _load_requirements(self):
        if not self._selected_belt:
            return
        self.req_list.clear()
        self.req_title.setText(f"REQUISITOS — {self._selected_belt['name'].upper()}")
        reqs = self.repo.get_requirements(self._selected_belt["id"])
        for req in reqs:
            tipo = f"[{req['type_name']}]  " if req.get("type_name") else ""
            item = QListWidgetItem(f"{tipo}{req['requirement']}")
            item.setData(Qt.ItemDataRole.UserRole, req)
            if req.get("type_name"):
                item.setForeground(QColor(BLUE))
            self.req_list.addItem(item)

    def _clear_requirements(self):
        self.req_list.clear()
        self.req_title.setText("REQUISITOS")
        self._selected_belt = None

    def _create_martial_art(self):
        dlg = MartialArtDialog(self.repo, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load_martial_arts()

    def _edit_martial_art(self):
        item = self.ma_list.currentItem()
        if not item:
            QMessageBox.information(self, "Aviso", "Selecciona un arte marcial primero.")
            return
        dlg = MartialArtDialog(self.repo, item.data(Qt.ItemDataRole.UserRole), parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load_martial_arts()

    def _delete_martial_art(self):
        item = self.ma_list.currentItem()
        if not item:
            QMessageBox.information(self, "Aviso", "Selecciona un arte marcial primero.")
            return
        ma = item.data(Qt.ItemDataRole.UserRole)
        confirm = QMessageBox(self)
        confirm.setWindowTitle("Confirmar")
        confirm.setText(f"¿Eliminar '{ma['name']}'?")
        confirm.setInformativeText("Se eliminarán todos sus cinturones y requisitos.")
        confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        confirm.setStyleSheet("background: #161616; color: #F0F0F0;")
        if confirm.exec() == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete_martial_art(ma["id"])
                self._load_martial_arts()
                self.belt_table.setRowCount(0)
                self._clear_requirements()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _create_belt(self):
        if not self._selected_ma:
            QMessageBox.information(self, "Aviso", "Selecciona un arte marcial primero.")
            return
        dlg = BeltDialog(self.repo, self._selected_ma["id"], parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load_belts()

    def _edit_belt(self, belt):
        dlg = BeltDialog(self.repo, self._selected_ma["id"], belt=belt, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load_belts()

    def _delete_belt(self, belt):
        confirm = QMessageBox(self)
        confirm.setWindowTitle("Confirmar")
        confirm.setText(f"¿Eliminar cinturón '{belt['name']}'?")
        confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        confirm.setStyleSheet("background: #161616; color: #F0F0F0;")
        if confirm.exec() == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete_belt(belt["id"])
                self._load_belts()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _create_requirement(self):
        if not self._selected_belt:
            QMessageBox.information(self, "Aviso", "Selecciona un cinturón primero.")
            return
        dlg = RequirementDialog(self.repo, self._selected_belt["id"], parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load_requirements()

    def _edit_requirement(self):
        item = self.req_list.currentItem()
        if not item:
            QMessageBox.information(self, "Aviso", "Selecciona un requisito primero.")
            return
        req = item.data(Qt.ItemDataRole.UserRole)
        dlg = RequirementDialog(self.repo, self._selected_belt["id"], req=req, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load_requirements()

    def _delete_requirement(self):
        item = self.req_list.currentItem()
        if not item:
            QMessageBox.information(self, "Aviso", "Selecciona un requisito primero.")
            return
        req = item.data(Qt.ItemDataRole.UserRole)
        confirm = QMessageBox(self)
        confirm.setWindowTitle("Confirmar")
        confirm.setText("¿Eliminar este requisito?")
        confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        confirm.setStyleSheet("background: #161616; color: #F0F0F0;")
        if confirm.exec() == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete_requirement(req["id"])
                self._load_requirements()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))