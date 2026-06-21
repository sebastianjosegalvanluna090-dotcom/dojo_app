from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy, QScrollArea, QGridLayout, QPushButton,
    QDialog, QLineEdit, QComboBox, QDateEdit
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QDate
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QPolygonF
from PyQt6.QtCore import QPointF
from datetime import datetime

BG_MAIN   = "#0D0D0D"
BG_CARD   = "#161616"
BG_TABLE  = "#121212"
BORDER    = "#2A2A2A"
RED       = "#C8102E"
RED_DARK  = "#7A0A1C"
TEXT_PRI  = "#F0F0F0"
TEXT_SEC  = "#999999"
TEXT_MUT  = "#444444"
GREEN     = "#22C55E"
YELLOW    = "#EAB308"
BLUE      = "#3B82F6"
PURPLE    = "#A855F7"
ORANGE    = "#F97316"


# ─── Worker ───────────────────────────────────────────────────────────
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

            # KPI: estudiantes activos
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

            # KPI: ingresos mes
            cur.execute("""
                SELECT COALESCE(SUM(total_paid), 0) FROM payments
                WHERE DATE_TRUNC('month', payment_date) = DATE_TRUNC('month', CURRENT_DATE)
            """)
            data["income_month"] = float((cur.fetchone() or [0])[0])

            # KPI: gastos mes
            cur.execute("""
                SELECT COALESCE(SUM(amount), 0) FROM expenses
                WHERE DATE_TRUNC('month', expense_date) = DATE_TRUNC('month', CURRENT_DATE)
            """)
            data["expenses_month"] = float((cur.fetchone() or [0])[0])

            # KPI: clases hoy
            cur.execute("SELECT COUNT(*) FROM classes WHERE date = CURRENT_DATE")
            data["classes_today"] = (cur.fetchone() or [0])[0]

            # Tareas pendientes
            cur.execute("""
                SELECT t.id, t.task, tt.name, t.limit_date
                FROM tasks t
                LEFT JOIN type_task tt ON tt.id = t.id_type_task
                ORDER BY t.limit_date ASC NULLS LAST, t.id DESC
                LIMIT 20
            """)
            data["tasks"] = cur.fetchall()

            # KPI: membresias por vencer (próximos 7 días)
            cur.execute("""
                SELECT COUNT(*) FROM student_memberships
                WHERE end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
                AND status = 'activo'
            """)
            data["memberships_expiring"] = (cur.fetchone() or [0])[0]

            # KPI: nuevos este mes
            cur.execute("""
                SELECT COUNT(*) FROM students s
                JOIN people p ON p.id = s.id_person
                WHERE DATE_TRUNC('month', p.created_at) = DATE_TRUNC('month', CURRENT_DATE)
            """)
            data["students_new"] = (cur.fetchone() or [0])[0]

            # Gráfico: ingresos y gastos últimos 6 meses
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

            # Cumpleaños próximos 30 días
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

            # Membresías por vencer — detalle
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

            # Clases hoy detalle
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
                data.setdefault(k, 0 if "chart" not in k and k not in
                               ["income_chart","expense_chart","birthdays","expiring_detail","classes_detail"] else [])
        finally:
            cur.close()
            self.db.release(conn)

        self.data_ready.emit(data)


# ─── Mini gráfico de líneas ───────────────────────────────────────────
class MiniChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.income_data  = []
        self.expense_data = []
        self.labels       = []
        self.setMinimumHeight(120)

    def set_data(self, income, expenses):
        self.income_data  = income
        self.expense_data = expenses
        # Alinear labels por mes
        months_i = {r[0]: float(r[2]) for r in income}
        months_e = {r[0]: float(r[2]) for r in expenses}
        all_months = sorted(set(list(months_i.keys()) + list(months_e.keys())))
        self.labels        = all_months
        self.income_vals   = [months_i.get(m, 0) for m in all_months]
        self.expense_vals  = [months_e.get(m, 0) for m in all_months]
        self.update()

    def paintEvent(self, event):
        if not self.labels:
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        pad_l, pad_r, pad_t, pad_b = 10, 10, 10, 28

        all_vals = self.income_vals + self.expense_vals
        max_val  = max(all_vals) if max(all_vals) > 0 else 1

        n = len(self.labels)
        if n < 2:
            return

        def to_pt(i, val):
            x = pad_l + i * (w - pad_l - pad_r) / (n - 1)
            y = pad_t + (1 - val / max_val) * (h - pad_t - pad_b)
            return QPointF(x, y)

        # Área rellena ingresos
        poly_i = QPolygonF([to_pt(i, v) for i, v in enumerate(self.income_vals)])
        poly_i.append(QPointF(to_pt(n-1, 0).x(), h - pad_b))
        poly_i.append(QPointF(to_pt(0, 0).x(), h - pad_b))
        brush_i = QBrush(QColor(34, 197, 94, 40))
        p.setBrush(brush_i)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPolygon(poly_i)

        # Área rellena gastos
        poly_e = QPolygonF([to_pt(i, v) for i, v in enumerate(self.expense_vals)])
        poly_e.append(QPointF(to_pt(n-1, 0).x(), h - pad_b))
        poly_e.append(QPointF(to_pt(0, 0).x(), h - pad_b))
        brush_e = QBrush(QColor(200, 16, 46, 30))
        p.setBrush(brush_e)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPolygon(poly_e)

        # Línea ingresos
        pen_i = QPen(QColor(GREEN)); pen_i.setWidth(2)
        p.setPen(pen_i); p.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(n - 1):
            p.drawLine(to_pt(i, self.income_vals[i]), to_pt(i+1, self.income_vals[i+1]))

        # Línea gastos
        pen_e = QPen(QColor(RED)); pen_e.setWidth(2)
        p.setPen(pen_e)
        for i in range(n - 1):
            p.drawLine(to_pt(i, self.expense_vals[i]), to_pt(i+1, self.expense_vals[i+1]))

        # Puntos y labels
        p.setFont(QFont("Arial", 8))
        for i, lbl in enumerate(self.labels):
            pt = to_pt(i, self.income_vals[i])
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(GREEN))
            p.drawEllipse(pt, 3, 3)

            pt_e = to_pt(i, self.expense_vals[i])
            p.setBrush(QColor(RED))
            p.drawEllipse(pt_e, 3, 3)

            p.setPen(QColor(TEXT_MUT))
            p.drawText(int(to_pt(i, 0).x()) - 12, h - 6, lbl)

        p.end()


# ─── Card base ────────────────────────────────────────────────────────
def make_card(accent=None):
    card = QFrame()
    border_left = f"border-left: 3px solid {accent};" if accent else ""
    card.setStyleSheet(f"""
        QFrame {{
            background-color: {BG_CARD};
            border: 1px solid {BORDER};
            {border_left}
            border-radius: 10px;
        }}
        QFrame * {{ border: none; background: transparent; }}
    """)
    return card


def section_title(text):
    lbl = QLabel(text)
    lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; letter-spacing: 1px; color: {TEXT_MUT}; padding-bottom: 4px;")
    return lbl


# ─── DASHBOARD VIEW ───────────────────────────────────────────────────
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
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        container.setStyleSheet(f"background-color: {BG_MAIN};")
        main = QVBoxLayout(container)
        main.setContentsMargins(28, 24, 28, 24)
        main.setSpacing(16)

        # ── Header
        hdr = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_PRI};")
        now = datetime.now().strftime("%A %d de %B, %Y").capitalize()
        date_lbl = QLabel(now)
        date_lbl.setStyleSheet(f"font-size: 12px; color: {TEXT_SEC};")
        date_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        hdr.addWidget(title); hdr.addStretch(); hdr.addWidget(date_lbl)
        main.addLayout(hdr)

        # Separador
        sep = QFrame(); sep.setFixedHeight(2)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.5 {RED_DARK}, stop:1 transparent);
            border: none;
        """)
        main.addWidget(sep)

        # ── Fila KPIs
        kpi_row = QHBoxLayout(); kpi_row.setSpacing(12)
        self.kpi_students   = self._kpi("Estudiantes Activos", "👥", BLUE)
        self.kpi_income     = self._kpi("Ingresos del Mes",    "💰", GREEN)
        self.kpi_expenses   = self._kpi("Gastos del Mes",      "📉", ORANGE)
        self.kpi_classes    = self._kpi("Clases Hoy",          "🥋", RED)
        self.kpi_expiring   = self._kpi("Vencen en 7 días",    "⚠️", YELLOW)
        self.kpi_new        = self._kpi("Nuevos Este Mes",     "✨", PURPLE)
        for kpi in [self.kpi_students, self.kpi_income, self.kpi_expenses,
                    self.kpi_classes, self.kpi_expiring, self.kpi_new]:
            kpi_row.addWidget(kpi[0])
        main.addLayout(kpi_row)

        # ── Fila principal: gráfico + cumpleaños + vencimientos
        mid_row = QHBoxLayout(); mid_row.setSpacing(12)

        # Gráfico ingresos vs gastos
        finance_card = make_card(GREEN)
        fl = QVBoxLayout(finance_card)
        fl.setContentsMargins(16, 14, 16, 14)
        fl.setSpacing(8)
        fl.addWidget(section_title("📊  FINANZAS — ÚLTIMOS 6 MESES"))
        legend = QHBoxLayout()
        for color, txt in [(GREEN, "Ingresos"), (RED, "Gastos")]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 12px;")
            lbl = QLabel(txt)
            lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")
            legend.addWidget(dot); legend.addWidget(lbl); legend.addSpacing(12)
        legend.addStretch()
        fl.addLayout(legend)
        self.chart = MiniChart()
        fl.addWidget(self.chart, 1)
        mid_row.addWidget(finance_card, 3)

        # Columna derecha: cumpleaños + vencimientos
        right_col = QVBoxLayout(); right_col.setSpacing(12)

        # Cumpleaños
        bday_card = make_card(PURPLE)
        bl = QVBoxLayout(bday_card)
        bl.setContentsMargins(16, 14, 16, 14); bl.setSpacing(6)
        bl.addWidget(section_title("🎂  CUMPLEAÑOS PRÓXIMOS"))
        self.bday_layout = QVBoxLayout(); self.bday_layout.setSpacing(4)
        bl.addLayout(self.bday_layout)
        bl.addStretch()
        right_col.addWidget(bday_card)

        # Membresías por vencer
        exp_card = make_card(YELLOW)
        el = QVBoxLayout(exp_card)
        el.setContentsMargins(16, 14, 16, 14); el.setSpacing(6)
        el.addWidget(section_title("⚠️  MEMBRESÍAS POR VENCER"))
        self.exp_layout = QVBoxLayout(); self.exp_layout.setSpacing(4)
        el.addLayout(self.exp_layout)
        el.addStretch()
        right_col.addWidget(exp_card)

        mid_row.addLayout(right_col, 2)
        main.addLayout(mid_row)

        # ── Tareas
        tasks_card = make_card(BLUE)
        tl = QVBoxLayout(tasks_card)
        tl.setContentsMargins(16, 14, 16, 14)
        tl.setSpacing(8)

        tasks_header = QHBoxLayout()
        tasks_header.addWidget(section_title("✅  TAREAS"))
        tasks_header.addStretch()

        self.btn_add_task = QPushButton("＋ Nueva tarea")
        self.btn_add_task.setFixedHeight(28)
        self.btn_add_task.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_task.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED}; color: white;
                border: none; border-radius: 6px;
                font-size: 11px; font-weight: 700; padding: 0 12px;
            }}
            QPushButton:hover {{ background-color: #E8152F; }}
        """)
        self.btn_add_task.clicked.connect(self._add_task)
        tasks_header.addWidget(self.btn_add_task)
        tl.addLayout(tasks_header)

        sep_t = QFrame(); sep_t.setFixedHeight(1)
        sep_t.setStyleSheet(f"background: {BORDER};")
        tl.addWidget(sep_t)

        self.tasks_scroll = QScrollArea()
        self.tasks_scroll.setWidgetResizable(True)
        self.tasks_scroll.setStyleSheet("border: none; background: transparent;")
        self.tasks_scroll.setMaximumHeight(200)

        self.tasks_container = QWidget()
        self.tasks_container.setStyleSheet("background: transparent;")
        self.tasks_vbox = QVBoxLayout(self.tasks_container)
        self.tasks_vbox.setContentsMargins(0, 0, 0, 0)
        self.tasks_vbox.setSpacing(4)
        self.tasks_vbox.addStretch()
        self.tasks_scroll.setWidget(self.tasks_container)
        tl.addWidget(self.tasks_scroll)

        main.addWidget(tasks_card)

        self.lbl_status = QLabel("Cargando...")
        self.lbl_status.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px;")
        main.addWidget(self.lbl_status)

        scroll.setWidget(container)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

    def _kpi(self, label, icon, accent):
        card = QFrame()
        card.setMinimumHeight(96)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-top: 3px solid {accent};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(2)

        top = QHBoxLayout()
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 16px; background: transparent; border: none;")
        lbl_title = QLabel(label.upper())
        lbl_title.setStyleSheet(f"font-size: 9px; font-weight: 700; letter-spacing: 1px; color: {TEXT_MUT}; background: transparent; border: none;")
        top.addWidget(lbl_icon); top.addWidget(lbl_title); top.addStretch()

        lbl_value = QLabel("—")
        lbl_value.setStyleSheet(f"font-size: 26px; font-weight: 700; color: {TEXT_PRI}; background: transparent; border: none;")

        layout.addLayout(top)
        layout.addWidget(lbl_value)
        return card, lbl_value

    def _refresh_tasks(self):
        """Recarga solo las tareas sin recargar todo el dashboard."""
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
        # Limpiar
        while self.tasks_vbox.count():
            item = self.tasks_vbox.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not tasks:
            lbl = QLabel("No hay tareas pendientes 🎉")
            lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px; padding: 8px 0;")
            self.tasks_vbox.addWidget(lbl)
            self.tasks_vbox.addStretch()
            return

        for task_id, task_text, task_type, limit_date in tasks:
            row_w = QWidget()
            row_w.setStyleSheet(f"""
                QWidget {{
                    background-color: #1A1A1A;
                    border-radius: 6px;
                }}
                QWidget:hover {{ background-color: #202020; }}
            """)
            row_l = QHBoxLayout(row_w)
            row_l.setContentsMargins(10, 6, 10, 6)
            row_l.setSpacing(10)

            btn_done = QPushButton("○")
            btn_done.setFixedSize(22, 22)
            btn_done.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_done.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {TEXT_MUT};
                    border: 1.5px solid {BORDER}; border-radius: 11px;
                    font-size: 10px;
                }}
                QPushButton:hover {{ border-color: {GREEN}; color: {GREEN}; }}
            """)
            btn_done.clicked.connect(lambda _, tid=task_id: self._complete_task(tid))

            lbl_task = QLabel(task_text)
            lbl_task.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px;")
            lbl_task.setWordWrap(True)

            if task_type:
                badge = QLabel(task_type)
                badge.setStyleSheet(f"""
                    color: {BLUE}; font-size: 10px; font-weight: 600;
                    border: 1px solid {BLUE}; border-radius: 4px;
                    padding: 1px 6px;
                """)
                badge.setFixedHeight(18)
            else:
                badge = QLabel("")

            if limit_date:
                from datetime import date
                today = date.today()
                days_left = (limit_date - today).days
                if days_left < 0:
                    due_text = f"Vencida {abs(days_left)}d"
                    due_color = RED
                elif days_left == 0:
                    due_text = "Hoy"
                    due_color = YELLOW
                elif days_left <= 3:
                    due_text = f"{days_left}d"
                    due_color = ORANGE
                else:
                    due_text = f"{days_left}d"
                    due_color = BLUE

                badge_date = QLabel(due_text)
                badge_date.setStyleSheet(f"""
                    color: {due_color}; font-size: 10px; font-weight: 600;
                    border: 1px solid {due_color}; border-radius: 4px;
                    padding: 1px 6px;
                """)
                badge_date.setFixedHeight(18)
            else:
                badge_date = None

            btn_del = QPushButton("✕")
            btn_del.setFixedSize(22, 22)
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {TEXT_MUT};
                    border: none; font-size: 11px; border-radius: 4px;
                }}
                QPushButton:hover {{ color: #FF4444; }}
            """)
            btn_del.clicked.connect(lambda _, tid=task_id: self._delete_task(tid))

            row_l.addWidget(btn_done)
            row_l.addWidget(lbl_task, 1)
            if task_type:
                row_l.addWidget(badge)
            if badge_date:
                row_l.addWidget(badge_date)
            row_l.addWidget(btn_del)

            self.tasks_vbox.addWidget(row_w)

        self.tasks_vbox.addStretch()

    def _complete_task(self, task_id):
        """Marca como completada (elimina de la lista)."""
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
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QComboBox, QPushButton, QLabel, QHBoxLayout, QDateEdit
        from PyQt6.QtCore import QDate
        dlg = QDialog(self)
        dlg.setWindowTitle("Nueva Tarea")
        dlg.setFixedSize(380, 280)
        dlg.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        dlg.setStyleSheet(f"background-color: #111111; color: {TEXT_PRI};")

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Descripción de la tarea:"))
        inp = QLineEdit()
        inp.setPlaceholderText("Ej: Revisar pagos pendientes...")
        inp.setStyleSheet(f"""
            QLineEdit {{
                background: #1C1C1C; color: {TEXT_PRI};
                border: 1.5px solid #2A2A2A; border-radius: 8px;
                padding: 0 12px; font-size: 13px; min-height: 38px;
            }}
            QLineEdit:focus {{ border-color: {RED}; }}
        """)
        layout.addWidget(inp)

        layout.addWidget(QLabel("Tipo:"))
        cmb = QComboBox()
        cmb.setStyleSheet(f"""
            QComboBox {{
                background: #1C1C1C; color: {TEXT_PRI};
                border: 1.5px solid #2A2A2A; border-radius: 8px;
                padding: 0 12px; font-size: 13px; min-height: 38px;
            }}
            QComboBox QAbstractItemView {{
                background: #1C1C1C; color: {TEXT_PRI};
                selection-background-color: {RED};
            }}
        """)
        conn = self.db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM type_task ORDER BY name")
            tipos = cur.fetchall()
            cur.close()
            cmb.addItem("Sin tipo", None)
            for tid, tname in tipos:
                cmb.addItem(tname, tid)
        except:
            pass
        finally:
            self.db.release(conn)
        layout.addWidget(cmb)

        layout.addWidget(QLabel("Fecha límite:"))
        date_container = QWidget()
        date_container.setStyleSheet("background: transparent;")
        date_hl = QHBoxLayout(date_container)
        date_hl.setContentsMargins(0, 0, 0, 0)
        date_hl.setSpacing(8)

        self._new_task_date = QDate.currentDate()
        inp_date = QLineEdit()
        inp_date.setReadOnly(True)
        inp_date.setText(self._new_task_date.toString("dd / MM / yyyy"))
        inp_date.setStyleSheet(f"""
            QLineEdit {{
                background: #1C1C1C; color: {TEXT_PRI};
                border: 1.5px solid #2A2A2A; border-radius: 8px;
                padding: 0 12px; font-size: 13px; min-height: 38px;
            }}
        """)

        btn_cal = QPushButton("📅")
        btn_cal.setFixedSize(40, 38)
        btn_cal.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cal.setStyleSheet(f"""
            QPushButton {{
                background: #222; border: 1.5px solid #2A2A2A;
                border-radius: 8px; font-size: 15px;
            }}
            QPushButton:hover {{ border-color: {RED}; }}
        """)

        def pick_date():
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCalendarWidget, QPushButton
            from PyQt6.QtGui import QTextCharFormat
            cdlg = QDialog(dlg)
            cdlg.setWindowTitle("Fecha límite")
            cdlg.setFixedSize(300, 260)
            cdlg.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
            cdlg.setStyleSheet("background-color: #141414;")
            cl = QVBoxLayout(cdlg)
            cl.setContentsMargins(12, 12, 12, 12)
            cl.setSpacing(8)
            cal = QCalendarWidget()
            cal.setGridVisible(False)
            cal.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
            cal.setMinimumDate(QDate.currentDate())
            cal.setSelectedDate(self._new_task_date)
            cal.setStyleSheet("""
                QCalendarWidget { background: #141414; color: #F0F0F0; border: none; }
                QCalendarWidget QAbstractItemView {
                    background: #141414; color: #F0F0F0;
                    selection-background-color: #C8102E; selection-color: white;
                }
                QCalendarWidget QWidget#qt_calendar_navigationbar {
                    background: #1C1C1C; min-height: 40px; border-radius: 6px;
                }
                QCalendarWidget QToolButton {
                    background: transparent; color: #F0F0F0;
                    border: none; border-radius: 4px; padding: 4px 8px;
                }
                QCalendarWidget QToolButton:hover { background: #2A2A2A; }
                QCalendarWidget QToolButton::menu-indicator { image: none; }
                QCalendarWidget QSpinBox {
                    background: #1C1C1C; color: #F0F0F0;
                    border: 1px solid #2A2A2A; border-radius: 4px; padding: 2px 6px;
                }
            """)
            fmt = QTextCharFormat()
            fmt.setForeground(QColor("#C8102E"))
            cal.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, fmt)
            cal.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, fmt)
            btn_ok = QPushButton("Confirmar")
            btn_ok.setFixedHeight(34)
            btn_ok.setStyleSheet("""
                QPushButton { background: #C8102E; color: white; border: none;
                    border-radius: 6px; font-size: 13px; font-weight: 700; }
                QPushButton:hover { background: #E8152F; }
            """)
            def confirm():
                self._new_task_date = cal.selectedDate()
                inp_date.setText(self._new_task_date.toString("dd / MM / yyyy"))
                cdlg.accept()
            btn_ok.clicked.connect(confirm)
            cal.activated.connect(lambda _: confirm())
            cl.addWidget(cal)
            cl.addWidget(btn_ok)
            cdlg.exec()

        btn_cal.clicked.connect(pick_date)
        date_hl.addWidget(inp_date, 1)
        date_hl.addWidget(btn_cal)
        layout.addWidget(date_container)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: #666;
                border: 1px solid #2A2A2A; border-radius: 7px; font-size: 13px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; }}
        """)
        btn_cancel.clicked.connect(dlg.reject)

        btn_save = QPushButton("Crear Tarea")
        btn_save.setFixedHeight(36)
        btn_save.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white;
                border: none; border-radius: 7px; font-size: 13px; font-weight: 700; }}
            QPushButton:hover {{ background: #E8152F; }}
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

    def _load_data(self):
        self.lbl_status.setText("Actualizando...")
        self.worker = DashboardWorker(self.db)
        self.worker.data_ready.connect(self._on_data)
        self.worker.start()

    def _on_data(self, data):
        # KPIs
        self.kpi_students[1].setText(str(data.get("students_active", 0)))
        self.kpi_income[1].setText(f"${data.get('income_month', 0):,.0f}")
        self.kpi_expenses[1].setText(f"${data.get('expenses_month', 0):,.0f}")
        self.kpi_classes[1].setText(str(data.get("classes_today", 0)))
        self.kpi_expiring[1].setText(str(data.get("memberships_expiring", 0)))
        self.kpi_new[1].setText(str(data.get("students_new", 0)))

        # Gráfico
        self.chart.set_data(data.get("income_chart", []), data.get("expense_chart", []))

        # Limpiar y rellenar cumpleaños
        while self.bday_layout.count():
            item = self.bday_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        birthdays = data.get("birthdays", [])
        if birthdays:
            for nombre, birthdate, _ in birthdays:
                row = QHBoxLayout()
                dot = QLabel("🎂")
                dot.setStyleSheet("font-size: 12px;")
                dot.setFixedWidth(20)
                lbl_n = QLabel(nombre)
                lbl_n.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px;")
                lbl_d = QLabel(birthdate.strftime("%d/%m") if birthdate else "—")
                lbl_d.setStyleSheet(f"color: {PURPLE}; font-size: 12px; font-weight: 600;")
                lbl_d.setAlignment(Qt.AlignmentFlag.AlignRight)
                row.addWidget(dot); row.addWidget(lbl_n, 1); row.addWidget(lbl_d)
                w = QWidget(); w.setStyleSheet("background: transparent;")
                w.setLayout(row)
                self.bday_layout.addWidget(w)
        else:
            lbl = QLabel("Sin cumpleaños próximos")
            lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px;")
            self.bday_layout.addWidget(lbl)

        # Limpiar y rellenar vencimientos
        while self.exp_layout.count():
            item = self.exp_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        expiring = data.get("expiring_detail", [])
        if expiring:
            for nombre, end_date, plan in expiring:
                row = QHBoxLayout()
                dot = QLabel("⚠️")
                dot.setStyleSheet("font-size: 11px;")
                dot.setFixedWidth(20)
                lbl_n = QLabel(nombre)
                lbl_n.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px;")
                lbl_d = QLabel(end_date.strftime("%d/%m") if end_date else "—")
                lbl_d.setStyleSheet(f"color: {YELLOW}; font-size: 12px; font-weight: 600;")
                lbl_d.setAlignment(Qt.AlignmentFlag.AlignRight)
                row.addWidget(dot); row.addWidget(lbl_n, 1); row.addWidget(lbl_d)
                w = QWidget(); w.setStyleSheet("background: transparent;")
                w.setLayout(row)
                self.exp_layout.addWidget(w)
        else:
            lbl = QLabel("Sin vencimientos próximos")
            lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 12px;")
            self.exp_layout.addWidget(lbl)

        # Tareas
        self._render_tasks(data.get("tasks", []))

        now = datetime.now().strftime("%H:%M:%S")
        self.lbl_status.setText(f"Última actualización: {now}  ·  Auto-refresh cada 60s")