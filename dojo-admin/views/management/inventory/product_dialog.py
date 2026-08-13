from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QPushButton, QFrame, QScrollArea, QWidget,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtGui import QPixmap
import os

from core.i18n import tr

BG_DIALOG = "#111111"
BG_INPUT  = "#1C1C1C"
BORDER    = "#2A2A2A"
RED       = "#C8102E"
RED_H     = "#E8152F"
TEXT_PRI  = "#F0F0F0"
TEXT_SEC  = "#888888"
TEXT_MUT  = "#666666"
GREEN     = "#22C55E"


def format_money(value):
    try:
        value = float(value or 0)
    except Exception:
        value = 0
    return "$" + f"{value:,.0f}".replace(",", ".")


class ProductDialog(QDialog):
    def __init__(self, repo, product=None, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.product = product
        from repositories.inventory_category_repository import InventoryCategoryRepository
        self.category_repo = InventoryCategoryRepository()
        self.setWindowTitle(tr("management.inventory.new_product") if product is None else tr("management.inventory.edit_product"))
        self.setMinimumSize(720, 620)
        self.resize(760, 680)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")
        self._build_ui()
        if product is not None:
            self._populate(product)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        form = QVBoxLayout(scroll_content)
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(16)

        main_frame = QFrame()
        main_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #161616;
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(10)

        main_header = QLabel(tr("management.inventory.product"))
        main_header.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; border: none; background: transparent;")
        main_layout.addWidget(main_header)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText(tr("management.inventory.product_placeholder"))
        self.input_name.setStyleSheet(self._input_style())
        main_layout.addWidget(self.input_name)

        category_row = QHBoxLayout()
        category_row.setSpacing(8)
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet(self._combo_style())
        self._load_categories()
        category_row.addWidget(self.category_combo, 1)
        self.btn_new_category = QPushButton("＋ " + tr("management.inventory.categories.new"))
        self.btn_new_category.setFixedHeight(38)
        self.btn_new_category.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_category.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 9px;
                font-size: 12px; font-weight: 700; padding: 0 12px;
            }}
            QPushButton:hover {{ border-color: {RED}; }}
        """)
        self.btn_new_category.clicked.connect(self._open_create_category)
        category_row.addWidget(self.btn_new_category)
        main_layout.addLayout(category_row)

        stock_lbl = QLabel(tr("management.inventory.stock"))
        stock_lbl.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        main_layout.addWidget(stock_lbl)
        self.spin_stock = QSpinBox()
        self.spin_stock.setMinimum(0)
        self.spin_stock.setMaximum(99999)
        self.spin_stock.setStyleSheet(self._spin_style())
        main_layout.addWidget(self.spin_stock)

        form.addWidget(main_frame)

        price_frame = QFrame()
        price_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #161616;
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        price_layout = QVBoxLayout(price_frame)
        price_layout.setContentsMargins(20, 16, 20, 16)
        price_layout.setSpacing(10)

        price_header = QLabel(tr("management.inventory.price"))
        price_header.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; border: none; background: transparent;")
        price_layout.addWidget(price_header)

        cost_row = QVBoxLayout()
        cost_row.setSpacing(4)
        cost_label = QLabel(tr("management.inventory.cost_price"))
        cost_label.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        cost_row.addWidget(cost_label)
        self.spin_cost = QDoubleSpinBox()
        self.spin_cost.setRange(0, 999999999)
        self.spin_cost.setDecimals(0)
        self.spin_cost.setSingleStep(1000)
        self.spin_cost.setPrefix("$ ")
        self.spin_cost.setStyleSheet(self._spin_style())
        cost_row.addWidget(self.spin_cost)
        price_layout.addLayout(cost_row)

        sale_row = QVBoxLayout()
        sale_row.setSpacing(4)
        sale_label = QLabel(tr("management.product.sale_price"))
        sale_label.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        sale_row.addWidget(sale_label)
        self.spin_price = QDoubleSpinBox()
        self.spin_price.setRange(0, 999999999)
        self.spin_price.setDecimals(0)
        self.spin_price.setSingleStep(1000)
        self.spin_price.setPrefix("$ ")
        self.spin_price.setStyleSheet(self._spin_style())
        sale_row.addWidget(self.spin_price)
        price_layout.addLayout(sale_row)

        self.lbl_preview_cost = QLabel("")
        self.lbl_preview_cost.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; font-weight: 600; border: none; background: transparent;")
        price_layout.addWidget(self.lbl_preview_cost)

        self.lbl_preview_sale = QLabel("")
        self.lbl_preview_sale.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; font-weight: 600; border: none; background: transparent;")
        price_layout.addWidget(self.lbl_preview_sale)

        self.lbl_preview_margin = QLabel("")
        self.lbl_preview_margin.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; font-weight: 600; border: none; background: transparent;")
        price_layout.addWidget(self.lbl_preview_margin)

        self.spin_cost.valueChanged.connect(self._update_preview)
        self.spin_price.valueChanged.connect(self._update_preview)

        form.addWidget(price_frame)

        img_frame = QFrame()
        img_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #161616;
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        img_layout = QVBoxLayout(img_frame)
        img_layout.setContentsMargins(20, 16, 20, 16)
        img_layout.setSpacing(10)

        img_header = QLabel(tr("management.product.image"))
        img_header.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900; border: none; background: transparent;")
        img_layout.addWidget(img_header)

        preview_row = QHBoxLayout()
        preview_row.setSpacing(12)

        self.img_preview = QLabel()
        self.img_preview.setFixedSize(100, 100)
        self.img_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_preview.setStyleSheet(f"""
            QLabel {{
                background-color: {BG_INPUT};
                border: 1px solid {BORDER};
                border-radius: 12px;
                color: {TEXT_MUT};
                font-size: 11px;
            }}
        """)
        self.img_preview.setText("\U0001f4e6 " + tr("management.product.no_image"))
        preview_row.addWidget(self.img_preview)

        img_col = QVBoxLayout()
        img_col.setSpacing(8)
        self.input_image = QLineEdit()
        self.input_image.setReadOnly(True)
        self.input_image.setPlaceholderText(tr("management.product.no_image"))
        self.input_image.setStyleSheet(self._input_style())
        img_col.addWidget(self.input_image)

        self.btn_image = QPushButton(tr("management.product.select_image"))
        self.btn_image.setFixedHeight(38)
        self.btn_image.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_image.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 9px;
                padding: 0 16px; font-size: 12px; font-weight: 600;
            }}
            QPushButton:hover {{ border-color: {RED}; }}
        """)
        self.btn_image.clicked.connect(self._select_image)
        img_col.addWidget(self.btn_image)
        preview_row.addLayout(img_col)
        img_layout.addLayout(preview_row)

        form.addWidget(img_frame)

        scroll.setWidget(scroll_content)
        root.addWidget(scroll, 1)

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

    def _update_preview(self):
        cost = self.spin_cost.value()
        sale = self.spin_price.value()
        self.lbl_preview_cost.setText(tr("management.product.cost_price") + ": " + format_money(cost))
        self.lbl_preview_sale.setText(tr("management.product.sale_price") + ": " + format_money(sale))
        margin = sale - cost
        if margin > 0:
            color = GREEN
        elif margin == 0:
            color = TEXT_MUT
        else:
            color = RED
        self.lbl_preview_margin.setText(tr("management.product.margin") + ": " + format_money(margin))
        self.lbl_preview_margin.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 600; border: none; background: transparent;")

    def _select_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("management.product.select_image"),
            "",
            "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if path:
            self.input_image.setText(path)
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.img_preview.setPixmap(scaled)
                self.img_preview.setStyleSheet(f"""
                    QLabel {{
                        background-color: {BG_INPUT};
                        border: 1px solid {BORDER};
                        border-radius: 12px;
                    }}
                """)

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
            QSpinBox, QDoubleSpinBox {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 12px; font-size: 13px; min-height: 38px;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{ border-color: {RED}; }}
        """

    def _load_categories(self):
        self.category_combo.clear()
        try:
            categories = self.category_repo.get_all()
            if not categories:
                self.category_combo.addItem(tr("management.category.no_types"), None)
                return
            for cat in categories:
                self.category_combo.addItem(cat["name"], cat["id"])
        except Exception as e:
            QMessageBox.critical(self, tr("common.error"), str(e))

    def _populate(self, product):
        self.input_name.setText(product["name"])
        for i in range(self.category_combo.count()):
            if self.category_combo.itemData(i) == product.get("id_inventory_category"):
                self.category_combo.setCurrentIndex(i)
                break
        self.spin_stock.setValue(product.get("stock", 0))
        self.spin_cost.setValue(product.get("cost_price", 0.0))
        self.spin_price.setValue(product.get("sale_price", 0.0))
        img = product.get("image_path", "")
        if img:
            self.input_image.setText(img)
            if os.path.exists(img):
                pixmap = QPixmap(img)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.img_preview.setPixmap(scaled)
                    self.img_preview.setStyleSheet(f"""
                        QLabel {{
                            background-color: {BG_INPUT};
                            border: 1px solid {BORDER};
                            border-radius: 12px;
                        }}
                    """)
        self._update_preview()

    def _validate(self):
        if not self.input_name.text().strip():
            self.lbl_error.setText(tr("management.inventory.err_name_required"))
            self.lbl_error.show()
            return False
        if self.category_combo.currentData() is None:
            self.lbl_error.setText(tr("management.inventory.err_category_required"))
            self.lbl_error.show()
            return False
        if self.spin_stock.value() < 0:
            self.lbl_error.setText(tr("management.inventory.err_stock_negative"))
            self.lbl_error.show()
            return False
        if self.spin_cost.value() < 0:
            self.lbl_error.setText(tr("management.inventory.err_cost_negative"))
            self.lbl_error.show()
            return False
        if self.spin_price.value() < 0:
            self.lbl_error.setText(tr("management.inventory.err_price_negative"))
            self.lbl_error.show()
            return False
        self.lbl_error.hide()
        return True

    def _open_create_category(self):
        from views.management.inventory.inventory_category_dialog import InventoryCategoryDialog
        dlg = InventoryCategoryDialog(repo=self.category_repo, parent=self)
        if dlg.exec():
            self._load_categories()

    def _save(self):
        if not self._validate():
            return
        sale = self.spin_price.value()
        cost = self.spin_cost.value()

        if sale < cost:
            reply = QMessageBox.question(
                self,
                self.windowTitle(),
                tr("management.inventory.price_below_cost_confirm"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        name = self.input_name.text().strip()
        id_cat = self.category_combo.currentData()
        stock = self.spin_stock.value()
        image_path = self.input_image.text().strip()

        try:
            if self.product is None:
                self.repo.create_product(id_cat, name, cost, sale, stock, image_path)
            else:
                self.repo.update_product(self.product["id"], id_cat, name, cost, sale, stock, image_path)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, tr("common.error"), str(e))
