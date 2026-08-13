"""
ExpensesView — PyQt6 implementation matching the dark-premium prototype.

Layout (mirrors income_view.py):
    Header (title + subtitle + "Categorías" ghost button)
    Filter pills row (Todos / Fijos / Inventario / Variables)
    KPI cards row (4 cards, left-accent border, count-up animation)
    Main content row:
        Left  → scrollable list of ExpenseCard (avatar + info + amount + •••)
        Right → PreviewPanel (340px, avatar + description + amount + detail rows)
    FAB (red, bottom-left, opens ExpenseDialog)

Connections preserved from the original expenses_view.py:
    - core.i18n.tr / trf
    - core.debug.debug_log
    - repositories.finances_expenses_repository.FinancesExpensesRepository
    - views.finances.expenses.expense_dialog.ExpenseDialog
    - views.finances.expenses.expense_category_dialog.ExpenseCategoryDialog
    - blur_on / blur_off callbacks
    - prepare_for_app_shutdown()
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QScrollArea, QMenu, QDialog,
    QMessageBox, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, pyqtProperty,
    QPropertyAnimation, QEasingCurve, QPoint, QTimer,
)
from PyQt6.QtGui import QColor, QCursor, QPainter
from datetime import datetime, date

from core.i18n import tr, trf
from core.debug import debug_log
from repositories.finances_expenses_repository import FinancesExpensesRepository
from views.finances.expenses.expense_dialog import ExpenseDialog
from views.finances.expenses.expense_category_dialog import ExpenseCategoryDialog

# ─────────────────────────────────────────────────────────────────────────────
# Palette  (identical to income_view.py)
# ─────────────────────────────────────────────────────────────────────────────
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
PURPLE   = "#A855F7"
ORANGE   = "#F97316"
TEXT_PRI = "#F0F0F0"
TEXT_SEC = "#9CA3AF"
TEXT_MUT = "#6B7280"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def format_money(value):
    try:
        value = float(value or 0)
    except Exception:
        value = 0
    return "$" + f"{value:,.0f}".replace(",", ".")


_CATEGORY_COLORS = {
    "gasto fijo": ("#2A0A0F", RED_H),
    "inventario": ("#1C1A0E", YELLOW),
    "servicios":  ("#0C1A4E", BLUE),
    "marketing":  ("#1A0A2E", PURPLE),
    "eventos":    ("#2A160A", ORANGE),
}


def _category_colors(name: str):
    """Returns (bg, fg) for the avatar, keyed by category name."""
    key = (name or "").lower()
    return _CATEGORY_COLORS.get(key, ("#1C1A0E", YELLOW))


def _is_fixed(expense: dict) -> bool:
    """A gasto is 'fixed' if it has is_fixed=True OR category is 'Gasto Fijo'."""
    if "is_fixed" in expense:
        return bool(expense.get("is_fixed"))
    return str(expense.get("category_name", "")).lower() == "gasto fijo"


def _expense_kind(expense: dict):
    """Returns (label, color) — analogous to income_view's _STATUS_MAP."""
    if expense.get("affects_inventory"):
        return ("INVENTARIO", GREEN)
    if _is_fixed(expense):
        return ("FIJO", RED_H)
    return ("VARIABLE", TEXT_SEC)


def _format_date(date_val) -> str:
    if not date_val:
        return "—"
    if hasattr(date_val, "strftime"):
        return date_val.strftime("%b %d, %Y")
    s = str(date_val)[:10]
    try:
        d = datetime.strptime(s, "%Y-%m-%d")
        return d.strftime("%b %d, %Y")
    except Exception:
        return s


# ─────────────────────────────────────────────────────────────────────────────
# Async loader
# ─────────────────────────────────────────────────────────────────────────────
class ExpensesLoadWorker(QThread):
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


# ─────────────────────────────────────────────────────────────────────────────
# FilterPill  (white when active — identical to income_view.FilterPill)
# ─────────────────────────────────────────────────────────────────────────────
class FilterPill(QPushButton):
    def __init__(self, label: str, count: int = 0, active: bool = False, parent=None):
        super().__init__("", parent)
        self._active = active
        self._count = count
        self._label = label
        self.setFixedHeight(34)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()
        self._refresh_text()

    def set_active(self, active: bool):
        self._active = active
        self._apply_style()
        self._refresh_text()

    def set_count(self, count: int):
        self._count = count
        self._refresh_text()

    def _refresh_text(self):
        self.setText(f"{self._label}  {self._count}")

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
                    background: {BG_CARD};
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


# ─────────────────────────────────────────────────────────────────────────────
# RotatingMoreButton  (••• that rotates 90° on hover)
# ─────────────────────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────────────────────
# KpiCard  (left-accent border + count-up animation)
# ─────────────────────────────────────────────────────────────────────────────
class KpiCard(QFrame):
    def __init__(self, title: str, value: str, accent_color: str,
                 fmt: str = "money", parent=None):
        super().__init__(parent)
        self._fmt = fmt
        self._anim_value = 0.0
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
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

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(14)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(6)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 10px; font-weight: 900; "
            f"font-family: 'Inter'; letter-spacing: 0.5px;"
        )
        layout.addWidget(lbl_title)

        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet(
            "color: white; font-size: 24px; font-weight: 900; font-family: 'Inter';"
        )
        layout.addWidget(self.value_lbl)

        # count-up animation
        self._anim = QPropertyAnimation(self, b"animValue", self)
        self._anim.setDuration(900)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    # ── pyqtProperty for count-up ──
    def getAnimValue(self):
        return self._anim_value

    def setAnimValue(self, v):
        self._anim_value = v
        if self._fmt == "money":
            self.value_lbl.setText(format_money(v))
        else:
            self.value_lbl.setText(str(int(round(v))))

    animValue = pyqtProperty(float, fget=getAnimValue, fset=setAnimValue)

    def set_value(self, target, animate=True):
        try:
            target = float(target or 0)
        except Exception:
            target = 0.0
        if animate and target > 0:
            self._anim.stop()
            self._anim.setStartValue(0.0 if self._anim_value == 0.0 else self._anim_value)
            self._anim.setEndValue(target)
            self._anim.start()
        else:
            self._anim_value = target
            self.setAnimValue(target)


# ─────────────────────────────────────────────────────────────────────────────
# ExpenseCard  (avatar + info + amount + •••  — mirrors IncomeCard)
# ─────────────────────────────────────────────────────────────────────────────
class ExpenseCard(QFrame):
    """Card showing a single expense — mirrors IncomeCard from income_view.py.

    Signals:
        clicked(dict)        — emitted on mouse press (single click)
        doubleClicked(dict)  — emitted on double click
        menuRequested(object, object) — emitted when ••• is pressed (expense, global_pos)
    """
    clicked = pyqtSignal(dict)
    doubleClicked = pyqtSignal(dict)
    menuRequested = pyqtSignal(object, object)   # expense, global_pos

    def __init__(self, expense: dict, selected: bool = False, parent=None):
        super().__init__(parent)
        self.expense = expense
        self._selected = selected
        self._hovered = False

        # Shadow directly on self (same pattern as IncomeCard).
        # A QWidget can only hold ONE QGraphicsEffect, so we use the shadow
        # and skip the opacity entrance — the hover/selected shadow changes
        # provide the visual feedback instead.
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

        cat_name = str(self.expense.get("category_name") or "")
        bg, fg = _category_colors(cat_name)
        kind_label, kind_color = _expense_kind(self.expense)

        # Avatar (first letter of category, colored)
        letter = (cat_name[:1] or "?").upper()
        avatar = QLabel(letter)
        avatar.setFixedSize(48, 48)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border-radius: 24px;
                font-size: 18px;
                font-weight: 800;
                font-family: 'Inter';
                border: none;
            }}
        """)
        hl.addWidget(avatar)

        # Info column
        info_col = QVBoxLayout()
        info_col.setSpacing(3)
        info_col.setContentsMargins(0, 0, 0, 0)

        self.desc_lbl = QLabel(str(self.expense.get("description") or "—"))
        self.desc_lbl.setStyleSheet(
            "color: #E5E5E5; font-size: 14px; font-weight: 700; "
            "font-family: 'Inter'; border: none; background: transparent;"
        )
        self.desc_lbl.setWordWrap(False)

        sub_text = (
            f"{cat_name} • {self.expense.get('subcategory_name') or '—'} • "
            f"{_format_date(self.expense.get('expense_date'))}"
        )
        self.sub_lbl = QLabel(sub_text)
        self.sub_lbl.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 11px; font-weight: 500; "
            f"font-family: 'Inter'; border: none; background: transparent;"
        )

        info_col.addWidget(self.desc_lbl)
        info_col.addWidget(self.sub_lbl)
        hl.addLayout(info_col, 1)

        # Right column — amount + kind badge
        right_col = QVBoxLayout()
        right_col.setSpacing(4)
        right_col.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        amount = format_money(self.expense.get("amount", 0))
        self.amount_lbl = QLabel(f"-{amount}")
        self.amount_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.amount_lbl.setStyleSheet(
            f"color: {RED_H}; font-size: 14px; font-weight: 700; "
            f"font-family: 'Inter'; border: none; background: transparent;"
        )

        self.kind_lbl = QLabel(kind_label)
        self.kind_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.kind_lbl.setStyleSheet(
            f"color: {kind_color}; font-size: 10px; font-weight: 700; "
            f"font-family: 'Inter'; letter-spacing: 0.5px; "
            f"border: none; background: transparent;"
        )

        right_col.addWidget(self.amount_lbl)
        right_col.addWidget(self.kind_lbl)
        hl.addLayout(right_col)

        # Rotating ••• button
        self.more_btn = RotatingMoreButton("•••")
        self.more_btn.clicked.connect(self._emit_menu)
        hl.addWidget(self.more_btn)

    def _emit_menu(self):
        self.menuRequested.emit(self.expense, self.mapToGlobal(QPoint(
            self.more_btn.pos().x() + self.more_btn.width() + 16,
            self.more_btn.pos().y() + self.more_btn.height()
        )))

    def _apply_style(self):
        if self._selected:
            self.setStyleSheet(f"""
                QFrame {{
                    background: {BG_HOVER};
                    border: 1px solid rgba(255,255,255,0.20);
                    border-radius: 16px;
                }}
            """)
            self._shadow.setBlurRadius(20)
            self._shadow.setOffset(0, 4)
            self._shadow.setColor(QColor(0, 0, 0, 120))
        else:
            blur = 24 if self._hovered else 14
            off  = 8  if self._hovered else 4
            self._shadow.setBlurRadius(blur)
            self._shadow.setOffset(0, off)
            self._shadow.setColor(
                QColor(0, 0, 0, 140 if self._hovered else 100)
            )
            self.setStyleSheet(f"""
                QFrame {{
                    background: {BG_CARD};
                    border: 1px solid {BORDER};
                    border-radius: 16px;
                }}
                QFrame:hover {{
                    background: {BG_HOVER};
                    border: 1px solid rgba(255,255,255,0.10);
                }}
            """)

    def set_selected(self, selected: bool):
        self._selected = selected
        self._apply_style()

    # ── Mouse events ──
    def mousePressEvent(self, event):
        self.clicked.emit(self.expense)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit(self.expense)
        super().mouseDoubleClickEvent(event)

    def enterEvent(self, event):
        self._hovered = True
        self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._apply_style()
        super().leaveEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
# PreviewPanel  (340px, avatar + description + amount + detail rows)
# ─────────────────────────────────────────────────────────────────────────────
class PreviewPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(340)
        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_SIDE};
                border: 1px solid {BORDER};
                border-radius: 24px;
            }}
            QLabel {{ background: transparent; border: none; }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 200))
        self.setGraphicsEffect(shadow)

        vl = QVBoxLayout(self)
        vl.setContentsMargins(24, 24, 24, 24)
        vl.setSpacing(0)

        # ── Header row ──
        hdr = QHBoxLayout()
        self._header_lbl = QLabel(
            trf("finances.expenses.detail_header", "Detalle del gasto")
        )
        self._header_lbl.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 13px; font-weight: 500; "
            f"font-family: 'Inter';"
        )
        more = QLabel("•••")
        more.setStyleSheet(f"color: #4B5563; font-size: 14px;")
        more.setCursor(Qt.CursorShape.PointingHandCursor)
        hdr.addWidget(self._header_lbl)
        hdr.addStretch()
        hdr.addWidget(more)
        vl.addLayout(hdr)
        vl.addSpacing(32)

        # ── Avatar (80×80, centered) ──
        avatar_row = QHBoxLayout()
        avatar_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._avatar = QLabel("?")
        self._avatar.setFixedSize(80, 80)
        self._avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._avatar.setStyleSheet(f"""
            QLabel {{
                background: #1C1A0E;
                color: {YELLOW};
                border-radius: 40px;
                font-size: 26px;
                font-weight: 800;
                font-family: 'Inter';
                border: 4px solid {BG_DEEP};
            }}
        """)
        avatar_row.addWidget(self._avatar)
        vl.addLayout(avatar_row)
        vl.addSpacing(16)

        # ── Description (centered, wraps 2 lines) ──
        self._desc_lbl = QLabel("—")
        self._desc_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._desc_lbl.setWordWrap(True)
        self._desc_lbl.setStyleSheet(
            "color: white; font-size: 20px; font-weight: 700; "
            "font-family: 'Inter';"
        )
        vl.addWidget(self._desc_lbl)
        vl.addSpacing(8)

        # ── Category chip (centered) ──
        type_row = QHBoxLayout()
        type_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._chip = QLabel("—")
        self._chip.setFixedHeight(28)
        self._chip.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_MUT};
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
                font-size: 13px; font-family: 'Inter';
                padding: 0 14px;
            }}
        """)
        type_row.addWidget(self._chip)
        vl.addLayout(type_row)
        vl.addSpacing(32)

        # ── "Monto total" label ──
        self._total_lbl = QLabel(
            trf("finances.expenses.total_amount", "Monto total")
        )
        self._total_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._total_lbl.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 13px; font-family: 'Inter';"
        )
        vl.addWidget(self._total_lbl)
        vl.addSpacing(4)

        # ── Big amount ──
        self._amount_lbl = QLabel("$0")
        self._amount_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._amount_lbl.setStyleSheet(
            "color: white; font-size: 34px; font-weight: 800; "
            "font-family: 'Inter'; letter-spacing: -1px;"
        )
        vl.addWidget(self._amount_lbl)
        vl.addSpacing(24)

        # ── Gradient separator ──
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 transparent, stop:0.5 #2A2A2A, stop:1 transparent);
            border: none;
        """)
        vl.addWidget(sep)
        vl.addSpacing(24)

        # ── Detail rows ──
        self._status_row    = self._make_detail_row("Estado")
        self._type_row      = self._make_detail_row("Tipo")
        self._date_row      = self._make_detail_row("Fecha")
        self._id_row        = self._make_detail_row("Gasto ID")
        self._supplier_row  = self._make_detail_row("Proveedor")
        self._invoice_row   = self._make_detail_row("Factura")
        self._inventory_row = self._make_detail_row("Afecta inventario")

        vl.addWidget(self._status_row)
        vl.addWidget(self._type_row)
        vl.addWidget(self._date_row)
        vl.addWidget(self._id_row)
        vl.addWidget(self._supplier_row)
        vl.addWidget(self._invoice_row)
        vl.addWidget(self._inventory_row)
        vl.addStretch()

    def _make_detail_row(self, label: str) -> QFrame:
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
            f"color: {TEXT_MUT}; font-size: 13px; font-family: 'Inter';"
        )
        lbl_val = QLabel("—")
        lbl_val.setStyleSheet(
            "color: #E5E5E5; font-size: 13px; font-weight: 600; "
            "font-family: 'Inter';"
        )
        lbl_val.setObjectName("val")
        hl.addWidget(lbl_key)
        hl.addStretch()
        hl.addWidget(lbl_val)
        return row

    def _get_detail_value(self, row_frame: QFrame):
        return row_frame.findChild(QLabel, "val")

    def _set_detail(self, row: QFrame, value: str, color: str = None):
        lbl = self._get_detail_value(row)
        if not lbl:
            return
        lbl.setText(str(value))
        if color:
            lbl.setStyleSheet(
                f"color: {color}; font-size: 13px; font-weight: 700; "
                f"font-family: 'Inter'; background: transparent; border: none;"
            )
        else:
            lbl.setStyleSheet(
                "color: #E5E5E5; font-size: 13px; font-weight: 600; "
                "font-family: 'Inter'; background: transparent; border: none;"
            )

    def update_expense(self, expense: dict):
        if not expense:
            return

        cat_name  = str(expense.get("category_name") or "")
        bg, fg    = _category_colors(cat_name)
        letter    = (cat_name[:1] or "?").upper()

        # Avatar
        self._avatar.setText(letter)
        self._avatar.setStyleSheet(f"""
            QLabel {{
                background: {bg}; color: {fg};
                border-radius: 40px; font-size: 26px; font-weight: 800;
                font-family: 'Inter'; border: 4px solid {BG_DEEP};
            }}
        """)

        # Description
        self._desc_lbl.setText(str(expense.get("description") or "—"))

        # Chip
        sub = expense.get("subcategory_name") or "—"
        self._chip.setText(f"{cat_name} · {sub}")
        self._chip.setStyleSheet(f"""
            QLabel {{
                color: {fg};
                background: {bg};
                border: 1px solid {fg}33;
                border-radius: 14px;
                font-size: 13px; font-family: 'Inter';
                padding: 0 14px;
            }}
        """)

        # Amount
        amount = format_money(expense.get("amount", 0))
        self._amount_lbl.setText(f"-{amount}")

        # Detail rows
        kind_label, kind_color = _expense_kind(expense)
        self._set_detail(self._status_row, kind_label, kind_color)
        self._set_detail(self._type_row, "Fijo" if _is_fixed(expense) else "Variable")
        self._set_detail(self._date_row, _format_date(expense.get("expense_date")))
        self._set_detail(self._id_row, f"EXP-{expense.get('id', '?')}")
        self._set_detail(self._supplier_row,
                         str(expense.get("supplier_name") or "—"))
        self._set_detail(self._invoice_row,
                         str(expense.get("invoice_number") or "—"))
        affects = "Sí" if expense.get("affects_inventory") else "No"
        affects_color = GREEN if expense.get("affects_inventory") else TEXT_MUT
        self._set_detail(self._inventory_row, affects, affects_color)


# ─────────────────────────────────────────────────────────────────────────────
# ExpensesView  (main view)
# ─────────────────────────────────────────────────────────────────────────────
class ExpensesView(QWidget):
    def __init__(self, blur_on=None, blur_off=None, parent=None):
        super().__init__(parent)
        self.repo = FinancesExpensesRepository()
        self.blur_on = blur_on or (lambda: None)
        self.blur_off = blur_off or (lambda: None)
        self._rows = []
        self._worker = None
        self._selected_expense = None
        self._card_widgets = []
        self._active_filter = "all"
        self._animations = []
        self._expense_dialog_open = False
        self._build_ui()
        self._load()

    # ════════════════════════════════════════════════════════════════════════
    # UI construction
    # ════════════════════════════════════════════════════════════════════════
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

        # ── Header (title + subtitle on the left, "Categorías" on the right) ──
        header_row = QHBoxLayout()
        header_row.setSpacing(16)
        header_left = QVBoxLayout()
        header_left.setSpacing(4)

        title = QLabel(trf("finances.expenses.title", "Gastos"))
        title.setStyleSheet(
            "color: white; font-size: 26px; font-weight: 800; "
            "font-family: 'Inter'; letter-spacing: -0.5px;"
        )
        subtitle = QLabel(trf(
            "finances.expenses.subtitle",
            "Pagos realizados, compras y egresos del dojo"
        ))
        subtitle.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 12px; font-weight: 500; "
            f"font-family: 'Inter';"
        )
        header_left.addWidget(title)
        header_left.addWidget(subtitle)
        header_row.addLayout(header_left)
        header_row.addStretch()

        # "Categorías" ghost button (preserves connection to ExpenseCategoryDialog)
        self.btn_categories = QPushButton(
            trf("finances.expenses.categories", "Categorías")
        )
        self.btn_categories.setFixedHeight(34)
        self.btn_categories.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_categories.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SEC};
                border: 1px solid {BORDER};
                border-radius: 17px;
                padding: 0 18px;
                font-size: 13px;
                font-weight: 700;
                font-family: 'Inter';
            }}
            QPushButton:hover {{
                border-color: {RED};
                color: white;
                background: rgba(200,16,46,0.08);
            }}
        """)
        self.btn_categories.clicked.connect(self._open_categories)
        header_row.addWidget(self.btn_categories)
        root.addLayout(header_row)

        # ── Filter pills row ──
        self._active_filter = "all"
        pills_row = QHBoxLayout()
        pills_row.setSpacing(8)
        pills_row.setContentsMargins(0, 0, 0, 0)

        self._pill_all       = FilterPill(trf("finances.expenses.filter.all", "Todos"),       0, active=True)
        self._pill_fixed     = FilterPill(trf("finances.expenses.filter.fixed", "Fijos"),      0, active=False)
        self._pill_inventory = FilterPill(trf("finances.expenses.filter.inventory", "Inventario"), 0, active=False)
        self._pill_variable  = FilterPill(trf("finances.expenses.filter.variable", "Variables"),  0, active=False)

        self._pill_all.clicked.connect       (lambda: self._set_filter("all"))
        self._pill_fixed.clicked.connect     (lambda: self._set_filter("fixed"))
        self._pill_inventory.clicked.connect (lambda: self._set_filter("inventory"))
        self._pill_variable.clicked.connect  (lambda: self._set_filter("variable"))

        pills_row.addWidget(self._pill_all)
        pills_row.addWidget(self._pill_fixed)
        pills_row.addWidget(self._pill_inventory)
        pills_row.addWidget(self._pill_variable)
        pills_row.addStretch()
        root.addLayout(pills_row)

        # ── KPI cards row ──
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(14)
        self._kpi_total     = KpiCard(trf("finances.expenses.total_month",          "TOTAL DEL MES"),       "0", BLUE)
        self._kpi_fixed     = KpiCard(trf("finances.expenses.fixed",                "GASTOS FIJOS"),        "0", RED)
        self._kpi_inventory = KpiCard(trf("finances.expenses.inventory_purchases",  "COMPRAS INVENTARIO"),  "0", YELLOW)
        self._kpi_cats      = KpiCard(trf("finances.expenses.categories_count",     "CATEGORÍAS"),          "0", GREEN, fmt="count")
        kpi_row.addWidget(self._kpi_total)
        kpi_row.addWidget(self._kpi_fixed)
        kpi_row.addWidget(self._kpi_inventory)
        kpi_row.addWidget(self._kpi_cats)
        root.addLayout(kpi_row)

        # ── Main content row: cards list (left) + preview panel (right) ──
        content_row = QHBoxLayout()
        content_row.setSpacing(24)
        content_row.setContentsMargins(0, 0, 0, 0)

        # Left side — scrollable cards + FAB
        left_w = QWidget()
        left_w.setStyleSheet("background: transparent;")
        left_layout = QVBoxLayout(left_w)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.cards_scroll = QScrollArea()
        self.cards_scroll.setWidgetResizable(True)
        self.cards_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
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

        # FAB — red, bottom-left
        self.btn_new = QPushButton("+")
        self.btn_new.setParent(left_w)
        self.btn_new.setFixedSize(56, 56)
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.setStyleSheet(f"""
            QPushButton {{
                background: {RED};
                color: #050505;
                border: none;
                border-radius: 16px;
                font-size: 26px;
                font-weight: 700;
                font-family: 'Inter';
            }}
            QPushButton:hover {{
                background: {RED_H};
            }}
        """)
        self.btn_new.clicked.connect(self._open_create)

        shadow_fab = QGraphicsDropShadowEffect(self.btn_new)
        shadow_fab.setBlurRadius(20)
        shadow_fab.setOffset(0, 0)
        shadow_fab.setColor(QColor(200, 16, 46, 80))
        self.btn_new.setGraphicsEffect(shadow_fab)
        self.btn_new.show()

        content_row.addWidget(left_w, 1)

        # Right side — preview panel
        self.preview_panel = PreviewPanel()
        content_row.addWidget(self.preview_panel)

        root.addLayout(content_row, 1)

        # ── Empty-state label ──
        self.lbl_empty = QLabel()
        self.lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 14px; "
            f"font-family: 'Inter'; padding: 40px;"
        )
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
        if hasattr(self, "btn_new") and hasattr(self, "cards_scroll"):
            parent = self.btn_new.parent()
            if parent:
                x = 16
                y = parent.height() - self.btn_new.height() - 16
                self.btn_new.move(x, y)
                self.btn_new.raise_()

    # ════════════════════════════════════════════════════════════════════════
    # KPI
    # ════════════════════════════════════════════════════════════════════════
    def _update_kpi(self, rows):
        today = date.today()
        current_month_rows = []
        for r in rows:
            d = r.get("expense_date")
            if not d:
                continue
            if hasattr(d, "month"):
                if d.month == today.month and d.year == today.year:
                    current_month_rows.append(r)
            else:
                s = str(d)[:10]
                if s.startswith(f"{today.year}-{today.month:02d}"):
                    current_month_rows.append(r)

        total_month = sum(float(r.get("amount", 0) or 0) for r in current_month_rows)
        fixed       = sum(float(r.get("amount", 0) or 0) for r in rows if _is_fixed(r))
        inventory   = sum(float(r.get("amount", 0) or 0) for r in rows if r.get("affects_inventory"))
        categories  = len(set(r.get("category_name") for r in rows if r.get("category_name")))

        self._kpi_total.set_value(total_month)
        self._kpi_fixed.set_value(fixed)
        self._kpi_inventory.set_value(inventory)
        self._kpi_cats.set_value(categories)

    # ════════════════════════════════════════════════════════════════════════
    # Data loading
    # ════════════════════════════════════════════════════════════════════════
    def _load(self):
        debug_log("[ExpensesView] _load: starting")
        self._worker = ExpensesLoadWorker(self.repo)
        self._worker.done.connect(self._on_loaded)
        self._worker.failed.connect(lambda e: self.lbl_empty.setText(f"Error: {e}"))
        self._worker.start()
        debug_log("[ExpensesView] _load: worker started")

    def _on_loaded(self, rows):
        debug_log(f"[ExpensesView] _on_loaded: received {len(rows)} rows")
        self._rows = rows
        self._selected_expense = rows[0] if rows else None
        self._update_kpi(rows)
        self._update_pill_counts(rows)
        self._apply_filter()
        if self._selected_expense:
            self.preview_panel.update_expense(self._selected_expense)
        debug_log("[ExpensesView] _on_loaded: complete")

    def _update_pill_counts(self, rows):
        self._pill_all.set_count(len(rows))
        self._pill_fixed.set_count(len([r for r in rows if _is_fixed(r)]))
        self._pill_inventory.set_count(len([r for r in rows if r.get("affects_inventory")]))
        self._pill_variable.set_count(
            len([r for r in rows if not _is_fixed(r) and not r.get("affects_inventory")])
        )

    # ════════════════════════════════════════════════════════════════════════
    # Filtering
    # ════════════════════════════════════════════════════════════════════════
    def _set_filter(self, filter_name: str):
        self._active_filter = filter_name
        self._pill_all.set_active      (filter_name == "all")
        self._pill_fixed.set_active    (filter_name == "fixed")
        self._pill_inventory.set_active(filter_name == "inventory")
        self._pill_variable.set_active (filter_name == "variable")
        self._apply_filter()

    def _apply_filter(self):
        if self._active_filter == "all":
            filtered = self._rows
        elif self._active_filter == "fixed":
            filtered = [r for r in self._rows if _is_fixed(r)]
        elif self._active_filter == "inventory":
            filtered = [r for r in self._rows if r.get("affects_inventory")]
        elif self._active_filter == "variable":
            filtered = [
                r for r in self._rows
                if not _is_fixed(r) and not r.get("affects_inventory")
            ]
        else:
            filtered = self._rows
        # Sort by date descending
        filtered = sorted(
            filtered,
            key=lambda r: str(r.get("expense_date") or ""),
            reverse=True,
        )
        self._paint_cards(filtered)

    def _paint_cards(self, rows: list):
        # Clear existing cards
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self._card_widgets = []

        if not rows:
            self.lbl_empty.show()
            self.lbl_empty.setText(
                trf("finances.expenses.empty_title", "Sin gastos")
                + "\n"
                + trf("finances.expenses.empty_subtitle",
                      "No se encontraron gastos con los filtros actuales.")
            )
            return

        self.lbl_empty.hide()

        for expense in rows:
            is_sel = (
                self._selected_expense is not None
                and expense.get("id") == self._selected_expense.get("id")
            )
            card = ExpenseCard(expense, selected=is_sel)
            card.clicked.connect(self._on_card_clicked)
            card.doubleClicked.connect(self._open_detail)
            card.menuRequested.connect(self._show_card_menu)
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
            self._card_widgets.append(card)

    def _on_card_clicked(self, expense: dict):
        self._selected_expense = expense
        for card in self._card_widgets:
            is_sel = card.expense.get("id") == expense.get("id")
            card.set_selected(is_sel)
        self.preview_panel.update_expense(expense)

    # ════════════════════════════════════════════════════════════════════════
    # Context menu
    # ════════════════════════════════════════════════════════════════════════
    def _build_menu(self) -> QMenu:
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {BG_CARD}; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 8px;
                font-size: 13px; font-family: 'Inter'; padding: 4px;
            }}
            QMenu::item {{ padding: 8px 16px; border-radius: 6px; }}
            QMenu::item:selected {{ background: {BG_HOVER}; }}
            QMenu::separator {{ height: 1px; background: {BORDER}; margin: 4px 8px; }}
        """)
        return menu

    def _show_card_menu(self, expense: dict, global_pos):
        menu = self._build_menu()
        act_detail = menu.addAction(trf("finances.expenses.detail",    "Detalle"))
        act_edit   = menu.addAction(trf("finances.expenses.edit",      "Editar"))
        act_dup    = menu.addAction(trf("finances.expenses.duplicate", "Duplicar"))
        menu.addSeparator()
        act_del    = menu.addAction(trf("finances.expenses.delete",    "Eliminar"))
        action = menu.exec(global_pos)
        if action == act_detail:
            self._open_detail(expense)
        elif action == act_edit:
            self._open_edit(expense)
        elif action == act_dup:
            self._duplicate_expense(expense)
        elif action == act_del:
            self._delete_expense(expense)

    # ════════════════════════════════════════════════════════════════════════
    # Dialog connections  (preserved from original expenses_view.py)
    # ════════════════════════════════════════════════════════════════════════
    def _open_detail(self, expense: dict):
        """Select the expense and show it in the preview panel.
        A dedicated details dialog can be added in a later iteration."""
        self._on_card_clicked(expense)

    def _open_create(self):
        """Opens ExpenseDialog for creating a new expense."""
        if self._expense_dialog_open:
            return
        self._expense_dialog_open = True
        debug_log("[ExpensesView] _open_create: opening ExpenseDialog")
        dlg = ExpenseDialog(repo=self.repo, parent=self)
        self.blur_on()
        try:
            result = dlg.exec()
            if result == QDialog.DialogCode.Accepted:
                QTimer.singleShot(300, self._load)
        finally:
            self._expense_dialog_open = False
            self.blur_off()
            dlg.deleteLater()

    def _open_edit(self, expense: dict):
        """Opens ExpenseDialog for editing.
        TODO: wire `expense=` kwarg once ExpenseDialog supports it
        (next iteration — forms)."""
        # For now, just open the create dialog as a placeholder.
        self._open_create()

    def _open_categories(self):
        """Opens ExpenseCategoryDialog for managing categories/subcategories."""
        dlg = ExpenseCategoryDialog(repo=self.repo, parent=self)
        self.blur_on()
        try:
            if dlg.exec():
                self._load()
        finally:
            self.blur_off()

    def _duplicate_expense(self, expense: dict):
        """TODO: implement once repository supports duplicate_expense()."""
        pass

    def _delete_expense(self, expense: dict):
        reply = QMessageBox.question(
            self,
            trf("finances.expenses.delete_title", "Eliminar gasto"),
            trf("finances.expenses.delete_confirm",
                "¿Eliminar '{name}'?").format(
                name=expense.get("description", "")),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.repo.delete_expense(expense["id"])
                self._load()
            except Exception as e:
                QMessageBox.critical(self, tr("common.error"), str(e))

    # ════════════════════════════════════════════════════════════════════════
    # Shutdown
    # ════════════════════════════════════════════════════════════════════════
    def prepare_for_app_shutdown(self):
        """Safe cleanup before app closes."""
        try:
            if self._worker and self._worker.isRunning():
                self._worker.quit()
                self._worker.wait(1500)
        except Exception:
            pass
