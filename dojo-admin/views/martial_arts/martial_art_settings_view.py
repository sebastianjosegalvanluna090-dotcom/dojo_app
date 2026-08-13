from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame,
    QLineEdit, QScrollArea, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QStackedWidget, QCheckBox,
    QSpinBox, QDialog, QTextEdit, QLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor
from core.debug import debug_log
from views.icon_library import (
    MARTIAL_ART_ICON_LIBRARY, MartialArtIcon, normalize_martial_art_icon,
)
from views.martial_arts.martial_art_widgets import (
    DisciplineIconPickerDialog, TemplatePreviewDialog, MartialArtConfirmDialog,
    IconTextButton, create_progression_level_preview,
)
from views.martial_arts.martial_art_theme import (
    MA_BG, MA_SIDE, MA_CARD, MA_HOVER, MA_INPUT, MA_SURFACE, MA_BORDER, MA_BORDER_HI,
    MA_RED, MA_RED_H, MA_GREEN, MA_YELLOW, MA_BLUE, MA_PURPLE, MA_ORANGE,
    MA_TEXT_PRI, MA_TEXT_SEC, MA_TEXT_MUT, MA_TEXT_DARK,
    MA_FIELD_QSS, MA_SCROLL_QSS, MA_SCROLLBAR_QSS, MA_CARD_QSS,
    valid_hex_color,
    _ma_shadow, _ma_card, _ma_primary_btn, _ma_secondary_btn, _ma_icon_btn,
    _ma_field_label, _ma_section_label, _ma_badge, _ma_scroll, _ma_separator, _ma_label,
)

_MA_FF = "font-family: 'Inter', 'Segoe UI', sans-serif;"


# ═══════════════════════════════════════════════════════════════════
#  Unsaved-changes helpers
# ═══════════════════════════════════════════════════════════════════


class UnsavedChangesAction:
    KEEP_EDITING = 0
    DISCARD = 1
    SAVE = 2


class UnsavedChangesDialog(QDialog):
    """Frameless 3-button dialog for unsaved-changes confirmation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Dialog
        )
        self.setFixedSize(520, 320)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setStyleSheet("background: rgba(0, 0, 0, 155);")
        self._build_ui()

    def _build_ui(self):
        shell = QFrame(self)
        shell.setObjectName("UnsavedDialogCard")
        shell.setGeometry(20, 20, 480, 280)
        shell.setStyleSheet("""
            QFrame#UnsavedDialogCard {
                background-color: #111113;
                border: 1px solid #303036;
                border-radius: 18px;
            }
        """)

        shadow = QGraphicsDropShadowEffect(shell)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 180))
        shell.setGraphicsEffect(shadow)

        cl = QVBoxLayout(shell)
        cl.setContentsMargins(24, 24, 24, 20)
        cl.setSpacing(12)

        title = QLabel("Cambios sin guardar")
        title.setObjectName("UnsavedDialogTitle")
        title.setStyleSheet(
            f"color: {MA_TEXT_PRI}; font-size: 16px; font-weight: 700; {_MA_FF}"
        )
        cl.addWidget(title)

        msg = QLabel("Que deseas hacer con los cambios realizados?")
        msg.setObjectName("UnsavedDialogSubtitle")
        msg.setStyleSheet(
            f"color: {MA_TEXT_SEC}; font-size: 13px; {_MA_FF}"
        )
        cl.addWidget(msg)
        cl.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_discard = QPushButton("Descartar cambios")
        btn_discard.setFixedHeight(40)
        btn_discard.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_discard.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {MA_TEXT_SEC};
                border: 1px solid {MA_BORDER}; border-radius: 10px;
                font-size: 13px; font-weight: 600; {_MA_FF} padding: 0 16px;
            }}
            QPushButton:hover {{
                background: #2A0A0C; color: {MA_RED};
                border-color: {MA_RED};
            }}
        """)
        btn_discard.clicked.connect(lambda: self.done(UnsavedChangesAction.DISCARD))
        btn_row.addWidget(btn_discard)

        btn_edit = QPushButton("Seguir editando")
        btn_edit.setFixedHeight(40)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet(f"""
            QPushButton {{
                background: {MA_CARD}; color: {MA_TEXT_SEC};
                border: 1px solid {MA_BORDER}; border-radius: 10px;
                font-size: 13px; font-weight: 600; {_MA_FF} padding: 0 16px;
            }}
            QPushButton:hover {{
                background: {MA_HOVER}; color: {MA_TEXT_PRI};
                border-color: {MA_BORDER_HI};
            }}
        """)
        btn_edit.clicked.connect(lambda: self.done(UnsavedChangesAction.KEEP_EDITING))
        btn_row.addWidget(btn_edit)

        btn_save = QPushButton("Guardar y salir")
        btn_save.setFixedHeight(40)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background: {MA_RED}; color: white; border: none;
                border-radius: 10px;
                font-size: 13px; font-weight: 700; {_MA_FF} padding: 0 20px;
            }}
            QPushButton:hover {{ background: {MA_RED_H}; }}
        """)
        btn_save.clicked.connect(lambda: self.done(UnsavedChangesAction.SAVE))
        btn_row.addWidget(btn_save)

        cl.addLayout(btn_row)


# ═══════════════════════════════════════════════════════════════════
#  Navigation button
# ═══════════════════════════════════════════════════════════════════


class _NavButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._active = False
        self.setFixedHeight(52)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._bar = QFrame(self)
        self._bar.setFixedWidth(3)
        self._bar.setFixedHeight(24)
        self._bar.setStyleSheet(f"background: {MA_RED}; border-radius: 1px; border: none;")
        self._bar.setVisible(False)
        self._apply()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._bar.move(0, (self.height() - self._bar.height()) // 2)

    def set_active(self, active: bool):
        self._active = active
        self._apply()

    def _apply(self):
        if self._active:
            self._bar.setVisible(True)
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(200,16,46,0.10);
                    color: #F4F4F5;
                    border: 1px solid rgba(200,16,46,0.30);
                    border-radius: 8px;
                    margin: 2px 10px 2px 14px;
                    padding: 0 12px; font-size: 13px; font-weight: 700;
                    {_MA_FF} text-align: left;
                }}
            """)
        else:
            self._bar.setVisible(False)
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: #858B96;
                    border: 1px solid transparent;
                    border-radius: 8px;
                    margin: 2px 10px 2px 14px;
                    padding: 0 12px; font-size: 13px; font-weight: 600;
                    {_MA_FF} text-align: left;
                }}
                QPushButton:hover {{
                    background-color: #1C1C1C;
                    border-color: #303030;
                    color: #DCDDDF;
                }}
            """)


# ═══════════════════════════════════════════════════════════════════
#  Progression system card (kept intact)
# ═══════════════════════════════════════════════════════════════════


def _safe_system_icon(icon_key):
    """Return icon_key if it exists in VALID_ICON_KEYS, else None."""
    from views.icon_library import VALID_ICON_KEYS
    if icon_key and icon_key in VALID_ICON_KEYS:
        return icon_key
    return None


class ProgressionSystemCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, label, description, system_type, icon_key, parent=None):
        super().__init__(parent)
        self.system_type = system_type
        self._selected = False
        self.setFixedHeight(72)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        hl = QHBoxLayout(self)
        hl.setContentsMargins(16, 8, 16, 8)
        hl.setSpacing(12)

        safe_key = _safe_system_icon(icon_key)
        if safe_key:
            icon = MartialArtIcon(safe_key, size=32, color=MA_RED)
            hl.addWidget(icon)

        col = QVBoxLayout()
        col.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"""
            color: {MA_TEXT_PRI}; font-size: 13px; font-weight: 600;
            background: transparent; border: none;
            {_MA_FF}
        """)
        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet(f"""
            color: {MA_TEXT_SEC}; font-size: 11px;
            background: transparent; border: none;
            {_MA_FF}
        """)
        col.addWidget(lbl)
        col.addWidget(desc_lbl)
        hl.addLayout(col, 1)
        self._apply_style()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def set_selected(self, selected):
        self._selected = selected
        self._apply_style()

    def _apply_style(self):
        if self._selected:
            self.setStyleSheet(f"""
                QFrame {{
                    background: rgba(200,16,46,0.08);
                    border: 1.5px solid rgba(200,16,46,0.55);
                    border-radius: 12px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background: #181818;
                    border: 1.5px solid #303030;
                    border-radius: 12px;
                }}
                QFrame:hover {{
                    background: #1C1C1C;
                    border: 1.5px solid #404040;
                }}
            """)


# ═══════════════════════════════════════════════════════════════════
#  Template card (kept intact)
# ═══════════════════════════════════════════════════════════════════


class TemplateCard(QFrame):
    apply_clicked = pyqtSignal(dict)
    preview_clicked = pyqtSignal(dict)

    _SYSTEM_LABEL = {
        "belt": "Cinturones", "sash": "Fajas", "shirt": "Camisas",
        "bracelet": "Brazaletes", "level": "Niveles", "grade": "Grados",
        "custom": "Personalizado", "none": "Sin progresion",
    }

    def __init__(self, template, levels=None, is_current=False, parent=None):
        super().__init__(parent)
        self.template = template
        self._levels = list(levels or [])
        self._is_current = bool(is_current)
        self.setObjectName("TemplateCard")
        self.setStyleSheet("""
            QFrame#TemplateCard {
                background: #181818;
                border: 1px solid #303030;
                border-radius: 12px;
            }
            QFrame#TemplateCard:hover {
                border-color: #404040;
            }
        """)

        vl = QVBoxLayout(self)
        vl.setContentsMargins(16, 14, 16, 14)
        vl.setSpacing(10)

        top = QHBoxLayout()
        top.setSpacing(10)
        icon_key = _safe_system_icon(template.get("icon_key"))
        if icon_key:
            icon = MartialArtIcon(icon_key, size=28, color=MA_RED)
            top.addWidget(icon)

        info = QVBoxLayout()
        info.setSpacing(3)
        name_row = QHBoxLayout()
        name_row.setSpacing(8)
        name = QLabel(template.get("name", ""))
        name.setStyleSheet(f"""
            color: {MA_TEXT_PRI}; font-size: 13px; font-weight: 600;
            background: transparent; border: none; {_MA_FF}
        """)
        name_row.addWidget(name)

        if template.get("is_builtin"):
            name_row.addWidget(self._badge("INTEGRADA", """
                background: rgba(59,130,246,0.10); color: #93C5FD;
                border: 1px solid rgba(59,130,246,0.35);
            """))
        else:
            name_row.addWidget(self._badge("PERSONALIZADA", """
                background: rgba(255,255,255,0.05); color: #A1A1AA;
                border: 1px solid #303030;
            """))

        if self._is_current:
            name_row.addWidget(self._badge("ACTUAL", """
                background: rgba(200,16,46,0.12); color: #FB7185;
                border: 1px solid rgba(200,16,46,0.45);
            """))

        name_row.addStretch()
        info.addLayout(name_row)

        system_type = template.get("system_type", "belt")
        system_label = self._SYSTEM_LABEL.get(system_type, system_type)
        sys_lbl = QLabel(f"{system_label} \u00b7 {len(self._levels)} nivel(es)")
        sys_lbl.setStyleSheet(f"""
            color: {MA_TEXT_SEC}; font-size: 11px;
            background: transparent; border: none; {_MA_FF}
        """)
        info.addWidget(sys_lbl)
        top.addLayout(info, 1)
        vl.addLayout(top)

        if self._levels:
            chips_wrap = QWidget()
            chips_wrap.setStyleSheet("background: transparent; border: none;")
            chips_lay = QHBoxLayout(chips_wrap)
            chips_lay.setContentsMargins(0, 0, 0, 0)
            chips_lay.setSpacing(4)
            max_shown = 8
            for lvl in self._levels[:max_shown]:
                chips_lay.addWidget(self._level_chip(lvl))
            if len(self._levels) > max_shown:
                more_lbl = QLabel(f"+{len(self._levels) - max_shown}")
                more_lbl.setStyleSheet(f"""
                    color: {MA_TEXT_MUT}; font-size: 10px; font-weight: 700;
                    background: transparent; border: none; {_MA_FF}
                """)
                chips_lay.addWidget(more_lbl)
            chips_lay.addStretch()
            vl.addWidget(chips_wrap)

        desc = template.get("description", "")
        if desc:
            desc_lbl = QLabel(desc)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(f"""
                color: {MA_TEXT_MUT}; font-size: 11px;
                background: transparent; border: none; {_MA_FF}
            """)
            vl.addWidget(desc_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_preview = QPushButton("Vista previa")
        btn_preview.setFixedHeight(32)
        btn_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_preview.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {MA_TEXT_SEC};
                border: 1px solid {MA_BORDER}; border-radius: 8px;
                font-size: 12px; font-weight: 600; {_MA_FF} padding: 0 14px; }}
            QPushButton:hover {{ color: {MA_TEXT_PRI}; border-color: {MA_BORDER_HI}; }}
        """)
        btn_preview.clicked.connect(lambda: self.preview_clicked.emit(template))

        btn_apply = QPushButton("Aplicar")
        btn_apply.setFixedHeight(32)
        btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_apply.setStyleSheet(f"""
            QPushButton {{ background: {MA_RED}; color: white;
                border: none; border-radius: 8px;
                font-size: 12px; font-weight: 700; {_MA_FF} padding: 0 18px; }}
            QPushButton:hover {{ background: {MA_RED_H}; }}
            QPushButton:disabled {{ background: {MA_BORDER}; color: {MA_TEXT_MUT}; }}
        """)
        btn_apply.clicked.connect(lambda: self.apply_clicked.emit(template))
        if self._is_current:
            btn_apply.setEnabled(False)
            btn_apply.setToolTip("Esta plantilla ya está en uso.")

        btn_row.addWidget(btn_preview)
        btn_row.addWidget(btn_apply)
        btn_row.addStretch()
        vl.addLayout(btn_row)

    def _badge(self, text: str, extra_qss: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            {extra_qss}
            border-radius: 4px; padding: 1px 6px;
            font-size: 9px; font-weight: 800; letter-spacing: 0.5px;
            {_MA_FF}
        """)
        return lbl

    def _grade_bar(self, grades, grade_color) -> QWidget:
        wrap = QWidget()
        wrap.setFixedHeight(4)
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(1)
        segments = min(max(int(grades or 0), 1), 4)
        for _ in range(segments):
            seg = QFrame()
            seg.setStyleSheet(
                f"background: {grade_color}; border-radius: 1px; border: none;"
            )
            lay.addWidget(seg, 1)
        return wrap

    def _level_chip(self, lvl) -> QWidget:
        chip = QWidget()
        chip.setFixedSize(30, 18)
        color = valid_hex_color(lvl.get("color"), "#888888")
        pre = lvl.get("pre_color")
        grades = lvl.get("grades") or 0
        grade_color = lvl.get("grade_color")

        tooltip = (lvl.get("name") or "").strip()
        if grades:
            tooltip += f" \u00b7 {grades} grado(s)"
        tooltip += f" \u00b7 {color}"
        if pre:
            tooltip += f" \u2192 {pre}"
        chip.setToolTip(tooltip)

        system_type = self.template.get("system_type", "belt")
        if system_type == "shirt" or lvl.get("level_type") == "shirt":
            preview = create_progression_level_preview(
                lvl,
                system_type,
                width=30,
                height=18,
                parent=self,
            )
            preview.setToolTip(tooltip)
            return preview

        lay = QVBoxLayout(chip)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        base = QFrame()
        if pre and valid_hex_color(pre, None):
            base.setStyleSheet(f"""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}, stop:0.72 {color}, stop:0.72 {pre}, stop:1 {pre});
                border-radius: 3px; border: 1px solid #444444;
            """)
        else:
            base.setStyleSheet(
                f"background: {color}; border-radius: 3px; border: 1px solid #444444;"
            )
        lay.addWidget(base, 1)

        if grades and valid_hex_color(grade_color, None):
            lay.addWidget(self._grade_bar(grades, grade_color))
        return chip


# ═══════════════════════════════════════════════════════════════════
#  Promotion rule row (kept intact)
# ═══════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════
#  Local helpers
# ═══════════════════════════════════════════════════════════════════


class SettingsSectionCard(QFrame):
    """Consistent card wrapper for settings sections with optional title + description."""

    def __init__(self, title="", description="", parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsSectionCard")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            QFrame#SettingsSectionCard {
                background-color: #181818;
                border: 1px solid #303030;
                border-radius: 16px;
            }
            QFrame#SettingsSectionCard:hover {
                background-color: #1C1C1C;
                border-color: #404040;
            }
        """)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 18, 20, 20)
        self._layout.setSpacing(12)

        if title:
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet(
                f"color: {MA_TEXT_MUT}; font-size: 10px; font-weight: 800; "
                f"letter-spacing: 0.5px; {_MA_FF} background: transparent; border: none;"
            )
            self._layout.addWidget(title_lbl)

        if description:
            desc_lbl = QLabel(description)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(
                f"color: {MA_TEXT_MUT}; font-size: 11px; {_MA_FF}"
                f" background: transparent; border: none;"
            )
            self._layout.addWidget(desc_lbl)

    def layout(self) -> QVBoxLayout:
        return self._layout


class SelectableSettingsCard(QFrame):
    """Card with `selected` property that highlights on selection."""

    def __init__(self, title="", description="", parent=None):
        super().__init__(parent)
        self.setObjectName("SelectableSettingsCard")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._selected = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QFrame#SelectableSettingsCard {
                background-color: #181818;
                border: 1px solid #303030;
                border-radius: 12px;
            }
            QFrame#SelectableSettingsCard:hover {
                background-color: #1C1C1C;
                border-color: #404040;
            }
            QFrame#SelectableSettingsCard[selected="true"] {
                background-color: rgba(200,16,46,0.08);
                border: 1px solid rgba(200,16,46,0.55);
            }
        """)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 14, 16, 14)
        self._layout.setSpacing(6)

        if title:
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet(
                f"color: {MA_TEXT_PRI}; font-size: 13px; font-weight: 600; "
                f"background: transparent; border: none; {_MA_FF}"
            )
            self._layout.addWidget(title_lbl)

        if description:
            desc_lbl = QLabel(description)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(
                f"color: {MA_TEXT_MUT}; font-size: 11px; "
                f"background: transparent; border: none; {_MA_FF}"
            )
            self._layout.addWidget(desc_lbl)

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool):
        self._selected = value
        self.style().unpolish(self)
        self.style().polish(self)

    def set_selected(self, value: bool):
        self.selected = value

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.selected = not self._selected

    def layout(self) -> QVBoxLayout:
        return self._layout


# ═══════════════════════════════════════════════════════════════════
#  Root stylesheet
# ═══════════════════════════════════════════════════════════════════

_ROOT_QSS = f"""
QWidget#MartialArtSettingsPage {{
    background-color: #101010;
    border: none;
}}

QFrame#SettingsRoot {{
    background-color: #101010;
    border: none;
}}

QWidget#GeneralSettingsPage, QWidget#SystemSettingsPage,
QWidget#RulesSettingsPage, QWidget#TemplatesSettingsPage {{
    background-color: #101010;
    border: none;
}}

QFrame#SettingsSidebar {{
    background-color: #151515;
    border: 1px solid #303030;
    border-radius: 16px;
}}

QFrame#SettingsContentShell {{
    background-color: #101010;
    border: 1px solid #404040;
    border-radius: 16px;
}}

QFrame#SettingsIdentityCard, QFrame#SettingsPreviewCard,
QFrame#SettingsSystemCard, QFrame#SettingsRulesCard, QFrame#SettingsSectionCard {{
    background-color: #181818;
    border: 1px solid #303030;
    border-radius: 16px;
}}
QFrame#SettingsIdentityCard:hover, QFrame#SettingsSystemCard:hover,
QFrame#SettingsSectionCard:hover {{
    background-color: #1C1C1C;
    border-color: #404040;
}}

QLineEdit#SettingsInput, QLineEdit#DisciplineNameInput, QLineEdit#DisciplineAccentInput {{
    background-color: #202020;
    color: #F4F4F5;
    border: 1px solid #303030;
    border-radius: 10px;
    padding: 0 12px;
    min-height: 42px;
    font-size: 13px;
    {_MA_FF}
}}
QLineEdit#SettingsInput:hover, QLineEdit#DisciplineNameInput:hover, QLineEdit#DisciplineAccentInput:hover {{
    border-color: #404040;
}}
QLineEdit#SettingsInput:focus, QLineEdit#DisciplineNameInput:focus, QLineEdit#DisciplineAccentInput:focus {{
    border-color: #C8102E;
    background-color: #1C1C1C;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: #404040;
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: #505050;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
    border: none;
    background: transparent;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}
QScrollBar:horizontal {{
    height: 0;
    border: none;
    background: transparent;
}}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: transparent;
}}
"""


# ═══════════════════════════════════════════════════════════════════
#  Main view
# ═══════════════════════════════════════════════════════════════════


class MartialArtSettingsView(QWidget):
    back_clicked = pyqtSignal()
    saved = pyqtSignal()

    def __init__(self, repo, martial_art_id, parent_view=None, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.martial_art_id = martial_art_id
        self.parent_view = parent_view
        self._ma_data = {}
        self._dirty = False
        self._loading = False
        self._selected_icon_key = "generic-martial-art"
        self._initial_icon_key = "generic-martial-art"
        self._last_valid_accent = "#C8102E"
        self._blur_snapshot = None
        self._modal_overlay = None
        self._preview_timer = None

        self.setObjectName("MartialArtSettingsPage")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(_ROOT_QSS)

        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        self._settings_root = QFrame()
        self._settings_root.setObjectName("SettingsRoot")
        self._settings_root.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._root_layout.addWidget(self._settings_root)

        self._debug_stage("Inicio __init__")

        try:
            self._debug_stage("Inicio _build_ui")
            self._build_ui()
            self._debug_stage("Fin _build_ui")
        except Exception as exc:
            debug_log(f"[MartialArtSettingsView] Error en _build_ui: {exc!r}")
            self._show_fatal_error("_build_ui", exc)
            return

        try:
            self._debug_stage("Inicio _load_data")
            self._load_data()
            self._debug_stage("Fin _load_data")
        except Exception as exc:
            debug_log(f"[MartialArtSettingsView] Error en _load_data: {exc!r}")
            self._show_fatal_error("_load_data", exc)

    def _debug_stage(self, stage: str):
        debug_log(f"[MartialArtSettingsView] {stage}")

    def _clear_settings_root(self):
        """Remove every widget inside _settings_root so it can be rebuilt.

        The top-level layout of _settings_root is kept (drained and reused)
        because QWidget::setLayout refuses to install a new one while a layout
        is already installed.
        """
        if not hasattr(self, "_settings_root") or self._settings_root is None:
            return
        for w in self._settings_root.findChildren(QWidget):
            w.setParent(None)
            w.deleteLater()
        layout = self._settings_root.layout()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                sub = item.layout()
                if sub is not None:
                    sub.setParent(None)

    def _root_vbox(self, margins: int = 0) -> QVBoxLayout:
        layout = self._settings_root.layout()
        if layout is None:
            layout = QVBoxLayout(self._settings_root)
        layout.setContentsMargins(margins, margins, margins, margins)
        layout.setSpacing(0)
        return layout

    def _show_fatal_error(self, stage: str, exc: Exception):
        """Show a visible error state inside _settings_root (never a black surface)."""
        self._clear_settings_root()
        root = self._root_vbox(32)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel("No se pudo cargar la configuración")
        lbl.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 16px; font-weight: 700; {_MA_FF}")
        root.addWidget(lbl, 0, Qt.AlignmentFlag.AlignCenter)

        stage_lbl = QLabel(f"Etapa:\n{stage}")
        stage_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stage_lbl.setStyleSheet(f"color: {MA_YELLOW}; font-size: 12px; {_MA_FF}")
        root.addWidget(stage_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        detail = QLabel(f"Detalle:\n{str(exc)}")
        detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        detail.setWordWrap(True)
        detail.setStyleSheet(f"color: {MA_TEXT_SEC}; font-size: 12px; {_MA_FF}")
        root.addWidget(detail, 0, Qt.AlignmentFlag.AlignCenter)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        retry = _ma_primary_btn("Reintentar", height=34)
        retry.setFixedWidth(140)
        retry.clicked.connect(self._rebuild_settings)
        btn_row.addWidget(retry, 0, Qt.AlignmentFlag.AlignCenter)
        back = _ma_secondary_btn("Volver a disciplinas", height=34)
        back.setFixedWidth(170)
        back.clicked.connect(self.back_clicked.emit)
        btn_row.addWidget(back, 0, Qt.AlignmentFlag.AlignCenter)
        root.addLayout(btn_row)

    def _rebuild_settings(self):
        """Rebuild the whole settings view from scratch, without a new root layout."""
        self._debug_stage("Inicio _rebuild_settings")
        self._clear_settings_root()
        self._ma_data = {}
        self._dirty = False
        self._loading = False

        try:
            self._debug_stage("Inicio _rebuild_settings _build_ui")
            self._build_ui()
            self._debug_stage("Fin _rebuild_settings _build_ui")
        except Exception as exc:
            debug_log(f"[MartialArtSettingsView] Error en _build_ui: {exc!r}")
            self._show_fatal_error("_build_ui", exc)
            return

        try:
            self._debug_stage("Inicio _rebuild_settings _load_data")
            self._load_data()
            self._debug_stage("Fin _rebuild_settings _load_data")
        except Exception as exc:
            debug_log(f"[MartialArtSettingsView] Error en _load_data: {exc!r}")
            self._show_fatal_error("_load_data", exc)

    # ── UI build ──────────────────────────────────────────────────────

    def _build_ui(self):
        self._clear_settings_root()
        root = self._root_vbox(0)

        header = QHBoxLayout()
        header.setContentsMargins(24, 20, 24, 12)
        header.setSpacing(16)

        back_btn = QPushButton("\u2190  Volver a disciplinas")
        back_btn.setFixedHeight(36)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet(f"""
            QPushButton {{ background: {MA_CARD}; color: {MA_TEXT_SEC};
                border: 1px solid {MA_BORDER}; border-radius: 8px;
                padding: 0 16px; font-size: 12px; {_MA_FF} }}
            QPushButton:hover {{ color: {MA_TEXT_PRI}; border-color: {MA_BORDER_HI}; }}
        """)
        back_btn.clicked.connect(self._on_back_clicked)
        header.addWidget(back_btn)
        header.addStretch()

        btn_instructions = IconTextButton(
            "comentario-info", "Instrucciones",
            icon_size=17, icon_color="#93C5FD", height=36, variant="info_secondary",
        )
        btn_instructions.setToolTip("Consultar instrucciones de configuración")
        btn_instructions.clicked.connect(self._open_instructions)
        header.addWidget(btn_instructions)

        self.btn_save = QPushButton("Guardar cambios")
        self.btn_save.setFixedHeight(36)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setToolTip("No hay cambios pendientes.")
        self.btn_save.setStyleSheet(f"""
            QPushButton {{ background: {MA_RED}; color: white;
                border: none; border-radius: 8px; padding: 0 20px;
                font-size: 12px; font-weight: 700; {_MA_FF} }}
            QPushButton:hover {{ background: {MA_RED_H}; }}
            QPushButton:disabled {{ background: {MA_BORDER}; color: {MA_TEXT_MUT}; }}
        """)
        self.btn_save.clicked.connect(self._save_settings)
        self.btn_save.setEnabled(False)
        header.addWidget(self.btn_save)
        root.addLayout(header)

        title = QLabel("Configuracion de la disciplina")
        title.setStyleSheet(f"""
            font-size: 20px; font-weight: 800; color: {MA_TEXT_PRI};
            {_MA_FF} padding-left: 24px;
        """)
        root.addWidget(title)

        subtitle = QLabel("Define como se organizan los niveles y ascensos de esta disciplina.")
        subtitle.setStyleSheet(f"""
            font-size: 12px; color: {MA_TEXT_SEC};
            {_MA_FF} padding-left: 24px; padding-bottom: 12px;
        """)
        root.addWidget(subtitle)

        body = QHBoxLayout()
        body.setContentsMargins(24, 0, 24, 24)
        body.setSpacing(16)

        sidebar = QFrame()
        sidebar.setObjectName("SettingsSidebar")
        sidebar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        sidebar.setFixedWidth(226)
        sidebar.setStyleSheet(f"""
            QFrame#SettingsSidebar {{
                background-color: #151515;
                border: 1px solid #303030;
                border-radius: 16px;
            }}
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(8, 10, 8, 10)
        sidebar_layout.setSpacing(5)

        nav_names = ["General", "Sistema", "Reglas", "Plantillas"]
        self._nav_btns = []
        for i, name in enumerate(nav_names):
            btn = _NavButton(name)
            btn.clicked.connect(lambda checked, idx=i: self._switch_tab(idx))
            sidebar_layout.addWidget(btn)
            self._nav_btns.append(btn)
        sidebar_layout.addStretch()

        body.addWidget(sidebar)

        self.content_shell = QFrame()
        self.content_shell.setObjectName("SettingsContentShell")
        self.content_shell.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        shell_layout = QVBoxLayout(self.content_shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.setObjectName("SettingsContentStack")
        self.stack.setStyleSheet("background: transparent; border: none;")
        for _name, _builder in [
            ("_build_general_tab", self._build_general_tab),
            ("_build_system_tab", self._build_system_tab),
            ("_build_rules_tab", self._build_rules_tab),
            ("_build_templates_tab", self._build_templates_tab),
        ]:
            try:
                self._debug_stage(f"Inicio {_name}")
                _tab = _builder()
                self._debug_stage(f"Fin {_name}")
            except Exception as exc:
                raise RuntimeError(f"Fallo {_name}: {exc!r}") from exc
            self.stack.addWidget(_tab)
        shell_layout.addWidget(self.stack)

        body.addWidget(self.content_shell, 1)

        root.addLayout(body, 1)

        self._switch_tab(0)

        if not hasattr(self, "stack"):
            raise RuntimeError("No se creó SettingsContentStack")
        if self.stack.count() != 4:
            raise RuntimeError(
                "Configuración debe contener General, Sistema, Reglas y Plantillas"
            )
        if not hasattr(self, "_nav_btns"):
            raise RuntimeError("No se creó la navegación de Configuración")

    # ── General tab ───────────────────────────────────────────────────

    def _build_general_tab(self):
        page = QWidget()
        page.setObjectName("GeneralSettingsPage")
        page.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(MA_SCROLL_QSS)
        scroll.viewport().setAutoFillBackground(False)
        scroll.viewport().setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        hl = QHBoxLayout(container)
        hl.setContentsMargins(24, 20, 24, 24)
        hl.setSpacing(16)

        # ── Left column: identity ──
        identity_card = SettingsSectionCard("IDENTIDAD", "Nombre, icono y color de la disciplina.")
        id_layout = identity_card.layout()

        id_layout.addWidget(_ma_field_label("NOMBRE"))
        self.inp_name = QLineEdit()
        self.inp_name.setObjectName("DisciplineNameInput")
        self.inp_name.setPlaceholderText("Nombre del arte marcial")
        self.inp_name.textChanged.connect(self._mark_dirty)
        self.inp_name.textChanged.connect(self._refresh_general_preview)
        id_layout.addWidget(self.inp_name)

        icon_section_label = _ma_field_label("ICONO")
        id_layout.addWidget(icon_section_label)

        icon_row = QHBoxLayout()
        icon_row.setSpacing(12)

        self._current_icon_preview = MartialArtIcon(
            self._selected_icon_key, size=44, color=MA_RED
        )
        self._current_icon_preview.setStyleSheet("background: transparent;")
        icon_row.addWidget(self._current_icon_preview)

        icon_info = QVBoxLayout()
        icon_info.setSpacing(4)
        self._current_icon_preview.setToolTip("Icono seleccionado")

        btn_pick_icon = QPushButton("Elegir icono")
        btn_pick_icon.setFixedHeight(30)
        btn_pick_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pick_icon.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {MA_TEXT_SEC};
                border: 1px solid {MA_BORDER}; border-radius: 6px;
                font-size: 11px; font-weight: 600; {_MA_FF} padding: 0 12px;
            }}
            QPushButton:hover {{ color: {MA_TEXT_PRI}; border-color: {MA_BORDER_HI}; }}
        """)
        btn_pick_icon.clicked.connect(self._open_icon_picker)
        icon_info.addWidget(btn_pick_icon)
        icon_info.addStretch()

        icon_row.addLayout(icon_info, 1)
        id_layout.addLayout(icon_row)

        id_layout.addWidget(_ma_field_label("COLOR PRINCIPAL"))
        color_row = QHBoxLayout()
        color_row.setSpacing(8)
        self.inp_accent = QLineEdit()
        self.inp_accent.setObjectName("DisciplineAccentInput")
        self.inp_accent.setPlaceholderText("#C8102E")
        self.inp_accent.setFixedWidth(120)
        self.inp_accent.textChanged.connect(self._mark_dirty)
        self.inp_accent.textChanged.connect(self._refresh_general_preview)
        color_row.addWidget(self.inp_accent)

        self.accent_preview = QFrame()
        self.accent_preview.setFixedSize(36, 36)
        self.accent_preview.setStyleSheet(f"""
            QFrame {{ background: {MA_RED}; border-radius: 8px; border: 2px solid {MA_BORDER_HI}; }}
        """)
        color_row.addWidget(self.accent_preview)
        color_row.addStretch()
        id_layout.addLayout(color_row)

        id_layout.addWidget(_ma_field_label("ESTADO"))
        state_row = QHBoxLayout()
        state_row.setSpacing(16)

        state_info = QVBoxLayout()
        state_info.setSpacing(3)
        self._lbl_state_title = QLabel("Activa")
        self._lbl_state_title.setStyleSheet(f"""
            color: {MA_GREEN}; font-size: 13px; font-weight: 700;
            background: transparent; border: none; {_MA_FF}
        """)
        state_desc = QLabel("La disciplina puede recibir estudiantes y ascensos.")
        state_desc.setWordWrap(True)
        state_desc.setStyleSheet(f"""
            color: {MA_TEXT_MUT}; font-size: 11px;
            background: transparent; border: none; {_MA_FF}
        """)
        state_info.addWidget(self._lbl_state_title)
        state_info.addWidget(state_desc)
        state_row.addLayout(state_info, 1)

        self.btn_toggle_active = QPushButton("Desactivar")
        self.btn_toggle_active.setFixedHeight(34)
        self.btn_toggle_active.setFixedWidth(120)
        self.btn_toggle_active.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_active.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {MA_TEXT_SEC};
                border: 1px solid {MA_BORDER}; border-radius: 8px;
                font-size: 12px; font-weight: 600; {_MA_FF}
            }}
            QPushButton:hover {{ color: {MA_RED}; border-color: {MA_RED}; }}
        """)
        self.btn_toggle_active.clicked.connect(self._toggle_active)
        self.btn_toggle_active.clicked.connect(self._refresh_general_preview)
        state_row.addWidget(self.btn_toggle_active)
        id_layout.addLayout(state_row)

        id_layout.addWidget(_ma_field_label("DESCRIPCION"))
        self.inp_description = QTextEdit()
        self.inp_description.setPlaceholderText(
            "Describe el objetivo, metodologia y caracteristicas de la disciplina."
        )
        self.inp_description.setMaximumHeight(90)
        self.inp_description.setStyleSheet(f"""
            QTextEdit {{ background: {MA_INPUT}; color: {MA_TEXT_PRI}; border: 1.5px solid {MA_BORDER};
                border-radius: 8px; padding: 8px 12px; font-size: 12px; {_MA_FF} }}
            QTextEdit:focus {{ border-color: {MA_BLUE}; }}
        """)
        self.inp_description.textChanged.connect(self._mark_dirty)
        id_layout.addWidget(self.inp_description)

        id_layout.addWidget(_ma_field_label("ENFOQUE DE ENTRENAMIENTO"))
        self.inp_training_focus = QLineEdit()
        self.inp_training_focus.setObjectName("TrainingFocusInput")
        self.inp_training_focus.setPlaceholderText(
            "Ejemplo: fuerza, movilidad, resistencia, coordinacion y tecnica."
        )
        self.inp_training_focus.setStyleSheet(MA_FIELD_QSS)
        self.inp_training_focus.textChanged.connect(self._mark_dirty)
        id_layout.addWidget(self.inp_training_focus)

        id_layout.addStretch()
        hl.addWidget(identity_card, 3)

        # ── Right column: preview ──
        preview_card = SettingsSectionCard("VISTA PREVIA", "Cambios reflejados en tiempo real.")
        pv_layout = preview_card.layout()

        self._preview_icon = MartialArtIcon(
            self._selected_icon_key, size=48, color=MA_RED
        )
        self._preview_icon.setStyleSheet("background: transparent;")
        pv_layout.addWidget(self._preview_icon, 0, Qt.AlignmentFlag.AlignHCenter)

        self._preview_name = QLabel("Nombre de disciplina")
        self._preview_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_name.setStyleSheet(
            f"color: {MA_TEXT_PRI}; font-size: 16px; font-weight: 700; {_MA_FF}"
            " background: transparent; border: none;"
        )
        pv_layout.addWidget(self._preview_name)

        self._preview_color_bar = QFrame()
        self._preview_color_bar.setFixedHeight(4)
        self._preview_color_bar.setStyleSheet(f"""
            QFrame {{ background: {MA_RED}; border-radius: 2px; border: none; }}
        """)
        pv_layout.addWidget(self._preview_color_bar)

        self._preview_status = _ma_badge("active")
        pv_layout.addWidget(self._preview_status, 0, Qt.AlignmentFlag.AlignHCenter)

        self._preview_system = QLabel("Sistema: Cinturones")
        self._preview_system.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_system.setStyleSheet(
            f"color: {MA_TEXT_MUT}; font-size: 12px; {_MA_FF}"
            " background: transparent; border: none;"
        )
        pv_layout.addWidget(self._preview_system)

        pv_layout.addStretch()
        hl.addWidget(preview_card, 2)

        scroll.setWidget(container)
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        return page

    # ── System tab ────────────────────────────────────────────────────

    def _build_system_tab(self):
        page = QWidget()
        page.setObjectName("SystemSettingsPage")
        page.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(MA_SCROLL_QSS)
        scroll.viewport().setAutoFillBackground(False)
        scroll.viewport().setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        vl = QVBoxLayout(container)
        vl.setContentsMargins(24, 20, 24, 24)
        vl.setSpacing(16)

        self.card_no_progression = ProgressionSystemCard(
            "Sin progresion", "No utiliza niveles ni grados.",
            "none", "personalizado"
        )
        self.card_no_progression.clicked.connect(lambda: self._select_system("none"))
        vl.addWidget(self.card_no_progression)

        self.card_use_progression = ProgressionSystemCard(
            "Utiliza un sistema", "Cinturones, camisas, brazaletes, niveles u otro.",
            "belt", "belt"
        )
        self.card_use_progression.clicked.connect(lambda: self._select_system("belt"))
        vl.addWidget(self.card_use_progression)

        self._system_detail_frame = SettingsSectionCard(
            "TIPO DE SISTEMA", "Elige como se clasifica la progresion."
        )
        detail_layout = self._system_detail_frame.layout()

        self._system_names_frame = SettingsSectionCard(
            "NOMBRES PERSONALIZADOS",
            "Define como se llamaran los niveles. Solo aplica al sistema Personalizado."
        )
        names_layout = self._system_names_frame.layout()
        name_row = QHBoxLayout()
        name_row.setSpacing(16)

        name_col = QVBoxLayout()
        name_col.addWidget(_ma_field_label("SINGULAR"))
        self.inp_label_singular = QLineEdit()
        self.inp_label_singular.setPlaceholderText("Nivel")
        self.inp_label_singular.setStyleSheet(MA_FIELD_QSS)
        self.inp_label_singular.textChanged.connect(self._mark_dirty)
        name_col.addWidget(self.inp_label_singular)
        name_row.addLayout(name_col)

        plural_col = QVBoxLayout()
        plural_col.addWidget(_ma_field_label("PLURAL"))
        self.inp_label_plural = QLineEdit()
        self.inp_label_plural.setPlaceholderText("Niveles")
        self.inp_label_plural.setStyleSheet(MA_FIELD_QSS)
        self.inp_label_plural.textChanged.connect(self._mark_dirty)
        plural_col.addWidget(self.inp_label_plural)
        name_row.addLayout(plural_col)

        names_layout.addLayout(name_row)
        self._system_names_frame.setVisible(False)

        self.system_cards_layout = QGridLayout()
        self.system_cards_layout.setSpacing(8)
        self.system_cards_layout.setContentsMargins(0, 0, 0, 0)
        self._system_type_cards = []
        system_types = [
            ("Cinturones", "belt", "cinto"),
            ("Camisas", "shirt", "camiza"),
            ("Brazaletes", "bracelet", "brazalete"),
            ("Niveles", "level", "niveles"),
            ("Personalizado", "custom", "personalizado"),
        ]
        for idx, (label, stype, icon_key) in enumerate(system_types):
            card = ProgressionSystemCard(label, "", stype, icon_key)
            card.setFixedHeight(56)
            card.setMinimumWidth(190)
            card.clicked.connect(lambda s=stype: self._select_sub_system(s))
            row = idx // 3
            col = idx % 3
            self.system_cards_layout.addWidget(card, row, col)
            self._system_type_cards.append((stype, card))
        detail_layout.addLayout(self.system_cards_layout)

        self._system_detail_frame.setVisible(False)
        vl.addWidget(self._system_detail_frame)
        vl.addWidget(self._system_names_frame)

        vl.addStretch()
        scroll.setWidget(container)
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        return page

    # ── Rules tab ─────────────────────────────────────────────────────

    def _build_rules_tab(self):
        page = QWidget()
        page.setObjectName("RulesSettingsPage")
        page.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(MA_SCROLL_QSS)
        scroll.viewport().setAutoFillBackground(False)
        scroll.viewport().setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        vl = QVBoxLayout(container)
        vl.setContentsMargins(24, 20, 24, 24)
        vl.setSpacing(16)

        mode_card = SettingsSectionCard(
            "MODO DE ASCENSO",
            "Define como los estudiantes avanzan entre niveles."
        )
        mode_layout = mode_card.layout()

        self._migration_warning = QLabel("")
        self._migration_warning.setWordWrap(True)
        self._migration_warning.setVisible(False)
        self._migration_warning.setStyleSheet(f"color: {MA_YELLOW}; font-size: 11px; {_MA_FF} background: transparent; border: none; padding: 4px 0;")
        mode_layout.addWidget(self._migration_warning)

        modes = [
            ("Secuencial", "Solo permite el siguiente nivel por orden. No se permiten saltos.", "sequential"),
            ("Permitir saltos", "El administrador puede seleccionar cualquier nivel superior.", "manual"),
        ]
        self._mode_cards = []
        for label, desc, mode in modes:
            card = ProgressionSystemCard(label, desc, mode, "belt")
            card.setFixedHeight(64)
            card.clicked.connect(lambda m=mode: self._select_promotion_mode(m))
            mode_layout.addWidget(card)
            self._mode_cards.append((mode, card))
        vl.addWidget(mode_card)

        age_card = SettingsSectionCard(
            "RESTRICCIONES DE EDAD POR NIVEL",
            "Define si algunos niveles solo aplican a ciertas edades (ej: infantil solo menores de 14 anios, avanzado solo mayores de 16)."
        )
        age_layout = age_card.layout()

        self.chk_age_enabled = QCheckBox("Habilitar restricciones de edad por nivel")
        self.chk_age_enabled.setStyleSheet(f"""
            QCheckBox {{ color: {MA_TEXT_PRI}; font-size: 13px; spacing: 8px; {_MA_FF} }}
            QCheckBox::indicator {{
                width: 18px; height: 18px; border-radius: 4px;
                border: 1.5px solid {MA_BORDER}; background: {MA_INPUT};
            }}
            QCheckBox::indicator:checked {{ background: {MA_GREEN}; border-color: {MA_GREEN}; }}
        """)
        self.chk_age_enabled.stateChanged.connect(self._on_age_toggle)
        age_layout.addWidget(self.chk_age_enabled)

        self._age_table_container = QWidget()
        self._age_table_container.setStyleSheet("background: transparent;")
        self._age_table_layout = QGridLayout(self._age_table_container)
        self._age_table_layout.setContentsMargins(0, 8, 0, 0)
        self._age_table_layout.setSpacing(6)
        self._age_table_container.setVisible(False)
        age_layout.addWidget(self._age_table_container)
        self._age_spin_boxes = {}
        self._age_note_edits = {}
        vl.addWidget(age_card)

        vl.addStretch()
        scroll.setWidget(container)
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        return page

    # ── Templates tab ─────────────────────────────────────────────────

    def _build_templates_tab(self):
        page = QWidget()
        page.setObjectName("TemplatesSettingsPage")
        page.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(MA_SCROLL_QSS)
        scroll.viewport().setAutoFillBackground(False)
        scroll.viewport().setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        vl = QVBoxLayout(container)
        vl.setContentsMargins(24, 20, 24, 24)
        vl.setSpacing(12)

        self.templates_layout = QVBoxLayout()
        self.templates_layout.setSpacing(12)
        vl.addLayout(self.templates_layout)
        vl.addStretch()

        scroll.setWidget(container)
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        return page

    # ── Tab switching ─────────────────────────────────────────────────

    def _switch_tab(self, idx):
        self.stack.setCurrentIndex(idx)
        new_widget = self.stack.currentWidget()
        for i, btn in enumerate(self._nav_btns):
            btn.set_active(i == idx)
        self._fade_transition(new_widget)

    def _fade_transition(self, widget):
        if not widget:
            return
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(180)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        widget._fade_anim = anim

    # ── System selection ──────────────────────────────────────────────

    def _select_system(self, system_type):
        pe = system_type != "none"
        self._ma_data["progression_enabled"] = pe
        self._ma_data["progression_system"] = system_type
        self.card_no_progression.set_selected(not pe)
        self.card_use_progression.set_selected(pe)
        self._system_detail_frame.setVisible(pe)
        self._system_names_frame.setVisible(pe and system_type == "custom")
        if not pe:
            self._ma_data["progression_label_singular"] = "Nivel"
            self._ma_data["progression_label_plural"] = "Niveles"
        if pe:
            self._load_age_rules()
        self._refresh_general_preview()
        self._mark_dirty()
        self._load_templates()

    def _select_sub_system(self, system_type):
        self._ma_data["progression_system"] = system_type
        for st, card in self._system_type_cards:
            card.set_selected(st == system_type)
        defaults = {
            "belt": ("Cinturon", "Cinturones"),
            "shirt": ("Camisa", "Camisas"),
            "bracelet": ("Brazalete", "Brazaletes"),
            "level": ("Nivel", "Niveles"),
            "custom": ("Nivel", "Niveles"),
        }
        singular, plural = defaults.get(system_type, ("Nivel", "Niveles"))
        self.inp_label_singular.setText(singular)
        self.inp_label_plural.setText(plural)
        self._ma_data["progression_label_singular"] = singular
        self._ma_data["progression_label_plural"] = plural
        is_custom = system_type == "custom"
        self._system_names_frame.setVisible(is_custom)
        self._refresh_general_preview()
        self._mark_dirty()
        self._load_templates()

    def _select_promotion_mode(self, mode):
        self._ma_data["promotion_mode"] = mode
        self._ma_data["allow_level_skips"] = (mode == "manual")
        for m, card in self._mode_cards:
            card.set_selected(m == mode)
        self._mark_dirty()

    # ── Icon picker ───────────────────────────────────────────────────

    def _open_icon_picker(self):
        dlg = DisciplineIconPickerDialog(
            current_key=self._selected_icon_key, parent=self
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_key = dlg.selected_key()
            self._selected_icon_key = new_key
            if hasattr(self, '_current_icon_preview'):
                self._current_icon_preview.set_icon(new_key)
            self._refresh_general_preview()
            self._mark_dirty()

    # ── Preview refresh ───────────────────────────────────────────────

    def _refresh_general_preview(self):
        self._debug_stage("Inicio _refresh_general_preview")
        if getattr(self, '_loading', False):
            return
        if self._preview_timer and self._preview_timer.isActive():
            self._preview_timer.stop()
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._do_refresh_general_preview)
        self._preview_timer.start(60)

    def _do_refresh_general_preview(self):
        name_text = self.inp_name.text().strip() or "Nombre de disciplina"

        accent_candidate = self.inp_accent.text().strip()
        valid = valid_hex_color(accent_candidate, None)
        if valid:
            self._last_valid_accent = valid
        accent = self._last_valid_accent

        self._preview_name.setText(name_text)
        self._preview_color_bar.setStyleSheet(f"""
            QFrame {{ background: {accent}; border-radius: 2px; border: none; }}
        """)
        if hasattr(self, 'accent_preview'):
            self.accent_preview.setStyleSheet(f"""
                QFrame {{ background: {accent}; border-radius: 8px;
                    border: 2px solid {MA_BORDER_HI}; }}
            """)
        if hasattr(self, '_preview_icon'):
            self._preview_icon.set_icon(self._selected_icon_key)
            self._preview_icon.set_color(accent)

        # Read state directly from the martial-art data
        is_active = self._ma_data.get("is_active", True)
        status_text = "Activa" if is_active else "Inactiva"
        self._preview_status.setText(status_text)

        pe = self._ma_data.get("progression_enabled", True)
        ps = self._ma_data.get("progression_system", "belt")
        if not pe:
            ps = "none"

        system_labels = {
            "none": "Sin progresión", "belt": "Cinturones",
            "sash": "Fajas", "shirt": "Camisas", "bracelet": "Brazaletes",
            "level": "Niveles", "grade": "Grados", "custom": "Personalizado",
        }
        self._preview_system.setText(
            f"Sistema: {system_labels.get(ps, ps)}"
        )

    # ── Active toggle ─────────────────────────────────────────────────

    def _toggle_active(self):
        current = self._ma_data.get("is_active", True)
        self._ma_data["is_active"] = not current
        self._is_active = not current
        self._refresh_active_ui()
        self._refresh_general_preview()
        self._mark_dirty()

    def _refresh_active_ui(self):
        is_active = self._ma_data.get("is_active", True)
        if is_active:
            self._lbl_state_title.setText("Activa")
            self._lbl_state_title.setStyleSheet(f"""
                color: {MA_GREEN}; font-size: 13px; font-weight: 700;
                background: transparent; border: none; {_MA_FF}
            """)
            self.btn_toggle_active.setText("Desactivar")
            self.btn_toggle_active.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {MA_TEXT_SEC};
                    border: 1px solid {MA_BORDER}; border-radius: 8px;
                    font-size: 12px; font-weight: 600; {_MA_FF}
                }}
                QPushButton:hover {{ color: {MA_RED}; border-color: {MA_RED}; }}
            """)
        else:
            self._lbl_state_title.setText("Inactiva")
            self._lbl_state_title.setStyleSheet(f"""
                color: {MA_TEXT_MUT}; font-size: 13px; font-weight: 700;
                background: transparent; border: none; {_MA_FF}
            """)
            self.btn_toggle_active.setText("Activar")
            self.btn_toggle_active.setStyleSheet(f"""
                QPushButton {{
                    background: {MA_GREEN}18; color: {MA_GREEN};
                    border: 1px solid {MA_GREEN}40; border-radius: 8px;
                    font-size: 12px; font-weight: 700; {_MA_FF}
                }}
                QPushButton:hover {{ background: {MA_GREEN}28; }}
            """)

    # ── Back / unsaved changes ────────────────────────────────────────

    def _on_back_clicked(self):
        if not self._dirty:
            self.back_clicked.emit()
            return
        self._show_modal_background()

    def _show_modal_background(self):
        root = self.window()
        self._modal_overlay = QFrame(root)
        self._modal_overlay.setObjectName("SettingsModalOverlay")
        self._modal_overlay.setGeometry(root.rect())
        self._modal_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 155); border: none;")
        self._modal_overlay.show()
        self._modal_overlay.raise_()

        dialog = UnsavedChangesDialog(parent=root)
        try:
            result = dialog.exec()
        finally:
            self._hide_modal_background()

        self._handle_unsaved_action(result)

    def _hide_modal_background(self):
        if hasattr(self, '_modal_overlay') and self._modal_overlay:
            self._modal_overlay.deleteLater()
            self._modal_overlay = None

    def _handle_unsaved_action(self, action):
        if action == UnsavedChangesAction.KEEP_EDITING:
            return
        if action == UnsavedChangesAction.DISCARD:
            self._set_clean()
            self.back_clicked.emit()
            return
        if action == UnsavedChangesAction.SAVE:
            if self._save_settings():
                self.back_clicked.emit()
            return

    def _open_instructions(self):
        from views.martial_arts.martial_art_widgets import MartialArtInstructionsDialog
        dlg = MartialArtInstructionsDialog(parent=self)
        dlg.exec()

    # ── Dirty tracking ────────────────────────────────────────────────

    def _mark_dirty(self):
        if getattr(self, '_loading', False):
            return
        self._dirty = True
        self.btn_save.setEnabled(True)
        self.btn_save.setToolTip("Guardar los cambios de la disciplina.")
        self._show_dirty_badge(True)

    def _set_clean(self):
        """Reset dirty state: disable save and restore the idle tooltip."""
        self._dirty = False
        self.btn_save.setEnabled(False)
        self.btn_save.setToolTip("No hay cambios pendientes.")

    def _show_dirty_badge(self, show: bool):
        pass

    # ── Age rules ─────────────────────────────────────────────────────

    def _load_age_rules(self):
        for i in reversed(range(self._age_table_layout.count())):
            item = self._age_table_layout.takeAt(i)
            if item.widget():
                item.widget().deleteLater()
        self._age_spin_boxes.clear()
        self._age_note_edits.clear()

        belts = self.repo.get_belts(self.martial_art_id)
        if not belts:
            no_belts = QLabel("Agrega niveles primero para configurar restricciones de edad.")
            no_belts.setStyleSheet(f"""
                color: {MA_TEXT_MUT}; font-size: 12px; font-style: italic;
                padding: 8px; background: transparent; border: none; {_MA_FF}
            """)
            self._age_table_layout.addWidget(no_belts, 0, 0, 1, 4)
            return

        rules = self.repo.get_level_age_rules(self.martial_art_id)
        rule_map = {r["level_id"]: r for r in rules}

        headers = ["Nivel", "Edad min", "Edad max", "Nota"]
        for col, h in enumerate(headers):
            lbl = QLabel(h)
            lbl.setStyleSheet(f"""
                color: {MA_TEXT_MUT}; font-size: 11px; font-weight: 600;
                padding: 4px; background: transparent; border: none; {_MA_FF}
            """)
            self._age_table_layout.addWidget(lbl, 0, col)

        for row_idx, belt in enumerate(belts):
            lv_id = belt["id"]
            rule = rule_map.get(lv_id, {})

            name_lbl = QLabel(belt.get("name", ""))
            name_lbl.setStyleSheet(f"""
                color: {MA_TEXT_PRI}; font-size: 12px;
                padding: 4px; background: transparent; border: none; {_MA_FF}
            """)
            self._age_table_layout.addWidget(name_lbl, row_idx + 1, 0)

            min_spin = QSpinBox()
            min_spin.setRange(0, 100)
            min_spin.setValue(rule.get("minimum_age") or 0)
            min_spin.setSpecialValueText("-")
            min_spin.setStyleSheet(MA_FIELD_QSS)
            min_spin.setMinimumWidth(80)
            min_spin.valueChanged.connect(self._mark_dirty)
            self._age_spin_boxes[lv_id] = {"min": min_spin}
            self._age_table_layout.addWidget(min_spin, row_idx + 1, 1)

            max_spin = QSpinBox()
            max_spin.setRange(0, 100)
            max_spin.setValue(rule.get("maximum_age") or 0)
            max_spin.setSpecialValueText("-")
            max_spin.setStyleSheet(MA_FIELD_QSS)
            max_spin.setMinimumWidth(80)
            max_spin.valueChanged.connect(self._mark_dirty)
            self._age_spin_boxes[lv_id]["max"] = max_spin
            self._age_table_layout.addWidget(max_spin, row_idx + 1, 2)

            note_edit = QLineEdit()
            note_edit.setPlaceholderText("Opcional")
            note_edit.setText(rule.get("age_restriction_note") or "")
            note_edit.setStyleSheet(MA_FIELD_QSS)
            note_edit.textChanged.connect(self._mark_dirty)
            self._age_note_edits[lv_id] = note_edit
            self._age_table_layout.addWidget(note_edit, row_idx + 1, 3)

    def _on_age_toggle(self, state):
        enabled = state == Qt.CheckState.Checked.value
        self._age_table_container.setVisible(enabled)
        if enabled and not self._age_spin_boxes:
            self._load_age_rules()
        self._mark_dirty()

    # ── Data loading ──────────────────────────────────────────────────

    def _load_data(self):
        self._debug_stage("Inicio _load_data")
        self._loading = True
        try:
            data = self.repo.get_martial_arts_full()
            for ma in data:
                if ma["id"] == self.martial_art_id:
                    self._ma_data = ma
                    break

            if not self._ma_data:
                raise ValueError("No se encontraron datos de la disciplina")

            self.inp_name.setText(self._ma_data.get("name", ""))
            accent = self._ma_data.get("accent_color", "#C8102E") or "#C8102E"
            self.inp_accent.setText(accent)
            self._last_valid_accent = valid_hex_color(accent, "#C8102E")
            self.accent_preview.setStyleSheet(f"""
                QFrame {{ background: {accent}; border-radius: 8px; border: 2px solid {MA_BORDER_HI}; }}
            """)
            self._refresh_active_ui()

            raw_icon = self._ma_data.get("icon_key")
            normalized = normalize_martial_art_icon(raw_icon, self._ma_data.get("name", ""))
            self._selected_icon_key = normalized
            self._initial_icon_key = normalized
            if hasattr(self, '_current_icon_preview'):
                self._current_icon_preview.set_icon(normalized)

            if hasattr(self, 'inp_description'):
                self.inp_description.setPlainText(self._ma_data.get("description") or "")
            if hasattr(self, 'inp_training_focus'):
                self.inp_training_focus.setText(self._ma_data.get("training_focus") or "")

            pe = self._ma_data.get("progression_enabled", True)
            ps = self._ma_data.get("progression_system", "belt")
            self.card_no_progression.set_selected(not pe)
            self.card_use_progression.set_selected(pe)
            self._system_detail_frame.setVisible(pe)
            self._system_names_frame.setVisible(pe and ps == "custom")
            if pe:
                self._load_age_rules()

            self.inp_label_singular.setText(self._ma_data.get("progression_label_singular", "Cinturon"))
            self.inp_label_plural.setText(self._ma_data.get("progression_label_plural", "Cinturones"))

            for st, card in self._system_type_cards:
                card.set_selected(st == ps)

            pm = self._ma_data.get("promotion_mode", "sequential")
            migration_map = {
                "sequential_with_grades": ("sequential", "Se migro el modo desde Secuencial con Grados a Secuencial simple."),
                "custom_rules": ("manual", "Se migro el modo desde Reglas Personalizadas a Permitir Saltos."),
            }
            if pm in migration_map:
                new_pm, warning_msg = migration_map[pm]
                pm = new_pm
                self._ma_data["promotion_mode"] = pm
                self._ma_data["allow_level_skips"] = (pm == "manual")
                self._migration_warning.setText(warning_msg)
                self._migration_warning.setVisible(True)
            else:
                self._migration_warning.setVisible(False)
            for m, card in self._mode_cards:
                card.set_selected(m == pm)

            self._load_templates()

            self._refresh_general_preview()
        finally:
            self._loading = False
            self._set_clean()
            self._do_refresh_general_preview()
            self._debug_stage("Fin _load_data")

    # ── Rules loading ─────────────────────────────────────────────────

    # ── Templates loading ─────────────────────────────────────────────

    def _load_templates(self):
        while self.templates_layout.count():
            item = self.templates_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        system = self._ma_data.get("progression_system", "belt")
        templates = self.repo.get_progression_templates(system_type=system)

        visible = []
        for tpl in templates:
            stype = tpl.get("system_type", "")
            key = tpl.get("template_key", "")
            if system == "none":
                if key == "no_progression":
                    visible.append(tpl)
            elif system == "custom":
                if key == "custom":
                    visible.append(tpl)
            elif stype == system:
                visible.append(tpl)

        if not visible:
            empty = QLabel("No hay plantillas disponibles para este tipo de sistema.")
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(f"""
                background: #181818; color: #71717A; font-size: 12px;
                border: 1px dashed #303030; border-radius: 12px;
                padding: 28px 20px; {_MA_FF}
            """)
            self.templates_layout.addWidget(empty)
            return

        current_key = self._ma_data.get("template_key")
        for tpl in visible:
            levels = self.repo.get_template_levels(tpl["id"])
            is_current = bool(current_key) and current_key == tpl.get("template_key")
            card = TemplateCard(tpl, levels, is_current=is_current)
            card.preview_clicked.connect(lambda t=tpl: self._preview_template(t))
            card.apply_clicked.connect(lambda t=tpl: self._apply_template(t))
            self.templates_layout.addWidget(card)

    def _preview_template(self, template):
        levels = self.repo.get_template_levels(template["id"])
        dlg = TemplatePreviewDialog(template, levels, parent=self)
        dlg.exec()

    def _apply_template(self, template):
        levels = self.repo.get_template_levels(template["id"])
        has_students = self.repo.has_students_with_levels(self.martial_art_id)

        if has_students:
            msg = MartialArtConfirmDialog(
                title="No disponible",
                message="Esta disciplina ya tiene niveles configurados.",
                detail_text="No se puede reemplazar porque existen estudiantes con niveles asignados.",
                confirm_text="Entendido",
                parent=self,
            )
            msg.exec()
            return

        confirm = MartialArtConfirmDialog(
            title="Aplicar plantilla",
            message=f"Aplicar la plantilla '{template.get('name', '')}'?",
            detail_text=f"Se crearan {len(levels)} nivel(es) para esta disciplina.",
            confirm_text="Aplicar",
            parent=self,
        )
        if confirm.exec() == QDialog.DialogCode.Accepted:
            try:
                self.repo.apply_progression_template(
                    self.martial_art_id, template["id"], "append_missing"
                )
                self._load_data()
                self.saved.emit()
            except Exception as e:
                err = MartialArtConfirmDialog(
                    title="Error", message=str(e),
                    confirm_text="Cerrar", parent=self,
                )
                err.exec()

    # ── Save ──────────────────────────────────────────────────────────

    def _save_settings(self) -> bool:
        self._ma_data["name"] = self.inp_name.text().strip()
        self._ma_data["accent_color"] = self.inp_accent.text().strip() or "#C8102E"
        self._ma_data["icon_key"] = getattr(self, '_selected_icon_key', None) or self._ma_data.get("icon_key", "generic-martial-art")
        self._ma_data["is_active"] = self._ma_data.get("is_active", True)
        self._ma_data["progression_label_singular"] = self.inp_label_singular.text().strip() or "Nivel"
        self._ma_data["progression_label_plural"] = self.inp_label_plural.text().strip() or "Niveles"
        pm = self._ma_data.get("promotion_mode", "sequential")
        self._ma_data["allow_level_skips"] = (pm == "manual")
        if hasattr(self, 'inp_description'):
            self._ma_data["description"] = self.inp_description.toPlainText().strip() or None
        if hasattr(self, 'inp_training_focus'):
            self._ma_data["training_focus"] = self.inp_training_focus.text().strip() or None

        try:
            self.repo.save_martial_art_settings(self.martial_art_id, self._ma_data)
            if hasattr(self, '_age_table_container') and self._age_table_container.isVisible() and self.chk_age_enabled.isChecked():
                self._save_age_rules()
            self._set_clean()
            self.saved.emit()
            return True
        except Exception as e:
            err = MartialArtConfirmDialog(
                title="Error", message=str(e),
                confirm_text="Cerrar", parent=self,
            )
            err.exec()
            return False

    def _save_age_rules(self):
        belts = self.repo.get_belts(self.martial_art_id)
        rules = []
        for belt in belts:
            lv_id = belt["id"]
            boxes = self._age_spin_boxes.get(lv_id)
            note_edit = self._age_note_edits.get(lv_id)
            min_val = boxes["min"].value() if boxes else 0
            max_val = boxes["max"].value() if boxes else 0
            note = note_edit.text().strip() if note_edit else ""
            rules.append({
                "level_id": lv_id,
                "minimum_age": min_val if min_val > 0 else None,
                "maximum_age": max_val if max_val > 0 else None,
                "age_restriction_note": note or None,
            })
        self.repo.save_level_age_rules(self.martial_art_id, rules)

    # ── Resize ────────────────────────────────────────────────────────

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_modal_overlay') and self._modal_overlay:
            self._modal_overlay.setGeometry(self.rect())
