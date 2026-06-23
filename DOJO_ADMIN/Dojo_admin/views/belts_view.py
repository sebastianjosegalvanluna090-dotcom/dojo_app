from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QLineEdit, QComboBox, QMessageBox, QScrollArea,
    QSizePolicy, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor
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
class BeltPreviewWidget(QWidget):
    def __init__(self, color, grades=0, martial_art=None):
        super().__init__()
        self.color = color or "#FFFFFF"
        self.grades = grades or 0
        self.martial_art = martial_art
        self.setFixedHeight(40)

    def paintEvent(self, event):
        painter = QPainter(self)

        # 🎨 cinturón base
        belt_color = QColor(self.color)
        painter.setBrush(belt_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 10, 200, 20, 10, 10)

        # 🔥 lógica por arte marcial
        if _is_bjj(self.martial_art):
            self.draw_bjj_stripes(painter)
        else:
            self.draw_default_grades(painter)

    def draw_bjj_stripes(self, painter):
        bar_x = 160
        bar_width = 30

        # barra negra o roja
        if self.color.lower() == "#000000":
            bar_color = QColor("red")
        else:
            bar_color = QColor("black")

        painter.setBrush(bar_color)
        painter.drawRect(bar_x, 10, bar_width, 20)

        # stripes
        stripe_width = 4
        spacing = 3

        for i in range(min(self.grades, 4)):
            x = bar_x + 5 + i * (stripe_width + spacing)
            painter.setBrush(QColor("white"))
            painter.drawRect(x, 12, stripe_width, 16)

    def draw_default_grades(self, painter):
        if self.grades <= 0:
            return

        painter.setBrush(QColor("white"))
        painter.drawRect(150, 12, 10, 16)

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


def _belt_border(color: str) -> str:
    """Returns a visible border color for light-colored belts."""
    light = {"#FFFFFF", "#FFD700", "#FF8C00", "#FFFF00", "#FFA500", "#FFFACD"}
    return "#999999" if color.upper() in light else color


def _is_bjj(name: str) -> bool:
    if not name:
        return False
    n = name.strip().lower()
    return n in {"brazilian jiu-jitsu", "bjj", "jiu-jitsu brasileño", "jiu jitsu brasileño"}


# ─── MartialArtDialog ─────────────────────────────────────────────────
class MartialArtDialog(QDialog):
    def __init__(self, repo, martial_art=None, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.martial_art = martial_art
        self.is_edit = martial_art is not None
        self.setWindowTitle("Editar Arte Marcial" if self.is_edit else "Nueva Arte Marcial")
        self.setFixedSize(380, 160)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: #111111; color: {TEXT_PRI};")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        root.addWidget(_lbl("NOMBRE DEL ARTE MARCIAL"))
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Ej: Karate, Judo, BJJ...")
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


# ─── BeltDialog ───────────────────────────────────────────────────────
class BeltDialog(QDialog):
    def __init__(self, repo, martial_art_id, martial_art_name="", belt=None, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.martial_art_id = martial_art_id
        self.martial_art_name = martial_art_name or ""
        self.belt = belt
        self.is_edit = belt is not None
        self.setWindowTitle("Editar Cinturón" if self.is_edit else "Nuevo Cinturón")
        self.setMinimumSize(760, 390)
        self.resize(760, 390)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: #111111; color: {TEXT_PRI};")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        # ── Grid de campos
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)

        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 2)
        grid.setColumnStretch(3, 2)

        grid.addWidget(_lbl("NOMBRE"), 0, 0)
        grid.addWidget(_lbl("ORDEN"), 0, 1)
        grid.addWidget(_lbl("COLOR"), 2, 0)
        grid.addWidget(_lbl("PRE-COLOR (opc.)"), 2, 1)

        # Nombre
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Ej: Blanco, Amarillo...")
        self.inp_name.setStyleSheet(FIELD_STYLE)
        if self.is_edit:
            self.inp_name.setText(belt["name"])
        grid.addWidget(self.inp_name, 1, 0)

        # Orden
        self.inp_orden = QLineEdit()
        self.inp_orden.setPlaceholderText("1, 2, 3...")
        self.inp_orden.setStyleSheet(FIELD_STYLE)
        if self.is_edit:
            self.inp_orden.setText(str(belt.get("orden") or ""))
        grid.addWidget(self.inp_orden, 1, 1)

        # Color
        color_w = QWidget()
        color_w.setStyleSheet("background: transparent;")
        color_hl = QHBoxLayout(color_w)
        color_hl.setContentsMargins(0, 0, 0, 0)
        color_hl.setSpacing(4)

        self.inp_color = QLineEdit()
        self.inp_color.setPlaceholderText("#FFFFFF")
        self.inp_color.setStyleSheet(FIELD_STYLE)
        self.inp_color.setFixedWidth(120)
        if self.is_edit:
            self.inp_color.setText(belt.get("color", "") or "")

        self.color_preview = QFrame()
        self.color_preview.setFixedSize(32, 36)
        self._update_color_preview(belt.get("color", "#888888") if self.is_edit else "#888888")

        btn_pick = QPushButton("🎨")
        btn_pick.setFixedSize(34, 36)
        btn_pick.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pick.setStyleSheet(f"""
            QPushButton {{ background:#1C1C1C; border:1.5px solid {BORDER};
                border-radius:6px; font-size:14px; }}
            QPushButton:hover {{ border-color:{RED}; }}
        """)
        btn_pick.clicked.connect(self._pick_color)
        self.inp_color.textChanged.connect(
            lambda t: self._update_color_preview(t) if len(t) == 7 and t.startswith("#") else None
        )
        color_hl.addWidget(self.inp_color)
        color_hl.addWidget(self.color_preview)
        color_hl.addWidget(btn_pick)
        grid.addWidget(color_w, 3, 0)

        # Pre-color
        pre_w = QWidget()
        pre_w.setStyleSheet("background: transparent;")
        pre_hl = QHBoxLayout(pre_w)
        pre_hl.setContentsMargins(0, 0, 0, 0)
        pre_hl.setSpacing(4)

        self.inp_pre_color = QLineEdit()
        self.inp_pre_color.setPlaceholderText("Sin pre")
        self.inp_pre_color.setStyleSheet(FIELD_STYLE)
        self.inp_pre_color.setFixedWidth(120)
        if self.is_edit:
            self.inp_pre_color.setText(belt.get("pre_color", "") or "")

        self.pre_color_preview = QFrame()
        self.pre_color_preview.setFixedSize(32, 36)
        self._update_pre_color_preview(belt.get("pre_color", "#2A2A2A") if self.is_edit else "#2A2A2A")

        btn_pick_pre = QPushButton("🎨")
        btn_pick_pre.setFixedSize(34, 36)
        btn_pick_pre.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pick_pre.setStyleSheet(f"""
            QPushButton {{ background:#1C1C1C; border:1.5px solid {BORDER};
                border-radius:6px; font-size:14px; }}
            QPushButton:hover {{ border-color:{RED}; }}
        """)
        btn_pick_pre.clicked.connect(self._pick_pre_color)
        self.inp_pre_color.textChanged.connect(
            lambda t: self._update_pre_color_preview(t) if len(t) == 7 and t.startswith("#") else None
        )
        pre_hl.addWidget(self.inp_pre_color)
        pre_hl.addWidget(self.pre_color_preview)
        pre_hl.addWidget(btn_pick_pre)
        grid.addWidget(pre_w, 3, 1)

        root.addLayout(grid)

        root.addWidget(_lbl("GRADOS / STRIPES (solo BJJ, 0-4)"))
        self.inp_grados = QLineEdit()
        self.inp_grados.setPlaceholderText("0")
        self.inp_grados.setStyleSheet(FIELD_STYLE)
        self.update_ui_by_martial_art(self.martial_art_name)

        if self.is_edit:
            self.inp_grados.setText(str(belt.get("grades") or 0))
        root.addWidget(self.inp_grados)

        # Color de grados
        grade_color_w = QWidget()
        grade_color_w.setStyleSheet("background: transparent;")
        grade_color_hl = QHBoxLayout(grade_color_w)
        grade_color_hl.setContentsMargins(0, 0, 0, 0)
        grade_color_hl.setSpacing(4)

        self.inp_grade_color = QLineEdit()
        self.inp_grade_color.setPlaceholderText("#FFFFFF")
        self.inp_grade_color.setStyleSheet(FIELD_STYLE)
        self.inp_grade_color.setFixedWidth(120)

        if self.is_edit:
            self.inp_grade_color.setText(belt.get("grade_color", "#FFFFFF") or "#FFFFFF")
        else:
            self.inp_grade_color.setText("#FFFFFF")

        self.grade_color_preview = QFrame()
        self.grade_color_preview.setFixedSize(32, 36)
        self._update_grade_color_preview(self.inp_grade_color.text())

        btn_pick_grade = QPushButton("🎨")
        btn_pick_grade.setFixedSize(34, 36)
        btn_pick_grade.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pick_grade.setStyleSheet(f"""
            QPushButton {{
                background:#1C1C1C;
                border:1.5px solid {BORDER};
                border-radius:6px;
                font-size:14px;
            }}
            QPushButton:hover {{ border-color:{RED}; }}
        """)
        btn_pick_grade.clicked.connect(self._pick_grade_color)

        self.inp_grade_color.textChanged.connect(
            lambda t: self._update_grade_color_preview(t) if len(t) == 7 and t.startswith("#") else None
        )

        grade_color_hl.addWidget(self.inp_grade_color)
        grade_color_hl.addWidget(self.grade_color_preview)
        grade_color_hl.addWidget(btn_pick_grade)

        grid.addWidget(_lbl("COLOR GRADOS"), 2, 2)
        grid.addWidget(grade_color_w, 3, 2)

        # ── Error + botones
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
            orden = int(self.inp_orden.text().strip()) if self.inp_orden.text().strip() else None
        except ValueError:
            self.lbl_error.setText("⚠ El orden debe ser un número.")
            return
        color = self.inp_color.text().strip() or None
        pre_color = self.inp_pre_color.text().strip() or None
        grade_color = self.inp_grade_color.text().strip() or "#FFFFFF"
        try:
            grados = int(self.inp_grados.text().strip()) if self.inp_grados.text().strip() else 0

            if _is_bjj(self.martial_art_name):
                grados = max(0, min(4, grados))
            else:
                grados = max(0, min(10, grados))

        except ValueError:
            self.lbl_error.setText("⚠ Grados debe ser un número entre 0 y 10.")
            return
        try:
            if self.is_edit:
                self.repo.update_belt(self.belt["id"], name, orden, color, pre_color, grados, grade_color)
            else:
                self.repo.create_belt(self.martial_art_id, name, orden, color, pre_color, grados, grade_color)
            self.accept()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")

    def _update_color_preview(self, color: str):
        try:
            border = _belt_border(color)
            self.color_preview.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 6px;
                    border: 2px solid {border};
                }}
            """)
        except Exception:
            pass

    def _pick_color(self):
        from PyQt6.QtWidgets import QColorDialog
        from PyQt6.QtGui import QColor
        current = self.inp_color.text().strip() or "#FFFFFF"
        color = QColorDialog.getColor(QColor(current), self, "Seleccionar color del cinturón")
        if color.isValid():
            hex_color = color.name().upper()
            self.inp_color.setText(hex_color)
            self._update_color_preview(hex_color)

    def _update_pre_color_preview(self, color: str):
        try:
            self.pre_color_preview.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 6px;
                    border: 2px solid #555;
                }}
            """)
        except Exception:
            pass

    def _pick_pre_color(self):
        from PyQt6.QtWidgets import QColorDialog
        from PyQt6.QtGui import QColor
        current = self.inp_pre_color.text().strip() or "#FFFFFF"
        color = QColorDialog.getColor(QColor(current), self, "Color del pre-grado")
        if color.isValid():
            hex_color = color.name().upper()
            self.inp_pre_color.setText(hex_color)
            self._update_pre_color_preview(hex_color)

    def _update_grade_color_preview(self, color: str):
        try:
            border = _belt_border(color)
            self.grade_color_preview.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border-radius: 6px;
                    border: 2px solid {border};
                }}
            """)
        except Exception:
            pass


    def _pick_grade_color(self):
        from PyQt6.QtWidgets import QColorDialog
        from PyQt6.QtGui import QColor

        current = self.inp_grade_color.text().strip() or "#FFFFFF"
        color = QColorDialog.getColor(QColor(current), self, "Color de las líneas de grado")

        if color.isValid():
            hex_color = color.name().upper()
            self.inp_grade_color.setText(hex_color)
            self._update_grade_color_preview(hex_color)
    
    def update_ui_by_martial_art(self, martial_art_name):
        if _is_bjj(martial_art_name):
            self.inp_grados.setPlaceholderText("Stripes (0-4)")
        else:
            self.inp_grados.setPlaceholderText("Grados / Dan")


# ─── RequirementDialog ────────────────────────────────────────────────
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
                    self.cmb_type.setCurrentIndex(i)
                    break
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


# ─── BeltsView ────────────────────────────────────────────────────────
class BeltsView(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = BeltsRepository()

        self._selected_ma = None
        self._selected_belt = None
        self.current_martial_art_name = ""

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
 
        # ── BOTÓN NUEVO: Ascenso de Cinturón ──
        btn_promote = QPushButton("🏅  Ascender Cinturón")
        btn_promote.setFixedHeight(38)
        btn_promote.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_promote.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {YELLOW};
                border: 1px solid {YELLOW}; border-radius: 7px;
                font-size: 13px; font-weight: 600; padding: 0 18px;
            }}
            QPushButton:hover {{ background: #1A1600; }}
        """)
        btn_promote.clicked.connect(self._open_promote_dialog)
 
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
 
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(btn_promote)   # ← nuevo
        hdr.addWidget(btn_new_ma)
        root.addLayout(hdr)

        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.4 {RED}, stop:1 transparent); border: none;
        """)
        root.addWidget(sep)

        # Tres columnas
        cols = QHBoxLayout()
        cols.setSpacing(14)

        # ── Col 1: Artes Marciales
        ma_card = make_card(RED)
        ma_layout = QVBoxLayout(ma_card)
        ma_layout.setContentsMargins(14, 14, 14, 14)
        ma_layout.setSpacing(8)
        ma_hdr = QHBoxLayout()
        ma_lbl = QLabel("ARTES MARCIALES")
        ma_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; letter-spacing: 1px; color: {TEXT_MUT};")
        ma_hdr.addWidget(ma_lbl)
        ma_hdr.addStretch()
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

        ma_btns = QHBoxLayout()
        ma_btns.setSpacing(8)
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
        ma_btns.addWidget(self.btn_edit_ma)
        ma_btns.addWidget(self.btn_del_ma)
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
        belt_hdr.addWidget(self.belt_title)
        belt_hdr.addStretch()
        belt_hdr.addWidget(btn_new_belt)
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
        req_hdr.addWidget(self.req_title)
        req_hdr.addStretch()
        req_hdr.addWidget(btn_new_req)
        req_layout.addLayout(req_hdr)

        self.req_list = QListWidget()
        self.req_list.setStyleSheet(f"""
            QListWidget {{ background: transparent; border: none; color: {TEXT_PRI}; font-size: 12px; }}
            QListWidget::item {{ padding: 8px 10px; border-radius: 6px; border-bottom: 1px solid {BORDER}; }}
            QListWidget::item:selected {{ background: #0A1A2A; }}
            QListWidget::item:hover {{ background: #1A1A1A; }}
        """)
        req_layout.addWidget(self.req_list, 1)

        req_btns = QHBoxLayout()
        req_btns.setSpacing(8)
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
        req_btns.addWidget(self.btn_edit_req)
        req_btns.addWidget(self.btn_del_req)
        req_layout.addLayout(req_btns)

        cols.addWidget(ma_card, 1)
        cols.addWidget(belt_card, 2)
        cols.addWidget(req_card, 2)
        root.addLayout(cols, 1)

        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px;")
        root.addWidget(self.lbl_status)
    
    def _open_promote_dialog(self):
        dlg = PromoteStudentDialog(self.repo, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            # Pequeño feedback visual
            self.lbl_status.setText("✓  Cinturón actualizado correctamente")
            QTimer = __import__("PyQt6.QtCore", fromlist=["QTimer"]).QTimer
            QTimer.singleShot(3000, self._clear_status_safe)

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

        martial_art_name = self._selected_ma["name"]
        self.current_martial_art_name = martial_art_name
        self.selected_martial_art_name = martial_art_name

        self.belt_title.setText(f"CINTURONES — {martial_art_name.upper()}")

        self._clear_requirements()
        self._load_belts()


    def _load_belts(self):
        if not self._selected_ma:
            return
        self.belt_table.setRowCount(0)
        belts = self.repo.get_belts(self._selected_ma["id"])
        self.belt_table.setRowCount(len(belts))

        for row, belt in enumerate(belts):
            orden_item = QTableWidgetItem(str(belt["orden"] or "—"))
            orden_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            orden_item.setForeground(QColor(TEXT_MUT))
            self.belt_table.setItem(row, 0, orden_item)


            # ── Col 1: Nombre + barra de color
            cell_w = QWidget()
            cell_w.setStyleSheet("background: transparent;")
            cell_hl = QHBoxLayout(cell_w)
            cell_hl.setContentsMargins(8, 6, 8, 6)
            cell_hl.setSpacing(12)

            lbl_name = QLabel(belt["name"])
            lbl_name.setStyleSheet(f"color: {TEXT_PRI}; font-size: 13px; font-weight: 500;")
            lbl_name.setFixedWidth(130)

            belt_color = belt.get("color") or "#888888"
            pre_color  = belt.get("pre_color")
            border_c   = _belt_border(belt_color)
            is_bjj     = _is_bjj(self._selected_ma.get("name"))

            # Belt bar — outer QFrame acts as the border+radius container
            bar_container = QFrame()
            bar_container.setFixedHeight(20)
            bar_container.setMinimumWidth(130)
            bar_container.setStyleSheet(f"""
                QFrame {{
                    background-color: {belt_color};
                    border-radius: 6px;
                    border: 1.5px solid {border_c};
                }}
            """)

            if is_bjj:
                grados = belt.get("grades") or 0
                grados = max(0, min(4, grados))
                stripe_box_color = "red" if belt_color.upper() == "#000000" else "black"

                inner = QHBoxLayout(bar_container)
                inner.setContentsMargins(0, 0, 4, 0)
                inner.setSpacing(0)

                inner.addStretch()

                stripe_box = QFrame()
                stripe_box.setFixedSize(45, 18)

                stripe_box.setStyleSheet(f"""
                    QFrame {{
                        background-color: {stripe_box_color};
                        border-top-left-radius: 0px;
                        border-bottom-left-radius: 0px;
                        border-top-right-radius: 5px;
                        border-bottom-right-radius: 5px;
                        border: none;
                    }}
                """)

                stripe_hl = QHBoxLayout(stripe_box)
                stripe_hl.setContentsMargins(3, 0, 3, 0)
                stripe_hl.setSpacing(4)
                stripe_hl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                max_stripes = 4

                for stripe_idx in range(max_stripes):
                    s = QFrame()
                    s.setFixedSize(4, 14)

                    if stripe_idx >= max_stripes - grados:
                        s.setStyleSheet("""
                            QFrame {
                                background-color: white;
                                border-radius: 1px;
                                border: none;
                            }
                        """)
                    else:
                        s.setStyleSheet("""
                            QFrame {
                                background: transparent;
                                border: none;
                            }
                        """)

                    stripe_hl.addWidget(s)

                inner.addWidget(stripe_box, 0, Qt.AlignmentFlag.AlignVCenter)

            elif pre_color:
                inner = QHBoxLayout(bar_container)
                inner.setContentsMargins(0, 0, 0, 0)
                inner.setSpacing(0)

                left = QFrame()
                left.setStyleSheet("QFrame { background: transparent; border: none; }")

                stripe = QFrame()
                stripe.setFixedWidth(10)
                stripe.setStyleSheet(f"QFrame {{ background-color: {pre_color}; border: none; border-radius: 0px; }}")

                right = QFrame()
                right.setStyleSheet("QFrame { background: transparent; border: none; }")

                inner.addWidget(left, 3)
                inner.addWidget(stripe)
                inner.addWidget(right, 1)
            
            else:
                grados = belt.get("grades") or 0
                grados = max(0, min(10, grados))

                grade_color = belt.get("grade_color") or "#FFFFFF"

                inner = QHBoxLayout(bar_container)
                inner.setContentsMargins(0, 0, 6, 0)
                inner.setSpacing(2)

                inner.addStretch()

                grade_box = QFrame()
                grade_box.setFixedHeight(18)
                grade_box.setStyleSheet("background: transparent; border:none;")

                grade_hl = QHBoxLayout(grade_box)
                grade_hl.setContentsMargins(0, 0, 0, 0)
                grade_hl.setSpacing(3)
                grade_hl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                # máximo 10 líneas
                for grade_idx in range(10):
                    s = QFrame()
                    s.setFixedSize(3, 14)

                    # 🔥 GRADOS DE DERECHA A IZQUIERDA
                    if grade_idx >= 10 - grados:
                        s.setStyleSheet(f"""
                            QFrame {{
                                background-color: {grade_color};
                                border-radius:1px;
                            }}
                        """)
                    else:
                        s.setStyleSheet("background: transparent; border:none;")

                    grade_hl.addWidget(s)

                inner.addWidget(grade_box, 0, Qt.AlignmentFlag.AlignVCenter)

            cell_hl.addWidget(lbl_name)
            cell_hl.addWidget(bar_container, 1)

            name_item = QTableWidgetItem("")
            name_item.setData(Qt.ItemDataRole.UserRole, belt)
            self.belt_table.setItem(row, 1, name_item)
            self.belt_table.setCellWidget(row, 1, cell_w)

            # ── Col 2: Botones
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

            btn_hl.addWidget(btn_e)
            btn_hl.addWidget(btn_d)
            self.belt_table.setCellWidget(row, 2, btn_w)
            self.belt_table.setRowHeight(row, 48)

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

    def _clear_status_safe(self):
        try:
            if hasattr(self, "lbl_status") and self.lbl_status is not None:
                self.lbl_status.setText("")
        except RuntimeError:
            pass

    # ── Martial Art CRUD
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

    # ── Belt CRUD
    def _create_belt(self):
        if not self._selected_ma:
            QMessageBox.information(self, "Aviso", "Selecciona un arte marcial primero.")
            return
        dlg = BeltDialog(
            self.repo,
            self._selected_ma["id"],
            martial_art_name=self._selected_ma["name"],
            parent=self
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load_belts()

    def _edit_belt(self, belt):
        dlg = BeltDialog(
            self.repo,
            self._selected_ma["id"],
            martial_art_name=self._selected_ma["name"],
            belt=belt,
            parent=self
        )
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

    # ── Requirement CRUD
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

class BeltBar(QWidget):
    def __init__(self, color, grades=0, martial_art_name=""):
        super().__init__()
        self.color = color or "#FFFFFF"
        self.grades = grades or 0
        self.martial_art = martial_art_name
        self.setFixedSize(220, 40)

    def paintEvent(self, event):
        painter = QPainter(self)

        # 🎨 cinturón base
        painter.setBrush(QColor(self.color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 10, 200, 20, 10, 10)

        # 🔥 lógica clave
        if _is_bjj(self.martial_art):
            self.draw_bjj(painter)
        else:
            self.draw_default(painter)

    def draw_bjj(self, painter):
        bar_x = 160

        # barra negra o roja
        if self.color.lower() == "#000000":
            painter.setBrush(QColor("red"))
        else:
            painter.setBrush(QColor("black"))

        painter.drawRect(bar_x, 10, 30, 20)

        # stripes
        for i in range(min(self.grades, 4)):
            x = bar_x + 25 - i * 6
            painter.setBrush(QColor("white"))
            painter.drawRect(x, 12, 4, 16)

    def draw_default(self, painter):
        if self.grades <= 0:
            return

        painter.setBrush(QColor("white"))
        painter.drawRect(150, 12, 10, 16)
 
 
class PromoteStudentDialog(QDialog):
    """
    Diálogo de ascenso de cinturón.
    Flujo: seleccionar arte marcial → instructor (can_promote) →
           estudiante → cinturón destino → confirmar.
    """
 
    def __init__(self, repo, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.setWindowTitle("Ascenso de Cinturón")
        self.setFixedSize(560, 620)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: #0D0D0D; color: {TEXT_PRI};")
 
        # Estado interno
        self._sel_ma          = None
        self._sel_instructor  = None
        self._sel_student     = None
        self._sel_belt        = None
 
        self._build_ui()
        self._load_martial_arts()
 
    # ── UI ────────────────────────────────────────────────────────────
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
 
        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
 
        container = QWidget()
        container.setStyleSheet("background: #0D0D0D;")
        root = QVBoxLayout(container)
        root.setContentsMargins(28, 24, 28, 20)
        root.setSpacing(18)
 
        # ── Header ────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        icon = QLabel("🥋"); icon.setStyleSheet("font-size: 22px;")
        title = QLabel("Ascenso de Cinturón")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {TEXT_PRI};")
        hdr.addWidget(icon); hdr.addSpacing(8); hdr.addWidget(title); hdr.addStretch()
        root.addLayout(hdr)
 
        sep = QFrame(); sep.setFixedHeight(2)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.4 {RED}, stop:1 transparent); border: none;
        """)
        root.addWidget(sep)
 
        # ── Paso 1: Arte Marcial ───────────────────────────────────────
        root.addWidget(self._step_label("1", "ARTE MARCIAL"))
        self.cmb_ma = QComboBox()
        self.cmb_ma.setStyleSheet(FIELD_STYLE)
        self.cmb_ma.currentIndexChanged.connect(self._on_ma_changed)
        root.addWidget(self.cmb_ma)
 
        # ── Paso 2: Instructor ─────────────────────────────────────────
        root.addWidget(self._step_label("2", "INSTRUCTOR (CON PERMISO DE ASCENSO)"))
        self.cmb_instructor = QComboBox()
        self.cmb_instructor.setStyleSheet(FIELD_STYLE)
        self.cmb_instructor.setEnabled(False)
        self.cmb_instructor.currentIndexChanged.connect(self._on_instructor_changed)
        root.addWidget(self.cmb_instructor)
 
        self.lbl_no_instructors = QLabel("⚠  Ningún instructor tiene permiso de ascenso en este arte.")
        self.lbl_no_instructors.setStyleSheet(f"color: {YELLOW}; font-size: 11px;")
        self.lbl_no_instructors.setVisible(False)
        root.addWidget(self.lbl_no_instructors)
 
        # ── Paso 3: Estudiante ─────────────────────────────────────────
        root.addWidget(self._step_label("3", "ESTUDIANTE"))
 
        # Buscador de estudiante
        self.search_student = QLineEdit()
        self.search_student.setPlaceholderText("🔍  Filtrar por nombre...")
        self.search_student.setStyleSheet(FIELD_STYLE)
        self.search_student.setEnabled(False)
        self.search_student.textChanged.connect(self._filter_students)
        root.addWidget(self.search_student)
 
        # Lista custom de estudiantes
        self.student_scroll = QScrollArea()
        self.student_scroll.setWidgetResizable(True)
        self.student_scroll.setFixedHeight(140)
        self.student_scroll.setEnabled(False)
        self.student_scroll.setStyleSheet(f"""
            QScrollArea {{
                background: #1A1A1A; border: 1.5px solid {BORDER}; border-radius: 8px;
            }}
            QScrollBar:vertical {{
                background: #1A1A1A; width: 6px; border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: #333; border-radius: 3px; min-height: 20px;
            }}
        """)
        self.student_container = QWidget()
        self.student_container.setStyleSheet("background: transparent;")
        self.student_vbox = QVBoxLayout(self.student_container)
        self.student_vbox.setContentsMargins(0, 4, 0, 4)
        self.student_vbox.setSpacing(1)
        self.student_scroll.setWidget(self.student_container)
        root.addWidget(self.student_scroll)
 
        # ── Paso 4: Cinturón destino ───────────────────────────────────
        root.addWidget(self._step_label("4", "CINTURÓN DESTINO"))
        self.cmb_belt = QComboBox()
        self.cmb_belt.setStyleSheet(FIELD_STYLE)
        self.cmb_belt.setEnabled(False)
        self.cmb_belt.currentIndexChanged.connect(self._on_belt_changed)
        root.addWidget(self.cmb_belt)
 
        # Preview del cinturón seleccionado
        self.belt_preview_row = QHBoxLayout()
        self.belt_preview_bar = QFrame()
        self.belt_preview_bar.setFixedHeight(20)
        self.belt_preview_bar.setMinimumWidth(80)
        self.belt_preview_bar.setStyleSheet(
            "background: #333; border-radius: 5px; border: 1.5px solid #555;"
        )
        self.lbl_belt_preview = QLabel("")
        self.lbl_belt_preview.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")
        self.belt_preview_row.addWidget(self.belt_preview_bar)
        self.belt_preview_row.addWidget(self.lbl_belt_preview)
        self.belt_preview_row.addStretch()
        root.addLayout(self.belt_preview_row)
 
        # ── Error ──────────────────────────────────────────────────────
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #FF4444; font-size: 12px;")
        self.lbl_error.setWordWrap(True)
        root.addWidget(self.lbl_error)
 
        root.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)
 
        # ── Botones fijos ──────────────────────────────────────────────
        btn_area = QWidget()
        btn_area.setStyleSheet(f"background: #0D0D0D; border-top: 1px solid {BORDER};")
        btn_hl = QHBoxLayout(btn_area)
        btn_hl.setContentsMargins(28, 14, 28, 14); btn_hl.setSpacing(10)
 
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(42)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 8px; font-size: 13px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; }}
        """)
        btn_cancel.clicked.connect(self.reject)
 
        self.btn_promote = QPushButton("🥋  Confirmar Ascenso")
        self.btn_promote.setFixedHeight(42)
        self.btn_promote.setEnabled(False)
        self.btn_promote.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_promote.setStyleSheet(f"""
            QPushButton {{
                background: {RED}; color: white; border: none;
                border-radius: 8px; font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background: {RED_H}; }}
            QPushButton:disabled {{ background: #3A1A1A; color: #666; }}
        """)
        self.btn_promote.clicked.connect(self._do_promote)
 
        btn_hl.addWidget(btn_cancel); btn_hl.addWidget(self.btn_promote)
        outer.addWidget(btn_area)
 
    # ── Helpers UI ────────────────────────────────────────────────────
    def _step_label(self, number: str, text: str) -> QWidget:
        w = QWidget(); w.setStyleSheet("background: transparent;")
        hl = QHBoxLayout(w); hl.setContentsMargins(0, 0, 0, 0); hl.setSpacing(8)
        badge = QLabel(number)
        badge.setFixedSize(20, 20)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"""
            background: {RED}; color: white; border-radius: 10px;
            font-size: 10px; font-weight: 700;
        """)
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {TEXT_SEC}; font-size: 10px; font-weight: 700; letter-spacing: 0.8px;"
        )
        hl.addWidget(badge); hl.addWidget(lbl); hl.addStretch()
        return w
 
    def _make_student_row(self, s: dict) -> QWidget:
        row = QWidget(); row.setFixedHeight(44)
        row.setCursor(Qt.CursorShape.PointingHandCursor)
        self._style_student_row(row, False)
 
        hl = QHBoxLayout(row)
        hl.setContentsMargins(12, 0, 12, 0); hl.setSpacing(10)
 
        # Nombre
        lbl_name = QLabel(s["nombre"])
        lbl_name.setStyleSheet(f"color: {TEXT_PRI}; font-size: 13px; background: transparent; border: none;")
 
        # Cinturón actual — barra de color pequeña + nombre
        belt_w = QWidget(); belt_w.setStyleSheet("background: transparent; border: none;")
        belt_hl = QHBoxLayout(belt_w)
        belt_hl.setContentsMargins(0, 0, 0, 0); belt_hl.setSpacing(6)
 
        bar = QFrame()
        bar.setFixedSize(28, 14)
        color = s["belt_color"]
        border = "#999" if color.upper() in {
            "#FFFFFF","#FFD700","#FF8C00","#FFFF00","#FFA500","#FFFACD"
        } else color
        bar.setStyleSheet(f"""
            QFrame {{ background: {color}; border-radius: 3px; border: 1.5px solid {border}; }}
        """)
 
        lbl_belt = QLabel(s["belt_name"])
        lbl_belt.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; background: transparent; border: none;")
 
        belt_hl.addWidget(bar); belt_hl.addWidget(lbl_belt)
 
        hl.addWidget(lbl_name, 1); hl.addWidget(belt_w)
        row.mousePressEvent = lambda e, r=row, st=s: self._select_student(r, st)
        return row
 
    def _style_student_row(self, row: QWidget, selected: bool):
        if selected:
            row.setStyleSheet(f"""
                QWidget {{
                    background-color: #2A0A0C; border-radius: 6px;
                    border-left: 3px solid {RED};
                }}
            """)
        else:
            row.setStyleSheet("""
                QWidget { background: transparent; border-radius: 6px; border: none; }
                QWidget:hover { background: #222; }
            """)
 
    # ── Carga de datos ────────────────────────────────────────────────
    def _load_martial_arts(self):
        self.cmb_ma.blockSignals(True)
        self.cmb_ma.clear()
        self.cmb_ma.addItem("Seleccionar arte marcial...", None)
        for ma in self.repo.get_martial_arts():
            self.cmb_ma.addItem(f"🥋  {ma['name']}", ma)
        self.cmb_ma.blockSignals(False)
 
    def _on_ma_changed(self, idx):
        self._sel_ma = self.cmb_ma.itemData(idx)
        self._sel_instructor = None
        self._sel_student    = None
        self._sel_belt       = None
        self._reset_from_step(2)
 
        if not self._sel_ma:
            return
 
        instructors = self.repo.get_instructors_that_can_promote(self._sel_ma["id"])
        self.cmb_instructor.blockSignals(True)
        self.cmb_instructor.clear()
        self.cmb_instructor.addItem("Seleccionar instructor...", None)
 
        if instructors:
            for ins in instructors:
                self.cmb_instructor.addItem(f"👤  {ins['nombre']}", ins)
            self.cmb_instructor.setEnabled(True)
            self.lbl_no_instructors.setVisible(False)
        else:
            self.cmb_instructor.setEnabled(False)
            self.lbl_no_instructors.setVisible(True)
 
        self.cmb_instructor.blockSignals(False)
 
    def _on_instructor_changed(self, idx):
        self._sel_instructor = self.cmb_instructor.itemData(idx)
        self._sel_student    = None
        self._sel_belt       = None
        self._reset_from_step(3)
 
        if not self._sel_instructor or not self._sel_ma:
            return
 
        self._all_students = self.repo.get_students_by_martial_art(self._sel_ma["id"])
        self.search_student.setEnabled(True)
        self.student_scroll.setEnabled(True)
        self.search_student.clear()
        self._populate_students(self._all_students)
 
    def _filter_students(self, text):
        text = text.lower()
        filtered = [s for s in self._all_students if text in s["nombre"].lower()]
        self._populate_students(filtered)
 
    def _populate_students(self, students):
        while self.student_vbox.count():
            item = self.student_vbox.takeAt(0)
            if item.widget(): item.widget().deleteLater()
 
        if not students:
            lbl = QLabel("Sin estudiantes en este arte marcial")
            lbl.setStyleSheet(
                f"color: {TEXT_MUT}; font-size: 12px; font-style: italic; padding: 10px 14px;"
            )
            self.student_vbox.addWidget(lbl)
        else:
            for s in students:
                row = self._make_student_row(s)
                self.student_vbox.addWidget(row)
 
        self.student_vbox.addStretch()
 
    def _select_student(self, clicked_row: QWidget, s: dict):
        for i in range(self.student_vbox.count()):
            item = self.student_vbox.itemAt(i)
            if item and item.widget():
                self._style_student_row(item.widget(), False)
        self._style_student_row(clicked_row, True)
        self._sel_student = s
        self._sel_belt    = None
        self._load_belts_for_student(s)
 
    def _load_belts_for_student(self, s: dict):
        self.cmb_belt.blockSignals(True)
        self.cmb_belt.clear()
        self.cmb_belt.addItem("Seleccionar cinturón...", None)
 
        belts = self.repo.get_next_belts(self._sel_ma["id"], s["belt_orden"])
        if belts:
            for b in belts:
                self.cmb_belt.addItem(f"  {b['name']}", b)
            self.cmb_belt.setEnabled(True)
        else:
            self.cmb_belt.addItem("No hay cinturones superiores", None)
            self.cmb_belt.setEnabled(False)
 
        self.cmb_belt.blockSignals(False)
        # Reset preview
        self.belt_preview_bar.setStyleSheet(
            "background: #333; border-radius: 5px; border: 1.5px solid #555;"
        )
        self.lbl_belt_preview.setText("")
        self._check_ready()
 
    def _on_belt_changed(self, idx):
        self._sel_belt = self.cmb_belt.itemData(idx)
        if self._sel_belt:
            color = self._sel_belt["color"]
            border = "#999" if color.upper() in {
                "#FFFFFF","#FFD700","#FF8C00","#FFFF00","#FFA500","#FFFACD"
            } else color
            self.belt_preview_bar.setStyleSheet(f"""
                QFrame {{
                    background: {color}; border-radius: 5px; border: 1.5px solid {border};
                }}
            """)
            self.lbl_belt_preview.setText(f"Cinturón seleccionado: {self._sel_belt['name']}")
        else:
            self.belt_preview_bar.setStyleSheet(
                "background: #333; border-radius: 5px; border: 1.5px solid #555;"
            )
            self.lbl_belt_preview.setText("")
        self._check_ready()
 
    def _check_ready(self):
        ok = all([self._sel_ma, self._sel_instructor, self._sel_student, self._sel_belt])
        self.btn_promote.setEnabled(ok)
 
    def _reset_from_step(self, step: int):
        """Resetea todos los controles a partir del paso indicado."""
        if step <= 2:
            self.cmb_instructor.clear()
            self.cmb_instructor.setEnabled(False)
            self.lbl_no_instructors.setVisible(False)
        if step <= 3:
            self.search_student.clear()
            self.search_student.setEnabled(False)
            self.student_scroll.setEnabled(False)
            while self.student_vbox.count():
                item = self.student_vbox.takeAt(0)
                if item.widget(): item.widget().deleteLater()
        if step <= 4:
            self.cmb_belt.clear()
            self.cmb_belt.setEnabled(False)
            self.belt_preview_bar.setStyleSheet(
                "background: #333; border-radius: 5px; border: 1.5px solid #555;"
            )
            self.lbl_belt_preview.setText("")
        self.lbl_error.setText("")
        self.btn_promote.setEnabled(False)
 
    # ── Acción ────────────────────────────────────────────────────────
    def _do_promote(self):
        self.lbl_error.setText("")
        if not all([self._sel_ma, self._sel_instructor, self._sel_student, self._sel_belt]):
            self.lbl_error.setText("⚠ Completa todos los pasos antes de confirmar.")
            return
 
        self.btn_promote.setEnabled(False)
        self.btn_promote.setText("Procesando...")
 
        try:
            self.repo.promote_student(
                student_id    = self._sel_student["id"],
                belt_id       = self._sel_belt["id"],
                instructor_id = self._sel_instructor["id"],
                martial_art_id= self._sel_ma["id"],
            )
            self.accept()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")
            self.btn_promote.setEnabled(True)
            self.btn_promote.setText("🥋  Confirmar Ascenso")
 