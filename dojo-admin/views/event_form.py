# ─── EVENT_FORM PREMIUM ──────────────────────────────────────────────
import math
from datetime import date

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QColorDialog,
    QCheckBox, QWidget, QFrame, QScrollArea, QSizePolicy,
    QCalendarWidget,
)
from PyQt6.QtCore import Qt, QDate, QTime, QPointF, QRectF, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen, QFont

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
CLOCK_BG   = "#0E0E0E"
CLOCK_RING = "#1A1A1A"

INPUT_STYLE = f"""
    QLineEdit, QComboBox, QTextEdit, QDateEdit {{
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
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDateEdit:focus {{
        border-color: {RED};
        background: {BG_HOVER};
    }}
    QLineEdit:hover, QComboBox:hover, QDateEdit:hover {{
        border-color: #444;
    }}
    QComboBox::drop-down {{ border: none; width: 28px; background: transparent; }}
    QComboBox QAbstractItemView {{
        background: {BG_INPUT}; color: {TEXT_PRI};
        selection-background-color: {RED};
        border: 1px solid {BORDER}; border-radius: 8px; padding: 4px;
        outline: none;
    }}
    QDateEdit::drop-down {{ border: none; width: 28px; background: transparent; }}
"""


# ═══════════════════════════════════════════════════════════════════
# SVG IconLabel
# ═══════════════════════════════════════════════════════════════════
class IconLabel(QWidget):
    ICONS = {
        "calendar":   '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
        "clock":      '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
        "map-pin":    '<line x1="12" y1="21" x2="12" y2="13"/><circle cx="12" cy="9" r="4"/><ellipse cx="12" cy="21" rx="2" ry="1"/>',
        "tag":        '<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/>',
        "star": '<polyline points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
        "palette":    '<circle cx="13.5" cy="6.5" r=".5"/><circle cx="17.5" cy="10.5" r=".5"/><circle cx="8.5" cy="7.5" r=".5"/><circle cx="6.5" cy="12.5" r=".5"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>',
        "save":       '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>',
        "trash":      '<polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>',
        "x":          '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
        "info":       '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
        "zap":        '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
        "align-left": '<line x1="17" y1="10" x2="3" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="17" y1="18" x2="3" y2="18"/>',
        "check-circle": '<circle cx="12" cy="12" r="10"/><polyline points="9 12 11 14 15 10"/>',
        "help-circle":'<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><circle cx="12" cy="8" r="1"/>',
        "alert-star":   '<path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z"/>',
    }

    def __init__(self, icon_name, size=18, color=TEXT_SEC, parent=None):
        super().__init__(parent)
        self._icon  = icon_name
        self._size  = size
        self._color = color
        self.setFixedSize(size, size)

    def set_color(self, c): self._color = c; self.update()

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
            p.setPen(pen)
            if getattr(self, "_filled", False):
                p.setBrush(QColor(self._color))
            else:
                p.setBrush(Qt.BrushStyle.NoBrush)
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
                        else: i+=1
                    p.drawPath(path)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════
# ClockFace + TimePickerDialog
# ═══════════════════════════════════════════════════════════════════
class ClockFace(QWidget):
    time_changed = pyqtSignal(int, int)
    released     = pyqtSignal()

    def __init__(self, mode="hour", parent=None):
        super().__init__(parent)
        self.mode            = mode
        self.selected_hour   = 8
        self.selected_minute = 0
        self.accent          = RED
        self._dragging       = False
        self.setMinimumSize(240, 240)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_mode(self, mode):      self.mode = mode; self.update()
    def set_time_values(self, h, m): self.selected_hour = h; self.selected_minute = m; self.update()

    def _angle_to_value(self, pos):
        cx, cy = self.width()/2, self.height()/2
        dx, dy = pos.x()-cx, pos.y()-cy
        angle  = math.degrees(math.atan2(dx, -dy))
        if angle < 0: angle += 360
        if self.mode == "hour":
            idx = int(round(angle/30)) % 12
            return [12,1,2,3,4,5,6,7,8,9,10,11][idx], None
        return None, int(round(angle/6)) % 60

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        size = min(w,h)-8; cx,cy = w/2, h/2; radius = size/2
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(CLOCK_BG))
        p.drawEllipse(QPointF(cx,cy), radius, radius)
        p.setPen(QPen(QColor(CLOCK_RING),2)); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(cx,cy), radius-1, radius-1)
        if self.mode == "minute":
            for m in range(60):
                ang = math.radians(m*6-90)
                r_outer = radius-8; r_inner = radius-(14 if m%5==0 else 10)
                p.setPen(QPen(QColor(BORDER_2 if m%5!=0 else "#333"), 1 if m%5!=0 else 1.5))
                p.drawLine(QPointF(cx+math.cos(ang)*r_inner, cy+math.sin(ang)*r_inner),
                           QPointF(cx+math.cos(ang)*r_outer, cy+math.sin(ang)*r_outer))
        p.setFont(QFont("Inter",10,QFont.Weight.Bold))
        tr = radius-34
        values = [12,1,2,3,4,5,6,7,8,9,10,11] if self.mode=="hour" else [0,5,10,15,20,25,30,35,40,45,50,55]
        sel_val = self.selected_hour if self.mode=="hour" else (self.selected_minute//5)*5
        sel_x, sel_y = cx, cy
        for idx, val in enumerate(values):
            ang = math.radians(idx*30-90)
            x = cx+math.cos(ang)*tr; y = cy+math.sin(ang)*tr
            is_sel = (val == sel_val)
            if is_sel:
                sel_x,sel_y = x,y
                p.setBrush(QColor(self.accent)); p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(QPointF(x,y),20,20); p.setPen(QColor("white"))
            else: p.setPen(QColor(TEXT_SEC))
            lbl = f"{val:02d}" if self.mode=="minute" else str(val)
            p.drawText(QRectF(x-16,y-9,32,18), Qt.AlignmentFlag.AlignCenter, lbl)
        if self.mode=="minute":
            fa = math.radians(self.selected_minute*6-90)
            fx,fy = cx+math.cos(fa)*tr, cy+math.sin(fa)*tr
            p.setBrush(QColor(self.accent)); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(fx,fy),14,14); p.setPen(QColor("white"))
            p.setFont(QFont("Inter",9,QFont.Weight.Bold))
            p.drawText(QRectF(fx-14,fy-8,28,16), Qt.AlignmentFlag.AlignCenter, f"{self.selected_minute:02d}")
            sel_x,sel_y = fx,fy
        lp = QPen(QColor(self.accent),2); lp.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(lp); p.drawLine(QPointF(cx,cy), QPointF(sel_x,sel_y))
        p.setBrush(QColor(self.accent)); p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx,cy),5,5)

    def _update_from_pos(self, pos):
        hour, minute = self._angle_to_value(pos)
        changed = False
        if self.mode=="hour" and hour is not None:
            if hour!=self.selected_hour: self.selected_hour=hour; changed=True
        elif self.mode=="minute" and minute is not None:
            if minute!=self.selected_minute: self.selected_minute=minute; changed=True
        if changed: self.update(); self.time_changed.emit(self.selected_hour, self.selected_minute)

    def mousePressEvent(self, ev):
        if ev.button()==Qt.MouseButton.LeftButton: self._dragging=True; self._update_from_pos(ev.position())
        super().mousePressEvent(ev)
    def mouseMoveEvent(self, ev):
        if self._dragging: self._update_from_pos(ev.position())
        super().mouseMoveEvent(ev)
    def mouseReleaseEvent(self, ev):
        self._dragging=False
        if ev.button()==Qt.MouseButton.LeftButton: self.released.emit()
        super().mouseReleaseEvent(ev)


class TimePickerDialog(QDialog):
    def __init__(self, initial_time=None, title="Hora", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(340, 500)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background: {BG_DIALOG}; color: {TEXT_PRI};")
        t = initial_time or QTime(8,0)
        self.is_pm=t.hour()>=12; self.hour_12=t.hour()%12 or 12; self.minute=t.minute(); self.mode="hour"
        self._build_ui(); self._refresh()

    def _build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(20,20,20,20); root.setSpacing(14)
        lbl_t = QLabel("Seleccionar hora"); lbl_t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_t.setStyleSheet(f"color:{TEXT_PRI};font-size:14px;font-weight:900;font-family:'Inter';border:none;")
        root.addWidget(lbl_t)
        disp=QHBoxLayout(); disp.setAlignment(Qt.AlignmentFlag.AlignCenter); disp.setSpacing(6)
        def _tb(w,h):
            b=QPushButton(); b.setFixedSize(w,h); b.setCursor(Qt.CursorShape.PointingHandCursor); return b
        self.btn_h=_tb(72,62); self.btn_h.clicked.connect(lambda:self._set_mode("hour"))
        sep=QLabel(":"); sep.setStyleSheet(f"color:{TEXT_PRI};font-size:32px;font-weight:900;border:none;background:transparent;")
        self.btn_m=_tb(72,62); self.btn_m.clicked.connect(lambda:self._set_mode("minute"))
        self.btn_ap=_tb(52,62); self.btn_ap.clicked.connect(self._toggle_ampm)
        disp.addWidget(self.btn_h); disp.addWidget(sep); disp.addWidget(self.btn_m); disp.addWidget(self.btn_ap)
        root.addLayout(disp)
        self.lbl_mode=QLabel("HORA"); self.lbl_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_mode.setStyleSheet(f"color:{TEXT_MUT};font-size:10px;font-weight:900;letter-spacing:1px;border:none;")
        root.addWidget(self.lbl_mode)
        self.clock=ClockFace("hour",self); self.clock.time_changed.connect(self._on_clock_change)
        self.clock.released.connect(self._on_clock_released)
        root.addWidget(self.clock, 0, Qt.AlignmentFlag.AlignCenter)
        foot=QHBoxLayout(); foot.setSpacing(10)
        btn_c=QPushButton("Cancelar"); btn_c.setFixedHeight(38); btn_c.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_c.setStyleSheet(f"QPushButton{{background:transparent;color:{TEXT_SEC};border:1px solid {BORDER};border-radius:9px;font-size:12px;font-weight:700;}}QPushButton:hover{{color:{TEXT_PRI};border-color:#444;}}")
        btn_c.clicked.connect(self.reject)
        btn_ok=QPushButton("Confirmar"); btn_ok.setFixedHeight(38); btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"QPushButton{{background:{RED};color:white;border:none;border-radius:9px;font-size:12px;font-weight:800;}}QPushButton:hover{{background:{RED_H};}}")
        btn_ok.clicked.connect(self.accept)
        foot.addWidget(btn_c); foot.addWidget(btn_ok); root.addLayout(foot)

    def _set_mode(self, mode): self.mode=mode; self.clock.set_mode(mode); self.clock.set_time_values(self.hour_12,self.minute); self._refresh()
    def _toggle_ampm(self): self.is_pm=not self.is_pm; self._refresh()
    def _on_clock_change(self,h,m): self.hour_12=h; self.minute=m; self._refresh()
    def _on_clock_released(self):
        if self.mode=="hour": QTimer.singleShot(180, lambda: self._set_mode("minute"))
    def _refresh(self):
        self.clock.set_time_values(self.hour_12, self.minute)
        act=f"QPushButton{{background:{RED_DARK};color:{RED};border:1.5px solid {RED};border-radius:9px;font-size:26px;font-weight:900;font-family:'Inter';}}"
        ina=f"QPushButton{{background:{BG_INPUT};color:{TEXT_SEC};border:1px solid {BORDER};border-radius:9px;font-size:26px;font-weight:900;font-family:'Inter';}}QPushButton:hover{{border-color:#444;color:{TEXT_PRI};}}"
        amp=f"QPushButton{{background:{BG_INPUT};color:{RED};border:1px solid {BORDER};border-radius:9px;font-size:13px;font-weight:900;font-family:'Inter';}}QPushButton:hover{{border-color:{RED};color:{RED};}}"
        self.btn_h.setText(f"{self.hour_12:02d}"); self.btn_m.setText(f"{self.minute:02d}")
        self.btn_ap.setText("PM" if self.is_pm else "AM")
        self.btn_h.setStyleSheet(act if self.mode=="hour" else ina)
        self.btn_m.setStyleSheet(act if self.mode=="minute" else ina)
        self.btn_ap.setStyleSheet(amp)
        self.lbl_mode.setText("HORAS" if self.mode=="hour" else "MINUTOS")
    def selected_time(self) -> QTime:
        h = self.hour_12 % 12
        if self.is_pm: h += 12
        return QTime(h, self.minute)


# ═══════════════════════════════════════════════════════════════════
# Helpers de layout
# ═══════════════════════════════════════════════════════════════════
def _card(accent_left=None) -> QFrame:
    frame = QFrame()
    bl = f"border-left: 3px solid {accent_left};" if accent_left else ""
    frame.setStyleSheet(f"""
        QFrame {{ background:{BG_CARD}; border:1px solid {BORDER}; {bl} border-radius:14px; }}
        QFrame * {{ background:transparent; border:none; }}
    """)
    return frame

def _section_label(text, color=TEXT_MUT) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color:{color};font-size:10px;font-weight:900;font-family:'Inter';letter-spacing:1px;")
    return lbl

def _field_label(text) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color:{TEXT_MUT};font-size:11px;font-weight:700;font-family:'Inter';")
    return lbl

def _sep(layout):
    s = QFrame(); s.setFixedHeight(1)
    s.setStyleSheet(f"background:{BORDER};border:none;min-height:1px;max-height:1px;")
    layout.addWidget(s)


# ═══════════════════════════════════════════════════════════════════
# DatePickerDialog — replica exacta del student_form premium
# ═══════════════════════════════════════════════════════════════════

CAL_STYLE_EVENT = f"""
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
        font-family: 'Inter';
        gridline-color: transparent;
        outline: none;
    }}
    QCalendarWidget QAbstractItemView:disabled {{
        color: #333333;
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background-color: {BG_DIALOG};
        border-bottom: 1px solid {BORDER};
        padding: 6px 8px;
        min-height: 48px;
    }}
    QCalendarWidget QToolButton {{
        background-color: transparent;
        color: {TEXT_PRI};
        font-size: 13px;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 6px 10px;
        min-width: 32px;
        min-height: 32px;
        font-family: 'Inter';
    }}
    QCalendarWidget QToolButton:hover {{
        background-color: rgba(255,255,255,0.07);
        border: 1px solid {BORDER};
    }}
    QCalendarWidget QToolButton::menu-indicator {{ image: none; }}
    QCalendarWidget QSpinBox {{
        background-color: {BG_INPUT};
        color: {TEXT_PRI};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 2px 8px;
        font-family: 'Inter';
        font-size: 13px;
        font-weight: 700;
    }}
    QCalendarWidget QSpinBox::up-button,
    QCalendarWidget QSpinBox::down-button {{
        width: 16px;
        background: transparent;
    }}
    QCalendarWidget QMenu {{
        background-color: {BG_INPUT};
        color: {TEXT_PRI};
        border: 1px solid {BORDER};
        border-radius: 8px;
        font-size: 13px;
        font-family: 'Inter';
    }}
    QCalendarWidget QMenu::item:selected {{
        background-color: {RED};
        color: white;
    }}
    QCalendarWidget QHeaderView {{
        background: {BG_CARD};
        border: none;
    }}
    QCalendarWidget QHeaderView::section {{
        background-color: {BG_CARD};
        color: {TEXT_MUT};
        border: none;
        padding: 8px 0;
        font-size: 10px;
        font-weight: 900;
        font-family: 'Inter';
        letter-spacing: 0.5px;
    }}
"""

from PyQt6.QtGui import QTextCharFormat

class DatePickerDialog(QDialog):
    def __init__(self, current_date: QDate = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar fecha")
        self.setFixedSize(380, 440)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_DIALOG};
                border-radius: 16px;
            }}
        """)
        self._selected = current_date or QDate.currentDate()
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        hdr = QFrame()
        hdr.setFixedHeight(56)
        hdr.setStyleSheet(f"background:{BG_CARD}; border-bottom:1px solid {BORDER}; border-radius:0;")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(20, 0, 20, 0)
        hl.setSpacing(10)

        icon_frame = QFrame()
        icon_frame.setFixedSize(32, 32)
        icon_frame.setStyleSheet(f"background:rgba(225,29,72,0.12); border:1px solid rgba(225,29,72,0.3); border-radius:8px;")
        il = QHBoxLayout(icon_frame); il.setContentsMargins(0,0,0,0)
        il.addWidget(IconLabel("calendar", 16, RED), 0, Qt.AlignmentFlag.AlignCenter)

        lbl_title = QLabel("Seleccionar fecha")
        lbl_title.setStyleSheet(f"color:{TEXT_PRI}; font-size:14px; font-weight:800; font-family:'Inter'; border:none;")

        hl.addWidget(icon_frame)
        hl.addWidget(lbl_title, 1)
        root.addWidget(hdr)

        cal_container = QWidget()
        cal_container.setStyleSheet(f"background:{BG_DIALOG};")
        cal_vl = QVBoxLayout(cal_container)
        cal_vl.setContentsMargins(16, 16, 16, 8)

        self.cal = QCalendarWidget()
        self.cal.setSelectedDate(self._selected)
        self.cal.setGridVisible(False)
        self.cal.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.cal.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
        self.cal.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        self.cal.setStyleSheet(CAL_STYLE_EVENT)

        fmt_weekend = QTextCharFormat()
        fmt_weekend.setForeground(QColor(RED))
        self.cal.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, fmt_weekend)
        self.cal.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, fmt_weekend)

        self.cal.activated.connect(lambda d: self._confirm())

        cal_vl.addWidget(self.cal)
        root.addWidget(cal_container, 1)

        sep = QFrame(); sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{BORDER}; border:none;")
        root.addWidget(sep)

        foot = QFrame()
        foot.setFixedHeight(62)
        foot.setStyleSheet(f"background:{BG_CARD}; border:none;")
        fl = QHBoxLayout(foot)
        fl.setContentsMargins(20, 0, 20, 0)
        fl.setSpacing(10)

        btn_today = QPushButton("Hoy")
        btn_today.setFixedHeight(36)
        btn_today.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_today.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 8px;
                font-size: 12px; font-weight: 700;
                font-family: 'Inter'; padding: 0 14px;
            }}
            QPushButton:hover {{ color:{TEXT_PRI}; border-color:#444; }}
        """)
        btn_today.clicked.connect(lambda: self.cal.setSelectedDate(QDate.currentDate()))

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 8px;
                font-size: 12px; font-weight: 700;
                font-family: 'Inter'; padding: 0 14px;
            }}
            QPushButton:hover {{ color:{TEXT_PRI}; border-color:#444; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("Confirmar")
        btn_ok.setFixedHeight(36)
        btn_ok.setMinimumWidth(110)
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background: {RED}; color: white; border: none;
                border-radius: 8px; font-size: 13px; font-weight: 800;
                font-family: 'Inter'; padding: 0 20px;
            }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        btn_ok.clicked.connect(self._confirm)

        fl.addWidget(btn_today)
        fl.addStretch()
        fl.addWidget(btn_cancel)
        fl.addWidget(btn_ok)
        root.addWidget(foot)

    def _confirm(self):
        self._selected = self.cal.selectedDate()
        self.accept()

    def selected_date(self) -> QDate:
        return self._selected


# ═══════════════════════════════════════════════════════════════════
# EventForm Premium
# ═══════════════════════════════════════════════════════════════════
class EventForm(QDialog):
    def __init__(self, repo, event_id=None, default_date=None, parent=None):
        super().__init__(parent)
        self.repo          = repo
        self.event_id      = event_id
        self.default_date  = default_date or date.today()
        self.selected_color = BLUE
        self.start_time_value = QTime(0, 0)
        self.end_time_value   = QTime(0, 0)
        self._use_time        = False

        self.setWindowTitle("Evento")
        self.setMinimumSize(820, 600)
        self.resize(860, 640)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background:{BG_DIALOG}; color:{TEXT_PRI};")

        self._build_ui()
        if self.event_id:
            self._load_data()
        else:
            self._apply_defaults()
        self._update_preview()

    # ── Build UI ──────────────────────────────────────────────────
    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0,0,0,0)
        outer.setSpacing(0)

        # ── LEFT scroll ───────────────────────────────────────────
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setStyleSheet("""
            QScrollArea { border:none; background:transparent; }
            QScrollBar:vertical { background:transparent; width:6px; }
            QScrollBar::handle:vertical { background:#2A2A2A; border-radius:3px; }
        """)
        left_w = QWidget(); left_w.setStyleSheet("background:transparent;")
        left = QVBoxLayout(left_w)
        left.setContentsMargins(24,24,24,24); left.setSpacing(16)

        # Header
        hdr = QHBoxLayout(); hdr.setSpacing(12)
        icon_frame = QFrame(); icon_frame.setFixedSize(42,42)
        icon_frame.setStyleSheet(f"background:{RED_GLOW};border:1px solid rgba(225,29,72,0.3);border-radius:10px;")
        il = QHBoxLayout(icon_frame); il.setContentsMargins(0,0,0,0)
        il.addWidget(IconLabel("zap",20,RED), 0, Qt.AlignmentFlag.AlignCenter)
        title_col = QVBoxLayout(); title_col.setSpacing(2)
        is_edit = bool(self.event_id)
        lbl_title = QLabel("Editar evento" if is_edit else "Nuevo evento")
        lbl_title.setStyleSheet(f"color:{TEXT_PRI};font-size:18px;font-weight:900;font-family:'Inter';")
        lbl_sub = QLabel("Modifica los datos del evento" if is_edit else "Completa los datos para registrar el evento")
        lbl_sub.setStyleSheet(f"color:{TEXT_MUT};font-size:12px;font-weight:500;")
        title_col.addWidget(lbl_title); title_col.addWidget(lbl_sub)
        hdr.addWidget(icon_frame); hdr.addLayout(title_col,1)

        btn_help = QPushButton()
        btn_help.setFixedHeight(34)
        btn_help.setMinimumWidth(130)
        btn_help.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_help.setStyleSheet(f"""
            QPushButton {{
                background: rgba(59,130,246,0.12);
                color: {BLUE};
                border: 1px solid rgba(59,130,246,0.35);
                border-radius: 9px;
                font-size: 11px;
                font-weight: 800;
                font-family: 'Inter';
            }}
            QPushButton:hover {{
                background: rgba(59,130,246,0.22);
                border-color: {BLUE};
            }}
            QPushButton * {{ background: transparent; border: none; }}
        """)
        btn_help_hl = QHBoxLayout(btn_help)
        btn_help_hl.setContentsMargins(12, 0, 12, 0)
        btn_help_hl.setSpacing(7)
        btn_help_hl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_help_hl.addWidget(IconLabel("help-circle", 14, BLUE))
        btn_help_lbl = QLabel("Instrucciones")
        btn_help_lbl.setStyleSheet(f"color:{BLUE};font-size:11px;font-weight:800;border:none;")
        btn_help_hl.addWidget(btn_help_lbl)
        btn_help.clicked.connect(self._open_instructions)
        hdr.addWidget(btn_help, 0, Qt.AlignmentFlag.AlignVCenter)

        left.addLayout(hdr)

        # ── Card 1: Info General ──────────────────────────────────
        card1 = _card(RED)
        c1l = QVBoxLayout(card1); c1l.setContentsMargins(18,16,18,16); c1l.setSpacing(14)
        c1l.addWidget(_section_label("INFORMACIÓN GENERAL"))
        _sep(c1l)

        c1l.addWidget(_field_label("Nombre del evento *"))
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ej: Torneo regional · Examen de grado")
        self.input_name.setStyleSheet(INPUT_STYLE)
        self.input_name.textChanged.connect(self._update_preview)
        c1l.addWidget(self.input_name)

        row1 = QHBoxLayout(); row1.setSpacing(14)
        col_type = QVBoxLayout(); col_type.setSpacing(6)
        col_type.addWidget(_field_label("Tipo de evento"))
        self.cmb_type = QComboBox(); self.cmb_type.setStyleSheet(INPUT_STYLE)
        self.cmb_type.addItem("Torneo",          "torneo")
        self.cmb_type.addItem("Examen de grado", "examen")
        self.cmb_type.addItem("Seminario",        "seminario")
        self.cmb_type.addItem("Festivo",          "festivo")
        self.cmb_type.addItem("Otro",             "otro")
        self.cmb_type.currentIndexChanged.connect(self._update_preview)
        col_type.addWidget(self.cmb_type)
        self.input_custom_type = QLineEdit()
        self.input_custom_type.setPlaceholderText("Describe el tipo de evento...")
        self.input_custom_type.setStyleSheet(INPUT_STYLE)
        self.input_custom_type.hide()
        col_type.addWidget(self.input_custom_type)
        self.cmb_type.currentIndexChanged.connect(self._on_type_changed)
        row1.addLayout(col_type,1)

        col_date = QVBoxLayout(); col_date.setSpacing(6)
        col_date.addWidget(_field_label("Fecha del evento"))
        self._current_date = QDate.currentDate()
        self.btn_date = QPushButton()
        self.btn_date.setFixedHeight(42)
        self.btn_date.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_date.setStyleSheet(f"""
            QPushButton {{
                background: {BG_INPUT};
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                font-family: 'Inter';
                text-align: left;
                padding: 0 14px;
            }}
            QPushButton:hover {{ border-color: #444; background: {BG_HOVER}; }}
            QPushButton:focus {{ border-color: {RED}; }}
            QPushButton * {{ background: transparent; border: none; }}
        """)
        btn_date_hl = QHBoxLayout(self.btn_date)
        btn_date_hl.setContentsMargins(14, 0, 14, 0)
        btn_date_hl.setSpacing(10)
        self._btn_date_lbl = QLabel(self._current_date.toString("dd/MM/yyyy"))
        self._btn_date_lbl.setStyleSheet(f"color:{TEXT_PRI};font-size:13px;font-weight:600;border:none;background:transparent;")
        btn_date_hl.addWidget(self._btn_date_lbl, 1)
        btn_date_hl.addWidget(IconLabel("calendar", 15, TEXT_MUT))
        self.btn_date.clicked.connect(self._open_date_picker)
        col_date.addWidget(self.btn_date)
        row1.addLayout(col_date, 1)
        c1l.addLayout(row1)

        left.addWidget(card1)

        # ── Card 2: Horario ───────────────────────────────────────
        card2 = _card(BLUE)
        c2l = QVBoxLayout(card2); c2l.setContentsMargins(18,16,18,16); c2l.setSpacing(14)
        c2l.addWidget(_section_label("HORARIO"))
        _sep(c2l)

        toggle_row = QHBoxLayout(); toggle_row.setSpacing(10)
        self.chk_has_time = QCheckBox()
        self.chk_has_time.setStyleSheet(f"""
            QCheckBox::indicator {{ width:20px; height:20px; border-radius:6px;
                border:1.5px solid {BORDER_2}; background:{BG_INPUT}; }}
            QCheckBox::indicator:checked {{ background:{BLUE}; border-color:{BLUE}; }}
        """)
        self.chk_has_time.stateChanged.connect(self._toggle_time)
        lbl_toggle = QLabel("Activar horario")
        lbl_toggle.setStyleSheet(f"color:{TEXT_SEC};font-size:12px;font-weight:700;")
        toggle_row.addWidget(self.chk_has_time)
        toggle_row.addWidget(lbl_toggle)
        toggle_row.addStretch()
        c2l.addLayout(toggle_row)

        row2 = QHBoxLayout(); row2.setSpacing(14)
        col_start = QVBoxLayout(); col_start.setSpacing(6)
        col_start.addWidget(_field_label("Hora inicio"))
        self.btn_time_start = QPushButton()
        self.btn_time_start.setFixedHeight(42)
        self.btn_time_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_time_start.clicked.connect(lambda: self._open_time("start"))
        col_start.addWidget(self.btn_time_start)
        row2.addLayout(col_start,1)

        col_end = QVBoxLayout(); col_end.setSpacing(6)
        col_end.addWidget(_field_label("Hora fin"))
        self.btn_time_end = QPushButton()
        self.btn_time_end.setFixedHeight(42)
        self.btn_time_end.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_time_end.clicked.connect(lambda: self._open_time("end"))
        col_end.addWidget(self.btn_time_end)
        row2.addLayout(col_end,1)

        self._time_row_widget = QWidget()
        self._time_row_widget.setLayout(row2)
        self._time_row_widget.setEnabled(False)
        self._time_row_widget.setStyleSheet("opacity: 0.4;")
        c2l.addWidget(self._time_row_widget)
        self._refresh_time_buttons()
        left.addWidget(card2)

        # ── Card 3: Detalles ──────────────────────────────────────
        card3 = _card(YELLOW)
        c3l = QVBoxLayout(card3); c3l.setContentsMargins(18,16,18,16); c3l.setSpacing(14)
        c3l.addWidget(_section_label("DETALLES ADICIONALES"))
        _sep(c3l)

        row3 = QHBoxLayout(); row3.setSpacing(14)
        col_loc = QVBoxLayout(); col_loc.setSpacing(6)
        col_loc.addWidget(_field_label("Ubicación"))
        self.input_location = QLineEdit()
        self.input_location.setPlaceholderText("Ej: Dojo principal · Coliseo")
        self.input_location.setStyleSheet(INPUT_STYLE)
        self.input_location.textChanged.connect(self._update_preview)
        col_loc.addWidget(self.input_location)
        row3.addLayout(col_loc,2)

        col_imp = QVBoxLayout(); col_imp.setSpacing(6)
        col_imp.addWidget(_field_label("Marcar como importante"))
        self.chk_important = QCheckBox()
        self.chk_important.setStyleSheet(f"""
            QCheckBox::indicator {{ width:20px; height:20px; border-radius:6px;
                border:1.5px solid {BORDER_2}; background:{BG_INPUT}; }}
            QCheckBox::indicator:checked {{ background:{YELLOW}; border-color:{YELLOW}; }}
        """)
        self.chk_important.stateChanged.connect(self._update_preview)
        col_imp.addWidget(self.chk_important)
        row3.addLayout(col_imp,1)
        c3l.addLayout(row3)

        c3l.addWidget(_field_label("Descripción"))
        self.input_description = QTextEdit()
        self.input_description.setPlaceholderText("Descripción del evento, indicaciones, requisitos...")
        self.input_description.setFixedHeight(90)
        self.input_description.setStyleSheet(INPUT_STYLE + f"QTextEdit{{padding:10px 14px;}}")
        self.input_description.textChanged.connect(self._update_preview)
        c3l.addWidget(self.input_description)

        left.addWidget(card3)

        # ── Card 4: Color ─────────────────────────────────────────
        card4 = _card(PURPLE)
        c4l = QVBoxLayout(card4); c4l.setContentsMargins(18,16,18,16); c4l.setSpacing(14)
        c4l.addWidget(_section_label("COLOR DEL EVENTO"))
        _sep(c4l)
        c4l.addWidget(_field_label("Color de identificación"))
        self.btn_color = QPushButton()
        self.btn_color.setFixedHeight(42)
        self.btn_color.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_color.clicked.connect(self._select_color)
        c4l.addWidget(self.btn_color)
        left.addWidget(card4)

        left.addStretch()

        # Footer
        foot = QHBoxLayout(); foot.setSpacing(10)
        if self.event_id:
            btn_del = QPushButton()
            btn_del.setFixedHeight(42)
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setStyleSheet(f"""
                QPushButton{{background:transparent;color:#FF4444;border:1px solid rgba(255,68,68,0.3);border-radius:10px;font-size:13px;font-weight:700;padding:0 18px;}}
                QPushButton:hover{{background:rgba(255,68,68,0.10);}}
                QPushButton *{{background:transparent;border:none;}}
            """)
            del_hl = QHBoxLayout(btn_del); del_hl.setContentsMargins(14,0,14,0); del_hl.setSpacing(7)
            del_hl.addWidget(IconLabel("trash",16,"#FF4444"))
            del_lbl = QLabel("Eliminar"); del_lbl.setStyleSheet("color:#FF4444;font-size:13px;font-weight:700;border:none;")
            del_hl.addWidget(del_lbl)
            btn_del.clicked.connect(self._delete)
            foot.addWidget(btn_del)
        foot.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(42); btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton{{background:transparent;color:{TEXT_SEC};border:1px solid {BORDER};border-radius:10px;font-size:13px;font-weight:700;padding:0 20px;}}
            QPushButton:hover{{color:{TEXT_PRI};border-color:#444;background:{BG_HOVER};}}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton()
        btn_save.setFixedHeight(42)
        btn_save.setMinimumWidth(160)
        btn_save.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton{{
                background:{RED}; color:white; border:none;
                border-radius:10px; font-size:13px; font-weight:800;
            }}
            QPushButton:hover{{background:{RED_H};}}
            QPushButton *{{background:transparent; border:none;}}
        """)
        save_hl = QHBoxLayout(btn_save)
        save_hl.setContentsMargins(18, 0, 18, 0)
        save_hl.setSpacing(8)
        save_hl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        save_hl.addWidget(IconLabel("save", 16, "white"))
        save_lbl = QLabel("Guardar evento")
        save_lbl.setStyleSheet("color:white; font-size:13px; font-weight:800; border:none;")
        save_hl.addWidget(save_lbl)
        btn_save.clicked.connect(self._save)
        foot.addWidget(btn_cancel); foot.addWidget(btn_save)
        left.addLayout(foot)

        left_scroll.setWidget(left_w)
        outer.addWidget(left_scroll, 3)

        # ── RIGHT: Vista previa ───────────────────────────────────
        right = QFrame(); right.setFixedWidth(260)
        right.setStyleSheet(f"QFrame{{background:{BG_CARD_2};border-left:1px solid {BORDER};}}")
        rl = QVBoxLayout(right); rl.setContentsMargins(20,24,20,24); rl.setSpacing(16)

        prev_title = QLabel("VISTA PREVIA")
        prev_title.setStyleSheet(f"color:{TEXT_MUT};font-size:10px;font-weight:900;letter-spacing:1px;")
        rl.addWidget(prev_title)
        _sep(rl)

        self.preview_card = QFrame(); self.preview_card.setFixedHeight(110)
        self.preview_card.setStyleSheet(f"QFrame{{background:{BG_CARD};border-left:4px solid {self.selected_color};border-radius:10px;}}")
        pcl = QVBoxLayout(self.preview_card); pcl.setContentsMargins(14,10,14,10); pcl.setSpacing(4)
        self.prev_lbl_name = QLabel("Nombre del evento")
        self.prev_lbl_name.setStyleSheet(f"color:{TEXT_PRI};font-size:14px;font-weight:900;border:none;")
        self.prev_lbl_type = QLabel("Tipo")
        self.prev_lbl_type.setStyleSheet(f"color:{TEXT_SEC};font-size:11px;font-weight:700;border:none;")
        self.prev_lbl_date = QLabel("Fecha")
        self.prev_lbl_date.setStyleSheet(f"color:{TEXT_MUT};font-size:11px;border:none;")
        pcl.addWidget(self.prev_lbl_name); pcl.addWidget(self.prev_lbl_type); pcl.addWidget(self.prev_lbl_date)
        rl.addWidget(self.preview_card)

        def _info_row(icon_name, default_text):
            row = QHBoxLayout(); row.setSpacing(10)
            ic = IconLabel(icon_name,16,TEXT_MUT)
            lbl = QLabel(default_text); lbl.setStyleSheet(f"color:{TEXT_MUT};font-size:12px;border:none;")
            row.addWidget(ic); row.addWidget(lbl,1)
            return row, lbl

        row_time, self.prev_time = _info_row("clock",    "Sin horario")
        row_loc,  self.prev_loc  = _info_row("map-pin",  "Sin ubicación")
        row_imp,  self.prev_imp  = _info_row("star",     "Normal")
        self._prev_imp_icon = row_imp.itemAt(0).widget()

        rl.addLayout(row_time); rl.addLayout(row_loc); rl.addLayout(row_imp)

        rl.addStretch()

        self.prev_color_swatch = QFrame(); self.prev_color_swatch.setFixedHeight(8)
        self.prev_color_swatch.setStyleSheet(f"background:{self.selected_color};border-radius:4px;border:none;")
        rl.addWidget(self.prev_color_swatch)

        outer.addWidget(right, 0)
        self._refresh_color_btn()

    # ── Helpers ───────────────────────────────────────────────────
    def _refresh_time_buttons(self):
        enabled = self._use_time
        def _ts(active):
            return f"""
                QPushButton{{background:{'#1A1A1A' if active else BG_INPUT};color:{TEXT_PRI};
                    border:1px solid {BLUE if active else BORDER};border-radius:10px;
                    font-size:14px;font-weight:800;font-family:'Inter';padding:0 14px;}}
                QPushButton:hover{{border-color:{BLUE};background:#1A1A1A;}}
                QPushButton *{{background:transparent;border:none;}}
            """
        self.btn_time_start.setText(self.start_time_value.toString("hh:mm AP") if enabled else "——")
        self.btn_time_end.setText(self.end_time_value.toString("hh:mm AP") if enabled else "——")
        self.btn_time_start.setStyleSheet(_ts(enabled))
        self.btn_time_end.setStyleSheet(_ts(enabled))

    def _refresh_color_btn(self):
        self.btn_color.setText(self.selected_color)
        self.btn_color.setStyleSheet(f"""
            QPushButton{{background:{self.selected_color};color:white;border:none;
                border-radius:10px;font-size:12px;font-weight:800;}}
        """)

    def _toggle_time(self, state):
        self._use_time = bool(state)
        self._time_row_widget.setEnabled(self._use_time)
        self._refresh_time_buttons()
        self._update_preview()

    def _open_time(self, target):
        current = self.start_time_value if target == "start" else self.end_time_value
        dlg = TimePickerDialog(current, "Hora inicio" if target=="start" else "Hora fin", self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            sel = dlg.selected_time()
            if target == "start":
                self.start_time_value = sel
                if self.end_time_value <= self.start_time_value:
                    self.end_time_value = self.start_time_value.addSecs(3600)
            else:
                self.end_time_value = sel
            self._refresh_time_buttons()
            self._update_preview()

    def _select_color(self):
        color = QColorDialog.getColor(QColor(self.selected_color), self)
        if color.isValid():
            self.selected_color = color.name()
            self._refresh_color_btn()
            self._update_preview()

    def _on_type_changed(self, index):
        tipo = self.cmb_type.currentData()
        if tipo == "otro":
            self.input_custom_type.show()
            self.input_custom_type.setFocus()
        else:
            self.input_custom_type.hide()
            self.input_custom_type.clear()
        self._update_preview()

    def _update_preview(self):
        name = self.input_name.text().strip() or "Nombre del evento"
        self.prev_lbl_name.setText(name)

        type_map = {"torneo":"Torneo","examen":"Examen de grado","seminario":"Seminario","festivo":"Festivo"}
        tipo = self.cmb_type.currentData()
        if tipo == "otro":
            custom = self.input_custom_type.text().strip() if hasattr(self, "input_custom_type") else ""
            self.prev_lbl_type.setText(custom or "Otro")
        else:
            self.prev_lbl_type.setText(type_map.get(tipo, "—"))

        self.prev_lbl_date.setText(self._current_date.toString("dd MMM yyyy"))

        if self._use_time:
            self.prev_time.setText(
                f"{self.start_time_value.toString('hh:mm AP')} – {self.end_time_value.toString('hh:mm AP')}"
            )
        else:
            self.prev_time.setText("Sin horario")

        loc = self.input_location.text().strip() if hasattr(self, "input_location") else ""
        self.prev_loc.setText(loc or "Sin ubicación")

        imp = self.chk_important.isChecked() if hasattr(self, "chk_important") else False

        if imp:
            self.prev_imp.setText("Importante")
            self.prev_imp.setStyleSheet(
                f"color:{YELLOW}; font-size:12px; border:none; font-weight:900;"
            )
        else:
            self.prev_imp.setText("Normal")
            self.prev_imp.setStyleSheet(
                f"color:{TEXT_MUT}; font-size:12px; border:none; font-weight:400;"
            )

        if hasattr(self, "_prev_imp_icon"):
            self._prev_imp_icon.set_color(YELLOW if imp else TEXT_MUT)
            self._prev_imp_icon._filled = imp
            self._prev_imp_icon.update()

        imp_border = f"border-top: 1px solid rgba(245,158,11,0.4); border-right: 1px solid rgba(245,158,11,0.4); border-bottom: 1px solid rgba(245,158,11,0.4);" if imp else ""
        self.preview_card.setStyleSheet(
            f"QFrame{{background:{BG_CARD};"
            f"border-left:4px solid {self.selected_color};"
            f"border-radius:10px;"
            f"{imp_border}}}"
        )

        self.prev_color_swatch.setStyleSheet(
            f"background:{self.selected_color};border-radius:4px;border:none;"
        )

    def _open_date_picker(self):
        dlg = DatePickerDialog(self._current_date, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._current_date = dlg.selected_date()
            self._btn_date_lbl.setText(self._current_date.toString("dd/MM/yyyy"))
            self._update_preview()

    def _get_date(self) -> QDate:
        return self._current_date

    def _apply_defaults(self):
        self._current_date = QDate(self.default_date.year, self.default_date.month, self.default_date.day)
        self._btn_date_lbl.setText(self._current_date.toString("dd/MM/yyyy"))
        self._refresh_color_btn()

    def _set_combo_value(self, combo, value):
        idx = combo.findData(value)
        if idx >= 0: combo.setCurrentIndex(idx)

    def _load_data(self):
        from PyQt6.QtWidgets import QMessageBox
        data = self.repo.get_by_id(self.event_id)
        if not data:
            QMessageBox.warning(self,"Aviso","No se encontró el evento.")
            self.reject(); return
        self.input_name.setText(data.get("name") or "")
        ed = data.get("event_date") or date.today()
        self._current_date = QDate(ed.year, ed.month, ed.day)
        self._btn_date_lbl.setText(self._current_date.toString("dd/MM/yyyy"))
        self._set_combo_value(self.cmb_type, data.get("event_type") or "otro")
        self.input_location.setText(data.get("location") or "")
        self.input_description.setPlainText(data.get("description") or "")
        self.selected_color = data.get("color") or BLUE
        if data.get("start_time") or data.get("end_time"):
            self._use_time = True; self.chk_has_time.setChecked(True)
        if data.get("start_time"):
            self.start_time_value = QTime(data["start_time"].hour, data["start_time"].minute)
        if data.get("end_time"):
            self.end_time_value = QTime(data["end_time"].hour, data["end_time"].minute)
        self.chk_important.setChecked(bool(data.get("is_important")))
        self._refresh_color_btn(); self._refresh_time_buttons(); self._update_preview()

    def _open_instructions(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Instrucciones — Formulario de eventos")
        dlg.setMinimumSize(620, 640)
        dlg.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        dlg.setStyleSheet(f"background:{BG_DIALOG}; color:{TEXT_PRI};")

        root = QVBoxLayout(dlg)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header premium
        hdr_f = QFrame()
        hdr_f.setFixedHeight(80)
        hdr_f.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 rgba(59,130,246,0.18), stop:1 {BG_CARD});
                border-bottom: 1px solid rgba(59,130,246,0.25);
            }}
            QFrame * {{ background: transparent; border: none; }}
        """)
        hdr_l = QHBoxLayout(hdr_f)
        hdr_l.setContentsMargins(24, 0, 24, 0)
        hdr_l.setSpacing(14)

        ic_f = QFrame(); ic_f.setFixedSize(44, 44)
        ic_f.setStyleSheet(f"""
            QFrame {{
                background: rgba(59,130,246,0.15);
                border: 1px solid rgba(59,130,246,0.4);
                border-radius: 12px;
            }}
        """)
        ic_l = QHBoxLayout(ic_f); ic_l.setContentsMargins(0,0,0,0)
        ic_l.addWidget(IconLabel("help-circle", 22, BLUE), 0, Qt.AlignmentFlag.AlignCenter)

        ttl_col = QVBoxLayout(); ttl_col.setSpacing(3)
        t1 = QLabel("Guía completa del formulario")
        t1.setStyleSheet(f"color:{TEXT_PRI};font-size:16px;font-weight:900;font-family:'Inter';")
        t2 = QLabel("Todo lo que necesitas saber para registrar eventos correctamente")
        t2.setStyleSheet(f"color:{TEXT_MUT};font-size:11px;")
        ttl_col.addWidget(t1); ttl_col.addWidget(t2)

        btn_cls = QPushButton()
        btn_cls.setFixedSize(30, 30)
        btn_cls.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cls.setStyleSheet(f"""
            QPushButton {{background:rgba(255,255,255,0.05);border:1px solid {BORDER};border-radius:8px;}}
            QPushButton:hover{{background:rgba(255,255,255,0.10);}}
            QPushButton *{{background:transparent;border:none;}}
        """)
        cl = QHBoxLayout(btn_cls); cl.setContentsMargins(0,0,0,0)
        cl.addWidget(IconLabel("x", 12, TEXT_SEC), 0, Qt.AlignmentFlag.AlignCenter)
        btn_cls.clicked.connect(dlg.close)

        hdr_l.addWidget(ic_f)
        hdr_l.addLayout(ttl_col, 1)
        hdr_l.addWidget(btn_cls, 0, Qt.AlignmentFlag.AlignTop)
        root.addWidget(hdr_f)

        # ── Scroll
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border:none; background:transparent; }
            QScrollBar:vertical { background:transparent; width:6px; }
            QScrollBar::handle:vertical { background:#2A2A2A; border-radius:3px; }
        """)
        sc_w = QWidget(); sc_w.setStyleSheet("background:transparent;")
        sc_l = QVBoxLayout(sc_w)
        sc_l.setContentsMargins(24, 20, 24, 20)
        sc_l.setSpacing(14)

        sections = [
            ("zap",         RED,    "Nombre del evento",
             "Identifica el evento en el calendario. Debe ser claro y específico.",
             [
                ("✓", GREEN,   "Torneo Regional de Kata — Infantil 2025"),
                ("✓", GREEN,   "Examen de grado · Cinturón Azul · Agosto"),
                ("✗", "#FF4444", "evento  /  torneo  /  cosa del sábado"),
             ]),

            ("tag",         PURPLE, "Tipo de evento",
             "Clasifica el evento para organizarlo en el calendario. Si ninguna categoría encaja, elige «Otro» y escribe el tipo.",
             [
                ("Torneo",          BLUE,    "Competencia con jueces, marcadores y podio"),
                ("Examen de grado", GREEN,   "Evaluación técnica oficial para ascenso de cinturón"),
                ("Seminario",       PURPLE,  "Clase especial con instructor invitado"),
                ("Festivo",         YELLOW,  "Día de cierre, celebración o evento comunitario"),
                ("Otro",            TEXT_MUT,"Actividad que no encaja en las categorías anteriores"),
             ]),

            ("calendar",    BLUE,   "Fecha del evento",
             "Selecciona la fecha exacta. Haz clic en el botón de fecha para abrir el selector de calendario.",
             [
                ("Tip", YELLOW, "Haz clic en el nombre del mes para saltar rápidamente a otro mes o año"),
                ("Tip", YELLOW, "El evento aparecerá marcado en el día exacto del calendario del dojo"),
             ]),

            ("clock",       GREEN,  "Horario (opcional)",
             "Solo activa el horario si el evento tiene una hora definida. Eventos de todo el día (festivos, cierres) deben dejarse sin horario.",
             [
                ("Con horario",  GREEN,    "Torneo: 08:00 AM – 06:00 PM  |  Examen: 10:00 AM – 12:00 PM"),
                ("Sin horario",  TEXT_MUT, "Festivo nacional  |  Día libre  |  Vacaciones"),
                ("Tip",          YELLOW,   "La hora fin debe ser siempre mayor que la hora inicio"),
             ]),

            ("map-pin",     YELLOW, "Ubicación",
             "Indica dónde se realizará el evento. Se muestra en la vista previa y en el detalle del evento.",
             [
                ("Ejemplos", TEXT_SEC, "«Dojo principal»  ·  «Coliseo Municipal Cra 5»  ·  «Zoom — link en descripción»"),
             ]),

            ("star",        YELLOW, "Marcar como importante",
             "Resalta el evento en el calendario con un ícono especial. Úsalo solo para eventos críticos que el dojo no puede olvidar.",
             [
                ("Sí marcar",  YELLOW,   "Exámenes de grado  |  Torneos oficiales  |  Fechas límite de inscripción"),
                ("No marcar",  TEXT_MUT, "Reuniones internas  |  Clases de repaso  |  Actividades opcionales"),
             ]),

            ("palette",     PURPLE, "Color del evento",
             "El color identifica visualmente el tipo de evento en el calendario. Te recomendamos un código de colores consistente.",
             [
                ("Sugerencia", TEXT_SEC, "Rojo → Torneos  ·  Verde → Exámenes  ·  Azul → Seminarios  ·  Amarillo → Festivos"),
             ]),

            ("align-left",  TEXT_MUT, "Descripción",
             "Campo libre para notas, instrucciones o información adicional. Visible en el detalle del evento.",
             [
                ("Ejemplos", TEXT_SEC, "«Llevar uniforme completo y tarjeta de pago»  ·  «Inscripción cierra el viernes»"),
             ]),
        ]

        for icon_name, icon_color, title_text, desc_text, examples in sections:
            sec = QFrame()
            sec.setStyleSheet(f"""
                QFrame {{
                    background: {BG_CARD};
                    border: 1px solid {BORDER};
                    border-left: 3px solid {icon_color};
                    border-radius: 12px;
                }}
                QFrame * {{ background: transparent; border: none; }}
            """)
            sl = QVBoxLayout(sec)
            sl.setContentsMargins(16, 14, 16, 14)
            sl.setSpacing(10)

            th = QHBoxLayout(); th.setSpacing(9)
            th.addWidget(IconLabel(icon_name, 15, icon_color))
            t_lbl = QLabel(title_text)
            t_lbl.setStyleSheet(f"color:{TEXT_PRI};font-size:13px;font-weight:900;font-family:'Inter';")
            th.addWidget(t_lbl, 1)
            sl.addLayout(th)

            d_lbl = QLabel(desc_text)
            d_lbl.setWordWrap(True)
            d_lbl.setStyleSheet(f"color:{TEXT_SEC};font-size:12px;line-height:160%;")
            sl.addWidget(d_lbl)

            if examples:
                s_line = QFrame(); s_line.setFixedHeight(1)
                s_line.setStyleSheet(f"background:{BORDER};min-height:1px;max-height:1px;")
                sl.addWidget(s_line)

                for tag, tag_color, ex_text in examples:
                    ex_row = QHBoxLayout(); ex_row.setSpacing(10)
                    ex_row.setContentsMargins(4, 0, 0, 0)

                    tag_f = QFrame(); tag_f.setFixedWidth(90)
                    tag_l = QHBoxLayout(tag_f); tag_l.setContentsMargins(0,0,0,0)
                    tag_lbl = QLabel(tag)
                    tag_lbl.setStyleSheet(f"color:{tag_color};font-size:10px;font-weight:900;")
                    tag_l.addWidget(tag_lbl)

                    ex_lbl = QLabel(ex_text)
                    ex_lbl.setWordWrap(True)
                    ex_lbl.setStyleSheet(f"color:{TEXT_MUT};font-size:11px;font-style:italic;")
                    ex_row.addWidget(tag_f)
                    ex_row.addWidget(ex_lbl, 1)
                    sl.addLayout(ex_row)

            sc_l.addWidget(sec)

        sc_l.addStretch()
        scroll.setWidget(sc_w)
        root.addWidget(scroll, 1)

        # ── Footer
        foot_f = QFrame()
        foot_f.setFixedHeight(62)
        foot_f.setStyleSheet(f"QFrame{{background:{BG_CARD};border-top:1px solid {BORDER};}}")
        fl = QHBoxLayout(foot_f)
        fl.setContentsMargins(24, 0, 24, 0)

        tip = QLabel("💡  Puedes volver a abrir esta guía en cualquier momento desde el botón «Instrucciones»")
        tip.setStyleSheet(f"color:{TEXT_MUT};font-size:10px;")
        tip.setWordWrap(True)

        btn_ok = QPushButton("Entendido")
        btn_ok.setFixedHeight(38); btn_ok.setMinimumWidth(110)
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton{{background:{RED};color:white;border:none;border-radius:9px;
                font-size:13px;font-weight:800;padding:0 24px;}}
            QPushButton:hover{{background:{RED_H};}}
        """)
        btn_ok.clicked.connect(dlg.accept)

        fl.addWidget(tip, 1)
        fl.addWidget(btn_ok)
        root.addWidget(foot_f)

        dlg.exec()

    def _save(self):
        from PyQt6.QtWidgets import QMessageBox
        name = self.input_name.text().strip()
        if not name:
            QMessageBox.information(self,"Aviso","Escribe el nombre del evento.")
            return
        if self._use_time and self.end_time_value <= self.start_time_value:
            QMessageBox.information(self,"Aviso","La hora fin debe ser mayor que la hora inicio.")
            return
        data = {
            "name":        name,
            "event_date":  self._current_date.toPyDate(),
            "event_type":  (
                self.input_custom_type.text().strip() or "otro"
                if self.cmb_type.currentData() == "otro"
                else self.cmb_type.currentData()
            ),
            "description": self.input_description.toPlainText().strip() or None,
            "color":       self.selected_color,
            "start_time":  self.start_time_value.toString("HH:mm") if self._use_time else None,
            "end_time":    self.end_time_value.toString("HH:mm")   if self._use_time else None,
            "location":    self.input_location.text().strip() or None,
            "is_important": self.chk_important.isChecked(),
        }
        try:
            if self.event_id: self.repo.update(self.event_id, data)
            else:              self.repo.create(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self,"Error",f"No se pudo guardar:\n{e}")

    def _delete(self):
        from PyQt6.QtWidgets import QMessageBox
        confirm = QMessageBox.question(
            self,"Confirmar eliminación","¿Eliminar este evento?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try: self.repo.delete(self.event_id); self.accept()
            except Exception as e: QMessageBox.critical(self,"Error",f"No se pudo eliminar:\n{e}")
