from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
    QScrollArea, QLineEdit, QMenu, QDialog, QSizePolicy,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint, QTimer, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QFont

from core.i18n import tr
from repositories.finances_collection_accounts_repository import FinancesCollectionAccountsRepository

BG_DEEP  = "#050505"
BG_CARD  = "#0C0C0C"
BG_HOVER = "#141414"
BORDER   = "#1F1F1F"
RED      = "#E11D48"
RED_H    = "#FF1F4E"
GREEN    = "#22C55E"
YELLOW   = "#EAB308"
BLUE     = "#3B82F6"
PURPLE   = "#A855F7"
ORANGE   = "#F97316"
TEXT_PRI = "#FAFAFA"
TEXT_SEC = "#A3A3A3"
TEXT_MUT = "#666666"

STATUS_COLORS = {
    "draft":     TEXT_MUT,
    "pending":   YELLOW,
    "approved":  BLUE,
    "paid":      GREEN,
    "cancelled": "#4B4B4B",
}
STATUS_LABELS = {
    "draft":     "Borrador",
    "pending":   "Pendiente",
    "approved":  "Aprobada",
    "paid":      "Pagada",
    "cancelled": "Cancelada",
}
MONTHS = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
          "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]


def fmt_money(v):
    try: v = float(v or 0)
    except: v = 0
    return "$" + f"{v:,.0f}".replace(",", ".")


def fmt_date(d):
    if not d: return "—"
    try: return d.strftime("%d/%m/%Y") if hasattr(d, "strftime") else str(d)[:10]
    except: return str(d)[:10]


class LoadWorker(QThread):
    done   = pyqtSignal(list)
    failed = pyqtSignal(str)
    def __init__(self, repo, search, status_filter):
        super().__init__()
        self.repo = repo; self.search = search; self.status_filter = status_filter
    def run(self):
        try:    self.done.emit(self.repo.get_all(self.search, self.status_filter))
        except Exception as e: self.failed.emit(str(e))


class FilterPill(QPushButton):
    def __init__(self, label, active=False, parent=None):
        super().__init__(label, parent)
        self._active = active
        self.setFixedHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply()
    def set_active(self, v):
        self._active = v; self._apply()
    def _apply(self):
        if self._active:
            self.setStyleSheet("""
                QPushButton { background:#FAFAFA; color:#050505; border:none;
                    border-radius:16px; font-size:12px; font-weight:700;
                    font-family:'Inter'; padding:0 16px; }
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{ background:{BG_CARD}; color:{TEXT_MUT}; border:1px solid {BORDER};
                    border-radius:16px; font-size:12px; font-weight:600;
                    font-family:'Inter'; padding:0 16px; }}
                QPushButton:hover {{ background:{BG_HOVER}; color:{TEXT_SEC}; }}
            """)


class KpiCard(QFrame):
    def __init__(self, title, color, parent=None):
        super().__init__(parent)
        self.setFixedHeight(86)
        self.setStyleSheet(f"QFrame {{ background:{BG_CARD}; border:1px solid {BORDER}; border-radius:12px; }}")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12); lay.setSpacing(4)
        lbl_t = QLabel(title)
        lbl_t.setStyleSheet(f"color:{TEXT_MUT}; font-size:10px; font-weight:700; font-family:'Inter'; letter-spacing:1px; border:none; background:transparent;")
        self.lbl_v = QLabel("—")
        self.lbl_v.setStyleSheet(f"color:{color}; font-size:22px; font-weight:900; font-family:'Inter'; border:none; background:transparent;")
        lay.addWidget(lbl_t); lay.addWidget(self.lbl_v)
    def set_value(self, v): self.lbl_v.setText(str(v))


class AccountCard(QFrame):
    clicked        = pyqtSignal(int)
    double_clicked = pyqtSignal(int)
    menu_requested = pyqtSignal(int, QPoint)

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._id   = data["id"]
        self._data = data
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(96)
        self._normal_style()
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16); shadow.setOffset(0, 3); shadow.setColor(QColor(0,0,0,80))
        self.setGraphicsEffect(shadow)
        self._build(data)

    def _normal_style(self):
        self.setStyleSheet(f"QFrame {{ background:{BG_CARD}; border:1px solid {BORDER}; border-radius:12px; }}")
    def enterEvent(self, e):
        self.setStyleSheet(f"QFrame {{ background:{BG_HOVER}; border:1px solid #2A2A2A; border-radius:12px; }}")
        super().enterEvent(e)
    def leaveEvent(self, e):
        self._normal_style(); super().leaveEvent(e)

    def _build(self, d):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 12, 14, 12); lay.setSpacing(14)

        name = d.get("person_name","?")
        initials = "".join(w[0].upper() for w in name.split()[:2]) or "?"
        av = QLabel(initials)
        av.setFixedSize(44, 44)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet(f"""
            QLabel {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #7C3AED, stop:1 #4F46E5);
                color:white; border-radius:22px; font-size:15px; font-weight:900;
                font-family:'Inter'; border:none; }}
        """)
        lay.addWidget(av)

        info = QVBoxLayout(); info.setSpacing(4); info.setContentsMargins(0,0,0,0)

        top = QHBoxLayout(); top.setSpacing(10)
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet(f"color:{TEXT_PRI}; font-size:14px; font-weight:700; font-family:'Inter'; border:none; background:transparent;")
        top.addWidget(lbl_name)

        pm, py = d.get("period_month"), d.get("period_year")
        if pm and py:
            period_lbl = QLabel(f"{MONTHS[pm-1]} {py}")
            period_lbl.setStyleSheet(f"color:{PURPLE}; font-size:11px; font-weight:700; font-family:'Inter'; border:none; background:transparent;")
            top.addWidget(period_lbl)

        status = d.get("status","draft")
        sc = STATUS_COLORS.get(status, TEXT_MUT)
        sl = STATUS_LABELS.get(status, status.capitalize())
        badge = QLabel(f" {sl} ")
        badge.setStyleSheet(f"""
            color:{sc}; background:{sc}18; border:1px solid {sc}40;
            border-radius:8px; font-size:10px; font-weight:700;
            font-family:'Inter'; padding:2px 8px;
        """)
        top.addWidget(badge)
        top.addStretch()

        btn_menu = QPushButton("•••")
        btn_menu.setFixedSize(26, 26)
        btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_menu.setStyleSheet(f"""
            QPushButton {{ background:transparent; color:{TEXT_MUT}; border:none; font-size:12px; border-radius:13px; }}
            QPushButton:hover {{ background:{BG_HOVER}; color:{TEXT_SEC}; }}
        """)
        btn_menu.clicked.connect(lambda: self.menu_requested.emit(
            self._id, self.mapToGlobal(QPoint(self.width()-10, 30))
        ))
        top.addWidget(btn_menu)
        info.addLayout(top)

        bot = QHBoxLayout(); bot.setSpacing(16)
        concept = d.get("concept","")
        if concept:
            lbl_c = QLabel(concept[:60] + ("…" if len(concept)>60 else ""))
            lbl_c.setStyleSheet(f"color:{TEXT_SEC}; font-size:11px; font-family:'Inter'; border:none; background:transparent;")
            bot.addWidget(lbl_c)
        if d.get("due_date"):
            lbl_d = QLabel(f"Vence: {fmt_date(d['due_date'])}")
            lbl_d.setStyleSheet(f"color:{YELLOW}; font-size:11px; font-weight:600; font-family:'Inter'; border:none; background:transparent;")
            bot.addWidget(lbl_d)
        bot.addStretch()
        info.addLayout(bot)
        lay.addLayout(info, 1)

        lbl_total = QLabel(fmt_money(d.get("total_amount",0)))
        lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl_total.setStyleSheet(f"color:{TEXT_PRI}; font-size:18px; font-weight:900; font-family:'Inter'; border:none; background:transparent;")
        lay.addWidget(lbl_total)

    def mousePressEvent(self, e):
        self.clicked.emit(self._id); super().mousePressEvent(e)
    def mouseDoubleClickEvent(self, e):
        self.double_clicked.emit(self._id); super().mouseDoubleClickEvent(e)


class CollectionAccountsView(QWidget):
    def __init__(self, blur_on=None, blur_off=None, parent=None):
        super().__init__(parent)
        self._repo               = FinancesCollectionAccountsRepository()
        self.blur_on             = blur_on  or (lambda: None)
        self.blur_off            = blur_off or (lambda: None)
        self._accounts           = []
        self._search_text        = ""
        self._active_filter      = "all"
        self._worker             = None
        self._dialog_open        = False
        self._details_open       = False
        self._build_ui()
        self._load()

    def _build_ui(self):
        self.setStyleSheet(f"background:{BG_DEEP};")
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24); root.setSpacing(18)

        hdr = QHBoxLayout()
        left = QVBoxLayout(); left.setSpacing(2)
        lbl_t = QLabel("Cuentas de Cobro")
        lbl_t.setStyleSheet(f"color:{TEXT_PRI}; font-size:24px; font-weight:900; font-family:'Inter'; border:none; background:transparent;")
        lbl_s = QLabel("GESTIÓN DE PAGOS A COLABORADORES")
        lbl_s.setStyleSheet(f"color:{TEXT_MUT}; font-size:9px; font-weight:800; letter-spacing:1.5px; font-family:'Inter'; border:none; background:transparent;")
        left.addWidget(lbl_t); left.addWidget(lbl_s)
        hdr.addLayout(left); hdr.addStretch()

        btn_scholars = QPushButton("🎓 Becas")
        btn_scholars.setFixedHeight(38)
        btn_scholars.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_scholars.setStyleSheet(f"""
            QPushButton {{ background:transparent; color:{TEXT_SEC}; border:1px solid {BORDER};
                border-radius:9px; font-size:12px; font-weight:700; font-family:'Inter'; padding:0 16px; }}
            QPushButton:hover {{ border-color:#444; color:{TEXT_PRI}; }}
        """)
        btn_scholars.clicked.connect(self._open_scholarships)
        hdr.addWidget(btn_scholars)

        btn_new = QPushButton("+ Nueva cuenta de cobro")
        btn_new.setFixedHeight(38)
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.setStyleSheet(f"""
            QPushButton {{ background:{RED}; color:white; border:none;
                border-radius:9px; font-size:12px; font-weight:800; font-family:'Inter'; padding:0 18px; }}
            QPushButton:hover {{ background:{RED_H}; }}
        """)
        btn_new.clicked.connect(self._open_new)
        hdr.addWidget(btn_new)
        root.addLayout(hdr)

        kpi_row = QHBoxLayout(); kpi_row.setSpacing(12)
        self.kpi_pending  = KpiCard("PENDIENTE DE PAGO",   RED)
        self.kpi_approved = KpiCard("APROBADAS ESTE MES",  YELLOW)
        self.kpi_paid     = KpiCard("PAGADAS ESTE MES",    GREEN)
        self.kpi_scholars = KpiCard("COLABORADORES ACTIVOS", BLUE)
        for k in [self.kpi_pending, self.kpi_approved, self.kpi_paid, self.kpi_scholars]:
            kpi_row.addWidget(k)
        root.addLayout(kpi_row)

        filter_row = QHBoxLayout(); filter_row.setSpacing(10)
        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar colaborador, concepto...")
        self._search.setFixedHeight(36)
        self._search.setStyleSheet(f"""
            QLineEdit {{ background:{BG_CARD}; color:{TEXT_PRI}; border:1px solid {BORDER};
                border-radius:9px; padding:0 14px; font-size:12px; font-family:'Inter'; }}
            QLineEdit:focus {{ border-color:{RED}; }}
        """)
        self._search.textChanged.connect(lambda t: QTimer.singleShot(300, self._load))
        filter_row.addWidget(self._search, 1)

        self._pills = {}
        for key, label in [("all","Todos"),("draft","Borradores"),("pending","Pendientes"),
                            ("approved","Aprobadas"),("paid","Pagadas")]:
            p = FilterPill(label, key == "all")
            p.clicked.connect(lambda _, k=key: self._set_filter(k))
            filter_row.addWidget(p)
            self._pills[key] = p
        root.addLayout(filter_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background:transparent; border:none; }}
            QScrollBar:vertical {{ background:transparent; width:5px; }}
            QScrollBar::handle:vertical {{ background:#2A2A2A; border-radius:2px; min-height:20px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
        """)
        cont = QWidget(); cont.setStyleSheet("background:transparent;")
        self.cards_layout = QVBoxLayout(cont)
        self.cards_layout.setContentsMargins(0,0,0,0); self.cards_layout.setSpacing(8)
        self.cards_layout.addStretch()
        scroll.setWidget(cont)
        root.addWidget(scroll, 1)

        self.empty_lbl = QLabel("No hay cuentas de cobro registradas.")
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setStyleSheet(f"color:{TEXT_MUT}; font-size:14px; font-family:'Inter'; padding:40px;")
        self.empty_lbl.hide()
        root.addWidget(self.empty_lbl)

    def _set_filter(self, key):
        self._active_filter = key
        for k, p in self._pills.items(): p.set_active(k == key)
        self._load()

    def _load(self):
        if self._worker and self._worker.isRunning(): return
        self._worker = LoadWorker(self._repo, self._search.text().strip(), self._active_filter)
        self._worker.done.connect(self._on_loaded)
        self._worker.failed.connect(lambda e: print(f"[CA load] {e}"))
        self._worker.start()

    def _on_loaded(self, accounts):
        self._accounts = accounts
        kpis = self._repo.get_kpis()
        self.kpi_pending.set_value(fmt_money(kpis["pending_amount"]))
        self.kpi_approved.set_value(str(kpis["approved_this_month"]))
        self.kpi_paid.set_value(fmt_money(kpis["paid_this_month"]))
        self.kpi_scholars.set_value(str(kpis["active_scholars"]))
        self._paint_cards()

    def _paint_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        if not self._accounts:
            self.empty_lbl.show()
        else:
            self.empty_lbl.hide()
            for acc in self._accounts:
                card = AccountCard(acc)
                card.double_clicked.connect(self._open_details)
                card.menu_requested.connect(self._on_menu)
                self.cards_layout.addWidget(card)
        self.cards_layout.addStretch()

    def _on_menu(self, account_id, pos):
        acc = next((a for a in self._accounts if a["id"] == account_id), None)
        if not acc: return
        status = acc.get("status","draft")
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background:{BG_CARD}; color:{TEXT_PRI}; border:1px solid {BORDER};
                border-radius:8px; padding:6px; font-size:12px; font-family:'Inter'; }}
            QMenu::item {{ padding:8px 18px; border-radius:4px; }}
            QMenu::item:selected {{ background:{BG_HOVER}; }}
        """)
        a_detail   = menu.addAction("Ver detalle")
        a_edit     = menu.addAction("Editar") if status not in ("paid","cancelled") else None
        menu.addSeparator()
        a_approve  = menu.addAction("✓ Aprobar")    if status in ("draft","pending")  else None
        a_pay      = menu.addAction("💰 Marcar pagada") if status == "approved"       else None
        a_cancel   = menu.addAction("✕ Cancelar")   if status not in ("paid","cancelled") else None
        menu.addSeparator()
        a_delete   = menu.addAction("Eliminar")
        action = menu.exec(pos)
        if action == a_detail:  self._open_details(account_id)
        elif a_edit   and action == a_edit:   self._open_edit(account_id)
        elif a_approve and action == a_approve: self._change_status(account_id,"approved")
        elif a_pay    and action == a_pay:    self._change_status(account_id,"paid")
        elif a_cancel and action == a_cancel: self._change_status(account_id,"cancelled")
        elif action == a_delete: self._delete(account_id)

    def _change_status(self, account_id, status):
        self._repo.update_status(account_id, status)
        self._load()

    def _open_new(self):
        if self._dialog_open: return
        from views.finances.collection_accounts.collection_account_dialog import CollectionAccountDialog
        self._dialog_open = True; self.blur_on()
        dlg = CollectionAccountDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted: self._load()
        self.blur_off(); dlg.deleteLater(); self._dialog_open = False

    def _open_edit(self, account_id):
        if self._dialog_open: return
        from views.finances.collection_accounts.collection_account_dialog import CollectionAccountDialog
        self._dialog_open = True; self.blur_on()
        dlg = CollectionAccountDialog(account_id=account_id, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted: self._load()
        self.blur_off(); dlg.deleteLater(); self._dialog_open = False

    def _open_details(self, account_id):
        if self._details_open: return
        from views.finances.collection_accounts.collection_account_details_dialog import CollectionAccountDetailsDialog
        self._details_open = True; self.blur_on()
        dlg = CollectionAccountDetailsDialog(account_id=account_id, parent=self)
        dlg.status_changed.connect(self._load)
        dlg.exec()
        self.blur_off(); dlg.deleteLater(); self._details_open = False

    def _open_scholarships(self):
        from views.finances.collection_accounts.scholarship_dialog import ScholarshipDialog
        self.blur_on()
        dlg = ScholarshipDialog(parent=self)
        dlg.exec()
        self.blur_off(); dlg.deleteLater()

    def _delete(self, account_id):
        from PyQt6.QtWidgets import QMessageBox
        acc = next((a for a in self._accounts if a["id"]==account_id), {})
        msg = QMessageBox(self)
        msg.setWindowTitle("Eliminar cuenta de cobro")
        msg.setText(f"¿Eliminar la cuenta de cobro de '{acc.get('person_name','')}'?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet(f"QMessageBox {{ background:{BG_DEEP}; color:{TEXT_PRI}; }}")
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self._repo.delete(account_id); self._load()

    def prepare_for_app_shutdown(self):
        if self._worker and self._worker.isRunning():
            self._worker.quit(); self._worker.wait(2000)
