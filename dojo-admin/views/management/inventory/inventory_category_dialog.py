from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QScrollArea,
    QWidget, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

from core.i18n import tr

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


class InventoryCategoryDialog(QDialog):
    def __init__(self, repo, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.setWindowTitle(tr("management.category.manage"))
        self.setMinimumSize(620, 520)
        self.resize(680, 580)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")
        self._categories = []
        self._build_ui()
        self._load()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        title = QLabel(tr("management.inventory.categories.title"))
        title.setStyleSheet("color: white; font-size: 22px; font-weight: 900;")
        root.addWidget(title)

        subtitle = QLabel(tr("management.inventory.categories.subtitle"))
        subtitle.setStyleSheet(f"color: {TEXT_MUT}; font-size: 13px; font-weight: 600;")
        root.addWidget(subtitle)

        create_frame = QFrame()
        create_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        create_layout = QHBoxLayout(create_frame)
        create_layout.setContentsMargins(20, 14, 20, 14)
        create_layout.setSpacing(10)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText(tr("management.category.inventory.name_placeholder"))
        self.input_name.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 9px;
                padding: 0 12px; font-size: 13px; min-height: 38px;
            }}
            QLineEdit:focus {{ border-color: {RED}; }}
        """)
        create_layout.addWidget(self.input_name, 1)

        self.btn_create = QPushButton(tr("management.inventory.categories.new"))
        self.btn_create.setFixedHeight(38)
        self.btn_create.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_create.setStyleSheet(f"""
            QPushButton {{
                background: {RED}; color: white;
                border: none; border-radius: 9px;
                padding: 0 18px; font-size: 12px; font-weight: 700;
            }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        self.btn_create.clicked.connect(self._create_category)
        create_layout.addWidget(self.btn_create)

        root.addWidget(create_frame)

        existing_label = QLabel(tr("management.inventory.categories.existing"))
        existing_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;")
        root.addWidget(existing_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
            }
            QScrollBar::handle:vertical {
                background: #333333;
                border-radius: 4px;
            }
        """)
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.categories_layout = QVBoxLayout(scroll_content)
        self.categories_layout.setContentsMargins(0, 0, 0, 0)
        self.categories_layout.setSpacing(8)
        self.categories_layout.addStretch()

        scroll.setWidget(scroll_content)
        root.addWidget(scroll, 1)

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

    def _load(self):
        try:
            self._categories = self.repo.get_all_with_product_count()
            self._render()
        except Exception as e:
            QMessageBox.critical(self, tr("common.error"), str(e))

    def _render(self):
        while self.categories_layout.count() > 0:
            item = self.categories_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.categories_layout.addStretch()

        for cat in self._categories:
            row = self._make_row(cat)
            self.categories_layout.addWidget(row)

    def _make_row(self, cat):
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
            QFrame QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(8)

        name_lbl = QLabel(cat["name"])
        name_lbl.setStyleSheet("color: white; font-size: 14px; font-weight: 800;")
        layout.addWidget(name_lbl)

        count = cat.get("product_count", 0)
        count_text = f"{count} " + tr("management.inventory.categories.products_count") if count == 1 else f"{count} " + tr("management.inventory.categories.products_count").lower()
        count_lbl = QLabel(count_text)
        count_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; font-weight: 600;")
        layout.addWidget(count_lbl)

        layout.addStretch()

        delete_btn = QPushButton()
        if count > 0:
            delete_btn.setText(tr("management.inventory.categories.in_use"))
            delete_btn.setEnabled(False)
            delete_btn.setToolTip(tr("management.inventory.categories.cannot_delete"))
            delete_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {TEXT_MUT};
                    border: 1px solid {BORDER};
                    border-radius: 8px;
                    padding: 4px 12px;
                    font-size: 10px;
                    font-weight: 700;
                }}
            """)
        else:
            delete_btn.setText(tr("management.inventory.categories.delete"))
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {RED};
                    border: 1px solid {RED};
                    border-radius: 8px;
                    padding: 4px 12px;
                    font-size: 10px;
                    font-weight: 700;
                }}
                QPushButton:hover {{
                    background: rgba(200,16,46,0.15);
                }}
            """)
            delete_btn.clicked.connect(lambda _, c=cat: self._delete_category(c))

        layout.addWidget(delete_btn)
        return container

    def _create_category(self):
        name = self.input_name.text().strip()
        if not name:
            QMessageBox.warning(self, self.windowTitle(), tr("management.category.required"))
            return
        if len(name) < 2:
            QMessageBox.warning(self, self.windowTitle(), tr("management.category.too_short"))
            return

        try:
            self.repo.create(name)
            self.input_name.clear()
            self._load()
        except Exception as e:
            QMessageBox.critical(self, tr("common.error"), str(e))

    def _delete_category(self, cat):
        reply = QMessageBox.question(
            self,
            tr("management.inventory.categories.delete"),
            tr("confirm_delete").format(name=cat["name"]),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self.repo.delete(cat["id"])
            self._load()
        except ValueError as e:
            QMessageBox.warning(self, self.windowTitle(), str(e))
        except Exception as e:
            QMessageBox.critical(self, tr("common.error"), str(e))
