from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QScrollArea, QSizePolicy, QPushButton,
    QDateEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView,
)
from PyQt6.QtCore import Qt, QTimer, QDate, QPoint
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QLinearGradient, QFont

from core.i18n import tr
from repositories.reports_repository import reports_repo

BG_MAIN  = "#050505"
BG_CARD  = "#0C0C0C"
BG_C2    = "#111111"
BORDER   = "#1F1F1F"
RED      = "#E11D48"
GREEN    = "#10B981"
YELLOW   = "#F59E0B"
BLUE     = "#3B82F6"
PURPLE   = "#A855F7"
ORANGE   = "#F97316"
TEXT_PRI = "#FAFAFA"
TEXT_SEC = "#A3A3A3"
TEXT_MUT = "#666666"

MONTH_NAMES = {1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
               7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"}

STATUS_COLORS = {"completed": GREEN, "cancelled": RED, "scheduled": BLUE, "pending": YELLOW}


class KPICard(QFrame):
    def __init__(self, icon, label, value, color=BLUE, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{ background-color: {BG_CARD}; border: 1px solid {BORDER};
                      border-radius: 14px; }}
            QFrame:hover {{ border: 1px solid {color}; }}
        """)
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(4)
        top = QHBoxLayout()
        ic = QLabel(icon)
        ic.setStyleSheet(f"font-size: 20px; background: transparent; color: {color};")
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 700; "
                          f"font-family: 'Inter'; letter-spacing: 0.6px; background: transparent;")
        top.addWidget(ic)
        top.addWidget(lbl)
        top.addStretch()
        self._value = QLabel(str(value))
        self._value.setStyleSheet(f"color: {TEXT_PRI}; font-size: 24px; font-weight: 900; "
                                  f"font-family: 'Inter'; background: transparent;")
        lay.addLayout(top)
        lay.addWidget(self._value)

    def set_value(self, v):
        self._value.setText(str(v))


class SectionCard(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{ background-color: {BG_CARD}; border: 1px solid {BORDER};
                      border-radius: 14px; }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(18, 16, 18, 16)
        self._lay.setSpacing(6)
        h = QLabel(title)
        h.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 800; "
                         f"font-family: 'Inter'; letter-spacing: 1.2px; background: transparent;")
        self._lay.addWidget(h)
        self._lay.addSpacing(6)

    def add_widget(self, w):
        self._lay.addWidget(w)

    def add_layout(self, l):
        self._lay.addLayout(l)


class MiniLineChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: list[float] = []
        self._labels: list[str] = []
        self._color = BLUE
        self.setMinimumHeight(180)
        self.setMaximumHeight(240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_data(self, data, labels=None, color=BLUE):
        self._data = data
        self._labels = labels or []
        self._color = color
        self.update()

    def paintEvent(self, event):
        if not self._data:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        pad_l, pad_r, pad_t, pad_b = 40, 20, 16, 28
        chart_w = w - pad_l - pad_r
        chart_h = h - pad_t - pad_b

        max_val = max(self._data) if max(self._data) > 0 else 1
        min_val = min(self._data)
        val_range = max_val - min_val if max_val != min_val else 1

        points = []
        for i, val in enumerate(self._data):
            x = pad_l + (i / max(len(self._data) - 1, 1)) * chart_w
            y = pad_t + chart_h - ((val - min_val) / val_range) * chart_h
            points.append(QPoint(int(x), int(y)))

        if len(points) >= 2:
            from PyQt6.QtGui import QPolygon
            grad = QLinearGradient(0, pad_t, 0, h - pad_b)
            co = QColor(self._color)
            grad.setColorAt(0.0, QColor(co.red(), co.green(), co.blue(), 50))
            grad.setColorAt(1.0, QColor(co.red(), co.green(), co.blue(), 0))

            fill_poly = QPolygon()
            fill_poly.append(QPoint(points[0].x(), h - pad_b))
            for pt in points:
                fill_poly.append(pt)
            fill_poly.append(QPoint(points[-1].x(), h - pad_b))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawPolygon(fill_poly)

            pen = QPen(QColor(self._color), 2, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPolyline(QPolygon(points))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(self._color)))
            painter.drawEllipse(points[-1], 4, 4)

        # X-axis labels
        if self._labels:
            font = QFont("Inter", 8)
            painter.setFont(font)
            painter.setPen(QColor(TEXT_SEC))
            for i, label in enumerate(self._labels):
                if i < len(points):
                    painter.drawText(points[i].x() - 15, h - 6, label)

        painter.end()


class ClassesReportView(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        QTimer.singleShot(200, self._load_data)

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: {BG_MAIN}; border: none; }}
            QScrollBar:vertical {{
                background: transparent; width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: #333; border-radius: 3px; min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

        container = QWidget()
        container.setStyleSheet(f"background-color: {BG_MAIN};")
        self._root = QVBoxLayout(container)
        self._root.setContentsMargins(32, 28, 32, 32)
        self._root.setSpacing(20)

        title = QLabel(tr("reports.classes.title"))
        title.setStyleSheet(f"color: {TEXT_PRI}; font-size: 22px; font-weight: 900; "
                             f"font-family: 'Inter'; background: transparent;")
        self._root.addWidget(title)

        # ── Date range ──────────────────────────────────────────────
        controls = QHBoxLayout()
        controls.setSpacing(12)
        date_style = f"""
            QDateEdit {{
                background-color: {BG_CARD}; color: {TEXT_PRI}; border: 1px solid {BORDER};
                border-radius: 8px; padding: 8px 14px; font-size: 13px;
                font-family: 'Inter'; font-weight: 600; min-width: 160px;
            }}
            QDateEdit:hover {{ border: 1px solid {BLUE}; }}
            QDateEdit::drop-down {{ border: none; width: 28px; }}
        """
        from_lbl = QLabel(tr("reports.classes.date_from"))
        from_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-weight: 700; "
                                f"font-family: 'Inter'; background: transparent;")
        self._date_from = QDateEdit()
        self._date_from.setCalendarPopup(True)
        self._date_from.setDate(QDate.currentDate().addMonths(-6))
        self._date_from.setStyleSheet(date_style)

        to_lbl = QLabel(tr("reports.classes.date_to"))
        to_lbl.setStyleSheet(from_lbl.styleSheet())
        self._date_to = QDateEdit()
        self._date_to.setCalendarPopup(True)
        self._date_to.setDate(QDate.currentDate())
        self._date_to.setStyleSheet(date_style)

        btn = QPushButton(tr("reports.classes.generate"))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BLUE}; color: white; border: none;
                border-radius: 8px; padding: 8px 20px; font-size: 13px;
                font-weight: 800; font-family: 'Inter';
            }}
            QPushButton:hover {{ background-color: #4B8BF5; }}
        """)
        btn.clicked.connect(self._load_data)

        controls.addWidget(from_lbl)
        controls.addWidget(self._date_from)
        controls.addWidget(to_lbl)
        controls.addWidget(self._date_to)
        controls.addWidget(btn)
        controls.addStretch()
        self._root.addLayout(controls)

        # ── KPIs ────────────────────────────────────────────────────
        self._kpi_grid = QGridLayout()
        self._kpi_grid.setSpacing(16)
        self._kpi_cards = {}
        self._root.addLayout(self._kpi_grid)

        # ── Chart + Breakdowns ──────────────────────────────────────
        mid = QHBoxLayout()
        mid.setSpacing(16)

        self._chart_card = SectionCard(tr("reports.classes.chart_monthly"))
        self._chart = MiniLineChart()
        self._chart_card.add_widget(self._chart)
        mid.addWidget(self._chart_card, 2)

        right_col = QVBoxLayout()
        right_col.setSpacing(16)

        self._ma_card = SectionCard(tr("reports.classes.by_martial_art"))
        self._ma_container = QVBoxLayout()
        self._ma_container.setSpacing(4)
        self._ma_card.add_layout(self._ma_container)
        right_col.addWidget(self._ma_card)

        self._inst_card = SectionCard(tr("reports.classes.by_instructor"))
        self._inst_container = QVBoxLayout()
        self._inst_container.setSpacing(4)
        self._inst_card.add_layout(self._inst_container)
        right_col.addWidget(self._inst_card)

        mid.addLayout(right_col, 1)
        self._root.addLayout(mid)

        # ── Table ───────────────────────────────────────────────────
        table_card = SectionCard(tr("reports.classes.detail_table"))
        self._table = QTableWidget()
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_C2}; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 8px;
                gridline-color: {BORDER}; font-family: 'Inter'; font-size: 12px;
            }}
            QHeaderView::section {{
                background-color: {BG_CARD}; color: {TEXT_SEC};
                border: none; border-bottom: 1px solid {BORDER};
                padding: 8px; font-weight: 800; font-size: 11px;
            }}
        """)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_card.add_widget(self._table)
        self._root.addWidget(table_card)

        self._root.addStretch()
        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _load_data(self):
        try:
            d_from = self._date_from.date().toPyDate()
            d_to = self._date_to.date().toPyDate()
            data = reports_repo.get_classes_report(str(d_from), str(d_to))

            # KPIs
            self._clear_layout(self._kpi_grid)
            kpis = [
                ("\U0001f3eb", tr("reports.classes.kpi_total"), str(data["total"]), BLUE),
                ("\u2705", tr("reports.classes.kpi_completed"), str(data["completed"]), GREEN),
                ("\u274c", tr("reports.classes.kpi_cancelled"), str(data["cancelled"]), RED),
                ("\u2611\ufe0f", tr("reports.classes.kpi_avg_att"),
                 f"{data['avg_attendance']:.1f}", ORANGE),
            ]
            for i, (icon, label, value, color) in enumerate(kpis):
                card = KPICard(icon, label, value, color)
                self._kpi_grid.addWidget(card, 0, i)

            # Chart
            monthly = data.get("monthly", [])
            chart_data = [float(m["count"]) for m in monthly]
            labels = [MONTH_NAMES.get(m["month"], str(m["month"])) for m in monthly]
            self._chart.set_data(chart_data, labels, BLUE)

            # Martial art breakdown
            self._clear_layout(self._ma_container)
            for item in data.get("by_martial_art", []):
                row = QLabel(f"  {item['martial_art']}  —  {item['count']}")
                row.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px; font-weight: 600; "
                                   f"font-family: 'Inter'; background: transparent; padding: 4px 0;")
                self._ma_container.addWidget(row)

            # Instructor breakdown
            self._clear_layout(self._inst_container)
            for item in data.get("by_instructor", []):
                row = QLabel(f"  {item['instructor']}  —  {item['count']}")
                row.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px; font-weight: 600; "
                                   f"font-family: 'Inter'; background: transparent; padding: 4px 0;")
                self._inst_container.addWidget(row)

            # Table
            detail = data.get("detail", [])
            headers = [tr("reports.classes.tbl_date"), tr("reports.classes.tbl_schedule"),
                       tr("reports.classes.tbl_martial_art"), tr("reports.classes.tbl_instructor"),
                       tr("reports.classes.tbl_status"), tr("reports.classes.tbl_attendance")]
            self._table.setColumnCount(len(headers))
            self._table.setHorizontalHeaderLabels(headers)
            self._table.setRowCount(len(detail))
            for r, cls in enumerate(detail):
                date_str = str(cls["date"])[:10] if cls["date"] else "—"
                status = cls["status"] or "—"
                att = f"{cls['attendees']}/{cls['capacity']}"
                row_data = [date_str, cls["schedule_name"], cls["martial_art"],
                            cls["instructor"], status, att]
                for c, val in enumerate(row_data):
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if c == 4:
                        sc = STATUS_COLORS.get(val, TEXT_SEC)
                        item.setForeground(QColor(sc))
                    self._table.setItem(r, c, item)

        except Exception as e:
            print(f"[ClassesReport] Error: {e}")

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
