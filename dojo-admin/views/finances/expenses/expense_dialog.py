from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QFrame, QScrollArea,
    QWidget, QMessageBox, QDateEdit, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QSpinBox,
    QDoubleSpinBox, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve, QTimer, QPoint, QParallelAnimationGroup
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

from core.i18n import tr
from repositories.finances_expenses_repository import FinancesExpensesRepository
from repositories.inventory_repository import InventoryRepository

# Paleta de colores
BG_DIALOG = "#0F0F0F"
BG_CARD   = "#161616"
BG_INPUT  = "#1A1A1A"
BORDER    = "#2A2A2A"
RED       = "#C8102E"
RED_H     = "#E8152F"
TEXT_PRI  = "#F0F0F0"
TEXT_MUT  = "#666666"
TEXT_SEC  = "#888888"
GREEN     = "#22C55E"
BLUE      = "#3B82F6"

class ExpenseDialog(QDialog):
    def __init__(self, repo, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.inventory_repo = InventoryRepository()
        self._inventory_items = []
        
        self.setWindowTitle(tr("finances.expenses.new"))
        self.setMinimumSize(980, 660)
        self.resize(980, 700)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")
        
        # Animación de entrada (Fade In)
        self.setWindowOpacity(0.0)
        self._anim_opacity = QPropertyAnimation(self, b"windowOpacity", self)
        self._anim_opacity.setDuration(300)
        self._anim_opacity.setStartValue(0.0)
        self._anim_opacity.setEndValue(1.0)
        self._anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._build_ui()
        self._load_categories()
        self._update_preview()
        
        QTimer.singleShot(50, self._anim_opacity.start)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)
        
        accent_line = QFrame()
        accent_line.setFixedWidth(4)
        accent_line.setFixedHeight(32)
        accent_line.setStyleSheet(f"background-color: {RED}; border-radius: 2px;")
        
        title = QLabel(tr("finances.expenses.new"))
        title.setStyleSheet("color: white; font-size: 24px; font-weight: 900; font-family: 'Inter';")
        
        header_layout.addWidget(accent_line)
        header_layout.addWidget(title)
        header_layout.addStretch()
        root.addLayout(header_layout)

        # Scroll Area principal
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        
        content_layout = QHBoxLayout(scroll_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(24)

        # Lado Izquierdo
        left_col = QVBoxLayout()
        left_col.setSpacing(20)
        
        # --- Frame Principal ---
        main_frame = QFrame()
        main_frame.setStyleSheet(f"""
            QFrame {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 16px; }}
            QLabel {{ background: transparent; border: none; }}
        """)
        
        shadow_main = QGraphicsDropShadowEffect(main_frame)
        shadow_main.setBlurRadius(30)
        shadow_main.setOffset(0, 10)
        shadow_main.setColor(QColor(0, 0, 0, 160))
        main_frame.setGraphicsEffect(shadow_main)

        main_layout = QGridLayout(main_frame)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        label_style = f"color: {TEXT_MUT}; font-size: 11px; font-weight: 800; font-family: 'Inter'; letter-spacing: 1px; text-transform: uppercase;"
        input_style = f"""
            QLineEdit, QDateEdit, QComboBox {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid transparent; border-radius: 10px;
                padding: 0 16px; font-size: 14px; min-height: 44px;
                font-family: 'Inter';
            }}
            QLineEdit:hover, QDateEdit:hover, QComboBox:hover {{
                border-color: #333333;
            }}
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {{
                border-color: {RED}; background: #1F1F1F;
            }}
            QComboBox::drop-down {{ border: none; width: 30px; }}
            QComboBox QAbstractItemView {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                selection-background-color: {RED}; border-radius: 8px;
                border: 1px solid {BORDER};
            }}
        """

        # Fila 0: Tipo (Full width para darle importancia)
        main_layout.addWidget(self._create_label(tr("finances.expenses.type"), label_style), 0, 0, 1, 2)
        self.cb_expense_type = QComboBox()
        self.cb_expense_type.addItem(" 🔴 Gasto Fijo", "fixed")
        self.cb_expense_type.addItem(" 🔵 Gasto Variable", "variable")
        self.cb_expense_type.setCurrentIndex(1)
        self.cb_expense_type.setStyleSheet(input_style)
        self.cb_expense_type.currentIndexChanged.connect(self._on_type_changed)
        self.cb_expense_type.currentTextChanged.connect(self._update_preview)
        main_layout.addWidget(self.cb_expense_type, 1, 0, 1, 2)

        # Fila 2: Fecha y Monto
        main_layout.addWidget(self._create_label(tr("finances.expenses.date"), label_style), 2, 0)
        main_layout.addWidget(self._create_label(tr("finances.expenses.amount"), label_style), 2, 1)

        self.expense_date = QDateEdit()
        self.expense_date.setDate(QDate.currentDate())
        self.expense_date.setCalendarPopup(True)
        self.expense_date.setStyleSheet(input_style)
        self.expense_date.dateChanged.connect(self._update_preview)
        main_layout.addWidget(self.expense_date, 3, 0)

        self.amount = QLineEdit()
        self.amount.setPlaceholderText("$ 0.00")
        self.amount.setStyleSheet(input_style)
        self.amount.textChanged.connect(self._update_preview)
        main_layout.addWidget(self.amount, 3, 1)

        # Fila 4: Categoría y Subcategoría
        main_layout.addWidget(self._create_label(tr("finances.expenses.category"), label_style), 4, 0)
        main_layout.addWidget(self._create_label(tr("finances.expenses.subcategory"), label_style), 4, 1)

        self.cb_category = QComboBox()
        self.cb_category.setStyleSheet(input_style)
        self.cb_category.currentIndexChanged.connect(self._on_category_changed)
        self.cb_category.currentTextChanged.connect(self._update_preview)
        main_layout.addWidget(self.cb_category, 5, 0)

        self.cb_subcategory = QComboBox()
        self.cb_subcategory.setStyleSheet(input_style)
        self.cb_subcategory.currentTextChanged.connect(self._update_preview)
        main_layout.addWidget(self.cb_subcategory, 5, 1)

        # Fila 6: Descripción
        main_layout.addWidget(self._create_label(tr("finances.expenses.description"), label_style), 6, 0, 1, 2)
        self.description = QLineEdit()
        self.description.setPlaceholderText("Ej: Compra de uniformes para el dojo")
        self.description.setStyleSheet(input_style)
        self.description.textChanged.connect(self._update_preview)
        main_layout.addWidget(self.description, 7, 0, 1, 2)

        # Fila 8: Proveedor y Factura
        main_layout.addWidget(self._create_label(tr("finances.expenses.supplier"), label_style), 8, 0)
        main_layout.addWidget(self._create_label(tr("finances.expenses.invoice"), label_style), 8, 1)

        self.supplier_name = QLineEdit()
        self.supplier_name.setStyleSheet(input_style)
        self.supplier_name.textChanged.connect(self._update_preview)
        main_layout.addWidget(self.supplier_name, 9, 0)

        self.invoice_number = QLineEdit()
        self.invoice_number.setStyleSheet(input_style)
        self.invoice_number.textChanged.connect(self._update_preview)
        main_layout.addWidget(self.invoice_number, 9, 1)

        # Fila 10: Checkbox Inventario
        self.affects_inventory = QCheckBox(tr("finances.expenses.affects_inventory"))
        self.affects_inventory.setStyleSheet(f"""
            QCheckBox {{
                color: {TEXT_PRI}; font-size: 14px; font-weight: 600;
                spacing: 12px; font-family: 'Inter'; background: transparent;
            }}
            QCheckBox::indicator {{
                width: 22px; height: 22px; border-radius: 6px;
                border: 2px solid {BORDER}; background: {BG_INPUT};
            }}
            QCheckBox::indicator:hover {{ border-color: {RED_H}; }}
            QCheckBox::indicator:checked {{ background-color: {RED}; border-color: {RED}; }}
        """)
        self.affects_inventory.stateChanged.connect(self._on_inventory_toggle)
        self.affects_inventory.stateChanged.connect(self._update_preview)
        main_layout.addWidget(self.affects_inventory, 10, 0, 1, 2)

        left_col.addWidget(main_frame)

        # --- Frame Inventario ---
        self.inventory_frame = QFrame()
        self.inventory_frame.setStyleSheet(f"""
            QFrame {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 16px; }}
            QLabel {{ background: transparent; border: none; }}
        """)
        
        shadow_inv = QGraphicsDropShadowEffect(self.inventory_frame)
        shadow_inv.setBlurRadius(30)
        shadow_inv.setOffset(0, 10)
        shadow_inv.setColor(QColor(0, 0, 0, 160))
        self.inventory_frame.setGraphicsEffect(shadow_inv)

        inv_layout = QVBoxLayout(self.inventory_frame)
        inv_layout.setContentsMargins(24, 20, 24, 20)
        inv_layout.setSpacing(16)

        inv_header = QLabel(tr("finances.expenses.inventory_items"))
        inv_header.setStyleSheet(f"color: {TEXT_PRI}; font-size: 16px; font-weight: 800; font-family: 'Inter';")
        inv_layout.addWidget(inv_header)

        self.inv_table = QTableWidget(0, 4)
        self.inv_table.setHorizontalHeaderLabels([
            tr("finances.expenses.product"), tr("finances.expenses.quantity"),
            tr("finances.expenses.unit_cost"), tr("finances.expenses.total"),
        ])
        self.inv_table.verticalHeader().setVisible(False)
        self.inv_table.setShowGrid(False)
        self.inv_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.inv_table.setStyleSheet(f"""
            QTableWidget {{ background-color: transparent; border: none; color: {TEXT_PRI}; font-size: 13px; font-family: 'Inter'; }}
            QHeaderView::section {{ background-color: #1A1A1A; color: {TEXT_MUT}; border: none; border-bottom: 1px solid #2A2A2A; padding: 12px; font-size: 10px; font-weight: 900; letter-spacing: 1px; }}
            QTableWidget::item {{ border: none; border-bottom: 1px solid #252525; padding: 10px; }}
            QTableWidget::item:hover {{ background-color: #1F1F1F; }}
        """)
        self.inv_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.inv_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.inv_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.inv_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.inv_table.setMinimumHeight(140)
        inv_layout.addWidget(self.inv_table)

        btn_add_product = QPushButton("＋ " + tr("finances.expenses.add_product"))
        btn_add_product.setFixedHeight(40)
        btn_add_product.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_product.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_SEC};
                border: 1.5px dashed #333333; border-radius: 10px;
                font-size: 13px; font-weight: 700; padding: 0 16px; font-family: 'Inter';
            }}
            QPushButton:hover {{ border-color: {RED}; color: {RED_H}; background: rgba(200, 16, 46, 0.05); }}
        """)
        btn_add_product.clicked.connect(self._add_inventory_product)
        inv_layout.addWidget(btn_add_product)

        self.inventory_frame.setMaximumHeight(0)
        self.inventory_frame.setVisible(False)
        left_col.addWidget(self.inventory_frame)
        
        content_layout.addLayout(left_col, 3)

        # --- Lado Derecho: Preview ---
        self._build_preview_card(content_layout)
        
        scroll.setWidget(scroll_content)
        root.addWidget(scroll, 1)

        # Error Label
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #FF4444; font-size: 13px; font-weight: 600; font-family: 'Inter'; margin-left: 10px;")
        self.lbl_error.hide()
        root.addWidget(self.lbl_error)

        # Footer
        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)
        
        btn_cancel = QPushButton(tr("cancel"))
        btn_cancel.setFixedHeight(46)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUT};
                border: 1.5px solid {BORDER}; border-radius: 12px; font-size: 14px;
                font-weight: 700; font-family: 'Inter'; padding: 0 24px;
            }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: #3A3A3A; background: {BG_INPUT}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton(tr("save"))
        self.btn_save.setFixedHeight(46)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background: {RED}; color: white;
                border: none; border-radius: 12px; font-size: 14px; font-weight: 800;
                font-family: 'Inter'; padding: 0 40px;
            }}
            QPushButton:hover {{ background: {RED_H}; }}
            QPushButton:pressed {{ background: #A60D24; }}
        """)
        
        shadow_save = QGraphicsDropShadowEffect(self.btn_save)
        shadow_save.setBlurRadius(20)
        shadow_save.setOffset(0, 6)
        shadow_save.setColor(QColor(200, 16, 46, 140))
        self.btn_save.setGraphicsEffect(shadow_save)
        
        self.btn_save.clicked.connect(self._save)

        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self.btn_save)
        root.addLayout(btn_row)

    def _build_preview_card(self, parent_layout):
        self.preview_frame = QFrame()
        self.preview_frame.setMinimumWidth(340)
        self.preview_frame.setStyleSheet(f"""
            QFrame {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 16px; }}
            QLabel {{ background: transparent; border: none; }}
        """)
        
        shadow_prev = QGraphicsDropShadowEffect(self.preview_frame)
        shadow_prev.setBlurRadius(30)
        shadow_prev.setOffset(0, 10)
        shadow_prev.setColor(QColor(0, 0, 0, 160))
        self.preview_frame.setGraphicsEffect(shadow_prev)
        
        vl = QVBoxLayout(self.preview_frame)
        vl.setContentsMargins(28, 28, 28, 28)
        vl.setSpacing(0)
        
        # Header
        hdr = QHBoxLayout()
        lbl_hdr = QLabel("VISTA PREVIA")
        lbl_hdr.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; font-weight: 900; letter-spacing: 1.5px; font-family: 'Inter';")
        hdr.addWidget(lbl_hdr)
        hdr.addStretch()
        vl.addLayout(hdr)
        vl.addSpacing(28)
        
        # Avatar Circulo
        avatar_row = QHBoxLayout()
        avatar_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.prev_avatar = QLabel("?")
        self.prev_avatar.setFixedSize(70, 70)
        self.prev_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prev_avatar.setStyleSheet(f"""
            QLabel {{
                background: #1C1A0E; color: #EAB308;
                border-radius: 35px; font-size: 26px; font-weight: 900;
                font-family: 'Inter'; border: 3px solid {BG_DIALOG};
            }}
        """)
        avatar_row.addWidget(self.prev_avatar)
        vl.addLayout(avatar_row)
        vl.addSpacing(16)
        
        # Category Chip
        chip_row = QHBoxLayout()
        chip_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.prev_chip = QLabel("Sin categoría")
        self.prev_chip.setFixedHeight(30)
        self.prev_chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prev_chip.setStyleSheet(f"background: {BG_INPUT}; color: {TEXT_SEC}; border-radius: 15px; padding: 0 16px; font-size: 12px; font-weight: 700; font-family: 'Inter';")
        chip_row.addWidget(self.prev_chip)
        vl.addLayout(chip_row)
        vl.addSpacing(16)
        
        # Description
        self.prev_desc = QLabel("Descripción del gasto...")
        self.prev_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prev_desc.setWordWrap(True)
        self.prev_desc.setStyleSheet("color: white; font-size: 18px; font-weight: 700; font-family: 'Inter';")
        vl.addWidget(self.prev_desc)
        vl.addSpacing(12)
        
        # Amount
        self.prev_amount = QLabel("$ 0")
        self.prev_amount.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prev_amount.setStyleSheet(f"color: {RED_H}; font-size: 36px; font-weight: 900; font-family: 'Inter'; letter-spacing: -1px;")
        vl.addWidget(self.prev_amount)
        vl.addSpacing(28)
        
        # Divider
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 transparent, stop:0.5 #2A2A2A, stop:1 transparent);")
        vl.addWidget(sep)
        vl.addSpacing(20)
        
        # Detail rows
        self._prev_type_row = self._make_preview_row("Tipo de Gasto")
        self._prev_date_row = self._make_preview_row("Fecha")
        self._prev_subcat_row = self._make_preview_row("Subcategoría")
        self._prev_supplier_row = self._make_preview_row("Proveedor")
        self._prev_invoice_row = self._make_preview_row("Factura")
        self._prev_inv_status_row = self._make_preview_row("Afecta Inventario")
        
        vl.addWidget(self._prev_type_row)
        vl.addWidget(self._prev_date_row)
        vl.addWidget(self._prev_subcat_row)
        vl.addWidget(self._prev_supplier_row)
        vl.addWidget(self._prev_invoice_row)
        vl.addWidget(self._prev_inv_status_row)
        vl.addStretch()
        
        parent_layout.addWidget(self.preview_frame, 2)

    def _make_preview_row(self, label_text):
        row = QFrame()
        row.setStyleSheet("QFrame { border: none; border-bottom: 1px solid rgba(42,42,42,0.4); }")
        hl = QHBoxLayout(row)
        hl.setContentsMargins(0, 12, 0, 12)
        
        lbl_k = QLabel(label_text)
        lbl_k.setStyleSheet(f"color: {TEXT_MUT}; font-size: 13px; font-family: 'Inter';")
        
        lbl_v = QLabel("—")
        lbl_v.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl_v.setStyleSheet("color: #E5E5E5; font-size: 13px; font-weight: 600; font-family: 'Inter';")
        lbl_v.setObjectName("val")
        
        hl.addWidget(lbl_k)
        hl.addStretch()
        hl.addWidget(lbl_v)
        return row

    def _set_preview_detail(self, row_frame, value, color=None):
        lbl = row_frame.findChild(QLabel, "val")
        if lbl:
            lbl.setText(str(value))
            if color:
                lbl.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: 700; font-family: 'Inter';")
            else:
                lbl.setStyleSheet("color: #E5E5E5; font-size: 13px; font-weight: 600; font-family: 'Inter';")

    def _update_preview(self):
        desc = self.description.text().strip()
        self.prev_desc.setText(desc if desc else "Descripción del gasto...")
        
        amt_text = self.amount.text().strip()
        try:
            amt = float(amt_text)
            self.prev_amount.setText(f"- $ {amt:,.0f}".replace(",", "."))
        except ValueError:
            self.prev_amount.setText("$ 0")
            
        cat = self.cb_category.currentText()
        if not cat or cat == "Seleccionar...":
            self.prev_chip.setText("Sin categoría")
            self.prev_chip.setStyleSheet(f"background: {BG_INPUT}; color: {TEXT_SEC}; border-radius: 15px; padding: 0 16px; font-size: 12px; font-weight: 700;")
            self.prev_avatar.setText("?")
            self.prev_avatar.setStyleSheet(f"background: #1C1A0E; color: #EAB308; border-radius: 35px; font-size: 26px; font-weight: 900; border: 3px solid {BG_DIALOG};")
        else:
            self.prev_chip.setText(cat)
            self.prev_chip.setStyleSheet(f"background: rgba(200,16,46,0.15); color: {RED_H}; border-radius: 15px; padding: 0 16px; font-size: 12px; font-weight: 700;")
            self.prev_avatar.setText(cat[:1].upper())
            self.prev_avatar.setStyleSheet(f"background: rgba(200,16,46,0.15); color: {RED_H}; border-radius: 35px; font-size: 26px; font-weight: 900; border: 3px solid {BG_DIALOG};")
            
        exp_type = self.cb_expense_type.currentData()
        type_label = "Fijo" if exp_type == "fixed" else "Variable"
        type_color = RED if exp_type == "fixed" else BLUE
        self._set_preview_detail(self._prev_type_row, type_label, type_color)

        self._set_preview_detail(self._prev_date_row, self.expense_date.date().toString("dd/MM/yyyy"))
        
        sub = self.cb_subcategory.currentText()
        self._set_preview_detail(self._prev_subcat_row, sub if sub != "Seleccionar..." else "—")
        
        sup = self.supplier_name.text().strip()
        self._set_preview_detail(self._prev_supplier_row, sup if sup else "—")
        
        inv = self.invoice_number.text().strip()
        self._set_preview_detail(self._prev_invoice_row, inv if inv else "—")
        
        if self.affects_inventory.isChecked():
            self._set_preview_detail(self._prev_inv_status_row, "Sí", GREEN)
        else:
            self._set_preview_detail(self._prev_inv_status_row, "No", TEXT_MUT)

    def _create_label(self, text, style):
        lbl = QLabel(text)
        lbl.setStyleSheet(style)
        return lbl

    def _on_type_changed(self, idx):
        expense_type = self.cb_expense_type.currentData()
        self._load_categories(expense_type=expense_type)
        self._update_preview()

    def _load_categories(self, expense_type=None):
        self.cb_category.clear()
        try:
            cats = self.repo.get_categories(expense_type=expense_type)
            if not cats:
                return
            self.cb_category.addItem("Seleccionar...", None)
            for c in cats:
                self.cb_category.addItem(c["name"], c["id"])
        except Exception as e:
            QMessageBox.critical(self, tr("common.error"), str(e))

    def _on_category_changed(self, idx):
        self.cb_subcategory.clear()
        cat_id = self.cb_category.currentData()
        if cat_id is None:
            return
        try:
            subs = self.repo.get_subcategories(cat_id)
            self.cb_subcategory.addItem("Seleccionar...", None)
            for s in subs:
                self.cb_subcategory.addItem(s["name"], s["id"])
        except Exception as e:
            QMessageBox.critical(self, tr("common.error"), str(e))

    def _on_inventory_toggle(self, state):
        checked = state == Qt.CheckState.Checked.value
        self.inventory_frame.setVisible(True)
        
        anim = QPropertyAnimation(self.inventory_frame, b"maximumHeight", self)
        anim.setDuration(350)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        opacity_effect = QGraphicsOpacityEffect(self.inventory_frame)
        self.inventory_frame.setGraphicsEffect(opacity_effect)
        fade_anim = QPropertyAnimation(opacity_effect, b"opacity", self)
        fade_anim.setDuration(300)
        fade_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        if checked:
            anim.setStartValue(0)
            anim.setEndValue(350)
            fade_anim.setStartValue(0.0)
            fade_anim.setEndValue(1.0)
        else:
            anim.setStartValue(self.inventory_frame.height())
            anim.setEndValue(0)
            fade_anim.setStartValue(1.0)
            fade_anim.setEndValue(0.0)
            anim.finished.connect(lambda: self.inventory_frame.setVisible(False))
            
        group = QParallelAnimationGroup(self)
        group.addAnimation(anim)
        group.addAnimation(fade_anim)
        group.start()

    def _add_inventory_product(self):
        from views.finances.expenses.inventory_product_selector import InventoryProductSelector
        dlg = InventoryProductSelector(self.inventory_repo, parent=self)
        if dlg.exec():
            product = dlg.selected_product
            qty = dlg.quantity
            unit_cost = dlg.unit_cost
            total = qty * unit_cost
            self._inventory_items.append({
                "product": product,
                "quantity": qty,
                "unit_cost": unit_cost,
                "total_cost": total,
            })
            self._refresh_inv_table()

    def _refresh_inv_table(self):
        self.inv_table.setRowCount(0)
        self.inv_table.setRowCount(len(self._inventory_items))
        for i, item in enumerate(self._inv_items()):
            self.inv_table.setItem(i, 0, QTableWidgetItem(item["product"]["name"]))
            self.inv_table.setItem(i, 1, QTableWidgetItem(str(item["quantity"])))
            self.inv_table.setItem(i, 2, QTableWidgetItem(f"${item['unit_cost']:,.0f}"))
            self.inv_table.setItem(i, 3, QTableWidgetItem(f"${item['total_cost']:,.0f}"))

    def _inv_items(self):
        return self._inventory_items

    def _shake_animation(self):
        anim = QPropertyAnimation(self, b"pos", self)
        anim.setDuration(300)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        original_pos = self.pos()
        anim.setKeyValues([
            (0.0, original_pos), (0.25, original_pos + QPoint(8, 0)),
            (0.5, original_pos + QPoint(-8, 0)), (0.75, original_pos + QPoint(4, 0)),
            (1.0, original_pos)
        ])
        anim.start()

    def _validate(self):
        amt_text = self.amount.text().strip()
        if not amt_text:
            self.lbl_error.setText(tr("finances.expenses.err_amount_required"))
            self.lbl_error.show()
            self._shake_animation()
            return False
        try:
            val = float(amt_text)
            if val <= 0:
                raise ValueError
        except ValueError:
            self.lbl_error.setText(tr("finances.expenses.err_amount_positive"))
            self.lbl_error.show()
            self._shake_animation()
            return False
        if self.cb_category.currentData() is None:
            self.lbl_error.setText(tr("finances.expenses.err_category_required"))
            self.lbl_error.show()
            self._shake_animation()
            return False
        self.lbl_error.hide()
        return True

    def _save(self):
        if not self._validate():
            return

        data = {
            "expense_date": self.expense_date.date().toString("yyyy-MM-dd"),
            "category_id": self.cb_category.currentData(),
            "subcategory_id": self.cb_subcategory.currentData(),
            "description": self.description.text().strip(),
            "amount": float(self.amount.text().strip()),
            "supplier_name": self.supplier_name.text().strip(),
            "invoice_number": self.invoice_number.text().strip(),
            "affects_inventory": self.affects_inventory.isChecked(),
            "inventory_items": self._inventory_items,
            "expense_type": self.cb_expense_type.currentData(),
        }
        try:
            self.repo.create_expense(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, tr("common.error"), str(e))