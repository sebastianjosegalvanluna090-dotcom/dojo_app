from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QScrollArea, QSizePolicy, QPushButton,
    QDateEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QSpacerItem,
)
from PyQt6.QtCore import Qt, QTimer, QDate, QPoint
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QLinearGradient, QFont

from core.i18n import tr
from repositories.reports_repository import reports_repo

BG_MAIN  = "#050505"
BG_CARD  = "#0C0C0C"
BG_C2    = "#111111"
BG_HOVER = "#141414"
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


# ── SHARED WIDGETS ─────────────────────────────────────────────────

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
        self._header = QLabel(title)
        self._header.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 800; "
                         f"font-family: 'Inter'; letter-spacing: 1.2px; background: transparent;")
        self._lay.addWidget(self._header)
        self._lay.addSpacing(6)

    def setTitle(self, title):
        self._header.setText(title)

    def add_widget(self, w):
        self._lay.addWidget(w)

    def add_layout(self, l):
        self._lay.addLayout(l)


class MiniBarChart(QWidget):
    """Gráfico de barras dual (comparativo A vs B)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data_a: list[float] = []
        self._data_b: list[float] = []
        self._labels: list[str] = []
        self._color_a = BLUE
        self._color_b = ORANGE
        self.setMinimumHeight(200)
        self.setMaximumHeight(280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_data(self, labels, data_a, data_b, color_a=BLUE, color_b=ORANGE):
        self._labels = labels
        self._data_a = data_a
        self._data_b = data_b
        self._color_a = color_a
        self._color_b = color_b
        self.update()

    def paintEvent(self, event):
        if not self._data_a and not self._data_b:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        pad_l, pad_r, pad_t, pad_b = 50, 20, 20, 30
        chart_w = w - pad_l - pad_r
        chart_h = h - pad_t - pad_b

        all_vals = self._data_a + self._data_b
        max_val = max(all_vals) if all_vals and max(all_vals) > 0 else 1

        n = max(len(self._data_a), len(self._data_b), 1)
        group_w = chart_w / n
        bar_w = group_w * 0.3
        gap = 4

        font = QFont("Inter", 8)
        painter.setFont(font)

        for i in range(n):
            x_base = pad_l + i * group_w + group_w * 0.15

            val_a = self._data_a[i] if i < len(self._data_a) else 0
            val_b = self._data_b[i] if i < len(self._data_b) else 0

            h_a = (val_a / max_val) * chart_h if max_val else 0
            h_b = (val_b / max_val) * chart_h if max_val else 0

            # Bar A
            y_a = pad_t + chart_h - h_a
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(self._color_a)))
            painter.drawRoundedRect(int(x_base), int(y_a), int(bar_w), int(h_a), 4, 4)

            # Bar B
            x_b = x_base + bar_w + gap
            y_b = pad_t + chart_h - h_b
            painter.setBrush(QBrush(QColor(self._color_b)))
            painter.drawRoundedRect(int(x_b), int(y_b), int(bar_w), int(h_b), 4, 4)

            # Label
            if i < len(self._labels):
                painter.setPen(QColor(TEXT_SEC))
                label_x = x_base + bar_w + gap / 2
                painter.drawText(int(label_x - 15), h - 8, self._labels[i])

        painter.end()


class AlertRow(QFrame):
    def __init__(self, icon, text, color=RED, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{ background-color: {BG_CARD}; border: 1px solid {BORDER};
                      border-radius: 10px; }}
        """)
        self.setFixedHeight(48)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 14, 0)
        ic = QLabel(icon)
        ic.setStyleSheet(f"font-size: 16px; background: transparent; color: {color};")
        tx = QLabel(text)
        tx.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px; font-weight: 600; "
                          f"font-family: 'Inter'; background: transparent;")
        lay.addWidget(ic)
        lay.addWidget(tx, 1)


# ── FINANCE REPORT VIEW ────────────────────────────────────────────

class FinanceReportView(QWidget):
    def __init__(self):
        super().__init__()
        self._current_source = "ingresos"
        self._current_type = "general"
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

        # Title
        title = QLabel(tr("reports.finance.title"))
        title.setStyleSheet(f"color: {TEXT_PRI}; font-size: 22px; font-weight: 900; "
                             f"font-family: 'Inter'; background: transparent;")
        self._root.addWidget(title)

        # ── Controls ────────────────────────────────────────────────
        controls = QHBoxLayout()
        controls.setSpacing(12)

        # Source selector
        src_lbl = QLabel(tr("reports.finance.source"))
        src_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-weight: 700; "
                               f"font-family: 'Inter'; background: transparent;")
        self._cmb_source = QComboBox()
        self._cmb_source.addItems([
            tr("reports.finance.src_income"),
            tr("reports.finance.src_expenses"),
            tr("reports.finance.src_receivables"),
            tr("reports.finance.src_collection"),
        ])
        self._cmb_source.currentIndexChanged.connect(self._on_source_changed)
        self._cmb_source.setStyleSheet(f"""
            QComboBox {{
                background-color: {BG_CARD}; color: {TEXT_PRI}; border: 1px solid {BORDER};
                border-radius: 8px; padding: 8px 14px; font-size: 13px;
                font-family: 'Inter'; font-weight: 600; min-width: 180px;
            }}
            QComboBox:hover {{ border: 1px solid {BLUE}; }}
            QComboBox::drop-down {{ border: none; width: 28px; }}
            QComboBox QAbstractItemView {{
                background-color: {BG_CARD}; color: {TEXT_PRI};
                border: 1px solid {BORDER}; selection-background-color: {BG_HOVER};
            }}
        """)

        # Report type selector
        type_lbl = QLabel(tr("reports.finance.type"))
        type_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-weight: 700; "
                                f"font-family: 'Inter'; background: transparent;")
        self._cmb_type = QComboBox()
        self._cmb_type.addItems([
            tr("reports.finance.type_general"),
            tr("reports.finance.type_periods"),
            tr("reports.finance.type_vs"),
            tr("reports.finance.type_detailed"),
        ])
        self._cmb_type.currentIndexChanged.connect(self._on_type_changed)
        self._cmb_type.setStyleSheet(self._cmb_source.styleSheet())

        controls.addWidget(src_lbl)
        controls.addWidget(self._cmb_source)
        controls.addSpacing(16)
        controls.addWidget(type_lbl)
        controls.addWidget(self._cmb_type)
        controls.addStretch()
        self._root.addLayout(controls)

        # ── Date range (for periods / VS / detailed) ────────────────
        self._date_frame = QFrame()
        self._date_frame.setStyleSheet(f"""
            QFrame {{ background-color: {BG_CARD}; border: 1px solid {BORDER};
                      border-radius: 10px; }}
        """)
        date_lay = QHBoxLayout(self._date_frame)
        date_lay.setContentsMargins(16, 10, 16, 10)
        date_lay.setSpacing(12)

        date_style = f"""
            QDateEdit {{
                background-color: {BG_C2}; color: {TEXT_PRI}; border: 1px solid {BORDER};
                border-radius: 8px; padding: 6px 10px; font-size: 13px;
                font-family: 'Inter'; font-weight: 600;
            }}
            QDateEdit:hover {{ border: 1px solid {BLUE}; }}
            QDateEdit::drop-down {{ border: none; width: 28px; }}
        """

        from_lbl = QLabel(tr("reports.finance.date_from"))
        from_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-weight: 700; "
                                f"font-family: 'Inter'; background: transparent;")
        self._date_from = QDateEdit()
        self._date_from.setCalendarPopup(True)
        self._date_from.setDate(QDate.currentDate().addMonths(-6))
        self._date_from.setStyleSheet(date_style)

        to_lbl = QLabel(tr("reports.finance.date_to"))
        to_lbl.setStyleSheet(from_lbl.styleSheet())
        self._date_to = QDateEdit()
        self._date_to.setCalendarPopup(True)
        self._date_to.setDate(QDate.currentDate())
        self._date_to.setStyleSheet(date_style)

        # VS second period (hidden by default)
        self._vs_frame = QFrame()
        self._vs_frame.setStyleSheet(self._date_frame.styleSheet())
        vs_lay = QHBoxLayout(self._vs_frame)
        vs_lay.setContentsMargins(16, 10, 16, 10)
        vs_lay.setSpacing(12)

        vs_lbl = QLabel(tr("reports.finance.vs_period"))
        vs_lbl.setStyleSheet(f"color: {ORANGE}; font-size: 12px; font-weight: 800; "
                              f"font-family: 'Inter'; background: transparent;")
        self._date_from_b = QDateEdit()
        self._date_from_b.setCalendarPopup(True)
        self._date_from_b.setDate(QDate.currentDate().addMonths(-12))
        self._date_from_b.setStyleSheet(date_style)
        self._date_to_b = QDateEdit()
        self._date_to_b.setCalendarPopup(True)
        self._date_to_b.setDate(QDate.currentDate().addMonths(-6))
        self._date_to_b.setStyleSheet(date_style)

        self._btn_generate = QPushButton(tr("reports.finance.generate"))
        self._btn_generate.setStyleSheet(f"""
            QPushButton {{
                background-color: {BLUE}; color: white; border: none;
                border-radius: 8px; padding: 8px 20px; font-size: 13px;
                font-weight: 800; font-family: 'Inter';
            }}
            QPushButton:hover {{ background-color: #4B8BF5; }}
        """)
        self._btn_generate.clicked.connect(self._load_data)

        date_lay.addWidget(from_lbl)
        date_lay.addWidget(self._date_from)
        date_lay.addWidget(to_lbl)
        date_lay.addWidget(self._date_to)
        vs_lay.addWidget(vs_lbl)
        vs_lay.addWidget(self._date_from_b)
        vs_lay.addWidget(self._date_to_b)

        self._root.addWidget(self._date_frame)
        self._root.addWidget(self._vs_frame)
        self._vs_frame.hide()
        self._root.addWidget(self._btn_generate)

        # ── KPIs ────────────────────────────────────────────────────
        self._kpi_grid = QGridLayout()
        self._kpi_grid.setSpacing(16)
        self._kpi_cards = {}
        self._root.addLayout(self._kpi_grid)

        # ── Chart ───────────────────────────────────────────────────
        self._chart_card = SectionCard("")
        self._chart = MiniBarChart()
        self._chart_card.add_widget(self._chart)
        self._root.addWidget(self._chart_card)

        # ── Analysis ────────────────────────────────────────────────
        self._analysis_frame = QFrame()
        self._analysis_frame.setStyleSheet(f"""
            QFrame {{ background-color: {BG_CARD}; border: 1px solid {BORDER};
                      border-radius: 14px; }}
        """)
        self._analysis_lay = QVBoxLayout(self._analysis_frame)
        self._analysis_lay.setContentsMargins(18, 16, 18, 16)
        self._analysis_lay.setSpacing(4)
        self._root.addWidget(self._analysis_frame)
        self._analysis_frame.hide()

        # ── Table ───────────────────────────────────────────────────
        self._table_card = SectionCard(tr("reports.finance.detail_table"))
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
                letter-spacing: 0.8px;
            }}
        """)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table_card.add_widget(self._table)
        self._root.addWidget(self._table_card)

        self._root.addStretch()
        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _on_source_changed(self, idx):
        sources = ["ingresos", "egresos", "cartera", "cuentas_cobro"]
        self._current_source = sources[idx]
        self._load_data()

    def _on_type_changed(self, idx):
        types = ["general", "periods", "vs", "detailed"]
        self._current_type = types[idx]
        show_dates = self._current_type in ("periods", "detailed")
        show_vs = self._current_type == "vs"
        self._date_frame.setVisible(show_dates or show_vs)
        self._vs_frame.setVisible(show_vs)
        self._load_data()

    def _load_data(self):
        try:
            if self._current_type == "vs":
                self._load_vs()
            elif self._current_type == "general":
                self._load_general_semester()
            elif self._current_type == "periods":
                self._load_by_period()
            else:
                self._load_detailed()
        except Exception as e:
            print(f"[FinanceReport] Error: {e}")

    def _load_general_semester(self):
        data = reports_repo.get_finance_summary()
        self._show_summary_kpis(data)
        self._show_summary_table(data)
        self._analysis_frame.hide()

    def _load_by_period(self):
        d_from = self._date_from.date().toPyDate()
        d_to = self._date_to.date().toPyDate()
        data = reports_repo.get_finance_summary(str(d_from), str(d_to))
        self._show_summary_kpis(data)
        self._show_summary_table(data)
        self._analysis_frame.hide()

    def _load_detailed(self):
        d_from = self._date_from.date().toPyDate()
        d_to = self._date_to.date().toPyDate()
        data = reports_repo.get_finance_summary(str(d_from), str(d_to))
        self._show_summary_kpis(data)
        self._show_summary_table(data)
        self._analysis_frame.hide()

    def _load_vs(self):
        d_a_from = self._date_from.date().toPyDate()
        d_a_to = self._date_to.date().toPyDate()
        d_b_from = self._date_from_b.date().toPyDate()
        d_b_to = self._date_to_b.date().toPyDate()

        vs = reports_repo.get_finance_vs(str(d_a_from), str(d_a_to),
                                          str(d_b_from), str(d_b_to))

        # KPIs
        self._clear_layout(self._kpi_grid)
        a, b = vs["period_a"], vs["period_b"]
        kpis = [
            ("\U0001f4b0", tr("reports.finance.total_income"),
             f"${a['income']:,.0f}", f"${b['income']:,.0f}", GREEN),
            ("\U0001f4e4", tr("reports.finance.total_expenses"),
             f"${a['expenses']:,.0f}", f"${b['expenses']:,.0f}", RED),
            ("\u2696\ufe0f", tr("reports.finance.balance"),
             f"${a['balance']:,.0f}", f"${b['balance']:,.0f}", BLUE),
            ("\U0001f9fe", tr("reports.finance.receivables"),
             f"${a['receivables_amount']:,.0f}", f"${b['receivables_amount']:,.0f}", YELLOW),
        ]
        for i, (icon, label, val_a, val_b, color) in enumerate(kpis):
            card = KPICard(icon, label, val_a, color)
            self._kpi_grid.addWidget(card, 0, i)

        # Chart
        self._chart_card.setTitle(tr("reports.finance.vs_chart"))
        labels = [tr("reports.finance.total_income"), tr("reports.finance.total_expenses"),
                  tr("reports.finance.balance"), tr("reports.finance.receivables")]
        d_a = [a["income"], a["expenses"], a["balance"], a["receivables_amount"]]
        d_b = [b["income"], b["expenses"], b["balance"], b["receivables_amount"]]
        self._chart.set_data(labels, d_a, d_b, GREEN, ORANGE)

        # Analysis
        self._analysis_frame.show()
        self._clear_layout(self._analysis_lay)
        analysis_title = QLabel(tr("reports.finance.vs_analysis"))
        analysis_title.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 800; "
                                      f"font-family: 'Inter'; letter-spacing: 1.2px; "
                                      f"background: transparent;")
        self._analysis_lay.addWidget(analysis_title)
        self._analysis_lay.addSpacing(6)

        for key, label in [("income", tr("reports.finance.total_income")),
                           ("expenses", tr("reports.finance.total_expenses")),
                           ("balance", tr("reports.finance.balance"))]:
            info = vs["analysis"][key]
            pct = info["pct_change"]
            arrow = "\u2191" if info["trend"] == "up" else ("\u2193" if info["trend"] == "down" else "\u2192")
            color = GREEN if info["trend"] == "up" else (RED if info["trend"] == "down" else TEXT_SEC)
            if key == "expenses":
                color = RED if info["trend"] == "up" else GREEN
            row = QLabel(f"  {label}: {arrow} {pct:+.1f}%  (${info['change']:+,.0f})")
            row.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: 600; "
                               f"font-family: 'Inter'; background: transparent; padding: 3px 0;")
            self._analysis_lay.addWidget(row)

        # Table
        self._show_vs_table(vs)

    def _show_summary_kpis(self, data):
        self._clear_layout(self._kpi_grid)
        kpis = [
            ("\U0001f4b0", tr("reports.finance.total_income"),
             f"${data['total_income']:,.0f}", GREEN),
            ("\U0001f4e4", tr("reports.finance.total_expenses"),
             f"${data['total_expenses']:,.0f}", RED),
            ("\u2696\ufe0f", tr("reports.finance.balance"),
             f"${data['balance']:,.0f}", BLUE),
            ("\U0001f9fe", tr("reports.finance.receivables"),
             f"{data['receivables_count']}", YELLOW),
        ]
        for i, (icon, label, value, color) in enumerate(kpis):
            card = KPICard(icon, label, value, color)
            self._kpi_grid.addWidget(card, 0, i)

    def _show_summary_table(self, data):
        sources = data.get("income_by_source", [])
        cats = data.get("expenses_by_category", [])

        if self._current_source == "ingresos":
            rows = [(s["source"], s["total"], s["count"]) for s in sources]
            headers = [tr("reports.finance.tbl_source"),
                       tr("reports.finance.tbl_total"),
                       tr("reports.finance.tbl_count")]
        elif self._current_source == "egresos":
            rows = [(c["category"], c["total"], c["count"]) for c in cats]
            headers = [tr("reports.finance.tbl_category"),
                       tr("reports.finance.tbl_total"),
                       tr("reports.finance.tbl_count")]
        elif self._current_source == "cartera":
            rows = [(tr("reports.finance.receivables"),
                     data["receivables_amount"], data["receivables_count"])]
            headers = [tr("reports.finance.tbl_type"),
                       tr("reports.finance.tbl_amount"),
                       tr("reports.finance.tbl_count")]
        else:
            rows = [(tr("reports.finance.src_collection"),
                     data["collection_amount"], data["collection_count"])]
            headers = [tr("reports.finance.tbl_type"),
                       tr("reports.finance.tbl_amount"),
                       tr("reports.finance.tbl_count")]

        self._table.setColumnCount(len(headers))
        self._table.setHorizontalHeaderLabels(headers)
        self._table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val) if not isinstance(val, float) else f"${val:,.0f}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._table.setItem(r, c, item)

        self._chart_card.setTitle(tr("reports.finance.chart_title"))

    def _show_vs_table(self, vs):
        headers = [tr("reports.finance.tbl_metric"),
                   tr("reports.finance.tbl_period_a"),
                   tr("reports.finance.tbl_period_b"),
                   tr("reports.finance.tbl_change"),
                   tr("reports.finance.tbl_pct")]
        rows = []
        for key, label in [("income", tr("reports.finance.total_income")),
                           ("expenses", tr("reports.finance.total_expenses")),
                           ("balance", tr("reports.finance.balance")),
                           ("receivables_amount", tr("reports.finance.receivables"))]:
            info = vs["analysis"][key]
            rows.append((
                label,
                f"${info['period_a']:,.0f}",
                f"${info['period_b']:,.0f}",
                f"${info['change']:+,.0f}",
                f"{info['pct_change']:+.1f}%",
            ))

        self._table.setColumnCount(len(headers))
        self._table.setHorizontalHeaderLabels(headers)
        self._table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if c == 4:
                    try:
                        pct = float(val.replace("%", "").replace("+", ""))
                        if pct > 0:
                            item.setForeground(QColor(GREEN))
                        elif pct < 0:
                            item.setForeground(QColor(RED))
                    except ValueError:
                        pass
                self._table.setItem(r, c, item)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
