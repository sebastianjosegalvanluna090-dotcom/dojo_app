from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QWidget, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

BG_DIALOG = "#111111"
BG_CARD   = "#161616"
BORDER    = "#2A2A2A"
RED       = "#C8102E"
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
    if not val: return "—"
    try:
        return val.strftime("%d/%m/%Y") if hasattr(val, "strftime") else str(val)[:10]
    except Exception:
        return str(val)

def _initials(name: str) -> str:
    words = (name or "?").strip().split()
    return "".join(w[0].upper() for w in words[:2]) or "?"


class ClientHistoryDialog(QDialog):
    def __init__(self, repo, person_id: int, debtor_name: str, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.person_id = person_id
        self.debtor_name = debtor_name
        self.setWindowTitle(f"Historial · {debtor_name}")
        self.setMinimumSize(820, 620)
        self.resize(900, 680)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        body = QVBoxLayout(content)
        body.setContentsMargins(28, 24, 28, 24)
        body.setSpacing(20)

        # Header with avatar + client data
        hdr = QHBoxLayout()
        hdr.setSpacing(16)

        avatar = QLabel(_initials(self.debtor_name))
        avatar.setFixedSize(56, 56)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background: #1A2A1A; color: {GREEN};
            border-radius: 28px; font-size: 18px; font-weight: 800;
        """)
        hdr.addWidget(avatar)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        name_lbl = QLabel(self.debtor_name)
        name_lbl.setStyleSheet("color: white; font-size: 20px; font-weight: 900;")
        info_col.addWidget(name_lbl)

        contact = {}
        try:
            contact = self.repo.get_person_contact(self.person_id)
        except Exception:
            pass

        if contact.get("documento"):
            doc_lbl = QLabel(contact["documento"])
            doc_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px;")
            info_col.addWidget(doc_lbl)

        contact_row = QHBoxLayout()
        if contact.get("email"):
            email_lbl = QLabel(contact['email'])
            email_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px;")
            contact_row.addWidget(email_lbl)
        if contact.get("phone"):
            phone_lbl = QLabel(contact['phone'])
            phone_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px;")
            contact_row.addWidget(phone_lbl)
        contact_row.addStretch()
        info_col.addLayout(contact_row)
        hdr.addLayout(info_col, 1)
        body.addLayout(hdr)

        # Load all receivables for this person
        all_receivables = []
        try:
            all_receivables = self.repo.get_by_person(self.person_id)
        except Exception:
            all_receivables = []

        # 3 KPI cards
        total_deuda     = sum(float(r.get("original_amount", 0) or 0) for r in all_receivables)
        total_pagado    = sum(float(r.get("paid_amount", 0) or 0) for r in all_receivables)
        total_pendiente = sum(float(r.get("pending_amount", 0) or 0) for r in all_receivables)

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)
        kpi_row.addWidget(self._kpi_card("Total deuda", _fmt(total_deuda), TEXT_PRI))
        kpi_row.addWidget(self._kpi_card("Total pagado", _fmt(total_pagado), GREEN))
        kpi_row.addWidget(self._kpi_card("Pendiente", _fmt(total_pendiente), YELLOW if total_pendiente > 0 else GREEN))
        body.addLayout(kpi_row)

        # Table: receivable history
        sec_lbl = QLabel("HISTORIAL DE CARTERAS")
        sec_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        body.addWidget(sec_lbl)

        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Fecha", "Monto original", "Pagado", "Pendiente", "Vencimiento", "Estado"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setShowGrid(False)
        table.setStyleSheet(f"""
            QTableWidget {{
                background: {BG_CARD}; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 10px; font-size: 13px;
            }}
            QHeaderView::section {{
                background: {BG_CARD}; color: {TEXT_SEC};
                border: none; border-bottom: 1px solid {BORDER};
                padding: 8px; font-size: 11px; font-weight: 700;
            }}
            QTableWidget::item {{ padding: 8px; border-bottom: 1px solid #1A1A1A; }}
            QTableWidget::item:selected {{ background: #1A0A0C; color: white; }}
        """)

        STATUS_LABELS = {
            "open": "Abierto", "partial": "Parcial",
            "paid": "Pagado", "cancelled": "Cancelado"
        }
        STATUS_COLORS = {
            "open": RED, "partial": YELLOW, "paid": GREEN, "cancelled": TEXT_MUT
        }

        table.setRowCount(len(all_receivables))
        for i, r in enumerate(all_receivables):
            status = r.get("status", "")
            color  = STATUS_COLORS.get(status, TEXT_MUT)

            items_data = [
                _fmt_date(r.get("created_at")),
                _fmt(r.get("original_amount")),
                _fmt(r.get("paid_amount")),
                _fmt(r.get("pending_amount")),
                _fmt_date(r.get("due_date")),
                STATUS_LABELS.get(status, status),
            ]
            for j, val in enumerate(items_data):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                if j == 5:
                    item.setForeground(QColor(color))
                self.table_item_safe(table, i, j, item)
            table.setRowHeight(i, 42)

        body.addWidget(table, 1)

        # Close button
        btn_close = QPushButton("Cerrar")
        btn_close.setFixedHeight(40)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 8px; font-size: 13px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #555; }}
        """)
        btn_close.clicked.connect(self.reject)
        body.addWidget(btn_close)

        scroll.setWidget(content)
        root.addWidget(scroll)

    def table_item_safe(self, table, row, col, item):
        try:
            table.setItem(row, col, item)
        except Exception:
            pass

    def _kpi_card(self, label: str, value: str, color: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD}; border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 80))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;")
        val = QLabel(value)
        val.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 900;")
        layout.addWidget(lbl)
        layout.addWidget(val)
        return card
