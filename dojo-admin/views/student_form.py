"""
student_form.py — Formulario de estudiantes premium con AddressBuilder.

Mejoras visuales:
    - Dialog con header gradient + icono SVG
    - Secciones con accent bar rojo + glow + staggered fade-up
    - Inputs con focus glow rojo + hover states
    - AddressBuilder modal para construir dirección colombiana (SURED)
    - Badges condicional/opcional en secciones
    - Animaciones de entrada escalonadas

Lógica de negocio preservada 100% del original:
    - StudentRepository connections (get_form_lookups, get_by_id, create, update, etc.)
    - PHONE_PREFIXES, GUARDIAN_RELATIONSHIPS, BLOOD_TYPES
    - _SearchableCombo
    - Calendar dialogs
    - Document upload/delete
    - Category conditional logic (KID/YOUTH/ADULT)
    - Save flow with guardian/emergency/health/documents
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QComboBox, QDateEdit, QPushButton,
    QLabel, QFrame, QMessageBox, QWidget, QCalendarWidget,
    QSizePolicy, QToolButton, QScrollArea, QCompleter,
    QFileDialog, QListWidget, QListWidgetItem, QTextEdit,
    QGraphicsOpacityEffect, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import (
    Qt, QDate, QLocale, QStringListModel, QTimer,
    QPropertyAnimation, QEasingCurve, QPoint, QRectF,
    pyqtProperty,
)
from PyQt6.QtGui import QColor, QTextCharFormat, QFont, QPainter, QPen, QPainterPath

from core.i18n import tr, trf

import os

# ─── PALETA ───────────────────────────────────────────────────────────
BG_DEEP   = "#050505"
BG_DARK   = "#0D0D0D"
BG_CARD   = "#161616"
BG_INPUT  = "#1C1C1C"
BG_HOVER  = "#1E1E1E"
BG_ACTIVE = "#1A0A0C"
BORDER    = "#2A2A2A"
BORDER_2  = "#1F1F1F"
BORDER_F  = "#C8102E"
RED       = "#C8102E"
RED_H     = "#E8152F"
RED_GLOW  = "rgba(200,16,46,0.12)"
TEXT_PRI  = "#F0F0F0"
TEXT_SEC  = "#9CA3AF"
TEXT_MUT  = "#6B7280"
TEXT_DIM  = "#4B5563"
GREEN     = "#22C55E"
YELLOW    = "#EAB308"
BLUE      = "#3B82F6"
PURPLE    = "#A855F7"
ERROR_C   = "#FF4444"

PHONE_PREFIXES = [
    ("🇦🇫", "+93", "Afganistán"),
    ("🇦🇱", "+355", "Albania"),
    ("🇩🇿", "+213", "Argelia"),
    ("🇦🇩", "+376", "Andorra"),
    ("🇦🇴", "+244", "Angola"),
    ("🇦🇷", "+54", "Argentina"),
    ("🇦🇲", "+374", "Armenia"),
    ("🇦🇺", "+61", "Australia"),
    ("🇦🇹", "+43", "Austria"),
    ("🇦🇿", "+994", "Azerbaiyán"),
    ("🇧🇸", "+1", "Bahamas"),
    ("🇧🇭", "+973", "Bahréin"),
    ("🇧🇩", "+880", "Bangladesh"),
    ("🇧🇾", "+375", "Bielorrusia"),
    ("🇧🇪", "+32", "Bélgica"),
    ("🇧🇿", "+501", "Belice"),
    ("🇧🇴", "+591", "Bolivia"),
    ("🇧🇦", "+387", "Bosnia y Herzegovina"),
    ("🇧🇷", "+55", "Brasil"),
    ("🇧🇬", "+359", "Bulgaria"),
    ("🇨🇦", "+1", "Canadá"),
    ("🇨🇱", "+56", "Chile"),
    ("🇨🇳", "+86", "China"),
    ("🇨🇴", "+57", "Colombia"),
    ("🇨🇷", "+506", "Costa Rica"),
    ("🇭🇷", "+385", "Croacia"),
    ("🇨🇺", "+53", "Cuba"),
    ("🇩🇰", "+45", "Dinamarca"),
    ("🇩🇴", "+1", "República Dominicana"),
    ("🇪🇨", "+593", "Ecuador"),
    ("🇪🇬", "+20", "Egipto"),
    ("🇸🇻", "+503", "El Salvador"),
    ("🇪🇸", "+34", "España"),
    ("🇺🇸", "+1", "Estados Unidos"),
    ("🇪🇪", "+372", "Estonia"),
    ("🇪🇹", "+251", "Etiopía"),
    ("🇵🇭", "+63", "Filipinas"),
    ("🇫🇮", "+358", "Finlandia"),
    ("🇫🇷", "+33", "Francia"),
    ("🇬🇪", "+995", "Georgia"),
    ("🇩🇪", "+49", "Alemania"),
    ("🇬🇷", "+30", "Grecia"),
    ("🇬🇹", "+502", "Guatemala"),
    ("🇭🇳", "+504", "Honduras"),
    ("🇭🇰", "+852", "Hong Kong"),
    ("🇭🇺", "+36", "Hungría"),
    ("🇮🇳", "+91", "India"),
    ("🇮🇩", "+62", "Indonesia"),
    ("🇮🇷", "+98", "Irán"),
    ("🇮🇪", "+353", "Irlanda"),
    ("🇮🇱", "+972", "Israel"),
    ("🇮🇹", "+39", "Italia"),
    ("🇯🇵", "+81", "Japón"),
    ("🇯🇴", "+962", "Jordania"),
    ("🇰🇿", "+7", "Kazajistán"),
    ("🇰🇪", "+254", "Kenia"),
    ("🇰🇷", "+82", "Corea del Sur"),
    ("🇱🇧", "+961", "Líbano"),
    ("🇱🇹", "+370", "Lituania"),
    ("🇱🇺", "+352", "Luxemburgo"),
    ("🇲🇾", "+60", "Malasia"),
    ("🇲🇽", "+52", "México"),
    ("🇲🇦", "+212", "Marruecos"),
    ("🇳🇱", "+31", "Países Bajos"),
    ("🇳🇿", "+64", "Nueva Zelanda"),
    ("🇳🇮", "+505", "Nicaragua"),
    ("🇳🇬", "+234", "Nigeria"),
    ("🇳🇴", "+47", "Noruega"),
    ("🇵🇰", "+92", "Pakistán"),
    ("🇵🇦", "+507", "Panamá"),
    ("🇵🇾", "+595", "Paraguay"),
    ("🇵🇪", "+51", "Perú"),
    ("🇵🇱", "+48", "Polonia"),
    ("🇵🇹", "+351", "Portugal"),
    ("🇬🇧", "+44", "Reino Unido"),
    ("🇨🇿", "+420", "República Checa"),
    ("🇷🇴", "+40", "Rumania"),
    ("🇷🇺", "+7", "Rusia"),
    ("🇸🇦", "+966", "Arabia Saudita"),
    ("🇸🇬", "+65", "Singapur"),
    ("🇿🇦", "+27", "Sudáfrica"),
    ("🇸🇪", "+46", "Suecia"),
    ("🇨🇭", "+41", "Suiza"),
    ("🇹🇭", "+66", "Tailandia"),
    ("🇹🇷", "+90", "Turquía"),
    ("🇦🇪", "+971", "Emiratos Árabes Unidos"),
    ("🇺🇦", "+380", "Ucrania"),
    ("🇺🇾", "+598", "Uruguay"),
    ("🇻🇪", "+58", "Venezuela"),
    ("🇻🇳", "+84", "Vietnam"),
]

# ─── ICON LABEL ───────────────────────────────────────────────────────
import re as _re
from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtGui import QPen

class IconLabel(QWidget):
    ICONS = {
        "pin":      '<line x1="12" y1="22" x2="12" y2="12"/><circle cx="12" cy="8" r="4"/><ellipse cx="12" cy="22" rx="3" ry="1"/>',
        "info":     '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="8"/><line x1="12" y1="12" x2="12" y2="16"/>',
        "edit":     '<line x1="18" y1="2" x2="22" y2="6"/><polyline points="14 6 18 2 22 6 8 20 2 22 4 16 14 6"/>',
        "plus":     '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
        "close":    '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
        "upload":   '<polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><rect x="3" y="3" width="18" height="5" rx="2"/><line x1="3" y1="15" x2="5" y2="15"/><line x1="19" y1="15" x2="21" y2="15"/>',
        "trash":    '<polyline points="3 6 21 6"/><polyline points="8 6 8 3 16 3 16 6"/><rect x="5" y="6" width="14" height="15" rx="1"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>',
        "check":    '<polyline points="20 6 9 17 4 12"/>',
        "key":      '<circle cx="7" cy="17" r="4"/><line x1="10.5" y1="13.5" x2="20" y2="4"/><line x1="18" y1="6" x2="20" y2="8"/>',
        "user":     '<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>',
        "lock":     '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
        "arrow-r":  '<polyline points="9 18 15 12 9 6"/>',
        "doc":      '<polyline points="14 2 14 8 20 8"/><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="13" y2="17"/>',
        "health":   '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
        "school":   '<polyline points="2 7 12 2 22 7"/><polyline points="2 17 12 22 22 17"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="12" y1="2" x2="12" y2="22"/>',
        "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
        "phone":    '<rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/>',
    }

    def __init__(self, icon_name: str, size: int = 18, color: str = "#9CA3AF", parent=None):
        super().__init__(parent)
        self._icon_name = icon_name
        self._size = size
        self._color = color
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

    def set_color(self, color: str):
        self._color = color
        self.update()

    def paintEvent(self, event):
        path_data = self.ICONS.get(self._icon_name)
        if not path_data:
            return
        try:
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            scale = self._size / 24.0
            p.scale(scale, scale)
            pen = QPen(QColor(self._color))
            pen.setWidthF(1.8)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            elements = _re.findall(r'<(circle|rect|line|polyline|ellipse|path)\s([^/]+)/?>', path_data)
            for tag, attrs_str in elements:
                attrs = dict(_re.findall(r'(\w+)="([^"]*)"', attrs_str))
                if tag == "circle":
                    cx, cy, r = float(attrs.get("cx", 0)), float(attrs.get("cy", 0)), float(attrs.get("r", 0))
                    p.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))
                elif tag == "ellipse":
                    cx, cy = float(attrs.get("cx", 0)), float(attrs.get("cy", 0))
                    rx, ry = float(attrs.get("rx", 0)), float(attrs.get("ry", 0))
                    p.drawEllipse(QRectF(cx - rx, cy - ry, rx * 2, ry * 2))
                elif tag == "rect":
                    x, y = float(attrs.get("x", 0)), float(attrs.get("y", 0))
                    w, h = float(attrs.get("width", 0)), float(attrs.get("height", 0))
                    rx = float(attrs.get("rx", 0))
                    rect = QRectF(x, y, w, h)
                    p.drawRoundedRect(rect, rx, rx) if rx > 0 else p.drawRect(rect)
                elif tag == "line":
                    p.drawLine(QPointF(float(attrs.get("x1", 0)), float(attrs.get("y1", 0))),
                               QPointF(float(attrs.get("x2", 0)), float(attrs.get("y2", 0))))
                elif tag == "polyline":
                    pts = _re.findall(r'-?[\d.]+', attrs.get("points", ""))
                    if len(pts) >= 4 and len(pts) % 2 == 0:
                        path = QPainterPath()
                        path.moveTo(float(pts[0]), float(pts[1]))
                        for i in range(2, len(pts), 2):
                            path.lineTo(float(pts[i]), float(pts[i + 1]))
                        p.drawPath(path)
                elif tag == "path":
                    d = attrs.get("d", "")
                    path = QPainterPath()
                    tokens = _re.findall(r'[MLCZQAmlczqa]|-?[\d.]+', d)
                    i = 0
                    current = QPointF(0, 0)
                    while i < len(tokens):
                        cmd = tokens[i]; i += 1
                        if cmd in ("M", "m"):
                            x, y = float(tokens[i]), float(tokens[i + 1]); i += 2
                            if cmd == "m": x += current.x(); y += current.y()
                            current = QPointF(x, y); path.moveTo(current)
                        elif cmd in ("L", "l"):
                            x, y = float(tokens[i]), float(tokens[i + 1]); i += 2
                            if cmd == "l": x += current.x(); y += current.y()
                            current = QPointF(x, y); path.lineTo(current)
                        elif cmd in ("C", "c"):
                            x1, y1 = float(tokens[i]), float(tokens[i+1])
                            x2, y2 = float(tokens[i+2]), float(tokens[i+3])
                            x, y   = float(tokens[i+4]), float(tokens[i+5]); i += 6
                            if cmd == "c":
                                x1+=current.x(); y1+=current.y()
                                x2+=current.x(); y2+=current.y()
                                x +=current.x(); y +=current.y()
                            path.cubicTo(QPointF(x1,y1), QPointF(x2,y2), QPointF(x,y))
                            current = QPointF(x, y)
                        elif cmd in ("Z", "z"):
                            path.closeSubpath()
                    p.drawPath(path)
        except Exception:
            pass


def _doc_icon_for_file(path: str) -> tuple[str, str]:
    """Retorna (simbolo, color) segun extension del archivo."""
    ext = os.path.splitext(path)[1].lower() if path else ""
    if ext == ".pdf":
        return "PDF", "#E11D48"
    elif ext in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
        return "IMG", "#3B82F6"
    elif ext in (".doc", ".docx"):
        return "DOC", "#2563EB"
    elif ext in (".xls", ".xlsx"):
        return "XLS", "#10B981"
    elif ext in (".zip", ".rar", ".7z"):
        return "ZIP", "#F59E0B"
    else:
        return "FIL", "#6B7280"


FIELD_STYLE = f"""
    QLineEdit, QComboBox, QTextEdit {{
        background-color: {BG_INPUT};
        color: {TEXT_PRI};
        border: 1.5px solid {BORDER};
        border-radius: 10px;
        padding: 0 14px;
        font-size: 13px;
        font-weight: 500;
        font-family: 'Inter';
    }}
    QLineEdit, QComboBox {{
        min-height: 42px;
        max-height: 42px;
    }}
    QTextEdit {{
        min-height: 82px;
        max-height: 96px;
        padding: 10px 14px;
    }}
    QLineEdit:hover, QComboBox:hover, QTextEdit:hover {{
        border-color: {TEXT_DIM};
    }}
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
        border-color: {RED};
        background-color: {BG_HOVER};
    }}
    QLineEdit:disabled {{
        color: {TEXT_MUT};
        background-color: rgba(255,255,255,0.02);
    }}
    QComboBox::drop-down {{ border: none; width: 30px; }}
    QComboBox QAbstractItemView {{
        background-color: {BG_INPUT};
        color: {TEXT_PRI};
        selection-background-color: {RED};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 4px;
        font-size: 13px;
    }}
"""

CAL_STYLE = f"""
    QCalendarWidget {{
        background-color: {BG_CARD};
        color: {TEXT_PRI};
        border: none;
    }}
    QCalendarWidget QAbstractItemView {{
        background-color: {BG_CARD};
        color: {TEXT_PRI};
        selection-background-color: {RED};
        selection-color: white;
        font-size: 13px;
    }}
    QCalendarWidget QAbstractItemView:disabled {{
        color: #333333;
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background-color: {BG_INPUT};
        border-radius: 8px;
        padding: 4px;
        min-height: 44px;
    }}
    QCalendarWidget QToolButton {{
        background-color: transparent;
        color: {TEXT_PRI};
        font-size: 13px;
        font-weight: 600;
        border: none;
        border-radius: 6px;
        padding: 4px 8px;
        min-width: 28px;
        min-height: 28px;
    }}
    QCalendarWidget QToolButton:hover {{
        background-color: {BG_HOVER};
    }}
    QCalendarWidget QToolButton::menu-indicator {{ image: none; }}
    QCalendarWidget QSpinBox {{
        background-color: {BG_INPUT};
        color: {TEXT_PRI};
        border: 1px solid {BORDER};
        border-radius: 6px;
        font-size: 13px;
        padding: 2px 6px;
    }}
    QCalendarWidget QMenu {{
        background-color: {BG_INPUT};
        color: {TEXT_PRI};
        border: 1px solid {BORDER};
        border-radius: 8px;
        font-size: 13px;
    }}
    QCalendarWidget QMenu::item:selected {{
        background-color: {RED};
    }}
"""

GUARDIAN_RELATIONSHIPS = [
    "MADRE", "PADRE", "ABUELA", "ABUELO", "TÍA", "TÍO",
    "HERMANA", "HERMANO", "PRIMA", "PRIMO",
    "MADRASTRA", "PADRASTRO", "TUTOR_LEGAL", "OTRO"
]

BLOOD_TYPES = ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

DOC_TYPES_STUDENT = ["carnet_photo", "eps_certificate", "identity_document"]


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def _lbl(text):
    """Label con asterisco rojo opcional si el texto contiene '*'."""
    l = QLabel()
    l.setStyleSheet(
        f"color: {TEXT_MUT}; font-size: 10px; font-weight: 800; "
        f"font-family: 'Inter'; letter-spacing: 0.6px; border: none; "
        f"padding-left: 2px; padding-bottom: 2px;"
    )
    if "*" in text:
        clean = text.replace("*", "").strip()
        l.setText(f"{clean} <span style='color: {RED_H}; font-size: 13px;'>*</span>")
        l.setTextFormat(Qt.TextFormat.RichText)
    else:
        l.setText(text)
    return l


def _divider():
    f = QFrame()
    f.setFixedHeight(1)
    f.setStyleSheet(f"background: {BORDER_2}; border: none;")
    return f


class _SearchableCombo(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.setStyleSheet(FIELD_STYLE)


# ═══════════════════════════════════════════════════════════════════════════════
# ADDRESS BUILDER MODAL — Constructor de dirección colombiana (SURED)
# ═══════════════════════════════════════════════════════════════════════════════
class AddressBuilder(QDialog):
    """Modal para construir direcciones con formato SURED colombiano."""

    VIA_TYPES = [
        ("", "Seleccionar..."),
        ("CALLE", "Calle"),
        ("CARRERA", "Carrera"),
        ("DIAGONAL", "Diagonal"),
        ("TRANSVERSAL", "Transversal"),
        ("AVENIDA", "Avenida"),
        ("AUTOPISTA", "Autopista"),
    ]

    LETTERS = [
        ("", "—"),
        ("A", "A"), ("B", "B"), ("C", "C"), ("D", "D"), ("E", "E"),
        ("F", "F"), ("G", "G"), ("H", "H"), ("I", "I"), ("J", "J"),
        ("K", "K"), ("L", "L"), ("M", "M"), ("N", "N"), ("O", "O"),
        ("P", "P"), ("Q", "Q"), ("R", "R"), ("S", "S"), ("T", "T"),
        ("U", "U"), ("V", "V"), ("W", "W"), ("X", "X"), ("Y", "Y"),
        ("Z", "Z"),
    ]
    QUADRANTS = [
        ("", "—"),
        ("NORTE", "Norte"),
        ("SUR", "Sur"),
        ("ESTE", "Este"),
        ("OESTE", "Oeste"),
    ]

    def __init__(self, current_address: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Constructor de dirección")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DARK}; color: {TEXT_PRI};")
        self.setMinimumSize(980, 580)
        self.resize(1020, 620)
        self._result_address = current_address

        self._build_ui()
        self._parse_address(current_address)
        self._update_result()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──
        header = QFrame()
        header.setFixedHeight(68)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_DARK};
                border-bottom: 1px solid {BORDER_2};
            }}
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 0, 24, 0)
        h_layout.setSpacing(12)

        # Icon
        icon_frame = QFrame()
        icon_frame.setFixedSize(36, 36)
        icon_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_INPUT};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)
        icon_layout = QHBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_svg = IconLabel("pin", 18, RED)
        icon_layout.addWidget(icon_svg, 0, Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(icon_frame)

        # Title block
        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        title = QLabel("Constructor de dirección")
        title.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 15px; font-weight: 900; "
            f"font-family: 'Inter'; border: none;"
        )
        subtitle = QLabel("Completa los campos para construir tu dirección colombiana")
        subtitle.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 11px; font-weight: 600; border: none;"
        )
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        h_layout.addLayout(title_col, 1)

        # Info button
        self.btn_info = QPushButton("ℹ  Instrucciones")
        self.btn_info.setFixedHeight(32)
        self.btn_info.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_info.setStyleSheet(f"""
            QPushButton {{
                background: rgba(234,179,8,0.10);
                border: 1px solid rgba(234,179,8,0.30);
                border-radius: 8px;
                color: {YELLOW};
                font-size: 11px;
                font-weight: 800;
                font-family: 'Inter';
                padding: 0 14px;
            }}
            QPushButton:hover {{
                background: rgba(234,179,8,0.18);
            }}
        """)
        self.btn_info.clicked.connect(self._toggle_instructions)
        h_layout.addWidget(self.btn_info)

        root.addWidget(header)

        # ── Body (scrollable) ──
        body_scroll = QScrollArea()
        body_scroll.setWidgetResizable(True)
        body_scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical { background: transparent; width: 6px; }
            QScrollBar::handle:vertical { background: #2A2A2A; border-radius: 3px; min-height: 20px; }
        """)

        body = QWidget()
        body.setStyleSheet(f"background-color: {BG_DARK};")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 20, 24, 20)
        body_layout.setSpacing(16)

        # Instructions — visible por defecto, con tabla de ejemplos
        self.instructions_frame = QFrame()
        self.instructions_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(59,130,246,0.06);
                border: 1px solid rgba(59,130,246,0.20);
                border-radius: 10px;
            }}
            QFrame QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        self.instructions_frame.setVisible(True)
        inst_layout = QVBoxLayout(self.instructions_frame)
        inst_layout.setContentsMargins(16, 14, 16, 14)
        inst_layout.setSpacing(10)

        inst_title = QLabel("ℹ  Cómo construir tu dirección")
        inst_title.setStyleSheet(
            f"color: {BLUE}; font-size: 11px; font-weight: 900; "
            f"font-family: 'Inter'; border: none;"
        )
        inst_layout.addWidget(inst_title)

        inst_desc = QLabel(
            "Completa los campos de izquierda a derecha según tu dirección. "
            "Los campos que no apliquen déjalos en «—»."
        )
        inst_desc.setWordWrap(True)
        inst_desc.setStyleSheet(
            f"color: {TEXT_SEC}; font-size: 12px; font-weight: 500; border: none;"
        )
        inst_layout.addWidget(inst_desc)

        # Tabla de ejemplos
        examples_table = QFrame()
        examples_table.setStyleSheet(f"""
            QFrame {{
                background: rgba(255,255,255,0.03);
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
            QFrame QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        ex_layout = QVBoxLayout(examples_table)
        ex_layout.setContentsMargins(12, 10, 12, 10)
        ex_layout.setSpacing(4)

        # Header de la tabla
        cols_header = ["Vía", "Nro", "Letra", "Cuad", "#", "#", "Letra", "Placa", "Cuad", "→ Resultado"]
        stretches   = [  2,     1,     1,       1,    1,   1,    1,       1,       1,        3          ]

        ex_header = QHBoxLayout()
        for h, st in zip(cols_header, stretches):
            lbl = QLabel(h)
            lbl.setStyleSheet(
                f"color: {TEXT_MUT}; font-size: 9px; font-weight: 900; "
                f"font-family: 'Inter'; letter-spacing: 0.5px; background: transparent; border: none;"
            )
            ex_header.addWidget(lbl, st)
        ex_layout.addLayout(ex_header)

        sep_ex = QFrame()
        sep_ex.setFixedHeight(1)
        sep_ex.setStyleSheet(f"background: {BORDER}; border: none; min-height: 1px; max-height: 1px;")
        ex_layout.addWidget(sep_ex)

        # Filas de ejemplo — muestran en qué campo exacto va cada parte
        examples = [
            # (via,      num, letra, cuadrante, num2, num3, letra2, placa, cuad2, resultado)
            ("Calle",    "14","A",   "",        "50", "",   "A",    "45",  "",    "CALLE 14 A # 50 A - 45"),
            ("Carrera",  "21","",    "Sur",     "10", "",   "",     "20",  "",    "CARRERA 21 SUR # 10 - 20"),
            ("Diagonal", "10","",    "",        "40", "",   "B",    "18",  "Norte","DIAGONAL 10 # 40 B - 18 NORTE"),
            ("Carrera",  "8", "K",   "",        "36", "",   "B",    "76",  "",    "CARRERA 8 K # 36 B - 76"),
        ]
        for row_data in examples:
            row_ex = QHBoxLayout()
            for i, (val, st) in enumerate(zip(row_data, stretches)):
                is_result = (i == len(row_data) - 1)
                display = val if val else "—"
                lbl = QLabel(display)
                lbl.setStyleSheet(
                    f"color: {TEXT_PRI if is_result else (TEXT_SEC if val else TEXT_DIM)}; "
                    f"font-size: 11px; font-weight: {'700' if is_result else '500'}; "
                    f"font-family: 'Inter'; background: transparent; border: none;"
                )
                row_ex.addWidget(lbl, st)
            ex_layout.addLayout(row_ex)

        inst_layout.addWidget(examples_table)
        body_layout.addWidget(self.instructions_frame)

        # ── Builder fields ──
        # Single row: Vía | # | Letra | Cuad | # | # | Letra | — | Placa | Cuad
        row = QHBoxLayout()
        row.setSpacing(4)
        self.cmb_via = self._make_combo(self.VIA_TYPES, row, "VÍA", stretch=2)
        self.inp_num1 = self._make_input(row, "#", "8", stretch=1)
        self.cmb_let1 = self._make_combo(self.LETTERS, row, "Letra", stretch=1)
        self.cmb_quad1 = self._make_combo(self.QUADRANTS, row, "Cuadrante", stretch=1)
        self.inp_num2 = self._make_input(row, "#", "36", stretch=1)
        self.inp_num3 = self._make_input(row, "#", "", stretch=1)
        self.cmb_let2 = self._make_combo(self.LETTERS, row, "Letra", stretch=1)

        sep = QLabel("—")
        sep.setFixedWidth(16)
        sep.setFixedHeight(38)
        sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sep.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 14px; font-weight: 900; "
            f"border: none; background: transparent;"
        )
        row.addWidget(sep)

        self.inp_placa = self._make_input(row, "Placa", "", stretch=1)
        self.cmb_quad2 = self._make_combo(self.QUADRANTS, row, "Cuadrante", stretch=1)
        body_layout.addLayout(row)

        # Connect signals for live update
        for w in [self.cmb_via, self.inp_num1, self.cmb_let1, self.cmb_quad1,
                  self.inp_num2, self.inp_num3, self.cmb_let2, self.inp_placa, self.cmb_quad2]:
            if isinstance(w, QComboBox):
                w.currentIndexChanged.connect(self._update_result)
            else:
                w.textChanged.connect(self._update_result)

        # ── Result box ──
        self.result_box = QFrame()
        self.result_box.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 rgba(34,197,94,0.06), stop:1 rgba(34,197,94,0.02));
                border: 1px solid rgba(34,197,94,0.25);
                border-radius: 10px;
            }}
            QFrame QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        result_layout = QVBoxLayout(self.result_box)
        result_layout.setContentsMargins(16, 14, 16, 14)
        result_layout.setSpacing(6)

        result_label = QLabel("✓  DIRECCIÓN CONSTRUIDA")
        result_label.setStyleSheet(
            f"color: {GREEN}; font-size: 10px; font-weight: 900; "
            f"font-family: 'Inter'; letter-spacing: 0.8px; border: none;"
        )
        result_layout.addWidget(result_label)

        self.result_value = QLabel("—")
        self.result_value.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 16px; font-weight: 900; "
            f"font-family: 'Inter'; border: none; letter-spacing: 0.3px;"
        )
        self.result_value.setWordWrap(True)
        result_layout.addWidget(self.result_value)

        body_layout.addWidget(self.result_box)
        body_layout.addStretch()

        body_scroll.setWidget(body)
        root.addWidget(body_scroll, 1)

        # ── Footer ──
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                background: {BG_DARK};
                border-top: 1px solid {BORDER_2};
            }}
        """)
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(24, 14, 24, 14)
        f_layout.setSpacing(10)

        btn_clear = QPushButton("Limpiar")
        btn_clear.setFixedHeight(36)
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SEC};
                border: 1px solid {BORDER};
                border-radius: 8px;
                font-size: 12px;
                font-weight: 800;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
                border-color: {TEXT_MUT};
                background: {BG_HOVER};
            }}
        """)
        btn_clear.clicked.connect(self._clear)
        f_layout.addWidget(btn_clear)
        f_layout.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SEC};
                border: 1px solid {BORDER};
                border-radius: 8px;
                font-size: 12px;
                font-weight: 800;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
                border-color: {TEXT_MUT};
                background: {BG_HOVER};
            }}
        """)
        btn_cancel.clicked.connect(self.reject)
        f_layout.addWidget(btn_cancel)

        btn_accept = QPushButton("✓  Aceptar")
        btn_accept.setFixedHeight(36)
        btn_accept.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_accept.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {RED_H}, stop:1 {RED});
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 800;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background: #FF2040;
            }}
        """)
        accept_shadow = QGraphicsDropShadowEffect(btn_accept)
        accept_shadow.setBlurRadius(12)
        accept_shadow.setOffset(0, 4)
        accept_shadow.setColor(QColor(200, 16, 46, 100))
        btn_accept.setGraphicsEffect(accept_shadow)
        btn_accept.clicked.connect(self._accept)
        f_layout.addWidget(btn_accept)

        root.addWidget(footer)

    def _make_combo(self, items, layout, label_text, stretch=1):
        col = QVBoxLayout()
        col.setSpacing(4)
        col.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(label_text)
        lbl.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 9px; font-weight: 900; "
            f"font-family: 'Inter'; letter-spacing: 0.8px; "
            f"border: none; background: transparent;"
        )
        col.addWidget(lbl)

        combo = QComboBox()
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {BG_INPUT};
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 28px 0 10px;
                font-size: 12px;
                font-weight: 600;
                font-family: 'Inter';
                min-height: 38px;
            }}
            QComboBox:hover {{ border-color: {TEXT_DIM}; }}
            QComboBox:focus {{ border-color: {RED}; }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
                background: transparent;
                subcontrol-origin: padding;
                subcontrol-position: center right;
            }}
            QComboBox::down-arrow {{
                width: 0; height: 0;
            }}
            QComboBox QAbstractItemView {{
                background-color: {BG_INPUT};
                color: {TEXT_PRI};
                selection-background-color: {RED};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 4px;
                font-size: 12px;
                outline: none;
            }}
        """)
        for value, display in items:
            combo.addItem(display, value)
        col.addWidget(combo)
        layout.addLayout(col, stretch)
        return combo

    def _make_input(self, layout, label_text, placeholder="", stretch=1):
        col = QVBoxLayout()
        col.setSpacing(4)
        col.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(label_text)
        lbl.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 9px; font-weight: 900; "
            f"font-family: 'Inter'; letter-spacing: 0.8px; "
            f"border: none; background: transparent;"
        )
        col.addWidget(lbl)

        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_INPUT};
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 10px;
                font-size: 12px;
                font-weight: 600;
                font-family: 'Inter';
                min-height: 38px;
            }}
            QLineEdit:hover {{ border-color: {TEXT_DIM}; }}
            QLineEdit:focus {{ border-color: {RED}; }}
        """)
        col.addWidget(inp)
        layout.addLayout(col, stretch)
        return inp

    def _toggle_instructions(self):
        self.instructions_frame.setVisible(not self.instructions_frame.isVisible())

    def _update_result(self):
        via = self.cmb_via.currentData() or ""
        num1 = self.inp_num1.text().strip()
        let1 = self.cmb_let1.currentData() or ""
        quad1 = self.cmb_quad1.currentData() or ""
        num2 = self.inp_num2.text().strip()
        num3 = self.inp_num3.text().strip()
        let2 = self.cmb_let2.currentData() or ""
        placa = self.inp_placa.text().strip()
        quad2 = self.cmb_quad2.currentData() or ""

        parts = []
        if via: parts.append(via)
        if num1: parts.append(num1)
        if let1: parts.append(let1)
        if quad1: parts.append(quad1)
        if num2: parts.append("#")
        if num2: parts.append(num2)
        if num3: parts.append("#")
        if num3: parts.append(num3)
        if let2: parts.append(let2)
        if placa: parts.append("-")
        if placa: parts.append(placa)
        if quad2: parts.append(quad2)

        result = " ".join(parts)
        self._result_address = result if result else ""
        self.result_value.setText(result if result else "—")
        if result:
            self.result_value.setStyleSheet(
                f"color: {TEXT_PRI}; font-size: 16px; font-weight: 900; "
                f"font-family: 'Inter'; border: none; letter-spacing: 0.3px;"
            )
        else:
            self.result_value.setStyleSheet(
                f"color: {TEXT_DIM}; font-size: 16px; font-weight: 600; "
                f"font-family: 'Inter'; border: none;"
            )

    def _clear(self):
        self.cmb_via.setCurrentIndex(0)
        self.inp_num1.clear()
        self.cmb_let1.setCurrentIndex(0)
        self.cmb_quad1.setCurrentIndex(0)
        self.inp_num2.clear()
        self.inp_num3.clear()
        self.cmb_let2.setCurrentIndex(0)
        self.inp_placa.clear()
        self.cmb_quad2.setCurrentIndex(0)
        self._update_result()

    def _parse_address(self, address: str):
        """Intenta parsear una dirección existente para rellenar los campos."""
        if not address:
            return
        try:
            parts = address.upper().split()
            if not parts:
                return
            # Find via type
            via_map = {"CALLE": "CALLE", "CARRERA": "CARRERA", "DIAGONAL": "DIAGONAL",
                       "TRANSVERSAL": "TRANSVERSAL", "AVENIDA": "AVENIDA", "AUTOPISTA": "AUTOPISTA"}
            idx = 0
            if parts[0] in via_map:
                via = via_map[parts[0]]
                for i in range(self.cmb_via.count()):
                    if self.cmb_via.itemData(i) == via:
                        self.cmb_via.setCurrentIndex(i)
                        break
                idx = 1
            # Parse remaining: number, letter, quadrant, #, number, letter, -, placa, quadrant
            # This is a best-effort parse
            remaining = parts[idx:]
            pos = 0
            if pos < len(remaining) and remaining[pos].isdigit():
                self.inp_num1.setText(remaining[pos]); pos += 1
            if pos < len(remaining) and len(remaining[pos]) == 1 and remaining[pos].isalpha():
                for i in range(self.cmb_let1.count()):
                    if self.cmb_let1.itemData(i) == remaining[pos]:
                        self.cmb_let1.setCurrentIndex(i); break
                pos += 1
            if pos < len(remaining) and remaining[pos] in ("NORTE", "SUR", "ESTE", "OESTE"):
                for i in range(self.cmb_quad1.count()):
                    if self.cmb_quad1.itemData(i) == remaining[pos]:
                        self.cmb_quad1.setCurrentIndex(i); break
                pos += 1
            if pos < len(remaining) and remaining[pos] == "#":
                pos += 1
            if pos < len(remaining) and remaining[pos].isdigit():
                self.inp_num2.setText(remaining[pos]); pos += 1
            if pos < len(remaining) and remaining[pos] == "#":
                pos += 1
            if pos < len(remaining) and remaining[pos].isdigit():
                self.inp_num3.setText(remaining[pos]); pos += 1
            if pos < len(remaining) and len(remaining[pos]) == 1 and remaining[pos].isalpha():
                for i in range(self.cmb_let2.count()):
                    if self.cmb_let2.itemData(i) == remaining[pos]:
                        self.cmb_let2.setCurrentIndex(i); break
                pos += 1
            if pos < len(remaining) and remaining[pos] == "-":
                pos += 1
            if pos < len(remaining) and remaining[pos].isdigit():
                self.inp_placa.setText(remaining[pos]); pos += 1
            if pos < len(remaining) and remaining[pos] in ("NORTE", "SUR", "ESTE", "OESTE"):
                for i in range(self.cmb_quad2.count()):
                    if self.cmb_quad2.itemData(i) == remaining[pos]:
                        self.cmb_quad2.setCurrentIndex(i); break
                pos += 1
        except Exception:
            pass

    def _accept(self):
        if self._result_address:
            self.accept()
        else:
            QMessageBox.warning(self, "Atención", "Construye una dirección antes de aceptar.")

    def get_address(self) -> str:
        return self._result_address


# ═══════════════════════════════════════════════════════════════════════════════
# STUDENT FORM
# ═══════════════════════════════════════════════════════════════════════════════
class StudentForm(QDialog):
    def __init__(self, repo, student_id: int = None, parent=None):
        super().__init__(parent)
        self.repo       = repo
        self.student_id = student_id
        self.is_edit    = student_id is not None
        self.created_credentials = None
        self._lookups   = self.repo.get_form_lookups()
        self._student_documents_data = []
        self._animations = []

        self.setWindowTitle(trf("student.form.title_edit", "Editar Estudiante") if self.is_edit else trf("student.form.title_new", "Nuevo Estudiante"))
        self.setMinimumSize(780, 660)
        self.resize(820, 720)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DARK}; color: {TEXT_PRI};")

        # Entrance animation
        self.setWindowOpacity(0.0)
        self._opacity_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._opacity_anim.setDuration(320)
        self._opacity_anim.setStartValue(0.0)
        self._opacity_anim.setEndValue(1.0)
        self._opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._build_ui()
        self._load_combos()
        if self.is_edit:
            self._load_student()

        QTimer.singleShot(50, self._opacity_anim.start)

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Header ──
        header = QFrame()
        header.setFixedHeight(72)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_DARK};
                border-bottom: 1px solid {BORDER_2};
            }}
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(28, 0, 28, 0)
        h_layout.setSpacing(14)

        # Icon
        icon_frame = QFrame()
        icon_frame.setFixedSize(40, 40)
        icon_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_INPUT};
                border: 1px solid {BORDER};
                border-radius: 11px;
            }}
        """)
        icon_layout = QHBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_svg = IconLabel("edit" if self.is_edit else "plus", 18, RED)
        icon_layout.addWidget(icon_svg, 0, Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(icon_frame)

        # Title block
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel(trf("student.form.title_edit", "Editar Estudiante") if self.is_edit else trf("student.form.title_new", "Nuevo Estudiante"))
        title.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 17px; font-weight: 900; "
            f"font-family: 'Inter'; letter-spacing: -0.3px; border: none;"
        )
        subtitle = QLabel("Completa los campos para registrar un nuevo estudiante" if not self.is_edit else "Modifica los datos del estudiante")
        subtitle.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 11px; font-weight: 600; border: none;"
        )
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        h_layout.addLayout(title_col, 1)

        # Instructions button
        btn_instructions = QPushButton("ℹ  Instrucciones")
        btn_instructions.setFixedHeight(34)
        btn_instructions.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_instructions.setStyleSheet(f"""
            QPushButton {{
                background: rgba(59,130,246,0.10);
                color: {BLUE};
                border: 1px solid rgba(59,130,246,0.30);
                border-radius: 9px;
                font-size: 12px;
                font-weight: 800;
                font-family: 'Inter';
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background: rgba(59,130,246,0.20);
                border-color: {BLUE};
            }}
        """)
        btn_instructions.clicked.connect(self._open_instructions)
        h_layout.addWidget(btn_instructions)

        outer.addWidget(header)

        # ── Scroll area ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical { background: transparent; width: 6px; }
            QScrollBar::handle:vertical { background: #2A2A2A; border-radius: 3px; min-height: 28px; }
            QScrollBar::handle:vertical:hover { background: #444444; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
        """)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container.setStyleSheet(f"background-color: {BG_DARK};")
        root = QVBoxLayout(container)
        root.setContentsMargins(28, 24, 28, 16)
        root.setSpacing(0)

        # ── DATOS PERSONALES ──
        root.addWidget(self._section_header(trf("student.form.personal_data", "DATOS PERSONALES")))
        root.addSpacing(12)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(12)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        self.inp_first = QLineEdit()
        self.inp_first.setPlaceholderText("Nombre")
        self.inp_first.setStyleSheet(FIELD_STYLE)

        self.inp_last = QLineEdit()
        self.inp_last.setPlaceholderText("Apellido")
        self.inp_last.setStyleSheet(FIELD_STYLE)

        grid.addWidget(_lbl("Nombre *"),   0, 0)
        grid.addWidget(_lbl("Apellido *"), 0, 1)
        grid.addWidget(self.inp_first,     1, 0)
        grid.addWidget(self.inp_last,      1, 1)

        self.inp_email = QLineEdit()
        self.inp_email.setPlaceholderText("correo@ejemplo.com")
        self.inp_email.setStyleSheet(FIELD_STYLE)
        grid.addWidget(_lbl("Email"), 2, 0, 1, 2)
        grid.addWidget(self.inp_email, 3, 0, 1, 2)

        # Profession (conditional ADULT)
        self._profession_container = QWidget()
        self._profession_container.setStyleSheet("QWidget { background: transparent; border: none; }")
        profession_layout = QVBoxLayout(self._profession_container)
        profession_layout.setContentsMargins(0, 0, 0, 0)
        profession_layout.setSpacing(6)
        self.inp_profession = QLineEdit()
        self.inp_profession.setPlaceholderText("Profesión / ocupación")
        self.inp_profession.setStyleSheet(FIELD_STYLE)
        profession_layout.addWidget(_lbl("Profesión"))
        profession_layout.addWidget(self.inp_profession)
        grid.addWidget(self._profession_container, 4, 0, 1, 2)
        self._profession_container.hide()

        # Phone with prefix
        self.cmb_prefix = QComboBox()
        self.cmb_prefix.setFixedWidth(150)
        self.cmb_prefix.setStyleSheet(FIELD_STYLE)
        for flag, code, country in PHONE_PREFIXES:
            self.cmb_prefix.addItem(f"{flag}  {code}", code)
            self.cmb_prefix.setItemData(
                self.cmb_prefix.count() - 1, country, Qt.ItemDataRole.ToolTipRole
            )

        self.inp_phone = QLineEdit()
        self.inp_phone.setPlaceholderText("Número sin prefijo")
        self.inp_phone.setStyleSheet(FIELD_STYLE)

        phone_container = QWidget()
        phone_container.setStyleSheet("QWidget { background: transparent; border: none; }")
        phone_layout = QHBoxLayout(phone_container)
        phone_layout.setContentsMargins(0, 0, 0, 0)
        phone_layout.setSpacing(8)
        phone_layout.addWidget(self.cmb_prefix)
        phone_layout.addWidget(self.inp_phone, 1)

        grid.addWidget(_lbl("Teléfono"), 5, 0, 1, 2)
        grid.addWidget(phone_container,  6, 0, 1, 2)

        # Birth date
        self._birth_date = QDate.currentDate().addYears(-18)
        self.inp_birth = QLineEdit()
        self.inp_birth.setReadOnly(True)
        self.inp_birth.setText(self._birth_date.toString("dd / MM / yyyy"))
        self.inp_birth.setStyleSheet(FIELD_STYLE)

        btn_cal_birth = QPushButton()
        btn_cal_birth.setFixedSize(40, 40)
        btn_cal_birth.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cal_birth.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_INPUT};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
            QPushButton:hover {{
                border-color: {RED};
                background-color: {BG_HOVER};
            }}
        """)
        cal_icon = IconLabel("calendar", 18, TEXT_SEC)
        cal_icon_layout = QHBoxLayout(btn_cal_birth)
        cal_icon_layout.setContentsMargins(0, 0, 0, 0)
        cal_icon_layout.addWidget(cal_icon, 0, Qt.AlignmentFlag.AlignCenter)
        btn_cal_birth.clicked.connect(self._show_calendar)

        birth_row = QWidget()
        birth_row.setStyleSheet("QWidget { background: transparent; border: none; }")
        birth_hl = QHBoxLayout(birth_row)
        birth_hl.setContentsMargins(0, 0, 0, 0)
        birth_hl.setSpacing(8)
        birth_hl.addWidget(self.inp_birth, 1)
        birth_hl.addWidget(btn_cal_birth)

        # Joined date
        self._joined_date = QDate.currentDate()
        self.inp_joined = QLineEdit()
        self.inp_joined.setReadOnly(True)
        self.inp_joined.setText(self._joined_date.toString("dd / MM / yyyy"))
        self.inp_joined.setStyleSheet(FIELD_STYLE)

        btn_cal_joined = QPushButton()
        btn_cal_joined.setFixedSize(40, 40)
        btn_cal_joined.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cal_joined.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_INPUT};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
            QPushButton:hover {{
                border-color: {RED};
                background-color: {BG_HOVER};
            }}
        """)
        cal_icon2 = IconLabel("calendar", 18, TEXT_SEC)
        cal_icon2_layout = QHBoxLayout(btn_cal_joined)
        cal_icon2_layout.setContentsMargins(0, 0, 0, 0)
        cal_icon2_layout.addWidget(cal_icon2, 0, Qt.AlignmentFlag.AlignCenter)
        btn_cal_joined.clicked.connect(self._show_calendar_joined)

        joined_row = QWidget()
        joined_row.setStyleSheet("QWidget { background: transparent; border: none; }")
        joined_hl = QHBoxLayout(joined_row)
        joined_hl.setContentsMargins(0, 0, 0, 0)
        joined_hl.setSpacing(8)
        joined_hl.addWidget(self.inp_joined, 1)
        joined_hl.addWidget(btn_cal_joined)

        grid.addWidget(_lbl("Fecha de nacimiento"), 7, 0)
        grid.addWidget(_lbl("Fecha de ingreso al dojo"), 7, 1)
        grid.addWidget(birth_row,  8, 0)
        grid.addWidget(joined_row, 8, 1)

        root.addLayout(grid)
        root.addSpacing(24)

        # ── INFORMACIÓN ACADÉMICA ──
        root.addWidget(self._section_header(trf("student.form.academic_info", "INFORMACIÓN ACADÉMICA")))
        root.addSpacing(12)

        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(16)
        grid2.setVerticalSpacing(12)
        grid2.setColumnStretch(0, 1)
        grid2.setColumnStretch(1, 1)

        self.cmb_doctype  = QComboBox(); self.cmb_doctype.setStyleSheet(FIELD_STYLE)
        self.inp_doc      = QLineEdit(); self.inp_doc.setPlaceholderText("Número"); self.inp_doc.setStyleSheet(FIELD_STYLE)
        self.cmb_status   = QComboBox(); self.cmb_status.setStyleSheet(FIELD_STYLE)
        self.cmb_category = QComboBox(); self.cmb_category.setStyleSheet(FIELD_STYLE)

        grid2.addWidget(_lbl("Tipo documento"), 0, 0)
        grid2.addWidget(_lbl("Nº Documento"),   0, 1)
        grid2.addWidget(self.cmb_doctype,        1, 0)
        grid2.addWidget(self.inp_doc,            1, 1)
        grid2.addWidget(_lbl("Estado"),          2, 0)
        grid2.addWidget(_lbl("Categoría *"),       2, 1)
        grid2.addWidget(self.cmb_status,         3, 0)
        grid2.addWidget(self.cmb_category,       3, 1)

        root.addLayout(grid2)
        root.addSpacing(24)

        # ── DIRECCIÓN, RESIDENCIA Y UBICACIÓN ──
        root.addWidget(self._section_header(trf("student.form.residence", "DIRECCIÓN, RESIDENCIA Y UBICACIÓN")))
        root.addSpacing(12)

        addr_grid = QGridLayout()
        addr_grid.setHorizontalSpacing(16)
        addr_grid.setVerticalSpacing(12)
        addr_grid.setColumnStretch(0, 1)
        addr_grid.setColumnStretch(1, 1)

        # Address builder trigger (replaces plain QLineEdit)
        self.inp_address = QLineEdit()
        self.inp_address.setVisible(False)  # Hidden — used as backing store

        self._address_trigger = self._make_address_trigger()
        addr_grid.addWidget(_lbl("Dirección *"), 0, 0, 1, 2)
        addr_grid.addWidget(self._address_trigger, 1, 0, 1, 2)

        self.inp_residence_details = QTextEdit()
        self.inp_residence_details.setObjectName("residenceDetailsInput")
        self.inp_residence_details.setPlaceholderText(
            "Ej: casa color blanco, segundo piso, edificio, torre, apto, referencia cercana..."
        )
        self.inp_residence_details.setStyleSheet(f"""
            QTextEdit#residenceDetailsInput {{
                background-color: {BG_INPUT};
                color: {TEXT_PRI};
                border: 1.5px solid {BORDER};
                border-radius: 10px;
                padding: 10px 14px;
                font-size: 13px;
                font-weight: 500;
                font-family: 'Inter';
                min-height: 82px;
                max-height: 96px;
            }}
            QTextEdit#residenceDetailsInput:hover {{
                border-color: {TEXT_DIM};
            }}
            QTextEdit#residenceDetailsInput:focus {{
                border-color: {RED};
                background-color: {BG_HOVER};
            }}
        """)

        self.inp_neighborhood = QLineEdit()
        self.inp_neighborhood.setPlaceholderText("Barrio")
        self.inp_neighborhood.setStyleSheet(FIELD_STYLE)

        self.cmb_stratum = QComboBox()
        self.cmb_stratum.setStyleSheet(FIELD_STYLE)
        self.cmb_stratum.addItem("Seleccionar...", None)
        for i in range(1, 7):
            self.cmb_stratum.addItem(f"Estrato {i}", i)

        self.cmb_res_country = _SearchableCombo()
        self.cmb_res_city    = _SearchableCombo()
        self.cmb_birth_country = _SearchableCombo()
        self.cmb_birth_city    = _SearchableCombo()

        addr_grid.addWidget(_lbl("Especificaciones de residencia"), 2, 0, 1, 2)
        addr_grid.addWidget(self.inp_residence_details, 3, 0, 1, 2)
        addr_grid.addWidget(_lbl("Barrio"), 4, 0)
        addr_grid.addWidget(_lbl("Estrato socioeconómico"), 4, 1)
        addr_grid.addWidget(self.inp_neighborhood, 5, 0)
        addr_grid.addWidget(self.cmb_stratum, 5, 1)
        addr_grid.addWidget(_lbl("País de residencia"), 6, 0)
        addr_grid.addWidget(_lbl("Ciudad de residencia"), 6, 1)
        addr_grid.addWidget(self.cmb_res_country, 7, 0)
        addr_grid.addWidget(self.cmb_res_city, 7, 1)
        addr_grid.addWidget(_lbl("País de nacimiento"), 8, 0)
        addr_grid.addWidget(_lbl("Ciudad de nacimiento"), 8, 1)
        addr_grid.addWidget(self.cmb_birth_country, 9, 0)
        addr_grid.addWidget(self.cmb_birth_city, 9, 1)

        self.cmb_res_country.currentTextChanged.connect(
            lambda txt: self._on_country_changed(txt, self.cmb_res_city, "residence")
        )
        self.cmb_birth_country.currentTextChanged.connect(
            lambda txt: self._on_country_changed(txt, self.cmb_birth_city, "birth")
        )

        root.addLayout(addr_grid)
        root.addSpacing(24)

        # ── ESCUELA (solo KID/YOUTH) ──
        self._school_container = QWidget()
        self._school_container.setStyleSheet("background: transparent; border: none;")
        sc_root = QVBoxLayout(self._school_container)
        sc_root.setContentsMargins(0, 0, 0, 0)
        sc_root.setSpacing(0)
        sc_root.addWidget(self._section_header(trf("student.form.school", "ESCUELA")))
        sc_root.addSpacing(12)

        school_grid = QGridLayout()
        school_grid.setHorizontalSpacing(16)
        school_grid.setVerticalSpacing(12)
        school_grid.setColumnStretch(0, 1)
        school_grid.setColumnStretch(1, 1)

        self.inp_school = QLineEdit()
        self.inp_school.setPlaceholderText("Nombre del colegio / escuela")
        self.inp_school.setStyleSheet(FIELD_STYLE)

        school_grid.addWidget(_lbl("Nombre del colegio"), 0, 0, 1, 2)
        school_grid.addWidget(self.inp_school, 1, 0, 1, 2)
        sc_root.addLayout(school_grid)
        sc_root.addSpacing(24)
        root.addWidget(self._school_container)

        # ── ACUDIENTE ──
        self._guardian_container = QWidget()
        self._guardian_container.setStyleSheet("background: transparent; border: none;")
        gc_root = QVBoxLayout(self._guardian_container)
        gc_root.setContentsMargins(0, 0, 0, 0)
        gc_root.setSpacing(0)
        gc_root.addWidget(self._section_header(trf("student.form.guardian", "ACUDIENTE")))
        gc_root.addSpacing(12)

        guardian_grid = QGridLayout()
        guardian_grid.setHorizontalSpacing(16)
        guardian_grid.setVerticalSpacing(12)
        guardian_grid.setColumnStretch(0, 1)
        guardian_grid.setColumnStretch(1, 1)

        self.inp_guardian_name = QLineEdit()
        self.inp_guardian_name.setPlaceholderText("Nombre completo del acudiente")
        self.inp_guardian_name.setStyleSheet(FIELD_STYLE)

        self.inp_guardian_doc = QLineEdit()
        self.inp_guardian_doc.setPlaceholderText("Documento de identidad")
        self.inp_guardian_doc.setStyleSheet(FIELD_STYLE)

        self.inp_guardian_phone = QLineEdit()
        self.inp_guardian_phone.setPlaceholderText("Teléfono del acudiente")
        self.inp_guardian_phone.setStyleSheet(FIELD_STYLE)

        self.inp_guardian_email = QLineEdit()
        self.inp_guardian_email.setPlaceholderText("Email del acudiente")
        self.inp_guardian_email.setStyleSheet(FIELD_STYLE)

        self.cmb_guardian_rel = QComboBox()
        self.cmb_guardian_rel.setEditable(True)
        self.cmb_guardian_rel.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.cmb_guardian_rel.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.cmb_guardian_rel.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.cmb_guardian_rel.setStyleSheet(FIELD_STYLE)
        for rel in GUARDIAN_RELATIONSHIPS:
            self.cmb_guardian_rel.addItem(rel)

        self.inp_guardian_profession = QLineEdit()
        self.inp_guardian_profession.setPlaceholderText("Profesión / ocupación")
        self.inp_guardian_profession.setStyleSheet(FIELD_STYLE)

        guardian_grid.addWidget(_lbl("Nombre completo *"), 0, 0, 1, 2)
        guardian_grid.addWidget(self.inp_guardian_name, 1, 0, 1, 2)
        guardian_grid.addWidget(_lbl("Documento"), 2, 0)
        guardian_grid.addWidget(_lbl("Teléfono *"), 2, 1)
        guardian_grid.addWidget(self.inp_guardian_doc, 3, 0)
        guardian_grid.addWidget(self.inp_guardian_phone, 3, 1)
        guardian_grid.addWidget(_lbl("Parentesco *"), 4, 0)
        guardian_grid.addWidget(_lbl("Profesión"), 4, 1)
        guardian_grid.addWidget(self.cmb_guardian_rel, 5, 0)
        guardian_grid.addWidget(self.inp_guardian_profession, 5, 1)
        guardian_grid.addWidget(_lbl("Email"), 6, 0, 1, 2)
        guardian_grid.addWidget(self.inp_guardian_email, 7, 0, 1, 2)

        gc_root.addLayout(guardian_grid)
        gc_root.addSpacing(24)
        root.addWidget(self._guardian_container)

        # ── CONTACTO DE EMERGENCIA ──
        self._emerg_container = QWidget()
        self._emerg_container.setStyleSheet("background: transparent; border: none;")
        ec_root = QVBoxLayout(self._emerg_container)
        ec_root.setContentsMargins(0, 0, 0, 0)
        ec_root.setSpacing(0)
        ec_root.addWidget(self._section_header(trf("student.form.emergency", "CONTACTO DE EMERGENCIA")))
        ec_root.addSpacing(12)

        emerg_grid = QGridLayout()
        emerg_grid.setHorizontalSpacing(16)
        emerg_grid.setVerticalSpacing(12)
        emerg_grid.setColumnStretch(0, 1)
        emerg_grid.setColumnStretch(1, 1)

        self.inp_emerg_name = QLineEdit()
        self.inp_emerg_name.setPlaceholderText("Nombre completo")
        self.inp_emerg_name.setStyleSheet(FIELD_STYLE)

        self.inp_emerg_phone = QLineEdit()
        self.inp_emerg_phone.setPlaceholderText("Teléfono")
        self.inp_emerg_phone.setStyleSheet(FIELD_STYLE)

        self.inp_emerg_email = QLineEdit()
        self.inp_emerg_email.setPlaceholderText("Email")
        self.inp_emerg_email.setStyleSheet(FIELD_STYLE)

        self.inp_emerg_rel = QLineEdit()
        self.inp_emerg_rel.setPlaceholderText("Parentesco")
        self.inp_emerg_rel.setStyleSheet(FIELD_STYLE)

        self.inp_emerg_note = QLineEdit()
        self.inp_emerg_note.setPlaceholderText("Nota opcional")
        self.inp_emerg_note.setStyleSheet(FIELD_STYLE)

        emerg_grid.addWidget(_lbl("Nombre completo *"), 0, 0, 1, 2)
        emerg_grid.addWidget(self.inp_emerg_name, 1, 0, 1, 2)
        emerg_grid.addWidget(_lbl("Teléfono *"), 2, 0)
        emerg_grid.addWidget(_lbl("Parentesco"), 2, 1)
        emerg_grid.addWidget(self.inp_emerg_phone, 3, 0)
        emerg_grid.addWidget(self.inp_emerg_rel, 3, 1)
        emerg_grid.addWidget(_lbl("Email"), 4, 0)
        emerg_grid.addWidget(_lbl("Nota"), 4, 1)
        emerg_grid.addWidget(self.inp_emerg_email, 5, 0)
        emerg_grid.addWidget(self.inp_emerg_note, 5, 1)

        ec_root.addLayout(emerg_grid)
        ec_root.addSpacing(24)
        root.addWidget(self._emerg_container)

        # ── SALUD ──
        root.addWidget(self._section_header(trf("student.form.health", "INFORMACIÓN DE SALUD")))
        root.addSpacing(12)

        health_grid = QGridLayout()
        health_grid.setHorizontalSpacing(16)
        health_grid.setVerticalSpacing(12)
        health_grid.setColumnStretch(0, 1)
        health_grid.setColumnStretch(1, 1)

        self.inp_health_entity = QLineEdit()
        self.inp_health_entity.setPlaceholderText("Entidad de salud (EPS/IPS/etc)")
        self.inp_health_entity.setStyleSheet(FIELD_STYLE)

        # Compat aliases — any code referencing eps/ips maps to the same field
        self.inp_health_eps = self.inp_health_entity
        self.inp_health_ips = self.inp_health_entity

        self.cmb_health_blood = QComboBox()
        self.cmb_health_blood.setStyleSheet(FIELD_STYLE)
        for bt in BLOOD_TYPES:
            self.cmb_health_blood.addItem(bt if bt else "Seleccionar...", bt if bt else None)

        self.inp_health_allergies = QLineEdit()
        self.inp_health_allergies.setPlaceholderText("Alergias")
        self.inp_health_allergies.setStyleSheet(FIELD_STYLE)

        self.inp_health_conditions = QLineEdit()
        self.inp_health_conditions.setPlaceholderText("Condiciones médicas")
        self.inp_health_conditions.setStyleSheet(FIELD_STYLE)

        self.inp_health_notes = QLineEdit()
        self.inp_health_notes.setPlaceholderText("Notas adicionales de salud")
        self.inp_health_notes.setStyleSheet(FIELD_STYLE)

        health_grid.addWidget(_lbl("Entidad de salud"), 0, 0)
        health_grid.addWidget(_lbl("Tipo de sangre"), 0, 1)
        health_grid.addWidget(self.inp_health_entity, 1, 0)
        health_grid.addWidget(self.cmb_health_blood, 1, 1)
        health_grid.addWidget(_lbl("Alergias"), 2, 0)
        health_grid.addWidget(_lbl("Condiciones médicas"), 2, 1)
        health_grid.addWidget(self.inp_health_allergies, 3, 0)
        health_grid.addWidget(self.inp_health_conditions, 3, 1)
        health_grid.addWidget(_lbl("Notas de salud"), 4, 0, 1, 2)
        health_grid.addWidget(self.inp_health_notes, 5, 0, 1, 2)

        # Nota instructiva
        _health_hint = QLabel(
            "Si el estudiante no tiene alergias, condiciones médicas ni notas de salud, "
            "deja esos campos en blanco."
        )
        _health_hint.setWordWrap(True)
        _health_hint.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 10px;
            font-weight: 600;
            font-family: 'Inter';
            background: transparent;
            border: none;
            padding: 2px 0;
        """)
        health_grid.addWidget(_health_hint, 6, 0, 1, 2)

        root.addLayout(health_grid)
        root.addSpacing(24)

        # ── DOCUMENTOS ──
        root.addWidget(self._section_header(trf("student.form.documents", "DOCUMENTOS")))
        root.addSpacing(12)

        doc_grid = QGridLayout()
        doc_grid.setHorizontalSpacing(16)
        doc_grid.setVerticalSpacing(12)
        doc_grid.setColumnStretch(0, 1)
        doc_grid.setColumnStretch(1, 1)

        self.cmb_doc_type = QComboBox()
        self.cmb_doc_type.setStyleSheet(FIELD_STYLE)
        self.cmb_doc_type.addItem("Seleccionar tipo...", None)
        self.cmb_doc_type.addItem("Foto carnet", "carnet_photo")
        self.cmb_doc_type.addItem("Certificado EPS", "eps_certificate")
        self.cmb_doc_type.addItem("Documento de identidad", "identity_document")

        self.lbl_doc_path = QLabel("Ningún archivo seleccionado")
        self.lbl_doc_path.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; font-weight: 600;")

        btn_upload = QPushButton("📎  Subir archivo")
        btn_upload.setFixedHeight(38)
        btn_upload.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_upload.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_INPUT}; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 10px;
                font-size: 12px; font-weight: 700;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                border-color: {RED};
                background-color: {BG_HOVER};
            }}
        """)
        btn_upload.clicked.connect(self._on_upload_document)

        doc_grid.addWidget(_lbl("Tipo de documento"), 0, 0, 1, 2)
        doc_grid.addWidget(self.cmb_doc_type, 1, 0, 1, 2)
        doc_grid.addWidget(_lbl("Archivo"), 2, 0)
        doc_grid.addWidget(self.lbl_doc_path, 2, 1)
        doc_grid.addWidget(btn_upload, 3, 0, 1, 2)

        self.lst_documents = QListWidget()
        self.lst_documents.setStyleSheet(f"""
            QListWidget {{
                background-color: {BG_INPUT};
                border: 1px solid {BORDER};
                border-radius: 10px;
                color: {TEXT_PRI};
                font-size: 12px;
                padding: 4px;
                min-height: 80px;
                max-height: 120px;
            }}
            QListWidget::item {{
                padding: 8px 10px;
                border-bottom: 1px solid {BORDER_2};
            }}
            QListWidget::item:hover {{
                background-color: {BG_HOVER};
            }}
        """)

        doc_grid.addWidget(_lbl("Documentos cargados"), 4, 0, 1, 2)
        doc_grid.addWidget(self.lst_documents, 5, 0, 1, 2)

        btn_delete_doc = QPushButton()
        btn_delete_doc.setFixedHeight(36)
        btn_delete_doc.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete_doc.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {ERROR_C};
                border: 1px solid rgba(255,68,68,0.3); border-radius: 8px;
                font-size: 12px; font-weight: 700;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                background-color: rgba(255,68,68,0.10);
            }}
        """)
        _del_layout = QHBoxLayout(btn_delete_doc)
        _del_layout.setContentsMargins(12, 0, 12, 0)
        _del_layout.setSpacing(6)
        _del_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        _del_icon = IconLabel("trash", 14, ERROR_C)
        _del_lbl = QLabel("Eliminar seleccionado")
        _del_lbl.setStyleSheet(f"color: {ERROR_C}; font-size: 12px; font-weight: 700; background: transparent; border: none;")
        _del_layout.addWidget(_del_icon)
        _del_layout.addWidget(_del_lbl)
        btn_delete_doc.clicked.connect(self._on_delete_document)

        doc_grid.addWidget(btn_delete_doc, 6, 0, 1, 2)

        root.addLayout(doc_grid)
        root.addSpacing(24)

        # ── ACCESO ──
        root.addWidget(self._section_header(trf("student.form.access", "ACCESO DEL ESTUDIANTE"), badge="optional"))
        root.addSpacing(12)

        access_grid = QGridLayout()
        access_grid.setHorizontalSpacing(16)
        access_grid.setVerticalSpacing(12)
        access_grid.setColumnStretch(0, 1)
        access_grid.setColumnStretch(1, 1)

        self.inp_username = QLineEdit()
        self.inp_username.setPlaceholderText("Opcional. Si queda vacío se genera automático")
        self.inp_username.setStyleSheet(FIELD_STYLE)

        self.inp_password = QLineEdit()
        self.inp_password.setPlaceholderText(
            "Opcional. Si queda vacío usa el documento" if not self.is_edit else "Dejar vacío para no cambiar"
        )
        self.inp_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_password.setStyleSheet(FIELD_STYLE)

        access_grid.addWidget(_lbl("Usuario de acceso"), 0, 0)
        access_grid.addWidget(_lbl("Contraseña"), 0, 1)
        access_grid.addWidget(self.inp_username, 1, 0)
        access_grid.addWidget(self.inp_password, 1, 1)

        self._access_info = QLabel("")
        self._access_info.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 11px; font-weight: 600; font-family: 'Inter'; "
            f"border: none; padding: 6px 0;"
        )
        self._access_info.setWordWrap(True)
        self._access_info.hide()

        root.addLayout(access_grid)
        root.addWidget(self._access_info)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(f"color: {ERROR_C}; font-size: 12px; font-weight: 700;")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.hide()
        root.addWidget(self.lbl_error)
        root.addStretch()

        scroll.setWidget(container)
        outer.addWidget(scroll, 1)

        # ── Footer ──
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_DARK};
                border-top: 1px solid {BORDER_2};
            }}
        """)
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(28, 14, 28, 14)
        f_layout.setSpacing(10)

        f_layout.addStretch()

        btn_cancel = QPushButton(trf("student.form.cancel", "Cancelar"))
        btn_cancel.setFixedHeight(42)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SEC};
                border: 1px solid {BORDER};
                border-radius: 10px;
                font-size: 13px;
                font-weight: 800;
                padding: 0 20px;
                font-family: 'Inter';
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
                border-color: {TEXT_MUT};
                background: {BG_HOVER};
            }}
        """)
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton(trf("student.form.save", "Guardar Cambios") if self.is_edit else trf("student.form.create", "Crear Estudiante"))
        self.btn_save.setFixedHeight(42)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {RED_H}, stop:1 {RED});
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 800;
                padding: 0 24px;
                font-family: 'Inter';
            }}
            QPushButton:hover {{
                background: #FF2040;
            }}
            QPushButton:pressed {{
                background: #A00C24;
            }}
            QPushButton:disabled {{
                background: #3A1A1A;
                color: #666;
            }}
        """)
        save_shadow = QGraphicsDropShadowEffect(self.btn_save)
        save_shadow.setBlurRadius(16)
        save_shadow.setOffset(0, 4)
        save_shadow.setColor(QColor(200, 16, 46, 120))
        self.btn_save.setGraphicsEffect(save_shadow)
        self.btn_save.clicked.connect(self._save)

        f_layout.addWidget(btn_cancel)
        f_layout.addWidget(self.btn_save)
        outer.addWidget(footer)

    def _section_header(self, text, badge=None):
        """Section header with accent bar + title + optional badge."""
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Accent bar
        accent = QFrame()
        accent.setFixedSize(3, 16)
        accent.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {RED_H}, stop:1 {RED});
            border-radius: 2px;
            border: none;
        """)
        accent_shadow = QGraphicsDropShadowEffect(accent)
        accent_shadow.setBlurRadius(8)
        accent_shadow.setOffset(0, 0)
        accent_shadow.setColor(QColor(200, 16, 46, 120))
        accent.setGraphicsEffect(accent_shadow)
        layout.addWidget(accent)

        # Title
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {TEXT_SEC}; font-size: 11px; font-weight: 900; "
            f"font-family: 'Inter'; letter-spacing: 1.4px; border: none;"
        )
        layout.addWidget(lbl, 1)

        # Badge
        if badge == "conditional":
            b = QLabel("CONDICIONAL")
            b.setStyleSheet(f"""
                color: {YELLOW};
                background: rgba(234,179,8,0.10);
                border-radius: 5px;
                padding: 2px 8px;
                font-size: 9px;
                font-weight: 800;
                font-family: 'Inter';
                letter-spacing: 0.5px;
                border: none;
            """)
            layout.addWidget(b)
        elif badge == "optional":
            b = QLabel("OPCIONAL")
            b.setStyleSheet(f"""
                color: {TEXT_MUT};
                background: rgba(107,114,128,0.10);
                border-radius: 5px;
                padding: 2px 8px;
                font-size: 9px;
                font-weight: 800;
                font-family: 'Inter';
                letter-spacing: 0.5px;
                border: none;
            """)
            layout.addWidget(b)

        # Bottom border
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER_2}; border: none;")
        layout.addWidget(sep)

        # Re-layout: accent + title + badge on first row, sep on second
        # Actually use a vertical layout for clean separator
        container2 = QWidget()
        container2.setStyleSheet("background: transparent; border: none;")
        vlayout = QVBoxLayout(container2)
        vlayout.setContentsMargins(0, 0, 0, 10)
        vlayout.setSpacing(8)
        vlayout.addWidget(container)
        vlayout.addWidget(sep)
        return container2

    def _make_address_trigger(self):
        """Creates the clickable address builder trigger widget."""
        trigger = QPushButton()
        trigger.setFixedHeight(56)
        trigger.setCursor(Qt.CursorShape.PointingHandCursor)
        trigger.setLayout(QHBoxLayout())
        trigger.layout().setContentsMargins(14, 12, 14, 12)
        trigger.layout().setSpacing(10)

        # Icon
        icon_frame = QFrame()
        icon_frame.setFixedSize(32, 32)
        icon_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(200,16,46,0.10);
                border-radius: 8px;
                border: none;
            }}
        """)
        icon_layout = QHBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_svg = IconLabel("pin", 18, RED)
        icon_layout.addWidget(icon_svg, 0, Qt.AlignmentFlag.AlignCenter)

        # Content
        content = QWidget()
        content.setStyleSheet("background: transparent; border: none;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)

        self._address_label = QLabel("DIRECCIÓN CONSTRUIDA")
        self._address_label.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 10px; font-weight: 800; "
            f"font-family: 'Inter'; letter-spacing: 0.6px; border: none;"
        )
        self._address_value = QLabel("Clic para construir dirección")
        self._address_value.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 13px; font-weight: 500; "
            f"font-family: 'Inter'; border: none;"
        )
        content_layout.addWidget(self._address_label)
        content_layout.addWidget(self._address_value)

        # Arrow
        arrow = QLabel("›")
        arrow.setFixedSize(20, 20)
        arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        arrow.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 20px; font-weight: 900; "
            f"font-family: 'Inter'; border: none; background: transparent;"
        )

        trigger.layout().addWidget(icon_frame)
        trigger.layout().addWidget(content, 1)
        trigger.layout().addWidget(arrow)

        trigger.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_INPUT};
                border: 1px dashed {BORDER};
                border-radius: 10px;
                text-align: left;
            }}
            QPushButton:hover {{
                border-color: {RED};
                background-color: rgba(200,16,46,0.04);
            }}
            QPushButton * {{
                background: transparent;
                border: none;
            }}
        """)

        trigger.clicked.connect(self._open_address_builder)
        return trigger

    def _open_address_builder(self):
        """Opens the AddressBuilder modal."""
        current = self.inp_address.text().strip()
        dlg = AddressBuilder(current_address=current, parent=self)
        if dlg.exec():
            address = dlg.get_address()
            self.inp_address.setText(address)
            self._update_address_display(address)

    def _update_address_display(self, address: str):
        """Updates the address trigger visual state."""
        if address:
            self._address_value.setText(address)
            self._address_value.setStyleSheet(
                f"color: {TEXT_PRI}; font-size: 13px; font-weight: 700; "
                f"font-family: 'Inter'; border: none;"
            )
            self._address_trigger.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(34,197,94,0.04);
                    border: 1px solid {GREEN};
                    border-radius: 10px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    border-color: {GREEN};
                    background-color: rgba(34,197,94,0.08);
                }}
            """)
            # Update icon frame to green
            icon_frame = self._address_trigger.layout().itemAt(0).widget()
            icon_frame.setStyleSheet(f"""
                QFrame {{
                    background: rgba(34,197,94,0.10);
                    border-radius: 8px;
                    border: none;
                }}
            """)
        else:
            self._address_value.setText("Clic para construir dirección")
            self._address_value.setStyleSheet(
                f"color: {TEXT_DIM}; font-size: 13px; font-weight: 500; "
                f"font-family: 'Inter'; border: none;"
            )
            self._address_trigger.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BG_INPUT};
                    border: 1px dashed {BORDER};
                    border-radius: 10px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    border-color: {RED};
                    background-color: rgba(200,16,46,0.04);
                }}
            """)
            icon_frame = self._address_trigger.layout().itemAt(0).widget()
            icon_frame.setStyleSheet(f"""
                QFrame {{
                    background: rgba(200,16,46,0.10);
                    border-radius: 8px;
                    border: none;
                }}
            """)

    # ── Combos ────────────────────────────────────────────────────────────
    def _load_combos(self):
        self.cmb_doctype.addItem("Seleccionar...", None)
        for doc_id, doc_name in self.repo.get_type_documents():
            self.cmb_doctype.addItem(doc_name, doc_id)

        self.cmb_status.addItem("Seleccionar...", None)
        for st_id, st_name in self.repo.get_statuses():
            self.cmb_status.addItem(st_name, st_id)

        self.cmb_category.addItem("Seleccionar...", None)
        self._category_map = {}
        for cat_id, cat_name in self.repo.get_categories():
            self.cmb_category.addItem(cat_name, cat_id)
            self._category_map[cat_id] = cat_name
        self.cmb_category.currentIndexChanged.connect(self._on_category_changed)

        countries = self._lookups.get("countries_cities", {})
        for country_name in countries:
            self.cmb_res_country.addItem(country_name)
            self.cmb_birth_country.addItem(country_name)

    def _on_category_changed(self):
        cat_name = self.cmb_category.currentText().upper()

        is_adult_or_scholarship = cat_name.startswith("ADULT") or cat_name.startswith("SCHOLARSHIP")
        if hasattr(self, "_profession_container"):
            self._profession_container.setVisible(is_adult_or_scholarship)

        is_minor = cat_name.startswith("KID") or cat_name.startswith("YOUTH")
        self._school_container.setVisible(is_minor)
        self._guardian_container.setVisible(is_minor)
        self._emerg_container.setVisible(not is_minor)

        is_kid = cat_name.startswith("KID")
        self.inp_email.setEnabled(not is_kid)
        self.inp_phone.setEnabled(not is_kid)
        self.cmb_prefix.setEnabled(not is_kid)

        if is_kid:
            self._access_info.setText(
                "Menores de edad no reciben acceso al sistema. El acceso es gestionado por el acudiente."
            )
            self._access_info.setStyleSheet(
                f"color: {YELLOW}; font-size: 11px; font-weight: 600; font-family: 'Inter'; "
                f"background: rgba(234,179,8,0.08); border: 1px solid rgba(234,179,8,0.20); "
                f"border-radius: 6px; padding: 8px 12px;"
            )
            self._access_info.show()
            self.inp_username.setEnabled(False)
            self.inp_password.setEnabled(False)
        else:
            self._access_info.hide()
            self.inp_username.setEnabled(True)
            self.inp_password.setEnabled(True)

    def _on_country_changed(self, country_name, city_combo, prefix):
        city_combo.clear()
        if not country_name:
            return
        countries = self._lookups.get("countries_cities", {})
        cities = countries.get(country_name, [])
        for city in cities:
            city_combo.addItem(city)

    # ── Calendar ──────────────────────────────────────────────────────────
    def _show_calendar(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Fecha de nacimiento")
        dlg.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        dlg.setStyleSheet(f"background-color: {BG_CARD}; color: {TEXT_PRI};")
        dlg.setFixedSize(340, 300)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        cal = QCalendarWidget()
        cal.setStyleSheet(CAL_STYLE)
        cal.setGridVisible(False)
        cal.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        cal.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        cal.setMaximumDate(QDate.currentDate())
        cal.setSelectedDate(self._birth_date)

        fmt_weekend = QTextCharFormat()
        fmt_weekend.setForeground(QColor(RED))
        cal.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, fmt_weekend)
        cal.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, fmt_weekend)

        btn_ok = QPushButton("Confirmar")
        btn_ok.setFixedHeight(38)
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {RED_H}, stop:1 {RED});
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 800;
                font-family: 'Inter';
            }}
            QPushButton:hover {{ background: #FF2040; }}
        """)

        def confirm():
            self._birth_date = cal.selectedDate()
            self.inp_birth.setText(self._birth_date.toString("dd / MM / yyyy"))
            dlg.accept()

        btn_ok.clicked.connect(confirm)
        cal.activated.connect(lambda _: confirm())

        layout.addWidget(cal)
        layout.addWidget(btn_ok)
        dlg.exec()

    def _show_calendar_joined(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Fecha de ingreso")
        dlg.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        dlg.setStyleSheet(f"background-color: {BG_CARD}; color: {TEXT_PRI};")
        dlg.setFixedSize(340, 300)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        cal = QCalendarWidget()
        cal.setStyleSheet(CAL_STYLE)
        cal.setGridVisible(False)
        cal.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        cal.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        cal.setSelectedDate(self._joined_date)

        fmt_weekend = QTextCharFormat()
        fmt_weekend.setForeground(QColor(RED))
        cal.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, fmt_weekend)
        cal.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, fmt_weekend)

        btn_ok = QPushButton("Confirmar")
        btn_ok.setFixedHeight(38)
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {RED_H}, stop:1 {RED});
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 800;
                font-family: 'Inter';
            }}
            QPushButton:hover {{ background: #FF2040; }}
        """)

        def confirm():
            self._joined_date = cal.selectedDate()
            self.inp_joined.setText(self._joined_date.toString("dd / MM / yyyy"))
            dlg.accept()

        btn_ok.clicked.connect(confirm)
        cal.activated.connect(lambda _: confirm())

        layout.addWidget(cal)
        layout.addWidget(btn_ok)
        dlg.exec()

    # ── Cargar datos (edición) ────────────────────────────────────────────
    def _load_student(self):
        data = self.repo.get_by_id(self.student_id)
        if not data:
            return

        self.inp_first.setText(data["first_name"] or "")
        self.inp_last.setText(data["last_name"] or "")
        self.inp_email.setText(data["email"] or "")

        if hasattr(self, "inp_profession"):
            self.inp_profession.setText(data.get("profession") or "")

        phone = data.get("phone") or ""
        matched = False
        for i, (_, code, _) in enumerate(PHONE_PREFIXES):
            if phone.startswith(code):
                self.cmb_prefix.setCurrentIndex(i)
                self.inp_phone.setText(phone[len(code):].strip())
                matched = True
                break
        if not matched:
            self.inp_phone.setText(phone)

        if data["birthdate"]:
            d = data["birthdate"]
            self._birth_date = QDate(d.year, d.month, d.day)
            self.inp_birth.setText(self._birth_date.toString("dd / MM / yyyy"))

        if data.get("joined_date"):
            d = data["joined_date"]
            self._joined_date = QDate(d.year, d.month, d.day)
            self.inp_joined.setText(self._joined_date.toString("dd / MM / yyyy"))

        self.inp_doc.setText(data["document"] or "")

        for i in range(self.cmb_doctype.count()):
            if self.cmb_doctype.itemData(i) == data["id_type_document"]:
                self.cmb_doctype.setCurrentIndex(i); break

        for i in range(self.cmb_status.count()):
            if self.cmb_status.itemData(i) == data["id_status"]:
                self.cmb_status.setCurrentIndex(i); break

        for i in range(self.cmb_category.count()):
            if self.cmb_category.itemData(i) == data["category_id"]:
                self.cmb_category.setCurrentIndex(i); break

        # Address: load into hidden field + update trigger display
        address = data.get("address_line") or ""
        self.inp_address.setText(address)
        self._update_address_display(address)

        if hasattr(self, "inp_residence_details"):
            self.inp_residence_details.setPlainText(data.get("residence_details") or "")

        self.inp_neighborhood.setText(data.get("neighborhood") or "")

        stratum = data.get("socioeconomic_stratum")
        if stratum is not None:
            for i in range(self.cmb_stratum.count()):
                if self.cmb_stratum.itemData(i) == stratum:
                    self.cmb_stratum.setCurrentIndex(i)
                    break

        self._set_combo_text(self.cmb_res_country, data.get("residence_country") or "")
        self._set_combo_text(self.cmb_res_city, data.get("residence_city") or "")
        self._set_combo_text(self.cmb_birth_country, data.get("birth_country") or "")
        self._set_combo_text(self.cmb_birth_city, data.get("birth_city") or "")

        self.inp_school.setText(data.get("school_name") or "")

        try:
            guardian = self.repo.get_primary_guardian(self.student_id)
            if guardian:
                self.inp_guardian_name.setText(guardian.get("full_name") or "")
                self.inp_guardian_doc.setText(guardian.get("document") or "")
                self.inp_guardian_phone.setText(guardian.get("phone") or "")
                self.inp_guardian_email.setText(guardian.get("email") or "")
                self._set_combo_text(self.cmb_guardian_rel, guardian.get("relationship") or "")
                self.inp_guardian_profession.setText(guardian.get("profession") or "")
        except Exception:
            pass

        try:
            emerg = self.repo.get_primary_emergency_contact(self.student_id)
            if emerg:
                self.inp_emerg_name.setText(emerg.get("full_name") or "")
                self.inp_emerg_phone.setText(emerg.get("phone") or "")
                self.inp_emerg_email.setText(emerg.get("email") or "")
                self.inp_emerg_rel.setText(emerg.get("relationship") or "")
                self.inp_emerg_note.setText(emerg.get("note") or "")
        except Exception:
            pass

        try:
            health = self.repo.get_health_info(self.student_id)
            if health:
                self.inp_health_eps.setText(health.get("eps") or "")
                self.inp_health_ips.setText(health.get("ips") or "")
                blood = health.get("blood_type") or ""
                for i in range(self.cmb_health_blood.count()):
                    if self.cmb_health_blood.itemData(i) == blood:
                        self.cmb_health_blood.setCurrentIndex(i)
                        break
                self.inp_health_allergies.setText(health.get("allergies") or "")
                self.inp_health_conditions.setText(health.get("medical_conditions") or "")
                self.inp_health_notes.setText(health.get("notes") or "")
        except Exception:
            pass

        try:
            docs = self.repo.get_student_documents(self.student_id)
            self._student_documents_data = docs
            self._refresh_doc_list()
        except Exception:
            pass

        user = self.repo.get_user_by_student_id(self.student_id)
        if user:
            self.inp_username.setText(user.get("username") or "")

    def _set_combo_text(self, combo, text):
        idx = combo.findText(text, Qt.MatchFlag.MatchFixedString)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        else:
            combo.setEditText(text)

    # ── Document upload ───────────────────────────────────────────────────
    def _on_upload_document(self):
        doc_type = self.cmb_doc_type.currentData()
        if not doc_type:
            self._show_toast(trf("student.form.error.select_doc_type", "Selecciona un tipo de documento."), "warning")
            return

        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo", "",
            "Archivos permitidos (*.png *.jpg *.jpeg *.pdf *.doc *.docx)"
        )
        if not path:
            return

        ext = os.path.splitext(path)[1].lower()
        allowed = (".png", ".jpg", ".jpeg", ".pdf", ".doc", ".docx")
        if ext not in allowed:
            self._show_toast(trf("student.form.error.invalid_file_type", "Tipo de archivo no permitido."), "error")
            return

        # Agregar a la lista en memoria para que se vea YA
        doc_type_labels = {
            "carnet_photo": "Foto carnet",
            "eps_certificate": "Certificado EPS",
            "identity_document": "Documento de identidad",
        }
        self._pending_doc = {"doc_type": doc_type, "path": path}

        # Mostrar en lista inmediatamente (id=None porque aun no esta guardado)
        self._student_documents_data.append({
            "id": None,
            "doc_type": doc_type_labels.get(doc_type, doc_type),
            "file_path": path,
            "_pending": True,
        })
        self._refresh_doc_list()
        self.lbl_doc_path.setText(os.path.basename(path))
        self._show_toast(f"Archivo listo: {os.path.basename(path)}", "success")

    def _refresh_doc_list(self):
        self.lst_documents.clear()
        for doc in self._student_documents_data:
            doc_type_name = doc.get("doc_type") or "—"
            file_path = doc.get("file_path") or ""
            file_name = os.path.basename(file_path)
            sym, color = _doc_icon_for_file(file_name)

            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, doc.get("id"))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            w = QWidget()
            w.setStyleSheet("background: transparent; border: none;")
            hl = QHBoxLayout(w)
            hl.setContentsMargins(8, 6, 8, 6)
            hl.setSpacing(8)

            badge = QLabel(sym)
            badge.setFixedSize(36, 22)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setStyleSheet(f"""
                QLabel {{
                    color: {color}; background: transparent;
                    border: 1px solid {color}; border-radius: 4px;
                    font-size: 9px; font-weight: 900; font-family: 'Inter';
                }}
            """)

            lbl_type = QLabel(f"{doc_type_name}")
            lbl_type.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 700; border: none; background: transparent;")
            lbl_type.setFixedWidth(110)

            lbl_name = QLabel(file_name or "—")
            lbl_name.setStyleSheet(f"color: {TEXT_PRI}; font-size: 11px; font-weight: 600; border: none; background: transparent;")
            lbl_name.setMinimumWidth(0)

            # Indicador pending
            if doc.get("_pending"):
                lbl_pend = QLabel("• nuevo")
                lbl_pend.setStyleSheet(f"color: {GREEN}; font-size: 9px; font-weight: 800; border: none; background: transparent;")
                hl.addWidget(lbl_pend)

            hl.addWidget(badge)
            hl.addWidget(lbl_type)
            hl.addWidget(lbl_name, 1)

            w.setFixedHeight(36)
            item.setSizeHint(w.sizeHint().__class__(self.lst_documents.width(), 36))
            self.lst_documents.addItem(item)
            self.lst_documents.setItemWidget(item, w)

    def _on_delete_document(self):
        item = self.lst_documents.currentItem()
        if not item:
            self._show_toast(trf("student.form.error.select_doc", "Selecciona un documento de la lista."), "warning")
            return
        doc_id = item.data(Qt.ItemDataRole.UserRole)

        # Si es un pending (id=None), solo eliminarlo de la lista en memoria
        if doc_id is None:
            row = self.lst_documents.currentRow()
            pending_idx = None
            for i, d in enumerate(self._student_documents_data):
                if d.get("_pending") and d.get("id") is None:
                    pending_idx = i
                    break
            if pending_idx is not None:
                self._student_documents_data.pop(pending_idx)
            self._pending_doc = None
            self._refresh_doc_list()
            self._show_toast("Archivo eliminado de la lista.", "info")
            return

        try:
            self.repo.delete_student_document(doc_id)
            self._student_documents_data = [d for d in self._student_documents_data if d.get("id") != doc_id]
            self._refresh_doc_list()
            self._show_toast("Documento eliminado.", "success")
        except Exception as e:
            self._show_toast(f"Error al eliminar: {e}", "error")

    def _show_toast(self, message: str, kind: str = "success"):
        """Muestra un toast usando el toast_manager global (core/toast.py)."""
        try:
            from core.toast import toast_manager
            if toast_manager._layer:
                toast_manager.show(message, kind)
            else:
                win = self.window()
                toast_manager.attach(win)
                toast_manager.show(message, kind)
        except Exception:
            pass

    # ── Instrucciones ────────────────────────────────────────────────────
    def _open_instructions(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Instrucciones del formulario")
        dlg.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        dlg.setMinimumSize(780, 620)
        dlg.setStyleSheet(f"background-color: {BG_DARK}; color: {TEXT_PRI};")

        outer = QVBoxLayout(dlg)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(64)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_DARK};
                border-bottom: 1px solid {BORDER_2};
            }}
        """)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(24, 0, 24, 0)
        hl.setSpacing(12)

        icon_frame = QFrame()
        icon_frame.setFixedSize(36, 36)
        icon_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(59,130,246,0.12);
                border: 1px solid rgba(59,130,246,0.30);
                border-radius: 10px;
            }}
        """)
        icon_layout = QHBoxLayout(icon_frame)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel("ℹ")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"color: {BLUE}; font-size: 16px; font-weight: 900; border: none;")
        icon_layout.addWidget(icon_lbl)
        hl.addWidget(icon_frame)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        t = QLabel("Guía completa del formulario de estudiantes")
        t.setStyleSheet(f"color: {TEXT_PRI}; font-size: 15px; font-weight: 900; font-family: 'Inter'; border: none;")
        s = QLabel("Cómo llenar cada sección correctamente con ejemplos reales")
        s.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; font-weight: 600; border: none;")
        title_col.addWidget(t)
        title_col.addWidget(s)
        hl.addLayout(title_col, 1)

        btn_close = QPushButton("✕  Cerrar")
        btn_close.setFixedHeight(32)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUT};
                border: 1px solid {BORDER}; border-radius: 8px;
                font-size: 12px; font-weight: 700; padding: 0 14px;
            }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: {TEXT_SEC}; }}
        """)
        btn_close.clicked.connect(dlg.accept)
        hl.addWidget(btn_close)
        outer.addWidget(header)

        # Scroll con contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical { background: transparent; width: 6px; }
            QScrollBar::handle:vertical { background: #2A2A2A; border-radius: 3px; min-height: 20px; }
        """)

        content = QWidget()
        content.setStyleSheet(f"background-color: {BG_DARK};")
        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(28, 24, 28, 32)
        vbox.setSpacing(20)

        def _section(title, color, items):
            """Bloque de sección con título y lista de instrucciones + ejemplos."""
            frame = QFrame()
            frame.setStyleSheet(f"""
                QFrame {{
                    background: rgba(255,255,255,0.02);
                    border: 1px solid {BORDER};
                    border-left: 3px solid {color};
                    border-radius: 10px;
                }}
                QFrame QLabel {{ background: transparent; border: none; }}
            """)
            fl = QVBoxLayout(frame)
            fl.setContentsMargins(20, 16, 20, 16)
            fl.setSpacing(10)

            sec_title = QLabel(title)
            sec_title.setStyleSheet(
                f"color: {color}; font-size: 12px; font-weight: 900; "
                f"font-family: 'Inter'; letter-spacing: 0.8px;"
            )
            fl.addWidget(sec_title)

            for field, instruction, example in items:
                row = QFrame()
                row.setStyleSheet(f"""
                    QFrame {{
                        background: rgba(255,255,255,0.02);
                        border: 1px solid {BORDER_2};
                        border-radius: 8px;
                    }}
                    QFrame QLabel {{ background: transparent; border: none; }}
                """)
                rl = QVBoxLayout(row)
                rl.setContentsMargins(14, 10, 14, 10)
                rl.setSpacing(4)

                field_lbl = QLabel(f"● {field}")
                field_lbl.setStyleSheet(
                    f"color: {TEXT_PRI}; font-size: 12px; font-weight: 800; font-family: 'Inter';"
                )
                instr_lbl = QLabel(instruction)
                instr_lbl.setWordWrap(True)
                instr_lbl.setStyleSheet(
                    f"color: {TEXT_SEC}; font-size: 12px; font-weight: 500;"
                )
                ex_lbl = QLabel(f"Ejemplo:  {example}")
                ex_lbl.setWordWrap(True)
                ex_lbl.setStyleSheet(f"""
                    color: {GREEN};
                    font-size: 11px;
                    font-weight: 700;
                    font-family: 'Inter';
                    background: rgba(34,197,94,0.06);
                    border: 1px solid rgba(34,197,94,0.20);
                    border-radius: 6px;
                    padding: 4px 10px;
                """)

                rl.addWidget(field_lbl)
                rl.addWidget(instr_lbl)
                rl.addWidget(ex_lbl)
                fl.addWidget(row)

            return frame

        # ── Intro ──
        intro = QLabel(
            "Este formulario registra todos los datos de un estudiante del dojo. "
            "Los campos marcados con  ✱  son obligatorios. Lee cada sección con atención "
            "antes de guardar — un dato incorrecto puede afectar la categoría, "
            "los permisos de acceso y el contacto de emergencia del estudiante."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 13px;
            font-weight: 500;
            background: rgba(59,130,246,0.06);
            border: 1px solid rgba(59,130,246,0.18);
            border-radius: 10px;
            padding: 14px 18px;
        """)
        vbox.addWidget(intro)

        # ── Sección 1: Datos personales ──
        vbox.addWidget(_section(
            "1 · DATOS PERSONALES", RED, [
                (
                    "Nombre y Apellido  ✱",
                    "Escribe el nombre legal completo tal como aparece en el documento de identidad. "
                    "No uses apodos ni abreviaciones.",
                    "Nombre: Santiago   |   Apellido: Martínez Ríos"
                ),
                (
                    "Email",
                    "Dirección de correo electrónico activa. Se usará para notificaciones del dojo. "
                    "Si el estudiante es menor de edad, usar el email del acudiente.",
                    "santiago.martinez@gmail.com"
                ),
                (
                    "Teléfono",
                    "Selecciona el prefijo del país en el combo de bandera, luego escribe solo "
                    "el número sin el código de país ni espacios.",
                    "Prefijo: 🇨🇴 +57   |   Número: 3001234567"
                ),
                (
                    "Fecha de nacimiento",
                    "Haz clic en el ícono de calendario y selecciona la fecha exacta. "
                    "La categoría (KID / YOUTH / ADULT) se asigna según la edad.",
                    "15 / 03 / 2010  →  el sistema la clasificará como YOUTH"
                ),
                (
                    "Fecha de ingreso al dojo",
                    "Día en que el estudiante se matriculó oficialmente. "
                    "Por defecto es hoy, cámbiala si el ingreso fue en otra fecha.",
                    "01 / 08 / 2024"
                ),
            ]
        ))

        # ── Sección 2: Información académica ──
        vbox.addWidget(_section(
            "2 · INFORMACIÓN ACADÉMICA", BLUE, [
                (
                    "Tipo de documento",
                    "Selecciona el tipo de identificación del estudiante. "
                    "Para menores de edad usa Tarjeta de Identidad (TI). "
                    "Para adultos usa Cédula de Ciudadanía (CC).",
                    "TI  (Tarjeta de Identidad)  para menores  |  CC para mayores de 18"
                ),
                (
                    "Nº Documento",
                    "Escribe el número completo sin puntos, comas ni espacios.",
                    "1234567890"
                ),
                (
                    "Estado",
                    "Indica si el estudiante está activo, inactivo o suspendido. "
                    "Solo los activos pueden asistir a clases.",
                    "Activo"
                ),
                (
                    "Categoría  ✱",
                    "KID: menores de ~8 años — no tienen usuario propio, el acudiente gestiona el acceso.\n"
                    "YOUTH: entre ~8 y 17 años — requiere acudiente Y contacto de emergencia.\n"
                    "ADULT: 18 años o más — gestionan su propio acceso.",
                    "YOUTH  (estudiante de 14 años)"
                ),
                (
                    "Profesión",
                    "Solo visible para ADULT y SCHOLARSHIP. Registra la ocupación del estudiante. "
                    "Este dato es opcional pero útil para el perfil del dojo.",
                    "Ingeniero de sistemas  /  Estudiante universitario  /  Médico general"
                ),
            ]
        ))

        # ── Sección 3: Dirección y residencia ──
        vbox.addWidget(_section(
            "3 · DIRECCIÓN, RESIDENCIA Y UBICACIÓN", YELLOW, [
                (
                    "Dirección  ✱",
                    "Haz clic en «Construir dirección» para abrir el constructor SURED. "
                    "Completa tipo de vía, número y complemento. "
                    "El resultado se genera automáticamente en formato estándar colombiano.",
                    "CALLE 45 # 23-18"
                ),
                (
                    "Especificaciones de residencia",
                    "Información adicional que ayude a ubicar el inmueble: color, piso, "
                    "apartamento, torre, referencia cercana.",
                    "Casa color blanco, segunda planta, portón negro, frente al parque"
                ),
                (
                    "Barrio",
                    "Nombre del barrio o urbanización donde reside el estudiante.",
                    "El Poblado"
                ),
                (
                    "Estrato socioeconómico",
                    "Selecciona el estrato del 1 al 6 según el recibo de servicios públicos. "
                    "Si no lo sabes, déjalo en blanco.",
                    "Estrato 3"
                ),
                (
                    "País y ciudad de residencia",
                    "Selecciona primero el país; la lista de ciudades se actualizará automáticamente.",
                    "País: Colombia   |   Ciudad: Cali"
                ),
                (
                    "País y ciudad de nacimiento",
                    "Puede ser diferente a la ciudad de residencia. "
                    "Importante para el expediente oficial del estudiante.",
                    "País: Colombia   |   Ciudad: Medellín"
                ),
            ]
        ))

        # ── Sección 4: Acudiente ──
        vbox.addWidget(_section(
            "4 · ACUDIENTE  (obligatorio para KID y YOUTH)", PURPLE, [
                (
                    "Nombre completo del acudiente  ✱",
                    "Nombre legal de la persona responsable del menor. "
                    "Debe ser el mismo que firma los permisos y autorizaciones.",
                    "María Elena Ríos de Martínez"
                ),
                (
                    "Parentesco  ✱",
                    "Relación del acudiente con el estudiante. "
                    "Si ninguna opción aplica, selecciona OTRO.",
                    "MADRE"
                ),
                (
                    "Teléfono del acudiente  ✱",
                    "Número de contacto directo. Se usará para notificaciones urgentes "
                    "y para gestionar el acceso de los KID al sistema.",
                    "+57 3109876543"
                ),
                (
                    "Profesión del acudiente",
                    "Campo opcional. Útil para conocer el perfil familiar del estudiante.",
                    "Docente universitaria"
                ),
            ]
        ))

        # ── Sección 5: Contacto de emergencia ──
        vbox.addWidget(_section(
            "5 · CONTACTO DE EMERGENCIA  (obligatorio para YOUTH y ADULT)", f"#F97316", [
                (
                    "Nombre  ✱",
                    "Persona a contactar si ocurre una emergencia durante el entrenamiento. "
                    "Puede ser la misma persona que el acudiente o alguien diferente.",
                    "Carlos Alberto Martínez"
                ),
                (
                    "Teléfono  ✱",
                    "Número que siempre esté disponible. Preferiblemente celular.",
                    "+57 3187654321"
                ),
                (
                    "Relación",
                    "Parentesco o vínculo con el estudiante.",
                    "Padre"
                ),
                (
                    "Nota",
                    "Cualquier indicación importante: horario de disponibilidad, "
                    "idioma preferido, etc.",
                    "Disponible solo después de las 6 PM. Habla español e inglés."
                ),
            ]
        ))

        # ── Sección 6: Salud ──
        vbox.addWidget(_section(
            "6 · INFORMACIÓN DE SALUD", GREEN, [
                (
                    "EPS",
                    "Entidad Promotora de Salud a la que está afiliado el estudiante.",
                    "Sura  /  Nueva EPS  /  Sanitas"
                ),
                (
                    "Tipo de sangre",
                    "Grupo sanguíneo. Fundamental en caso de emergencia médica. "
                    "Si no lo sabes, déjalo en blanco y actualízalo luego.",
                    "O+"
                ),
                (
                    "Alergias",
                    "Lista las alergias conocidas separadas por coma. "
                    "Incluye alergias a medicamentos, alimentos o materiales.",
                    "Penicilina, látex, mariscos"
                ),
                (
                    "Condiciones médicas",
                    "Enfermedades crónicas, lesiones previas o condiciones que el instructor "
                    "debe conocer para adaptar el entrenamiento.",
                    "Asma leve controlada, lesión previa de rodilla derecha"
                ),
            ]
        ))

        # ── Sección 7: Acceso al sistema ──
        vbox.addWidget(_section(
            "7 · ACCESO AL SISTEMA  (no aplica para KID)", BLUE, [
                (
                    "Usuario",
                    "Nombre de usuario único para que el estudiante inicie sesión en el portal. "
                    "Sin espacios, sin caracteres especiales. Los KID no tienen usuario propio — "
                    "su acudiente gestiona el acceso.",
                    "santiago.martinez  o  smartinez2010"
                ),
                (
                    "Contraseña",
                    "Contraseña inicial que el estudiante deberá cambiar en su primer ingreso. "
                    "Mínimo 8 caracteres, combina letras y números.",
                    "Dojo2024*"
                ),
            ]
        ))

        scroll.setWidget(content)
        outer.addWidget(scroll)

        dlg.exec()

    # ── Guardar ───────────────────────────────────────────────────────────
    def _save(self):
        self.lbl_error.hide()

        first = self.inp_first.text().strip()
        last  = self.inp_last.text().strip()

        if not first or not last:
            self._show_toast(trf("student.form.error.required_name", "Nombre y apellido son obligatorios."), "error")
            return

        prefix = self.cmb_prefix.currentData()
        number = self.inp_phone.text().strip()
        phone  = f"{prefix}{number}" if number else None

        birth = self._birth_date
        category_id = self.cmb_category.currentData()
        data = {
            "first_name":       first,
            "last_name":        last,
            "phone":            phone,
            "email":            self.inp_email.text().strip() or None,
            "profession":       self.inp_profession.text().strip() or None
                if hasattr(self, "inp_profession") else None,
            "birthdate":        birth.toPyDate(),
            "joined_date":      self._joined_date.toPyDate(),
            "document":         self.inp_doc.text().strip() or None,
            "id_type_document": self.cmb_doctype.currentData(),
            "id_status":        self.cmb_status.currentData(),
            "category_id":      category_id,
            "username":         self.inp_username.text().strip(),
            "password":         self.inp_password.text().strip(),
            "address_line":     self.inp_address.text().strip() or None,
            "residence_details": self.inp_residence_details.toPlainText().strip() or None
                if hasattr(self, "inp_residence_details") else None,
            "neighborhood":     self.inp_neighborhood.text().strip() or None,
            "socioeconomic_stratum": self.cmb_stratum.currentData(),
            "residence_country": self.cmb_res_country.currentText().strip() or None,
            "residence_city":   self.cmb_res_city.currentText().strip() or None,
            "birth_country":    self.cmb_birth_country.currentText().strip() or None,
            "birth_city":       self.cmb_birth_city.currentText().strip() or None,
            "school_name":      self.inp_school.text().strip() or None,
        }

        cat_name = self.cmb_category.currentText()
        cat_upper = cat_name.upper()

        if cat_upper.startswith("KID"):
            data["access_type"] = "guardian"
            data["username"] = None
            data["password"] = None
        else:
            data["access_type"] = "student"

        guardian_name = self.inp_guardian_name.text().strip()
        guardian_phone = self.inp_guardian_phone.text().strip()
        guardian_rel = self.cmb_guardian_rel.currentText().strip()
        emerg_name = self.inp_emerg_name.text().strip()
        emerg_phone = self.inp_emerg_phone.text().strip()

        valid_categories = any(
            cat_name.upper().startswith(prefix)
            for prefix in ("KID", "YOUTH", "ADULT", "SCHOLARSHIP")
        )
        if not valid_categories:
            self._show_toast(trf("student.form.error.select_category", "Selecciona una categoria valida."), "error")
            return

        if cat_name.upper().startswith("KID"):
            if not guardian_name or not guardian_phone or not guardian_rel:
                self._show_toast(trf("student.form.error.kid_guardian_required", "Para KID el acudiente (nombre, telefono, parentesco) es obligatorio."), "error")
                return
            if phone:
                self._show_toast(trf("student.form.error.kid_no_phone", "KID no puede tener su propio telefono."), "warning")
                return
        elif cat_name.upper().startswith("YOUTH"):
            if not guardian_name or not guardian_phone or not guardian_rel:
                self._show_toast(trf("student.form.error.youth_guardian_required", "Para YOUTH el acudiente (nombre, telefono, parentesco) es obligatorio."), "error")
                return
            if not emerg_name or not emerg_phone:
                self._show_toast(trf("student.form.error.youth_emergency_required", "Para YOUTH el contacto de emergencia es obligatorio."), "error")
                return

        self.btn_save.setEnabled(False)
        self.btn_save.setText(trf("student.form.saving", "Guardando..."))
        try:
            if self.is_edit:
                self.repo.update(self.student_id, data)
                sid = self.student_id
            else:
                result = self.repo.create(data)
                self.created_credentials = result
                sid = result.get("student_id")

            if guardian_name:
                self.repo.save_guardian(sid, {
                    "full_name":   guardian_name,
                    "document":    self.inp_guardian_doc.text().strip() or None,
                    "phone":       guardian_phone,
                    "email":       self.inp_guardian_email.text().strip() or None,
                    "relationship": guardian_rel,
                    "profession":  self.inp_guardian_profession.text().strip() or None,
                })

            if emerg_name:
                self.repo.save_emergency_contact(sid, {
                    "full_name":     emerg_name,
                    "phone":         emerg_phone,
                    "email":         self.inp_emerg_email.text().strip() or None,
                    "relationship":  self.inp_emerg_rel.text().strip() or None,
                    "note":          self.inp_emerg_note.text().strip() or None,
                })

            health_data = {
                "eps":               self.inp_health_entity.text().strip() or None,
                "ips":               None,
                "blood_type":        self.cmb_health_blood.currentData(),
                "allergies":         self.inp_health_allergies.text().strip() or None,
                "medical_conditions": self.inp_health_conditions.text().strip() or None,
                "notes":             self.inp_health_notes.text().strip() or None,
            }
            self.repo.save_health_info(sid, health_data)

            if hasattr(self, "_pending_doc") and self._pending_doc:
                self.repo.save_student_document(sid, self._pending_doc["doc_type"], self._pending_doc["path"])

            self._show_toast(
                trf("student.form.saved", "Estudiante guardado correctamente.") if self.is_edit
                else trf("student.form.created", "Estudiante creado correctamente."),
                "success"
            )
            self.accept()
        except Exception as e:
            self._show_toast(f"Error: {e}", "error")
            self.btn_save.setEnabled(True)
            self.btn_save.setText(trf("student.form.save", "Guardar Cambios") if self.is_edit else trf("student.form.create", "Crear Estudiante"))
