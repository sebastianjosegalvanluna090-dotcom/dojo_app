from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QComboBox,
    QTreeWidget, QTreeWidgetItem, QStackedWidget,
    QWidget, QMessageBox, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

from core.i18n import tr

# Paleta de colores refinada
BG_DIALOG = "#0D0D0D"
BG_CARD   = "#161616"
BG_INPUT  = "#1C1C1C"
BORDER    = "#2A2A2A"
RED       = "#C8102E"
RED_H     = "#E8152F"
TEXT_PRI  = "#F0F0F0"
TEXT_MUT  = "#6B7280"
TEXT_SEC  = "#9CA3AF"

class ExpenseCategoryDialog(QDialog):
    def __init__(self, repo, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.current_type = "variable"
        
        self.setWindowTitle("Gestión de Categorías")
        self.setMinimumSize(900, 580)
        self.resize(920, 620)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")
        
        # Animación de entrada global
        self.setWindowOpacity(0.0)
        self._anim_opacity = QPropertyAnimation(self, b"windowOpacity", self)
        self._anim_opacity.setDuration(350)
        self._anim_opacity.setStartValue(0.0)
        self._anim_opacity.setEndValue(1.0)
        self._anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._build_ui()
        self._load_tree()
        
        QTimer.singleShot(50, self._anim_opacity.start)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(24)

        # Header Premium
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        title = QLabel("Categorías de Egresos")
        title.setStyleSheet("color: white; font-size: 26px; font-weight: 900; font-family: 'Inter'; letter-spacing: -0.5px;")
        
        subtitle = QLabel("Organiza y administra los tipos de gastos del dojo")
        subtitle.setStyleSheet(f"color: {TEXT_MUT}; font-size: 13px; font-weight: 500; font-family: 'Inter';")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        root.addLayout(header_layout)

        # Main Content Split
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)

        # --- Lado Izquierdo: Lista (Tree) ---
        left_panel = QFrame()
        left_panel.setMaximumWidth(340)
        left_panel.setStyleSheet(f"QFrame {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 16px; }}")

        shadow_left = QGraphicsDropShadowEffect(left_panel)
        shadow_left.setBlurRadius(40)
        shadow_left.setOffset(0, 12)
        shadow_left.setColor(QColor(0, 0, 0, 200))
        left_panel.setGraphicsEffect(shadow_left)

        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(18, 18, 18, 20)
        left_layout.setSpacing(14)

        # Filtros Tipo (Segmented Control Style)
        seg_container = QFrame()
        seg_container.setFixedHeight(46)
        seg_container.setStyleSheet(f"""
            QFrame {{
                background: {BG_DIALOG};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)
        seg_layout = QHBoxLayout(seg_container)
        seg_layout.setContentsMargins(5, 5, 5, 5)
        seg_layout.setSpacing(4)

        self.btn_filter_fixed = QPushButton("Fijos")
        self.btn_filter_variable = QPushButton("Variables")

        for btn in [self.btn_filter_fixed, self.btn_filter_variable]:
            btn.setFixedHeight(34)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{ background: transparent; color: {TEXT_MUT}; border: none; border-radius: 8px; font-size: 13px; font-weight: 700; font-family: 'Inter'; }}
                QPushButton:hover {{ color: white; }}
            """)
            seg_layout.addWidget(btn)

        self._update_filter_styles()
        self.btn_filter_fixed.clicked.connect(lambda: self._change_type("fixed"))
        self.btn_filter_variable.clicked.connect(lambda: self._change_type("variable"))

        left_layout.addWidget(seg_container)

        # Tree Widget Premium
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(16)
        self.tree.setStyleSheet(f"""
            QTreeWidget {{ background-color: transparent; border: none; color: {TEXT_PRI}; font-family: 'Inter'; outline: 0; }}
            QTreeWidget::item {{ padding: 12px 8px; border-bottom: 1px solid {BG_DIALOG}; }}
            QTreeWidget::item:hover {{ background-color: {BG_INPUT}; }}
            QTreeWidget::item:selected {{ background-color: rgba(200, 16, 46, 0.08); color: white; border-left: 3px solid {RED}; }}
            QTreeWidget::branch {{ background: transparent; }}
            QTreeWidget::branch:has-siblings:!adjoins-item {{ background: transparent; }}
            QTreeWidget::branch:has-siblings:adjoins-item {{ background: transparent; }}
            QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {{ background: transparent; }}
            QTreeWidget::branch:closed:has-children:has-siblings {{ background: transparent; }}
            QTreeWidget::branch:open:has-children:has-siblings {{ background: transparent; }}
        """)
        self.tree.itemClicked.connect(self._on_tree_item_clicked)
        left_layout.addWidget(self.tree)

        # Separador antes de los botones
        list_btn_layout = QHBoxLayout()
        list_btn_layout.setSpacing(8)

        self.btn_new_cat = QPushButton("＋ Nueva Categoría")
        self.btn_new_sub = QPushButton("＋ Subcategoría")

        for btn in [self.btn_new_cat, self.btn_new_sub]:
            btn.setFixedHeight(38)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{ background: transparent; color: {TEXT_SEC}; border: 1px solid {BORDER}; border-radius: 10px; font-size: 12px; font-weight: 700; font-family: 'Inter'; }}
                QPushButton:hover {{ border-color: {RED}; color: {RED_H}; background: {BG_INPUT}; }}
            """)
            list_btn_layout.addWidget(btn)

        self.btn_new_cat.clicked.connect(self._show_new_category_form)
        self.btn_new_sub.clicked.connect(self._show_new_subcategory_form)

        left_layout.addLayout(list_btn_layout)
        content_layout.addWidget(left_panel, 1)

        # --- Lado Derecho: Formulario Dinámico ---
        right_panel = QFrame()
        right_panel.setStyleSheet(f"QFrame {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 16px; }}")

        shadow_right = QGraphicsDropShadowEffect(right_panel)
        shadow_right.setBlurRadius(40)
        shadow_right.setOffset(0, 12)
        shadow_right.setColor(QColor(0, 0, 0, 200))
        right_panel.setGraphicsEffect(shadow_right)

        self.form_layout = QVBoxLayout(right_panel)
        self.form_layout.setContentsMargins(28, 24, 28, 24)
        self.form_layout.setSpacing(16)

        self.lbl_form_title = QLabel("Nueva Categoría")
        self.lbl_form_title.setStyleSheet(
            f"color: {TEXT_PRI}; font-size: 17px; font-weight: 700; "
            f"font-family: 'Inter'; padding-bottom: 4px;"
        )
        self.form_layout.addWidget(self.lbl_form_title)

        # Stack para cambiar entre formularios con animación
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("QStackedWidget { border: none; background: transparent; }")

        # Form 1: Vacío
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_lbl = QLabel("No hay nada seleccionado\nElige o crea una categoría para empezar")
        empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 14px; font-family: 'Inter';")
        empty_layout.addWidget(empty_lbl)
        self.stack.addWidget(empty_widget)

        # Form 2 y 3
        self.cat_form_widget = self._build_category_form()
        self.stack.addWidget(self.cat_form_widget)
        self.sub_form_widget = self._build_subcategory_form()
        self.stack.addWidget(self.sub_form_widget)

        self.form_layout.addWidget(self.stack, 1)

        # Separador visual antes de los botones
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f" stop:0 transparent, stop:0.3 {BORDER},"
            f" stop:0.7 {BORDER}, stop:1 transparent); border: none;"
        )
        self.form_layout.addWidget(sep)

        self.form_layout.addSpacing(4)

        # Botones de Acción
        action_layout = QHBoxLayout()
        action_layout.setSpacing(12)
        action_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_delete = QPushButton("Eliminar")
        self.btn_delete.setFixedHeight(44)
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: #FF4444; border: 1px solid #3A1A1A; border-radius: 11px; font-size: 13px; font-weight: 700; font-family: 'Inter'; padding: 0 22px; }}
            QPushButton:hover {{ background: rgba(255, 68, 68, 0.1); border-color: #FF4444; }}
        """)
        self.btn_delete.clicked.connect(self._delete_selected)
        self.btn_delete.hide()

        self.btn_save = QPushButton("Guardar Cambios")
        self.btn_save.setFixedHeight(44)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{ background: {RED}; color: white; border: none; border-radius: 11px; font-size: 13px; font-weight: 800; font-family: 'Inter'; padding: 0 32px; }}
            QPushButton:hover {{ background: {RED_H}; }}
            QPushButton:pressed {{ background: #A60D24; }}
        """)
        shadow_save = QGraphicsDropShadowEffect(self.btn_save)
        shadow_save.setBlurRadius(20)
        shadow_save.setOffset(0, 6)
        shadow_save.setColor(QColor(200, 16, 46, 150))
        self.btn_save.setGraphicsEffect(shadow_save)
        self.btn_save.clicked.connect(self._save_current_form)

        action_layout.addStretch()
        action_layout.addWidget(self.btn_delete)
        action_layout.addWidget(self.btn_save)

        self.form_layout.addLayout(action_layout)

        content_layout.addWidget(right_panel, 2)
        root.addLayout(content_layout)

    def _animate_stack_transition(self, index):
        """Fade suave al cambiar de formulario — sin animación de posición."""
        if self.stack.currentIndex() == index:
            return

        self.stack.setCurrentIndex(index)
        next_widget = self.stack.currentWidget()

        effect = QGraphicsOpacityEffect(next_widget)
        next_widget.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(220)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(lambda: next_widget.setGraphicsEffect(None))
        anim.start()

    def _build_category_form(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)  # spacing reducido entre label e input; stretch separa grupos

        label_style = f"color: {TEXT_SEC}; font-size: 10px; font-weight: 700; font-family: 'Inter'; letter-spacing: 1px; padding-left: 2px; padding-bottom: 4px;"
        input_style = f"""
            QLineEdit, QComboBox {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 10px;
                padding: 0 16px; font-size: 13px;
                min-height: 42px; max-height: 42px;
                font-family: 'Inter';
            }}
            QLineEdit:hover, QComboBox:hover {{ border-color: #3F3F3F; }}
            QLineEdit:focus, QComboBox:focus {{ border-color: {RED}; background: #1F1010; }}
            QComboBox::drop-down {{ border: none; width: 30px; }}
            QComboBox QAbstractItemView {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                selection-background-color: {RED};
                border-radius: 8px; border: 1px solid {BORDER}; padding: 4px;
            }}
        """

        lbl_type = QLabel("TIPO DE GASTO")
        lbl_type.setStyleSheet(label_style)
        layout.addWidget(lbl_type)
        self.cb_cat_type = QComboBox()
        self.cb_cat_type.addItem("Gasto Fijo", "fixed")
        self.cb_cat_type.addItem("Gasto Variable", "variable")
        self.cb_cat_type.setStyleSheet(input_style)
        layout.addWidget(self.cb_cat_type)

        layout.addSpacing(18)

        lbl_name = QLabel("NOMBRE DE LA CATEGORÍA")
        lbl_name.setStyleSheet(label_style)
        layout.addWidget(lbl_name)
        self.input_cat_name = QLineEdit()
        self.input_cat_name.setPlaceholderText("Ej: Alquiler, Sueldos, Equipos...")
        self.input_cat_name.setStyleSheet(input_style)
        layout.addWidget(self.input_cat_name)

        layout.addSpacing(18)

        lbl_desc = QLabel("DESCRIPCIÓN")
        lbl_desc.setStyleSheet(label_style)
        layout.addWidget(lbl_desc)
        self.input_cat_desc = QLineEdit()
        self.input_cat_desc.setPlaceholderText("Breve detalle (Opcional)")
        self.input_cat_desc.setStyleSheet(input_style)
        layout.addWidget(self.input_cat_desc)

        layout.addStretch()
        return widget

    def _build_subcategory_form(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        label_style = f"color: {TEXT_SEC}; font-size: 10px; font-weight: 700; font-family: 'Inter'; letter-spacing: 1px; padding-left: 2px; padding-bottom: 4px;"
        input_style = f"""
            QLineEdit {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 10px;
                padding: 0 16px; font-size: 13px;
                min-height: 42px; max-height: 42px;
                font-family: 'Inter';
            }}
            QLineEdit:hover {{ border-color: #3F3F3F; }}
            QLineEdit:focus {{ border-color: {RED}; background: #1F1010; }}
        """

        lbl_parent = QLabel("CATEGORÍA PADRE")
        lbl_parent.setStyleSheet(label_style)
        layout.addWidget(lbl_parent)

        self.lbl_sub_parent = QLabel("—")
        self.lbl_sub_parent.setStyleSheet(f"""
            QLabel {{
                background: rgba(200, 16, 46, 0.08); color: {RED_H};
                border: 1px solid rgba(200, 16, 46, 0.2); border-radius: 10px;
                padding: 12px 16px; font-size: 14px; font-weight: 700;
                font-family: 'Inter';
            }}
        """)
        layout.addWidget(self.lbl_sub_parent)

        layout.addSpacing(18)

        lbl_name = QLabel("NOMBRE DE LA SUBCATEGORÍA")
        lbl_name.setStyleSheet(label_style)
        layout.addWidget(lbl_name)
        self.input_sub_name = QLineEdit()
        self.input_sub_name.setPlaceholderText("Ej: Luz, Agua, Cinturones...")
        self.input_sub_name.setStyleSheet(input_style)
        layout.addWidget(self.input_sub_name)

        layout.addSpacing(18)

        lbl_desc = QLabel("DESCRIPCIÓN")
        lbl_desc.setStyleSheet(label_style)
        layout.addWidget(lbl_desc)
        self.input_sub_desc = QLineEdit()
        self.input_sub_desc.setPlaceholderText("Breve detalle (Opcional)")
        self.input_sub_desc.setStyleSheet(input_style)
        layout.addWidget(self.input_sub_desc)

        layout.addStretch()
        return widget

    def _update_filter_styles(self):
        active_style = (
            f"QPushButton {{ background: {BG_CARD}; color: {TEXT_PRI}; "
            f"border: 1px solid {BORDER}; border-radius: 8px; "
            f"font-size: 13px; font-weight: 800; font-family: 'Inter'; }}"
        )
        inactive_style = (
            f"QPushButton {{ background: transparent; color: {TEXT_MUT}; "
            f"border: none; border-radius: 8px; "
            f"font-size: 13px; font-weight: 600; font-family: 'Inter'; }} "
            f"QPushButton:hover {{ color: {TEXT_SEC}; }}"
        )
        
        if self.current_type == "fixed":
            self.btn_filter_fixed.setStyleSheet(active_style)
            self.btn_filter_variable.setStyleSheet(inactive_style)
        else:
            self.btn_filter_variable.setStyleSheet(active_style)
            self.btn_filter_fixed.setStyleSheet(inactive_style)

    def _change_type(self, type_name):
        self.current_type = type_name
        self._update_filter_styles()
        self._load_tree()
        self._animate_stack_transition(0)
        self.btn_delete.hide()

    def _load_tree(self):
        self.tree.clear()
        cats = self.repo.get_categories(expense_type=self.current_type)
        
        color_hex = "#C8102E" if self.current_type == "fixed" else "#3B82F6"
        
        for c in cats:
            cat_item = QTreeWidgetItem([c['name']])
            cat_item.setForeground(0, QColor(color_hex))
            font = cat_item.font(0)
            font.setBold(True)
            font.setPointSize(12)
            cat_item.setFont(0, font)
            cat_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "category", "data": c})
            
            subs = self.repo.get_subcategories(c["id"])
            for s in subs:
                sub_item = QTreeWidgetItem([s['name']])
                sub_item.setForeground(0, QColor(TEXT_SEC))
                font_sub = sub_item.font(0)
                font_sub.setPointSize(11)
                sub_item.setFont(0, font_sub)
                cat_item.addChild(sub_item)
                sub_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "subcategory", "data": s, "parent": c})
                
            self.tree.addTopLevelItem(cat_item)
        self.tree.expandAll()

    def _on_tree_item_clicked(self, item, column):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
            
        self.btn_delete.show()
        
        if data["type"] == "category":
            cat = data["data"]
            self.lbl_form_title.setText("Editar Categoría")
            self.input_cat_name.setText(cat.get("name", ""))
            self.input_cat_desc.setText(cat.get("description", ""))
            
            idx = self.cb_cat_type.findData(cat.get("expense_type", "variable"))
            if idx >= 0:
                self.cb_cat_type.setCurrentIndex(idx)
            self._animate_stack_transition(1)
                
        elif data["type"] == "subcategory":
            sub = data["data"]
            parent = data["parent"]
            self.lbl_form_title.setText("Editar Subcategoría")
            self.lbl_sub_parent.setText(parent["name"])
            self.input_sub_name.setText(sub.get("name", ""))
            self.input_sub_desc.setText(sub.get("description", ""))
            self._animate_stack_transition(2)

    def _show_new_category_form(self):
        self.tree.clearSelection()
        self.lbl_form_title.setText("Nueva Categoría")
        self.input_cat_name.clear()
        self.input_cat_desc.clear()
        
        idx = self.cb_cat_type.findData(self.current_type)
        if idx >= 0:
            self.cb_cat_type.setCurrentIndex(idx)
            
        self.btn_delete.hide()
        self._animate_stack_transition(1)

    def _show_new_subcategory_form(self):
        selected = self.tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "Atención", "Selecciona una categoría padre primero.")
            return
            
        data = selected.data(0, Qt.ItemDataRole.UserRole)
        if not data or data["type"] != "category":
            QMessageBox.warning(self, "Atención", "Selecciona una categoría padre primero.")
            return
            
        self.lbl_form_title.setText("Nueva Subcategoría")
        self.lbl_sub_parent.setText(data["data"]["name"])
        self.input_sub_name.clear()
        self.input_sub_desc.clear()
        self.btn_delete.hide()
        self._animate_stack_transition(2)

    def _save_current_form(self):
        if self.stack.currentIndex() == 1:
            name = self.input_cat_name.text().strip()
            desc = self.input_cat_desc.text().strip()
            exp_type = self.cb_cat_type.currentData()
            
            if not name:
                QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
                return
                
            selected = self.tree.currentItem()
            if selected:
                data = selected.data(0, Qt.ItemDataRole.UserRole)
                if data and data["type"] == "category":
                    self.repo.update_category(data["data"]["id"], name, desc, exp_type)
                else:
                    self.repo.create_category(name, desc, exp_type)
            else:
                self.repo.create_category(name, desc, exp_type)
                
        elif self.stack.currentIndex() == 2:
            name = self.input_sub_name.text().strip()
            desc = self.input_sub_desc.text().strip()
            
            if not name:
                QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
                return
                
            selected = self.tree.currentItem()
            if selected:
                data = selected.data(0, Qt.ItemDataRole.UserRole)
                if data["type"] == "category":
                    parent_id = data["data"]["id"]
                elif data["type"] == "subcategory":
                    parent_id = data["parent"]["id"]
            else:
                return QMessageBox.warning(self, "Error", "No se pudo determinar la categoría padre.")
            
            if selected and selected.parent() and self.lbl_form_title.text() == "Editar Subcategoría":
                data = selected.data(0, Qt.ItemDataRole.UserRole)
                self.repo.update_subcategory(data["data"]["id"], name, desc)
            else:
                self.repo.create_subcategory(parent_id, name, desc)
                
        self._load_tree()
        self._animate_stack_transition(0)
        self.btn_delete.hide()
        QMessageBox.information(self, "Éxito", "Cambios guardados correctamente.")

    def _delete_selected(self):
        selected = self.tree.currentItem()
        if not selected:
            return
            
        data = selected.data(0, Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, "Confirmar", f"¿Seguro que deseas eliminar '{selected.text(0).strip()}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if data["type"] == "category":
                self.repo.delete_category(data["data"]["id"])
            else:
                self.repo.delete_subcategory(data["data"]["id"])
                
            self._load_tree()
            self._animate_stack_transition(0)
            self.btn_delete.hide()