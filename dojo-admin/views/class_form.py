"""
views/class_form.py — Formulario premium de clase con:
  - Diseño en cards tipo HTML/CSS premium
  - Vista previa en tiempo real
  - Reloj analógico con selección libre de cualquier minuto
  - Actualización automática al seleccionar hora
  - Iconos SVG (sin emojis)
  - Toasts en lugar de QMessageBox
"""
import math

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QSpinBox,
    QColorDialog, QWidget, QFrame, QScrollArea,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QTime, QPointF, QRectF, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen, QFont, QLinearGradient

# ─── PALETA ───────────────────────────────────────────────────────────
BG_DIALOG  = "#0A0A0A"
BG_CARD    = "#111111"
BG_CARD_2  = "#161616"
BG_INPUT   = "#1C1C1C"
BG_HOVER   = "#1E1E1E"
BORDER     = "#222222"
BORDER_2   = "#2A2A2A"
RED        = "#E11D48"
RED_H      = "#F43F5E"
RED_DARK   = "#1A0810"
RED_GLOW   = "rgba(225,29,72,0.12)"
GREEN      = "#10B981"
BLUE       = "#3B82F6"
YELLOW     = "#F59E0B"
PURPLE     = "#A855F7"
TEXT_PRI   = "#FAFAFA"
TEXT_SEC   = "#A3A3A3"
TEXT_MUT   = "#525252"
TEXT_DIM   = "#333333"
CLOCK_BG   = "#0E0E0E"
CLOCK_RING = "#1A1A1A"

DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

INPUT_STYLE = f"""
    QLineEdit, QComboBox, QSpinBox {{
        background: {BG_INPUT};
        color: {TEXT_PRI};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 0 14px;
        font-size: 13px;
        font-weight: 500;
        font-family: 'Inter';
        min-height: 42px;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border-color: {RED};
        background: {BG_HOVER};
    }}
    QLineEdit:hover, QComboBox:hover, QSpinBox:hover {{
        border-color: #444;
    }}
    QComboBox::drop-down {{ border: none; width: 28px; background: transparent; }}
    QComboBox QAbstractItemView {{
        background: {BG_INPUT}; color: {TEXT_PRI};
        selection-background-color: {RED};
        border: 1px solid {BORDER}; border-radius: 8px; padding: 4px;
        outline: none;
    }}
    QSpinBox::up-button, QSpinBox::down-button {{
        width: 20px; background: transparent; border: none;
    }}
"""


# ═══════════════════════════════════════════════════════════════════
# SVG IconLabel (sin emojis)
# ═══════════════════════════════════════════════════════════════════
class IconLabel(QWidget):
    ICONS = {
        "calendar": (
            '<rect x="3" y="4" width="18" height="18" rx="2"/>'
            '<line x1="16" y1="2" x2="16" y2="6"/>'
            '<line x1="8" y1="2" x2="8" y2="6"/>'
            '<line x1="3" y1="10" x2="21" y2="10"/>'
        ),

        "clock": (
            '<circle cx="12" cy="12" r="10"/>'
            '<polyline points="12 6 12 12 16 14"/>'
        ),

        "instructions": (
            '<rect x="4" y="3" width="16" height="18" rx="2"/>'
            '<line x1="8" y1="8" x2="16" y2="8"/>'
            '<line x1="8" y1="12" x2="16" y2="12"/>'
            '<line x1="8" y1="16" x2="13" y2="16"/>'
        ),

        "capacity": (
            '<circle cx="12" cy="7" r="3"/>'
            '<circle cx="5" cy="9" r="2"/>'
            '<circle cx="19" cy="9" r="2"/>'
            '<polyline points="7 21 7 18 9 15 15 15 17 18 17 21"/>'
            '<polyline points="1 20 1 17 3 14 6 14"/>'
            '<polyline points="18 14 21 14 23 17 23 20"/>'
        ),

        "location": (
            '<circle cx="12" cy="8" r="5"/>'
            '<circle cx="12" cy="8" r="2"/>'
            '<polyline points="8.5 11.5 12 21 15.5 11.5"/>'
        ),

        "user": (
            '<circle cx="10" cy="7" r="4"/>'
            '<path d="M3 21v-2a4 4 0 0 1 4-4h6a4 4 0 0 1 4 4v2"/>'
            '<line x1="17" y1="11" x2="21" y2="11"/>'
        ),

        "map-pin": (
            '<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>'
            '<circle cx="12" cy="9" r="2.5" fill="currentColor"/>'
        ),

        "users": (
            '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>'
            '<circle cx="9" cy="7" r="4"/>'
            '<path d="M23 21v-2a4 4 0 0 0-3-3.87"/>'
            '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
        ),

        "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',

        "repeat": (
            '<polyline points="17 1 21 5 17 9"/>'
            '<path d="M3 11V9a4 4 0 0 1 4-4h14"/>'
            '<polyline points="7 23 3 19 7 15"/>'
            '<path d="M21 13v2a4 4 0 0 1-4 4H3"/>'
        ),

        "palette": (
            '<circle cx="13.5" cy="6.5" r=".5"/>'
            '<circle cx="17.5" cy="10.5" r=".5"/>'
            '<circle cx="8.5" cy="7.5" r=".5"/>'
            '<circle cx="6.5" cy="12.5" r=".5"/>'
            '<path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>'
        ),

        "tag": (
            '<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>'
            '<line x1="7" y1="7" x2="7.01" y2="7"/>'
        ),

        "check":        '<polyline points="20 6 9 17 4 12"/>',
        "x":            '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
        "eye":          '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
        "save": (
            '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>'
            '<polyline points="17 21 17 13 7 13 7 21"/>'
            '<polyline points="7 3 7 8 15 8"/>'
        ),
        "info":         '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
        "building":     '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>',
        "check-circle": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
        "x-circle":     '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
        "pause-circle": '<circle cx="12" cy="12" r="10"/><line x1="10" y1="15" x2="10" y2="9"/><line x1="14" y1="15" x2="14" y2="9"/>',
        "align-left":   '<line x1="17" y1="10" x2="3" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="17" y1="18" x2="3" y2="18"/>',
        "plus":         '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
        "minus":        '<line x1="5" y1="12" x2="19" y2="12"/>',
    }

    def __init__(self, icon_name, size=18, color=TEXT_SEC, parent=None):
        super().__init__(parent)
        self._icon  = icon_name
        self._size  = size
        self._color = color
        self.setFixedSize(size, size)

    def set_color(self, c): self._color = c; self.update()
    def set_icon(self, n):  self._icon  = n; self.update()

    def paintEvent(self, ev):
        import re
        path_data = self.ICONS.get(self._icon, "")
        if not path_data: return
        try:
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            sc = self._size / 24.0
            p.scale(sc, sc)
            pen = QPen(QColor(self._color))
            pen.setWidthF(1.8)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
            elems = re.findall(r'<(circle|rect|line|polyline|polygon|path)\s([^/]+)/?>', path_data)
            for tag, attrs_str in elems:
                attrs = dict(re.findall(r'(\w[\w-]*)="([^"]*)"', attrs_str))
                if tag == "circle":
                    cx,cy,r = float(attrs.get("cx",0)),float(attrs.get("cy",0)),float(attrs.get("r",0))
                    p.drawEllipse(QRectF(cx-r,cy-r,r*2,r*2))
                elif tag == "rect":
                    x,y,w,h = float(attrs.get("x",0)),float(attrs.get("y",0)),float(attrs.get("width",0)),float(attrs.get("height",0))
                    rx = float(attrs.get("rx",0))
                    if rx: p.drawRoundedRect(QRectF(x,y,w,h),rx,rx)
                    else: p.drawRect(QRectF(x,y,w,h))
                elif tag == "line":
                    p.drawLine(QPointF(float(attrs.get("x1",0)),float(attrs.get("y1",0))),QPointF(float(attrs.get("x2",0)),float(attrs.get("y2",0))))
                elif tag in ("polyline","polygon"):
                    pts = re.findall(r'-?[\d.]+', attrs.get("points",""))
                    if len(pts)>=2 and len(pts)%2==0:
                        from PyQt6.QtGui import QPainterPath as PP
                        path=PP(); path.moveTo(float(pts[0]),float(pts[1]))
                        for i in range(2,len(pts),2): path.lineTo(float(pts[i]),float(pts[i+1]))
                        if tag=="polygon": path.closeSubpath()
                        p.drawPath(path)
                elif tag == "path":
                    from PyQt6.QtGui import QPainterPath as PP
                    d = attrs.get("d","")
                    tokens = re.findall(r'[MLCQZSHVAmlcqzshva]|-?[\d.]+(?:e[+-]?\d+)?', d)
                    path=PP(); cur=QPointF(0,0); i=0
                    while i<len(tokens):
                        cmd=tokens[i]; i+=1
                        if cmd in "Mm":
                            x,y=float(tokens[i]),float(tokens[i+1]); i+=2
                            if cmd=="m": x+=cur.x(); y+=cur.y()
                            cur=QPointF(x,y); path.moveTo(cur)
                        elif cmd in "Ll":
                            x,y=float(tokens[i]),float(tokens[i+1]); i+=2
                            if cmd=="l": x+=cur.x(); y+=cur.y()
                            cur=QPointF(x,y); path.lineTo(cur)
                        elif cmd in "Cc":
                            x1,y1=float(tokens[i]),float(tokens[i+1])
                            x2,y2=float(tokens[i+2]),float(tokens[i+3])
                            x,y=float(tokens[i+4]),float(tokens[i+5]); i+=6
                            if cmd=="c": x1+=cur.x();y1+=cur.y();x2+=cur.x();y2+=cur.y();x+=cur.x();y+=cur.y()
                            cur=QPointF(x,y); path.cubicTo(QPointF(x1,y1),QPointF(x2,y2),cur)
                        elif cmd in "Zz":
                            path.closeSubpath()
                        elif cmd in "Hh":
                            x=float(tokens[i]); i+=1
                            if cmd=="h": x+=cur.x()
                            cur=QPointF(x,cur.y()); path.lineTo(cur)
                        elif cmd in "Vv":
                            y=float(tokens[i]); i+=1
                            if cmd=="v": y+=cur.y()
                            cur=QPointF(cur.x(),y); path.lineTo(cur)
                        else: i+=1  # skip unknown
                    p.drawPath(path)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════
# ClockFace — selección libre de cualquier minuto/hora
# ═══════════════════════════════════════════════════════════════════
class ClockFace(QWidget):
    time_changed = pyqtSignal(int, int)  # hour_12, minute
    released     = pyqtSignal()

    def __init__(self, mode="hour", parent=None):
        super().__init__(parent)
        self.mode           = mode
        self.selected_hour  = 8
        self.selected_minute = 0
        self.accent         = RED
        self._dragging      = False
        self.setMinimumSize(240, 240)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_mode(self, mode):
        self.mode = mode; self.update()

    def set_time_values(self, hour_12, minute):
        self.selected_hour   = hour_12
        self.selected_minute = minute
        self.update()

    def _angle_to_value(self, pos):
        cx, cy = self.width() / 2, self.height() / 2
        dx, dy = pos.x() - cx, pos.y() - cy
        angle  = math.degrees(math.atan2(dx, -dy))
        if angle < 0: angle += 360
        if self.mode == "hour":
            idx = int(round(angle / 30)) % 12
            vals = [12,1,2,3,4,5,6,7,8,9,10,11]
            return vals[idx], None
        else:
            # Libre: cualquier minuto 0-59
            minute = int(round(angle / 6)) % 60
            return None, minute

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        size = min(w, h) - 8
        cx, cy = w / 2, h / 2
        radius = size / 2

        # Fondo
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(CLOCK_BG))
        p.drawEllipse(QPointF(cx, cy), radius, radius)

        # Anillo exterior
        pen = QPen(QColor(CLOCK_RING), 2)
        p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(cx, cy), radius - 1, radius - 1)

        # Marcas de minutos (si modo minute)
        if self.mode == "minute":
            for m in range(60):
                ang = math.radians(m * 6 - 90)
                r_outer = radius - 8
                r_inner = radius - (14 if m % 5 == 0 else 10)
                x1 = cx + math.cos(ang) * r_inner
                y1 = cy + math.sin(ang) * r_inner
                x2 = cx + math.cos(ang) * r_outer
                y2 = cy + math.sin(ang) * r_outer
                tick_pen = QPen(QColor(BORDER_2 if m % 5 != 0 else "#333"), 1 if m % 5 != 0 else 1.5)
                p.setPen(tick_pen)
                p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Valores y selección
        p.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        text_radius = radius - 34

        if self.mode == "hour":
            values = [12,1,2,3,4,5,6,7,8,9,10,11]
            selected_val = self.selected_hour
            step = 30
        else:
            values = [0,5,10,15,20,25,30,35,40,45,50,55]
            selected_val = (self.selected_minute // 5) * 5
            step = 30

        sel_x, sel_y = cx, cy
        for idx, val in enumerate(values):
            ang = math.radians(idx * step - 90)
            x = cx + math.cos(ang) * text_radius
            y = cy + math.sin(ang) * text_radius

            is_sel = (val == selected_val)
            if is_sel:
                sel_x, sel_y = x, y
                p.setBrush(QColor(self.accent))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(QPointF(x, y), 20, 20)
                p.setPen(QColor("white"))
            else:
                p.setPen(QColor(TEXT_SEC))

            lbl = f"{val:02d}" if self.mode == "minute" else str(val)
            p.drawText(QRectF(x-16, y-9, 32, 18), Qt.AlignmentFlag.AlignCenter, lbl)

        # Si minuto libre no cae en múltiplo de 5, dibujar puntero libre
        if self.mode == "minute":
            free_ang = math.radians(self.selected_minute * 6 - 90)
            free_x = cx + math.cos(free_ang) * text_radius
            free_y = cy + math.sin(free_ang) * text_radius
            # Resaltar el minuto exacto
            p.setBrush(QColor(self.accent))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(free_x, free_y), 14, 14)
            p.setPen(QColor("white"))
            p.setFont(QFont("Inter", 9, QFont.Weight.Bold))
            p.drawText(QRectF(free_x-14, free_y-8, 28, 16), Qt.AlignmentFlag.AlignCenter, f"{self.selected_minute:02d}")
            sel_x, sel_y = free_x, free_y

        # Línea del centro al seleccionado
        line_pen = QPen(QColor(self.accent), 2)
        line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(line_pen)
        p.drawLine(QPointF(cx, cy), QPointF(sel_x, sel_y))

        # Punto central
        p.setBrush(QColor(self.accent))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), 5, 5)

    def _update_from_pos(self, pos):
        hour, minute = self._angle_to_value(pos)
        changed = False
        if self.mode == "hour" and hour is not None:
            if hour != self.selected_hour:
                self.selected_hour = hour; changed = True
        elif self.mode == "minute" and minute is not None:
            if minute != self.selected_minute:
                self.selected_minute = minute; changed = True
        if changed:
            self.update()
            self.time_changed.emit(self.selected_hour, self.selected_minute)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._update_from_pos(ev.position())
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        if self._dragging:
            self._update_from_pos(ev.position())
        super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev):
        self._dragging = False
        if ev.button() == Qt.MouseButton.LeftButton:
            self.released.emit()
        super().mouseReleaseEvent(ev)


# ═══════════════════════════════════════════════════════════════════
# TimePickerDialog — reloj con actualización automática
# ═══════════════════════════════════════════════════════════════════
class TimePickerDialog(QDialog):
    def __init__(self, initial_time=None, title="Hora", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(340, 500)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background: {BG_DIALOG}; color: {TEXT_PRI};")

        t = initial_time or QTime(8, 0)
        self.is_pm   = t.hour() >= 12
        h12          = t.hour() % 12 or 12
        self.hour_12 = h12
        self.minute  = t.minute()
        self.mode    = "hour"
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        # Title
        lbl_t = QLabel("Seleccionar hora")
        lbl_t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_t.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; font-family: 'Inter'; border: none;")
        root.addWidget(lbl_t)

        # Display row HH : MM AM/PM
        disp = QHBoxLayout()
        disp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        disp.setSpacing(6)

        def _time_btn(w, h):
            btn = QPushButton()
            btn.setFixedSize(w, h)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            return btn

        self.btn_h  = _time_btn(72, 62)
        self.btn_h.clicked.connect(lambda: self._set_mode("hour"))
        self.lbl_sep = QLabel(":")
        self.lbl_sep.setStyleSheet(f"color: {TEXT_PRI}; font-size: 32px; font-weight: 900; border: none; background: transparent;")
        self.btn_m  = _time_btn(72, 62)
        self.btn_m.clicked.connect(lambda: self._set_mode("minute"))
        self.btn_ap = _time_btn(52, 62)
        self.btn_ap.clicked.connect(self._toggle_ampm)

        disp.addWidget(self.btn_h)
        disp.addWidget(self.lbl_sep)
        disp.addWidget(self.btn_m)
        disp.addWidget(self.btn_ap)
        root.addLayout(disp)

        # Mode label
        self.lbl_mode = QLabel("HORA")
        self.lbl_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_mode.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 900; letter-spacing: 1px; border: none;")
        root.addWidget(self.lbl_mode)

        # Clock
        self.clock = ClockFace("hour", self)
        self.clock.time_changed.connect(self._on_clock_change)
        self.clock.released.connect(self._on_clock_released)
        root.addWidget(self.clock, 0, Qt.AlignmentFlag.AlignCenter)

        # Footer
        foot = QHBoxLayout(); foot.setSpacing(10)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 9px; font-size: 12px; font-weight: 700; }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #444; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("Confirmar")
        btn_ok.setFixedHeight(38)
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white;
                border: none; border-radius: 9px; font-size: 12px; font-weight: 800; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        btn_ok.clicked.connect(self.accept)
        foot.addWidget(btn_cancel); foot.addWidget(btn_ok)
        root.addLayout(foot)

    def _set_mode(self, mode):
        self.mode = mode
        self.clock.set_mode(mode)
        self.clock.set_time_values(self.hour_12, self.minute)
        self._refresh()

    def _toggle_ampm(self):
        self.is_pm = not self.is_pm; self._refresh()

    def _on_clock_change(self, hour_12, minute):
        """Actualización al arrastrar — solo guarda el valor, no cambia modo."""
        self.hour_12 = hour_12
        self.minute  = minute
        self._refresh()

    def _on_clock_released(self):
        """Cambia a minutos solo cuando el usuario suelta el mouse en modo hora."""
        if self.mode == "hour":
            QTimer.singleShot(180, lambda: self._set_mode("minute"))

    def _refresh(self):
        self.clock.set_time_values(self.hour_12, self.minute)

        active_ss = f"""
            QPushButton {{
                background: {RED_DARK};
                color: {RED};
                border: 1.5px solid {RED};
                border-radius: 9px;
                font-size: 26px;
                font-weight: 900;
                font-family: 'Inter';
            }}
        """
        inactive_ss = f"""
            QPushButton {{
                background: {BG_INPUT};
                color: {TEXT_SEC};
                border: 1px solid {BORDER};
                border-radius: 9px;
                font-size: 26px;
                font-weight: 900;
                font-family: 'Inter';
            }}
            QPushButton:hover {{ border-color: #444; color: {TEXT_PRI}; }}
        """
        ampm_ss = f"""
            QPushButton {{
                background: {BG_INPUT};
                color: {RED if True else TEXT_SEC};
                border: 1px solid {BORDER};
                border-radius: 9px;
                font-size: 13px;
                font-weight: 900;
                font-family: 'Inter';
            }}
            QPushButton:hover {{ border-color: {RED}; color: {RED}; }}
        """

        self.btn_h.setText(f"{self.hour_12:02d}")
        self.btn_m.setText(f"{self.minute:02d}")
        self.btn_ap.setText("PM" if self.is_pm else "AM")
        self.btn_h.setStyleSheet(active_ss if self.mode == "hour" else inactive_ss)
        self.btn_m.setStyleSheet(active_ss if self.mode == "minute" else inactive_ss)
        self.btn_ap.setStyleSheet(ampm_ss)
        self.lbl_mode.setText("HORAS" if self.mode == "hour" else "MINUTOS")

    def selected_time(self) -> QTime:
        h = self.hour_12 % 12
        if self.is_pm: h += 12
        return QTime(h, self.minute)


# ═══════════════════════════════════════════════════════════════════
# ClassForm — Formulario premium con cards + vista previa
# ═══════════════════════════════════════════════════════════════════
def _card(accent_left=None) -> QFrame:
    frame = QFrame()
    border_left = f"border-left: 3px solid {accent_left};" if accent_left else ""
    frame.setStyleSheet(f"""
        QFrame {{
            background: {BG_CARD};
            border: 1px solid {BORDER};
            {border_left}
            border-radius: 14px;
        }}
        QFrame * {{ background: transparent; border: none; }}
    """)
    return frame


def _section_label(text, color=TEXT_MUT) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: {color}; font-size: 10px; font-weight: 900; "
        f"font-family: 'Inter'; letter-spacing: 1px;"
    )
    return lbl


def _field_label(text) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; font-weight: 700; font-family: 'Inter';")
    return lbl


def _sep(parent_layout):
    s = QFrame(); s.setFixedHeight(1)
    s.setStyleSheet(f"background: {BORDER}; border: none; min-height:1px; max-height:1px;")
    parent_layout.addWidget(s)


class ClassForm(QDialog):
    def __init__(self, repo, schedule_id=None, default_day=None, default_hour=None, parent=None):
        super().__init__(parent)
        self.repo          = repo
        self.schedule_id   = schedule_id
        self.default_day   = default_day
        self.default_hour  = default_hour
        self.selected_color = BLUE

        self.start_time_value = QTime(18, 0)
        self.end_time_value   = QTime(19, 0)

        self.setWindowTitle("Nueva clase" if not schedule_id else "Editar clase")
        self.setMinimumSize(860, 640)
        self.resize(920, 680)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background: {BG_DIALOG}; color: {TEXT_PRI};")

        self._build_ui()
        self._load_options()

        if self.schedule_id:
            self._load_data()
        else:
            self._apply_defaults()

        self._update_preview()

    # ── Build UI ──────────────────────────────────────────────────
    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── LEFT: scroll con formulario ────────────────────────────
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: transparent; width: 6px; }
            QScrollBar::handle:vertical { background: #2A2A2A; border-radius: 3px; }
        """)

        left_w = QWidget(); left_w.setStyleSheet("background: transparent;")
        left = QVBoxLayout(left_w)
        left.setContentsMargins(24, 24, 24, 24)
        left.setSpacing(16)

        # ── Header
        hdr = QHBoxLayout(); hdr.setSpacing(12)
        icon_frame = QFrame()
        icon_frame.setFixedSize(42, 42)
        icon_frame.setStyleSheet(f"background: {RED_GLOW}; border: 1px solid rgba(225,29,72,0.3); border-radius: 10px;")
        il = QHBoxLayout(icon_frame); il.setContentsMargins(0,0,0,0)
        il.addWidget(IconLabel("calendar", 20, RED), 0, Qt.AlignmentFlag.AlignCenter)

        title_col = QVBoxLayout(); title_col.setSpacing(2)
        is_edit = bool(self.schedule_id)
        lbl_title = QLabel("Editar clase" if is_edit else "Nueva clase")
        lbl_title.setStyleSheet(f"color: {TEXT_PRI}; font-size: 18px; font-weight: 900; font-family: 'Inter';")
        lbl_sub = QLabel("Modifica los datos de la clase" if is_edit else "Completa los datos para programar la clase")
        lbl_sub.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; font-weight: 500;")
        title_col.addWidget(lbl_title); title_col.addWidget(lbl_sub)

        btn_help = QPushButton()
        btn_help.setFixedHeight(34)
        btn_help.setMinimumWidth(130)
        btn_help.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_help.setStyleSheet(f"""
            QPushButton {{
                background: rgba(59,130,246,0.08);
                border: 1px solid rgba(59,130,246,0.25);
                border-radius: 9px;
            }}
            QPushButton:hover {{ background: rgba(59,130,246,0.14); }}
            QPushButton * {{ background: transparent; border: none; }}
        """)
        btn_help_hl = QHBoxLayout(btn_help)
        btn_help_hl.setContentsMargins(12, 0, 12, 0); btn_help_hl.setSpacing(7)
        btn_help_hl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_help_hl.addWidget(IconLabel("instructions", 15, BLUE))
        btn_help_lbl = QLabel("Instrucciones")
        btn_help_lbl.setStyleSheet(f"color:{BLUE};font-size:11px;font-weight:800;border:none;")
        btn_help_hl.addWidget(btn_help_lbl)
        btn_help.clicked.connect(self._open_instructions)

        hdr.addWidget(icon_frame); hdr.addLayout(title_col, 1)
        hdr.addWidget(btn_help, 0, Qt.AlignmentFlag.AlignVCenter)
        left.addLayout(hdr)

        # ── Card 1: Información general ────────────────────────────
        card1 = _card(RED)
        c1l = QVBoxLayout(card1); c1l.setContentsMargins(18,16,18,16); c1l.setSpacing(14)
        c1l.addWidget(_section_label("INFORMACIÓN GENERAL"))
        _sep(c1l)

        # Nombre
        c1l.addWidget(_field_label("Nombre de la clase *"))
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ej: BJJ Adultos · Karate Infantil")
        self.input_name.setStyleSheet(INPUT_STYLE)
        self.input_name.textChanged.connect(self._update_preview)
        c1l.addWidget(self.input_name)

        # Arte marcial + Instructor (fila)
        row1 = QHBoxLayout(); row1.setSpacing(14)
        col_ma = QVBoxLayout(); col_ma.setSpacing(6)
        col_ma.addWidget(_field_label("Arte marcial *"))
        self.cmb_martial_art = QComboBox()
        self.cmb_martial_art.setStyleSheet(INPUT_STYLE)
        self.cmb_martial_art.currentIndexChanged.connect(self._update_preview)
        col_ma.addWidget(self.cmb_martial_art)
        row1.addLayout(col_ma, 1)

        col_ins = QVBoxLayout(); col_ins.setSpacing(6)
        col_ins.addWidget(_field_label("Instructor"))
        self.cmb_instructor = QComboBox()
        self.cmb_instructor.setStyleSheet(INPUT_STYLE)
        col_ins.addWidget(self.cmb_instructor)
        row1.addLayout(col_ins, 1)
        c1l.addLayout(row1)

        left.addWidget(card1)

        # ── Card 2: Horario ────────────────────────────────────────
        card2 = _card(BLUE)
        c2l = QVBoxLayout(card2); c2l.setContentsMargins(18,16,18,16); c2l.setSpacing(14)
        c2l.addWidget(_section_label("HORARIO Y FRECUENCIA"))
        _sep(c2l)

        # ── Tipo de frecuencia ──────────────────────────────────────
        c2l.addWidget(_field_label("¿Cómo se repite esta clase?"))
        self._freq_buttons = {}
        freq_row = QHBoxLayout(); freq_row.setSpacing(8)
        freq_opts = [
            ("weekly",      "Semanal fija",    "Mismo día cada semana"),
            ("multi_day",   "Varios días",      "Ej: Martes y Jueves"),
            ("multi_time",  "Mismo día",       "Varios horarios durante el mismo día"),
            ("once",        "Una sola vez",     "Clase puntual"),
        ]
        for key, label, tip in freq_opts:
            btn = QPushButton(label)
            btn.setFixedHeight(38)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(tip)
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {BG_INPUT}; color: {TEXT_SEC};
                    border: 1px solid {BORDER}; border-radius: 9px;
                    font-size: 11px; font-weight: 700; font-family: 'Inter';
                }}
                QPushButton:checked {{
                    background: rgba(59,130,246,0.12); color: {BLUE};
                    border: 1.5px solid {BLUE};
                }}
                QPushButton:hover {{ border-color: #444; color: {TEXT_PRI}; }}
            """)
            btn.clicked.connect(lambda _, k=key: self._on_freq_change(k))
            self._freq_buttons[key] = btn
            freq_row.addWidget(btn, 1)
        c2l.addLayout(freq_row)

        # ── Selector de días (multi_day) ───────────────────────────
        self._days_frame = QFrame()
        self._days_frame.setStyleSheet("background: transparent; border: none;")
        days_hl = QHBoxLayout(self._days_frame); days_hl.setContentsMargins(0,0,0,0); days_hl.setSpacing(6)
        self._day_toggles = {}
        day_abbr = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for idx, abbr in enumerate(day_abbr):
            btn = QPushButton(abbr)
            btn.setFixedSize(42, 38)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {BG_INPUT}; color: {TEXT_MUT};
                    border: 1px solid {BORDER}; border-radius: 8px;
                    font-size: 11px; font-weight: 700;
                }}
                QPushButton:checked {{
                    background: rgba(59,130,246,0.15); color: {BLUE};
                    border: 1.5px solid {BLUE};
                }}
            """)
            btn.toggled.connect(self._update_preview)
            self._day_toggles[idx] = btn
            days_hl.addWidget(btn)
        self._days_frame.setVisible(False)
        c2l.addWidget(self._days_frame)

        # ── Día único (weekly/once) ────────────────────────────────
        self._single_day_frame = QFrame()
        self._single_day_frame.setStyleSheet("background: transparent; border: none;")
        sdfl = QVBoxLayout(self._single_day_frame); sdfl.setContentsMargins(0,0,0,0); sdfl.setSpacing(6)
        sdfl.addWidget(_field_label("Día de la semana"))
        self.cmb_day = QComboBox()
        for idx, name in enumerate(DAYS):
            self.cmb_day.addItem(name, idx)
        self.cmb_day.setStyleSheet(INPUT_STYLE)
        self.cmb_day.currentIndexChanged.connect(self._update_preview)
        sdfl.addWidget(self.cmb_day)
        c2l.addWidget(self._single_day_frame)

        # ── Horario ────────────────────────────────────────────────
        self._base_time_frame = QFrame()
        self._base_time_frame.setStyleSheet("background: transparent; border: none;")
        row_times = QHBoxLayout(self._base_time_frame)
        row_times.setContentsMargins(0, 0, 0, 0)
        row_times.setSpacing(14)

        col_start = QVBoxLayout(); col_start.setSpacing(6)
        col_start.addWidget(_field_label("Hora inicio"))
        self.btn_time_start = QPushButton()
        self.btn_time_start.setFixedHeight(42)
        self.btn_time_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_time_start.clicked.connect(lambda: self._open_time("start"))
        col_start.addWidget(self.btn_time_start)
        row_times.addLayout(col_start, 1)

        col_end = QVBoxLayout(); col_end.setSpacing(6)
        col_end.addWidget(_field_label("Hora fin"))
        self.btn_time_end = QPushButton()
        self.btn_time_end.setFixedHeight(42)
        self.btn_time_end.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_time_end.clicked.connect(lambda: self._open_time("end"))
        col_end.addWidget(self.btn_time_end)
        row_times.addLayout(col_end, 1)
        c2l.addWidget(self._base_time_frame)

        # Nota para "una sola vez"
        self._once_note = QLabel("Esta clase se registrará una sola vez y no se repetirá en el calendario.")
        self._once_note.setWordWrap(True)
        self._once_note.setStyleSheet(f"color: {YELLOW}; font-size: 11px; font-style: italic; border: none;")
        self._once_note.setVisible(False)
        c2l.addWidget(self._once_note)

        # ── Panel multi-horario (mismo día, franjas dinámicas) ────────
        self._multi_time_frame = QFrame()
        self._multi_time_frame.setStyleSheet("background: transparent; border: none;")
        mt_vl = QVBoxLayout(self._multi_time_frame)
        mt_vl.setContentsMargins(0, 0, 0, 0)
        mt_vl.setSpacing(8)

        mt_vl.addWidget(_field_label("Día de la semana"))
        self.cmb_day_mt = QComboBox()
        for idx, name in enumerate(DAYS):
            self.cmb_day_mt.addItem(name, idx)
        self.cmb_day_mt.setStyleSheet(INPUT_STYLE)
        self.cmb_day_mt.currentIndexChanged.connect(self._update_preview)
        mt_vl.addWidget(self.cmb_day_mt)

        # Contenedor dinámico de franjas
        self._mt_franjas_widget = QWidget()
        self._mt_franjas_widget.setStyleSheet("background:transparent;border:none;")
        self._mt_franjas_layout = QVBoxLayout(self._mt_franjas_widget)
        self._mt_franjas_layout.setContentsMargins(0, 0, 0, 0)
        self._mt_franjas_layout.setSpacing(8)
        mt_vl.addWidget(self._mt_franjas_widget)

        # Botón "+" para agregar franja
        self._btn_add_franja = QPushButton()
        self._btn_add_franja.setFixedHeight(36)
        self._btn_add_franja.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_add_franja.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {BLUE};
                border: 1px dashed rgba(59,130,246,0.4);
                border-radius: 9px;
                font-size: 12px;
                font-weight: 700;
                font-family: 'Inter';
            }}
            QPushButton:hover {{
                background: rgba(59,130,246,0.08);
                border-color: {BLUE};
            }}
            QPushButton * {{ background: transparent; border: none; }}
        """)
        add_hl = QHBoxLayout(self._btn_add_franja)
        add_hl.setContentsMargins(12, 0, 12, 0)
        add_hl.setSpacing(6)
        add_hl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        add_icon = IconLabel("plus", 14, BLUE)
        add_hl.addWidget(add_icon)
        add_lbl = QLabel("Agregar horario")
        add_lbl.setStyleSheet(f"color:{BLUE};font-size:12px;font-weight:700;border:none;")
        add_hl.addWidget(add_lbl)
        self._btn_add_franja.clicked.connect(lambda: self._mt_add_franja())
        mt_vl.addWidget(self._btn_add_franja)

        self._multi_time_note = QLabel()
        self._multi_time_note.setWordWrap(True)
        self._multi_time_note.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; border: none;")
        mt_vl.addWidget(self._multi_time_note)

        self._multi_time_frame.setVisible(False)
        c2l.addWidget(self._multi_time_frame)

        # Estado interno de franjas: lista de (QTime_start, QTime_end)
        self._mt_franjas: list[list] = []
        # Inicializar con 2 franjas por defecto
        self._mt_add_franja(QTime(18, 0), QTime(19, 0))
        self._mt_add_franja(QTime(20, 0), QTime(21, 0))

        # Activar "Semanal fija" por defecto
        self._current_freq = "weekly"
        self._freq_buttons["weekly"].setChecked(True)

        self._refresh_time_buttons()
        left.addWidget(card2)

        # ── Card 3: Detalles adicionales ───────────────────────────
        card3 = _card(YELLOW)
        c3l = QVBoxLayout(card3); c3l.setContentsMargins(18,16,18,16); c3l.setSpacing(14)
        c3l.addWidget(_section_label("DETALLES ADICIONALES"))
        _sep(c3l)

        row3 = QHBoxLayout(); row3.setSpacing(14)

        col_cap = QVBoxLayout(); col_cap.setSpacing(6)
        col_cap.addWidget(_field_label("Capacidad máxima"))
        self.spin_capacity = QSpinBox()
        self.spin_capacity.setRange(0, 999)
        self.spin_capacity.setSpecialValueText("Sin límite")
        self.spin_capacity.setValue(0)
        self.spin_capacity.setStyleSheet(INPUT_STYLE)
        col_cap.addWidget(self.spin_capacity)
        row3.addLayout(col_cap, 1)

        col_loc = QVBoxLayout(); col_loc.setSpacing(6)
        col_loc.addWidget(_field_label("Ubicación / Sala"))
        self.input_location = QLineEdit()
        self.input_location.setPlaceholderText("Ej: Tatami principal")
        self.input_location.setStyleSheet(INPUT_STYLE)
        col_loc.addWidget(self.input_location)
        row3.addLayout(col_loc, 2)

        c3l.addLayout(row3)

        col_col = QVBoxLayout(); col_col.setSpacing(6)
        col_col.addWidget(_field_label("Color del bloque en el calendario"))
        self.btn_color = QPushButton()
        self.btn_color.setFixedHeight(42)
        self.btn_color.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_color.clicked.connect(self._pick_color)
        col_col.addWidget(self.btn_color)
        self._refresh_color_btn()
        c3l.addLayout(col_col)

        # Estado oculto — valor fijo "active", se cambia al registrar asistencia
        self.cmb_status = QComboBox()  # mantenido para compatibilidad con _save/_load
        self.cmb_status.addItem("Activa",    "active")
        self.cmb_status.addItem("Inactiva",  "inactive")
        self.cmb_status.addItem("Cancelada", "canceled")
        self.cmb_status.setVisible(False)  # no se muestra al usuario
        left.addWidget(card3)

        left.addStretch()

        # ── Footer botones ─────────────────────────────────────────
        foot = QHBoxLayout(); foot.setSpacing(10)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(42)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 10px;
                font-size: 13px; font-weight: 700; padding: 0 20px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #444; background: {BG_HOVER}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton()
        btn_save.setFixedHeight(42)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white;
                border: none; border-radius: 10px;
                font-size: 13px; font-weight: 800; padding: 0 24px; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        save_hl = QHBoxLayout(btn_save); save_hl.setContentsMargins(16,0,16,0); save_hl.setSpacing(8)
        save_hl.addWidget(IconLabel("save", 16, "white"))
        save_lbl = QLabel("Guardar clase"); save_lbl.setStyleSheet("color: white; font-size: 13px; font-weight: 800; border:none;")
        save_hl.addWidget(save_lbl)
        btn_save.clicked.connect(self._save)
        foot.addWidget(btn_cancel); foot.addWidget(btn_save)
        left.addLayout(foot)

        left_scroll.setWidget(left_w)
        outer.addWidget(left_scroll, 3)

        # ── RIGHT: Vista previa ────────────────────────────────────
        right = QFrame()
        right.setFixedWidth(320)
        right.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD_2};
                border-left: 1px solid {BORDER};
                border: none;
                border-left: 1px solid {BORDER};
            }}
        """)
        right_l = QVBoxLayout(right)
        right_l.setContentsMargins(20, 24, 20, 24)
        right_l.setSpacing(16)

        prev_title = QLabel("VISTA PREVIA")
        prev_title.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 900; letter-spacing: 1px;")
        right_l.addWidget(prev_title)

        _sep(right_l)

        # Card preview
        self.preview_card = QFrame()
        self.preview_card.setMinimumHeight(100)
        self.preview_card.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border-left: 4px solid {self.selected_color};
                border-radius: 10px;
            }}
        """)
        pcl = QVBoxLayout(self.preview_card); pcl.setContentsMargins(14,10,14,10); pcl.setSpacing(4)
        self.prev_lbl_name = QLabel("Nombre de la clase")
        self.prev_lbl_name.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; border:none;")
        self.prev_lbl_time = QLabel("00:00 – 00:00")
        self.prev_lbl_time.setWordWrap(True)
        self.prev_lbl_time.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 700; border:none;")
        self.prev_lbl_art  = QLabel("Arte marcial")
        self.prev_lbl_art.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; border:none;")
        pcl.addWidget(self.prev_lbl_name)
        pcl.addWidget(self.prev_lbl_time)
        pcl.addWidget(self.prev_lbl_art)
        right_l.addWidget(self.preview_card)

        # Info rows
        def _info_row(icon_name, key_lbl):
            row = QHBoxLayout(); row.setSpacing(10)
            ic = IconLabel(icon_name, 18, TEXT_MUT)
            lbl = QLabel(key_lbl)
            lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; border:none;")
            row.addWidget(ic); row.addWidget(lbl, 1)
            return row, lbl

        # Frecuencia
        row_freq, self.prev_freq = _info_row("repeat",   "Semanal")
        # Día
        row_day, self.prev_day   = _info_row("calendar", "Día")
        # Horario
        row_time, self.prev_time2 = _info_row("clock",   "00:00 – 00:00")
        self.prev_time2.setWordWrap(True)
        # Capacidad — icono user con número (más claro que grupo genérico)
        row_cap, self.prev_cap   = _info_row("capacity",  "Sin límite de personas")
        # Ubicación — map-pin es universalmente reconocible como "lugar"
        row_loc, self.prev_loc   = _info_row("location",  "Sin ubicación asignada")
        # Estado QUITADO del formulario — se gestiona al registrar asistencia

        right_l.addLayout(row_freq)
        right_l.addLayout(row_day)
        right_l.addLayout(row_time)
        right_l.addLayout(row_cap)
        right_l.addLayout(row_loc)
        right_l.addStretch()

        # Conectar después de que prev_cap ya existe
        self.spin_capacity.valueChanged.connect(self._update_preview)
        self.input_location.textChanged.connect(self._update_preview)

        outer.addWidget(right, 0)

    # ── Helpers ───────────────────────────────────────────────────
    def _refresh_time_buttons(self):
        def _time_btn_style(is_set):
            return f"""
                QPushButton {{
                    background: {BG_INPUT if not is_set else BG_HOVER};
                    color: {TEXT_PRI};
                    border: 1px solid {RED if is_set else BORDER};
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 800;
                    font-family: 'Inter';
                    padding: 0 14px;
                }}
                QPushButton:hover {{ border-color: {RED}; background: {BG_HOVER}; }}
                QPushButton * {{ background: transparent; border: none; }}
            """
        self.btn_time_start.setText(self.start_time_value.toString("hh:mm AP"))
        self.btn_time_end.setText(self.end_time_value.toString("hh:mm AP"))
        self.btn_time_start.setStyleSheet(_time_btn_style(True))
        self.btn_time_end.setStyleSheet(_time_btn_style(True))
        self._update_preview()

    def _refresh_color_btn(self):
        self.btn_color.setText(self.selected_color)
        self.btn_color.setStyleSheet(f"""
            QPushButton {{
                background: {self.selected_color};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 800;
            }}
        """)

    def _open_time(self, target):
        current = self.start_time_value if target == "start" else self.end_time_value
        dlg = TimePickerDialog(current, "Hora inicio" if target == "start" else "Hora fin", self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            sel = dlg.selected_time()
            if target == "start":
                self.start_time_value = sel
                if self.end_time_value <= self.start_time_value:
                    self.end_time_value = self.start_time_value.addSecs(3600)
            else:
                self.end_time_value = sel
            self._refresh_time_buttons()

    def _pick_color(self):
        color = QColorDialog.getColor(QColor(self.selected_color), self, "Color del bloque")
        if color.isValid():
            self.selected_color = color.name()
            self._refresh_color_btn()
            self._update_preview()

    def _on_freq_change(self, key):
        """Cambia entre frecuencias: weekly, multi_day, multi_time, once."""
        self._current_freq = key
        for k, btn in self._freq_buttons.items():
            btn.setChecked(k == key)
        self._days_frame.setVisible(key == "multi_day")
        self._single_day_frame.setVisible(key in ("weekly", "once"))
        self._multi_time_frame.setVisible(key == "multi_time")
        self._base_time_frame.setVisible(key != "multi_time")
        self._once_note.setVisible(key == "once")
        self._update_preview()

    def _mt_add_franja(self, t_start=None, t_end=None):
        if len(self._mt_franjas) >= 5:
            self._toast("Máximo 5 horarios por día.", "warning")
            return
        if t_start is None:
            if self._mt_franjas:
                prev_end = self._mt_franjas[-1][1]
                t_start = prev_end.addSecs(3600)
                t_end   = t_start.addSecs(3600)
            else:
                t_start = QTime(18, 0)
                t_end   = QTime(19, 0)
        self._mt_franjas.append([t_start, t_end if t_end else t_start.addSecs(3600)])
        self._mt_rebuild_ui()

    def _mt_remove_franja(self, idx):
        if len(self._mt_franjas) <= 1:
            self._toast("Debe haber al menos un horario.", "warning")
            return
        self._mt_franjas.pop(idx)
        self._mt_rebuild_ui()

    def _mt_rebuild_ui(self):
        while self._mt_franjas_layout.count():
            item = self._mt_franjas_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for idx, (t_start, t_end) in enumerate(self._mt_franjas):
            color = RED

            franja_header = QHBoxLayout()
            franja_header.setSpacing(8)
            lbl_franja = QLabel(f"Horario {idx + 1}")
            lbl_franja.setStyleSheet(f"color:{color};font-size:11px;font-weight:900;border:none;")
            franja_header.addWidget(lbl_franja, 1)

            if len(self._mt_franjas) > 1:
                btn_rem = QPushButton()
                btn_rem.setFixedSize(24, 24)
                btn_rem.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_rem.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        border: 1px solid rgba(255,68,68,0.3);
                        border-radius: 6px;
                    }}
                    QPushButton:hover {{ background: rgba(255,68,68,0.12); }}
                    QPushButton * {{ background: transparent; border: none; }}
                """)
                rem_l = QHBoxLayout(btn_rem); rem_l.setContentsMargins(0,0,0,0)
                rem_l.addWidget(IconLabel("minus", 10, "#FF4444"), 0, Qt.AlignmentFlag.AlignCenter)
                btn_rem.clicked.connect(lambda _, i=idx: self._mt_remove_franja(i))
                franja_header.addWidget(btn_rem)

            franja_container = QWidget()
            franja_container.setStyleSheet("background:transparent;border:none;")
            franja_vl = QVBoxLayout(franja_container)
            franja_vl.setContentsMargins(0, 0, 0, 0)
            franja_vl.setSpacing(4)
            franja_vl.addLayout(franja_header)

            row = QHBoxLayout(); row.setSpacing(10)

            btn_s = QPushButton(t_start.toString("hh:mm AP"))
            btn_e = QPushButton(t_end.toString("hh:mm AP"))
            for btn in (btn_s, btn_e):
                btn.setFixedHeight(42)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {BG_INPUT}; color: {TEXT_PRI};
                        border: 1px solid {color}; border-radius: 10px;
                        font-size: 13px; font-weight: 800; font-family: 'Inter';
                    }}
                    QPushButton:hover {{ border-color: {RED_H}; background: {BG_HOVER}; }}
                """)
                row.addWidget(btn, 1)

            btn_s.clicked.connect(lambda _, i=idx: self._mt_open_time(i, "start"))
            btn_e.clicked.connect(lambda _, i=idx: self._mt_open_time(i, "end"))

            franja_vl.addLayout(row)
            self._mt_franjas_layout.addWidget(franja_container)

        n = len(self._mt_franjas)
        self._multi_time_note.setText(
            f"El calendario mostrará {n} horario{'s' if n != 1 else ''} independiente{'s' if n != 1 else ''} para este mismo día."
        )
        self._update_preview()

    def _mt_open_time(self, franja_idx, target):
        current = self._mt_franjas[franja_idx][0 if target == "start" else 1]
        label_t = f"Horario {franja_idx + 1} — {'Inicio' if target == 'start' else 'Fin'}"
        dlg = TimePickerDialog(current, label_t, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            sel = dlg.selected_time()
            if target == "start":
                self._mt_franjas[franja_idx][0] = sel
                if self._mt_franjas[franja_idx][1] <= sel:
                    self._mt_franjas[franja_idx][1] = sel.addSecs(3600)
            else:
                self._mt_franjas[franja_idx][1] = sel
            self._mt_rebuild_ui()

    def _get_days_label(self):
        """Devuelve string de días seleccionados según frecuencia."""
        if not hasattr(self, "_current_freq"):
            return "Semanal"
        if self._current_freq == "multi_day":
            day_abbr = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
            sel = [day_abbr[i] for i, btn in self._day_toggles.items() if btn.isChecked()]
            return " · ".join(sel) if sel else "Sin días"
        elif self._current_freq == "once":
            return "Una sola vez"
        elif self._current_freq == "multi_time":
            return self.cmb_day_mt.currentText() if hasattr(self, "cmb_day_mt") else "Lunes"
        else:
            return self.cmb_day.currentText() if hasattr(self, "cmb_day") else "Lunes"

    def _update_preview(self):
        if not hasattr(self, "prev_lbl_name"):
            return
        name = self.input_name.text().strip() if hasattr(self, "input_name") else ""
        self.prev_lbl_name.setText(name or "Nombre de la clase")

        st = self.start_time_value.toString("hh:mm AP")
        et = self.end_time_value.toString("hh:mm AP")
        self.prev_lbl_time.setText(f"{st}  –  {et}")
        if hasattr(self, "prev_time2"):
            if getattr(self, "_current_freq", "") == "multi_time":
                if hasattr(self, "_mt_franjas") and self._mt_franjas:
                    partes = [
                        f"{f[0].toString('hh:mm AP')}–{f[1].toString('hh:mm AP')}"
                        for f in self._mt_franjas
                    ]
                    texto = "\n".join(partes)
                    self.prev_time2.setText(texto)
                    self.prev_lbl_time.setText(texto)
                    extra_lines = max(0, len(partes) - 1)
                    self.preview_card.setMinimumHeight(100 + extra_lines * 18)
                else:
                    self.prev_time2.setText("Sin horarios")
                    self.prev_lbl_time.setText("Sin horarios")
            else:
                self.preview_card.setMinimumHeight(100)
                st = self.start_time_value.toString("hh:mm AP")
                et = self.end_time_value.toString("hh:mm AP")
                self.prev_time2.setText(f"{st}  –  {et}")

        ma = self.cmb_martial_art.currentText() if hasattr(self, "cmb_martial_art") else "Arte marcial"
        self.prev_lbl_art.setText(ma)

        # Frecuencia + día
        n_franjas = len(self._mt_franjas) if hasattr(self, "_mt_franjas") else 2
        freq_label = {
            "weekly":     "Semanal",
            "multi_day":  "Varios días",
            "multi_time": f"Mismo día · {n_franjas} horario{'s' if n_franjas != 1 else ''}",
            "once":       "Una vez",
        }.get(getattr(self, "_current_freq", "weekly"), "Semanal")
        if hasattr(self, "prev_freq"):
            self.prev_freq.setText(freq_label)
        if hasattr(self, "prev_day"):
            self.prev_day.setText(self._get_days_label())

        # Capacidad — conectado con valueChanged
        cap = self.spin_capacity.value() if hasattr(self, "spin_capacity") else 0
        if hasattr(self, "prev_cap"):
            self.prev_cap.setText(f"Máx. {cap} personas" if cap > 0 else "Sin límite de personas")

        # Ubicación
        loc = self.input_location.text().strip() if hasattr(self, "input_location") else ""
        if hasattr(self, "prev_loc"):
            self.prev_loc.setText(loc or "Sin ubicación asignada")

        # Borde de color
        self.preview_card.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border-left: 4px solid {self.selected_color};
                border-radius: 10px;
            }}
        """)

    # ── Data ──────────────────────────────────────────────────────
    def _load_options(self):
        try:
            opts = self.repo.get_form_options()
            self.cmb_martial_art.clear()
            self.cmb_martial_art.addItem("Seleccionar...", None)
            for ma_id, ma_name in opts.get("martial_arts", []):
                self.cmb_martial_art.addItem(ma_name, ma_id)
            self.cmb_instructor.clear()
            self.cmb_instructor.addItem("Sin instructor fijo", None)
            for ins_id, ins_name in opts.get("instructors", []):
                self.cmb_instructor.addItem(ins_name, ins_id)
        except Exception as e:
            self._toast(f"No se pudieron cargar opciones: {e}", "error")

    def _apply_defaults(self):
        if self.default_day is not None:
            idx = self.cmb_day.findData(self.default_day)
            if idx >= 0: self.cmb_day.setCurrentIndex(idx)
        hour = int(self.default_hour or 18)
        self.start_time_value = QTime(hour, 0)
        self.end_time_value   = QTime(min(hour + 1, 23), 0)
        self._refresh_time_buttons()

    def _load_data(self):
        data = self.repo.get_by_id(self.schedule_id)
        if not data:
            self._toast("No se encontró la clase.", "error")
            self.reject(); return
        self.input_name.setText(data.get("name") or "")
        self._set_combo(self.cmb_martial_art, data.get("id_martial_art"))
        self._set_combo(self.cmb_instructor,  data.get("id_instructor"))
        self._set_combo(self.cmb_day,    data.get("day_of_week"))
        self._set_combo(self.cmb_status, data.get("status") or "active")
        repeat = data.get("repeat_type") or "weekly"
        self._on_freq_change(repeat if repeat in ("weekly","multi_day","once") else "weekly")
        if data.get("start_time"):
            self.start_time_value = QTime(data["start_time"].hour, data["start_time"].minute)
        if data.get("end_time"):
            self.end_time_value = QTime(data["end_time"].hour, data["end_time"].minute)
        self._refresh_time_buttons()
        self.spin_capacity.setValue(int(data.get("capacity") or 0))
        self.input_location.setText(data.get("location") or "")
        self.selected_color = data.get("color") or BLUE
        self._refresh_color_btn()
        self._update_preview()

    def _set_combo(self, combo, value):
        idx = combo.findData(value)
        if idx >= 0: combo.setCurrentIndex(idx)

    def _save(self):
        name = self.input_name.text().strip()
        if not name:
            self._toast("El nombre de la clase es obligatorio.", "warning"); return
        if self.cmb_martial_art.currentData() is None:
            self._toast("Selecciona un arte marcial.", "warning"); return
        if self.end_time_value <= self.start_time_value:
            self._toast("La hora de fin debe ser mayor que la hora de inicio.", "warning"); return

        cap = self.spin_capacity.value()
        data = {
            "name":          name,
            "id_martial_art": self.cmb_martial_art.currentData(),
            "id_instructor":  self.cmb_instructor.currentData(),
            "day_of_week":    self.cmb_day.currentData() if self._current_freq != "multi_day" else None,
            "start_time":     self.start_time_value.toString("HH:mm"),
            "end_time":       self.end_time_value.toString("HH:mm"),
            "capacity":       cap if cap > 0 else None,
            "location":       self.input_location.text().strip() or None,
            "color":          self.selected_color,
            "status":         "active",
            "repeat_type":    self._current_freq,
        }
        try:
            if self._current_freq == "multi_time" and not self.schedule_id:
                day_val = self.cmb_day_mt.currentData() if hasattr(self, "cmb_day_mt") else data["day_of_week"]
                if not hasattr(self, "_mt_franjas") or not self._mt_franjas:
                    self._toast("Agrega al menos un horario.", "warning"); return
                for i, (t_start, t_end) in enumerate(self._mt_franjas):
                    if t_end <= t_start:
                        self._toast(f"Horario {i+1}: la hora fin debe ser mayor que la hora inicio.", "warning")
                        return
                    entry = {**data,
                        "day_of_week": day_val,
                        "start_time":  t_start.toString("HH:mm"),
                        "end_time":    t_end.toString("HH:mm"),
                        "repeat_type": "weekly",
                    }
                    self.repo.create_schedule(entry)
            elif self.schedule_id:
                self.repo.update_schedule(self.schedule_id, data)
            else:
                self.repo.create_schedule(data)
            self.accept()
        except Exception as e:
            self._toast(f"No se pudo guardar: {e}", "error")

    def _open_instructions(self):
        from PyQt6.QtWidgets import QScrollArea
        dlg = QDialog(self)
        dlg.setWindowTitle("Instrucciones — Formulario de clases")
        dlg.setMinimumSize(640, 660)
        dlg.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        dlg.setStyleSheet(f"background:{BG_DIALOG}; color:{TEXT_PRI};")

        root = QVBoxLayout(dlg)
        root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        # Header
        hdr_f = QFrame(); hdr_f.setFixedHeight(80)
        hdr_f.setStyleSheet(f"""
            QFrame {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 rgba(225,29,72,0.15), stop:1 {BG_CARD});
                border-bottom: 1px solid rgba(225,29,72,0.2); }}
            QFrame * {{ background: transparent; border: none; }}
        """)
        hl = QHBoxLayout(hdr_f); hl.setContentsMargins(24,0,24,0); hl.setSpacing(14)
        ic_f = QFrame(); ic_f.setFixedSize(44,44)
        ic_f.setStyleSheet(f"background:rgba(225,29,72,0.12);border:1px solid rgba(225,29,72,0.35);border-radius:12px;")
        ic_l = QHBoxLayout(ic_f); ic_l.setContentsMargins(0,0,0,0)
        ic_l.addWidget(IconLabel("instructions",22,RED), 0, Qt.AlignmentFlag.AlignCenter)
        ttl_col = QVBoxLayout(); ttl_col.setSpacing(3)
        t1 = QLabel("Guía completa — Formulario de clases")
        t1.setStyleSheet(f"color:{TEXT_PRI};font-size:16px;font-weight:900;font-family:'Inter';")
        t2 = QLabel("Todo lo que necesitas saber para registrar y programar clases correctamente")
        t2.setStyleSheet(f"color:{TEXT_MUT};font-size:11px;")
        ttl_col.addWidget(t1); ttl_col.addWidget(t2)
        btn_cls = QPushButton(); btn_cls.setFixedSize(30,30)
        btn_cls.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cls.setStyleSheet(f"QPushButton{{background:rgba(255,255,255,0.05);border:1px solid {BORDER};border-radius:8px;}}QPushButton:hover{{background:rgba(255,255,255,0.10);}}QPushButton *{{background:transparent;border:none;}}")
        cl = QHBoxLayout(btn_cls); cl.setContentsMargins(0,0,0,0)
        cl.addWidget(IconLabel("x",12,TEXT_SEC),0,Qt.AlignmentFlag.AlignCenter)
        btn_cls.clicked.connect(dlg.close)
        hl.addWidget(ic_f); hl.addLayout(ttl_col,1); hl.addWidget(btn_cls,0,Qt.AlignmentFlag.AlignTop)
        root.addWidget(hdr_f)

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}QScrollBar:vertical{background:transparent;width:6px;}QScrollBar::handle:vertical{background:#2A2A2A;border-radius:3px;}")
        sc_w = QWidget(); sc_w.setStyleSheet("background:transparent;")
        sc_l = QVBoxLayout(sc_w); sc_l.setContentsMargins(24,20,24,20); sc_l.setSpacing(14)

        sections = [
            ("tag", RED, "Nombre de la clase",
             "El nombre identifica la clase en el calendario. Debe ser claro y describir el arte marcial, el nivel y el grupo.",
             [("✓", GREEN, "BJJ Adultos · Intermedio"),
              ("✓", GREEN, "Karate Infantil — Grupo A"),
              ("✓", GREEN, "Kickboxing Mañana / Kickboxing Tarde  (clases diferentes)"),
              ("✗", "#FF4444", "clase  /  entreno  /  cosa del martes")]),

            ("users", BLUE, "Arte marcial e Instructor",
             "Selecciona el arte marcial que se dicta y el instructor responsable. Si el instructor varía cada semana, elige «Sin instructor fijo» y asígnalo al registrar la asistencia.",
             [("Tip", YELLOW, "Un mismo instructor puede dictar varias artes marciales en el mismo día")]),

            ("repeat", GREEN, "Frecuencia — ¿Cómo se repite la clase?",
             "Este es el campo más importante. Elige cómo se repite la clase:",
             [("Semanal fija",  BLUE,    "La clase se dicta el mismo día cada semana. Ej: Karate todos los Lunes a las 6pm"),
              ("Varios días",   PURPLE,  "La clase se dicta en múltiples días de la semana. Ej: BJJ Martes y Jueves a las 7pm"),
              ("Mismo día",      RED,     "Úsalo cuando una misma clase tiene varios horarios el mismo día. Selecciona el día y agrega de 1 a 5 horarios; cada horario crea una entrada independiente en el calendario."),
              ("Una sola vez",  YELLOW,  "Clase especial que no se repetirá. Ej: BJJ Kids — solo se dictó una vez")]),

            ("clock", YELLOW, "Horario",
             "Selecciona la hora de inicio y fin de la clase. Haz clic en el botón de hora para abrir el reloj interactivo. Puedes seleccionar cualquier minuto arrastrando el puntero.",
             [("Tip", YELLOW, "La hora fin debe ser siempre mayor que la hora inicio"),
              ("Mismo día", RED, "Cada bloque llamado «Horario 1», «Horario 2», etc. tiene su propia hora de inicio y fin. Usa «Agregar horario» para incluir otro turno y el botón menos para quitarlo."),
              ("Vista previa", TEXT_MUT, "Todos los horarios aparecerán en líneas separadas para que puedas comprobarlos antes de guardar.")]),

            ("building", TEXT_SEC, "Ubicación y capacidad",
             "Indica en qué espacio físico se dicta la clase y cuántos estudiantes puede recibir.",
             [("Ejemplos", TEXT_SEC, "«Tatami principal»  ·  «Sala 2»  ·  «Cancha sur»"),
              ("Capacidad 0", TEXT_MUT, "Deja la capacidad en 0 si no quieres limitar el número de participantes")]),

            ("palette", PURPLE, "Color del bloque",
             "El color identifica visualmente la clase en el calendario. Te recomendamos un código de colores por arte marcial.",
             [("Sugerencia", TEXT_SEC, "Azul → BJJ  ·  Rojo → Karate  ·  Verde → Kickboxing  ·  Amarillo → Taekwondo")]),

        ]

        for icon_name, icon_color, title_text, desc_text, examples in sections:
            sec = QFrame()
            sec.setStyleSheet(f"""
                QFrame {{ background:{BG_CARD}; border:1px solid {BORDER};
                    border-left:3px solid {icon_color}; border-radius:12px; }}
                QFrame * {{ background:transparent; border:none; }}
            """)
            sl = QVBoxLayout(sec); sl.setContentsMargins(16,14,16,14); sl.setSpacing(10)
            th = QHBoxLayout(); th.setSpacing(9)
            th.addWidget(IconLabel(icon_name, 15, icon_color))
            t_lbl = QLabel(title_text)
            t_lbl.setStyleSheet(f"color:{TEXT_PRI};font-size:13px;font-weight:900;font-family:'Inter';")
            th.addWidget(t_lbl, 1); sl.addLayout(th)
            d_lbl = QLabel(desc_text); d_lbl.setWordWrap(True)
            d_lbl.setStyleSheet(f"color:{TEXT_SEC};font-size:12px;")
            sl.addWidget(d_lbl)
            if examples:
                s_line = QFrame(); s_line.setFixedHeight(1)
                s_line.setStyleSheet(f"background:{BORDER};min-height:1px;max-height:1px;")
                sl.addWidget(s_line)
                for tag, tag_color, ex_text in examples:
                    ex_row = QHBoxLayout(); ex_row.setSpacing(10); ex_row.setContentsMargins(4,0,0,0)
                    tag_f = QFrame(); tag_f.setFixedWidth(90)
                    tag_l = QHBoxLayout(tag_f); tag_l.setContentsMargins(0,0,0,0)
                    tag_lbl = QLabel(tag)
                    tag_lbl.setStyleSheet(f"color:{tag_color};font-size:10px;font-weight:900;")
                    tag_l.addWidget(tag_lbl)
                    ex_lbl = QLabel(ex_text); ex_lbl.setWordWrap(True)
                    ex_lbl.setStyleSheet(f"color:{TEXT_MUT};font-size:11px;font-style:italic;")
                    ex_row.addWidget(tag_f); ex_row.addWidget(ex_lbl,1)
                    sl.addLayout(ex_row)
            sc_l.addWidget(sec)

        sc_l.addStretch()
        scroll.setWidget(sc_w); root.addWidget(scroll,1)

        foot_f = QFrame(); foot_f.setFixedHeight(62)
        foot_f.setStyleSheet(f"QFrame{{background:{BG_CARD};border-top:1px solid {BORDER};}}")
        fl = QHBoxLayout(foot_f); fl.setContentsMargins(24,0,24,0)
        tip = QLabel("Puedes volver a abrir esta guía en cualquier momento desde el botón «Instrucciones»")
        tip.setStyleSheet(f"color:{TEXT_MUT};font-size:10px;"); tip.setWordWrap(True)
        btn_ok = QPushButton("Entendido")
        btn_ok.setFixedHeight(38); btn_ok.setMinimumWidth(110)
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"QPushButton{{background:{RED};color:white;border:none;border-radius:9px;font-size:13px;font-weight:800;padding:0 24px;}}QPushButton:hover{{background:{RED_H};}}")
        btn_ok.clicked.connect(dlg.accept)
        fl.addWidget(tip,1); fl.addWidget(btn_ok)
        root.addWidget(foot_f)
        dlg.exec()

    def _toast(self, msg, kind="info"):
        """Delegar al toast_manager global si está disponible, o print como fallback."""
        try:
            from core.toast import toast_manager
            toast_manager.show(msg, kind)
        except Exception:
            print(f"[ClassForm] {kind.upper()}: {msg}")