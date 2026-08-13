from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QScrollArea, QGridLayout,
    QGraphicsDropShadowEffect, QSizePolicy,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor

from core.i18n import tr
from repositories.services_repository import ServicesRepository
from views.management.services.service_dialog import ServiceDialog

BG_MAIN  = "#0D0D0D"
BG_CARD  = "#161616"
BG_HOVER = "#1A1A1A"
BORDER   = "#2A2A2A"
RED      = "#C8102E"
TEXT_PRI = "#F0F0F0"
TEXT_SEC = "#888888"
TEXT_MUT = "#666666"


def format_money(value):
    try:
        value = float(value or 0)
    except Exception:
        value = 0
    return "$" + f"{value:,.0f}".replace(",", ".")


class ServicesLoadWorker(QThread):
    done = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self, repo):
        super().__init__()
        self.repo = repo

    def run(self):
        try:
            self.done.emit(self.repo.get_all())
        except Exception as e:
            self.failed.emit(str(e))


class ServicesView(QWidget):
    def __init__(self, blur_on=None, blur_off=None, parent=None):
        super().__init__(parent)
        self.repo = ServicesRepository()
        self.blur_on = blur_on or (lambda: None)
        self.blur_off = blur_off or (lambda: None)
        self._rows = []
        self._animations = []
        self._build_ui()
        self._load()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(24)

        header_row = QHBoxLayout()
        header_left = QVBoxLayout()
        header_left.setSpacing(4)

        title = QLabel(tr("management.services.title"))
        title.setStyleSheet("""
            color: white;
            font-size: 32px;
            font-weight: 900;
            letter-spacing: -0.8px;
        """)
        subtitle = QLabel(tr("management.services.subtitle"))
        subtitle.setStyleSheet("""
            color: #666666;
            font-size: 14px;
            font-weight: 600;
        """)
        header_left.addWidget(title)
        header_left.addWidget(subtitle)

        self.btn_new = QPushButton("＋ " + tr("management.services.new_service"))
        self.btn_new.setFixedHeight(42)
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 0 22px;
                font-size: 13px;
                font-weight: 900;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        self.btn_new.clicked.connect(self._open_create)

        header_row.addLayout(header_left)
        header_row.addStretch()
        header_row.addWidget(self.btn_new)
        root.addLayout(header_row)

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
        self.cards_layout = QGridLayout(scroll_content)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(20)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        scroll.setWidget(scroll_content)
        root.addWidget(scroll, 1)

        self.lbl_empty = QLabel()
        self.lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 14px;
            padding: 40px;
        """)
        self.lbl_empty.hide()
        root.addWidget(self.lbl_empty)

    def _load(self):
        self._worker = ServicesLoadWorker(self.repo)
        self._worker.done.connect(self._on_loaded)
        self._worker.failed.connect(lambda e: self.lbl_empty.setText(f"Error: {e}"))
        self._worker.start()

    def _on_loaded(self, rows):
        self._rows = rows
        if not rows:
            self.lbl_empty.show()
            self.lbl_empty.setText("🚀\n\n" + tr("management.services.empty_title") + "\n" + tr("management.services.empty_subtitle"))
            self._clear_cards()
            return
        self.lbl_empty.hide()
        self._render_cards(rows)

    def _clear_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _render_cards(self, rows):
        self._clear_cards()
        cols = 3
        for i, svc in enumerate(rows):
            card = self._make_card(svc)
            row = i // cols
            col = i % cols
            self.cards_layout.addWidget(card, row, col)

    def _make_card(self, svc):
        accent = svc.get("accent_color", "#3B82F6")
        name = svc.get("name", "")
        desc = svc.get("description", "")
        price = format_money(svc.get("price", 0))
        icon = svc.get("icon", "🚀")

        card = QFrame()
        card.setObjectName("serviceCard")
        card.setMinimumSize(280, 190)
        card.setMaximumWidth(340)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame#serviceCard {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-top: 4px solid {accent};
                border-radius: 20px;
            }}
            QFrame#serviceCard QLabel {{
                background: transparent;
                border: none;
            }}
            QFrame#serviceCard:hover {{
                border-top-color: white;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 160))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(6)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 28px;")
        layout.addWidget(icon_lbl)

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("color: white; font-size: 16px; font-weight: 900;")
        layout.addWidget(name_lbl)

        if desc:
            desc_lbl = QLabel(desc)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px;")
            layout.addWidget(desc_lbl)

        layout.addStretch()

        bottom = QHBoxLayout()
        bottom.setSpacing(8)
        price_lbl = QLabel(price)
        price_lbl.setStyleSheet("color: white; font-size: 18px; font-weight: 900;")
        bottom.addWidget(price_lbl)
        bottom.addStretch()

        edit_btn = QPushButton(tr("management.services.edit_service"))
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #1A1A1A;
                color: {accent};
                border: none;
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 10px;
                font-weight: 900;
            }}
            QPushButton:hover {{
                background-color: #222222;
                color: white;
            }}
        """)
        edit_btn.clicked.connect(lambda _, s=svc: self._open_edit(s))
        bottom.addWidget(edit_btn)

        delete_btn = QPushButton(tr("management.services.delete_service"))
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(200, 16, 46, 0.10);
                color: {RED};
                border: 1px solid rgba(200, 16, 46, 0.35);
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 10px;
                font-weight: 900;
            }}
            QPushButton:hover {{
                background-color: rgba(200, 16, 46, 0.18);
                color: white;
                border-color: {RED};
            }}
        """)
        delete_btn.clicked.connect(lambda _, s=svc: self._delete_service(s))
        bottom.addWidget(delete_btn)

        layout.addLayout(bottom)

        card.mouseDoubleClickEvent = lambda e, s=svc: self._open_edit(s)

        return card

    def _delete_service(self, service):
        service_name = service.get("name", "")

        reply = QMessageBox.question(
            self,
            tr("management.services.delete_title"),
            tr("management.services.delete_confirm").format(name=service_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self.repo.delete_service(service["id"])
            self._load()
        except Exception as e:
            QMessageBox.critical(self, tr("common.error"), str(e))

    def _open_create(self):
        dlg = ServiceDialog(repo=self.repo, service=None, parent=self)
        self.blur_on()
        try:
            if dlg.exec():
                self._load()
        finally:
            self.blur_off()

    def _open_edit(self, service):
        dlg = ServiceDialog(repo=self.repo, service=service, parent=self)
        self.blur_on()
        try:
            if dlg.exec():
                self._load()
        finally:
            self.blur_off()
