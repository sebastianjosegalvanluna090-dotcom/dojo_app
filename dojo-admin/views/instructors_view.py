"""
views/instructors_view.py
Vista de gestión de instructores — Versión Premium con Rejilla de Tarjetas Holográficas.
Embebido en SettingsView (página Instructores).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QMessageBox, QDialog,
    QListWidget, QListWidgetItem, QCheckBox, QScrollArea, QGridLayout,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QSizePolicy,
    QComboBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPoint, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QPainter

from repositories.instructors_repository import InstructorsRepository

# ─── PALETA PREMIUM SENSHE FIGHT (Cyberpunk Dark Mode) ────────────────
BG_MAIN  = "#050505"
BG_CARD  = "#0C0C0C"
BG_TABLE = "#090909"
BG_INPUT = "#121212"
BORDER   = "#1F1F1F"
RED      = "#E11D48"
RED_H    = "#F43F5E"
RED_DARK = "#3B0712"
TEXT_PRI = "#FAFAFA"
TEXT_SEC = "#A3A3A3"
TEXT_MUT = "#525252"
GREEN    = "#10B981"
BLUE     = "#3B82F6"
ORANGE   = "#F97316"
CARD_MIN_W = 430
CARD_MAX_W = 510
CARD_H = 280
GRID_GAP = 24

FIELD_STYLE = f"""
    QLineEdit {{
        background-color: {BG_INPUT}; color: {TEXT_PRI};
        border: 1.5px solid {BORDER}; border-radius: 8px;
        padding: 0 14px; font-size: 13px;
        min-height: 40px; max-height: 40px;
        font-family: 'Inter';
    }}
    QLineEdit:focus {{ border-color: {RED}; background-color: #1A0A0C; }}
"""


def _lbl(text):
    l = QLabel(text)
    l.setStyleSheet(
        f"color: {TEXT_SEC}; font-size: 10px; font-weight: 800; letter-spacing: 1px; font-family: 'Inter';"
    )
    return l


def _make_card(accent=None):
    card = QFrame()
    bl = f"border-left: 4px solid {accent};" if accent else ""
    card.setStyleSheet(f"""
        QFrame {{
            background-color: {BG_CARD}; border: 1px solid {BORDER};
            {bl} border-radius: 12px;
        }}
        QFrame * {{ border: none; background: transparent; }}
    """)
    shadow = QGraphicsDropShadowEffect(card)
    shadow.setBlurRadius(12)
    shadow.setColor(QColor(0, 0, 0, 150))
    shadow.setOffset(0, 3)
    card.setGraphicsEffect(shadow)
    return card


def _resolve_instructor_rank(is_sensei: bool, martial_arts: list):
    if is_sensei:
        return "Sensei", GREEN

    can_promote = any(bool(ma.get("can_promote")) for ma in (martial_arts or []))

    if can_promote:
        return "Instructor líder", ORANGE

    return "Instructor auxiliar", TEXT_SEC


class InstructorBeltMiniBar(QWidget):
    def __init__(self, belt_name, color, pre_color=None, grades=0, grade_color="#FFFFFF", martial_art_name="", parent=None):
        super().__init__(parent)
        self.belt_name = belt_name or "Sin cinturón"
        self.color = color or "#FFFFFF"
        self.pre_color = pre_color
        self.grades = int(grades or 0)
        self.grade_color = grade_color or "#FFFFFF"
        self.martial_art_name = martial_art_name or ""
        self.setFixedHeight(24)
        self.setFixedWidth(190)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width(); h = self.height()

        painter.setPen(QColor(BORDER))
        painter.setBrush(QColor("#090909"))
        painter.drawRoundedRect(0, 0, w - 1, h - 1, 7, 7)

        bar_x, bar_y, bar_w, bar_h = 8, 7, 52, 10
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.color))
        painter.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 4, 4)

        if self.pre_color:
            painter.setBrush(QColor(self.pre_color))
            painter.drawRoundedRect(bar_x + bar_w // 2, bar_y, bar_w // 2, bar_h, 4, 4)

        border_color = "#999999" if str(self.color).upper() in {"#FFFFFF", "#FFFF00", "#FFD700", "#FFA500", "#FFFACD"} else "#222222"
        painter.setPen(QColor(border_color))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 4, 4)

        if self.grades > 0:
            stripe_w, gap = 3, 3
            start_x = bar_x + bar_w - ((stripe_w + gap) * self.grades) - 4
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(self.grade_color))
            for i in range(self.grades):
                x = start_x + i * (stripe_w + gap)
                painter.drawRect(x, bar_y + 1, stripe_w, bar_h - 2)

        painter.setPen(QColor(TEXT_SEC))
        font = painter.font(); font.setPointSize(7); font.setBold(True)
        painter.setFont(font)
        text = self.belt_name[:15] + "…"  if len(self.belt_name) > 16 else self.belt_name
        painter.drawText(bar_x + bar_w + 8, 0, w - bar_w - 18, h,
                         Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)


# ─── WORKER ASÍNCRONO DE CARGA ────────────────────────────────────────
class LoadWorker(QThread):
    done = pyqtSignal(list)

    def __init__(self, repo, search="", belt_id=None):
        super().__init__()
        self.repo    = repo
        self.search  = search
        self.belt_id = belt_id

    def run(self):
        try:
            self.done.emit(self.repo.get_all(self.search, self.belt_id))
        except Exception as e:
            print(f"[Instructors error] {e}")
            self.done.emit([])


# ─── TARJETA DE INSTRUCTOR HOLOGRÁFICA ────────────────────────────────
class InstructorCard(QFrame):
    clicked = pyqtSignal(int)
    double_clicked = pyqtSignal(int)

    def __init__(self, data, class_count=0, martial_arts=None, instructor_belts=None, parent=None):
        super().__init__(parent)
        self.data = data
        self.instructor_id = data[0]
        self.selected = False
        self.hovered = False
        self.instructor_belts = instructor_belts or []

        self.setObjectName("InstructorCard")
        self.setFixedSize(CARD_MAX_W, CARD_H)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style(False)

        # Sombra de la card
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(16)
        self.shadow.setColor(QColor(0, 0, 0, 180))
        self.shadow.setOffset(0, 5)
        self.setGraphicsEffect(self.shadow)

        self._anim_shadow = QPropertyAnimation(self.shadow, b"blurRadius", self)
        self._anim_shadow.setDuration(160)
        self._anim_shadow.setEasingCurve(QEasingCurve.Type.OutCubic)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(16)

        # ── Cabecera fija: avatar + nombre/email ───────────────────────
        nombre = data[1] or "Sin nombre"
        initials = "".join(p[0].upper() for p in nombre.split()[:2] if p)

        header_box = QFrame()
        header_box.setObjectName("InstructorCardHeader")
        header_box.setFixedHeight(82)
        header_box.setStyleSheet("""
            QFrame#InstructorCardHeader {
                background: transparent;
                border: none;
            }
        """)

        header = QHBoxLayout(header_box)
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(14)
        header.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Avatar directo, sin wrapper para evitar desplazamientos raros
        self.avatar = QLabel(initials or "?")
        self.avatar.setObjectName("InstructorAvatar")
        self.avatar.setFixedSize(58, 58)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar.setStyleSheet(f"""
            QLabel#InstructorAvatar {{
                background-color: #121212;
                color: {RED};
                font-size: 15px;
                font-weight: 900;
                border-radius: 29px;
                border: 2px solid {BORDER};
            }}
        """)
        self._apply_avatar_style(False)

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(4)

        self.lbl_name = QLabel(nombre)
        self.lbl_name.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_PRI};
                font-size: 14px;
                font-weight: 900;
                font-family: 'Inter';
                background: transparent;
                border: none;
            }}
        """)
        self.lbl_name.setWordWrap(True)

        self.lbl_email = QLabel(data[3] or "Sin email")
        self.lbl_email.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_MUT};
                font-size: 10px;
                font-weight: 700;
                font-family: 'Inter';
                background: transparent;
                border: none;
            }}
        """)
        self.lbl_email.setWordWrap(True)

        title_col.addStretch()
        title_col.addWidget(self.lbl_name)
        title_col.addWidget(self.lbl_email)

        belts_row = QHBoxLayout()
        belts_row.setContentsMargins(0, 4, 0, 0)
        belts_row.setSpacing(6)

        if self.instructor_belts:
            for belt in self.instructor_belts[:2]:
                belt_widget = InstructorBeltMiniBar(
                    belt_name=belt.get("belt_name"),
                    color=belt.get("color"),
                    pre_color=belt.get("pre_color"),
                    grades=belt.get("grades", 0),
                    grade_color=belt.get("grade_color", "#FFFFFF"),
                    martial_art_name=belt.get("ma_name", ""),
                )
                belts_row.addWidget(belt_widget)
            if len(self.instructor_belts) > 2:
                more = QLabel(f"+{len(self.instructor_belts) - 2}")
                more.setStyleSheet(f"color: {TEXT_MUT}; font-size: 9px; font-weight: 800; background: transparent; border: none;")
                belts_row.addWidget(more)
        else:
            no_belt = QLabel("Sin cinturón asignado")
            no_belt.setStyleSheet(f"color: {TEXT_MUT}; font-size: 9px; font-weight: 700; background: transparent; border: none;")
            belts_row.addWidget(no_belt)

        belts_row.addStretch()
        title_col.addLayout(belts_row)

        title_col.addStretch()

        header.addWidget(
            self.avatar,
            0,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )
        header.addLayout(title_col, 1)

        layout.addWidget(header_box)

        layout.addSpacing(4)

        # ── Métricas ──────────────────────────────────────────────────
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(8)

        total_classes = class_count

        is_sensei = bool(data[-1]) if len(data) > 0 and isinstance(data[-1], bool) else False
        mas = martial_arts or []
        rank_text, rank_color = _resolve_instructor_rank(is_sensei, mas)

        box1 = QFrame()
        box1.setFixedHeight(82)
        box1.setStyleSheet("background-color: #070707; border: 1px solid #141414; border-radius: 8px;")
        v1 = QVBoxLayout(box1)
        v1.setContentsMargins(8, 8, 8, 8)
        v1.setSpacing(2)
        lbl_c_val = QLabel(str(total_classes))
        lbl_c_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_c_val.setStyleSheet(f"color: {TEXT_PRI}; font-size: 13px; font-weight: 800;")
        lbl_c_tag = QLabel("CLASES")
        lbl_c_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_c_tag.setStyleSheet(f"color: {TEXT_MUT}; font-size: 8px; font-weight: 700; letter-spacing: 0.5px;")
        v1.addWidget(lbl_c_val)
        v1.addWidget(lbl_c_tag)

        box2 = QFrame()
        box2.setFixedHeight(82)
        box2.setStyleSheet("background-color: #070707; border: 1px solid #141414; border-radius: 8px;")
        v2 = QVBoxLayout(box2)
        v2.setContentsMargins(8, 8, 8, 8)
        v2.setSpacing(2)
        lbl_r_val = QLabel(rank_text)
        lbl_r_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_r_val.setStyleSheet(f"color: {rank_color}; font-size: 13px; font-weight: 800;")
        lbl_r_tag = QLabel("RANGO")
        lbl_r_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_r_tag.setStyleSheet(f"color: {TEXT_MUT}; font-size: 8px; font-weight: 700; letter-spacing: 0.5px;")
        v2.addWidget(lbl_r_val)
        v2.addWidget(lbl_r_tag)

        metrics_layout.addWidget(box1)
        metrics_layout.addWidget(box2)
        layout.addLayout(metrics_layout)

        # ── Insignias ─────────────────────────────────────────────────
        tag_layout = QHBoxLayout()
        tag_layout.setSpacing(4)

        if mas:
            for m in mas[:3]:
                tag = QLabel(m["ma_name"][:12])
                tag.setStyleSheet(f"""
                    QLabel {{
                        background-color: #121212;
                        color: {TEXT_SEC};
                        border: 1px solid {BORDER};
                        border-radius: 5px;
                        font-size: 9px;
                        font-weight: 700;
                        padding: 2px 6px;
                    }}
                """)
                tag_layout.addWidget(tag)
        else:
            tag = QLabel("SIN ARTES ASIGNADAS")
            tag.setStyleSheet(f"color: {TEXT_MUT}; font-size: 9px; font-weight: 700; font-style: italic;")
            tag_layout.addWidget(tag)

        tag_layout.addStretch()
        layout.addLayout(tag_layout)

        # ── Footer ────────────────────────────────────────────────────
        footer_layout = QHBoxLayout()
        lbl_exp = QLabel("Ver Expediente →")
        lbl_exp.setStyleSheet(f"color: {TEXT_MUT}; font-size: 9px; font-weight: 800; letter-spacing: 0.5px;")
        lbl_id = QLabel(f"ID: {self.instructor_id}")
        lbl_id.setStyleSheet(f"color: {TEXT_MUT}; font-size: 9px; font-weight: 800;")
        footer_layout.addWidget(lbl_exp)
        footer_layout.addStretch()
        footer_layout.addWidget(lbl_id)
        layout.addLayout(footer_layout)

    def _apply_style(self, hovered):
        bg = "#101010" if hovered or self.selected else BG_CARD
        border_col = RED if self.selected else (RED_H if hovered else BORDER)

        self.setStyleSheet(f"""
            QFrame#InstructorCard {{
                background-color: {bg};
                border: 1px solid {border_col};
                border-radius: 18px;
            }}
        """)

    def _apply_avatar_style(self, active=False):
        border_col = GREEN if active else BORDER
        text_col = GREEN if active else RED

        self.avatar.setStyleSheet(f"""
            QLabel#InstructorAvatar {{
                background-color: #121212;
                color: {text_col};
                font-size: 15px;
                font-weight: 900;
                border-radius: 29px;
                border: 2px solid {border_col};
            }}
        """)

    def set_selected(self, selected):
        self.selected = selected
        self._apply_style(self.hovered)
        self._apply_avatar_style(selected or self.hovered)

    def enterEvent(self, event):
        self.hovered = True

        self.raise_()
        self.shadow.setColor(QColor(RED))
        self.shadow.setOffset(0, 12)

        self._anim_shadow.stop()
        self._anim_shadow.setStartValue(self.shadow.blurRadius())
        self._anim_shadow.setEndValue(34)
        self._anim_shadow.start()

        self._apply_style(True)
        self._apply_avatar_style(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False

        self.shadow.setColor(QColor(0, 0, 0, 180))
        self.shadow.setOffset(0, 5)

        self._anim_shadow.stop()
        self._anim_shadow.setStartValue(self.shadow.blurRadius())
        self._anim_shadow.setEndValue(16)
        self._anim_shadow.start()

        self._apply_style(False)
        self._apply_avatar_style(self.selected)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.instructor_id)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.instructor_id)
        super().mouseDoubleClickEvent(event)


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

    def _build_create_ui(self, root):
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


# ─── GESTIÓN DE ARTES MARCIALES ───────────────────────────────────────
class MartialArtsDialog(QDialog):
    def __init__(self, repo, instructor_id, parent=None):
        super().__init__(parent)
        self.repo          = repo
        self.instructor_id = instructor_id
        self.setWindowTitle("Artes Marciales del Instructor")
        self.setFixedSize(460, 500)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: #111111; color: {TEXT_PRI};")
        self._selected_ma_id = None

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)

        hdr1 = QHBoxLayout()
        lbl1 = QLabel("ASIGNADAS")
        lbl1.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; font-weight: 700; letter-spacing: 0.8px;")
        self.btn_remove = QPushButton("🗑  Quitar")
        self.btn_remove.setFixedHeight(28)
        self.btn_remove.setEnabled(False)
        self.btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_remove.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: #FF4444;
                border: 1px solid #FF4444; border-radius: 6px;
                font-size: 11px; font-weight: 600; padding: 0 12px;
            }}
            QPushButton:hover {{ background: #2A0A0A; }}
            QPushButton:disabled {{ color: #3A1A1A; border-color: #2A1A1A; }}
        """)
        self.btn_remove.clicked.connect(self._remove_ma)
        hdr1.addWidget(lbl1); hdr1.addStretch(); hdr1.addWidget(self.btn_remove)
        root.addLayout(hdr1)

        self.assigned_scroll = QScrollArea()
        self.assigned_scroll.setWidgetResizable(True)
        self.assigned_scroll.setFixedHeight(160)
        self.assigned_scroll.setStyleSheet(f"""
            QScrollArea {{ background: #1A1A1A; border: 1.5px solid {BORDER}; border-radius: 8px; }}
            QScrollBar:vertical {{ background: #1A1A1A; width: 6px; border-radius: 3px; }}
            QScrollBar::handle:vertical {{ background: #333; border-radius: 3px; min-height: 20px; }}
        """)
        self.assigned_container = QWidget()
        self.assigned_container.setStyleSheet("background: transparent;")
        self.assigned_vbox = QVBoxLayout(self.assigned_container)
        self.assigned_vbox.setContentsMargins(0, 4, 0, 4)
        self.assigned_vbox.setSpacing(2)
        self.assigned_scroll.setWidget(self.assigned_container)
        root.addWidget(self.assigned_scroll)

        lbl2 = QLabel("AGREGAR ARTE MARCIAL")
        lbl2.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; font-weight: 700; letter-spacing: 0.8px;")
        root.addWidget(lbl2)

        self.avail_scroll = QScrollArea()
        self.avail_scroll.setWidgetResizable(True)
        self.avail_scroll.setFixedHeight(120)
        self.avail_scroll.setStyleSheet(f"""
            QScrollArea {{ background: #1A1A1A; border: 1.5px solid {BORDER}; border-radius: 8px; }}
            QScrollBar:vertical {{ background: #1A1A1A; width: 6px; border-radius: 3px; }}
            QScrollBar::handle:vertical {{ background: #333; border-radius: 3px; min-height: 20px; }}
        """)
        self.avail_container = QWidget()
        self.avail_container.setStyleSheet("background: transparent;")
        self.avail_vbox = QVBoxLayout(self.avail_container)
        self.avail_vbox.setContentsMargins(0, 4, 0, 4)
        self.avail_vbox.setSpacing(2)
        self.avail_scroll.setWidget(self.avail_container)
        root.addWidget(self.avail_scroll)

        add_row = QHBoxLayout(); add_row.setSpacing(10)
        self.chk_promote = QCheckBox("Puede promover estudiantes")
        self.chk_promote.setStyleSheet(f"""
            QCheckBox {{ color: {TEXT_PRI}; font-size: 12px; spacing: 8px; background: transparent; border: none; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 4px; border: 1.5px solid {BORDER}; background: #1C1C1C; }}
            QCheckBox::indicator:checked {{ background: {RED}; border-color: {RED}; }}
            QCheckBox::indicator:hover {{ border-color: {RED}; }}
        """)
        self.btn_add = QPushButton("＋  Agregar")
        self.btn_add.setFixedHeight(34)
        self.btn_add.setFixedWidth(110)
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white; border: none; border-radius: 7px; font-size: 12px; font-weight: 700; }}
            QPushButton:hover {{ background: {RED_H}; }}
            QPushButton:disabled {{ background: #3A1A1A; color: #666; }}
        """)
        self.btn_add.clicked.connect(self._add_ma)
        add_row.addWidget(self.chk_promote, 1); add_row.addWidget(self.btn_add)
        root.addLayout(add_row)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #FF4444; font-size: 11px;")
        self.lbl_error.setFixedHeight(16)
        root.addWidget(self.lbl_error)

        btn_close = QPushButton("Cerrar")
        btn_close.setFixedHeight(34)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC}; border: 1px solid {BORDER}; border-radius: 7px; font-size: 13px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; }}
        """)
        btn_close.clicked.connect(self.accept)
        root.addWidget(btn_close)

        self._load_data()

    def _make_assigned_row(self, a: dict) -> QWidget:
        row = QWidget()
        row.setFixedHeight(38)
        row.setCursor(Qt.CursorShape.PointingHandCursor)
        self._style_assigned_row(row, False)
        hl = QHBoxLayout(row)
        hl.setContentsMargins(12, 0, 12, 0)
        hl.setSpacing(10)
        icon = QLabel("🥋")
        icon.setStyleSheet("font-size: 13px; background: transparent; border: none;")
        icon.setFixedWidth(20)
        lbl = QLabel(a["ma_name"])
        lbl.setStyleSheet("color: #F0F0F0; font-size: 13px; background: transparent; border: none;")
        promo = QLabel()
        if a["can_promote"]:
            promo.setText("★ Puede promover")
            promo.setStyleSheet(f"color: {ORANGE}; font-size: 10px; font-weight: 600; background: transparent; border: none;")
        hl.addWidget(icon); hl.addWidget(lbl, 1); hl.addWidget(promo)
        row.mousePressEvent = lambda e, r=row, aid=a: self._select_assigned(r, aid)
        return row

    def _style_assigned_row(self, row, selected):
        if selected:
            row.setStyleSheet(f"QWidget {{ background-color: #2A0A0C; border-radius: 6px; border-left: 3px solid {RED}; }}")
        else:
            row.setStyleSheet("QWidget { background-color: transparent; border-radius: 6px; border: none; } QWidget:hover { background-color: #222222; }")

    def _make_avail_row(self, ma: dict) -> QWidget:
        row = QWidget()
        row.setFixedHeight(36)
        row.setCursor(Qt.CursorShape.PointingHandCursor)
        self._style_avail_row(row, False)
        hl = QHBoxLayout(row)
        hl.setContentsMargins(12, 0, 12, 0)
        hl.setSpacing(8)
        lbl = QLabel(ma["name"])
        lbl.setStyleSheet("color: #D0D0D0; font-size: 13px; background: transparent; border: none;")
        hl.addWidget(lbl)
        row.mousePressEvent = lambda e, r=row, m=ma: self._select_avail(r, m)
        return row

    def _style_avail_row(self, row, selected):
        if selected:
            row.setStyleSheet(f"QWidget {{ background-color: #1A0A0C; border-radius: 6px; border-left: 3px solid {RED}; }}")
        else:
            row.setStyleSheet("QWidget { background-color: transparent; border-radius: 6px; border: none; } QWidget:hover { background-color: #222222; }")

    def _select_assigned(self, clicked_row, a):
        for i in range(self.assigned_vbox.count()):
            item = self.assigned_vbox.itemAt(i)
            if item and item.widget():
                self._style_assigned_row(item.widget(), False)
        self._style_assigned_row(clicked_row, True)
        self._selected_assigned = a
        self.btn_remove.setEnabled(True)

    def _select_avail(self, clicked_row, ma):
        for i in range(self.avail_vbox.count()):
            item = self.avail_vbox.itemAt(i)
            if item and item.widget():
                self._style_avail_row(item.widget(), False)
        self._style_avail_row(clicked_row, True)
        self._selected_avail = ma
        self.btn_add.setEnabled(True)

    def _load_data(self):
        self._selected_assigned = None
        self._selected_avail    = None
        self.btn_remove.setEnabled(False)

        while self.assigned_vbox.count():
            item = self.assigned_vbox.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        assigned     = self.repo.get_instructor_martial_arts(self.instructor_id)
        assigned_ids = set()

        if assigned:
            for a in assigned:
                row = self._make_assigned_row(a)
                self.assigned_vbox.addWidget(row)
                assigned_ids.add(a["ma_id"])
        else:
            lbl = QLabel("Sin artes marciales asignadas")
            lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; font-style: italic; padding: 12px 14px; background: transparent;")
            self.assigned_vbox.addWidget(lbl)

        self.assigned_vbox.addStretch()

        while self.avail_vbox.count():
            item = self.avail_vbox.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        available = [ma for ma in self.repo.get_martial_arts() if ma["id"] not in assigned_ids]
        self.btn_add.setEnabled(False)

        if available:
            for ma in available:
                row = self._make_avail_row(ma)
                self.avail_vbox.addWidget(row)
        else:
            lbl = QLabel("Todas las artes marciales ya están asignadas")
            lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; font-style: italic; padding: 12px 14px; background: transparent;")
            self.avail_vbox.addWidget(lbl)

        self.avail_vbox.addStretch()

    def _add_ma(self):
        self.lbl_error.setText("")
        if not hasattr(self, "_selected_avail") or not self._selected_avail:
            self.lbl_error.setText("⚠ Selecciona un arte marcial de la lista.")
            return
        try:
            self.repo.assign_instructor_martial_art(
                self.instructor_id, self._selected_avail["id"], self.chk_promote.isChecked()
            )
            self.chk_promote.setChecked(False)
            self._load_data()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")

    def _remove_ma(self):
        self.lbl_error.setText("")
        if not hasattr(self, "_selected_assigned") or not self._selected_assigned:
            self.lbl_error.setText("⚠ Selecciona una asignación para quitar.")
            return
        try:
            self.repo.remove_instructor_martial_art(self._selected_assigned["id"])
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
        self.setFixedSize(680, 500)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet("background-color: #111111; color: #F0F0F0;")

        self._data = repo.get_by_id(instructor_id)
        data    = self._data
        classes = repo.get_recent_classes(instructor_id)
        total_c = repo.get_class_count(instructor_id)
        mas     = repo.get_instructor_martial_arts(instructor_id)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 18)
        root.setSpacing(12)

        hdr = QHBoxLayout(); hdr.setSpacing(14)
        nombre = f"{(data or {}).get('first_name','')} {(data or {}).get('last_name','')}".strip()
        initials = "".join(p[0].upper() for p in nombre.split()[:2] if p)

        avatar = QLabel(initials or "?")
        avatar.setFixedSize(60, 60)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(
            "background-color: #1A1A1A; color: #C8102E; font-size: 18px; "
            "font-weight: 700; border-radius: 30px; border: 2px solid #2A2A2A;"
        )

        info_col = QVBoxLayout(); info_col.setSpacing(3)
        lbl_name = QLabel(nombre or "—")
        lbl_name.setStyleSheet("font-size: 17px; font-weight: 700; color: #F0F0F0;")
        lbl_sub = QLabel(
            f"Instructor  ·  ID: {(data or {}).get('id','—')}  ·  "
            f"{total_c} clase{'s' if total_c != 1 else ''} impartida{'s' if total_c != 1 else ''}"
        )
        lbl_sub.setStyleSheet("font-size: 11px; color: #666;")
        info_col.addWidget(lbl_name); info_col.addWidget(lbl_sub)

        rank_text, rank_color = _resolve_instructor_rank(
            bool(data.get("is_sensei")) if data else False, mas or []
        )
        badge = QLabel(f"🥋  {rank_text}")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter); badge.setFixedHeight(26)
        badge.setStyleSheet(f"""
            background-color: #1A1000; color: {rank_color};
            border: 1px solid {rank_color}; border-radius: 6px;
            font-size: 11px; font-weight: 600; padding: 0 12px;
        """)

        hdr.addWidget(avatar)
        hdr.addLayout(info_col, 1)
        hdr.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)
        root.addLayout(hdr)

        sep = QFrame(); sep.setFixedHeight(2)
        sep.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #C8102E, stop:0.4 #C8102E, stop:1 transparent); border: none;
        """)
        root.addWidget(sep)

        cards_row = QHBoxLayout(); cards_row.setSpacing(12)

        left_card = _make_card()
        ll = QVBoxLayout(left_card)
        ll.setContentsMargins(16, 14, 16, 14); ll.setSpacing(0)
        ll.addWidget(self._slbl("DATOS PERSONALES"))
        ll.addSpacing(6)
        ll.addLayout(self._drow("Email",    (data or {}).get("email") or "—"))
        ll.addLayout(self._drow("Teléfono", (data or {}).get("phone") or "—"))
        ll.addSpacing(14)
        inner_sep = QFrame(); inner_sep.setFixedHeight(1)
        inner_sep.setStyleSheet("background: #222; border: none;")
        ll.addWidget(inner_sep)
        ll.addSpacing(12)
        ll.addWidget(self._slbl("ARTES MARCIALES"))
        ll.addSpacing(6)
        if mas:
            for m in mas:
                r = QHBoxLayout(); r.setSpacing(8)
                dot = QLabel("●"); dot.setStyleSheet(f"color: {RED}; font-size: 9px;"); dot.setFixedWidth(12)
                lbl_ma = QLabel(m["ma_name"]); lbl_ma.setStyleSheet("color: #F0F0F0; font-size: 12px;")
                promo = QLabel("★ Puede promover" if m["can_promote"] else "")
                promo.setStyleSheet(f"color: {ORANGE}; font-size: 10px;")
                r.addWidget(dot); r.addWidget(lbl_ma, 1); r.addWidget(promo)
                ll.addLayout(r); ll.addSpacing(2)
        else:
            ll.addWidget(QLabel("Sin artes marciales asignadas"))
        ll.addStretch()
        cards_row.addWidget(left_card, 1)

        right_card = _make_card()
        cl = QVBoxLayout(right_card)
        cl.setContentsMargins(16, 14, 16, 14); cl.setSpacing(0)
        cl.addWidget(self._slbl("ÚLTIMAS CLASES"))
        cl.addSpacing(6)
        if classes:
            for fecha, clase, arte in classes:
                r = QHBoxLayout(); r.setSpacing(8)
                dot = QLabel("●"); dot.setStyleSheet(f"color: {BLUE}; font-size: 9px;"); dot.setFixedWidth(12)
                clase_text = str(clase) + (f"  ({arte})" if arte and arte != "—" else "")
                lbl_c = QLabel(clase_text); lbl_c.setStyleSheet("color: #F0F0F0; font-size: 12px;")
                lbl_d = QLabel(str(fecha)); lbl_d.setStyleSheet("color: #555; font-size: 11px;")
                lbl_d.setAlignment(Qt.AlignmentFlag.AlignRight); lbl_d.setMinimumWidth(60)
                r.addWidget(dot); r.addWidget(lbl_c, 1); r.addWidget(lbl_d)
                cl.addLayout(r); cl.addSpacing(4)
        else:
            empty_w = QWidget(); empty_w.setStyleSheet("background: transparent;")
            empty_l = QVBoxLayout(empty_w); empty_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl = QLabel("🗓️"); icon_lbl.setStyleSheet("font-size: 28px;"); icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg_lbl = QLabel("Sin clases registradas"); msg_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px;"); msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_l.addWidget(icon_lbl); empty_l.addWidget(msg_lbl)
            cl.addWidget(empty_w, 1)
        cl.addStretch()
        cards_row.addWidget(right_card, 1)
        root.addLayout(cards_row, 1)

        btn_row = QHBoxLayout(); btn_row.setSpacing(8)
        btn_ma = QPushButton("🥋  Artes Marciales")
        btn_ma.setFixedHeight(36); btn_ma.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ma.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {ORANGE}; border: 1px solid {ORANGE}; border-radius: 7px; font-size: 12px; font-weight: 600; padding: 0 14px; }}
            QPushButton:hover {{ background: #1A1000; }}
        """)
        btn_ma.clicked.connect(self._manage_martial_arts)
        btn_belts = QPushButton("🥋  Cinturones")
        btn_belts.setFixedHeight(36); btn_belts.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_belts.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {BLUE}; border: 1px solid {BLUE}; border-radius: 7px; font-size: 12px; font-weight: 600; padding: 0 14px; }}
            QPushButton:hover {{ background: #0A0A2A; }}
        """)
        btn_belts.clicked.connect(self._manage_belts)
        btn_sensei = QPushButton("🥋  Nombrar Sensei")
        btn_sensei.setFixedHeight(36); btn_sensei.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sensei.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {GREEN}; border: 1px solid {GREEN}; border-radius: 7px; font-size: 12px; font-weight: 600; padding: 0 14px; }}
            QPushButton:hover {{ background: #0A1F0A; }}
        """)
        btn_sensei.clicked.connect(self._appoint_sensei)
        btn_edit = QPushButton("✎  Editar")
        btn_edit.setFixedHeight(36); btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC}; border: 1px solid {BORDER}; border-radius: 7px; font-size: 12px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; }}
        """)
        btn_edit.clicked.connect(self._open_edit)
        btn_close = QPushButton("Cerrar")
        btn_close.setFixedHeight(36); btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white; border: none; border-radius: 7px; font-size: 12px; font-weight: 700; padding: 0 20px; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        btn_close.clicked.connect(self.reject)
        btn_row.addWidget(btn_ma); btn_row.addWidget(btn_belts); btn_row.addWidget(btn_sensei); btn_row.addStretch(); btn_row.addWidget(btn_edit); btn_row.addWidget(btn_close)
        root.addLayout(btn_row)

    def _slbl(self, text):
        l = QLabel(text)
        l.setStyleSheet("font-size: 10px; font-weight: 700; letter-spacing: 1px; color: #555; padding-bottom: 2px;")
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

    def _manage_belts(self):
        nombre = f"{self._data.get('first_name','')} {self._data.get('last_name','')}".strip()
        dlg = InstructorBeltsDialog(self.repo, self.instructor_id, instructor_name=nombre, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.accept()

    def _appoint_sensei(self):
        nombre = f"{self._data.get('first_name','')} {self._data.get('last_name','')}".strip()
        reply = QMessageBox.question(
            self, "Nombrar Sensei",
            f"¿Nombrar a {nombre} como Sensei principal?\n\n"
            "Si ya existe otro Sensei, será reemplazado.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.repo.appoint_sensei(self.instructor_id)
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


# ─── DIÁLOGO DE CINTURONES DEL INSTRUCTOR ─────────────────────────────
class InstructorBeltsDialog(QDialog):
    def __init__(self, repo, instructor_id, instructor_name="", parent=None):
        super().__init__(parent)
        self.repo = repo
        self.instructor_id = instructor_id
        self.instructor_name = instructor_name

        self.setWindowTitle(f"Cinturones — {instructor_name}")
        self.setFixedSize(520, 380)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: #111111; color: {TEXT_PRI};")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        title = QLabel("Asignar cinturón por arte marcial")
        title.setStyleSheet(f"font-size: 15px; font-weight: 800; color: {TEXT_PRI};")
        root.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        cont = QWidget()
        cont.setStyleSheet("background: transparent;")
        self.form_layout = QVBoxLayout(cont)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(10)
        scroll.setWidget(cont)
        root.addWidget(scroll, 1)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #FF4444; font-size: 11px;")
        root.addWidget(self.lbl_error)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 8px; font-size: 13px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; }}
        """)
        btn_cancel.clicked.connect(self.reject)
        self.btn_save = QPushButton("Guardar Cinturones")
        self.btn_save.setFixedHeight(38)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white; border: none;
                border-radius: 8px; font-size: 13px; font-weight: 700; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        self.btn_save.clicked.connect(self._save)
        btns.addWidget(btn_cancel); btns.addWidget(self.btn_save)
        root.addLayout(btns)

        self._load_data()

    def _load_data(self):
        martial_arts = self.repo.get_instructor_martial_arts(self.instructor_id)
        current_belts = self.repo.get_instructor_belts_batch([self.instructor_id])
        current_map = {}
        for belt in current_belts.get(self.instructor_id, []):
            current_map[belt["ma_id"]] = belt["belt_id"]

        self._combo_map = {}

        if not martial_arts:
            lbl = QLabel("El instructor no tiene artes marciales asignadas.")
            lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; padding: 20px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.form_layout.addWidget(lbl)
            self.btn_save.setEnabled(False)
            return

        for ma in martial_arts:
            row = QHBoxLayout()
            row.setSpacing(10)
            lbl_ma = QLabel(ma["ma_name"])
            lbl_ma.setFixedWidth(140)
            lbl_ma.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px; font-weight: 700;")

            combo = QComboBox()
            combo.addItem("— Sin cinturón —", None)
            combo.setStyleSheet(f"""
                QComboBox {{
                    background: #1C1C1C; color: {TEXT_PRI};
                    border: 1px solid {BORDER}; border-radius: 6px;
                    padding: 0 10px; font-size: 11px; min-height: 32px;
                }}
                QComboBox:hover {{ border-color: #555; }}
                QComboBox::drop-down {{ border: none; width: 20px; }}
                QComboBox QAbstractItemView {{
                    background: #1A1A1A; color: {TEXT_PRI};
                    border: 1px solid {BORDER}; border-radius: 4px;
                    selection-background-color: {RED}; outline: none;
                    font-size: 11px;
                }}
            """)

            belts = self.repo.get_belts_by_martial_art(ma["ma_id"])
            selected_idx = 0
            for i, belt in enumerate(belts):
                label = belt["name"]
                combo.addItem(label, belt["id"])
                if belt["id"] == current_map.get(ma["ma_id"]):
                    selected_idx = i + 1

            combo.setCurrentIndex(selected_idx)
            self._combo_map[ma["ma_id"]] = combo

            row.addWidget(lbl_ma); row.addWidget(combo, 1)
            self.form_layout.addLayout(row)

        self.form_layout.addStretch()

    def _save(self):
        belts_to_save = []
        for ma_id, combo in self._combo_map.items():
            belt_id = combo.currentData()
            if belt_id is not None:
                belts_to_save.append({"id_martial_art": ma_id, "id_belt": belt_id})

        try:
            self.btn_save.setEnabled(False)
            self.btn_save.setText("Guardando...")
            self.repo.save_instructor_belts(self.instructor_id, belts_to_save)
            self.accept()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")
            self.btn_save.setEnabled(True)
            self.btn_save.setText("Guardar Cinturones")


# ─── VISTA PRINCIPAL ──────────────────────────────────────────────────
class InstructorsView(QWidget):
    def __init__(self):
        super().__init__()
        self.repo  = InstructorsRepository()
        self._rows = []
        self._card_widgets = []
        self._selected_id = None
        self._build_ui()
        self._load()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {BG_MAIN};")
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        hdr = QHBoxLayout()
        title = QLabel("🥋  Staff de Instructores")
        title.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {TEXT_PRI}; font-family: 'Inter'; letter-spacing: -0.3px;")
        self.btn_delete = QPushButton("🗑  Eliminar")
        self.btn_delete.setFixedHeight(38); self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: #FF4444; border: 1px solid #FF4444; border-radius: 7px; font-size: 13px; font-weight: 600; padding: 0 18px; }}
            QPushButton:hover {{ background: #2A0A0A; }}
        """)
        self.btn_delete.clicked.connect(self._delete_instructor)
        self.btn_new = QPushButton("＋  Registrar Instructor")
        self.btn_new.setFixedHeight(38); self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white; border: none; border-radius: 7px; font-size: 13px; font-weight: 600; padding: 0 18px; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        self.btn_new.clicked.connect(self._create_instructor)
        hdr.addWidget(title); hdr.addStretch(); hdr.addWidget(self.btn_delete); hdr.addWidget(self.btn_new)
        root.addLayout(hdr)

        sep = QFrame(); sep.setFixedHeight(2)
        sep.setStyleSheet(f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {RED},stop:0.4 {RED},stop:1 transparent); border: none;")
        root.addWidget(sep)

        toolbar = QHBoxLayout(); toolbar.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Filtrar por instructor, disciplina o contacto...")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{ background: #121212; color: {TEXT_PRI}; border: 1.5px solid {BORDER}; border-radius: 8px; padding: 0 14px; font-size: 13px; font-family: 'Inter'; }}
            QLineEdit:focus {{ border-color: {RED}; }}
        """)
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._load)
        self.search_input.textChanged.connect(lambda: self._search_timer.start(350))

        btn_refresh = QPushButton("↻  Sincronizar")
        btn_refresh.setFixedHeight(40); btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC}; border: 1px solid {BORDER}; border-radius: 8px; font-size: 12px; padding: 0 16px; font-weight: 700; }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; background-color: #121212; }}
        """)
        btn_refresh.clicked.connect(self._load)

        btn_edit = QPushButton("✎  Editar")
        btn_edit.setFixedHeight(40); btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC}; border: 1px solid {BORDER}; border-radius: 8px; font-size: 12px; padding: 0 16px; font-weight: 700; }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; background-color: #121212; }}
        """)
        btn_edit.clicked.connect(self._edit_instructor)

        self.cmb_belt_filter = QComboBox()
        self.cmb_belt_filter.addItem("Todos los cinturones", None)
        self.cmb_belt_filter.setFixedHeight(40)
        self.cmb_belt_filter.setMinimumWidth(170)
        self.cmb_belt_filter.setStyleSheet(f"""
            QComboBox {{
                background: #121212; color: {TEXT_SEC};
                border: 1.5px solid {BORDER}; border-radius: 8px;
                padding: 0 12px; font-size: 11px; font-family: 'Inter';
            }}
            QComboBox:hover {{ border-color: #555; }}
            QComboBox::drop-down {{
                border: none; width: 24px;
            }}
            QComboBox::down-arrow {{
                image: none; border: none;
            }}
            QComboBox QAbstractItemView {{
                background: #1A1A1A; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 6px;
                selection-background-color: {RED}; outline: none;
                font-size: 11px; padding: 4px;
            }}
        """)
        self.cmb_belt_filter.currentIndexChanged.connect(self._load)
        self._populate_belt_filter()

        toolbar.addWidget(self.cmb_belt_filter)
        toolbar.addWidget(self.search_input, 1)
        toolbar.addWidget(btn_refresh); toolbar.addWidget(btn_edit)
        root.addLayout(toolbar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { border: none; background: #080808; width: 8px; margin: 0px; }
            QScrollBar::handle:vertical { background: #1F1F1F; border-radius: 4px; min-height: 20px; }
            QScrollBar::handle:vertical:hover { background: #333333; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
        """)

        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background: transparent;")
        self.grid_widget.setMinimumWidth(0)
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setHorizontalSpacing(GRID_GAP)
        self.grid_layout.setVerticalSpacing(26)
        self.grid_layout.setContentsMargins(8, 8, 8, 18)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.scroll_area.setWidget(self.grid_widget)
        root.addWidget(self.scroll_area, 1)

        self.lbl_count = QLabel("Cargando staff...")
        self.lbl_count.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; font-weight: 600; font-family: 'Inter';")
        root.addWidget(self.lbl_count)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._rows:
            self._reorganize_grid()

    def _populate_belt_filter(self):
        try:
            options = self.repo.get_belt_filter_options()
            for opt in options:
                label = f"{opt['ma_name']} — {opt['name']}"
                self.cmb_belt_filter.addItem(label, opt["id"])
        except Exception:
            pass

    def _load(self):
        self.lbl_count.setText("Cargando staff...")
        belt_id = self.cmb_belt_filter.currentData()
        self._worker = LoadWorker(
            self.repo,
            self.search_input.text().strip(),
            belt_id=belt_id
        )
        self._worker.done.connect(self._on_data)
        self._worker.start()

    def _on_data(self, rows):
        self._rows = rows
        self._clear_grid()
        self._destroy_cards()
        self._card_widgets.clear()

        if not rows:
            self.lbl_count.setText("No se encontraron perfiles de instructores.")
            return

        ids = [r[0] for r in rows]
        class_counts        = self.repo.get_class_counts_batch(ids) if ids else {}
        martial_arts_map    = self.repo.get_instructor_martial_arts_batch(ids) if ids else {}
        instructor_belts_map = self.repo.get_instructor_belts_batch(ids) if ids else {}

        for r in rows:
            iid  = r[0]
            card = InstructorCard(
                r,
                class_count=class_counts.get(iid, 0),
                martial_arts=martial_arts_map.get(iid, []),
                instructor_belts=instructor_belts_map.get(iid, []),
                parent=self
            )
            card.clicked.connect(self._on_card_selected)
            card.double_clicked.connect(self._view_detail)
            self._card_widgets.append(card)

        self._reorganize_grid()

    def _clear_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

    def _destroy_cards(self):
        for card in self._card_widgets:
            card.deleteLater()

    def _reorganize_grid(self):
        self._clear_grid()
        if not self._card_widgets:
            return

        cols = 2
        viewport_w = self.scroll_area.viewport().width()
        available_w = viewport_w - GRID_GAP - 32
        card_w = int(available_w / cols)
        card_w = max(CARD_MIN_W, min(CARD_MAX_W, card_w))

        for i, card in enumerate(self._card_widgets):
            card.setFixedSize(card_w, CARD_H)

            self.grid_layout.addWidget(
                card, i // cols, i % cols,
                alignment=Qt.AlignmentFlag.AlignTop
            )
            is_selected = card.instructor_id == self._selected_id
            card.selected = is_selected
            card.hovered  = False
            card._apply_style(False)
            card._apply_avatar_style(is_selected)

        for c in range(cols):
            self.grid_layout.setColumnStretch(c, 0)

        total = len(self._rows)
        self.lbl_count.setText(
            f"{total} instructor{'es' if total != 1 else ''} registrado{'s' if total != 1 else ''} en Dojo"
        )

    def _on_card_selected(self, instructor_id):
        self._selected_id = instructor_id
        for card in self._card_widgets:
            card.set_selected(card.instructor_id == instructor_id)

    def _get_selected(self):
        if not self._selected_id:
            return None
        return next((r for r in self._rows if r[0] == self._selected_id), None)

    def _view_detail(self, instructor_id=None):
        target_id = instructor_id or self._selected_id
        if not target_id:
            return
        dlg = InstructorDetail(target_id, self.repo, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load()

    def _create_instructor(self):
        dlg = InstructorFormDialog(self.repo, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load()

    def _edit_instructor(self):
        r = self._get_selected()
        if not r:
            QMessageBox.information(self, "Aviso", "Selecciona un instructor de la lista.")
            return
        dlg = InstructorFormDialog(self.repo, instructor_id=r[0], parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._load()

    def _delete_instructor(self):
        r = self._get_selected()
        if not r:
            QMessageBox.information(self, "Aviso", "Selecciona una tarjeta de instructor.")
            return
        confirm = QMessageBox(self)
        confirm.setWindowTitle("Confirmar eliminación")
        confirm.setText(f"¿Eliminar a {r[1]} como instructor?")
        confirm.setInformativeText(
            "No se puede eliminar si tiene clases asignadas.\n"
            "Se eliminará su perfil de instructor y artes marciales.\n"
            "La persona no se eliminará del sistema."
        )
        confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        confirm.setDefaultButton(QMessageBox.StandardButton.Cancel)
        confirm.setStyleSheet("background-color: #161616; color: #F0F0F0;")
        if confirm.exec() == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete(r[0])
                self._selected_id = None
                self._load()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{e}")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._view_detail()
        elif event.key() == Qt.Key.Key_E:
            self._edit_instructor()
        super().keyPressEvent(event)