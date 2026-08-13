from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QDoubleSpinBox,
    QPushButton, QFrame, QMessageBox, QColorDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QPainter

from core.i18n import tr
from views.management.services.icon_library_dialog import IconLibraryDialog


BG_MAIN     = "#0D0D0D"
BG_CARD     = "#171717"
BG_INPUT    = "#202020"
BG_INPUT_FOCUS = "#242424"
BORDER      = "#2A2A2A"
BORDER_HOVER = "#3A3A3A"
RED         = "#C8102E"
TEXT_PRI    = "#F0F0F0"
TEXT_SEC    = "#A3A3A3"
TEXT_MUT    = "#666666"


def format_money(value):
    try:
        value = float(value or 0)
    except Exception:
        value = 0
    return "$" + f"{value:,.0f}".replace(",", ".")


class AnimatedSwitch(QFrame):
    toggled = pyqtSignal(bool)

    def __init__(self, checked=True, accent="#3B82F6", parent=None):
        super().__init__(parent)
        self._checked = checked
        self._accent = accent
        self._knob_x = 26 if checked else 3

        self.setFixedSize(58, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._anim = QPropertyAnimation(self, b"knobX", self)
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def getKnobX(self):
        return self._knob_x

    def setKnobX(self, value):
        self._knob_x = value
        self.update()

    knobX = pyqtProperty(float, getKnobX, setKnobX)

    def paintEvent(self, event):
        p = QPainter(self)
        if not p.isActive():
            return

        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        bg = QColor(self._accent if self._checked else "#333333")
        p.setBrush(bg)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(self.rect(), 15, 15)

        p.setBrush(QColor("#FFFFFF"))
        p.drawEllipse(int(self._knob_x), 3, 24, 24)

    def mousePressEvent(self, event):
        self.setChecked(not self._checked)
        self.toggled.emit(self._checked)
        super().mousePressEvent(event)

    def setChecked(self, checked):
        self._checked = checked
        self._anim.stop()
        self._anim.setStartValue(self._knob_x)
        self._anim.setEndValue(26 if checked else 3)
        self._anim.start()
        self.update()

    def isChecked(self):
        return self._checked

    def setAccent(self, accent):
        self._accent = accent
        self.update()


class ServiceDialog(QDialog):
    def __init__(self, repo, service=None, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.service = service
        self.selected_icon = "🚀"
        self.selected_color = "#3B82F6"

        self.setWindowTitle(
            tr("management.services.create_title") if service is None
            else tr("management.services.edit_title")
        )
        self.setMinimumSize(860, 640)
        self.resize(920, 700)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_MAIN};
                color: {TEXT_PRI};
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
            QFrame#sectionCard {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 20px;
            }}
            QLineEdit, QTextEdit, QDoubleSpinBox {{
                background-color: {BG_INPUT};
                color: {TEXT_PRI};
                border: 1px solid #333333;
                border-radius: 12px;
                padding: 0 14px;
                min-height: 44px;
                font-size: 14px;
                font-weight: 600;
            }}
            QTextEdit {{
                padding: 12px 14px;
                min-height: 130px;
            }}
            QLineEdit:focus, QTextEdit:focus, QDoubleSpinBox:focus {{
                background-color: {BG_INPUT_FOCUS};
                border-color: {RED};
            }}
            QCheckBox {{
                color: {TEXT_PRI};
                font-size: 13px;
                font-weight: 800;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
        """)
        self._build_ui()
        if service is not None:
            self._populate(service)

    def _field_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("""
            QLabel {
                color: #F0F0F0;
                font-size: 12px;
                font-weight: 900;
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }
        """)
        return lbl

    def _section_title(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 11px;
            font-weight: 950;
            letter-spacing: 1.2px;
            background: transparent;
            border: none;
        """)
        return lbl

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 26, 28, 24)
        root.setSpacing(22)

        # ── Header ──────────────────────────────────────────────
        header_title = QLabel(self.windowTitle())
        header_title.setStyleSheet("""
            color: white;
            font-size: 30px;
            font-weight: 950;
            letter-spacing: -0.8px;
        """)
        root.addWidget(header_title)

        header_sub = QLabel(tr("management.services.form_subtitle"))
        header_sub.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 13px;
            font-weight: 700;
            margin-top: -8px;
        """)
        root.addWidget(header_sub)

        # ── Content: Left + Right ──────────────────────────────
        content = QHBoxLayout()
        content.setSpacing(22)

        # ── LEFT: Datos del servicio ──────────────────────────
        left_card = QFrame()
        left_card.setObjectName("sectionCard")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(24, 22, 24, 24)
        left_layout.setSpacing(16)

        left_layout.addWidget(self._section_title(tr("management.services.service_data")))

        # Name
        left_layout.addWidget(self._field_label(tr("management.services.name")))
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText(tr("management.services.default_name"))
        left_layout.addWidget(self.input_name)

        # Price
        left_layout.addWidget(self._field_label(tr("management.services.price")))
        self.spin_price = QDoubleSpinBox()
        self.spin_price.setRange(0, 999999999)
        self.spin_price.setDecimals(0)
        self.spin_price.setSingleStep(1000)
        self.spin_price.setPrefix("$ ")
        self.spin_price.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        left_layout.addWidget(self.spin_price)

        self.price_preview = QLabel("$0")
        self.price_preview.setStyleSheet(f"""
            color: #22C55E;
            font-size: 12px;
            font-weight: 900;
            background: transparent;
            border: none;
        """)
        left_layout.addWidget(self.price_preview)

        # Description
        left_layout.addWidget(self._field_label(tr("management.services.description")))
        self.input_description = QTextEdit()
        self.input_description.setPlaceholderText(tr("management.services.default_description"))
        left_layout.addWidget(self.input_description)

        content.addWidget(left_card, 1)

        # ── RIGHT: Preview + Apariencia ─────────────────────────
        right_col = QVBoxLayout()
        right_col.setSpacing(18)

        # ── Preview card ────────────────────────────────────────
        self.preview_card = QFrame()
        self.preview_card.setObjectName("previewCard")
        preview_layout = QVBoxLayout(self.preview_card)
        preview_layout.setContentsMargins(24, 22, 24, 22)
        preview_layout.setSpacing(10)

        self.preview_icon = QLabel("🚀")
        self.preview_icon.setStyleSheet("font-size: 30px; background: transparent; border: none; color: white;")

        self.preview_name = QLabel(tr("management.services.default_name"))
        self.preview_name.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: 950;
            background: transparent;
            border: none;
        """)

        self.preview_desc = QLabel(tr("management.services.default_description"))
        self.preview_desc.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 12px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)

        self.preview_price = QLabel("$0")
        self.preview_price.setStyleSheet("""
            color: white;
            font-size: 22px;
            font-weight: 950;
            background: transparent;
            border: none;
        """)

        preview_layout.addWidget(self.preview_icon)
        preview_layout.addWidget(self.preview_name)
        preview_layout.addWidget(self.preview_desc)
        preview_layout.addWidget(self.preview_price)
        right_col.addWidget(self.preview_card)

        # ── Appearance card ─────────────────────────────────────
        appearance_card = QFrame()
        appearance_card.setObjectName("sectionCard")
        appearance_ly = QVBoxLayout(appearance_card)
        appearance_ly.setContentsMargins(24, 22, 24, 24)
        appearance_ly.setSpacing(16)

        appearance_ly.addWidget(self._section_title(tr("management.services.appearance")))

        # Icon row
        appearance_ly.addWidget(self._field_label(tr("management.services.icon")))
        icon_row = QHBoxLayout()
        icon_row.setSpacing(12)

        self.icon_preview = QLabel(self.selected_icon)
        self.icon_preview.setObjectName("iconPreview")
        self.icon_preview.setFixedSize(52, 52)
        self.icon_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_preview.setStyleSheet("""
            QLabel {
                background-color: #202020;
                border: 1px solid #333333;
                border-radius: 14px;
                font-size: 26px;
            }
        """)

        self.btn_choose_icon = QPushButton(tr("management.services.choose_icon"))
        self.btn_choose_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_icon.setStyleSheet(f"""
            QPushButton {{
                background-color: #202020;
                color: white;
                border: 1px solid #333333;
                border-radius: 12px;
                min-height: 42px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 900;
            }}
            QPushButton:hover {{
                background-color: #242424;
                border-color: {RED};
            }}
        """)
        self.btn_choose_icon.clicked.connect(self._open_icon_library)

        icon_row.addWidget(self.icon_preview)
        icon_row.addWidget(self.btn_choose_icon)
        icon_row.addStretch()
        appearance_ly.addLayout(icon_row)

        # Color row
        appearance_ly.addWidget(self._field_label(tr("management.services.accent_color")))
        color_row = QHBoxLayout()
        color_row.setSpacing(12)

        self.color_swatch = QLabel()
        self.color_swatch.setObjectName("colorSwatch")
        self.color_swatch.setFixedSize(52, 42)

        self.color_text = QLabel(self.selected_color)
        self.color_text.setStyleSheet("color: #F0F0F0; font-size: 13px; font-weight: 700; background: transparent; border: none;")

        self.btn_choose_color = QPushButton(tr("management.services.choose_color"))
        self.btn_choose_color.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_color.setStyleSheet(f"""
            QPushButton {{
                background-color: #202020;
                color: white;
                border: 1px solid #333333;
                border-radius: 12px;
                min-height: 42px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 900;
            }}
            QPushButton:hover {{
                background-color: #242424;
                border-color: {RED};
            }}
        """)
        self.btn_choose_color.clicked.connect(self._open_color_dialog)

        color_row.addWidget(self.color_swatch)
        color_row.addWidget(self.color_text)
        color_row.addWidget(self.btn_choose_color)
        color_row.addStretch()
        appearance_ly.addLayout(color_row)

        # Active switch
        status_layout = QHBoxLayout()
        status_layout.setSpacing(12)
        status_label = QLabel(tr("management.services.status"))
        status_label.setStyleSheet("""
            color: #F0F0F0;
            font-size: 12px;
            font-weight: 900;
            background: transparent;
            border: none;
        """)
        self.active_switch = AnimatedSwitch(checked=True, accent=self.selected_color or "#3B82F6")
        self.active_label = QLabel(tr("management.services.active"))
        self.active_label.setStyleSheet("""
            color: #22C55E;
            font-size: 12px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)
        self.active_switch.toggled.connect(self._on_active_changed)
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.active_switch)
        status_layout.addWidget(self.active_label)
        status_layout.addStretch()
        appearance_ly.addLayout(status_layout)

        right_col.addWidget(appearance_card)
        content.addLayout(right_col)

        root.addLayout(content, 1)

        # ── Footer ──────────────────────────────────────────────
        footer = QHBoxLayout()
        btn_cancel = QPushButton(tr("cancel"))
        btn_cancel.setFixedHeight(42)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: #1A1A1A; color: {TEXT_MUT};
                border: 1px solid #333333; border-radius: 12px;
                font-size: 13px; font-weight: 700;
                padding: 0 24px;
            }}
            QPushButton:hover {{ color: {TEXT_PRI}; border-color: {BORDER_HOVER}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton(tr("save"))
        self.btn_save.setFixedHeight(42)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background: {RED}; color: white;
                border: none; border-radius: 12px;
                font-size: 13px; font-weight: 700;
                padding: 0 28px;
            }}
            QPushButton:hover {{ background: #E8152F; }}
        """)
        self.btn_save.clicked.connect(self._save)

        footer.addStretch()
        footer.addWidget(btn_cancel)
        footer.addWidget(self.btn_save)
        root.addLayout(footer)

        # ── Live preview connections ──
        self.input_name.textChanged.connect(self._update_preview)
        self.input_description.textChanged.connect(self._update_preview)
        self.spin_price.valueChanged.connect(self._update_preview)
        self.spin_price.valueChanged.connect(self._update_price_preview_label)
        self._refresh_color_swatch()
        self._update_preview()

    # ── Preview helpers ─────────────────────────────────────────

    def _update_price_preview_label(self):
        self.price_preview.setText(format_money(self.spin_price.value()))

    def _update_preview(self):
        icon = self.selected_icon or "🚀"
        color = self.selected_color or "#3B82F6"
        name = self.input_name.text().strip() or tr("management.services.default_name")
        desc = self.input_description.toPlainText().strip() or tr("management.services.default_description")
        price = self.spin_price.value()

        self.preview_icon.setText(icon)
        self.preview_name.setText(name)
        self.preview_desc.setText(desc)
        self.preview_price.setText(format_money(price))
        self.preview_card.setStyleSheet(f"""
            QFrame#previewCard {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-top: 4px solid {color};
                border-radius: 20px;
            }}
            QFrame#previewCard QLabel {{
                background: transparent;
                border: none;
            }}
        """)

    # ── Icon library ────────────────────────────────────────────

    def _open_icon_library(self):
        dlg = IconLibraryDialog(self.selected_icon, parent=self)
        if dlg.exec():
            self.selected_icon = dlg.selected()
            self.icon_preview.setText(self.selected_icon)
            self._update_preview()

    # ── Color dialog ────────────────────────────────────────────

    def _open_color_dialog(self):
        current = QColor(self.selected_color or "#3B82F6")
        dialog = QColorDialog(current, self)
        dialog.setWindowTitle(tr("management.services.select_color"))
        dialog.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, False)
        if dialog.exec():
            color = dialog.selectedColor()
            if color.isValid():
                self.selected_color = color.name()
                self._refresh_color_swatch()
                self._update_preview()
                self.active_switch.setAccent(self.selected_color)

    def _refresh_color_swatch(self):
        self.color_swatch.setStyleSheet(f"""
            QLabel {{
                background-color: {self.selected_color};
                border: 1px solid #333333;
                border-radius: 10px;
            }}
        """)
        self.color_text.setText(self.selected_color)

    def _on_active_changed(self, checked):
        self.active_label.setText(
            tr("management.services.active") if checked else tr("management.services.inactive")
        )
        self.active_label.setStyleSheet(f"""
            color: {"#22C55E" if checked else "#888888"};
            font-size: 12px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)

    # ── Populate (edit mode) ────────────────────────────────────

    def _populate(self, service):
        self.input_name.setText(service.get("name", ""))
        self.input_description.setPlainText(service.get("description", ""))
        self.spin_price.setValue(float(service.get("price", 0)))
        self.selected_icon = service.get("icon", "🚀")
        self.selected_color = service.get("accent_color", "#3B82F6")
        is_active = bool(service.get("is_active", True))
        self.active_switch.setChecked(is_active)
        self.active_label.setText(tr("management.services.active") if is_active else tr("management.services.inactive"))
        self.active_label.setStyleSheet(f"""
            color: {"#22C55E" if is_active else "#888888"};
            font-size: 12px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)
        self.active_switch.setAccent(self.selected_color)
        self.icon_preview.setText(self.selected_icon)
        self._refresh_color_swatch()
        self._update_preview()

    # ── Save ────────────────────────────────────────────────────

    def _save(self):
        name = self.input_name.text().strip()
        if not name:
            QMessageBox.warning(self, tr("common.warning"), tr("management.services.name_required"))
            return

        description = self.input_description.toPlainText().strip()
        price = self.spin_price.value()
        if price < 0:
            QMessageBox.warning(self, tr("common.warning"), tr("management.services.invalid_price"))
            return

        icon = self.selected_icon or "🚀"
        accent_color = self.selected_color or "#3B82F6"
        is_active = self.active_switch.isChecked()

        try:
            if self.service is None:
                self.repo.create_service(name, description, price, icon, accent_color, is_active)
            else:
                self.repo.update_service(self.service["id"], name, description, price, icon, accent_color, is_active)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, tr("common.error"), str(e))
