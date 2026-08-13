from PyQt6.QtWidgets import (
    QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox,
    QRadioButton, QPushButton, QScrollArea, QWidget,
    QCheckBox, QFileDialog,
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor

from core.i18n import tr, trf

BG_DIALOG = "#111111"
BG_INPUT  = "#1C1C1C"
BG_CARD   = "#161616"
BORDER    = "#2A2A2A"
RED       = "#C8102E"
RED_H     = "#E8152F"
TEXT_PRI  = "#F0F0F0"
TEXT_SEC  = "#888888"
TEXT_MUT  = "#666666"
GREEN     = "#22C55E"


def format_money(value):
    return f"${value:,.0f}".replace(",", ".")


class MembershipPlanDialog(QDialog):
    def __init__(self, repo, plan=None, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.plan = plan
        self.setWindowTitle(tr("management.memberships.create_plan") if plan is None else tr("management.memberships.edit_plan"))
        self.setMinimumSize(720, 680)
        self.resize(760, 720)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"background-color: {BG_DIALOG}; color: {TEXT_PRI};")
        self._build_ui()
        if plan is not None:
            self._populate(plan)
        self._update_price_preview()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        header = QLabel(tr("management.memberships.plan_section_title"))
        header.setStyleSheet("color: white; font-size: 18px; font-weight: 900;")
        root.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        content = QVBoxLayout(scroll_content)
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(20)

        plan_card = QFrame()
        plan_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        plan_layout = QVBoxLayout(plan_card)
        plan_layout.setContentsMargins(20, 16, 20, 16)
        plan_layout.setSpacing(12)

        plan_layout.addWidget(self._label(tr("management.memberships.plan_name")))
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ej: Plan Básico...")
        self.input_name.setStyleSheet(self._input_style())
        plan_layout.addWidget(self.input_name)

        plan_layout.addWidget(self._label(tr("management.memberships.plan_type")))
        type_row = QHBoxLayout()
        type_row.setSpacing(16)
        self.radio_individual = QRadioButton(tr("management.membership.individual_desc"))
        self.radio_individual.setChecked(True)
        self.radio_group = QRadioButton(tr("management.membership.group_desc"))
        for rb in (self.radio_individual, self.radio_group):
            rb.setStyleSheet(f"""
                QRadioButton {{
                    color: {TEXT_PRI}; font-size: 13px; spacing: 6px;
                }}
                QRadioButton::indicator {{
                    width: 16px; height: 16px;
                    border: 2px solid {BORDER}; border-radius: 8px;
                    background: {BG_INPUT};
                }}
                QRadioButton::indicator:checked {{
                    background: {RED}; border-color: {RED};
                }}
            """)
        self.radio_individual.toggled.connect(self._on_plan_type_changed)
        type_row.addWidget(self.radio_individual)
        type_row.addWidget(self.radio_group)
        type_row.addStretch()
        plan_layout.addLayout(type_row)

        classes_row = QHBoxLayout()
        classes_row.setSpacing(12)

        col_classes = QVBoxLayout()
        col_classes.setSpacing(4)
        col_classes.addWidget(self._label(tr("management.memberships.weekly_classes")))
        self.cmb_classes = QComboBox()
        self.cmb_classes.addItem("1 " + tr("management.membership.classes_per_week"), 1)
        self.cmb_classes.addItem("2 " + tr("management.membership.classes_per_week"), 2)
        self.cmb_classes.addItem("3 " + tr("management.membership.classes_per_week"), 3)
        self.cmb_classes.addItem(tr("management.memberships.group_classes"), -1)
        self.cmb_classes.setStyleSheet(self._combo_style())
        self.cmb_classes.currentIndexChanged.connect(self._update_price_preview)
        col_classes.addWidget(self.cmb_classes)
        classes_row.addLayout(col_classes)

        plan_layout.addLayout(classes_row)

        fee_row = QHBoxLayout()
        fee_row.setSpacing(12)

        col_fee = QVBoxLayout()
        col_fee.setSpacing(4)
        col_fee.addWidget(self._label(tr("management.memberships.monthly_fee")))
        self.monthly_fee_spin = QDoubleSpinBox()
        self.monthly_fee_spin.setRange(0, 99999999)
        self.monthly_fee_spin.setDecimals(2)
        self.monthly_fee_spin.setSingleStep(1000)
        self.monthly_fee_spin.setPrefix("$ ")
        self.monthly_fee_spin.setStyleSheet(self._spin_style())
        self.monthly_fee_spin.valueChanged.connect(self._update_price_preview)
        col_fee.addWidget(self.monthly_fee_spin)
        fee_row.addLayout(col_fee)

        col_discount = QVBoxLayout()
        col_discount.setSpacing(4)
        col_discount.addWidget(self._label(tr("management.memberships.discount_type")))
        self.discount_type_combo = QComboBox()
        self.discount_type_combo.addItem(tr("management.memberships.discount_percent"), "percent")
        self.discount_type_combo.addItem(tr("management.memberships.discount_fixed"), "amount")
        self.discount_type_combo.setStyleSheet(self._combo_style())
        self.discount_type_combo.currentIndexChanged.connect(self._on_discount_type_changed)
        col_discount.addWidget(self.discount_type_combo)
        fee_row.addLayout(col_discount)

        col_discount_val = QVBoxLayout()
        col_discount_val.setSpacing(4)
        col_discount_val.addWidget(self._label(tr("management.memberships.discount")))
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setRange(0, 100)
        self.discount_spin.setSuffix(" %")
        self.discount_spin.setDecimals(0)
        self.discount_spin.setStyleSheet(self._spin_style())
        self.discount_spin.valueChanged.connect(self._update_price_preview)
        col_discount_val.addWidget(self.discount_spin)
        fee_row.addLayout(col_discount_val)

        plan_layout.addLayout(fee_row)

        col_capacity = QVBoxLayout()
        col_capacity.setSpacing(4)
        col_capacity.addWidget(self._label(tr("management.memberships.group_capacity")))
        self.spin_capacity = QSpinBox()
        self.spin_capacity.setRange(1, 99)
        self.spin_capacity.setValue(4)
        self.spin_capacity.setStyleSheet(self._spin_style())
        col_capacity.addWidget(self.spin_capacity)
        self.group_capacity_row = col_capacity
        plan_layout.addLayout(col_capacity)

        prepaid_section = QVBoxLayout()
        prepaid_section.setSpacing(8)
        self.chk_prepaid = QCheckBox(tr("management.memberships.prepaid_checkbox"))
        self.chk_prepaid.setStyleSheet(f"""
            QCheckBox {{
                color: {TEXT_PRI}; font-size: 13px; spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px; height: 18px;
                border: 2px solid {BORDER}; border-radius: 4px;
                background: {BG_INPUT};
            }}
            QCheckBox::indicator:checked {{
                background: {RED}; border-color: {RED};
            }}
        """)
        self.chk_prepaid.toggled.connect(self._on_prepaid_toggled)
        prepaid_section.addWidget(self.chk_prepaid)

        prepaid_months_row = QHBoxLayout()
        prepaid_months_row.setSpacing(8)
        prepaid_months_label = QLabel(tr("management.memberships.prepaid_months"))
        prepaid_months_label.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        prepaid_months_row.addWidget(prepaid_months_label)
        self.spin_prepaid_months = QSpinBox()
        self.spin_prepaid_months.setRange(1, 36)
        self.spin_prepaid_months.setValue(3)
        self.spin_prepaid_months.setStyleSheet(self._spin_style())
        self.spin_prepaid_months.setEnabled(False)
        prepaid_months_row.addWidget(self.spin_prepaid_months)
        prepaid_months_row.addStretch()
        self.prepaid_months_container = QWidget()
        self.prepaid_months_container.setLayout(prepaid_months_row)
        self.prepaid_months_container.setVisible(False)
        prepaid_section.addWidget(self.prepaid_months_container)

        plan_layout.addLayout(prepaid_section)
        self.prepaid_section_widget = prepaid_section

        plan_layout.addWidget(self._label(tr("management.memberships.description")))
        self.input_description = QLineEdit()
        self.input_description.setPlaceholderText(tr("management.memberships.description_placeholder"))
        self.input_description.setStyleSheet(self._input_style())
        plan_layout.addWidget(self.input_description)

        content.addWidget(plan_card)

        benefits_header = QLabel(tr("management.memberships.benefits_section_title"))
        benefits_header.setStyleSheet("color: white; font-size: 16px; font-weight: 800;")
        content.addWidget(benefits_header)

        benefits_card = QFrame()
        benefits_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        benefits_layout = QVBoxLayout(benefits_card)
        benefits_layout.setContentsMargins(20, 16, 20, 16)
        benefits_layout.setSpacing(8)

        self.benefit_inputs = []
        for i in range(1, 11):
            lbl = QLabel(tr(f"management.memberships.benefit_{i}"))
            lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 600; border: none; background: transparent;")
            entry = QLineEdit()
            entry.setStyleSheet(self._input_style())
            entry.setPlaceholderText("")
            self.benefit_inputs.append(entry)
            benefits_layout.addWidget(lbl)
            benefits_layout.addWidget(entry)

        content.addWidget(benefits_card)

        price_header = QLabel(tr("management.memberships.price_section_title"))
        price_header.setStyleSheet("color: white; font-size: 16px; font-weight: 800;")
        content.addWidget(price_header)

        price_card = QFrame()
        price_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
            QFrame QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(price_card)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 150))
        price_card.setGraphicsEffect(shadow)

        price_layout = QVBoxLayout(price_card)
        price_layout.setContentsMargins(20, 16, 20, 16)
        price_layout.setSpacing(8)

        def info_row(label_text):
            row = QHBoxLayout()
            row.setSpacing(8)
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px; font-weight: 700;")
            val = QLabel("")
            val.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 900;")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            frame = QFrame()
            frame.setLayout(row)
            frame.setStyleSheet("background: transparent; border: none;")
            return frame, val

        normal_frame, self.lbl_preview_normal = info_row(tr("management.memberships.normal_value"))
        price_layout.addWidget(normal_frame)

        discount_frame, self.lbl_preview_discount = info_row(tr("management.memberships.discount"))
        self.lbl_preview_discount.setStyleSheet(f"color: {GREEN}; font-size: 13px; font-weight: 800;")
        price_layout.addWidget(discount_frame)

        self.prepaid_preview_frame, self.lbl_preview_prepaid = info_row(tr("management.memberships.prepaid_months_count"))
        self.lbl_preview_prepaid.setStyleSheet(f"color: #7E22CE; font-size: 13px; font-weight: 800;")
        price_layout.addWidget(self.prepaid_preview_frame)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {BORDER}; border: none;")
        price_layout.addWidget(sep)

        final_frame, self.lbl_preview_final = info_row(tr("management.memberships.discounted_value"))
        self.lbl_preview_final.setStyleSheet(f"color: white; font-size: 22px; font-weight: 900;")
        price_layout.addWidget(final_frame)

        content.addWidget(price_card)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #FF4444; font-size: 11px;")
        self.lbl_error.hide()
        content.addWidget(self.lbl_error)

        content.addStretch()
        scroll.setWidget(scroll_content)
        root.addWidget(scroll)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton(tr("cancel"))
        btn_cancel.setFixedHeight(38)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUT};
                border: 1px solid {BORDER}; border-radius: 7px; font-size: 13px;
            }}
            QPushButton:hover {{ color: {TEXT_PRI}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton(tr("save"))
        self.btn_save.setFixedHeight(38)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background: {RED}; color: white;
                border: none; border-radius: 7px; font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background: {RED_H}; }}
        """)
        self.btn_save.clicked.connect(self._save)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self.btn_save)
        root.addLayout(btn_row)

        self._on_plan_type_changed()

    def _on_plan_type_changed(self):
        is_group = self.radio_group.isChecked()
        self.spin_capacity.setVisible(is_group)
        for i in range(self.group_capacity_row.count()):
            w = self.group_capacity_row.itemAt(i)
            if w and w.widget():
                w.widget().setVisible(is_group)
        if is_group:
            self.cmb_classes.setCurrentIndex(3)
            self.cmb_classes.setEnabled(False)
        else:
            self.cmb_classes.setEnabled(True)
        is_individual = self.radio_individual.isChecked()
        for i in range(self.prepaid_section_widget.count()):
            w = self.prepaid_section_widget.itemAt(i)
            if w and w.widget():
                w.widget().setVisible(is_individual)
        if not is_individual:
            self.chk_prepaid.setChecked(False)
        self._update_price_preview()

    def _on_prepaid_toggled(self, checked):
        self.spin_prepaid_months.setEnabled(checked)
        self.prepaid_months_container.setVisible(checked)
        if not checked:
            self.spin_prepaid_months.setValue(3)
        self._update_price_preview()

    def _on_discount_type_changed(self):
        discount_type = self.discount_type_combo.currentData()
        old_value = self.discount_spin.value()
        if discount_type == "percent":
            self.discount_spin.setRange(0, 100)
            self.discount_spin.setPrefix("")
            self.discount_spin.setSuffix(" %")
            self.discount_spin.setDecimals(0)
            self.discount_spin.setSingleStep(1)
            if old_value > 100:
                self.discount_spin.setValue(0)
        else:
            self.discount_spin.setRange(0, 99999999)
            self.discount_spin.setPrefix("$ ")
            self.discount_spin.setSuffix("")
            self.discount_spin.setDecimals(0)
            self.discount_spin.setSingleStep(1000)
        self._update_price_preview()

    def _calculate_discount(self, base_price, discount, discount_type):
        if discount_type == "amount":
            discount_amount = discount
        else:
            discount_amount = base_price * (discount / 100)
        discount_amount = max(0, min(discount_amount, base_price))
        final_price = max(0, base_price - discount_amount)
        return discount_amount, final_price

    def _update_price_preview(self):
        fee = self.monthly_fee_spin.value()
        discount = self.discount_spin.value()
        discount_type = self.discount_type_combo.currentData()
        is_individual = self.radio_individual.isChecked()
        is_prepaid = self.chk_prepaid.isChecked() if is_individual else False
        prepaid_months = self.spin_prepaid_months.value() if is_prepaid else 1
        if fee > 0:
            discount_amount, final_price = self._calculate_discount(fee, discount, discount_type)
            self.lbl_preview_normal.setText(f"{format_money(fee)}")
            if discount > 0:
                if discount_type == "percent":
                    discount_text = f"{discount:.0f}%"
                else:
                    discount_text = format_money(discount_amount)
                self.lbl_preview_discount.setText(f"-{discount_text}")
                self.lbl_preview_discount.show()
            else:
                self.lbl_preview_discount.hide()
            if is_prepaid and is_individual:
                self.lbl_preview_prepaid.setText(
                    trf("management.memberships.prepaid_months_value", "{months} meses", months=prepaid_months)
                )
                self.prepaid_preview_frame.show()
            else:
                self.prepaid_preview_frame.hide()
            self.lbl_preview_final.setText(format_money(final_price))
            self.lbl_preview_final.show()
        else:
            self.lbl_preview_normal.setText("")
            self.lbl_preview_discount.hide()
            self.prepaid_preview_frame.hide()
            self.lbl_preview_final.hide()

    def _label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        return lbl

    def _input_style(self):
        return f"""
            QLineEdit {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 8px;
                padding: 0 12px; font-size: 13px; min-height: 36px;
            }}
            QLineEdit:focus {{ border-color: {RED}; }}
        """

    def _combo_style(self):
        return f"""
            QComboBox {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 8px;
                padding: 0 12px; font-size: 13px; min-height: 36px;
            }}
            QComboBox::drop-down {{ border: none; width: 30px; }}
            QComboBox QAbstractItemView {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                selection-background-color: {RED};
            }}
        """

    def _spin_style(self):
        return f"""
            QSpinBox, QDoubleSpinBox {{
                background: {BG_INPUT}; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 8px;
                padding: 0 12px; font-size: 13px; min-height: 36px;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{ border-color: {RED}; }}
        """

    def _populate(self, plan):
        self.input_name.setText(plan["name"])
        pt = plan.get("plan_type", "individual")
        if pt == "group":
            self.radio_group.setChecked(True)
        else:
            self.radio_individual.setChecked(True)
        self.monthly_fee_spin.setValue(plan.get("monthly_fee", 0.0))
        self.discount_spin.setValue(plan.get("discount", 0.0))
        discount_type = plan.get("discount_type", "percent")
        idx = self.discount_type_combo.findData(discount_type)
        if idx >= 0:
            self.discount_type_combo.setCurrentIndex(idx)
        is_unlimited = plan.get("is_unlimited", False)
        wc = plan.get("weekly_classes", 0)
        if is_unlimited or wc is None or wc == 0:
            self.cmb_classes.setCurrentIndex(3)
        elif wc == 1:
            self.cmb_classes.setCurrentIndex(0)
        elif wc == 2:
            self.cmb_classes.setCurrentIndex(1)
        elif wc == 3:
            self.cmb_classes.setCurrentIndex(2)
        self.input_description.setText(plan.get("description", ""))
        cap = plan.get("group_capacity", 4)
        self.spin_capacity.setValue(cap if cap > 0 else 4)
        is_prepaid = plan.get("is_prepaid_months", False)
        self.chk_prepaid.setChecked(is_prepaid)
        prepaid_count = plan.get("prepaid_months_count", 1)
        if prepaid_count < 2:
            prepaid_count = 3
        self.spin_prepaid_months.setValue(prepaid_count)
        benefits_text = plan.get("benefits", "")
        lines = benefits_text.splitlines()
        for i in range(10):
            if i < len(lines) and lines[i].strip():
                self.benefit_inputs[i].setText(lines[i].strip())

    def _validate(self):
        if not self.input_name.text().strip():
            self.lbl_error.setText(tr("management.memberships.err_name_required"))
            self.lbl_error.show()
            return False
        if self.monthly_fee_spin.value() < 0:
            self.lbl_error.setText(tr("management.memberships.err_fee_negative"))
            self.lbl_error.show()
            return False
        if self.discount_spin.value() < 0:
            self.lbl_error.setText(tr("management.memberships.err_discount_negative"))
            self.lbl_error.show()
            return False
        if self.chk_prepaid.isChecked() and self.radio_individual.isChecked():
            if self.spin_prepaid_months.value() < 2:
                self.lbl_error.setText(tr("management.memberships.err_prepaid_min_months"))
                self.lbl_error.show()
                return False
        self.lbl_error.hide()
        return True

    def _save(self):
        if not self._validate():
            return
        name = self.input_name.text().strip()
        plan_type = "group" if self.radio_group.isChecked() else "individual"
        fee = self.monthly_fee_spin.value()
        discount = self.discount_spin.value()
        desc = self.input_description.text().strip()

        classes_data = self.cmb_classes.currentData()
        if classes_data == -1:
            is_unlimited = True
            weekly_classes = 0
        else:
            is_unlimited = False
            weekly_classes = classes_data

        if plan_type == "group":
            is_unlimited = True
            weekly_classes = 0

        group_cap = self.spin_capacity.value() if plan_type == "group" else 1

        benefits = "\n".join(
            inp.text().strip()
            for inp in self.benefit_inputs
            if inp.text().strip()
        )

        discount_type = self.discount_type_combo.currentData()

        is_prepaid = self.chk_prepaid.isChecked() if plan_type == "individual" else False
        prepaid_months = self.spin_prepaid_months.value() if is_prepaid else 1

        if self.plan is None:
            self.repo.create_plan(name, plan_type, weekly_classes, is_unlimited, fee, discount, desc, benefits, group_cap, discount_type, is_prepaid, prepaid_months)
        else:
            self.repo.update_plan(self.plan["id"], name, plan_type, weekly_classes, is_unlimited, fee, discount, desc, benefits, group_cap, discount_type, is_prepaid, prepaid_months)

        self.accept()
