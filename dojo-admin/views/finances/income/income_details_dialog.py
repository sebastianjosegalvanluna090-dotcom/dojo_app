from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QScrollArea, QWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

from core.i18n import tr, trf
from services.receipt_generator import generate_receipt, build_receipt_number


BG_DIALOG = "#111111"
BG_CARD   = "#161616"
BG_HOVER  = "#1A1A1A"
BORDER    = "#2A2A2A"
RED       = "#C8102E"
GREEN     = "#22C55E"
YELLOW    = "#EAB308"
TEXT_PRI  = "#F0F0F0"
TEXT_SEC  = "#888888"
TEXT_MUT  = "#666666"


def format_money(value):
    try:
        value = float(value or 0)
    except Exception:
        value = 0
    return "$" + f"{value:,.0f}".replace(",", ".")


class IncomeDetailsDialog(QDialog):
    editRequested = pyqtSignal(object)
    deleteRequested = pyqtSignal(object)

    def __init__(self, repo, income, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.income = income
        self._action = None
        self.setWindowTitle(trf("finances.income.details.title", "Income Details"))
        self.setMinimumSize(860, 680)
        self.resize(920, 760)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")
        self._build_ui()

    @property
    def action(self):
        return self._action

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        body = QVBoxLayout(scroll_content)
        body.setContentsMargins(24, 20, 24, 16)
        body.setSpacing(20)

        header = QFrame()
        header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)

        text_col = QVBoxLayout()
        text_col.setSpacing(4)

        title = QLabel(str(self.income.get("payer_name") or ""))
        title.setStyleSheet("color: white; font-size: 22px; font-weight: 900;")
        text_col.addWidget(title)

        payer_type = self.income.get("payer_type", "third_party")
        type_map = {
            "student": trf("finances.income.dialog.payer_type.student", "Student"),
            "guardian": trf("finances.income.dialog.payer_type.guardian", "Guardian"),
            "third_party": trf("finances.income.dialog.payer_type.third_party", "Third Party"),
        }
        type_str = type_map.get(payer_type, payer_type)
        type_lbl = QLabel(type_str)
        type_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px; font-weight: 600;")
        text_col.addWidget(type_lbl)

        date_val = self.income.get("income_date", "")
        if date_val:
            try:
                if hasattr(date_val, "strftime"):
                    date_str = date_val.strftime("%d/%m/%Y")
                else:
                    date_str = str(date_val)[:10]
            except Exception:
                date_str = str(date_val)
        else:
            date_str = "—"
        date_lbl = QLabel(f"{trf('finances.income.details.date', 'Date')}: {date_str}")
        date_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; font-weight: 600;")
        text_col.addWidget(date_lbl)

        text_col.addStretch()
        header_layout.addLayout(text_col, 1)

        status = self.income.get("status", "pending")
        status_map = {
            "paid": (tr("finances.income.status.paid"), GREEN, "rgba(34,197,94,0.10)", "rgba(34,197,94,0.25)"),
            "partial": (tr("finances.income.status.partial"), YELLOW, "rgba(234,179,8,0.10)", "rgba(234,179,8,0.25)"),
            "pending": (tr("finances.income.status.pending"), RED, "rgba(200,16,46,0.10)", "rgba(200,16,46,0.25)"),
            "cancelled": (tr("finances.income.status.cancelled"), TEXT_MUT, "rgba(102,102,102,0.10)", "rgba(102,102,102,0.25)"),
        }
        stext, scolor, sbg, sborder = status_map.get(status, status_map["pending"])
        badge = QLabel(stext)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setMinimumWidth(104)
        badge.setFixedHeight(32)
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {sbg};
                color: {scolor};
                border: 1px solid {sborder};
                border-radius: 7px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 900;
            }}
        """)
        header_layout.addWidget(badge)

        body.addWidget(header)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)

        stats_row.addWidget(self._stat_card(
            trf("finances.income.details.total", "Total"),
            format_money(self.income.get("total", 0)),
            TEXT_PRI
        ))
        stats_row.addWidget(self._stat_card(
            trf("finances.income.details.paid", "Paid"),
            format_money(self.income.get("total_paid", 0)),
            GREEN
        ))
        stats_row.addWidget(self._stat_card(
            trf("finances.income.details.pending", "Pending"),
            format_money(self.income.get("pending_amount", 0)),
            YELLOW if float(self.income.get("pending_amount", 0) or 0) > 0 else TEXT_MUT
        ))

        body.addLayout(stats_row)

        items_header = QLabel(trf("finances.income.details.items", "Items"))
        items_header.setStyleSheet(f"color: {TEXT_PRI}; font-size: 15px; font-weight: 800;")
        body.addWidget(items_header)

        self.items_table = QTableWidget(0, 6)
        self.items_table.setHorizontalHeaderLabels([
            trf("finances.income.dialog.item_name", "Item name"),
            trf("finances.income.dialog.item_type", "Type"),
            trf("finances.income.dialog.item_quantity", "Quantity"),
            trf("finances.income.dialog.item_unit_price", "Unit price"),
            trf("finances.income.dialog.item_discount", "Discount"),
            trf("finances.income.dialog.item_subtotal", "Subtotal"),
        ])
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setShowGrid(False)
        self.items_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.items_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.items_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
                outline: none;
                color: {TEXT_PRI};
                gridline-color: transparent;
                selection-background-color: {BG_HOVER};
                font-size: 13px;
            }}
            QHeaderView::section {{
                background-color: {BG_HOVER};
                color: {TEXT_SEC};
                border: none;
                border-bottom: 1px solid {BORDER};
                padding: 12px;
                font-size: 10px;
                font-weight: 900;
            }}
            QTableWidget::item {{
                border: none;
                border-bottom: 1px solid {BORDER};
                padding: 8px;
            }}
        """)
        self.items_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.items_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.items_table.setColumnWidth(1, 130)
        self.items_table.setColumnWidth(2, 80)
        self.items_table.setColumnWidth(3, 120)
        self.items_table.setColumnWidth(4, 110)
        self.items_table.setColumnWidth(5, 120)
        for i in range(1, 6):
            self.items_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)

        body.addWidget(self.items_table)

        participants_header = QLabel(trf("finances.income.details.participants", "Participants"))
        participants_header.setStyleSheet(f"color: {TEXT_PRI}; font-size: 15px; font-weight: 800;")
        body.addWidget(participants_header)

        self.participants_table = QTableWidget(0, 5)
        self.participants_table.setHorizontalHeaderLabels([
            trf("finances.income.dialog.participant_name", "Name"),
            trf("finances.income.dialog.participant_expected", "Expected"),
            trf("finances.income.dialog.participant_paid", "Paid"),
            trf("finances.income.dialog.participant_pending", "Pending"),
            trf("finances.income.dialog.participant_due", "Due Date"),
        ])
        self.participants_table.verticalHeader().setVisible(False)
        self.participants_table.setShowGrid(False)
        self.participants_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.participants_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.participants_table.setStyleSheet(self.items_table.styleSheet())
        self.participants_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.participants_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.participants_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.participants_table.setColumnWidth(1, 110)
        self.participants_table.setColumnWidth(2, 110)
        self.participants_table.setColumnWidth(3, 110)
        self.participants_table.setColumnWidth(4, 120)
        for i in range(1, 5):
            self.participants_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)

        body.addWidget(self.participants_table)

        note = self.income.get("note", "").strip()
        if note:
            note_lbl = QLabel(trf("finances.income.details.notes", "Notes") + ": " + note)
            note_lbl.setWordWrap(True)
            note_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-weight: 600;")
            body.addWidget(note_lbl)

        agreement = self.income.get("agreement_note", "").strip()
        if agreement:
            agreement_lbl = QLabel(trf("finances.income.details.agreement_notes", "Agreement Notes") + ": " + agreement)
            agreement_lbl.setWordWrap(True)
            agreement_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-weight: 600;")
            body.addWidget(agreement_lbl)

        body.addStretch()
        scroll.setWidget(scroll_content)
        root.addWidget(scroll, 1)

        footer_container = QFrame()
        footer_container.setStyleSheet("background: transparent;")
        footer_layout = QVBoxLayout(footer_container)
        footer_layout.setContentsMargins(24, 14, 24, 20)
        footer_layout.setSpacing(0)

        sep_footer = QFrame()
        sep_footer.setFixedHeight(1)
        sep_footer.setStyleSheet(f"background: {BORDER}; border: none;")
        footer_layout.addWidget(sep_footer)
        footer_layout.addSpacing(12)

        footer = QHBoxLayout()
        footer.setSpacing(10)

        self.btn_edit = QPushButton(trf("finances.income.edit", "Edit"))
        self.btn_edit.setFixedSize(110, 42)
        self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 9px;
                font-size: 13px; font-weight: 800; padding: 0 18px;
            }}
            QPushButton:hover {{ background: {BG_HOVER}; border-color: {GREEN}; }}
        """)
        self.btn_edit.clicked.connect(lambda: self._on_action("edit"))

        self.btn_delete = QPushButton(trf("finances.income.delete", "Delete"))
        self.btn_delete.setFixedSize(110, 42)
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {RED};
                border: 1px solid {BORDER}; border-radius: 9px;
                font-size: 13px; font-weight: 800; padding: 0 18px;
            }}
            QPushButton:hover {{ border-color: {RED}; background: rgba(200,16,46,0.1); }}
        """)
        self.btn_delete.clicked.connect(lambda: self._on_action("delete"))

        self.btn_receipt = QPushButton()
        self.btn_receipt.setFixedSize(140, 42)
        self.btn_receipt.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_receipt_button()
        self.btn_receipt.clicked.connect(self._on_receipt_action)

        footer.addWidget(self.btn_edit)
        footer.addWidget(self.btn_delete)
        footer.addWidget(self.btn_receipt)
        footer.addStretch()

        btn_close = QPushButton(trf("close", "Close"))
        btn_close.setFixedSize(110, 42)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 9px;
                font-size: 13px; font-weight: 800; padding: 0 18px;
            }}
            QPushButton:hover {{ border-color: {RED}; }}
        """)
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)

        footer_layout.addLayout(footer)
        root.addWidget(footer_container)

        self._populate_tables()

    @staticmethod
    def _fit_table_height(table, max_visible_rows=5):
        header_h = table.horizontalHeader().height()
        rows = table.rowCount()
        visible_rows = min(max(rows, 1), max_visible_rows)
        row_h = 44
        total_h = header_h + (visible_rows * row_h) + 18
        table.setMinimumHeight(total_h)
        table.setMaximumHeight(total_h)

    def _stat_card(self, label, value, color):
        card = QFrame()
        card.setFixedHeight(100)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 150))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        lbl_label = QLabel(label)
        lbl_label.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 900; border: none; background: transparent;")
        layout.addWidget(lbl_label)

        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 900; border: none; background: transparent;")
        layout.addWidget(lbl_value)

        return card

    def _on_action(self, action: str):
        self._action = action
        if action == "edit":
            self.editRequested.emit(self.income)
        elif action == "delete":
            self.deleteRequested.emit(self.income)

    def _update_receipt_button(self):
        file_path = self.income.get("receipt_pdf_path") or self.income.get("receipt_html_path")
        import os
        file_exists = bool(file_path) and os.path.exists(file_path)

        if file_exists:
            text = trf("finances.income.receipt.open", "Abrir recibo")
            bg = "transparent"
            border_color = GREEN
            text_color = GREEN
            hover_bg = "rgba(34,197,94,0.1)"
        else:
            text = trf("finances.income.receipt.generate", "Generar recibo")
            bg = "transparent"
            border_color = BORDER
            text_color = TEXT_SEC
            hover_bg = BG_HOVER

        self.btn_receipt.setText(text)
        self.btn_receipt.setStyleSheet(f"""
            QPushButton {{
                background: {bg}; color: {text_color};
                border: 1px solid {border_color}; border-radius: 9px;
                font-size: 13px; font-weight: 800; padding: 0 18px;
            }}
            QPushButton:hover {{ background: {hover_bg}; }}
        """)

    def _on_receipt_action(self):
        import os
        import subprocess
        import sys

        file_path = self.income.get("receipt_pdf_path") or self.income.get("receipt_html_path")
        file_exists = file_path and os.path.exists(file_path)

        if file_exists:
            self._open_file(file_path)
            return

        try:
            income_id = self.income.get("id")
            if not income_id:
                return

            full_income = self.repo.get_by_id(income_id)
            if not full_income:
                return
            items = self.repo.get_income_items(income_id)
            participants = self.repo.get_income_participants(income_id)

            result = generate_receipt(full_income, items, participants)

            stored_path = result.get("pdf_path") or result.get("html_path")
            self.repo.update_receipt_info(
                income_id,
                result["receipt_number"],
                stored_path,
            )

            self.income["receipt_number"] = result["receipt_number"]
            self.income["receipt_pdf_path"] = stored_path
            self._update_receipt_button()

            QMessageBox.information(
                self,
                trf("finances.income.receipt.generated_success", "Recibo generado"),
                trf("finances.income.receipt.generated_success_msg",
                    "Recibo generado correctamente."),
            )

            if stored_path and os.path.exists(stored_path):
                self._open_file(stored_path)

        except Exception as e:
            QMessageBox.critical(
                self,
                trf("finances.income.receipt.generated_error", "Error"),
                str(e),
            )

    @staticmethod
    def _open_file(path):
        import os
        import subprocess
        import sys

        path = str(path)
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])

    def closeEvent(self, event):
        self.setGraphicsEffect(None)
        super().closeEvent(event)

    def _populate_tables(self):
        items = self.income.get("items", [])
        self.items_table.setRowCount(0)
        if items:
            self.items_table.setRowCount(len(items))
            type_map = {
                "membership": trf("finances.income.dialog.item_type.membership", "Membership"),
                "product": trf("finances.income.dialog.item_type.product", "Product"),
                "service": trf("finances.income.dialog.item_type.service", "Service"),
                "receivable": trf("finances.income.dialog.item_type.receivable", "Receivable"),
                "agreement": trf("finances.income.dialog.item_type.agreement", "Agreement"),
                "inventory": trf("finances.income.dialog.item_type.product", "Product"),
                "inventory_product": trf("finances.income.dialog.item_type.product", "Product"),
                "custom": trf("finances.income.dialog.item_type.custom", "Custom"),
            }
            for i, item in enumerate(items):
                self.items_table.setItem(i, 0, QTableWidgetItem(str(item.get("name", ""))))
                self.items_table.setItem(i, 1, QTableWidgetItem(type_map.get(item.get("item_type", ""), item.get("item_type", ""))))
                self.items_table.setItem(i, 2, QTableWidgetItem(str(item.get("quantity", 1))))
                self.items_table.setItem(i, 3, QTableWidgetItem(format_money(item.get("unit_price", 0))))
                self.items_table.setItem(i, 4, QTableWidgetItem(format_money(item.get("discount", 0))))
                self.items_table.setItem(i, 5, QTableWidgetItem(format_money(item.get("subtotal", 0))))
                self.items_table.setRowHeight(i, 44)
                details = item.get("details", "")
                if details:
                    self.items_table.item(i, 0).setToolTip(details)
        else:
            self.items_table.setRowCount(1)
            self.items_table.setRowHeight(0, 44)
            self.items_table.setSpan(0, 0, 1, 6)
            empty_item = QTableWidgetItem(trf("finances.income.details.no_items", "No items registered for this income."))
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.items_table.setItem(0, 0, empty_item)

        participants = self.income.get("participants", [])
        self.participants_table.setRowCount(0)
        if participants:
            self.participants_table.setRowCount(len(participants))
            for i, p in enumerate(participants):
                self.participants_table.setItem(i, 0, QTableWidgetItem(str(p.get("display_name", ""))))
                self.participants_table.setItem(i, 1, QTableWidgetItem(format_money(p.get("expected_amount", 0))))
                self.participants_table.setItem(i, 2, QTableWidgetItem(format_money(p.get("paid_amount", 0))))
                self.participants_table.setItem(i, 3, QTableWidgetItem(format_money(p.get("pending_amount", 0))))
                due = p.get("due_date", "")
                if due:
                    try:
                        if hasattr(due, "strftime"):
                            due_str = due.strftime("%d/%m/%Y")
                        else:
                            due_str = str(due)[:10]
                    except Exception:
                        due_str = str(due)
                else:
                    due_str = "—"
                self.participants_table.setItem(i, 4, QTableWidgetItem(due_str))
                self.participants_table.setRowHeight(i, 44)
        else:
            self.participants_table.setRowCount(1)
            self.participants_table.setRowHeight(0, 44)
            self.participants_table.setSpan(0, 0, 1, 5)
            empty_item = QTableWidgetItem(trf("finances.income.details.no_participants", "No participants associated."))
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.participants_table.setItem(0, 0, empty_item)

        self._fit_table_height(self.items_table, max_visible_rows=4)
        self._fit_table_height(self.participants_table, max_visible_rows=4)
