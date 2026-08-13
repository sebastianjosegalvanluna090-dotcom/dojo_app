from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from repositories.finances_collection_accounts_repository import FinancesCollectionAccountsRepository

BG_DIALOG = "#0E0E0E"
BG_CARD   = "#141414"
BG_HOVER  = "#1E1E1E"
BORDER    = "#222222"
RED       = "#E11D48"
RED_H     = "#FF1F4E"
GREEN     = "#22C55E"
YELLOW    = "#EAB308"
BLUE      = "#3B82F6"
PURPLE    = "#A855F7"
TEXT_PRI  = "#FAFAFA"
TEXT_SEC  = "#A3A3A3"
TEXT_MUT  = "#666666"

STATUS_COLORS = {
    "draft":"#6B7280","pending":YELLOW,"approved":BLUE,"paid":GREEN,"cancelled":"#4B4B4B"
}
STATUS_LABELS = {
    "draft":"Borrador","pending":"Pendiente","approved":"Aprobada",
    "paid":"Pagada","cancelled":"Cancelada"
}
MONTHS = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
          "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]


def fmt_money(v):
    try: v = float(v or 0)
    except: v = 0
    return "$" + f"{v:,.0f}".replace(",",".")

def fmt_date(d):
    if not d: return "—"
    try: return d.strftime("%d/%m/%Y") if hasattr(d,"strftime") else str(d)[:10]
    except: return str(d)[:10]


class CollectionAccountDetailsDialog(QDialog):
    status_changed = pyqtSignal()

    def __init__(self, account_id, parent=None):
        super().__init__(parent)
        self._account_id = account_id
        self._repo       = FinancesCollectionAccountsRepository()
        self._account    = None
        self._items      = []
        self.setWindowTitle("Detalle de cuenta de cobro")
        self.setMinimumSize(720, 580)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background:{BG_DIALOG}; color:{TEXT_PRI};")
        self._build_ui()
        self._load()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border:none; background:transparent; }}
            QScrollBar:vertical {{ background:transparent; width:5px; }}
            QScrollBar::handle:vertical {{ background:#2A2A2A; border-radius:2px; min-height:20px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
        """)
        cont = QWidget(); cont.setStyleSheet("background:transparent;")
        cv = QVBoxLayout(cont); cv.setContentsMargins(28,24,28,16); cv.setSpacing(16)

        self.hdr_frame = QFrame()
        self.hdr_frame.setStyleSheet(f"QFrame {{ background:{BG_CARD}; border:1px solid {BORDER}; border-radius:12px; }} QFrame * {{ border:none; background:transparent; }}")
        hfl = QVBoxLayout(self.hdr_frame); hfl.setContentsMargins(20,18,20,18); hfl.setSpacing(10)

        top = QHBoxLayout()
        self.lbl_name = QLabel("—")
        self.lbl_name.setStyleSheet(f"color:{TEXT_PRI}; font-size:20px; font-weight:900; font-family:'Inter';")
        top.addWidget(self.lbl_name, 1)
        self.badge_status = QLabel("—")
        self.badge_status.setStyleSheet(f"color:{TEXT_MUT}; font-size:11px; font-weight:700; font-family:'Inter'; padding:4px 12px; border-radius:8px;")
        top.addWidget(self.badge_status)
        hfl.addLayout(top)

        self.lbl_concept = QLabel("—")
        self.lbl_concept.setWordWrap(True)
        self.lbl_concept.setStyleSheet(f"color:{TEXT_SEC}; font-size:12px; font-family:'Inter';")
        hfl.addWidget(self.lbl_concept)

        meta = QHBoxLayout(); meta.setSpacing(20)
        self.lbl_period  = QLabel()
        self.lbl_issued  = QLabel()
        self.lbl_due     = QLabel()
        for l in [self.lbl_period, self.lbl_issued, self.lbl_due]:
            l.setStyleSheet(f"color:{TEXT_MUT}; font-size:11px; font-family:'Inter';")
            meta.addWidget(l)
        meta.addStretch()
        hfl.addLayout(meta)
        cv.addWidget(self.hdr_frame)

        kpi_row = QHBoxLayout(); kpi_row.setSpacing(10)
        self.kpi_activities = self._kpi("ACTIVIDADES", GREEN)
        self.kpi_penalties  = self._kpi("PENALIZACIONES", RED)
        self.kpi_total      = self._kpi("TOTAL NETO", TEXT_PRI)
        for k in [self.kpi_activities, self.kpi_penalties, self.kpi_total]:
            kpi_row.addWidget(k)
        cv.addLayout(kpi_row)

        cv.addWidget(self._section_lbl("DETALLE DE ACTIVIDADES"))
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Tipo","Descripción","Fecha","Cant.","Precio unit.","Subtotal"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for col, w in [(0,110),(2,85),(3,50),(4,95),(5,90)]:
            self.table.setColumnWidth(col, w)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{ background:transparent; color:{TEXT_PRI}; border:none;
                font-size:12px; font-family:'Inter'; }}
            QHeaderView::section {{ background:{BG_CARD}; color:{TEXT_MUT}; border:none;
                border-bottom:1px solid {BORDER}; padding:6px 8px; font-size:9px;
                font-weight:800; letter-spacing:1px; }}
            QTableWidget::item {{ padding:6px 8px; border-bottom:1px solid {BORDER}; }}
            QTableWidget::item:selected {{ background:#1F0A10; }}
        """)
        cv.addWidget(self.table)

        self.notes_frame = QFrame()
        self.notes_frame.setStyleSheet(f"QFrame {{ background:{BG_CARD}; border:1px solid {BORDER}; border-radius:10px; }} QFrame * {{ border:none; background:transparent; }}")
        nfl = QVBoxLayout(self.notes_frame); nfl.setContentsMargins(16,14,16,14); nfl.setSpacing(6)
        nfl.addWidget(self._section_lbl("NOTAS INTERNAS"))
        self.lbl_notes = QLabel("—")
        self.lbl_notes.setWordWrap(True)
        self.lbl_notes.setStyleSheet(f"color:{TEXT_SEC}; font-size:12px; font-family:'Inter';")
        nfl.addWidget(self.lbl_notes)
        cv.addWidget(self.notes_frame)
        cv.addStretch()
        scroll.setWidget(cont)
        root.addWidget(scroll, 1)

        footer = QFrame()
        footer.setStyleSheet(f"QFrame {{ background:{BG_CARD}; border-top:1px solid {BORDER}; }}")
        fl = QHBoxLayout(footer); fl.setContentsMargins(24,14,24,14); fl.setSpacing(10)

        self.btn_approve = QPushButton("✓ Aprobar")
        self.btn_pay     = QPushButton("💰 Marcar pagada")
        self.btn_edit    = QPushButton("Editar")
        btn_close        = QPushButton("Cerrar")

        for btn in [self.btn_approve, self.btn_pay]:
            btn.setFixedHeight(38)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_approve.setStyleSheet(f"""
            QPushButton {{ background:{BLUE}; color:white; border:none;
                border-radius:8px; font-size:12px; font-weight:700; font-family:'Inter'; padding:0 16px; }}
            QPushButton:hover {{ background:#2563EB; }}
        """)
        self.btn_pay.setStyleSheet(f"""
            QPushButton {{ background:{GREEN}; color:white; border:none;
                border-radius:8px; font-size:12px; font-weight:700; font-family:'Inter'; padding:0 16px; }}
            QPushButton:hover {{ background:#16A34A; }}
        """)
        self.btn_edit.setFixedHeight(38)
        self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit.setStyleSheet(f"""
            QPushButton {{ background:transparent; color:{TEXT_SEC}; border:1px solid {BORDER};
                border-radius:8px; font-size:12px; font-family:'Inter'; padding:0 16px; }}
            QPushButton:hover {{ color:{TEXT_PRI}; }}
        """)
        btn_close.setFixedHeight(38)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{ background:transparent; color:{TEXT_SEC}; border:1px solid {BORDER};
                border-radius:8px; font-size:12px; font-family:'Inter'; padding:0 16px; }}
            QPushButton:hover {{ color:{TEXT_PRI}; }}
        """)
        self.btn_approve.clicked.connect(lambda: self._change_status("approved"))
        self.btn_pay.clicked.connect(lambda:     self._change_status("paid"))
        self.btn_edit.clicked.connect(self._open_edit)
        btn_close.clicked.connect(self.accept)

        fl.addWidget(self.btn_approve)
        fl.addWidget(self.btn_pay)
        fl.addWidget(self.btn_edit)
        fl.addStretch()
        fl.addWidget(btn_close)
        root.addWidget(footer)

    def _kpi(self, title, color):
        f = QFrame()
        f.setStyleSheet(f"QFrame {{ background:{BG_CARD}; border:1px solid {BORDER}; border-radius:10px; }}")
        lay = QVBoxLayout(f); lay.setContentsMargins(16,12,16,12); lay.setSpacing(4)
        lt = QLabel(title)
        lt.setStyleSheet(f"color:{TEXT_MUT}; font-size:9px; font-weight:800; letter-spacing:1px; font-family:'Inter'; border:none; background:transparent;")
        lv = QLabel("—")
        lv.setStyleSheet(f"color:{color}; font-size:20px; font-weight:900; font-family:'Inter'; border:none; background:transparent;")
        lay.addWidget(lt); lay.addWidget(lv)
        f._lv = lv
        return f

    def _section_lbl(self, text):
        l = QLabel(text)
        l.setStyleSheet(f"color:{TEXT_MUT}; font-size:9px; font-weight:800; letter-spacing:1.4px; font-family:'Inter'; border:none; background:transparent;")
        return l

    def _load(self):
        self._account = self._repo.get_by_id(self._account_id)
        self._items   = self._repo.get_items(self._account_id)
        if not self._account: return
        acc = self._account

        self.lbl_name.setText(acc.get("person_name","—"))
        status = acc.get("status","draft")
        sc = STATUS_COLORS.get(status, TEXT_MUT)
        sl = STATUS_LABELS.get(status, status)
        self.badge_status.setText(f" {sl} ")
        self.badge_status.setStyleSheet(f"""
            color:{sc}; background:{sc}18; border:1px solid {sc}40;
            border-radius:8px; font-size:11px; font-weight:700; font-family:'Inter'; padding:4px 12px;
        """)

        self.lbl_concept.setText(acc.get("concept","—"))
        pm, py = acc.get("period_month"), acc.get("period_year")
        if pm and py:
            self.lbl_period.setText(f"Período: {MONTHS[pm-1]} {py}")
        self.lbl_issued.setText(f"Emisión: {fmt_date(acc.get('issued_date'))}")
        if acc.get("due_date"):
            self.lbl_due.setText(f"Vence: {fmt_date(acc['due_date'])}")

        activities = sum(i["subtotal"] for i in self._items if not i.get("penalty"))
        penalties  = sum(i["subtotal"] for i in self._items if i.get("penalty"))
        total      = activities - penalties
        self.kpi_activities._lv.setText(fmt_money(activities))
        self.kpi_penalties._lv.setText(fmt_money(penalties))
        self.kpi_total._lv.setText(fmt_money(total))

        ACTIVITY_LABELS = {
            "clase":"Clase","aseo_profundo":"Aseo profundo",
            "aseo_mantenimiento":"Aseo mantenimiento",
            "penalizacion":"Penalización","otro":"Otro"
        }
        self.table.setRowCount(len(self._items))
        for i, item in enumerate(self._items):
            is_pen = item.get("penalty", False)
            color  = RED if is_pen else None
            self.table.setRowHeight(i, 38)

            cells = [
                ACTIVITY_LABELS.get(item.get("activity_type","otro"), "Otro"),
                item.get("description",""),
                fmt_date(item.get("activity_date")),
                str(item.get("quantity",1)),
                fmt_money(item.get("unit_price",0)),
                ("-" if is_pen else "") + fmt_money(item.get("subtotal",0)),
            ]
            for col, val in enumerate(cells):
                qi = QTableWidgetItem(val)
                if color: qi.setForeground(QColor(color))
                qi.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | (
                    Qt.AlignmentFlag.AlignRight if col in (3,4,5) else Qt.AlignmentFlag.AlignLeft
                ))
                self.table.setItem(i, col, qi)

        notes = acc.get("notes","").strip()
        self.lbl_notes.setText(notes if notes else "Sin notas.")
        self.notes_frame.setVisible(bool(notes))

        self.btn_approve.setVisible(status in ("draft","pending"))
        self.btn_pay.setVisible(status == "approved")
        self.btn_edit.setVisible(status not in ("paid","cancelled"))

    def _change_status(self, status):
        self._repo.update_status(self._account_id, status)
        self.status_changed.emit()
        self._load()

    def _open_edit(self):
        from views.finances.collection_accounts.collection_account_dialog import CollectionAccountDialog
        dlg = CollectionAccountDialog(account_id=self._account_id, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.status_changed.emit()
            self._load()
