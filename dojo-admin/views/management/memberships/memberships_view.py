from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QScrollArea, QGridLayout,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

from core.i18n import tr, trf
from repositories.memberships_repository import MembershipsRepository
from views.management.memberships.membership_plan_dialog import MembershipPlanDialog
from views.management.memberships.membership_details_dialog import MembershipDetailsDialog

BG_MAIN  = "#0D0D0D"
BG_CARD  = "#171717"
BG_HOVER = "#1A1A1A"
BORDER   = "#2A2A2A"
RED      = "#C8102E"
RED_H    = "#E8152F"
TEXT_PRI = "#F0F0F0"
TEXT_SEC = "#888888"
TEXT_MUT = "#666666"

SELECTED_BORDER = RED


def format_money(value):
    try:
        value = float(value or 0)
    except Exception:
        value = 0
    return "$" + f"{value:,.0f}".replace(",", ".")


def calculate_discount(base_price, discount, discount_type):
    if discount_type == "amount":
        discount_amount = discount
    else:
        discount_amount = base_price * (discount / 100)
    discount_amount = max(0, min(discount_amount, base_price))
    final_price = max(0, base_price - discount_amount)
    return discount_amount, final_price


class MembershipsLoadWorker(QThread):
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


class MembershipCard(QFrame):
    clicked = pyqtSignal(dict)
    double_clicked = pyqtSignal(dict)

    def __init__(self, plan, selected=False, parent=None):
        super().__init__(parent)
        self.plan = plan
        self.selected = selected
        self._hovered = False

        self.setObjectName("membershipCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(300, 330)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self._build_ui()
        self._apply_style()

    def _apply_style(self):
        if self.selected:
            bg = "#2A0A0C"
            border = RED
        elif self._hovered:
            bg = "#1D1D1D"
            border = "#444444"
        else:
            bg = "#171717"
            border = BORDER

        self.setStyleSheet(f"""
            QFrame#membershipCard {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 18px;
            }}
            QFrame#membershipCard QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32 if self.selected else 24)
        shadow.setOffset(0, 12)
        shadow.setColor(QColor(200, 16, 46, 80) if self.selected else QColor(0, 0, 0, 170))
        self.setGraphicsEffect(shadow)

    def enterEvent(self, event):
        self._hovered = True
        if not self.selected:
            self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._apply_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.plan)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.plan)
        super().mouseDoubleClickEvent(event)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(10)

        name = QLabel(str(self.plan.get("name") or "Plan"))
        name.setWordWrap(True)
        name.setStyleSheet("color: white; font-size: 24px; font-weight: 900; letter-spacing: -0.5px;")
        layout.addWidget(name)

        desc = str(self.plan.get("description") or "").strip()
        desc_lbl = QLabel(desc if desc else "Plan de membresía")
        desc_lbl.setWordWrap(True)
        desc_lbl.setMaximumHeight(44)
        desc_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px; font-weight: 700;")
        layout.addWidget(desc_lbl)

        layout.addStretch()

        monthly_fee = self.plan.get("monthly_fee", 0)
        discount = self.plan.get("discount", 0) or 0
        discount_type = self.plan.get("discount_type", "percent") or "percent"
        discount_amount, final_price = calculate_discount(monthly_fee, discount, discount_type)

        if discount_amount > 0:
            old_price = QLabel(f"Antes {format_money(monthly_fee)}/mes")
            old_price.setStyleSheet(f"color: {TEXT_MUT}; font-size: 13px; font-weight: 800;")
            layout.addWidget(old_price)

            price = QLabel(f"{format_money(final_price)}")
            price.setStyleSheet("color: white; font-size: 31px; font-weight: 950; letter-spacing: -1px;")
            layout.addWidget(price)

            per_month = QLabel("/mes")
            per_month.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px; font-weight: 800;")
            layout.addWidget(per_month)

            if discount_type == "amount":
                discount_text = f"{format_money(discount_amount)} descuento"
            else:
                discount_text = f"{discount:.0f}% descuento"
            discount_lbl = QLabel(discount_text)
            discount_lbl.setStyleSheet("color: #22C55E; font-size: 12px; font-weight: 900;")
            layout.addWidget(discount_lbl)
        else:
            price = QLabel(format_money(monthly_fee))
            price.setStyleSheet("color: white; font-size: 34px; font-weight: 950; letter-spacing: -1px;")
            layout.addWidget(price)

            per_month = QLabel("/mes")
            per_month.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px; font-weight: 800;")
            layout.addWidget(per_month)

        layout.addSpacing(8)

        plan_type = self.plan.get("plan_type", "individual")
        unlimited = self.plan.get("is_unlimited", False)
        if plan_type == "group":
            type_text = tr("management.membership.group") + " · " + tr("management.membership.unlimited")
        elif unlimited:
            type_text = tr("management.membership.individual") + " · " + tr("management.membership.unlimited")
        else:
            wc = self.plan.get("weekly_classes", 0)
            type_text = tr("management.membership.individual") + f" · {wc} " + tr("management.membership.classes_per_week")

        type_lbl = QLabel(type_text)
        type_lbl.setWordWrap(True)
        type_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-weight: 800;")
        layout.addWidget(type_lbl)

        is_prepaid = self.plan.get("is_prepaid_months", False)
        prepaid_count = self.plan.get("prepaid_months_count", 1)
        if is_prepaid and self.plan.get("plan_type", "individual") == "individual":
            prepaid_lbl = QLabel(trf("management.memberships.prepaid_badge", "ADELANTADA · {months} MESES", months=prepaid_count))
            prepaid_lbl.setStyleSheet(f"""
                color: #7E22CE;
                font-size: 11px;
                font-weight: 900;
                background: rgba(126, 34, 206, 0.12);
                border: 1px solid rgba(126, 34, 206, 0.3);
                border-radius: 6px;
                padding: 2px 10px;
            """)
            layout.addWidget(prepaid_lbl)

        benefits = str(self.plan.get("benefits") or "").splitlines()
        clean_benefits = [b.strip() for b in benefits if b.strip()]
        if clean_benefits:
            benefit_lbl = QLabel("✦ " + clean_benefits[0])
            benefit_lbl.setWordWrap(True)
            benefit_lbl.setMaximumHeight(36)
            benefit_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; font-weight: 700;")
            layout.addWidget(benefit_lbl)


class MembershipsView(QWidget):
    def __init__(self, blur_on=None, blur_off=None, parent=None):
        super().__init__(parent)
        self.repo = MembershipsRepository()
        self.blur_on = blur_on or (lambda: None)
        self.blur_off = blur_off or (lambda: None)
        self._rows = []
        self._selected_id = None
        self._build_ui()
        self._load()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(28)

        header_row = QHBoxLayout()
        header_left = QVBoxLayout()
        header_left.setSpacing(4)

        title = QLabel(tr("management.memberships.title"))
        title.setStyleSheet("color: white; font-size: 25px; font-weight: 900;")
        subtitle = QLabel(tr("management.memberships.subtitle"))
        subtitle.setStyleSheet("color: #666666; font-size: 14px; font-weight: 600;")
        header_left.addWidget(title)
        header_left.addWidget(subtitle)

        self.btn_new = QPushButton("＋ " + tr("management.memberships.create_plan"))
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

        self.btn_edit = QPushButton("✎ " + tr("management.memberships.edit_plan"))
        self.btn_edit.setFixedHeight(38)
        self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit.setEnabled(False)
        self.btn_edit.setStyleSheet(f"""
            QPushButton {{
                background-color: #1A1A1A;
                color: white;
                border: 1px solid #333333;
                border-radius: 9px;
                padding: 0 16px;
                min-height: 38px;
                font-size: 12px;
                font-weight: 900;
            }}
            QPushButton:hover {{
                border-color: {RED};
                background-color: #222222;
            }}
            QPushButton:disabled {{
                color: #555555;
                border-color: #222222;
                background-color: #141414;
            }}
        """)
        self.btn_edit.clicked.connect(self._open_edit_selected)

        self.btn_delete = QPushButton("🗑 " + tr("management.memberships.delete_plan"))
        self.btn_delete.setFixedHeight(38)
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setEnabled(False)
        self.btn_delete.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {RED};
                border: 1px solid rgba(200,16,46,0.35);
                border-radius: 9px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 900;
            }}
            QPushButton:hover {{
                background-color: rgba(200,16,46,0.12);
                border-color: {RED};
            }}
            QPushButton:disabled {{
                color: #4A4A4A;
                border-color: #222222;
                background-color: #141414;
            }}
        """)
        self.btn_delete.clicked.connect(self._delete_selected)

        header_row.addLayout(header_left)
        header_row.addStretch()
        header_row.addWidget(self.btn_edit)
        header_row.addSpacing(8)
        header_row.addWidget(self.btn_delete)
        header_row.addSpacing(8)
        header_row.addWidget(self.btn_new)
        root.addLayout(header_row)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"""
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
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: #333333;
                border-radius: 3px;
                min-height: 26px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #555555;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                background: none;
                border: none;
            }}
        """)

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_grid = QGridLayout(self.cards_container)
        self.cards_grid.setContentsMargins(0, 12, 0, 32)
        self.cards_grid.setHorizontalSpacing(26)
        self.cards_grid.setVerticalSpacing(26)
        self.cards_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.scroll.setWidget(self.cards_container)
        root.addWidget(self.scroll)

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
        self._worker = MembershipsLoadWorker(self.repo)
        self._worker.done.connect(self._on_loaded)
        self._worker.failed.connect(self._on_load_failed)
        self._worker.start()

    def _on_loaded(self, rows):
        self._selected_id = None
        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self._rows = rows or []
        if not self._rows:
            self.scroll.hide()
            self.lbl_empty.show()
            self.lbl_empty.setText("💳\n\n" + tr("management.memberships.empty_title") + "\n" + tr("management.memberships.empty_subtitle"))
            return
        self.lbl_empty.hide()
        self.scroll.show()
        self._paint_cards(self._rows)

    def _on_load_failed(self, error: str):
        self._rows = []
        self._selected_id = None
        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.scroll.hide()
        self.lbl_empty.show()
        self.lbl_empty.setText(
            "⚠️\n\n"
            + tr("common.error")
            + "\n"
            + str(error)
        )

    def _paint_cards(self, rows):
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, plan in enumerate(rows):
            card = self._make_card(plan)
            row = i // 3
            col = i % 3
            self.cards_grid.addWidget(card, row, col)

        self.cards_grid.setColumnStretch(0, 0)
        self.cards_grid.setColumnStretch(1, 0)
        self.cards_grid.setColumnStretch(2, 0)
        self.cards_grid.setColumnStretch(3, 1)

    def _make_card(self, plan):
        card = MembershipCard(
            plan=plan,
            selected=self._selected_id == plan.get("id"),
            parent=self
        )
        card.clicked.connect(self._on_card_click)
        card.double_clicked.connect(self._on_card_double_click)
        return card

    def _on_card_click(self, plan):
        if plan.get("id") != self._selected_id:
            self._selected_id = plan["id"]
            self.btn_edit.setEnabled(True)
            self.btn_delete.setEnabled(True)
            self._paint_cards(self._rows)
        else:
            self._selected_id = plan["id"]
            self.btn_edit.setEnabled(True)
            self.btn_delete.setEnabled(True)

    def _on_card_double_click(self, plan):
        dlg = MembershipDetailsDialog(plan, parent=self)
        self.blur_on()
        try:
            dlg.exec()
        finally:
            self.blur_off()

    def _open_create(self):
        dlg = MembershipPlanDialog(repo=self.repo, plan=None, parent=self)
        self.blur_on()
        try:
            if dlg.exec():
                self._load()
        finally:
            self.blur_off()

    def _open_edit(self, plan):
        dlg = MembershipPlanDialog(repo=self.repo, plan=plan, parent=self)
        self.blur_on()
        try:
            if dlg.exec():
                self._load()
        finally:
            self.blur_off()

    def _open_edit_selected(self):
        plan = next((p for p in self._rows if p["id"] == self._selected_id), None)
        if plan:
            self._open_edit(plan)

    def _delete_selected(self):
        plan = next((p for p in self._rows if p["id"] == self._selected_id), None)
        if not plan:
            return

        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            tr("management.memberships.delete_title"),
            tr("management.memberships.delete_confirm").format(name=plan.get("name", "")),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self.repo.delete_plan(plan["id"])
            self._selected_id = None
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self._load()
        except Exception as e:
            QMessageBox.critical(self, tr("common.error"), str(e))
