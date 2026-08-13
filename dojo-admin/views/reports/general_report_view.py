from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QGraphicsDropShadowEffect, QScrollArea, QSizePolicy,
    QSpacerItem,
)
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint, QRectF
from PyQt6.QtGui import QColor, QPainter, QPen, QFont, QLinearGradient, QBrush

from core.i18n import tr
from repositories.reports_repository import reports_repo

BG_MAIN  = "#050505"
BG_CARD  = "#0C0C0C"
BG_HOVER = "#141414"
BORDER   = "#1F1F1F"
RED      = "#E11D48"
GREEN    = "#22C55E"
YELLOW   = "#EAB308"
BLUE     = "#3B82F6"
PURPLE   = "#A855F7"
ORANGE   = "#F97316"
TEXT_PRI = "#FAFAFA"
TEXT_SEC = "#A3A3A3"
TEXT_MUT = "#666666"


# ── MINI LINE CHART ────────────────────────────────────────────────

class MiniLineChart(QWidget):
    """Gráfico de línea simple, sin dependencias externas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: list[float] = []
        self._color = BLUE
        self.setMinimumHeight(160)
        self.setMaximumHeight(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_data(self, data: list[float], color: str = BLUE):
        self._data = data
        self._color = color
        self.update()

    def paintEvent(self, event):
        if not self._data:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        pad = 16
        chart_w = w - pad * 2
        chart_h = h - pad * 2

        max_val = max(self._data) if max(self._data) > 0 else 1
        min_val = min(self._data)
        val_range = max_val - min_val if max_val != min_val else 1

        points = []
        for i, val in enumerate(self._data):
            x = pad + (i / max(len(self._data) - 1, 1)) * chart_w
            y = pad + chart_h - ((val - min_val) / val_range) * chart_h
            points.append(QPoint(int(x), int(y)))

        if len(points) >= 2:
            grad = QLinearGradient(0, pad, 0, h - pad)
            color_obj = QColor(self._color)
            grad.setColorAt(0.0, QColor(color_obj.red(), color_obj.green(), color_obj.blue(), 60))
            grad.setColorAt(1.0, QColor(color_obj.red(), color_obj.green(), color_obj.blue(), 0))

            from PyQt6.QtGui import QPolygon
            fill_poly = QPolygon()
            fill_poly.append(QPoint(points[0].x(), h - pad))
            for pt in points:
                fill_poly.append(pt)
            fill_poly.append(QPoint(points[-1].x(), h - pad))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawPolygon(fill_poly)

            pen = QPen(QColor(self._color), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            from PyQt6.QtGui import QPolygon
            line_poly = QPolygon(points)
            painter.drawPolyline(line_poly)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(self._color)))
            last = points[-1]
            painter.drawEllipse(last, 4, 4)

        painter.end()


# ── KPI CARD ───────────────────────────────────────────────────────

class KPICard(QFrame):
    def __init__(self, icon, label, value, color=BLUE, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
            QFrame:hover {{
                border: 1px solid {color};
            }}
        """)
        self.setMinimumHeight(110)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(6)

        top = QHBoxLayout()
        ic = QLabel(icon)
        ic.setStyleSheet(f"font-size: 22px; background: transparent; color: {color};")
        lbl = QLabel(label)
        lbl.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 11px;
            font-weight: 700;
            font-family: 'Inter';
            letter-spacing: 0.6px;
            background: transparent;
        """)
        top.addWidget(ic)
        top.addWidget(lbl)
        top.addStretch()

        self._value_label = QLabel(str(value))
        self._value_label.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 26px;
            font-weight: 900;
            font-family: 'Inter';
            background: transparent;
        """)

        lay.addLayout(top)
        lay.addWidget(self._value_label)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def set_value(self, val):
        self._value_label.setText(str(val))


# ── ALERT ROW ──────────────────────────────────────────────────────

class AlertRow(QFrame):
    def __init__(self, icon, text, color=RED, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)
        self.setFixedHeight(52)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 14, 0)
        ic = QLabel(icon)
        ic.setStyleSheet(f"font-size: 16px; background: transparent; color: {color};")
        tx = QLabel(text)
        tx.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 13px;
            font-weight: 600;
            font-family: 'Inter';
            background: transparent;
        """)
        lay.addWidget(ic)
        lay.addWidget(tx, 1)
        lay.addStretch()


# ── LIST ROW ───────────────────────────────────────────────────────

class ListRow(QFrame):
    def __init__(self, left_text, right_text, left_color=TEXT_PRI, right_color=TEXT_SEC, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border-bottom: 1px solid {BORDER};
            }}
        """)
        self.setFixedHeight(44)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        left = QLabel(left_text)
        left.setStyleSheet(f"""
            color: {left_color};
            font-size: 13px;
            font-weight: 600;
            font-family: 'Inter';
            background: transparent;
        """)
        right = QLabel(right_text)
        right.setStyleSheet(f"""
            color: {right_color};
            font-size: 13px;
            font-weight: 600;
            font-family: 'Inter';
            background: transparent;
        """)
        lay.addWidget(left, 1)
        lay.addWidget(right, 0, Qt.AlignmentFlag.AlignRight)


# ── SECTION CARD ───────────────────────────────────────────────────

class SectionCard(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(18, 16, 18, 16)
        self._main_layout.setSpacing(4)

        header = QLabel(title)
        header.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 11px;
            font-weight: 800;
            font-family: 'Inter';
            letter-spacing: 1.2px;
            text-transform: uppercase;
            background: transparent;
        """)
        self._main_layout.addWidget(header)
        self._main_layout.addSpacing(8)

    def add_widget(self, w):
        self._main_layout.addWidget(w)

    def add_layout(self, l):
        self._main_layout.addLayout(l)


# ── GENERAL REPORT VIEW ────────────────────────────────────────────

class GeneralReportView(QWidget):
    def __init__(self):
        super().__init__()
        self._kpi_cards: dict[str, KPICard] = {}
        self._build_ui()
        QTimer.singleShot(200, self._load_data)

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {BG_MAIN};
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: #333;
                border-radius: 3px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)

        container = QWidget()
        container.setStyleSheet(f"background-color: {BG_MAIN};")
        self._root = QVBoxLayout(container)
        self._root.setContentsMargins(32, 28, 32, 32)
        self._root.setSpacing(24)

        # ── KPIs ────────────────────────────────────────────────────
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(16)

        self._kpi_cards["students"] = KPICard("\U0001f393", tr("reports.kpi.total_students"), "—", PURPLE)
        self._kpi_cards["active"] = KPICard("\u2705", tr("reports.kpi.active_students"), "—", GREEN)
        self._kpi_cards["classes"] = KPICard("\U0001f3eb", tr("reports.kpi.total_classes"), "—", BLUE)
        self._kpi_cards["attendance"] = KPICard("\u2611\ufe0f", tr("reports.kpi.total_attendance"), "—", ORANGE)
        self._kpi_cards["income"] = KPICard("\U0001f4b0", tr("reports.kpi.monthly_income"), "$0", GREEN)
        self._kpi_cards["expenses"] = KPICard("\U0001f4e4", tr("reports.kpi.monthly_expenses"), "$0", RED)
        self._kpi_cards["balance"] = KPICard("\u2696\ufe0f", tr("reports.kpi.balance"), "$0", BLUE)
        self._kpi_cards["receivables"] = KPICard("\U0001f9fe", tr("reports.kpi.open_receivables"), "0", YELLOW)

        kpi_grid.addWidget(self._kpi_cards["students"], 0, 0)
        kpi_grid.addWidget(self._kpi_cards["active"], 0, 1)
        kpi_grid.addWidget(self._kpi_cards["classes"], 0, 2)
        kpi_grid.addWidget(self._kpi_cards["attendance"], 0, 3)
        kpi_grid.addWidget(self._kpi_cards["income"], 1, 0)
        kpi_grid.addWidget(self._kpi_cards["expenses"], 1, 1)
        kpi_grid.addWidget(self._kpi_cards["balance"], 1, 2)
        kpi_grid.addWidget(self._kpi_cards["receivables"], 1, 3)
        self._root.addLayout(kpi_grid)

        # ── Chart + Alerts row ──────────────────────────────────────
        mid = QHBoxLayout()
        mid.setSpacing(16)

        chart_card = SectionCard(tr("reports.general.attendance_trend"))
        self._chart = MiniLineChart()
        chart_card.add_widget(self._chart)
        mid.addWidget(chart_card, 2)

        alerts_card = SectionCard(tr("reports.general.alerts"))
        self._alerts_container = QVBoxLayout()
        self._alerts_container.setSpacing(6)
        alerts_card.add_layout(self._alerts_container)
        mid.addWidget(alerts_card, 1)

        self._root.addLayout(mid)

        # ── Bottom row: Aging + Stock + Recent ──────────────────────
        bottom = QHBoxLayout()
        bottom.setSpacing(16)

        aging_card = SectionCard(tr("reports.general.aging_receivables"))
        self._aging_container = QVBoxLayout()
        self._aging_container.setSpacing(0)
        aging_card.add_layout(self._aging_container)
        bottom.addWidget(aging_card, 1)

        stock_card = SectionCard(tr("reports.general.low_stock"))
        self._stock_container = QVBoxLayout()
        self._stock_container.setSpacing(0)
        stock_card.add_layout(self._stock_container)
        bottom.addWidget(stock_card, 1)

        recent_card = SectionCard(tr("reports.general.recent_activity"))
        self._recent_container = QVBoxLayout()
        self._recent_container.setSpacing(0)
        recent_card.add_layout(self._recent_container)
        bottom.addWidget(recent_card, 1)

        self._root.addLayout(bottom)

        self._root.addStretch()
        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _load_data(self):
        try:
            kpis = reports_repo.get_general_kpis()
            self._kpi_cards["students"].set_value(kpis["total_students"])
            self._kpi_cards["active"].set_value(kpis["active_students"])
            self._kpi_cards["classes"].set_value(kpis["total_classes"])
            self._kpi_cards["attendance"].set_value(kpis["total_attendance"])
            self._kpi_cards["income"].set_value(f"${kpis['monthly_income']:,.0f}")
            self._kpi_cards["expenses"].set_value(f"${kpis['monthly_expenses']:,.0f}")
            self._kpi_cards["balance"].set_value(f"${kpis['monthly_balance']:,.0f}")
            self._kpi_cards["receivables"].set_value(str(kpis["open_receivables_count"]))

            trend = reports_repo.get_general_chart_6m()
            chart_data = [float(m["total"]) for m in trend]
            self._chart.set_data(chart_data, BLUE)

            alerts = reports_repo.get_general_alerts()
            self._clear_layout(self._alerts_container)

            open_amt = alerts["open_receivables"]["amount"]
            if open_amt > 0:
                self._alerts_container.addWidget(
                    AlertRow("\u26a0\ufe0f", f"{tr('reports.alerts.open_receivables')}: ${open_amt:,.0f}", RED))
            if alerts["low_stock"]:
                names = ", ".join(p["name"] for p in alerts["low_stock"][:3])
                self._alerts_container.addWidget(
                    AlertRow("\U0001f4e6", f"{tr('reports.alerts.low_stock')}: {names}", ORANGE))
            if self._alerts_container.count() == 0:
                self._alerts_container.addWidget(
                    AlertRow("\u2705", tr("reports.alerts.all_ok"), GREEN))

            self._clear_layout(self._aging_container)
            self._aging_container.addWidget(
                ListRow(tr("reports.aging.open_accounts"),
                        str(alerts["open_receivables"]["count"]), TEXT_PRI, BLUE))
            amt_label = f"${open_amt:,.0f}" if open_amt else "$0"
            self._aging_container.addWidget(
                ListRow(tr("reports.aging.total_pending"), amt_label, TEXT_PRI, YELLOW))

            self._clear_layout(self._stock_container)
            if alerts["low_stock"]:
                for p in alerts["low_stock"][:5]:
                    color = RED if p["stock"] == 0 else YELLOW
                    self._stock_container.addWidget(
                        ListRow(p["name"], f"{p['stock']} {tr('reports.stock.units')}", TEXT_PRI, color))
            else:
                self._stock_container.addWidget(
                    ListRow(tr("reports.stock.all_ok"), "\u2705", TEXT_PRI, GREEN))

            self._clear_layout(self._recent_container)
            for cls in alerts["recent_classes"][:4]:
                date_str = str(cls["date"])[:10] if cls["date"] else "—"
                detail = f"{cls['schedule_name']} | {cls['attendees']}/{cls['capacity']}"
                self._recent_container.addWidget(
                    ListRow(date_str, detail, TEXT_SEC, TEXT_MUT))
            for ev in alerts["upcoming_events"][:3]:
                date_str = str(ev["date"])[:10] if ev["date"] else "—"
                self._recent_container.addWidget(
                    ListRow(date_str, ev["name"], TEXT_SEC, TEXT_MUT))

        except Exception as e:
            print(f"[ReportsGeneral] Error loading data: {e}")

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
