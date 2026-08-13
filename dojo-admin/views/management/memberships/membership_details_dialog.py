from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QScrollArea, QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

from core.i18n import tr


def calculate_discount(base_price, discount, discount_type):
    if discount_type == "amount":
        discount_amount = discount
    else:
        discount_amount = base_price * (discount / 100)
    discount_amount = max(0, min(discount_amount, base_price))
    final_price = max(0, base_price - discount_amount)
    return discount_amount, final_price


def format_money(value):
    try:
        value = float(value or 0)
    except Exception:
        value = 0
    return "$" + f"{value:,.0f}".replace(",", ".")

BG_DIALOG = "#111111"
BG_CARD   = "#161616"
BORDER    = "#2A2A2A"
RED       = "#C8102E"
TEXT_PRI  = "#F0F0F0"
TEXT_SEC  = "#888888"
TEXT_MUT  = "#666666"
GREEN     = "#22C55E"


class MembershipDetailsDialog(QDialog):
    def __init__(self, plan, parent=None):
        super().__init__(parent)
        self.plan = plan
        self.setWindowTitle(tr("management.memberships.details_title"))
        self.setMinimumSize(720, 620)
        self.resize(760, 680)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        content = QVBoxLayout(scroll_content)
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(20)

        header = QFrame()
        header.setStyleSheet("background: transparent;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)

        title = QLabel(self.plan["name"])
        title.setStyleSheet("color: white; font-size: 24px; font-weight: 900;")
        header_layout.addWidget(title)

        desc = self.plan.get("description", "")
        if desc:
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px; font-weight: 600;")
            desc_lbl.setWordWrap(True)
            header_layout.addWidget(desc_lbl)

        content.addWidget(header)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)

        pt = self.plan.get("plan_type", "individual")
        plan_type_label = tr("management.membership.individual_desc") if pt == "individual" else tr("management.membership.group_desc")
        stats_row.addWidget(self._stat_card(tr("management.membership.plan_type"), plan_type_label, TEXT_SEC))

        is_unlimited = self.plan.get("is_unlimited", False)
        if is_unlimited:
            classes_text = tr("management.membership.unlimited")
        else:
            classes_text = f"{self.plan.get('weekly_classes', 0)} " + tr("management.membership.classes_per_week")
        stats_row.addWidget(self._stat_card(tr("management.membership.weekly_classes"), classes_text, TEXT_SEC))

        discount_val = self.plan.get("discount", 0)
        discount_type = self.plan.get("discount_type", "percent")
        if discount_val > 0 and discount_type == "amount":
            discount_text = format_money(discount_val)
        elif discount_val > 0:
            discount_text = f"{discount_val:.0f}%"
        else:
            discount_text = "\u2014"
        stats_row.addWidget(self._stat_card(tr("management.membership.discount"), discount_text, GREEN if discount_val > 0 else TEXT_MUT))

        is_prepaid = self.plan.get("is_prepaid_months", False)
        prepaid_count = self.plan.get("prepaid_months_count", 1)
        if is_prepaid and pt == "individual":
            prepaid_text = f"{prepaid_count} " + tr("management.memberships.months")
            stats_row.addWidget(self._stat_card(tr("management.memberships.prepaid_badge"), prepaid_text, "#7E22CE"))

        content.addLayout(stats_row)

        price_card = QFrame()
        price_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(price_card)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 150))
        price_card.setGraphicsEffect(shadow)

        price_layout = QVBoxLayout(price_card)
        price_layout.setContentsMargins(20, 16, 20, 16)
        price_layout.setSpacing(8)

        monthly_fee = self.plan["monthly_fee"]
        discount = self.plan.get("discount", 0)
        discount_type = self.plan.get("discount_type", "percent")
        discount_amount, final_price = calculate_discount(monthly_fee, discount, discount_type)

        if discount > 0 and discount_type == "amount":
            discount_label = format_money(discount_amount)
        elif discount > 0:
            discount_label = f"{discount:.0f}%"
        else:
            discount_label = ""

        price_layout.addWidget(self._info_row(
            tr("management.membership.normal_value"),
            format_money(monthly_fee),
            TEXT_MUT
        ))
        if discount > 0:
            price_layout.addWidget(self._info_row(
                tr("management.membership.discount_amount"),
                f"-{discount_label}",
                GREEN
            ))
        price_layout.addWidget(self._info_row(
            tr("management.membership.discounted_value"),
            format_money(final_price),
            RED
        ))

        is_prepaid = self.plan.get("is_prepaid_months", False)
        prepaid_count = self.plan.get("prepaid_months_count", 1)
        if is_prepaid and pt == "individual":
            prepaid_total = final_price * prepaid_count
            price_layout.addWidget(self._separator())
            price_layout.addWidget(self._info_row(
                tr("management.memberships.prepaid_months"),
                str(prepaid_count),
                TEXT_PRI
            ))
            price_layout.addWidget(self._info_row(
                tr("management.memberships.prepaid_total"),
                format_money(prepaid_total),
                "#7E22CE"
            ))

        if pt == "group":
            group_cap = self.plan.get("group_capacity", 1)
            cap = max(group_cap, 1)
            normal_per_person = monthly_fee / cap
            final_per_person = final_price / cap
            discount_per_person = discount_amount / cap

            price_layout.addWidget(self._separator())

            group_header = QLabel(tr("management.memberships.group_summary"))
            group_header.setStyleSheet("color: white; font-size: 13px; font-weight: 900; border: none; background: transparent; margin-top: 6px;")
            price_layout.addWidget(group_header)

            price_layout.addLayout(self._detail_row(
                tr("management.memberships.group_capacity"),
                str(cap)
            ))
            price_layout.addLayout(self._detail_row(
                tr("management.memberships.normal_total"),
                format_money(monthly_fee)
            ))
            price_layout.addLayout(self._detail_row(
                tr("management.memberships.discounted_total"),
                format_money(final_price),
                RED
            ))
            price_layout.addWidget(self._separator())
            price_layout.addLayout(self._detail_row(
                tr("management.memberships.normal_per_person"),
                format_money(normal_per_person)
            ))
            price_layout.addLayout(self._detail_row(
                tr("management.memberships.discounted_per_person"),
                format_money(final_per_person),
                RED
            ))
            if discount > 0:
                price_layout.addLayout(self._detail_row(
                    tr("management.memberships.discount_per_person"),
                    f"-{format_money(discount_per_person)}",
                    GREEN
                ))

        content.addWidget(price_card)

        benefits = self.plan.get("benefits", "")
        if benefits:
            ben_header = QLabel(tr("management.membership.benefits"))
            ben_header.setStyleSheet("color: white; font-size: 14px; font-weight: 900;")
            content.addWidget(ben_header)

            benefits_box = QFrame()
            benefits_box.setObjectName("benefitsBox")
            benefits_box.setStyleSheet(f"""
                QFrame#benefitsBox {{
                    background-color: #161616;
                    border: 1px solid {BORDER};
                    border-radius: 14px;
                }}
                QFrame#benefitsBox QLabel {{
                    background: transparent;
                    border: none;
                }}
            """)
            ben_layout = QVBoxLayout(benefits_box)
            ben_layout.setContentsMargins(20, 16, 20, 16)
            ben_layout.setSpacing(8)
            lines = benefits.splitlines()
            any_benefit = False
            for line in lines:
                if line.strip():
                    any_benefit = True
                    blbl = QLabel("\u2713 " + line.strip())
                    blbl.setWordWrap(True)
                    blbl.setStyleSheet("""
                        color: #D1D5DB;
                        font-size: 13px;
                        font-weight: 700;
                        padding: 2px 0;
                        border: none;
                        background: transparent;
                    """)
                    ben_layout.addWidget(blbl)
            if not any_benefit:
                no_ben = QLabel(tr("management.membership.no_benefits"))
                no_ben.setStyleSheet(f"color: {TEXT_MUT}; font-size: 13px;")
                ben_layout.addWidget(no_ben)
            content.addWidget(benefits_box)
        else:
            no_ben = QLabel(tr("management.membership.no_benefits"))
            no_ben.setStyleSheet(f"color: {TEXT_MUT}; font-size: 13px; padding: 8px 0;")
            content.addWidget(no_ben)

        content.addStretch()
        scroll.setWidget(scroll_content)
        root.addWidget(scroll)

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
        card.setMinimumHeight(90)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        lbl_label = QLabel(label)
        lbl_label.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 900; border: none; background: transparent;")
        layout.addWidget(lbl_label)

        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: 900; border: none; background: transparent;")
        layout.addWidget(lbl_value)

        return card

    def _info_row(self, label, value, value_color=TEXT_PRI):
        row = QHBoxLayout()
        row.setSpacing(8)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        val = QLabel(value)
        val.setStyleSheet(f"color: {value_color}; font-size: 14px; font-weight: 700; border: none; background: transparent;")
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(val)
        container = QFrame()
        container.setLayout(row)
        container.setStyleSheet("background: transparent; border: none;")
        return container

    def _detail_row(self, label_text, value_text, value_color="#F0F0F0"):
        row = QHBoxLayout()
        row.setSpacing(8)

        label = QLabel(label_text)
        label.setStyleSheet("""
            color: #888888;
            font-size: 13px;
            font-weight: 800;
            border: none;
            background: transparent;
        """)

        value = QLabel(value_text)
        value.setStyleSheet(f"""
            color: {value_color};
            font-size: 14px;
            font-weight: 900;
            border: none;
            background: transparent;
        """)

        row.addWidget(label)
        row.addStretch()
        row.addWidget(value)
        return row

    def _separator(self):
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {BORDER}; border: none;")
        return sep
