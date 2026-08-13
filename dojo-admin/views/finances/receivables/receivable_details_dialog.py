"""
ReceivableDetailsDialog — detalle de un receivable.
Estructura visual idéntica a IncomeDetailsDialog.
Ubicación destino: views/finances/receivables/receivable_details_dialog.py
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QScrollArea, QWidget,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from datetime import datetime

from core.i18n import tr, trf

BG_DIALOG = "#111111"
BG_CARD   = "#161616"
BG_HOVER  = "#1A1A1A"
BORDER    = "#2A2A2A"
RED       = "#C8102E"
RED_H     = "#E8152F"
GREEN     = "#22C55E"
YELLOW    = "#EAB308"
BLUE      = "#3B82F6"
TEXT_PRI  = "#F0F0F0"
TEXT_SEC  = "#888888"
TEXT_MUT  = "#666666"


def _fmt(value) -> str:
    try:
        return "$" + f"{float(value or 0):,.0f}".replace(",", ".")
    except Exception:
        return "$0"


def _fmt_date(val) -> str:
    if not val:
        return "—"
    try:
        if hasattr(val, "strftime"):
            return val.strftime("%d/%m/%Y")
        return str(val)[:10]
    except Exception:
        return str(val)


def _initials(name: str) -> str:
    words = (name or "?").strip().split()
    return "".join(w[0].upper() for w in words[:2]) or "?"


class ReceivableDetailsDialog(QDialog):
    """
    Diálogo de detalle del receivable.
    Idéntico en estructura visual al IncomeDetailsDialog.
    """

    def __init__(self, repo, receivable: dict, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.receivable = receivable
        self._action = None

        debtor = str(receivable.get("debtor_name") or "Deudor")
        self.setWindowTitle(f"Detalle · {debtor}")
        self.setMinimumSize(780, 580)
        self.resize(860, 640)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")
        self._build_ui()

    @property
    def action(self):
        return self._action

    # ─────────────────────────────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Cache de pagos (una sola llamada al repo) ──────────────────
        try:
            self._payments_cache = self.repo.get_payments(self.receivable["id"])
        except Exception:
            self._payments_cache = []

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
        """)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        body = QVBoxLayout(content)
        body.setContentsMargins(28, 24, 28, 20)
        body.setSpacing(20)

        # ── Header: avatar + nombre + estado ──
        body.addLayout(self._build_header())

        # ── Stats: total / pagado / pendiente ──
        body.addLayout(self._build_stats())

        # ── Historial de pagos ──
        body.addWidget(self._section_label("HISTORIAL DE PAGOS REALIZADOS"))
        self.lbl_last_payment = self._build_last_payment_row()
        body.addWidget(self.lbl_last_payment)
        self.payments_table = self._build_payments_table()
        body.addWidget(self.payments_table)

        # ── Nota ──
        note = str(self.receivable.get("note") or self.receivable.get("concept") or "").strip()
        if note:
            note_lbl = QLabel("Nota: " + note)
            note_lbl.setWordWrap(True)
            note_lbl.setStyleSheet(
                f"color: {TEXT_SEC}; font-size: 12px; font-weight: 600;")
            body.addWidget(note_lbl)

        body.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        # ── Footer botones ──
        root.addWidget(self._build_footer())

        self._populate_payments()

    def _build_header(self) -> QHBoxLayout:
        hl = QHBoxLayout()
        hl.setSpacing(20)

        # Avatar circular
        initials = _initials(self.receivable.get("debtor_name", "?"))
        av = QLabel(initials)
        av.setFixedSize(56, 56)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet(f"""
            QLabel {{
                background: #1A2A1A; color: {GREEN};
                border-radius: 28px;
                font-size: 18px; font-weight: 800;
                font-family: 'Inter'; border: none;
            }}
        """)
        hl.addWidget(av)

        # Nombre + tipo + fecha vencimiento
        text_col = QVBoxLayout()
        text_col.setSpacing(4)

        name_lbl = QLabel(str(self.receivable.get("debtor_name") or "—"))
        name_lbl.setStyleSheet(
            "color: white; font-size: 22px; font-weight: 900; font-family: 'Inter';")
        text_col.addWidget(name_lbl)

        concept = str(self.receivable.get("concept") or self.receivable.get("note") or "")
        if concept:
            concept_lbl = QLabel(concept)
            concept_lbl.setStyleSheet(
                f"color: {TEXT_SEC}; font-size: 13px; font-weight: 600; font-family: 'Inter';")
            text_col.addWidget(concept_lbl)

        due_str = _fmt_date(self.receivable.get("due_date"))
        due_lbl = QLabel(f"Vencimiento: {due_str}")
        due_lbl.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 12px; font-weight: 600; font-family: 'Inter';")
        text_col.addWidget(due_lbl)
        text_col.addStretch()

        hl.addLayout(text_col, 1)

        # Badge de estado
        status = str(self.receivable.get("status", "open"))
        status_map = {
            "open":      ("Abierto",    RED,     "rgba(200,16,46,0.10)",    "rgba(200,16,46,0.25)"),
            "partial":   ("Parcial",    YELLOW,  "rgba(234,179,8,0.10)",    "rgba(234,179,8,0.25)"),
            "paid":      ("Pagado",     GREEN,   "rgba(34,197,94,0.10)",    "rgba(34,197,94,0.25)"),
            "cancelled": ("Cancelado",  TEXT_MUT,"rgba(102,102,102,0.10)", "rgba(102,102,102,0.25)"),
        }
        stext, scolor, sbg, sborder = status_map.get(status, status_map["open"])
        badge = QLabel(stext)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setMinimumWidth(100)
        badge.setFixedHeight(32)
        badge.setStyleSheet(f"""
            QLabel {{
                background: {sbg}; color: {scolor};
                border: 1px solid {sborder};
                border-radius: 7px; padding: 4px 12px;
                font-size: 11px; font-weight: 900; font-family: 'Inter';
            }}
        """)
        hl.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)
        return hl

    def _build_stats(self) -> QHBoxLayout:
        hl = QHBoxLayout()
        hl.setSpacing(14)

        original = self.receivable.get("original_amount", 0)
        paid     = self.receivable.get("paid_amount", 0)
        pending  = self.receivable.get("pending_amount", 0)
        p_color  = YELLOW if float(pending or 0) > 0 else TEXT_MUT

        hl.addWidget(self._stat_card("Total original", _fmt(original), TEXT_PRI))
        hl.addWidget(self._stat_card("Pagado",         _fmt(paid),     GREEN))
        hl.addWidget(self._stat_card("Pendiente",      _fmt(pending),  p_color))
        return hl

    def _build_last_payment_row(self) -> QLabel:
        lbl = QLabel("")
        lbl.setStyleSheet(
            f"color: {GREEN}; font-size: 13px; font-weight: 800; font-family: 'Inter';")
        try:
            payments = getattr(self, "_payments_cache", [])
            if payments:
                last = payments[-1]
                date_str = _fmt_date(last.get("payment_date"))
                amount_str = _fmt(last.get("amount", 0))
                lbl.setText(f"Último pago: {date_str}  —  {amount_str}")
            else:
                lbl.setText("Sin pagos registrados")
                lbl.setStyleSheet(
                    f"color: {TEXT_MUT}; font-size: 13px; font-weight: 800; font-family: 'Inter';")
        except Exception:
            lbl.setText("Sin pagos registrados")
            lbl.setStyleSheet(
                f"color: {TEXT_MUT}; font-size: 13px; font-weight: 800; font-family: 'Inter';")
        return lbl

    def _stat_card(self, label: str, value: str, color: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD}; border: 1px solid {BORDER};
                border-radius: 12px;
            }}
            QLabel {{ background: transparent; border: none; }}
        """)
        vl = QVBoxLayout(card)
        vl.setContentsMargins(16, 14, 16, 14)
        vl.setSpacing(6)

        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 11px; font-weight: 700; font-family: 'Inter';")
        val = QLabel(value)
        val.setStyleSheet(
            f"color: {color}; font-size: 22px; font-weight: 900; font-family: 'Inter';")

        vl.addWidget(lbl)
        vl.addWidget(val)
        return card

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 14px; font-weight: 800; font-family: 'Inter';")
        return lbl

    def _build_payments_table(self) -> QTableWidget:
        tbl = QTableWidget(0, 4)
        tbl.setHorizontalHeaderLabels(["Fecha", "Monto", "Método", "Nota"])
        tbl.verticalHeader().setVisible(False)
        tbl.setShowGrid(False)
        tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tbl.setStyleSheet(f"""
            QTableWidget {{
                background: {BG_CARD}; border: 1px solid {BORDER};
                border-radius: 12px; outline: none;
                color: {TEXT_PRI}; gridline-color: transparent;
                selection-background-color: {BG_HOVER}; font-size: 13px;
            }}
            QHeaderView::section {{
                background: {BG_HOVER}; color: {TEXT_SEC};
                border: none; border-bottom: 1px solid {BORDER};
                padding: 12px; font-size: 10px; font-weight: 900;
                font-family: 'Inter';
            }}
            QTableWidget::item {{
                border: none; border-bottom: 1px solid {BORDER}; padding: 8px;
            }}
        """)
        tbl.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        tbl.setColumnWidth(0, 120)
        tbl.setColumnWidth(1, 130)
        tbl.setColumnWidth(2, 130)
        tbl.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        return tbl

    def _build_footer(self) -> QFrame:
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                background: {BG_DIALOG};
                border-top: 1px solid {BORDER};
            }}
            QLabel {{ background: transparent; border: none; }}
        """)
        hl = QHBoxLayout(footer)
        hl.setContentsMargins(28, 14, 28, 14)
        hl.setSpacing(12)

        hl.addStretch()

        btn_cancel_rec = QPushButton("Cancelar receivable")
        btn_cancel_rec.setFixedHeight(38)
        btn_cancel_rec.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel_rec.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: #FF4444;
                border: 1px solid #3A1A1A; border-radius: 9px;
                font-size: 13px; font-weight: 700; font-family: 'Inter';
                padding: 0 18px;
            }}
            QPushButton:hover {{
                background: rgba(255,68,68,0.10); border-color: #FF4444;
            }}
        """)
        btn_cancel_rec.clicked.connect(lambda: self._on_action("cancel"))

        btn_pay = QPushButton("⚡  Registrar pago")
        btn_pay.setFixedHeight(38)
        btn_pay.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pay.setStyleSheet(f"""
            QPushButton {{
                background: {RED}; color: white;
                border: none; border-radius: 9px;
                font-size: 13px; font-weight: 800; font-family: 'Inter';
                padding: 0 22px;
            }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        btn_pay.clicked.connect(lambda: self._on_action("pay"))

        status = str(self.receivable.get("status", "open"))
        if status in ("paid", "cancelled"):
            btn_cancel_rec.hide()
            btn_pay.hide()

        hl.addWidget(btn_cancel_rec)
        hl.addWidget(btn_pay)
        return footer

    # ─────────────────────────────────────────────────────────────────
    # Data
    # ─────────────────────────────────────────────────────────────────
    def _populate_payments(self):
        payments = getattr(self, "_payments_cache", [])

        self.payments_table.setRowCount(0)
        if not payments:
            self.payments_table.setRowCount(1)
            self.payments_table.setRowHeight(0, 44)
            self.payments_table.setSpan(0, 0, 1, 4)
            empty = QTableWidgetItem("Sin pagos registrados")
            empty.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.payments_table.setItem(0, 0, empty)
            self.payments_table.setFixedHeight(
                self.payments_table.horizontalHeader().height() + 44 + 2)
            return

        self.payments_table.setRowCount(len(payments))
        for i, p in enumerate(payments):
            self.payments_table.setItem(i, 0, QTableWidgetItem(_fmt_date(p.get("payment_date"))))
            self.payments_table.setItem(i, 1, QTableWidgetItem(_fmt(p.get("amount", 0))))
            method = str(p.get("payment_method_id") or p.get("payment_method") or "—")
            self.payments_table.setItem(i, 2, QTableWidgetItem(method))
            self.payments_table.setItem(i, 3, QTableWidgetItem(str(p.get("note") or "")))
            self.payments_table.setRowHeight(i, 44)

        hdr_h = self.payments_table.horizontalHeader().height()
        visible = min(len(payments), 5)
        self.payments_table.setFixedHeight(hdr_h + 44 * visible + 4)
        if len(payments) > 5:
            self.payments_table.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    # ─────────────────────────────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────────────────────────────
    def _on_action(self, action: str):
        self._action = action
        self.accept()

    def closeEvent(self, event):
        self.setGraphicsEffect(None)
        super().closeEvent(event)