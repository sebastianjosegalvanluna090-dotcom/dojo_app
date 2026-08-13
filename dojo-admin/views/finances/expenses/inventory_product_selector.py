from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QListWidget,
    QListWidgetItem, QMessageBox, QSpinBox, QDoubleSpinBox,
    QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from core.i18n import tr
from repositories.inventory_repository import InventoryRepository

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


class InventoryProductSelector(QDialog):
    def __init__(self, repo, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.selected_product = None
        self.quantity = 1
        self.unit_cost = 0
        self.setWindowTitle(tr("finances.expenses.select_product"))
        self.setMinimumSize(500, 480)
        self.resize(540, 520)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")
        self._build_ui()
        self._load_products()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        title = QLabel(tr("finances.expenses.select_product"))
        title.setStyleSheet("color: white; font-size: 18px; font-weight: 900;")
        root.addWidget(title)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 " + tr("finances.expenses.search_product"))
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 12px; font-size: 13px; min-height: 36px;
            }}
            QLineEdit:focus {{ border-color: {RED}; }}
        """)
        self.search_input.textChanged.connect(self._filter_products)
        root.addWidget(self.search_input)

        self.product_list = QListWidget()
        self.product_list.setStyleSheet(f"""
            QListWidget {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
                color: {TEXT_PRI};
                font-size: 13px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 10px 14px;
                border-radius: 8px;
            }}
            QListWidget::item:hover {{
                background-color: {BG_INPUT};
            }}
            QListWidget::item:selected {{
                background-color: rgba(200,16,46,0.3);
                color: white;
            }}
        """)
        root.addWidget(self.product_list, 1)

        details_frame = QFrame()
        details_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        details_layout = QHBoxLayout(details_frame)
        details_layout.setContentsMargins(16, 12, 16, 12)
        details_layout.setSpacing(12)

        qty_layout = QVBoxLayout()
        qty_layout.setSpacing(4)
        qty_label = QLabel(tr("finances.expenses.quantity"))
        qty_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 700; border: none; background: transparent;")
        qty_layout.addWidget(qty_label)
        self.spin_qty = QSpinBox()
        self.spin_qty.setMinimum(1)
        self.spin_qty.setMaximum(99999)
        self.spin_qty.setValue(1)
        self.spin_qty.setStyleSheet(f"""
            QSpinBox {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 10px; font-size: 13px; min-height: 34px;
            }}
        """)
        qty_layout.addWidget(self.spin_qty)
        details_layout.addLayout(qty_layout)

        cost_layout = QVBoxLayout()
        cost_layout.setSpacing(4)
        cost_label = QLabel(tr("finances.expenses.unit_cost"))
        cost_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 700; border: none; background: transparent;")
        cost_layout.addWidget(cost_label)
        self.spin_cost = QDoubleSpinBox()
        self.spin_cost.setRange(0, 999999999)
        self.spin_cost.setDecimals(0)
        self.spin_cost.setSingleStep(1000)
        self.spin_cost.setPrefix("$ ")
        self.spin_cost.setStyleSheet(f"""
            QDoubleSpinBox {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 10px; font-size: 13px; min-height: 34px;
            }}
        """)
        cost_layout.addWidget(self.spin_cost)
        details_layout.addLayout(cost_layout)

        root.addWidget(details_frame)

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

        self.btn_accept = QPushButton(tr("finances.expenses.add_product"))
        self.btn_accept.setFixedHeight(36)
        self.btn_accept.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_accept.setStyleSheet(f"""
            QPushButton {{
                background: {RED}; color: white;
                border: none; border-radius: 9px; font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        self.btn_accept.clicked.connect(self._accept)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self.btn_accept)
        root.addLayout(btn_row)

    def _load_products(self, search=""):
        self.product_list.clear()
        try:
            products = self.repo.get_all(search)
            for p in products:
                item = QListWidgetItem(f"{p['name']} — {self._format_money(p.get('sale_price', 0))}")
                item.setData(Qt.ItemDataRole.UserRole, p)
                self.product_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, tr("common.error"), str(e))

    def _format_money(self, value):
        try:
            value = float(value or 0)
        except Exception:
            value = 0
            return "$0"
        return "$" + f"{value:,.0f}".replace(",", ".")

    def _filter_products(self, text):
        self._load_products(text.strip())

    def _accept(self):
        current = self.product_list.currentItem()
        if current is None:
            QMessageBox.warning(self, self.windowTitle(), tr("finances.expenses.err_select_product"))
            return
        self.selected_product = current.data(Qt.ItemDataRole.UserRole)
        self.quantity = self.spin_qty.value()
        self.unit_cost = self.spin_cost.value()
        if self.unit_cost <= 0:
            QMessageBox.warning(self, self.windowTitle(), tr("finances.expenses.err_unit_cost"))
            return
        self.accept()
