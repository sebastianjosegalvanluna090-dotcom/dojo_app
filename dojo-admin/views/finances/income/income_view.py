from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QTableWidget,
    QGraphicsOpacityEffect, QGraphicsDropShadowEffect,
    QScrollArea, QMenu, QDialog,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtProperty, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt6.QtGui import QColor, QCursor, QPainter
from datetime import datetime

from core.i18n import tr, trf
from core.debug import debug_log
from repositories.finances_income_repository import FinancesIncomeRepository
from views.finances.income.income_dialog import IncomeDialog
from views.finances.income.income_details_dialog import IncomeDetailsDialog

BG_DEEP  = "#050505"
BG_SIDE  = "#0D0D0D"
BG_CARD  = "#161616"
BG_HOVER = "#1E1E1E"
BORDER   = "#2A2A2A"
RED      = "#C8102E"
RED_H    = "#E8152F"
GREEN    = "#22C55E"
YELLOW   = "#EAB308"
BLUE     = "#3B82F6"
TEXT_PRI = "#F0F0F0"
TEXT_SEC = "#9CA3AF"
TEXT_MUT = "#6B7280"


def format_money(value):
    try:
        value = float(value or 0)
    except Exception:
        value = 0
    return "$" + f"{value:,.0f}".replace(",", ".")


class IncomeLoadWorker(QThread):
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


class FilterPill(QPushButton):
    def __init__(self, label: str, active: bool = False, parent=None):
        super().__init__(label, parent)
        self._active = active
        self.setFixedHeight(34)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(False)
        self._apply_style()

    def set_active(self, active: bool):
        self._active = active
        self._apply_style()

    def _apply_style(self):
        if self._active:
            self.setStyleSheet("""
                QPushButton {
                    background: #FFFFFF;
                    color: #050505;
                    border: none;
                    border-radius: 17px;
                    font-size: 13px;
                    font-weight: 700;
                    font-family: 'Inter';
                    padding: 0 18px;
                }
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: #161616;
                    color: {TEXT_MUT};
                    border: 1px solid {BORDER};
                    border-radius: 17px;
                    font-size: 13px;
                    font-weight: 600;
                    font-family: 'Inter';
                    padding: 0 18px;
                }}
                QPushButton:hover {{
                    background: {BG_HOVER};
                    color: {TEXT_SEC};
                }}
            """)


class RotatingMoreButton(QPushButton):
    def __init__(self, text="•••", parent=None):
        super().__init__("", parent)
        self._text = text
        self._angle = 0
        self._anim = QPropertyAnimation(self, b"angle", self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.setFixedSize(28, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_MUT};
                border: none;
                border-radius: 14px;
            }}
            QPushButton:hover {{
                background: {BG_HOVER};
                color: {TEXT_SEC};
            }}
        """)

    def getAngle(self):
        return self._angle

    def setAngle(self, value):
        self._angle = value
        self.update()

    angle = pyqtProperty(float, fget=getAngle, fset=setAngle)

    def enterEvent(self, event):
        self._anim.stop()
        self._anim.setStartValue(self._angle)
        self._anim.setEndValue(90)
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._anim.stop()
        self._anim.setStartValue(self._angle)
        self._anim.setEndValue(0)
        self._anim.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self._angle)
        painter.translate(-self.width() / 2, -self.height() / 2)
        painter.setPen(QColor(TEXT_SEC))
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._text)


class IncomeCard(QFrame):
    clicked = pyqtSignal(dict)
    doubleClicked = pyqtSignal(dict)
    menuRequested = pyqtSignal(object, object)

    _STATUS_MAP = {
        "paid":      ("completed", "#22C55E", "#22C55E"),
        "partial":   ("processing", "#3B82F6", "#3B82F6"),
        "pending":   ("pending",   "#EAB308", "#EAB308"),
        "cancelled": ("cancelled", "#6B7280", "#6B7280"),
    }

    def __init__(self, income: dict, selected: bool = False, parent=None):
        super().__init__(parent)
        self.income = income
        self._selected = selected
        self._hovered = False
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(14)
        self._shadow.setOffset(0, 4)
        self._shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(self._shadow)
        self._build()
        self._apply_style()

    def _build(self):
        self.setFixedHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        hl = QHBoxLayout(self)
        hl.setContentsMargins(16, 0, 16, 0)
        hl.setSpacing(14)

        payer_type = self.income.get("payer_type", "third_party")
        payer_name = str(self.income.get("payer_name") or "")

        student_names = (
            self.income.get("student_names")
            or self.income.get("student_display_name")
            or self.income.get("student_name")
            or ""
        )

        if payer_type == "guardian" and student_names:
            title_name = payer_name
            avatar_name = student_names
            subtitle_person = student_names
        else:
            title_name = payer_name
            avatar_name = payer_name
            subtitle_person = ""

        initials = "".join(w[0].upper() for w in avatar_name.split()[:2]) or "?"
        status = self.income.get("status", "pending")

        avatar = QLabel(initials)
        avatar.setFixedSize(48, 48)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if status == "paid":
            av_style = "background: #052E16; color: #22C55E;"
        elif status == "partial":
            av_style = "background: #0C1A4E; color: #3B82F6;"
        else:
            av_style = "background: #1C1A0E; color: #EAB308;"
        avatar.setStyleSheet(f"""
            QLabel {{
                {av_style}
                border-radius: 24px;
                font-size: 14px;
                font-weight: 800;
                font-family: 'Inter';
                border: none;
            }}
        """)
        hl.addWidget(avatar)

        info_col = QVBoxLayout()
        info_col.setSpacing(3)
        info_col.setContentsMargins(0, 0, 0, 0)

        self.name_lbl = QLabel(title_name or "\u2014")
        self.name_lbl.setStyleSheet("""
            color: #E5E5E5; font-size: 14px; font-weight: 700;
            font-family: 'Inter'; border: none; background: transparent;
        """)

        type_map = {"student": "Student", "guardian": "Guardian",
                    "third_party": "Third Party"}
        type_str = type_map.get(payer_type, payer_type)
        date_val = self.income.get("income_date", "")
        if date_val and hasattr(date_val, "strftime"):
            date_str = date_val.strftime("%b %d, %Y")
        else:
            date_str = str(date_val)[:10] if date_val else "\u2014"
        if payer_type == "guardian" and subtitle_person:
            sub_text = f"{subtitle_person} • {type_str} • {date_str}"
        else:
            sub_text = f"{type_str} • {date_str}"

        self.sub_lbl = QLabel(sub_text)
        self.sub_lbl.setStyleSheet("""
            color: #6B7280; font-size: 11px; font-weight: 500;
            font-family: 'Inter'; border: none; background: transparent;
        """)

        info_col.addWidget(self.name_lbl)
        info_col.addWidget(self.sub_lbl)
        hl.addLayout(info_col, 1)

        right_col = QVBoxLayout()
        right_col.setSpacing(4)
        right_col.setAlignment(Qt.AlignmentFlag.AlignRight |
                               Qt.AlignmentFlag.AlignVCenter)

        total = float(self.income.get("total", 0) or 0)
        self.amount_lbl = QLabel(f"+${total:,.2f}")
        self.amount_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.amount_lbl.setStyleSheet("""
            color: #22C55E; font-size: 14px; font-weight: 700;
            font-family: 'Inter'; border: none; background: transparent;
        """)

        status_label, status_color, _ = self._STATUS_MAP.get(
            status, ("pending", "#EAB308", "#EAB308"))
        icon = "\u2713" if status == "paid" else "\u25F7"
        self.status_lbl = QLabel(f"{icon} {status_label.upper()}")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.status_lbl.setStyleSheet(f"""
            color: {status_color}; font-size: 10px; font-weight: 700;
            font-family: 'Inter'; letter-spacing: 0.5px;
            border: none; background: transparent;
        """)

        right_col.addWidget(self.amount_lbl)
        right_col.addWidget(self.status_lbl)
        hl.addLayout(right_col)

        self.more_btn = RotatingMoreButton("•••")
        self.more_btn.clicked.connect(self._emit_menu)
        hl.addWidget(self.more_btn)

    def _emit_menu(self):
        self.menuRequested.emit(self.income, self.mapToGlobal(QPoint(
            self.more_btn.pos().x() + self.more_btn.width(),
            self.more_btn.pos().y() + self.more_btn.height()
        )))

    def _apply_style(self):
        if self._selected:
            self.setStyleSheet(f"""
                QFrame {{
                    background: {BG_HOVER};
                    border: 1px solid rgba(255,255,255,0.2);
                    border-radius: 16px;
                }}
            """)
            self._shadow.setBlurRadius(20)
            self._shadow.setOffset(0, 4)
            self._shadow.setColor(QColor(0, 0, 0, 120))
        else:
            blur = 24 if self._hovered else 14
            off = 8 if self._hovered else 4
            self._shadow.setBlurRadius(blur)
            self._shadow.setOffset(0, off)
            self._shadow.setColor(QColor(0, 0, 0, 140 if self._hovered else 100))
            self.setStyleSheet(f"""
                QFrame {{
                    background: {BG_CARD};
                    border: 1px solid {BORDER};
                    border-radius: 16px;
                }}
                QFrame:hover {{
                    background: {BG_HOVER};
                    border: 1px solid rgba(255,255,255,0.1);
                }}
            """)

    def set_selected(self, selected: bool):
        self._selected = selected
        self._apply_style()

    def mousePressEvent(self, event):
        self.clicked.emit(self.income)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit(self.income)
        super().mouseDoubleClickEvent(event)

    def enterEvent(self, event):
        self._hovered = True
        self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._apply_style()
        super().leaveEvent(event)


class IncomeView(QWidget):
    def __init__(self, blur_on=None, blur_off=None, parent=None):
        super().__init__(parent)
        self.repo = FinancesIncomeRepository()
        self.blur_on = blur_on or (lambda: None)
        self.blur_off = blur_off or (lambda: None)
        self._rows = []
        self._worker = None
        self._selected_income = None
        self._card_widgets = []
        self._active_filter = "all"
        self._animations = []
        self._income_dialog_open = False
        self._build_ui()
        self._load()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
        """)

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        root = QVBoxLayout(inner)
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(20)

        header_row = QHBoxLayout()
        header_left = QVBoxLayout()
        header_left.setSpacing(4)

        title = QLabel(trf("finances.income.title", "Income"))
        title.setStyleSheet("""
            color: white; font-size: 26px; font-weight: 800;
            font-family: 'Inter'; letter-spacing: -0.5px;
        """)
        subtitle = QLabel(trf("finances.income.subtitle", "Payments received, agreements and credits to the dojo"))
        subtitle.setStyleSheet(f"""
            color: {TEXT_MUT}; font-size: 12px; font-weight: 500;
            font-family: 'Inter';
        """)
        header_left.addWidget(title)
        header_left.addWidget(subtitle)
        header_row.addLayout(header_left)
        header_row.addStretch()
        root.addLayout(header_row)

        self._active_filter = "all"
        pills_row = QHBoxLayout()
        pills_row.setSpacing(8)
        pills_row.setContentsMargins(0, 0, 0, 0)

        self._pill_all = FilterPill(tr("finances.income.filter.all"), active=True)
        self._pill_completed = FilterPill(tr("finances.income.filter.completed"), active=False)
        self._pill_processing = FilterPill(tr("finances.income.filter.processing"), active=False)

        self._pill_all.clicked.connect(lambda: self._set_filter("all"))
        self._pill_completed.clicked.connect(lambda: self._set_filter("completed"))
        self._pill_processing.clicked.connect(lambda: self._set_filter("processing"))

        pills_row.addWidget(self._pill_all)
        pills_row.addWidget(self._pill_completed)
        pills_row.addWidget(self._pill_processing)
        pills_row.addStretch()
        root.addLayout(pills_row)

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(14)
        self._kpi_received = self._make_kpi_card(tr("finances.income.total_received"), "0", BLUE)
        self._kpi_pending = self._make_kpi_card(tr("finances.income.pending_generated"), "0", YELLOW)
        self._kpi_partial = self._make_kpi_card(tr("finances.income.partial_count"), "0", GREEN)
        self._kpi_month = self._make_kpi_card(tr("finances.income.month_income"), "0", RED)

        kpi_frame = QFrame()
        kpi_frame.setStyleSheet("background: transparent; border: none;")
        kpi_inner = QHBoxLayout(kpi_frame)
        kpi_inner.setSpacing(14)
        kpi_inner.setContentsMargins(0, 0, 0, 0)
        kpi_inner.addWidget(self._kpi_received)
        kpi_inner.addWidget(self._kpi_pending)
        kpi_inner.addWidget(self._kpi_partial)
        kpi_inner.addWidget(self._kpi_month)
        kpi_frame.setVisible(False)
        root.addWidget(kpi_frame)

        content_row = QHBoxLayout()
        content_row.setSpacing(24)
        content_row.setContentsMargins(0, 0, 0, 0)

        left_w = QWidget()
        left_w.setStyleSheet("background: transparent;")
        left_layout = QVBoxLayout(left_w)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.cards_scroll = QScrollArea()
        self.cards_scroll.setWidgetResizable(True)
        self.cards_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.cards_scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical { background: transparent; width: 6px; }
            QScrollBar::handle:vertical {
                background: #2A2A2A; border-radius: 3px; min-height: 20px;
            }
        """)

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 8, 80)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch()

        self.cards_scroll.setWidget(self.cards_container)
        left_layout.addWidget(self.cards_scroll, 1)

        self.table = QTableWidget(0, 8)
        self.table.setParent(self)
        self.table.setGeometry(-10000, -10000, 0, 0)
        self.table.hide()

        self.btn_new = QPushButton("\uff0b")
        self.btn_new.setParent(left_w)
        self.btn_new.setFixedSize(56, 56)
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.setStyleSheet("""
            QPushButton {
                background: #22C55E;
                color: #050505;
                border: none;
                border-radius: 16px;
                font-size: 26px;
                font-weight: 700;
                font-family: 'Inter';
            }
            QPushButton:hover {
                background: #16A34A;
            }
        """)
        self.btn_new.clicked.connect(self._open_create)

        shadow_fab = QGraphicsDropShadowEffect(self.btn_new)
        shadow_fab.setBlurRadius(20)
        shadow_fab.setOffset(0, 0)
        shadow_fab.setColor(QColor(34, 197, 94, 80))
        self.btn_new.setGraphicsEffect(shadow_fab)
        self.btn_new.show()

        content_row.addWidget(left_w, 1)

        self.preview_panel = self._build_preview_panel()
        content_row.addWidget(self.preview_panel)

        root.addLayout(content_row, 1)

        self.lbl_empty = QLabel()
        self.lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 14px;
            font-family: 'Inter';
            padding: 40px;
        """)
        self.lbl_empty.hide()
        root.addWidget(self.lbl_empty)

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(scroll)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition_fab()

    def _reposition_fab(self):
        if hasattr(self, 'btn_new') and hasattr(self, 'cards_scroll'):
            parent = self.btn_new.parent()
            if parent:
                x = 16
                y = parent.height() - self.btn_new.height() - 16
                self.btn_new.move(x, y)
                self.btn_new.raise_()

    def _make_kpi_card(self, title, value, accent_color):
        card = QFrame()
        card.setFixedHeight(100)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-left: 3px solid {accent_color};
                border-radius: 14px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(14)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 120))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(6)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 900; font-family: 'Inter'; letter-spacing: 0.5px;")
        layout.addWidget(lbl_title)

        lbl_value = QLabel(value)
        lbl_value.setStyleSheet("color: white; font-size: 24px; font-weight: 900; font-family: 'Inter';")
        layout.addWidget(lbl_value)

        return card

    def _build_preview_panel(self) -> QFrame:
        panel = QFrame()
        panel.setFixedWidth(340)
        panel.setStyleSheet(f"""
            QFrame {{
                background: {BG_SIDE};
                border: 1px solid {BORDER};
                border-radius: 24px;
            }}
            QLabel {{ background: transparent; border: none; }}
        """)
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 200))
        panel.setGraphicsEffect(shadow)

        vl = QVBoxLayout(panel)
        vl.setContentsMargins(24, 24, 24, 24)
        vl.setSpacing(0)

        hdr = QHBoxLayout()
        self._preview_header_lbl = QLabel("Payment Details")
        self._preview_header_lbl.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 13px; font-weight: 500; "
            "font-family: 'Inter';")
        more = QLabel("\u2022\u2022\u2022")
        more.setStyleSheet(f"color: #4B5563; font-size: 14px;")
        more.setCursor(Qt.CursorShape.PointingHandCursor)
        hdr.addWidget(self._preview_header_lbl)
        hdr.addStretch()
        hdr.addWidget(more)
        vl.addLayout(hdr)
        vl.addSpacing(32)

        avatar_row = QHBoxLayout()
        avatar_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._preview_avatar = QLabel("?")
        self._preview_avatar.setFixedSize(80, 80)
        self._preview_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_avatar.setStyleSheet("""
            QLabel {
                background: #052E16;
                color: #22C55E;
                border-radius: 40px;
                font-size: 22px;
                font-weight: 800;
                font-family: 'Inter';
                border: 4px solid #050505;
            }
        """)
        avatar_row.addWidget(self._preview_avatar)
        vl.addLayout(avatar_row)
        vl.addSpacing(16)

        self._preview_name = QLabel("\u2014")
        self._preview_name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._preview_name.setStyleSheet("""
            color: white; font-size: 20px; font-weight: 700;
            font-family: 'Inter';
        """)
        vl.addWidget(self._preview_name)
        vl.addSpacing(8)

        type_row = QHBoxLayout()
        type_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._preview_type = QLabel("\u2014")
        self._preview_type.setFixedHeight(28)
        self._preview_type.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_MUT};
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
                font-size: 13px; font-family: 'Inter';
                padding: 0 14px;
            }}
        """)
        type_row.addWidget(self._preview_type)
        vl.addLayout(type_row)
        vl.addSpacing(32)

        self._preview_total_lbl = QLabel("Total Amount")
        self._preview_total_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._preview_total_lbl.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 13px; font-family: 'Inter';")
        vl.addWidget(self._preview_total_lbl)
        vl.addSpacing(4)

        self._preview_amount = QLabel("$0.00")
        self._preview_amount.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._preview_amount.setStyleSheet("""
            color: white; font-size: 34px; font-weight: 800;
            font-family: 'Inter'; letter-spacing: -1px;
        """)
        vl.addWidget(self._preview_amount)
        vl.addSpacing(24)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 transparent, stop:0.5 #2A2A2A, stop:1 transparent);
            border: none;
        """)
        vl.addWidget(sep)
        vl.addSpacing(24)

        self._preview_status_row = self._make_detail_row("Status", "\u2014")
        self._preview_date_row = self._make_detail_row("Date", "\u2014")
        self._preview_id_row = self._make_detail_row("Income ID", "\u2014")
        self._preview_payment_method_row = self._make_detail_row("Método de pago", "\u2014")
        self._preview_destination_account_row = self._make_detail_row("Cuenta destino", "\u2014")
        self._preview_receipt_row = self._make_detail_row("Recibo", "\u2014")

        vl.addWidget(self._preview_status_row)
        vl.addWidget(self._preview_date_row)
        vl.addWidget(self._preview_id_row)
        vl.addWidget(self._preview_payment_method_row)
        vl.addWidget(self._preview_destination_account_row)
        vl.addWidget(self._preview_receipt_row)
        vl.addStretch()

        return panel

    def _make_detail_row(self, label: str, value: str) -> QFrame:
        row = QFrame()
        row.setStyleSheet("""
            QFrame { background: transparent; border: none;
                     border-bottom: 1px solid rgba(42,42,42,0.5); }
            QLabel { background: transparent; border: none; }
        """)
        hl = QHBoxLayout(row)
        hl.setContentsMargins(0, 10, 0, 10)
        lbl_key = QLabel(label)
        lbl_key.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 13px; font-family: 'Inter';")
        lbl_val = QLabel(value)
        lbl_val.setStyleSheet(
            f"color: #E5E5E5; font-size: 13px; font-weight: 600; "
            "font-family: 'Inter';")
        lbl_val.setObjectName("val")
        hl.addWidget(lbl_key)
        hl.addStretch()
        hl.addWidget(lbl_val)
        return row

    def _get_detail_value(self, row_frame: QFrame) -> QLabel:
        return row_frame.findChild(QLabel, "val")

    def _update_kpi(self, rows):
        total_received = sum(
            float(r.get("total_paid", 0) or 0) for r in rows
            if r.get("status") != "cancelled"
        )
        pending_generated = sum(
            float(r.get("pending_amount", 0) or 0) for r in rows
            if r.get("status") in ("pending", "partial")
        )
        partial_count = len([r for r in rows if r.get("status") == "partial"])
        current_month = datetime.now().month
        month_income = sum(
            float(r.get("total", 0) or 0) for r in rows
            if r.get("status") != "cancelled"
            and r.get("income_date")
            and hasattr(r["income_date"], "month")
            and r["income_date"].month == current_month
        )

        self._kpi_received.layout().itemAt(1).widget().setText(format_money(total_received))
        self._kpi_pending.layout().itemAt(1).widget().setText(format_money(pending_generated))
        self._kpi_partial.layout().itemAt(1).widget().setText(str(partial_count))
        self._kpi_month.layout().itemAt(1).widget().setText(format_money(month_income))

    def _load(self):
        debug_log(f"[FORENSIC] IncomeView._load: starting income load")
        self._worker = IncomeLoadWorker(self.repo)
        self._worker.done.connect(self._on_loaded)
        self._worker.failed.connect(lambda e: self.lbl_empty.setText(f"Error: {e}"))
        self._worker.start()
        debug_log(f"[FORENSIC] IncomeView._load: worker started")

    def _on_loaded(self, rows):
        debug_log(f"[FORENSIC] IncomeView._on_loaded: received {len(rows)} rows")
        self._hover_row = -1
        self._animations.clear()
        self._rows = rows
        self._selected_income = rows[0] if rows else None
        self._update_kpi(rows)
        self._apply_filter()
        if self._selected_income:
            self._update_preview(self._selected_income)
        debug_log(f"[FORENSIC] IncomeView._on_loaded: complete")

    def _set_filter(self, filter_name: str):
        self._active_filter = filter_name
        self._pill_all.set_active(filter_name == "all")
        self._pill_completed.set_active(filter_name == "completed")
        self._pill_processing.set_active(filter_name == "processing")
        self._apply_filter()

    def _apply_filter(self):
        if self._active_filter == "all":
            filtered = self._rows
        elif self._active_filter == "completed":
            filtered = [r for r in self._rows if r.get("status") == "paid"]
        elif self._active_filter == "processing":
            filtered = [r for r in self._rows if r.get("status") in ("partial", "pending")]
        else:
            filtered = self._rows
        self._paint_cards(filtered)

    def _paint_cards(self, rows: list):
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        if not rows:
            self.lbl_empty.show()
            self.lbl_empty.setText(
                "\U0001f4b0\n\n" + trf("finances.income.empty_title", "No income registered.")
                + "\n" + trf("finances.income.empty_subtitle", "Register your first income to get started.")
            )
            return

        self.lbl_empty.hide()

        self._card_widgets = []
        for income in rows:
            is_sel = (
                self._selected_income is not None
                and income.get("id") == self._selected_income.get("id")
            )
            card = IncomeCard(income, selected=is_sel)
            card.clicked.connect(self._on_card_clicked)
            card.doubleClicked.connect(self._open_detail)
            card.menuRequested.connect(self._show_card_menu)
            self.cards_layout.insertWidget(
                self.cards_layout.count() - 1, card)
            self._card_widgets.append(card)

    def _paint_table(self, rows):
        self._paint_cards(rows)

    def _on_card_clicked(self, income: dict):
        self._selected_income = income
        for card in self._card_widgets:
            is_sel = card.income.get("id") == income.get("id")
            card.set_selected(is_sel)
        full_income = self._get_full_income(income)
        self._update_preview(full_income)

    def _update_preview(self, income: dict):
        name = str(income.get("payer_name") or "\u2014")
        initials = "".join(w[0].upper() for w in name.split()[:2]) or "?"
        status = income.get("status", "pending")

        if status == "paid":
            av_bg, av_color = "#052E16", "#22C55E"
        elif status == "partial":
            av_bg, av_color = "#0C1A4E", "#3B82F6"
        else:
            av_bg, av_color = "#1C1A0E", "#EAB308"
        self._preview_avatar.setText(initials)
        self._preview_avatar.setStyleSheet(f"""
            QLabel {{
                background: {av_bg}; color: {av_color};
                border-radius: 40px; font-size: 22px; font-weight: 800;
                font-family: 'Inter'; border: 4px solid {BG_DEEP};
            }}
        """)

        self._preview_name.setText(name)
        payer_type = income.get("payer_type", "third_party")
        type_map = {"student": "Student", "guardian": "Guardian",
                    "third_party": "Third Party"}
        self._preview_type.setText(type_map.get(payer_type, payer_type))

        total = float(income.get("total", 0) or 0)
        self._preview_amount.setText(f"${total:,.2f}")

        status_labels = {
            "paid":      ("\u2713 Completed", "#22C55E"),
            "partial":   ("\u25F7 Processing", "#3B82F6"),
            "pending":   ("\u23F3 Pending",   "#EAB308"),
            "cancelled": ("\u2715 Cancelled",  "#6B7280"),
        }
        status_text, status_color = status_labels.get(
            status, ("\u2014 Unknown", "#6B7280"))
        val_lbl = self._get_detail_value(self._preview_status_row)
        if val_lbl:
            val_lbl.setText(status_text)
            val_lbl.setStyleSheet(
                f"color: {status_color}; font-size: 13px; "
                f"font-weight: 700; font-family: 'Inter'; "
                f"background: transparent; border: none;")

        date_val = income.get("income_date", "")
        if date_val and hasattr(date_val, "strftime"):
            date_str = date_val.strftime("%b %d, %Y")
        else:
            date_str = str(date_val)[:10] if date_val else "\u2014"
        val_date = self._get_detail_value(self._preview_date_row)
        if val_date:
            val_date.setText(date_str)

        val_id = self._get_detail_value(self._preview_id_row)
        if val_id:
            val_id.setText(f"INC-{income.get('id', '?')}")

        payment_name = (
            income.get("payment_method_name")
            or income.get("payment_method")
            or "\u2014"
        )
        destination_name = (
            income.get("destination_account_name")
            or income.get("destination_account")
            or "\u2014"
        )

        val_payment = self._get_detail_value(self._preview_payment_method_row)
        if val_payment:
            val_payment.setText(payment_name)

        val_destination = self._get_detail_value(self._preview_destination_account_row)
        if val_destination:
            val_destination.setText(destination_name)

        receipt_number = income.get("receipt_number", "")
        val_receipt = self._get_detail_value(self._preview_receipt_row)
        if val_receipt:
            val_receipt.setText(receipt_number if receipt_number else "\u2014")

    def _build_income_menu(self) -> QMenu:
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {BG_CARD}; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 8px;
                font-size: 13px; font-family: 'Inter'; padding: 4px;
            }}
            QMenu::item {{ padding: 8px 16px; border-radius: 6px; }}
            QMenu::item:selected {{ background: {BG_HOVER}; }}
        """)
        return menu

    def _show_context_menu_at(self, income: dict, global_pos):
        menu = self._build_income_menu()
        act_detail = menu.addAction(trf("finances.income.detail", "Detail"))
        act_edit = menu.addAction(trf("finances.income.edit", "Edit"))
        act_dup = menu.addAction(trf("finances.income.duplicate", "Duplicate"))
        menu.addSeparator()
        act_del = menu.addAction(trf("finances.income.delete", "Delete"))
        action = menu.exec(global_pos)
        if action == act_detail:
            self._open_detail(income)
        elif action == act_edit:
            self._open_edit(self._get_full_income(income))
        elif action == act_dup:
            self._duplicate_income(income)
        elif action == act_del:
            self._delete_income(income)

    def _show_card_menu(self, income: dict, global_pos):
        self._show_context_menu_at(income, global_pos)

    def _get_full_income(self, income: dict) -> dict:
        income_id = income.get("id")
        if not income_id:
            return income
        try:
            full = self.repo.get_by_id(income_id)
            if not full:
                return income
            full["items"] = self.repo.get_income_items(income_id)
            full["participants"] = self.repo.get_income_participants(income_id)
            return full
        except Exception:
            return income

    def _open_detail(self, income: dict):
        full = self._get_full_income(income)
        dlg = IncomeDetailsDialog(self.repo, full, parent=self)
        dlg.editRequested.connect(lambda inc: self._open_edit_from_detail(dlg, inc))
        dlg.deleteRequested.connect(lambda inc: self._delete_from_detail(dlg, inc))
        self.blur_on()
        try:
            dlg.exec()
        finally:
            self.blur_off()

    def _open_create(self):
        if self._income_dialog_open:
            return

        debug_log("IncomeView._open_create: creating new IncomeDialog")

        self._income_dialog_open = True
        dlg = IncomeDialog(repo=self.repo, income=None, parent=self)

        self.blur_on()
        try:
            result = dlg.exec()
            if result == QDialog.DialogCode.Accepted:
                QTimer.singleShot(300, self._load)
        finally:
            self._income_dialog_open = False
            self.blur_off()
            dlg.deleteLater()

    def _open_edit(self, income):
        if self._income_dialog_open:
            return

        debug_log(f"IncomeView._open_edit: creating IncomeDialog for id={income.get('id')}")
        full = self._get_full_income(income)

        self._income_dialog_open = True
        dlg = IncomeDialog(repo=self.repo, income=full, parent=self)

        self.blur_on()
        try:
            result = dlg.exec()
            if result == QDialog.DialogCode.Accepted:
                QTimer.singleShot(300, self._load)
        finally:
            self._income_dialog_open = False
            self.blur_off()
            dlg.deleteLater()

    def _open_edit_from_detail(self, detail_dlg, income):
        detail_dlg.done(0)
        QTimer.singleShot(0, lambda: self._open_edit(income))

    def _delete_from_detail(self, detail_dlg, income):
        detail_dlg.done(0)
        QTimer.singleShot(0, lambda: self._delete_income(income))

    def _duplicate_income(self, income: dict):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            trf("finances.income.duplicate", "Duplicate"),
            trf("finances.income.duplicate_confirm",
                "Duplicate the income from {name}?").format(
                    name=income.get("payer_name", "")),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                new_id = self.repo.duplicate_income(income["id"])
                if new_id:
                    self._load()
            except Exception as e:
                QMessageBox.critical(self, tr("common.error"), str(e))

    def prepare_for_app_shutdown(self):
        """Limpieza segura antes de cerrar la aplicación."""
        try:
            if self._worker and self._worker.isRunning():
                self._worker.quit()
                self._worker.wait(1500)
        except Exception:
            pass

    def _delete_income(self, income):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            trf("finances.income.delete_title", "Delete income"),
            trf("finances.income.delete_confirm", "Delete '{name}'?").format(
                name=income.get("payer_name", "")),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete_income(income["id"])
                self._load()
            except Exception as e:
                QMessageBox.critical(self, tr("common.error"), str(e))
