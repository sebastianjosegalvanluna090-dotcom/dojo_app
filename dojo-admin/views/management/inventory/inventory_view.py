from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox,
    QSizePolicy, QGraphicsOpacityEffect, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QEvent,
    QPropertyAnimation, QEasingCurve,
)
from PyQt6.QtGui import QColor, QCursor

from core.i18n import tr
from repositories.inventory_repository import InventoryRepository
from views.management.inventory.product_dialog import ProductDialog
from views.management.inventory.product_details_dialog import ProductDetailsDialog
from views.management.inventory.inventory_category_dialog import InventoryCategoryDialog

BG_MAIN  = "#0D0D0D"
BG_CARD  = "#161616"
BG_HOVER = "#1A1A1A"
BORDER   = "#2A2A2A"
RED      = "#C8102E"
RED_H    = "#E8152F"
TEXT_PRI = "#F0F0F0"
TEXT_SEC = "#888888"
TEXT_MUT = "#666666"
GREEN    = "#22C55E"
YELLOW   = "#EAB308"


def format_money(value):
    try:
        value = float(value or 0)
    except Exception:
        value = 0
    return "$" + f"{value:,.0f}".replace(",", ".")


class InventoryLoadWorker(QThread):
    done = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self, repo, search=""):
        super().__init__()
        self.repo = repo
        self.search = search

    def run(self):
        try:
            self.done.emit(self.repo.get_all(self.search))
        except Exception as e:
            self.failed.emit(str(e))


class InventoryView(QWidget):
    def __init__(self, blur_on=None, blur_off=None, parent=None):
        super().__init__(parent)
        self.repo = InventoryRepository()
        self.blur_on = blur_on or (lambda: None)
        self.blur_off = blur_off or (lambda: None)
        self._rows = []
        self._worker = None
        self._selected_product = None
        self._hover_row = -1
        self._animations = []
        self._build_ui()
        self.table.viewport().installEventFilter(self)
        self._load()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(24)

        header_row = QHBoxLayout()
        header_left = QVBoxLayout()
        header_left.setSpacing(4)

        title = QLabel(tr("management.inventory.title"))
        title.setStyleSheet("""
            color: white;
            font-size: 32px;
            font-weight: 900;
            letter-spacing: -0.8px;
        """)
        subtitle = QLabel(tr("management.inventory.subtitle"))
        subtitle.setStyleSheet("""
            color: #666666;
            font-size: 14px;
            font-weight: 600;
        """)
        header_left.addWidget(title)
        header_left.addWidget(subtitle)

        self.btn_categories = QPushButton("＋ " + tr("management.category.new"))
        self.btn_categories.setFixedHeight(38)
        self.btn_categories.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_categories.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 9px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 900;
            }}
            QPushButton:hover {{
                border-color: {RED};
                color: white;
            }}
        """)
        self.btn_categories.clicked.connect(self._open_categories)

        self.btn_new = QPushButton("＋ " + tr("management.inventory.add_product"))
        self.btn_new.setFixedHeight(38)
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED};
                color: white;
                border: none;
                border-radius: 9px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 900;
            }}
            QPushButton:hover {{
                background-color: {RED_H};
            }}
        """)
        self.btn_new.clicked.connect(self._open_create)

        header_row.addLayout(header_left)
        header_row.addStretch()
        header_row.addWidget(self.btn_categories)
        header_row.addSpacing(8)
        header_row.addWidget(self.btn_new)
        root.addLayout(header_row)

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(16)
        self._kpi_total = self._make_kpi_card(tr("management.inventory.total_items"), "0", "#3B82F6")
        self._kpi_low = self._make_kpi_card(tr("management.inventory.low_stock"), "0", YELLOW)
        self._kpi_cats = self._make_kpi_card(tr("management.inventory.categories_count"), "0", "#8B5CF6")
        self._kpi_out = self._make_kpi_card(tr("management.inventory.no_stock"), "0", RED)
        kpi_row.addWidget(self._kpi_total)
        kpi_row.addWidget(self._kpi_low)
        kpi_row.addWidget(self._kpi_cats)
        kpi_row.addWidget(self._kpi_out)
        root.addLayout(kpi_row)

        table_card = QFrame()
        table_card.setObjectName("inventoryTableCard")
        table_card.setStyleSheet(f"""
            QFrame#inventoryTableCard {{
                background-color: {BG_CARD};
                border: 1px solid #303030;
                border-radius: 22px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(table_card)
        shadow.setBlurRadius(42)
        shadow.setOffset(0, 18)
        shadow.setColor(QColor(0, 0, 0, 210))
        table_card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(table_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            tr("management.inventory.product"),
            tr("management.inventory.status"),
            tr("management.inventory.stock"),
            tr("management.inventory.price"),
            tr("management.inventory.actions"),
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(False)
        self.table.setMouseTracking(True)
        self.table.viewport().setMouseTracking(True)
        self.table.setMinimumHeight(360)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_CARD};
                border: none;
                outline: none;
                color: {TEXT_PRI};
                gridline-color: transparent;
                selection-background-color: rgba(200,16,46,0.10);
                selection-color: white;
                font-size: 13px;
                border-radius: 22px;
            }}

            QHeaderView::section {{
                background-color: #1A1A1A;
                color: {TEXT_SEC};
                border: none;
                border-bottom: 1px solid #2A2A2A;
                padding: 18px;
                font-size: 10px;
                font-weight: 900;
                letter-spacing: 1.2px;
            }}

            QTableWidget::item {{
                border: none;
                border-bottom: 1px solid #252525;
                padding: 8px;
            }}

            QTableWidget::item:hover {{
                background-color: rgba(26,26,26,0.5);
            }}

            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: #333333;
                border-radius: 4px;
            }}
        """)
        self.table.cellClicked.connect(self._on_row_click)
        self.table.cellDoubleClicked.connect(self._on_row_double_click)

        card_layout.addWidget(self.table)
        root.addWidget(table_card, 1)

        self.lbl_empty = QLabel()
        self.lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 14px;
            padding: 40px;
        """)
        self.lbl_empty.hide()
        root.addWidget(self.lbl_empty)

    def _make_kpi_card(self, title, value, accent_color):
        card = QFrame()
        card.setFixedHeight(92)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-left: 4px solid {accent_color};
                border-radius: 16px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(6)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 900; letter-spacing: 0.5px;")
        layout.addWidget(lbl_title)

        lbl_value = QLabel(value)
        lbl_value.setStyleSheet("color: white; font-size: 26px; font-weight: 900;")
        layout.addWidget(lbl_value)

        return card

    def _update_kpi(self, rows):
        total_items = len(rows)
        low_stock = len([r for r in rows if 1 <= r["stock"] <= 10])
        categories = len(set(r.get("category_name") for r in rows if r.get("category_name")))
        out_stock = len([r for r in rows if r["stock"] <= 0])

        card = self._kpi_total
        card.layout().itemAt(1).widget().setText(str(total_items))
        card = self._kpi_low
        card.layout().itemAt(1).widget().setText(str(low_stock))
        card = self._kpi_cats
        card.layout().itemAt(1).widget().setText(str(categories))
        card = self._kpi_out
        card.layout().itemAt(1).widget().setText(str(out_stock))

    def _load(self):
        self._worker = InventoryLoadWorker(self.repo, "")
        self._worker.done.connect(self._on_loaded)
        self._worker.failed.connect(lambda e: self.lbl_empty.setText(f"Error: {e}"))
        self._worker.start()

    def _on_loaded(self, rows):
        self._selected_product = None
        self._hover_row = -1
        self._animations.clear()
        self._rows = rows
        self._update_kpi(rows)
        if not rows:
            self.table.hide()
            self.lbl_empty.show()
            self.lbl_empty.setText("📦\n\n" + tr("management.inventory.empty_title") + "\n" + tr("management.inventory.empty_subtitle"))
            return
        self.table.show()
        self.lbl_empty.hide()
        self._paint_table(rows)

    def _paint_table(self, rows):
        self.table.setRowCount(0)
        self.table.setRowCount(len(rows))

        for i, p in enumerate(rows):
            self.table.setCellWidget(i, 0, self._product_cell(p))
            self.table.setCellWidget(i, 1, self._status_cell(p))
            self.table.setCellWidget(i, 2, self._stock_cell(p))
            self.table.setCellWidget(i, 3, self._price_cell(p))
            self.table.setCellWidget(i, 4, self._actions_cell(p, visible=False))

            self.table.setRowHeight(i, 82)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)

        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 130)
        self.table.setColumnWidth(4, 170)

    def _product_cell(self, product):
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 8, 16, 8)
        layout.setSpacing(4)

        name = QLabel(str(product.get("name") or ""))
        name.setStyleSheet("""
            color: white;
            font-size: 15px;
            font-weight: 900;
            border: none;
            background: transparent;
        """)
        layout.addWidget(name)

        cat = product.get("category_name") or "Sin categoría"
        cat_lbl = QLabel(str(cat).upper())
        cat_lbl.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 11px;
            font-weight: 700;
            border: none;
            background: transparent;
        """)
        layout.addWidget(cat_lbl)

        return container

    def _status_cell(self, product):
        stock = product.get("stock", 0)
        if stock <= 0:
            text = tr("management.inventory.out_of_stock")
            bg = "rgba(200,16,46,0.10)"
            color = RED
            border_color = "rgba(200,16,46,0.25)"
        elif stock <= 10:
            text = tr("management.inventory.restock")
            bg = "rgba(234,179,8,0.10)"
            color = YELLOW
            border_color = "rgba(234,179,8,0.25)"
        else:
            text = tr("management.inventory.available")
            bg = "rgba(34,197,94,0.10)"
            color = GREEN
            border_color = "rgba(34,197,94,0.25)"

        badge = QLabel(text)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setMinimumWidth(104)
        badge.setFixedHeight(32)
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {color};
                border: 1px solid {border_color};
                border-radius: 7px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 900;
            }}
        """)

        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.addWidget(badge)
        layout.addStretch()

        return container

    def _stock_cell(self, product):
        stock = int(product.get("stock", 0) or 0)

        if stock <= 0:
            percent = 0
            bar_color = RED
            text_color = RED
        elif stock <= 10:
            percent = 25
            bar_color = YELLOW
            text_color = YELLOW
        elif stock <= 30:
            percent = 55
            bar_color = YELLOW
            text_color = TEXT_PRI
        else:
            percent = 80
            bar_color = GREEN
            text_color = TEXT_PRI

        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        bar_bg = QFrame()
        bar_bg.setFixedSize(70, 7)
        bar_bg.setStyleSheet("""
            QFrame {
                background-color: #1F1F1F;
                border-radius: 3px;
                border: none;
            }
        """)

        bar_fill = QFrame(bar_bg)
        bar_fill.setGeometry(0, 0, max(1, int(70 * percent / 100)), 7)
        bar_fill.setStyleSheet(f"""
            QFrame {{
                background-color: {bar_color};
                border-radius: 3px;
                border: none;
            }}
        """)

        stock_text = QLabel(f"{stock} und")
        stock_text.setStyleSheet(f"""
            color: {text_color};
            font-size: 12px;
            font-weight: 900;
            border: none;
            background: transparent;
        """)

        layout.addWidget(bar_bg)
        layout.addWidget(stock_text)
        layout.addStretch()

        return container

    def _price_cell(self, product):
        price = format_money(product.get("sale_price", 0))

        lbl = QLabel(price)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: 900;
            border: none;
            background: transparent;
        """)

        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.addStretch()
        layout.addWidget(lbl)
        layout.addStretch()

        return container

    def _actions_cell(self, product, visible=False):
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
        """)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 0, 16, 0)
        layout.setSpacing(8)
        layout.addStretch()

        if not visible:
            placeholder = QLabel("•••")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            placeholder.setStyleSheet(f"""
                color: {TEXT_MUT};
                font-size: 13px;
                font-weight: 900;
                background: transparent;
                border: none;
            """)
            layout.addWidget(placeholder)
            return container

        edit_btn = QPushButton(tr("management.inventory.edit"))
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setFixedHeight(30)
        edit_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #888888;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 900;
                padding: 4px 8px;
            }
            QPushButton:hover {
                color: white;
                background-color: #222222;
            }
        """)
        edit_btn.clicked.connect(lambda _, p=product: self._open_edit(p))

        delete_btn = QPushButton(tr("management.inventory.delete"))
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setFixedHeight(30)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {RED};
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 900;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                color: white;
                background-color: rgba(200,16,46,0.25);
            }}
        """)
        delete_btn.clicked.connect(lambda _, p=product: self._delete_product(p))

        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)

        effect = QGraphicsOpacityEffect(container)
        container.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(160)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        def cleanup():
            container.setGraphicsEffect(None)

        anim.finished.connect(cleanup)
        anim.start()
        self._animations.append(anim)

        return container

    def _set_hover_row(self, row):
        if row == self._hover_row:
            return

        old_row = self._hover_row
        self._hover_row = row

        if 0 <= old_row < len(self._rows):
            self.table.setCellWidget(
                old_row,
                4,
                self._actions_cell(self._rows[old_row], visible=False)
            )

        if 0 <= row < len(self._rows):
            self.table.setCellWidget(
                row,
                4,
                self._actions_cell(self._rows[row], visible=True)
            )

    def eventFilter(self, obj, event):
        if obj == self.table.viewport():
            if event.type() == QEvent.Type.MouseMove:
                row = self.table.rowAt(int(event.position().toPoint().y()))
                self._set_hover_row(row)
                return False

            if event.type() == QEvent.Type.Leave:
                pos = self.table.viewport().mapFromGlobal(QCursor.pos())
                if not self.table.viewport().rect().contains(pos):
                    self._set_hover_row(-1)
                return False

        return super().eventFilter(obj, event)

    def _on_row_click(self, row, col):
        if 0 <= row < len(self._rows):
            self._selected_product = self._rows[row]

    def _on_row_double_click(self, row, col):
        if 0 <= row < len(self._rows):
            product = self._rows[row]
            dlg = ProductDetailsDialog(self.repo, product, parent=self)
            self.blur_on()
            try:
                dlg.exec()
            finally:
                self.blur_off()

    def _open_categories(self):
        from repositories.inventory_category_repository import InventoryCategoryRepository
        cat_repo = InventoryCategoryRepository()
        dlg = InventoryCategoryDialog(repo=cat_repo, parent=self)
        self.blur_on()
        try:
            if dlg.exec():
                self._load()
        finally:
            self.blur_off()

    def _open_create(self):
        dlg = ProductDialog(repo=self.repo, product=None, parent=self)
        self.blur_on()
        try:
            if dlg.exec():
                self._load()
        finally:
            self.blur_off()

    def _open_edit(self, product):
        dlg = ProductDialog(repo=self.repo, product=product, parent=self)
        self.blur_on()
        try:
            if dlg.exec():
                self._load()
        finally:
            self.blur_off()

    def _delete_product(self, product):
        reply = QMessageBox.question(
            self,
            tr("management.inventory.delete_title"),
            tr("management.inventory.delete_confirm").format(name=product.get("name", "")),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete_product(product["id"])
                self._load()
            except Exception as e:
                QMessageBox.critical(self, tr("common.error"), str(e))
