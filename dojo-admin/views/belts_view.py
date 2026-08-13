# ─── BELTS_VIEW ─────────────────────────────────────────────
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QDialog, QLineEdit, QComboBox, QScrollArea, QMenu,
    QSizePolicy, QGraphicsBlurEffect, QGraphicsOpacityEffect,
    QGraphicsDropShadowEffect, QStackedWidget, QSplitter, QApplication,
    QSpinBox, QCheckBox, QTextEdit,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QRectF, QRect
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QPen, QKeyEvent, QFont, QTextOption
from core.debug import debug_log
from repositories.belts_repository import BeltsRepository
from views.icon_library import AppIcon, MartialArtIcon, MARTIAL_ART_ICON_LIBRARY, normalize_martial_art_icon
from views.martial_arts.martial_art_theme import (
    MA_BG, MA_SIDE, MA_CARD, MA_HOVER, MA_INPUT, MA_SURFACE, MA_BORDER, MA_BORDER_HI,
    MA_RED, MA_RED_H, MA_GREEN, MA_YELLOW, MA_BLUE, MA_PURPLE, MA_ORANGE,
    MA_TEXT_PRI, MA_TEXT_SEC, MA_TEXT_MUT, MA_TEXT_DARK,
    MA_MODAL_BG, MA_MODAL_BORDER, MA_MODAL_CARD,
    MA_FIELD_QSS, MA_SCROLL_QSS, MA_SCROLLBAR_QSS, MA_CARD_QSS,
    _ma_shadow, _ma_card, _ma_primary_btn, _ma_secondary_btn, _ma_icon_btn,
    _ma_field_label, _ma_section_label, _ma_badge, _ma_scroll, _ma_separator,
    _ma_empty_state, _ma_label, valid_hex_color, normalize_active_state,
)
from views.martial_arts.martial_art_widgets import (
    ExistingProgressionPanel, RequirementTypeDialog, MartialArtConfirmDialog,
    DisciplineExerciseCard, DisciplineExerciseDialog,
    ColorPaletteSelector, IconTextButton, MartialArtFormDialog,
    BeltFormSection, LevelStateButton,
    RequirementVisualCard, RequirementCard,
    create_progression_level_preview, ShirtLevelPreview,
)
from views.martial_arts.martial_art_settings_view import MartialArtSettingsView

RED = "#C8102E"
BLACK = "#000000"

_MA_FF = "font-family: 'Inter', 'Segoe UI', sans-serif;"

# Layout constants
CARD_MIN_WIDTH = 260
CARD_MAX_WIDTH = 320

_DIALOG_CARD_QSS = f"""
    QFrame#dialogCard {{
        background: {MA_CARD};
        border: 1px solid {MA_BORDER};
        border-radius: 20px;
    }}
    QFrame#dialogCard * {{
        background: transparent;
        border: none;
    }}
"""
_DIALOG_OVERLAY_QSS = "background: rgba(0,0,0,140);"


# ============================================================
# PROTECTED BELT RENDERING
# Do not modify without explicit user authorization.
# ============================================================
# ─── Protected zone ──────────────────────────────────────────
def _belt_border(color: str) -> str:
    light = {"#FFFFFF", "#FFD700", "#FF8C00", "#FFFF00", "#FFA500", "#FFFACD", "#E8E8E8"}
    return "#999999" if color.upper() in light else "#333333"


def _is_bjj(name: str) -> bool:
    if not name:
        return False
    n = name.strip().lower()
    return n in {"brazilian jiu-jitsu", "bjj", "jiu-jitsu brasile\u00f1o", "jiu jitsu brasile\u00f1o"}


def _lbl(text):
    return _ma_field_label(text)


def _make_glass_card():
    return _ma_card()


_BELT_SCROLL_QSS = f"""
    QScrollArea#BeltFormScroll {{
        background: {MA_MODAL_BG};
        border: none;
    }}
    QScrollArea#BeltFormScroll > QWidget > QWidget {{
        background: {MA_MODAL_BG};
    }}
    QWidget#BeltFormBody {{
        background: {MA_MODAL_BG};
    }}
    QScrollBar:vertical {{
        background: {MA_MODAL_BG};
        width: 12px;
        margin: 4px;
        border: none;
    }}
    QScrollBar::handle:vertical {{
        background: {MA_MODAL_BORDER};
        min-height: 36px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {MA_RED};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: transparent;
    }}
    {_MA_FF}
"""


# ─── PremiumBeltBar ──────────────────────────────────────────
class PremiumBeltBar(QWidget):
    def __init__(self, color="#FFFFFF", pre_color=None, grades=0, grade_color="#FFFFFF",
                 martial_art_name="", width=140, height=24, parent=None):
        super().__init__(parent)
        self.color = color or "#FFFFFF"
        self.pre_color = pre_color
        self.grades = grades or 0
        self.grade_color = grade_color or "#FFFFFF"
        self.martial_art_name = martial_art_name
        self.setFixedSize(width, height)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        h = rect.height()
        belt_h = int(h * 0.7)
        belt_y = (h - belt_h) // 2
        belt_rect = rect.adjusted(0, belt_y, 0, -belt_y)
        r = belt_h // 2

        path = QPainterPath()
        path.addRoundedRect(QRectF(belt_rect), r, r)
        painter.setClipPath(path)

        base_color = QColor(self.color)
        painter.setBrush(base_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(belt_rect, r, r)

        w = belt_rect.width()
        top = belt_rect.top()
        bh = belt_rect.height()

        if self.pre_color:
            stripe_w = max(10, int(w * 0.08))
            stripe_x = belt_rect.right() - stripe_w - int(w * 0.03)
            painter.setBrush(QColor(self.pre_color))
            painter.drawRect(stripe_x, top, stripe_w, bh)

        elif _is_bjj(self.martial_art_name):
            tip_w = int(w * 0.35)
            tip_x = belt_rect.right() - tip_w
            if self.color.upper() == "#000000" or QColor(self.color).lightness() < 40:
                tip_color = QColor(BLACK)
            else:
                tip_color = QColor("#1A1A1A")
            painter.setBrush(tip_color)
            painter.drawRect(tip_x, top, tip_w, bh)

            max_stripes = min(self.grades, 4)
            stripe_h = int(bh * 0.6)
            stripe_y = top + (bh - stripe_h) // 2
            s_w = 3
            s_gap = 4
            total_s = max_stripes * s_w + (max_stripes - 1) * s_gap
            s_start = tip_x + (tip_w - total_s) // 2
            painter.setBrush(QColor(self.grade_color))
            for i in range(max_stripes):
                sx = s_start + i * (s_w + s_gap)
                painter.drawRoundedRect(sx, stripe_y, s_w, stripe_h, 1, 1)

        elif self.grades > 0:
            max_grades = min(self.grades, 10)
            stripe_h = int(bh * 0.6)
            stripe_y = top + (bh - stripe_h) // 2
            s_w = 3
            s_gap = 3
            total = max_grades * s_w + (max_grades - 1) * s_gap
            s_start = belt_rect.right() - total - 6
            painter.setBrush(QColor(self.grade_color))
            for i in range(max_grades):
                sx = s_start + i * (s_w + s_gap)
                painter.drawRoundedRect(sx, stripe_y, s_w, stripe_h, 1, 1)

        painter.setClipping(False)

        border_color = QColor(_belt_border(self.color))
        pen = QPen(border_color, 1.5)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(belt_rect, r, r)

    def set_belt_data(self, color=None, pre_color=None, grades=None, grade_color=None, martial_art_name=None):
        if color is not None: self.color = color
        if pre_color is not None: self.pre_color = pre_color
        if grades is not None: self.grades = grades
        if grade_color is not None: self.grade_color = grade_color
        if martial_art_name is not None: self.martial_art_name = martial_art_name
        self.update()


# ─── BeltWidget ─────────────────────────────────────────────────────────
class BeltWidget(QWidget):
    def __init__(self, color="#FFFFFF", pre_color=None, grades=0,
                 grade_color="#FFFFFF", martial_art="", parent=None):
        super().__init__(parent)
        self.color = color or "#FFFFFF"
        self.pre_color = pre_color
        self.grades = int(grades or 0)
        self.grade_color = grade_color or "#FFFFFF"
        self.martial_art = martial_art or ""
        self.setFixedSize(110, 20)

    def _is_light(self, hex_color):
        try:
            c = QColor(hex_color)
            return (c.red() * 0.299 + c.green() * 0.587 + c.blue() * 0.114) > 180
        except Exception:
            return False

    def _is_bjj(self):
        n = (self.martial_art or "").strip().lower()
        return n in {
            "brazilian jiu-jitsu", "bjj",
            "jiu-jitsu brasile\u00f1o", "jiu jitsu brasile\u00f1o",
            "brazilian jiu jitsu"
        }

    def _border_color(self):
        light_colors = {
            "#FFFFFF", "#FFD700", "#FF8C00",
            "#FFFF00", "#FFA500", "#FFFACD", "#E8E8E8"
        }
        if (self.color or "").upper() in light_colors:
            return "#999999"
        if self._is_light(self.color):
            return "#999999"
        return "#333333"

    def paintEvent(self, event):
        p = QPainter(self)
        if not p.isActive():
            return
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 4, 4)
        p.save()
        p.setClipPath(path)
        p.fillPath(path, QColor(self.color))

        if self.pre_color:
            stripe_w = max(7, min(11, rect.width() // 10))
            right_padding = max(10, rect.width() // 10)
            stripe_x = rect.right() - right_padding - stripe_w
            stripe_rect = QRect(stripe_x, rect.y(), stripe_w, rect.height())
            p.fillRect(stripe_rect, QColor(self.pre_color))

        elif self._is_bjj():
            tip_w = 38
            tip_rect = QRect(rect.right() - tip_w, rect.y(), tip_w, rect.height())
            c = QColor(self.color)
            tip_color = QColor(RED) if c.red() < 40 and c.green() < 40 and c.blue() < 40 else QColor("#111111")
            p.fillRect(tip_rect, tip_color)
            count = min(max(self.grades, 0), 4)
            stripe_w = 4
            gap = 3
            start_x = tip_rect.right() - 6 - ((stripe_w + gap) * count)
            for i in range(count):
                x = start_x + i * (stripe_w + gap)
                stripe_rect = QRect(x, tip_rect.y() + 2, stripe_w, tip_rect.height() - 4)
                p.fillRect(stripe_rect, QColor(self.grade_color or "#FFFFFF"))

        elif self.grades:
            count = min(max(self.grades, 0), 4)
            stripe_w = 4
            gap = 4
            total_w = count * stripe_w + max(0, count - 1) * gap
            start_x = rect.right() - total_w - 8
            for i in range(count):
                x = start_x + i * (stripe_w + gap)
                stripe_rect = QRect(x, rect.y() + 2, stripe_w, rect.height() - 4)
                p.fillRect(stripe_rect, QColor(self.grade_color or "#FFFFFF"))

        p.restore()
        p.setPen(QColor(self._border_color()))
        p.drawRoundedRect(QRectF(rect), 4, 4)


# ─── New UI components ────────────────────────────────────────
class MartialArtsEmptyState(QWidget):
    def __init__(self, icon_key, title, description="", action_text="", action_cb=None, parent=None):
        super().__init__(parent)
        self.setObjectName("MartialArtsEmptyState")
        self.setStyleSheet("""
            QWidget#MartialArtsEmptyState {
                background-color: #0E0E0E;
                border: 1px dashed #2A2A2A;
                border-radius: 14px;
            }
        """)
        self._vl = QVBoxLayout(self)
        self._vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._vl.setSpacing(12)
        self._vl.setContentsMargins(32, 32, 32, 32)

        self._ico = MartialArtIcon(icon_key, size=40, color=MA_TEXT_DARK)
        self._vl.addWidget(self._ico, 0, Qt.AlignmentFlag.AlignCenter)

        self._title_lbl = QLabel(title)
        self._title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_lbl.setStyleSheet(f"color: {MA_TEXT_SEC}; font-size: 14px; font-weight: 700; {_MA_FF} background: transparent; border: none;")
        self._vl.addWidget(self._title_lbl)

        self._desc_lbl = QLabel(description)
        self._desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._desc_lbl.setWordWrap(True)
        self._desc_lbl.setStyleSheet(f"color: {MA_TEXT_MUT}; font-size: 11px; {_MA_FF} background: transparent; border: none;")
        self._desc_lbl.setVisible(bool(description))
        self._vl.addWidget(self._desc_lbl)

        self._action_btn = None
        if action_text and action_cb:
            self._action_btn = _ma_primary_btn(action_text, height=34)
            self._action_btn.setFixedWidth(180)
            self._action_btn.clicked.connect(action_cb)
            self._vl.addWidget(self._action_btn, 0, Qt.AlignmentFlag.AlignCenter)

    def set_message(self, title, description="", action_label=None):
        self._title_lbl.setText(title)
        self._desc_lbl.setText(description)
        self._desc_lbl.setVisible(bool(description))
        if self._action_btn:
            self._action_btn.setVisible(action_label is not None)
            if action_label:
                self._action_btn.setText(action_label)


def _error_banner(text=""):
    lbl = QLabel(text)
    lbl.setObjectName("MartialArtsErrorBanner")
    lbl.setWordWrap(True)
    lbl.setVisible(bool(text))
    lbl.setStyleSheet(f"""
        QLabel#MartialArtsErrorBanner {{
            color: #FB7185;
            background-color: rgba(225,29,72,0.08);
            border: 1px solid rgba(225,29,72,0.25);
            border-radius: 9px;
            padding: 10px 12px;
            font-size: 10px; font-weight: 700;
            {_MA_FF}
        }}
    """)
    return lbl


# ─── MartialArtItem (Tarjeta de Disciplina) ──────────────────
class MartialArtItem(QFrame):
    clicked = pyqtSignal(dict)
    edit_clicked = pyqtSignal(dict)
    delete_clicked = pyqtSignal(dict)
    settings_clicked = pyqtSignal(dict)

    def __init__(self, martial_art, parent=None):
        super().__init__(parent)
        self.setObjectName("DisciplineCard")
        self.martial_art = martial_art
        self._selected = False
        self._hovered = False
        self.setFixedHeight(140)
        self.setMinimumWidth(CARD_MIN_WIDTH)
        self.setMaximumWidth(CARD_MAX_WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        accent = valid_hex_color(martial_art.get("accent_color"), MA_RED)
        icon_key = martial_art.get("icon_key") or ""
        _known = {e["key"] for e in MARTIAL_ART_ICON_LIBRARY}
        if not icon_key or icon_key not in _known:
            icon_key = normalize_martial_art_icon(icon_key, martial_art.get("name", ""))

        is_active = normalize_active_state(martial_art.get("is_active"))
        pe = normalize_active_state(martial_art.get("progression_enabled"))
        ps = martial_art.get("progression_system") or "belt"
        systems = {"belt": "Cinturones", "sash": "Fajas", "shirt": "Camisas",
                   "bracelet": "Brazaletes", "level": "Niveles", "grade": "Grados",
                   "custom": "Personalizado", "none": "Sin sistema"}
        sys_text = systems.get(ps, ps) if pe else "Sin progresion"

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(0)

        # Top accent line
        self.top_accent = QFrame()
        self.top_accent.setFixedHeight(3)
        self.top_accent.setStyleSheet(f"background: transparent; border: none; border-radius: 1px;")
        main_layout.addWidget(self.top_accent)

        main_layout.addSpacing(12)

        # Top row (Icon + Status)
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        
        icon_box = QFrame()
        icon_box.setObjectName("CardIconBox")
        icon_box.setFixedSize(44, 44)
        self._icon_box = icon_box
        icon_layout = QHBoxLayout(icon_box)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_w = MartialArtIcon(icon_key, size=24, color=MA_TEXT_SEC)
        icon_layout.addWidget(self._icon_w)
        top_row.addWidget(icon_box)

        top_row.addStretch()

        _badge_bg     = "#052E16" if is_active else "#1A1A1A"
        _badge_color  = MA_GREEN  if is_active else MA_TEXT_MUT
        _badge_border = "#166534" if is_active else MA_BORDER
        _badge_text   = "ACTIVO"  if is_active else "INACTIVO"
        status_badge = QLabel(_badge_text)
        status_badge.setStyleSheet(f"""
            background: {_badge_bg};
            color: {_badge_color};
            border: 1px solid {_badge_border};
            border-radius: 6px; padding: 4px 8px;
            font-size: 9px; font-weight: 800; {_MA_FF}
        """)
        top_row.addWidget(status_badge, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(top_row)
        main_layout.addStretch()

        # Info
        self.name_lbl = QLabel(martial_art["name"])
        self.name_lbl.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 16px; font-weight: 800; {_MA_FF} background: transparent; border: none;")
        main_layout.addWidget(self.name_lbl)

        self.sys_lbl = QLabel(sys_text)
        self.sys_lbl.setStyleSheet(f"color: {MA_TEXT_MUT}; font-size: 12px; font-weight: 500; {_MA_FF} background: transparent; border: none;")
        main_layout.addWidget(self.sys_lbl)

        self._apply_style()

    def _apply_style(self):
        if self._selected:
            self.setStyleSheet(f"""
                QFrame#DisciplineCard {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 #2A0A10, stop:0.55 #210B0F, stop:1 #160B0D);
                    border: 1px solid #7A1A2C;
                    border-radius: 16px;
                }}
            """)
            self.name_lbl.setStyleSheet(f"color: #FFFFFF; font-size: 16px; font-weight: 800; {_MA_FF} background: transparent; border: none;")
            self.sys_lbl.setStyleSheet(f"color: #F8B4C0; font-size: 12px; font-weight: 500; {_MA_FF} background: transparent; border: none;")
            self.top_accent.setStyleSheet(f"background: {MA_RED}; border: none; border-radius: 1px;")
        elif self._hovered:
            self.setStyleSheet(f"""
                QFrame#DisciplineCard {{
                    background-color: {MA_CARD};
                    border: 1px solid {MA_BORDER_HI};
                    border-radius: 16px;
                }}
            """)
            self.name_lbl.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 16px; font-weight: 800; {_MA_FF} background: transparent; border: none;")
            self.sys_lbl.setStyleSheet(f"color: {MA_TEXT_MUT}; font-size: 12px; font-weight: 500; {_MA_FF} background: transparent; border: none;")
            self.top_accent.setStyleSheet(f"background: transparent; border: none; border-radius: 1px;")
        else:
            self.setStyleSheet(f"""
                QFrame#DisciplineCard {{
                    background-color: {MA_SURFACE};
                    border: 1px solid {MA_BORDER};
                    border-radius: 16px;
                }}
            """)
            self.name_lbl.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 16px; font-weight: 800; {_MA_FF} background: transparent; border: none;")
            self.sys_lbl.setStyleSheet(f"color: {MA_TEXT_MUT}; font-size: 12px; font-weight: 500; {_MA_FF} background: transparent; border: none;")
            self.top_accent.setStyleSheet(f"background: transparent; border: none; border-radius: 1px;")

        self._apply_visual_state()

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _apply_visual_state(self):
        if self._selected:
            self._icon_box.setStyleSheet(f"""
                QFrame#CardIconBox {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 rgba(200,16,46,0.16), stop:1 rgba(200,16,46,0.06));
                    border: 1px solid rgba(232,21,47,0.35);
                    border-radius: 11px;
                }}
            """)
            self._icon_w.set_color("#FFFFFF")
        else:
            self._icon_box.setStyleSheet(f"""
                QFrame#CardIconBox {{
                    background-color: #171717;
                    border: 1px solid #2C2C2C;
                    border-radius: 11px;
                }}
            """)
            self._icon_w.set_color(MA_TEXT_SEC)

    def set_selected(self, selected: bool):
        self._selected = selected
        self._apply_style()

    def enterEvent(self, event):
        self._hovered = True
        self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._apply_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.clicked.emit(self.martial_art)
        super().mousePressEvent(event)


# ─── TimelineBeltItem ────────────────────────────────────────
class TimelineBeltItem(QFrame):
    clicked = pyqtSignal(dict)
    edit_clicked = pyqtSignal(dict)
    delete_clicked = pyqtSignal(dict)

    def __init__(
        self,
        belt,
        index,
        martial_art_name="",
        progression_system="belt",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("TimelineBeltItem")
        self.belt = belt
        self._selected = False
        self._hovered = False
        self.setMinimumHeight(92)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.level_type = str(belt.get("level_type") or "").strip().lower()
        self.progression_system = str(progression_system or "").strip().lower()
        self.effective_type = self.level_type or self.progression_system or "belt"

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 10, 18, 10)
        main_layout.setSpacing(14)

        self._selection_bar = QFrame()
        self._selection_bar.setFixedWidth(3)
        self._selection_bar.setObjectName("SelectionBar")
        self._selection_bar.setStyleSheet("QFrame#SelectionBar { background: transparent; border-radius: 1px; }")
        main_layout.addWidget(self._selection_bar)

        self.marker = QLabel(f"{index:02d}")
        self.marker.setFixedWidth(28)
        self.marker.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.marker.setStyleSheet(f"color: {MA_TEXT_MUT}; font-size: 11px; font-weight: 800; {_MA_FF} background: transparent; border: none;")
        main_layout.addWidget(self.marker)

        self.level_preview = create_progression_level_preview(
            self.belt,
            self.progression_system,
            width=84,
            height=68,
            belt_width=136,
            belt_height=24,
            martial_art_name=martial_art_name,
            parent=self,
        )
        main_layout.addWidget(self.level_preview)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        self.name_lbl = QLabel(belt["name"])
        self.name_lbl.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 13px; font-weight: 700; background: transparent; border: none; {_MA_FF}")
        
        sub = f"Orden {belt.get('orden', '—')}"
        if belt.get("grades"):
            sub += f" · {belt['grades']} grado(s)"
        self.sub_lbl = QLabel(sub)
        self.sub_lbl.setStyleSheet(f"color: {MA_TEXT_MUT}; font-size: 11px; background: transparent; border: none; {_MA_FF}")

        info_col.addWidget(self.name_lbl)
        info_col.addWidget(self.sub_lbl)
        main_layout.addLayout(info_col, 1)

        self.action_w = QWidget()
        self.action_w.setFixedWidth(60)
        self.action_w.setStyleSheet("background: transparent; border: none;")
        action_hl = QHBoxLayout(self.action_w)
        action_hl.setContentsMargins(0, 0, 0, 0)
        action_hl.setSpacing(4)

        self.btn_edit = _ma_icon_btn("✎", size=28, accent=MA_TEXT_SEC)
        self.btn_edit.clicked.connect(lambda: self.edit_clicked.emit(self.belt))
        self.btn_delete = _ma_icon_btn("✕", size=28, accent=MA_RED)
        self.btn_delete.clicked.connect(lambda: self.delete_clicked.emit(self.belt))

        action_hl.addWidget(self.btn_edit)
        action_hl.addWidget(self.btn_delete)
        main_layout.addWidget(self.action_w)

        self.action_opacity = QGraphicsOpacityEffect(self.action_w)
        self.action_opacity.setOpacity(0)
        self.action_w.setGraphicsEffect(self.action_opacity)

        self._apply_style()

    def _apply_style(self):
        if self._selected:
            self._selection_bar.setStyleSheet(f"QFrame#SelectionBar {{ background: {MA_RED}; border-radius: 1px; }}")
            self.setStyleSheet(f"QFrame#TimelineBeltItem {{ background: {MA_CARD}; border: 1px solid rgba(200,16,46,0.3); border-radius: 12px; }}")
            self.marker.setStyleSheet(f"color: {MA_RED}; font-size: 11px; font-weight: 800; {_MA_FF} background: transparent; border: none;")
        elif self._hovered:
            self._selection_bar.setStyleSheet(f"QFrame#SelectionBar {{ background: rgba(200,16,46,0.3); border-radius: 1px; }}")
            self.setStyleSheet(f"QFrame#TimelineBeltItem {{ background: {MA_CARD}; border: 1px solid transparent; border-radius: 12px; }}")
            self.marker.setStyleSheet(f"color: {MA_TEXT_SEC}; font-size: 11px; font-weight: 800; {_MA_FF} background: transparent; border: none;")
        else:
            self._selection_bar.setStyleSheet("QFrame#SelectionBar { background: transparent; border-radius: 1px; }")
            self.setStyleSheet(f"QFrame#TimelineBeltItem {{ background: transparent; border: 1px solid transparent; border-radius: 12px; }}")
            self.marker.setStyleSheet(f"color: {MA_TEXT_MUT}; font-size: 11px; font-weight: 800; {_MA_FF} background: transparent; border: none;")

    def set_selected(self, selected: bool):
        self._selected = selected
        self._apply_style()

    def enterEvent(self, event):
        self._hovered = True
        self.action_opacity.setOpacity(1)
        self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.action_opacity.setOpacity(0)
        self._apply_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.clicked.emit(self.belt)
        super().mousePressEvent(event)


# ─── RequirementCard ─────────────────────────────────────────
# RequirementCard now lives in views.martial_arts.martial_art_widgets
# as a subclass of RequirementVisualCard (imported above).


# ─── MartialArtDialog ─────────────────────────────────────────
class MartialArtDialog(MartialArtFormDialog):
    def __init__(self, repo, martial_art=None, parent=None):
        self.is_edit = martial_art is not None
        title = "Editar disciplina" if self.is_edit else "Nueva disciplina"
        super().__init__(960, 700, title, parent)
        self.setObjectName("MartialArtDialog")
        self.repo = repo
        self.martial_art = martial_art

        self._selected_icon_key = (
            martial_art.get("icon_key") or ""
        ) if martial_art else ""
        _lib_keys = {e["key"] for e in MARTIAL_ART_ICON_LIBRARY}
        if self._selected_icon_key and self._selected_icon_key not in _lib_keys:
            self._selected_icon_key = normalize_martial_art_icon(
                self._selected_icon_key,
                (martial_art.get("name") if martial_art else "") or ""
            )
        self._selected_accent = (
            (martial_art.get("accent_color") if martial_art else None) or MA_RED
        )

        two_col = QHBoxLayout()
        two_col.setSpacing(20)

        left_col = QWidget()
        left_vl = QVBoxLayout(left_col)
        left_vl.setContentsMargins(0, 0, 0, 0)
        left_vl.setSpacing(16)

        left_vl.addWidget(_lbl("NOMBRE DEL ARTE MARCIAL"))
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Ej: Karate, Judo, BJJ...")
        self.inp_name.setStyleSheet(MA_FIELD_QSS)
        if self.is_edit:
            self.inp_name.setText(martial_art["name"])
        left_vl.addWidget(self.inp_name)

        left_vl.addWidget(_lbl("COLOR PRINCIPAL"))
        self.color_selector = ColorPaletteSelector(self._selected_accent)
        self.color_selector.color_changed.connect(self._refresh_preview)
        left_vl.addWidget(self.color_selector)

        left_vl.addWidget(_lbl("SISTEMA DE PROGRESION"))
        prog_row = QHBoxLayout()
        prog_row.setSpacing(10)

        self.chk_progression = QPushButton("Activar progresi\u00f3n")
        self.chk_progression.setCheckable(True)
        self.chk_progression.setChecked(
            normalize_active_state(martial_art.get("progression_enabled")) if martial_art else True
        )
        self.chk_progression.setFixedHeight(38)
        self.chk_progression.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_prog_btn_style()
        self.chk_progression.clicked.connect(self._update_prog_btn_style)
        self.chk_progression.clicked.connect(self._update_system_visibility)
        prog_row.addWidget(self.chk_progression, 1)

        self.cmb_system = QComboBox()
        self.cmb_system.setStyleSheet(MA_FIELD_QSS)
        self.cmb_system.setFixedHeight(38)
        self.cmb_system.addItems(["belt", "sash", "shirt", "bracelet", "level", "grade", "custom", "none"])
        _sys_labels = {"belt": "Cinturones", "sash": "Fajas", "shirt": "Camisas",
                       "bracelet": "Brazaletes", "level": "Niveles", "grade": "Grados",
                       "custom": "Personalizado", "none": "Ninguno"}
        for i in range(self.cmb_system.count()):
            val = self.cmb_system.itemText(i)
            self.cmb_system.setItemText(i, _sys_labels.get(val, val))
        if martial_art:
            ps = martial_art.get("progression_system") or "belt"
            for i in range(self.cmb_system.count()):
                if self.cmb_system.itemData(i) == ps or self.cmb_system.itemText(i) == _sys_labels.get(ps, ps):
                    self.cmb_system.setCurrentIndex(i)
                    break
        prog_row.addWidget(self.cmb_system, 1)
        left_vl.addLayout(prog_row)

        self._update_system_visibility()

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(f"color: {MA_RED}; font-size: 11px; {_MA_FF}")
        left_vl.addWidget(self.lbl_error)

        self.btn_cancel = _ma_secondary_btn("Cancelar", height=38)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_save = _ma_primary_btn("Guardar" if self.is_edit else "Crear", height=38)
        self.btn_save.clicked.connect(self._save)
        self.inp_name.returnPressed.connect(self._save)
        self._add_footer_buttons(self.btn_cancel, self.btn_save)

        left_vl.addStretch()

        right_col = QWidget()
        right_col.setStyleSheet("background: transparent;")
        right_vl = QVBoxLayout(right_col)
        right_vl.setContentsMargins(0, 0, 0, 0)
        right_vl.setSpacing(12)

        right_vl.addWidget(_lbl("ICONO"))

        self.icon_search = QLineEdit()
        self.icon_search.setPlaceholderText("Buscar icono...")
        self.icon_search.setStyleSheet(MA_FIELD_QSS)
        self.icon_search.textChanged.connect(self._filter_icons)
        right_vl.addWidget(self.icon_search)

        icon_scroll = QScrollArea()
        icon_scroll.setWidgetResizable(True)
        icon_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        icon_scroll.setStyleSheet(MA_SCROLL_QSS)
        self.icon_container = QWidget()
        self.icon_container.setStyleSheet("background: transparent;")
        self.icon_grid = QGridLayout(self.icon_container)
        self.icon_grid.setContentsMargins(4, 4, 4, 4)
        self.icon_grid.setSpacing(6)
        icon_scroll.setWidget(self.icon_container)
        right_vl.addWidget(icon_scroll, 1)

        self._populate_icon_grid("")

        two_col.addWidget(left_col, 2)
        two_col.addWidget(right_col, 3)
        self._card_layout.addLayout(two_col, 1)

    def _populate_icon_grid(self, filter_text):
        while self.icon_grid.count():
            item = self.icon_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        ft = filter_text.strip().lower()
        row, col = 0, 0
        for entry in MARTIAL_ART_ICON_LIBRARY:
            if ft and ft not in entry["key"].lower() and ft not in entry["label"].lower():
                continue
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            border = MA_TEXT_PRI if entry["key"] == self._selected_icon_key else MA_BORDER
            btn.setStyleSheet(f"QPushButton {{ background: {MA_HOVER}; border: 2px solid {border}; border-radius: 8px; }} QPushButton:hover {{ border-color: {MA_BORDER_HI}; }}")
            inner = MartialArtIcon(entry["key"], size=24, color=MA_TEXT_SEC)
            layout = QVBoxLayout(btn)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(inner)
            btn.clicked.connect(lambda checked, k=entry["key"]: self._select_icon(k))
            self.icon_grid.addWidget(btn, row, col)
            col += 1
            if col >= 8:
                col = 0
                row += 1

    def _filter_icons(self, text):
        self._populate_icon_grid(text)

    def _select_icon(self, key):
        self._selected_icon_key = key
        self._populate_icon_grid(self.icon_search.text())

    def _refresh_preview(self, color):
        self._selected_accent = color

    def _update_prog_btn_style(self):
        checked = self.chk_progression.isChecked()
        if checked:
            self.chk_progression.setStyleSheet(f"""
                QPushButton {{ background: rgba(5,46,22,0.5); color: {MA_GREEN}; border: 1px solid #166534;
                    border-radius: 8px; font-size: 12px; font-weight: 800; {_MA_FF} }}
                QPushButton:hover {{ background: rgba(5,46,22,0.8); }}
            """)
        else:
            self.chk_progression.setStyleSheet(f"""
                QPushButton {{ background: {MA_INPUT}; color: {MA_TEXT_MUT}; border: 1px solid {MA_BORDER};
                    border-radius: 8px; font-size: 12px; font-weight: 700; {_MA_FF} }}
                QPushButton:hover {{ color: {MA_TEXT_SEC}; border-color: {MA_BORDER_HI}; }}
            """)

    def _update_system_visibility(self):
        self.cmb_system.setVisible(self.chk_progression.isChecked())

    def _save(self):
        name = self.inp_name.text().strip()
        if not name:
            self.lbl_error.setText("El nombre es obligatorio.")
            return
        try:
            icon_key = self._selected_icon_key or None
            accent = self.color_selector.color() or MA_RED
            prog_enabled = self.chk_progression.isChecked()
            prog_system = "none"
            if prog_enabled:
                _sys_labels_inv = {"Cinturones": "belt", "Fajas": "sash", "Camisas": "shirt",
                                   "Brazaletes": "bracelet", "Niveles": "level", "Grados": "grade",
                                   "Personalizado": "custom", "Ninguno": "none"}
                raw = self.cmb_system.currentText()
                prog_system = _sys_labels_inv.get(raw, raw)
            if self.is_edit:
                self.repo.update_martial_art(self.martial_art["id"], name, icon_key, accent)
            else:
                self.repo.create_martial_art(name, icon_key, accent)
            self.accept()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")

# ─── BeltDialog ──────────────────────────────────────────────
class BeltDialog(MartialArtFormDialog):
    def __init__(self, repo, martial_art_id, martial_art_name="", belt=None,
                 progression_system="belt", parent=None):
        self.is_edit = belt is not None
        self.belt = belt
        _level_labels = {
            "belt": ("Cinturón", "Cinturones"), "sash": ("Faja", "Fajas"),
            "shirt": ("Camisa", "Camisas"), "bracelet": ("Brazalete", "Brazaletes"),
            "level": ("Nivel", "Niveles"), "grade": ("Grado", "Grados"),
            "custom": ("Nivel", "Niveles"), "none": ("Nivel", "Niveles"),
        }
        _sl = _level_labels.get(progression_system, ("Nivel", "Niveles"))
        _level_name = _sl[0]
        title = f"Editar {_level_name}" if self.is_edit else f"Nuevo {_level_name}"
        super().__init__(1040, 720, title, parent)
        self.setObjectName("BeltDialog")
        self.repo = repo
        self.martial_art_id = martial_art_id
        self.martial_art_name = martial_art_name or ""
        self._progression_system = progression_system
        self.setMinimumSize(920, 650)

        self._instructions_btn = IconTextButton(
            "comentario-info", "Instrucciones",
            icon_size=15, icon_color="#60A5FA", height=32, variant="info",
        )
        self._instructions_btn.setToolTip("Consultar instrucciones de configuracion")
        self._instructions_btn.clicked.connect(self._open_instructions)
        self._set_header_subtitle(
            "Actualiza la representación, reglas y restricciones."
            if self.is_edit
            else "Configura representación, reglas y restricciones."
        )
        self._header_row.insertWidget(
            self._header_row.count() - 1, self._instructions_btn,
        )

        two_col = QHBoxLayout()
        two_col.setSpacing(16)

        left_col = QWidget()
        left_l = QVBoxLayout(left_col)
        left_l.setContentsMargins(0, 0, 8, 0)
        left_l.setSpacing(10)

        info_sec = BeltFormSection("INFORMACIÓN")
        name_orden = QHBoxLayout()
        name_orden.setSpacing(12)
        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        name_col.addWidget(_lbl("NOMBRE"))
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Ej: Blanco, Amarillo...")
        self.inp_name.setStyleSheet(MA_FIELD_QSS)
        if self.is_edit:
            self.inp_name.setText(belt["name"])
        name_col.addWidget(self.inp_name)
        name_orden.addLayout(name_col, 3)

        orden_col = QVBoxLayout()
        orden_col.setSpacing(4)
        orden_col.addWidget(_lbl("ORDEN"))
        self.inp_orden = QLineEdit()
        self.inp_orden.setPlaceholderText("1, 2, 3...")
        self.inp_orden.setStyleSheet(MA_FIELD_QSS)
        if self.is_edit:
            self.inp_orden.setText(str(belt.get("orden") or ""))
        orden_col.addWidget(self.inp_orden)
        name_orden.addLayout(orden_col, 1)
        info_sec.add_layout(name_orden)
        left_l.addWidget(info_sec)

        rep_sec = BeltFormSection("REPRESENTACIÓN")
        rep_sec.add_child(_lbl("COLOR PRINCIPAL"))
        init_color = (belt.get("color") or "#888888") if self.is_edit else "#888888"
        self._belt_palette = ColorPaletteSelector(init_color)
        rep_sec.add_child(self._belt_palette)

        rep_sec.add_child(_lbl("PRECOLOR"))
        init_pre = (belt.get("pre_color") or "") if self.is_edit else ""
        pre_wrap = QWidget()
        pre_wrap.setStyleSheet("background: transparent; border: none;")
        pre_wrap_l = QVBoxLayout(pre_wrap)
        pre_wrap_l.setContentsMargins(0, 0, 0, 0)
        pre_wrap_l.setSpacing(6)
        self.chk_use_precolor = QCheckBox("Usar precolor")
        self.chk_use_precolor.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_use_precolor.setStyleSheet(f"""
            QCheckBox {{ color: {MA_TEXT_SEC}; font-size: 12px; spacing: 8px; {_MA_FF}
                background: transparent; border: none; }}
            QCheckBox:hover {{ color: {MA_TEXT_PRI}; }}
            QCheckBox::indicator {{
                width: 16px; height: 16px; border-radius: 4px;
                border: 1.5px solid {MA_BORDER}; background: {MA_INPUT};
            }}
            QCheckBox::indicator:hover {{ border-color: {MA_BORDER_HI}; }}
            QCheckBox::indicator:checked {{ background: {MA_RED}; border-color: {MA_RED}; }}
        """)
        self.chk_use_precolor.setChecked(bool(init_pre))
        self.chk_use_precolor.toggled.connect(self._on_precolor_toggle)
        self._pre_palette = ColorPaletteSelector(init_pre if init_pre else "#FFFFFF")
        self._pre_palette.setEnabled(bool(init_pre))
        pre_wrap_l.addWidget(self.chk_use_precolor)
        pre_wrap_l.addWidget(self._pre_palette)
        rep_sec.add_child(pre_wrap)

        rep_sec.add_child(_lbl("GRADOS / STRIPES"))
        self.inp_grados = QLineEdit()
        self.inp_grados.setPlaceholderText("0")
        self.inp_grados.setStyleSheet(MA_FIELD_QSS)
        if self.is_edit:
            self.inp_grados.setText(str(belt.get("grades") or 0))
        self.inp_grados.textChanged.connect(self._on_grados_changed)
        rep_sec.add_child(self.inp_grados)

        self._grade_color_wrap = QWidget()
        self._grade_color_wrap.setStyleSheet("background: transparent; border: none;")
        gcw_l = QVBoxLayout(self._grade_color_wrap)
        gcw_l.setContentsMargins(0, 0, 0, 0)
        gcw_l.setSpacing(4)
        gcw_l.addWidget(_lbl("COLOR DE GRADO"))
        init_grade = (belt.get("grade_color") or "#FFFFFF") if self.is_edit else "#FFFFFF"
        self._grade_palette = ColorPaletteSelector(init_grade)
        gcw_l.addWidget(self._grade_palette)
        rep_sec.add_child(self._grade_color_wrap)
        self._grade_color_wrap.setVisible(False)
        self._on_grados_changed(self.inp_grados.text())
        left_l.addWidget(rep_sec)

        self._has_age_restriction = bool(
            (belt.get("minimum_age") if self.is_edit else False)
            or (belt.get("maximum_age") if self.is_edit else False)
            or (belt.get("age_restriction_note") if self.is_edit else False)
        )

        age_sec = BeltFormSection("RESTRICCIONES DE EDAD")
        self.chk_age_restricted = QPushButton("Este nivel tiene restricciones de edad")
        self.chk_age_restricted.setCheckable(True)
        self.chk_age_restricted.setChecked(self._has_age_restriction)
        self.chk_age_restricted.setFixedHeight(32)
        self.chk_age_restricted.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_age_restricted.clicked.connect(self._toggle_age_fields)
        self.chk_age_restricted.setStyleSheet(f"QPushButton {{ background: {MA_INPUT}; color: {MA_TEXT_SEC}; border: 1px solid {MA_BORDER}; border-radius: 6px; font-size: 11px; font-weight: 600; {_MA_FF} padding: 0 12px; }} QPushButton:hover {{ color: {MA_TEXT_PRI}; border-color: {MA_BORDER_HI}; }}")
        if self._has_age_restriction:
            self.chk_age_restricted.setStyleSheet(f"QPushButton {{ background: rgba(5,46,22,0.5); color: {MA_GREEN}; border: 1px solid #166534; border-radius: 6px; font-size: 11px; font-weight: 800; {_MA_FF} padding: 0 12px; }} QPushButton:hover {{ background: rgba(5,46,22,0.8); }}")
        age_sec.add_child(self.chk_age_restricted)

        self._age_fields_widget = QWidget()
        self._age_fields_widget.setStyleSheet("background: transparent;")
        af_l = QVBoxLayout(self._age_fields_widget)
        af_l.setContentsMargins(0, 4, 0, 0)
        af_l.setSpacing(6)

        age_row = QHBoxLayout()
        age_row.setSpacing(10)
        min_col = QVBoxLayout()
        min_col.setSpacing(2)
        min_col.addWidget(_ma_field_label("EDAD MIN"))
        self.spin_min_age = QSpinBox()
        self.spin_min_age.setRange(0, 120)
        self.spin_min_age.setSpecialValueText("Sin limite")
        self.spin_min_age.setStyleSheet(MA_FIELD_QSS)
        if self.is_edit and belt.get("minimum_age") is not None:
            self.spin_min_age.setValue(belt["minimum_age"])
        else:
            self.spin_min_age.setValue(0)
        min_col.addWidget(self.spin_min_age)
        age_row.addLayout(min_col)

        max_col = QVBoxLayout()
        max_col.setSpacing(2)
        max_col.addWidget(_ma_field_label("EDAD MAX"))
        self.spin_max_age = QSpinBox()
        self.spin_max_age.setRange(0, 120)
        self.spin_max_age.setSpecialValueText("Sin limite")
        self.spin_max_age.setStyleSheet(MA_FIELD_QSS)
        if self.is_edit and belt.get("maximum_age") is not None:
            self.spin_max_age.setValue(belt["maximum_age"])
        else:
            self.spin_max_age.setValue(0)
        max_col.addWidget(self.spin_max_age)
        age_row.addLayout(max_col)

        af_l.addLayout(age_row)

        self.inp_age_note = QLineEdit()
        self.inp_age_note.setPlaceholderText("Nota opcional sobre la restriccion...")
        self.inp_age_note.setStyleSheet(MA_FIELD_QSS)
        if self.is_edit and belt.get("age_restriction_note"):
            self.inp_age_note.setText(belt["age_restriction_note"])
        af_l.addWidget(self.inp_age_note)

        self._age_error_label = QLabel("")
        self._age_error_label.setStyleSheet(f"color: {MA_RED}; font-size: 10px; {_MA_FF}")
        af_l.addWidget(self._age_error_label)

        age_sec.add_child(self._age_fields_widget)
        self._age_fields_widget.setVisible(self._has_age_restriction)
        left_l.addWidget(age_sec)

        state_sec = BeltFormSection("ESTADO DEL NIVEL")
        state_row = QHBoxLayout()
        state_row.setSpacing(10)
        self.chk_initial = LevelStateButton("Inicial", role="initial")
        if self.is_edit and belt.get("is_initial"):
            self.chk_initial.setChecked(True)
        state_row.addWidget(self.chk_initial)

        self.chk_final = LevelStateButton("Final", role="final")
        if self.is_edit and belt.get("is_final"):
            self.chk_final.setChecked(True)
        state_row.addWidget(self.chk_final)

        self.chk_active = LevelStateButton(
            "Activo", role="active",
            tooltip="Permite usar este nivel en nuevas asignaciones y ascensos.",
        )
        self.chk_active.setChecked(not self.is_edit or belt.get("is_active", True))
        state_row.addWidget(self.chk_active)

        state_row.addStretch()
        state_sec.add_layout(state_row)
        left_l.addWidget(state_sec)

        prev_sec = BeltFormSection("VISTA PREVIA")
        self._live_preview = create_progression_level_preview(
            {
                "color": init_color,
                "pre_color": init_pre if init_pre else None,
                "grades": 0,
                "grade_color": init_grade,
                "level_type": "shirt" if self._progression_system == "shirt" else "belt",
            },
            self._progression_system,
            width=170,
            height=28,
            martial_art_name=self.martial_art_name,
            parent=self,
        )
        prev_lay = QHBoxLayout()
        prev_lay.setContentsMargins(0, 0, 0, 0)
        prev_lay.setSpacing(0)
        prev_lay.addWidget(self._live_preview)
        prev_lay.addStretch()
        prev_sec.add_layout(prev_lay)
        left_l.addWidget(prev_sec)

        self._belt_palette.color_changed.connect(self._refresh_live_preview)
        self._pre_palette.color_changed.connect(self._refresh_live_preview)
        self._grade_palette.color_changed.connect(self._refresh_live_preview)
        self.chk_use_precolor.toggled.connect(self._refresh_live_preview)
        self.inp_grados.textChanged.connect(self._refresh_live_preview)
        self._refresh_live_preview()

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(f"color: {MA_RED}; font-size: 11px; {_MA_FF}")
        left_l.addWidget(self.lbl_error)

        self.btn_cancel = IconTextButton("", "Cancelar", height=38, variant="secondary")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_save = QPushButton("Guardar cambios" if self.is_edit else "+")
        self.btn_save.setObjectName("CreateLevelButton")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        if self.is_edit:
            self.btn_save.setFixedHeight(42)
            self.btn_save.setMinimumWidth(150)
            self.btn_save.setStyleSheet(f"""
                QPushButton#CreateLevelButton {{
                    background: {MA_RED}; color: #FFFFFF; border: none;
                    border-radius: 11px; font-size: 12px; font-weight: 700;
                    padding: 0 20px; {_MA_FF}
                }}
                QPushButton#CreateLevelButton:hover {{ background: #D90D32; }}
                QPushButton#CreateLevelButton:pressed {{ background: #B90A2A; }}
            """)
        else:
            self.btn_save.setFixedSize(52, 42)
            self.btn_save.setToolTip("Crear cinturón")
            self.btn_save.setAccessibleName("Crear cinturón")
            self.btn_save.setStyleSheet(f"""
                QPushButton#CreateLevelButton {{
                    background: {MA_RED}; color: #FFFFFF; border: none;
                    border-radius: 11px; font-size: 24px; font-weight: 600;
                    padding-bottom: 3px; {_MA_FF}
                }}
                QPushButton#CreateLevelButton:hover {{ background: #D90D32; }}
                QPushButton#CreateLevelButton:pressed {{ background: #B90A2A; }}
            """)
        self.btn_save.clicked.connect(self._save)
        self.inp_name.returnPressed.connect(self._save)
        self._add_footer_buttons(self.btn_cancel, self.btn_save)
        left_l.addStretch()

        right_col = QWidget()
        right_l = QVBoxLayout(right_col)
        right_l.setContentsMargins(8, 0, 0, 0)
        right_l.setSpacing(10)

        existing_sec = BeltFormSection("NIVELES EXISTENTES")
        self._progression_panel = ExistingProgressionPanel(
            martial_art_id, repo,
            editing_level_id=belt["id"] if belt else None,
            martial_art_name=self.martial_art_name,
            belt_preview_factory=self._create_existing_belt_preview,
        )
        existing_sec.add_child(self._progression_panel)
        right_l.addWidget(existing_sec)

        self._progression_panel.edit_level_requested.connect(self._edit_existing_level)
        self._progression_panel.delete_level_requested.connect(self._delete_existing_level)

        if not self.is_edit:
            next_order = repo.get_next_available_order(martial_art_id)
            self.inp_orden.setText(str(next_order))

        self.inp_orden.textChanged.connect(self._on_orden_changed)

        two_col.addWidget(left_col, 3)
        two_col.addWidget(right_col, 4)

        self._body_scroll = QScrollArea()
        self._body_scroll.setObjectName("BeltFormScroll")
        self._body_scroll.setWidgetResizable(True)
        self._body_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._body_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._body_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._body_scroll.setStyleSheet(_BELT_SCROLL_QSS)
        self._body_scroll.viewport().setAutoFillBackground(False)
        self._body_scroll.viewport().setStyleSheet(
            f"background-color: {MA_MODAL_BG}; border: none;"
        )

        self._belt_form_body = QWidget()
        self._belt_form_body.setObjectName("BeltFormBody")
        self._belt_form_body.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._belt_form_layout = QVBoxLayout(self._belt_form_body)
        self._belt_form_layout.setContentsMargins(24, 20, 24, 24)
        self._belt_form_layout.setSpacing(16)
        self._belt_form_layout.addLayout(two_col, 1)
        self._body_scroll.setWidget(self._belt_form_body)

        self._card_layout.setContentsMargins(0, 0, 0, 0)
        self._card_layout.setSpacing(0)
        self._card_layout.addWidget(self._body_scroll, 1)

    def _create_existing_belt_preview(self, belt: dict):
        return create_progression_level_preview(
            belt,
            self._progression_system,
            width=170,
            height=28,
            martial_art_name=self.martial_art_name,
            parent=self,
        )

    def _on_precolor_toggle(self, checked):
        self._pre_palette.setEnabled(bool(checked))

    def _on_grados_changed(self, text):
        try:
            grados = int(text.strip()) if text.strip() else 0
        except ValueError:
            grados = 0
        if hasattr(self, '_grade_color_wrap'):
            self._grade_color_wrap.setVisible(grados > 0)

    def _refresh_live_preview(self):
        if not hasattr(self, "_live_preview"):
            return
        pre = None
        if self.chk_use_precolor.isChecked():
            pre = self._pre_palette.color()
        try:
            grados = int(self.inp_grados.text().strip()) if self.inp_grados.text().strip() else 0
        except ValueError:
            grados = 0
        pv = self._live_preview
        if isinstance(pv, ShirtLevelPreview):
            pv.set_color(self._belt_palette.color() or "#FFFFFF")
        else:
            pv.color = self._belt_palette.color() or "#FFFFFF"
            pv.pre_color = pre
            pv.grades = grados
            pv.grade_color = self._grade_palette.color() or "#FFFFFF"
        pv.update()

    def _toggle_age_fields(self):
        checked = self.chk_age_restricted.isChecked()
        self._age_fields_widget.setVisible(checked)
        if checked:
            self.chk_age_restricted.setStyleSheet(f"QPushButton {{ background: rgba(5,46,22,0.5); color: {MA_GREEN}; border: 1px solid #166534; border-radius: 6px; font-size: 11px; font-weight: 800; {_MA_FF} padding: 0 12px; }} QPushButton:hover {{ background: rgba(5,46,22,0.8); }}")
        else:
            self.chk_age_restricted.setStyleSheet(f"QPushButton {{ background: {MA_INPUT}; color: {MA_TEXT_SEC}; border: 1px solid {MA_BORDER}; border-radius: 6px; font-size: 11px; font-weight: 600; {_MA_FF} padding: 0 12px; }} QPushButton:hover {{ color: {MA_TEXT_PRI}; border-color: {MA_BORDER_HI}; }}")

    def _on_orden_changed(self, text):
        try:
            orden = int(text.strip()) if text.strip() else None
        except ValueError:
            return
        if orden is None:
            return
        exclude = self.belt["id"] if self.is_edit else None
        available = self.repo.is_level_order_available(self.martial_art_id, orden, exclude)
        if not available:
            self.lbl_error.setText("Este orden ya esta ocupado por otro nivel.")
        else:
            self.lbl_error.setText("")
        self._progression_panel.set_proposed_order(orden)

    def _show_inline_error(self, message: str):
        self.lbl_error.setText(message)

    def _refresh_parent_view(self):
        parent = self.parent()
        while parent is not None:
            loader = getattr(parent, "_load_belts", None)
            if callable(loader):
                try:
                    loader()
                except Exception:
                    pass
                return
            parent = parent.parent()

    def _edit_existing_level(self, belt: dict):
        full_belt = self.repo.get_level(belt["id"])
        if not full_belt:
            self._show_inline_error("No se pudo cargar el nivel.")
            return
        dlg = BeltDialog(
            repo=self.repo,
            martial_art_id=self.martial_art_id,
            martial_art_name=self.martial_art_name,
            belt=full_belt,
            progression_system=self._progression_system,
            parent=self,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._progression_panel.refresh()
            self._refresh_parent_view()

    def _delete_existing_level(self, belt: dict):
        deps = self.repo.get_level_dependencies(belt["id"])
        if deps["students"] > 0:
            self._show_inline_error(
                "No se puede eliminar este nivel porque tiene estudiantes asignados."
            )
            return
        if deps["requirements"] or deps["promotion_rules"] or deps["initial_assignments"]:
            confirm = MartialArtConfirmDialog(
                title="Eliminar nivel",
                message=f"¿Quieres eliminar “{belt.get('name') or 'nivel'}”?",
                detail_text="Esta acción no se puede deshacer.",
                confirm_text="Eliminar",
                cancel_text="Cancelar",
                is_danger=True,
                parent=self,
            )
            if confirm.exec() != QDialog.DialogCode.Accepted:
                return
        try:
            self.repo.delete_belt(belt["id"])
        except Exception as e:
            self._show_inline_error(f"Error: {e}")
            return
        self._progression_panel.refresh()
        self._refresh_parent_view()

    def _save(self):
        name = self.inp_name.text().strip()
        if not name:
            self.lbl_error.setText("El nombre es obligatorio.")
            return
        try:
            orden = int(self.inp_orden.text().strip()) if self.inp_orden.text().strip() else None
        except ValueError:
            self.lbl_error.setText("El orden debe ser un numero.")
            return
        color = self._belt_palette.color() or None
        pre_color = (
            self._pre_palette.color()
            if self.chk_use_precolor.isChecked()
            else None
        )
        grade_color = self._grade_palette.color() or "#FFFFFF"

        if orden is not None:
            exclude = self.belt["id"] if self.is_edit else None
            if not self.repo.is_level_order_available(self.martial_art_id, orden, exclude):
                self.lbl_error.setText("Este orden ya esta ocupado por otro nivel.")
                return

        try:
            grados = int(self.inp_grados.text().strip()) if self.inp_grados.text().strip() else 0
            if _is_bjj(self.martial_art_name):
                grados = max(0, min(4, grados))
            else:
                grados = max(0, min(10, grados))
        except ValueError:
            self.lbl_error.setText("Grados debe ser un numero entre 0 y 10.")
            return

        min_age = None
        max_age = None
        age_note = None
        self._age_error_label.setText("")
        if self.chk_age_restricted.isChecked():
            min_age = self.spin_min_age.value() if self.spin_min_age.value() > 0 else None
            max_age = self.spin_max_age.value() if self.spin_max_age.value() > 0 else None
            if min_age is not None and min_age < 0:
                self._age_error_label.setText("La edad minima no puede ser negativa.")
                return
            if max_age is not None and max_age < 0:
                self._age_error_label.setText("La edad maxima no puede ser negativa.")
                return
            if min_age is not None and max_age is not None and min_age > max_age:
                self._age_error_label.setText("La edad maxima no puede ser menor que la edad minima.")
                return
            age_note = self.inp_age_note.text().strip() or None
            if age_note and len(age_note) > 250:
                self._age_error_label.setText("La nota no puede superar 250 caracteres.")
                return
        is_initial = self.chk_initial.isChecked()
        is_final = self.chk_final.isChecked()
        is_active = self.chk_active.isChecked()

        try:
            if self.is_edit:
                self.repo.update_belt(self.belt["id"], name, orden, color, pre_color,
                                      grados, grade_color, min_age, max_age, age_note,
                                      is_initial, is_final, is_active)
            else:
                self.repo.create_belt(self.martial_art_id, name, orden, color, pre_color,
                                      grados, grade_color, min_age, max_age, age_note,
                                      is_initial, is_final, is_active)
            self.accept()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")

    def _open_instructions(self):
        from views.martial_arts.martial_art_widgets import MartialArtInstructionsDialog
        dlg = MartialArtInstructionsDialog(self, initial_section="Crear y editar niveles")
        dlg.exec()


# ─── RequirementDialog ───────────────────────────────────────

_REQ_FOOTER_CANCEL_QSS = """
    QPushButton {
        background: #202020; color: #D4D4D8;
        border: 1px solid #343434; border-radius: 11px;
        font-size: 13px; font-weight: 600;
        font-family: 'Inter', 'Segoe UI', sans-serif; padding: 0 22px;
    }
    QPushButton:hover { background: #262626; color: #F4F4F5; }
    QPushButton:pressed { background: #1A1A1A; }
"""

_REQ_FOOTER_SAVE_QSS = """
    QPushButton {
        background: #D90D32; color: #FFFFFF; border: none; border-radius: 11px;
        font-size: 13px; font-weight: 700;
        font-family: 'Inter', 'Segoe UI', sans-serif; padding: 0 22px;
    }
    QPushButton:hover { background: #E0163B; }
    QPushButton:pressed { background: #B50B29; }
"""


class _RequirementDescriptionEdit(QTextEdit):
    """QTextEdit with a placeholder hint (QTextEdit has no native one)."""

    def __init__(self, placeholder: str, parent=None):
        super().__init__(parent)
        self._placeholder = placeholder
        self.setObjectName("RequirementDescriptionEdit")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.viewport().setAutoFillBackground(False)
        self.setStyleSheet("""
            QTextEdit#RequirementDescriptionEdit {
                background-color: #202020;
                color: #F4F4F5;
                border: 1px solid #343434;
                border-radius: 10px;
                padding: 10px 12px;
                font-size: 12px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                selection-background-color: #2563EB;
            }
            QTextEdit#RequirementDescriptionEdit:focus {
                border-color: #3B82F6;
            }
            QTextEdit#RequirementDescriptionEdit QScrollBar:horizontal {
                height: 0px;
                max-height: 0px;
                background: transparent;
                border: none;
            }
            QTextEdit#RequirementDescriptionEdit QScrollBar:vertical {
                width: 6px;
                margin: 7px 2px;
                background: transparent;
                border: none;
            }
            QTextEdit#RequirementDescriptionEdit QScrollBar::handle:vertical {
                background-color: #3A3A3A;
                border-radius: 3px;
                min-height: 24px;
            }
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.toPlainText() == "" and not self.hasFocus():
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setPen(QColor("#71717A"))
            font = QFont(self.font())
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(
                self.viewport().rect().adjusted(12, 10, -12, -10),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                self._placeholder,
            )
            painter.end()


class RequirementDialog(MartialArtFormDialog):
    def __init__(self, repo, belt_id, req=None, parent=None):
        self.repo = repo
        self.belt_id = belt_id
        self.req = req
        self.is_edit = req is not None
        title = "Editar Requisito" if self.is_edit else "Nuevo Requisito"
        super().__init__(760, 650, title, parent)
        self.setObjectName("RequirementDialog")
        self._card_layout.setContentsMargins(30, 20, 30, 18)
        self._card_layout.setSpacing(14)

        initial_color = "#3B82F6"
        if self.is_edit and req:
            initial_color = req.get("accent_color") or initial_color

        self.lbl_error = QLabel("")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setStyleSheet(f"""
            color: {MA_RED}; font-size: 11px; {_MA_FF}
            background: transparent; border: none;
            padding: 0; margin: 0;
        """)
        self._set_error("")

        self._card_layout.addWidget(_lbl("TIPO DE REQUISITO"))
        type_row = QHBoxLayout()
        type_row.setSpacing(8)
        self.cmb_type = QComboBox()
        self.cmb_type.setStyleSheet(MA_FIELD_QSS)
        type_row.addWidget(self.cmb_type, 1)
        self.btn_new_type = QPushButton("+ Nuevo tipo")
        self.btn_new_type.setFixedHeight(38)
        self.btn_new_type.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_type.setStyleSheet(f"QPushButton {{ background: {MA_CARD}; color: {MA_TEXT_SEC}; border: 1px solid {MA_BORDER}; border-radius: 8px; font-size: 12px; {_MA_FF} padding: 0 12px; }} QPushButton:hover {{ color: {MA_TEXT_PRI}; border-color: {MA_RED}; }}")
        self.btn_new_type.clicked.connect(self._open_new_type)
        type_row.addWidget(self.btn_new_type)
        self._card_layout.addLayout(type_row)

        self._card_layout.addWidget(_lbl("DESCRIPCIÓN DEL REQUISITO"))
        self.description_input = _RequirementDescriptionEdit(
            "Ej: Completar 20 clases y dominar kata Heian Shodan."
        )
        self.description_input.setFixedHeight(76)
        if self.is_edit and req:
            self.description_input.setPlainText(req["requirement"])
        self._card_layout.addWidget(self.description_input)

        self._card_layout.addWidget(self.lbl_error)

        self._card_layout.addWidget(_lbl("COLOR DE LA CARD"))
        self.color_selector = ColorPaletteSelector(initial_color)
        self._card_layout.addWidget(self.color_selector)

        self._card_layout.addWidget(_lbl("VISTA PREVIA"))
        self.preview_card = RequirementVisualCard(preview=True)
        self._card_layout.addWidget(self.preview_card)

        self._card_layout.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(42)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(_REQ_FOOTER_CANCEL_QSS)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Guardar cambios" if self.is_edit else "Agregar")
        btn_save.setFixedHeight(42)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(_REQ_FOOTER_SAVE_QSS)
        btn_save.clicked.connect(self._save)
        self._add_footer_buttons(btn_cancel, btn_save)

        self._load_types()
        self.cmb_type.currentIndexChanged.connect(self._refresh_preview)
        self.description_input.textChanged.connect(self._refresh_preview)
        self.description_input.textChanged.connect(lambda: self._set_error(""))
        self.color_selector.color_changed.connect(self._refresh_preview)
        self._refresh_preview()

    def _load_types(self):
        self.cmb_type.blockSignals(True)
        self.cmb_type.clear()
        self.cmb_type.addItem("Sin tipo", None)
        types = self.repo.get_requirement_types()
        if not types:
            self.cmb_type.setEnabled(False)
            self._set_error("No hay tipos de requisito. Crea uno con '+ Nuevo tipo'.")
        else:
            self.cmb_type.setEnabled(True)
            self._set_error("")
        for tid, tname in types:
            self.cmb_type.addItem(tname, tid)
        if self.is_edit and self.req and self.req.get("id_type"):
            for i in range(self.cmb_type.count()):
                if self.cmb_type.itemData(i) == self.req["id_type"]:
                    self.cmb_type.setCurrentIndex(i)
                    break
        self.cmb_type.blockSignals(False)

    def _open_new_type(self):
        saved_text = self.description_input.toPlainText()
        dlg = RequirementTypeDialog(self.repo, parent=self)
        dlg.type_created.connect(lambda name, nid: self._on_type_created(name, nid))
        dlg.exec()
        self.description_input.setPlainText(saved_text)
        self._load_types()

    def _on_type_created(self, name, nid):
        self._load_types()
        for i in range(self.cmb_type.count()):
            if self.cmb_type.itemData(i) == nid:
                self.cmb_type.setCurrentIndex(i)
                break

    def _refresh_preview(self):
        self.preview_card.set_type_name(self.cmb_type.currentText())
        self.preview_card.set_description(self.description_input.toPlainText())
        self.preview_card.set_accent_color(self.color_selector.color())

    def _set_error(self, text: str):
        """Show a red inline error, or hide the label entirely when empty."""
        text = (text or "").strip()
        self.lbl_error.setText(text)
        self.lbl_error.setVisible(bool(text))

    def _save(self):
        req_text = self.description_input.toPlainText().strip()
        if not req_text:
            self._set_error("La descripcion es obligatoria.")
            return
        tipo_id = self.cmb_type.currentData()
        accent_color = self.color_selector.color()
        try:
            if self.is_edit:
                self.repo.update_requirement(self.req["id"], req_text, tipo_id, accent_color)
            else:
                self.repo.create_requirement(self.belt_id, req_text, tipo_id, accent_color)
            self.accept()
        except Exception as e:
            self._set_error(f"Error: {e}")

    def keyPressEvent(self, event: QKeyEvent):
        if (
            event.key() == Qt.Key.Key_Return
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self._save()
        else:
            super().keyPressEvent(event)


# ─── PromoteStudentDialog ────────────────────────────────────

# ── QSS del formulario de ascenso ─────────────────────────────
_PROMO_SECTION_QSS = """
    QFrame#PromotionFormSection {
        background-color: #1A1A1A;
        border: 1px solid #303030;
        border-radius: 12px;
    }
"""
_PROMO_MARKER_QSS = """
    QLabel {
        background: #D90D32;
        color: #FFFFFF;
        border-radius: 14px;
        font-size: 12px;
        font-weight: 800;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
"""
_PROMO_SECTION_TITLE_QSS = """
    QLabel {
        color: #A1A1AA;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.8px;
        background: transparent;
        border: none;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
"""
_PROMO_COMBO_QSS = """
    QComboBox {
        background-color: #202020;
        border: 1px solid #343434;
        border-radius: 10px;
        padding: 0 12px;
        color: #F4F4F5;
        font-size: 12px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    QComboBox:hover { border-color: #4A4A4A; }
    QComboBox:focus { border-color: #C8102E; }
    QComboBox:disabled { color: #71717A; }
    QComboBox::drop-down { border: none; width: 30px; }
    QComboBox QAbstractItemView {
        background-color: #1D1D1D;
        border: 1px solid #353535;
        border-radius: 8px;
        color: #F4F4F5;
        selection-background-color: #292929;
        outline: none;
        padding: 4px;
        font-size: 12px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
"""
_PROMO_SEARCH_QSS = """
    QLineEdit {
        background-color: #202020;
        border: 1px solid #343434;
        border-radius: 10px;
        padding: 0 12px;
        color: #F4F4F5;
        font-size: 12px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    QLineEdit:focus { border-color: #C8102E; }
    QLineEdit:disabled { color: #71717A; }
    QLineEdit::placeholder { color: #71717A; }
"""
_PROMO_LIST_QSS = """
    QScrollArea {
        background-color: #202020;
        border: 1px solid #343434;
        border-radius: 10px;
    }
    QScrollArea > QWidget > QWidget { background: transparent; }
    QScrollBar:vertical {
        width: 7px;
        margin: 6px 3px;
        background: transparent;
        border: none;
    }
    QScrollBar::handle:vertical {
        background-color: #3A3A3A;
        border-radius: 3px;
        min-height: 30px;
    }
    QScrollBar::handle:vertical:hover { background-color: #505050; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
"""
_PROMO_SCROLL_QSS = """
    QScrollArea { background: transparent; border: none; }
    QScrollArea > QWidget > QWidget { background: transparent; }
    QScrollBar:vertical {
        width: 7px;
        margin: 6px 3px;
        background: transparent;
        border: none;
    }
    QScrollBar::handle:vertical {
        background-color: #3A3A3A;
        border-radius: 3px;
        min-height: 30px;
    }
    QScrollBar::handle:vertical:hover { background-color: #505050; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
"""
_PROMO_ERR_QSS = """
    background-color: rgba(200, 16, 46, 0.10);
    border: 1px solid rgba(200, 16, 46, 0.32);
    border-radius: 9px;
    color: #FB7185;
    padding: 10px 12px;
    font-size: 12px;
    font-family: 'Inter', 'Segoe UI', sans-serif;
"""
_PROMO_OK_QSS = """
    background-color: rgba(34, 197, 94, 0.08);
    border: 1px solid rgba(34, 197, 94, 0.24);
    border-radius: 9px;
    color: #4ADE80;
    padding: 10px 12px;
    font-size: 12px;
    font-family: 'Inter', 'Segoe UI', sans-serif;
"""
_PROMO_CANCEL_QSS = """
    QPushButton#PromotionCancelButton {
        background-color: #202020;
        color: #D4D4D8;
        border: 1px solid #343434;
        border-radius: 11px;
        font-size: 12px;
        font-weight: 700;
        padding: 0 20px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    QPushButton#PromotionCancelButton:hover {
        background-color: #292929;
        border-color: #4A4A4A;
        color: #FFFFFF;
    }
    QPushButton#PromotionCancelButton:pressed {
        background-color: #181818;
        border-color: #3F3F3F;
    }
"""
_PROMO_CONFIRM_QSS = """
    QPushButton#ConfirmPromotionButton {
        background-color: #D90D32;
        color: #FFFFFF;
        border: none;
        border-radius: 11px;
        font-size: 12px;
        font-weight: 800;
        padding: 0 22px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    QPushButton#ConfirmPromotionButton:hover { background-color: #EA1740; }
    QPushButton#ConfirmPromotionButton:pressed { background-color: #B90A2A; }
    QPushButton#ConfirmPromotionButton:disabled {
        background-color: #2A2A2A;
        color: #666666;
    }
"""


class PromoteStudentDialog(MartialArtFormDialog):
    def __init__(self, repo, parent=None):
        self.repo = repo
        super().__init__(720, 680, "Ascender estudiante", parent)
        self.setObjectName("PromoteStudentDialog")
        self.setMinimumSize(660, 580)

        self._header_row.setContentsMargins(22, 0, 14, 0)
        self._header_row.setSpacing(10)
        self._close_btn.setFixedSize(32, 32)
        self._close_btn.setToolTip("Cerrar")
        self._header_frame.setFixedHeight(64)
        self._title_lbl.setStyleSheet(
            "color: #F4F4F5; font-size: 18px; font-weight: 800; "
            "background: transparent; border: none; "
            "font-family: 'Inter', 'Segoe UI', sans-serif;"
        )
        self._header_row.setStretch(0, 1)

        self._sel_ma = None
        self._sel_instructor = None
        self._sel_student = None
        self._sel_belt = None
        self._selected_martial_art_name = ""
        self._progression_enabled = True

        self._build_ui()
        self._load_martial_arts()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(_PROMO_SCROLL_QSS)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.viewport().setAutoFillBackground(False)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        root = QVBoxLayout(container)
        root.setContentsMargins(24, 20, 24, 24)
        root.setSpacing(18)

        # ── 1. DISCIPLINA ───────────────────────────────────────
        sec_discipline, lay_discipline = self._promotion_section("1", "DISCIPLINA")
        self.cmb_ma = QComboBox()
        self.cmb_ma.setMinimumHeight(46)
        self.cmb_ma.setStyleSheet(_PROMO_COMBO_QSS)
        self.cmb_ma.currentIndexChanged.connect(self._on_ma_changed)
        lay_discipline.addWidget(self.cmb_ma)

        self.discipline_info_row = QWidget()
        self.discipline_info_row.setStyleSheet("background: transparent; border: none;")
        dhl = QHBoxLayout(self.discipline_info_row)
        dhl.setContentsMargins(2, 0, 0, 0)
        dhl.setSpacing(10)
        self._discipline_icon = MartialArtIcon("karate-nuevo", size=28, color=MA_RED)
        dhl.addWidget(self._discipline_icon)
        dcol = QVBoxLayout()
        dcol.setSpacing(2)
        self.lbl_discipline_name = QLabel("")
        self.lbl_discipline_name.setStyleSheet("color: #F4F4F5; font-size: 13px; font-weight: 700; background: transparent; border: none; font-family: 'Inter', 'Segoe UI', sans-serif;")
        self.lbl_discipline_system = QLabel("")
        self.lbl_discipline_system.setStyleSheet("color: #A1A1AA; font-size: 11px; background: transparent; border: none; font-family: 'Inter', 'Segoe UI', sans-serif;")
        dcol.addWidget(self.lbl_discipline_name)
        dcol.addWidget(self.lbl_discipline_system)
        dhl.addLayout(dcol, 1)
        self.discipline_info_row.setVisible(False)
        lay_discipline.addWidget(self.discipline_info_row)
        root.addWidget(sec_discipline)

        # ── 2. INSTRUCTOR ───────────────────────────────────────
        sec_instructor, lay_instructor = self._promotion_section("2", "INSTRUCTOR CON PERMISO DE ASCENSO")
        self.cmb_instructor = QComboBox()
        self.cmb_instructor.setMinimumHeight(46)
        self.cmb_instructor.setStyleSheet(_PROMO_COMBO_QSS)
        self.cmb_instructor.setEnabled(False)
        self.cmb_instructor.currentIndexChanged.connect(self._on_instructor_changed)
        lay_instructor.addWidget(self.cmb_instructor)

        self.lbl_no_instructors = QLabel("No hay instructores con permiso para ascender.")
        self.lbl_no_instructors.setWordWrap(True)
        self.lbl_no_instructors.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.04);
            border: 1px solid #2E2E2E;
            border-radius: 8px;
            color: #A1A1AA;
            padding: 8px 12px;
            font-size: 11px;
            font-family: 'Inter', 'Segoe UI', sans-serif;
        """)
        self.lbl_no_instructors.setVisible(False)
        lay_instructor.addWidget(self.lbl_no_instructors)
        root.addWidget(sec_instructor)

        # ── 3. ESTUDIANTE ───────────────────────────────────────
        sec_student, lay_student = self._promotion_section("3", "ESTUDIANTE")
        self.search_student = QLineEdit()
        self.search_student.setPlaceholderText("Filtrar por nombre...")
        self.search_student.setMinimumHeight(46)
        self.search_student.setStyleSheet(_PROMO_SEARCH_QSS)
        self.search_student.setEnabled(False)
        self.search_student.textChanged.connect(self._filter_students)
        lay_student.addWidget(self.search_student)

        self.student_scroll = QScrollArea()
        self.student_scroll.setWidgetResizable(True)
        self.student_scroll.setMinimumHeight(150)
        self.student_scroll.setMaximumHeight(230)
        self.student_scroll.setEnabled(False)
        self.student_scroll.setStyleSheet(_PROMO_LIST_QSS)
        self.student_container = QWidget()
        self.student_container.setStyleSheet("background: transparent;")
        self.student_vbox = QVBoxLayout(self.student_container)
        self.student_vbox.setContentsMargins(4, 6, 4, 6)
        self.student_vbox.setSpacing(2)
        self.student_scroll.setWidget(self.student_container)
        lay_student.addWidget(self.student_scroll)
        root.addWidget(sec_student)

        # ── 4. CINTURÓN DESTINO ─────────────────────────────────
        sec_belt, lay_belt = self._promotion_section("4", "CINTURÓN DESTINO")
        self.cmb_belt = QComboBox()
        self.cmb_belt.setMinimumHeight(46)
        self.cmb_belt.setStyleSheet(_PROMO_COMBO_QSS)
        self.cmb_belt.setEnabled(False)
        self.cmb_belt.currentIndexChanged.connect(self._on_belt_changed)
        lay_belt.addWidget(self.cmb_belt)

        self._destination_preview_layout = QHBoxLayout()
        self._destination_preview_layout.setContentsMargins(2, 0, 0, 0)
        self._destination_preview_layout.setSpacing(14)
        self._destination_belt_preview = None
        self._destination_empty_lbl = None

        dest_info_col = QVBoxLayout()
        dest_info_col.setSpacing(4)
        self.lbl_destination_name = QLabel("")
        self.lbl_destination_name.setStyleSheet("color: #F4F4F5; font-size: 13px; font-weight: 700; background: transparent; border: none; font-family: 'Inter', 'Segoe UI', sans-serif;")
        self._destination_badges_lay = QHBoxLayout()
        self._destination_badges_lay.setSpacing(6)
        self._destination_badges_lay.addStretch()
        dest_info_col.addWidget(self.lbl_destination_name)
        dest_info_col.addLayout(self._destination_badges_lay)
        dest_info_col.addStretch()
        self._destination_preview_layout.addLayout(dest_info_col, 1)
        lay_belt.addLayout(self._destination_preview_layout)

        self.lbl_destination_age = QLabel("")
        self.lbl_destination_age.setStyleSheet("color: #A1A1AA; font-size: 11px; background: transparent; border: none; font-family: 'Inter', 'Segoe UI', sans-serif;")
        lay_belt.addWidget(self.lbl_destination_age)

        self.lbl_validation = QLabel("")
        self.lbl_validation.setWordWrap(True)
        self.lbl_validation.hide()
        lay_belt.addWidget(self.lbl_validation)
        root.addWidget(sec_belt)

        root.addStretch()
        scroll.setWidget(container)
        self._card_layout.addWidget(scroll)

        # ── Footer ──────────────────────────────────────────────
        self._footer_frame.setFixedHeight(64)
        self._footer_lay.setContentsMargins(26, 0, 26, 0)
        self._footer_lay.setSpacing(12)

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setObjectName("PromotionCancelButton")
        self.btn_cancel.setFixedHeight(42)
        self.btn_cancel.setMinimumWidth(112)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet(_PROMO_CANCEL_QSS)
        self.btn_cancel.clicked.connect(self.reject)
        self._footer_lay.addWidget(self.btn_cancel)

        self._footer_lay.addStretch()

        self.btn_confirm = QPushButton("Confirmar")
        self.btn_confirm.setObjectName("ConfirmPromotionButton")
        self.btn_confirm.setFixedHeight(42)
        self.btn_confirm.setMinimumWidth(132)
        self.btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirm.setStyleSheet(_PROMO_CONFIRM_QSS)
        self.btn_confirm.setEnabled(False)
        self.btn_confirm.clicked.connect(self._do_promote)
        self._footer_lay.addWidget(self.btn_confirm)

    def _promotion_section(self, number: str, title: str):
        card = QFrame()
        card.setObjectName("PromotionFormSection")
        card.setStyleSheet(_PROMO_SECTION_QSS)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 14, 16, 16)
        lay.setSpacing(10)

        head = QHBoxLayout()
        head.setContentsMargins(0, 0, 0, 0)
        head.setSpacing(10)
        marker = QLabel(number)
        marker.setFixedSize(28, 28)
        marker.setAlignment(Qt.AlignmentFlag.AlignCenter)
        marker.setStyleSheet(_PROMO_MARKER_QSS)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(_PROMO_SECTION_TITLE_QSS)
        head.addWidget(marker)
        head.addWidget(title_lbl)
        head.addStretch()
        lay.addLayout(head)
        return card, lay

    def _make_badge(self, text: str, color: str) -> QLabel:
        badge = QLabel(text)
        badge.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                color: {color};
                border: 1px solid {color};
                border-radius: 4px;
                padding: 1px 6px;
                font-size: 9px;
                font-weight: 800;
                letter-spacing: 0.5px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}
        """)
        return badge

    def _make_student_row(self, s: dict) -> QWidget:
        row = QWidget()
        row.setFixedHeight(44)
        row.setCursor(Qt.CursorShape.PointingHandCursor)
        self._style_student_row(row, False)

        hl = QHBoxLayout(row)
        hl.setContentsMargins(12, 0, 12, 0)
        hl.setSpacing(10)

        lbl_name = QLabel(s["nombre"])
        lbl_name.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 13px; background: transparent; border: none; {_MA_FF}")

        belt_w = QWidget()
        belt_w.setStyleSheet("background: transparent; border: none;")
        belt_hl = QHBoxLayout(belt_w)
        belt_hl.setContentsMargins(0, 0, 0, 0)
        belt_hl.setSpacing(6)

        bar = QFrame()
        bar.setFixedSize(28, 14)
        color = s["belt_color"]
        border_c = "#999" if color.upper() in {"#FFFFFF", "#FFD700", "#FF8C00", "#FFFF00", "#FFA500", "#FFFACD"} else color
        bar.setStyleSheet(f"QFrame {{ background: {color}; border-radius: 3px; border: 1.5px solid {border_c}; }}")

        lbl_belt = QLabel(s["belt_name"])
        lbl_belt.setStyleSheet(f"color: {MA_TEXT_SEC}; font-size: 11px; background: transparent; border: none; {_MA_FF}")

        belt_hl.addWidget(bar)
        belt_hl.addWidget(lbl_belt)

        hl.addWidget(lbl_name, 1)
        hl.addWidget(belt_w)
        row.mousePressEvent = lambda e, r=row, st=s: self._select_student(r, st)
        return row

    def _style_student_row(self, row: QWidget, selected: bool):
        if selected:
            row.setStyleSheet("QWidget { background-color: rgba(200, 16, 46, 0.12); border-radius: 6px; border-left: 3px solid #C8102E; }")
        else:
            row.setStyleSheet("QWidget { background: transparent; border-radius: 6px; border: none; } QWidget:hover { background: #202020; }")

    def _load_martial_arts(self):
        self.cmb_ma.blockSignals(True)
        self.cmb_ma.clear()
        self.cmb_ma.addItem("Seleccionar arte marcial...", None)
        for ma in self.repo.get_martial_arts():
            self.cmb_ma.addItem(ma['name'], ma)
        self.cmb_ma.blockSignals(False)

    def _update_discipline_info(self):
        if self._sel_ma:
            systems = {"belt": "Cinturones", "shirt": "Camisas", "bracelet": "Brazaletes",
                       "level": "Niveles", "custom": "Personalizado", "none": "Sin progresion"}
            ps = self._sel_ma.get("progression_system", "belt")
            self.lbl_discipline_name.setText(self._sel_ma.get("name") or "")
            self.lbl_discipline_system.setText(f"Sistema de progresión: {systems.get(ps, ps)}")
            icon_key = self._sel_ma.get("icon_key")
            if icon_key:
                self._discipline_icon.set_icon(icon_key)
            self.discipline_info_row.setVisible(True)
        else:
            self.discipline_info_row.setVisible(False)

    def _on_ma_changed(self, idx):
        self._sel_ma = self.cmb_ma.itemData(idx)
        self._sel_instructor = None
        self._sel_student = None
        self._sel_belt = None
        self._selected_martial_art_name = self._sel_ma["name"] if self._sel_ma else ""
        self._update_discipline_info()
        self._reset_from_step(2)

        if not self._sel_ma:
            return

        settings = self.repo.get_martial_art(self._sel_ma["id"])
        self._progression_enabled = settings.get("progression_enabled", True) if settings else True

        instructors = self.repo.get_instructors_that_can_promote(self._sel_ma["id"])
        self.cmb_instructor.blockSignals(True)
        self.cmb_instructor.clear()
        self.cmb_instructor.addItem("Seleccionar instructor...", None)

        if instructors:
            for ins in instructors:
                self.cmb_instructor.addItem(ins['nombre'], ins)
            self.cmb_instructor.setEnabled(True)
            self.lbl_no_instructors.setVisible(False)
        else:
            self.cmb_instructor.setEnabled(False)
            self.lbl_no_instructors.setVisible(True)

        self.cmb_instructor.blockSignals(False)

    def _on_instructor_changed(self, idx):
        self._sel_instructor = self.cmb_instructor.itemData(idx)
        self._sel_student = None
        self._sel_belt = None
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
            if item.widget():
                item.widget().deleteLater()

        if not students:
            lbl = QLabel("Sin estudiantes en este arte marcial")
            lbl.setStyleSheet(f"color: {MA_TEXT_MUT}; font-size: 12px; font-style: italic; padding: 10px 14px; {_MA_FF}")
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
        self._sel_belt = None
        self._load_belts_for_student(s)

    def _load_belts_for_student(self, s: dict):
        self.cmb_belt.blockSignals(True)
        self.cmb_belt.clear()
        self.cmb_belt.addItem("Seleccionar cinturon...", None)

        if self._progression_enabled:
            allowed = self.repo.get_allowed_promotion_levels(self._sel_ma["id"], s.get("belt_id") or None)
        else:
            allowed = []

        if allowed:
            for b in allowed:
                self.cmb_belt.addItem(b['name'], b)
            self.cmb_belt.setEnabled(True)
        else:
            if not self._progression_enabled:
                self.cmb_belt.addItem("Progresion no habilitada", None)
            else:
                self.cmb_belt.addItem("No hay cinturones superiores", None)
            self.cmb_belt.setEnabled(False)

        self.cmb_belt.blockSignals(False)
        self._sel_belt = None
        self._refresh_destination_preview()
        self._update_destination_info(None)
        self._update_validation_message()
        self._update_confirm_state()

    def _on_belt_changed(self, idx):
        self._sel_belt = self.cmb_belt.itemData(idx)
        self._refresh_destination_preview()
        self._update_destination_info(self._sel_belt)
        self._update_validation_message()
        self._update_confirm_state()

    def _selected_destination(self):
        return self._sel_belt

    @property
    def _selected_instructor_id(self):
        return self._sel_instructor["id"] if self._sel_instructor else None

    @property
    def _selected_student_id(self):
        return self._sel_student["id"] if self._sel_student else None

    @property
    def _selected_destination_id(self):
        return self._sel_belt["id"] if self._sel_belt else None

    def _clear_destination_preview(self):
        if self._destination_belt_preview is not None:
            self._destination_preview_layout.removeWidget(self._destination_belt_preview)
            self._destination_belt_preview.deleteLater()
            self._destination_belt_preview = None
        if self._destination_empty_lbl is not None:
            self._destination_preview_layout.removeWidget(self._destination_empty_lbl)
            self._destination_empty_lbl.deleteLater()
            self._destination_empty_lbl = None

    def _show_destination_empty_state(self):
        lbl = QLabel("Selecciona un nivel de destino.")
        lbl.setStyleSheet("color: #71717A; font-size: 12px; background: transparent; border: none; font-family: 'Inter', 'Segoe UI', sans-serif;")
        self._destination_empty_lbl = lbl
        self._destination_preview_layout.addWidget(
            lbl,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )

    def _refresh_destination_preview(self):
        destination = self._selected_destination()

        self._clear_destination_preview()

        if not destination:
            self._show_destination_empty_state()
            return

        preview = create_progression_level_preview(
            destination,
            self._sel_ma.get("progression_system", "belt") if self._sel_ma else "belt",
            width=140,
            height=24,
            martial_art_name=self._selected_martial_art_name,
            parent=self,
        )

        self._destination_preview_layout.addWidget(
            preview,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )

        self._destination_belt_preview = preview

    def _clear_badges(self):
        while self._destination_badges_lay.count():
            item = self._destination_badges_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _update_destination_info(self, destination):
        self._clear_badges()
        if not destination:
            self.lbl_destination_name.setText("")
            self.lbl_destination_age.hide()
            self._destination_badges_lay.addStretch()
            return

        self.lbl_destination_name.setText(destination.get("display_name") or destination.get("name") or "")
        if destination.get("is_initial"):
            self._destination_badges_lay.addWidget(self._make_badge("INICIAL", "#3B82F6"))
        if destination.get("is_final"):
            self._destination_badges_lay.addWidget(self._make_badge("FINAL", "#FACC15"))
        self._destination_badges_lay.addStretch()

        min_age = destination.get("minimum_age")
        max_age = destination.get("maximum_age")
        note = destination.get("age_restriction_note")
        if min_age is None and max_age is None:
            age_text = "Sin restricción de edad"
        elif min_age is not None and max_age is not None:
            age_text = f"Edad permitida: {min_age} a {max_age} años"
        elif min_age is not None:
            age_text = f"Edad mínima: {min_age} años"
        else:
            age_text = f"Edad máxima: {max_age} años"
        if note:
            age_text = f"{age_text} · {note}"
        self.lbl_destination_age.setText(age_text)
        self.lbl_destination_age.show()

    def _update_validation_message(self):
        if not all([self._selected_instructor_id, self._selected_student_id, self._selected_destination_id]):
            self.lbl_validation.hide()
            return

        promotion_ok, promotion_message = self.repo.validate_promotion(
            self._selected_student_id,
            self._sel_ma["id"],
            self._selected_destination_id,
        )
        age_ok, age_message = self.repo.validate_level_age(
            self._selected_student_id,
            self._selected_destination_id,
        )

        if promotion_ok and age_ok:
            self.lbl_validation.setStyleSheet(_PROMO_OK_QSS)
            self.lbl_validation.setText("Ascenso válido.")
        else:
            message = promotion_message if not promotion_ok else age_message
            self.lbl_validation.setStyleSheet(_PROMO_ERR_QSS)
            self.lbl_validation.setText(message)
        self.lbl_validation.show()

    def _update_confirm_state(self):
        ready = all([
            self._selected_instructor_id,
            self._selected_student_id,
            self._selected_destination_id,
        ])

        if ready:
            promotion_ok, promotion_message = self.repo.validate_promotion(
                self._selected_student_id,
                self._sel_ma["id"],
                self._selected_destination_id,
            )

            age_ok, age_message = self.repo.validate_level_age(
                self._selected_student_id,
                self._selected_destination_id,
            )

            ready = promotion_ok and age_ok

        self.btn_confirm.setEnabled(ready)

    def _show_validation_error(self, message: str):
        self.lbl_validation.setStyleSheet(_PROMO_ERR_QSS)
        self.lbl_validation.setText(message)
        self.lbl_validation.show()

    def _reset_from_step(self, step: int):
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
                if item.widget():
                    item.widget().deleteLater()
        if step <= 4:
            self.cmb_belt.clear()
            self.cmb_belt.setEnabled(False)
            self._sel_belt = None
            self._refresh_destination_preview()
            self._update_destination_info(None)
        self._update_validation_message()
        self._update_confirm_state()

    def _do_promote(self):
        self.lbl_validation.hide()
        if not all([self._selected_instructor_id, self._selected_student_id, self._selected_destination_id]):
            self._show_validation_error("Completa todos los pasos antes de confirmar.")
            return

        if self._progression_enabled:
            ok, msg = self.repo.validate_promotion(
                self._selected_student_id,
                self._sel_ma["id"],
                self._selected_destination_id,
            )
            if not ok:
                self._show_validation_error(msg)
                return

            age_ok, age_msg = self.repo.validate_level_age(
                self._selected_student_id,
                self._selected_destination_id,
            )
            if not age_ok:
                self._show_validation_error(age_msg)
                return

        self.btn_confirm.setEnabled(False)
        self.btn_confirm.setText("Procesando...")

        try:
            self.repo.promote_student(
                student_id=self._selected_student_id,
                belt_id=self._selected_destination_id,
                instructor_id=self._selected_instructor_id,
                martial_art_id=self._sel_ma["id"],
            )
            self.accept()
        except Exception as e:
            self._show_validation_error(f"Error: {e}")
            self.btn_confirm.setText("Confirmar")
            self._update_confirm_state()


# ─── BeltsView ─────────────────────────────────────────────────
class BeltsView(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = BeltsRepository()

        self.selected_martial_art = None
        self.selected_belt = None

        self._blur_effect = None
        self._blur_target_widget = None
        self._martial_art_items = []
        self._current_cols = 0

        self._build_ui()
        self._animate_enter()
        self._load_initial_data()

    def _blur_target(self):
        win = self.window()
        if hasattr(win, "centralWidget") and win.centralWidget():
            return win.centralWidget()
        return win

    def _blur_on(self):
        target = self._blur_target()
        if self._blur_effect:
            return
        self._blur_target_widget = target
        self._blur_effect = QGraphicsBlurEffect(target)
        self._blur_effect.setBlurRadius(0)
        target.setGraphicsEffect(self._blur_effect)
        self._blur_anim = QPropertyAnimation(self._blur_effect, b"blurRadius", self)
        self._blur_anim.setDuration(220)
        self._blur_anim.setStartValue(0)
        self._blur_anim.setEndValue(14)
        self._blur_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._blur_anim.start()

    def _blur_off(self):
        if not self._blur_effect:
            return
        target = self._blur_target_widget
        self._blur_anim_out = QPropertyAnimation(self._blur_effect, b"blurRadius", self)
        self._blur_anim_out.setDuration(180)
        self._blur_anim_out.setStartValue(self._blur_effect.blurRadius())
        self._blur_anim_out.setEndValue(0)
        self._blur_anim_out.setEasingCurve(QEasingCurve.Type.InCubic)

        def cleanup():
            if target:
                target.setGraphicsEffect(None)
            self._blur_effect = None
            self._blur_target_widget = None

        self._blur_anim_out.finished.connect(cleanup)
        self._blur_anim_out.start()

    def _fade_widget(self, widget):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", widget)
        anim.setDuration(300)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(lambda: widget.setGraphicsEffect(None))
        anim.start()

    def _animate_enter(self):
        for w, d in [(self._header, 0), (self._grid_section, 60), (self._detail_panel, 120)]:
            effect = QGraphicsOpacityEffect(w)
            w.setGraphicsEffect(effect)
            effect.setOpacity(0)
            anim = QPropertyAnimation(effect, b"opacity", self)
            anim.setDuration(400)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.finished.connect(lambda w=w: w.setGraphicsEffect(None))
            QTimer.singleShot(d, anim.start)

    # ══════════════════════════════════════════════════════════════
    #  BUILD UI (TOP-DOWN DASHBOARD STRUCTURE)
    # ══════════════════════════════════════════════════════════════
    def _build_ui(self):
        self.setObjectName("MartialArtsPage")
        self.setStyleSheet(f"QWidget#MartialArtsPage {{ background-color: {MA_BG}; border: none; }}")

        self.main_stack = QStackedWidget()
        self.main_stack.setObjectName("BeltsMainStack")

        page0 = QWidget()
        page0.setStyleSheet(f"background-color: {MA_BG};")

        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        main_scroll.setObjectName("DisciplineMainScroll")
        main_scroll.setStyleSheet(f"""
            QScrollArea#DisciplineMainScroll {{
                border: none;
                background: transparent;
            }}
            QScrollArea#DisciplineMainScroll > QWidget > QWidget {{
                background: transparent;
            }}
        """)
        main_scroll.setFrameShape(QFrame.Shape.NoFrame)
        main_scroll.viewport().setAutoFillBackground(False)
        main_scroll.viewport().setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        outer = QVBoxLayout(scroll_content)
        outer.setContentsMargins(32, 32, 32, 32)
        outer.setSpacing(24)

        # --- 1. HEADER ---
        self._build_header(outer)

        # --- 2. GRID SECTION (DISCIPLINES) ---
        self._build_grid_section(outer)

        # --- 3. DETAIL PANEL (SPLIT VIEW) ---
        self._build_detail_panel(outer)

        outer.addStretch()

        main_scroll.setWidget(scroll_content)

        page0_layout = QVBoxLayout(page0)
        page0_layout.setContentsMargins(0, 0, 0, 0)
        page0_layout.setSpacing(0)
        page0_layout.addWidget(main_scroll)

        self.settings_container = QWidget()
        self.settings_container.setObjectName("DisciplineSettingsContainer")
        self.settings_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.settings_container.setStyleSheet(f"background-color: {MA_BG}; border: none;")
        self.settings_layout = QVBoxLayout(self.settings_container)
        self.settings_layout.setContentsMargins(0, 0, 0, 0)
        self.settings_layout.setSpacing(0)
        self.main_stack.addWidget(page0)
        self.main_stack.addWidget(self.settings_container)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self.main_stack)

    def _build_header(self, parent_layout):
        self._header = QFrame()
        self._header.setObjectName("PageHeader")
        self._header.setStyleSheet(f"QFrame#PageHeader {{ background: transparent; border-bottom: 1px solid {MA_BORDER}; }}")
        
        hl = QHBoxLayout(self._header)
        hl.setContentsMargins(0, 0, 0, 24)
        hl.setSpacing(16)

        left = QHBoxLayout()
        left.setSpacing(14)
        left.setContentsMargins(0, 0, 0, 0)

        icon_container = QFrame()
        icon_container.setObjectName("DisciplinePageHeaderIcon")
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet("QWidget#DisciplinePageHeaderIcon { background: transparent; border: none; }")
        icon_lay = QHBoxLayout(icon_container)
        icon_lay.setContentsMargins(0, 0, 0, 0)
        icon_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._page_header_icon = MartialArtIcon("karate-nuevo", size=40, color=MA_RED)
        icon_lay.addWidget(self._page_header_icon)
        left.addWidget(icon_container)

        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        eyebrow = QLabel("DISCIPLINAS")
        eyebrow.setStyleSheet(f"color: {MA_RED}; font-size: 10px; font-weight: 800; letter-spacing: 1.5px; {_MA_FF} background: transparent; border: none;")
        title_col.addWidget(eyebrow)
        title = QLabel("Gestión de disciplinas")
        title.setStyleSheet(f"color: #F4F4F5; font-size: 24px; font-weight: 900; {_MA_FF} background: transparent; border: none;")
        title_col.addWidget(title)
        subtitle = QLabel("Administra sistemas de progresión, ejercicios y requisitos.")
        subtitle.setStyleSheet(f"color: {MA_TEXT_MUT}; font-size: 13px; font-weight: 500; {_MA_FF} background: transparent; border: none;")
        title_col.addWidget(subtitle)
        left.addLayout(title_col)

        hl.addLayout(left, 1)

        right = QHBoxLayout()
        right.setSpacing(12)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Buscar disciplina...")
        self._search_input.setFixedHeight(40)
        self._search_input.setMinimumWidth(260)
        self._search_input.setStyleSheet(f"""
            QLineEdit {{ background: {MA_INPUT}; color: {MA_TEXT_PRI}; border: 1px solid {MA_BORDER}; border-radius: 10px; padding: 0 16px; font-size: 13px; {_MA_FF} }}
            QLineEdit:focus {{ border-color: {MA_BORDER_HI}; }}
        """)
        self._search_input.textChanged.connect(self._filter_cards)
        right.addWidget(self._search_input)

        btn_new = QPushButton("+ Nueva Disciplina")
        btn_new.setFixedHeight(40)
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.setStyleSheet(f"""
            QPushButton {{ background-color: {MA_RED}; color: white; border: none; border-radius: 10px; font-size: 13px; font-weight: 700; {_MA_FF} padding: 0 20px; }}
            QPushButton:hover {{ background-color: {MA_RED_H}; }}
        """)
        btn_new.clicked.connect(self._open_create_martial_art)
        right.addWidget(btn_new)

        hl.addLayout(right)
        parent_layout.addWidget(self._header)

    def _build_grid_section(self, parent_layout):
        self._grid_section = QFrame()
        self._grid_section.setStyleSheet("background: transparent; border: none;")
        
        vl = QVBoxLayout(self._grid_section)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(16)

        # Section Title
        self._grid_title = QLabel("DISCIPLINAS DISPONIBLES")
        self._grid_title.setStyleSheet(f"color: {MA_TEXT_MUT}; font-size: 11px; font-weight: 800; letter-spacing: 1.2px; {_MA_FF} background: transparent; border: none;")
        vl.addWidget(self._grid_title)

        # Grid Container
        self._grid_container = QWidget()
        self._grid_container.setStyleSheet("background: transparent;")
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        self._grid_layout.setSpacing(16)
        vl.addWidget(self._grid_container)

        self._grid_empty = MartialArtsEmptyState(
            "generic-martial-art", "Sin disciplinas",
            "Crea tu primera disciplina para comenzar a gestionar niveles y requisitos.",
            "Crear disciplina", self._open_create_martial_art,
        )
        self._grid_empty.setVisible(False)
        vl.addWidget(self._grid_empty)

        parent_layout.addWidget(self._grid_section)

    def _build_detail_panel(self, parent_layout):
        self._detail_panel = QFrame()
        self._detail_panel.setObjectName("DetailPanel")
        self._detail_panel.setStyleSheet(f"""
            QFrame#DetailPanel {{
                background-color: {MA_SURFACE};
                border: 1px solid {MA_BORDER};
                border-radius: 20px;
            }}
        """)
        _ma_shadow(self._detail_panel, blur=30, offset_y=10, alpha=150)
        self._detail_panel.setVisible(False)
        self._detail_panel.setMinimumHeight(620)
        self._detail_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)

        outer_vl = QVBoxLayout(self._detail_panel)
        outer_vl.setContentsMargins(0, 0, 0, 0)
        outer_vl.setSpacing(0)

        detail_scroll = QScrollArea()
        detail_scroll.setObjectName("DisciplineDetailScroll")
        detail_scroll.setWidgetResizable(True)
        detail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        detail_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        detail_scroll.setFrameShape(QFrame.Shape.NoFrame)
        detail_scroll.viewport().setAutoFillBackground(False)
        detail_scroll.viewport().setStyleSheet("background: transparent; border: none;")
        detail_scroll.setStyleSheet(f"""
            QScrollArea#DisciplineDetailScroll {{ border: none; background: transparent; }}
            QScrollArea#DisciplineDetailScroll > QWidget > QWidget {{ background: transparent; }}
            QScrollBar:vertical {{ background: transparent; width: 7px; border: none; margin: 3px 1px; }}
            QScrollBar::handle:vertical {{ background-color: #303030; border-radius: 3px; min-height: 32px; }}
            QScrollBar::handle:vertical:hover {{ background-color: #464646; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; background: transparent; border: none; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
        """)

        detail_scroll_w = QWidget()
        detail_scroll_w.setStyleSheet("background: transparent;")
        vl = QVBoxLayout(detail_scroll_w)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)

        # --- Detail Header ---
        header_frame = QFrame()
        header_frame.setStyleSheet(f"QFrame {{ background: transparent; border-bottom: 1px solid {MA_BORDER}; border-top-left-radius: 20px; border-top-right-radius: 20px; }}")
        hl = QHBoxLayout(header_frame)
        hl.setContentsMargins(32, 24, 32, 24)
        hl.setSpacing(16)

        self._detail_icon_box = QFrame()
        self._detail_icon_box.setObjectName("SelectedDisciplineIconBox")
        self._detail_icon_box.setFixedSize(58, 58)
        self._detail_icon_box.setStyleSheet(f"""
            QFrame#SelectedDisciplineIconBox {{
                background-color: rgba(200, 16, 46, 0.12);
                border: 1px solid rgba(232, 21, 47, 0.32);
                border-radius: 15px;
            }}
        """)
        icon_lay = QHBoxLayout(self._detail_icon_box)
        icon_lay.setContentsMargins(0, 0, 0, 0)
        icon_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._detail_icon = MartialArtIcon("generic-martial-art", size=32, color=MA_RED)
        self._detail_icon.setObjectName("SelectedDisciplineIcon")
        icon_lay.addWidget(self._detail_icon)
        hl.addWidget(self._detail_icon_box)

        info_col = QVBoxLayout()
        info_col.setSpacing(4)
        self._detail_name = QLabel("")
        self._detail_name.setStyleSheet(f"color: #F4F4F5; font-size: 20px; font-weight: 800; {_MA_FF} background: transparent; border: none;")
        info_col.addWidget(self._detail_name)

        self._detail_badges_row = QHBoxLayout()
        self._detail_badges_row.setSpacing(8)
        self._detail_badges_row.setContentsMargins(0, 0, 0, 0)
        info_col.addLayout(self._detail_badges_row)

        hl.addLayout(info_col, 1)

        btn_row_header = QHBoxLayout()
        btn_row_header.setSpacing(10)

        self._btn_promote_student = IconTextButton(
            "insignia", "Ascender estudiante",
            icon_size=17, icon_color="#FFFFFF", height=40, variant="primary",
        )
        self._btn_promote_student.setMinimumWidth(190)
        self._btn_promote_student.setToolTip("Ascender o asignar nivel a un estudiante")
        self._btn_promote_student.clicked.connect(self._open_promote_student)
        btn_row_header.addStretch(1)
        btn_row_header.addWidget(self._btn_promote_student, 0)

        self._sel_config_btn = IconTextButton(
            "ajustes", "Configurar",
            icon_size=16, icon_color="#D4D4D8", height=40, variant="secondary",
        )
        self._sel_config_btn.setMinimumWidth(144)
        self._sel_config_btn.setToolTip("Configurar disciplina")
        self._sel_config_btn.setEnabled(False)
        self._sel_config_btn.setStyleSheet(
            self._sel_config_btn.styleSheet() + """
                QPushButton#IconTextButton {
                    padding-left: 16px;
                    padding-right: 18px;
                    text-align: center;
                }
            """
        )
        self._sel_config_btn.clicked.connect(self._open_settings_from_header)
        btn_row_header.addWidget(self._sel_config_btn, 0)

        hl.addLayout(btn_row_header)
        vl.addWidget(header_frame)
        vl.addSpacing(10)

        # --- Tab Bar ---
        self._tab_bar = QFrame()
        self._tab_bar.setStyleSheet(f"QFrame {{ background: transparent; border-bottom: 1px solid {MA_BORDER}; }}")
        tab_lay = QHBoxLayout(self._tab_bar)
        tab_lay.setContentsMargins(32, 0, 32, 0)
        tab_lay.setSpacing(0)

        self._tab_levels = QPushButton("Niveles")
        self._tab_levels.setCheckable(True)
        self._tab_levels.setChecked(True)
        self._tab_levels.setFixedHeight(42)
        self._tab_levels.setCursor(Qt.CursorShape.PointingHandCursor)
        self._tab_reqs = QPushButton("Requisitos")
        self._tab_reqs.setCheckable(True)
        self._tab_reqs.setFixedHeight(42)
        self._tab_reqs.setCursor(Qt.CursorShape.PointingHandCursor)
        self._tab_desc = QPushButton("Descripcion")
        self._tab_desc.setCheckable(True)
        self._tab_desc.setFixedHeight(42)
        self._tab_desc.setCursor(Qt.CursorShape.PointingHandCursor)
        self._tab_exercises = QPushButton("Ejercicios")
        self._tab_exercises.setCheckable(True)
        self._tab_exercises.setFixedHeight(42)
        self._tab_exercises.setCursor(Qt.CursorShape.PointingHandCursor)

        for tb in [self._tab_levels, self._tab_reqs, self._tab_desc, self._tab_exercises]:
            tb.setStyleSheet(f"""
                QPushButton {{ background: transparent; color: {MA_TEXT_MUT}; border: none; border-bottom: 2px solid transparent;
                    font-size: 12px; font-weight: 700; {_MA_FF} padding: 0 16px; }}
                QPushButton:checked {{ color: {MA_TEXT_PRI}; border-bottom: 2px solid {MA_RED}; }}
                QPushButton:hover {{ color: {MA_TEXT_SEC}; }}
            """)

        self._tab_levels.clicked.connect(lambda: self._switch_tab("levels"))
        self._tab_reqs.clicked.connect(lambda: self._switch_tab("requirements"))
        self._tab_desc.clicked.connect(lambda: self._switch_tab("description"))
        self._tab_exercises.clicked.connect(lambda: self._switch_tab("exercises"))

        tab_lay.addWidget(self._tab_levels)
        tab_lay.addWidget(self._tab_reqs)
        tab_lay.addWidget(self._tab_desc)
        tab_lay.addWidget(self._tab_exercises)
        tab_lay.addStretch()
        vl.addWidget(self._tab_bar)

        # --- Content Stack ---
        self._content_stack = QStackedWidget()
        self._content_stack.setObjectName("DetailContentStack")

        # Levels page
        self._levels_page = QWidget()
        self._levels_page.setStyleSheet("background: transparent;")
        levels_layout = QVBoxLayout(self._levels_page)
        levels_layout.setContentsMargins(24, 20, 24, 20)
        levels_layout.setSpacing(16)

        belts_header = QHBoxLayout()
        belts_header.setSpacing(0)
        b_title = QLabel("Niveles de Progresion")
        b_title.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 14px; font-weight: 700; {_MA_FF} background: transparent; border: none;")
        belts_header.addWidget(b_title)
        belts_header.addStretch()

        self._btn_new_belt = QPushButton("+ Anadir Nivel")
        self._btn_new_belt.setFixedHeight(32)
        self._btn_new_belt.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_new_belt.setStyleSheet(f"""
            QPushButton {{ background: rgba(255,255,255,0.05); color: {MA_TEXT_SEC}; border: 1px dashed {MA_BORDER_HI}; border-radius: 8px; font-size: 11px; font-weight: 600; {_MA_FF} padding: 0 12px; }}
            QPushButton:hover {{ border-color: {MA_RED}; color: {MA_RED_H}; }}
        """)
        self._btn_new_belt.clicked.connect(self._open_create_belt)
        belts_header.addWidget(self._btn_new_belt)
        levels_layout.addLayout(belts_header)

        self._belts_scroll = QScrollArea()
        self._belts_scroll.setWidgetResizable(True)
        self._belts_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._belts_scroll.setStyleSheet(MA_SCROLL_QSS)
        belts_container = QWidget()
        belts_container.setStyleSheet("background: transparent;")
        self._timeline_list_layout = QVBoxLayout(belts_container)
        self._timeline_list_layout.setContentsMargins(0, 0, 0, 0)
        self._timeline_list_layout.setSpacing(8)
        self._timeline_list_layout.addStretch()
        self._belts_scroll.setWidget(belts_container)
        levels_layout.addWidget(self._belts_scroll)

        self._levels_empty = MartialArtsEmptyState(
            "generic-martial-art", "Sin niveles configurados",
            "Agrega niveles de progresion para esta disciplina.",
            "Crear nivel", self._open_create_belt,
        )
        self._levels_empty.setVisible(False)
        levels_layout.addWidget(self._levels_empty)

        self._content_stack.addWidget(self._levels_page)

        # Requirements page
        self._requirements_page = QWidget()
        self._requirements_page.setStyleSheet("background: transparent;")
        reqs_layout = QVBoxLayout(self._requirements_page)
        reqs_layout.setContentsMargins(24, 20, 24, 20)
        reqs_layout.setSpacing(16)

        reqs_header = QHBoxLayout()
        reqs_header.setSpacing(0)
        self._reqs_title = QLabel("Requisitos")
        self._reqs_title.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 14px; font-weight: 700; {_MA_FF} background: transparent; border: none;")
        reqs_header.addWidget(self._reqs_title)
        reqs_header.addStretch()

        self._btn_new_req = QPushButton("+ Crear Requisito")
        self._btn_new_req.setFixedHeight(32)
        self._btn_new_req.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_new_req.setStyleSheet(f"""
            QPushButton {{ background: rgba(255,255,255,0.05); color: {MA_TEXT_SEC}; border: 1px dashed {MA_BORDER_HI}; border-radius: 8px; font-size: 11px; font-weight: 600; {_MA_FF} padding: 0 12px; }}
            QPushButton:hover {{ border-color: {MA_RED}; color: {MA_RED_H}; }}
        """)
        self._btn_new_req.clicked.connect(self._open_create_requirement)
        reqs_header.addWidget(self._btn_new_req)
        reqs_layout.addLayout(reqs_header)

        self._reqs_scroll = QScrollArea()
        self._reqs_scroll.setWidgetResizable(True)
        self._reqs_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._reqs_scroll.setStyleSheet(MA_SCROLL_QSS)
        req_container = QWidget()
        req_container.setStyleSheet("background: transparent;")
        self._req_list_layout = QVBoxLayout(req_container)
        self._req_list_layout.setContentsMargins(0, 0, 0, 0)
        self._req_list_layout.setSpacing(12)
        self._req_list_layout.addStretch()
        self._reqs_scroll.setWidget(req_container)
        reqs_layout.addWidget(self._reqs_scroll)

        self._reqs_empty = MartialArtsEmptyState(
            "generic-martial-art", "No existen requisitos configurados",
            "Agrega condiciones de tiempo, tecnica, asistencia o conducta para los ascensos.",
            "Crear requisito", self._open_create_requirement,
        )
        self._reqs_empty.setVisible(False)
        reqs_layout.addWidget(self._reqs_empty)

        self._content_stack.addWidget(self._requirements_page)

        # Description page
        self._description_page = QWidget()
        self._description_page.setStyleSheet("background: transparent;")
        desc_layout = QVBoxLayout(self._description_page)
        desc_layout.setContentsMargins(24, 20, 24, 20)
        desc_layout.setSpacing(16)

        desc_title = QLabel("Descripcion de la disciplina")
        desc_title.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 14px; font-weight: 700; {_MA_FF} background: transparent; border: none;")
        desc_layout.addWidget(desc_title)

        self._desc_about_card = QFrame()
        self._desc_about_card.setStyleSheet(f"QFrame {{ background: {MA_CARD}; border: 1px solid {MA_BORDER}; border-radius: 12px; }} QFrame * {{ background: transparent; border: none; }}")
        about_vl = QVBoxLayout(self._desc_about_card)
        about_vl.setContentsMargins(16, 14, 16, 14)
        about_vl.setSpacing(6)
        about_lbl = QLabel("Acerca de la disciplina")
        about_lbl.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 13px; font-weight: 700; {_MA_FF}")
        about_vl.addWidget(about_lbl)
        self._desc_about_text = QLabel("Todavia no se ha agregado una descripcion para esta disciplina.")
        self._desc_about_text.setWordWrap(True)
        self._desc_about_text.setStyleSheet(f"color: {MA_TEXT_SEC}; font-size: 12px; {_MA_FF}")
        about_vl.addWidget(self._desc_about_text)
        desc_layout.addWidget(self._desc_about_card)

        self._desc_focus_card = QFrame()
        self._desc_focus_card.setStyleSheet(f"QFrame {{ background: {MA_CARD}; border: 1px solid {MA_BORDER}; border-radius: 12px; }} QFrame * {{ background: transparent; border: none; }}")
        focus_vl = QVBoxLayout(self._desc_focus_card)
        focus_vl.setContentsMargins(16, 14, 16, 14)
        focus_vl.setSpacing(6)
        focus_lbl = QLabel("Que se trabaja")
        focus_lbl.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 13px; font-weight: 700; {_MA_FF}")
        focus_vl.addWidget(focus_lbl)
        self._desc_focus_text = QLabel("Aun no se ha definido el enfoque de entrenamiento.")
        self._desc_focus_text.setWordWrap(True)
        self._desc_focus_text.setStyleSheet(f"color: {MA_TEXT_SEC}; font-size: 12px; {_MA_FF}")
        focus_vl.addWidget(self._desc_focus_text)
        desc_layout.addWidget(self._desc_focus_card)

        self._desc_summary_card = QFrame()
        self._desc_summary_card.setStyleSheet(f"QFrame {{ background: {MA_CARD}; border: 1px solid {MA_BORDER}; border-radius: 12px; }} QFrame * {{ background: transparent; border: none; }}")
        sum_vl = QVBoxLayout(self._desc_summary_card)
        sum_vl.setContentsMargins(16, 14, 16, 14)
        sum_vl.setSpacing(6)
        sum_lbl = QLabel("Resumen operativo")
        sum_lbl.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 13px; font-weight: 700; {_MA_FF}")
        sum_vl.addWidget(sum_lbl)
        self._desc_summary_text = QLabel("")
        self._desc_summary_text.setWordWrap(True)
        self._desc_summary_text.setStyleSheet(f"color: {MA_TEXT_SEC}; font-size: 12px; {_MA_FF}")
        sum_vl.addWidget(self._desc_summary_text)
        desc_layout.addWidget(self._desc_summary_card)

        desc_layout.addStretch()
        self._content_stack.addWidget(self._description_page)

        # Exercises page
        self._exercises_page = QWidget()
        self._exercises_page.setStyleSheet("background: transparent;")
        ex_layout = QVBoxLayout(self._exercises_page)
        ex_layout.setContentsMargins(24, 20, 24, 20)
        ex_layout.setSpacing(16)

        ex_header = QHBoxLayout()
        ex_header.setSpacing(0)
        ex_title_col = QVBoxLayout()
        ex_title_col.setSpacing(2)
        ex_title = QLabel("Ejercicios de la disciplina")
        ex_title.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 14px; font-weight: 700; {_MA_FF} background: transparent; border: none;")
        ex_title_col.addWidget(ex_title)
        self._ex_subtitle = QLabel("")
        self._ex_subtitle.setStyleSheet(f"color: {MA_TEXT_MUT}; font-size: 11px; {_MA_FF} background: transparent; border: none;")
        ex_title_col.addWidget(self._ex_subtitle)
        ex_header.addLayout(ex_title_col, 1)

        self._btn_new_exercise = QPushButton("+ Nuevo ejercicio")
        self._btn_new_exercise.setFixedHeight(32)
        self._btn_new_exercise.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_new_exercise.setStyleSheet(f"""
            QPushButton {{ background: rgba(255,255,255,0.05); color: {MA_TEXT_SEC}; border: 1px dashed {MA_BORDER_HI}; border-radius: 8px; font-size: 11px; font-weight: 600; {_MA_FF} padding: 0 12px; }}
            QPushButton:hover {{ border-color: {MA_RED}; color: {MA_RED_H}; }}
        """)
        self._btn_new_exercise.clicked.connect(self._open_create_exercise)
        ex_header.addWidget(self._btn_new_exercise)
        ex_layout.addLayout(ex_header)

        self._exercises_scroll = QScrollArea()
        self._exercises_scroll.setWidgetResizable(True)
        self._exercises_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._exercises_scroll.setStyleSheet(MA_SCROLL_QSS)
        ex_container = QWidget()
        ex_container.setStyleSheet("background: transparent;")
        self._exercises_list_layout = QVBoxLayout(ex_container)
        self._exercises_list_layout.setContentsMargins(0, 0, 0, 0)
        self._exercises_list_layout.setSpacing(10)
        self._exercises_list_layout.addStretch()
        self._exercises_scroll.setWidget(ex_container)
        ex_layout.addWidget(self._exercises_scroll)

        self._exercises_empty = MartialArtsEmptyState(
            "ejercicio", "No hay ejercicios configurados",
            "Agrega los ejercicios o actividades que pueden encontrarse en esta disciplina.",
            "Crear primer ejercicio", self._open_create_exercise,
        )
        self._exercises_empty.setVisible(False)
        ex_layout.addWidget(self._exercises_empty)

        self._content_stack.addWidget(self._exercises_page)

        vl.addWidget(self._content_stack, 1)

        detail_scroll.setWidget(detail_scroll_w)
        outer_vl.addWidget(detail_scroll)
        parent_layout.addWidget(self._detail_panel)

    # ══════════════════════════════════════════════════════════════
    #  RESPONSIVE GRID
    # ══════════════════════════════════════════════════════════════
    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._rebuild_grid)

    def _rebuild_grid(self):
        w = self._grid_container.width()
        if w <= 0:
            return
        
        if w >= CARD_MIN_WIDTH * 4 + 48:
            cols = 4
        elif w >= CARD_MIN_WIDTH * 3 + 32:
            cols = 3
        elif w >= CARD_MIN_WIDTH * 2 + 16:
            cols = 2
        else:
            cols = 1
            
        if cols == self._current_cols:
            return
        self._current_cols = cols
        self._apply_grid_layout()

    def _apply_grid_layout(self):
        while self._grid_layout.count():
            self._grid_layout.takeAt(0)
        for idx, item in enumerate(self._martial_art_items):
            if item.isVisible():
                row = idx // self._current_cols
                col = idx % self._current_cols
                self._grid_layout.addWidget(item, row, col)

    # ══════════════════════════════════════════════════════════════
    #  DATA LOADING & FILTERING
    # ══════════════════════════════════════════════════════════════
    def _load_initial_data(self):
        self._load_martial_arts()

    def _load_martial_arts(self):
        self._clear_ma_items()
        arts = self.repo.get_martial_arts()
        for ma in arts:
            item = MartialArtItem(ma)
            item.clicked.connect(self._select_martial_art)
            item.edit_clicked.connect(self._open_edit_martial_art)
            item.delete_clicked.connect(self._delete_martial_art)
            item.settings_clicked.connect(self._open_settings_from_item)
            self._martial_art_items.append(item)
            self._grid_layout.addWidget(item)

        self._current_cols = 0
        QTimer.singleShot(50, self._rebuild_grid)

        if arts:
            self._select_martial_art(arts[0])
        else:
            self.selected_martial_art = None
            self._detail_panel.setVisible(False)
            self._sel_config_btn.setEnabled(False)
            self._grid_empty.setVisible(True)

    def _clear_ma_items(self):
        for item in self._martial_art_items:
            item.setParent(None)
            item.deleteLater()
        self._martial_art_items.clear()
        while self._grid_layout.count():
            self._grid_layout.takeAt(0)

    def _filter_cards(self):
        query = self._search_input.text().strip().lower()
        arts = self.repo.get_martial_arts()
        visible = [ma for ma in arts if not query or query in (ma.get("name") or "").lower()]

        visible_ids = {ma["id"] for ma in visible}
        for item in self._martial_art_items:
            item.setVisible(item.martial_art["id"] in visible_ids)

        if not visible:
            self._grid_empty.setVisible(True)
        else:
            self._grid_empty.setVisible(False)

    def _select_martial_art(self, martial_art):
        self.selected_martial_art = martial_art
        
        # Paint selection
        for item in self._martial_art_items:
            is_sel = item.martial_art.get("id") == martial_art.get("id")
            item.set_selected(is_sel)

        self._show_detail_panel(martial_art)
        pe = bool(martial_art.get("progression_enabled", True))
        if pe:
            self._load_belts()
            self._load_requirements()
        else:
            self._clear_belt_items()
            self._clear_req_items()
            self._clear_exercises_list()

    def _show_detail_panel(self, ma):
        was_visible = self._detail_panel.isVisible()
        self._detail_panel.setVisible(True)
        self._sel_config_btn.setEnabled(True)

        if not was_visible:
            effect = QGraphicsOpacityEffect(self._detail_panel)
            self._detail_panel.setGraphicsEffect(effect)
            anim = QPropertyAnimation(effect, b"opacity", self)
            anim.setDuration(300)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.finished.connect(lambda: self._detail_panel.setGraphicsEffect(None))
            anim.start()

        pe = bool(ma.get("progression_enabled", True))
        ps = ma.get("progression_system") or "belt"
        accent = valid_hex_color(ma.get("accent_color"), MA_RED)
        icon_key = ma.get("icon_key") or "generic-martial-art"
        active = normalize_active_state(ma.get("is_active"))

        self._detail_icon.set_icon(icon_key)
        self._detail_icon.set_color(accent)
        self._detail_name.setText(ma["name"])

        # Clear badges
        for i in reversed(range(self._detail_badges_row.count())):
            w = self._detail_badges_row.takeAt(i).widget()
            if w:
                w.deleteLater()

        systems = {"belt": "Cinturones", "sash": "Fajas", "shirt": "Camisas",
                   "bracelet": "Brazaletes", "level": "Niveles", "grade": "Grados",
                   "custom": "Personalizado", "none": "Sin sistema"}
        
        _b1_bg     = "#052E16" if active else "#1A1A1A"
        _b1_color  = MA_GREEN  if active else MA_TEXT_MUT
        _b1_border = "#166534" if active else MA_BORDER
        _b1_text   = "ACTIVA"  if active else "INACTIVA"
        b1 = QLabel(_b1_text)
        b1.setStyleSheet(f"background: {_b1_bg}; color: {_b1_color}; border: 1px solid {_b1_border}; border-radius: 6px; padding: 4px 8px; font-size: 9px; font-weight: 800; {_MA_FF}")
        self._detail_badges_row.addWidget(b1)

        if pe:
            b2 = QLabel(systems.get(ps, ps).upper())
            b2.setStyleSheet(f"background: #0C1A4E; color: {MA_BLUE}; border: 1px solid #0C1A4E; border-radius: 6px; padding: 4px 8px; font-size: 9px; font-weight: 800; {_MA_FF}")
            self._detail_badges_row.addWidget(b2)
        else:
            b2 = QLabel("SIN PROGRESION")
            b2.setStyleSheet(f"background: #1A1A1A; color: {MA_TEXT_MUT}; border: 1px solid {MA_BORDER}; border-radius: 6px; padding: 4px 8px; font-size: 9px; font-weight: 800; {_MA_FF}")
            self._detail_badges_row.addWidget(b2)
            
        self._detail_badges_row.addStretch()

        self._configure_detail_mode(ma)

    def _configure_detail_mode(self, ma):
        pe = bool(ma.get("progression_enabled", True))
        active = normalize_active_state(ma.get("is_active"))

        self._tab_levels.setVisible(pe)
        self._tab_reqs.setVisible(pe)
        self._tab_desc.setVisible(not pe)
        self._tab_exercises.setVisible(not pe)
        self._btn_new_belt.setVisible(pe)
        self._btn_new_req.setVisible(pe)
        self._btn_new_exercise.setVisible(not pe)

        self._btn_promote_student.setVisible(pe)
        self._btn_promote_student.setEnabled(pe and active)
        if not active:
            self._btn_promote_student.setToolTip("La disciplina esta inactiva.")
        elif not pe:
            self._btn_promote_student.setToolTip("")
        else:
            self._btn_promote_student.setToolTip("")

        if pe:
            self._switch_tab("levels")
        else:
            self._switch_tab("description")

    def _switch_tab(self, tab_name):
        all_tabs = [self._tab_levels, self._tab_reqs, self._tab_desc, self._tab_exercises]
        for tb in all_tabs:
            tb.setChecked(False)

        if tab_name == "levels":
            self._tab_levels.setChecked(True)
            self._content_stack.setCurrentWidget(self._levels_page)
        elif tab_name == "requirements":
            self._tab_reqs.setChecked(True)
            self._content_stack.setCurrentWidget(self._requirements_page)
        elif tab_name == "description":
            self._tab_desc.setChecked(True)
            self._content_stack.setCurrentWidget(self._description_page)
            self._load_description_page()
        elif tab_name == "exercises":
            self._tab_exercises.setChecked(True)
            self._content_stack.setCurrentWidget(self._exercises_page)
            self._load_exercises_page()

    def _load_description_page(self):
        ma = self.selected_martial_art
        if not ma:
            return
        desc = ma.get("description") or ""
        focus = ma.get("training_focus") or ""
        active = normalize_active_state(ma.get("is_active"))
        pe = bool(ma.get("progression_enabled", True))
        ps = ma.get("progression_system") or "belt"

        if desc:
            self._desc_about_text.setText(desc)
            self._desc_about_text.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 12px; {_MA_FF}")
        else:
            self._desc_about_text.setText("Todavia no se ha agregado una descripcion para esta disciplina.")
            self._desc_about_text.setStyleSheet(f"color: {MA_TEXT_SEC}; font-size: 12px; font-style: italic; {_MA_FF}")

        if focus:
            self._desc_focus_text.setText(focus)
            self._desc_focus_text.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 12px; {_MA_FF}")
        else:
            self._desc_focus_text.setText("Aun no se ha definido el enfoque de entrenamiento.")
            self._desc_focus_text.setStyleSheet(f"color: {MA_TEXT_SEC}; font-size: 12px; font-style: italic; {_MA_FF}")

        try:
            summary = self.repo.get_discipline_summary(ma["id"])
            systems = {"belt": "Cinturones", "sash": "Fajas", "shirt": "Camisas",
                       "bracelet": "Brazaletes", "level": "Niveles", "grade": "Grados",
                       "custom": "Personalizado", "none": "No utiliza progresion"}
            sys_text = systems.get(ps, ps) if pe else "No utiliza progresion"
            status_text = "Activa" if active else "Inactiva"
            lines = [
                f"Estado: {status_text}",
                f"Horarios activos: {summary.get('active_schedule_count', 0)}",
                f"Ejercicios: {summary.get('exercise_count', 0)}",
                f"Sistema de progresion: {sys_text}",
            ]
            self._desc_summary_text.setText("\n".join(lines))
        except Exception:
            self._desc_summary_text.setText("No se pudo cargar el resumen.")

    def _load_exercises_page(self):
        ma = self.selected_martial_art
        if not ma:
            return

        name = ma.get("name") or "esta disciplina"
        self._ex_subtitle.setText(f"Actividades que pueden encontrarse en las clases de {name}.")

        self._clear_exercises_list()
        try:
            exercises = self.repo.get_discipline_exercises(ma["id"])
        except Exception:
            exercises = []

        self._exercises_empty.setVisible(not exercises)
        for ex in exercises:
            card = DisciplineExerciseCard(ex)
            card.edit_clicked.connect(self._open_edit_exercise)
            card.delete_clicked.connect(self._delete_exercise)
            self._exercises_list_layout.insertWidget(
                self._exercises_list_layout.count() - 1, card
            )

    def _clear_exercises_list(self):
        while self._exercises_list_layout.count() > 1:
            item = self._exercises_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _open_create_exercise(self):
        if not self.selected_martial_art:
            return
        self._blur_on()
        try:
            dlg = DisciplineExerciseDialog(
                self.repo, self.selected_martial_art["id"], parent=self
            )
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self._load_exercises_page()
        finally:
            self._blur_off()

    def _open_edit_exercise(self, exercise):
        self._blur_on()
        try:
            dlg = DisciplineExerciseDialog(
                self.repo, exercise["martial_art_id"], exercise=exercise, parent=self
            )
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self._load_exercises_page()
        finally:
            self._blur_off()

    def _delete_exercise(self, exercise):
        dlg = MartialArtConfirmDialog(
            title="Confirmar eliminacion",
            message=f"Eliminar ejercicio '{exercise.get('name', '')}'?",
            confirm_text="Eliminar", is_danger=True, parent=self,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            try:
                self.repo.delete_discipline_exercise(exercise["id"])
                self._load_exercises_page()
            except Exception as e:
                err = MartialArtConfirmDialog(title="Error", message=str(e), confirm_text="Cerrar", parent=self)
                err.exec()

    def _open_settings_from_item(self, martial_art):
        self.open_settings_view(martial_art["id"])

    # ── Belts ───────────────────────────────────────────────────
    def _load_belts(self):
        self._clear_belt_items()
        if not self.selected_martial_art:
            return

        ma = self.selected_martial_art
        pe = ma.get("progression_enabled", True)
        ma_name = ma["name"]

        if not pe:
            self._levels_empty.set_message(
                "Sin sistema de progresión",
                "Esta disciplina no tiene niveles configurados.\n"
                "La sección de especificaciones estará disponible próximamente.",
                action_label=None,
            )
            self._levels_empty.setVisible(True)
            self._btn_new_belt.setVisible(False)
            return

        self._btn_new_belt.setVisible(True)
        belts = self.repo.get_belts(ma["id"])
        if not belts:
            self._levels_empty.set_message(
                "Sin niveles configurados",
                "Agrega niveles de progresion para esta disciplina.",
                action_label="Crear nivel",
            )
        self._levels_empty.setVisible(not belts)

        progression_system = str(ma.get("progression_system") or "belt").strip().lower()
        for idx, belt in enumerate(belts, 1):
            item = TimelineBeltItem(
                belt,
                idx,
                martial_art_name=ma_name,
                progression_system=progression_system,
            )
            item.clicked.connect(self._select_belt)
            item.edit_clicked.connect(self._open_edit_belt)
            item.delete_clicked.connect(self._delete_belt)
            self._timeline_list_layout.insertWidget(self._timeline_list_layout.count() - 1, item)

        if belts:
            self._select_belt(belts[0])

    def _clear_belt_items(self):
        self.selected_belt = None
        while self._timeline_list_layout.count() > 1:
            item = self._timeline_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _select_belt(self, belt):
        self.selected_belt = belt
        self._paint_belts_timeline()
        self._load_requirements()

    def _paint_belts_timeline(self):
        for i in range(self._timeline_list_layout.count()):
            w = self._timeline_list_layout.itemAt(i)
            if w and w.widget() and isinstance(w.widget(), TimelineBeltItem):
                tl_item = w.widget()
                is_sel = tl_item.belt.get("id") == (self.selected_belt or {}).get("id")
                tl_item.set_selected(is_sel)

    # ── Requirements ─────────────────────────────────────────────
    def _load_requirements(self):
        self._clear_req_items()
        if not self.selected_belt:
            self._reqs_title.setText("Requisitos")
            return

        self._reqs_title.setText(f"Requisitos: {self.selected_belt['name']}")
        reqs = self.repo.get_requirements(self.selected_belt["id"])
        self._reqs_empty.setVisible(not reqs)

        for req in reqs:
            card = RequirementCard(req)
            card.edit_clicked.connect(self._open_edit_requirement)
            card.delete_clicked.connect(self._delete_requirement)
            self._req_list_layout.insertWidget(self._req_list_layout.count() - 1, card)

    def _clear_req_items(self):
        while self._req_list_layout.count() > 1:
            item = self._req_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ══════════════════════════════════════════════════════════════
    #  SETTINGS
    # ══════════════════════════════════════════════════════════════
    def _open_settings_from_header(self):
        if not self.selected_martial_art:
            return
        self.open_settings_view(self.selected_martial_art["id"])

    def _clear_settings_container(self):
        while self.settings_layout.count():
            item = self.settings_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()
        self._settings_view = None

    def _create_settings_loading_state(self):
        w = QWidget()
        w.setStyleSheet(f"background: {MA_BG};")
        vl = QVBoxLayout(w)
        vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.setSpacing(16)
        ico = MartialArtIcon("ajustes-deslizadores", size=48, color=MA_TEXT_MUT)
        ico.setStyleSheet("background: transparent;")
        vl.addWidget(ico, 0, Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel("Cargando configuración...")
        lbl.setStyleSheet(f"color: {MA_TEXT_SEC}; font-size: 14px; font-weight: 600; {_MA_FF} background: transparent; border: none;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(lbl)
        return w

    def _create_settings_error_state(self, error_msg, ma_id):
        w = QWidget()
        w.setStyleSheet(f"background: {MA_BG};")
        vl = QVBoxLayout(w)
        vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.setSpacing(16)
        ico = QLabel("\u26a0")
        ico.setStyleSheet(f"font-size: 40px; color: {MA_RED}; background: transparent; border: none;")
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(ico)
        title = QLabel("No se pudo cargar la configuración")
        title.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 16px; font-weight: 700; {_MA_FF} background: transparent; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(title)
        detail = QLabel(str(error_msg)[:200])
        detail.setStyleSheet(f"color: {MA_TEXT_DARK}; font-size: 11px; {_MA_FF} background: transparent; border: none;")
        detail.setWordWrap(True)
        detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(detail)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_retry = QPushButton("Reintentar")
        btn_retry.setFixedHeight(36)
        btn_retry.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_retry.setStyleSheet(f"QPushButton {{ background: {MA_RED}; color: white; border: none; border-radius: 8px; font-size: 12px; font-weight: 700; {_MA_FF} padding: 0 20px; }} QPushButton:hover {{ background: {MA_RED_H}; }}")
        btn_retry.clicked.connect(lambda: self.open_settings_view(ma_id))
        btn_row.addWidget(btn_retry)
        btn_back = QPushButton("Volver a disciplinas")
        btn_back.setFixedHeight(36)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet(f"QPushButton {{ background: {MA_CARD}; color: {MA_TEXT_SEC}; border: 1px solid {MA_BORDER}; border-radius: 8px; font-size: 12px; font-weight: 600; {_MA_FF} padding: 0 20px; }} QPushButton:hover {{ color: {MA_TEXT_PRI}; border-color: {MA_BORDER_HI}; }}")
        btn_back.clicked.connect(self._close_settings_view)
        btn_row.addWidget(btn_back)
        btn_row.addStretch()
        vl.addLayout(btn_row)
        return w

    def open_settings_view(self, ma_id):
        self._clear_settings_container()
        loading = self._create_settings_loading_state()
        self.settings_layout.addWidget(loading)
        self.main_stack.setCurrentWidget(self.settings_container)
        QApplication.processEvents()
        try:
            view = MartialArtSettingsView(
                self.repo, ma_id, parent_view=self, parent=self.settings_container,
            )
            self.settings_layout.removeWidget(loading)
            loading.deleteLater()
            self._settings_view = view
            view.back_clicked.connect(self._close_settings_view)
            view.saved.connect(self._on_settings_saved)
            self.settings_layout.addWidget(view)
            view.show()
            view.raise_()
            view.setFocus()
        except Exception as exc:
            debug_log(f"[BeltsView] Error abriendo configuración: {repr(exc)}")
            self.settings_layout.removeWidget(loading)
            loading.deleteLater()
            self.settings_layout.addWidget(self._create_settings_error_state(str(exc), ma_id))

    def _close_settings_view(self):
        self.main_stack.setCurrentIndex(0)
        self._clear_settings_container()
        self._load_martial_arts()
        if self.selected_martial_art:
            ma_id = self.selected_martial_art["id"]
            updated = self.repo.get_martial_art(ma_id)
            if updated:
                self.selected_martial_art = updated
                self._show_detail_panel(updated)
                pe = bool(updated.get("progression_enabled", True))
                if pe:
                    self._load_belts()
                    self._load_requirements()
                else:
                    self._load_description_page()
                    self._load_exercises_page()

    def _on_settings_saved(self):
        self._load_martial_arts()
        if self.selected_martial_art:
            ma_id = self.selected_martial_art["id"]
            updated = self.repo.get_martial_art(ma_id)
            if updated:
                self.selected_martial_art = updated
                for item in self._martial_art_items:
                    is_sel = item.martial_art.get("id") == ma_id
                    item.set_selected(is_sel)
                self._show_detail_panel(updated)
                pe = bool(updated.get("progression_enabled", True))
                if pe:
                    self._load_belts()
                    self._load_requirements()
                else:
                    self._load_description_page()
                    self._load_exercises_page()

    # ══════════════════════════════════════════════════════════════
    #  CRUD
    # ══════════════════════════════════════════════════════════════
    def _open_create_martial_art(self):
        self._blur_on()
        try:
            dlg = MartialArtDialog(self.repo, parent=self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self._load_martial_arts()
        finally:
            self._blur_off()

    def _open_edit_martial_art(self, martial_art):
        self._blur_on()
        try:
            dlg = MartialArtDialog(self.repo, martial_art=martial_art, parent=self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self._load_martial_arts()
        finally:
            self._blur_off()

    def _delete_martial_art(self, martial_art):
        dlg = MartialArtConfirmDialog(
            title="Confirmar eliminacion", message=f"Eliminar '{martial_art['name']}'?",
            detail_text="Se eliminaran todos sus cinturones y requisitos.",
            confirm_text="Eliminar", is_danger=True, parent=self,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            try:
                self.repo.delete_martial_art(martial_art["id"])
                self._load_martial_arts()
                self._detail_panel.setVisible(False)
            except Exception as e:
                err = MartialArtConfirmDialog(title="Error", message=str(e), confirm_text="Cerrar", parent=self)
                err.exec()

    def _open_create_belt(self):
        if not self.selected_martial_art:
            return
        self._blur_on()
        try:
            dlg = BeltDialog(
                self.repo, self.selected_martial_art["id"],
                martial_art_name=self.selected_martial_art["name"], parent=self,
            )
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self._load_belts()
        finally:
            self._blur_off()

    def _open_edit_belt(self, belt):
        self._blur_on()
        try:
            dlg = BeltDialog(
                self.repo, self.selected_martial_art["id"],
                martial_art_name=self.selected_martial_art["name"],
                belt=belt, parent=self,
            )
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self._load_belts()
        finally:
            self._blur_off()

    def _delete_belt(self, belt):
        dlg = MartialArtConfirmDialog(
            title="Confirmar eliminacion", message=f"Eliminar cinturon '{belt['name']}'?",
            confirm_text="Eliminar", is_danger=True, parent=self,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            try:
                self.repo.delete_belt(belt["id"])
                self._load_belts()
            except Exception as e:
                err = MartialArtConfirmDialog(title="Error", message=str(e), confirm_text="Cerrar", parent=self)
                err.exec()

    def _open_create_requirement(self):
        if not self.selected_belt:
            return
        self._blur_on()
        try:
            dlg = RequirementDialog(self.repo, self.selected_belt["id"], parent=self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self._load_requirements()
        finally:
            self._blur_off()

    def _open_edit_requirement(self, req):
        self._blur_on()
        try:
            dlg = RequirementDialog(self.repo, self.selected_belt["id"], req=req, parent=self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self._load_requirements()
        finally:
            self._blur_off()

    def _delete_requirement(self, req):
        dlg = MartialArtConfirmDialog(
            title="Confirmar eliminacion", message="Eliminar este requisito?",
            confirm_text="Eliminar", is_danger=True, parent=self,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            try:
                self.repo.delete_requirement(req["id"])
                self._load_requirements()
            except Exception as e:
                err = MartialArtConfirmDialog(title="Error", message=str(e), confirm_text="Cerrar", parent=self)
                err.exec()

    def _open_promote_student(self):
        self._blur_on()
        try:
            dlg = PromoteStudentDialog(self.repo, parent=self)
            dlg.exec()
        finally:
            self._blur_off()