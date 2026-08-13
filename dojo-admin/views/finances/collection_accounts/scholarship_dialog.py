from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QDoubleSpinBox, QComboBox, QDateEdit, QTextEdit,
    QPushButton, QFrame, QScrollArea, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox,
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from datetime import date

from repositories.finances_scholarships_repository import FinancesScholarshipsRepository

BG_DIALOG = "#0E0E0E"
BG_INPUT  = "#1A1A1A"
BG_CARD   = "#141414"
BG_HOVER  = "#1E1E1E"
BORDER    = "#222222"
RED       = "#E11D48"
RED_H     = "#FF1F4E"
GREEN     = "#22C55E"
YELLOW    = "#EAB308"
TEXT_PRI  = "#FAFAFA"
TEXT_SEC  = "#A3A3A3"
TEXT_MUT  = "#666666"

INPUT_STYLE = f"""
    QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit {{
        background:{BG_INPUT}; color:{TEXT_PRI};
        border:1px solid {BORDER}; border-radius:8px;
        padding:0 12px; font-size:12px; font-family:'Inter'; min-height:36px;
    }}
    QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{ border-color:{RED}; }}
    QComboBox::drop-down {{ border:none; width:22px; }}
    QComboBox QAbstractItemView {{
        background:{BG_INPUT}; color:{TEXT_PRI}; selection-background-color:{RED};
        border:1px solid {BORDER};
    }}
"""


def _lbl(text):
    l = QLabel(text)
    l.setStyleSheet(f"color:{TEXT_MUT}; font-size:9px; font-weight:800; letter-spacing:1px; font-family:'Inter'; border:none; background:transparent;")
    return l


class ScholarshipDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._repo    = FinancesScholarshipsRepository()
        self._edit_id = None
        self._people  = []
        self._selected_person = None
        self.setWindowTitle("Gestionar Becas de Colaboradores")
        self.setMinimumSize(780, 600)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background:{BG_DIALOG}; color:{TEXT_PRI};")
        self._build_ui()
        self._load()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        left = QFrame()
        left.setFixedWidth(360)
        left.setStyleSheet(f"QFrame {{ background:{BG_CARD}; border-right:1px solid {BORDER}; }}")
        lv = QVBoxLayout(left); lv.setContentsMargins(22,22,22,22); lv.setSpacing(14)

        self.lbl_form_title = QLabel("Nueva beca")
        self.lbl_form_title.setStyleSheet(f"color:{TEXT_PRI}; font-size:16px; font-weight:900; font-family:'Inter'; border:none; background:transparent;")
        lv.addWidget(self.lbl_form_title)

        lv.addWidget(_lbl("COLABORADOR"))
        self.inp_person = QLineEdit()
        self.inp_person.setPlaceholderText("Buscar por nombre...")
        self.inp_person.setStyleSheet(INPUT_STYLE)
        self.inp_person.textChanged.connect(self._search_person)
        lv.addWidget(self.inp_person)
        self.person_results = QFrame()
        self.person_results.setStyleSheet(f"QFrame {{ background:{BG_INPUT}; border:1px solid {BORDER}; border-radius:8px; }}")
        self.person_results.hide()
        self._pr_layout = QVBoxLayout(self.person_results)
        self._pr_layout.setContentsMargins(4,4,4,4); self._pr_layout.setSpacing(2)
        lv.addWidget(self.person_results)
        self.lbl_person_sel = QLabel("Sin seleccionar")
        self.lbl_person_sel.setStyleSheet(f"color:{TEXT_MUT}; font-size:11px; font-family:'Inter'; border:none; background:transparent;")
        lv.addWidget(self.lbl_person_sel)

        lv.addWidget(_lbl("MENSUALIDAD BASE ($)"))
        self.sp_fee = QDoubleSpinBox()
        self.sp_fee.setRange(0, 9999999); self.sp_fee.setDecimals(0); self.sp_fee.setSingleStep(10000)
        self.sp_fee.setPrefix("$ "); self.sp_fee.setStyleSheet(INPUT_STYLE)
        lv.addWidget(self.sp_fee)

        rates_frame = QFrame()
        rates_frame.setStyleSheet(f"QFrame {{ background:{BG_DIALOG}; border:1px solid {BORDER}; border-radius:10px; }} QFrame * {{ border:none; background:transparent; }}")
        rf = QVBoxLayout(rates_frame); rf.setContentsMargins(14,12,14,12); rf.setSpacing(8)
        rf.addWidget(_lbl("TARIFAS ACORDADAS"))

        def _rate_row(label, default):
            rw = QHBoxLayout(); rw.setSpacing(10)
            l = QLabel(label)
            l.setStyleSheet(f"color:{TEXT_SEC}; font-size:11px; font-family:'Inter';")
            l.setFixedWidth(150)
            sp = QDoubleSpinBox()
            sp.setRange(0, 9999999); sp.setDecimals(0); sp.setSingleStep(5000)
            sp.setValue(default); sp.setPrefix("$")
            sp.setStyleSheet(INPUT_STYLE)
            rw.addWidget(l); rw.addWidget(sp, 1)
            rf.addLayout(rw)
            return sp

        self.sp_rate_class = _rate_row("Por hora de clase:", 25000)
        self.sp_rate_deep  = _rate_row("Aseo profundo:", 50000)
        self.sp_rate_maint = _rate_row("Aseo mantenimiento:", 25000)
        self.sp_penalty    = _rate_row("Penalización/inasistencia:", 25000)
        lv.addWidget(rates_frame)

        dates_row = QHBoxLayout(); dates_row.setSpacing(10)
        start_col = QVBoxLayout(); start_col.setSpacing(4)
        start_col.addWidget(_lbl("INICIO"))
        self.dp_start = QDateEdit(QDate.currentDate())
        self.dp_start.setCalendarPopup(True); self.dp_start.setStyleSheet(INPUT_STYLE)
        start_col.addWidget(self.dp_start)
        dates_row.addLayout(start_col)

        end_col = QVBoxLayout(); end_col.setSpacing(4)
        end_col.addWidget(_lbl("FIN (OPC.)"))
        self.dp_end = QDateEdit()
        self.dp_end.setCalendarPopup(True); self.dp_end.setStyleSheet(INPUT_STYLE)
        self.dp_end.setSpecialValueText("Sin fecha de fin")
        self.dp_end.setDate(QDate.currentDate().addYears(1))
        end_col.addWidget(self.dp_end)
        dates_row.addLayout(end_col)
        lv.addLayout(dates_row)

        lv.addWidget(_lbl("NOTAS"))
        self.inp_notes = QTextEdit()
        self.inp_notes.setFixedHeight(54)
        self.inp_notes.setStyleSheet(INPUT_STYLE + "QTextEdit { padding:8px 12px; }")
        lv.addWidget(self.inp_notes)

        lv.addStretch()

        btns = QHBoxLayout(); btns.setSpacing(8)
        self.btn_cancel_edit = QPushButton("Cancelar edición")
        self.btn_cancel_edit.setFixedHeight(36)
        self.btn_cancel_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel_edit.setStyleSheet(f"""
            QPushButton {{ background:transparent; color:{TEXT_SEC}; border:1px solid {BORDER};
                border-radius:8px; font-size:11px; font-family:'Inter'; }}
            QPushButton:hover {{ color:{TEXT_PRI}; }}
        """)
        self.btn_cancel_edit.clicked.connect(self._cancel_edit)
        self.btn_cancel_edit.hide()
        btns.addWidget(self.btn_cancel_edit)

        self.btn_save = QPushButton("Guardar beca")
        self.btn_save.setFixedHeight(36)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{ background:{RED}; color:white; border:none;
                border-radius:8px; font-size:12px; font-weight:800; font-family:'Inter'; }}
            QPushButton:hover {{ background:{RED_H}; }}
        """)
        self.btn_save.clicked.connect(self._save)
        btns.addWidget(self.btn_save, 1)
        lv.addLayout(btns)

        right = QWidget()
        right.setStyleSheet("background:transparent;")
        rv = QVBoxLayout(right); rv.setContentsMargins(22,22,22,22); rv.setSpacing(12)

        lbl_list = QLabel("Becas activas")
        lbl_list.setStyleSheet(f"color:{TEXT_PRI}; font-size:16px; font-weight:900; font-family:'Inter'; border:none; background:transparent;")
        rv.addWidget(lbl_list)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Colaborador","Mensualidad","Inicio","Estado","Acciones"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col, w in [(1,90),(2,80),(3,80),(4,80)]:
            self.table.setColumnWidth(col, w)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{ background:transparent; color:{TEXT_PRI}; border:none;
                font-size:12px; font-family:'Inter'; }}
            QHeaderView::section {{ background:{BG_CARD}; color:{TEXT_MUT}; border:none;
                border-bottom:1px solid {BORDER}; padding:6px 8px;
                font-size:9px; font-weight:800; letter-spacing:1px; }}
            QTableWidget::item {{ padding:6px 8px; border-bottom:1px solid {BORDER}; }}
            QTableWidget::item:selected {{ background:#1F0A10; }}
        """)
        rv.addWidget(self.table, 1)

        btn_close = QPushButton("Cerrar")
        btn_close.setFixedHeight(36)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{ background:transparent; color:{TEXT_SEC}; border:1px solid {BORDER};
                border-radius:8px; font-size:12px; font-family:'Inter'; padding:0 20px; }}
            QPushButton:hover {{ color:{TEXT_PRI}; }}
        """)
        btn_close.clicked.connect(self.accept)
        close_row = QHBoxLayout(); close_row.addStretch(); close_row.addWidget(btn_close)
        rv.addLayout(close_row)

        root.addWidget(left)
        root.addWidget(right, 1)

    def _search_person(self, text):
        if len(text) < 2: self.person_results.hide(); return
        self._people = self._repo.search_people(text)
        while self._pr_layout.count():
            item = self._pr_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for p in self._people[:8]:
            btn = QPushButton(p["name"])
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{ background:transparent; color:{TEXT_PRI}; border:none;
                    text-align:left; padding:0 10px; font-size:12px; font-family:'Inter'; border-radius:4px; }}
                QPushButton:hover {{ background:{BG_HOVER}; }}
            """)
            btn.clicked.connect(lambda _, pp=p: self._select_person(pp))
            self._pr_layout.addWidget(btn)
        self.person_results.show()

    def _select_person(self, p):
        self._selected_person = p
        self.inp_person.blockSignals(True)
        self.inp_person.setText(p["name"])
        self.inp_person.blockSignals(False)
        self.person_results.hide()
        self.lbl_person_sel.setText(f"✓ {p['name']}")
        self.lbl_person_sel.setStyleSheet(f"color:{GREEN}; font-size:11px; font-family:'Inter'; border:none; background:transparent;")

    def _load(self):
        scholarships = self._repo.get_all()
        self.table.setRowCount(len(scholarships))
        STATUS_COLORS = {"active": GREEN, "suspended": YELLOW, "terminated": TEXT_MUT}
        STATUS_LABELS = {"active":"Activa","suspended":"Suspendida","terminated":"Terminada"}
        for row, s in enumerate(scholarships):
            self.table.setRowHeight(row, 40)
            status = s.get("status","active")
            color  = STATUS_COLORS.get(status, TEXT_MUT)
            for col, val in [
                (0, s.get("person_name","—")),
                (1, "$" + f"{s.get('monthly_fee',0):,.0f}".replace(",",".")),
                (2, s.get("start_date","").strftime("%d/%m/%y") if hasattr(s.get("start_date"),"strftime") else "—"),
                (3, STATUS_LABELS.get(status, status)),
            ]:
                qi = QTableWidgetItem(str(val))
                if col == 3: qi.setForeground(QColor(color))
                self.table.setItem(row, col, qi)

            btn_w = QWidget(); btn_w.setStyleSheet("background:transparent;")
            bl = QHBoxLayout(btn_w); bl.setContentsMargins(4,2,4,2); bl.setSpacing(4)

            btn_edit = QPushButton("Editar")
            btn_edit.setFixedHeight(26)
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.setStyleSheet(f"""
                QPushButton {{ background:transparent; color:{TEXT_SEC}; border:1px solid {BORDER};
                    border-radius:4px; font-size:10px; font-family:'Inter'; padding:0 8px; }}
                QPushButton:hover {{ color:{TEXT_PRI}; }}
            """)
            btn_edit.clicked.connect(lambda _, sid=s["id"]: self._start_edit(sid))

            if status == "active":
                btn_term = QPushButton("Terminar")
                btn_term.setFixedHeight(26)
                btn_term.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_term.setStyleSheet(f"""
                    QPushButton {{ background:transparent; color:{RED}; border:1px solid {RED}40;
                        border-radius:4px; font-size:10px; font-family:'Inter'; padding:0 8px; }}
                    QPushButton:hover {{ background:{RED}18; }}
                """)
                btn_term.clicked.connect(lambda _, sid=s["id"]: self._terminate(sid))
                bl.addWidget(btn_term)

            bl.addWidget(btn_edit)
            self.table.setCellWidget(row, 4, btn_w)

    def _start_edit(self, scholarship_id):
        s = self._repo.get_by_id(scholarship_id)
        if not s: return
        self._edit_id = scholarship_id
        self.lbl_form_title.setText("Editar beca")
        self.inp_person.setText(s.get("person_name",""))
        self.lbl_person_sel.setText(f"✓ {s.get('person_name','')}")
        self.lbl_person_sel.setStyleSheet(f"color:{GREEN}; font-size:11px; font-family:'Inter'; border:none; background:transparent;")
        self._selected_person = {"id": s.get("person_id"), "name": s.get("person_name","")}
        self.sp_fee.setValue(s.get("monthly_fee",0))
        self.sp_rate_class.setValue(s.get("rate_class",25000))
        self.sp_rate_deep.setValue(s.get("rate_deep_clean",50000))
        self.sp_rate_maint.setValue(s.get("rate_maintenance",25000))
        self.sp_penalty.setValue(s.get("penalty_per_miss",25000))
        if s.get("start_date"):
            d = s["start_date"]
            self.dp_start.setDate(QDate(d.year, d.month, d.day))
        if s.get("end_date"):
            d = s["end_date"]
            self.dp_end.setDate(QDate(d.year, d.month, d.day))
        self.inp_notes.setPlainText(s.get("notes",""))
        self.btn_cancel_edit.show()

    def _cancel_edit(self):
        self._edit_id = None
        self._selected_person = None
        self.lbl_form_title.setText("Nueva beca")
        self.inp_person.clear()
        self.lbl_person_sel.setText("Sin seleccionar")
        self.lbl_person_sel.setStyleSheet(f"color:{TEXT_MUT}; font-size:11px; font-family:'Inter'; border:none; background:transparent;")
        self.sp_fee.setValue(0)
        self.sp_rate_class.setValue(25000); self.sp_rate_deep.setValue(50000)
        self.sp_rate_maint.setValue(25000); self.sp_penalty.setValue(25000)
        self.dp_start.setDate(QDate.currentDate())
        self.inp_notes.clear()
        self.btn_cancel_edit.hide()

    def _save(self):
        person = getattr(self,"_selected_person", None)
        if not person:
            QMessageBox.warning(self, "Aviso", "Selecciona un colaborador."); return
        data = {
            "person_id":         person["id"],
            "monthly_fee":       self.sp_fee.value(),
            "start_date":        self.dp_start.date().toPyDate(),
            "end_date":          self.dp_end.date().toPyDate(),
            "status":            "active",
            "rate_class":        self.sp_rate_class.value(),
            "rate_deep_clean":   self.sp_rate_deep.value(),
            "rate_maintenance":  self.sp_rate_maint.value(),
            "penalty_per_miss":  self.sp_penalty.value(),
            "notes":             self.inp_notes.toPlainText().strip(),
        }
        try:
            if self._edit_id:
                self._repo.update(self._edit_id, data)
            else:
                self._repo.create(data)
            self._cancel_edit()
            self._load()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _terminate(self, scholarship_id):
        msg = QMessageBox(self)
        msg.setWindowTitle("Terminar beca")
        msg.setText("¿Terminar esta beca? No podrá reactivarse automáticamente.")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet(f"QMessageBox {{ background:{BG_DIALOG}; color:{TEXT_PRI}; }}")
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self._repo.terminate(scholarship_id)
            self._load()
