from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QSizePolicy, QScrollArea, QGridLayout, QPushButton,
    QDialog, QLineEdit, QComboBox, QCalendarWidget,
    QGraphicsOpacityEffect, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QDate,
    QPropertyAnimation, QEasingCurve, QRectF, QPointF, QSequentialAnimationGroup,
)
from PyQt6.QtGui import (
    QColor, QFont, QPainter, QPen, QBrush, QPolygonF,
    QLinearGradient, QPainterPath, QTextCharFormat,
)
from datetime import datetime, date


# ─── PALETA ───────────────────────────────────────────────────────────
BG_MAIN    = "#050505"
BG_CARD    = "#0E0E0E"
BG_CARD_2  = "#111111"
BG_INPUT   = "#1A1A1A"
BORDER     = "#1F1F1F"
BORDER_2   = "#2A2A2A"
RED        = "#C8102E"
RED_H      = "#E8152F"
RED_DIM    = "rgba(200,16,46,0.12)"
TEXT_PRI   = "#F5F5F5"
TEXT_SEC   = "#9CA3AF"
TEXT_MUT   = "#6B7280"
TEXT_DIM   = "#374151"
GREEN      = "#10B981"
GREEN_DIM  = "rgba(16,185,129,0.12)"
YELLOW     = "#F59E0B"
YELLOW_DIM = "rgba(245,158,11,0.12)"
BLUE       = "#3B82F6"
BLUE_DIM   = "rgba(59,130,246,0.12)"
PURPLE     = "#A855F7"
PURPLE_DIM = "rgba(168,85,247,0.12)"
ORANGE     = "#F97316"
ORANGE_DIM = "rgba(249,115,22,0.12)"


# ═══════════════════════════════════════════════════════════════════════
# WORKER — sin cambios en queries, toda la lógica de datos intacta
# ═══════════════════════════════════════════════════════════════════════
class DashboardWorker(QThread):
    data_ready = pyqtSignal(dict)

    def __init__(self, db):
        super().__init__()
        self.db = db

    def run(self):
        data = {}
        conn = self.db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                SELECT COUNT(*) FROM students s
                JOIN status st ON st.id = s.id_status
                WHERE LOWER(st.status) IN ('activo', 'active')
            """)
            row = cur.fetchone()
            data["students_active"] = row[0] if row else 0
            if data["students_active"] == 0:
                cur.execute("SELECT COUNT(*) FROM students")
                data["students_active"] = (cur.fetchone() or [0])[0]

            cur.execute("""
                SELECT COALESCE(SUM(total_paid), 0) FROM payments
                WHERE DATE_TRUNC('month', payment_date) = DATE_TRUNC('month', CURRENT_DATE)
            """)
            data["income_month"] = float((cur.fetchone() or [0])[0])

            cur.execute("""
                SELECT COALESCE(SUM(amount), 0) FROM expenses
                WHERE DATE_TRUNC('month', expense_date) = DATE_TRUNC('month', CURRENT_DATE)
            """)
            data["expenses_month"] = float((cur.fetchone() or [0])[0])

            cur.execute("SELECT COUNT(*) FROM classes WHERE date = CURRENT_DATE")
            data["classes_today"] = (cur.fetchone() or [0])[0]

            cur.execute("""
                SELECT t.id, t.task, tt.name, t.limit_date
                FROM tasks t
                LEFT JOIN type_task tt ON tt.id = t.id_type_task
                ORDER BY t.limit_date ASC NULLS LAST, t.id DESC
                LIMIT 20
            """)
            data["tasks"] = cur.fetchall()

            cur.execute("""
                SELECT COUNT(*) FROM student_memberships
                WHERE end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
                AND status = 'activo'
            """)
            data["memberships_expiring"] = (cur.fetchone() or [0])[0]

            cur.execute("""
                SELECT COUNT(*) FROM students s
                JOIN people p ON p.id = s.id_person
                WHERE DATE_TRUNC('month', p.created_at) = DATE_TRUNC('month', CURRENT_DATE)
            """)
            data["students_new"] = (cur.fetchone() or [0])[0]

            cur.execute("""
                SELECT
                    TO_CHAR(DATE_TRUNC('month', payment_date), 'Mon') AS mes,
                    DATE_TRUNC('month', payment_date) AS fecha,
                    COALESCE(SUM(total_paid), 0)
                FROM payments
                WHERE payment_date >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY DATE_TRUNC('month', payment_date)
                ORDER BY fecha
            """)
            data["income_chart"] = cur.fetchall()

            cur.execute("""
                SELECT
                    TO_CHAR(DATE_TRUNC('month', expense_date), 'Mon') AS mes,
                    DATE_TRUNC('month', expense_date) AS fecha,
                    COALESCE(SUM(amount), 0)
                FROM expenses
                WHERE expense_date >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY DATE_TRUNC('month', expense_date)
                ORDER BY fecha
            """)
            data["expense_chart"] = cur.fetchall()

            cur.execute("""
                SELECT
                    p.first_name || ' ' || p.last_name AS nombre,
                    p.birthdate,
                    EXTRACT(DAY FROM AGE(
                        DATE_TRUNC('year', CURRENT_DATE) +
                        (DATE_TRUNC('year', CURRENT_DATE) - DATE_TRUNC('year', p.birthdate)) +
                        (p.birthdate - DATE_TRUNC('year', p.birthdate)),
                        CURRENT_DATE
                    )) AS dias
                FROM people p
                JOIN students s ON s.id_person = p.id
                WHERE p.birthdate IS NOT NULL
                AND (
                    TO_CHAR(p.birthdate, 'MM-DD') >= TO_CHAR(CURRENT_DATE, 'MM-DD')
                    AND TO_CHAR(p.birthdate, 'MM-DD') <= TO_CHAR(CURRENT_DATE + INTERVAL '30 days', 'MM-DD')
                )
                ORDER BY TO_CHAR(p.birthdate, 'MM-DD')
                LIMIT 5
            """)
            data["birthdays"] = cur.fetchall()

            cur.execute("""
                SELECT
                    p.first_name || ' ' || p.last_name AS nombre,
                    sm.end_date,
                    COALESCE(mp.name, 'Plan') AS plan
                FROM student_memberships sm
                JOIN students s ON s.id = sm.id_student
                JOIN people p ON p.id = s.id_person
                LEFT JOIN membership_plans mp ON mp.id = sm.id_membership_plan
                WHERE sm.end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
                AND sm.status = 'activo'
                ORDER BY sm.end_date
                LIMIT 5
            """)
            data["expiring_detail"] = cur.fetchall()

            cur.execute("""
                SELECT
                    COALESCE(sc.name, 'Sin nombre') AS clase,
                    COALESCE(ma.name, '—') AS arte,
                    COALESCE(p.first_name || ' ' || p.last_name, 'Sin instructor') AS instructor
                FROM classes c
                LEFT JOIN schedule sc ON sc.id = c.id_schedule
                LEFT JOIN martial_arts ma ON ma.id = sc.id_martial_art
                LEFT JOIN instructors i ON i.id = c.id_instructor
                LEFT JOIN people p ON p.id = i.id_person
                WHERE c.date = CURRENT_DATE
                ORDER BY c.id DESC
                LIMIT 8
            """)
            data["classes_detail"] = cur.fetchall()

        except Exception as e:
            print(f"[Dashboard error] {e}")
            for k in ["students_active","income_month","expenses_month","classes_today",
                      "memberships_expiring","students_new","income_chart","expense_chart",
                      "birthdays","expiring_detail","classes_detail"]:
                data.setdefault(k, 0 if k not in
                    ["income_chart","expense_chart","birthdays","expiring_detail","classes_detail"] else [])
        finally:
            cur.close()
            self.db.release(conn)

        self.data_ready.emit(data)


# ═══════════════════════════════════════════════════════════════════════
# ANIMATED NUMBER LABEL — cuenta desde 0 hasta el valor final
# ═══════════════════════════════════════════════════════════════════════
class AnimatedValueLabel(QLabel):
    def __init__(self, prefix="", suffix="", parent=None):
        super().__init__("—", parent)
        self._prefix = prefix
        self._suffix = suffix
        self._target = 0
        self._current = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._steps = 0
        self._step_val = 0.0
        self.setStyleSheet(
            f"font-size: 28px; font-weight: 900; color: {TEXT_PRI}; "
            f"background: transparent; border: none; letter-spacing: -0.5px;"
        )

    def animate_to(self, value: float, is_currency=False):
        self._is_currency = is_currency
        self._target = value
        self._current = 0.0
        self._steps = 30
        self._step_val = value / self._steps if self._steps else value
        self._timer.start(20)

    def _tick(self):
        self._current += self._step_val
        self._steps -= 1
        if self._steps <= 0:
            self._current = self._target
            self._timer.stop()
        self._update_text(self._current)

    def _update_text(self, val):
        if hasattr(self, "_is_currency") and self._is_currency:
            if val >= 1_000_000:
                txt = f"${val/1_000_000:.1f}M"
            elif val >= 1_000:
                txt = f"${val:,.0f}"
            else:
                txt = f"${val:.0f}"
        else:
            txt = str(int(val))
        self.setText(f"{self._prefix}{txt}{self._suffix}")


# ═══════════════════════════════════════════════════════════════════════
# PREMIUM CHART — líneas suavizadas con gradiente de área
# ═══════════════════════════════════════════════════════════════════════
class PremiumChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.income_vals  = []
        self.expense_vals = []
        self.labels       = []
        self.setMinimumHeight(160)
        self.setStyleSheet("background: transparent;")

    def set_data(self, income, expenses):
        months_i = {r[0]: float(r[2]) for r in income}
        months_e = {r[0]: float(r[2]) for r in expenses}
        all_months = sorted(set(list(months_i.keys()) + list(months_e.keys())))
        self.labels       = all_months
        self.income_vals  = [months_i.get(m, 0) for m in all_months]
        self.expense_vals = [months_e.get(m, 0) for m in all_months]
        self.update()

    def _smooth_points(self, pts):
        """Catmull-Rom spline — curva suave entre puntos."""
        if len(pts) < 2:
            return pts
        result = []
        for i in range(len(pts) - 1):
            p0 = pts[max(i - 1, 0)]
            p1 = pts[i]
            p2 = pts[i + 1]
            p3 = pts[min(i + 2, len(pts) - 1)]
            for t in [j / 10 for j in range(10)]:
                x = 0.5 * ((2*p1[0]) + (-p0[0]+p2[0])*t +
                    (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t*t +
                    (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t*t*t)
                y = 0.5 * ((2*p1[1]) + (-p0[1]+p2[1])*t +
                    (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t*t +
                    (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t*t*t)
                result.append((x, y))
        result.append(pts[-1])
        return result

    def paintEvent(self, event):
        if not self.labels or len(self.labels) < 2:
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setPen(QColor(TEXT_MUT))
            p.setFont(QFont("Arial", 11))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Sin datos disponibles")
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        pad_l, pad_r, pad_t, pad_b = 8, 8, 12, 28

        all_vals = self.income_vals + self.expense_vals
        max_val = max(all_vals) if max(all_vals) > 0 else 1

        n = len(self.labels)

        def to_xy(i, val):
            x = pad_l + i * (w - pad_l - pad_r) / (n - 1)
            y = pad_t + (1 - val / max_val) * (h - pad_t - pad_b)
            return (x, y)

        raw_i = [to_xy(i, v) for i, v in enumerate(self.income_vals)]
        raw_e = [to_xy(i, v) for i, v in enumerate(self.expense_vals)]
        pts_i = self._smooth_points(raw_i)
        pts_e = self._smooth_points(raw_e)

        def draw_area(pts, raw, color_hex, alpha=30):
            if not pts:
                return
            path = QPainterPath()
            path.moveTo(pts[0][0], pts[0][1])
            for x, y in pts[1:]:
                path.lineTo(x, y)
            # Cerrar hacia abajo
            path.lineTo(raw[-1][0], h - pad_b)
            path.lineTo(raw[0][0], h - pad_b)
            path.closeSubpath()

            grad = QLinearGradient(0, pad_t, 0, h - pad_b)
            c = QColor(color_hex)
            c.setAlpha(alpha)
            grad.setColorAt(0, c)
            c2 = QColor(color_hex); c2.setAlpha(0)
            grad.setColorAt(1, c2)
            p.setBrush(QBrush(grad))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawPath(path)

        def draw_line(pts, color_hex, width=2):
            if not pts:
                return
            pen = QPen(QColor(color_hex))
            pen.setWidthF(width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            path = QPainterPath()
            path.moveTo(pts[0][0], pts[0][1])
            for x, y in pts[1:]:
                path.lineTo(x, y)
            p.drawPath(path)

        # Líneas de referencia horizontales
        pen_grid = QPen(QColor(BORDER))
        pen_grid.setWidthF(0.5)
        p.setPen(pen_grid)
        for frac in [0.25, 0.5, 0.75, 1.0]:
            y = pad_t + (1 - frac) * (h - pad_t - pad_b)
            p.drawLine(QPointF(pad_l, y), QPointF(w - pad_r, y))

        # Áreas y líneas
        draw_area(pts_i, raw_i, GREEN, 35)
        draw_area(pts_e, raw_e, RED, 25)
        draw_line(pts_i, GREEN, 2.0)
        draw_line(pts_e, RED, 2.0)

        # Dots en puntos reales
        for rx, ry in raw_i:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(BG_CARD))
            p.drawEllipse(QPointF(rx, ry), 5, 5)
            p.setBrush(QColor(GREEN))
            p.drawEllipse(QPointF(rx, ry), 3, 3)

        for rx, ry in raw_e:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(BG_CARD))
            p.drawEllipse(QPointF(rx, ry), 5, 5)
            p.setBrush(QColor(RED))
            p.drawEllipse(QPointF(rx, ry), 3, 3)

        # Labels meses
        p.setFont(QFont("Arial", 8))
        p.setPen(QColor(TEXT_MUT))
        for i, lbl in enumerate(self.labels):
            rx, _ = to_xy(i, 0)
            p.drawText(int(rx) - 12, h - 6, lbl)

        p.end()


# ═══════════════════════════════════════════════════════════════════════
# KPI CARD — premium con animación de entrada y glow
# ═══════════════════════════════════════════════════════════════════════
class KpiCard(QFrame):
    def __init__(self, label: str, icon: str, accent: str,
                 accent_dim: str, is_currency=False, parent=None):
        super().__init__(parent)
        self._accent = accent
        self._is_currency = is_currency

        self.setMinimumHeight(108)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
        """)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(6)

        # Top row: icon pill + label
        top = QHBoxLayout()
        top.setSpacing(10)

        icon_pill = QFrame()
        icon_pill.setFixedSize(36, 36)
        icon_pill.setStyleSheet(f"""
            QFrame {{
                background-color: {accent_dim};
                border-radius: 10px;
                border: none;
            }}
        """)
        icon_l = QHBoxLayout(icon_pill)
        icon_l.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 16px; background: transparent; border: none;")
        icon_l.addWidget(icon_lbl)

        lbl_title = QLabel(label.upper())
        lbl_title.setStyleSheet(
            f"font-size: 9px; font-weight: 800; letter-spacing: 1.2px; "
            f"color: {TEXT_MUT}; background: transparent; border: none;"
        )
        lbl_title.setWordWrap(True)

        top.addWidget(icon_pill)
        top.addWidget(lbl_title, 1)
        layout.addLayout(top)

        # Value
        self.lbl_value = AnimatedValueLabel()
        layout.addWidget(self.lbl_value)

        # Accent bottom line
        line = QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {accent}, stop:1 transparent);
            border: none; border-radius: 1px;
        """)
        layout.addWidget(line)

    def set_value(self, val):
        self.lbl_value.animate_to(val, self._is_currency)

    def enterEvent(self, event):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD_2};
                border: 1px solid {self._accent};
                border-radius: 14px;
            }}
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
        """)
        super().leaveEvent(event)


# ═══════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════
def _card(accent_left=None):
    card = QFrame()
    border_left = f"border-left: 3px solid {accent_left};" if accent_left else ""
    card.setStyleSheet(f"""
        QFrame {{
            background-color: {BG_CARD};
            border: 1px solid {BORDER};
            {border_left}
            border-radius: 14px;
        }}
        QFrame * {{ border: none; background: transparent; }}
    """)
    shadow = QGraphicsDropShadowEffect(card)
    shadow.setBlurRadius(16); shadow.setOffset(0, 3)
    shadow.setColor(QColor(0, 0, 0, 60))
    card.setGraphicsEffect(shadow)
    return card


def _section_lbl(text):
    l = QLabel(text)
    l.setStyleSheet(
        f"font-size: 10px; font-weight: 800; letter-spacing: 1.4px; "
        f"color: {TEXT_MUT}; padding-bottom: 6px;"
    )
    return l


def _sep():
    f = QFrame(); f.setFixedHeight(1)
    f.setStyleSheet(f"background: {BORDER}; border: none;")
    return f


INPUT_STYLE = f"""
    QLineEdit, QComboBox {{
        background: {BG_INPUT}; color: {TEXT_PRI};
        border: 1.5px solid {BORDER_2}; border-radius: 8px;
        padding: 0 12px; font-size: 13px; min-height: 38px;
    }}
    QLineEdit:focus, QComboBox:focus {{ border-color: {RED}; }}
    QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox QAbstractItemView {{
        background: {BG_INPUT}; color: {TEXT_PRI};
        selection-background-color: {RED};
    }}
"""


# ═══════════════════════════════════════════════════════════════════════
# DASHBOARD VIEW
# ═══════════════════════════════════════════════════════════════════════
class DashboardView(QWidget):
    def __init__(self, db, user):
        super().__init__()
        self.db   = db
        self.user = user
        self._build_ui()
        self._load_data()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._load_data)
        self._timer.start(60_000)

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {BG_MAIN}; color: {TEXT_PRI};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: transparent; width: 4px; }
            QScrollBar::handle:vertical { background: #2A2A2A; border-radius: 2px; min-height: 20px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        container = QWidget()
        container.setStyleSheet(f"background-color: {BG_MAIN};")
        main = QVBoxLayout(container)
        main.setContentsMargins(28, 24, 28, 24)
        main.setSpacing(20)

        # ── Header ──────────────────────────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(0)

        left_hdr = QVBoxLayout()
        left_hdr.setSpacing(2)
        greeting = self._get_greeting()
        username = str(self.user.get("username", "")).capitalize()
        lbl_greeting = QLabel(f"{greeting}, {username}!")
        lbl_greeting.setStyleSheet(
            f"font-size: 11px; font-weight: 600; color: {TEXT_MUT}; letter-spacing: 0.5px;"
        )
        lbl_title = QLabel("Dashboard")
        lbl_title.setStyleSheet(
            f"font-size: 28px; font-weight: 900; color: {TEXT_PRI}; letter-spacing: -0.5px;"
        )
        left_hdr.addWidget(lbl_greeting)
        left_hdr.addWidget(lbl_title)

        now = datetime.now().strftime("%A %d de %B, %Y").capitalize()
        date_pill = QFrame()
        date_pill.setFixedHeight(36)
        date_pill.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 10px;
            }}
            QFrame * {{ border: none; background: transparent; }}
        """)
        dp = QHBoxLayout(date_pill)
        dp.setContentsMargins(14, 0, 14, 0); dp.setSpacing(6)
        dp.addWidget(QLabel("📅"))
        date_lbl = QLabel(now)
        date_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 600;")
        dp.addWidget(date_lbl)

        hdr.addLayout(left_hdr)
        hdr.addStretch()
        hdr.addWidget(date_pill)
        main.addLayout(hdr)

        # Separator gradient
        sep_hdr = QFrame(); sep_hdr.setFixedHeight(1)
        sep_hdr.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.3 {RED}, stop:1 transparent);
            border: none;
        """)
        main.addWidget(sep_hdr)

        # ── KPI Grid (2 filas x 3 cols) ─────────────────────────
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(12)

        self.kpi_students = KpiCard("Estudiantes Activos", "👥", BLUE,   BLUE_DIM)
        self.kpi_income   = KpiCard("Ingresos del Mes",    "💰", GREEN,  GREEN_DIM,  is_currency=True)
        self.kpi_expenses = KpiCard("Gastos del Mes",      "📉", ORANGE, ORANGE_DIM, is_currency=True)
        self.kpi_classes  = KpiCard("Clases Hoy",          "🥋", RED,    RED_DIM)
        self.kpi_expiring = KpiCard("Vencen en 7 días",    "⚠️", YELLOW, YELLOW_DIM)
        self.kpi_new      = KpiCard("Nuevos Este Mes",     "✨", PURPLE, PURPLE_DIM)

        for col, kpi in enumerate([self.kpi_students, self.kpi_income, self.kpi_expenses]):
            kpi_grid.addWidget(kpi, 0, col)
        for col, kpi in enumerate([self.kpi_classes, self.kpi_expiring, self.kpi_new]):
            kpi_grid.addWidget(kpi, 1, col)

        main.addLayout(kpi_grid)

        # ── Fila media: gráfico + sidebar derecho ────────────────
        mid = QHBoxLayout(); mid.setSpacing(14)

        # Gráfico financiero
        fin_card = _card(GREEN)
        fl = QVBoxLayout(fin_card)
        fl.setContentsMargins(20, 18, 20, 18); fl.setSpacing(10)

        fin_hdr = QHBoxLayout()
        fin_hdr.addWidget(_section_lbl("📊  FINANZAS — ÚLTIMOS 6 MESES"))
        fin_hdr.addStretch()
        legend = QHBoxLayout(); legend.setSpacing(16)
        for color, txt in [(GREEN, "Ingresos"), (RED, "Gastos")]:
            leg_row = QHBoxLayout(); leg_row.setSpacing(6)
            dot = QFrame()
            dot.setFixedSize(8, 8)
            dot.setStyleSheet(f"background: {color}; border-radius: 4px; border: none;")
            lbl = QLabel(txt)
            lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 600;")
            leg_row.addWidget(dot); leg_row.addWidget(lbl)
            legend.addLayout(leg_row)
        fin_hdr.addLayout(legend)
        fl.addLayout(fin_hdr)
        fl.addWidget(_sep())

        self.chart = PremiumChart()
        fl.addWidget(self.chart, 1)
        mid.addWidget(fin_card, 3)

        # Columna derecha: cumpleaños + vencimientos
        right_col = QVBoxLayout(); right_col.setSpacing(14)

        bday_card = _card(PURPLE)
        bl = QVBoxLayout(bday_card)
        bl.setContentsMargins(18, 16, 18, 16); bl.setSpacing(8)
        bl.addWidget(_section_lbl("🎂  CUMPLEAÑOS PRÓXIMOS"))
        bl.addWidget(_sep())
        self.bday_layout = QVBoxLayout(); self.bday_layout.setSpacing(6)
        bl.addLayout(self.bday_layout)
        bl.addStretch()
        right_col.addWidget(bday_card)

        exp_card = _card(YELLOW)
        el = QVBoxLayout(exp_card)
        el.setContentsMargins(18, 16, 18, 16); el.setSpacing(8)
        el.addWidget(_section_lbl("⚠️  MEMBRESÍAS POR VENCER"))
        el.addWidget(_sep())
        self.exp_layout = QVBoxLayout(); self.exp_layout.setSpacing(6)
        el.addLayout(self.exp_layout)
        el.addStretch()
        right_col.addWidget(exp_card)

        mid.addLayout(right_col, 2)
        main.addLayout(mid)

        # ── Tareas ───────────────────────────────────────────────
        tasks_card = _card(BLUE)
        tl = QVBoxLayout(tasks_card)
        tl.setContentsMargins(20, 18, 20, 18); tl.setSpacing(10)

        tasks_hdr = QHBoxLayout()
        tasks_hdr.addWidget(_section_lbl("✅  TAREAS"))
        tasks_hdr.addStretch()

        self.btn_add_task = QPushButton("＋ Nueva tarea")
        self.btn_add_task.setFixedHeight(32)
        self.btn_add_task.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_task.setStyleSheet(f"""
            QPushButton {{
                background: {RED}; color: white;
                border: none; border-radius: 8px;
                font-size: 11px; font-weight: 800; padding: 0 14px;
            }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        self.btn_add_task.clicked.connect(self._add_task)
        tasks_hdr.addWidget(self.btn_add_task)
        tl.addLayout(tasks_hdr)
        tl.addWidget(_sep())

        self.tasks_scroll = QScrollArea()
        self.tasks_scroll.setWidgetResizable(True)
        self.tasks_scroll.setStyleSheet("border: none; background: transparent;")
        self.tasks_scroll.setMaximumHeight(220)

        self.tasks_container = QWidget()
        self.tasks_container.setStyleSheet("background: transparent;")
        self.tasks_vbox = QVBoxLayout(self.tasks_container)
        self.tasks_vbox.setContentsMargins(0, 0, 0, 0)
        self.tasks_vbox.setSpacing(5)
        self.tasks_vbox.addStretch()
        self.tasks_scroll.setWidget(self.tasks_container)
        tl.addWidget(self.tasks_scroll)

        main.addWidget(tasks_card)

        # Status bar
        self.lbl_status = QLabel("Cargando...")
        self.lbl_status.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 10px; font-weight: 500;"
        )
        main.addWidget(self.lbl_status)

        scroll.setWidget(container)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

    def _get_greeting(self):
        h = datetime.now().hour
        if h < 12: return "Buenos días"
        if h < 18: return "Buenas tardes"
        return "Buenas noches"

    # ── Data loading ─────────────────────────────────────────────
    def _load_data(self):
        self.lbl_status.setText("Actualizando...")
        self.worker = DashboardWorker(self.db)
        self.worker.data_ready.connect(self._on_data)
        self.worker.start()

    def _on_data(self, data):
        # KPIs con animación
        self.kpi_students.set_value(data.get("students_active", 0))
        self.kpi_income.set_value(data.get("income_month", 0))
        self.kpi_expenses.set_value(data.get("expenses_month", 0))
        self.kpi_classes.set_value(data.get("classes_today", 0))
        self.kpi_expiring.set_value(data.get("memberships_expiring", 0))
        self.kpi_new.set_value(data.get("students_new", 0))

        # Gráfico
        self.chart.set_data(data.get("income_chart", []), data.get("expense_chart", []))

        # Cumpleaños
        self._clear_layout(self.bday_layout)
        birthdays = data.get("birthdays", [])
        if birthdays:
            for nombre, birthdate, _ in birthdays:
                row = self._info_row(
                    "🎂", nombre,
                    birthdate.strftime("%d/%m") if birthdate else "—",
                    PURPLE
                )
                self.bday_layout.addWidget(row)
        else:
            self.bday_layout.addWidget(self._empty_lbl("Sin cumpleaños próximos"))

        # Vencimientos
        self._clear_layout(self.exp_layout)
        expiring = data.get("expiring_detail", [])
        if expiring:
            for nombre, end_date, plan in expiring:
                row = self._info_row(
                    "⚠️", nombre,
                    end_date.strftime("%d/%m") if end_date else "—",
                    YELLOW
                )
                self.exp_layout.addWidget(row)
        else:
            self.exp_layout.addWidget(self._empty_lbl("Sin vencimientos próximos"))

        # Tareas
        self._render_tasks(data.get("tasks", []))

        now = datetime.now().strftime("%H:%M:%S")
        self.lbl_status.setText(f"Última actualización: {now}  ·  Auto-refresh cada 60s")

    def _info_row(self, icon: str, name: str, date_str: str, accent: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"""
            QWidget {{
                background: {BG_CARD_2}; border-radius: 8px;
            }}
            QWidget:hover {{ background: #181818; }}
        """)
        hl = QHBoxLayout(w)
        hl.setContentsMargins(10, 7, 10, 7); hl.setSpacing(10)

        ic = QLabel(icon)
        ic.setStyleSheet("font-size: 13px; background: transparent; border: none;")
        ic.setFixedWidth(18)

        lbl_n = QLabel(name)
        lbl_n.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px; font-weight: 500; background: transparent; border: none;")

        lbl_d = QLabel(date_str)
        lbl_d.setStyleSheet(
            f"color: {accent}; font-size: 11px; font-weight: 800; "
            f"background: transparent; border: none;"
        )
        lbl_d.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        hl.addWidget(ic); hl.addWidget(lbl_n, 1); hl.addWidget(lbl_d)
        return w

    def _empty_lbl(self, text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; padding: 4px 0;")
        return l

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ── Tasks ────────────────────────────────────────────────────
    def _refresh_tasks(self):
        conn = self.db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT t.id, t.task, tt.name, t.limit_date
                FROM tasks t
                LEFT JOIN type_task tt ON tt.id = t.id_type_task
                ORDER BY t.limit_date ASC NULLS LAST, t.id DESC
                LIMIT 20
            """)
            tasks = cur.fetchall()
            cur.close()
            self._render_tasks(tasks)
        except Exception as e:
            print(f"[Tasks error] {e}")
        finally:
            self.db.release(conn)

    def _render_tasks(self, tasks):
        self._clear_layout(self.tasks_vbox)

        if not tasks:
            lbl = QLabel("No hay tareas pendientes 🎉")
            lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; padding: 8px 0;")
            self.tasks_vbox.addWidget(lbl)
            self.tasks_vbox.addStretch()
            return

        for task_id, task_text, task_type, limit_date in tasks:
            row_w = QWidget()
            row_w.setStyleSheet(f"""
                QWidget {{ background: {BG_CARD_2}; border-radius: 8px; }}
                QWidget:hover {{ background: #181818; }}
            """)
            row_l = QHBoxLayout(row_w)
            row_l.setContentsMargins(12, 8, 12, 8); row_l.setSpacing(10)

            # Botón completar
            btn_done = QPushButton("○")
            btn_done.setFixedSize(22, 22)
            btn_done.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_done.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {TEXT_DIM};
                    border: 1.5px solid {BORDER_2}; border-radius: 11px; font-size: 10px;
                }}
                QPushButton:hover {{ border-color: {GREEN}; color: {GREEN}; }}
            """)
            btn_done.clicked.connect(lambda _, tid=task_id: self._complete_task(tid))

            # Texto
            lbl_task = QLabel(task_text)
            lbl_task.setStyleSheet(
                f"color: {TEXT_PRI}; font-size: 12px; font-weight: 500; background: transparent; border: none;"
            )
            lbl_task.setWordWrap(True)

            row_l.addWidget(btn_done)
            row_l.addWidget(lbl_task, 1)

            # Badge tipo
            if task_type:
                badge = QLabel(task_type)
                badge.setStyleSheet(f"""
                    color: {BLUE}; font-size: 9px; font-weight: 800;
                    border: 1px solid rgba(59,130,246,0.4); border-radius: 5px;
                    padding: 2px 7px; background: {BLUE_DIM};
                """)
                badge.setFixedHeight(18)
                row_l.addWidget(badge)

            # Badge fecha
            if limit_date:
                today = date.today()
                days_left = (limit_date - today).days
                if days_left < 0:
                    due_text, due_color, due_bg = f"Vencida {abs(days_left)}d", RED, RED_DIM
                elif days_left == 0:
                    due_text, due_color, due_bg = "Hoy", YELLOW, YELLOW_DIM
                elif days_left <= 3:
                    due_text, due_color, due_bg = f"{days_left}d", ORANGE, ORANGE_DIM
                else:
                    due_text, due_color, due_bg = f"{days_left}d", BLUE, BLUE_DIM

                badge_d = QLabel(due_text)
                badge_d.setStyleSheet(f"""
                    color: {due_color}; font-size: 9px; font-weight: 800;
                    border: 1px solid {due_color}; border-radius: 5px;
                    padding: 2px 7px; background: {due_bg};
                """)
                badge_d.setFixedHeight(18)
                row_l.addWidget(badge_d)

            # Botón eliminar
            btn_del = QPushButton("✕")
            btn_del.setFixedSize(20, 20)
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {TEXT_DIM};
                    border: none; font-size: 10px;
                }}
                QPushButton:hover {{ color: {RED_H}; }}
            """)
            btn_del.clicked.connect(lambda _, tid=task_id: self._delete_task(tid))
            row_l.addWidget(btn_del)

            self.tasks_vbox.addWidget(row_w)

        self.tasks_vbox.addStretch()

    def _complete_task(self, task_id):
        self._delete_task(task_id)

    def _delete_task(self, task_id):
        conn = self.db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            conn.commit()
            cur.close()
            self._refresh_tasks()
        except Exception as e:
            print(f"[Delete task error] {e}")
        finally:
            self.db.release(conn)

    def _add_task(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Nueva Tarea")
        dlg.setFixedSize(400, 290)
        dlg.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        dlg.setStyleSheet(f"background-color: #0E0E0E; color: {TEXT_PRI};")

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(12)

        title_lbl = QLabel("Nueva tarea")
        title_lbl.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 16px; font-weight: 900; border: none;"
        )
        layout.addWidget(title_lbl)

        lbl_desc = QLabel("Descripción")
        lbl_desc.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 700; border: none;")
        layout.addWidget(lbl_desc)
        inp = QLineEdit()
        inp.setPlaceholderText("Ej: Revisar pagos pendientes...")
        inp.setStyleSheet(INPUT_STYLE)
        layout.addWidget(inp)

        row2 = QHBoxLayout(); row2.setSpacing(12)

        tipo_col = QVBoxLayout(); tipo_col.setSpacing(4)
        lbl_tipo = QLabel("Tipo")
        lbl_tipo.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 700; border: none;")
        tipo_col.addWidget(lbl_tipo)
        cmb = QComboBox()
        cmb.setStyleSheet(INPUT_STYLE)
        conn = self.db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM type_task ORDER BY name")
            tipos = cur.fetchall()
            cur.close()
            cmb.addItem("Sin tipo", None)
            for tid, tname in tipos:
                cmb.addItem(tname, tid)
        except Exception:
            pass
        finally:
            self.db.release(conn)
        tipo_col.addWidget(cmb)
        row2.addLayout(tipo_col, 1)

        date_col = QVBoxLayout(); date_col.setSpacing(4)
        lbl_date = QLabel("Fecha límite")
        lbl_date.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 700; border: none;")
        date_col.addWidget(lbl_date)
        self._new_task_date = QDate.currentDate()
        inp_date = QLineEdit()
        inp_date.setReadOnly(True)
        inp_date.setText(self._new_task_date.toString("dd / MM / yyyy"))
        inp_date.setStyleSheet(INPUT_STYLE)
        inp_date.setCursor(Qt.CursorShape.PointingHandCursor)

        def pick_date():
            cdlg = QDialog(dlg)
            cdlg.setWindowTitle("Fecha límite")
            cdlg.setFixedSize(300, 260)
            cdlg.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
            cdlg.setStyleSheet("background-color: #111111;")
            cl = QVBoxLayout(cdlg); cl.setContentsMargins(12, 12, 12, 12); cl.setSpacing(8)
            cal = QCalendarWidget()
            cal.setGridVisible(False)
            cal.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
            cal.setMinimumDate(QDate.currentDate())
            cal.setSelectedDate(self._new_task_date)
            cal.setStyleSheet("""
                QCalendarWidget { background: #111111; color: #F0F0F0; border: none; }
                QCalendarWidget QAbstractItemView {
                    background: #111111; color: #F0F0F0;
                    selection-background-color: #C8102E; selection-color: white;
                }
                QCalendarWidget QWidget#qt_calendar_navigationbar {
                    background: #1A1A1A; min-height: 40px; border-radius: 6px;
                }
                QCalendarWidget QToolButton {
                    background: transparent; color: #F0F0F0;
                    border: none; border-radius: 4px; padding: 4px 8px;
                }
                QCalendarWidget QToolButton:hover { background: #2A2A2A; }
                QCalendarWidget QToolButton::menu-indicator { image: none; }
                QCalendarWidget QSpinBox {
                    background: #1A1A1A; color: #F0F0F0;
                    border: 1px solid #2A2A2A; border-radius: 4px; padding: 2px 6px;
                }
            """)
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(RED))
            cal.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, fmt)
            cal.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, fmt)
            btn_ok = QPushButton("Confirmar")
            btn_ok.setFixedHeight(34)
            btn_ok.setStyleSheet(f"""
                QPushButton {{ background: {RED}; color: white; border: none;
                    border-radius: 7px; font-size: 13px; font-weight: 700; }}
                QPushButton:hover {{ background: {RED_H}; }}
            """)
            def confirm():
                self._new_task_date = cal.selectedDate()
                inp_date.setText(self._new_task_date.toString("dd / MM / yyyy"))
                cdlg.accept()
            btn_ok.clicked.connect(confirm)
            cal.activated.connect(lambda _: confirm())
            cl.addWidget(cal); cl.addWidget(btn_ok)
            cdlg.exec()

        inp_date.mousePressEvent = lambda e: pick_date()
        date_col.addWidget(inp_date)
        row2.addLayout(date_col, 1)
        layout.addLayout(row2)

        btn_row = QHBoxLayout(); btn_row.setSpacing(10)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER_2}; border-radius: 8px; font-size: 13px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; }}
        """)
        btn_cancel.clicked.connect(dlg.reject)

        btn_save = QPushButton("Crear Tarea")
        btn_save.setFixedHeight(38)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white;
                border: none; border-radius: 8px; font-size: 13px; font-weight: 800; }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)

        def save():
            text = inp.text().strip()
            if not text:
                return
            tipo_id = cmb.currentData()
            conn2 = self.db.get_conn()
            try:
                cur2 = conn2.cursor()
                cur2.execute(
                    "INSERT INTO tasks (task, id_type_task, limit_date) VALUES (%s, %s, %s)",
                    (text, tipo_id, self._new_task_date.toPyDate())
                )
                conn2.commit()
                cur2.close()
                dlg.accept()
                self._refresh_tasks()
            except Exception as e:
                print(f"[Add task error] {e}")
            finally:
                self.db.release(conn2)

        btn_save.clicked.connect(save)
        inp.returnPressed.connect(save)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)
        dlg.exec()