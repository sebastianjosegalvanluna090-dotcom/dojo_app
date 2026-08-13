"""
views/account_view.py — Vista de configuración de cuenta (PyQt6).

Layout: sub-navegación lateral izquierda + content panel derecho.
3 submódulos: Perfil / Seguridad / Notificaciones.
(Preferencias NO se incluye — ya existe en otro módulo del sistema.)

Idéntico al prototipo HTML account_view_prototype.html, adaptado a PyQt6.

Conexiones sugeridas (cuando se integre a main.py):
    - main.py: agregar btn_account al sidebar → llama a _show_account()
    - _show_account() instancia AccountView(user=self.user) y lo agrega al content_layout
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QLineEdit, QTextEdit,
    QComboBox, QSizePolicy, QScrollArea,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
    QButtonGroup, QRadioButton, QDateEdit,
    QCheckBox, QSpinBox,
)
from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QRectF, QPropertyAnimation,
    QEasingCurve, pyqtProperty, pyqtSignal, QDate,
    QThread,
)
from PyQt6.QtGui import QColor, QPainter, QPen, QFont, QPainterPath, QLinearGradient

# ─── PALETA ───────────────────────────────────────────────────────────
BG_DEEP   = "#050505"
BG_SIDE   = "#0D0D0D"
BG_CARD   = "#161616"
BG_INPUT  = "#1C1C1C"
BG_HOVER  = "#1E1E1E"
BG_ACTIVE = "#1A0A0C"
BORDER    = "#2A2A2A"
BORDER_2  = "#1F1F1F"
RED       = "#C8102E"
RED_H     = "#E8152F"
RED_GLOW  = "rgba(200,16,46,0.15)"
GREEN     = "#22C55E"
YELLOW    = "#EAB308"
BLUE      = "#3B82F6"
PURPLE    = "#A855F7"
ORANGE    = "#F97316"
TEXT_PRI  = "#F0F0F0"
TEXT_SEC  = "#9CA3AF"
TEXT_MUT  = "#6B7280"
TEXT_DIM  = "#4B5563"


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Icon renderer (iconos SVG vectoriales, mismo sistema que main.py)
# ═══════════════════════════════════════════════════════════════════════════════
class IconLabel(QWidget):
    ICONS = {
        "user": '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
        "lock": '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
        "bell": '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>',
        "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
        "camera": '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/>',
        "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>',
        "trash": '<polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
        "check": '<polyline points="20 6 9 17 4 12"/>',
        "x": '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
        "desktop": '<rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>',
        "mobile": '<rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/>',
        "logout": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
        "home": '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
        "chevron-right": '<polyline points="9 18 15 12 9 6"/>',
        "globe": '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
        "mail": '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
    }

    def __init__(self, icon_name: str, size: int = 20, color: str = TEXT_SEC, parent=None):
        super().__init__(parent)
        self._icon_name = icon_name
        self._size = size
        self._color = color
        self.setFixedSize(size, size)

    def set_color(self, color: str):
        self._color = color
        self.update()

    def set_icon(self, icon_name: str):
        self._icon_name = icon_name
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
            self._draw_path(p, path_data)
        except Exception:
            pass

    def _draw_path(self, p: QPainter, path_data: str):
        import re
        from PyQt6.QtCore import QPointF
        elements = re.findall(r'<(circle|rect|line|polyline|path)\s([^/]+)/?>', path_data)
        for tag, attrs_str in elements:
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', attrs_str))
            if tag == "circle":
                cx = float(attrs.get("cx", 0)); cy = float(attrs.get("cy", 0))
                r = float(attrs.get("r", 0))
                p.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))
            elif tag == "rect":
                x = float(attrs.get("x", 0)); y = float(attrs.get("y", 0))
                w = float(attrs.get("width", 0)); h = float(attrs.get("height", 0))
                rx = float(attrs.get("rx", 0))
                if rx > 0: p.drawRoundedRect(QRectF(x, y, w, h), rx, rx)
                else: p.drawRect(QRectF(x, y, w, h))
            elif tag == "line":
                x1 = float(attrs.get("x1", 0)); y1 = float(attrs.get("y1", 0))
                x2 = float(attrs.get("x2", 0)); y2 = float(attrs.get("y2", 0))
                p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            elif tag == "polyline":
                pts = re.findall(r'-?[\d.]+', attrs.get("points", ""))
                if len(pts) >= 2 and len(pts) % 2 == 0:
                    path = QPainterPath()
                    path.moveTo(float(pts[0]), float(pts[1]))
                    for i in range(2, len(pts), 2):
                        path.lineTo(float(pts[i]), float(pts[i + 1]))
                    p.drawPath(path)
            elif tag == "path":
                d = attrs.get("d", "")
                path = QPainterPath()
                tokens = re.findall(r'[MLCZmlcz]|-?[\d.]+', d)
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
                        x1, y1 = float(tokens[i]), float(tokens[i + 1])
                        x2, y2 = float(tokens[i + 2]), float(tokens[i + 3])
                        x, y = float(tokens[i + 4]), float(tokens[i + 5]); i += 6
                        if cmd == "c":
                            x1 += current.x(); y1 += current.y()
                            x2 += current.x(); y2 += current.y()
                            x += current.x(); y += current.y()
                        path.cubicTo(QPointF(x1, y1), QPointF(x2, y2), QPointF(x, y))
                        current = QPointF(x, y)
                    elif cmd in ("Z", "z"):
                        path.closeSubpath()
                p.drawPath(path)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Sub-nav item
# ═══════════════════════════════════════════════════════════════════════════════
class SubNavItem(QWidget):
    clicked_nav = pyqtSignal(str)

    def __init__(self, icon_name: str, label: str, section_key: str,
                 badge: str = "", parent=None):
        super().__init__(parent)
        self._icon_name = icon_name
        self._label = label
        self._section_key = section_key
        self._active = False
        self._hovered = False

        self.setFixedHeight(42)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(12)

        self.icon_widget = IconLabel(icon_name, 20, TEXT_SEC)
        layout.addWidget(self.icon_widget)

        self.label = QLabel(label)
        self.label.setStyleSheet(
            f"color: {TEXT_SEC}; font-size: 13px; font-weight: 600; "
            f"font-family: 'Inter'; border: none; background: transparent;"
        )
        layout.addWidget(self.label, 1)

        if badge:
            b = QLabel(badge)
            b.setStyleSheet(f"""
                QLabel {{
                    color: {RED_H};
                    background: rgba(200,16,46,0.15);
                    border-radius: 6px;
                    padding: 2px 6px;
                    font-size: 9px;
                    font-weight: 900;
                    font-family: 'Inter';
                    border: none;
                }}
            """)
            layout.addWidget(b)

        self._apply_style()

    def set_active(self, active: bool):
        self._active = active
        self._apply_style()
        if active:
            self.icon_widget.set_color(RED_H)
            self.label.setStyleSheet(
                f"color: {TEXT_PRI}; font-size: 13px; font-weight: 800; "
                f"font-family: 'Inter'; border: none; background: transparent;"
            )
        else:
            self.icon_widget.set_color(TEXT_SEC)
            self.label.setStyleSheet(
                f"color: {TEXT_SEC}; font-size: 13px; font-weight: 600; "
                f"font-family: 'Inter'; border: none; background: transparent;"
            )

    def _apply_style(self):
        if self._active:
            self.setStyleSheet(f"""
                QWidget {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {RED_GLOW}, stop:1 rgba(200,16,46,0.04));
                    border-radius: 10px;
                }}
            """)
        elif self._hovered:
            self.setStyleSheet(f"""
                QWidget {{
                    background: {BG_HOVER};
                    border-radius: 10px;
                }}
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background: transparent;
                    border-radius: 10px;
                }
            """)

    def enterEvent(self, event):
        self._hovered = True
        self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._apply_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.clicked_nav.emit(self._section_key)
        super().mousePressEvent(event)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Toggle switch
# ═══════════════════════════════════════════════════════════════════════════════
class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, initial: bool = False, parent=None):
        super().__init__(parent)
        self._on = initial
        self.setFixedSize(44, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def is_on(self) -> bool:
        return self._on

    def set_on(self, on: bool):
        self._on = on
        self.update()
        self.toggled.emit(on)

    def mousePressEvent(self, event):
        self.set_on(not self._on)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Track
        if self._on:
            track_color = QColor(GREEN)
        else:
            track_color = QColor(BORDER)
        p.setBrush(track_color)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(0, 0, 44, 24), 12, 12)
        # Knob
        knob_x = 22 if self._on else 2
        p.setBrush(QColor("white"))
        p.drawEllipse(QRectF(knob_x, 2, 20, 20))


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Radio card (género, etc.)
# ═══════════════════════════════════════════════════════════════════════════════
class RadioCard(QFrame):
    clicked_radio = pyqtSignal(str)

    def __init__(self, value: str, label: str, selected: bool = False, parent=None):
        super().__init__(parent)
        self._value = value
        self._label = label
        self._selected = selected
        self._hovered = False
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(10)

        self.dot = QLabel()
        self.dot.setFixedSize(18, 18)
        self._update_dot()
        layout.addWidget(self.dot)

        self.label = QLabel(label)
        self.label.setStyleSheet(
            f"color: {TEXT_SEC if not selected else TEXT_PRI}; "
            f"font-size: 13px; font-weight: 600; font-family: 'Inter'; border: none;"
        )
        layout.addWidget(self.label, 1)

    def set_selected(self, selected: bool):
        self._selected = selected
        self._apply_style()
        self._update_dot()
        self.label.setStyleSheet(
            f"color: {TEXT_PRI if selected else TEXT_SEC}; "
            f"font-size: 13px; font-weight: 600; font-family: 'Inter'; border: none;"
        )

    def _update_dot(self):
        if self._selected:
            self.dot.setStyleSheet(f"""
                QLabel {{
                    background: transparent;
                    border: 2px solid {RED};
                    border-radius: 9px;
                }}
            """)
            # Inner dot
            inner = QLabel(self.dot)
            inner.setFixedSize(10, 10)
            inner.move(4, 4)
            inner.setStyleSheet(f"background: {RED}; border-radius: 5px; border: none;")
            inner.show()
            self._inner = inner
        else:
            self.dot.setStyleSheet(f"""
                QLabel {{
                    background: transparent;
                    border: 2px solid {TEXT_DIM};
                    border-radius: 9px;
                }}
            """)
            if hasattr(self, "_inner"):
                self._inner.deleteLater()

    def _apply_style(self):
        if self._selected:
            self.setStyleSheet(f"""
                QFrame {{
                    background: rgba(200,16,46,0.06);
                    border: 1px solid {RED};
                    border-radius: 10px;
                }}
            """)
        elif self._hovered:
            self.setStyleSheet(f"""
                QFrame {{
                    background: {BG_INPUT};
                    border: 1px solid {TEXT_MUT};
                    border-radius: 10px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background: {BG_INPUT};
                    border: 1px solid {BORDER};
                    border-radius: 10px;
                }}
            """)

    def enterEvent(self, event):
        self._hovered = True
        self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._apply_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.clicked_radio.emit(self._value)
        super().mousePressEvent(event)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Field label (con asterisco rojo para requeridos)
# ═══════════════════════════════════════════════════════════════════════════════
class FieldLabel(QLabel):
    def __init__(self, text: str, required: bool = False, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 11px; font-weight: 800; "
            f"font-family: 'Inter'; letter-spacing: 0.5px; border: none;"
        )
        if required:
            self.setText(f"{text} <span style='color: {RED_H}; font-size: 14px;'>*</span>")
        else:
            self.setText(text)
        self.setTextFormat(Qt.TextFormat.RichText)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Styled input (con focus glow)
# ═══════════════════════════════════════════════════════════════════════════════
INPUT_STYLE = f"""
    QLineEdit, QTextEdit, QComboBox, QDateEdit {{
        background: {BG_INPUT};
        color: {TEXT_PRI};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 0 14px;
        font-size: 14px;
        font-weight: 500;
        font-family: 'Inter';
        min-height: 44px;
    }}
    QLineEdit:hover, QTextEdit:hover, QComboBox:hover, QDateEdit:hover {{
        border-color: {TEXT_DIM};
    }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {{
        border-color: {RED};
        background: {BG_HOVER};
    }}
    QLineEdit:disabled {{
        color: {TEXT_MUT};
        background: rgba(255,255,255,0.02);
    }}
    QTextEdit {{
        padding: 12px 14px;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    QComboBox QAbstractItemView {{
        background: {BG_INPUT};
        color: {TEXT_PRI};
        selection-background-color: {RED};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 4px;
    }}
    QDateEdit::drop-down {{
        border: none;
        width: 30px;
    }}
"""


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION: Profile
# ═══════════════════════════════════════════════════════════════════════════════
class ProfileSection(QFrame):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self._user = user
        self.setStyleSheet("background: transparent; border: none;")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border-bottom: 1px solid {BORDER_2};
            }}
        """)
        header.setFixedHeight(80)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(28, 22, 28, 22)

        h_left = QVBoxLayout()
        h_left.setSpacing(4)
        h_title = QLabel("Perfil")
        h_title.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 18px; font-weight: 900; "
            f"font-family: 'Inter'; border: none;"
        )
        h_sub = QLabel("Información personal del administrador")
        h_sub.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 12px; font-weight: 500; border: none;"
        )
        h_left.addWidget(h_title)
        h_left.addWidget(h_sub)
        h_layout.addLayout(h_left)
        h_layout.addStretch()

        btn_cancel = QPushButton("  Cancelar")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SEC};
                border: 1px solid {BORDER};
                border-radius: 10px;
                font-size: 12px;
                font-weight: 800;
                font-family: 'Inter';
                padding: 0 16px;
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
                border-color: {TEXT_MUT};
                background: {BG_HOVER};
            }}
        """)
        h_layout.addWidget(btn_cancel)

        layout.addWidget(header)

        # Body
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(28, 28, 28, 28)
        body_layout.setSpacing(20)

        # ── Avatar section ──
        avatar_row = QHBoxLayout()
        avatar_row.setSpacing(20)

        avatar_wrapper = QFrame()
        avatar_wrapper.setFixedSize(94, 94)
        avatar_wrapper.setStyleSheet("background: transparent; border: none;")
        avatar_wrapper_layout = QVBoxLayout(avatar_wrapper)
        avatar_wrapper_layout.setContentsMargins(0, 0, 0, 0)

        avatar = QLabel(self._user_initials())
        avatar.setFixedSize(88, 88)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {PURPLE}, stop:1 #581C87);
                color: white;
                border-radius: 22px;
                font-size: 32px;
                font-weight: 900;
                font-family: 'Inter';
                border: 3px solid {BG_CARD};
            }}
        """)
        avatar_shadow = QGraphicsDropShadowEffect(avatar)
        avatar_shadow.setBlurRadius(20)
        avatar_shadow.setOffset(0, 8)
        avatar_shadow.setColor(QColor(0, 0, 0, 160))
        avatar.setGraphicsEffect(avatar_shadow)
        avatar_wrapper_layout.addWidget(avatar)

        # Camera button (overlaid)
        cam_btn = QPushButton()
        cam_btn.setParent(avatar_wrapper)
        cam_btn.setFixedSize(32, 32)
        cam_btn.move(60, 60)
        cam_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cam_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {RED_H}, stop:1 {RED});
                border: 2px solid {BG_CARD};
                border-radius: 10px;
            }}
        """)
        cam_shadow = QGraphicsDropShadowEffect(cam_btn)
        cam_shadow.setBlurRadius(10)
        cam_shadow.setOffset(0, 4)
        cam_shadow.setColor(QColor(200, 16, 46, 100))
        cam_btn.setGraphicsEffect(cam_shadow)
        cam_layout = QHBoxLayout(cam_btn)
        cam_layout.setContentsMargins(0, 0, 0, 0)
        cam_icon = IconLabel("camera", 14, "white")
        cam_layout.addWidget(cam_icon)
        avatar_wrapper_layout.addWidget(cam_btn)

        avatar_row.addWidget(avatar_wrapper)

        # Avatar info
        info_col = QVBoxLayout()
        info_col.setSpacing(4)
        name = QLabel(
            f"{self._user.get('first_name', '')} {self._user.get('last_name', '')}".strip()
            or str(self._user.get("username", "Usuario"))
        )
        name.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 18px; font-weight: 900; "
            f"font-family: 'Inter'; border: none;"
        )
        email = QLabel(self._user.get("email", "Sin email"))
        email.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 13px; font-weight: 500; border: none;"
        )
        info_col.addWidget(name)
        info_col.addWidget(email)

        # Avatar actions
        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)
        actions_row.setContentsMargins(0, 8, 0, 0)

        btn_upload = QPushButton("  Subir nueva")
        btn_upload.setFixedHeight(38)
        btn_upload.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_upload.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {RED_H}, stop:1 {RED});
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 800;
                font-family: 'Inter';
                padding: 0 16px;
            }}
        """)
        upload_icon = IconLabel("upload", 14, "white")
        # Insert icon before text
        actions_row.addWidget(btn_upload)

        btn_delete = QPushButton("  Eliminar")
        btn_delete.setFixedHeight(38)
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {RED_H};
                border: 1px solid rgba(200,16,46,0.3);
                border-radius: 10px;
                font-size: 12px;
                font-weight: 800;
                font-family: 'Inter';
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background: rgba(200,16,46,0.10);
            }}
        """)
        actions_row.addWidget(btn_delete)
        info_col.addLayout(actions_row)

        avatar_row.addLayout(info_col, 1)
        body_layout.addLayout(avatar_row)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER_2}; border: none;")
        body_layout.addWidget(sep)

        # ── Form grid ──
        form_widget = QWidget()
        form_widget.setStyleSheet("background: transparent;")
        form_widget.setStyleSheet(INPUT_STYLE)
        form_layout = QHBoxLayout(form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(20)

        # Left column
        left_col = QVBoxLayout()
        left_col.setSpacing(16)

        # First name
        left_col.addWidget(FieldLabel("Nombre", required=True))
        self.input_name = QLineEdit(self._user.get("first_name", ""))
        self.input_name.setStyleSheet(INPUT_STYLE)
        left_col.addWidget(self.input_name)

        left_col.addWidget(FieldLabel("Email", required=True))
        self.input_email = QLineEdit(self._user.get("email", ""))
        self.input_email.setStyleSheet(INPUT_STYLE)
        left_col.addWidget(self.input_email)

        # Gender (radio cards)
        left_col.addWidget(FieldLabel("Género"))
        gender_row = QHBoxLayout()
        gender_row.setSpacing(12)
        self.radio_male = RadioCard("M", "Masculino", selected=True)
        self.radio_female = RadioCard("F", "Femenino")
        self.radio_male.clicked_radio.connect(self._on_gender_change)
        self.radio_female.clicked_radio.connect(self._on_gender_change)
        gender_row.addWidget(self.radio_male)
        gender_row.addWidget(self.radio_female)
        left_col.addLayout(gender_row)

        left_col.addWidget(FieldLabel("Fecha de nacimiento"))
        self.input_birth = QDateEdit()
        self.input_birth.setCalendarPopup(True)
        birthdate = self._user.get("birthdate")
        if birthdate:
            qdate = QDate(birthdate.year, birthdate.month, birthdate.day)
        else:
            qdate = QDate.currentDate()
        self.input_birth.setDate(qdate)
        self.input_birth.setStyleSheet(INPUT_STYLE)
        left_col.addWidget(self.input_birth)

        left_col.addWidget(FieldLabel("Dirección residencial"))
        self.input_address = QTextEdit(self._user.get("address_line", ""))
        self.input_address.setMaximumHeight(70)
        self.input_address.setStyleSheet(INPUT_STYLE)
        left_col.addWidget(self.input_address)

        left_col.addStretch()
        form_layout.addLayout(left_col, 1)

        # Right column
        right_col = QVBoxLayout()
        right_col.setSpacing(16)

        right_col.addWidget(FieldLabel("Apellido", required=True))
        self.input_lastname = QLineEdit(self._user.get("last_name", ""))
        self.input_lastname.setStyleSheet(INPUT_STYLE)
        right_col.addWidget(self.input_lastname)

        right_col.addWidget(FieldLabel("Teléfono móvil"))
        phone_widget = QFrame()
        phone_widget.setStyleSheet(f"""
            QFrame {{
                background: {BG_INPUT};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)
        phone_layout = QHBoxLayout(phone_widget)
        phone_layout.setContentsMargins(0, 0, 0, 0)
        phone_layout.setSpacing(0)
        prefix = QLabel("🇨🇴  +57")
        prefix.setFixedHeight(44)
        prefix.setStyleSheet(
            f"color: {TEXT_SEC}; font-size: 13px; font-weight: 700; "
            f"font-family: 'Inter'; border: none; "
            f"border-right: 1px solid {BORDER}; padding: 0 12px; "
            f"background: rgba(255,255,255,0.02);"
        )
        phone_layout.addWidget(prefix)
        self.input_phone = QLineEdit(self._user.get("phone", ""))
        self.input_phone.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {TEXT_PRI};
                padding: 0 14px;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Inter';
                min-height: 44px;
            }}
            QLineEdit:focus {{
                background: transparent;
            }}
        """)
        phone_layout.addWidget(self.input_phone)
        right_col.addWidget(phone_widget)

        right_col.addWidget(FieldLabel("Tipo de documento"))
        self.cmb_doc_type = QComboBox()
        self.cmb_doc_type.setStyleSheet(INPUT_STYLE)
        for tid, tname in [(1, "Cédula de ciudadanía"), (2, "Cédula extranjería"), (3, "Pasaporte"), (4, "Tarjeta de identidad")]:
            self.cmb_doc_type.addItem(tname, tid)
        current_type = self._user.get("id_document_type") or 1
        for i in range(self.cmb_doc_type.count()):
            if self.cmb_doc_type.itemData(i) == current_type:
                self.cmb_doc_type.setCurrentIndex(i)
                break
        right_col.addWidget(self.cmb_doc_type)

        right_col.addWidget(FieldLabel("Número de documento"))
        self.input_doc = QLineEdit(str(self._user.get("document", "") or ""))
        self.input_doc.setStyleSheet(INPUT_STYLE)
        right_col.addWidget(self.input_doc)

        right_col.addWidget(FieldLabel("Rol en el dojo"))
        self.input_role = QLineEdit(str(self._user.get("role", "")) or "Usuario")
        self.input_role.setEnabled(False)
        self.input_role.setStyleSheet(INPUT_STYLE)
        right_col.addWidget(self.input_role)

        right_col.addWidget(FieldLabel("Biografía"))
        self.input_bio = QTextEdit(self._user.get("profession", ""))
        self.input_bio.setMaximumHeight(70)
        self.input_bio.setStyleSheet(INPUT_STYLE)
        right_col.addWidget(self.input_bio)

        right_col.addStretch()
        form_layout.addLayout(right_col, 1)

        body_layout.addWidget(form_widget)

        # Footer
        body_layout.addStretch()
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border-top: 1px solid {BORDER_2};
            }}
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 20, 0, 0)
        footer_layout.addStretch()

        btn_cancel2 = QPushButton("  Cancelar")
        btn_cancel2.setFixedHeight(42)
        btn_cancel2.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel2.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SEC};
                border: 1px solid {BORDER};
                border-radius: 10px;
                font-size: 12px;
                font-weight: 800;
                font-family: 'Inter';
                padding: 0 20px;
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
                border-color: {TEXT_MUT};
                background: {BG_HOVER};
            }}
        """)
        footer_layout.addWidget(btn_cancel2)

        btn_save = QPushButton("  Guardar cambios")
        btn_save.setFixedHeight(42)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {RED_H}, stop:1 {RED});
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 800;
                font-family: 'Inter';
                padding: 0 24px;
            }}
        """)
        save_shadow = QGraphicsDropShadowEffect(btn_save)
        save_shadow.setBlurRadius(16)
        save_shadow.setOffset(0, 4)
        save_shadow.setColor(QColor(200, 16, 46, 120))
        btn_save.setGraphicsEffect(save_shadow)
        footer_layout.addWidget(btn_save)

        body_layout.addWidget(footer)

        layout.addWidget(body, 1)

    def _on_gender_change(self, value: str):
        self.radio_male.set_selected(value == "M")
        self.radio_female.set_selected(value == "F")

    def _user_initials(self) -> str:
        first = str(self._user.get("first_name", "")).strip()
        last = str(self._user.get("last_name", "")).strip()
        if first and last:
            return (first[0] + last[0]).upper()
        if first:
            return first[0].upper()
        name = str(self._user.get("username", "U"))
        parts = name.strip().split()
        return "".join(p[0].upper() for p in parts[:2]) or "U"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION: Security
# ═══════════════════════════════════════════════════════════════════════════════
class SecuritySection(QFrame):
    def __init__(self, user: dict = None, parent=None):
        super().__init__(parent)
        self._user = user or {}
        self.setStyleSheet("background: transparent; border: none;")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet(f"background: transparent; border-bottom: 1px solid {BORDER_2};")
        header.setFixedHeight(80)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(28, 22, 28, 22)
        h_left = QVBoxLayout()
        h_left.setSpacing(4)
        h_title = QLabel("Seguridad")
        h_title.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 18px; font-weight: 900; "
            f"font-family: 'Inter'; border: none;"
        )
        h_sub = QLabel("Contraseña, autenticación y sesiones activas")
        h_sub.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; font-weight: 500; border: none;")
        h_left.addWidget(h_title)
        h_left.addWidget(h_sub)
        h_layout.addLayout(h_left)
        h_layout.addStretch()
        layout.addWidget(header)

        # Body
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(28, 28, 28, 28)
        body_layout.setSpacing(32)

        # ── Change password block ──
        pwd_title = QLabel("🔑  Cambiar contraseña")
        pwd_title.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; "
            f"font-family: 'Inter'; border: none;"
        )
        body_layout.addWidget(pwd_title)
        pwd_desc = QLabel("Usa una contraseña de al menos 8 caracteres con mayúsculas, números y símbolos.")
        pwd_desc.setWordWrap(True)
        pwd_desc.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; font-weight: 500; border: none;")
        body_layout.addWidget(pwd_desc)

        pwd_form = QHBoxLayout()
        pwd_form.setSpacing(20)

        # Left: current + new
        left = QVBoxLayout()
        left.setSpacing(12)
        left.addWidget(FieldLabel("Contraseña actual"))
        self.input_pwd_current = QLineEdit()
        self.input_pwd_current.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pwd_current.setText("password123")
        self.input_pwd_current.setStyleSheet(INPUT_STYLE)
        left.addWidget(self.input_pwd_current)

        left.addWidget(FieldLabel("Nueva contraseña"))
        self.input_pwd_new = QLineEdit()
        self.input_pwd_new.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pwd_new.setPlaceholderText("••••••••")
        self.input_pwd_new.setStyleSheet(INPUT_STYLE)
        self.input_pwd_new.textChanged.connect(self._update_strength)
        left.addWidget(self.input_pwd_new)

        # Strength bars
        self.strength_bars = []
        strength_row = QHBoxLayout()
        strength_row.setSpacing(4)
        for _ in range(4):
            bar = QFrame()
            bar.setFixedHeight(4)
            bar.setStyleSheet(f"background: {BORDER}; border-radius: 2px; border: none;")
            strength_row.addWidget(bar)
            self.strength_bars.append(bar)
        left.addLayout(strength_row)

        pwd_form.addLayout(left, 1)

        # Right: confirm
        right = QVBoxLayout()
        right.setSpacing(12)
        right.addWidget(FieldLabel("Confirmar contraseña"))
        self.input_pwd_confirm = QLineEdit()
        self.input_pwd_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pwd_confirm.setPlaceholderText("••••••••")
        self.input_pwd_confirm.setStyleSheet(INPUT_STYLE)
        right.addWidget(self.input_pwd_confirm)
        right.addStretch()
        pwd_form.addLayout(right, 1)

        body_layout.addLayout(pwd_form)

        # Separator
        sep1 = QFrame()
        sep1.setFixedHeight(1)
        sep1.setStyleSheet(f"background: {BORDER_2}; border: none;")
        body_layout.addWidget(sep1)

        # ── 2FA block ──
        fa_title = QLabel("🛡️  Autenticación de dos factores")
        fa_title.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; "
            f"font-family: 'Inter'; border: none;"
        )
        body_layout.addWidget(fa_title)
        fa_desc = QLabel("Añade una capa extra de seguridad a tu cuenta.")
        fa_desc.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; font-weight: 500; border: none;")
        body_layout.addWidget(fa_desc)

        # Toggle: SMS
        sms_row = self._make_toggle_row(
            "Autenticación por SMS",
            "Recibe un código por mensaje de texto al iniciar sesión",
            initial=False
        )
        body_layout.addWidget(sms_row)

        # Toggle: App
        app_row = self._make_toggle_row(
            "App autenticadora",
            "Usa Google Authenticator, Authy o similar",
            initial=True
        )
        body_layout.addWidget(app_row)

        # Separator
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background: {BORDER_2}; border: none;")
        body_layout.addWidget(sep2)

        # ── Active sessions ──
        sess_title = QLabel("💻  Sesiones activas")
        sess_title.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; "
            f"font-family: 'Inter'; border: none;"
        )
        body_layout.addWidget(sess_title)
        sess_desc = QLabel("Dispositivos donde has iniciado sesión recientemente.")
        sess_desc.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; font-weight: 500; border: none;")
        body_layout.addWidget(sess_desc)

        # Current session (Windows)
        sess1 = self._make_session_card(
            "desktop", BLUE,
            "Windows · Chrome",
            "Cali, Colombia · 192.168.1.1 · Activa ahora",
            is_current=True
        )
        body_layout.addWidget(sess1)

        # Other session (iPhone)
        sess2 = self._make_session_card(
            "mobile", PURPLE,
            "iPhone · Safari",
            "Cali, Colombia · Hace 3 horas",
            is_current=False
        )
        body_layout.addWidget(sess2)

        # ── Separador ──
        sep3 = QFrame()
        sep3.setFixedHeight(1)
        sep3.setStyleSheet(f"background: {BORDER_2}; border: none;")
        body_layout.addWidget(sep3)

        # ── Palabra de seguridad ──
        sw_title = QLabel("Palabra de seguridad")
        sw_title.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; font-family: 'Inter'; border: none;"
        )
        body_layout.addWidget(sw_title)
        sw_desc = QLabel("Se usa para recuperar tu contrasena. Guardala en un lugar seguro.")
        sw_desc.setWordWrap(True)
        sw_desc.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; font-weight: 500; border: none;")
        body_layout.addWidget(sw_desc)

        has_word = bool(self._user.get("security_word"))

        if has_word:
            badge = QFrame()
            badge.setStyleSheet(f"""
                QFrame {{
                    background: rgba(34,197,94,0.1);
                    border: 1px solid rgba(34,197,94,0.3);
                    border-radius: 8px;
                }}
            """)
            badge_layout = QHBoxLayout(badge)
            badge_layout.setContentsMargins(12, 8, 12, 8)
            badge_layout.setSpacing(8)
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {GREEN}; font-size: 10px; border: none;")
            badge_layout.addWidget(dot)
            badge_lbl = QLabel("Ya tienes una palabra de seguridad registrada")
            badge_lbl.setStyleSheet(f"color: {GREEN}; font-size: 12px; font-weight: 700; border: none;")
            badge_layout.addWidget(badge_lbl, 1)
            body_layout.addWidget(badge)

            sw_change_lbl = FieldLabel("Nueva palabra de seguridad (dejar vacio para mantener la actual)")
        else:
            sw_change_lbl = FieldLabel("Palabra de seguridad")

        body_layout.addWidget(sw_change_lbl)
        self.input_security_word = QLineEdit()
        self.input_security_word.setPlaceholderText(
            "Nueva palabra..." if has_word else "Ej: nombre de tu mascota, ciudad natal..."
        )
        self.input_security_word.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_security_word.setStyleSheet(INPUT_STYLE)
        body_layout.addWidget(self.input_security_word)

        # ── Separador ──
        sep4 = QFrame()
        sep4.setFixedHeight(1)
        sep4.setStyleSheet(f"background: {BORDER_2}; border: none;")
        body_layout.addWidget(sep4)

        # ── PIN de seguridad ──
        pin_title = QLabel("PIN de seguridad")
        pin_title.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; font-family: 'Inter'; border: none;"
        )
        body_layout.addWidget(pin_title)
        pin_desc = QLabel("Si lo activas, se pedira este PIN cada vez que quieras guardar cambios en tu perfil.")
        pin_desc.setWordWrap(True)
        pin_desc.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; font-weight: 500; border: none;")
        body_layout.addWidget(pin_desc)

        pin_enable_row = self._make_toggle_row(
            "Activar PIN de seguridad",
            "Protege los cambios de perfil con un PIN de 4-6 digitos",
            initial=False
        )
        body_layout.addWidget(pin_enable_row)
        self._toggle_pin = pin_enable_row.findChild(ToggleSwitch)

        pin_inputs = QHBoxLayout()
        pin_inputs.setSpacing(16)
        left_pin = QVBoxLayout()
        left_pin.setSpacing(8)
        left_pin.addWidget(FieldLabel("PIN (4-6 digitos)"))
        self.input_pin = QLineEdit()
        self.input_pin.setPlaceholderText("****")
        self.input_pin.setMaxLength(6)
        self.input_pin.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pin.setStyleSheet(INPUT_STYLE)
        left_pin.addWidget(self.input_pin)
        pin_inputs.addLayout(left_pin, 1)

        right_pin = QVBoxLayout()
        right_pin.setSpacing(8)
        right_pin.addWidget(FieldLabel("Confirmar PIN"))
        self.input_pin_confirm = QLineEdit()
        self.input_pin_confirm.setPlaceholderText("****")
        self.input_pin_confirm.setMaxLength(6)
        self.input_pin_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pin_confirm.setStyleSheet(INPUT_STYLE)
        right_pin.addWidget(self.input_pin_confirm)
        right_pin.addStretch()
        pin_inputs.addLayout(right_pin, 1)
        body_layout.addLayout(pin_inputs)

        # ── Boton guardar seguridad ──
        btn_save_security = QPushButton("  Guardar configuracion de seguridad")
        btn_save_security.setFixedHeight(42)
        btn_save_security.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save_security.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {RED_H}, stop:1 {RED});
                color: white; border: none; border-radius: 10px;
                font-size: 12px; font-weight: 800; font-family: 'Inter'; padding: 0 24px;
            }}
        """)
        btn_save_security.clicked.connect(self._save_security)
        body_layout.addWidget(btn_save_security)

        body_layout.addStretch()
        layout.addWidget(body, 1)

    def _make_toggle_row(self, label: str, desc: str, initial: bool) -> QFrame:
        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border-bottom: 1px solid {BORDER_2};
            }}
        """)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 16, 0, 16)
        row_layout.setSpacing(14)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 13px; font-weight: 700; "
            f"font-family: 'Inter'; border: none;"
        )
        d = QLabel(desc)
        d.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 11px; font-weight: 500; border: none;"
        )
        d.setWordWrap(True)
        info_col.addWidget(lbl)
        info_col.addWidget(d)
        row_layout.addLayout(info_col, 1)

        toggle = ToggleSwitch(initial=initial)
        row_layout.addWidget(toggle)

        return row

    def _make_session_card(self, icon_name: str, icon_color: str,
                           device: str, meta: str, is_current: bool) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {BG_INPUT};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        c_layout = QHBoxLayout(card)
        c_layout.setContentsMargins(14, 14, 14, 14)
        c_layout.setSpacing(14)

        # Icon
        icon_box = QFrame()
        icon_box.setFixedSize(40, 40)
        icon_box.setStyleSheet(f"""
            QFrame {{
                background: {icon_color}1A;
                border-radius: 10px;
                border: none;
            }}
        """)
        icon_layout = QHBoxLayout(icon_box)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon = IconLabel(icon_name, 20, icon_color)
        icon_layout.addWidget(icon)
        c_layout.addWidget(icon_box)

        # Info
        info_col = QVBoxLayout()
        info_col.setSpacing(2)

        device_row = QHBoxLayout()
        device_row.setSpacing(8)
        dev_lbl = QLabel(device)
        dev_lbl.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 13px; font-weight: 800; "
            f"font-family: 'Inter'; border: none;"
        )
        device_row.addWidget(dev_lbl)

        if is_current:
            current_badge = QLabel("Actual")
            current_badge.setStyleSheet(f"""
                QLabel {{
                    color: {GREEN};
                    background: rgba(34,197,94,0.10);
                    border-radius: 6px;
                    padding: 3px 8px;
                    font-size: 10px;
                    font-weight: 900;
                    font-family: 'Inter';
                    border: none;
                }}
            """)
            device_row.addWidget(current_badge)
        device_row.addStretch()
        info_col.addLayout(device_row)

        meta_lbl = QLabel(meta)
        meta_lbl.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 11px; font-weight: 500; border: none;"
        )
        info_col.addWidget(meta_lbl)
        c_layout.addLayout(info_col, 1)

        # Logout button (only for non-current)
        if not is_current:
            btn = QPushButton()
            btn.setFixedSize(38, 38)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {RED_H};
                    border: 1px solid rgba(200,16,46,0.3);
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    background: rgba(200,16,46,0.10);
                }}
            """)
            btn_layout = QHBoxLayout(btn)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_icon = IconLabel("logout", 14, RED_H)
            btn_layout.addWidget(btn_icon)
            c_layout.addWidget(btn)

        return card

    def _update_strength(self, pwd: str):
        score = 0
        if len(pwd) >= 8: score += 1
        if any(c.isupper() for c in pwd): score += 1
        if any(c.isdigit() for c in pwd): score += 1
        if any(not c.isalnum() for c in pwd): score += 1

        for i, bar in enumerate(self.strength_bars):
            if i < score:
                if score <= 1:
                    color = RED_H
                elif score <= 3:
                    color = YELLOW
                else:
                    color = GREEN
                bar.setStyleSheet(f"background: {color}; border-radius: 2px; border: none;")
            else:
                bar.setStyleSheet(f"background: {BORDER}; border-radius: 2px; border: none;")

    def _save_security(self):
        if self._toggle_pin and self._toggle_pin.is_on():
            pin = self.input_pin.text().strip()
            pin_confirm = self.input_pin_confirm.text().strip()
            if len(pin) < 4:
                return
            if pin != pin_confirm:
                return


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION: Notifications
# ═══════════════════════════════════════════════════════════════════════════════
class NotificationPreferencesLoadWorker(QThread):
    loaded = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, repository, user_id):
        super().__init__()
        self._repository = repository
        self._user_id = user_id

    def run(self):
        try:
            prefs = self._repository.get_notification_preferences(self._user_id)
            self.loaded.emit(prefs)
        except Exception as e:
            self.failed.emit(str(e))


class NotificationPreferencesSaveWorker(QThread):
    saved = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, repository, user_id, preferences):
        super().__init__()
        self._repository = repository
        self._user_id = user_id
        self._preferences = preferences

    def run(self):
        try:
            self._repository.save_notification_preferences(
                self._user_id, self._preferences,
            )
            self.saved.emit(self._preferences)
        except Exception as e:
            self.failed.emit(str(e))


class NotificationsSection(QFrame):
    preferences_saved = pyqtSignal(dict)

    _DESC_CLASSES = "Recibe recordatorios antes del inicio de cada clase"
    _DESC_EVENTS = "Recibe recordatorios de eventos programados en el calendario"
    _DESC_CLASSES_OFF = "Las notificaciones de clases están desactivadas."
    _DESC_EVENTS_OFF = "Las notificaciones de eventos están desactivadas."

    _CHANNEL_QSS = f"""
        QCheckBox#ChannelOption {{
            background-color: #151515;
            color: #D1D5DB;
            border: 1px solid #292929;
            border-radius: 10px;
            padding: 12px 14px;
            spacing: 10px;
            font-size: 11px;
            font-weight: 700;
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }}
        QCheckBox#ChannelOption:hover {{
            background-color: #181818;
            border-color: #3A3A3A;
        }}
        QCheckBox#ChannelOption:checked {{
            background-color: rgba(200, 16, 46, 0.08);
            border: 1px solid rgba(200, 16, 46, 0.50);
            color: #F0F0F0;
        }}
        QCheckBox#ChannelOption::indicator {{
            width: 17px; height: 17px;
            border: 1px solid #454545;
            border-radius: 5px;
            background-color: #0F0F0F;
        }}
        QCheckBox#ChannelOption::indicator:checked {{
            background-color: #C8102E;
            border-color: #E8152F;
        }}
    """

    _COMBO_QSS = f"""
        QComboBox#NotificationTimeCombo {{
            background-color: #191919;
            color: #F0F0F0;
            border: 1px solid #303030;
            border-radius: 9px;
            padding: 0 14px;
            font-size: 11px;
            font-weight: 700;
            font-family: 'Inter', 'Segoe UI', sans-serif;
            min-height: 38px;
        }}
        QComboBox#NotificationTimeCombo:hover {{
            border-color: #454545;
        }}
        QComboBox#NotificationTimeCombo:focus {{
            border-color: #C8102E;
        }}
        QComboBox#NotificationTimeCombo::drop-down {{
            width: 32px;
            border: none;
        }}
        QComboBox#NotificationTimeCombo QAbstractItemView {{
            background-color: #181818;
            color: #F0F0F0;
            border: 1px solid #333333;
            selection-background-color: #C8102E;
            outline: none;
            padding: 4px;
        }}
    """

    _START_QSS = f"""
        QFrame#StartNotificationRow {{
            background-color: #151515;
            border: 1px solid #282828;
            border-radius: 10px;
        }}
        QCheckBox#StartOption {{
            color: #D1D5DB;
            font-size: 12px;
            font-weight: 700;
            font-family: 'Inter', 'Segoe UI', sans-serif;
            spacing: 10px;
            background: transparent;
            border: none;
        }}
        QCheckBox#StartOption::indicator {{
            width: 16px; height: 16px;
            border: 1px solid #454545;
            border-radius: 4px;
            background-color: #0F0F0F;
        }}
        QCheckBox#StartOption::indicator:checked {{
            background-color: #C8102E;
            border-color: #E8152F;
        }}
    """

    def __init__(self, user_id, repository, parent=None):
        super().__init__(parent)
        self._user_id = int(user_id)
        self._repository = repository
        self._preferences = {}
        self._loading = False
        self.setStyleSheet("background: transparent; border: none;")
        self._load_worker = None
        self._save_worker = None
        self._build()
        self._load_preferences()

    # ── Helpers ───────────────────────────────────────────────────

    def _make_icon_box(self, icon_name, accent_bg, accent_border):
        box = QFrame()
        box.setObjectName("NotificationIconBox")
        box.setFixedSize(40, 40)
        box.setStyleSheet(f"""
            QFrame#NotificationIconBox {{
                background-color: {accent_bg};
                border: 1px solid {accent_border};
                border-radius: 10px;
            }}
        """)
        lay = QHBoxLayout(box)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico = IconLabel(icon_name, 18, TEXT_PRI)
        lay.addWidget(ico)
        return box

    def _make_status_badge(self, active=True):
        lbl = QLabel("ACTIVO" if active else "INACTIVO")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if active:
            lbl.setStyleSheet(
                f"color: #22C55E; background-color: rgba(34,197,94,0.10); "
                f"border: 1px solid rgba(34,197,94,0.20); border-radius: 8px; "
                f"padding: 4px 8px; font-size: 8px; font-weight: 900; "
                f"letter-spacing: 0.8px; font-family: 'Inter','Segoe UI',sans-serif;"
            )
        else:
            lbl.setStyleSheet(
                f"color: #6B7280; background-color: rgba(107,114,128,0.08); "
                f"border: 1px solid rgba(107,114,128,0.15); border-radius: 8px; "
                f"padding: 4px 8px; font-size: 8px; font-weight: 900; "
                f"letter-spacing: 0.8px; font-family: 'Inter','Segoe UI',sans-serif;"
            )
        return lbl

    def _make_separator(self):
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("QFrame { background-color: #242424; border: none; }")
        return sep

    def _make_field_caption(self, title, description=""):
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        t = QLabel(title)
        t.setStyleSheet(
            f"color: #555D69; font-size: 9px; font-weight: 900; "
            f"letter-spacing: 1px; font-family: 'Inter','Segoe UI',sans-serif; "
            f"background: transparent; border: none;"
        )
        lay.addWidget(t)
        if description:
            d = QLabel(description)
            d.setWordWrap(True)
            d.setStyleSheet(
                f"color: #6B7280; font-size: 11px; font-weight: 500; "
                f"font-family: 'Inter','Segoe UI',sans-serif; "
                f"background: transparent; border: none;"
            )
            lay.addWidget(d)
        return w

    def _create_channel_option(self, text, subtitle, checked=True):
        card = QFrame()
        card.setObjectName("ChannelCard")
        card.setStyleSheet(f"""
            QFrame#ChannelCard {{
                background-color: #151515;
                border: 1px solid #292929;
                border-radius: 10px;
            }}
            QFrame#ChannelCard:hover {{
                background-color: #181818;
                border-color: #3A3A3A;
            }}
        """)
        card.setMinimumHeight(48)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        lay = QHBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(10)
        chk = QCheckBox(text)
        chk.setObjectName("ChannelOption")
        chk.setChecked(checked)
        chk.setStyleSheet(self._CHANNEL_QSS)
        lay.addWidget(chk)
        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet(
                f"color: #6B7280; font-size: 10px; font-weight: 500; "
                f"font-family: 'Inter','Segoe UI',sans-serif; "
                f"background: transparent; border: none;"
            )
            lay.addWidget(sub)
        return chk, card

    def _create_time_combo(self, options):
        combo = QComboBox()
        combo.setObjectName("NotificationTimeCombo")
        combo.setMinimumWidth(220)
        combo.setMaximumWidth(280)
        combo.setFixedHeight(42)
        combo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        for text, val in options:
            combo.addItem(text, val)
        combo.setStyleSheet(self._COMBO_QSS)
        return combo

    def _create_start_option(self, description):
        row = QFrame()
        row.setObjectName("StartNotificationRow")
        row.setStyleSheet(self._START_QSS)
        row.setFixedHeight(64)
        lay = QHBoxLayout(row)
        lay.setContentsMargins(12, 14, 12, 14)
        lay.setSpacing(10)
        return row, lay, description

    def _build_notification_settings_card(
        self, parent_layout, category, eyebrow, title, description,
        accent_color, accent_bg, accent_border, icon_name, toggle,
    ):
        card = QFrame()
        card.setObjectName("NotificationSettingsCard")
        card.setStyleSheet(f"""
            QFrame#NotificationSettingsCard {{
                background-color: #111111;
                border: 1px solid #252525;
                border-radius: 16px;
            }}
            QFrame#NotificationSettingsCard:hover {{
                border-color: #343434;
                background-color: #131313;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(16)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(14)

        icon_box = self._make_icon_box(icon_name, accent_bg, accent_border)
        header_row.addWidget(icon_box)

        text_col = QVBoxLayout()
        text_col.setSpacing(3)
        eyebrow_lbl = QLabel(eyebrow)
        eyebrow_lbl.setStyleSheet(
            f"color: #6B7280; font-size: 9px; font-weight: 900; "
            f"letter-spacing: 1.2px; font-family: 'Inter','Segoe UI',sans-serif; "
            f"background: transparent; border: none;"
        )
        text_col.addWidget(eyebrow_lbl)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"color: #F0F0F0; font-size: 15px; font-weight: 800; "
            f"font-family: 'Inter','Segoe UI',sans-serif; "
            f"background: transparent; border: none;"
        )
        text_col.addWidget(title_lbl)
        desc_lbl = QLabel(description)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(
            f"color: #737B88; font-size: 11px; font-weight: 500; "
            f"font-family: 'Inter','Segoe UI',sans-serif; "
            f"background: transparent; border: none;"
        )
        text_col.addWidget(desc_lbl)
        header_row.addLayout(text_col, 1)

        right_col = QVBoxLayout()
        right_col.setSpacing(6)
        right_col.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        status_lbl = self._make_status_badge(True)
        right_col.addWidget(status_lbl, 0, Qt.AlignmentFlag.AlignRight)
        right_col.addWidget(toggle, 0, Qt.AlignmentFlag.AlignRight)
        header_row.addLayout(right_col)

        card_layout.addLayout(header_row)

        separator = self._make_separator()
        card_layout.addWidget(separator)

        advanced = QFrame()
        advanced.setObjectName("AdvancedNotificationPanel")
        advanced.setStyleSheet(
            "QFrame#AdvancedNotificationPanel { background-color: transparent; border: none; }"
        )
        adv_lay = QVBoxLayout(advanced)
        adv_lay.setContentsMargins(0, 0, 0, 0)
        adv_lay.setSpacing(16)
        card_layout.addWidget(advanced)
        advanced.hide()

        parent_layout.addWidget(card)

        return card, advanced, adv_lay, separator, status_lbl, desc_lbl

    # ── Build ─────────────────────────────────────────────────────

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setStyleSheet(f"background: transparent; border-bottom: 1px solid {BORDER_2};")
        header.setFixedHeight(80)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(28, 22, 28, 22)
        h_left = QVBoxLayout()
        h_left.setSpacing(4)
        h_title = QLabel("Notificaciones")
        h_title.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 18px; font-weight: 900; "
            f"font-family: 'Inter'; border: none;"
        )
        h_sub = QLabel("Configura cómo y cuándo recibir alertas del sistema")
        h_sub.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; font-weight: 500; border: none;")
        h_left.addWidget(h_title)
        h_left.addWidget(h_sub)
        h_layout.addLayout(h_left)
        h_layout.addStretch()
        layout.addWidget(header)

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(28, 28, 28, 28)
        body_layout.setSpacing(16)

        self._build_classes_card(body_layout)
        self._build_events_card(body_layout)

        body_layout.addSpacing(8)
        body_layout.addWidget(self._make_disabled_group_title("Email", "PRÓXIMAMENTE"))
        body_layout.addWidget(self._make_disabled_toggle_row(
            "Nuevo estudiante inscrito",
            "Recibe un email cuando alguien se inscriba al dojo",
        ))
        body_layout.addWidget(self._make_disabled_toggle_row(
            "Pago recibido",
            "Notificación de cada ingreso registrado",
        ))
        body_layout.addSpacing(8)
        body_layout.addWidget(self._make_disabled_group_title("SMS", "PRÓXIMAMENTE"))
        body_layout.addWidget(self._make_disabled_toggle_row(
            "Emergencias",
            "Solo alertas críticas del sistema",
        ))
        body_layout.addStretch()

        self.lbl_notification_error = QLabel()
        self.lbl_notification_error.setStyleSheet(
            f"background-color: rgba(225,29,72,0.08); border: 1px solid rgba(225,29,72,0.25); "
            f"border-radius: 8px; color: #FB7185; padding: 10px 12px; "
            f"font-size: 11px; font-weight: 700; font-family: 'Inter';"
        )
        self.lbl_notification_error.hide()
        body_layout.addWidget(self.lbl_notification_error)

        self.lbl_notification_success = QLabel()
        self.lbl_notification_success.setStyleSheet(
            f"background-color: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.25); "
            f"border-radius: 8px; color: #4ADE80; padding: 10px 12px; "
            f"font-size: 11px; font-weight: 700; font-family: 'Inter';"
        )
        self.lbl_notification_success.hide()
        body_layout.addWidget(self.lbl_notification_success)

        footer = QFrame()
        footer.setObjectName("NotificationsFooter")
        footer.setStyleSheet(f"""
            QFrame#NotificationsFooter {{
                background: transparent;
                border-top: 1px solid #242424;
            }}
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 12, 0, 0)
        footer_hint = QLabel("Los cambios se aplican inmediatamente después de guardar.")
        footer_hint.setStyleSheet(
            f"color: #555D69; font-size: 11px; font-weight: 500; "
            f"font-family: 'Inter'; border: none;"
        )
        footer_layout.addWidget(footer_hint)
        footer_layout.addStretch()

        self.btn_save = QPushButton("Guardar preferencias")
        self.btn_save.setFixedHeight(42)
        self.btn_save.setMinimumWidth(180)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {RED_H}, stop:1 {RED});
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 800;
                font-family: 'Inter';
                padding: 0 24px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #FF2040, stop:1 {RED_H});
            }}
            QPushButton:pressed {{
                background: #9A0C22;
            }}
            QPushButton:disabled {{
                background: #252525;
                color: #666666;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self.btn_save)
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(200, 16, 46, 70))
        self.btn_save.setGraphicsEffect(shadow)
        self.btn_save.clicked.connect(self._save_preferences)
        footer_layout.addWidget(self.btn_save)
        body_layout.addWidget(footer)

        layout.addWidget(body, 1)

    # ── Classes Card ──────────────────────────────────────────────

    def _build_classes_card(self, parent_layout):
        self.toggle_classes = ToggleSwitch(initial=True)
        self.toggle_classes.toggled.connect(self._on_classes_toggle)

        card, advanced, adv_lay, sep, status_lbl, desc_lbl = (
            self._build_notification_settings_card(
                parent_layout,
                category="classes",
                eyebrow="CLASES",
                title="Clases próximas",
                description=self._DESC_CLASSES,
                accent_color=RED,
                accent_bg="rgba(200,16,46,0.12)",
                accent_border="rgba(200,16,46,0.25)",
                icon_name="calendar",
                toggle=self.toggle_classes,
            )
        )
        self.classes_notification_card = card
        self.classes_advanced_container = advanced
        self.classes_separator = sep
        self.lbl_classes_status = status_lbl
        self.lbl_classes_desc = desc_lbl

        chan_caption = self._make_field_caption("CANALES DE ENTREGA")
        adv_lay.addWidget(chan_caption)
        chan_row = QHBoxLayout()
        chan_row.setSpacing(12)
        self._classes_channel_cards = []
        self.chk_classes_in_app, c1 = self._create_channel_option(
            "Campana interna", "Dentro de DOJO ADMIN"
        )
        self._classes_channel_cards.append(c1)
        self.chk_classes_windows, c2 = self._create_channel_option(
            "Notificación de Windows", "Centro de notificaciones"
        )
        self._classes_channel_cards.append(c2)
        chan_row.addWidget(self.chk_classes_in_app)
        chan_row.addWidget(self.chk_classes_windows)
        adv_lay.addLayout(chan_row)

        time_caption = self._make_field_caption(
            "ANTICIPACIÓN",
            "Define cuánto tiempo antes se enviará el recordatorio"
        )
        adv_lay.addWidget(time_caption)
        time_row = QHBoxLayout()
        time_row.setContentsMargins(0, 0, 0, 0)
        time_row.setSpacing(0)
        self.combo_classes_minutes = self._create_time_combo([
            ("5 minutos antes", 5),
            ("10 minutos antes", 10),
            ("15 minutos antes", 15),
            ("30 minutos antes", 30),
            ("1 hora antes", 60),
        ])
        time_row.addWidget(self.combo_classes_minutes)
        time_row.addStretch()
        adv_lay.addLayout(time_row)

        start_row, start_lay, start_desc = self._create_start_option(
            "Envía una segunda alerta cuando la clase inicie."
        )
        self.chk_classes_at_start = QCheckBox("Notificar al comenzar")
        self.chk_classes_at_start.setObjectName("StartOption")
        self.chk_classes_at_start.setChecked(True)
        self.chk_classes_at_start.setStyleSheet(self._START_QSS)
        start_lay.addWidget(self.chk_classes_at_start)
        start_text_col = QVBoxLayout()
        start_text_col.setSpacing(2)
        start_text_col.addWidget(self.chk_classes_at_start)
        start_sub = QLabel(start_desc)
        start_sub.setStyleSheet(
            f"color: #6B7280; font-size: 10px; font-weight: 500; "
            f"font-family: 'Inter','Segoe UI',sans-serif; "
            f"background: transparent; border: none;"
        )
        start_text_col.addWidget(start_sub)
        start_lay.addLayout(start_text_col, 1)
        adv_lay.addWidget(start_row)

    # ── Events Card ───────────────────────────────────────────────

    def _build_events_card(self, parent_layout):
        self.toggle_events = ToggleSwitch(initial=True)
        self.toggle_events.toggled.connect(self._on_events_toggle)

        card, advanced, adv_lay, sep, status_lbl, desc_lbl = (
            self._build_notification_settings_card(
                parent_layout,
                category="events",
                eyebrow="EVENTOS",
                title="Futuros eventos",
                description=self._DESC_EVENTS,
                accent_color=PURPLE,
                accent_bg="rgba(168,85,247,0.10)",
                accent_border="rgba(168,85,247,0.22)",
                icon_name="bell",
                toggle=self.toggle_events,
            )
        )
        self.events_notification_card = card
        self.events_advanced_container = advanced
        self.events_separator = sep
        self.lbl_events_status = status_lbl
        self.lbl_events_desc = desc_lbl

        chan_caption = self._make_field_caption("CANALES DE ENTREGA")
        adv_lay.addWidget(chan_caption)
        chan_row = QHBoxLayout()
        chan_row.setSpacing(12)
        self._events_channel_cards = []
        self.chk_events_in_app, e1 = self._create_channel_option(
            "Campana interna", "Dentro de DOJO ADMIN"
        )
        self._events_channel_cards.append(e1)
        self.chk_events_windows, e2 = self._create_channel_option(
            "Notificación de Windows", "Centro de notificaciones"
        )
        self._events_channel_cards.append(e2)
        chan_row.addWidget(self.chk_events_in_app)
        chan_row.addWidget(self.chk_events_windows)
        adv_lay.addLayout(chan_row)

        time_caption = self._make_field_caption(
            "ANTICIPACIÓN",
            "Define cuánto tiempo antes se enviará el recordatorio"
        )
        adv_lay.addWidget(time_caption)
        time_row = QHBoxLayout()
        time_row.setContentsMargins(0, 0, 0, 0)
        time_row.setSpacing(0)
        self.combo_events_minutes = self._create_time_combo([
            ("15 minutos antes", 15),
            ("30 minutos antes", 30),
            ("1 hora antes", 60),
            ("3 horas antes", 180),
            ("12 horas antes", 720),
            ("1 día antes", 1440),
            ("2 días antes", 2880),
            ("1 semana antes", 10080),
        ])
        time_row.addWidget(self.combo_events_minutes)
        time_row.addStretch()
        adv_lay.addLayout(time_row)

        start_row, start_lay, start_desc = self._create_start_option(
            "Envía una segunda alerta cuando el evento inicie."
        )
        self.chk_events_at_start = QCheckBox("Notificar al comenzar")
        self.chk_events_at_start.setObjectName("StartOption")
        self.chk_events_at_start.setChecked(True)
        self.chk_events_at_start.setStyleSheet(self._START_QSS)
        start_text_col = QVBoxLayout()
        start_text_col.setSpacing(2)
        start_text_col.addWidget(self.chk_events_at_start)
        start_sub = QLabel(start_desc)
        start_sub.setStyleSheet(
            f"color: #6B7280; font-size: 10px; font-weight: 500; "
            f"font-family: 'Inter','Segoe UI',sans-serif; "
            f"background: transparent; border: none;"
        )
        start_text_col.addWidget(start_sub)
        start_lay.addLayout(start_text_col, 1)
        adv_lay.addWidget(start_row)

    # ── Disabled helpers ──────────────────────────────────────────

    def _make_disabled_group_title(self, text, badge=""):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 11px; font-weight: 900; "
            f"font-family: 'Inter'; letter-spacing: 1px; "
            f"border: none; padding-bottom: 8px; "
            f"border-bottom: 1px solid {BORDER_2};"
        )
        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(8)
        wrapper_layout.addWidget(lbl)
        if badge:
            b = QLabel(badge)
            b.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_DIM};
                    background: rgba(255,255,255,0.04);
                    border-radius: 4px;
                    padding: 1px 5px;
                    font-size: 8px;
                    font-weight: 900;
                    font-family: 'Inter';
                    border: none;
                }}
            """)
            wrapper_layout.addWidget(b)
            wrapper_layout.addStretch()
        return wrapper

    def _make_disabled_toggle_row(self, label, desc):
        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border-bottom: 1px solid {BORDER_2};
                opacity: 0.4;
            }}
        """)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 10, 0, 10)
        row_layout.setSpacing(14)
        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 13px; font-weight: 600; "
            f"font-family: 'Inter'; border: none;"
        )
        d = QLabel(desc)
        d.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 11px; font-weight: 500; border: none;"
        )
        d.setWordWrap(True)
        info_col.addWidget(lbl)
        info_col.addWidget(d)
        row_layout.addLayout(info_col, 1)
        return row

    # ── Toggle handlers ───────────────────────────────────────────

    def _on_classes_toggle(self, on):
        if on:
            self.classes_advanced_container.show()
            self.classes_separator.show()
            self.lbl_classes_desc.setText(self._DESC_CLASSES)
            self.lbl_classes_status.setText("ACTIVO")
            self.lbl_classes_status.setStyleSheet(
                f"color: #22C55E; background-color: rgba(34,197,94,0.10); "
                f"border: 1px solid rgba(34,197,94,0.20); border-radius: 8px; "
                f"padding: 4px 8px; font-size: 8px; font-weight: 900; "
                f"letter-spacing: 0.8px; font-family: 'Inter','Segoe UI',sans-serif;"
            )
        else:
            self.classes_advanced_container.hide()
            self.classes_separator.hide()
            self.lbl_classes_desc.setText(self._DESC_CLASSES_OFF)
            self.lbl_classes_status.setText("INACTIVO")
            self.lbl_classes_status.setStyleSheet(
                f"color: #6B7280; background-color: rgba(107,114,128,0.08); "
                f"border: 1px solid rgba(107,114,128,0.15); border-radius: 8px; "
                f"padding: 4px 8px; font-size: 8px; font-weight: 900; "
                f"letter-spacing: 0.8px; font-family: 'Inter','Segoe UI',sans-serif;"
            )

    def _on_events_toggle(self, on):
        if on:
            self.events_advanced_container.show()
            self.events_separator.show()
            self.lbl_events_desc.setText(self._DESC_EVENTS)
            self.lbl_events_status.setText("ACTIVO")
            self.lbl_events_status.setStyleSheet(
                f"color: #22C55E; background-color: rgba(34,197,94,0.10); "
                f"border: 1px solid rgba(34,197,94,0.20); border-radius: 8px; "
                f"padding: 4px 8px; font-size: 8px; font-weight: 900; "
                f"letter-spacing: 0.8px; font-family: 'Inter','Segoe UI',sans-serif;"
            )
        else:
            self.events_advanced_container.hide()
            self.events_separator.hide()
            self.lbl_events_desc.setText(self._DESC_EVENTS_OFF)
            self.lbl_events_status.setText("INACTIVO")
            self.lbl_events_status.setStyleSheet(
                f"color: #6B7280; background-color: rgba(107,114,128,0.08); "
                f"border: 1px solid rgba(107,114,128,0.15); border-radius: 8px; "
                f"padding: 4px 8px; font-size: 8px; font-weight: 900; "
                f"letter-spacing: 0.8px; font-family: 'Inter','Segoe UI',sans-serif;"
            )

    # ── Load / Save ───────────────────────────────────────────────

    def _load_preferences(self):
        self._loading = True
        self._load_worker = NotificationPreferencesLoadWorker(
            self._repository, self._user_id,
        )
        self._load_worker.loaded.connect(self._apply_preferences)
        self._load_worker.failed.connect(self._on_load_failed)
        self._load_worker.start()

    def _apply_preferences(self, preferences):
        self._preferences = dict(preferences)
        self._loading = True

        self.toggle_classes.blockSignals(True)
        self.toggle_classes.set_on(bool(preferences.get("classes_enabled", True)))
        self.toggle_classes.blockSignals(False)

        self.chk_classes_in_app.blockSignals(True)
        self.chk_classes_in_app.setChecked(bool(preferences.get("classes_in_app", True)))
        self.chk_classes_in_app.blockSignals(False)

        self.chk_classes_windows.blockSignals(True)
        self.chk_classes_windows.setChecked(bool(preferences.get("classes_windows", True)))
        self.chk_classes_windows.blockSignals(False)

        class_minutes = int(preferences.get("classes_minutes_before", 15))
        for i in range(self.combo_classes_minutes.count()):
            if self.combo_classes_minutes.itemData(i) == class_minutes:
                self.combo_classes_minutes.blockSignals(True)
                self.combo_classes_minutes.setCurrentIndex(i)
                self.combo_classes_minutes.blockSignals(False)
                break

        self.chk_classes_at_start.blockSignals(True)
        self.chk_classes_at_start.setChecked(bool(preferences.get("classes_notify_at_start", True)))
        self.chk_classes_at_start.blockSignals(False)

        self.toggle_events.blockSignals(True)
        self.toggle_events.set_on(bool(preferences.get("events_enabled", True)))
        self.toggle_events.blockSignals(False)

        self.chk_events_in_app.blockSignals(True)
        self.chk_events_in_app.setChecked(bool(preferences.get("events_in_app", True)))
        self.chk_events_in_app.blockSignals(False)

        self.chk_events_windows.blockSignals(True)
        self.chk_events_windows.setChecked(bool(preferences.get("events_windows", True)))
        self.chk_events_windows.blockSignals(False)

        event_minutes = int(preferences.get("events_minutes_before", 1440))
        for i in range(self.combo_events_minutes.count()):
            if self.combo_events_minutes.itemData(i) == event_minutes:
                self.combo_events_minutes.blockSignals(True)
                self.combo_events_minutes.setCurrentIndex(i)
                self.combo_events_minutes.blockSignals(False)
                break

        self.chk_events_at_start.blockSignals(True)
        self.chk_events_at_start.setChecked(bool(preferences.get("events_notify_at_start", True)))
        self.chk_events_at_start.blockSignals(False)

        self._loading = False
        self._on_classes_toggle(self.toggle_classes.is_on())
        self._on_events_toggle(self.toggle_events.is_on())

    def _on_load_failed(self, error):
        self._loading = False
        self._show_error(f"Error cargando preferencias: {error}")

    def _save_preferences(self):
        classes_enabled = self.toggle_classes.is_on()
        events_enabled = self.toggle_events.is_on()

        if classes_enabled:
            in_app = self.chk_classes_in_app.isChecked()
            windows = self.chk_classes_windows.isChecked()
            if not in_app and not windows:
                self._show_error("Selecciona al menos un canal para clases")
                return

        if events_enabled:
            in_app = self.chk_events_in_app.isChecked()
            windows = self.chk_events_windows.isChecked()
            if not in_app and not windows:
                self._show_error("Selecciona al menos un canal para eventos")
                return

        self._hide_error()
        self.btn_save.setEnabled(False)
        self.btn_save.setText("Guardando...")

        preferences = {
            "classes_enabled": classes_enabled,
            "classes_in_app": self.chk_classes_in_app.isChecked(),
            "classes_windows": self.chk_classes_windows.isChecked(),
            "classes_minutes_before": int(
                self.combo_classes_minutes.currentData()
            ),
            "classes_notify_at_start": self.chk_classes_at_start.isChecked(),
            "events_enabled": events_enabled,
            "events_in_app": self.chk_events_in_app.isChecked(),
            "events_windows": self.chk_events_windows.isChecked(),
            "events_minutes_before": int(
                self.combo_events_minutes.currentData()
            ),
            "events_notify_at_start": self.chk_events_at_start.isChecked(),
        }

        self._save_worker = NotificationPreferencesSaveWorker(
            self._repository, self._user_id, preferences,
        )
        self._save_worker.saved.connect(self._on_save_success)
        self._save_worker.failed.connect(self._on_save_failed)
        self._save_worker.start()

    def _on_save_success(self, preferences):
        self._preferences = dict(preferences)
        self.btn_save.setEnabled(True)
        self.btn_save.setText("Guardar preferencias")
        self._show_success("Preferencias guardadas correctamente")
        self.preferences_saved.emit(preferences)

    def _on_save_failed(self, error):
        self.btn_save.setEnabled(True)
        self.btn_save.setText("Guardar preferencias")
        self._show_error(f"Error guardando: {error}")

    def _show_error(self, text):
        self.lbl_notification_success.hide()
        self.lbl_notification_error.setText(text)
        self.lbl_notification_error.show()
        QTimer.singleShot(5000, self._hide_error)

    def _show_success(self, text):
        self.lbl_notification_error.hide()
        self.lbl_notification_success.setText(text)
        self.lbl_notification_success.show()
        QTimer.singleShot(3500, self._hide_success)

    def _hide_error(self):
        self.lbl_notification_error.hide()

    def _hide_success(self):
        self.lbl_notification_success.hide()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN: AccountView
# ═══════════════════════════════════════════════════════════════════════════════
class AccountView(QWidget):
    notification_preferences_changed = pyqtSignal(dict)

    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self._user = user
        self._current_section = "profile"
        self.setStyleSheet(f"background-color: {BG_DEEP};")

        from repositories.account_repository import AccountRepository
        self.account_repository = AccountRepository()

        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical { background: transparent; width: 6px; }
            QScrollBar::handle:vertical {
                background: #2A2A2A; border-radius: 3px; min-height: 20px;
            }
        """)

        inner = QWidget()
        inner.setStyleSheet(f"background-color: {BG_DEEP};")
        root = QVBoxLayout(inner)
        root.setContentsMargins(28, 28, 28, 60)
        root.setSpacing(20)

        # ── Page header ──
        header = QFrame()
        header.setStyleSheet("background: transparent; border: none;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        title = QLabel("Configuración de cuenta")
        title.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 26px; font-weight: 900; "
            f"font-family: 'Inter'; letter-spacing: -0.5px; border: none;"
        )
        header_layout.addWidget(title)

        subtitle = QLabel("Gestiona tu perfil, seguridad y notificaciones del sistema")
        subtitle.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 13px; font-weight: 500; border: none;"
        )
        header_layout.addWidget(subtitle)

        root.addWidget(header)

        # ── Account layout: sub-nav + content ──
        account_layout = QHBoxLayout()
        account_layout.setSpacing(24)
        account_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Sub-nav
        sub_nav = self._build_sub_nav()
        account_layout.addWidget(sub_nav, 0)

        # Content panel
        self.content_panel = QFrame()
        self.content_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 18px;
            }}
        """)
        self.content_layout = QVBoxLayout(self.content_panel)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Sections
        self.section_profile = ProfileSection(self._user)
        self.section_security = SecuritySection(user=self._user)
        self.section_notifications = NotificationsSection(
            user_id=self._user.get("id"),
            repository=self.account_repository,
        )

        self.section_notifications.preferences_saved.connect(
            self.notification_preferences_changed.emit
        )

        self.content_layout.addWidget(self.section_profile)
        self.content_layout.addWidget(self.section_security)
        self.content_layout.addWidget(self.section_notifications)

        # Show only profile by default
        self.section_security.hide()
        self.section_notifications.hide()

        account_layout.addWidget(self.content_panel, 1)
        root.addLayout(account_layout)

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(scroll)

    def _build_sub_nav(self) -> QFrame:
        nav = QFrame()
        nav.setFixedWidth(240)
        nav.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 18px;
            }}
        """)
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(8, 8, 8, 8)
        nav_layout.setSpacing(2)

        # Header
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border-bottom: 1px solid {BORDER_2};
                border-radius: 0;
            }}
        """)
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(14, 14, 14, 10)
        h_layout.setSpacing(4)

        h_title = QLabel("CUENTA")
        h_title.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 10px; font-weight: 900; "
            f"font-family: 'Inter'; letter-spacing: 1.2px; border: none;"
        )
        h_layout.addWidget(h_title)

        # User mini-card
        user_row = QHBoxLayout()
        user_row.setSpacing(10)
        avatar = QLabel(self._user_initials())
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {PURPLE}, stop:1 #581C87);
                color: white;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 900;
                font-family: 'Inter';
                border: none;
            }}
        """)
        user_row.addWidget(avatar)

        user_info = QVBoxLayout()
        user_info.setSpacing(1)
        u_name = QLabel(str(self._user.get("username", "Usuario")))
        u_name.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 12px; font-weight: 800; "
            f"font-family: 'Inter'; border: none;"
        )
        u_role = QLabel("Administrador")
        u_role.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 10px; font-weight: 600; border: none;"
        )
        user_info.addWidget(u_name)
        user_info.addWidget(u_role)
        user_row.addLayout(user_info, 1)
        h_layout.addLayout(user_row)

        nav_layout.addWidget(header)

        # Nav items
        self.nav_profile = SubNavItem("user", "Perfil", "profile")
        self.nav_security = SubNavItem("lock", "Seguridad", "security")
        self.nav_notifications = SubNavItem("bell", "Notificaciones", "notifications", badge="3")

        self.nav_profile.clicked_nav.connect(self._switch_section)
        self.nav_security.clicked_nav.connect(self._switch_section)
        self.nav_notifications.clicked_nav.connect(self._switch_section)

        self.nav_profile.set_active(True)

        nav_layout.addWidget(self.nav_profile)
        nav_layout.addWidget(self.nav_security)
        nav_layout.addWidget(self.nav_notifications)
        nav_layout.addStretch()

        return nav

    def _switch_section(self, section: str):
        self._current_section = section

        # Update nav active states
        self.nav_profile.set_active(section == "profile")
        self.nav_security.set_active(section == "security")
        self.nav_notifications.set_active(section == "notifications")

        # Update sections visibility
        self.section_profile.setVisible(section == "profile")
        self.section_security.setVisible(section == "security")
        self.section_notifications.setVisible(section == "notifications")

    def _user_initials(self) -> str:
        name = str(self._user.get("username", "U"))
        parts = name.strip().split()
        return "".join(p[0].upper() for p in parts[:2]) or "U"
