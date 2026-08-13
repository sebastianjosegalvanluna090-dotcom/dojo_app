import re

from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QFrame, QScrollArea, QLineEdit, QComboBox,
    QGraphicsDropShadowEffect, QHBoxLayout, QVBoxLayout, QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def valid_hex_color(value, fallback="#C8102E"):
    """Return *value* if it is a valid 6-digit hex colour, else *fallback*."""
    if value and isinstance(value, str) and _HEX_RE.match(value):
        return value
    return fallback


def normalize_active_state(value):
    """Normalize is_active to bool. None defaults to True (active)."""
    if value is None:
        return True
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() not in {"false", "0", "inactive", "inactivo", "no"}
    return True

# ── Paleta ────────────────────────────────────────────────────
MA_BG       = "#050505"
MA_SIDE     = "#0D0D0D"
MA_CARD     = "#161616"
MA_HOVER    = "#1E1E1E"
MA_INPUT    = "#1C1C1C"
MA_SURFACE  = "#111111"
MA_BORDER   = "#2A2A2A"
MA_BORDER_HI = "#3F3F3F"

# ── Tokens para modales (unificados) ──────────────────────────
MA_MODAL_BG     = "#151515"
MA_MODAL_CARD   = "#1A1A1A"
MA_MODAL_INPUT  = "#202020"
MA_MODAL_HEADER = "#181818"
MA_MODAL_BORDER = "#303030"

MA_RED      = "#C8102E"
MA_RED_H    = "#E8152F"
MA_GREEN    = "#22C55E"
MA_YELLOW   = "#EAB308"
MA_BLUE     = "#3B82F6"
MA_PURPLE   = "#7E22CE"
MA_ORANGE   = "#F97316"
MA_TEXT_PRI = "#F0F0F0"
MA_TEXT_SEC = "#9CA3AF"
MA_TEXT_MUT = "#6B7280"
MA_TEXT_DARK = "#4B5563"

# ── Font family (reused across all QSS) ───────────────────────
_MA_FF = "font-family: 'Inter', 'Segoe UI', sans-serif;"

# ── QSS: Fields (QLineEdit + QComboBox) ───────────────────────
MA_FIELD_QSS = f"""
    QLineEdit, QComboBox {{
        background: {MA_INPUT};
        color: {MA_TEXT_PRI};
        border: 1.5px solid {MA_BORDER};
        border-radius: 8px;
        padding: 0 12px;
        font-size: 13px;
        {_MA_FF}
        min-height: 38px;
    }}
    QLineEdit:focus, QComboBox:focus {{
        border-color: {MA_BLUE};
    }}
    QLineEdit:hover, QComboBox:hover {{
        border-color: {MA_BORDER_HI};
    }}
    QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox QAbstractItemView {{
        background: {MA_INPUT};
        color: {MA_TEXT_PRI};
        border: 1px solid {MA_BORDER};
        border-radius: 8px;
        selection-background-color: {MA_HOVER};
    }}
"""

# ── QSS: SpinBox (dedicated -- MA_FIELD_QSS only covers QLineEdit/QComboBox) ──
MA_SPINBOX_QSS = f"""
    QSpinBox {{
        background-color: {MA_MODAL_INPUT};
        color: #F4F4F5;
        border: 1px solid #343434;
        border-radius: 10px;
        padding-left: 12px;
        padding-right: 40px;
        min-height: 42px;
        font-size: 13px;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        selection-background-color: #2563EB;
    }}
    QSpinBox:hover {{
        border-color: #484848;
    }}
    QSpinBox:focus {{
        border-color: #3B82F6;
    }}
    QSpinBox::up-button {{
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 34px;
        height: 20px;
        background-color: #252525;
        border-left: 1px solid #343434;
        border-bottom: 1px solid #303030;
        border-top-right-radius: 9px;
    }}
    QSpinBox::down-button {{
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 34px;
        height: 20px;
        background-color: #252525;
        border-left: 1px solid #343434;
        border-bottom-right-radius: 9px;
    }}
    QSpinBox::up-button:hover,
    QSpinBox::down-button:hover {{
        background-color: #303030;
    }}
    QSpinBox::up-arrow {{
        image: none;
        width: 0px;
        height: 0px;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 5px solid #A1A1AA;
    }}
    QSpinBox::down-arrow {{
        image: none;
        width: 0px;
        height: 0px;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid #A1A1AA;
    }}
"""

# ── QSS: Scrollbar (standalone, for any widget) ───────────────
MA_SCROLLBAR_QSS = f"""
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        border: none;
    }}
    QScrollBar::handle:vertical {{
        background: #303030;
        border-radius: 3px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: #454545;
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
        border: none;
        background: transparent;
    }}
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        background: transparent;
    }}
    QScrollBar:horizontal {{
        height: 0;
        border: none;
        background: transparent;
    }}
    QScrollBar::add-page:horizontal,
    QScrollBar::sub-page:horizontal {{
        background: transparent;
    }}
"""

# ── QSS: Scroll Area ──────────────────────────────────────────
MA_SCROLL_QSS = f"""
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    QScrollArea > QWidget > QWidget {{
        background: transparent;
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        border: none;
    }}
    QScrollBar::handle:vertical {{
        background: #303030;
        border-radius: 3px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: #454545;
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
        border: none;
        background: transparent;
    }}
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        background: transparent;
    }}
    QScrollBar:horizontal {{
        height: 0;
        border: none;
        background: transparent;
    }}
    QScrollBar::add-page:horizontal,
    QScrollBar::sub-page:horizontal {{
        background: transparent;
    }}
"""

# ── QSS: Card ─────────────────────────────────────────────────
MA_CARD_QSS = f"""
    QFrame {{
        background: {MA_CARD};
        border: 1px solid {MA_BORDER};
        border-radius: 16px;
    }}
    QFrame * {{
        background: transparent;
        border: none;
    }}
"""

# ── Badge presets ─────────────────────────────────────────────
MA_BADGE_PRESETS = {
    "active":     ("Activo",      "#052E16", MA_GREEN,  "#052E16"),
    "inactive":   ("Inactivo",    "#1A1A1A", MA_TEXT_MUT, MA_BORDER),
    "initial":    ("Inicial",     "#0C1A4E", MA_BLUE,   "#0C1A4E"),
    "final":      ("Final",       "#1C1A0E", MA_YELLOW, "#1C1A0E"),
    "blocked":    ("Bloqueado",   "#1A0A0A", MA_RED,    "#2A0A0A"),
    "pending":    ("Pendiente",   "#1C1A0E", MA_YELLOW, "#1C1A0E"),
    "processing": ("Procesando",  "#0C1A4E", MA_BLUE,   "#0C1A4E"),
    "error":      ("Error",       "#2A0A0A", MA_RED,    "#2A0A0A"),
}


# ═══════════════════════════════════════════════════════════════
#  Helper functions
# ═══════════════════════════════════════════════════════════════

def _ma_shadow(widget, blur: int = 20, offset_y: int = 4, alpha: int = 100):
    """Standard drop-shadow for elevated elements."""
    s = QGraphicsDropShadowEffect(widget)
    s.setBlurRadius(blur)
    s.setOffset(0, offset_y)
    s.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(s)
    return s


def _ma_card(radius: str = "16px", bg: str = None, border: str = None) -> QFrame:
    """Glass card with shadow and standard styling."""
    card = QFrame()
    bg_c = bg or MA_CARD
    bd_c = border or MA_BORDER
    card.setStyleSheet(f"""
        QFrame {{
            background: {bg_c};
            border: 1px solid {bd_c};
            border-radius: {radius};
        }}
        QFrame * {{
            background: transparent;
            border: none;
        }}
    """)
    _ma_shadow(card)
    return card


def _ma_primary_btn(label: str, color: str = None, height: int = 40) -> QPushButton:
    """Primary action button (create, save, confirm)."""
    c = color or MA_RED
    hover = MA_RED_H if c == MA_RED else f"{c}CC"
    btn = QPushButton(label)
    btn.setFixedHeight(height)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {c}; color: white; border: none;
            border-radius: {height // 4}px;
            font-size: 13px; font-weight: 700;
            {_MA_FF} padding: 0 20px;
        }}
        QPushButton:hover {{ background: {hover}; }}
        QPushButton:disabled {{ background: {MA_BORDER}; color: {MA_TEXT_MUT}; }}
    """)
    return btn


def _ma_secondary_btn(label: str, height: int = 40) -> QPushButton:
    """Secondary / cancel button."""
    btn = QPushButton(label)
    btn.setFixedHeight(height)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {MA_CARD}; color: {MA_TEXT_SEC};
            border: 1px solid {MA_BORDER};
            border-radius: {height // 4}px;
            font-size: 13px; font-weight: 600;
            {_MA_FF} padding: 0 20px;
        }}
        QPushButton:hover {{
            background: {MA_HOVER}; border-color: {MA_RED};
            color: {MA_TEXT_PRI};
        }}
    """)
    return btn


def _ma_icon_btn(icon: str, size: int = 32, accent: str = None) -> QPushButton:
    """Square icon button (edit, delete, expand)."""
    btn = QPushButton(icon)
    btn.setFixedSize(size, size)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    a = accent or MA_TEXT_MUT
    btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent; color: {MA_TEXT_DARK};
            border: none; border-radius: {size // 4}px;
            font-size: {size // 2 - 1}px;
        }}
        QPushButton:hover {{
            color: {a}; background: {MA_HOVER};
        }}
    """)
    return btn


def _ma_field_label(text: str) -> QLabel:
    """Section / field label (10px, uppercase, letter-spacing).

    Clean label: transparent background, no border, no padding,
    no icon and no decorative boxes.
    """
    lbl = QLabel(text)
    lbl.setObjectName("FieldLabel")
    lbl.setStyleSheet(f"""
        QLabel#FieldLabel {{
            color: #A1A1AA;
            background: transparent;
            border: none;
            padding: 0;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.8px;
            {_MA_FF}
        }}
    """)
    return lbl


def _ma_section_label(text: str) -> QWidget:
    """Section separator: uppercase label + horizontal line."""
    w = QWidget()
    w.setStyleSheet("background: transparent;")
    hl = QHBoxLayout(w)
    hl.setContentsMargins(0, 0, 0, 0)
    hl.setSpacing(12)
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(f"""
        color: {MA_TEXT_MUT}; font-size: 10px; font-weight: 700;
        {_MA_FF}
        letter-spacing: 1.5px; background: transparent; border: none;
    """)
    line = QFrame()
    line.setFixedHeight(1)
    line.setStyleSheet(f"QFrame {{ background: {MA_BORDER}; border: none; }}")
    hl.addWidget(lbl)
    hl.addWidget(line, 1)
    return w


def _ma_badge(status_key: str, custom_text: str = None) -> QLabel:
    """
    Status badge with presets.
    Keys: active, inactive, initial, final, blocked, pending, processing, error.
    Falls back to a neutral style for unknown keys.
    """
    text, bg, color, border = MA_BADGE_PRESETS.get(
        status_key.lower(),
        (status_key.upper(), MA_HOVER, MA_TEXT_MUT, MA_BORDER),
    )
    lbl = QLabel(custom_text or text)
    lbl.setFixedHeight(22)
    lbl.setStyleSheet(f"""
        QLabel {{
            background: {bg}; color: {color};
            border: 1px solid {border};
            border-radius: 11px;
            font-size: 10px; font-weight: 700;
            {_MA_FF}
            padding: 0 8px; letter-spacing: 0.3px;
        }}
    """)
    return lbl


def _ma_scroll(container: QWidget) -> QScrollArea:
    """Standard scroll area wrapping *container*."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(
        Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
    )
    scroll.setStyleSheet(MA_SCROLL_QSS)
    scroll.setWidget(container)
    return scroll


def _ma_separator(vertical: bool = False) -> QFrame:
    """Gradient separator that fades at both ends."""
    sep = QFrame()
    if vertical:
        sep.setFixedWidth(1)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 transparent, stop:0.3 {MA_BORDER},
                stop:0.7 {MA_BORDER}, stop:1 transparent);
            border: none;
        """)
    else:
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 transparent, stop:0.3 {MA_BORDER},
                stop:0.7 {MA_BORDER}, stop:1 transparent);
            border: none;
        """)
    return sep


def _ma_empty_state(icon: str, title: str, subtitle: str = "") -> QWidget:
    """Empty-state display shown when a list has no data."""
    w = QWidget()
    w.setStyleSheet("background: transparent;")
    vl = QVBoxLayout(w)
    vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    vl.setSpacing(12)

    ico = QLabel(icon)
    ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
    ico.setStyleSheet(
        "font-size: 40px; background: transparent; border: none;"
    )

    t = QLabel(title)
    t.setAlignment(Qt.AlignmentFlag.AlignCenter)
    t.setStyleSheet(f"""
        color: {MA_TEXT_SEC}; font-size: 16px; font-weight: 600;
        {_MA_FF}
        background: transparent; border: none;
    """)

    vl.addWidget(ico)
    vl.addWidget(t)

    if subtitle:
        s = QLabel(subtitle)
        s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s.setWordWrap(True)
        s.setStyleSheet(f"""
            color: {MA_TEXT_MUT}; font-size: 13px;
            {_MA_FF}
            background: transparent; border: none;
        """)
        vl.addWidget(s)

    return w


def _ma_label(text: str) -> QLabel:
    """Short helper: secondary text, 11px, weight 600."""
    lbl = QLabel(text)
    lbl.setStyleSheet(f"""
        color: {MA_TEXT_SEC}; font-size: 11px; font-weight: 600;
        {_MA_FF}
    """)
    return lbl
