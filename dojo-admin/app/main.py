"""
app/main.py  — punto de entrada principal con soporte i18n en caliente.
"""

import sys
import os
import traceback
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame,
    QScrollArea, QGraphicsDropShadowEffect, QSizePolicy,
    QSystemTrayIcon,
)
from PyQt6.QtCore import (
    Qt, qInstallMessageHandler, QTimer, QRectF, QPointF,
    QPropertyAnimation, QEasingCurve, pyqtSignal,
)
from PyQt6.QtGui import (
    QColor, QPainter, QPen, QPainterPath, QIcon,
)


# ── LOGGING SYSTEM ────────────────────────────────────────────────────
from core.app_logger import (
    get_logger,
    get_log_directory,
    install_global_exception_logging,
    resource_path,
)

logger = get_logger("main")

install_global_exception_logging()


# ── GLOBAL EXCEPTION HOOK ─────────────────────────────────────────────
def global_exception_hook(exc_type, exc_value, exc_traceback):
    import time as _time
    ts = _time.strftime("%H:%M:%S")

    logger.critical(
        "UNCAUGHT PYTHON EXCEPTION | TYPE=%s VALUE=%s",
        exc_type.__name__,
        exc_value,
        exc_info=(exc_type, exc_value, exc_traceback),
    )

    if sys.stdout is not None:
        print("\n" + "=" * 80)
        print(f"[FORENSIC {ts}] UNCAUGHT PYTHON EXCEPTION")
        print(f"TYPE: {exc_type.__name__}")
        print(f"VALUE: {exc_value}")
        print("=" * 80)
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print("=" * 80)

sys.excepthook = global_exception_hook


# ── QT MESSAGE HANDLER ────────────────────────────────────────────────
def qt_message_handler(mode, context, message):
    try:
        mode_name = getattr(mode, "name", None)
        if not mode_name:
            mode_name = str(mode)

        logger.warning("QT %s: %s", mode_name, message)

        if sys.stdout is not None:
            print(f"[QT:{mode_name}] {message}")
    except Exception as e:
        if sys.stdout is not None:
            print(f"[QT:LOGGER_ERROR] {message} | logger_error={e}")

qInstallMessageHandler(qt_message_handler)


# ── Cargar idioma guardado ANTES de importar cualquier vista ──────────
from config import settings as cfg
from core.i18n import i18n, tr
from core.debug import debug_log

_saved_lang = cfg.get("language", "es")
if _saved_lang != "es":
    i18n._load(_saved_lang)


# ── Importaciones de vistas ───────────────────────────────────────────
from services.auth_service import AuthService
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.students_view import StudentsView
from database.connection import db
from repositories.classes_repository import ClassesRepository


# ─── PALETA ───────────────────────────────────────────────────────────
BG_SIDEBAR  = "#0A0A0A"
BG_MAIN     = "#050505"
BG_CARD     = "#161616"
BG_HOVER    = "#1A1A1A"
BG_ACTIVE   = "#1E1E1E"
BORDER      = "#2A2A2A"
BORDER_2    = "#1A1A1A"
RED         = "#C8102E"
RED_H       = "#E8152F"
PURPLE      = "#A855F7"
TEXT_PRI    = "#F0F0F0"
TEXT_SEC    = "#9CA3AF"
TEXT_MUT    = "#6B7280"
TEXT_DIM    = "#3D4451"

SIDEBAR_W           = 240
SIDEBAR_W_COLLAPSED = 64


# ═══════════════════════════════════════════════════════════════════════
# ICON LABEL
# ═══════════════════════════════════════════════════════════════════════
class IconLabel(QWidget):
    ICONS = {
        "dashboard":     '<rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/><rect x="3" y="13" width="8" height="8" rx="1"/><rect x="13" y="13" width="8" height="8" rx="1"/>',
        "students":      '<circle cx="9" cy="7" r="4"/><line x1="3" y1="21" x2="3" y2="19"/><line x1="15" y1="21" x2="15" y2="19"/><polyline points="3 19 3 18 5 15 9 14 13 15 15 18 15 19"/><line x1="16" y1="11" x2="19" y2="11"/><line x1="19" y1="8" x2="22" y2="11"/><line x1="22" y1="11" x2="19" y2="14"/>',
        "classes":       '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
        "belts":         '<rect x="2" y="9" width="20" height="6" rx="3"/><line x1="2" y1="12" x2="8" y2="12"/><line x1="16" y1="12" x2="22" y2="12"/><circle cx="12" cy="12" r="2"/>',
        "finances":      '<rect x="2" y="6" width="20" height="14" rx="2"/><polyline points="2 10 22 10"/><line x1="6" y1="15" x2="10" y2="15"/>',
        "income":        '<polyline points="2 17 8 11 12 15 22 5"/><polyline points="16 5 22 5 22 11"/>',
        "expense":       '<polyline points="2 7 8 13 12 9 22 19"/><polyline points="16 19 22 19 22 13"/>',
        "receivables":   '<rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/><line x1="13" y1="15" x2="17" y2="15"/>',
        "collection":    '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
        "inventory":     '<rect x="2" y="7" width="20" height="15" rx="2"/><polyline points="16 2 12 7 8 2"/><line x1="12" y1="12" x2="12" y2="17"/><line x1="9.5" y1="14.5" x2="14.5" y2="14.5"/>',
        "memberships":   '<rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/><line x1="6" y1="15" x2="8" y2="15"/><line x1="11" y1="15" x2="14" y2="15"/>',
        "services":      '<polyline points="14 2 14 8 20 8"/><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="13" y2="17"/>',
        "reports":       '<line x1="6" y1="20" x2="6" y2="14"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="18" y1="20" x2="18" y2="10"/>',
        "settings":      '<circle cx="12" cy="12" r="3"/><line x1="12" y1="2" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="22"/><line x1="4.22" y1="4.22" x2="6.34" y2="6.34"/><line x1="17.66" y1="17.66" x2="19.78" y2="19.78"/><line x1="2" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="22" y2="12"/><line x1="4.22" y1="19.78" x2="6.34" y2="17.66"/><line x1="17.66" y1="6.34" x2="19.78" y2="4.22"/>',
        "home":          '<polyline points="3 9 12 2 21 9"/><polyline points="9 22 9 12 15 12 15 22"/><rect x="3" y="9" width="18" height="13" rx="1"/>',
        "chevron-right": '<polyline points="9 18 15 12 9 6"/>',
        "chevron-left":  '<polyline points="15 18 9 12 15 6"/>',
        "chevron-down":  '<polyline points="6 9 12 15 18 9"/>',
        "chevron-up":    '<polyline points="18 15 12 9 6 15"/>',
        "calendar":      '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
        "event": (
            '<rect x="3" y="4" width="18" height="18" rx="2"/>'
            '<line x1="8" y1="2" x2="8" y2="6"/>'
            '<line x1="16" y1="2" x2="16" y2="6"/>'
            '<line x1="3" y1="10" x2="21" y2="10"/>'
            '<polyline points="12 13 13 15 16 15 14 17 '
            '15 20 12 18 9 20 10 17 8 15 11 15 12 13"/>'
        ),
        "bell": (
            '<path d="M6 16 L7 14 L7 9 '
            'C7 6 9 4 12 4 '
            'C15 4 17 6 17 9 '
            'L17 14 L18 16 Z"/>'
            '<line x1="5" y1="16" x2="19" y2="16"/>'
            '<path d="M10 19 C10.5 21 13.5 21 14 19"/>'
            '<line x1="12" y1="2" x2="12" y2="4"/>'
        ),
        "search":        '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
        "logout":        '<polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/><rect x="3" y="3" width="8" height="18" rx="1"/>',
        "panel-left":    '<rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/>',
    }

    def __init__(self, icon_name: str, size: int = 18, color: str = TEXT_SEC, parent=None):
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
        import re
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
            elements = re.findall(r'<(circle|rect|line|polyline|path)\s([^/]+)/?>', path_data)
            for tag, attrs_str in elements:
                attrs = dict(re.findall(r'(\w+)="([^"]*)"', attrs_str))
                if tag == "circle":
                    cx, cy, r = float(attrs.get("cx", 0)), float(attrs.get("cy", 0)), float(attrs.get("r", 0))
                    p.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))
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
                    pts = re.findall(r'[\d.]+', attrs.get("points", ""))
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
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════
# NAV BUTTON — item simple de navegación
# ═══════════════════════════════════════════════════════════════════════
class NavButton(QWidget):
    clicked_nav = pyqtSignal(str)

    def __init__(self, icon_name: str, label: str, page_key: str, parent=None, label_key: str = None):
        super().__init__(parent)
        self._icon_name = icon_name
        self._label_text = label
        self._label_key = label_key
        self._page_key = page_key
        self._active = False
        self._hovered = False

        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._apply_style()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        self.icon_w = IconLabel(icon_name, 18, TEXT_MUT)
        layout.addWidget(self.icon_w)

        self.lbl = QLabel(label)
        self.lbl.setStyleSheet(
            f"color: {TEXT_SEC}; font-size: 13px; font-weight: 500; border: none; background: transparent;"
        )
        layout.addWidget(self.lbl, 1)

    def set_active(self, active: bool):
        self._active = active
        self._apply_style()
        if active:
            self.icon_w.set_color(TEXT_PRI)
            self.lbl.setStyleSheet(
                f"color: {TEXT_PRI}; font-size: 13px; font-weight: 700; border: none; background: transparent;"
            )
        else:
            self.icon_w.set_color(TEXT_MUT)
            self.lbl.setStyleSheet(
                f"color: {TEXT_SEC}; font-size: 13px; font-weight: 500; border: none; background: transparent;"
            )

    def set_label(self, text: str):
        self._label_text = text
        self.lbl.setText(text)

    def set_collapsed(self, collapsed: bool):
        self.lbl.setVisible(not collapsed)

    def _apply_style(self):
        if self._active:
            self.setStyleSheet(f"""
                QWidget {{
                    background: {BG_ACTIVE};
                    border-radius: 8px;
                    border-left: 2px solid {RED_H};
                }}
            """)
        elif self._hovered:
            self.setStyleSheet(f"QWidget {{ background: {BG_HOVER}; border-radius: 8px; }}")
        else:
            self.setStyleSheet("QWidget { background: transparent; border-radius: 8px; }")

    def enterEvent(self, event):
        self._hovered = True
        if not self._active:
            self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        if not self._active:
            self._apply_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.clicked_nav.emit(self._page_key)
        super().mousePressEvent(event)


# ═══════════════════════════════════════════════════════════════════════
# SUBMENU ITEM — fila pequeña dentro de un grupo expandible
# ═══════════════════════════════════════════════════════════════════════
class SubmenuItem(QWidget):
    clicked_sub = pyqtSignal(str)  # emite page_key

    def __init__(self, icon_name: str, label: str, page_key: str, parent=None):
        super().__init__(parent)
        self._icon_name = icon_name
        self._label_text = label
        self._page_key = page_key
        self._active = False
        self._hovered = False

        self.setFixedHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._apply_style()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 10, 0)
        layout.setSpacing(10)

        # Dot indicator
        self.dot = QLabel()
        self.dot.setFixedSize(6, 6)
        self._set_dot_color(TEXT_DIM)
        layout.addWidget(self.dot)

        self.icon_w = IconLabel(icon_name, 15, TEXT_DIM)
        layout.addWidget(self.icon_w)

        self.lbl = QLabel(label)
        self.lbl.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 12px; font-weight: 500; border: none; background: transparent;"
        )
        layout.addWidget(self.lbl, 1)

    def _set_dot_color(self, color: str):
        self.dot.setStyleSheet(
            f"background: {color}; border-radius: 3px; border: none;"
        )

    def set_active(self, active: bool):
        self._active = active
        self._apply_style()
        if active:
            self._set_dot_color(RED_H)
            self.icon_w.set_color(TEXT_PRI)
            self.lbl.setStyleSheet(
                f"color: {TEXT_PRI}; font-size: 12px; font-weight: 700; border: none; background: transparent;"
            )
        else:
            self._set_dot_color(TEXT_DIM)
            self.icon_w.set_color(TEXT_DIM)
            self.lbl.setStyleSheet(
                f"color: {TEXT_MUT}; font-size: 12px; font-weight: 500; border: none; background: transparent;"
            )

    def set_collapsed(self, collapsed: bool):
        self.lbl.setVisible(not collapsed)
        self.dot.setVisible(not collapsed)

    def set_label(self, text: str):
        self._label_text = text
        self.lbl.setText(text)

    def _apply_style(self):
        if self._active:
            self.setStyleSheet(f"QWidget {{ background: {BG_ACTIVE}; border-radius: 6px; }}")
        elif self._hovered:
            self.setStyleSheet(f"QWidget {{ background: {BG_HOVER}; border-radius: 6px; }}")
        else:
            self.setStyleSheet("QWidget { background: transparent; border-radius: 6px; }")

    def enterEvent(self, event):
        self._hovered = True
        if not self._active:
            self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        if not self._active:
            self._apply_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.clicked_sub.emit(self._page_key)
        super().mousePressEvent(event)


# ═══════════════════════════════════════════════════════════════════════
# EXPANDABLE GROUP — botón con submenu animado (Finanzas / Administración)
# ═══════════════════════════════════════════════════════════════════════
class ExpandableGroup(QWidget):
    """Un NavButton con submenu que se expande/colapsa con animación."""
    sub_clicked = pyqtSignal(str)  # page_key del subitem

    def __init__(self, icon_name: str, label: str, subitems: list, parent=None):
        """
        subitems: list of (icon_name, label, page_key)
        """
        super().__init__(parent)
        self._expanded = False
        self._sub_items: list[SubmenuItem] = []
        self._active_sub: str | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header row ──
        self.header = QWidget()
        self.header.setFixedHeight(40)
        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._hdr_hovered = False

        hdr_layout = QHBoxLayout(self.header)
        hdr_layout.setContentsMargins(10, 0, 10, 0)
        hdr_layout.setSpacing(10)

        self.icon_w = IconLabel(icon_name, 18, TEXT_MUT)
        hdr_layout.addWidget(self.icon_w)

        self.lbl = QLabel(label)
        self.lbl.setStyleSheet(
            f"color: {TEXT_SEC}; font-size: 13px; font-weight: 500; border: none; background: transparent;"
        )
        hdr_layout.addWidget(self.lbl, 1)

        self.chevron = IconLabel("chevron-down", 14, TEXT_DIM)
        hdr_layout.addWidget(self.chevron)

        self.header.mousePressEvent = lambda e: self._toggle()
        self.header.enterEvent = lambda e: self._hdr_enter()
        self.header.leaveEvent = lambda e: self._hdr_leave()
        layout.addWidget(self.header)

        # ── Submenu container ──
        self.sub_container = QWidget()
        self.sub_container.setStyleSheet("background: transparent;")
        sub_layout = QVBoxLayout(self.sub_container)
        sub_layout.setContentsMargins(8, 2, 0, 2)
        sub_layout.setSpacing(1)

        for icon, lbl_text, page_key in subitems:
            item = SubmenuItem(icon, lbl_text, page_key)
            item.clicked_sub.connect(self._on_sub_clicked)
            self._sub_items.append(item)
            sub_layout.addWidget(item)

        # Start collapsed
        self.sub_container.setMaximumHeight(0)
        self.sub_container.setVisible(True)
        layout.addWidget(self.sub_container)

        self._apply_hdr_style()

    def _toggle(self):
        self._expanded = not self._expanded
        target_h = self.sub_container.sizeHint().height() if self._expanded else 0

        anim = QPropertyAnimation(self.sub_container, b"maximumHeight", self)
        anim.setDuration(250)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(self.sub_container.maximumHeight())
        anim.setEndValue(target_h)
        anim.start()
        self._anim = anim

        self.chevron.set_icon("chevron-up" if self._expanded else "chevron-down")

    def _on_sub_clicked(self, page_key: str):
        self._active_sub = page_key
        for item in self._sub_items:
            item.set_active(item._page_key == page_key)
        # Mark header as having an active child
        self._apply_hdr_style(has_active=True)
        self.sub_clicked.emit(page_key)

    def set_active_sub(self, page_key: str | None):
        """Called externally to mark a subitem as active."""
        self._active_sub = page_key
        has = page_key is not None
        for item in self._sub_items:
            item.set_active(item._page_key == page_key)
        self._apply_hdr_style(has_active=has)
        if has and not self._expanded:
            self._toggle()

    def clear_active(self):
        self._active_sub = None
        for item in self._sub_items:
            item.set_active(False)
        self._apply_hdr_style(has_active=False)

    def set_collapsed(self, collapsed: bool):
        self.lbl.setVisible(not collapsed)
        self.chevron.setVisible(not collapsed)
        for item in self._sub_items:
            item.set_collapsed(collapsed)
        if collapsed and self._expanded:
            self._toggle()

    def set_label(self, text: str):
        self.lbl.setText(text)

    def set_sub_label(self, page_key: str, text: str):
        for item in self._sub_items:
            if item._page_key == page_key:
                item.set_label(text)
                break

    def _apply_hdr_style(self, has_active: bool = False):
        if not hasattr(self, "icon_w"):
            return
        if has_active:
            self.header.setStyleSheet(f"""
                QWidget {{
                    background: {BG_ACTIVE};
                    border-radius: 8px;
                    border-left: 2px solid {RED_H};
                }}
            """)
            self.icon_w.set_color(TEXT_PRI)
            self.lbl.setStyleSheet(
                f"color: {TEXT_PRI}; font-size: 13px; font-weight: 700; border: none; background: transparent;"
            )
        elif self._hdr_hovered:
            self.header.setStyleSheet(f"QWidget {{ background: {BG_HOVER}; border-radius: 8px; }}")
        else:
            self.header.setStyleSheet("QWidget { background: transparent; border-radius: 8px; }")
            self.icon_w.set_color(TEXT_MUT)
            self.lbl.setStyleSheet(
                f"color: {TEXT_SEC}; font-size: 13px; font-weight: 500; border: none; background: transparent;"
            )

    def _hdr_enter(self):
        self._hdr_hovered = True
        if self._active_sub is None:
            self._apply_hdr_style(has_active=False)

    def _hdr_leave(self):
        self._hdr_hovered = False
        if self._active_sub is None:
            self._apply_hdr_style(has_active=False)


# ═══════════════════════════════════════════════════════════════════════
# SECTION LABEL
# ═══════════════════════════════════════════════════════════════════════
def _section_label(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(
        f"color: {TEXT_DIM}; font-size: 9px; font-weight: 800; "
        f"letter-spacing: 1.5px; padding: 14px 10px 6px 10px; border: none; background: transparent;"
    )
    return lbl


# ═══════════════════════════════════════════════════════════════════════
# COLLAPSE BUTTON — botón con tooltip direccional animado
# ═══════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════
# SIDEBAR ICON PAINTER
# ═══════════════════════════════════════════════════════════════════════
class _SidebarIconWidget(QWidget):
    """
    direction: "none" | "left" | "right"
    color_stroke: color del trazo (TEXT_MUT en fondo claro, "white" en rojo)
    """
    def __init__(self, size=26, direction="none", color_stroke=TEXT_MUT, parent=None):
        super().__init__(parent)
        self._direction   = direction
        self._color       = color_stroke
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def set_direction(self, direction: str, color_stroke: str = None):
        self._direction = direction
        if color_stroke:
            self._color = color_stroke
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h   = self.width(), self.height()
        pad    = 3
        radius = 5.0
        color  = QColor(self._color)

        pen = QPen(color)
        pen.setWidthF(2.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)

        # ── Rectángulo exterior ───────────────────────────────────────
        outer = QRectF(pad, pad, w - pad * 2, h - pad * 2)
        p.drawRoundedRect(outer, radius, radius)

        # ── Franja izquierda (pestaña) — ancho = 22% del total ────────
        tab_w  = (w - pad * 2) * 0.22
        tab_x1 = pad + tab_w
        # Línea vertical divisoria
        p.drawLine(QPointF(tab_x1, pad), QPointF(tab_x1, h - pad))

        # ── Triángulo de dirección (sin relleno, solo contorno) ────────
        if self._direction != "none":
            # Zona del panel derecho
            right_x0 = tab_x1 + 2
            right_x1 = w - pad - 2
            cx        = (right_x0 + right_x1) / 2
            cy        = h / 2

            tri_h = (h - pad * 2) * 0.62   # alto del triángulo
            tri_w = (right_x1 - right_x0) * 0.72  # ancho (profundidad)

            tri = QPainterPath()
            if self._direction == "left":
                # punta a la izquierda
                tri.moveTo(cx - tri_w / 2, cy)            # punta
                tri.lineTo(cx + tri_w / 2, cy - tri_h / 2)  # esquina sup
                tri.lineTo(cx + tri_w / 2, cy + tri_h / 2)  # esquina inf
                tri.closeSubpath()
            else:
                # punta a la derecha
                tri.moveTo(cx + tri_w / 2, cy)
                tri.lineTo(cx - tri_w / 2, cy - tri_h / 2)
                tri.lineTo(cx - tri_w / 2, cy + tri_h / 2)
                tri.closeSubpath()

            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(tri)

        p.end()


# ═══════════════════════════════════════════════════════════════════════
# COLLAPSE BUTTON — botón cerrar sidebar
# ═══════════════════════════════════════════════════════════════════════
class _CollapseButton(QWidget):
    clicked = pyqtSignal()

    def __init__(self, collapsed: bool = False, parent=None):
        super().__init__(parent)
        self._hovered = False
        self.setFixedSize(28, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._icon = _SidebarIconWidget(
            size=28, direction="none", color_stroke=TEXT_MUT, parent=self
        )
        self._icon.move(0, 0)
        self._apply_style()

    def set_collapsed(self, collapsed: bool):
        pass  # se oculta externamente cuando está colapsado

    def _apply_style(self):
        if self._hovered:
            self.setStyleSheet(f"""
                QWidget {{
                    background: {RED};
                    border: 1px solid {RED_H};
                    border-radius: 7px;
                }}
            """)
            self._icon.set_direction("left", color_stroke="white")
        else:
            self.setStyleSheet(f"""
                QWidget {{
                    background: {BG_CARD};
                    border: 1px solid {BORDER};
                    border-radius: 7px;
                }}
            """)
            self._icon.set_direction("none", color_stroke=TEXT_MUT)

    def enterEvent(self, event):
        self._hovered = True
        self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._apply_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


# ═══════════════════════════════════════════════════════════════════════
# DOUBLE CLICK FRAME — QFrame que emite señal al hacer doble click
# ═══════════════════════════════════════════════════════════════════════
class _DoubleClickFrame(QFrame):
    double_clicked = pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)


# ═══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════
class Sidebar(QFrame):
    nav_requested = pyqtSignal(str)   # page_key (incluyendo sub)

    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self._collapsed = False
        self._nav_buttons: list[NavButton] = []
        self._section_labels: list[QLabel] = []
        self._groups: list[ExpandableGroup] = []

        self.setFixedWidth(SIDEBAR_W)
        self.setStyleSheet(f"background-color: {BG_SIDEBAR};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header ──
        header = QFrame()
        header.setFixedHeight(72)
        header.setStyleSheet(f"QFrame {{ background: transparent; border-bottom: 1px solid {BORDER_2}; }}")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 0, 12, 0)
        h_layout.setSpacing(12)

        self.logo_circle = QLabel("D")
        self.logo_circle.setFixedSize(38, 38)
        self.logo_circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_circle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logo_circle.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {RED_H}, stop:1 {RED});
                color: white; border-radius: 10px;
                font-size: 18px; font-weight: 900; border: none;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self.logo_circle)
        shadow.setBlurRadius(10); shadow.setOffset(0, 3)
        shadow.setColor(QColor(200, 16, 46, 80))
        self.logo_circle.setGraphicsEffect(shadow)
        self.logo_circle.mousePressEvent = lambda e: self._on_logo_click()
        self.logo_circle.enterEvent     = lambda e: self._on_logo_hover(True)
        self.logo_circle.leaveEvent     = lambda e: self._on_logo_hover(False)
        h_layout.addWidget(self.logo_circle)

        self.logo_text = QWidget()
        lt = QVBoxLayout(self.logo_text)
        lt.setContentsMargins(0, 0, 0, 0); lt.setSpacing(1)
        lbl_title = QLabel("DOJO")
        lbl_title.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; letter-spacing: 1px; border: none;")
        lbl_sub = QLabel("Admin")
        lbl_sub.setStyleSheet(f"color: {TEXT_MUT}; font-size: 9px; font-weight: 600; letter-spacing: 1.5px; border: none;")
        lt.addWidget(lbl_title); lt.addWidget(lbl_sub)
        h_layout.addWidget(self.logo_text, 1)

        self.btn_collapse = _CollapseButton(collapsed=False)
        self.btn_collapse.clicked.connect(self.toggle_collapse)
        h_layout.addWidget(self.btn_collapse)

        layout.addWidget(header)

        # ── Nav scroll ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical { background: transparent; width: 3px; }
            QScrollBar::handle:vertical { background: #2A2A2A; border-radius: 1px; min-height: 20px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)
        nav_content = QWidget()
        nav_content.setStyleSheet("background: transparent;")
        self.nav_layout = QVBoxLayout(nav_content)
        self.nav_layout.setContentsMargins(10, 8, 10, 8)
        self.nav_layout.setSpacing(1)
        scroll.setWidget(nav_content)
        layout.addWidget(scroll, 1)

        self._build_nav()

        # ── Footer ──
        footer = QFrame()
        footer.setStyleSheet(f"QFrame {{ background: transparent; border-top: 1px solid {BORDER_2}; }}")
        f_layout = QVBoxLayout(footer)
        f_layout.setContentsMargins(10, 10, 10, 10)
        f_layout.setSpacing(6)

        self.user_card = _DoubleClickFrame()
        self.user_card.setStyleSheet(f"""
            QFrame {{ background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 8px; }}
            QFrame:hover {{ border-color: {RED}; }}
        """)
        uc = QHBoxLayout(self.user_card)
        uc.setContentsMargins(10, 8, 10, 8); uc.setSpacing(8)

        initials = "".join(p[0].upper() for p in str(user.get("username", "U")).split()[:2]) or "U"
        avatar = QLabel(initials)
        avatar.setFixedSize(30, 30)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {PURPLE}, stop:1 #581C87);
                color: white; border-radius: 8px; font-size: 11px; font-weight: 900; border: none;
            }}
        """)
        uc.addWidget(avatar)

        self.user_info = QWidget()
        ui = QVBoxLayout(self.user_info)
        ui.setContentsMargins(0, 0, 0, 0); ui.setSpacing(0)
        self.lbl_username = QLabel(str(user.get("username", "Usuario")))
        self.lbl_username.setStyleSheet(f"color: {TEXT_PRI}; font-size: 11px; font-weight: 700; border: none;")
        lbl_role = QLabel("Administrador")
        lbl_role.setStyleSheet(f"color: {TEXT_MUT}; font-size: 9px; font-weight: 500; border: none;")
        ui.addWidget(self.lbl_username); ui.addWidget(lbl_role)
        uc.addWidget(self.user_info, 1)
        self.user_card.double_clicked.connect(
            lambda: self.nav_requested.emit("account")
        )
        self.user_card.setCursor(Qt.CursorShape.PointingHandCursor)
        self.user_card.setToolTip("Doble clic para abrir tu cuenta")
        f_layout.addWidget(self.user_card)

        self.btn_logout = QPushButton("  Cerrar sesión")
        self.btn_logout.setFixedHeight(34)
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUT};
                border: 1px solid {BORDER_2}; border-radius: 7px;
                font-size: 11px; font-weight: 600; text-align: left; padding-left: 12px;
            }}
            QPushButton:hover {{ color: {RED_H}; border-color: {RED}; }}
        """)
        f_layout.addWidget(self.btn_logout)
        layout.addWidget(footer)

    def _build_nav(self):
        # ── MENU section ──
        self._lbl_menu = _section_label("Menú")
        self._section_labels.append(self._lbl_menu)
        self.nav_layout.addWidget(self._lbl_menu)

        for icon, label_key, page_key in [
            ("dashboard", "dashboard", "dashboard"),
            ("students",  "students",  "students"),
        ]:
            btn = NavButton(icon, tr(label_key), page_key, label_key=label_key)
            btn.clicked_nav.connect(self._on_nav_clicked)
            self.nav_layout.addWidget(btn)
            self._nav_buttons.append(btn)

        self.grp_classes_events = ExpandableGroup(
            "classes", tr("classes_events"), [
                ("calendar", tr("classes_events.classes"), "classes_calendar"),
                ("event",    tr("classes_events.events"),  "classes_events"),
            ]
        )
        self.grp_classes_events.sub_clicked.connect(self._on_sub_clicked)
        self._groups.append(self.grp_classes_events)
        self.nav_layout.addWidget(self.grp_classes_events)

        btn_belts = NavButton("belts", tr("martial_arts"), "belts", label_key="martial_arts")
        btn_belts.clicked_nav.connect(self._on_nav_clicked)
        self.nav_layout.addWidget(btn_belts)
        self._nav_buttons.append(btn_belts)

        # ── Finanzas (expandable) ──
        self.grp_finances = ExpandableGroup(
            "finances", tr("finances"), [
                ("income",      tr("finances.income"),              "finances_income"),
                ("expense",     tr("finances.expenses"),            "finances_expenses"),
                ("receivables", tr("finances.receivables"),         "finances_receivables"),
                ("collection",  tr("finances.collection_accounts"), "finances_collection"),
            ]
        )
        self.grp_finances.sub_clicked.connect(self._on_sub_clicked)
        self._groups.append(self.grp_finances)
        self.nav_layout.addWidget(self.grp_finances)

        # ── Administración (expandable) ──
        self.grp_management = ExpandableGroup(
            "inventory", tr("management"), [
                ("inventory",    tr("management.inventory"),    "mgmt_inventory"),
                ("memberships",  tr("management.memberships"),  "mgmt_memberships"),
                ("services",     tr("management.services.nav"), "mgmt_services"),
            ]
        )
        self.grp_management.sub_clicked.connect(self._on_sub_clicked)
        self._groups.append(self.grp_management)
        self.nav_layout.addWidget(self.grp_management)

        self.nav_layout.addSpacing(4)

        # ── OTHER section ──
        self._lbl_other = _section_label("Otro")
        self._section_labels.append(self._lbl_other)
        self.nav_layout.addWidget(self._lbl_other)

        for icon, label_key, page_key in [
            ("reports",  "reports",  "reports"),
            ("settings", "settings", "settings"),
        ]:
            btn = NavButton(icon, tr(label_key), page_key)
            btn.clicked_nav.connect(self._on_nav_clicked)
            self.nav_layout.addWidget(btn)
            self._nav_buttons.append(btn)

        self.nav_layout.addStretch()

    def _on_nav_clicked(self, page_key: str):
        # Deactivate groups when a plain nav button is clicked
        for grp in self._groups:
            grp.clear_active()
        self.nav_requested.emit(page_key)

    def _on_sub_clicked(self, page_key: str):
        # Deactivate plain nav buttons when a sub is clicked
        for btn in self._nav_buttons:
            btn.set_active(False)
        self.nav_requested.emit(page_key)

    def set_active_page(self, page_key: str):
        for btn in self._nav_buttons:
            btn.set_active(btn._page_key == page_key)

        classes_events_keys = {"classes_calendar", "classes_events"}
        finances_keys = {"finances_income", "finances_expenses", "finances_receivables", "finances_collection"}
        mgmt_keys     = {"mgmt_inventory", "mgmt_memberships", "mgmt_services"}

        if page_key in classes_events_keys:
            self.grp_classes_events.set_active_sub(page_key)
            self.grp_finances.clear_active()
            self.grp_management.clear_active()
        elif page_key in finances_keys:
            self.grp_finances.set_active_sub(page_key)
            self.grp_classes_events.clear_active()
            self.grp_management.clear_active()
        elif page_key in mgmt_keys:
            self.grp_management.set_active_sub(page_key)
            self.grp_classes_events.clear_active()
            self.grp_finances.clear_active()
        else:
            self.grp_classes_events.clear_active()
            self.grp_finances.clear_active()
            self.grp_management.clear_active()

    def retranslate(self):
        for btn in self._nav_buttons:
            if btn._label_key:
                btn.set_label(tr(btn._label_key))
        self.grp_classes_events.set_label(tr("classes_events"))
        self.grp_classes_events.set_sub_label("classes_calendar", tr("classes_events.classes"))
        self.grp_classes_events.set_sub_label("classes_events", tr("classes_events.events"))
        self.btn_logout.setText("  " + tr("logout") if not self._collapsed else "")

    def toggle_collapse(self):
        self._collapsed = not self._collapsed
        target_w = SIDEBAR_W_COLLAPSED if self._collapsed else SIDEBAR_W

        for prop in (b"minimumWidth", b"maximumWidth"):
            anim = QPropertyAnimation(self, prop, self)
            anim.setDuration(300)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.setStartValue(self.width())
            anim.setEndValue(target_w)
            anim.start()
            setattr(self, f"_anim_{prop.decode()}", anim)

        QTimer.singleShot(160, self._update_collapsed_visibility)

    def _update_collapsed_visibility(self):
        c = self._collapsed
        for btn in self._nav_buttons:
            btn.set_collapsed(c)
        for grp in self._groups:
            grp.set_collapsed(c)
        for lbl in self._section_labels:
            lbl.setVisible(not c)
        self.logo_text.setVisible(not c)
        self.btn_collapse.setVisible(not c)
        self.user_info.setVisible(not c)
        self.btn_logout.setText("" if c else "  Cerrar sesión")
        self.btn_collapse.set_collapsed(c)

        # Limpiar overlay del botón abrir SIEMPRE al cambiar estado
        if hasattr(self, "_open_icon_overlay") and self._open_icon_overlay:
            self._open_icon_overlay.hide()
            self._open_icon_overlay.setParent(None)
            self._open_icon_overlay = None

        # Restaurar logo a "S" limpio
        self.logo_circle.setText("S")
        self.logo_circle.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {RED_H}, stop:1 {RED});
                color: white; border-radius: 10px;
                font-size: 18px; font-weight: 900; border: none;
            }}
        """)
        self.logo_circle.update()

    def _on_logo_click(self):
        if self._collapsed:
            self.toggle_collapse()

    def _on_logo_hover(self, entering: bool):
        if not self._collapsed:
            return

        if entering:
            self.logo_circle.setText("")
            self.logo_circle.setStyleSheet(f"""
                QLabel {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 {RED_H}, stop:1 {RED});
                    color: white; border-radius: 10px;
                    font-size: 18px; font-weight: 900; border: none;
                }}
            """)
            # Limpiar overlay anterior de forma síncrona
            if hasattr(self, "_open_icon_overlay") and self._open_icon_overlay:
                self._open_icon_overlay.hide()
                self._open_icon_overlay.setParent(None)
                self._open_icon_overlay = None

            self._open_icon_overlay = _SidebarIconWidget(
                size=34, direction="right", color_stroke="white"
            )
            self._open_icon_overlay.setParent(self.logo_circle)
            self._open_icon_overlay.move(2, 2)
            self._open_icon_overlay.show()
            self._open_icon_overlay.raise_()

        else:
            # Destruir síncrono ANTES de restaurar texto
            if hasattr(self, "_open_icon_overlay") and self._open_icon_overlay:
                self._open_icon_overlay.hide()
                self._open_icon_overlay.setParent(None)
                self._open_icon_overlay = None

            self.logo_circle.setText("S")
            self.logo_circle.setStyleSheet(f"""
                QLabel {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                        stop:0 {RED_H}, stop:1 {RED});
                    color: white; border-radius: 10px;
                    font-size: 18px; font-weight: 900; border: none;
                }}
            """)
            self.logo_circle.update()

# ═══════════════════════════════════════════════════════════════════════
# CLASS NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════

class NotificationCard(QFrame):
    def __init__(self, notification, parent=None):
        super().__init__(parent)

        self.notification = notification

        self.setObjectName("NotificationCard")
        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True
        )

        notification_type = notification.get(
            "type",
            "upcoming"
        )
        category = notification.get("category", "class")

        if notification_type == "started":
            if category == "event":
                accent = "#3B82F6"
                status_text = "EVENTO INICIADO"
            else:
                accent = "#22C55E"
                status_text = "CLASE INICIADA"
        else:
            if category == "event":
                accent = "#A855F7"
                status_text = "PROXIMO EVENTO"
            else:
                accent = "#F59E0B"
                status_text = "PROXIMA CLASE"

        self.setStyleSheet(f"""
            QFrame#NotificationCard {{
                background-color: #111111;
                border: 1px solid #252525;
                border-left: 3px solid {accent};
                border-radius: 9px;
            }}

            QFrame#NotificationCard:hover {{
                background-color: #161616;
                border-color: #343434;
                border-left: 3px solid {accent};
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(5)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)

        lbl_status = QLabel(status_text)
        lbl_status.setStyleSheet(f"""
            color: {accent};
            font-size: 8px;
            font-weight: 900;
            letter-spacing: 1px;
        """)

        lbl_time = QLabel(
            notification.get("time", "")
        )
        lbl_time.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 9px;
            font-weight: 800;
        """)

        top_row.addWidget(lbl_status)
        top_row.addStretch()
        top_row.addWidget(lbl_time)

        root.addLayout(top_row)

        lbl_title = QLabel(
            notification.get("title", "Clase")
        )
        lbl_title.setWordWrap(True)
        lbl_title.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 12px;
            font-weight: 900;
        """)

        root.addWidget(lbl_title)

        lbl_message = QLabel(
            notification.get("message", "")
        )
        lbl_message.setWordWrap(True)
        lbl_message.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 10px;
            font-weight: 600;
        """)

        root.addWidget(lbl_message)

        details = notification.get("details", "")

        if details:
            lbl_details = QLabel(details)
            lbl_details.setWordWrap(True)
            lbl_details.setStyleSheet(f"""
                color: {TEXT_MUT};
                font-size: 9px;
                font-weight: 600;
            """)

            root.addWidget(lbl_details)


class NotificationPopup(QFrame):
    cleared = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(
            None,
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
        )

        self.owner_window = parent

        self.setObjectName("NotificationPopup")
        self.setFixedWidth(360)
        self.setMinimumHeight(180)
        self.setMaximumHeight(480)

        # No utilizar WA_TranslucentBackground.
        # En Windows puede provocar UpdateLayeredWindowIndirect failed.
        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True
        )

        self.setStyleSheet("""
            QFrame#NotificationPopup {
                background-color: #0D0D0D;
                border: 1px solid #303030;
                border-radius: 12px;
            }

            QLabel {
                background-color: transparent;
                border: none;
            }

            QScrollArea {
                background-color: transparent;
                border: none;
            }

            QScrollArea > QWidget {
                background-color: transparent;
            }

            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }

            QScrollBar:vertical {
                background-color: #090909;
                width: 7px;
                margin: 0;
                border: none;
            }

            QScrollBar::handle:vertical {
                background-color: #343434;
                border-radius: 3px;
                min-height: 28px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #484848;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
                background: transparent;
            }
        """)

        # No agregar QGraphicsDropShadowEffect a una ventana Popup
        # en Windows. La sombra provocaba el error de LayeredWindow.

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(11)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        title = QLabel("Notificaciones")
        title.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 14px;
            font-weight: 900;
        """)

        self.lbl_count = QLabel("0")
        self.lbl_count.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.lbl_count.setFixedSize(24, 20)
        self.lbl_count.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(200, 16, 46, 45);
                color: {RED_H};
                border: 1px solid {RED};
                border-radius: 10px;
                font-size: 9px;
                font-weight: 900;
            }}
        """)

        self.btn_clear = QPushButton("Limpiar")
        self.btn_clear.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.btn_clear.setFixedHeight(28)
        self.btn_clear.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_MUT};
                border: none;
                border-radius: 6px;
                font-size: 10px;
                font-weight: 800;
                padding: 0 8px;
            }}

            QPushButton:hover {{
                background-color: #191919;
                color: {TEXT_PRI};
            }}

            QPushButton:disabled {{
                color: #383838;
                background-color: transparent;
            }}
        """)

        self.btn_clear.clicked.connect(
            self.cleared.emit
        )

        header.addWidget(title)
        header.addWidget(self.lbl_count)
        header.addStretch()
        header.addWidget(self.btn_clear)

        root.addLayout(header)

        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("""
            QFrame {
                background-color: #242424;
                border: none;
            }
        """)

        root.addWidget(separator)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.content = QWidget()
        self.content.setObjectName(
            "NotificationContent"
        )
        self.content.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True
        )
        self.content.setStyleSheet("""
            QWidget#NotificationContent {
                background-color: #0D0D0D;
                border: none;
            }
        """)

        self.items_layout = QVBoxLayout(
            self.content
        )
        self.items_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )
        self.items_layout.setSpacing(8)
        self.items_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.scroll.setWidget(self.content)
        root.addWidget(self.scroll, 1)

        self.set_notifications([])

    def _clear_items(self):
        while self.items_layout.count():
            item = self.items_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

            child_layout = item.layout()

            if child_layout is not None:
                self._clear_child_layout(
                    child_layout
                )

    def _clear_child_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

            child_layout = item.layout()

            if child_layout is not None:
                self._clear_child_layout(
                    child_layout
                )

    def set_notifications(self, notifications):
        self._clear_items()

        notification_count = len(
            notifications
        )

        self.lbl_count.setText(
            str(notification_count)
        )

        self.btn_clear.setEnabled(
            notification_count > 0
        )

        if notification_count == 0:
            empty_container = QFrame()
            empty_container.setObjectName(
                "EmptyNotifications"
            )
            empty_container.setMinimumHeight(112)
            empty_container.setStyleSheet("""
                QFrame#EmptyNotifications {
                    background-color: #101010;
                    border: 1px dashed #292929;
                    border-radius: 9px;
                }

                QLabel {
                    background: transparent;
                    border: none;
                }
            """)

            empty_layout = QVBoxLayout(
                empty_container
            )
            empty_layout.setContentsMargins(
                16,
                18,
                16,
                18
            )
            empty_layout.setSpacing(7)
            empty_layout.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            empty_icon = IconLabel(
                "bell",
                24,
                TEXT_MUT
            )

            empty_message = QLabel(
                "No hay notificaciones de clases."
            )
            empty_message.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
            empty_message.setWordWrap(True)
            empty_message.setStyleSheet(f"""
                color: {TEXT_MUT};
                font-size: 11px;
                font-weight: 600;
            """)

            empty_layout.addWidget(
                empty_icon,
                0,
                Qt.AlignmentFlag.AlignCenter
            )
            empty_layout.addWidget(
                empty_message
            )

            self.items_layout.addWidget(
                empty_container
            )
            return

        for notification in notifications:
            card = NotificationCard(
                notification,
                self.content
            )

            self.items_layout.addWidget(card)

        self.items_layout.addStretch()

    def show_below(self, anchor):
        # Calcular primero el tamaño final.
        self.adjustSize()

        desired_height = min(
            480,
            max(
                180,
                self.sizeHint().height()
            )
        )

        self.resize(
            360,
            desired_height
        )

        anchor_bottom_right = (
            anchor.mapToGlobal(
                anchor.rect().bottomRight()
            )
        )

        popup_x = (
            anchor_bottom_right.x()
            - self.width()
        )

        popup_y = (
            anchor_bottom_right.y()
            + 8
        )

        screen = anchor.screen()

        if screen is not None:
            available = screen.availableGeometry()

            popup_x = max(
                available.left() + 10,
                min(
                    popup_x,
                    available.right()
                    - self.width()
                    - 10
                )
            )

            popup_y = max(
                available.top() + 10,
                min(
                    popup_y,
                    available.bottom()
                    - self.height()
                    - 10
                )
            )

        self.move(
            popup_x,
            popup_y
        )

        self.show()
        self.raise_()
        self.activateWindow()

# ═══════════════════════════════════════════════════════════════════════
# TOPBAR
# ═══════════════════════════════════════════════════════════════════════
class TopBar(QFrame):
    bell_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(60)
        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_SIDEBAR};
                border-bottom: 1px solid {BORDER_2};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 0, 28, 0)
        layout.setSpacing(16)

        left = QHBoxLayout()
        left.setSpacing(8)

        left.addWidget(
            IconLabel("home", 15, TEXT_MUT)
        )

        inicio = QLabel("Inicio")
        inicio.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 13px;
            font-weight: 500;
            border: none;
        """)

        left.addWidget(inicio)

        left.addWidget(
            IconLabel(
                "chevron-right",
                11,
                TEXT_DIM
            )
        )

        self.current_page_lbl = QLabel(
            "Dashboard"
        )
        self.current_page_lbl.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 13px;
            font-weight: 700;
            border: none;
        """)

        left.addWidget(
            self.current_page_lbl
        )

        layout.addLayout(left)
        layout.addStretch()

        date_str = datetime.now().strftime(
            "%A, %d %b %Y"
        ).capitalize()

        date_pill = QFrame()
        date_pill.setFixedHeight(34)
        date_pill.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)

        date_layout = QHBoxLayout(date_pill)
        date_layout.setContentsMargins(
            12,
            0,
            12,
            0
        )
        date_layout.setSpacing(8)

        date_layout.addWidget(
            IconLabel(
                "calendar",
                13,
                TEXT_MUT
            )
        )

        date_lbl = QLabel(date_str)
        date_lbl.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 11px;
            font-weight: 600;
            border: none;
        """)

        date_layout.addWidget(date_lbl)
        layout.addWidget(date_pill)

        # Botón de notificaciones
        self.btn_bell = QPushButton()
        self.btn_bell.setFixedSize(38, 38)
        self.btn_bell.setToolTip("Notificaciones de clases")
        self.btn_bell.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.btn_bell.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 9px;
            }}

            QPushButton:hover {{
                background-color: {BG_HOVER};
                border-color: #4B5563;
            }}

            QPushButton:pressed {{
                background-color: #101010;
                border-color: {RED};
            }}
        """)

        bell_layout = QHBoxLayout(
            self.btn_bell
        )
        bell_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.bell_icon = IconLabel(
            "bell",
            18,
            TEXT_SEC
        )

        bell_layout.addWidget(
            self.bell_icon,
            0,
            Qt.AlignmentFlag.AlignCenter
        )

        self.btn_bell.clicked.connect(
            self.bell_clicked.emit
        )

        layout.addWidget(self.btn_bell)

        # Contador sobre la campana
        self.bell_badge = QLabel(
            self.btn_bell
        )
        self.bell_badge.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.bell_badge.setFixedSize(18, 18)
        self.bell_badge.move(23, -1)
        self.bell_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {RED};
                color: white;
                border: 2px solid {BG_SIDEBAR};
                border-radius: 9px;
                font-size: 8px;
                font-weight: 900;
            }}
        """)
        self.bell_badge.hide()

        # Botón de búsqueda
        self.btn_search = QPushButton()
        self.btn_search.setFixedSize(34, 34)
        self.btn_search.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.btn_search.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}

            QPushButton:hover {{
                border-color: {TEXT_MUT};
                background: {BG_HOVER};
            }}
        """)

        search_layout = QHBoxLayout(
            self.btn_search
        )
        search_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        search_layout.addWidget(
            IconLabel(
                "search",
                16,
                TEXT_SEC
            )
        )

        layout.addWidget(self.btn_search)

    def set_notification_count(self, count):
        count = max(0, int(count or 0))

        if count <= 0:
            self.bell_badge.hide()
            return

        self.bell_badge.setText(
            "9+" if count > 9 else str(count)
        )
        self.bell_badge.show()
        self.bell_badge.raise_()

    def set_current_page(self, name: str):
        self.current_page_lbl.setText(name)


# ═══════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()

        self.user = user

        self.setWindowTitle("Dojo Admin")
        self.setMinimumSize(1100, 680)
        self.setStyleSheet(
            f"background-color: {BG_MAIN};"
        )
        
        self._logging_out = False
        self._force_exit = False

        self.classes_repo = ClassesRepository()
        self.notifications = []
        self.notification_preferences = {}

        self._build_ui()

        self._setup_desktop_notifications()
        self._setup_class_notification_service()
        self._setup_event_notification_service()
        self._load_notification_preferences()

        i18n.language_changed.connect(
            self._retranslate_ui
        )

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar(self.user)
        self.sidebar.nav_requested.connect(self._on_nav)
        self.sidebar.btn_logout.clicked.connect(self._logout)
        root.addWidget(self.sidebar)

        sep = QFrame()
        sep.setFixedWidth(1)
        sep.setStyleSheet(f"background-color: {BORDER_2};")
        root.addWidget(sep)

        content = QWidget()
        content.setStyleSheet(f"background-color: {BG_MAIN};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.topbar = TopBar()
        self.topbar.bell_clicked.connect(
            self._toggle_notification_popup
        )

        content_layout.addWidget(self.topbar)

        self.content_area = QWidget()
        self.content_area.setStyleSheet(f"background-color: {BG_MAIN};")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.content_area, 1)

        root.addWidget(content, 1)

        self._show_dashboard()
        self.sidebar.set_active_page("dashboard")

        # Conectar el sistema global de avisos emergentes
        from core.toast import toast_manager
        toast_manager.attach(self)

    def _setup_desktop_notifications(self):
        """Inicializa el servicio de notificaciones de escritorio + tray."""
        from services.desktop_notification_service import (
            DesktopNotificationService
        )

        self.desktop_notifications = (
            DesktopNotificationService(
                self,
                "assets/icons/dojo_admin.ico"
            )
        )

        QTimer.singleShot(
            2500,
            lambda: self.desktop_notifications.show_info(
                "DOJO ADMIN",
                "Sistema de notificaciones activado."
            )
        )

    def _setup_class_notification_service(self):
        """Inicializa el servicio de notificación de clases."""
        from services.class_notification_service import (
            ClassNotificationService
        )

        self.class_notification_service = (
            ClassNotificationService(
                self.classes_repo, self
            )
        )

        self.notification_popup = NotificationPopup(self)
        self.notification_popup.cleared.connect(
            self._clear_notifications
        )

        self.class_notification_service.notification_ready.connect(
            self._on_class_notification
        )

        self.class_notification_service.start()

    def _setup_event_notification_service(self):
        from services.event_notification_service import (
            EventNotificationService
        )
        from repositories.events_repository import EventsRepository

        self.events_repo = EventsRepository()
        self.event_notification_service = EventNotificationService(
            self.events_repo, self,
        )
        self.event_notification_service.notification_ready.connect(
            self._on_event_notification
        )
        self.event_notification_service.start()

    def _load_notification_preferences(self):
        from repositories.account_repository import AccountRepository
        from PyQt6.QtCore import QThread

        class _PrefWorker(QThread):
            def __init__(self, repo, user_id):
                super().__init__()
                self._repo = repo
                self._user_id = user_id
                self.result = None

            def run(self):
                self.result = self._repo.get_notification_preferences(
                    self._user_id,
                )

        user_id = self.user.get("id")
        if user_id:
            repo = AccountRepository()
            worker = _PrefWorker(repo, user_id)
            worker.finished.connect(
                lambda: self._apply_notification_preferences(worker.result)
            )
            worker.start()

    def _apply_notification_preferences(self, preferences):
        if preferences is None:
            return
        self.notification_preferences = dict(preferences)

        if hasattr(self, "class_notification_service"):
            self.class_notification_service.set_preferences(preferences)

        if hasattr(self, "event_notification_service"):
            self.event_notification_service.set_preferences(preferences)

        if hasattr(self, "desktop_notifications"):
            should_enable = bool(
                preferences.get("classes_windows", True)
                or preferences.get("events_windows", True)
            )
            if should_enable:
                self.desktop_notifications.enable_notifications()
            else:
                self.desktop_notifications.disable_notifications()

    def _toggle_notification_popup(self):
        if self.notification_popup.isVisible():
            self.notification_popup.hide()
            return

        combined = list(self.notifications)
        if hasattr(self, "event_notification_service"):
            combined.extend(
                self.event_notification_service.get_notifications()
            )
        self.notification_popup.set_notifications(combined[:30])

        self.notification_popup.show_below(
            self.topbar.btn_bell
        )

    def _clear_notifications(self):
        if hasattr(self, "class_notification_service"):
            self.class_notification_service.clear_notifications()
        if hasattr(self, "event_notification_service"):
            self.event_notification_service.clear_notifications()

        self.notifications.clear()
        self.topbar.set_notification_count(0)

        if hasattr(self, "notification_popup"):
            self.notification_popup.set_notifications([])

    def _on_class_notification(self, notification):
        show_in_app = bool(notification.get("show_in_app", True))
        show_windows = bool(notification.get("show_windows", True))

        if show_in_app:
            self.notifications.insert(0, notification)
            self.notifications = self.notifications[:30]

            self.topbar.set_notification_count(len(self.notifications))

            if hasattr(self, "notification_popup") and self.notification_popup.isVisible():
                combined = list(self.notifications)
                if hasattr(self, "event_notification_service"):
                    combined.extend(
                        self.event_notification_service.get_notifications()
                    )
                self.notification_popup.set_notifications(combined[:30])

            try:
                from core.toast import toast_manager
                toast_message = (
                    f"{notification['title']}: {notification['message']}"
                )
                toast_manager.show(toast_message, "info")
            except Exception as e:
                debug_log(
                    "[MainWindow] No se pudo mostrar el toast: " + str(e)
                )

        if show_windows and hasattr(self, "desktop_notifications"):
            notif_type = notification.get("type")
            class_name = notification.get("title", "Clase")
            time_text = notification.get("time", "")

            if notif_type == "started":
                self.desktop_notifications.show_class_started(
                    class_name, time_text
                )
            else:
                minutes = notification.get("minutes_until", 0)
                self.desktop_notifications.show_class_upcoming(
                    class_name, time_text, max(1, minutes)
                )

    def _on_event_notification(self, notification):
        show_in_app = bool(notification.get("show_in_app", True))
        show_windows = bool(notification.get("show_windows", True))

        if show_in_app:
            self.notifications.insert(0, notification)
            self.notifications = self.notifications[:30]

            self.topbar.set_notification_count(len(self.notifications))

            if hasattr(self, "notification_popup") and self.notification_popup.isVisible():
                combined = list(self.notifications)
                if hasattr(self, "class_notification_service"):
                    combined.extend(
                        self.class_notification_service.get_notifications()
                    )
                self.notification_popup.set_notifications(combined[:30])

            try:
                from core.toast import toast_manager
                toast_message = (
                    f"{notification['title']}: {notification['message']}"
                )
                toast_manager.show(toast_message, "info")
            except Exception as e:
                debug_log(
                    "[MainWindow] No se pudo mostrar el toast evento: " + str(e)
                )

        if show_windows and hasattr(self, "desktop_notifications"):
            notif_type = notification.get("type")
            event_name = notification.get("title", "Evento")
            time_text = notification.get("time", "")
            date_text = notification.get("date", "")

            if notif_type == "started":
                self.desktop_notifications.show_event_started(
                    event_name, time_text
                )
            else:
                minutes = notification.get("minutes_until", 0)
                self.desktop_notifications.show_event_upcoming(
                    event_name, date_text, time_text, max(1, minutes)
                )

    def open_classes_module(self):
        """Navega a la vista de Clases."""
        if hasattr(self, "desktop_notifications"):
            self.desktop_notifications.restore_window()
        self._on_nav("classes_calendar")

    def _toggle_sidebar(self):
        self.sidebar.toggle_collapse()

    def _retranslate_ui(self, _lang: str = ""):
        self.sidebar.retranslate()

    def _on_nav(self, page_key: str):
        # Alias temporal para compatibilidad con notificaciones y código existente.
        if page_key == "classes":
            page_key = "classes_calendar"

        self.sidebar.set_active_page(page_key)

        routes = {
            "dashboard":            (tr("dashboard"),    self._show_dashboard),
            "students":             (tr("students"),     self._show_students),
            "classes_calendar":     (tr("classes_events.classes"), self._show_classes),
            "classes_events":       (tr("classes_events.events"),  self._show_events),
            "belts":                (tr("martial_arts"), self._show_belts),
            "finances_income":      (tr("finances.income"),              lambda: self._show_finances("income")),
            "finances_expenses":    (tr("finances.expenses"),            lambda: self._show_finances("expenses")),
            "finances_receivables": (tr("finances.receivables"),         lambda: self._show_finances("receivables")),
            "finances_collection":  (tr("finances.collection_accounts"), lambda: self._show_finances("collection_accounts")),
            "mgmt_inventory":       (tr("management.inventory"),    lambda: self._show_management("inventory")),
            "mgmt_memberships":     (tr("management.memberships"),  lambda: self._show_management("memberships")),
            "mgmt_services":        (tr("management.services.nav"), lambda: self._show_management("services")),
            "reports":              (tr("reports"),  lambda: self._show_placeholder(tr("reports"))),
            "settings":             (tr("settings"), self._show_settings),
            "account":              ("Mi cuenta",    self._show_account),
        }
        if page_key in routes:
            label, fn = routes[page_key]
            self.topbar.set_current_page(label)
            fn()

    def _clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_dashboard(self):
        self._clear_content()
        self.content_layout.addWidget(DashboardView(db, self.user))

    def _show_students(self):
        self._clear_content()
        self.content_layout.addWidget(StudentsView())

    def _show_classes(self):
        self._clear_content()

        from views.classes_view import ClassesView

        current_user_id = self.user.get("id")

        self.content_layout.addWidget(
            ClassesView(
                current_user_id=current_user_id
            )
        )

    def _show_events(self):
        self._clear_content()
        from views.events.events_view import EventsView
        self.content_layout.addWidget(
            EventsView(
                current_user=self.user,
                parent_window=self,
            )
        )

    def open_events_module(self):
        self._show_events()
        self.sidebar.set_active_page("classes_events")

    def _show_belts(self):
        self._clear_content()
        from views.belts_view import BeltsView
        self.content_layout.addWidget(BeltsView())

    def _show_finances(self, section: str = "income"):
        self._clear_content()
        from views.finances.finances_view import FinancesView
        view = FinancesView()
        self.content_layout.addWidget(view)
        view._switch_view(section)

    def _show_management(self, section: str = "inventory"):
        self._clear_content()
        from views.management.management_view import ManagementView
        view = ManagementView()
        self.content_layout.addWidget(view)
        view._switch_view(section)

    def _show_account(self):
        self._clear_content()
        from views.account_view import AccountView
        from repositories.account_repository import AccountRepository
        repo = AccountRepository()
        full_data = repo.get_account(self.user.get("id"))
        merged_user = {**self.user, **full_data}

        self.account_view = AccountView(user=merged_user)
        self.account_view.notification_preferences_changed.connect(
            self._apply_notification_preferences
        )
        self.content_layout.addWidget(self.account_view)

    def _show_settings(self):
        self._clear_content()
        from views.settings_view import SettingsView
        self.content_layout.addWidget(SettingsView())

    def _show_placeholder(self, name):
        self._clear_content()
        lbl = QLabel(f"{name}\n\nMódulo en desarrollo 🚧")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 18px;")
        self.content_layout.addWidget(lbl)

    def _logout(self):
        self._logging_out = True

        if hasattr(self, "class_notification_service"):
            self.class_notification_service.stop()

        if hasattr(self, "event_notification_service"):
            self.event_notification_service.stop()

        if hasattr(self, "notification_popup"):
            self.notification_popup.hide()

        if hasattr(self, "desktop_notifications"):
            self.desktop_notifications.tray.hide()

        try:
            i18n.language_changed.disconnect(
                self._retranslate_ui
            )
        except Exception:
            pass

        try:
            from views.finances.income.income_view import IncomeView

            for widget in self.findChildren(QWidget):
                if isinstance(widget, IncomeView):
                    widget.prepare_for_app_shutdown()
                    break

        except Exception:
            pass

        self.login = LoginView(
            AuthService()
        )

        self.login.show()
        self.login.raise_()
        self.login.activateWindow()

        self.close()

    def closeEvent(self, event):
        if not self._force_exit:
            self.hide()

            if hasattr(self, "desktop_notifications"):
                self.desktop_notifications.tray.showMessage(
                    "DOJO ADMIN",
                    "La aplicacion sigue ejecutandose en segundo plano.",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000,
                )

            event.ignore()
            return

        if hasattr(self, "class_notification_service"):
            self.class_notification_service.stop()

        if hasattr(self, "event_notification_service"):
            self.event_notification_service.stop()

        if hasattr(self, "notification_popup"):
            self.notification_popup.hide()

        if self._logging_out:
            event.accept()
            return

        self._logging_out = True

        try:
            i18n.language_changed.disconnect(
                self._retranslate_ui
            )
        except Exception:
            pass

        try:
            from views.finances.income.income_view import IncomeView

            for widget in self.findChildren(QWidget):
                if isinstance(widget, IncomeView):
                    widget.prepare_for_app_shutdown()
                    break

        except Exception:
            pass

        event.accept()



# ─── ENTRY POINT ──────────────────────────────────────────────────────
_main_window = None


def _set_windows_app_id():
    if os.name != "nt":
        return
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "SenshiFightAcademy.DojoAdmin"
        )
    except Exception:
        logger.exception("No se pudo establecer AppUserModelID")


def main():
    os.environ["PYTHONIOENCODING"] = "utf-8"

    _set_windows_app_id()

    if sys.stdout is not None:
        print("PYTHON EJECUTANDO DOJO_ADMIN:", sys.executable)
        print("VERSION PYTHON:", sys.version)

    logger.info("PYTHON EJECUTANDO DOJO_ADMIN: %s", sys.executable)
    logger.info("VERSION PYTHON: %s", sys.version)

    # ── Run social events migration (idempotent) ──────────────────
    try:
        from database.connection import db
        import os as _os
        _migration_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "database", "migration_social_events.sql"
        )
        if os.path.exists(_migration_path):
            db.run_sql_file(_migration_path)
            logger.info("Migración social events ejecutada: %s", _migration_path)
            if sys.stdout is not None:
                print(f"MIGRACIÓN SOCIAL EVENTS OK: {_migration_path}")
    except Exception as mig_err:
        logger.warning("Migración social events falló: %s", mig_err)
        if sys.stdout is not None:
            print(f"MIGRACIÓN SOCIAL EVENTS WARN: {mig_err}")

    try:
        _age_migration = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "database", "migration_martial_art_age_rules.sql"
        )
        if os.path.exists(_age_migration):
            db.run_sql_file(_age_migration)
            logger.info("Migración age rules ejecutada: %s", _age_migration)
    except Exception as age_err:
        logger.warning("Migración age rules falló: %s", age_err)

    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        if sys.stdout is not None:
            print("WEBENGINE STATUS: OK")
        logger.info("WEBENGINE STATUS: OK")
    except Exception as e:
        if sys.stdout is not None:
            print(f"WEBENGINE STATUS: FAILED — {e}")
        logger.warning("WEBENGINE STATUS: FAILED — %s", e)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("Fusion")

    app_icon_path = resource_path(
        os.path.join("assets", "Icons", "dojo_admin.ico")
    )
    app_icon = QIcon(app_icon_path)
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)
        logger.info("Icono global establecido: %s", app_icon_path)
    else:
        logger.error(
            "No se pudo establecer icono global: %s", app_icon_path
        )

    auth_service = AuthService()

    def on_login_success(user, login_win):
        global _main_window
        _main_window = MainWindow(user)
        _main_window.setWindowIcon(app_icon)
        _main_window.show()
        _main_window.raise_()
        _main_window.activateWindow()
        QTimer.singleShot(50, login_win.close)

    login = LoginView(auth_service)
    login._on_login_success = lambda user: on_login_success(user, login)
    login.show()
    login.raise_()
    login.activateWindow()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()