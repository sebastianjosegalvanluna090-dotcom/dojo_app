from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDoubleSpinBox, QCheckBox, QTextEdit,
    QPushButton, QFrame, QScrollArea, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox, QDateEdit, QRadioButton,
    QButtonGroup, QSizePolicy,
)
from PyQt6.QtCore import Qt, QDate
from datetime import date

from repositories.finances_collection_accounts_repository import FinancesCollectionAccountsRepository
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
PURPLE    = "#A855F7"
BLUE      = "#3B82F6"
TEXT_PRI  = "#FAFAFA"
TEXT_SEC  = "#A3A3A3"
TEXT_MUT  = "#666666"

ACTIVITY_TYPES = [
    ("clase",            "Clase dictada"),
    ("aseo_profundo",    "Aseo profundo"),
    ("aseo_mantenimiento","Aseo mantenimiento"),
    ("penalizacion",     "Penalización"),
    ("otro",             "Otro"),
]
MONTHS = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
          "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

INPUT_STYLE = f"""
    QLineEdit, QComboBox, QTextEdit, QDoubleSpinBox, QDateEdit {{
        background:{BG_INPUT}; color:{TEXT_PRI};
        border:1px solid {BORDER}; border-radius:8px;
        padding:0 12px; font-size:12px; font-family:'Inter'; min-height:36px;
    }}
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDateEdit:focus {{
        border-color:{RED};
    }}
    QComboBox::drop-down {{ border:none; width:22px; }}
    QComboBox QAbstractItemView {{
        background:{BG_INPUT}; color:{TEXT_PRI};
        selection-background-color:{RED}; border:1px solid {BORDER};
    }}
"""


def fmt_money(v):
    try: v = float(v or 0)
    except: v = 0
    return "$" + f"{v:,.0f}".replace(",",".")


def _lbl(text):
    l = QLabel(text)
    l.setStyleSheet(f"color:{TEXT_MUT}; font-size:9px; font-weight:800; letter-spacing:1px; font-family:'Inter'; border:none; background:transparent;")
    return l


class CollectionAccountDialog(QDialog):
    def __init__(self, account_id=None, parent=None):
        super().__init__(parent)
        self._account_id = account_id
        self._repo       = FinancesCollectionAccountsRepository()
        self._sch_repo   = FinancesScholarshipsRepository()
        self._items      = []
        self._people     = []
        self._selected_person = None

        self.setWindowTitle("Editar cuenta de cobro" if account_id else "Nueva cuenta de cobro")
        self.setMinimumSize(860, 660)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background:{BG_DIALOG}; color:{TEXT_PRI};")
        self._build_ui()
        if account_id:
            self._load_existing()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFixedWidth(560)
        left_scroll.setStyleSheet("QScrollArea { border:none; background:transparent; }")
        left_w = QWidget(); left_w.setStyleSheet("background:transparent;")
        left = QVBoxLayout(left_w)
        left.setContentsMargins(24,24,20,24); left.setSpacing(16)

        lbl_title = QLabel("Editar cuenta" if self._account_id else "Nueva cuenta de cobro")
        lbl_title.setStyleSheet(f"color:{TEXT_PRI}; font-size:20px; font-weight:900; font-family:'Inter'; border:none;")
        left.addWidget(lbl_title)

        type_card = self._card()
        tc = QVBoxLayout(type_card); tc.setContentsMargins(16,14,16,14); tc.setSpacing(10)
        tc.addWidget(_lbl("TIPO DE CUENTA"))
        self._rg = QButtonGroup(self)
        rb_row = QHBoxLayout(); rb_row.setSpacing(16)
        self.rb_free  = QRadioButton("Cuenta libre")
        self.rb_beca  = QRadioButton("Liquidación de beca")
        for rb in [self.rb_free, self.rb_beca]:
            rb.setStyleSheet(f"""
                QRadioButton {{ color:{TEXT_SEC}; font-size:13px; font-family:'Inter'; border:none; background:transparent; }}
                QRadioButton::indicator {{ width:14px; height:14px; border-radius:7px;
                    border:1.5px solid {BORDER}; background:{BG_INPUT}; }}
                QRadioButton::indicator:checked {{ background:{RED}; border:1.5px solid {RED}; }}
            """)
            self._rg.addButton(rb); rb_row.addWidget(rb)
        self.rb_free.setChecked(True)
        rb_row.addStretch(); tc.addLayout(rb_row)
        self.rb_beca.toggled.connect(self._on_type_changed)
        left.addWidget(type_card)

        person_card = self._card()
        pc = QVBoxLayout(person_card); pc.setContentsMargins(16,14,16,14); pc.setSpacing(8)
        pc.addWidget(_lbl("COLABORADOR"))
        self.inp_person = QLineEdit()
        self.inp_person.setPlaceholderText("Buscar por nombre, email...")
        self.inp_person.setStyleSheet(INPUT_STYLE)
        self.inp_person.textChanged.connect(self._search_person)
        pc.addWidget(self.inp_person)
        self.person_results = QFrame()
        self.person_results.setStyleSheet(f"QFrame {{ background:{BG_INPUT}; border:1px solid {BORDER}; border-radius:8px; }}")
        self.person_results.hide()
        self._person_res_layout = QVBoxLayout(self.person_results)
        self._person_res_layout.setContentsMargins(4,4,4,4); self._person_res_layout.setSpacing(2)
        pc.addWidget(self.person_results)
        self.lbl_person_sel = QLabel("Sin seleccionar")
        self.lbl_person_sel.setStyleSheet(f"color:{TEXT_MUT}; font-size:11px; font-family:'Inter'; border:none; background:transparent;")
        pc.addWidget(self.lbl_person_sel)
        left.addWidget(person_card)

        self.period_card = self._card()
        prc = QVBoxLayout(self.period_card); prc.setContentsMargins(16,14,16,14); prc.setSpacing(8)
        prc.addWidget(_lbl("PERÍODO"))
        pr_row = QHBoxLayout(); pr_row.setSpacing(10)
        self.cmb_month = QComboBox()
        self.cmb_month.setStyleSheet(INPUT_STYLE)
        for i,m in enumerate(MONTHS): self.cmb_month.addItem(m, i+1)
        self.cmb_month.setCurrentIndex(date.today().month - 1)
        self.cmb_year = QComboBox()
        self.cmb_year.setStyleSheet(INPUT_STYLE)
        for y in range(date.today().year-1, date.today().year+2):
            self.cmb_year.addItem(str(y), y)
        self.cmb_year.setCurrentIndex(1)
        pr_row.addWidget(self.cmb_month,1); pr_row.addWidget(self.cmb_year)
        prc.addLayout(pr_row)
        self.period_card.hide()
        left.addWidget(self.period_card)

        data_card = self._card()
        dc = QVBoxLayout(data_card); dc.setContentsMargins(16,14,16,14); dc.setSpacing(10)
        dc.addWidget(_lbl("DATOS GENERALES"))

        dc.addWidget(_lbl("CONCEPTO"))
        self.inp_concept = QTextEdit()
        self.inp_concept.setPlaceholderText("Descripción del servicio prestado...")
        self.inp_concept.setFixedHeight(64)
        self.inp_concept.setStyleSheet(INPUT_STYLE + "QTextEdit { padding:8px 12px; }")
        dc.addWidget(self.inp_concept)

        dates_row = QHBoxLayout(); dates_row.setSpacing(12)
        issued_col = QVBoxLayout(); issued_col.setSpacing(4)
        issued_col.addWidget(_lbl("FECHA DE EMISIÓN"))
        self.dp_issued = QDateEdit(QDate.currentDate())
        self.dp_issued.setCalendarPopup(True)
        self.dp_issued.setStyleSheet(INPUT_STYLE)
        issued_col.addWidget(self.dp_issued)
        dates_row.addLayout(issued_col)

        due_col = QVBoxLayout(); due_col.setSpacing(4)
        due_col.addWidget(_lbl("FECHA DE VENCIMIENTO (OPC.)"))
        self.dp_due = QDateEdit()
        self.dp_due.setCalendarPopup(True)
        self.dp_due.setStyleSheet(INPUT_STYLE)
        self.dp_due.setSpecialValueText("Sin vencimiento")
        self.dp_due.setDate(QDate.currentDate().addDays(30))
        due_col.addWidget(self.dp_due)
        dates_row.addLayout(due_col)
        dc.addLayout(dates_row)

        dc.addWidget(_lbl("NOTAS INTERNAS"))
        self.inp_notes = QTextEdit()
        self.inp_notes.setPlaceholderText("Notas internas (no aparecen en el PDF)...")
        self.inp_notes.setFixedHeight(54)
        self.inp_notes.setStyleSheet(INPUT_STYLE + "QTextEdit { padding:8px 12px; }")
        dc.addWidget(self.inp_notes)
        left.addWidget(data_card)

        self.btn_calc = QPushButton("⚡ Calcular desde beca")
        self.btn_calc.setFixedHeight(38)
        self.btn_calc.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_calc.setStyleSheet(f"""
            QPushButton {{ background:{PURPLE}18; color:{PURPLE}; border:1px solid {PURPLE}40;
                border-radius:8px; font-size:12px; font-weight:700; font-family:'Inter'; }}
            QPushButton:hover {{ background:{PURPLE}30; }}
        """)
        self.btn_calc.clicked.connect(self._calculate_from_scholarship)
        self.btn_calc.hide()
        left.addWidget(self.btn_calc)

        items_card = self._card()
        ic = QVBoxLayout(items_card); ic.setContentsMargins(16,14,16,14); ic.setSpacing(10)

        items_hdr = QHBoxLayout()
        items_hdr.addWidget(_lbl("ACTIVIDADES REALIZADAS"))
        items_hdr.addStretch()
        btn_add_item = QPushButton("＋ Agregar")
        btn_add_item.setFixedHeight(28)
        btn_add_item.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_item.setStyleSheet(f"""
            QPushButton {{ background:{RED}; color:white; border:none;
                border-radius:6px; font-size:11px; font-weight:700; font-family:'Inter'; padding:0 12px; }}
            QPushButton:hover {{ background:{RED_H}; }}
        """)
        btn_add_item.clicked.connect(self._add_item_row)
        items_hdr.addWidget(btn_add_item)
        ic.addLayout(items_hdr)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(7)
        self.items_table.setHorizontalHeaderLabels(
            ["Tipo","Descripción","Fecha","Cant.","Precio unit.","Subtotal","Pen."]
        )
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for col, w in [(0,110),(2,90),(3,55),(4,95),(5,85),(6,40)]:
            self.items_table.setColumnWidth(col, w)
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.items_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.items_table.setShowGrid(False)
        self.items_table.setStyleSheet(f"""
            QTableWidget {{ background:transparent; color:{TEXT_PRI}; border:none; font-size:11px; font-family:'Inter'; }}
            QHeaderView::section {{ background:{BG_CARD}; color:{TEXT_MUT}; border:none;
                border-bottom:1px solid {BORDER}; padding:5px 8px; font-size:9px; font-weight:800; letter-spacing:1px; }}
            QTableWidget::item {{ padding:4px 8px; border-bottom:1px solid {BORDER}; }}
            QTableWidget::item:selected {{ background:#1F0A10; }}
        """)
        self.items_table.setFixedHeight(200)
        ic.addWidget(self.items_table)
        left.addWidget(items_card)
        left.addStretch()
        left_scroll.setWidget(left_w)

        right = QFrame()
        right.setFixedWidth(270)
        right.setStyleSheet(f"QFrame {{ background:{BG_CARD}; border-left:1px solid {BORDER}; }}")
        rv = QVBoxLayout(right); rv.setContentsMargins(20,24,20,24); rv.setSpacing(14)

        lbl_sum = QLabel("RESUMEN")
        lbl_sum.setStyleSheet(f"color:{TEXT_MUT}; font-size:9px; font-weight:800; letter-spacing:1.5px; font-family:'Inter'; border:none; background:transparent;")
        rv.addWidget(lbl_sum)

        def _sum_row(label, color=TEXT_SEC):
            row = QHBoxLayout()
            l = QLabel(label)
            l.setStyleSheet(f"color:{TEXT_MUT}; font-size:11px; font-family:'Inter'; border:none; background:transparent;")
            v = QLabel("$0")
            v.setAlignment(Qt.AlignmentFlag.AlignRight)
            v.setStyleSheet(f"color:{color}; font-size:13px; font-weight:700; font-family:'Inter'; border:none; background:transparent;")
            row.addWidget(l,1); row.addWidget(v)
            rv.addLayout(row)
            return v

        self.lbl_activities = _sum_row("Actividades:", GREEN)
        self.lbl_penalties  = _sum_row("Penalizaciones:", RED)
        sep1 = QFrame(); sep1.setFixedHeight(1)
        sep1.setStyleSheet(f"background:{BORDER}; border:none;")
        rv.addWidget(sep1)
        self.lbl_net        = _sum_row("Total cuenta:", TEXT_PRI)

        self.beca_frame = QFrame()
        self.beca_frame.setStyleSheet("background:transparent; border:none;")
        bf = QVBoxLayout(self.beca_frame); bf.setContentsMargins(0,0,0,0); bf.setSpacing(8)
        sep2 = QFrame(); sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background:{BORDER}; border:none;")
        bf.addWidget(sep2)
        self.lbl_monthly    = _sum_row("Mensualidad base:", TEXT_SEC)
        sep3 = QFrame(); sep3.setFixedHeight(1)
        sep3.setStyleSheet(f"background:{BORDER}; border:none;")
        bf.addWidget(sep3)
        self.lbl_dojo_owes  = _sum_row("Dojo debe pagar:", GREEN)
        self.lbl_beca_owes  = _sum_row("Becado debe pagar:", RED)
        rv.addWidget(self.beca_frame)
        self.beca_frame.hide()

        rv.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(40)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ background:transparent; color:{TEXT_SEC}; border:1px solid {BORDER};
                border-radius:9px; font-size:12px; font-family:'Inter'; }}
            QPushButton:hover {{ color:{TEXT_PRI}; }}
        """)
        btn_cancel.clicked.connect(self.reject)
        rv.addWidget(btn_cancel)

        self.btn_save = QPushButton("Crear cuenta" if not self._account_id else "Guardar cambios")
        self.btn_save.setFixedHeight(40)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{ background:{RED}; color:white; border:none;
                border-radius:9px; font-size:12px; font-weight:800; font-family:'Inter'; }}
            QPushButton:hover {{ background:{RED_H}; }}
        """)
        self.btn_save.clicked.connect(self._save)
        rv.addWidget(self.btn_save)

        root.addWidget(left_scroll)
        root.addWidget(right)

    def _card(self):
        f = QFrame()
        f.setStyleSheet(f"QFrame {{ background:{BG_CARD}; border:1px solid {BORDER}; border-radius:10px; }} QFrame * {{ border:none; background:transparent; }}")
        return f

    def _on_type_changed(self, is_beca):
        self.period_card.setVisible(is_beca)
        self.btn_calc.setVisible(is_beca)
        self.beca_frame.setVisible(is_beca)

    def _search_person(self, text):
        if len(text) < 2:
            self.person_results.hide(); return
        self._people = self._repo.search_people(text)
        while self._person_res_layout.count():
            item = self._person_res_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for p in self._people[:8]:
            btn = QPushButton(p["name"])
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{ background:transparent; color:{TEXT_PRI}; border:none; text-align:left;
                    padding:0 10px; font-size:12px; font-family:'Inter'; border-radius:4px; }}
                QPushButton:hover {{ background:{BG_HOVER}; }}
            """)
            btn.clicked.connect(lambda _, pp=p: self._select_person(pp))
            self._person_res_layout.addWidget(btn)
        self.person_results.show()

    def _select_person(self, p):
        self._selected_person = p
        self.inp_person.blockSignals(True)
        self.inp_person.setText(p["name"])
        self.inp_person.blockSignals(False)
        self.person_results.hide()
        self.lbl_person_sel.setText(
            f"✓ {p['name']}" + (f" · {p.get('phone','')}" if p.get('phone') else "")
        )
        self.lbl_person_sel.setStyleSheet(f"color:{GREEN}; font-size:11px; font-family:'Inter'; border:none; background:transparent;")

    def _add_item_row(self, data=None):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        self.items_table.setRowHeight(row, 36)

        cmb = QComboBox()
        cmb.setStyleSheet(f"QComboBox {{ background:{BG_INPUT}; color:{TEXT_PRI}; border:1px solid {BORDER}; border-radius:5px; font-size:11px; font-family:'Inter'; }}")
        for code, label in ACTIVITY_TYPES: cmb.addItem(label, code)
        if data and data.get("activity_type"):
            for i, (c,_) in enumerate(ACTIVITY_TYPES):
                if c == data["activity_type"]: cmb.setCurrentIndex(i); break
        cmb.currentIndexChanged.connect(self._recalc)
        self.items_table.setCellWidget(row, 0, cmb)

        inp_desc = QLineEdit(data.get("description","") if data else "")
        inp_desc.setStyleSheet(f"QLineEdit {{ background:{BG_INPUT}; color:{TEXT_PRI}; border:1px solid {BORDER}; border-radius:5px; font-size:11px; font-family:'Inter'; padding:0 6px; }}")
        inp_desc.textChanged.connect(self._recalc)
        self.items_table.setCellWidget(row, 1, inp_desc)

        dp = QDateEdit()
        dp.setCalendarPopup(True)
        dp.setStyleSheet(f"QDateEdit {{ background:{BG_INPUT}; color:{TEXT_PRI}; border:1px solid {BORDER}; border-radius:5px; font-size:10px; font-family:'Inter'; }}")
        dp.setSpecialValueText("—")
        if data and data.get("activity_date"):
            d = data["activity_date"]
            dp.setDate(QDate(d.year, d.month, d.day) if hasattr(d,"year") else QDate.currentDate())
        else:
            dp.setDate(QDate.currentDate())
        self.items_table.setCellWidget(row, 2, dp)

        sp_qty = QDoubleSpinBox()
        sp_qty.setRange(0.01, 9999); sp_qty.setDecimals(1); sp_qty.setValue(data.get("quantity",1) if data else 1)
        sp_qty.setStyleSheet(f"QDoubleSpinBox {{ background:{BG_INPUT}; color:{TEXT_PRI}; border:1px solid {BORDER}; border-radius:5px; font-size:11px; font-family:'Inter'; }}")
        sp_qty.valueChanged.connect(self._recalc)
        self.items_table.setCellWidget(row, 3, sp_qty)

        sp_price = QDoubleSpinBox()
        sp_price.setRange(0, 99999999); sp_price.setDecimals(0); sp_price.setSingleStep(1000)
        sp_price.setValue(data.get("unit_price",0) if data else 0)
        sp_price.setPrefix("$")
        sp_price.setStyleSheet(f"QDoubleSpinBox {{ background:{BG_INPUT}; color:{TEXT_PRI}; border:1px solid {BORDER}; border-radius:5px; font-size:11px; font-family:'Inter'; }}")
        sp_price.valueChanged.connect(self._recalc)
        self.items_table.setCellWidget(row, 4, sp_price)

        sub = QLabel(fmt_money(data.get("subtotal",0) if data else 0))
        sub.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        sub.setStyleSheet(f"color:{TEXT_PRI}; font-size:11px; font-family:'Inter'; padding-right:6px; background:transparent; border:none;")
        self.items_table.setCellWidget(row, 5, sub)

        chk = QCheckBox()
        chk.setChecked(data.get("penalty", False) if data else False)
        chk.setStyleSheet(f"""
            QCheckBox::indicator {{ width:14px; height:14px; border-radius:3px;
                border:1.5px solid {BORDER}; background:{BG_INPUT}; }}
            QCheckBox::indicator:checked {{ background:{RED}; border:1.5px solid {RED}; }}
        """)
        chk.stateChanged.connect(self._recalc)
        chk_w = QWidget(); cl = QHBoxLayout(chk_w)
        cl.setContentsMargins(6,0,0,0); cl.addWidget(chk)
        chk_w.setStyleSheet("background:transparent;")
        self.items_table.setCellWidget(row, 6, chk_w)

        self._recalc()

    def _recalc(self):
        activities = 0.0; penalties = 0.0
        for row in range(self.items_table.rowCount()):
            sp_qty   = self.items_table.cellWidget(row, 3)
            sp_price = self.items_table.cellWidget(row, 4)
            chk_w    = self.items_table.cellWidget(row, 6)
            sub_lbl  = self.items_table.cellWidget(row, 5)
            if not all([sp_qty, sp_price, chk_w, sub_lbl]): continue
            chk = chk_w.findChild(QCheckBox)
            qty   = sp_qty.value()
            price = sp_price.value()
            sub   = qty * price
            sub_lbl.setText(fmt_money(sub))
            is_pen = chk and chk.isChecked()
            color = RED if is_pen else TEXT_PRI
            sub_lbl.setStyleSheet(f"color:{color}; font-size:11px; font-family:'Inter'; padding-right:6px; background:transparent; border:none;")
            if is_pen: penalties += sub
            else:      activities += sub

        net     = activities - penalties
        monthly = 0.0
        if self.rb_beca.isChecked() and self._selected_person:
            sch = self._sch_repo.get_by_person(self._selected_person["id"])
            if sch: monthly = float(sch["monthly_fee"])

        self.lbl_activities.setText(fmt_money(activities))
        self.lbl_penalties.setText(fmt_money(penalties))
        self.lbl_net.setText(fmt_money(net))

        if self.rb_beca.isChecked():
            balance = net - monthly
            dojo_owes = max(balance, 0)
            beca_owes = max(-balance, 0)
            self.lbl_monthly.setText(fmt_money(monthly))
            self.lbl_dojo_owes.setText(fmt_money(dojo_owes))
            self.lbl_beca_owes.setText(fmt_money(beca_owes))

    def _calculate_from_scholarship(self):
        if not self._selected_person:
            QMessageBox.warning(self, "Aviso", "Selecciona un colaborador primero.")
            return
        month = self.cmb_month.currentData()
        year  = self.cmb_year.currentData()
        sch   = self._sch_repo.get_by_person(self._selected_person["id"])
        if not sch:
            QMessageBox.warning(self, "Sin beca", "Este colaborador no tiene una beca activa.")
            return
        balance = self._sch_repo.calculate_monthly_balance(self._selected_person["id"], month, year)
        if not balance:
            QMessageBox.information(self, "Sin datos", "No se encontraron actividades para este período.")
            return
        m_name = MONTHS[month-1]
        self.inp_concept.setPlainText(
            f"Liquidación de beca - {m_name} {year}\n"
            f"Colaborador: {self._selected_person['name']}"
        )
        QMessageBox.information(self, "Cálculo completado",
            f"Actividades: {fmt_money(balance['activities'])}\n"
            f"Penalizaciones: {fmt_money(balance['penalties'])}\n"
            f"Total neto: {fmt_money(balance['net'])}\n"
            f"Mensualidad base: {fmt_money(balance['monthly_fee'])}\n\n"
            + (f"El dojo debe pagar: {fmt_money(balance['dojo_owes'])}" if balance['dojo_owes'] > 0
               else f"El becado debe pagar: {fmt_money(balance['becado_owes'])}")
        )
        self._recalc()

    def _collect_items(self):
        items = []
        for row in range(self.items_table.rowCount()):
            cmb      = self.items_table.cellWidget(row, 0)
            inp_desc = self.items_table.cellWidget(row, 1)
            dp       = self.items_table.cellWidget(row, 2)
            sp_qty   = self.items_table.cellWidget(row, 3)
            sp_price = self.items_table.cellWidget(row, 4)
            chk_w    = self.items_table.cellWidget(row, 6)
            if not all([cmb, inp_desc, sp_qty, sp_price, chk_w]): continue
            chk = chk_w.findChild(QCheckBox)
            qty   = sp_qty.value()
            price = sp_price.value()
            items.append({
                "activity_type": cmb.currentData(),
                "description":   inp_desc.text().strip(),
                "quantity":      qty,
                "unit_price":    price,
                "subtotal":      qty * price,
                "activity_date": dp.date().toPyDate() if dp else None,
                "penalty":       bool(chk and chk.isChecked()),
            })
        return items

    def _load_existing(self):
        acc = self._repo.get_by_id(self._account_id)
        if not acc: return
        items = self._repo.get_items(self._account_id)

        if acc.get("person_id"):
            people = self._repo.search_people("")
            p = next((pp for pp in people if pp["id"] == acc["person_id"]), None)
            if p: self._select_person(p)
        if acc.get("person_name") and not self._selected_person:
            self.inp_person.setText(acc["person_name"])

        if acc.get("scholarship_id") or (acc.get("period_month") and acc.get("period_year")):
            self.rb_beca.setChecked(True)
            if acc.get("period_month"):
                self.cmb_month.setCurrentIndex(acc["period_month"] - 1)
            if acc.get("period_year"):
                for i in range(self.cmb_year.count()):
                    if self.cmb_year.itemData(i) == acc["period_year"]:
                        self.cmb_year.setCurrentIndex(i); break

        self.inp_concept.setPlainText(acc.get("concept",""))
        if acc.get("issued_date"):
            d = acc["issued_date"]
            self.dp_issued.setDate(QDate(d.year, d.month, d.day))
        if acc.get("due_date"):
            d = acc["due_date"]
            self.dp_due.setDate(QDate(d.year, d.month, d.day))
        self.inp_notes.setPlainText(acc.get("notes",""))

        for item in items:
            self._add_item_row(item)

    def _save(self):
        concept = self.inp_concept.toPlainText().strip()
        if not concept:
            QMessageBox.warning(self, "Aviso", "El concepto es obligatorio."); return
        if not self._selected_person and not self.inp_person.text().strip():
            QMessageBox.warning(self, "Aviso", "Debes indicar un colaborador."); return

        items = self._collect_items()
        activities = sum(i["subtotal"] for i in items if not i["penalty"])
        penalties  = sum(i["subtotal"] for i in items if i["penalty"])
        total      = activities - penalties

        data = {
            "person_id":     self._selected_person["id"] if self._selected_person else None,
            "person_name":   self._selected_person["name"] if self._selected_person else self.inp_person.text().strip(),
            "concept":       concept,
            "total_amount":  total,
            "status":        "draft",
            "issued_date":   self.dp_issued.date().toPyDate(),
            "due_date":      self.dp_due.date().toPyDate(),
            "notes":         self.inp_notes.toPlainText().strip(),
            "scholarship_id":None,
            "period_month":  self.cmb_month.currentData() if self.rb_beca.isChecked() else None,
            "period_year":   self.cmb_year.currentData()  if self.rb_beca.isChecked() else None,
            "items":         items,
        }

        try:
            if self._account_id:
                self._repo.update(self._account_id, data)
            else:
                self._repo.create(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
