"""
ReceivablesView — PyQt6 implementation matching the premium HTML prototype.

Features:
    - KPI cards with animated circular progress rings + count-up values
    - Segmented filter control with sliding red pill (Todos / Abiertos / Parciales / Pagados)
    - Search input with icon
    - Receivable cards (replaces QTableWidget) with:
        · Gradient avatar with initials
        · Debtor name + concept
        · Progress bar (paid/total) with shimmer animation
        · Percentage badge
        · Status badge with glowing dot
        · Due date with overdue/soon coloring
        · Action buttons (pay / history / cancel) that appear on hover
    - Card hover lift with shadow animation
    - Staggered entrance animation
    - Slide-in drawer for payment history (custom dialog with QPropertyAnimation)

Connections preserved from the original:
    - core.i18n.tr
    - repositories.finances_receivables_repository.FinancesReceivablesRepository
    - views.finances.receivables.receivable_payment_dialog.ReceivablePaymentDialog
    - views.finances.receivables.receivable_details_dialog.ReceivableDetailsDialog
    - repo.get_all() / repo.get_payments(id) / repo.cancel_receivable(id)
    - blur_on() / blur_off() callbacks
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QScrollArea,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
    QSizePolicy, QLineEdit, QSpacerItem,
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, pyqtProperty,
    QPropertyAnimation, QEasingCurve, QTimer, QPoint,
    QRectF, QSize,
)
from PyQt6.QtGui import (
    QColor, QPainter, QPen, QBrush, QLinearGradient,
    QFont, QPainterPath,
)
from datetime import date, datetime

from core.i18n import tr
from repositories.finances_receivables_repository import FinancesReceivablesRepository
from views.finances.receivables.receivable_payment_dialog import ReceivablePaymentDialog

# ─────────────────────────────────────────────────────────────────────────────
# Palette (matches income_view.py / expenses_view.py)
# ─────────────────────────────────────────────────────────────────────────────
BG_DEEP  = "#050505"
BG_SIDE  = "#0D0D0D"
BG_CARD  = "#161616"
BG_INPUT = "#1C1C1C"
BG_HOVER = "#1E1E1E"
BORDER   = "#2A2A2A"
RED      = "#C8102E"
RED_H    = "#E8152F"
GREEN    = "#22C55E"
GREEN_D  = "#16A34A"
YELLOW   = "#EAB308"
BLUE     = "#3B82F6"
PURPLE   = "#A855F7"
ORANGE   = "#F97316"
TEXT_PRI = "#F0F0F0"
TEXT_SEC = "#9CA3AF"
TEXT_MUT = "#6B7280"


def format_money(value):
    try:
        value = float(value or 0)
    except Exception:
        value = 0
    return "$" + f"{value:,.0f}".replace(",", ".")


def _format_date(date_val) -> str:
    if not date_val:
        return "—"
    if hasattr(date_val, "strftime"):
        return date_val.strftime("%d %b %Y")
    s = str(date_val)[:10]
    try:
        d = datetime.strptime(s, "%Y-%m-%d")
        return d.strftime("%d %b %Y")
    except Exception:
        return s


def _days_until(date_val) -> int:
    if not date_val:
        return 999
    s = str(date_val)[:10]
    try:
        d = datetime.strptime(s, "%Y-%m-%d").date()
        return (d - date.today()).days
    except Exception:
        return 999


def _initials(name: str) -> str:
    words = (name or "?").strip().split()
    return "".join(w[0].upper() for w in words[:2]) or "?"


# ─────────────────────────────────────────────────────────────────────────────
# Async loader
# ─────────────────────────────────────────────────────────────────────────────
class ReceivablesLoadWorker(QThread):
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
# CircularRing — SVG-like circular progress painted with QPainter
# ─────────────────────────────────────────────────────────────────────────────
class CircularRing(QWidget):
    def __init__(self, size=56, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._progress = 0.0
        self._color = QColor(RED_H)
        self._icon = "$"

    def set_color(self, color: str):
        self._color = QColor(color)
        self.update()

    def set_icon(self, icon: str):
        self._icon = icon
        self.update()

    def getProgress(self):
        return self._progress

    def setProgress(self, val):
        self._progress = max(0.0, min(1.0, float(val)))
        self.update()

    progress = pyqtProperty(float, fget=getProgress, fset=setProgress)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        margin = 5
        rect = QRectF(margin, margin, w - 2 * margin, h - 2 * margin)

        # Background circle
        pen = QPen(QColor(BORDER), 4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawArc(rect, 0, 360 * 16)

        # Progress arc
        if self._progress > 0.001:
            glow = QPen(self._color, 4)
            glow.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(glow)
            start_angle = 90 * 16
            span = int(-self._progress * 360 * 16)
            p.drawArc(rect, start_angle, span)

        # Center icon
        p.setPen(self._color)
        font = QFont("Inter", int(w * 0.22))
        font.setWeight(QFont.Weight.Black)
        p.setFont(font)
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._icon)


# ─────────────────────────────────────────────────────────────────────────────
# CountUpLabel — animates from 0 to target value
# ─────────────────────────────────────────────────────────────────────────────
class CountUpLabel(QLabel):
    def __init__(self, text="", fmt="money", parent=None):
        super().__init__(text, parent)
        self._fmt = fmt
        self._current = 0.0
        self._target = 0.0
        self._anim = QPropertyAnimation(self, b"animValue", self)
        self._anim.setDuration(1100)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def getAnimValue(self):
        return self._current

    def setAnimValue(self, v):
        self._current = v
        if self._fmt == "money":
            self.setText(format_money(v))
        else:
            self.setText(str(int(round(v))))

    animValue = pyqtProperty(float, fget=getAnimValue, fset=setAnimValue)

    def set_target(self, target, animate=True):
        try:
            target = float(target or 0)
        except Exception:
            target = 0.0
        self._target = target
        if animate:
            self._anim.stop()
            self._anim.setStartValue(self._current)
            self._anim.setEndValue(target)
            self._anim.start()
        else:
            self._current = target
            self.setAnimValue(target)


# ─────────────────────────────────────────────────────────────────────────────
# ShimmerBar — progress bar with shimmer overlay
# ─────────────────────────────────────────────────────────────────────────────
class ShimmerBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(6)
        self._progress = 0.0
        self._shimmer_x = 0.0
        self._color = GREEN

        # Shimmer animation (loops forever)
        self._shimmer_anim = QPropertyAnimation(self, b"shimmerX", self)
        self._shimmer_anim.setDuration(2400)
        self._shimmer_anim.setStartValue(-1.0)
        self._shimmer_anim.setEndValue(2.0)
        self._shimmer_anim.setLoopCount(-1)
        self._shimmer_anim.start()

    def getShimmerX(self):
        return self._shimmer_x

    def setShimmerX(self, v):
        self._shimmer_x = v
        self.update()

    shimmerX = pyqtProperty(float, fget=getShimmerX, fset=setShimmerX)

    def set_progress(self, pct: float):
        self._progress = max(0.0, min(1.0, float(pct)))
        self.update()

    def set_color(self, color: str):
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        rect = QRectF(0, 0, w, h)

        # Track
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(BG_INPUT))
        p.drawRoundedRect(rect, 3, 3)

        # Fill
        if self._progress > 0.001:
            fill_w = w * self._progress
            fill_rect = QRectF(0, 0, fill_w, h)
            grad = QLinearGradient(0, 0, fill_w, 0)
            grad.setColorAt(0.0, self._color)
            lighter = QColor(self._color)
            lighter.lighter(120)
            grad.setColorAt(1.0, lighter)
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(fill_rect, 3, 3)

            # Shimmer overlay
            shimmer_w = fill_w * 0.4
            shimmer_center = self._shimmer_x * fill_w
            if shimmer_center > -shimmer_w and shimmer_center < fill_w + shimmer_w:
                s_grad = QLinearGradient(
                    shimmer_center - shimmer_w / 2, 0,
                    shimmer_center + shimmer_w / 2, 0,
                )
                s_grad.setColorAt(0.0, QColor(255, 255, 255, 0))
                s_grad.setColorAt(0.5, QColor(255, 255, 255, 65))
                s_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
                p.setBrush(QBrush(s_grad))
                p.drawRoundedRect(fill_rect, 3, 3)


# ─────────────────────────────────────────────────────────────────────────────
# KpiRingCard — KPI card with ring + count-up + hover lift
# ─────────────────────────────────────────────────────────────────────────────
class KpiRingCard(QFrame):
    def __init__(self, label: str, accent: str, ring_pct: float, ring_icon: str,
                 delta_text: str = "", delta_up: bool = False, sub_text: str = "",
                 parent=None):
        super().__init__(parent)
        self._accent = accent
        self._hovered = False

        self.setFixedHeight(110)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 18px;
            }}
            QLabel {{ background: transparent; border: none; }}
        """)

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(14)
        self._shadow.setOffset(0, 6)
        self._shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(self._shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        # Top row: label + delta
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 10px; font-weight: 900; "
            f"font-family: 'Inter'; letter-spacing: 0.8px;"
        )
        top_row.addWidget(lbl)
        top_row.addStretch()
        if delta_text:
            delta = QLabel(delta_text)
            delta_color = GREEN if delta_up else RED_H
            delta.setStyleSheet(
                f"color: {delta_color}; font-size: 10px; font-weight: 900; "
                f"background: {'rgba(34,197,94,0.10)' if delta_up else 'rgba(200,16,46,0.10)'}; "
                f"border-radius: 5px; padding: 2px 6px;"
            )
            top_row.addWidget(delta)
        layout.addLayout(top_row)

        # Body row: ring + value
        body_row = QHBoxLayout()
        body_row.setSpacing(14)

        self.ring = CircularRing(52)
        self.ring.set_color(accent)
        self.ring.set_icon(ring_icon)
        body_row.addWidget(self.ring)

        val_col = QVBoxLayout()
        val_col.setSpacing(2)
        self.value_lbl = CountUpLabel("0", fmt="money")
        self.value_lbl.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 22px; font-weight: 900; "
            f"font-family: 'Inter'; letter-spacing: -0.4px;"
        )
        val_col.addWidget(self.value_lbl)

        if sub_text:
            sub = QLabel(sub_text)
            sub.setStyleSheet(
                f"color: {TEXT_MUT}; font-size: 11px; font-weight: 600;"
            )
            val_col.addWidget(sub)

        body_row.addLayout(val_col, 1)
        layout.addLayout(body_row)

        # Store ring target for animation
        self._ring_target = ring_pct

    def start_animations(self):
        """Trigger ring fill + count-up."""
        self.ring._progress = 0.0
        ring_anim = QPropertyAnimation(self.ring, b"progress", self)
        ring_anim.setDuration(1400)
        ring_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        ring_anim.setStartValue(0.0)
        ring_anim.setEndValue(self._ring_target)
        ring_anim.start()

    def set_value(self, target, animate=True):
        self.value_lbl.set_target(target, animate=animate)

    def set_ring_pct(self, pct, animate=True):
        self._ring_target = pct
        if animate:
            ring_anim = QPropertyAnimation(self.ring, b"progress", self)
            ring_anim.setDuration(1400)
            ring_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            ring_anim.setStartValue(self.ring._progress)
            ring_anim.setEndValue(pct)
            ring_anim.start()
        else:
            self.ring.setProgress(pct)

    def enterEvent(self, event):
        self._hovered = True
        self._shadow.setBlurRadius(24)
        self._shadow.setOffset(0, 8)
        self._shadow.setColor(QColor(0, 0, 0, 140))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._shadow.setBlurRadius(14)
        self._shadow.setOffset(0, 6)
        self._shadow.setColor(QColor(0, 0, 0, 120))
        super().leaveEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
# SegmentedControl — filter tabs with sliding pill
# ─────────────────────────────────────────────────────────────────────────────
class SegmentedControl(QFrame):
    filterChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._filters = []
        self._active = "all"
        self._buttons = []
        self._pill = QFrame(self)
        self._pill.setStyleSheet(
            f"background: rgba(200, 16, 46, 0.45);"
            f"border-radius: 8px;"
            f"border: 1px solid rgba(232, 21, 47, 0.6);"
        )
        self._pill.setVisible(False)
        self._pill_ready = False

        self.setFixedHeight(42)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 11px;
            }}
        """)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setSpacing(2)

    def add_filter(self, key: str, label: str, count: int = 0):
        btn = QPushButton(f"{label}  {count}")
        btn.setFixedHeight(32)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_MUT};
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 700;
                font-family: 'Inter';
                padding: 0 14px;
            }}
            QPushButton:hover {{ color: {TEXT_PRI}; }}
        """)
        btn.clicked.connect(lambda _, k=key: self.set_active(k))
        self._layout.addWidget(btn)
        self._buttons.append((key, btn, label))
        self._filters.append(key)

    def set_count(self, key: str, count: int):
        for k, btn, label in self._buttons:
            if k == key:
                btn.setText(f"{label}  {count}")
                break

    def showEvent(self, event):
        super().showEvent(event)
        if not self._pill_ready and self._buttons:
            self._pill_ready = True
            QTimer.singleShot(50, lambda: self.set_active(self._active or self._buttons[0][0]))

    def set_active(self, key: str):
        self._active = key

        for k, btn, _label in self._buttons:
            if k == key:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 12px;
                        font-weight: 800;
                        font-family: 'Inter';
                        padding: 0 14px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {TEXT_MUT};
                        border: none;
                        border-radius: 8px;
                        font-size: 12px;
                        font-weight: 700;
                        font-family: 'Inter';
                        padding: 0 14px;
                    }}
                    QPushButton:hover {{ color: {TEXT_PRI}; }}
                """)

        for k, btn, _label in self._buttons:
            if k == key:
                def _move_pill(b=btn):
                    target = b.geometry()
                    if target.width() == 0:
                        QTimer.singleShot(30, _move_pill)
                        return
                    self._pill.setVisible(True)
                    anim = QPropertyAnimation(self._pill, b"geometry", self)
                    anim.setDuration(280)
                    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                    anim.setStartValue(self._pill.geometry() if self._pill.geometry().width() > 0 else target)
                    anim.setEndValue(target)
                    anim.start()
                    self._pill.raise_()
                QTimer.singleShot(0, _move_pill)
                break

        self.filterChanged.emit(key)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self._pill.isVisible():
            return
        for k, btn, _label in self._buttons:
            if k == self._active:
                self._pill.setGeometry(btn.geometry())
                self._pill.raise_()
                break


# ─────────────────────────────────────────────────────────────────────────────
# ReceivableCard — full card replacing table row
# ─────────────────────────────────────────────────────────────────────────────
class ReceivableCard(QFrame):
    clicked_card = pyqtSignal(int)           # receivable id
    double_clicked_card = pyqtSignal(int)    # receivable id — opens detail dialog
    pay_requested = pyqtSignal(int)          # receivable id
    history_requested = pyqtSignal(int)      # receivable id
    cancel_requested = pyqtSignal(int)       # receivable id

    # Status → accent color mapping
    STATUS_ACCENT = {
        "open":      RED_H,
        "partial":   YELLOW,
        "paid":      GREEN,
        "cancelled": TEXT_MUT,
    }

    def __init__(self, receivable: dict, parent=None):
        super().__init__(parent)
        self._rec = receivable
        self._hovered = False
        self._selected = False

        status = str(receivable.get("status", ""))
        days = _days_until(receivable.get("due_date"))

        # Accent color: status color unless overdue (then red)
        if status == "paid":
            accent = GREEN
        elif status == "partial":
            accent = YELLOW
        elif status == "open":
            accent = RED_H if days < 0 else BLUE
        else:
            accent = TEXT_MUT

        self._accent = accent
        self.setObjectName("recCard")

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame#recCard {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 18px;
            }}
        """)

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(14)
        self._shadow.setOffset(0, 4)
        self._shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self._shadow)

        self._build(receivable, accent, days)

    def _build(self, rec: dict, accent: str, days: int):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(24)

        # ── Left: avatar + debtor info ──
        left = QHBoxLayout()
        left.setSpacing(12)

        # Avatar — solid circle, same style as instructors/students/income views
        initials = _initials(rec.get("debtor_name", "?"))
        avatar = QLabel(initials)
        avatar.setFixedSize(44, 44)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                background: #1A2A1A;
                color: {GREEN};
                border-radius: 22px;
                font-size: 15px;
                font-weight: 800;
                font-family: 'Inter';
                border: none;
            }}
        """)
        left.addWidget(avatar)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        name = QLabel(str(rec.get("debtor_name") or "—"))
        name.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 14px; font-weight: 800; "
            f"font-family: 'Inter'; border: none; background: transparent;"
        )
        concept = QLabel(str(rec.get("concept") or rec.get("note") or "")[:50])
        concept.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 11px; font-weight: 600; "
            f"font-family: 'Inter'; border: none; background: transparent;"
        )
        info_col.addWidget(name)
        info_col.addWidget(concept)
        left.addLayout(info_col, 0)

        layout.addLayout(left, 0)

        # ── Middle: progress bar ──
        progress_col = QVBoxLayout()
        progress_col.setSpacing(8)

        original = float(rec.get("original_amount", 0) or 0)
        paid = float(rec.get("paid_amount", 0) or 0)
        pending = float(rec.get("pending_amount", 0) or 0)
        pct = (paid / original * 100) if original > 0 else 0

        # Amounts row
        amounts_row = QHBoxLayout()
        amounts_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        paid_lbl = QLabel(format_money(paid))
        paid_lbl.setStyleSheet(
            f"color: {GREEN}; font-size: 14px; font-weight: 900; "
            f"font-family: 'Inter'; border: none; background: transparent;"
        )
        sep = QLabel("/")
        sep.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 12px; font-weight: 700; "
            f"font-family: 'Inter'; border: none; background: transparent;"
        )
        total_lbl = QLabel(format_money(original))
        total_lbl.setStyleSheet(
            f"color: {TEXT_SEC}; font-size: 13px; font-weight: 700; "
            f"font-family: 'Inter'; border: none; background: transparent;"
        )
        amounts_row.addWidget(paid_lbl)
        amounts_row.addWidget(sep)
        amounts_row.addWidget(total_lbl)
        amounts_row.addStretch()
        pct_lbl = QLabel(f"{pct:.0f}%")
        pct_lbl.setStyleSheet(
            f"color: {accent}; font-size: 11px; font-weight: 900; "
            f"font-family: 'Inter'; background: {accent}22; "
            f"border-radius: 6px; padding: 2px 8px; border: none;"
        )
        amounts_row.addWidget(pct_lbl)
        progress_col.addLayout(amounts_row)

        # Progress bar
        self.bar = ShimmerBar()
        self.bar.set_progress(pct / 100.0 if original > 0 else 0)
        self.bar.set_color(GREEN)
        progress_col.addWidget(self.bar)

        layout.addLayout(progress_col, 1)

        # ── Right: status + due date + actions ──
        right = QVBoxLayout()
        right.setSpacing(6)
        right.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Status badge
        status = str(rec.get("status", ""))
        status_text, status_color = self._status_info(status)
        badge = QLabel(status_text)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedHeight(26)
        badge.setStyleSheet(f"""
            QLabel {{
                color: {status_color};
                background: {status_color}1A;
                border: 1px solid {status_color}40;
                border-radius: 6px;
                padding: 0 10px;
                font-size: 10px;
                font-weight: 900;
                font-family: 'Inter';
                letter-spacing: 0.5px;
            }}
        """)
        right.addWidget(badge, 0, Qt.AlignmentFlag.AlignRight)

        # Due date
        due_text = _format_date(rec.get("due_date"))
        due_color = TEXT_MUT
        if status not in ("paid", "cancelled"):
            if days < 0:
                due_text = f"Vencido {abs(days)}d"
                due_color = RED_H
            elif days <= 7:
                due_text = f"En {days}d · {_format_date(rec.get('due_date'))[:6]}"
                due_color = YELLOW
        due_lbl = QLabel(due_text)
        due_lbl.setStyleSheet(
            f"color: {due_color}; font-size: 11px; font-weight: 700; "
            f"font-family: 'Inter'; border: none; background: transparent;"
        )
        right.addWidget(due_lbl, 0, Qt.AlignmentFlag.AlignRight)

        # Action buttons
        actions = QHBoxLayout()
        actions.setSpacing(6)

        if status in ("open", "partial"):
            pay_btn = QPushButton("⚡")
            pay_btn.setFixedSize(32, 32)
            pay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            pay_btn.setToolTip(tr("finances.receivables.pay"))
            pay_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {GREEN};
                    border: 1px solid rgba(34,197,94,0.30);
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 900;
                }}
                QPushButton:hover {{
                    background: rgba(34,197,94,0.12);
                }}
            """)
            pay_btn.clicked.connect(
                lambda _, rid=rec.get("id"): self.pay_requested.emit(rid)
            )
            actions.addWidget(pay_btn)

        hist_btn = QPushButton("⏱")
        hist_btn.setFixedSize(32, 32)
        hist_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        hist_btn.setToolTip(tr("finances.receivables.history"))
        hist_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                border-color: {TEXT_MUT};
                background: {BG_INPUT};
            }}
        """)
        hist_btn.clicked.connect(
            lambda _, rid=rec.get("id"): self.history_requested.emit(rid)
        )
        actions.addWidget(hist_btn)

        if status in ("open", "partial"):
            cancel_btn = QPushButton("✕")
            cancel_btn.setFixedSize(32, 32)
            cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_btn.setToolTip(tr("finances.receivables.cancel"))
            cancel_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {RED_H};
                    border: 1px solid rgba(200,16,46,0.30);
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: 900;
                }}
                QPushButton:hover {{
                    background: rgba(200,16,46,0.12);
                }}
            """)
            cancel_btn.clicked.connect(
                lambda _, rid=rec.get("id"): self.cancel_requested.emit(rid)
            )
            actions.addWidget(cancel_btn)

        right.addLayout(actions)

        layout.addLayout(right, 0)

    @staticmethod
    def _avatar_colors(name: str):
        """Returns (from, to) gradient colors based on name hash."""
        colors = [
            ("#C8102E", "#7F0A1E"),
            ("#EAB308", "#7C5E04"),
            ("#3B82F6", "#1E3A8A"),
            ("#A855F7", "#581C87"),
            ("#F97316", "#7C2D12"),
            ("#22C55E", "#15803D"),
        ]
        h = hash(name) % len(colors)
        return colors[h]

    @staticmethod
    def _status_info(status: str):
        mapping = {
            "open":      (tr("finances.receivables.status_open"), RED_H),
            "partial":   (tr("finances.receivables.status_partial"), YELLOW),
            "paid":      (tr("finances.receivables.status_paid"), GREEN),
            "cancelled": (tr("finances.receivables.status_cancelled"), TEXT_MUT),
        }
        return mapping.get(status, (status, TEXT_MUT))

    def set_selected(self, selected: bool):
        self._selected = selected
        self._apply_style()

    def _apply_style(self):
        if self._selected:
            self.setStyleSheet(f"""
                QFrame#recCard {{
                    background-color: {BG_HOVER};
                    border: 1px solid rgba(255,255,255,0.18);
                    border-radius: 18px;
                }}
            """)
        elif self._hovered:
            self.setStyleSheet(f"""
                QFrame#recCard {{
                    background-color: {BG_HOVER};
                    border: 1px solid rgba(255,255,255,0.10);
                    border-radius: 18px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame#recCard {{
                    background-color: {BG_CARD};
                    border: 1px solid {BORDER};
                    border-radius: 18px;
                }}
            """)

    def mousePressEvent(self, event):
        self.clicked_card.emit(self._rec.get("id"))
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked_card.emit(self._rec.get("id"))
        super().mouseDoubleClickEvent(event)

    def enterEvent(self, event):
        self._hovered = True
        self._apply_style()
        self._shadow.setBlurRadius(24)
        self._shadow.setOffset(0, 8)
        self._shadow.setColor(QColor(0, 0, 0, 140))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._apply_style()
        self._shadow.setBlurRadius(14)
        self._shadow.setOffset(0, 4)
        self._shadow.setColor(QColor(0, 0, 0, 80))
        super().leaveEvent(event)


# ─────────────────────────────────────────────────────────────────────────────
# HistoryDrawer — slide-in panel for payment history
# ─────────────────────────────────────────────────────────────────────────────
class HistoryDrawer(QWidget):
    """A slide-in panel that animates from the right edge."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setWindowFlag(Qt.WindowType.Dialog, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")

        self._frame = QFrame(self)
        self._frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SIDE};
                border-left: 1px solid {BORDER};
            }}
        """)
        self._frame.setFixedWidth(420)

        layout = QVBoxLayout(self._frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(64)
        header.setStyleSheet(f"""
            QFrame {{
                background: {BG_SIDE};
                border-bottom: 1px solid {BORDER};
            }}
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 0, 24, 0)

        self._title_lbl = QLabel("Historial de pagos")
        self._title_lbl.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 16px; font-weight: 900; "
            f"font-family: 'Inter'; border: none;"
        )
        h_layout.addWidget(self._title_lbl)
        h_layout.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_MUT};
                border: 1px solid {BORDER};
                border-radius: 8px;
                font-size: 12px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
                border-color: {TEXT_MUT};
                background: {BG_HOVER};
            }}
        """)
        close_btn.clicked.connect(self.close_drawer)
        h_layout.addWidget(close_btn)

        layout.addWidget(header)

        # Body
        self._body = QWidget()
        self._body.setStyleSheet(f"background: {BG_SIDE};")
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(24, 20, 24, 20)
        self._body_layout.setSpacing(16)
        layout.addWidget(self._body, 1)

        self._frame.move(420, 0)  # hidden off-screen to the right
        self.resize(420, 600)

    def show_history(self, receivable: dict, payments: list):
        self._title_lbl.setText("Historial de pagos")

        # Clear body
        while self._body_layout.count():
            item = self._body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Summary
        original = float(receivable.get("original_amount", 0) or 0)
        paid = float(receivable.get("paid_amount", 0) or 0)
        pending = float(receivable.get("pending_amount", 0) or 0)

        summary = QFrame()
        summary.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        s_layout = QVBoxLayout(summary)
        s_layout.setContentsMargins(16, 14, 16, 14)
        s_layout.setSpacing(6)

        s_layout.addWidget(self._summary_row("Total original", format_money(original), TEXT_PRI))
        s_layout.addWidget(self._summary_row("Pagado", format_money(paid), GREEN))
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER}; border: none;")
        s_layout.addWidget(sep)
        pend_color = YELLOW if pending > 0 else GREEN
        s_layout.addWidget(self._summary_row("Pendiente", format_money(pending), pend_color, bold=True))

        self._body_layout.addWidget(summary)

        # Payments header
        count_lbl = QLabel(f"PAGOS REGISTRADOS · {len(payments)}")
        count_lbl.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 10px; font-weight: 900; "
            f"font-family: 'Inter'; letter-spacing: 0.6px; border: none;"
        )
        self._body_layout.addWidget(count_lbl)

        # Payment items
        if payments:
            for p in payments:
                item = self._payment_item(p)
                self._body_layout.addWidget(item)
        else:
            empty = QLabel("Sin pagos registrados")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(
                f"color: {TEXT_MUT}; font-size: 13px; font-weight: 700; "
                f"font-family: 'Inter'; padding: 40px; border: none;"
            )
            self._body_layout.addWidget(empty)

        self._body_layout.addStretch()

    def _summary_row(self, label: str, value: str, color: str, bold: bool = False):
        row = QFrame()
        row.setStyleSheet("border: none; background: transparent;")
        r_layout = QHBoxLayout(row)
        r_layout.setContentsMargins(0, 2, 0, 2)
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 12px; font-weight: 600; "
            f"font-family: 'Inter'; border: none;"
        )
        val = QLabel(value)
        weight = "900" if bold else "800"
        val.setStyleSheet(
            f"color: {color}; font-size: {'14px' if bold else '12px'}; "
            f"font-weight: {weight}; font-family: 'Inter'; border: none;"
        )
        r_layout.addWidget(lbl)
        r_layout.addStretch()
        r_layout.addWidget(val)
        return row

    def _payment_item(self, p: dict):
        item = QFrame()
        item.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border: 1px solid rgba(34,197,94,0.30);
            }}
        """)
        i_layout = QHBoxLayout(item)
        i_layout.setContentsMargins(16, 14, 16, 14)
        i_layout.setSpacing(12)

        # Green dot
        dot = QLabel()
        dot.setFixedSize(10, 10)
        dot.setStyleSheet(
            f"background: {GREEN}; border-radius: 5px; border: none;"
        )
        dot_shadow = QGraphicsDropShadowEffect(dot)
        dot_shadow.setBlurRadius(8)
        dot_shadow.setOffset(0, 0)
        dot_shadow.setColor(QColor(34, 197, 94, 180))
        dot.setGraphicsEffect(dot_shadow)
        i_layout.addWidget(dot)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        date_lbl = QLabel(_format_date(p.get("payment_date")))
        date_lbl.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 12px; font-weight: 700; "
            f"font-family: 'Inter'; border: none;"
        )
        note_lbl = QLabel(str(p.get("note", "")) or "Sin nota")
        note_lbl.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 11px; "
            f"font-family: 'Inter'; border: none;"
        )
        info_col.addWidget(date_lbl)
        info_col.addWidget(note_lbl)
        i_layout.addLayout(info_col, 1)

        amount_lbl = QLabel("+" + format_money(p.get("amount", 0)))
        amount_lbl.setStyleSheet(
            f"color: {GREEN}; font-size: 14px; font-weight: 900; "
            f"font-family: 'Inter'; border: none;"
        )
        i_layout.addWidget(amount_lbl)

        return item

    def show_drawer(self):
        self.show()
        # Slide in animation
        screen = self.screen() or self.parentWidget()
        if screen:
            geo = screen.availableGeometry() if hasattr(screen, 'availableGeometry') else screen.geometry()
        else:
            geo = self.geometry()

        self.move(geo.width(), geo.y())
        self.resize(420, geo.height())

        # Move frame to fill
        self._frame.move(0, 0)
        self._frame.setFixedHeight(geo.height())

        anim = QPropertyAnimation(self, b"pos", self)
        anim.setDuration(320)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(QPoint(geo.width(), geo.y()))
        anim.setEndValue(QPoint(geo.width() - 420, geo.y()))
        anim.start()
        self._slide_anim = anim  # keep reference

    def close_drawer(self):
        geo = self.geometry()
        screen = self.screen()
        if screen:
            screen_geo = screen.availableGeometry() if hasattr(screen, 'availableGeometry') else screen.geometry()
        else:
            screen_geo = geo

        anim = QPropertyAnimation(self, b"pos", self)
        anim.setDuration(280)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(self.pos())
        anim.setEndValue(QPoint(screen_geo.width(), screen_geo.y()))
        anim.finished.connect(self.hide)
        anim.start()
        self._slide_anim = anim


# ─────────────────────────────────────────────────────────────────────────────
# ReceivablesView — main view
# ─────────────────────────────────────────────────────────────────────────────
class ReceivablesView(QWidget):
    def __init__(self, blur_on=None, blur_off=None, parent=None):
        super().__init__(parent)
        self.repo = FinancesReceivablesRepository()
        self.blur_on = blur_on or (lambda: None)
        self.blur_off = blur_off or (lambda: None)
        self._rows = []
        self._worker = None
        self._active_filter = "all"
        self._search_query = ""
        self._selected_id = None
        self._card_widgets = []
        self._animations = []
        self._history_drawer = None

        self._build_ui()
        self._load()

    # ════════════════════════════════════════════════════════════════════════
    # UI construction
    # ════════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical { background: transparent; width: 6px; }
            QScrollBar::handle:vertical {
                background: #2A2A2A; border-radius: 3px; min-height: 20px;
            }
        """)

        inner = QWidget()
        inner.setStyleSheet(f"background: {BG_DEEP};")
        root = QVBoxLayout(inner)
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(20)

        # ── Header ──
        header_row = QHBoxLayout()
        header_row.setSpacing(16)
        header_left = QVBoxLayout()
        header_left.setSpacing(4)

        title = QLabel(tr("finances.receivables.title"))
        title.setStyleSheet(
            "color: white; font-size: 28px; font-weight: 900; "
            "font-family: 'Inter'; letter-spacing: -0.8px;"
        )
        subtitle = QLabel(tr("finances.receivables.subtitle"))
        subtitle.setStyleSheet(
            f"color: {TEXT_MUT}; font-size: 13px; font-weight: 500; "
            f"font-family: 'Inter';"
        )
        header_left.addWidget(title)
        header_left.addWidget(subtitle)
        header_row.addLayout(header_left)
        header_row.addStretch()

        # Export button
        btn_export = QPushButton("⬇  Exportar")
        btn_export.setFixedHeight(38)
        btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_export.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SEC};
                border: 1px solid {BORDER};
                border-radius: 10px;
                font-size: 12px;
                font-weight: 800;
                font-family: 'Inter';
                padding: 0 18px;
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
                border-color: {TEXT_MUT};
                background: {BG_HOVER};
            }}
        """)
        header_row.addWidget(btn_export)

        root.addLayout(header_row)

        # ── KPI row ──
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(14)
        self._kpi_total = KpiRingCard(
            tr("finances.receivables.total_portfolio"), RED_H,
            ring_pct=0.78, ring_icon="$",
            delta_text="↑ 8%", delta_up=False, sub_text="Pendiente total"
        )
        self._kpi_overdue = KpiRingCard(
            tr("finances.receivables.overdue"), YELLOW,
            ring_pct=0.42, ring_icon="!",
            delta_text="↑ 3%", delta_up=False, sub_text="Vencidos"
        )
        self._kpi_pending = KpiRingCard(
            tr("finances.receivables.due_soon"), GREEN,
            ring_pct=0.61, ring_icon="→",
            delta_text="↓ 5%", delta_up=True, sub_text="Por vencer"
        )
        self._kpi_debtors = KpiRingCard(
            tr("finances.receivables.debtors"), BLUE,
            ring_pct=0.55, ring_icon="☚",
            delta_text="+1", delta_up=True, sub_text="Activos",
        )
        # Override fmt for debtors (count, not money)
        self._kpi_debtors.value_lbl._fmt = "count"

        kpi_row.addWidget(self._kpi_total)
        kpi_row.addWidget(self._kpi_overdue)
        kpi_row.addWidget(self._kpi_pending)
        kpi_row.addWidget(self._kpi_debtors)
        root.addLayout(kpi_row)

        # ── Filter bar ──
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)

        self._seg = SegmentedControl()
        self._seg.setFixedHeight(42)
        self._seg.setMaximumWidth(400)
        self._seg.add_filter("all", tr("finances.receivables.filter_all") if tr("finances.receivables.filter_all") != "finances.receivables.filter_all" else "Todos", 0)
        self._seg.add_filter("open", tr("finances.receivables.filter_open") if tr("finances.receivables.filter_open") != "finances.receivables.filter_open" else "Abiertos", 0)
        self._seg.add_filter("partial", tr("finances.receivables.filter_partial") if tr("finances.receivables.filter_partial") != "finances.receivables.filter_partial" else "Parciales", 0)
        self._seg.add_filter("paid", tr("finances.receivables.filter_paid") if tr("finances.receivables.filter_paid") != "finances.receivables.filter_paid" else "Pagados", 0)
        self._seg.filterChanged.connect(self._on_filter_changed)
        filter_row.addWidget(self._seg)

        filter_row.addStretch()

        # Search input
        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar deudor, concepto o monto…")
        self._search.setFixedHeight(38)
        self._search.setMinimumWidth(280)
        self._search.setMaximumWidth(400)
        self._search.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_CARD};
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 10px;
                padding: 0 14px 0 38px;
                font-size: 13px;
                font-weight: 500;
                font-family: 'Inter';
            }}
            QLineEdit::placeholder {{
                color: {TEXT_MUT};
            }}
            QLineEdit:focus {{
                border-color: {RED};
                background: {BG_HOVER};
            }}
        """)
        self._search.textChanged.connect(self._on_search_changed)
        filter_row.addWidget(self._search)

        root.addLayout(filter_row)

        # ── Cards list (replaces QTableWidget) ──
        self.cards_scroll = QScrollArea()
        self.cards_scroll.setWidgetResizable(True)
        self.cards_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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
        self.cards_layout.setContentsMargins(0, 0, 8, 0)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch()

        self.cards_scroll.setWidget(self.cards_container)
        root.addWidget(self.cards_scroll, 1)

        # ── Empty state ──
        self.lbl_empty = QLabel()
        self.lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 14px;
            font-family: 'Inter';
            padding: 60px;
            background: {BG_CARD};
            border: 1px dashed {BORDER};
            border-radius: 18px;
        """)
        self.lbl_empty.hide()
        root.addWidget(self.lbl_empty)

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(scroll)

    # ════════════════════════════════════════════════════════════════════════
    # KPI updates
    # ════════════════════════════════════════════════════════════════════════
    def _update_kpi(self, rows):
        today = date.today()
        active_statuses = ("open", "partial")
        active_rows = [r for r in rows if r.get("status", "") in active_statuses]

        total_pending = sum(float(r.get("pending_amount", 0) or 0) for r in active_rows)
        overdue = sum(
            float(r.get("pending_amount", 0) or 0)
            for r in active_rows
            if r.get("due_date") and str(r["due_date"])[:10] < today.isoformat()
        )
        due_soon = sum(
            float(r.get("pending_amount", 0) or 0)
            for r in active_rows
            if r.get("due_date") and str(r["due_date"])[:10] >= today.isoformat()
        )
        debtors = len(set(r.get("debtor_name", "") for r in active_rows if r.get("debtor_name")))

        self._kpi_total.set_value(total_pending)
        self._kpi_overdue.set_value(overdue)
        self._kpi_pending.set_value(due_soon)
        self._kpi_debtors.set_value(debtors)

        # Ring percentages
        total = total_pending if total_pending > 0 else 1
        self._kpi_total.set_ring_pct(0.78)  # demo ratio
        self._kpi_overdue.set_ring_pct(overdue / total if total > 0 else 0)
        self._kpi_pending.set_ring_pct(due_soon / total if total > 0 else 0)
        self._kpi_debtors.set_ring_pct(min(debtors / 20.0, 1.0))

        # Trigger animations
        QTimer.singleShot(100, self._start_kpi_animations)

    def _start_kpi_animations(self):
        for kpi in [self._kpi_total, self._kpi_overdue, self._kpi_pending, self._kpi_debtors]:
            kpi.start_animations()

    # ════════════════════════════════════════════════════════════════════════
    # Data loading
    # ════════════════════════════════════════════════════════════════════════
    def _load(self):
        self._worker = ReceivablesLoadWorker(self.repo)
        self._worker.done.connect(self._on_loaded)
        self._worker.failed.connect(lambda e: self.lbl_empty.setText(f"Error: {e}"))
        self._worker.start()

    def _on_loaded(self, rows):
        self._rows = rows
        self._update_kpi(rows)
        self._update_filter_counts(rows)
        self._apply_filter()

    def _update_filter_counts(self, rows):
        self._seg.set_count("all", len(rows))
        self._seg.set_count("open", len([r for r in rows if r.get("status") == "open"]))
        self._seg.set_count("partial", len([r for r in rows if r.get("status") == "partial"]))
        self._seg.set_count("paid", len([r for r in rows if r.get("status") == "paid"]))

    # ════════════════════════════════════════════════════════════════════════
    # Filtering
    # ════════════════════════════════════════════════════════════════════════
    def _on_filter_changed(self, filter_key: str):
        self._active_filter = filter_key
        self._apply_filter()

    def _on_search_changed(self, text: str):
        self._search_query = text.strip().lower()
        self._apply_filter()

    def _apply_filter(self):
        filtered = self._rows

        if self._active_filter != "all":
            filtered = [r for r in filtered if r.get("status") == self._active_filter]

        if self._search_query:
            q = self._search_query
            filtered = [
                r for r in filtered
                if q in str(r.get("debtor_name", "")).lower()
                or q in str(r.get("concept", "") or r.get("note", "")).lower()
                or q in format_money(r.get("pending_amount", 0)).lower()
            ]

        filtered = sorted(
            filtered,
            key=lambda r: str(r.get("due_date") or ""),
            reverse=False,
        )

        self._paint_cards(filtered)

    # ════════════════════════════════════════════════════════════════════════
    # Cards rendering
    # ════════════════════════════════════════════════════════════════════════
    def _paint_cards(self, rows: list):
        # Clear existing
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self._card_widgets = []

        if not rows:
            self.cards_scroll.hide()
            self.lbl_empty.show()
            self.lbl_empty.setText(
                tr("finances.receivables.empty")
                if tr("finances.receivables.empty") != "finances.receivables.empty"
                else "Sin resultados\nNo se encontraron receivables con los filtros actuales"
            )
            return

        self.cards_scroll.show()
        self.lbl_empty.hide()

        for i, rec in enumerate(rows):
            card = ReceivableCard(rec)
            card.clicked_card.connect(self._on_card_clicked)
            card.double_clicked_card.connect(self._on_card_double_clicked)
            card.pay_requested.connect(self._register_payment_by_id)
            card.history_requested.connect(self._open_detail_by_id)
            card.cancel_requested.connect(self._cancel_receivable_by_id)
            if rec.get("id") == self._selected_id:
                card.set_selected(True)
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
            self._card_widgets.append(card)

            # Staggered fade-in — NO position animation to avoid visual jump
            opacity = QGraphicsOpacityEffect(card)
            opacity.setOpacity(0.0)
            card.setGraphicsEffect(opacity)
            anim = QPropertyAnimation(opacity, b"opacity", card)
            anim.setDuration(300)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim_offset = min(i * 30, 300)
            anim.finished.connect(lambda c=card: c.setGraphicsEffect(None))
            QTimer.singleShot(anim_offset, anim.start)

    def _on_card_clicked(self, rec_id):
        self._selected_id = rec_id if self._selected_id != rec_id else None
        for card in self._card_widgets:
            card.set_selected(card._rec.get("id") == self._selected_id)

    # ════════════════════════════════════════════════════════════════════════
    # Actions — preserve connections to existing dialogs
    # ════════════════════════════════════════════════════════════════════════
    def _register_payment_by_id(self, rec_id):
        rec = next((r for r in self._rows if r.get("id") == rec_id), None)
        if rec:
            self._register_payment(rec)

    def _open_detail_by_id(self, rec_id):
        rec = next((r for r in self._rows if r.get("id") == rec_id), None)
        if not rec:
            return
        person_id   = rec.get("person_id")
        debtor_name = rec.get("debtor_name", "Cliente")

        if not person_id:
            self._show_history(rec)
            return

        from views.finances.receivables.client_history_dialog import ClientHistoryDialog
        dlg = ClientHistoryDialog(
            repo=self.repo,
            person_id=person_id,
            debtor_name=debtor_name,
            parent=self,
        )
        self.blur_on()
        try:
            dlg.exec()
        finally:
            self.blur_off()

    def _cancel_receivable_by_id(self, rec_id):
        rec = next((r for r in self._rows if r.get("id") == rec_id), None)
        if rec:
            self._cancel_receivable(rec)

    def _on_card_double_clicked(self, rec_id):
        self._open_receivable_detail(rec_id)

    def _open_receivable_detail(self, rec_id):
        rec = next((r for r in self._rows if r.get("id") == rec_id), None)
        if not rec:
            return

        source_income_id = rec.get("source_income_id")

        if source_income_id:
            try:
                from repositories.finances_income_repository import FinancesIncomeRepository
                from views.finances.income.income_details_dialog import IncomeDetailsDialog
                income_repo = FinancesIncomeRepository()
                income = income_repo.get_by_id(source_income_id)
                if income:
                    if "items" not in income or income["items"] is None:
                        income["items"] = income_repo.get_income_items(source_income_id)
                    if "participants" not in income or income["participants"] is None:
                        income["participants"] = income_repo.get_income_participants(source_income_id)
                    dlg = IncomeDetailsDialog(repo=income_repo, income=income, parent=self)
                    self.blur_on()
                    try:
                        dlg.exec()
                    finally:
                        self.blur_off()
                    return
            except Exception as e:
                print(f"[Receivables] Error abriendo income detail: {e}")

        from views.finances.receivables.receivable_details_dialog import ReceivableDetailsDialog
        dlg = ReceivableDetailsDialog(repo=self.repo, receivable=rec, parent=self)
        self.blur_on()
        try:
            result = dlg.exec()
            if result:
                if dlg.action == "pay":
                    self._register_payment(rec)
                elif dlg.action == "cancel":
                    self._cancel_receivable(rec)
        finally:
            self.blur_off()

    def _register_payment(self, rec: dict):
        try:
            from views.finances.income.income_dialog import IncomeDialog
            income_repo = self._income_repo()
            dlg = IncomeDialog(repo=income_repo, income=None, parent=self)
            dlg._reset_for_new()
            self._prefill_income_dialog_for_receivable(dlg, rec)
            self.blur_on()
            try:
                if dlg.exec():
                    self._load()
            finally:
                self.blur_off()
        except Exception:
            dlg = ReceivablePaymentDialog(
                receivable=rec,
                repo=self.repo,
                on_payment_done=self._load,
                parent=self,
            )
            self.blur_on()
            try:
                dlg.exec()
            finally:
                self.blur_off()

    def _income_repo(self):
        from repositories.finances_income_repository import FinancesIncomeRepository
        return FinancesIncomeRepository()

    def _prefill_income_dialog_for_receivable(self, dlg, rec: dict):
        person_id   = rec.get("person_id")
        debtor_name = str(rec.get("debtor_name") or "")
        pending     = float(rec.get("pending_amount", 0) or 0)
        original    = float(rec.get("original_amount", 0) or 0)
        paid_amt    = float(rec.get("paid_amount", 0) or 0)
        concept     = rec.get("concept") or rec.get("note") or ""

        source_income_id = rec.get("source_income_id")
        income_data = None
        if source_income_id:
            try:
                income_repo = self._income_repo()
                income_data = income_repo.get_by_id(source_income_id)
            except Exception as e:
                print(f"[Receivables] No se pudo cargar ingreso fuente: {e}")

        selected = False
        if person_id:
            for i in range(dlg.client_combo.count()):
                item_data = dlg.client_combo.itemData(i)
                if isinstance(item_data, dict):
                    pid = item_data.get("person_id") or item_data.get("id")
                    if pid == person_id:
                        dlg.client_combo.setCurrentIndex(i)
                        selected = True
                        break

        if not selected:
            dlg.input_client_name.setText(debtor_name)
            dlg.input_client_name.setReadOnly(False)
            dlg.input_client_doc.setReadOnly(False)
            dlg.input_client_email.setReadOnly(False)
            dlg.input_client_phone.setReadOnly(False)

            doc, email, phone = "", "", ""

            if income_data:
                doc   = str(income_data.get("payer_document") or "")
                email = str(income_data.get("payer_email") or "")
                phone = str(income_data.get("payer_phone") or "")

            if not any([doc, email, phone]) and person_id:
                try:
                    contact = self.repo.get_person_contact(person_id)
                    doc   = contact.get("documento", "")
                    email = contact.get("email", "")
                    phone = contact.get("phone", "")
                except Exception as e:
                    print(f"[Receivables] Error contacto: {e}")

            if doc:   dlg.input_client_doc.setText(doc)
            if email: dlg.input_client_email.setText(email)
            if phone: dlg.input_client_phone.setText(phone)

        elif income_data:
            if not dlg.input_client_doc.text() and income_data.get("payer_document"):
                dlg.input_client_doc.setReadOnly(False)
                dlg.input_client_doc.setText(str(income_data["payer_document"]))
            if not dlg.input_client_email.text() and income_data.get("payer_email"):
                dlg.input_client_email.setReadOnly(False)
                dlg.input_client_email.setText(str(income_data["payer_email"]))
            if not dlg.input_client_phone.text() and income_data.get("payer_phone"):
                dlg.input_client_phone.setReadOnly(False)
                dlg.input_client_phone.setText(str(income_data["payer_phone"]))

        for i in range(dlg.combo_category.count()):
            if dlg.combo_category.itemData(i) == "receivable":
                dlg.combo_category.setCurrentIndex(i)
                break

        if not dlg._items:
            item_name = concept if concept else f"Cartera — {debtor_name}"
            item = {
                "item_type":    "receivable",
                "name":         f"Abono: {item_name}",
                "base_name":    item_name,
                "quantity":     1,
                "unit_price":   pending,
                "discount":     0.0,
                "subtotal":     pending,
                "reference_id": rec.get("id"),
                "details": (
                    f"Abono a cartera de {debtor_name}. "
                    f"Pendiente total: {original}. Ya pagado: {paid_amt}."
                ),
            }
            dlg._items.append(item)
            dlg._refresh_items_table()
            dlg._on_items_changed()
            dlg._schedule_receipt_preview_update()

    def _show_history(self, rec: dict):
        """Show payment history in a slide-in drawer."""
        try:
            payments = self.repo.get_payments(rec["id"])
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, tr("common.error"), str(e))
            return

        # Create or reuse drawer
        if self._history_drawer is None:
            self._history_drawer = HistoryDrawer(parent=self.window())
        self._history_drawer.show_history(rec, payments)
        self._history_drawer.show_drawer()

    def _cancel_receivable(self, rec: dict):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            tr("finances.receivables.cancel"),
            tr("finances.receivables.cancel_confirm").format(
                name=rec.get("debtor_name", "")
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.repo.cancel_receivable(rec["id"])
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
        try:
            if self._history_drawer:
                self._history_drawer.close()
        except Exception:
            pass