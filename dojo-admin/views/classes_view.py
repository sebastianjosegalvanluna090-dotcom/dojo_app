# ─── CLASSES_VIEW PREMIUM CALENDAR ────────────────────────────────────

import re as _re

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QComboBox, QStackedWidget,
    QGridLayout, QMessageBox, QScrollArea,
    QGraphicsOpacityEffect, QGraphicsBlurEffect,
    QGraphicsDropShadowEffect, QDialog, QSizePolicy,
    QCheckBox, QSpinBox, QTextEdit, QInputDialog
)

from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    QPoint, QMimeData, pyqtSignal, QRectF, QPointF
)
from PyQt6.QtGui import QDrag, QColor, QPainter, QPen, QPainterPath
from datetime import date, time, timedelta, datetime


from repositories.classes_repository import ClassesRepository
from repositories.events_repository import EventsRepository
from core.debug import debug_log


# ─── PALETA BASE ──────────────────────────────────────────────────────
BG_MAIN      = "#050505"
BG_SHELL     = "#090909"
BG_HEADER    = "#0C0C0C"
BG_PANEL     = "#0E0E0E"
BG_CELL      = "#0C0C0C"
BG_CELL_H    = "#161616"
BORDER       = "#1F1F1F"
BORDER_2     = "#222222"
TEXT_PRI     = "#FAFAFA"
TEXT_SEC     = "#A3A3A3"
TEXT_MUT     = "#525252"
CURRENT_BG = "#111317"
CURRENT_BG_HOVER = "#171A20"
CURRENT_BORDER = "#475569"
CURRENT_TEXT = "#CBD5E1"
CURRENT_LINE = "#94A3B8"
CURRENT_COLUMN_BG = "#0F1115"
LIVE_CLASS_BG = "#171A20"
LIVE_CLASS_BORDER = "#64748B"

ACCENTS = {
    "rose": {
        "name": "Rose",
        "color": "#E11D48",
        "hover": "#F43F5E",
        "active": "#BE123C",
        "glow": "rgba(225, 29, 72, 0.15)",
    },
    "blue": {
        "name": "Azul Cobalto",
        "color": "#3B82F6",
        "hover": "#60A5FA",
        "active": "#2563EB",
        "glow": "rgba(59, 130, 246, 0.15)",
    },
    "emerald": {
        "name": "Esmeralda",
        "color": "#10B981",
        "hover": "#34D399",
        "active": "#059669",
        "glow": "rgba(16, 185, 129, 0.15)",
    },
    "violet": {
        "name": "Violeta Cyber",
        "color": "#A855F7",
        "hover": "#C084FC",
        "active": "#7E22CE",
        "glow": "rgba(168, 85, 247, 0.15)",
    },
}


class IconLabel(QWidget):
    ICONS = {
        "pin":      '<line x1="12" y1="22" x2="12" y2="12"/><circle cx="12" cy="8" r="4"/><ellipse cx="12" cy="22" rx="3" ry="1"/>',
        "info":     '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="8"/><line x1="12" y1="12" x2="12" y2="16"/>',
        "edit":     '<line x1="18" y1="2" x2="22" y2="6"/><polyline points="14 6 18 2 22 6 8 20 2 22 4 16 14 6"/>',
        "plus":     '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
        "close":    '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
        "martial-art": (
            '<rect x="2" y="8" width="20" height="8" rx="2"/>'
            '<rect x="9" y="8" width="6" height="8" rx="1"/>'
            '<line x1="2" y1="12" x2="9" y2="12"/>'
            '<line x1="15" y1="12" x2="22" y2="12"/>'
            '<line x1="11" y1="10" x2="13" y2="14"/>'
        ),
        "user":     '<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>',
        "instructor": (
            '<circle cx="12" cy="7" r="4"/>'
            '<path d="M4 21 L4 19 C4 15 7 13 12 13 C17 13 20 15 20 19 L20 21"/>'
            '<line x1="17" y1="9" x2="21" y2="5"/>'
            '<line x1="18" y1="5" x2="21" y2="5"/>'
            '<line x1="21" y1="5" x2="21" y2="8"/>'
        ),
        "upload":   '<polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><rect x="3" y="3" width="18" height="5" rx="2"/><line x1="3" y1="15" x2="5" y2="15"/><line x1="19" y1="15" x2="21" y2="15"/>',
        "trash":    '<polyline points="3 6 21 6"/><polyline points="8 6 8 3 16 3 16 6"/><rect x="5" y="6" width="14" height="15" rx="1"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>',
        "check":    '<polyline points="20 6 9 17 4 12"/>',
        "key":      '<circle cx="7" cy="17" r="4"/><line x1="10.5" y1="13.5" x2="20" y2="4"/><line x1="18" y1="6" x2="20" y2="8"/>',
        "lock":     '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
        "arrow-r":  '<polyline points="9 18 15 12 9 6"/>',
        "doc":      '<polyline points="14 2 14 8 20 8"/><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="13" y2="17"/>',
        "health":   '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
        "school":   '<polyline points="2 7 12 2 22 7"/><polyline points="2 17 12 22 22 17"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="12" y1="2" x2="12" y2="22"/>',
        "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
        "event": (
            '<rect x="3" y="4" width="18" height="18" rx="2"/>'
            '<line x1="8" y1="2" x2="8" y2="6"/>'
            '<line x1="16" y1="2" x2="16" y2="6"/>'
            '<line x1="3" y1="10" x2="21" y2="10"/>'
            '<polyline points="12 13 13 15 16 15 14 17 15 20 12 18 9 20 10 17 8 15 11 15 12 13"/>'
        ),
        "clock": (
            '<circle cx="12" cy="12" r="9"/>'
            '<line x1="12" y1="7" x2="12" y2="12"/>'
            '<line x1="12" y1="12" x2="16" y2="14"/>'
        ),
        "location": (
            '<path d="M12 22 C12 22 5 15 5 9 C5 5 8 2 12 2 C16 2 19 5 19 9 C19 15 12 22 12 22 Z"/>'
            '<circle cx="12" cy="9" r="3"/>'
        ),
        "more": (
            '<circle cx="5" cy="12" r="1"/>'
            '<circle cx="12" cy="12" r="1"/>'
            '<circle cx="19" cy="12" r="1"/>'
        ),
        "phone":    '<rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/>',
        "flame": (
            '<path d="M12 2 C12 2 8 8 8 13 C8 16 10 18 12 18 C14 18 16 16 16 13 C16 8 12 2 12 2 Z"/>'
            '<path d="M12 10 C12 10 10 13 10 15 C10 16.5 11 17 12 17 C13 17 14 16.5 14 15 C14 13 12 10 12 10 Z"/>'
        ),
        "x-circle": '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
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
                            current = QPointF(x, y); path.cubicTo(QPointF(x1,y1), QPointF(x2,y2), current)
                        elif cmd in ("Z", "z"):
                            path.closeSubpath()
                    p.drawPath(path)
            p.end()
        except Exception as e:
            try:
                debug_log(
                    f"[ClassesView.IconLabel] Error dibujando "
                    f"{self._icon_name}: {e}"
                )
            except Exception:
                pass


DAYS_FULL = [
    "Lunes", "Martes", "Miércoles",
    "Jueves", "Viernes", "Sábado", "Domingo"
]

DAYS_SHORT = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


# ─────────────────────────────────────────────────────────────
# Toast Notification
# ─────────────────────────────────────────────────────────────
class Toast(QFrame):
    def __init__(self, message, accent="#E11D48", kind="success", parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self.setFixedHeight(62)
        self.setMinimumWidth(290)
        self.setMaximumWidth(360)

        icon = {
            "success": "✓",
            "info": "i",
            "warning": "!",
            "error": "×",
        }.get(kind, "✓")

        color = {
            "success": "#10B981",
            "info": "#3B82F6",
            "warning": "#F59E0B",
            "error": "#E11D48",
        }.get(kind, accent)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(14, 14, 14, 235);
                border: 1px solid #222222;
                border-radius: 12px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(14, 10, 14, 10)
        root.setSpacing(10)

        lbl_icon = QLabel(icon)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setFixedSize(28, 28)
        lbl_icon.setStyleSheet(f"""
            QLabel {{
                color: {color};
                border: 1px solid {color};
                border-radius: 14px;
                font-weight: 900;
                font-size: 13px;
            }}
        """)

        lbl_msg = QLabel(message)
        lbl_msg.setWordWrap(True)
        lbl_msg.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 12px;
            font-weight: 600;
        """)

        root.addWidget(lbl_icon)
        root.addWidget(lbl_msg, 1)

        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)

        self.anim_in = QPropertyAnimation(self.effect, b"opacity", self)
        self.anim_in.setDuration(240)
        self.anim_in.setStartValue(0.0)
        self.anim_in.setEndValue(1.0)
        self.anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_out = QPropertyAnimation(self.effect, b"opacity", self)
        self.anim_out.setDuration(260)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self.anim_out.finished.connect(self._finish)

        self.anim_in.start()
        QTimer.singleShot(3000, self.anim_out.start)

    def _finish(self):
        parent = self.parentWidget()

        if parent and parent.layout():
            parent.layout().removeWidget(self)

        self.deleteLater()


# ─────────────────────────────────────────────────────────────
# Glass Overlay + blur controller
# ─────────────────────────────────────────────────────────────
class GlassOverlay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.hide()

        self.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 110);
                border: none;
            }
        """)

        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)

        self.anim = QPropertyAnimation(self.effect, b"opacity", self)
        self.anim.setDuration(260)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def fade_in(self):
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.show()
        self.raise_()
        self.anim.stop()
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

    def fade_out(self):
        self.anim.stop()
        try:
            self.anim.finished.disconnect(self._on_fade_out_finished)
        except (TypeError, RuntimeError):
            pass
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.finished.connect(self._on_fade_out_finished)
        self.anim.start()

    def _on_fade_out_finished(self):
        try:
            self.anim.finished.disconnect(self._on_fade_out_finished)
        except (TypeError, RuntimeError):
            pass
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.hide()


# ─────────────────────────────────────────────────────────────
# Day Header
# ─────────────────────────────────────────────────────────────
class DayHeader(QFrame):
    def __init__(self, day_name, day_num="", parent=None):
        super().__init__(parent)

        self.day_name = day_name
        self.day_num = day_num
        self.accent = "#E11D48"

        # Estados separados para evitar que el hover borre "hoy"
        self.is_today = False
        self.is_hover = False

        self.setFixedHeight(56)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 6, 4, 6)
        layout.setSpacing(2)

        self.lbl_name = QLabel(day_name)
        self.lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_date = QLabel(str(day_num))
        self.lbl_date.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.lbl_name)
        layout.addWidget(self.lbl_date)

        self.refresh()

    def set_today(self, active):
        self.is_today = bool(active)
        self.refresh()

    def set_hover(self, active):
        self.is_hover = bool(active)
        self.refresh()

    def set_highlight(self, active):
        # Compatibilidad con el código existente
        self.set_hover(active)

    def set_accent(self, color):
        self.accent = color
        self.refresh()

    def set_day_num(self, day_num):
        self.day_num = day_num
        self.lbl_date.setText(str(day_num))
        self.refresh()

    def refresh(self):
        if self.is_today and self.is_hover:
            # El cursor intensifica el resaltado, pero no elimina "hoy"
            bg = CURRENT_BG_HOVER
            border_top = CURRENT_LINE
            name_color = "#E2E8F0"
            date_color = "#FFFFFF"

        elif self.is_today:
            bg = CURRENT_BG
            border_top = CURRENT_BORDER
            name_color = CURRENT_TEXT
            date_color = "#E2E8F0"

        elif self.is_hover:
            bg = "#141414"
            border_top = self.accent
            name_color = self.accent
            date_color = self.accent

        else:
            bg = "#0E0E0E"
            border_top = "#0E0E0E"
            name_color = TEXT_SEC
            date_color = TEXT_MUT

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-right: 1px solid #1C1C1C;
                border-bottom: 1px solid #1A1A1A;
                border-top: 2px solid {border_top};
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        self.lbl_name.setStyleSheet(f"""
            color: {name_color};
            font-size: 12px;
            font-weight: 800;
        """)

        self.lbl_date.setStyleSheet(f"""
            color: {date_color};
            font-size: 11px;
            font-weight: 900;
        """)


# ─────────────────────────────────────────────────────────────
# Calendar Time Cell
# ─────────────────────────────────────────────────────────────
class TimeCell(QFrame):
    clicked = pyqtSignal(int, int)
    dropped = pyqtSignal(int, int, int)
    hover_day = pyqtSignal(int, bool)

    def __init__(self, day_index, hour, accent="#E11D48", parent=None):
        super().__init__(parent)

        self.day_index = day_index
        self.hour = hour
        self.accent = accent

        self.is_today_column = False
        self.is_hover = False

        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.refresh()

    def set_accent(self, color):
        self.accent = color
        self.refresh()

    def set_today_column(self, active):
        self.is_today_column = bool(active)
        self.refresh()

    def refresh(self, hover=None):
        if hover is not None:
            self.is_hover = bool(hover)

        if self.is_today_column and self.is_hover:
            bg = CURRENT_BG_HOVER
            border = CURRENT_BORDER

        elif self.is_today_column:
            bg = CURRENT_COLUMN_BG
            border = "#1E232B"

        elif self.is_hover:
            bg = BG_CELL_H
            border = self.accent

        else:
            bg = "rgba(12, 12, 12, 100)"
            border = "#141414"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-right: 1px solid #141414;
                border-bottom: 1px solid {border};
            }}
        """)

    def enterEvent(self, event):
        self.refresh(True)
        self.hover_day.emit(self.day_index, True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.refresh(False)
        self.hover_day.emit(self.day_index, False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.day_index, self.hour)

        super().mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            self.refresh(True)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.refresh(False)
        super().dragLeaveEvent(event)

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        self.refresh(False)

        try:
            schedule_id = int(event.mimeData().text())
            self.dropped.emit(
                schedule_id,
                self.day_index,
                self.hour
            )
            event.acceptProposedAction()

        except Exception:
            event.ignore()


# ─────────────────────────────────────────────────────────────
# Class Block Draggable
# ─────────────────────────────────────────────────────────────
class ClassBlock(QFrame):
    def __init__(
        self,
        data,
        parent_view,
        accent="#E11D48",
        parent=None
    ):
        super().__init__(parent)

        self.data = data
        self.parent_view = parent_view
        self.accent = accent

        self.drag_start_pos = None
        self.was_dragging = False
        self.is_live = False

        self.setCursor(Qt.CursorShape.OpenHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)

        # Indicador de clase activa
        self.lbl_live = QLabel("EN CURSO")
        self.lbl_live.setFixedHeight(16)
        self.lbl_live.setVisible(False)
        self.lbl_live.setStyleSheet(f"""
            color: {CURRENT_TEXT};
            background: transparent;
            border: none;
            font-size: 8px;
            font-weight: 900;
            letter-spacing: 1px;
        """)

        self.lbl_name = QLabel(
            data.get("name", "Clase")
        )
        self.lbl_name.setWordWrap(True)

        self.lbl_time = QLabel(
            f"{data.get('start_time', '—')} - "
            f"{data.get('end_time', '—')}"
        )

        self.lbl_inst = QLabel(
            data.get("instructor", "Sin instructor")
        )
        self.lbl_inst.setWordWrap(True)

        layout.addWidget(self.lbl_live)
        layout.addWidget(self.lbl_name)
        layout.addWidget(self.lbl_time)

        inst_row = QHBoxLayout()
        inst_row.setContentsMargins(0, 0, 0, 0)
        inst_row.setSpacing(3)

        inst_row.addWidget(
            IconLabel("instructor", 9, TEXT_SEC)
        )
        inst_row.addWidget(self.lbl_inst)

        layout.addLayout(inst_row)
        layout.addStretch()

        self.setToolTip(
            f"{data.get('name', '')}\n"
            f"Arte: {data.get('martial_art', '—')}\n"
            f"Instructor: {data.get('instructor', '—')}\n"
            f"Horario: {data.get('start_time', '—')} - "
            f"{data.get('end_time', '—')}\n"
            f"Ubicación: {data.get('location', '—')}"
        )

        self.refresh_style()

    def set_live(self, active):
        active = bool(active)

        if self.is_live == active:
            return

        self.is_live = active
        self.lbl_live.setVisible(active)
        self.refresh_style()

    def refresh_style(self):
        class_color = (
            self.data.get("color")
            or self.accent
        )

        if self.is_live:
            background = LIVE_CLASS_BG
            border = LIVE_CLASS_BORDER
            left_border = CURRENT_LINE
            name_color = "#F8FAFC"
            time_color = CURRENT_TEXT

        else:
            background = "rgba(18, 18, 18, 245)"
            border = "#1C1C1C"
            left_border = class_color
            name_color = TEXT_PRI
            time_color = class_color

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {background};
                border: 1px solid {border};
                border-left: 4px solid {left_border};
                border-radius: 9px;
            }}

            QFrame:hover {{
                background-color: #17191D;
                border-color: {
                    CURRENT_LINE
                    if self.is_live
                    else "#333333"
                };
                border-left: 4px solid {left_border};
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        self.lbl_name.setStyleSheet(f"""
            color: {name_color};
            font-size: 11px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)

        self.lbl_time.setStyleSheet(f"""
            color: {time_color};
            font-size: 9px;
            font-weight: 900;
            background: transparent;
            border: none;
        """)

        self.lbl_inst.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 9px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = (
                event.position().toPoint()
            )
            self.was_dragging = False
            self.setCursor(
                Qt.CursorShape.ClosedHandCursor
            )

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.drag_start_pos:
            return

        distance = (
            event.position().toPoint()
            - self.drag_start_pos
        ).manhattanLength()

        if distance < 8:
            return

        self.was_dragging = True

        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(
            str(self.data.get("id"))
        )
        drag.setMimeData(mime)

        self.setWindowOpacity(0.45)

        drag.exec(
            Qt.DropAction.MoveAction
        )

        self.setWindowOpacity(1.0)
        self.setCursor(
            Qt.CursorShape.OpenHandCursor
        )

    def mouseReleaseEvent(self, event):
        self.setCursor(
            Qt.CursorShape.OpenHandCursor
        )

        if (
            not self.was_dragging
            and event.button()
            == Qt.MouseButton.LeftButton
        ):
            self.parent_view.open_class_detail(
                self.data
            )

        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.parent_view.open_class_form(
            schedule_id=self.data.get("id")
        )

        super().mouseDoubleClickEvent(event)


# ─────────────────────────────────────────────────────────────
# Weekly Calendar Canvas
# ─────────────────────────────────────────────────────────────
class WeeklyCalendarWidget(QWidget):
    def __init__(self, repo, parent_view):
        super().__init__()

        self.repo = repo
        self.parent_view = parent_view

        self.start_hour = 6
        self.end_hour = 22

        self.hour_col_w = 75
        self.header_h = 56
        self.cell_h = 82

        self.accent = parent_view.accent_color

        self.day_headers = []
        self.cells = []
        self.blocks = []

        today = date.today()

        self.week_start = (
            today
            - timedelta(days=today.weekday())
        )

        self.setMinimumWidth(920)

        self.setMinimumHeight(
            self.header_h
            + (
                self.end_hour
                - self.start_hour
                + 1
            )
            * self.cell_h
        )

        self.setStyleSheet(
            f"background-color: {BG_MAIN};"
        )

        self._build_base()

        # Línea horizontal de hora actual
        self.current_time_indicator = QFrame(self)
        self.current_time_indicator.setFixedHeight(2)
        self.current_time_indicator.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True
        )
        self.current_time_indicator.setStyleSheet(f"""
            QFrame {{
                background-color: {CURRENT_LINE};
                border: none;
            }}
        """)
        self.current_time_indicator.hide()

        # Punto al inicio de la línea
        self.current_time_dot = QFrame(self)
        self.current_time_dot.setFixedSize(8, 8)
        self.current_time_dot.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True
        )
        self.current_time_dot.setStyleSheet(f"""
            QFrame {{
                background-color: {CURRENT_LINE};
                border: none;
                border-radius: 4px;
            }}
        """)
        self.current_time_dot.hide()

        # Etiqueta con hora exacta
        self.current_time_label = QLabel(self)
        self.current_time_label.setFixedSize(46, 18)
        self.current_time_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.current_time_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True
        )
        self.current_time_label.setStyleSheet(f"""
            QLabel {{
                background-color: #171A20;
                color: {CURRENT_TEXT};
                border: 1px solid {CURRENT_BORDER};
                border-radius: 5px;
                font-size: 8px;
                font-weight: 900;
            }}
        """)
        self.current_time_label.hide()

        self.clock_timer = QTimer(self)
        self.clock_timer.setInterval(30000)
        self.clock_timer.timeout.connect(
            self._update_realtime_state
        )
        self.clock_timer.start()

        QTimer.singleShot(
            0,
            self._update_realtime_state
        )

    def _build_base(self):
        self.corner = QLabel("HORARIO", self)
        self.corner.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.corner.setStyleSheet(f"""
            QLabel {{
                background-color: #0E0E0E;
                color: {TEXT_MUT};
                border-right: 1px solid #1C1C1C;
                border-bottom: 1px solid #1A1A1A;
                font-size: 9px;
                font-weight: 900;
                letter-spacing: 1px;
            }}
        """)

        for name in DAYS_SHORT:
            header = DayHeader(
                name,
                "",
                self
            )
            header.set_accent(self.accent)
            self.day_headers.append(header)

        for hour in range(
            self.start_hour,
            self.end_hour + 1
        ):
            lbl = QLabel(
                f"{hour:02d}:00",
                self
            )

            lbl.setAlignment(
                Qt.AlignmentFlag.AlignTop
                | Qt.AlignmentFlag.AlignCenter
            )

            lbl.setStyleSheet(f"""
                QLabel {{
                    background-color: {BG_MAIN};
                    color: {TEXT_MUT};
                    border-right: 1px solid #1C1C1C;
                    font-size: 10px;
                    font-weight: 800;
                    padding-top: 8px;
                }}
            """)

            row_cells = []

            for day in range(7):
                cell = TimeCell(
                    day,
                    hour,
                    self.accent,
                    self
                )

                cell.clicked.connect(
                    self.parent_view.open_class_form
                )

                cell.dropped.connect(
                    self.parent_view.move_schedule_from_drop
                )

                cell.hover_day.connect(
                    self._set_day_highlight
                )

                row_cells.append(cell)

            self.cells.append(
                (lbl, row_cells)
            )

        self._update_day_numbers()

    def set_accent(self, color):
        self.accent = color

        for header in self.day_headers:
            header.set_accent(color)

        for _, row_cells in self.cells:
            for cell in row_cells:
                cell.set_accent(color)

        for block in self.blocks:
            block.accent = color
            block.refresh_style()

    def set_week_start(self, week_start):
        self.week_start = week_start
        self._update_day_numbers()
        self._update_realtime_state()

    def _update_day_numbers(self):
        today = date.today()

        for idx, header in enumerate(
            self.day_headers
        ):
            displayed_date = (
                self.week_start
                + timedelta(days=idx)
            )

            is_today = (
                displayed_date == today
            )

            header.set_day_num(
                displayed_date.day
            )

            header.set_today(is_today)

            for _, row_cells in self.cells:
                row_cells[idx].set_today_column(
                    is_today
                )

    def _set_day_highlight(
        self,
        day,
        active
    ):
        if 0 <= day < len(self.day_headers):
            self.day_headers[day].set_hover(
                active
            )

    def _is_showing_current_week(self):
        today = date.today()
        week_end = (
            self.week_start
            + timedelta(days=6)
        )

        return (
            self.week_start
            <= today
            <= week_end
        )

    def _update_realtime_state(self):
        self._update_current_time_indicator()
        self._update_live_classes()

    def _update_current_time_indicator(self):
        if not self._is_showing_current_week():
            self.current_time_indicator.hide()
            self.current_time_dot.hide()
            self.current_time_label.hide()
            return

        now = datetime.now()

        total_minutes = (
            now.hour * 60
            + now.minute
        )

        calendar_start = (
            self.start_hour * 60
        )

        # Cada celda representa desde HH:00
        # hasta la hora siguiente.
        calendar_end = (
            (self.end_hour + 1) * 60
        )

        if not (
            calendar_start
            <= total_minutes
            < calendar_end
        ):
            self.current_time_indicator.hide()
            self.current_time_dot.hide()
            self.current_time_label.hide()
            return

        available_width = max(
            self.width(),
            920
        )

        day_width = int(
            (
                available_width
                - self.hour_col_w
            )
            / 7
        )

        current_day = now.weekday()

        x = (
            self.hour_col_w
            + current_day * day_width
        )

        y = (
            self.header_h
            + int(
                (
                    total_minutes
                    - calendar_start
                )
                / 60
                * self.cell_h
            )
        )

        line_x = x + 4
        line_width = max(
            20,
            day_width - 8
        )

        self.current_time_indicator.setGeometry(
            line_x,
            y,
            line_width,
            2
        )

        self.current_time_dot.move(
            line_x,
            y - 3
        )

        label_x = max(
            x + 6,
            x + day_width - 52
        )

        self.current_time_label.setText(
            now.strftime("%H:%M")
        )

        self.current_time_label.move(
            label_x,
            max(
                self.header_h,
                y - 9
            )
        )

        self.current_time_indicator.show()
        self.current_time_dot.show()
        self.current_time_label.show()

        # La línea queda encima de las celdas.
        self.current_time_indicator.raise_()
        self.current_time_dot.raise_()
        self.current_time_label.raise_()

        # Los bloques deben quedar por encima de la línea.
        for block in self.blocks:
            block.raise_()

    def _update_live_classes(self):
        now = datetime.now()
        showing_current_week = (
            self._is_showing_current_week()
        )

        current_minutes = (
            now.hour * 60
            + now.minute
        )

        for block in self.blocks:
            data = block.data

            try:
                day = int(
                    data.get("day_of_week")
                )

                start_h, start_m = self._parse_time(
                    data.get("start_time")
                )

                end_h, end_m = self._parse_time(
                    data.get("end_time")
                )

                start_minutes = (
                    start_h * 60
                    + start_m
                )

                end_minutes = (
                    end_h * 60
                    + end_m
                )

                is_live = (
                    showing_current_week
                    and day == now.weekday()
                    and start_minutes
                    <= current_minutes
                    < end_minutes
                )

            except Exception:
                is_live = False

            block.set_live(is_live)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self._layout_absolute()
        self._update_current_time_indicator()

    def _layout_absolute(self):
        width = max(
            self.width(),
            920
        )

        day_width = int(
            (
                width
                - self.hour_col_w
            )
            / 7
        )

        self.corner.setGeometry(
            0,
            0,
            self.hour_col_w,
            self.header_h
        )

        for day, header in enumerate(
            self.day_headers
        ):
            header.setGeometry(
                self.hour_col_w
                + day * day_width,
                0,
                day_width,
                self.header_h
            )

        for row_index, item in enumerate(
            self.cells
        ):
            hour_label, row_cells = item

            y = (
                self.header_h
                + row_index * self.cell_h
            )

            hour_label.setGeometry(
                0,
                y,
                self.hour_col_w,
                self.cell_h
            )

            for day, cell in enumerate(
                row_cells
            ):
                cell.setGeometry(
                    self.hour_col_w
                    + day * day_width,
                    y,
                    day_width,
                    self.cell_h
                )

        self._layout_blocks()
        self._update_current_time_indicator()

    def load_data(self, filters=None):
        self.clear_blocks()

        try:
            rows = self.repo.get_week_schedules(
                filters or {}
            )

        except Exception as e:
            debug_log(
                f"[WeeklyCalendarWidget] Error cargando datos: {e}"
            )
            rows = []

        for row in rows:
            data = {
                "id": row[0],
                "name": row[1],
                "day_of_week": row[2],
                "start_time": self._time_to_str(
                    row[3]
                ),
                "end_time": self._time_to_str(
                    row[4]
                ),
                "capacity": row[5],
                "location": row[6],
                "status": row[7],
                "repeat_type": row[8],
                "instructor": row[9],
                "martial_art": row[10],
                "color": row[11],
                "id_instructor": row[12],
                "id_martial_art": row[13],
            }

            block = ClassBlock(
                data,
                self.parent_view,
                self.accent,
                self
            )

            block.show()
            self.blocks.append(block)

        self._layout_blocks()
        self._update_realtime_state()

    def clear_blocks(self):
        for block in self.blocks:
            block.deleteLater()

        self.blocks = []

    def _layout_blocks(self):
        if not self.blocks:
            return

        width = max(
            self.width(),
            920
        )

        day_width = int(
            (
                width
                - self.hour_col_w
            )
            / 7
        )

        for block in self.blocks:
            data = block.data

            try:
                day = int(
                    data["day_of_week"]
                )

                start_h, start_m = self._parse_time(
                    data["start_time"]
                )

                end_h, end_m = self._parse_time(
                    data["end_time"]
                )

            except Exception:
                continue

            if day < 0 or day > 6:
                continue

            start_minutes = (
                start_h * 60
                + start_m
            )

            end_minutes = (
                end_h * 60
                + end_m
            )

            calendar_start = (
                self.start_hour * 60
            )

            duration_minutes = max(
                30,
                end_minutes - start_minutes
            )

            x = (
                self.hour_col_w
                + day * day_width
                + 6
            )

            y = (
                self.header_h
                + int(
                    (
                        start_minutes
                        - calendar_start
                    )
                    / 60
                    * self.cell_h
                )
                + 6
            )

            height = (
                int(
                    duration_minutes
                    / 60
                    * self.cell_h
                )
                - 12
            )

            height = max(
                48,
                min(height, 180)
            )

            block.setGeometry(
                x,
                y,
                day_width - 12,
                height
            )

            block.raise_()

    def _parse_time(self, value):
        if not value or value == "—":
            return 0, 0

        parts = str(value).split(":")

        return (
            int(parts[0]),
            int(parts[1])
        )

    def _time_to_str(self, value):
        if not value:
            return "—"

        try:
            return value.strftime("%H:%M")

        except Exception:
            return str(value)[:5]


# ─────────────────────────────────────────────────────────────
# Monthly Events
# ─────────────────────────────────────────────────────────────

MAX_VISIBLE_EVENTS_PER_DAY = 2


def normalize_event_row(row):
    """Normalize a raw tuple from get_month_events into a dict."""
    return {
        "id": row[0],
        "name": row[1] or "Sin nombre",
        "event_date": row[2],
        "event_type": row[3] or "",
        "description": row[4] or "",
        "color": row[5] or "#3B82F6",
        "start_time": row[6],
        "end_time": row[7],
        "location": row[8] or "",
        "is_important": row[9] if len(row) > 9 else False,
    }


class EventMiniChip(QFrame):
    """Compact chip shown inside a monthly day cell for each event."""

    def __init__(self, event, parent=None):
        super().__init__(parent)
        self._event = event
        self.setObjectName("EventMiniChip")
        self.setFixedHeight(24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        color = event["color"]
        r = int(color[1:3], 16) if len(color) >= 7 else 200
        g = int(color[3:5], 16) if len(color) >= 7 else 16
        b = int(color[5:7], 16) if len(color) >= 7 else 46

        self.setStyleSheet(f"""
            QFrame#EventMiniChip {{
                background-color: rgba({r},{g},{b},0.10);
                border: 1px solid rgba({r},{g},{b},0.30);
                border-radius: 6px;
            }}
            QFrame#EventMiniChip:hover {{
                background-color: rgba({r},{g},{b},0.18);
                border-color: rgba({r},{g},{b},0.50);
            }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 0, 6, 0)
        lay.setSpacing(4)

        dot = QLabel()
        dot.setFixedSize(6, 6)
        dot.setStyleSheet(
            f"background-color: {color}; border-radius: 3px; border: none;"
        )
        lay.addWidget(dot, 0, Qt.AlignmentFlag.AlignVCenter)

        name = event["name"]
        if len(name) > 16:
            name = name[:15] + "…"

        lbl = QLabel(name)
        lbl.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 9px; font-weight: 700; "
            f"font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;"
        )
        lbl.setFixedWidth(90)
        lay.addWidget(lbl, 1, Qt.AlignmentFlag.AlignVCenter)

        time_str = ""
        if event["start_time"]:
            st = event["start_time"]
            if hasattr(st, "strftime"):
                time_str = st.strftime("%H:%M")
            else:
                time_str = str(st)[:5]
        if time_str:
            lbl_t = QLabel(time_str)
            lbl_t.setStyleSheet(
                f"color: {TEXT_MUT}; font-size: 8px; font-weight: 600; "
                f"font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;"
            )
            lay.addWidget(lbl_t, 0, Qt.AlignmentFlag.AlignVCenter)

        tip = event["name"]
        if event["start_time"]:
            st = event["start_time"]
            ts = st.strftime("%H:%M") if hasattr(st, "strftime") else str(st)[:5]
            tip += f"\n{ts}"
        if event["location"]:
            tip += f"\n{event['location']}"
        if event["description"]:
            tip += f"\n{event['description'][:60]}"
        self.setToolTip(tip)


class MonthlyDayCell(QFrame):
    """Interactive day cell in the monthly calendar grid."""

    def __init__(self, day_num, year, month, events, accent, parent_view, parent=None):
        super().__init__(parent)
        self._day_num = day_num
        self._year = year
        self._month = month
        self._events = events
        self._accent = accent
        self._parent_view = parent_view
        self._hovered = False

        today = date.today()
        self._is_today = (today.year == year and today.month == month and today.day == day_num)

        self.setObjectName("MonthlyDayCell")
        self.setMinimumHeight(105)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

        self._apply_style()
        self._build_content()

    def _apply_style(self):
        if self._is_today:
            bg = CURRENT_BG
            border = CURRENT_BORDER
            bw = 2
            day_color = "#E2E8F0"
        else:
            bg = "#0E0E0E"
            border = "#1C1C1C"
            bw = 1
            day_color = TEXT_PRI

        hover_bg = CURRENT_BG_HOVER if self._is_today else "#121212"
        hover_border = CURRENT_LINE if self._is_today else self._accent

        self.setStyleSheet(f"""
            QFrame#MonthlyDayCell {{
                background-color: {bg};
                border: {bw}px solid {border};
                border-radius: 10px;
            }}
            QFrame#MonthlyDayCell:hover {{
                background-color: {hover_bg};
                border-color: {hover_border};
            }}
        """)
        self._day_color = day_color

    def _build_content(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(4)

        lbl_day = QLabel(str(self._day_num))
        lbl_day.setStyleSheet(
            f"color: {self._day_color}; font-size: 12px; font-weight: 900; "
            f"background: transparent; border: none;"
        )
        top_row.addWidget(lbl_day)
        top_row.addStretch()

        if self._is_today:
            lbl_hoy = QLabel("HOY")
            lbl_hoy.setStyleSheet(
                f"color: {CURRENT_TEXT}; font-size: 8px; font-weight: 900; "
                f"letter-spacing: 1px; background: transparent; border: none;"
            )
            top_row.addWidget(lbl_hoy)

        layout.addLayout(top_row)

        ev_count = len(self._events)
        visible = self._events[:MAX_VISIBLE_EVENTS_PER_DAY]

        for ev in visible:
            chip = EventMiniChip(ev)
            chip.mousePressEvent = lambda e, ev=ev: self._open_day_dialog(ev)
            layout.addWidget(chip)

        if ev_count > MAX_VISIBLE_EVENTS_PER_DAY:
            more = QLabel(f"+{ev_count - MAX_VISIBLE_EVENTS_PER_DAY} eventos")
            more.setStyleSheet(
                f"color: {TEXT_MUT}; font-size: 9px; font-weight: 600; "
                f"background: transparent; border: none;"
            )
            more.setCursor(Qt.CursorShape.PointingHandCursor)
            more.mousePressEvent = lambda e: self._open_day_dialog()
            layout.addWidget(more)

        self._lbl_action = QLabel("+ Agregar evento")
        self._lbl_action.setStyleSheet(
            f"color: #3F4651; font-size: 9px; font-weight: 600; "
            f"background: transparent; border: none;"
        )
        self._lbl_action.hide()
        layout.addWidget(self._lbl_action)

        layout.addStretch()

    def enterEvent(self, event):
        self._hovered = True
        if not self._events:
            self._lbl_action.setStyleSheet(
                f"color: {self._accent}; font-size: 9px; font-weight: 600; "
                f"background: transparent; border: none;"
            )
            self._lbl_action.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._lbl_action.hide()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)
        if self._events:
            self._open_day_dialog()
        else:
            self._parent_view.open_event_form(
                default_date=date(self._year, self._month, self._day_num)
            )
        super().mousePressEvent(event)

    def _open_day_dialog(self, focus_event=None):
        parent_view = self._parent_view

        parent_view.glass.setGeometry(parent_view.rect())
        parent_view.glass.fade_in()
        parent_view.glass.raise_()

        dlg = DayEventsDialog(
            selected_date=date(self._year, self._month, self._day_num),
            events=self._events,
            parent_view=parent_view,
            focus_event=focus_event,
            parent=parent_view,
        )

        try:
            dlg.exec()

            if dlg.next_action == "edit":
                parent_view.open_event_form(
                    event_id=dlg.next_event_id,
                    default_date=dlg.selected_date,
                    blur_already_active=True,
                )
            elif dlg.next_action == "add":
                parent_view.open_event_form(
                    event_id=None,
                    default_date=dlg.selected_date,
                    blur_already_active=True,
                )
        finally:
            parent_view.glass.fade_out()
            parent_view.reload_current_view()


class DraggableDialogHeader(QFrame):
    """Frameless-dialog header that supports mouse drag."""

    def __init__(self, parent_dialog):
        super().__init__(parent_dialog)
        self._dialog = parent_dialog
        self._drag_pos = None

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = ev.globalPosition().toPoint() - self._dialog.frameGeometry().topLeft()
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        if self._drag_pos is not None and ev.buttons() & Qt.MouseButton.LeftButton:
            self._dialog.move(ev.globalPosition().toPoint() - self._drag_pos)
        super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev):
        self._drag_pos = None
        super().mouseReleaseEvent(ev)


class DayEventsDialog(QDialog):
    """Modal dialog showing all events for a specific day."""

    def __init__(self, selected_date, events, parent_view, focus_event=None, parent=None):
        super().__init__(parent)
        self.selected_date = selected_date
        self._events = events
        self._parent_view = parent_view
        self._focus_event = focus_event
        self.next_action = None
        self.next_event_id = None

        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)

        dialog_height = min(640, max(380, 250 + len(events) * 112))
        self.setFixedWidth(560)
        self.resize(560, dialog_height)

        self.setStyleSheet("QDialog { background: transparent; }")

        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(0)

        self.card = QFrame()
        self.card.setObjectName("DayEventsDialogCard")
        self.card.setStyleSheet("""
            QFrame#DayEventsDialogCard {
                background-color: #101010;
                border: 1px solid #292929;
                border-radius: 18px;
            }
            QFrame#DayEventsDialogCard QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        card_lay = QVBoxLayout(self.card)
        card_lay.setContentsMargins(0, 0, 0, 0)
        card_lay.setSpacing(0)

        self._build_header(card_lay)
        self._build_body(card_lay)
        self._build_footer(card_lay)

        card_shadow = QGraphicsDropShadowEffect(self.card)
        card_shadow.setBlurRadius(32)
        card_shadow.setOffset(0, 10)
        card_shadow.setColor(QColor(0, 0, 0, 190))
        self.card.setGraphicsEffect(card_shadow)
        self._card_shadow = card_shadow

        root.addWidget(self.card)

    # ── Header ─────────────────────────────────────────────────

    def _build_header(self, parent_lay):
        header = DraggableDialogHeader(self)
        header.setObjectName("DayEventsHeader")
        header.setStyleSheet("""
            QFrame#DayEventsHeader {
                background-color: #0D0D0D;
                border: none;
                border-bottom: 1px solid #242424;
                border-top-left-radius: 18px;
                border-top-right-radius: 18px;
            }
            QFrame#DayEventsHeader QLabel {
                background: transparent;
                border: none;
            }
        """)
        header.setFixedHeight(90)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(22, 18, 18, 18)
        h_lay.setSpacing(14)

        icon_box = QFrame()
        icon_box.setFixedSize(42, 42)
        icon_box.setObjectName("DayCalendarIconBox")
        icon_box.setStyleSheet("""
            QFrame#DayCalendarIconBox {
                background-color: rgba(200, 16, 46, 0.10);
                border: 1px solid rgba(200, 16, 46, 0.28);
                border-radius: 11px;
            }
        """)
        icon_lay = QVBoxLayout(icon_box)
        icon_lay.setContentsMargins(0, 0, 0, 0)
        icon_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lay.addWidget(IconLabel("calendar", 20, "#E8152F"))
        h_lay.addWidget(icon_box)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        eyebrow = QLabel("EVENTOS")
        eyebrow.setStyleSheet(
            "color: #C8102E; font-size: 8px; font-weight: 900; "
            "letter-spacing: 1.4px; font-family: 'Inter','Segoe UI',sans-serif;"
        )
        text_col.addWidget(eyebrow)

        lbl_title = QLabel("Eventos del día")
        lbl_title.setStyleSheet(
            "color: #F4F4F5; font-size: 17px; font-weight: 900; "
            "font-family: 'Inter','Segoe UI',sans-serif;"
        )
        text_col.addWidget(lbl_title)

        day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        month_names = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]
        dn = day_names[self.selected_date.weekday()]
        mn = month_names[self.selected_date.month - 1]
        lbl_date = QLabel(f"{dn}, {self.selected_date.day} de {mn} de {self.selected_date.year}")
        lbl_date.setStyleSheet(
            "color: #737B88; font-size: 11px; font-weight: 600; "
            "font-family: 'Inter','Segoe UI',sans-serif;"
        )
        text_col.addWidget(lbl_date)

        h_lay.addLayout(text_col, 1)

        self._close_icon = IconLabel("close", 16, "#9CA3AF")
        btn_close = QPushButton()
        btn_close.setObjectName("DayDialogCloseButton")
        btn_close.setFixedSize(38, 38)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setToolTip("Cerrar")
        btn_close.setStyleSheet("""
            QPushButton#DayDialogCloseButton {
                background-color: #151515;
                border: 1px solid #292929;
                border-radius: 10px;
            }
            QPushButton#DayDialogCloseButton:hover {
                background-color: rgba(200, 16, 46, 0.10);
                border-color: rgba(200, 16, 46, 0.45);
            }
        """)
        close_lay = QVBoxLayout(btn_close)
        close_lay.setContentsMargins(0, 0, 0, 0)
        close_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        close_lay.addWidget(self._close_icon)
        btn_close.clicked.connect(self.reject)
        h_lay.addWidget(btn_close, 0, Qt.AlignmentFlag.AlignTop)

        parent_lay.addWidget(header)

    # ── Body ───────────────────────────────────────────────────

    def _build_body(self, parent_lay):
        body = QFrame()
        body.setObjectName("DayEventsBody")
        body.setStyleSheet("""
            QFrame#DayEventsBody {
                background-color: #101010;
                border: none;
            }
            QFrame#DayEventsBody QLabel {
                background: transparent;
                border: none;
            }
        """)
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(22, 18, 22, 18)
        body_lay.setSpacing(14)

        count = len(self._events)
        count_text = f"{count} EVENTO PROGRAMADO" if count == 1 else f"{count} EVENTOS PROGRAMADOS"
        lbl_count = QLabel(count_text)
        lbl_count.setObjectName("DayEventCountBadge")
        lbl_count.setStyleSheet("""
            QLabel#DayEventCountBadge {
                color: #A5ACB8;
                background-color: #161616;
                border: 1px solid #292929;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 8px;
                font-weight: 900;
                letter-spacing: 0.8px;
                font-family: 'Inter','Segoe UI',sans-serif;
            }
        """)
        lbl_count.setFixedWidth(lbl_count.sizeHint().width() + 20)
        body_lay.addWidget(lbl_count)

        scroll = QScrollArea()
        scroll.setObjectName("DayEventsScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea#DayEventsScroll {
                background: transparent;
                border: none;
            }
            QScrollArea#DayEventsScroll > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                width: 6px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background-color: #303030;
                border-radius: 3px;
                min-height: 24px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        scroll_widget = QWidget()
        scroll_widget.setObjectName("DayEventsScrollContent")
        scroll_widget.setStyleSheet("background: transparent; border: none;")
        events_lay = QVBoxLayout(scroll_widget)
        events_lay.setContentsMargins(0, 0, 0, 0)
        events_lay.setSpacing(10)

        for ev in self._events:
            ev_card = self._make_event_card(ev)
            events_lay.addWidget(ev_card)

        events_lay.addStretch()
        scroll.setWidget(scroll_widget)
        body_lay.addWidget(scroll, 1)

        parent_lay.addWidget(body, 1)

    # ── Footer ─────────────────────────────────────────────────

    def _build_footer(self, parent_lay):
        footer = QFrame()
        footer.setObjectName("DayEventsFooter")
        footer.setStyleSheet("""
            QFrame#DayEventsFooter {
                background-color: #0D0D0D;
                border: none;
                border-top: 1px solid #242424;
                border-bottom-left-radius: 18px;
                border-bottom-right-radius: 18px;
            }
            QFrame#DayEventsFooter QLabel {
                background: transparent;
                border: none;
            }
        """)
        footer_lay = QHBoxLayout(footer)
        footer_lay.setContentsMargins(22, 16, 22, 16)
        footer_lay.setSpacing(12)

        btn_add = QPushButton()
        btn_add.setObjectName("DayDialogPrimaryButton")
        btn_add.setMinimumWidth(156)
        btn_add.setFixedHeight(40)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton#DayDialogPrimaryButton {
                background-color: #C8102E;
                color: white;
                border: 1px solid #E8152F;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 900;
                font-family: 'Inter','Segoe UI',sans-serif;
            }
            QPushButton#DayDialogPrimaryButton:hover {
                background-color: #E8152F;
            }
            QPushButton#DayDialogPrimaryButton:pressed {
                background-color: #A70D26;
            }
        """)
        add_lay = QHBoxLayout(btn_add)
        add_lay.setContentsMargins(14, 0, 14, 0)
        add_lay.setSpacing(8)
        add_lay.addWidget(IconLabel("plus", 14, "white"))
        add_lbl = QLabel("Agregar evento")
        add_lbl.setStyleSheet(
            "color: white; background: transparent; border: none; "
            "font-size: 11px; font-weight: 900; font-family: 'Inter','Segoe UI',sans-serif;"
        )
        add_lay.addWidget(add_lbl)
        btn_add.clicked.connect(self._add_another)
        btn_add.setToolTip("Agregar otro evento para este día")
        footer_lay.addWidget(btn_add)

        footer_lay.addStretch()

        btn_close = QPushButton("Cerrar")
        btn_close.setObjectName("DayDialogSecondaryButton")
        btn_close.setMinimumWidth(92)
        btn_close.setFixedHeight(40)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton#DayDialogSecondaryButton {
                background-color: #171717;
                color: #AEB4BE;
                border: 1px solid #2C2C2C;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 800;
                font-family: 'Inter','Segoe UI',sans-serif;
            }
            QPushButton#DayDialogSecondaryButton:hover {
                background-color: #202020;
                color: #F0F0F0;
                border-color: #3A3A3A;
            }
        """)
        btn_close.clicked.connect(self.reject)
        footer_lay.addWidget(btn_close)

        parent_lay.addWidget(footer)

    # ── Event card ─────────────────────────────────────────────

    def _make_event_card(self, ev):
        color = ev["color"]

        card = QFrame()
        card.setObjectName("DayEventInfoCard")
        card.setMinimumHeight(96)
        card.setStyleSheet(f"""
            QFrame#DayEventInfoCard {{
                background-color: #141414;
                border: 1px solid #292929;
                border-radius: 12px;
            }}
            QFrame#DayEventInfoCard:hover {{
                background-color: #1A1A1A;
                border-color: #383838;
            }}
        """)

        main_lay = QHBoxLayout(card)
        main_lay.setContentsMargins(0, 0, 12, 0)
        main_lay.setSpacing(0)

        accent_bar = QFrame()
        accent_bar.setFixedWidth(4)
        accent_bar.setStyleSheet(
            f"background-color: {color}; border-radius: 2px;"
        )
        main_lay.addWidget(accent_bar)

        content = QVBoxLayout()
        content.setContentsMargins(14, 12, 2, 12)
        content.setSpacing(5)

        top = QHBoxLayout()
        top.setSpacing(8)

        ev_icon_box = QFrame()
        ev_icon_box.setFixedSize(34, 34)
        ev_icon_box.setObjectName("EventIconBox")
        ev_icon_box.setStyleSheet(f"""
            QFrame#EventIconBox {{
                background-color: {color}18;
                border: 1px solid {color}44;
                border-radius: 9px;
            }}
        """)
        ev_icon_lay = QVBoxLayout(ev_icon_box)
        ev_icon_lay.setContentsMargins(0, 0, 0, 0)
        ev_icon_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ev_icon_lay.addWidget(IconLabel("event", 17, color))
        top.addWidget(ev_icon_box)

        name_col = QVBoxLayout()
        name_col.setSpacing(1)
        lbl_name = QLabel(ev["name"])
        lbl_name.setStyleSheet(
            "color: #F1F1F1; font-size: 13px; font-weight: 900; "
            "font-family: 'Inter','Segoe UI',sans-serif;"
        )
        name_col.addWidget(lbl_name)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(10)
        if ev["start_time"]:
            st = ev["start_time"]
            ts = st.strftime("%H:%M") if hasattr(st, "strftime") else str(st)[:5]
            time_chip = QHBoxLayout()
            time_chip.setSpacing(4)
            time_chip.addWidget(IconLabel("clock", 12, "#737B88"))
            tl = QLabel(ts)
            tl.setStyleSheet(
                "color: #737B88; font-size: 10px; font-weight: 600; "
                "font-family: 'Inter','Segoe UI',sans-serif;"
            )
            time_chip.addWidget(tl)
            meta_row.addLayout(time_chip)
        if ev["location"]:
            loc_chip = QHBoxLayout()
            loc_chip.setSpacing(4)
            loc_chip.addWidget(IconLabel("location", 12, "#737B88"))
            ll = QLabel(ev["location"])
            ll.setStyleSheet(
                "color: #737B88; font-size: 10px; font-weight: 600; "
                "font-family: 'Inter','Segoe UI',sans-serif;"
            )
            loc_chip.addWidget(ll)
            meta_row.addLayout(loc_chip)
        meta_row.addStretch()
        name_col.addLayout(meta_row)

        top.addLayout(name_col, 1)

        if ev["is_important"]:
            imp_badge = QLabel("★ IMPORTANTE")
            imp_badge.setStyleSheet(
                "color: #FBBF24; background-color: rgba(245, 158, 11, 0.10); "
                "border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 7px; "
                "padding: 3px 7px; font-size: 7px; font-weight: 900; "
                "letter-spacing: 0.7px; font-family: 'Inter','Segoe UI',sans-serif;"
            )
            top.addWidget(imp_badge)

        content.addLayout(top)

        if ev["description"]:
            desc = ev["description"][:120]
            if len(ev["description"]) > 120:
                desc += "..."
            lbl_desc = QLabel(desc)
            lbl_desc.setWordWrap(True)
            lbl_desc.setMaximumHeight(30)
            lbl_desc.setStyleSheet(
                "color: #737B88; font-size: 10px; font-weight: 500; "
                "font-family: 'Inter','Segoe UI',sans-serif;"
            )
            content.addWidget(lbl_desc)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 2, 0, 0)
        actions.addStretch()

        btn_edit = QPushButton()
        btn_edit.setObjectName("DayEventEditButton")
        btn_edit.setFixedSize(86, 32)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setToolTip("Editar evento")
        btn_edit.setStyleSheet("""
            QPushButton#DayEventEditButton {
                background-color: #1A1A1A;
                color: #CBD0D8;
                border: 1px solid #303030;
                border-radius: 8px;
                font-size: 10px;
                font-weight: 800;
                font-family: 'Inter','Segoe UI',sans-serif;
            }
            QPushButton#DayEventEditButton:hover {
                background-color: rgba(200, 16, 46, 0.10);
                color: #F2F2F2;
                border-color: rgba(200, 16, 46, 0.45);
            }
            QPushButton#DayEventEditButton:pressed {
                background-color: rgba(200, 16, 46, 0.18);
            }
        """)
        edit_lay = QHBoxLayout(btn_edit)
        edit_lay.setContentsMargins(0, 0, 0, 0)
        edit_lay.setSpacing(4)
        edit_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        edit_lay.addWidget(IconLabel("edit", 13, "#CBD0D8"))
        edit_lbl = QLabel("Editar")
        edit_lbl.setStyleSheet(
            "color: #CBD0D8; background: transparent; border: none; "
            "font-size: 10px; font-weight: 800; font-family: 'Inter','Segoe UI',sans-serif;"
        )
        edit_lay.addWidget(edit_lbl)

        eid = ev["id"]
        btn_edit.clicked.connect(lambda _, eid=eid: self._edit_event(eid))
        actions.addWidget(btn_edit)

        content.addLayout(actions)
        main_lay.addLayout(content, 1)

        if self._focus_event and self._focus_event.get("id") == ev["id"]:
            card.setStyleSheet(card.styleSheet().replace("#292929", "#4A4A4A"))

        return card

    # ── Actions ────────────────────────────────────────────────

    def _edit_event(self, event_id):
        self.next_action = "edit"
        self.next_event_id = event_id
        self.accept()

    def _add_another(self):
        self.next_action = "add"
        self.next_event_id = None
        self.accept()

    # ── Cleanup ────────────────────────────────────────────────

    def done(self, result):
        try:
            if hasattr(self, "_fade_animation"):
                self._fade_animation.stop()

            if hasattr(self, "card") and self.card is not None:
                self.card.setGraphicsEffect(None)

            self.setGraphicsEffect(None)
        except Exception as e:
            debug_log(f"[DayEventsDialog] Error limpiando efectos: {e}")

        super().done(result)

    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(ev)


class MonthlyEventsWidget(QWidget):
    def __init__(self, repo, parent_view):
        super().__init__()

        self.repo = repo
        self.parent_view = parent_view
        self.year = date.today().year
        self.month = date.today().month

        self.accent = parent_view.accent_color
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        top = QHBoxLayout()

        self.lbl_title = QLabel("Eventos del mes")
        self.lbl_title.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 18px;
            font-weight: 800;
        """)

        tag = QLabel("CALENDARIO DE EVENTOS")
        tag.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 9px;
            font-weight: 900;
            letter-spacing: 1px;
        """)

        top.addWidget(IconLabel("event", 18, TEXT_SEC))
        top.addWidget(self.lbl_title)
        top.addStretch()
        top.addWidget(tag)
        root.addLayout(top)

        self.lbl_subtitle = QLabel("Selecciona un día para crear o administrar eventos.")
        self.lbl_subtitle.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 11px;
            font-weight: 500;
        """)
        root.addWidget(self.lbl_subtitle)

        shell = QFrame()
        shell.setStyleSheet(f"""
            QFrame {{
                background-color: #0C0C0C;
                border: 1px solid #1C1C1C;
                border-radius: 14px;
            }}
        """)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(16, 16, 16, 16)
        shell_layout.setSpacing(10)

        # Header días
        self.header_grid = QGridLayout()
        self.header_grid.setSpacing(8)
        self.header_grid.setContentsMargins(0, 0, 0, 0)

        for i, d in enumerate(DAYS_SHORT):
            lbl = QLabel(d.upper())
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFixedHeight(28)
            lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            lbl.setStyleSheet(f"""
                QLabel {{
                    background-color: #090909;
                    color: {TEXT_MUT};
                    border: 1px solid #1C1C1C;
                    border-radius: 0px;
                    font-size: 10px;
                    font-weight: 900;
                    letter-spacing: 1px;
                }}
            """)
            self.header_grid.addWidget(lbl, 0, i)
            self.header_grid.setColumnStretch(i, 1)

        shell_layout.addLayout(self.header_grid)

        # Grid días del mes
        self.grid = QGridLayout()
        self.grid.setSpacing(8)
        self.grid.setContentsMargins(0, 0, 0, 0)

        for i in range(7):
            self.grid.setColumnStretch(i, 1)

        shell_layout.addLayout(self.grid, 1)

        root.addWidget(shell, 1)

    def set_accent(self, color):
        self.accent = color

    def load_month(self, year, month):
        self.year = year
        self.month = month

        month_names = [
            "Enero", "Febrero", "Marzo", "Abril",
            "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        self.lbl_title.setText(f"Eventos · {month_names[month - 1]} {year}")
        self._clear_grid()

        for i in range(7):
            self.grid.setColumnStretch(i, 1)

        try:
            events = self.repo.get_month_events(year, month)
        except Exception as e:
            debug_log(f"[MonthlyEventsWidget] Error cargando eventos: {e}")
            events = []

        events_by_day = {}
        for ev in events:
            day_num = ev[2].day
            norm = normalize_event_row(ev)
            events_by_day.setdefault(day_num, []).append(norm)

        first = date(year, month, 1)
        start_col = first.weekday()

        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)

        total_days = (next_month - first).days

        row = 0
        col = 0

        for _ in range(start_col):
            empty = self._make_empty_cell()
            self.grid.addWidget(empty, row, col)
            col += 1

        for day_num in range(1, total_days + 1):
            cell = MonthlyDayCell(
                day_num, year, month,
                events_by_day.get(day_num, []),
                self.accent,
                self.parent_view,
            )
            self.grid.addWidget(cell, row, col)
            col += 1
            if col > 6:
                col = 0
                row += 1

        if col != 0:
            while col <= 6:
                empty = self._make_empty_cell()
                self.grid.addWidget(empty, row, col)
                col += 1

        for r in range(row + 1):
            self.grid.setRowStretch(r, 1)

    def _make_empty_cell(self):
        cell = QFrame()
        cell.setMinimumHeight(105)
        cell.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        cell.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 10px;
            }
        """)

        return cell

    def _clear_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


# ─────────────────────────────────────────────────────────────
# Yearly Summary
# ─────────────────────────────────────────────────────────────
class YearlySummaryWidget(QWidget):
    def __init__(self, repo, parent_view):
        super().__init__()

        self.repo = repo
        self.parent_view = parent_view
        self.year = date.today().year
        self.accent = parent_view.accent_color

        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        top = QHBoxLayout()

        self.lbl_title = QLabel("Resumen anual de eventos")
        self.lbl_title.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 18px;
            font-weight: 800;
        """)

        tag = QLabel("DISTRIBUCIÓN DE EVENTOS")
        tag.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 9px;
            font-weight: 900;
            letter-spacing: 1px;
        """)

        top.addWidget(IconLabel("event", 18, TEXT_SEC))
        top.addWidget(self.lbl_title)
        top.addStretch()
        top.addWidget(tag)
        root.addLayout(top)

        self.grid = QGridLayout()
        self.grid.setSpacing(12)

        root.addLayout(self.grid, 1)

    def set_accent(self, color):
        self.accent = color

    def load_year(self, year):
        self.year = year
        self.lbl_title.setText(f"Resumen anual de eventos · {year}")
        self._clear_grid()

        try:
            summary = self.repo.get_year_summary(year)
        except Exception as e:
            debug_log(f"[YearlySummaryWidget] Error cargando resumen anual: {e}")
            summary = {}

        months = [
            "Enero", "Febrero", "Marzo", "Abril",
            "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        for idx, name in enumerate(months):
            month = idx + 1
            count = summary.get(month, 0)

            card = self._month_card(name, month, count)
            self.grid.addWidget(card, idx // 4, idx % 4)

    def _month_card(
        self,
        name,
        month,
        count
    ):
        today = date.today()

        is_current_month = (
            self.year == today.year
            and month == today.month
        )

        if count == 0:
            density_color = "#444444"

        elif count < 3:
            density_color = "#3B82F6"

        elif count < 6:
            density_color = "#F59E0B"

        else:
            density_color = "#10B981"

        if is_current_month:
            background = CURRENT_BG
            border = CURRENT_BORDER
            left_border = CURRENT_LINE
            month_color = "#E2E8F0"
            hover_background = CURRENT_BG_HOVER
            hover_border = CURRENT_LINE

        else:
            background = "#0E0E0E"
            border = "#1F1F1F"
            left_border = density_color
            month_color = TEXT_MUT
            hover_background = "#121212"
            hover_border = self.accent

        card = QFrame()
        card.setMinimumHeight(120)

        card.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        card.setStyleSheet(f"""
            QFrame {{
                background-color: {background};
                border: 1px solid {border};
                border-left: 4px solid {left_border};
                border-radius: 12px;
            }}

            QFrame:hover {{
                background-color: {hover_background};
                border-color: {hover_border};
                border-left: 4px solid {left_border};
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(
            16,
            14,
            16,
            14
        )
        layout.setSpacing(8)

        month_row = QHBoxLayout()
        month_row.setContentsMargins(
            0,
            0,
            0,
            0
        )
        month_row.setSpacing(6)

        lbl_name = QLabel(name)
        lbl_name.setStyleSheet(f"""
            color: {month_color};
            font-size: 11px;
            font-weight: 900;
            letter-spacing: 1px;
        """)

        month_row.addWidget(lbl_name)
        month_row.addStretch()

        if is_current_month:
            lbl_current = QLabel("ACTUAL")
            lbl_current.setStyleSheet(f"""
                color: {CURRENT_TEXT};
                font-size: 8px;
                font-weight: 900;
                letter-spacing: 1px;
            """)

            month_row.addWidget(lbl_current)

        lbl_count = QLabel(
            f"{count} "
            f"{'evento' if count == 1 else 'eventos'}"
        )

        lbl_count.setStyleSheet(f"""
            color: {
                TEXT_PRI
                if count
                else TEXT_MUT
            };
            font-size: 18px;
            font-weight: 900;
        """)

        lbl_action = QLabel("Ver mes  →")
        lbl_action.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 9px;
            font-weight: 900;
            letter-spacing: 1px;
        """)

        layout.addLayout(month_row)
        layout.addWidget(lbl_count)
        layout.addStretch()
        layout.addWidget(lbl_action)

        def click(event):
            self.parent_view.switch_to_month(
                self.year,
                month
            )

        card.mousePressEvent = click

        return card

    def _clear_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

            child_layout = item.layout()

            if child_layout is not None:
                self._clear_layout(child_layout)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

            child_layout = item.layout()

            if child_layout is not None:
                self._clear_layout(child_layout)

# ─────────────────────────────────────────────────────────────
# Class Detail Dialog Premium
# ─────────────────────────────────────────────────────────────
class ClassDetailDialog(QDialog):
    def __init__(self, data, accent="#E11D48", parent=None):
        super().__init__(parent)

        self.data = data
        self.accent = data.get("color") or accent
        self.schedule_id = int(data.get("id") or 0)
        self.action = None  # "edit" | "delete" | "attendance" | None

        self.setWindowTitle("Detalle de clase")
        self.setFixedSize(500, 445)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setStyleSheet("""
            QDialog {
                background: transparent;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.card = QFrame()
        self.card.setObjectName("DetailCard")
        self.card.setStyleSheet("""
            QFrame#DetailCard {
                background-color: #0F0F0F;
                border: 1px solid #252525;
                border-radius: 14px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(26)
        shadow.setColor(QColor(0, 0, 0, 210))
        shadow.setOffset(0, 8)
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(82)
        header.setStyleSheet("""
            QFrame {
                background-color: #0D0D0D;
                border-top-left-radius: 14px;
                border-top-right-radius: 14px;
                border-bottom: 1px solid #202020;
            }
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 18, 0)
        header_layout.setSpacing(0)

        accent_bar = QFrame()
        accent_bar.setFixedWidth(7)
        accent_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {self.accent};
                border-top-left-radius: 14px;
            }}
        """)

        header_content = QHBoxLayout()
        header_content.setContentsMargins(24, 0, 0, 0)
        header_content.setSpacing(10)

        title = QLabel("Ficha Informativa")
        title.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 19px;
            font-weight: 900;
        """)

        btn_close = QPushButton()
        btn_close.setFixedSize(34, 34)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #1A1A1A;
                border-radius: 8px;
            }}
        """)
        close_icon = IconLabel("close", size=18, color=TEXT_SEC)
        btn_close.setLayout(QHBoxLayout())
        btn_close.layout().setContentsMargins(0, 0, 0, 0)
        btn_close.layout().addWidget(close_icon)
        btn_close.clicked.connect(self.reject)

        header_content.addWidget(title)
        header_content.addStretch()
        header_content.addWidget(btn_close)

        header_layout.addWidget(accent_bar)
        header_layout.addLayout(header_content, 1)

        card_layout.addWidget(header)

        # Body
        body = QFrame()
        body.setStyleSheet("""
            QFrame {
                background-color: #0F0F0F;
                border: none;
            }
        """)

        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(26, 24, 26, 24)
        body_layout.setSpacing(22)

        body_layout.addLayout(
            self._info_block(
                "ACTIVIDAD DEPORTIVA",
                self.data.get("name") or "Clase",
                big=True
            )
        )

        info_row = QHBoxLayout()
        info_row.setSpacing(34)

        info_row.addLayout(
            self._info_block(
                "INTERVALO HORARIO",
                f"{self.data.get('start_time', '—')} - {self.data.get('end_time', '—')}"
            ),
            1
        )

        info_row.addLayout(
            self._info_block(
                "SENSEI / KRU",
                self.data.get("instructor") or "Sin instructor"
            ),
            1
        )

        body_layout.addLayout(info_row)

        body_layout.addLayout(
            self._info_block(
                "ARTE MARCIAL",
                self.data.get("martial_art") or "Sin arte"
            )
        )

        location = self.data.get("location") or "Sin ubicación"
        location_block = QVBoxLayout()
        location_block.setSpacing(8)

        lbl_location_key = QLabel("DOJO ASIGNADO")
        lbl_location_key.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 10px;
            font-weight: 900;
            letter-spacing: 1.2px;
        """)

        location_val_row = QHBoxLayout()
        location_val_row.setContentsMargins(0, 0, 0, 0)
        location_val_row.setSpacing(4)
        location_val_row.addWidget(IconLabel("pin", 14, self.accent))
        lbl_location_value = QLabel(location)
        lbl_location_value.setWordWrap(True)
        lbl_location_value.setStyleSheet(f"""
            color: {self.accent};
            font-size: 14px;
            font-weight: 900;
        """)
        location_val_row.addWidget(lbl_location_value)
        location_val_row.addStretch()

        location_block.addWidget(lbl_location_key)
        location_block.addLayout(location_val_row)

        body_layout.addLayout(location_block)
        body_layout.addStretch()

        card_layout.addWidget(body, 1)

        # Footer
        footer = QFrame()
        footer.setFixedHeight(86)
        footer.setStyleSheet("""
            QFrame {
                background-color: #0D0D0D;
                border-top: 1px solid #202020;
                border-bottom-left-radius: 14px;
                border-bottom-right-radius: 14px;
            }
        """)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 16, 20, 16)
        footer_layout.setSpacing(10)

        btn_delete = QPushButton("Eliminar")
        btn_delete.setFixedHeight(40)
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: rgba(120, 10, 20, 0.18);
                color: #FF6B6B;
                border: 1px solid #7A1A1A;
                border-radius: 9px;
                font-size: 13px;
                font-weight: 900;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: rgba(120, 10, 20, 0.34);
                border-color: #FF4444;
                color: #FF8888;
            }
        """)
        btn_delete.clicked.connect(self._delete)

        btn_attendance = QPushButton("Asistencia")
        btn_attendance.setFixedHeight(40)
        btn_attendance.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_attendance.setStyleSheet("""
            QPushButton {
                background-color: rgba(16, 185, 129, 0.10);
                color: #10B981;
                border: 1px solid rgba(16, 185, 129, 0.25);
                border-radius: 9px;
                font-size: 13px;
                font-weight: 900;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #10B981;
                color: white;
            }
        """)
        btn_attendance.clicked.connect(self._attendance)

        btn_edit = QPushButton("Editar")
        btn_edit.setFixedHeight(40)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255,255,255,0.04);
                color: {self.accent};
                border: 1px solid {self.accent};
                border-radius: 9px;
                font-size: 13px;
                font-weight: 900;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background-color: rgba(255,255,255,0.08);
            }}
        """)
        btn_edit.clicked.connect(self._edit)

        btn_ok = QPushButton("Aceptar")
        btn_ok.setFixedHeight(40)
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #242424;
                color: #FAFAFA;
                border: none;
                border-radius: 9px;
                font-size: 14px;
                font-weight: 900;
                padding: 0 18px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        btn_ok.clicked.connect(self.accept)

        footer_layout.addWidget(btn_delete)
        footer_layout.addWidget(btn_attendance)
        footer_layout.addStretch()
        footer_layout.addWidget(btn_edit)
        footer_layout.addWidget(btn_ok)

        card_layout.addWidget(footer)

        root.addWidget(self.card)

    def _info_block(self, key, value, big=False):
        layout = QVBoxLayout()
        layout.setSpacing(8)

        lbl_key = QLabel(str(key).upper())
        lbl_key.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 10px;
            font-weight: 900;
            letter-spacing: 1.2px;
        """)

        lbl_value = QLabel(str(value))
        lbl_value.setWordWrap(True)

        if big:
            lbl_value.setStyleSheet(f"""
                color: {TEXT_PRI};
                font-size: 21px;
                font-weight: 900;
            """)
        else:
            lbl_value.setStyleSheet(f"""
                color: {TEXT_SEC};
                font-size: 14px;
                font-weight: 900;
            """)

        layout.addWidget(lbl_key)
        layout.addWidget(lbl_value)

        return layout

    def _edit(self):
        self.action = "edit"
        self.accept()

    def _delete(self):
        self.action = "delete"
        self.accept()

    def _attendance(self):
        self.action = "attendance"
        self.accept()


# ─────────────────────────────────────────────────────────────
# Attendance Dialog Premium
# ─────────────────────────────────────────────────────────────
class AttendanceDialog(QDialog):
    def __init__(
        self,
        class_data,
        students,
        present_student_ids,
        instructors=None,
        current_instructor_id=None,
        guest_count=0,
        guest_names="",
        class_status="completed",
        is_admin=False,
        current_user_id=None,
        student_allowances=None,
        accent="#10B981",
        parent=None
    ):
        super().__init__(parent)

        self.class_data = class_data
        self.students = students or []
        self.present_student_ids = set(present_student_ids or [])
        self.selected_ids = set(self.present_student_ids)

        self.initial_guest_count = int(guest_count or 0)
        self.initial_guest_names = guest_names or ""

        self.instructors = instructors or []
        self.current_instructor_id = current_instructor_id

        self.is_admin = bool(is_admin)
        self.current_user_id = current_user_id
        self.initial_class_status = class_status or "completed"

        self.admin_overrides = {}
        self.student_allowances = student_allowances or {}
        self.student_rows = {}

        self.setWindowTitle("Control de asistencia")
        self.setFixedSize(500, 720)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setStyleSheet("""
            QDialog {
                background: transparent;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("AttendanceCard")
        card.setStyleSheet(f"""
            QFrame#AttendanceCard {{
                background-color: #0F0F0F;
                border: 1px solid #252525;
                border-top: 4px solid {accent};
                border-radius: 14px;
            }}

            QFrame#AttendanceCard QLabel {{
                background: transparent;
                border: none;
            }}

            QFrame#AttendanceCard QCheckBox {{
                background: transparent;
                border: none;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(26)
        shadow.setColor(QColor(0, 0, 0, 220))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()

        title = QLabel("Control de Asistencia")
        title.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 17px;
            font-weight: 900;
        """)

        btn_close = QPushButton()
        btn_close.setFixedSize(30, 30)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #1A1A1A;
                border-radius: 6px;
            }}
        """)
        close_icon = IconLabel("close", size=16, color="#737373")
        btn_close.setLayout(QHBoxLayout())
        btn_close.layout().setContentsMargins(0, 0, 0, 0)
        btn_close.layout().addWidget(close_icon)
        btn_close.clicked.connect(self.reject)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(btn_close)

        layout.addLayout(header)

        # Info clase
        info_row = QHBoxLayout()
        info_row.setContentsMargins(0, 0, 0, 0)
        info_row.setSpacing(6)

        icon_martial = IconLabel("martial-art", size=14, color=TEXT_SEC)
        lbl_name = QLabel(class_data.get('name', 'Clase'))
        lbl_name.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 11px;
            font-weight: 800;
        """)

        icon_user = IconLabel("instructor", size=14, color=TEXT_SEC)
        lbl_instructor = QLabel(class_data.get('instructor', 'Sin instructor'))
        lbl_instructor.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 11px;
            font-weight: 800;
        """)

        info_row.addWidget(icon_martial)
        info_row.addWidget(lbl_name)
        info_row.addSpacing(12)
        info_row.addWidget(icon_user)
        info_row.addWidget(lbl_instructor)
        info_row.addStretch()

        layout.addLayout(info_row)

        # ── Estado de la clase ──
        lbl_status = QLabel("ESTADO DE LA CLASE")
        lbl_status.setStyleSheet("""
            QLabel {
                color: #525252;
                background: transparent;
                border: none;
                font-size: 9px;
                font-weight: 900;
                letter-spacing: 1.2px;
            }
        """)
        layout.addWidget(lbl_status)

        self.cmb_class_status = QComboBox()
        self.cmb_class_status.setFixedHeight(36)

        self.cmb_class_status.addItem("Dictada", "completed")
        self.cmb_class_status.addItem("Cancelada", "cancelled")
        self.cmb_class_status.addItem("Inactiva", "inactive")

        self.cmb_class_status.setStyleSheet("""
            QComboBox {
                background-color: #121212;
                color: #FAFAFA;
                border: 1px solid #1F1F1F;
                border-radius: 7px;
                padding: 0 10px;
                font-size: 12px;
                font-weight: 700;
            }

            QComboBox:focus {
                border-color: #10B981;
            }

            QComboBox QAbstractItemView {
                background-color: #121212;
                color: #FAFAFA;
                selection-background-color: #10B981;
                border: 1px solid #1F1F1F;
            }
        """)

        status_map = {
            "scheduled": "completed",
            "active": "completed",
            "dictada": "completed",
            "completed": "completed",
            "cancelled": "cancelled",
            "canceled": "cancelled",
            "cancelada": "cancelled",
            "inactive": "inactive",
            "inactiva": "inactive",
        }

        normalized_status = status_map.get(
            str(self.initial_class_status).strip().lower(),
            "completed"
        )

        status_index = self.cmb_class_status.findData(normalized_status)

        if status_index >= 0:
            self.cmb_class_status.setCurrentIndex(status_index)

        layout.addWidget(self.cmb_class_status)

        # ── Instructor ──
        lbl_ins = QLabel("INSTRUCTOR QUE DICTÓ LA CLASE")
        lbl_ins.setStyleSheet("""
            QLabel {
                color: #525252;
                background: transparent;
                border: none;
                font-size: 9px;
                font-weight: 900;
                letter-spacing: 1.2px;
            }
        """)
        layout.addWidget(lbl_ins)

        self.cmb_instructor = QComboBox()
        self.cmb_instructor.setFixedHeight(34)
        self.cmb_instructor.setStyleSheet("""
            QComboBox {
                background-color: #121212;
                color: #FAFAFA;
                border: 1px solid #1F1F1F;
                border-radius: 7px;
                padding: 0 10px;
                font-size: 12px;
                font-weight: 700;
            }
            QComboBox:focus {
                border-color: #10B981;
            }
            QComboBox QAbstractItemView {
                background-color: #121212;
                color: #FAFAFA;
                selection-background-color: #10B981;
                border: 1px solid #1F1F1F;
            }
        """)

        self.cmb_instructor.addItem("Seleccionar instructor...", None)

        for ins_id, ins_name in self.instructors:
            self.cmb_instructor.addItem(ins_name, ins_id)

        if self.current_instructor_id is not None:
            idx = self.cmb_instructor.findData(self.current_instructor_id)
            if idx >= 0:
                self.cmb_instructor.setCurrentIndex(idx)

        layout.addWidget(self.cmb_instructor)

        self.lbl_stats = QLabel("")
        self.lbl_stats.setStyleSheet("""
            color: #10B981;
            font-size: 11px;
            font-weight: 900;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(self.lbl_stats)

        # ── Invitados ──
        self.guest_box = QFrame()
        guest_box = self.guest_box
        guest_box.setObjectName("GuestBox")
        guest_box.setStyleSheet("""
            QFrame#GuestBox {
                background-color: #0B0B0B;
                border: 1px solid #202020;
                border-radius: 10px;
            }

            QFrame#GuestBox QLabel {
                background: transparent;
                border: none;
            }

            QFrame#GuestBox QSpinBox {
                background-color: #121212;
                color: #FAFAFA;
                border: 1px solid #1F1F1F;
                border-radius: 7px;
                padding: 0 10px;
                font-size: 12px;
                font-weight: 800;
            }

            QFrame#GuestBox QSpinBox:focus {
                border-color: #10B981;
            }

            QFrame#GuestBox QTextEdit {
                background-color: #121212;
                color: #FAFAFA;
                border: 1px solid #1F1F1F;
                border-radius: 7px;
                padding: 8px 10px;
                font-size: 12px;
                font-weight: 700;
            }

            QFrame#GuestBox QTextEdit:focus {
                border-color: #10B981;
            }
        """)

        guest_layout = QVBoxLayout(guest_box)
        guest_layout.setContentsMargins(12, 10, 12, 10)
        guest_layout.setSpacing(8)

        guest_title = QLabel("INVITADOS DE PRUEBA")
        guest_title.setStyleSheet("""
            QLabel {
                color: #525252;
                background: transparent;
                border: none;
                font-size: 9px;
                font-weight: 900;
                letter-spacing: 1.2px;
            }
        """)
        guest_layout.addWidget(guest_title)

        guest_row = QHBoxLayout()
        guest_row.setSpacing(10)

        guest_count_label = QLabel("Cantidad")
        guest_count_label.setStyleSheet("""
            QLabel {
                color: #A3A3A3;
                background: transparent;
                border: none;
                font-size: 11px;
                font-weight: 800;
            }
        """)

        self.spin_guest_count = QSpinBox()
        self.spin_guest_count.setRange(0, 99)
        self.spin_guest_count.setValue(self.initial_guest_count)
        self.spin_guest_count.setFixedHeight(34)
        self.spin_guest_count.setStyleSheet("""
            QSpinBox {
                background-color: #121212;
                color: #FAFAFA;
                border: 1px solid #1F1F1F;
                border-radius: 7px;
                padding: 0 10px;
                font-size: 12px;
                font-weight: 800;
            }
            QSpinBox:focus {
                border-color: #10B981;
            }
        """)
        self.spin_guest_count.valueChanged.connect(self._update_stats)

        guest_row.addWidget(guest_count_label)
        guest_row.addWidget(self.spin_guest_count)
        guest_row.addStretch()

        guest_layout.addLayout(guest_row)

        self.input_guest_names = QTextEdit()
        self.input_guest_names.setPlaceholderText(
            "Nombres de invitados. Ej: Carlos Pérez, Ana Gómez..."
        )
        self.input_guest_names.setPlainText(self.initial_guest_names)
        self.input_guest_names.setFixedHeight(70)
        self.input_guest_names.setStyleSheet("""
            QTextEdit {
                background-color: #121212;
                color: #FAFAFA;
                border: 1px solid #1F1F1F;
                border-radius: 7px;
                padding: 8px 10px;
                font-size: 12px;
                font-weight: 700;
            }
            QTextEdit:focus {
                border-color: #10B981;
            }
        """)

        guest_layout.addWidget(self.input_guest_names)

        layout.addWidget(guest_box)

        # ── Scroll de estudiantes ──
        self.attendance_scroll = QScrollArea()
        scroll = self.attendance_scroll
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #080808;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #222222;
                border-radius: 4px;
            }
        """)

        scroll.viewport().setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True
        )

        scroll.viewport().setStyleSheet("""
            background-color: #0F0F0F;
            border: none;
        """)

        content = QWidget()
        content.setObjectName("AttendanceContent")
        content.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        content.setStyleSheet("""
            QWidget#AttendanceContent {
                background-color: #0F0F0F;
                border: none;
            }
        """)

        self.list_layout = QVBoxLayout(content)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(7)

        self.checkboxes = {}

        for student_id, student_name, document in self.students:
            row = QFrame()
            row.setObjectName("AttendanceRow")
            row.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            row.setAutoFillBackground(False)

            row.setStyleSheet("""
                QFrame#AttendanceRow {
                    background-color: #0E0E0E;
                    border: 1px solid #1F1F1F;
                    border-radius: 9px;
                }

                QFrame#AttendanceRow:hover {
                    background-color: #121212;
                    border: 1px solid #2A2A2A;
                }

                QFrame#AttendanceRow QLabel {
                    background-color: transparent;
                    border: none;
                }

                QFrame#AttendanceRow QCheckBox {
                    background-color: transparent;
                    border: none;
                }

                QFrame#AttendanceRow:disabled {
                    background-color: #0A0A0A;
                    border-color: #171717;
                }

                QFrame#AttendanceRow:disabled QLabel {
                    color: #3F3F3F;
                }
            """)

            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 9, 12, 9)
            row_layout.setSpacing(8)

            name_col = QVBoxLayout()
            name_col.setContentsMargins(0, 0, 0, 0)
            name_col.setSpacing(3)

            lbl_name = QLabel(student_name)
            lbl_name.setWordWrap(True)
            lbl_name.setStyleSheet(f"""
                QLabel {{
                    background-color: transparent;
                    border: none;
                    color: {TEXT_PRI};
                    font-size: 12px;
                    font-weight: 800;
                }}
            """)

            lbl_doc = QLabel(str(document or ""))
            lbl_doc.setStyleSheet(f"""
                QLabel {{
                    background-color: transparent;
                    border: none;
                    color: {TEXT_MUT};
                    font-size: 10px;
                    font-weight: 700;
                }}
            """)

            name_col.addWidget(lbl_name)

            if document:
                name_col.addWidget(lbl_doc)

            # ── Clases restantes ──
            allowance = self.student_allowances.get(
                student_id,
                {
                    "plan_name": "Sin mensualidad activa",
                    "weekly_limit": 0,
                    "used_classes": 0,
                    "remaining": 0,
                    "is_unlimited": False,
                    "has_membership": False,
                }
            )

            is_unlimited = allowance.get("is_unlimited", False)
            remaining = allowance.get("remaining")
            has_membership = allowance.get("has_membership", False)

            COLOR_REMAINING = "#3B82F6"

            if is_unlimited:
                allowance_text = "Ilimitado"
                allowance_color = "#10B981"
            elif not has_membership:
                allowance_text = "Sin mensualidad"
                allowance_color = "#EF4444"
            else:
                allowance_text = f"{remaining} clases restantes"
                allowance_color = COLOR_REMAINING

            lbl_allowance = QLabel(allowance_text)
            lbl_allowance.setStyleSheet(f"""
                QLabel {{
                    background-color: transparent;
                    border: none;
                    color: {allowance_color};
                    font-size: 10px;
                    font-weight: 900;
                }}
            """)

            name_col.addWidget(lbl_allowance)

            # ── Checkbox ──
            chk = QCheckBox()
            chk.setCursor(Qt.CursorShape.PointingHandCursor)
            chk.setChecked(student_id in self.selected_ids)
            chk.setStyleSheet("""
                QCheckBox {
                    background: transparent;
                    border: none;
                }

                QCheckBox::indicator {
                    width: 19px;
                    height: 19px;
                    border: 2px solid #2A2A2A;
                    border-radius: 5px;
                    background-color: #121212;
                }

                QCheckBox::indicator:hover {
                    border: 2px solid #10B981;
                }

                QCheckBox::indicator:checked {
                    border: 2px solid #10B981;
                    background-color: #10B981;
                }
            """)
            chk.stateChanged.connect(
                lambda state, sid=student_id: self._on_check_changed(sid, state)
            )

            self.checkboxes[student_id] = chk

            # ── Bloquear si no hay cupos ──
            already_present = student_id in self.present_student_ids

            can_mark_normally = (
                is_unlimited
                or (
                    has_membership
                    and remaining is not None
                    and remaining > 0
                )
                or already_present
            )

            chk.setEnabled(can_mark_normally)

            self.student_allowances.setdefault(student_id, {})
            self.student_allowances[student_id][
                "can_mark_normally"
            ] = can_mark_normally

            row_layout.addLayout(name_col, 1)
            row_layout.addWidget(chk, 0, Qt.AlignmentFlag.AlignCenter)

            # ── Botón de excepción admin ──
            if self.is_admin and not can_mark_normally:
                btn_override = QPushButton()
                btn_override.setFixedSize(28, 28)
                btn_override.setCursor(
                    Qt.CursorShape.PointingHandCursor
                )
                btn_override.setToolTip(
                    "Autorizar asistencia por acuerdo administrativo"
                )

                btn_override.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: 1px solid #292929;
                        border-radius: 7px;
                    }

                    QPushButton:hover {
                        background-color: rgba(245, 158, 11, 0.10);
                        border-color: #F59E0B;
                    }

                    QPushButton * {
                        background: transparent;
                        border: none;
                    }
                """)

                override_layout = QHBoxLayout(btn_override)
                override_layout.setContentsMargins(0, 0, 0, 0)

                override_layout.addWidget(
                    IconLabel("key", 13, "#F59E0B"),
                    0,
                    Qt.AlignmentFlag.AlignCenter
                )

                btn_override.clicked.connect(
                    lambda _, sid=student_id, checkbox=chk:
                        self._request_admin_override(
                            sid,
                            checkbox
                        )
                )

                row_layout.addWidget(btn_override)

            self.student_rows[student_id] = row
            self.list_layout.addWidget(row)

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        self._update_stats()

        self.cmb_class_status.currentIndexChanged.connect(
            self._apply_class_status
        )

        self._apply_class_status()

        # Buttons
        actions = QHBoxLayout()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #A3A3A3;
                border: none;
                font-size: 12px;
                font-weight: 800;
            }
            QPushButton:hover {
                color: white;
            }
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Confirmar Asistencias")
        btn_save.setFixedHeight(38)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 900;
                padding: 0 18px;
            }
            QPushButton:hover {
                background-color: #34D399;
            }
        """)
        btn_save.clicked.connect(self.accept)

        actions.addWidget(btn_cancel)
        actions.addStretch()
        actions.addWidget(btn_save)

        layout.addLayout(actions)

        root.addWidget(card)

    def _on_check_changed(self, student_id, state):
        if state == Qt.CheckState.Checked.value:
            self.selected_ids.add(student_id)
        else:
            self.selected_ids.discard(student_id)

        self._update_stats()

    def _update_stats(self):
        total = len(self.students)
        present = len(self.selected_ids)
        guests = self.spin_guest_count.value() if hasattr(self, "spin_guest_count") else 0
        total_people = present + guests
        pct = int((present / total) * 100) if total else 0

        self.lbl_stats.setText(
            f"Presentes: {present} / {total}  •  Invitados: {guests}  •  Total clase: {total_people}  •  {pct}%"
        )

    def get_present_student_ids(self):
        return set(self.selected_ids)

    def get_guest_count(self):
        return self.spin_guest_count.value()

    def get_guest_names(self):
        return self.input_guest_names.toPlainText().strip()

    def get_selected_instructor_id(self):
        return self.cmb_instructor.currentData()

    def get_class_status(self):
        return self.cmb_class_status.currentData()

    def get_admin_overrides(self):
        return dict(self.admin_overrides)

    def _apply_class_status(self):
        status = self.cmb_class_status.currentData()
        enabled = status == "completed"

        self.cmb_instructor.setEnabled(enabled)
        self.guest_box.setEnabled(enabled)
        self.attendance_scroll.setEnabled(enabled)

        for row in self.student_rows.values():
            row.setEnabled(enabled)

        for checkbox in self.checkboxes.values():
            checkbox.setEnabled(enabled)

        if not enabled:
            self.spin_guest_count.blockSignals(True)
            self.spin_guest_count.setValue(0)
            self.spin_guest_count.blockSignals(False)

            self.input_guest_names.clear()

            self.selected_ids.clear()

            for checkbox in self.checkboxes.values():
                checkbox.blockSignals(True)
                checkbox.setChecked(False)
                checkbox.blockSignals(False)

            self.lbl_stats.setText(
                "La asistencia está deshabilitada porque la clase no fue dictada."
            )
            self.lbl_stats.setStyleSheet("""
                color: #525252;
                font-size: 11px;
                font-weight: 800;
            """)
        else:
            self.lbl_stats.setStyleSheet("""
                color: #10B981;
                font-size: 11px;
                font-weight: 900;
                letter-spacing: 0.5px;
            """)

            self._update_stats()

    def _request_admin_override(
        self,
        student_id,
        checkbox
    ):
        if not self.is_admin:
            return

        reason, accepted = QInputDialog.getMultiLineText(
            self,
            "Autorización administrativa",
            "Explica brevemente el acuerdo que permite registrar "
            "la asistencia sin cupos disponibles:"
        )

        reason = reason.strip()

        if not accepted or not reason:
            return

        self.admin_overrides[student_id] = reason

        checkbox.setEnabled(True)
        checkbox.setChecked(True)

        self.selected_ids.add(student_id)
        self._update_stats()


# ─────────────────────────────────────────────────────────────
# Main Classes View
# ─────────────────────────────────────────────────────────────
class ClassesView(QWidget):
    def __init__(self, current_user_id=None):
        super().__init__()

        self.current_user_id = current_user_id

        self.classes_repo = ClassesRepository()
        self.events_repo = EventsRepository()

        self.current_date = date.today()
        self.current_year = date.today().year
        self.current_month = date.today().month

        self.accent_color  = "#E11D48"
        self.accent_hover  = "#F43F5E"
        self.accent_active = "#BE123C"

        self._animations = []

        self._build_ui()
        self.reload_current_view()

    # ─────────────────────────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(f"background-color: {BG_MAIN};")

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(0)

        # Shell principal que se desenfoca
        self.content_shell = QFrame()
        self.content_shell.setStyleSheet("""
            QFrame {
                background-color: #090909;
                border: 1px solid #1F1F1F;
                border-radius: 18px;
            }
        """)

        shell_layout = QVBoxLayout(self.content_shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        # Header premium
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: rgba(12, 12, 12, 230);
                border: none;
                border-bottom: 1px solid #1A1A1A;
                border-top-left-radius: 18px;
                border-top-right-radius: 18px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)

        hl = QHBoxLayout(header)
        hl.setContentsMargins(26, 24, 26, 22)
        hl.setSpacing(14)

        title_col = QVBoxLayout()
        title_col.setSpacing(4)

        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        title_icon = IconLabel("event", 22, "#E11D48")
        self.lbl_title = QLabel("Clases y Eventos")
        self.lbl_title.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 25px;
            font-weight: 900;
            background: transparent; border: none;
        """)
        title_row.addWidget(title_icon)
        title_row.addWidget(self.lbl_title)

        subtitle = QLabel("Gestiona horarios, registra asistencia y organiza los eventos del dojo.")
        subtitle.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 12px;
        """)

        title_col.addLayout(title_row)
        title_col.addWidget(subtitle)

        self.btn_new_event = QPushButton()
        self.btn_new_event.setFixedHeight(40)
        self.btn_new_event.setMinimumWidth(158)
        self.btn_new_event.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_event.setStyleSheet(
            self._secondary_button_style() +
            " QPushButton * { background: transparent; border: none; }"
        )
        _ev_inner = QHBoxLayout(self.btn_new_event)
        _ev_inner.setContentsMargins(14, 0, 14, 0)
        _ev_inner.setSpacing(7)
        _ev_ico = IconLabel("calendar", 15, TEXT_SEC)
        _ev_lbl = QLabel("Nuevo Evento")
        _ev_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-weight: 800;")
        _ev_inner.addWidget(_ev_ico)
        _ev_inner.addWidget(_ev_lbl)
        self.btn_new_event.clicked.connect(lambda: self.open_event_form())

        self.btn_new_class = QPushButton("＋  Nueva Clase")
        self.btn_new_class.setFixedHeight(40)
        self.btn_new_class.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_class.setStyleSheet(self._primary_button_style())
        self.btn_new_class.clicked.connect(lambda: self.open_class_form())

        hl.addLayout(title_col, 1)
        hl.addWidget(self.btn_new_event)
        hl.addWidget(self.btn_new_class)

        shell_layout.addWidget(header)

        self.header_line = QFrame()
        self.header_line.setFixedHeight(2)
        self.header_line.setStyleSheet(self._gradient_line_style())
        shell_layout.addWidget(self.header_line)

        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background-color: rgba(8, 8, 8, 230);
                border: none;
                border-bottom: 1px solid #141414;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)

        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(24, 14, 24, 14)
        tl.setSpacing(8)

        self.btn_prev = QPushButton("‹")
        self.btn_today = QPushButton("Hoy")
        self.btn_next = QPushButton("›")

        for btn in [self.btn_prev, self.btn_today, self.btn_next]:
            btn.setFixedHeight(36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self._nav_button_style())

        self.btn_prev.setFixedWidth(42)
        self.btn_next.setFixedWidth(42)

        self.btn_prev.clicked.connect(self.go_prev)
        self.btn_today.clicked.connect(self.go_today)
        self.btn_next.clicked.connect(self.go_next)

        self.lbl_range = QLabel("Cargando...")
        self.lbl_range.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 14px;
            font-weight: 900;
            padding-left: 12px;
        """)

        lbl_view = QLabel("VISUALIZAR EN:")
        lbl_view.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 10px;
            font-weight: 900;
            letter-spacing: 1px;
        """)

        self.cmb_view = QComboBox()
        self.cmb_view.setFixedHeight(36)
        self.cmb_view.setMinimumWidth(170)
        self.cmb_view.addItem("Semana (Clases)", 0)
        self.cmb_view.addItem("Mes (Eventos)", 1)
        self.cmb_view.addItem("Año (Resumen)", 2)
        self.cmb_view.setStyleSheet(self._combo_style())
        self.cmb_view.currentIndexChanged.connect(self._switch_view)

        tl.addWidget(self.btn_prev)
        tl.addWidget(self.btn_today)
        tl.addWidget(self.btn_next)
        tl.addWidget(self.lbl_range)
        tl.addStretch()
        tl.addWidget(lbl_view)
        tl.addWidget(self.cmb_view)

        shell_layout.addWidget(toolbar)

        # Stack
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #070707; border: none;")

        # Weekly scroll
        weekly_scroll = QScrollArea()
        weekly_scroll.setWidgetResizable(True)
        weekly_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #070707;
            }
            QScrollBar:vertical {
                background: #080808;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #222222;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #333333;
            }
            QScrollBar:horizontal {
                background: #080808;
                height: 8px;
            }
            QScrollBar::handle:horizontal {
                background: #222222;
                border-radius: 4px;
            }
        """)

        self.week_view = WeeklyCalendarWidget(self.classes_repo, self)
        weekly_scroll.setWidget(self.week_view)

        self.month_view = MonthlyEventsWidget(self.events_repo, self)
        self.year_view = YearlySummaryWidget(self.events_repo, self)

        self.stack.addWidget(weekly_scroll)
        self.stack.addWidget(self.month_view)
        self.stack.addWidget(self.year_view)

        shell_layout.addWidget(self.stack, 1)

        root.addWidget(self.content_shell, 1)

        # Overlay glass
        self.glass = GlassOverlay(self)
        self.glass.raise_()

        # Toast area
        self.toast_layer = QWidget(self)
        self.toast_layer.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.toast_layer.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.toast_layer.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.toast_layer.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.toast_layer.setAutoFillBackground(False)
        self.toast_layer.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
        """)

        self.toast_layout = QVBoxLayout(self.toast_layer)
        self.toast_layout.setContentsMargins(0, 0, 0, 0)
        self.toast_layout.setSpacing(8)
        self.toast_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self.toast_layout.addStretch()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.glass.setGeometry(self.rect())

        toast_w = 380
        toast_h = 260
        self.toast_layer.setGeometry(
            self.width() - toast_w - 24,
            self.height() - toast_h - 24,
            toast_w,
            toast_h
        )
        self.toast_layer.raise_()


    # ─────────────────────────────────────────────────────────────
    # Reload
    # ─────────────────────────────────────────────────────────────
    def reload_current_view(self):
        index = self.stack.currentIndex()

        if index == 0:
            self.lbl_range.setText(self._week_label())
            self.week_view.set_week_start(self._week_start())
            self.week_view.load_data({})

        elif index == 1:
            self.lbl_range.setText(f"{self.current_month:02d}/{self.current_year}")
            self.month_view.load_month(self.current_year, self.current_month)

        elif index == 2:
            self.lbl_range.setText(f"Gestión Anual {self.current_year}")
            self.year_view.load_year(self.current_year)

    def _switch_view(self):
        self.stack.setCurrentIndex(self.cmb_view.currentData())
        self._animate_stack()
        self.reload_current_view()

    def _animate_stack(self):
        effect = QGraphicsOpacityEffect(self.stack)
        self.stack.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(320)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(lambda: self.stack.setGraphicsEffect(None))

        self._animations.append(anim)
        anim.start()

    # ─────────────────────────────────────────────────────────────
    # Navigation
    # ─────────────────────────────────────────────────────────────
    def go_today(self):
        today = date.today()
        self.current_date = today
        self.current_month = today.month
        self.current_year = today.year
        self.reload_current_view()

    def go_prev(self):
        index = self.stack.currentIndex()

        if index == 0:
            self.current_date -= timedelta(days=7)
        elif index == 1:
            if self.current_month == 1:
                self.current_month = 12
                self.current_year -= 1
            else:
                self.current_month -= 1
        elif index == 2:
            self.current_year -= 1

        self.reload_current_view()

    def go_next(self):
        index = self.stack.currentIndex()

        if index == 0:
            self.current_date += timedelta(days=7)
        elif index == 1:
            if self.current_month == 12:
                self.current_month = 1
                self.current_year += 1
            else:
                self.current_month += 1
        elif index == 2:
            self.current_year += 1

        self.reload_current_view()

    def switch_to_month(self, year, month):
        self.current_year = year
        self.current_month = month
        self.cmb_view.setCurrentIndex(1)
        self.stack.setCurrentIndex(1)
        self.reload_current_view()

    def _week_start(self):
        return self.current_date - timedelta(days=self.current_date.weekday())

    def _week_label(self):
        start = self._week_start()
        end = start + timedelta(days=6)
        return f"{start.strftime('%d %b')} - {end.strftime('%d %b, %Y')}"

    # ─────────────────────────────────────────────────────────────
    # Forms
    # ─────────────────────────────────────────────────────────────
    def open_class_form(self, default_day=None, default_hour=None, schedule_id=None, blur_already_active=False):
        try:
            from views.class_form import ClassForm
        except Exception as e:
            self.show_toast(f"Falta crear views/class_form.py: {e}", "error")
            return

        if not blur_already_active:
            self._blur_on()

        dlg = ClassForm(
            self.classes_repo,
            schedule_id=schedule_id,
            default_day=default_day,
            default_hour=default_hour,
            parent=self
        )

        result = dlg.exec()

        if not blur_already_active:
            self._blur_off()

        if result == ClassForm.DialogCode.Accepted:
            self.reload_current_view()
            self.show_toast("Sincronizado: clase guardada", "success")

    def open_event_form(self, event_id=None, default_date=None, blur_already_active=False):
        try:
            from views.event_form import EventForm
        except Exception as e:
            self.show_toast(f"Falta crear views/event_form.py: {e}", "error")
            return

        if not blur_already_active:
            self._blur_on()

        dlg = EventForm(
            self.events_repo,
            event_id=event_id,
            default_date=default_date,
            parent=self
        )

        result = dlg.exec()

        if not blur_already_active:
            self._blur_off()

        if result == EventForm.DialogCode.Accepted:
            self.reload_current_view()
            self.show_toast("Evento sincronizado", "success")

    def open_class_detail(self, data):
        self._blur_on()

        dlg = ClassDetailDialog(data, self.accent_color, self)
        dlg.exec()

        action = dlg.action
        schedule_id = dlg.schedule_id

        if action == "delete":
            self._blur_off(force=True)
            self.delete_schedule_from_detail(schedule_id)

        elif action == "edit":
            self.open_class_form(schedule_id=schedule_id, blur_already_active=True)
            self._blur_off(force=True)

        elif action == "attendance":
            self.open_attendance_dialog(data, blur_already_active=True)
            self._blur_off(force=True)

        else:
            self._blur_off(force=True)

    def open_attendance_dialog(self, class_data, blur_already_active=False):
        try:
            schedule_id = int(class_data.get("id"))
            day_of_week = int(class_data.get("day_of_week"))
            class_date = self._week_start() + timedelta(days=day_of_week)

            class_id = self.classes_repo.get_or_create_class_instance(
                schedule_id=schedule_id,
                class_date=class_date,
                id_instructor=class_data.get("id_instructor"),
            )

            students = self.classes_repo.get_active_students_for_attendance()
            present_ids = self.classes_repo.get_attendance_student_ids(class_id)
            guest_info = self.classes_repo.get_class_guest_info(class_id)
            instructors = self.classes_repo.get_form_options().get("instructors", [])

        except Exception as e:
            self.show_toast(f"Error al preparar asistencia: {e}", "error")
            return

        student_ids = [
            student[0]
            for student in students
        ]

        try:
            student_allowances = (
                self.classes_repo.get_students_weekly_allowance(
                    student_ids,
                    class_date
                )
            )
        except Exception as e:
            student_allowances = {}
            self.show_toast(
                f"No se pudieron calcular los cupos semanales: {e}",
                "error"
            )

        current_user_id = getattr(
            self,
            "current_user_id",
            None
        )

        try:
            is_admin = self.classes_repo.is_admin_user(
                current_user_id
            )
        except Exception:
            is_admin = False

        if not blur_already_active:
            self._blur_on()

        dlg = AttendanceDialog(
            class_data=class_data,
            students=students,
            present_student_ids=present_ids,
            instructors=instructors,
            current_instructor_id=(
                guest_info.get("id_instructor")
                or class_data.get("id_instructor")
            ),
            guest_count=guest_info.get("guest_count", 0),
            guest_names=guest_info.get("guest_names", ""),
            class_status=guest_info.get("class_status", "completed"),
            student_allowances=student_allowances,
            is_admin=is_admin,
            current_user_id=current_user_id,
            accent="#10B981",
            parent=self
        )

        result = dlg.exec()

        if not blur_already_active:
            self._blur_off()

        if result == AttendanceDialog.DialogCode.Accepted:
            try:
                selected_ids = dlg.get_present_student_ids()
                guest_count = dlg.get_guest_count()
                guest_names = dlg.get_guest_names()
                selected_instructor_id = dlg.get_selected_instructor_id()
                class_status = dlg.get_class_status()
                admin_overrides = dlg.get_admin_overrides()

                if (
                    class_status == "completed"
                    and selected_instructor_id is None
                ):
                    self.show_toast(
                        "Selecciona el instructor que dictó la clase",
                        "warning"
                    )
                    return

                self.classes_repo.save_attendance(
                    class_id=class_id,
                    class_status=class_status,
                    instructor_id=selected_instructor_id,
                    present_student_ids=selected_ids,
                    guest_count=guest_count,
                    guest_names=guest_names,
                    admin_overrides=admin_overrides,
                    current_user_id=self.current_user_id,
                )

                total = len(students)
                present = len(selected_ids)
                pct = int((present / total) * 100) if total else 0

                self.reload_current_view()

                self.show_toast(
                    f"Asistencia guardada: {present}/{total} presentes + {guest_count} invitado(s)",
                    "success"
                )

            except Exception as e:
                self.show_toast(f"Error al guardar asistencia: {e}", "error")

    def delete_schedule_from_detail(self, schedule_id):
        dlg = QDialog(self)
        dlg.setWindowTitle("Confirmar")
        dlg.setFixedSize(360, 160)
        dlg.setStyleSheet(f"background: #111111; color: {TEXT_PRI};")
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        msg = QLabel("¿Eliminar esta clase del calendario?")
        msg.setStyleSheet(f"color: {TEXT_PRI}; font-size: 13px; font-weight: 600; border: none;")
        layout.addWidget(msg)
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setStyleSheet(f"background: transparent; color: {TEXT_SEC}; border: 1px solid #2A2A2A; border-radius: 8px; font-size: 12px;")
        btn_cancel.clicked.connect(dlg.reject)
        btn_ok = QPushButton("Eliminar")
        btn_ok.setFixedHeight(36)
        btn_ok.setStyleSheet(f"background: #E11D48; color: white; border: none; border-radius: 8px; font-size: 12px; font-weight: 800;")
        btn_ok.clicked.connect(dlg.accept)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            try:
                self.classes_repo.delete_schedule(schedule_id)
                self.reload_current_view()
                self.show_toast("Clase eliminada", "warning")
            except Exception as e:
                self.show_toast(f"No se pudo eliminar: {e}", "error")

    # ─────────────────────────────────────────────────────────────
    # Drag & Drop update
    # ─────────────────────────────────────────────────────────────
    def move_schedule_from_drop(self, schedule_id, target_day, target_hour):
        try:
            data = self.classes_repo.get_by_id(schedule_id)

            if not data:
                self.show_toast("No se encontró la clase", "error")
                return

            old_start = data.get("start_time")
            old_end = data.get("end_time")

            duration = self._duration_minutes(old_start, old_end)

            start_total = target_hour * 60
            end_total = start_total + duration

            data["day_of_week"] = target_day
            data["start_time"] = self._minutes_to_time(start_total)
            data["end_time"] = self._minutes_to_time(end_total)

            self.classes_repo.update_schedule(schedule_id, data)

            self.reload_current_view()
            self.show_toast(f'Clase "{data.get("name")}" reubicada con éxito', "success")

        except Exception as e:
            self.show_toast(f"No se pudo mover la clase: {e}", "error")

    def _duration_minutes(self, start_value, end_value):
        def to_minutes(v):
            if hasattr(v, "hour"):
                return (v.hour * 60) + v.minute

            parts = str(v)[:5].split(":")
            return (int(parts[0]) * 60) + int(parts[1])

        try:
            return max(30, to_minutes(end_value) - to_minutes(start_value))
        except Exception:
            return 90

    def _minutes_to_time(self, total):
        total = max(0, min(total, 23 * 60 + 59))
        return time(total // 60, total % 60)

    # ─────────────────────────────────────────────────────────────
    # Blur
    # ─────────────────────────────────────────────────────────────
    def _blur_on(self):
        depth = getattr(self, "_blur_depth", 0) + 1
        self._blur_depth = depth

        if depth > 1:
            return

        win = self.window()

        overlay = QWidget(win)
        overlay.setObjectName("fullBlurOverlay")
        overlay.resize(win.size())
        overlay.move(0, 0)
        overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        overlay.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        overlay.setStyleSheet("background-color: rgba(0,0,0,0);")
        overlay.show()
        overlay.raise_()

        self._full_overlay       = overlay
        self._full_overlay_alpha = 0

        self._blur_timer_in = QTimer(self)
        self._blur_timer_in.setInterval(10)

        def _step_in():
            self._full_overlay_alpha = min(160, self._full_overlay_alpha + 16)
            a = self._full_overlay_alpha
            if overlay and not overlay.isHidden():
                overlay.setStyleSheet(f"background-color: rgba(0,0,0,{a});")
            if a >= 160:
                self._blur_timer_in.stop()

        self._blur_timer_in.timeout.connect(_step_in)
        self._blur_timer_in.start()

        self.blur_effect = QGraphicsBlurEffect(self.content_shell)
        self.blur_effect.setBlurRadius(0)
        self.content_shell.setGraphicsEffect(self.blur_effect)
        self.blur_anim = QPropertyAnimation(self.blur_effect, b"blurRadius", self)
        self.blur_anim.setDuration(220)
        self.blur_anim.setStartValue(0)
        self.blur_anim.setEndValue(16)
        self.blur_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.blur_anim.start()

        try:
            central = win.centralWidget()
            if central and central is not self:
                self._central_blur = QGraphicsBlurEffect(central)
                self._central_blur.setBlurRadius(0)
                central.setGraphicsEffect(self._central_blur)
                self._central_blur_anim = QPropertyAnimation(self._central_blur, b"blurRadius", self)
                self._central_blur_anim.setDuration(220)
                self._central_blur_anim.setStartValue(0)
                self._central_blur_anim.setEndValue(16)
                self._central_blur_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                self._central_blur_anim.start()
        except Exception:
            pass

        self.glass.fade_in()

        self._blur_win_ref     = win
        self._orig_resize_blur = win.resizeEvent

        def _on_win_resize(ev):
            self._orig_resize_blur(ev)
            if overlay and not overlay.isHidden():
                overlay.resize(win.size())
            overlay.raise_()

        win.resizeEvent = _on_win_resize

    def _blur_off(self, force=False):
        if force:
            self._blur_depth = 0
        else:
            self._blur_depth = max(0, getattr(self, "_blur_depth", 0) - 1)

        if self._blur_depth > 0:
            return

        overlay = getattr(self, "_full_overlay", None)

        if getattr(self, "_blur_timer_in", None):
            self._blur_timer_in.stop()

        if overlay:
            self._full_overlay_alpha_out = getattr(self, "_full_overlay_alpha", 160)
            self._blur_timer_out = QTimer(self)
            self._blur_timer_out.setInterval(10)

            def _step_out():
                self._full_overlay_alpha_out = max(0, self._full_overlay_alpha_out - 20)
                a = self._full_overlay_alpha_out
                if overlay and not overlay.isHidden():
                    overlay.setStyleSheet(f"background-color: rgba(0,0,0,{a});")
                if a <= 0:
                    self._blur_timer_out.stop()
                    try:
                        overlay.hide()
                        overlay.deleteLater()
                    except Exception:
                        pass
                    self._full_overlay = None

            self._blur_timer_out.timeout.connect(_step_out)
            self._blur_timer_out.start()

        win = getattr(self, "_blur_win_ref", None)
        orig = getattr(self, "_orig_resize_blur", None)
        if win and orig:
            win.resizeEvent = orig
            self._blur_win_ref = None

        try:
            if hasattr(self, "blur_anim"):
                self.blur_anim.stop()
            self.blur_anim = QPropertyAnimation(self.blur_effect, b"blurRadius", self)
            self.blur_anim.setDuration(180)
            self.blur_anim.setStartValue(self.blur_effect.blurRadius())
            self.blur_anim.setEndValue(0)
            self.blur_anim.setEasingCurve(QEasingCurve.Type.InCubic)
            self.blur_anim.finished.connect(lambda: self.content_shell.setGraphicsEffect(None))
            self.blur_anim.start()
        except Exception:
            self.content_shell.setGraphicsEffect(None)

        try:
            if hasattr(self, "_central_blur_anim"):
                self._central_blur_anim.stop()
            if hasattr(self, "_central_blur"):
                win_ref = self.window()
                central = win_ref.centralWidget() if win_ref else None
                if central:
                    anim = QPropertyAnimation(self._central_blur, b"blurRadius", self)
                    anim.setDuration(180)
                    anim.setStartValue(self._central_blur.blurRadius())
                    anim.setEndValue(0)
                    anim.setEasingCurve(QEasingCurve.Type.InCubic)
                    anim.finished.connect(lambda: central.setGraphicsEffect(None))
                    anim.start()
                    self._central_blur_anim = anim
        except Exception:
            try:
                w = self.window()
                if w:
                    c = w.centralWidget()
                    if c: c.setGraphicsEffect(None)
            except Exception:
                pass

        self.glass.fade_out()

    # ─────────────────────────────────────────────────────────────
    # Toasts
    # ─────────────────────────────────────────────────────────────
    def show_toast(self, message, kind="success"):
        toast = Toast(message, self.accent_color, kind, self.toast_layer)
        toast.setFixedWidth(360)

        # Insertar antes del stretch final
        index = max(0, self.toast_layout.count() - 1)
        self.toast_layout.insertWidget(
            index,
            toast,
            0,
            Qt.AlignmentFlag.AlignRight
        )

        self.toast_layer.raise_()

    # ─────────────────────────────────────────────────────────────
    # Styles
    # ─────────────────────────────────────────────────────────────
    def _primary_button_style(self):
        return f"""
            QPushButton {{
                background-color: {self.accent_color};
                color: white;
                border: none;
                border-radius: 9px;
                font-size: 12px;
                font-weight: 900;
                padding: 0 18px;
            }}
            QPushButton:hover {{
                background-color: {self.accent_hover};
            }}
            QPushButton:pressed {{
                background-color: {self.accent_active};
            }}
        """

    def _secondary_button_style(self):
        return f"""
            QPushButton {{
                background-color: #141414;
                color: {TEXT_SEC};
                border: 1px solid #222222;
                border-radius: 9px;
                font-size: 12px;
                font-weight: 800;
                padding: 0 18px;
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
                background-color: #1E1E1E;
                border-color: #333333;
            }}
            QPushButton:pressed {{
                border-color: {self.accent_color};
            }}
        """

    def _nav_button_style(self):
        return f"""
            QPushButton {{
                background-color: #121212;
                color: {TEXT_PRI};
                border: 1px solid #222222;
                border-radius: 9px;
                font-size: 12px;
                font-weight: 900;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background-color: #1C1C1C;
                border-color: #333333;
            }}
            QPushButton:pressed {{
                background-color: #080808;
                border-color: {self.accent_color};
            }}
        """

    def _combo_style(self):
        return f"""
            QComboBox {{
                background-color: #121212;
                color: {TEXT_PRI};
                border: 1px solid #222222;
                border-radius: 9px;
                padding: 0 12px;
                font-size: 12px;
                font-weight: 800;
            }}
            QComboBox:hover {{
                border-color: #444444;
            }}
            QComboBox:focus {{
                border-color: {self.accent_color};
            }}
            QComboBox QAbstractItemView {{
                background-color: #121212;
                color: {TEXT_PRI};
                selection-background-color: {self.accent_color};
                border: 1px solid #222222;
            }}
        """

    def _gradient_line_style(self):
        return f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.accent_color},
                    stop:0.4 rgba(225,29,72,80),
                    stop:1 transparent
                );
                border: none;
            }}
        """
