from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QFrame, QTextEdit,
    QWidget, QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

from core.i18n import tr
from repositories.finances_receivables_repository import FinancesReceivablesRepository
from repositories.finances_income_repository import FinancesIncomeRepository

BG_DIALOG = "#111111"
BG_CARD   = "#161616"
BG_INPUT  = "#1C1C1C"
BORDER    = "#2A2A2A"
RED       = "#C8102E"
RED_H     = "#E8152F"
TEXT_PRI  = "#F0F0F0"
TEXT_MUT  = "#666666"
TEXT_SEC  = "#888888"
GREEN     = "#22C55E"


class ReceivablePaymentDialog(QDialog):
    def __init__(self, repo, receivable, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.receivable = receivable
        self.income_repo = FinancesIncomeRepository()
        self.setWindowTitle(tr("finances.receivables.register_payment"))
        self.setMinimumSize(480, 420)
        self.resize(520, 460)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        title = QLabel(tr("finances.receivables.register_payment"))
        title.setStyleSheet("color: white; font-size: 22px; font-weight: 900;")
        root.addWidget(title)

        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(20, 14, 20, 14)
        info_layout.setSpacing(8)

        debtor_row = QHBoxLayout()
        debtor_label = QLabel(tr("finances.receivables.debtor"))
        debtor_label.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; font-weight: 700; border: none; background: transparent;")
        debtor_row.addWidget(debtor_label)
        debtor_val = QLabel(str(self.receivable.get("debtor_name", "")))
        debtor_val.setStyleSheet("color: white; font-size: 14px; font-weight: 900; border: none; background: transparent;")
        debtor_row.addWidget(debtor_val, 1)
        info_layout.addLayout(debtor_row)

        pending_row = QHBoxLayout()
        pending_label = QLabel(tr("finances.receivables.pending"))
        pending_label.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; font-weight: 700; border: none; background: transparent;")
        pending_row.addWidget(pending_label)
        pending_amount = float(self.receivable.get("pending_amount", 0) or 0)
        self._pending_val = QLabel(self._format_money(pending_amount))
        self._pending_val.setStyleSheet("color: white; font-size: 14px; font-weight: 900; border: none; background: transparent;")
        pending_row.addWidget(self._pending_val, 1)
        info_layout.addLayout(pending_row)

        root.addWidget(info_frame)

        form_frame = QFrame()
        form_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 16, 20, 16)
        form_layout.setSpacing(10)

        amount_layout = QVBoxLayout()
        amount_layout.setSpacing(4)
        amt_label = QLabel(tr("finances.receivables.payment_amount"))
        amt_label.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        amount_layout.addWidget(amt_label)
        self.amount = QLineEdit()
        self.amount.setPlaceholderText("0")
        self.amount.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 12px; font-size: 13px; min-height: 38px;
            }}
            QLineEdit:focus {{ border-color: {RED}; }}
        """)
        amount_layout.addWidget(self.amount)
        form_layout.addLayout(amount_layout)

        method_layout = QVBoxLayout()
        method_layout.setSpacing(4)
        method_label = QLabel(tr("finances.receivables.payment_method"))
        method_label.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        method_layout.addWidget(method_label)
        self.payment_method = QComboBox()
        self.payment_method.addItem("Efectivo", None)
        self.payment_method.addItem("Transferencia", None)
        self.payment_method.addItem("Tarjeta", None)
        self.payment_method.addItem("Otro", None)
        self.payment_method.setStyleSheet(f"""
            QComboBox {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 12px; font-size: 13px; min-height: 38px;
            }}
            QComboBox::drop-down {{ border: none; width: 30px; }}
            QComboBox QAbstractItemView {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                selection-background-color: {RED};
            }}
        """)
        method_layout.addWidget(self.payment_method)
        form_layout.addLayout(method_layout)

        note_layout = QVBoxLayout()
        note_layout.setSpacing(4)
        note_label = QLabel(tr("finances.receivables.payment_note"))
        note_label.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        note_layout.addWidget(note_label)
        self.note = QTextEdit()
        self.note.setMaximumHeight(80)
        self.note.setStyleSheet(f"""
            QTextEdit {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 8px 12px; font-size: 13px;
            }}
            QTextEdit:focus {{ border-color: {RED}; }}
        """)
        note_layout.addWidget(self.note)
        form_layout.addLayout(note_layout)

        root.addWidget(form_frame)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #FF4444; font-size: 11px;")
        self.lbl_error.hide()
        root.addWidget(self.lbl_error)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton(tr("cancel"))
        btn_cancel.setFixedHeight(38)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUT};
                border: 1px solid {BORDER}; border-radius: 9px; font-size: 13px;
            }}
            QPushButton:hover {{ color: {TEXT_PRI}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton(tr("save"))
        self.btn_save.setFixedHeight(38)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background: {RED}; color: white;
                border: none; border-radius: 9px; font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        self.btn_save.clicked.connect(self._save)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self.btn_save)
        root.addLayout(btn_row)

    def _format_money(self, value):
        try:
            value = float(value or 0)
        except Exception:
            value = 0
        return "$" + f"{value:,.0f}".replace(",", ".")

    def _validate(self):
        amt_text = self.amount.text().strip()
        if not amt_text:
            self.lbl_error.setText(tr("finances.receivables.err_amount_required"))
            self.lbl_error.show()
            return False
        try:
            val = float(amt_text)
            if val <= 0:
                raise ValueError
            pending = float(self.receivable.get("pending_amount", 0) or 0)
            if val > pending:
                self.lbl_error.setText(tr("finances.receivables.err_amount_exceeds"))
                self.lbl_error.show()
                return False
        except ValueError:
            self.lbl_error.setText(tr("finances.receivables.err_amount_positive"))
            self.lbl_error.show()
            return False
        self.lbl_error.hide()
        return True

    def _save(self):
        if not self._validate():
            return

        amount_val = float(self.amount.text().strip())
        payment_method = self.payment_method.currentText()

        try:
            self.repo.register_payment(
                receivable_id=self.receivable["id"],
                amount=amount_val,
                payment_method=payment_method,
                note=self.note.toPlainText().strip(),
            )

            self.income_repo.create_income(
                item_type="receivable_payment",
                reference_id=self.receivable["id"],
                payer_name=self.receivable.get("debtor_name", ""),
                total=amount_val,
                note=self.note.toPlainText().strip(),
            )

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, tr("common.error"), str(e))
