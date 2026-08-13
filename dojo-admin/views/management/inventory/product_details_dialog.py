from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
import os

from core.i18n import tr

BG_DIALOG = "#111111"
BG_CARD   = "#161616"
BG_HOVER  = "#1A1A1A"
BORDER    = "#2A2A2A"
RED       = "#C8102E"
TEXT_PRI  = "#F0F0F0"
TEXT_SEC  = "#888888"
TEXT_MUT  = "#666666"
GREEN     = "#22C55E"
YELLOW    = "#EAB308"


class PurchaseHistoryWorker(QThread):
    done = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self, repo, product_id):
        super().__init__()
        self.repo = repo
        self.product_id = product_id

    def run(self):
        try:
            self.done.emit(self.repo.get_product_purchase_history(self.product_id))
        except Exception as e:
            self.failed.emit(str(e))


class ProductDetailsDialog(QDialog):
    def __init__(self, repo, product, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.product = product
        self.setWindowTitle(tr("management.product.details"))
        self.setMinimumSize(720, 520)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")
        self._build_ui()
        self._load_history()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(20)

        header = QFrame()
        header.setStyleSheet(f"background: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)

        img_frame = QFrame()
        img_frame.setFixedSize(140, 140)
        img_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        img_layout = QVBoxLayout(img_frame)
        img_layout.setContentsMargins(0, 0, 0, 0)
        img_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.img_label = QLabel()
        self.img_label.setFixedSize(120, 120)
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_path = self.product.get("image_path", "")
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(
                120, 120, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.img_label.setPixmap(pixmap)
            self.img_label.setStyleSheet("background: transparent; border: none;")
        else:
            self.img_label.setText(tr("management.product.no_image"))
            self.img_label.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; background: transparent; border: none;")
        img_layout.addWidget(self.img_label)

        header_layout.addWidget(img_frame)

        text_col = QVBoxLayout()
        text_col.setSpacing(4)

        title = QLabel(self.product["name"])
        title.setStyleSheet("color: white; font-size: 22px; font-weight: 900;")
        text_col.addWidget(title)

        cat_name = self.product.get("category_name", "")
        if cat_name:
            cat = QLabel(cat_name)
            cat.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px; font-weight: 600;")
            text_col.addWidget(cat)

        text_col.addStretch()
        header_layout.addLayout(text_col)
        root.addWidget(header)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)

        stats_row.addWidget(self._stat_card(
            tr("management.product.cost_price"),
            f"${self.product['cost_price']:,.0f}",
            TEXT_SEC
        ))
        stats_row.addWidget(self._stat_card(
            tr("management.product.sale_price"),
            f"${self.product['sale_price']:,.0f}",
            RED
        ))
        stats_row.addWidget(self._stat_card(
            tr("management.product.current_stock"),
            f"{self.product['stock']} und",
            GREEN if self.product['stock'] > 0 else RED
        ))

        cost = self.product["cost_price"]
        price = self.product["sale_price"]
        if cost > 0 and price > 0:
            margin_pct = ((price - cost) / cost) * 100
            margin_color = GREEN if margin_pct >= 0 else RED
            margin_text = f"{margin_pct:.1f}%"
        else:
            margin_color = TEXT_MUT
            margin_text = "—"
        stats_row.addWidget(self._stat_card(
            tr("management.product.margin"),
            margin_text,
            margin_color
        ))

        root.addLayout(stats_row)

        history_header = QLabel(tr("management.product.purchase_history"))
        history_header.setStyleSheet(f"color: {TEXT_PRI}; font-size: 15px; font-weight: 800;")
        root.addWidget(history_header)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            tr("management.product.buyer"),
            tr("management.product.purchase_date"),
            tr("management.product.quantity"),
            tr("management.product.total_price"),
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setStyleSheet(f"""
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
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        root.addWidget(self.table)

        self.lbl_no_history = QLabel(tr("management.product.no_purchases"))
        self.lbl_no_history.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_no_history.setStyleSheet(f"color: {TEXT_MUT}; font-size: 13px; padding: 20px;")
        self.lbl_no_history.hide()
        root.addWidget(self.lbl_no_history)

        btn_close = QPushButton(tr("close"))
        btn_close.setFixedHeight(38)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 9px;
                font-size: 13px; font-weight: 800;
            }}
            QPushButton:hover {{ border-color: {RED}; }}
        """)
        btn_close.clicked.connect(self.accept)
        root.addWidget(btn_close)

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

    def _load_history(self):
        self._worker = PurchaseHistoryWorker(self.repo, self.product["id"])
        self._worker.done.connect(self._on_loaded)
        self._worker.failed.connect(lambda e: self.lbl_no_history.setText(f"Error: {e}"))
        self._worker.start()

    def _on_loaded(self, rows):
        if not rows:
            self.table.hide()
            self.lbl_no_history.show()
            return
        self.table.show()
        self.lbl_no_history.hide()
        self.table.setRowCount(0)
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            date_str = str(r["purchase_date"]) if r["purchase_date"] else ""
            self.table.setItem(i, 0, QTableWidgetItem(r["buyer_name"]))
            self.table.setItem(i, 1, QTableWidgetItem(date_str))
            self.table.setItem(i, 2, QTableWidgetItem(str(r["quantity"])))
            self.table.setItem(i, 3, QTableWidgetItem(f"${r['total_price']:.2f}"))
            self.table.setRowHeight(i, 40)
