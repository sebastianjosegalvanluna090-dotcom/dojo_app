# ─── CLASSES_VIEW PREMIUM CALENDAR ────────────────────────────────────

from datetime import date, timedelta, time

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QComboBox, QStackedWidget,
    QGridLayout, QMessageBox, QScrollArea,
    QGraphicsOpacityEffect, QGraphicsBlurEffect,
    QGraphicsDropShadowEffect, QDialog, QSizePolicy,
    QCheckBox
)

from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    QPoint, QMimeData, pyqtSignal
)
from PyQt6.QtGui import QDrag, QColor, QPainter, QPen


from repositories.classes_repository import ClassesRepository
from repositories.events_repository import EventsRepository


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

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
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
        self.show()
        self.raise_()
        self.anim.stop()
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

    def fade_out(self):
        self.anim.stop()
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.finished.connect(self.hide)
        self.anim.start()


# ─────────────────────────────────────────────────────────────
# Day Header
# ─────────────────────────────────────────────────────────────
class DayHeader(QFrame):
    def __init__(self, day_name, day_num="", parent=None):
        super().__init__(parent)

        self.day_name = day_name
        self.day_num = day_num
        self.accent = "#E11D48"
        self.active = False

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

    def set_accent(self, color):
        self.accent = color
        self.refresh()

    def set_highlight(self, active):
        self.active = active
        self.refresh()

    def set_day_num(self, day_num):
        self.day_num = day_num
        self.lbl_date.setText(str(day_num))
        self.refresh()

    def refresh(self):
        name_color = self.accent if self.active else TEXT_SEC
        bg = "#141414" if self.active else "#0E0E0E"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-right: 1px solid #1C1C1C;
                border-bottom: 1px solid #1A1A1A;
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
            color: {TEXT_MUT};
            font-size: 10px;
            font-weight: 700;
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

        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh(False)

    def set_accent(self, color):
        self.accent = color
        self.refresh(False)

    def refresh(self, hover=False):
        bg = BG_CELL_H if hover else "rgba(12, 12, 12, 100)"
        border = self.accent if hover else "#141414"

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
            self.dropped.emit(schedule_id, self.day_index, self.hour)
            event.acceptProposedAction()
        except Exception:
            event.ignore()


# ─────────────────────────────────────────────────────────────
# Class Block Draggable
# ─────────────────────────────────────────────────────────────
class ClassBlock(QFrame):
    def __init__(self, data, parent_view, accent="#E11D48", parent=None):
        super().__init__(parent)

        self.data = data
        self.parent_view = parent_view
        self.accent = accent
        self.drag_start_pos = None
        self.was_dragging = False

        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.refresh_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)

        self.lbl_name = QLabel(data.get("name", "Clase"))
        self.lbl_name.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 11px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)
        self.lbl_name.setWordWrap(True)

        self.lbl_time = QLabel(f"{data.get('start_time', '—')} - {data.get('end_time', '—')}")
        self.lbl_time.setStyleSheet(f"""
            color: {data.get('color') or accent};
            font-size: 9px;
            font-weight: 900;
            background: transparent;
            border: none;
        """)

        self.lbl_inst = QLabel(f"👤 {data.get('instructor', 'Sin instructor')}")
        self.lbl_inst.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 9px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        self.lbl_inst.setWordWrap(True)

        layout.addWidget(self.lbl_name)
        layout.addWidget(self.lbl_time)
        layout.addWidget(self.lbl_inst)
        layout.addStretch()

        self.setToolTip(
            f"{data.get('name', '')}\n"
            f"Arte: {data.get('martial_art', '—')}\n"
            f"Instructor: {data.get('instructor', '—')}\n"
            f"Horario: {data.get('start_time', '—')} - {data.get('end_time', '—')}\n"
            f"Ubicación: {data.get('location', '—')}"
        )

    def refresh_style(self):
        color = self.data.get("color") or self.accent
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(18, 18, 18, 245);
                border: 1px solid #1C1C1C;
                border-left: 4px solid {color};
                border-radius: 9px;
            }}
            QFrame:hover {{
                background-color: #171717;
                border-color: #333333;
                border-left: 4px solid {color};
            }}
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.position().toPoint()
            self.was_dragging = False
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.drag_start_pos:
            return

        distance = (event.position().toPoint() - self.drag_start_pos).manhattanLength()

        if distance < 8:
            return

        self.was_dragging = True

        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(str(self.data.get("id")))
        drag.setMimeData(mime)

        self.setProperty("dragging", True)
        self.setWindowOpacity(0.45)

        drag.exec(Qt.DropAction.MoveAction)

        self.setWindowOpacity(1.0)
        self.setProperty("dragging", False)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        if not self.was_dragging and event.button() == Qt.MouseButton.LeftButton:
            self.parent_view.open_class_detail(self.data)

        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.parent_view.open_class_form(schedule_id=self.data.get("id"))
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

        self.week_start = date.today() - timedelta(days=date.today().weekday())

        self.setMinimumWidth(920)
        self.setMinimumHeight(self.header_h + ((self.end_hour - self.start_hour + 1) * self.cell_h))
        self.setStyleSheet(f"background-color: {BG_MAIN};")

        self._build_base()

    def _build_base(self):
        self.corner = QLabel("HORARIO", self)
        self.corner.setAlignment(Qt.AlignmentFlag.AlignCenter)
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

        for i, name in enumerate(DAYS_SHORT):
            header = DayHeader(name, "", self)
            header.set_accent(self.accent)
            self.day_headers.append(header)

        for hour in range(self.start_hour, self.end_hour + 1):
            lbl = QLabel(f"{hour:02d}:00", self)
            lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
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
            lbl.setObjectName(f"hour_label_{hour}")

            row_cells = []
            for day in range(7):
                cell = TimeCell(day, hour, self.accent, self)
                cell.clicked.connect(self.parent_view.open_class_form)
                cell.dropped.connect(self.parent_view.move_schedule_from_drop)
                cell.hover_day.connect(self._set_day_highlight)
                row_cells.append(cell)

            self.cells.append((lbl, row_cells))

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

    def _update_day_numbers(self):
        for idx, header in enumerate(self.day_headers):
            d = self.week_start + timedelta(days=idx)
            header.set_day_num(d.day)

    def _set_day_highlight(self, day, active):
        if 0 <= day < len(self.day_headers):
            self.day_headers[day].set_highlight(active)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._layout_absolute()

    def _layout_absolute(self):
        w = max(self.width(), 920)
        day_w = int((w - self.hour_col_w) / 7)

        self.corner.setGeometry(0, 0, self.hour_col_w, self.header_h)

        for day, header in enumerate(self.day_headers):
            header.setGeometry(
                self.hour_col_w + (day * day_w),
                0,
                day_w,
                self.header_h
            )

        for row_idx, (hour_lbl, row_cells) in enumerate(self.cells):
            y = self.header_h + (row_idx * self.cell_h)

            hour_lbl.setGeometry(0, y, self.hour_col_w, self.cell_h)

            for day, cell in enumerate(row_cells):
                cell.setGeometry(
                    self.hour_col_w + (day * day_w),
                    y,
                    day_w,
                    self.cell_h
                )

        self._layout_blocks()

    def load_data(self, filters=None):
        self.clear_blocks()

        try:
            rows = self.repo.get_week_schedules(filters or {})
        except Exception as e:
            print(f"[WeeklyCalendar error] {e}")
            rows = []

        for row in rows:
            data = {
                "id": row[0],
                "name": row[1],
                "day_of_week": row[2],
                "start_time": self._time_to_str(row[3]),
                "end_time": self._time_to_str(row[4]),
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

            block = ClassBlock(data, self.parent_view, self.accent, self)
            block.show()
            self.blocks.append(block)

        self._layout_blocks()

    def clear_blocks(self):
        for block in self.blocks:
            block.deleteLater()
        self.blocks = []

    def _layout_blocks(self):
        if not self.blocks:
            return

        w = max(self.width(), 920)
        day_w = int((w - self.hour_col_w) / 7)

        for block in self.blocks:
            data = block.data

            try:
                day = int(data["day_of_week"])
                start_h, start_m = self._parse_time(data["start_time"])
                end_h, end_m = self._parse_time(data["end_time"])
            except Exception:
                continue

            if day < 0 or day > 6:
                continue

            start_minutes = (start_h * 60) + start_m
            end_minutes = (end_h * 60) + end_m
            calendar_start = self.start_hour * 60

            duration_minutes = max(30, end_minutes - start_minutes)

            x = self.hour_col_w + (day * day_w) + 6
            y = self.header_h + int(((start_minutes - calendar_start) / 60) * self.cell_h) + 6
            h = int((duration_minutes / 60) * self.cell_h) - 12
            h = max(48, min(h, 180))

            block.setGeometry(x, y, day_w - 12, h)
            block.raise_()

    def _parse_time(self, value):
        if not value or value == "—":
            return 0, 0
        parts = str(value).split(":")
        return int(parts[0]), int(parts[1])

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

        self.lbl_title = QLabel("📅 Eventos del mes")
        self.lbl_title.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 18px;
            font-weight: 800;
        """)

        tag = QLabel("Vista de Hitos")
        tag.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1px;
        """)

        top.addWidget(self.lbl_title)
        top.addStretch()
        top.addWidget(tag)
        root.addLayout(top)

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

        self.lbl_title.setText(f"📅 Eventos · {month_names[month - 1]} {year}")
        self._clear_grid()

        for i in range(7):
            self.grid.setColumnStretch(i, 1)

        try:
            events = self.repo.get_month_events(year, month)
        except Exception as e:
            print(f"[MonthlyEvents error] {e}")
            events = []

        events_by_day = {}
        for ev in events:
            day_num = ev[2].day
            events_by_day.setdefault(day_num, []).append(ev)

        first = date(year, month, 1)
        start_col = first.weekday()  # lunes=0, domingo=6

        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)

        total_days = (next_month - first).days

        row = 0
        col = 0

        # Celdas vacías antes del día 1
        for _ in range(start_col):
            empty = self._make_empty_cell()
            self.grid.addWidget(empty, row, col)
            col += 1

        # Días reales
        for day_num in range(1, total_days + 1):
            cell = self._make_day_cell(day_num, events_by_day.get(day_num, []))
            self.grid.addWidget(cell, row, col)

            col += 1

            if col > 6:
                col = 0
                row += 1

        # Celdas vacías después del último día para cerrar semana
        if col != 0:
            while col <= 6:
                empty = self._make_empty_cell()
                self.grid.addWidget(empty, row, col)
                col += 1

        # Forzar altura uniforme por filas
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

    def _make_day_cell(self, day_num, events):
        today = date.today()
        is_today = (
            today.year == self.year
            and today.month == self.month
            and today.day == day_num
        )

        cell = QFrame()
        cell.setMinimumHeight(105)
        cell.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        cell.setCursor(Qt.CursorShape.PointingHandCursor)

        border = self.accent if is_today else "#1C1C1C"
        bg = "#121215" if is_today else "#0E0E0E"

        cell.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 10px;
            }}
            QFrame:hover {{
                border-color: {self.accent};
                background-color: #121212;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        layout = QVBoxLayout(cell)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(5)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)

        lbl_day = QLabel(str(day_num))
        lbl_day.setStyleSheet(f"""
            color: {self.accent if is_today else TEXT_PRI};
            font-size: 12px;
            font-weight: 900;
        """)

        row.addWidget(lbl_day)

        if is_today:
            lbl_today = QLabel("HOY")
            lbl_today.setStyleSheet(f"""
                color: {self.accent};
                font-size: 8px;
                font-weight: 900;
                letter-spacing: 1px;
            """)
            row.addStretch()
            row.addWidget(lbl_today)
        else:
            row.addStretch()

        layout.addLayout(row)

        for ev in events[:3]:
            name = ev[1]
            color = ev[5] or self.accent

            lbl_ev = QLabel(f"● {name}")
            lbl_ev.setToolTip(ev[4] or name)
            lbl_ev.setStyleSheet(f"""
                color: {color};
                font-size: 9px;
                font-weight: 700;
            """)
            lbl_ev.setWordWrap(False)
            layout.addWidget(lbl_ev)

        if len(events) > 3:
            more = QLabel(f"+{len(events) - 3} más")
            more.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px;")
            layout.addWidget(more)

        layout.addStretch()

        def click(event):
            self.parent_view.open_event_form(
                default_date=date(self.year, self.month, day_num)
            )

        cell.mousePressEvent = click

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

        self.lbl_title = QLabel("📊 Métricas Anuales")
        self.lbl_title.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 18px;
            font-weight: 800;
        """)

        tag = QLabel("Resumen de densidad")
        tag.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1px;
        """)

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
        self.lbl_title.setText(f"📊 Métricas Anuales · {year}")
        self._clear_grid()

        try:
            summary = self.repo.get_year_summary(year)
        except Exception as e:
            print(f"[YearSummary error] {e}")
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

    def _month_card(self, name, month, count):
        if count == 0:
            accent = "#444444"
        elif count < 3:
            accent = "#3B82F6"
        elif count < 6:
            accent = "#F59E0B"
        else:
            accent = "#10B981"

        card = QFrame()
        card.setMinimumHeight(120)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        card.setStyleSheet(f"""
            QFrame {{
                background-color: #0E0E0E;
                border: 1px solid #1F1F1F;
                border-left: 4px solid {accent};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border-color: {self.accent};
                background-color: #121212;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        lbl_name = QLabel(name)
        lbl_name.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 11px;
            font-weight: 900;
            letter-spacing: 1px;
        """)

        lbl_count = QLabel(f"{count} {'Hito' if count == 1 else 'Hitos'}")
        lbl_count.setStyleSheet(f"""
            color: {TEXT_PRI if count else TEXT_MUT};
            font-size: 18px;
            font-weight: 900;
        """)

        lbl_action = QLabel("Analizar  →")
        lbl_action.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 9px;
            font-weight: 900;
            letter-spacing: 1px;
        """)

        layout.addWidget(lbl_name)
        layout.addWidget(lbl_count)
        layout.addStretch()
        layout.addWidget(lbl_action)

        def click(event):
            self.parent_view.switch_to_month(self.year, month)

        card.mousePressEvent = click

        return card

    def _clear_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


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

        btn_close = QPushButton("×")
        btn_close.setFixedSize(34, 34)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SEC};
                border: none;
                font-size: 26px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
            }}
        """)
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

        lbl_location_value = QLabel(f"📍  {location}")
        lbl_location_value.setWordWrap(True)
        lbl_location_value.setStyleSheet(f"""
            color: {self.accent};
            font-size: 14px;
            font-weight: 900;
        """)

        location_block.addWidget(lbl_location_key)
        location_block.addWidget(lbl_location_value)

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
        accent="#10B981",
        parent=None
    ):
        super().__init__(parent)

        self.class_data = class_data
        self.students = students or []
        self.present_student_ids = set(present_student_ids or [])
        self.selected_ids = set(self.present_student_ids)

        self.setWindowTitle("Control de asistencia")
        self.setFixedSize(430, 520)
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
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #0F0F0F;
                border: 1px solid #252525;
                border-top: 4px solid {accent};
                border-radius: 14px;
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}

            QCheckBox {{
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

        btn_close = QPushButton("×")
        btn_close.setFixedSize(30, 30)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SEC};
                border: none;
                font-size: 24px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
            }}
        """)
        btn_close.clicked.connect(self.reject)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(btn_close)

        layout.addLayout(header)

        # Info clase
        lbl_class = QLabel(
            f"🥋 {class_data.get('name', 'Clase')}  •  👤 {class_data.get('instructor', 'Sin instructor')}"
        )
        lbl_class.setWordWrap(True)
        lbl_class.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 11px;
            font-weight: 800;
        """)
        layout.addWidget(lbl_class)

        self.lbl_stats = QLabel("")
        self.lbl_stats.setStyleSheet("""
            color: #10B981;
            font-size: 11px;
            font-weight: 900;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(self.lbl_stats)

        # Scroll
        scroll = QScrollArea()
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

        content = QWidget()
        content.setStyleSheet("background: transparent;")

        self.list_layout = QVBoxLayout(content)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(7)

        self.checkboxes = {}

        for student_id, student_name, document in self.students:
            row = QFrame()
            row.setObjectName("AttendanceRow")
            row.setStyleSheet("""
                QFrame#AttendanceRow {
                    background-color: #0E0E0E;
                    border: 1px solid #1F1F1F;
                    border-radius: 9px;
                }

                QFrame#AttendanceRow:hover {
                    background-color: #131313;
                    border-color: #2A2A2A;
                }

                QLabel {
                    background: transparent;
                    border: none;
                }

                QCheckBox {
                    background: transparent;
                    border: none;
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
                    background: transparent;
                    border: none;
                    color: {TEXT_PRI};
                    font-size: 12px;
                    font-weight: 800;
                }}
            """)

            lbl_doc = QLabel(str(document or ""))
            lbl_doc.setStyleSheet(f"""
                QLabel {{
                    background: transparent;
                    border: none;
                    color: {TEXT_MUT};
                    font-size: 10px;
                    font-weight: 700;
                }}
            """)

            name_col.addWidget(lbl_name)

            if document:
                name_col.addWidget(lbl_doc)

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

            row_layout.addLayout(name_col, 1)
            row_layout.addWidget(chk, 0, Qt.AlignmentFlag.AlignCenter)

            self.list_layout.addWidget(row)

            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 9, 12, 9)
            row_layout.setSpacing(8)

            name_col = QVBoxLayout()
            name_col.setSpacing(2)

            lbl_name = QLabel(student_name)
            lbl_name.setStyleSheet(f"""
                color: {TEXT_PRI};
                font-size: 12px;
                font-weight: 800;
            """)

            lbl_doc = QLabel(str(document or ""))
            lbl_doc.setStyleSheet(f"""
                color: {TEXT_MUT};
                font-size: 10px;
                font-weight: 700;
            """)

            name_col.addWidget(lbl_name)

            if document:
                name_col.addWidget(lbl_doc)

            chk = QCheckBox()
            chk.setCursor(Qt.CursorShape.PointingHandCursor)
            chk.setChecked(student_id in self.selected_ids)
            chk.setStyleSheet("""
                QCheckBox::indicator {
                    width: 19px;
                    height: 19px;
                    border: 2px solid #2A2A2A;
                    border-radius: 5px;
                    background-color: #121212;
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

            row_layout.addLayout(name_col, 1)
            row_layout.addWidget(chk)

            self.list_layout.addWidget(row)

        self.list_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        self._update_stats()

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
        pct = int((present / total) * 100) if total else 0

        self.lbl_stats.setText(
            f"Presentes: {present} / {total}  •  {pct}% de asistencia"
        )

    def get_present_student_ids(self):
        return set(self.selected_ids)


# ─────────────────────────────────────────────────────────────
# Main Classes View
# ─────────────────────────────────────────────────────────────
class ClassesView(QWidget):
    def __init__(self):
        super().__init__()

        self.classes_repo = ClassesRepository()
        self.events_repo = EventsRepository()

        self.current_date = date.today()
        self.current_year = date.today().year
        self.current_month = date.today().month

        self.accent_key = "rose"
        self.accent_color = ACCENTS[self.accent_key]["color"]
        self.accent_hover = ACCENTS[self.accent_key]["hover"]
        self.accent_active = ACCENTS[self.accent_key]["active"]

        self._animations = []

        self._build_ui()
        self.reload_current_view()
        self.show_toast("Consola de Gestión inicializada con éxito", "info")

    # ─────────────────────────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(f"background-color: {BG_MAIN};")

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        # Selector de acento flotante
        top_controls = QHBoxLayout()
        top_controls.setSpacing(8)

        accent_box = QFrame()
        accent_box.setStyleSheet("""
            QFrame {
                background-color: #121212;
                border: 1px solid #222222;
                border-radius: 15px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)

        ab = QHBoxLayout(accent_box)
        ab.setContentsMargins(12, 6, 12, 6)
        ab.setSpacing(8)

        lbl_palette = QLabel("Paleta de acento PyQt:")
        lbl_palette.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 700;")

        ab.addWidget(lbl_palette)

        self.accent_buttons = {}

        for key, data in ACCENTS.items():
            btn = QPushButton()
            btn.setFixedSize(18, 18)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(data["name"])
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {data["color"]};
                    border: 2px solid {'white' if key == self.accent_key else data["color"]};
                    border-radius: 9px;
                }}
                QPushButton:hover {{
                    border: 2px solid white;
                }}
            """)
            btn.clicked.connect(lambda _, k=key: self.set_accent(k))
            self.accent_buttons[key] = btn
            ab.addWidget(btn)

        status = QLabel("●  Simulador de Alta Fidelidad Activo")
        status.setStyleSheet("""
            color: #525252;
            font-size: 10px;
            font-weight: 900;
            letter-spacing: 1px;
        """)

        top_controls.addWidget(accent_box)
        top_controls.addStretch()
        top_controls.addWidget(status)

        root.addLayout(top_controls)

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

        self.lbl_title = QLabel("🔥  Clases y Eventos")
        self.lbl_title.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 25px;
            font-weight: 900;
        """)

        subtitle = QLabel("Arrastra clases para reprogramar. Explora vistas dinámicas con micro-animaciones.")
        subtitle.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 12px;
        """)

        title_col.addWidget(self.lbl_title)
        title_col.addWidget(subtitle)

        self.btn_new_event = QPushButton("📅  Nuevo Evento")
        self.btn_new_event.setFixedHeight(40)
        self.btn_new_event.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_event.setStyleSheet(self._secondary_button_style())
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
    # Accent
    # ─────────────────────────────────────────────────────────────
    def set_accent(self, key):
        self.accent_key = key
        data = ACCENTS[key]

        self.accent_color = data["color"]
        self.accent_hover = data["hover"]
        self.accent_active = data["active"]

        for k, btn in self.accent_buttons.items():
            color = ACCENTS[k]["color"]
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 2px solid {'white' if k == key else color};
                    border-radius: 9px;
                }}
                QPushButton:hover {{
                    border: 2px solid white;
                }}
            """)

        self.btn_new_class.setStyleSheet(self._primary_button_style())
        self.btn_new_event.setStyleSheet(self._secondary_button_style())
        self.btn_prev.setStyleSheet(self._nav_button_style())
        self.btn_today.setStyleSheet(self._nav_button_style())
        self.btn_next.setStyleSheet(self._nav_button_style())
        self.cmb_view.setStyleSheet(self._combo_style())
        self.header_line.setStyleSheet(self._gradient_line_style())

        self.week_view.set_accent(self.accent_color)
        self.month_view.set_accent(self.accent_color)
        self.year_view.set_accent(self.accent_color)

        self.reload_current_view()
        self.show_toast("Acento de marca actualizado", "success")

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
        self.show_toast("Sincronizado a fecha actual", "success")

    def go_prev(self):
        index = self.stack.currentIndex()

        if index == 0:
            self.current_date -= timedelta(days=7)
            self.show_toast("Retrocediendo semana", "info")

        elif index == 1:
            if self.current_month == 1:
                self.current_month = 12
                self.current_year -= 1
            else:
                self.current_month -= 1
            self.show_toast("Retrocediendo mes", "info")

        elif index == 2:
            self.current_year -= 1
            self.show_toast("Retrocediendo año", "info")

        self.reload_current_view()

    def go_next(self):
        index = self.stack.currentIndex()

        if index == 0:
            self.current_date += timedelta(days=7)
            self.show_toast("Avanzando semana", "info")

        elif index == 1:
            if self.current_month == 12:
                self.current_month = 1
                self.current_year += 1
            else:
                self.current_month += 1
            self.show_toast("Avanzando mes", "info")

        elif index == 2:
            self.current_year += 1
            self.show_toast("Avanzando año", "info")

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
    def open_class_form(self, default_day=None, default_hour=None, schedule_id=None):
        try:
            from views.class_form import ClassForm
        except Exception as e:
            QMessageBox.information(self, "Pendiente", f"Falta crear views/class_form.py.\n{e}")
            return

        self._blur_on()

        dlg = ClassForm(
            self.classes_repo,
            schedule_id=schedule_id,
            default_day=default_day,
            default_hour=default_hour,
            parent=self
        )

        result = dlg.exec()
        self._blur_off()

        if result == ClassForm.DialogCode.Accepted:
            self.reload_current_view()
            self.show_toast("Sincronizado: clase guardada", "success")

    def open_event_form(self, event_id=None, default_date=None):
        try:
            from views.event_form import EventForm
        except Exception as e:
            QMessageBox.information(self, "Pendiente", f"Falta crear views/event_form.py.\n{e}")
            return

        self._blur_on()

        dlg = EventForm(
            self.events_repo,
            event_id=event_id,
            default_date=default_date,
            parent=self
        )

        result = dlg.exec()
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

        self._blur_off()

        if action == "delete":
            self.delete_schedule_from_detail(schedule_id)

        elif action == "edit":
            QTimer.singleShot(
                120,
                lambda sid=schedule_id: self.open_class_form(schedule_id=sid)
            )

        elif action == "attendance":
            QTimer.singleShot(
                120,
                lambda d=data: self.open_attendance_dialog(d)
            )

    def open_attendance_dialog(self, class_data):
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

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo preparar la asistencia:\n{e}"
            )
            return

        self._blur_on()

        dlg = AttendanceDialog(
            class_data=class_data,
            students=students,
            present_student_ids=present_ids,
            accent="#10B981",
            parent=self
        )

        result = dlg.exec()
        self._blur_off()

        if result == AttendanceDialog.DialogCode.Accepted:
            try:
                selected_ids = dlg.get_present_student_ids()
                self.classes_repo.save_attendance(class_id, selected_ids)

                total = len(students)
                present = len(selected_ids)
                pct = int((present / total) * 100) if total else 0

                self.show_toast(
                    f"Asistencia guardada: {present}/{total} presentes ({pct}%)",
                    "success"
                )

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"No se pudo guardar la asistencia:\n{e}"
                )

    def delete_schedule_from_detail(self, schedule_id):
        confirm = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Eliminar esta clase del calendario?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.classes_repo.delete_schedule(schedule_id)
                self.reload_current_view()
                self.show_toast("Clase eliminada de la DB", "warning")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{e}")

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
            data["start_time"] = self._minutes_to_time_string(start_total)
            data["end_time"] = self._minutes_to_time_string(end_total)

            self.classes_repo.update_schedule(schedule_id, data)

            self.reload_current_view()
            self.show_toast(f'Clase "{data.get("name")}" reubicada con éxito', "success")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo mover la clase:\n{e}")

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

    def _minutes_to_time_string(self, total):
        total = max(0, min(total, 23 * 60 + 59))
        h = total // 60
        m = total % 60
        return f"{h:02d}:{m:02d}"

    # ─────────────────────────────────────────────────────────────
    # Blur
    # ─────────────────────────────────────────────────────────────
    def _blur_on(self):
        self.blur_effect = QGraphicsBlurEffect(self.content_shell)
        self.blur_effect.setBlurRadius(0)
        self.content_shell.setGraphicsEffect(self.blur_effect)

        self.blur_anim = QPropertyAnimation(self.blur_effect, b"blurRadius", self)
        self.blur_anim.setDuration(220)
        self.blur_anim.setStartValue(0)
        self.blur_anim.setEndValue(16)
        self.blur_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.blur_anim.start()

        self.glass.fade_in()

    def _blur_off(self):
        try:
            if hasattr(self, "blur_anim"):
                self.blur_anim.stop()

            self.blur_anim = QPropertyAnimation(self.blur_effect, b"blurRadius", self)
            self.blur_anim.setDuration(180)
            self.blur_anim.setStartValue(self.blur_effect.blurRadius())
            self.blur_anim.setEndValue(0)
            self.blur_anim.setEasingCurve(QEasingCurve.Type.InCubic)

            def clear():
                self.content_shell.setGraphicsEffect(None)

            self.blur_anim.finished.connect(clear)
            self.blur_anim.start()
        except Exception:
            self.content_shell.setGraphicsEffect(None)

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
