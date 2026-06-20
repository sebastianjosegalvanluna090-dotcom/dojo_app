from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from datetime import datetime

# ─── PALETA ───────────────────────────────────────────────────────────
BG_MAIN     = "#0D0D0D"
BG_CARD     = "#161616"
BG_TABLE    = "#121212"
BORDER      = "#2A2A2A"
RED         = "#C8102E"
RED_DARK    = "#7A0A1C"
TEXT_PRI    = "#F0F0F0"
TEXT_SEC    = "#999999"
TEXT_MUT    = "#555555"
GREEN       = "#22C55E"
YELLOW      = "#EAB308"
BLUE        = "#3B82F6"
PURPLE      = "#A855F7"


# ─── Worker para cargar datos en background ───────────────────────────
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

            # Total estudiantes activos
            cur.execute("""
                SELECT COUNT(*) FROM students s
                JOIN status st ON st.id = s.id_status
                WHERE LOWER(st.status) = 'activo'
            """)
            row = cur.fetchone()
            data["students_active"] = row[0] if row else 0

            # Total estudiantes (sin filtro de estado como fallback)
            if data["students_active"] == 0:
                cur.execute("SELECT COUNT(*) FROM students")
                row = cur.fetchone()
                data["students_active"] = row[0] if row else 0

            # Ingresos del mes actual
            cur.execute("""
                SELECT COALESCE(SUM(total_paid), 0)
                FROM payments
                WHERE DATE_TRUNC('month', payment_date) = DATE_TRUNC('month', CURRENT_DATE)
            """)
            row = cur.fetchone()
            data["income_month"] = float(row[0]) if row else 0.0

            # Clases de hoy
            cur.execute("""
                SELECT COUNT(*) FROM classes
                WHERE date = CURRENT_DATE
            """)
            row = cur.fetchone()
            data["classes_today"] = row[0] if row else 0

            # Pagos pendientes (total - total_paid > 0)
            cur.execute("""
                SELECT COUNT(*) FROM payments
                WHERE total > total_paid
            """)
            row = cur.fetchone()
            data["payments_pending"] = row[0] if row else 0

            # Gastos del mes
            cur.execute("""
                SELECT COALESCE(SUM(amount), 0)
                FROM expenses
                WHERE DATE_TRUNC('month', expense_date) = DATE_TRUNC('month', CURRENT_DATE)
            """)
            row = cur.fetchone()
            data["expenses_month"] = float(row[0]) if row else 0.0

            # Estudiantes nuevos este mes
            cur.execute("""
                SELECT COUNT(*) FROM students s
                JOIN people p ON p.id = s.id_person
                WHERE DATE_TRUNC('month', p.created_at) = DATE_TRUNC('month', CURRENT_DATE)
            """)
            row = cur.fetchone()
            data["students_new"] = row[0] if row else 0

            # Clases de hoy - detalle
            cur.execute("""
                SELECT
                    COALESCE(sc.name, 'Sin nombre') AS clase,
                    COALESCE(ma.name, '-')           AS arte,
                    COALESCE(
                        p.first_name || ' ' || p.last_name,
                        'Sin instructor'
                    )                                AS instructor,
                    c.date
                FROM classes c
                LEFT JOIN schedule sc    ON sc.id = c.id_schedule
                LEFT JOIN martial_arts ma ON ma.id = sc.id_martial_art
                LEFT JOIN instructors i  ON i.id = c.id_instructor
                LEFT JOIN people p       ON p.id = i.id_person
                WHERE c.date = CURRENT_DATE
                ORDER BY c.id DESC
                LIMIT 20
            """)
            data["classes_detail"] = cur.fetchall()

        except Exception as e:
            print(f"[Dashboard error] {e}")
            data.setdefault("students_active", 0)
            data.setdefault("income_month", 0.0)
            data.setdefault("classes_today", 0)
            data.setdefault("payments_pending", 0)
            data.setdefault("expenses_month", 0.0)
            data.setdefault("students_new", 0)
            data.setdefault("classes_detail", [])
        finally:
            cur.close()
            self.db.release(conn)

        self.data_ready.emit(data)


# ─── DASHBOARD VIEW ───────────────────────────────────────────────────
class DashboardView(QWidget):
    def __init__(self, db, user):
        super().__init__()
        self.db   = db
        self.user = user
        self._build_ui()
        self._load_data()

        # Auto-refresh cada 60 segundos
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._load_data)
        self._timer.start(60_000)

    # ── UI ────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(f"background-color: {BG_MAIN}; color: {TEXT_PRI};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        container.setStyleSheet(f"background-color: {BG_MAIN};")
        main = QVBoxLayout(container)
        main.setContentsMargins(28, 24, 28, 24)
        main.setSpacing(20)

        # Encabezado
        main.addWidget(self._make_header())

        # Separador rojo
        main.addWidget(self._make_divider())

        # Fila 1 KPIs: estudiantes activos | ingresos mes | clases hoy
        row1 = QHBoxLayout()
        row1.setSpacing(14)
        self.kpi_students  = self._make_kpi("Estudiantes Activos", "—", "👥", BLUE)
        self.kpi_income    = self._make_kpi("Ingresos del Mes",    "—", "💰", GREEN)
        self.kpi_classes   = self._make_kpi("Clases Hoy",          "—", "🥋", RED)
        row1.addWidget(self.kpi_students[0])
        row1.addWidget(self.kpi_income[0])
        row1.addWidget(self.kpi_classes[0])
        main.addLayout(row1)

        # Fila 2 KPIs: pagos pendientes | gastos mes | nuevos este mes
        row2 = QHBoxLayout()
        row2.setSpacing(14)
        self.kpi_pending   = self._make_kpi("Pagos Pendientes",     "—", "⚠️",  YELLOW)
        self.kpi_expenses  = self._make_kpi("Gastos del Mes",       "—", "📉", PURPLE)
        self.kpi_new       = self._make_kpi("Nuevos Este Mes",      "—", "✨", GREEN)
        row2.addWidget(self.kpi_pending[0])
        row2.addWidget(self.kpi_expenses[0])
        row2.addWidget(self.kpi_new[0])
        main.addLayout(row2)

        # Tabla clases de hoy
        main.addWidget(self._make_section_title("📅  Clases de Hoy"))
        self.table = self._make_table()
        main.addWidget(self.table)

        # Estado de carga
        self.lbl_status = QLabel("Cargando datos...")
        self.lbl_status.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px;")
        main.addWidget(self.lbl_status)

        scroll.setWidget(container)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

    # ── Encabezado ────────────────────────────────────────────────────
    def _make_header(self):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Dashboard")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_PRI};")

        now = datetime.now().strftime("%A %d de %B, %Y")
        date_lbl = QLabel(now.capitalize())
        date_lbl.setStyleSheet(f"font-size: 12px; color: {TEXT_SEC};")
        date_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        h.addWidget(title)
        h.addStretch()
        h.addWidget(date_lbl)
        return w

    # ── Separador ─────────────────────────────────────────────────────
    def _make_divider(self):
        line = QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet(f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {RED}, stop:0.5 {RED_DARK}, stop:1 transparent
            );
            border: none;
        """)
        return line

    # ── KPI card ──────────────────────────────────────────────────────
    def _make_kpi(self, label, value, icon, accent):
        card = QFrame()
        card.setMinimumHeight(110)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-left: 3px solid {accent};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        top = QHBoxLayout()
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        lbl_title = QLabel(label.upper())
        lbl_title.setStyleSheet(f"""
            font-size: 10px; font-weight: 600;
            letter-spacing: 1px; color: {TEXT_SEC};
            background: transparent; border: none;
        """)
        top.addWidget(lbl_icon)
        top.addWidget(lbl_title)
        top.addStretch()

        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"""
            font-size: 28px; font-weight: 700;
            color: {TEXT_PRI}; background: transparent; border: none;
        """)

        layout.addLayout(top)
        layout.addWidget(lbl_value)

        return card, lbl_value

    # ── Título de sección ─────────────────────────────────────────────
    def _make_section_title(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            font-size: 14px; font-weight: 600;
            color: {TEXT_PRI}; padding-top: 6px;
        """)
        return lbl

    # ── Tabla ─────────────────────────────────────────────────────────
    def _make_table(self):
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Clase / Horario", "Arte Marcial", "Instructor"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setMinimumHeight(200)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_TABLE};
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 10px;
                gridline-color: {BORDER};
                font-size: 13px;
            }}
            QHeaderView::section {{
                background-color: {BG_CARD};
                color: {TEXT_SEC};
                border: none;
                border-bottom: 1px solid {BORDER};
                padding: 8px 12px;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
            }}
            QTableWidget::item {{
                padding: 10px 12px;
                border-bottom: 1px solid {BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: {RED_DARK};
                color: white;
            }}
        """)
        return table

    # ── Cargar datos ──────────────────────────────────────────────────
    def _load_data(self):
        self.lbl_status.setText("Actualizando...")
        self.worker = DashboardWorker(self.db)
        self.worker.data_ready.connect(self._on_data_ready)
        self.worker.start()

    def _on_data_ready(self, data):
        # KPIs
        self.kpi_students[1].setText(str(data.get("students_active", 0)))
        self.kpi_income[1].setText(
            f"${data.get('income_month', 0):,.0f}"
        )
        self.kpi_classes[1].setText(str(data.get("classes_today", 0)))
        self.kpi_pending[1].setText(str(data.get("payments_pending", 0)))
        self.kpi_expenses[1].setText(
            f"${data.get('expenses_month', 0):,.0f}"
        )
        self.kpi_new[1].setText(str(data.get("students_new", 0)))

        # Tabla clases
        rows = data.get("classes_detail", [])
        self.table.setRowCount(len(rows))

        if not rows:
            self.table.setRowCount(1)
            item = QTableWidgetItem("No hay clases programadas para hoy")
            item.setForeground(QColor(TEXT_SEC))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(0, 0, item)
            self.table.setSpan(0, 0, 1, 3)
        else:
            self.table.setSpan(0, 0, 1, 1)  # reset span
            for i, row in enumerate(rows):
                clase, arte, instructor, fecha = row
                self.table.setItem(i, 0, QTableWidgetItem(str(clase)))
                self.table.setItem(i, 1, QTableWidgetItem(str(arte)))
                self.table.setItem(i, 2, QTableWidgetItem(str(instructor)))
                self.table.setRowHeight(i, 42)

        now = datetime.now().strftime("%H:%M:%S")
        self.lbl_status.setText(f"Última actualización: {now}  ·  Auto-refresh cada 60s")
