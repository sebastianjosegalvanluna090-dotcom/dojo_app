from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit,
    QTextBrowser,
    QPushButton, QFrame, QScrollArea, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox, QDateEdit,
    QCompleter, QSizePolicy, QApplication,
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer
from datetime import datetime, date
import re
import json
import os
import webbrowser
from urllib.parse import quote

from core.i18n import tr
from core.debug import debug_log
from services.receipt_generator import (
    prepare_receipt_files,
    build_receipt_number,
    render_receipt_html,
)
from services.receipt_data_builder import build_receipt_widget_data
from views.finances.income.receipt_widget import ReceiptPreviewArea
from pathlib import Path

WEB_ENGINE_AVAILABLE = False


def trf(key, fallback):
    value = tr(key)
    return fallback if value == key else value


BG_DIALOG = "#111111"
BG_INPUT  = "#1C1C1C"
BG_CARD   = "#161616"
BG_HOVER  = "#1E1E1E"
BORDER    = "#2A2A2A"
RED       = "#C8102E"
RED_H     = "#E8152F"
TEXT_PRI  = "#F0F0F0"
TEXT_SEC  = "#888888"
TEXT_MUT  = "#666666"
GREEN     = "#22C55E"
YELLOW    = "#EAB308"

RECEIPT_PAPER = "#F8FAFC"
RECEIPT_INK   = "#111827"
RECEIPT_MUTED = "#6B7280"
RECEIPT_LINE  = "#CBD5E1"


def format_money(value):
    try:
        value = float(value or 0)
    except Exception:
        value = 0
    return "$" + f"{value:,.0f}".replace(",", ".")


class ItemDialog(QDialog):
    def __init__(self, parent=None, item_data=None):
        super().__init__(parent)
        self._item_data = item_data
        is_edit = item_data is not None
        self.setWindowTitle(trf("finances.income.dialog.item_add", "Agregar artículo") if not is_edit
                            else trf("finances.income.dialog.item_edit", "Editar artículo"))
        self.setMinimumSize(420, 320)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")
        self._build_ui()
        if is_edit:
            self._populate(item_data)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)

        self.input_item_type = QComboBox()
        self.input_item_type.setStyleSheet(self._combo_style())
        self.input_item_type.addItem(trf("finances.income.dialog.item_type.membership", "Membresía"), "membership")
        self.input_item_type.addItem(trf("finances.income.dialog.item_type.product", "Producto de inventario"), "product")
        self.input_item_type.addItem(trf("finances.income.dialog.item_type.service", "Servicio"), "service")
        self.input_item_type.addItem(trf("finances.income.dialog.item_type.receivable", "Cartera"), "receivable")
        self.input_item_type.addItem(trf("finances.income.dialog.item_type.agreement", "Acuerdo"), "agreement")
        root.addWidget(QLabel(trf("finances.income.dialog.item_type", "Tipo de artículo")))
        root.addWidget(self.input_item_type)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText(trf("finances.income.dialog.item_name", "Nombre del artículo"))
        self.input_name.setStyleSheet(self._input_style())
        root.addWidget(QLabel(trf("finances.income.dialog.item_name", "Nombre del artículo")))
        root.addWidget(self.input_name)

        qty_row = QHBoxLayout()
        qty_row.setSpacing(12)

        qty_col = QVBoxLayout()
        qty_col.setSpacing(4)
        qty_col.addWidget(QLabel(trf("finances.income.dialog.item_quantity", "Cantidad")))
        self.spin_qty = QDoubleSpinBox()
        self.spin_qty.setRange(1, 999999)
        self.spin_qty.setDecimals(0)
        self.spin_qty.setValue(1)
        self.spin_qty.setStyleSheet(self._spin_style())
        qty_col.addWidget(self.spin_qty)
        qty_row.addLayout(qty_col)

        price_col = QVBoxLayout()
        price_col.setSpacing(4)
        price_col.addWidget(QLabel(trf("finances.income.dialog.item_unit_price", "Valor unitario")))
        self.spin_price = QDoubleSpinBox()
        self.spin_price.setRange(0, 999999999)
        self.spin_price.setDecimals(0)
        self.spin_price.setSingleStep(1000)
        self.spin_price.setPrefix("$ ")
        self.spin_price.setStyleSheet(self._spin_style())
        price_col.addWidget(self.spin_price)
        qty_row.addLayout(price_col)

        disc_col = QVBoxLayout()
        disc_col.setSpacing(4)
        disc_col.addWidget(QLabel(trf("finances.income.dialog.item_discount", "Descuento")))
        self.spin_discount = QDoubleSpinBox()
        self.spin_discount.setRange(0, 999999999)
        self.spin_discount.setDecimals(0)
        self.spin_discount.setSingleStep(500)
        self.spin_discount.setPrefix("$ ")
        self.spin_discount.setStyleSheet(self._spin_style())
        disc_col.addWidget(self.spin_discount)
        qty_row.addLayout(disc_col)

        root.addLayout(qty_row)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton(tr("cancel"))
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUT};
                border: 1px solid {BORDER}; border-radius: 9px; font-size: 13px;
            }}
            QPushButton:hover {{ color: {TEXT_PRI}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        is_edit = self._item_data is not None
        btn_add = QPushButton(tr("save") if not is_edit else trf("finances.income.dialog.item_edit", "Editar artículo"))
        btn_add.setFixedHeight(36)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background: {RED}; color: white;
                border: none; border-radius: 9px; font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        btn_add.clicked.connect(self.accept)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_add)
        root.addLayout(btn_row)

    def _populate(self, item_data):
        idx = self.input_item_type.findData(item_data.get("item_type", ""))
        if idx >= 0:
            self.input_item_type.setCurrentIndex(idx)
        self.input_name.setText(item_data.get("name", ""))
        self.spin_qty.setValue(float(item_data.get("quantity", 1)))
        self.spin_price.setValue(float(item_data.get("unit_price", 0)))
        self.spin_discount.setValue(float(item_data.get("discount", 0)))

    def get_data(self):
        qty = int(self.spin_qty.value())
        unit_price = self.spin_price.value()
        discount = self.spin_discount.value()
        subtotal = (qty * unit_price) - discount
        name = self.input_name.text().strip()
        return {
            "item_type": self.input_item_type.currentData(),
            "name": name,
            "base_name": name,
            "quantity": qty,
            "unit_price": unit_price,
            "discount": discount,
            "subtotal": subtotal,
        }

    def _input_style(self):
        return f"""
            QLineEdit {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 12px; font-size: 13px; min-height: 36px;
            }}
            QLineEdit:focus {{ border-color: {RED}; }}
        """

    def _combo_style(self):
        return f"""
            QComboBox {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 12px; font-size: 13px; min-height: 36px;
            }}
            QComboBox::drop-down {{ border: none; width: 30px; }}
            QComboBox QAbstractItemView {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                selection-background-color: {RED};
            }}
        """

    def _spin_style(self):
        return f"""
            QDoubleSpinBox {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 12px; font-size: 13px; min-height: 36px;
            }}
            QDoubleSpinBox:focus {{ border-color: {RED}; }}
        """


class ParticipantDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("finances.income.dialog.participant_add"))
        self.setMinimumSize(400, 280)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText(tr("finances.income.dialog.participant_name"))
        self.input_name.setStyleSheet(self._input_style())
        root.addWidget(QLabel(tr("finances.income.dialog.participant_name")))
        root.addWidget(self.input_name)

        row = QHBoxLayout()
        row.setSpacing(12)

        expected_col = QVBoxLayout()
        expected_col.setSpacing(4)
        expected_col.addWidget(QLabel(tr("finances.income.dialog.participant_expected")))
        self.spin_expected = QDoubleSpinBox()
        self.spin_expected.setRange(0, 999999999)
        self.spin_expected.setDecimals(0)
        self.spin_expected.setSingleStep(1000)
        self.spin_expected.setPrefix("$ ")
        self.spin_expected.setStyleSheet(self._spin_style())
        expected_col.addWidget(self.spin_expected)
        row.addLayout(expected_col)

        paid_col = QVBoxLayout()
        paid_col.setSpacing(4)
        paid_col.addWidget(QLabel(tr("finances.income.dialog.participant_paid")))
        self.spin_paid = QDoubleSpinBox()
        self.spin_paid.setRange(0, 999999999)
        self.spin_paid.setDecimals(0)
        self.spin_paid.setSingleStep(1000)
        self.spin_paid.setPrefix("$ ")
        self.spin_paid.setStyleSheet(self._spin_style())
        paid_col.addWidget(self.spin_paid)
        row.addLayout(paid_col)

        root.addLayout(row)

        self.date_due = QDateEdit()
        self.date_due.setCalendarPopup(True)
        self.date_due.setDate(QDate.currentDate())
        self.date_due.setStyleSheet(f"""
            QDateEdit {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 12px; font-size: 13px; min-height: 36px;
            }}
            QDateEdit:focus {{ border-color: {RED}; }}
        """)
        root.addWidget(QLabel(tr("finances.income.dialog.participant_due")))
        root.addWidget(self.date_due)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton(tr("cancel"))
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUT};
                border: 1px solid {BORDER}; border-radius: 9px; font-size: 13px;
            }}
            QPushButton:hover {{ color: {TEXT_PRI}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_add = QPushButton(tr("save"))
        btn_add.setFixedHeight(36)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background: {RED}; color: white;
                border: none; border-radius: 9px; font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        btn_add.clicked.connect(self.accept)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_add)
        root.addLayout(btn_row)

    def get_data(self):
        expected = self.spin_expected.value()
        paid = self.spin_paid.value()
        return {
            "display_name": self.input_name.text().strip(),
            "expected_amount": expected,
            "paid_amount": paid,
            "pending_amount": expected - paid,
            "due_date": self.date_due.date().toPyDate(),
        }

    def _input_style(self):
        return f"""
            QLineEdit {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 12px; font-size: 13px; min-height: 36px;
            }}
            QLineEdit:focus {{ border-color: {RED}; }}
        """

    def _spin_style(self):
        return f"""
            QDoubleSpinBox {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 12px; font-size: 13px; min-height: 36px;
            }}
            QDoubleSpinBox:focus {{ border-color: {RED}; }}
        """


class ReceiptGeneratedDialog(QDialog):
    def __init__(self, receipt_number, receipt_path, payer_name="", payer_phone="", payer_email="", parent=None):
        debug_log(f"ReceiptGeneratedDialog.__init__ starting id={id(self)}")
        super().__init__(parent)
        self.receipt_number = receipt_number
        self.receipt_path = receipt_path
        self.payer_name = payer_name or ""
        self.payer_phone = payer_phone or ""
        self.payer_email = payer_email or ""

        self.setWindowTitle(trf("finances.income.receipt.success_title", "Recibo generado"))
        self.setMinimumWidth(460)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")

        # Conectar señal de destrucción para tracking
        self.destroyed.connect(lambda: debug_log(f"[FORENSIC] ReceiptGeneratedDialog.destroyed id={id(self)}"))
        
        self._build_ui()
        debug_log(f"[FORENSIC] ReceiptGeneratedDialog.__init__ complete id={id(self)}")

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 22)
        root.setSpacing(16)

        icon = QLabel("\u2705")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 42px; background: transparent; border: none;")
        root.addWidget(icon)

        title = QLabel(trf("finances.income.receipt.success_title", "Recibo generado correctamente"))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 20px;
            font-weight: 900;
            background: transparent;
            border: none;
        """)
        root.addWidget(title)

        subtitle = QLabel(f"Recibo: {self.receipt_number}")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"""
            color: {GREEN};
            font-size: 14px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)
        root.addWidget(subtitle)

        path_label = QLabel(self.receipt_path or trf("finances.income.receipt.generated_file", "Archivo generado"))
        path_label.setWordWrap(True)
        path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        path_label.setStyleSheet(f"""
            color: {TEXT_SEC};
            background: {BG_INPUT};
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 10px 12px;
            font-size: 11px;
        """)
        root.addWidget(path_label)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_close = QPushButton(trf("common.close", "Cerrar"))
        self.btn_whatsapp = QPushButton(trf("finances.income.receipt.send_whatsapp", "Enviar por WhatsApp"))
        self.btn_email = QPushButton(trf("finances.income.receipt.send_email", "Enviar por Email"))

        for btn in (self.btn_close, self.btn_whatsapp, self.btn_email):
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_close.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 10px;
                font-size: 12px;
                font-weight: 700;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                border-color: {TEXT_SEC};
            }}
        """)

        self.btn_whatsapp.setStyleSheet(f"""
            QPushButton {{
                background: #22C55E;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 800;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                background: #16A34A;
            }}
        """)

        self.btn_email.setStyleSheet(f"""
            QPushButton {{
                background: #2563EB;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 800;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                background: #1D4ED8;
            }}
        """)

        self.btn_close.clicked.connect(self.accept)
        self.btn_whatsapp.clicked.connect(self._send_whatsapp)
        self.btn_email.clicked.connect(self._send_email)

        btn_row.addWidget(self.btn_close)
        btn_row.addWidget(self.btn_whatsapp)
        btn_row.addWidget(self.btn_email)

        root.addLayout(btn_row)

    def _send_whatsapp(self):
        # WhatsApp Web y mailto no adjuntan archivos automáticamente de forma universal.
        # Por ahora se abre el mensaje con la ruta del recibo.
        # Para adjuntar realmente el PDF se necesita integración con SMTP, Outlook COM o API oficial.
        message = (
            f"Hola {self.payer_name}, te compartimos tu recibo {self.receipt_number} "
            f"de Senshi Fight Academy. Archivo: {self.receipt_path}"
        )

        phone = "".join(ch for ch in str(self.payer_phone or "") if ch.isdigit())

        if phone and not phone.startswith("57") and len(phone) == 10:
            phone = "57" + phone

        if phone:
            url = f"https://wa.me/{phone}?text={quote(message)}"
        else:
            url = f"https://wa.me/?text={quote(message)}"

        webbrowser.open(url)

    def _send_email(self):
        subject = f"Recibo {self.receipt_number} - Senshi Fight Academy"
        body = (
            f"Hola {self.payer_name},\n\n"
            f"Te compartimos tu recibo {self.receipt_number} de Senshi Fight Academy.\n\n"
            f"Archivo generado:\n{self.receipt_path}\n\n"
            f"Osu."
        )

        mailto = (
            f"mailto:{self.payer_email or ''}"
            f"?subject={quote(subject)}"
            f"&body={quote(body)}"
        )

        webbrowser.open(mailto)

    def closeEvent(self, event):
        debug_log(f"[FORENSIC] ReceiptGeneratedDialog.closeEvent id={id(self)}")
        event.accept()

    def reject(self):
        debug_log(f"[FORENSIC] ReceiptGeneratedDialog.reject id={id(self)}")
        super().reject()

    def __del__(self):
        debug_log(f"[FORENSIC] ReceiptGeneratedDialog.__del__ id={id(self)}")


class IncomeDialog(QDialog):
    def __init__(self, repo, income=None, parent=None):
        debug_log(f"IncomeDialog.__init__ starting id={id(self)}")
        super().__init__(parent)
        self.repo = repo
        self.income = income
        self._items = []
        self._participants = []
        self._students = []
        self._cartera_items = []
        self._clients = []
        self._student_db = []
        self._people_cache = []
        self._membership_plans = []
        self._inventory_products = []
        self._services = []
        self._receivables = []
        self._payment_methods = []
        self._accounts = []
        self._max_students = 0
        self._has_membership = False
        self._has_enrollment = False
        self._selected_person_id = None
        self._selected_payer_type = "third_party"
        self._selected_student_id = None
        self._selected_student_person_id = None
        self._selected_student_name = ""
        self._is_populating = False
        self._enrollment_students = []
        self._generating_receipt = False
        self._pending_close_after_receipt = False
        self._pdf_print_view = None
        self._pdf_print_page = None
        self._receipt_result_pending = None
        self._closing_dialog = False
        self._receipt_success_dialog = None
        self.receipt_preview_area = None

        # Guardar referencias de callbacks para desconexión segura
        self._pdf_on_load_finished = None
        self._pdf_on_pdf_finished = None

        # ── Wallet / Cartera state ─────────────────────────────
        self._refreshing_wallet = False
        self._editing_wallet_values = False
        self._wallet_distribution = []
        self._wallet_paid_spins = []


        self.setWindowTitle(tr("finances.income.dialog.title"))
        screen = self.screen() or QApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else None
        if avail:
            resp_w = min(1400, max(1100, int(avail.width() * 0.78)))
            resp_h = min(900, max(680, int(avail.height() * 0.82)))
        else:
            resp_w, resp_h = 1200, 760
        self.setMinimumSize(1100, 680)
        self.resize(resp_w, resp_h)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")

        self._load_lookups()
        self._build_ui()

        self._receipt_preview_timer = QTimer(self)
        self._receipt_preview_timer.setSingleShot(True)
        self._receipt_preview_timer.setInterval(180)
        self._receipt_preview_timer.timeout.connect(self._render_receipt_preview)

        self._soft_closed = False

        self._on_client_selected(0)

        if income is not None:
            self._populate(income)

        # Conectar señal de destrucción para tracking
        self.destroyed.connect(lambda: debug_log(f"[FORENSIC] IncomeDialog.destroyed id={id(self)}"))
        debug_log(f"[FORENSIC] IncomeDialog.__init__ complete id={id(self)}")

    def __del__(self):
        """Destructor para tracking."""
        debug_log(f"[FORENSIC] IncomeDialog.__del__ id={id(self)}")

    def _reset_for_new(self):
        self._soft_closed = False
        self._closing_dialog = False
        self._generating_receipt = False
        self._pending_close_after_receipt = False
        self._receipt_result_pending = None
        self._receipt_success_dialog = None
        self.income = None
        self._selected_person_id = None
        self._selected_payer_type = "third_party"
        self._selected_student_id = None
        self._selected_student_person_id = None
        self._selected_student_name = ""
        self._items = []
        self._participants = []
        self._students = []
        self._enrollment_students = []
        self._is_populating = True
        try:
            self.client_combo.setCurrentIndex(0)
            self.input_client_name.clear()
            self.input_client_doc.clear()
            self.input_client_email.clear()
            self.input_client_phone.clear()
            self.date_income.setDate(QDate.currentDate())
            self.spin_paid.setValue(0)
            self.spin_discount.setValue(0)
            self.combo_payment_method.setCurrentIndex(0)
            self.combo_account.setCurrentIndex(0)
            self.input_note.clear()
            self.input_agreement_note.clear()
            self._clear_items_table()
            self.lbl_error.hide()
            self.btn_save.setEnabled(True)
            if hasattr(self, "btn_receipt"):
                self.btn_receipt.setEnabled(True)
        finally:
            self._is_populating = False
        self._on_client_selected(0)
        self._schedule_receipt_preview_update()
        # Refresco diferido: repaint completo 150ms después para evitar pantalla negra
        if WEB_ENGINE_AVAILABLE:
            QTimer.singleShot(150, self._delayed_preview_repaint)

    def _reset_for_edit(self, income: dict):
        self._reset_for_new()
        self.income = income
        self._is_populating = True
        try:
            self._populate(income)
        finally:
            self._is_populating = False
        self._schedule_receipt_preview_update()
        if WEB_ENGINE_AVAILABLE:
            QTimer.singleShot(150, self._delayed_preview_repaint)

    def _delayed_preview_repaint(self):
        """Repaint forzado del preview tras reabrir diálogo."""
        try:
            if not getattr(self, "_closing_dialog", False):
                self._render_receipt_preview()
        except Exception:
            pass

    def _clear_items_table(self):
        self._items = []
        if hasattr(self, "items_table"):
            self.items_table.setRowCount(0)
        self._recalc()

    # ── Lookups ────────────────────────────────────────────────────

    def _load_lookups(self):
        try:
            self._membership_plans = self.repo.get_membership_plans()
        except Exception:
            self._membership_plans = []
        try:
            self._inventory_products = self.repo.get_inventory_products()
        except Exception:
            self._inventory_products = []
        try:
            self._services = self.repo.get_services()
        except Exception:
            self._services = []
        try:
            self._receivables = self.repo.get_open_receivables()
        except Exception:
            self._receivables = []
        try:
            self._payment_methods = self.repo.get_payment_methods()
        except Exception:
            self._payment_methods = []
        try:
            self._accounts = self.repo.get_destination_accounts()
        except Exception:
            self._accounts = []
        try:
            self._clients = self.repo.get_people_for_income()
        except Exception as e:
            print(f"Error loading clients: {e}")
            self._clients = []
        try:
            self._student_db = self.repo.get_students_for_income()
        except Exception as e:
            print(f"Error loading students: {e}")
            self._student_db = []

    # ── Enrollment helpers ─────────────────────────────────────────

    @staticmethod
    def _is_enrollment_item(item):
        name = str(item.get("base_name") or item.get("name") or "").lower()
        item_type = str(item.get("item_type") or "").lower()
        return (
            item_type == "service"
            and (
                "matricula" in name
                or "matrícula" in name
                or "enrollment" in name
            )
        )

    def _get_enrollment_items_count(self):
        count = 0
        for item in self._items:
            if self._is_enrollment_item(item):
                qty = int(item.get("quantity", 1) or 1)
                count += max(1, qty)
        return count

    # ── Lookups ────────────────────────────────────────────────────

    def _ensure_item_membership_discount(self, item):
        if item.get("item_type") != "membership":
            return item
        plan = self._find_membership_plan_for_item(item)
        if plan:
            item["membership_discount"] = float(plan.get("discount", 0) or 0)
            item["membership_discount_type"] = str(plan.get("discount_type", "amount") or "amount")
        else:
            item["membership_discount"] = 0
            item["membership_discount_type"] = "amount"
        return item

    def _get_membership_target_year_month(self):
        month = int(self.membership_month_combo.currentData() or QDate.currentDate().month())
        income_qdate = self.date_income.date()
        year = int(income_qdate.year())
        return year, month

    def _is_membership_discount_date_valid(self):
        income_date = self.date_income.date().toPyDate()
        target_year, target_month = self._get_membership_target_year_month()
        deadline = date(target_year, target_month, 10)
        return income_date <= deadline

    def _calculate_membership_item_discount(self, item):
        if item.get("item_type") != "membership":
            return 0
        if not self._is_membership_discount_date_valid():
            return 0
        plan = self._find_membership_plan_for_item(item)
        if not plan:
            return 0
        discount = float(plan.get("discount", item.get("membership_discount", 0)) or 0)
        discount_type = str(
            plan.get("discount_type", item.get("membership_discount_type", "amount"))
            or "amount"
        ).lower()
        unit_price = float(item.get("unit_price", 0) or 0)
        qty = int(item.get("quantity", 1) or 1)
        if discount <= 0:
            return 0
        if discount_type == "percent":
            discount_per_unit = round(unit_price * (discount / 100), 0)
        else:
            discount_per_unit = discount
        return min(discount_per_unit * qty, unit_price * qty)

    def _apply_membership_discounts_to_items(self):
        changed = False
        for item in self._items:
            if item.get("item_type") != "membership":
                continue
            discount = self._calculate_membership_item_discount(item)
            old_discount = float(item.get("discount", 0) or 0)
            line_total = float(item.get("unit_price", 0) or 0) * int(item.get("quantity", 1) or 1)
            new_subtotal = max(0, line_total - discount)
            if old_discount != discount or float(item.get("subtotal", 0) or 0) != new_subtotal:
                item["discount"] = discount
                item["subtotal"] = new_subtotal
                changed = True
        return changed

    # ── Build UI ───────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        body.addLayout(self._build_left_panel(), 1)
        body.addWidget(self._build_preview_panel(), 0)

        root.addLayout(body, 1)

    def _build_left_panel(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 16, 20)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(380)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background: transparent;")
        scroll_content = QWidget()
        scroll_content.setMinimumWidth(380)
        scroll_content.setStyleSheet("background: transparent;")
        form = QVBoxLayout(scroll_content)
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(16)

        form.addLayout(self._build_client_section())
        form.addLayout(self._build_category_add_section())
        form.addWidget(self._build_items_section())
        self._students_frame = self._build_students_section()
        form.addWidget(self._students_frame)

        self._enrollment_details_frame = self._build_enrollment_details_section()
        self._enrollment_details_frame.hide()
        form.addWidget(self._enrollment_details_frame)

        form.addWidget(self._build_payment_section())
        self._wallet_frame = self._build_wallet_section()
        form.addWidget(self._wallet_frame)
        form.addWidget(self._build_notes_section())

        form.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #FF4444; font-size: 11px; padding: 4px 0;")
        self.lbl_error.hide()
        layout.addWidget(self.lbl_error)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 8, 0, 0)
        btn_row.setSpacing(10)

        btn_cancel = QPushButton(tr("finances.income.dialog.cancel"))
        btn_cancel.setFixedHeight(40)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUT};
                border: 1px solid {BORDER}; border-radius: 10px; font-size: 13px;
                padding: 0 20px;
            }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: {TEXT_SEC}; }}
        """)
        btn_cancel.clicked.connect(self._soft_reject)

        self.btn_save = QPushButton(tr("finances.income.dialog.save"))
        self.btn_save.setFixedHeight(40)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background: {RED}; color: white;
                border: none; border-radius: 10px; font-size: 13px; font-weight: 700;
                padding: 0 24px;
            }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        self.btn_save.clicked.connect(self._save)

        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_save)
        layout.addLayout(btn_row)

        return layout

    # ── Client Section ─────────────────────────────────────────────

    def _build_client_section(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        frame = QFrame()
        frame.setObjectName("clientFrame")
        frame.setStyleSheet(f"""
            QFrame#clientFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        inner = QVBoxLayout(frame)
        inner.setContentsMargins(20, 16, 20, 16)
        inner.setSpacing(10)

        header = QLabel(tr("finances.income.dialog.client_section"))
        header.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; border: none; background: transparent;")
        inner.addWidget(header)

        self.client_combo = QComboBox()
        self.client_combo.setEditable(True)
        self.client_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.client_combo.setPlaceholderText(tr("finances.income.dialog.client_search"))
        self.client_combo.setStyleSheet(self._combo_style())
        self.client_combo.addItem(tr("finances.income.select_client"), None)
        self.client_combo.addItem(tr("finances.income.external_client"), {"external": True})
        for person in self._clients:
            if person.get("payer_type") == "guardian" and person.get("student_name"):
                person["display_name"] = f"{person['name']} · {tr('finances.income.guardian_of')} {person['student_name']}"
            else:
                person["display_name"] = person["name"]
            self.client_combo.addItem(person["display_name"], person)

        completer = QCompleter([p.get("display_name", p["name"]) for p in self._clients], self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.client_combo.setCompleter(completer)
        self.client_combo.currentIndexChanged.connect(self._on_client_selected)
        inner.addWidget(self.client_combo)

        self.input_client_name = QLineEdit()
        self.input_client_name.setPlaceholderText(tr("finances.income.dialog.client_name_placeholder"))
        self.input_client_name.setStyleSheet(self._input_style())
        self.input_client_name.textChanged.connect(self._update_preview)
        inner.addWidget(QLabel(tr("finances.income.dialog.client_name")))
        inner.addWidget(self.input_client_name)

        self.input_client_doc = QLineEdit()
        self.input_client_doc.setPlaceholderText(tr("finances.income.dialog.document_placeholder"))
        self.input_client_doc.setStyleSheet(self._input_style())
        self.input_client_doc.textChanged.connect(self._update_preview)
        inner.addWidget(QLabel(tr("finances.income.dialog.client_document")))
        inner.addWidget(self.input_client_doc)

        self.input_client_email = QLineEdit()
        self.input_client_email.setPlaceholderText(tr("finances.income.dialog.email_placeholder"))
        self.input_client_email.setStyleSheet(self._input_style())
        self.input_client_email.textChanged.connect(self._update_preview)
        inner.addWidget(QLabel(tr("finances.income.dialog.client_email")))
        inner.addWidget(self.input_client_email)

        self.input_client_phone = QLineEdit()
        self.input_client_phone.setPlaceholderText(tr("finances.income.dialog.phone_placeholder"))
        self.input_client_phone.setStyleSheet(self._input_style())
        self.input_client_phone.textChanged.connect(self._update_preview)
        inner.addWidget(QLabel(tr("finances.income.dialog.client_phone")))
        inner.addWidget(self.input_client_phone)

        self._kid_warning_label = QLabel("")
        self._kid_warning_label.setStyleSheet("color: #E67E22; font-size: 11px; padding: 2px 0;")
        self._kid_warning_label.setWordWrap(True)
        self._kid_warning_label.hide()
        inner.addWidget(self._kid_warning_label)

        layout.addWidget(frame)
        return layout

    def _on_client_selected(self, index):
        data = self.client_combo.itemData(index)
        if not data:
            self._selected_person_id = None
            self._selected_payer_type = "third_party"
            self._selected_student_id = None
            self._selected_student_person_id = None
            self._selected_student_name = ""
            self.input_client_name.clear()
            self.input_client_name.setReadOnly(False)
            self.input_client_doc.clear()
            self.input_client_email.clear()
            self.input_client_phone.clear()
            self.input_client_doc.setReadOnly(False)
            self.input_client_email.setReadOnly(False)
            self.input_client_phone.setReadOnly(False)
            self._clear_kid_warning()
            self._update_preview()
            return
        if isinstance(data, dict) and data.get("external"):
            self._selected_person_id = None
            self._selected_payer_type = "third_party"
            self._selected_student_id = None
            self._selected_student_person_id = None
            self._selected_student_name = ""
            self.input_client_name.clear()
            self.input_client_name.setReadOnly(False)
            self.input_client_doc.clear()
            self.input_client_email.clear()
            self.input_client_phone.clear()
            self.input_client_doc.setReadOnly(False)
            self.input_client_email.setReadOnly(False)
            self.input_client_phone.setReadOnly(False)
            self._clear_kid_warning()
            self._update_preview()
            return
        self._selected_person_id = data.get("person_id") or data["id"]
        self._selected_payer_type = data.get("payer_type", "third_party")
        self._selected_student_id = data.get("student_id")
        self._selected_student_person_id = (
            data.get("student_person_id")
            or data.get("person_id")
            or data.get("id")
        )

        # Nombre real del estudiante asociado.
        # Para KID con acudiente, el estudiante debe ser data["name"] o data["student_name"].
        self._selected_student_name = (
            data.get("student_name")
            or data.get("name")
            or ""
        )

        if data.get("is_kid") and data.get("guardian_name"):
            guardian_name = data.get("guardian_name", "")

            # El cliente/pagador real es el acudiente.
            self._selected_payer_type = "guardian"

            # Guardar claramente quién es el estudiante KID asociado.
            self._selected_student_id = data.get("student_id")
            self._selected_student_person_id = (
                data.get("student_person_id")
                or data.get("person_id")
                or data.get("id")
            )
            self._selected_student_name = (
                data.get("student_name")
                or data.get("name", "")
            )

            self.input_client_name.setText(guardian_name)
            self.input_client_doc.setText(data.get("guardian_document", "") or "")
            self.input_client_email.setText(data.get("guardian_email", ""))
            self.input_client_phone.setText(data.get("guardian_phone", ""))
            self._clear_kid_warning()
            self._show_kid_info(guardian_name)
        elif data.get("is_kid") and not data.get("guardian_name"):
            self.input_client_name.setText(data.get("name", ""))
            self.input_client_doc.setText(data.get("document", ""))
            self.input_client_email.setText(data.get("email", ""))
            self.input_client_phone.setText(data.get("phone", ""))
            self._show_kid_guardian_missing()
        else:
            self.input_client_name.setText(data.get("name", ""))
            self.input_client_doc.setText(data.get("document", ""))
            self.input_client_email.setText(data.get("email", ""))
            self.input_client_phone.setText(data.get("phone", ""))
            self._clear_kid_warning()

        self.input_client_name.setReadOnly(True)
        self.input_client_doc.setReadOnly(True)
        self.input_client_email.setReadOnly(True)
        self.input_client_phone.setReadOnly(True)
        self._update_preview()

    # ── Category + Quick Add ───────────────────────────────────────

    def _build_category_add_section(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        frame = QFrame()
        frame.setObjectName("catFrame")
        frame.setStyleSheet(f"""
            QFrame#catFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        inner = QVBoxLayout(frame)
        inner.setContentsMargins(20, 16, 20, 16)
        inner.setSpacing(10)

        header_row = QHBoxLayout()
        cat_header = QLabel(tr("finances.income.dialog.items_section"))
        cat_header.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; border: none; background: transparent;")
        header_row.addWidget(cat_header)
        header_row.addStretch()

        self.btn_open_item_dialog = QPushButton("＋ " + trf("finances.income.dialog.create_agreement", "Crear acuerdo"))
        self.btn_open_item_dialog.setFixedHeight(32)
        self.btn_open_item_dialog.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_item_dialog.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 8px;
                font-size: 11px; font-weight: 700; padding: 0 12px;
            }}
            QPushButton:hover {{ border-color: {RED}; }}
        """)
        self.btn_open_item_dialog.clicked.connect(self._add_item)
        header_row.addWidget(self.btn_open_item_dialog)
        inner.addLayout(header_row)

        cat_inner = QHBoxLayout()
        cat_inner.setSpacing(10)

        cat_col = QVBoxLayout()
        cat_col.setSpacing(4)
        cat_col.addWidget(QLabel(tr("finances.income.dialog.item_category")))
        self.combo_category = QComboBox()
        self.combo_category.setStyleSheet(self._combo_style())
        self._cats = [
            ("membership", tr("finances.income.dialog.category_membership")),
            ("service", tr("finances.income.dialog.category_service")),
            ("inventory", tr("finances.income.dialog.category_inventory")),
            ("receivable", tr("finances.income.dialog.category_receivable")),
            ("collection_account", tr("finances.income.dialog.category_collection_account")),
            ("agreement", tr("finances.income.dialog.category_agreement")),
        ]
        for val, label in self._cats:
            self.combo_category.addItem(label, val)
        self.combo_category.currentIndexChanged.connect(self._on_category_changed)
        cat_col.addWidget(self.combo_category)
        cat_inner.addLayout(cat_col, 1)

        product_col = QVBoxLayout()
        product_col.setSpacing(4)
        product_col.addWidget(QLabel(tr("finances.income.dialog.item_name")))
        self.combo_product = QComboBox()
        self.combo_product.setStyleSheet(self._combo_style())
        product_col.addWidget(self.combo_product)
        cat_inner.addLayout(product_col, 1)

        inner.addLayout(cat_inner)

        self._on_category_changed()

        layout.addWidget(frame)
        return layout

    def _on_category_changed(self):
        cat = self.combo_category.currentData()
        self.combo_product.clear()
        self.combo_product.addItem("—", None)
        if cat == "membership":
            for p in self._membership_plans:
                self.combo_product.addItem(f"{p['name']}  ({format_money(p['price'])})", ("membership", p["id"], p["name"], p["price"], p.get("is_prepaid_months", False), p.get("prepaid_months_count", 1), p.get("plan_type", "individual")))
        elif cat == "service":
            for s in self._services:
                self.combo_product.addItem(f"{s['name']}  ({format_money(s['price'])})", ("service", s["id"], s["name"], s["price"]))
        elif cat == "inventory":
            for p in self._inventory_products:
                self.combo_product.addItem(f"{p['name']}  (stock: {p['stock']})  {format_money(p['price'])}", ("inventory", p["id"], p["name"], p["price"]))
        elif cat == "receivable":
            for r in self._receivables:
                self.combo_product.addItem(f"{r['debtor_name']}  ({format_money(r['pending_amount'])})", ("receivable", r["id"], r["debtor_name"], r["pending_amount"]))
        elif cat == "collection_account":
            pass
        elif cat == "agreement":
            pass

    # ── Items Section ──────────────────────────────────────────────

    def _build_items_section(self):
        frame = QFrame()
        frame.setObjectName("itemsFrame")
        frame.setStyleSheet(f"""
            QFrame#itemsFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        header_row = QHBoxLayout()
        items_header = QLabel(trf("finances.income.dialog.concept_details", "Detalles del concepto"))
        items_header.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; border: none; background: transparent;")
        header_row.addWidget(items_header)
        header_row.addStretch()
        layout.addLayout(header_row)

        self.items_table = QTableWidget(0, 6)
        self.items_table.setHorizontalHeaderLabels([
            tr("finances.income.dialog.product_name"),
            tr("finances.income.dialog.quantity"),
            tr("finances.income.dialog.unit_price"),
            tr("finances.income.dialog.line_total"),
            tr("finances.income.dialog.item_discount"),
            tr("finances.income.dialog.item_category"),
        ])
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setShowGrid(False)
        self.items_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.items_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.items_table.setMinimumHeight(120)
        self.items_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_INPUT};
                border: 1px solid {BORDER};
                border-radius: 10px;
                outline: none;
                color: {TEXT_PRI};
                gridline-color: transparent;
                selection-background-color: {BG_HOVER};
                font-size: 12px;
            }}
            QHeaderView::section {{
                background-color: #1A1A1A;
                color: {TEXT_SEC};
                border: none;
                border-bottom: 1px solid {BORDER};
                padding: 10px;
                font-size: 9px;
                font-weight: 900;
            }}
            QTableWidget::item {{
                border: none;
                border-bottom: 1px solid #252525;
                padding: 6px;
            }}
        """)
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.items_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.items_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.items_table.setColumnWidth(1, 60)
        self.items_table.setColumnWidth(2, 110)
        self.items_table.setColumnWidth(3, 110)
        self.items_table.setColumnWidth(4, 100)

        layout.addWidget(self.items_table)

        item_btn_row = QHBoxLayout()
        item_btn_row.setSpacing(8)

        self.btn_quick_add = QPushButton(tr("finances.income.dialog.item_add"))
        self.btn_quick_add.setFixedHeight(32)
        self.btn_quick_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_quick_add.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 8px;
                font-size: 11px; font-weight: 700; padding: 0 12px;
            }}
            QPushButton:hover {{ border-color: {RED}; }}
        """)
        self.btn_quick_add.clicked.connect(self._quick_add_item)
        item_btn_row.addWidget(self.btn_quick_add)

        btn_edit_item = QPushButton(trf("finances.income.dialog.item_edit", "Editar artículo"))
        btn_edit_item.setFixedHeight(32)
        btn_edit_item.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit_item.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 8px;
                font-size: 11px; font-weight: 700; padding: 0 12px;
            }}
            QPushButton:hover {{ border-color: {RED}; }}
        """)
        btn_edit_item.clicked.connect(self._edit_item)
        item_btn_row.addWidget(btn_edit_item)

        btn_remove_item = QPushButton(tr("finances.income.dialog.item_remove"))
        btn_remove_item.setFixedHeight(32)
        btn_remove_item.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_remove_item.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {RED};
                border: 1px solid rgba(200,16,46,0.3); border-radius: 8px;
                font-size: 11px; font-weight: 700; padding: 0 12px;
            }}
            QPushButton:hover {{ background: rgba(200,16,46,0.12); }}
        """)
        btn_remove_item.clicked.connect(self._remove_item)
        item_btn_row.addWidget(btn_remove_item)

        item_btn_row.addStretch()
        layout.addLayout(item_btn_row)

        return frame

    def _quick_add_item(self):
        cat = self.combo_category.currentData()
        data = self.combo_product.currentData()
        if not data:
            self._add_item()
            return
        cat_key, ref_id, name, price = data[0], data[1], data[2], data[3]
        qty = 1
        line_subtotal = qty * price
        item = {
            "item_type": cat_key,
            "name": name,
            "base_name": name,
            "quantity": qty,
            "unit_price": price,
            "discount": 0,
            "subtotal": line_subtotal,
            "reference_id": ref_id,
        }
        if cat_key == "membership" and len(data) >= 7:
            is_prepaid = bool(data[4])
            prepaid_count = int(data[5] or 1)
            plan_type = str(data[6] or "individual")
            is_prepaid_active = plan_type == "individual" and is_prepaid and prepaid_count > 1
            item["is_prepaid_months"] = is_prepaid_active
            item["prepaid_months_count"] = min(max(prepaid_count, 1), 12) if is_prepaid_active else 1
        if cat_key == "membership":
            self._hydrate_membership_prepaid_flags(item)
            self._ensure_item_membership_discount(item)
        if cat_key == "receivable":
            item["name"] = f"Abono: {name}"
        self._items.append(item)
        self._apply_membership_discounts_to_items()
        self._on_items_changed()
        self._refresh_items_table()
        self._update_preview()
        self._refresh_prepaid_months_flow()

    def _add_item(self):
        dlg = ItemDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            self._hydrate_membership_prepaid_flags(data)
            self._ensure_item_membership_discount(data)
            self._items.append(data)
            self._apply_membership_discounts_to_items()
            self._refresh_items_table()
            self._on_items_changed()
            self._update_preview()
            self._refresh_prepaid_months_flow()

    def _edit_item(self):
        row = self.items_table.currentRow()
        if row < 0 or row >= len(self._items):
            QMessageBox.information(self,
                trf("finances.income.dialog.select_item_first", "Select an item first."),
                trf("finances.income.dialog.select_item_first", "Select an item first."))
            return
        dlg = ItemDialog(self, item_data=self._items[row])
        if dlg.exec():
            old_item = self._items[row]
            old_wallet_paid = float(old_item.get("wallet_paid", 0) or 0)
            old_details = old_item.get("details", "")

            data = dlg.get_data()

            # Mantener campos importantes del item original.
            data["reference_id"] = old_item.get("reference_id")
            data["details"] = old_details

            self._hydrate_membership_prepaid_flags(data)
            self._ensure_item_membership_discount(data)

            item_total = self._item_total_for_wallet(data)
            data["wallet_paid"] = min(max(0, old_wallet_paid), item_total)
            data["wallet_pending"] = max(0, item_total - data["wallet_paid"])

            self._items[row] = data
            self._apply_membership_discounts_to_items()
            self._refresh_items_table()
            self._on_items_changed()
            self._update_preview()
            self._refresh_prepaid_months_flow()

    def _remove_item(self):
        row = self.items_table.currentRow()
        if 0 <= row < len(self._items):
            del self._items[row]
            self._apply_membership_discounts_to_items()
            self._refresh_items_table()
            self._on_items_changed()
            self._update_preview()
            self._refresh_prepaid_months_flow()

    def _refresh_items_table(self):
        self.items_table.setRowCount(0)
        self.items_table.setRowCount(len(self._items))
        type_map = {
            "membership": tr("finances.income.dialog.category_membership"),
            "service": tr("finances.income.dialog.category_service"),
            "inventory": tr("finances.income.dialog.category_inventory"),
            "receivable": tr("finances.income.dialog.category_receivable"),
            "collection_account": tr("finances.income.dialog.category_collection_account"),
            "agreement": tr("finances.income.dialog.category_agreement"),
        }
        for i, item in enumerate(self._items):
            self.items_table.setItem(i, 0, QTableWidgetItem(item.get("name", "")))
            self.items_table.setItem(i, 1, QTableWidgetItem(str(item.get("quantity", 1))))
            self.items_table.setItem(i, 2, QTableWidgetItem(format_money(item.get("unit_price", 0))))
            disc = float(item.get("discount", 0) or 0)
            subtotal_val = float(item.get("subtotal", 0) or 0)
            if subtotal_val == 0 and disc == 0:
                subtotal_val = float(item.get("quantity", 1) or 1) * float(item.get("unit_price", 0) or 0)
            subtotal_item = QTableWidgetItem(format_money(max(0, subtotal_val)))
            if disc > 0:
                subtotal_item.setToolTip(
                    trf("finances.income.dialog.membership_discount_applied", "Descuento aplicado")
                    + ": "
                    + format_money(disc)
                )
            self.items_table.setItem(i, 3, subtotal_item)
            self.items_table.setItem(i, 4, QTableWidgetItem(format_money(disc) if disc > 0 else "—"))
            self.items_table.setItem(i, 5, QTableWidgetItem(type_map.get(item.get("item_type", ""), item.get("item_type", ""))))
            self.items_table.setRowHeight(i, 36)

    # ── Students Section ──────────────────────────────────────────

    def _build_students_section(self):
        frame = QFrame()
        frame.setObjectName("studentsFrame")
        frame.setStyleSheet(f"""
            QFrame#studentsFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        header = QLabel(tr("finances.income.dialog.students"))
        header.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; border: none; background: transparent;")
        layout.addWidget(header)

        self.lbl_student_limit = QLabel("")
        self.lbl_student_limit.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; border: none; background: transparent;")
        layout.addWidget(self.lbl_student_limit)

        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        self.student_combo = QComboBox()
        self.student_combo.setEditable(True)
        self.student_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.student_combo.setPlaceholderText(tr("finances.income.dialog.search_student"))
        self.student_combo.setStyleSheet(self._combo_style())
        self._student_label_map = {}
        for s in self._student_db:
            label = f"{s['name']}  ({s['document']})  ·  {s['status']}"
            self._student_label_map[label] = s
            self.student_combo.addItem(label, s)

        completer = QCompleter(list(self._student_label_map.keys()), self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.activated.connect(self._on_student_completed)
        self.student_combo.setCompleter(completer)
        search_row.addWidget(self.student_combo, 1)

        self.btn_add_student = QPushButton("＋ " + tr("finances.income.dialog.add_student"))
        self.btn_add_student.setFixedHeight(32)
        self.btn_add_student.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_student.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 8px;
                font-size: 11px; font-weight: 700; padding: 0 12px;
            }}
            QPushButton:hover {{ border-color: {RED}; }}
        """)
        self.btn_add_student.clicked.connect(self._add_student)
        search_row.addWidget(self.btn_add_student)
        layout.addLayout(search_row)

        self.students_list = QVBoxLayout()
        self.students_list.setSpacing(4)
        layout.addLayout(self.students_list)

        self._period_sep = QFrame()
        self._period_sep.setFrameShape(QFrame.Shape.HLine)
        self._period_sep.setStyleSheet(f"border: none; border-top: 1px solid {BORDER}; background: transparent;")
        layout.addWidget(self._period_sep)

        self.lbl_period_header = QLabel(trf("finances.income.dialog.period", "Periodo del pago"))
        self.lbl_period_header.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; font-weight: 900; border: none; background: transparent;")
        layout.addWidget(self.lbl_period_header)

        period_row = QHBoxLayout()
        period_row.setSpacing(12)

        month_col = QVBoxLayout()
        month_col.setContentsMargins(0, 0, 0, 0)
        month_col.setSpacing(6)
        self.lbl_membership_month = QLabel(trf("finances.income.dialog.membership_month", "Mes de membresía"))
        self.lbl_membership_month.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; border: none; background: transparent;")
        month_col.addWidget(self.lbl_membership_month)

        self.prepaid_months_inline_row = QWidget()
        self.prepaid_months_inline_row.setStyleSheet("background: transparent;")
        self.prepaid_months_inline_row.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        self.prepaid_months_inline_layout = QHBoxLayout(self.prepaid_months_inline_row)
        self.prepaid_months_inline_layout.setContentsMargins(0, 0, 0, 0)
        self.prepaid_months_inline_layout.setSpacing(10)

        self.membership_month_combo = QComboBox()
        self.membership_month_combo.setStyleSheet(self._combo_style())
        months = [
            ("01", "Enero"), ("02", "Febrero"), ("03", "Marzo"),
            ("04", "Abril"), ("05", "Mayo"), ("06", "Junio"),
            ("07", "Julio"), ("08", "Agosto"), ("09", "Septiembre"),
            ("10", "Octubre"), ("11", "Noviembre"), ("12", "Diciembre"),
        ]
        for value, label in months:
            self.membership_month_combo.addItem(label, value)
        self.membership_month_combo.currentIndexChanged.connect(self._on_membership_month_changed)
        self.membership_month_combo.setFixedWidth(156)
        self.prepaid_months_inline_layout.addWidget(self.membership_month_combo, 0)

        self.prepaid_months_extra_layout = QHBoxLayout()
        self.prepaid_months_extra_layout.setContentsMargins(0, 0, 0, 0)
        self.prepaid_months_extra_layout.setSpacing(10)
        self.prepaid_months_inline_layout.addLayout(self.prepaid_months_extra_layout)
        self.prepaid_months_inline_layout.addStretch()

        month_col.addWidget(self.prepaid_months_inline_row)

        self.prepaid_months_summary = QFrame()
        self.prepaid_months_summary.setObjectName("prepaidMonthsSummary")
        self.prepaid_months_summary.setStyleSheet(f"""
            QFrame#prepaidMonthsSummary {{
                background: rgba(200, 16, 46, 0.08);
                border: 1px solid rgba(200, 16, 46, 0.28);
                border-radius: 12px;
            }}
            QFrame#prepaidMonthsSummary QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        summary_layout = QVBoxLayout(self.prepaid_months_summary)
        summary_layout.setContentsMargins(14, 10, 14, 10)
        summary_layout.setSpacing(8)
        self.prepaid_months_summary_title = QLabel(
            trf("finances.income.dialog.prepaid_months_flow", "Meses adelantados incluidos")
        )
        self.prepaid_months_summary_title.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 10px;
            font-weight: 900;
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: transparent;
            border: none;
        """)
        summary_layout.addWidget(self.prepaid_months_summary_title)
        self.prepaid_months_summary_text = QLabel("")
        self.prepaid_months_summary_text.setWordWrap(True)
        self.prepaid_months_summary_text.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 13px;
            font-weight: 800;
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: transparent;
            border: none;
        """)
        summary_layout.addWidget(self.prepaid_months_summary_text)
        self.prepaid_months_summary.hide()
        month_col.addWidget(self.prepaid_months_summary)

        period_row.addLayout(month_col, 1)

        period_row.addStretch()
        layout.addLayout(period_row)

        self.prepaid_months_inline_row.hide()
        self.lbl_membership_month.hide()
        self.membership_month_combo.hide()
        self.lbl_period_header.hide()
        self._period_sep.hide()

        frame.hide()
        return frame

    def _build_enrollment_details_section(self):
        frame = QFrame()
        frame.setObjectName("enrollmentDetailsFrame")
        frame.setStyleSheet(f"""
            QFrame#enrollmentDetailsFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        header = QLabel(trf("finances.income.dialog.enrollment_details", "Detalles matrícula"))
        header.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; border: none; background: transparent;")
        layout.addWidget(header)

        self.lbl_enrollment_limit = QLabel("")
        self.lbl_enrollment_limit.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; border: none; background: transparent;")
        layout.addWidget(self.lbl_enrollment_limit)

        self.lbl_enrollment_help = QLabel(trf(
            "finances.income.dialog.enrollment_details_help",
            "Agrega estudiantes que se matriculan o participan en este pago."
        ))
        self.lbl_enrollment_help.setWordWrap(True)
        self.lbl_enrollment_help.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; border: none; background: transparent;")
        layout.addWidget(self.lbl_enrollment_help)

        self.lbl_enrollment_year = QLabel(trf("finances.income.dialog.enrollment_year", "Año de matrícula"))
        self.lbl_enrollment_year.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; border: none; background: transparent;")
        layout.addWidget(self.lbl_enrollment_year)

        self.enrollment_year_spin = QDoubleSpinBox()
        self.enrollment_year_spin.setDecimals(0)
        self.enrollment_year_spin.setRange(2020, 2100)
        self.enrollment_year_spin.setValue(QDate.currentDate().year())
        self.enrollment_year_spin.setStyleSheet(self._spin_style())
        self.enrollment_year_spin.valueChanged.connect(self._on_enrollment_year_changed)
        layout.addWidget(self.enrollment_year_spin)

        self._enrollment_frame = QFrame()
        self._enrollment_frame.setStyleSheet("background: transparent;")
        enroll_layout = QVBoxLayout(self._enrollment_frame)
        enroll_layout.setContentsMargins(0, 4, 0, 4)
        enroll_layout.setSpacing(8)

        self.lbl_enrollment_header = QLabel(trf("finances.income.dialog.enrollment_student", "Estudiante (matrícula)"))
        self.lbl_enrollment_header.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; font-weight: 900; border: none; background: transparent;")
        enroll_layout.addWidget(self.lbl_enrollment_header)

        enroll_search = QHBoxLayout()
        enroll_search.setSpacing(8)

        self.enrollment_student_combo = QComboBox()
        self.enrollment_student_combo.setEditable(True)
        self.enrollment_student_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.enrollment_student_combo.setPlaceholderText(tr("finances.income.dialog.search_student"))
        self.enrollment_student_combo.setStyleSheet(self._combo_style())
        self._enrollment_student_label_map = {}
        for s in self._student_db:
            label = f"{s['name']}  ({s['document']})  ·  {s['status']}"
            self._enrollment_student_label_map[label] = s
            self.enrollment_student_combo.addItem(label, s)

        enroll_completer = QCompleter(list(self._enrollment_student_label_map.keys()), self)
        enroll_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        enroll_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        enroll_completer.activated.connect(self._on_enrollment_student_completed)
        self.enrollment_student_combo.setCompleter(enroll_completer)
        enroll_search.addWidget(self.enrollment_student_combo, 1)

        self.btn_add_enrollment_student = QPushButton("＋ " + tr("finances.income.dialog.add_student"))
        self.btn_add_enrollment_student.setFixedHeight(32)
        self.btn_add_enrollment_student.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_enrollment_student.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 8px;
                font-size: 11px; font-weight: 700; padding: 0 12px;
            }}
            QPushButton:hover {{ border-color: {RED}; }}
        """)
        self.btn_add_enrollment_student.clicked.connect(self._add_enrollment_student)
        enroll_search.addWidget(self.btn_add_enrollment_student)
        enroll_layout.addLayout(enroll_search)

        self.enrollment_students_list = QVBoxLayout()
        self.enrollment_students_list.setSpacing(4)
        enroll_layout.addLayout(self.enrollment_students_list)

        layout.addWidget(self._enrollment_frame)
        return frame

    def _on_enrollment_year_changed(self, value):
        self._update_payment_periods()
        self._update_preview()

    def _update_enrollment_limit_label(self):
        if self._max_students > 0:
            self.lbl_enrollment_limit.setText(
                f"{len(self._enrollment_students)} / {self._max_students} "
                + trf("finances.income.dialog.enrollment_students", "estudiantes de matrícula")
            )
        else:
            self.lbl_enrollment_limit.setText("")

    MONTHS_I18N = [
        ("01", "month.january", "Enero"),
        ("02", "month.february", "Febrero"),
        ("03", "month.march", "Marzo"),
        ("04", "month.april", "Abril"),
        ("05", "month.may", "Mayo"),
        ("06", "month.june", "Junio"),
        ("07", "month.july", "Julio"),
        ("08", "month.august", "Agosto"),
        ("09", "month.september", "Septiembre"),
        ("10", "month.october", "Octubre"),
        ("11", "month.november", "Noviembre"),
        ("12", "month.december", "Diciembre"),
    ]

    def _get_prepaid_month_labels(self, start_month_value, count):
        count = min(max(int(count or 1), 1), 12)
        start_index = 0
        for i, (value, key, _) in enumerate(self.MONTHS_I18N):
            if value == str(start_month_value).zfill(2):
                start_index = i
                break
        result = []
        for offset in range(count):
            idx = (start_index + offset) % 12
            _, key, fallback = self.MONTHS_I18N[idx]
            result.append(trf(key, fallback))
        return result

    def _get_active_membership_prepaid_count(self):
        counts = []
        for item in self._items:
            if item.get("item_type") != "membership":
                continue
            is_prepaid = bool(item.get("is_prepaid_months", False))
            prepaid_count = int(item.get("prepaid_months_count", 1) or 1)
            if is_prepaid and prepaid_count > 1:
                counts.append(prepaid_count)
        if not counts:
            return 1
        return min(max(max(counts), 1), 12)

    def _make_prepaid_month_box(self, text):
        lbl = QLabel(text)
        lbl.setFixedHeight(50)
        lbl.setMinimumWidth(140)
        lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        lbl.setStyleSheet(f"""
            QLabel {{
                background: {BG_INPUT};
                color: {TEXT_PRI};
                border: 1.5px solid {BORDER};
                border-radius: 10px;
                padding: 0 16px;
                font-size: 13px;
                font-weight: 600;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}
        """)
        return lbl

    def _make_prepaid_month_arrow(self):
        lbl = QLabel("→")
        lbl.setFixedWidth(28)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"""
            QLabel {{
                color: {BORDER};
                font-size: 26px;
                font-weight: 900;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: transparent;
                border: none;
            }}
        """)
        return lbl

    def _clear_prepaid_months_extra_layout(self):
        if not hasattr(self, "prepaid_months_extra_layout"):
            return
        while self.prepaid_months_extra_layout.count():
            item = self.prepaid_months_extra_layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget:
                widget.deleteLater()
            elif child_layout:
                self._clear_layout(child_layout)

    def _refresh_prepaid_months_flow(self):
        if not hasattr(self, "prepaid_months_extra_layout"):
            return
        self._clear_prepaid_months_extra_layout()
        prepaid_count = self._get_active_membership_prepaid_count()
        if prepaid_count <= 1:
            if hasattr(self, "prepaid_months_summary"):
                self.prepaid_months_summary.hide()
            if hasattr(self, "prepaid_months_inline_row"):
                self.prepaid_months_inline_row.setVisible(self._has_membership)
            return
        start_month = self.membership_month_combo.currentData()
        labels = self._get_prepaid_month_labels(start_month, prepaid_count)
        for month_label in labels[1:]:
            self.prepaid_months_extra_layout.addWidget(
                self._make_prepaid_month_arrow()
            )
            self.prepaid_months_extra_layout.addWidget(
                self._make_prepaid_month_box(month_label)
            )
        self.prepaid_months_inline_row.show()
        self.prepaid_months_inline_row.setVisible(True)
        if hasattr(self, "prepaid_months_summary"):
            self.prepaid_months_summary_text.setText(" → ".join(labels))
            self.prepaid_months_summary.show()
            self.prepaid_months_summary.setVisible(True)
        self.prepaid_months_inline_row.updateGeometry()
        if hasattr(self, "prepaid_months_summary"):
            self.prepaid_months_summary.updateGeometry()
        parent = self.prepaid_months_inline_row.parentWidget()
        if parent:
            parent.updateGeometry()
        self._students_frame.updateGeometry()

    @staticmethod
    def _infer_prepaid_months_count_from_name(name):
        text = str(name or "").strip().lower()
        if not text:
            return 1
        patterns = [
            r"\bx\s*(\d{1,2})\b",
            r"\b(\d{1,2})\s*mes(?:es)?\s*adelant",
            r"\b(\d{1,2})\s*mes(?:es)?\s*anticip",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                count = int(match.group(1))
                return max(1, min(count, 12))
        return 1

    def _find_membership_plan_for_item(self, item):
        ref_id = item.get("reference_id")
        if ref_id is not None:
            for plan in self._membership_plans:
                if plan.get("id") == ref_id:
                    return plan
        item_name = (item.get("base_name") or item.get("name") or "").strip().lower()
        if item_name:
            for plan in self._membership_plans:
                plan_name = str(plan.get("name", "")).strip().lower()
                if plan_name == item_name:
                    return plan
        return None

    def _hydrate_membership_prepaid_flags(self, item):
        if item.get("item_type") != "membership":
            item.pop("is_prepaid_months", None)
            item.pop("prepaid_months_count", None)
            return item

        plan = self._find_membership_plan_for_item(item)

        plan_type = "individual"
        plan_is_prepaid = False
        plan_prepaid_count = 1

        if plan:
            plan_type = str(
                plan.get("plan_type", "individual") or "individual"
            ).strip().lower()
            plan_is_prepaid = bool(plan.get("is_prepaid_months", False))
            plan_prepaid_count = int(plan.get("prepaid_months_count", 1) or 1)
            plan_prepaid_count = max(1, min(plan_prepaid_count, 12))

        name_count = self._infer_prepaid_months_count_from_name(
            item.get("base_name") or item.get("name", "")
        )

        prepaid_count = max(plan_prepaid_count, name_count)
        prepaid_count = max(1, min(prepaid_count, 12))

        is_prepaid = (
            plan_type == "individual"
            and prepaid_count > 1
            and (plan_is_prepaid or name_count > 1)
        )

        item["is_prepaid_months"] = is_prepaid
        item["prepaid_months_count"] = prepaid_count if is_prepaid else 1

        if plan and not item.get("reference_id"):
            item["reference_id"] = plan.get("id")

        return item

    def _on_student_completed(self, text):
        idx = self.student_combo.findText(text)
        if idx >= 0:
            self.student_combo.setCurrentIndex(idx)

    def _add_student(self):
        data = self.student_combo.currentData()
        if not data:
            text = self.student_combo.currentText().strip()
            if text in self._student_label_map:
                data = self._student_label_map[text]
        if not data:
            self.lbl_error.setText(tr("finances.income.dialog.select_student_first"))
            self.lbl_error.show()
            return
        sid = data["student_id"]
        if any(s["student_id"] == sid for s in self._students):
            self.lbl_error.setText(tr("finances.income.dialog.student_already_added"))
            self.lbl_error.show()
            return
        if self._max_students > 0 and len(self._students) >= self._max_students:
            self.lbl_error.setText(tr("finances.income.dialog.max_students_reached"))
            self.lbl_error.show()
            return
        self._students.append(data)
        self._refresh_students_list()
        self.lbl_error.hide()
        # Reset combo
        self.student_combo.setCurrentIndex(0)

    def _refresh_students_list(self):
        for i in reversed(range(self.students_list.count())):
            item = self.students_list.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        status_map = {"active": tr("finances.income.status.active"), "inactive": tr("finances.income.status.inactive"), "retired": tr("finances.income.status.retired")}

        for s in self._students:
            row = QHBoxLayout()
            row.setSpacing(8)
            name_label = QLabel(s.get("name", ""))
            name_label.setStyleSheet(f"color: {TEXT_PRI}; font-size: 11px; font-weight: 600; border: none; background: transparent;")
            row.addWidget(name_label)
            info_label = QLabel(f"{s.get('document', '')} · {status_map.get(s.get('status', ''), s.get('status', ''))}")
            info_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; border: none; background: transparent;")
            row.addWidget(info_label)
            row.addStretch()
            btn_del = QPushButton("✕")
            btn_del.setFixedSize(22, 22)
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {RED};
                    border: none; font-size: 12px; font-weight: 700;
                }}
                QPushButton:hover {{ color: #FF4444; }}
            """)
            sid = s["student_id"]
            btn_del.clicked.connect(lambda checked, id=sid: self._remove_student(id))
            row.addWidget(btn_del)
            self.students_list.addLayout(row)
        self._update_student_limit_label()
        self._update_preview()

    def _remove_student(self, student_id):
        self._students = [s for s in self._students if s["student_id"] != student_id]
        self._refresh_students_list()

    # ── Enrollment Student Management ──────────────────────────────

    def _on_enrollment_student_completed(self, text):
        idx = self.enrollment_student_combo.findText(text)
        if idx >= 0:
            self.enrollment_student_combo.setCurrentIndex(idx)

    def _add_enrollment_student(self):
        data = self.enrollment_student_combo.currentData()
        if not data:
            text = self.enrollment_student_combo.currentText().strip()
            if text in self._enrollment_student_label_map:
                data = self._enrollment_student_label_map[text]
        if not data:
            self.lbl_error.setText(tr("finances.income.dialog.select_student_first"))
            self.lbl_error.show()
            return
        sid = data["student_id"]
        if any(s["student_id"] == sid for s in self._enrollment_students):
            self.lbl_error.setText(tr("finances.income.dialog.student_already_added"))
            self.lbl_error.show()
            return
        self._enrollment_students.append(data)
        self._refresh_enrollment_students_list()
        self.lbl_error.hide()
        self.enrollment_student_combo.setCurrentIndex(0)

    def _refresh_enrollment_students_list(self):
        for i in reversed(range(self.enrollment_students_list.count())):
            item = self.enrollment_students_list.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        for s in self._enrollment_students:
            row = QHBoxLayout()
            row.setSpacing(8)
            name_label = QLabel(s.get("name", ""))
            name_label.setStyleSheet(f"color: {TEXT_PRI}; font-size: 11px; font-weight: 600; border: none; background: transparent;")
            row.addWidget(name_label)
            info_label = QLabel(f"{s.get('document', '')} · {s.get('status', '')}")
            info_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; border: none; background: transparent;")
            row.addWidget(info_label)
            row.addStretch()
            btn_del = QPushButton("✕")
            btn_del.setFixedSize(22, 22)
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {RED};
                    border: none; font-size: 12px; font-weight: 700;
                }}
                QPushButton:hover {{ color: #FF4444; }}
            """)
            sid = s["student_id"]
            btn_del.clicked.connect(lambda checked, id=sid: self._remove_enrollment_student(id))
            row.addWidget(btn_del)
            self.enrollment_students_list.addLayout(row)

        self._update_enrollment_limit_label()

    def _remove_enrollment_student(self, student_id):
        self._enrollment_students = [s for s in self._enrollment_students if s["student_id"] != student_id]
        self._refresh_enrollment_students_list()

    def _update_student_limit_label(self):
        if self._max_students > 0:
            self.lbl_student_limit.setText(f"{len(self._students)} / {self._max_students} " + tr("finances.income.dialog.students"))
        else:
            self.lbl_student_limit.setText("")

    # ── Wallet / Cartera Section ─────────────────────────────────

    WALLET_DETAILS_PREFIX = "__wallet_distribution__="

    def _item_total_for_wallet(self, item):
        return float(
            item.get(
                "subtotal",
                float(item.get("quantity", 1) or 1)
                * float(item.get("unit_price", 0) or 0)
                - float(item.get("discount", 0) or 0)
            )
            or 0
        )

    def _extract_wallet_paid_from_details(self, details):
        text = str(details or "")
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith(self.WALLET_DETAILS_PREFIX):
                continue

            raw = line.replace(self.WALLET_DETAILS_PREFIX, "", 1).strip()
            try:
                data = json.loads(raw)
                return float(data.get("paid", 0) or 0)
            except Exception:
                return None

        return None

    def _strip_wallet_details_from_text(self, details):
        lines = []
        for line in str(details or "").splitlines():
            if not line.strip().startswith(self.WALLET_DETAILS_PREFIX):
                lines.append(line)
        return "\n".join(lines).strip()

    def _inject_wallet_details(self, details, paid, pending):
        clean_details = self._strip_wallet_details_from_text(details)

        payload = {
            "paid": float(paid or 0),
            "pending": float(pending or 0),
        }

        wallet_line = self.WALLET_DETAILS_PREFIX + json.dumps(
            payload,
            ensure_ascii=False
        )

        if clean_details:
            return clean_details + "\n" + wallet_line

        return wallet_line

    def _strip_wallet_note_block(self, text):
        """
        Evita que al guardar varias veces se duplique el bloque de cartera
        dentro de agreement_note.
        """
        value = str(text or "").strip()
        header = tr("finances.income.dialog.wallet_detail_header")

        if not header or header == "finances.income.dialog.wallet_detail_header":
            header = "Detalle de cartera"

        idx = value.find(header)
        if idx >= 0:
            return value[:idx].strip()

        return value

    def _build_wallet_section(self):
        frame = QFrame()
        frame.setObjectName("walletFrame")
        frame.setStyleSheet(f"""
            QFrame#walletFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        header = QLabel(tr("finances.income.dialog.wallet"))
        header.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; border: none; background: transparent;")
        layout.addWidget(header)

        self.wallet_warning_label = QLabel("")
        self.wallet_warning_label.setStyleSheet(f"color: {RED}; font-size: 10px; font-weight: 600; border: none; background: transparent;")
        self.wallet_warning_label.hide()
        layout.addWidget(self.wallet_warning_label)

        wallet_hint = QLabel(
            trf("finances.income.dialog.wallet_distribution_help",
                "Distribuye el valor cancelado por cada concepto pendiente.")
        )
        wallet_hint.setWordWrap(True)
        wallet_hint.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        layout.addWidget(wallet_hint)

        wallet_rows_widget = QWidget()
        wallet_rows_widget.setStyleSheet("background: transparent;")
        self.wallet_rows_container = QVBoxLayout(wallet_rows_widget)
        self.wallet_rows_container.setContentsMargins(0, 0, 0, 0)
        self.wallet_rows_container.setSpacing(8)

        self.wallet_rows_scroll = QScrollArea()
        self.wallet_rows_scroll.setWidgetResizable(True)
        self.wallet_rows_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.wallet_rows_scroll.setMinimumHeight(160)
        self.wallet_rows_scroll.setMaximumHeight(280)
        self.wallet_rows_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
                border: none;
            }}
        """)
        self.wallet_rows_scroll.setWidget(wallet_rows_widget)
        layout.addWidget(self.wallet_rows_scroll)

        due_row = QHBoxLayout()
        due_row.setSpacing(8)
        due_row.addWidget(QLabel(tr("finances.income.dialog.wallet_due_date")))
        self.wallet_due_date = QDateEdit()
        self.wallet_due_date.setCalendarPopup(True)
        self.wallet_due_date.setDate(QDate.currentDate().addDays(10))
        self.wallet_due_date.setStyleSheet(f"""
            QDateEdit {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 12px; font-size: 13px; min-height: 36px;
            }}
            QDateEdit:focus {{ border-color: {RED}; }}
        """)
        due_row.addWidget(self.wallet_due_date)
        due_row.addStretch()
        layout.addLayout(due_row)

        help_lbl = QLabel(tr("finances.income.dialog.wallet_due_help"))
        help_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; border: none; background: transparent;")
        layout.addWidget(help_lbl)

        frame.hide()
        return frame

    def _clear_wallet_rows(self):
        while self.wallet_rows_container.count():
            item = self.wallet_rows_container.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
            elif child_layout:
                self._clear_layout(child_layout)

    def _refresh_wallet_table(self):
        if getattr(self, "_refreshing_wallet", False):
            return
        if getattr(self, "_is_populating", False):
            return

        self._refreshing_wallet = True
        try:
            self._clear_wallet_rows()
            self._wallet_paid_spins = []

            total_paid_all = self.spin_paid.value()
            if not self._items or total_paid_all <= 0:
                self._wallet_frame.hide()
                return

            subtotal = sum(float(item.get("subtotal", 0) or 0) for item in self._items)
            discount = self.spin_discount.value()
            total = max(0, subtotal - discount)
            pending = max(0, total - total_paid_all)

            if pending <= 0:
                self._wallet_frame.hide()
                return

            self._wallet_frame.show()

            has_saved_distribution = any(
                "wallet_paid" in item for item in self._items
            )

            for i, item in enumerate(self._items):
                item_total = self._item_total_for_wallet(item)

                if has_saved_distribution:
                    # Si hay distribución guardada, NO dividir proporcionalmente.
                    # Mostrar exactamente lo que ya estaba distribuido.
                    fallback_paid = 0
                else:
                    # Solo para ingresos viejos sin distribución guardada.
                    if total > 0:
                        ratio = item_total / total
                        fallback_paid = round(total_paid_all * ratio, 0)
                    else:
                        fallback_paid = 0

                item_paid = self._get_existing_wallet_paid_for_item(i, fallback_paid)
                item_paid = min(max(0, item_paid), item_total)

                item["wallet_paid"] = item_paid
                item["wallet_pending"] = max(0, item_total - item_paid)

                item_pending = item["wallet_pending"]

                row_frame = QFrame()
                row_frame.setObjectName("walletConceptRow")
                row_frame.setStyleSheet(f"""
                    QFrame#walletConceptRow {{
                        background: {BG_INPUT};
                        border: 1px solid {BORDER};
                        border-radius: 12px;
                    }}
                    QFrame#walletConceptRow QLabel {{
                        background: transparent;
                        border: none;
                    }}
                """)

                rlay = QHBoxLayout(row_frame)
                rlay.setContentsMargins(12, 10, 12, 10)
                rlay.setSpacing(12)

                left = QVBoxLayout()
                left.setSpacing(3)

                name_lbl = QLabel(item.get("name", ""))
                name_lbl.setStyleSheet(f"""
                    color: {TEXT_PRI};
                    font-size: 12px;
                    font-weight: 800;
                """)
                left.addWidget(name_lbl)

                meta_lbl = QLabel(
                    trf("finances.income.dialog.total_product", "Total producto")
                    + ": "
                    + format_money(item_total)
                )
                meta_lbl.setStyleSheet(f"""
                    color: {TEXT_MUT};
                    font-size: 10px;
                    font-weight: 600;
                """)
                left.addWidget(meta_lbl)

                rlay.addLayout(left, 1)

                spin_paid = QDoubleSpinBox()
                spin_paid.setRange(0, item_total)
                spin_paid.setDecimals(0)
                spin_paid.setSingleStep(1000)
                spin_paid.setPrefix("$ ")
                spin_paid.setValue(item_paid)
                spin_paid.setFixedWidth(140)
                spin_paid.setFixedHeight(36)
                spin_paid.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
                spin_paid.setStyleSheet(self._spin_style())
                spin_paid.valueChanged.connect(self._on_wallet_paid_changed)
                rlay.addWidget(spin_paid)

                pending_lbl = QLabel(format_money(item_pending))
                pending_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                pending_lbl.setMinimumWidth(90)
                pending_lbl.setStyleSheet(f"""
                    color: {YELLOW};
                    font-size: 12px;
                    font-weight: 900;
                """)
                rlay.addWidget(pending_lbl)

                self.wallet_rows_container.addWidget(row_frame)
                self._wallet_paid_spins.append(spin_paid)
        finally:
            self._refreshing_wallet = False

    def _on_wallet_paid_changed(self):
        total_paid = self.spin_paid.value()
        distributed = 0
        self._wallet_distribution = getattr(self, "_wallet_distribution", [])
        self._editing_wallet_values = True
        try:
            for i, spin in enumerate(getattr(self, "_wallet_paid_spins", [])):
                item_total = 0
                if i < len(self._items):
                    item = self._items[i]
                    item_total = self._item_total_for_wallet(item)
                else:
                    item = None
                    item_total = 0

                val = min(max(0, float(spin.value() or 0)), item_total)
                distributed += val
                pending = max(0, item_total - val)

                while len(self._wallet_distribution) <= i:
                    self._wallet_distribution.append(0)

                self._wallet_distribution[i] = val

                if item is not None:
                    item["wallet_paid"] = val
                    item["wallet_pending"] = pending

                row_frame = spin.parentWidget()
                if row_frame:
                    rlay = row_frame.layout()
                    if rlay and rlay.count() >= 3:
                        lbl = rlay.itemAt(2).widget()
                        if lbl and isinstance(lbl, QLabel):
                            lbl.setText(format_money(pending))
                            if pending > 0:
                                lbl.setStyleSheet(f"""
                                    color: {YELLOW};
                                    font-size: 12px;
                                    font-weight: 900;
                                """)
                            else:
                                lbl.setStyleSheet(f"""
                                    color: {GREEN};
                                    font-size: 12px;
                                    font-weight: 900;
                                """)
            if distributed > total_paid:
                self.wallet_warning_label.setText(tr("finances.income.dialog.wallet_warning_distributed"))
                self.wallet_warning_label.show()
            else:
                self.wallet_warning_label.hide()
            
            self._update_preview()
        finally:
            self._editing_wallet_values = False


    def _sync_wallet_distribution_from_spins(self):
        dist = []

        for i, spin in enumerate(getattr(self, "_wallet_paid_spins", [])):
            if i >= len(self._items):
                continue

            item = self._items[i]
            item_total = self._item_total_for_wallet(item)

            val = min(max(0, float(spin.value() or 0)), item_total)
            pending = max(0, item_total - val)

            while len(dist) <= i:
                dist.append(0)

            dist[i] = val

            item["wallet_paid"] = val
            item["wallet_pending"] = pending

        self._wallet_distribution = dist
        return dist

    def _get_existing_wallet_paid_for_item(self, index, fallback):
        if 0 <= index < len(self._items):
            item = self._items[index]

            if "wallet_paid" in item:
                item_total = self._item_total_for_wallet(item)
                return min(max(0, float(item.get("wallet_paid", 0) or 0)), item_total)

        distribution = getattr(self, "_wallet_distribution", [])

        if index < len(distribution):
            val = float(distribution[index] or 0)
            if val > 0:
                return val

        return fallback

    # ── Items Changed ─────────────────────────────────────────────

    def _on_items_changed(self):
        for item in self._items:
            self._hydrate_membership_prepaid_flags(item)
            self._ensure_item_membership_discount(item)

        if not getattr(self, "_is_populating", False):
            self._apply_membership_discounts_to_items()

        self._recalc()
        self._has_membership = False
        self._has_enrollment = False
        self._max_students = 0
        capacities = []

        for item in self._items:
            item_type = item.get("item_type", "")
            name = item.get("name", "").lower()
            if item_type == "membership":
                self._has_membership = True
                plan_cap = 1
                for plan in self._membership_plans:
                    if plan.get("id") == item.get("reference_id"):
                        pname = plan.get("name", "").lower()
                        if "grupal" in pname or "group" in pname or "familiar" in pname or "team" in pname:
                            plan_cap = plan.get("group_capacity", 3)
                        break
                capacities.append(plan_cap)
            if "matricula" in name or "matrícula" in name or "enrollment" in name:
                self._has_enrollment = True

        self._max_students = max(capacities) if capacities else 0

        if self._has_membership:
            self._students_frame.show()
        else:
            self._students_frame.hide()

        has_period = self._has_membership or self._has_enrollment
        self._period_sep.setVisible(has_period)
        self.lbl_period_header.setVisible(has_period)
        self.lbl_membership_month.setVisible(self._has_membership)
        self.membership_month_combo.setVisible(self._has_membership)
        self.prepaid_months_inline_row.setVisible(self._has_membership)
        self.lbl_enrollment_year.setVisible(self._has_enrollment)
        self.enrollment_year_spin.setVisible(self._has_enrollment)
        if hasattr(self, "_enrollment_details_frame"):
            self._enrollment_details_frame.setVisible(bool(self._has_enrollment))

        self._update_payment_periods()
        self._update_student_limit_label()
        self._update_enrollment_limit_label()
        self._refresh_wallet_table()
        self._refresh_prepaid_months_flow()

    def _build_membership_payment_period(self, item):
        self._hydrate_membership_prepaid_flags(item)
        month_value = self.membership_month_combo.currentData()
        year = QDate.currentDate().year()
        prepaid_count = int(item.get("prepaid_months_count", 1) or 1)
        is_prepaid = bool(item.get("is_prepaid_months", False))
        if is_prepaid and prepaid_count > 1:
            labels = self._get_prepaid_month_labels(month_value, prepaid_count)
            return "Meses: " + " → ".join(labels) + f" {year}"
        month_text = self.membership_month_combo.currentText()
        return f"Mes: {month_text} {year}"

    def _update_payment_periods(self):
        for item in self._items:
            item_type = item.get("item_type", "")
            name = item.get("name", "").lower()
            if item_type == "membership":
                item["payment_period"] = self._build_membership_payment_period(item)
            elif "matricula" in name or "matrícula" in name or "enrollment" in name:
                year = int(self.enrollment_year_spin.value())
                item["payment_period"] = f"Año matrícula: {year}"
            else:
                item.pop("payment_period", None)

    # ── Payment Section ────────────────────────────────────────────

    def _build_payment_section(self):
        frame = QFrame()
        frame.setObjectName("payFrame")
        frame.setStyleSheet(f"""
            QFrame#payFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        header = QLabel(tr("finances.income.dialog.payment_section"))
        header.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; border: none; background: transparent;")
        layout.addWidget(header)

        mid_row = QHBoxLayout()
        mid_row.setSpacing(12)

        m_col = QVBoxLayout()
        m_col.setSpacing(4)
        m_col.addWidget(QLabel(tr("finances.income.dialog.payment_method")))
        self.combo_payment_method = QComboBox()
        self.combo_payment_method.setStyleSheet(self._combo_style())
        self.combo_payment_method.addItem("—", None)
        for pm in self._payment_methods:
            self.combo_payment_method.addItem(pm["name"], pm["id"])
        self.combo_payment_method.currentIndexChanged.connect(self._update_preview)
        m_col.addWidget(self.combo_payment_method)
        mid_row.addLayout(m_col)

        a_col = QVBoxLayout()
        a_col.setSpacing(4)
        a_col.addWidget(QLabel(tr("finances.income.dialog.destination_account")))
        self.combo_account = QComboBox()
        self.combo_account.setStyleSheet(self._combo_style())
        self.combo_account.addItem("—", None)
        for ac in self._accounts:
            label = ac["name"]
            if ac["account_number"]:
                label += f" ({ac['account_number']})"
            self.combo_account.addItem(label, ac["id"])
        self.combo_account.currentIndexChanged.connect(self._update_preview)
        a_col.addWidget(self.combo_account)
        mid_row.addLayout(a_col)

        layout.addLayout(mid_row)

        amount_row = QHBoxLayout()
        amount_row.setSpacing(12)

        date_col = QVBoxLayout()
        date_col.setSpacing(4)
        date_col.addWidget(QLabel(tr("finances.income.dialog.income_date")))
        self.date_income = QDateEdit()
        self.date_income.setCalendarPopup(True)
        self.date_income.setDate(QDate.currentDate())
        self.date_income.setStyleSheet(f"""
            QDateEdit {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 12px; font-size: 13px; min-height: 38px;
            }}
            QDateEdit:focus {{ border-color: {RED}; }}
        """)
        self.date_income.dateChanged.connect(self._on_payment_date_changed)
        date_col.addWidget(self.date_income)
        amount_row.addLayout(date_col)

        paid_col = QVBoxLayout()
        paid_col.setSpacing(4)
        paid_col.addWidget(QLabel(tr("finances.income.dialog.paid_amount")))
        self.spin_paid = QDoubleSpinBox()
        self.spin_paid.setRange(0, 999999999)
        self.spin_paid.setDecimals(0)
        self.spin_paid.setSingleStep(1000)
        self.spin_paid.setPrefix("$ ")
        self.spin_paid.setStyleSheet(self._spin_style())
        self.spin_paid.valueChanged.connect(self._recalc)
        paid_col.addWidget(self.spin_paid)
        amount_row.addLayout(paid_col)

        disc_col = QVBoxLayout()
        disc_col.setSpacing(4)
        disc_col.addWidget(QLabel(tr("finances.income.dialog.discount")))
        self.spin_discount = QDoubleSpinBox()
        self.spin_discount.setRange(0, 999999999)
        self.spin_discount.setDecimals(0)
        self.spin_discount.setSingleStep(1000)
        self.spin_discount.setPrefix("$ ")
        self.spin_discount.setStyleSheet(self._spin_style())
        self.spin_discount.valueChanged.connect(self._recalc)
        disc_col.addWidget(self.spin_discount)
        amount_row.addLayout(disc_col)

        layout.addLayout(amount_row)

        return frame

    # ── Notes Section ──────────────────────────────────────────────

    def _build_notes_section(self):
        frame = QFrame()
        frame.setObjectName("notesFrame")
        frame.setStyleSheet(f"""
            QFrame#notesFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        layout.addWidget(QLabel(tr("finances.income.dialog.notes")))
        self.input_note = QTextEdit()
        self.input_note.setMaximumHeight(80)
        self.input_note.setStyleSheet(f"""
            QTextEdit {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 8px 12px; font-size: 13px;
            }}
            QTextEdit:focus {{ border-color: {RED}; }}
        """)
        self.input_note.textChanged.connect(self._update_preview)
        layout.addWidget(self.input_note)

        layout.addWidget(QLabel(tr("finances.income.dialog.agreement_notes")))
        self.input_agreement_note = QTextEdit()
        self.input_agreement_note.setMaximumHeight(80)
        self.input_agreement_note.setStyleSheet(self.input_note.styleSheet())
        self.input_agreement_note.textChanged.connect(self._update_preview)
        layout.addWidget(self.input_agreement_note)

        return frame

    # ── Preview Panel ──────────────────────────────────────────────

    def _build_preview_panel(self):
        panel = QFrame()
        panel.setObjectName("previewPanel")
        panel.setMinimumWidth(460)
        panel.setMaximumWidth(760)
        panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        panel.setStyleSheet(f"""
            QFrame#previewPanel {{
                background-color: #101010;
                border-left: 1px solid {BORDER};
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        header = QLabel(trf("finances.income.receipt.preview_title", "Vista previa del recibo"))
        header.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; font-weight: 900; letter-spacing: 2px; border: none; background: transparent; text-transform: uppercase;")
        layout.addWidget(header)

        self.receipt_preview_area = ReceiptPreviewArea()
        layout.addWidget(self.receipt_preview_area, 1)

        self.btn_receipt = QPushButton(trf("finances.income.receipt.save_generate", "Guardar y generar recibo"))
        self.btn_receipt.setFixedHeight(40)
        self.btn_receipt.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_receipt.setStyleSheet(f"""
            QPushButton {{
                background: {GREEN}; color: white;
                border: none; border-radius: 10px;
                font-size: 12px; font-weight: 700;
                padding: 0 16px;
            }}
            QPushButton:hover {{ background: #16A34A; }}
        """)
        self.btn_receipt.clicked.connect(lambda: self._save(generate_receipt=True))
        layout.addWidget(self.btn_receipt)

        return panel

    # ── Recalc ─────────────────────────────────────────────────────

    def _recalc(self):
        subtotal = sum(item.get("subtotal", 0) for item in self._items)
        discount = self.spin_discount.value()
        total = max(0, subtotal - discount)
        paid = self.spin_paid.value()
        pending = max(0, total - paid)

        if pending <= 0 and total > 0:
            status = "paid"
        elif paid > 0:
            status = "partial"
        else:
            status = "pending"

        self._current_status = status

        self._schedule_receipt_preview_update()

        if not getattr(self, "_editing_wallet_values", False):
            self._refresh_wallet_table()

    def _make_preview_item_row(self, item):
        item_type = item.get("item_type", "")
        name = item.get("base_name") or item.get("name", "")
        qty = item.get("quantity", 1)
        subtotal = float(item.get("subtotal", 0) or 0)
        disc = float(item.get("discount", 0) or 0)

        type_map = {
            "membership": trf("finances.income.dialog.item_type.membership", "Membresía"),
            "inventory": trf("finances.income.dialog.item_type.product", "Producto de inventario"),
            "inventory_product": trf("finances.income.dialog.item_type.product", "Producto de inventario"),
            "service": trf("finances.income.dialog.item_type.service", "Servicio"),
            "receivable": trf("finances.income.dialog.item_type.receivable", "Cartera"),
            "agreement": trf("finances.income.dialog.item_type.agreement", "Acuerdo"),
        }

        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{
                background: #111111;
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        lay = QVBoxLayout(row)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(2)

        type_lbl = QLabel(type_map.get(item_type, item_type))
        type_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 8px; font-weight: 900; letter-spacing: 1px;")
        lay.addWidget(type_lbl)

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"color: {TEXT_PRI}; font-size: 11px; font-weight: 800;")
        lay.addWidget(name_lbl)

        if item.get("payment_period"):
            period_lbl = QLabel(item["payment_period"])
            period_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px;")
            lay.addWidget(period_lbl)

        meta = f"{qty} × {format_money(subtotal / qty) if qty else '$0'}"
        meta_lbl = QLabel(meta)
        meta_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 9px;")
        lay.addWidget(meta_lbl)

        sub_row = QHBoxLayout()
        sub_row.setSpacing(8)

        if disc > 0:
            disc_lbl = QLabel(f"{tr('finances.income.dialog.discount')}: -{format_money(disc)}")
            disc_lbl.setStyleSheet(f"color: {GREEN}; font-size: 10px; font-weight: 700;")
            sub_row.addWidget(disc_lbl)

        sub_row.addStretch()
        sub_lbl = QLabel(format_money(subtotal))
        sub_lbl.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px; font-weight: 900;")
        sub_row.addWidget(sub_lbl)
        lay.addLayout(sub_row)

        return row

    def _clear_kid_warning(self):
        self._kid_warning_label.hide()
        self._kid_warning_label.setText("")

    def _show_kid_info(self, guardian_name):
        msg = trf("finances.income.dialog.kid_guardian_applied",
                   "KID student: guardian information will be used as client data.")
        self._kid_warning_label.setText("ℹ️ " + msg)
        self._kid_warning_label.setStyleSheet(
            "color: #27AE60; font-size: 11px; padding: 2px 0; font-weight: bold;")
        self._kid_warning_label.show()

    def _show_kid_guardian_missing(self):
        msg = trf("finances.income.dialog.guardian_missing",
                   "This KID student does not have a primary guardian registered.")
        self._kid_warning_label.setText("⚠️ " + msg)
        self._kid_warning_label.setStyleSheet(
            "color: #E67E22; font-size: 11px; padding: 2px 0; font-weight: bold;")
        self._kid_warning_label.show()

    def _on_payment_date_changed(self):
        if self._apply_membership_discounts_to_items():
            self._recalc()
            self._refresh_items_table()
        self._update_preview()

    def _on_membership_month_changed(self):
        self._update_payment_periods()
        self._apply_membership_discounts_to_items()
        self._recalc()
        self._refresh_items_table()
        self._update_preview()
        self._refresh_prepaid_months_flow()

    @staticmethod
    def _clear_layout(layout):
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            else:
                cl = item.layout()
                if cl:
                    IncomeDialog._clear_layout(cl)

    def _update_preview(self):
        self._schedule_receipt_preview_update()

    def _schedule_receipt_preview_update(self):
        if getattr(self, "_closing_dialog", False):
            return
        if getattr(self, "_is_populating", False):
            return
        if hasattr(self, "_receipt_preview_timer"):
            self._receipt_preview_timer.start()
        else:
            self._render_receipt_preview()

    def _build_receipt_preview_payload(self):
        subtotal = sum(float(item.get("subtotal", 0) or 0) for item in self._items)
        discount = float(self.spin_discount.value() or 0)
        total = max(0, subtotal - discount)
        paid = float(self.spin_paid.value() or 0)
        pending = max(0, total - paid)

        income_date = self.date_income.date().toPyDate()

        income = {
            "id": self.income.get("id") if self.income else 0,
            "receipt_number": self.income.get("receipt_number") if self.income else None,
            "payer_name": self.input_client_name.text().strip(),
            "payer_document": self.input_client_doc.text().strip(),
            "payer_email": self.input_client_email.text().strip(),
            "payer_phone": self.input_client_phone.text().strip(),
            "income_date": income_date,
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
            "total_paid": paid,
            "pending_amount": pending,
            "payment_method_name": self.combo_payment_method.currentText()
                if self.combo_payment_method.currentText() != "—" else "",
            "destination_account_name": self.combo_account.currentText()
                if self.combo_account.currentText() != "—" else "",
            "note": self.input_note.toPlainText().strip(),
            "agreement_note": self.input_agreement_note.toPlainText().strip(),
        }

        items = []
        for item in self._items:
            clean = dict(item)
            base_name = clean.get("base_name") or clean.get("name", "")
            payment_period = clean.get("payment_period")
            clean["name"] = f"{base_name} — {payment_period}" if payment_period else base_name
            items.append(clean)

        participants = []

        for s in self._students:
            participants.append({
                "display_name": s.get("name", ""),
                "expected_amount": 0,
                "paid_amount": 0,
                "pending_amount": 0,
                "person_id": s.get("person_id"),
            })

        for s in self._enrollment_students:
            if not any(p.get("display_name") == s.get("name") for p in participants):
                participants.append({
                    "display_name": s.get("name", ""),
                    "expected_amount": 0,
                    "paid_amount": 0,
                    "pending_amount": 0,
                    "person_id": s.get("person_id"),
                })

        if getattr(self, "_selected_payer_type", "") == "guardian" and self._selected_student_name:
            if not any(p.get("display_name") == self._selected_student_name for p in participants):
                participants.append({
                    "display_name": self._selected_student_name,
                    "expected_amount": 0,
                    "paid_amount": 0,
                    "pending_amount": 0,
                    "person_id": self._selected_student_person_id,
                })

        return income, items, participants

    def _render_receipt_preview(self):
        if getattr(self, "_closing_dialog", False):
            return

        try:
            income, items, participants = self._build_receipt_preview_payload()

            receipt_number = (
                self.income.get("receipt_number")
                if self.income and self.income.get("receipt_number")
                else "R-BORRADOR"
            )

            data = build_receipt_widget_data(
                income=income,
                items=items,
                participants=participants,
                receipt_number=receipt_number,
            )

            self._set_receipt_preview_data(data)

        except Exception as e:
            debug_log(f"[ReceiptWidgetPreview] error: {e}")

    def _set_receipt_preview_data(self, data: dict):
        try:
            if hasattr(self, "receipt_preview_area") and self.receipt_preview_area:
                self.receipt_preview_area.set_receipt_data(data)
        except Exception as e:
            debug_log(f"[ReceiptWidgetPreview] set data error: {e}")

    # ── Split helpers ──────────────────────────────────────────────

    def _split_item_name_and_period(self, raw_name):
        name = str(raw_name or "")
        if " — Meses: " in name:
            base, period_value = name.split(" — Meses: ", 1)
            return base.strip(), f"Meses: {period_value.strip()}"
        if " — Mes: " in name:
            base, period_value = name.split(" — Mes: ", 1)
            return base.strip(), f"Mes: {period_value.strip()}"
        if " — Año matrícula: " in name:
            base, period_value = name.split(" — Año matrícula: ", 1)
            return base.strip(), f"Año matrícula: {period_value.strip()}"
        return name.strip(), None

    def _set_membership_month_from_period(self, payment_period):
        if not payment_period:
            return
        text = str(payment_period)
        months = {
            "enero": "01", "febrero": "02", "marzo": "03",
            "abril": "04", "mayo": "05", "junio": "06",
            "julio": "07", "agosto": "08", "septiembre": "09",
            "octubre": "10", "noviembre": "11", "diciembre": "12",
        }
        lower = text.lower()
        for month_name, month_value in months.items():
            if month_name in lower:
                idx = self.membership_month_combo.findData(month_value)
                if idx >= 0:
                    self.membership_month_combo.setCurrentIndex(idx)
                return

    def _load_students_from_participants(self, participants):
        self._students = []

        for p in participants:
            expected = float(p.get("expected_amount", 0) or 0)
            pending = float(p.get("pending_amount", 0) or 0)

            # Los participantes de cartera tienen monto esperado/pending.
            # No deben cargarse como estudiantes.
            if expected > 0 or pending > 0:
                continue

            person_id = p.get("person_id")
            display_name = p.get("display_name", "")

            matched = None
            if person_id:
                matched = next(
                    (s for s in self._student_db if s.get("person_id") == person_id),
                    None
                )

            if matched:
                self._students.append(matched)
            else:
                self._students.append({
                    "student_id": p.get("student_id"),
                    "person_id": person_id,
                    "name": display_name,
                    "document": "",
                    "status": "",
                })

    # ── Populate (edit mode) ───────────────────────────────────────

    def _populate(self, income):
        self._is_populating = True

        try:
            self.date_income.blockSignals(True)
            self.membership_month_combo.blockSignals(True)
            self.spin_discount.blockSignals(True)
            self.spin_paid.blockSignals(True)

            self.input_client_name.setText(income.get("payer_name", ""))
            self.input_client_doc.setText(income.get("payer_document", ""))
            self.input_client_email.setText(income.get("payer_email", ""))
            self.input_client_phone.setText(income.get("payer_phone", ""))

            person_id = income.get("payer_person_id")
            if person_id:
                for idx in range(self.client_combo.count()):
                    d = self.client_combo.itemData(idx)
                    if isinstance(d, dict) and d.get("id") == person_id:
                        self.client_combo.setCurrentIndex(idx)
                        break

            items = income.get("items", [])
            if items:
                for item in items:
                    item_name = item.get("name", "")
                    base_name, payment_period = self._split_item_name_and_period(item_name)
                    loaded_item = {
                        "item_type": item.get("item_type", "agreement"),
                        "name": base_name,
                        "base_name": base_name,
                        "quantity": item.get("quantity", 1),
                        "unit_price": float(item.get("unit_price", 0)),
                        "discount": float(item.get("discount", 0)),
                        "subtotal": float(item.get("subtotal", 0)),
                        "reference_id": item.get("reference_id"),
                        "details": item.get("details", ""),
                    }
                    wallet_paid = self._extract_wallet_paid_from_details(
                        loaded_item.get("details", "")
                    )

                    if wallet_paid is not None:
                        item_total = self._item_total_for_wallet(loaded_item)
                        wallet_paid = min(max(0, wallet_paid), item_total)

                        loaded_item["wallet_paid"] = wallet_paid
                        loaded_item["wallet_pending"] = max(0, item_total - wallet_paid)

                    if payment_period:
                        loaded_item["payment_period"] = payment_period
                    self._items.append(loaded_item)

                for loaded_item in self._items:
                    if loaded_item.get("item_type") == "membership":
                        self._hydrate_membership_prepaid_flags(loaded_item)

                for loaded_item in self._items:
                    if loaded_item.get("item_type") == "membership":
                        self._set_membership_month_from_period(loaded_item.get("payment_period"))
                        break

            participants = income.get("participants", [])
            if participants:
                for p in participants:
                    expected = float(p.get("expected_amount", 0))
                    paid = float(p.get("paid_amount", 0))
                    due = p.get("due_date")
                    if due and not isinstance(due, QDate):
                        try:
                            due = QDate(due.year, due.month, due.day)
                        except Exception:
                            due = QDate.currentDate()
                    self._participants.append({
                        "display_name": p.get("display_name", ""),
                        "expected_amount": expected,
                        "paid_amount": paid,
                        "pending_amount": expected - paid,
                        "due_date": due,
                    })

                self._load_students_from_participants(participants)

                if any(self._is_enrollment_item(it) for it in self._items):
                    student_ids = {s["student_id"] for s in self._students}
                    for p in participants:
                        pid = p.get("person_id")
                        name = p.get("display_name", "")
                        matched = next(
                            (s for s in self._student_db if s.get("person_id") == pid),
                            None
                        )
                        if matched and matched["student_id"] not in student_ids:
                            self._enrollment_students.append(matched)
                        elif not matched and pid:
                            self._enrollment_students.append({
                                "student_id": pid,
                                "person_id": pid,
                                "name": name,
                                "document": "",
                                "status": "",
                            })

            self.spin_discount.setValue(float(income.get("discount", 0)))
            self.spin_paid.setValue(float(income.get("total_paid", 0)))
            self.input_note.setText(income.get("note", ""))
            self.input_agreement_note.setText(income.get("agreement_note", ""))

            if income.get("payment_method_id"):
                idx = self.combo_payment_method.findData(income["payment_method_id"])
                if idx >= 0:
                    self.combo_payment_method.setCurrentIndex(idx)

            if income.get("destination_account_id"):
                idx = self.combo_account.findData(income["destination_account_id"])
                if idx >= 0:
                    self.combo_account.setCurrentIndex(idx)

            if income.get("income_date"):
                try:
                    dt = income["income_date"]
                    if hasattr(dt, "strftime"):
                        qd = QDate(dt.year, dt.month, dt.day)
                        self.date_income.setDate(qd)
                except Exception:
                    pass

        finally:
            self.date_income.blockSignals(False)
            self.membership_month_combo.blockSignals(False)
            self.spin_discount.blockSignals(False)
            self.spin_paid.blockSignals(False)
            self._is_populating = False

        self._on_items_changed()
        self._refresh_items_table()
        self._refresh_students_list()
        self._refresh_enrollment_students_list()
        self._refresh_wallet_table()
        self._update_preview()

    # ── Validate & Save ────────────────────────────────────────────

    def _validate(self):
        client_data = self.client_combo.currentData()
        if client_data is None:
            self.lbl_error.setText(tr("finances.income.dialog.err_payer_required"))
            self.lbl_error.show()
            return False
        payer_name = self.input_client_name.text().strip()
        if isinstance(client_data, dict) and client_data.get("external") and not payer_name:
            self.lbl_error.setText(tr("finances.income.dialog.err_payer_required"))
            self.lbl_error.show()
            return False
        if not self._items:
            self.lbl_error.setText(tr("finances.income.dialog.err_items_required"))
            self.lbl_error.show()
            return False
        if self._has_membership and not self._students:
            self.lbl_error.setText(tr("finances.income.dialog.err_students_required"))
            self.lbl_error.show()
            return False
        if self._has_enrollment and not self._enrollment_students:
            self.lbl_error.setText(trf(
                "finances.income.dialog.err_enrollment_students_required",
                "Debe agregar al menos un estudiante de matrícula."
            ))
            self.lbl_error.show()
            return False
        self.lbl_error.hide()
        return True

    def _save(self, generate_receipt=False):
        if not self._validate():
            return

        self._recalc()
        self._sync_wallet_distribution_from_spins()

        client_data = self.client_combo.currentData()
        payer_name = self.input_client_name.text().strip()
        payer_type = "third_party"
        payer_person_id = None
        payer_doc = self.input_client_doc.text().strip()
        payer_email = self.input_client_email.text().strip()
        payer_phone = self.input_client_phone.text().strip()

        if isinstance(client_data, dict) and not client_data.get("external"):
            if not payer_name:
                payer_name = client_data.get("name", "")

            payer_person_id = client_data.get("id")

            if not payer_doc:
                payer_doc = client_data.get("document", "")

            if not payer_email:
                payer_email = client_data.get("email", "")

            if not payer_phone:
                payer_phone = client_data.get("phone", "")

            payer_type = client_data.get("payer_type", "third_party")

            # Caso KID: el pagador debe ser el acudiente, no el estudiante.
            if client_data.get("is_kid") and client_data.get("guardian_name"):
                payer_type = "guardian"
                payer_name = client_data.get("guardian_name", payer_name)
                payer_doc = client_data.get("guardian_document", payer_doc) or payer_doc
                payer_email = client_data.get("guardian_email", payer_email) or payer_email
                payer_phone = client_data.get("guardian_phone", payer_phone) or payer_phone

        if not payer_name:
            payer_name = payer_doc if payer_doc else tr("finances.income.dialog.unnamed")

        subtotal = sum(item.get("subtotal", 0) for item in self._items)
        discount = self.spin_discount.value()
        total = max(0, subtotal - discount)
        paid = self.spin_paid.value()
        pending = max(0, total - paid)

        if pending <= 0 and total > 0:
            status = "paid"
        elif paid > 0:
            status = "partial"
        else:
            status = "pending"

        # Build agreement_note with wallet details if pending
        agreement_note = self._strip_wallet_note_block(
            self.input_agreement_note.toPlainText().strip()
        )
        if pending > 0:
            wallet_lines = [tr("finances.income.dialog.wallet_detail_header")]
            for item in self._items:
                item_total = self._item_total_for_wallet(item)
                item_paid = float(item.get("wallet_paid", 0) or 0)
                item_paid = min(max(0, item_paid), item_total)
                item_pending = max(0, item_total - item_paid)

                wallet_lines.append(
                    f"- {item.get('name', '')}: total {format_money(item_total)}, "
                    f"pagado {format_money(item_paid)}, "
                    f"pendiente {format_money(item_pending)}"
                )
            if agreement_note:
                agreement_note += "\n\n" + "\n".join(wallet_lines)
            else:
                agreement_note = "\n".join(wallet_lines)

        # Build payload items without mutating self._items
        payload_items = []

        for i, item in enumerate(self._items):
            clean_item = dict(item)

            item_total = self._item_total_for_wallet(clean_item)
            item_paid = float(clean_item.get("wallet_paid", 0) or 0)
            item_paid = min(max(0, item_paid), item_total)
            item_pending = max(0, item_total - item_paid)

            clean_item["details"] = self._inject_wallet_details(
                clean_item.get("details", ""),
                item_paid,
                item_pending
            )

            base_name = clean_item.get("base_name") or clean_item.get("name", "")
            payment_period = clean_item.get("payment_period")

            if payment_period:
                clean_item["name"] = f"{base_name} — {payment_period}"
            else:
                clean_item["name"] = base_name

            payload_items.append(clean_item)

        # Build participants payload
        participants = []
        for s in self._students:
            participants.append({
                "display_name": s.get("name", ""),
                "expected_amount": 0,
                "paid_amount": 0,
                "pending_amount": 0,
                "due_date": None,
                "person_id": s.get("person_id"),
            })
        for es in self._enrollment_students:
            if not any(p.get("person_id") == es.get("person_id") for p in participants):
                participants.append({
                    "display_name": es.get("name", ""),
                    "expected_amount": 0,
                    "paid_amount": 0,
                    "pending_amount": 0,
                    "due_date": None,
                    "person_id": es.get("person_id"),
                })

        # Si el cliente seleccionado es un KID con acudiente, el estudiante KID
        # debe quedar asociado como participante.
        if (
            isinstance(client_data, dict)
            and client_data.get("is_kid")
            and client_data.get("guardian_name")
        ):
            kid_person_id = (
                client_data.get("student_person_id")
                or client_data.get("person_id")
                or self._selected_student_person_id
            )
            kid_name = (
                client_data.get("student_name")
                or client_data.get("name")
                or self._selected_student_name
            )

            if kid_name and not any(p.get("person_id") == kid_person_id for p in participants):
                participants.append({
                    "display_name": kid_name,
                    "expected_amount": 0,
                    "paid_amount": 0,
                    "pending_amount": 0,
                    "due_date": None,
                    "person_id": kid_person_id,
                })

        # If pending > 0, always create cartera participant
        if pending > 0:
            participants.append({
                "display_name": payer_name,
                "expected_amount": total,
                "paid_amount": paid,
                "pending_amount": pending,
                "due_date": self.wallet_due_date.date().toPyDate(),
                "person_id": payer_person_id,
                "is_wallet_summary": True,
            })

        data = {
            "payer_name": payer_name,
            "payer_type": payer_type,
            "payer_person_id": payer_person_id,
            "payer_document": payer_doc,
            "payer_email": payer_email,
            "payer_phone": payer_phone,
            "income_date": self.date_income.date().toPyDate(),
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
            "total_paid": paid,
            "pending_amount": pending,
            "status": status,
            "payment_method_id": self.combo_payment_method.currentData(),
            "destination_account_id": self.combo_account.currentData(),
            "note": self.input_note.toPlainText().strip(),
            "agreement_note": agreement_note,
            "items": payload_items,
            "participants": participants,
        }

        try:
            self.btn_save.setEnabled(False)
            if hasattr(self, "btn_receipt"):
                self.btn_receipt.setEnabled(False)

            if self.income is None:
                income_id = self.repo.create_income(data)
            else:
                income_id = self.income["id"]
                self.repo.update_income(income_id, data)

            if generate_receipt:
                try:
                    receipt_result = self._prepare_receipt_generation(income_id)
                    self._start_receipt_pdf_print(receipt_result)
                    return
                except Exception as e:
                    self.btn_save.setEnabled(True)
                    if hasattr(self, "btn_receipt"):
                        self.btn_receipt.setEnabled(True)

                    QMessageBox.warning(
                        self,
                        trf("finances.income.receipt.generated_error", "Error al generar recibo"),
                        str(e),
                    )
                    return
            else:
                self._soft_accept()
        except Exception as e:
            self.btn_save.setEnabled(True)
            if hasattr(self, "btn_receipt"):
                self.btn_receipt.setEnabled(True)
            QMessageBox.critical(self, tr("common.error"), str(e))

    def _disconnect_all_signals(self):
        """Desconecta signals de forma segura sin tocar objetos destruidos."""
        try:
            # NUNCA hacer .disconnect() sin argumentos en widgets específicos
            # porque puede que ya estén destruidos.
            # Solo usar blockSignals que es seguro.
            self.blockSignals(True)
        except Exception as e:
            print(f"[IncomeDialog] blockSignals error (safe): {e}")
            pass

        # Detener el timer específicamente
        try:
            if hasattr(self, '_receipt_preview_timer'):
                timer = getattr(self, '_receipt_preview_timer')
                if timer:
                    timer.stop()
                    # Solo desconectar conexiones conocidas si el timer es válido
                    try:
                        timer.timeout.disconnect()
                    except RuntimeError:
                        # Ya fue destruido, es ok
                        pass
        except Exception:
            pass

    def _soft_accept(self):
        if getattr(self, "_soft_closed", False):
            return

        self._soft_closed = True
        self._closing_dialog = True

        try:
            if hasattr(self, "_receipt_preview_timer"):
                self._receipt_preview_timer.stop()
        except Exception:
            pass

        self.done(QDialog.DialogCode.Accepted)

    def _soft_reject(self):
        if getattr(self, "_generating_receipt", False):
            QMessageBox.information(
                self,
                "Generando recibo",
                "Espera un momento mientras se genera el PDF del recibo."
            )
            return

        if getattr(self, "_soft_closed", False):
            return

        self._soft_closed = True
        self._closing_dialog = True

        try:
            if hasattr(self, "_receipt_preview_timer"):
                self._receipt_preview_timer.stop()
        except Exception:
            pass

        self.done(QDialog.DialogCode.Rejected)

    def _prepare_receipt_generation(self, income_id):
        full_income = self.repo.get_by_id(income_id)
        if not full_income:
            raise RuntimeError("No se pudo cargar el ingreso guardado.")

        items = self.repo.get_income_items(income_id)
        participants = self.repo.get_income_participants(income_id)

        result = prepare_receipt_files(full_income, items, participants)

        return {
            "receipt_number": result["receipt_number"],
            "html_path": result["html_path"],
            "pdf_path": result["pdf_path"],
            "income": full_income,
            "income_id": income_id,
        }

    def _start_receipt_pdf_print(self, receipt_result):
        debug_log(f"[FORENSIC] _start_receipt_pdf_print called, id={id(self)}")
        if not WEB_ENGINE_AVAILABLE:
            debug_log(f"[FORENSIC] PyQt6-WebEngine not available")
            raise RuntimeError("PyQt6-WebEngine no esta disponible para generar el PDF.")

        self._generating_receipt = True
        debug_log(f"[FORENSIC] _generating_receipt set to True")
        self._receipt_result_pending = receipt_result

        html_path = receipt_result["html_path"]
        pdf_path = receipt_result["pdf_path"]
        debug_log(f"[FORENSIC] Creating PDF WebEngine for {pdf_path}")

        self._pdf_print_view = QWebEngineView()
        self._pdf_print_view.hide()

        try:
            _WEBENGINE_KEEPALIVE.append(self._pdf_print_view)
            debug_log(f"[FORENSIC] Added PDF WebEngine to keepalive, count={len(_WEBENGINE_KEEPALIVE)}")
        except Exception:
            pass

        page = self._pdf_print_view.page()
        self._pdf_print_page = page

        # Conectar signals para tracking
        try:
            page.loadStarted.connect(
                lambda: debug_log(f"[FORENSIC] PDF loadStarted")
            )
            page.loadFinished.connect(
                lambda ok: debug_log(f"[FORENSIC] PDF loadFinished ok={ok}")
            )
            page.pdfPrintingFinished.connect(
                lambda path, ok: debug_log(f"[FORENSIC] PDF pdfPrintingFinished ok={ok}")
            )
        except Exception as e:
            debug_log(f"[FORENSIC] Failed to connect PDF signals: {e}")

        # Conectar destrucción
        self._pdf_print_view.destroyed.connect(
            lambda: debug_log(f"[FORENSIC] _pdf_print_view destroyed, id={id(self._pdf_print_view)}")
        )

        debug_log(f"[FORENSIC] PDF WebEngine created id={id(self._pdf_print_view)}")

        # Guardar referencias de las callbacks para poder desconectarlas
        def on_load_finished(ok):
            # Verificar que el diálogo no se está cerrando
            if getattr(self, "_closing_dialog", False):
                debug_log(f"[FORENSIC] on_load_finished: _closing_dialog=True, SKIPPING")
                return
            debug_log(f"[FORENSIC] on_load_finished called, ok={ok}")
            if not ok:
                self._finish_receipt_pdf_print(False, "No se pudo cargar el HTML del recibo.")
                return
            try:
                # Verificar nuevamente antes de ejecutar
                if not getattr(self, "_closing_dialog", False):
                    debug_log(f"[FORENSIC] on_load_finished: calling printToPdf")
                    page.printToPdf(pdf_path)
            except Exception as e:
                debug_log(f"[FORENSIC] on_load_finished error: {e}")
                if not getattr(self, "_closing_dialog", False):
                    self._finish_receipt_pdf_print(False, str(e))

        def on_pdf_finished(path, success):
            # Verificar que el diálogo no se está cerrando
            if getattr(self, "_closing_dialog", False):
                debug_log(f"[FORENSIC] on_pdf_finished: _closing_dialog=True, SKIPPING")
                return
            debug_log(f"[FORENSIC] on_pdf_finished called, path={path}, success={success}")
            QTimer.singleShot(
                0,
                lambda: self._finish_receipt_pdf_print(
                    bool(success),
                    "" if success else "No se pudo imprimir el PDF."
                ) if not getattr(self, "_closing_dialog", False) else None
            )

        # Guardar las callbacks para desconexión posterior
        self._pdf_on_load_finished = on_load_finished
        self._pdf_on_pdf_finished = on_pdf_finished

        page.loadFinished.connect(on_load_finished)
        page.pdfPrintingFinished.connect(on_pdf_finished)

        debug_log(f"[FORENSIC] Loading HTML from {html_path}")
        self._pdf_print_view.load(QUrl.fromLocalFile(str(Path(html_path).resolve())))

    def _finish_receipt_pdf_print(self, success, error_message=""):
        # Evitar ejecución si el diálogo se está cerrando
        if getattr(self, "_closing_dialog", False):
            debug_log(f"[FORENSIC] _finish_receipt_pdf_print: _closing_dialog=True, SKIPPING")
            return

        debug_log(f"[FORENSIC] _finish_receipt_pdf_print called, success={success}, error={error_message}")

        receipt_result = self._receipt_result_pending or {}

        # Desconectar usando referencias específicas (NO wildcard)
        try:
            page = getattr(self, "_pdf_print_page", None)
            if page:
                debug_log(f"[FORENSIC] Disconnecting PDF signals from page id={id(page)}")
                on_load = getattr(self, "_pdf_on_load_finished", None)
                on_pdf = getattr(self, "_pdf_on_pdf_finished", None)
                
                if on_load:
                    try:
                        page.loadFinished.disconnect(on_load)
                        debug_log(f"[FORENSIC] Disconnected loadFinished")
                    except RuntimeError:
                        pass
                
                if on_pdf:
                    try:
                        page.pdfPrintingFinished.disconnect(on_pdf)
                        debug_log(f"[FORENSIC] Disconnected pdfPrintingFinished")
                    except RuntimeError:
                        pass
        except Exception as e:
            debug_log(f"[FORENSIC] Error disconnecting signals: {e}")
            pass

        pdf_path = receipt_result.get("pdf_path")
        debug_log(f"[FORENSIC] PDF path={pdf_path}, exists={os.path.exists(pdf_path) if pdf_path else False}")

        if not success or not pdf_path or not os.path.exists(pdf_path):
            debug_log(f"[FORENSIC] PDF generation FAILED, cleaning up")
            self._generating_receipt = False
            self._cleanup_pdf_print_view_delayed()

            if not getattr(self, "_closing_dialog", False):
                QMessageBox.warning(
                    self,
                    "Error al generar recibo",
                    error_message or "No se pudo generar el PDF del recibo.",
                )

            self.btn_save.setEnabled(True)
            if hasattr(self, "btn_receipt"):
                self.btn_receipt.setEnabled(True)
            return

        try:
            debug_log(f"[FORENSIC] Updating receipt info for income_id={receipt_result.get('income_id')}")
            self.repo.update_receipt_info(
                receipt_result["income_id"],
                receipt_result["receipt_number"],
                pdf_path,
            )
        except Exception as e:
            debug_log(f"[FORENSIC] Error updating receipt info: {e}")
            self._generating_receipt = False
            self._cleanup_pdf_print_view_delayed()

            if not getattr(self, "_closing_dialog", False):
                QMessageBox.warning(self, "Error al guardar recibo", str(e))
            return

        self._generating_receipt = False
        debug_log(f"[FORENSIC] PDF generation SUCCESS, showing success dialog")

        if not getattr(self, "_closing_dialog", False):
            self._show_receipt_success_dialog(receipt_result, pdf_path)

    def _cleanup_pdf_print_view_delayed(self):
        view = getattr(self, "_pdf_print_view", None)

        self._pdf_print_page = None
        self._pdf_print_view = None
        self._receipt_result_pending = None

        if not view:
            return

        try:
            view.stop()
        except Exception:
            pass

        try:
            view.hide()
        except Exception:
            pass

        try:
            view.setParent(None)
        except Exception:
            pass

        try:
            if view not in _WEBENGINE_KEEPALIVE:
                _WEBENGINE_KEEPALIVE.append(view)
        except Exception:
            pass

    def _show_receipt_success_dialog(self, receipt_result, pdf_path):
        # No mostrar diálogo si el diálogo padre se está cerrando
        if getattr(self, "_closing_dialog", False):
            debug_log(f"[FORENSIC] _show_receipt_success_dialog: _closing_dialog=True, SKIPPING")
            return

        debug_log(f"[FORENSIC] _show_receipt_success_dialog called, id={id(self)}")
        income_for_dialog = receipt_result.get("income") or {}

        dlg = ReceiptGeneratedDialog(
            receipt_number=receipt_result.get("receipt_number", ""),
            receipt_path=pdf_path,
            payer_name=income_for_dialog.get("payer_name", ""),
            payer_phone=income_for_dialog.get("payer_phone", ""),
            payer_email=income_for_dialog.get("payer_email", ""),
            parent=self,
        )

        self._receipt_success_dialog = dlg

        def after_dialog_closed():
            debug_log(f"[FORENSIC] ReceiptGeneratedDialog finished, after_dialog_closed called")
            if not getattr(self, "_closing_dialog", False):
                self._receipt_success_dialog = None
                self._cleanup_pdf_print_view_delayed()
                QTimer.singleShot(500, self._soft_accept)

        dlg.finished.connect(lambda _: after_dialog_closed())
        debug_log(f"[FORENSIC] Calling dlg.open()")
        QTimer.singleShot(0, dlg.open)

    def showEvent(self, event):
        super().showEvent(event)

        self._closing_dialog = False
        self._soft_closed = False

        QTimer.singleShot(0, self._schedule_receipt_preview_update)
        QTimer.singleShot(150, self._schedule_receipt_preview_update)
        QTimer.singleShot(400, self._schedule_receipt_preview_update)

    def closeEvent(self, event):
        event.ignore()
        self._soft_reject()

    def reject(self):
        self._soft_reject()

    # ── Styles ─────────────────────────────────────────────────────

    def _input_style(self):
        return f"""
            QLineEdit {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 12px; font-size: 13px; min-height: 38px;
            }}
            QLineEdit:focus {{ border-color: {RED}; }}
        """

    def _combo_style(self):
        return f"""
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
        """

    def _spin_style(self):
        return f"""
            QDoubleSpinBox {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 12px; font-size: 13px; min-height: 38px;
            }}
            QDoubleSpinBox:focus {{ border-color: {RED}; }}
        """