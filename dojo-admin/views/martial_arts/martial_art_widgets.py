"""Dojo Admin -- Consolidated martial arts widgets.

Combines: promotion_system_widgets, discipline_icon_picker_dialog,
          martial_art_template_dialog, martial_art_instructions_dialog
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QScrollArea, QSizePolicy,
    QDialog, QLineEdit, QPushButton, QGridLayout, QApplication,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QTextEdit, QComboBox,
    QSpinBox, QColorDialog, QMenu, QFileDialog,
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QSignalBlocker, QTimer, QStandardPaths
from PyQt6.QtGui import QColor, QKeyEvent, QIcon, QPixmap, QCursor, QPainter, QPainterPath, QPen

import shutil
import uuid
from pathlib import Path

from views.icon_library import (
    AppIcon, MARTIAL_ART_ICON_LIBRARY, MartialArtIcon, search_icon_library,
    normalize_martial_art_icon, render_icon_pixmap,
)
from views.martial_arts.martial_art_theme import (
    MA_BG, MA_SIDE, MA_CARD, MA_HOVER, MA_INPUT, MA_SURFACE, MA_BORDER, MA_BORDER_HI,
    MA_RED, MA_RED_H, MA_GREEN, MA_YELLOW, MA_BLUE, MA_PURPLE, MA_ORANGE,
    MA_TEXT_PRI, MA_TEXT_SEC, MA_TEXT_MUT, MA_TEXT_DARK,
    MA_MODAL_BG, MA_MODAL_CARD, MA_MODAL_INPUT, MA_MODAL_HEADER, MA_MODAL_BORDER,
    MA_FIELD_QSS, MA_SCROLL_QSS, MA_SCROLLBAR_QSS, MA_SPINBOX_QSS,
    _ma_shadow, _ma_card, _ma_primary_btn, _ma_secondary_btn, _ma_icon_btn,
    _ma_field_label, _ma_section_label, _ma_badge, _ma_scroll, _ma_label,
    valid_hex_color, _HEX_RE,
)

_MA_FF = "font-family: 'Inter', 'Segoe UI', sans-serif;"

_PALETTE_COLORS = [
    "#C8102E", "#2563EB", "#16A34A", "#EAB308", "#9333EA",
    "#EA580C", "#06B6D4", "#F43F5E", "#84CC16", "#0F766E",
    "#71717A", "#FFFFFF", "#000000", "#F97316",
]


class ColorPaletteSelector(QWidget):
    """Compact color selector that opens a native QColorDialog.

    Layout: [swatch 36x36] [HEX 110px] [Elegir color]
    No inline palette circles.
    """

    color_changed = pyqtSignal(str)

    def __init__(self, initial_color: str = "#C8102E", parent=None):
        super().__init__(parent)
        self.setObjectName("ColorPaletteSelector")
        self._color = valid_hex_color(initial_color, "#C8102E")
        self._build_ui()

    def _build_ui(self):
        self.setFixedHeight(44)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        self._preview = QFrame()
        self._preview.setFixedSize(36, 36)
        self._update_preview_style(valid=True)
        row.addWidget(self._preview)

        self._hex_input = QLineEdit()
        self._hex_input.setPlaceholderText("#C8102E")
        self._hex_input.setFixedWidth(110)
        self._hex_input.setStyleSheet(self._input_qss(valid=True))
        self._hex_input.setText(self._color)
        self._hex_input.textChanged.connect(self._on_hex_input)
        row.addWidget(self._hex_input)

        self._pick_btn = QPushButton("Elegir color")
        self._pick_btn.setFixedHeight(36)
        self._pick_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._pick_btn.setStyleSheet(f"""
            QPushButton {{
                background: {MA_CARD}; color: {MA_TEXT_SEC};
                border: 1px solid {MA_BORDER}; border-radius: 8px;
                font-size: 12px; font-weight: 600; {_MA_FF} padding: 0 14px;
            }}
            QPushButton:hover {{
                background: {MA_HOVER}; color: {MA_TEXT_PRI};
                border-color: {MA_BORDER_HI};
            }}
        """)
        self._pick_btn.clicked.connect(self._open_dialog)
        row.addWidget(self._pick_btn)
        row.addStretch()

    def _input_qss(self, valid: bool) -> str:
        border = MA_BORDER if valid else "#EF4444"
        return f"""
            QLineEdit {{
                background: {MA_MODAL_INPUT}; color: {MA_TEXT_PRI};
                border: 1.5px solid {border}; border-radius: 8px;
                padding: 0 12px; font-size: 13px; {_MA_FF} min-height: 38px;
            }}
            QLineEdit:focus {{ border-color: {MA_BLUE}; }}
        """

    def _update_preview_style(self, valid: bool = True):
        border = MA_TEXT_PRI if valid else "#EF4444"
        self._preview.setStyleSheet(
            f"background: {self._color}; border-radius: 18px;"
            f" border: 2px solid {border};"
        )

    def _open_dialog(self):
        initial = QColor(self._color)
        dialog = QColorDialog(initial, self.window())
        dialog.setWindowTitle("Seleccionar color")
        dialog.setOption(
            QColorDialog.ColorDialogOption.DontUseNativeDialog, True,
        )
        dialog.setOption(
            QColorDialog.ColorDialogOption.ShowAlphaChannel, False,
        )
        dialog.setStyleSheet(f"""
            QColorDialog {{
                background-color: {MA_MODAL_INPUT};
                color: #F4F4F5;
            }}
            QColorDialog QLabel {{
                color: #E4E4E7; background: transparent; border: none;
            }}
            QColorDialog QLineEdit, QColorDialog QSpinBox {{
                background-color: #292929; color: #FFFFFF;
                border: 1px solid #3A3A3A; border-radius: 5px;
                min-height: 28px; padding: 0 6px;
            }}
            QColorDialog QPushButton {{
                background-color: #303030; color: #F4F4F5;
                border: 1px solid #444444; border-radius: 6px;
                min-height: 30px; padding: 0 14px;
            }}
            QColorDialog QPushButton:hover {{
                background-color: #3A3A3A; border-color: #5A5A5A;
            }}
            QColorDialog QPushButton:default {{
                background-color: #C8102E; border-color: #E8152F;
                color: #FFFFFF;
            }}
        """)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            selected = dialog.selectedColor()
            if selected.isValid():
                self.set_color(selected.name().upper())

    def _on_hex_input(self, text: str):
        candidate = text.strip().upper()
        if len(candidate) == 7 and candidate.startswith("#") and _HEX_RE.match(candidate):
            self._color = candidate
            self._hex_input.setStyleSheet(self._input_qss(valid=True))
            self._update_preview_style(valid=True)
            self.color_changed.emit(candidate)
        else:
            self._hex_input.setStyleSheet(self._input_qss(valid=False))

    def color(self) -> str:
        return self._color

    def set_color(self, c: str):
        c = valid_hex_color(c, self._color)
        self._color = c
        with QSignalBlocker(self._hex_input):
            self._hex_input.setText(c)
        self._hex_input.setStyleSheet(self._input_qss(valid=True))
        self._update_preview_style(valid=True)
        self.color_changed.emit(c)


def _is_dark_color(color: QColor) -> bool:
    luminance = (
        0.2126 * color.redF()
        + 0.7152 * color.greenF()
        + 0.0722 * color.blueF()
    )
    return luminance < 0.18


class ShirtLevelPreview(QWidget):
    def __init__(
        self,
        color: str = "#FFFFFF",
        width: int = 110,
        height: int = 90,
        outline_color: str = "#050505",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("ShirtLevelPreview")
        self._color = valid_hex_color(color, "#FFFFFF")
        self._outline_color = valid_hex_color(outline_color, "#050505")
        self.setFixedSize(width, height)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

    def set_color(self, color: str) -> None:
        self._color = valid_hex_color(color, self._color)
        self.update()

    def color(self) -> str:
        return self._color

    def set_outline_color(self, color: str) -> None:
        self._outline_color = valid_hex_color(color, self._outline_color)
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(self.width(), self.height())

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        available_width = self.width()
        available_height = self.height()
        scale = min(available_width / 400.0, available_height / 400.0)
        offset_x = (available_width - 400.0 * scale) / 2.0
        offset_y = (available_height - 400.0 * scale) / 2.0

        painter.translate(offset_x, offset_y)
        painter.scale(scale, scale)

        shirt_color = QColor(self._color)
        outline_color = QColor(self._outline_color)

        shirt_path = QPainterPath()
        shirt_path.moveTo(165, 48)
        shirt_path.cubicTo(145, 44, 125, 44, 120, 42)
        shirt_path.cubicTo(90, 44, 70, 58, 62, 66)
        shirt_path.cubicTo(40, 90, 38, 114, 38, 120)
        shirt_path.cubicTo(32, 160, 32, 190, 30, 200)
        shirt_path.cubicTo(46, 210, 74, 222, 96, 222)
        shirt_path.cubicTo(90, 260, 92, 300, 96, 340)
        shirt_path.cubicTo(145, 360, 175, 372, 200, 374)
        shirt_path.cubicTo(225, 372, 255, 360, 304, 340)
        shirt_path.cubicTo(308, 300, 310, 260, 304, 222)
        shirt_path.cubicTo(326, 218, 354, 206, 370, 200)
        shirt_path.cubicTo(362, 190, 362, 160, 362, 120)
        shirt_path.cubicTo(352, 92, 330, 70, 280, 42)
        shirt_path.cubicTo(260, 44, 235, 48, 235, 48)
        shirt_path.lineTo(165, 48)
        shirt_path.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(shirt_color)
        painter.drawPath(shirt_path)

        if _is_dark_color(shirt_color):
            halo_pen = QPen(QColor("#4A4A4A"), 15, Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(halo_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(shirt_path)

        pen = QPen(outline_color, 13, Qt.PenStyle.SolidLine,
                   Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(shirt_path)

        collar = QPainterPath()
        collar.moveTo(155, 56)
        collar.cubicTo(170, 42, 230, 42, 245, 56)
        collar.cubicTo(245, 70, 235, 86, 200, 92)
        collar.cubicTo(165, 86, 155, 70, 155, 56)
        collar.closeSubpath()

        collar_pen = QPen(outline_color, 14, Qt.PenStyle.SolidLine,
                          Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(collar_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(collar)

        sleeve_line = QPainterPath()
        sleeve_line.moveTo(82, 125)
        sleeve_line.cubicTo(84, 135, 90, 150, 96, 160)
        sleeve_line.cubicTo(96, 180, 94, 205, 96, 220)
        painter.setPen(QPen(outline_color, 12, Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.drawPath(sleeve_line)

        sleeve_line2 = QPainterPath()
        sleeve_line2.moveTo(318, 125)
        sleeve_line2.cubicTo(316, 135, 310, 150, 304, 160)
        sleeve_line2.cubicTo(304, 180, 306, 205, 304, 220)
        painter.drawPath(sleeve_line2)


def create_progression_level_preview(
    level: dict,
    progression_system: str,
    *,
    width: int = 110,
    height: int = 90,
    belt_width: int | None = None,
    belt_height: int = 24,
    martial_art_name: str = "",
    parent=None,
) -> QWidget:
    level_type = str(level.get("level_type") or "").strip().lower()
    system_type = str(progression_system or "").strip().lower()
    is_shirt = level_type == "shirt" or system_type == "shirt"
    if is_shirt:
        return ShirtLevelPreview(
            color=level.get("color") or "#FFFFFF",
            width=width,
            height=height,
            parent=parent,
        )
    from views.belts_view import PremiumBeltBar
    resolved_belt_width = belt_width if belt_width is not None else width
    resolved_belt_height = max(
        18,
        min(int(belt_height), 30),
    )
    return PremiumBeltBar(
        color=level.get("color") or "#FFFFFF",
        pre_color=level.get("pre_color"),
        grades=level.get("grades") or 0,
        grade_color=level.get("grade_color") or "#FFFFFF",
        martial_art_name=martial_art_name,
        width=resolved_belt_width,
        height=resolved_belt_height,
        parent=parent,
    )


class IconTextButton(QPushButton):
    def __init__(self, icon_key: str = "", text: str = "",
                 icon_size: int = 17, icon_color: str = "#FFFFFF",
                 height: int = 40, variant: str = "primary",
                 parent=None):
        super().__init__(text, parent)
        self.setObjectName("IconTextButton")
        self.setFixedHeight(height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("variant", variant)

        if icon_key:
            from views.icon_library import render_icon_pixmap
            pixmap = render_icon_pixmap(icon_key, icon_size, icon_color)
            self.setIcon(QIcon(pixmap))
            self.setIconSize(QSize(icon_size, icon_size))

        text_width = self.fontMetrics().horizontalAdvance(text)
        self.setMinimumWidth(text_width + icon_size + 52)

        if variant == "primary":
            self.setStyleSheet(f"""
                QPushButton#IconTextButton {{
                    background: {MA_RED}; color: #FFFFFF; border: none;
                    border-radius: 10px; font-size: 12px; font-weight: 700;
                    padding: 0 16px; {_MA_FF}
                }}
                QPushButton#IconTextButton:hover {{ background: #E8152F; }}
                QPushButton#IconTextButton:disabled {{
                    background: #2A2A2A; color: #555555;
                }}
            """)
        elif variant == "danger":
            self.setStyleSheet(f"""
                QPushButton#IconTextButton {{
                    background: rgba(200,16,46,0.1); color: {MA_RED};
                    border: 1px solid rgba(200,16,46,0.3); border-radius: 10px;
                    font-size: 12px; font-weight: 700; padding: 0 16px; {_MA_FF}
                }}
                QPushButton#IconTextButton:hover {{ background: rgba(200,16,46,0.2); border-color: {MA_RED}; }}
                QPushButton#IconTextButton:disabled {{ color: #555; border-color: #1F1F1F; background: transparent; }}
            """)
        elif variant == "blue":
            self.setStyleSheet(f"""
                QPushButton#IconTextButton {{
                    background: #2563EB; color: #FFFFFF; border: none;
                    border-radius: 10px; font-size: 12px; font-weight: 700;
                    padding: 0 16px; {_MA_FF}
                }}
                QPushButton#IconTextButton:hover {{ background: #1D4ED8; }}
                QPushButton#IconTextButton:disabled {{
                    background: #2A2A2A; color: #555555;
                }}
            """)
        elif variant == "warning":
            self.setStyleSheet(f"""
                QPushButton#IconTextButton {{
                    background: rgba(234,179,8,0.10);
                    border: 1px solid rgba(234,179,8,0.30);
                    border-radius: 8px;
                    color: #EAB308;
                    font-size: 11px;
                    font-weight: 800;
                    padding: 0 14px; {_MA_FF}
                }}
                QPushButton#IconTextButton:hover {{
                    background: rgba(234,179,8,0.18);
                    border-color: rgba(234,179,8,0.45);
                }}
                QPushButton#IconTextButton:pressed {{
                    background: rgba(234,179,8,0.24);
                }}
                QPushButton#IconTextButton:disabled {{
                    color: rgba(234,179,8,0.45);
                    border-color: rgba(234,179,8,0.15);
                    background: transparent;
                }}
            """)
        elif variant == "info":
            self.setStyleSheet(f"""
                QPushButton#IconTextButton[variant="info"] {{
                    background: rgba(37,99,235,0.12);
                    border: 1px solid rgba(59,130,246,0.40);
                    border-radius: 8px;
                    color: #60A5FA;
                    font-size: 11px;
                    font-weight: 700;
                    padding: 0 14px; {_MA_FF}
                }}
                QPushButton#IconTextButton[variant="info"]:hover {{
                    background: rgba(37,99,235,0.22);
                    border-color: rgba(59,130,246,0.55);
                    color: #93C5FD;
                }}
                QPushButton#IconTextButton[variant="info"]:pressed {{
                    background: rgba(30,64,175,0.34);
                }}
                QPushButton#IconTextButton[variant="info"]:disabled {{
                    color: rgba(96,165,250,0.45);
                    border-color: rgba(59,130,246,0.15);
                    background: transparent;
                }}
            """)
        elif variant == "info_secondary":
            self.setStyleSheet(f"""
                QPushButton#IconTextButton {{
                    background: rgba(59,130,246,0.10);
                    border: 1px solid rgba(59,130,246,0.35);
                    border-radius: 9px;
                    color: #93C5FD;
                    font-size: 12px;
                    font-weight: 700;
                    padding: 0 16px; {_MA_FF}
                }}
                QPushButton#IconTextButton:hover {{
                    background: rgba(59,130,246,0.18);
                    border-color: rgba(96,165,250,0.65);
                    color: #DBEAFE;
                }}
                QPushButton#IconTextButton:pressed {{
                    background: rgba(59,130,246,0.24);
                }}
                QPushButton#IconTextButton:disabled {{
                    color: rgba(147,197,253,0.45);
                    border-color: rgba(59,130,246,0.15);
                    background: transparent;
                }}
            """)
        elif variant == "ghost":
            self.setStyleSheet(f"""
                QPushButton#IconTextButton {{
                    background: transparent; color: {MA_TEXT_SEC};
                    border: 1px solid {MA_BORDER}; border-radius: 10px;
                    font-size: 12px; font-weight: 600; padding: 0 16px; {_MA_FF}
                }}
                QPushButton#IconTextButton:hover {{ border-color: {MA_BORDER_HI}; color: #FFF; }}
                QPushButton#IconTextButton:disabled {{ color: #555; border-color: #1F1F1F; }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton#IconTextButton {{
                    background: {MA_CARD}; color: {MA_TEXT_SEC};
                    border: 1px solid {MA_BORDER}; border-radius: 10px;
                    font-size: 12px; font-weight: 600; padding: 0 16px; {_MA_FF}
                }}
                QPushButton#IconTextButton:hover {{ background: {MA_HOVER}; color: {MA_TEXT_PRI}; border-color: {MA_RED}; }}
                QPushButton#IconTextButton:disabled {{ color: #555; border-color: #1F1F1F; }}
            """)


class BeltFormSection(QFrame):
    """Card wrapper for a single belt form section.

    Provides a #1A1A1A surface with a 1px #303030 border, 12px radius
    and an uppercase section title (QLabel#BeltFormSectionTitle).
    """

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("BeltFormSection")
        self.setStyleSheet(f"""
            QFrame#BeltFormSection {{
                background: {MA_MODAL_CARD};
                border: 1px solid {MA_MODAL_BORDER};
                border-radius: 12px;
            }}
        """)
        self.vl = QVBoxLayout(self)
        self.vl.setContentsMargins(14, 12, 14, 12)
        self.vl.setSpacing(10)
        if title:
            self.set_title(title)

    def set_title(self, title: str):
        lbl = QLabel(title)
        lbl.setObjectName("BeltFormSectionTitle")
        lbl.setStyleSheet(f"""
            QLabel#BeltFormSectionTitle {{
                color: #A1A1AA;
                background: transparent;
                border: none;
                padding: 0;
                font-size: 10px;
                font-weight: 800;
                letter-spacing: 0.8px;
                {_MA_FF}
            }}
        """)
        self.vl.addWidget(lbl)

    def add_child(self, widget: QWidget):
        self.vl.addWidget(widget)

    def add_layout(self, layout):
        self.vl.addLayout(layout)


class LevelStateButton(QPushButton):
    """Fixed-geometry checkable state button (Inicial/Final/Activo).

    Same size, border, radius, padding and font in every state; the
    checked color depends on the role.
    """

    _CHECKED_QSS = {
        "initial": ("rgba(37,99,235,0.16)", "#60A5FA", "rgba(59,130,246,0.60)"),
        "final": ("rgba(234,179,8,0.14)", "#FACC15", "rgba(234,179,8,0.54)"),
        "active": ("rgba(34,197,94,0.14)", "#4ADE80", "rgba(34,197,94,0.56)"),
    }

    def __init__(self, text: str, role: str = "active", tooltip: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("LevelStateButton")
        self._role = role if role in self._CHECKED_QSS else "active"
        self.setCheckable(True)
        self.setFixedHeight(40)
        self.setMinimumWidth(98)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if tooltip:
            self.setToolTip(tooltip)
        self.setProperty("role", self._role)
        self._apply_style()

    def _apply_style(self):
        bg, color, border = self._CHECKED_QSS[self._role]
        self.setStyleSheet(f"""
            QPushButton#LevelStateButton {{
                background: #202020; color: #A1A1AA;
                border: 1px solid #343434; border-radius: 9px;
                font-size: 11px; font-weight: 700;
                padding: 0 12px; {_MA_FF}
            }}
            QPushButton#LevelStateButton:hover {{
                background: #252525; color: #E4E4E7;
                border-color: #484848;
            }}
            QPushButton#LevelStateButton:checked {{
                background: {bg}; color: {color};
                border-color: {border};
            }}
            QPushButton#LevelStateButton:checked:hover {{
                background: {bg};
            }}
            QPushButton#LevelStateButton:disabled {{
                color: #555; border-color: #1F1F1F;
            }}
        """)


# ═══════════════════════════════════════════════════════════════
#  1. Promotion system widgets (from promotion_system_widgets.py)
# ═══════════════════════════════════════════════════════════════


class ExistingLevelRow(QFrame):
    edit_requested = pyqtSignal(dict)
    delete_requested = pyqtSignal(dict)

    def __init__(self, belt: dict, index: int, martial_art_name: str = "",
                 is_proposed: bool = False, is_duplicate: bool = False,
                 belt_preview_factory=None, parent=None):
        super().__init__(parent)
        self.belt = belt
        self.setObjectName("ExistingLevelRow")
        self.setFixedHeight(74)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Doble clic o clic derecho para editar o eliminar.")
        self._is_proposed = is_proposed
        self._is_duplicate = is_duplicate
        self._belt_preview_factory = belt_preview_factory
        self._apply_base_style()
        self._build_ui(index)

    def _state_border(self):
        if self._is_duplicate:
            return MA_RED
        if self._is_proposed:
            return "#4B5563"
        return "transparent"

    def _apply_base_style(self):
        self.setStyleSheet(f"""
            QFrame#ExistingLevelRow {{
                background: transparent;
                border: 1px solid {self._state_border()};
                border-radius: 10px;
            }}
        """)

    def enterEvent(self, event):
        self.setStyleSheet(f"""
            QFrame#ExistingLevelRow {{
                background: #202020;
                border: 1px solid {MA_RED if self._is_duplicate else "#383838"};
                border-radius: 10px;
            }}
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._apply_base_style()
        super().leaveEvent(event)

    def _build_ui(self, index: int):
        hl = QHBoxLayout(self)
        hl.setContentsMargins(14, 9, 14, 9)
        hl.setSpacing(12)

        self._index_label = QLabel(f"{index:02d}")
        self._index_label.setObjectName("ExistingLevelIndex")
        self._index_label.setFixedSize(44, 44)
        self._index_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._index_label.setStyleSheet(f"""
            QLabel#ExistingLevelIndex {{
                background: #202020; color: #A1A1AA;
                border: 1px solid #303030; border-radius: 11px;
                font-size: 12px; font-weight: 800;
                {_MA_FF}
            }}
        """)
        hl.addWidget(self._index_label)

        if self._belt_preview_factory:
            preview = self._belt_preview_factory(self.belt)
            preview.setFixedSize(170, 28)
        else:
            preview = QFrame()
            preview.setFixedSize(170, 28)
            belt_color = self.belt.get("color", "#888888")
            light_belts = {
                "#FFFFFF", "#FFD700", "#FF8C00", "#FFFF00", "#FFA500", "#FFFACD",
            }
            border_c = "#999" if belt_color.upper() in light_belts else belt_color
            preview.setStyleSheet(f"""
                QFrame {{
                    background: {belt_color};
                    border-radius: 3px;
                    border: 1.5px solid {border_c};
                }}
            """)
        hl.addWidget(preview)

        name = QLabel(self.belt.get("name", ""))
        name.setStyleSheet(f"""
            color: {MA_TEXT_PRI}; font-size: 13px; font-weight: 600;
            background: transparent; border: none;
            {_MA_FF}
        """)
        hl.addWidget(name, 1)

        grades = self.belt.get("grades", 0)
        if grades:
            grades_lbl = QLabel(f"{grades} grado(s)")
            grades_lbl.setStyleSheet(f"""
                color: {MA_TEXT_SEC}; font-size: 11px;
                background: transparent; border: none;
                {_MA_FF}
            """)
            hl.addWidget(grades_lbl)

        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(4)

        if self.belt.get("is_initial"):
            badge = QLabel("INICIAL")
            badge.setStyleSheet(f"""
                background: #0F2A1A; color: {MA_GREEN};
                font-size: 9px; font-weight: 700; padding: 2px 6px;
                border-radius: 3px; border: none;
                {_MA_FF}
            """)
            badges_layout.addWidget(badge)

        if self.belt.get("is_final"):
            badge = QLabel("FINAL")
            badge.setStyleSheet(f"""
                background: #2A0A0C; color: {MA_RED};
                font-size: 9px; font-weight: 700; padding: 2px 6px;
                border-radius: 3px; border: none;
                {_MA_FF}
            """)
            badges_layout.addWidget(badge)

        if badges_layout.count():
            badges_w = QWidget()
            badges_w.setStyleSheet("background: transparent; border: none;")
            badges_w.setLayout(badges_layout)
            hl.addWidget(badges_w)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._show_actions_menu(event.globalPosition().toPoint())
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        self._show_actions_menu(event.globalPos())
        event.accept()

    def _show_actions_menu(self, global_pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1D1D1D;
                color: #F4F4F5;
                border: 1px solid #353535;
                border-radius: 8px;
                padding: 4px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 12px;
            }
            QMenu::item {
                min-width: 130px;
                padding: 8px 14px;
                border-radius: 6px;
            }
            QMenu::item:selected { background: #292929; }
        """)
        edit_action = menu.addAction("Editar")
        delete_action = menu.addAction("Eliminar")
        chosen = menu.exec(global_pos)
        if chosen is edit_action:
            self.edit_requested.emit(self.belt)
        elif chosen is delete_action:
            self.delete_requested.emit(self.belt)


class ExistingProgressionPanel(QFrame):
    edit_level_requested = pyqtSignal(dict)
    delete_level_requested = pyqtSignal(dict)

    def __init__(self, martial_art_id: int, repo, editing_level_id=None,
                 martial_art_name="", belt_preview_factory=None, parent=None):
        super().__init__(parent)
        self.martial_art_id = martial_art_id
        self.repo = repo
        self.editing_level_id = editing_level_id
        self.martial_art_name = martial_art_name
        self._belt_preview_factory = belt_preview_factory
        self._proposed_order = None
        self._proposed_name = ""
        self.setObjectName("ExistingProgressionPanel")
        self.setMinimumHeight(300)
        self.setStyleSheet("""
            #ExistingProgressionPanel {
                background: transparent;
                border: none;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        subtitle = QLabel("Consulta la progresión actual antes de guardar.")
        subtitle.setStyleSheet(f"""
            color: {MA_TEXT_MUT}; font-size: 11px; padding: 0 4px 4px 4px;
            background: transparent; border: none;
            {_MA_FF}
        """)
        root.addWidget(subtitle)

        self.container = QWidget()
        self.container.setObjectName("ProgressionPanelContainer")
        self.container.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setContentsMargins(8, 8, 8, 8)
        self.list_layout.setSpacing(4)
        self.list_layout.addStretch()

        scroll = QScrollArea()
        scroll.setObjectName("ProgressionPanelScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(MA_SCROLL_QSS)
        scroll.setWidget(self.container)
        root.addWidget(scroll, 1)

        self.refresh()

    def refresh(self):
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        belts = self.repo.get_belts(self.martial_art_id)
        if not belts:
            empty = QLabel("Este arte todavia no tiene niveles.")
            empty.setStyleSheet(f"""
                color: {MA_TEXT_MUT}; font-size: 12px; font-style: italic;
                padding: 16px; background: transparent; border: none;
                {_MA_FF}
            """)
            self.list_layout.insertWidget(0, empty)
            hint = QLabel("El primer nivel normalmente utiliza el orden 1.")
            hint.setStyleSheet(f"""
                color: {MA_TEXT_MUT}; font-size: 11px; padding: 0 16px 8px 16px;
                background: transparent; border: none;
                {_MA_FF}
            """)
            self.list_layout.insertWidget(1, hint)
            return

        for idx, belt in enumerate(belts, 1):
            is_dup = (
                self._proposed_order is not None
                and belt.get("orden") == self._proposed_order
                and belt.get("id") != self.editing_level_id
            )
            is_prop = (
                self._proposed_name
                and belt.get("name", "").lower() == self._proposed_name.lower()
                and belt.get("id") != self.editing_level_id
            )
            row = ExistingLevelRow(
                belt, idx, is_proposed=is_prop, is_duplicate=is_dup,
                belt_preview_factory=self._belt_preview_factory,
            )
            row.edit_requested.connect(self.edit_level_requested.emit)
            row.delete_requested.connect(self.delete_level_requested.emit)
            self.list_layout.insertWidget(self.list_layout.count() - 1, row)

    def set_proposed_order(self, order):
        self._proposed_order = order
        self.refresh()

    def set_proposed_name(self, name):
        self._proposed_name = name or ""
        self.refresh()


# ═══════════════════════════════════════════════════════════════
#  2. Icon picker (from discipline_icon_picker_dialog.py)
# ═══════════════════════════════════════════════════════════════

_CELL_W = 110
_CELL_H = 90
_COLS = 4
_ICON_SIZE = 28


class _IconCell(QFrame):
    """Single icon cell inside the grid."""

    def __init__(self, entry: dict[str, str], is_selected: bool, parent=None):
        super().__init__(parent)
        self._key = entry["key"]
        self.setFixedSize(_CELL_W, _CELL_H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style(is_selected)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 8, 6, 6)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.addStretch()

        self._check = QLabel("\u2713")
        self._check.setStyleSheet(
            f"color: {MA_RED}; font-size: 12px; font-weight: 700; {_MA_FF}"
            " background: transparent; border: none;"
        )
        self._check.setVisible(is_selected)
        top_row.addWidget(self._check)

        layout.addLayout(top_row)

        icon_widget = MartialArtIcon(entry["key"], size=_ICON_SIZE, color=MA_TEXT_PRI)
        icon_widget.setStyleSheet("background: transparent;")
        layout.addWidget(icon_widget, 0, Qt.AlignmentFlag.AlignHCenter)

        label = QLabel(entry.get("label", ""))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet(
            f"color: {MA_TEXT_PRI}; font-size: 11px; font-weight: 600; {_MA_FF}"
            " background: transparent; border: none;"
        )
        layout.addWidget(label)

        cat = QLabel(entry.get("category", ""))
        cat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cat.setStyleSheet(
            f"color: {MA_TEXT_MUT}; font-size: 10px; {_MA_FF}"
            " background: transparent; border: none;"
        )
        layout.addWidget(cat)

    @property
    def icon_key(self) -> str:
        return self._key

    def set_selected(self, selected: bool) -> None:
        self._check.setVisible(selected)
        self._update_style(selected)

    def _update_style(self, selected: bool) -> None:
        if selected:
            border_color = MA_RED
            bg = "#2A0A0C"
        else:
            border_color = MA_BORDER
            bg = "transparent"
        self.setStyleSheet(f"""
            QFrame {{
                border: 1.5px solid {border_color};
                background: {bg};
                border-radius: 10px;
            }}
            QFrame * {{ background: transparent; border: none; }}
        """)

    def enterEvent(self, event):
        if self._key != "":
            self.setStyleSheet(f"""
                QFrame {{
                    border: 1px solid {MA_BORDER_HI};
                    background: {MA_HOVER};
                    border-radius: 10px;
                }}
                QFrame * {{ background: transparent; border: none; }}
            """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._update_style(self._check.isVisible())
        super().leaveEvent(event)


class DisciplineIconPickerDialog(QDialog):
    """Modal dialog for picking a martial arts discipline icon."""

    def __init__(self, current_key: str = "generic-martial-art", parent=None):
        super().__init__(parent)
        self._selected_key = normalize_martial_art_icon(current_key)
        self._active_category: str | None = None
        self._cells: list[_IconCell] = []
        self._category_buttons: dict[str, QPushButton] = {}

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Dialog
        )
        self.setFixedSize(900, 650)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setStyleSheet(f"background: {MA_SIDE};")

        self._build_ui()
        self._refresh_grid()

    def selected_key(self) -> str:
        return self._selected_key

    # ── UI construction ────────────────────────────────────────────────

    def _build_ui(self):
        shell = QFrame(self)
        shell.setObjectName("IconPickerShell")
        shell.setGeometry(0, 0, 900, 650)
        shell.setStyleSheet(f"""
            QFrame#IconPickerShell {{
                background: {MA_CARD};
                border: 1px solid {MA_BORDER};
                border-radius: 16px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(shell)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 180))
        shell.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(shell)
        card_layout.setContentsMargins(24, 24, 24, 20)
        card_layout.setSpacing(16)

        title = QLabel("Seleccionar icono de disciplina")
        title.setStyleSheet(
            f"color: {MA_TEXT_PRI}; font-size: 18px; font-weight: 700; {_MA_FF}"
        )
        card_layout.addWidget(title)

        self._search = QLineEdit()
        self._search.setPlaceholderText(
            "Buscar por nombre, categoria o palabra clave..."
        )
        self._search.setFixedHeight(38)
        self._search.setStyleSheet(f"""
            QLineEdit {{
                background: {MA_INPUT}; color: {MA_TEXT_PRI};
                border: 1.5px solid {MA_BORDER}; border-radius: 8px;
                padding: 0 12px; font-size: 13px; {_MA_FF}
            }}
            QLineEdit:focus {{ border-color: {MA_RED}; }}
            QLineEdit:hover {{ border-color: {MA_BORDER_HI}; }}
        """)
        self._search.textChanged.connect(self._on_search)
        card_layout.addWidget(self._search)

        self._build_category_tabs(card_layout)

        self._grid_scroll = QScrollArea()
        self._grid_scroll.setWidgetResizable(True)
        self._grid_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._grid_scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: transparent; }}
            QScrollArea > QWidget > QWidget {{ background: transparent; }}
            QScrollBar:vertical {{
                background: transparent; width: 6px; border: none;
            }}
            QScrollBar::handle:vertical {{
                background: #303030; border-radius: 3px; min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{ background: #454545; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0; border: none; background: transparent;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)
        self._grid_container = QWidget()
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setContentsMargins(4, 4, 4, 4)
        self._grid_layout.setSpacing(8)
        self._grid_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )
        self._grid_scroll.setWidget(self._grid_container)
        card_layout.addWidget(self._grid_scroll, 1)

        self._build_buttons(card_layout)

    def _build_category_tabs(self, parent_layout: QVBoxLayout):
        categories = sorted(
            {e.get("category", "") for e in MARTIAL_ART_ICON_LIBRARY}
        )

        tabs_layout = QHBoxLayout()
        tabs_layout.setSpacing(6)
        tabs_layout.setContentsMargins(0, 0, 0, 0)

        all_btn = QPushButton("Todos")
        all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._category_buttons["Todos"] = all_btn
        self._style_cat_button(all_btn, True)
        all_btn.clicked.connect(lambda: self._set_category(None))
        tabs_layout.addWidget(all_btn)

        for cat in categories:
            if not cat:
                continue
            btn = QPushButton(cat)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._category_buttons[cat] = btn
            self._style_cat_button(btn, False)
            btn.clicked.connect(lambda checked, c=cat: self._set_category(c))
            tabs_layout.addWidget(btn)

        tabs_layout.addStretch()
        parent_layout.addLayout(tabs_layout)

    def _build_buttons(self, parent_layout: QVBoxLayout):
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(12)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: {MA_CARD}; color: {MA_TEXT_SEC};
                border: 1px solid {MA_BORDER}; border-radius: 10px;
                font-size: 13px; font-weight: 600; {_MA_FF} padding: 0 20px;
            }}
            QPushButton:hover {{
                background: {MA_HOVER}; color: {MA_TEXT_PRI};
                border-color: {MA_RED};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        btn_row.addStretch()

        select_btn = QPushButton("Seleccionar")
        select_btn.setFixedHeight(40)
        select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        select_btn.setStyleSheet(f"""
            QPushButton {{
                background: {MA_RED}; color: white; border: none;
                border-radius: 10px;
                font-size: 13px; font-weight: 700; {_MA_FF} padding: 0 24px;
            }}
            QPushButton:hover {{ background: #E8152F; }}
            QPushButton:disabled {{ background: {MA_BORDER}; color: {MA_TEXT_MUT}; }}
        """)
        select_btn.clicked.connect(self._on_select)
        btn_row.addWidget(select_btn)

        parent_layout.addLayout(btn_row)

    # ── Logic ──────────────────────────────────────────────────────────

    def _set_category(self, category: str | None):
        self._active_category = category
        for cat_key, btn in self._category_buttons.items():
            is_active = (cat_key == "Todos" and category is None) or cat_key == category
            self._style_cat_button(btn, is_active)
        self._refresh_grid()

    def _style_cat_button(self, btn: QPushButton, active: bool):
        if active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {MA_RED}; color: white; border: none;
                    border-radius: 8px; font-size: 12px; font-weight: 700;
                    {_MA_FF} padding: 0 14px; min-height: 30px;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {MA_TEXT_SEC};
                    border: 1px solid {MA_BORDER}; border-radius: 8px;
                    font-size: 12px; font-weight: 600;
                    {_MA_FF} padding: 0 14px; min-height: 30px;
                }}
                QPushButton:hover {{
                    background: {MA_HOVER}; color: {MA_TEXT_PRI};
                    border-color: {MA_BORDER_HI};
                }}
            """)

    def _on_search(self, text: str):
        self._refresh_grid()

    def _refresh_grid(self):
        query = self._search.text().strip()
        results = search_icon_library(query, MARTIAL_ART_ICON_LIBRARY)

        if self._active_category:
            results = [
                e for e in results
                if e.get("category", "") == self._active_category
            ]

        for cell in self._cells:
            cell.setParent(None)
            cell.deleteLater()
        self._cells.clear()

        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, entry in enumerate(results):
            row = i // _COLS
            col = i % _COLS
            is_sel = entry["key"] == self._selected_key
            cell = _IconCell(entry, is_sel)
            cell.mousePressEvent = lambda ev, k=entry["key"]: self._on_cell_click(k)
            self._grid_layout.addWidget(cell, row, col)
            self._cells.append(cell)

    def _on_cell_click(self, key: str):
        self._selected_key = key
        for cell in self._cells:
            cell.set_selected(cell.icon_key == key)

    def _on_select(self):
        self.accept()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


# ═══════════════════════════════════════════════════════════════
#  3. Template dialogs (from martial_art_template_dialog.py)
# ═══════════════════════════════════════════════════════════════

CARD_QSS = f"""
    QFrame#dialogCard {{
        background: {MA_CARD};
        border: 1px solid {MA_BORDER};
        border-radius: 20px;
    }}
"""

OVERLAY_QSS = "background: rgba(0,0,0,140);"

CLOSE_BTN_QSS = f"""
    QPushButton {{
        background: transparent; color: {MA_TEXT_MUT};
        border: none; border-radius: 6px;
        font-size: 13px; font-weight: 700;
        {_MA_FF}
    }}
    QPushButton:hover {{ color: {MA_TEXT_PRI}; background: #2A2A2A; }}
"""

CHIP_QSS = f"""
    QPushButton {{
        background: #1A1A1A; color: {MA_TEXT_SEC};
        border: 1px solid {MA_BORDER}; border-radius: 12px;
        padding: 5px 14px; font-size: 11px; font-weight: 600;
        {_MA_FF}
    }}
    QPushButton:hover {{
        border-color: {MA_BLUE}; color: {MA_TEXT_PRI}; background: {MA_HOVER};
    }}
"""

CHIP_ACTIVE_QSS = f"""
    QPushButton {{
        background: #0C1A4E; color: {MA_BLUE};
        border: 1px solid {MA_BLUE}; border-radius: 12px;
        padding: 5px 14px; font-size: 11px; font-weight: 600;
        {_MA_FF}
    }}
"""


class MartialArtConfirmDialog(QDialog):
    def __init__(
        self,
        title: str,
        message: str,
        detail_text: str = "",
        confirm_text: str = "Confirmar",
        cancel_text: str = "Cancelar",
        is_danger: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("MartialArtConfirmDialog")
        self.setWindowTitle("")
        self.setFixedSize(440, 280)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._drag_pos = None
        self._is_danger = is_danger
        self.setStyleSheet(f"background: {MA_SIDE};")

        shell = QFrame(self)
        shell.setObjectName("ConfirmShell")
        shell.setGeometry(0, 0, 440, 280)
        shell.setStyleSheet(f"""
            QFrame#ConfirmShell {{
                background: {MA_CARD};
                border: 1px solid {MA_BORDER};
                border-radius: 16px;
            }}
        """)
        _ma_shadow(shell, blur=40, offset_y=12, alpha=200)

        card_layout = QVBoxLayout(shell)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(0)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(0)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"color: {MA_TEXT_PRI}; font-size: 16px; font-weight: 700; "
            f"background: transparent; border: none; {_MA_FF}"
        )
        header_row.addWidget(title_lbl)
        header_row.addStretch()

        close_btn = QPushButton("\u2715")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(CLOSE_BTN_QSS)
        close_btn.clicked.connect(self.reject)
        header_row.addWidget(close_btn)
        card_layout.addLayout(header_row)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {MA_BORDER}; border: none;")
        card_layout.addWidget(sep)

        card_layout.addSpacing(8)

        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(
            f"color: {MA_TEXT_PRI}; font-size: 14px; font-weight: 600; "
            f"background: transparent; border: none; {_MA_FF}"
        )
        card_layout.addWidget(msg_lbl)

        if detail_text:
            card_layout.addSpacing(4)
            detail_lbl = QLabel(detail_text)
            detail_lbl.setWordWrap(True)
            detail_lbl.setStyleSheet(
                f"color: {MA_TEXT_SEC}; font-size: 12px; "
                f"background: transparent; border: none; {_MA_FF}"
            )
            card_layout.addWidget(detail_lbl)

        card_layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(12)

        btn_cancel = _ma_secondary_btn(cancel_text, height=38)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_confirm = _ma_primary_btn(
            confirm_text,
            color=MA_RED if is_danger else MA_GREEN,
            height=38,
        )
        btn_confirm.clicked.connect(self.accept)
        btn_row.addWidget(btn_confirm)

        card_layout.addLayout(btn_row)

    def exec(self) -> QDialog.DialogCode:
        return super().exec()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)



SUGGESTED_TYPES = [
    "Tiempo", "Tecnico", "Fisico", "Conducta",
    "Asistencia", "Documentacion",
]


class RequirementTypeDialog(QDialog):
    type_created = pyqtSignal(str, int)

    def __init__(self, repo, parent=None):
        super().__init__(parent)
        self.setObjectName("RequirementTypeDialog")
        self.repo = repo
        self.setWindowTitle("Crear Tipo de Requisito")
        self.setFixedSize(560, 430)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._drag_pos = None
        self.setStyleSheet(f"background: {MA_SIDE};")

        self._build_ui()

    def _build_ui(self):
        shell = QFrame(self)
        shell.setObjectName("ReqTypeShell")
        shell.setGeometry(0, 0, 560, 430)
        shell.setStyleSheet(f"""
            QFrame#ReqTypeShell {{
                background: {MA_CARD};
                border: 1px solid {MA_BORDER};
                border-radius: 16px;
            }}
        """)
        _ma_shadow(shell, blur=40, offset_y=12, alpha=200)

        card_layout = QVBoxLayout(shell)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(14)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(0)

        title = QLabel("Crear Tipo de Requisito")
        title.setStyleSheet(
            f"color: {MA_TEXT_PRI}; font-size: 16px; font-weight: 700; "
            f"background: transparent; border: none; {_MA_FF}"
        )
        header_row.addWidget(title)
        header_row.addStretch()

        close_btn = QPushButton("\u2715")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(CLOSE_BTN_QSS)
        close_btn.clicked.connect(self.reject)
        header_row.addWidget(close_btn)
        card_layout.addLayout(header_row)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {MA_BORDER}; border: none;")
        card_layout.addWidget(sep)

        card_layout.addWidget(_ma_field_label("NOMBRE DEL TIPO"))

        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Ej: Tecnico, Fisico, Tiempo...")
        self.inp_name.setStyleSheet(MA_FIELD_QSS)
        self.inp_name.returnPressed.connect(self._save)
        card_layout.addWidget(self.inp_name)

        card_layout.addWidget(_ma_field_label("SUGERIDOS (click para usar)"))

        chips_wrap = QWidget()
        chips_wrap.setStyleSheet("background: transparent;")
        chips_layout = QHBoxLayout(chips_wrap)
        chips_layout.setContentsMargins(0, 0, 0, 0)
        chips_layout.setSpacing(8)

        self._chips = []
        for tname in SUGGESTED_TYPES:
            chip = QPushButton(tname)
            chip.setCursor(Qt.CursorShape.PointingHandCursor)
            chip.setStyleSheet(CHIP_QSS)
            chip.clicked.connect(lambda checked, n=tname, c=chip: self._pick_chip(n, c))
            chips_layout.addWidget(chip)
            self._chips.append((tname, chip))
        chips_layout.addStretch()
        card_layout.addWidget(chips_wrap)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(
            f"color: {MA_RED}; font-size: 11px; "
            f"background: transparent; border: none; {_MA_FF}"
        )
        card_layout.addWidget(self.lbl_error)

        card_layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(12)

        btn_cancel = _ma_secondary_btn("Cancelar", height=38)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_save = _ma_primary_btn("Crear tipo", color=MA_RED, height=38)
        btn_save.clicked.connect(self._save)
        btn_row.addWidget(btn_save)

        card_layout.addLayout(btn_row)

    def _pick_chip(self, name: str, clicked_chip: QPushButton):
        self.inp_name.setText(name)
        for chip_name, chip_btn in self._chips:
            if chip_btn is clicked_chip:
                chip_btn.setStyleSheet(CHIP_ACTIVE_QSS)
            else:
                chip_btn.setStyleSheet(CHIP_QSS)

    def _save(self):
        name = self.inp_name.text().strip()
        if not name:
            self.lbl_error.setText("El nombre es obligatorio.")
            return
        try:
            new_id = self.repo.create_requirement_type(name)
            self.type_created.emit(name, new_id)
            self.accept()
        except Exception as e:
            self.lbl_error.setText(f"Error: {e}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


_SYSTEM_LABELS = {
    "belt": "Cinturones",
    "sash": "Fajas",
    "shirt": "Camisas",
    "bracelet": "Brazaletes",
    "level": "Niveles",
    "grade": "Grados",
    "custom": "Personalizado",
    "none": "Sin progresion",
}


class TemplatePreviewDialog(QDialog):
    def __init__(self, template: dict, levels: list, parent=None):
        super().__init__(parent)
        self.setObjectName("TemplatePreviewDialog")
        self.template = template
        self.levels = levels
        self.setWindowTitle(f"Vista previa: {template.get('name', '')}")
        self.setFixedSize(520, 600)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._drag_pos = None
        self.setStyleSheet(f"background: {MA_SIDE};")

        self._build_ui()

    def _build_ui(self):
        shell = QFrame(self)
        shell.setObjectName("TemplateShell")
        shell.setGeometry(0, 0, 520, 600)
        shell.setStyleSheet(f"""
            QFrame#TemplateShell {{
                background: {MA_CARD};
                border: 1px solid {MA_BORDER};
                border-radius: 16px;
            }}
        """)
        _ma_shadow(shell, blur=40, offset_y=12, alpha=200)

        card_layout = QVBoxLayout(shell)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(12)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(10)

        icon_key = self.template.get("icon_key", "generic-martial-art")
        icon = MartialArtIcon(icon_key, size=28, color=MA_RED)
        header_row.addWidget(icon)

        title = QLabel(self.template.get("name", "Plantilla"))
        title.setStyleSheet(
            f"color: {MA_TEXT_PRI}; font-size: 16px; font-weight: 700; "
            f"background: transparent; border: none; {_MA_FF}"
        )
        header_row.addWidget(title)
        header_row.addStretch()

        close_btn = QPushButton("\u2715")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(CLOSE_BTN_QSS)
        close_btn.clicked.connect(self.reject)
        header_row.addWidget(close_btn)
        card_layout.addLayout(header_row)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {MA_BORDER}; border: none;")
        card_layout.addWidget(sep)

        system_type = self.template.get("system_type", "belt")
        system_label = _SYSTEM_LABELS.get(system_type, system_type)
        sys_lbl = _ma_label(f"Sistema: {system_label}")
        card_layout.addWidget(sys_lbl)

        desc = self.template.get("description", "")
        if desc:
            desc_lbl = QLabel(desc)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(
                f"color: {MA_TEXT_MUT}; font-size: 12px; "
                f"background: transparent; border: none; {_MA_FF}"
            )
            card_layout.addWidget(desc_lbl)

        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background: {MA_BORDER}; border: none;")
        card_layout.addWidget(sep2)

        origin_label = "Integrada" if self.template.get("is_builtin") else "Personalizada"
        origin_lbl = _ma_label(f"Origen: {origin_label}")
        card_layout.addWidget(origin_lbl)

        count_lbl = _ma_label(f"{len(self.levels)} nivel(es)")
        card_layout.addWidget(count_lbl)

        list_container = QWidget()
        list_container.setStyleSheet("background: transparent;")
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(4)

        for idx, lvl in enumerate(self.levels, 1):
            row = QFrame()
            row.setMinimumHeight(50)
            row.setStyleSheet(f"""
                QFrame {{
                    background: transparent;
                    border: 1px solid transparent;
                    border-radius: 6px;
                }}
            """)
            row_hl = QHBoxLayout(row)
            row_hl.setContentsMargins(8, 4, 8, 4)
            row_hl.setSpacing(8)

            marker = QLabel(str(idx).zfill(2))
            marker.setFixedSize(24, 24)
            marker.setAlignment(Qt.AlignmentFlag.AlignCenter)
            marker.setStyleSheet(f"""
                background: #2A2A2A; color: {MA_TEXT_SEC};
                border-radius: 12px; font-size: 10px; font-weight: 700;
                border: 1px solid #333; {_MA_FF}
            """)
            row_hl.addWidget(marker)

            preview = create_progression_level_preview(
                lvl,
                self.template.get("system_type", "belt"),
                width=48,
                height=24,
                parent=self,
            )
            row_hl.addWidget(preview)

            name_col = QVBoxLayout()
            name_col.setSpacing(1)
            name_lbl = QLabel(lvl.get("name", ""))
            name_lbl.setStyleSheet(
                f"color: {MA_TEXT_PRI}; font-size: 13px; "
                f"background: transparent; border: none; {_MA_FF}"
            )
            name_col.addWidget(name_lbl)

            tags = []
            if lvl.get("is_initial"):
                tags.append("Inicial")
            if lvl.get("is_final"):
                tags.append("Final")
            grades = lvl.get("grades", 0) or 0
            if grades:
                tags.append(f"{grades} grado(s)")
            sub_lbl = QLabel(" \u00b7 ".join(tags))
            sub_lbl.setStyleSheet(
                f"color: {MA_TEXT_MUT}; font-size: 10px; "
                f"background: transparent; border: none; {_MA_FF}"
            )
            name_col.addWidget(sub_lbl)
            row_hl.addLayout(name_col, 1)

            grade_color = lvl.get("grade_color")
            if grades and valid_hex_color(grade_color, None):
                gbar = QWidget()
                gbar.setFixedSize(48, 10)
                glay = QHBoxLayout(gbar)
                glay.setContentsMargins(0, 0, 0, 0)
                glay.setSpacing(1)
                segments = min(max(int(grades), 1), 4)
                for _ in range(segments):
                    seg = QFrame()
                    seg.setStyleSheet(
                        f"background: {grade_color}; border-radius: 1px; border: none;"
                    )
                    glay.addWidget(seg, 1)
                row_hl.addWidget(gbar)

            list_layout.addWidget(row)

        list_layout.addStretch()

        if len(self.levels) >= 2:
            first_name = self.levels[0].get("name", "")
            last_name = self.levels[-1].get("name", "")
            range_lbl = _ma_label(
                f"Primer nivel: {first_name} \u00b7 Ultimo nivel: {last_name}"
            )
            card_layout.addWidget(range_lbl)

        scroll = _ma_scroll(list_container)
        card_layout.addWidget(scroll, 1)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_close = _ma_secondary_btn("Cerrar", height=36)
        btn_close.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        btn_row.addStretch()
        card_layout.addLayout(btn_row)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


# ═══════════════════════════════════════════════════════════════
#  4. Instructions dialog (from martial_art_instructions_dialog.py)
# ═══════════════════════════════════════════════════════════════


class _Section(QFrame):
    def __init__(self, title, content_blocks, parent=None):
        super().__init__(parent)
        self.setObjectName("InstructionSection")
        self.setStyleSheet(f"""
            QFrame#InstructionSection {{
                background: #0D0D0D;
                border: 1px solid #1E1E1E;
                border-radius: 12px;
            }}
        """)
        vl = QVBoxLayout(self)
        vl.setContentsMargins(20, 16, 20, 16)
        vl.setSpacing(10)

        lbl = QLabel(title)
        lbl.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 14px; font-weight: 800; {_MA_FF} background: transparent; border: none;")
        vl.addWidget(lbl)

        for block in content_blocks:
            if isinstance(block, tuple):
                subtitle, text = block
                s = QLabel(subtitle)
                s.setStyleSheet(f"color: {MA_RED}; font-size: 10px; font-weight: 700; letter-spacing: 0.8px; {_MA_FF} background: transparent; border: none; text-transform: uppercase;")
                vl.addWidget(s)
                t = QLabel(text)
                t.setWordWrap(True)
                t.setStyleSheet(f"color: {MA_TEXT_SEC}; font-size: 12px; font-weight: 500; {_MA_FF} background: transparent; border: none; line-height: 1.5;")
                vl.addWidget(t)
            else:
                t = QLabel(block)
                t.setWordWrap(True)
                t.setStyleSheet(f"color: {MA_TEXT_SEC}; font-size: 12px; font-weight: 500; {_MA_FF} background: transparent; border: none; line-height: 1.5;")
                vl.addWidget(t)


class MartialArtInstructionsDialog(QDialog):
    def __init__(self, parent=None, initial_section=None):
        super().__init__(parent)
        self.setWindowTitle("Instrucciones - Configuracion de disciplinas")
        self.setFixedSize(960, 760)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setStyleSheet(f"background: {MA_MODAL_BG};")
        self._initial_section = initial_section

        shell = QFrame(self)
        shell.setObjectName("InstructionsShell")
        shell.setGeometry(0, 0, 960, 760)
        shell.setStyleSheet(f"""
            QFrame#InstructionsShell {{
                background: {MA_CARD};
                border: 1px solid {MA_BORDER};
                border-radius: 20px;
            }}
        """)
        _ma_shadow(shell, blur=40, offset_y=12, alpha=200)

        card_layout = QVBoxLayout(shell)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        header = QHBoxLayout()
        header.setContentsMargins(24, 16, 24, 12)
        header.setSpacing(12)
        title = QLabel("Instrucciones de configuracion")
        title.setStyleSheet(f"color: {MA_TEXT_PRI}; font-size: 18px; font-weight: 800; {_MA_FF}")
        header.addWidget(title)
        header.addStretch()
        btn_close = QPushButton("\u2715")
        btn_close.setFixedSize(32, 32)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {MA_TEXT_DARK}; border: none; border-radius: 8px; font-size: 14px; }}
            QPushButton:hover {{ color: {MA_TEXT_SEC}; background: {MA_HOVER}; }}
        """)
        btn_close.clicked.connect(self.reject)
        header.addWidget(btn_close)
        card_layout.addLayout(header)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {MA_BORDER};")
        card_layout.addWidget(sep)

        search = QLineEdit()
        search.setPlaceholderText("Buscar en instrucciones...")
        search.setFixedHeight(36)
        search.setStyleSheet(f"""
            QLineEdit {{
                background: {MA_INPUT}; color: {MA_TEXT_PRI};
                border: 1px solid {MA_BORDER}; border-radius: 8px;
                padding: 0 12px; font-size: 12px; {_MA_FF}
                margin: 8px 24px;
            }}
        """)
        card_layout.addWidget(search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setObjectName("InstructionsScroll")
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: transparent; }}
            QScrollBar:vertical {{ background: transparent; width: 6px; border: none; }}
            QScrollBar::handle:vertical {{ background: #303030; border-radius: 3px; min-height: 20px; }}
            QScrollBar::handle:vertical:hover {{ background: #454545; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; border: none; background: transparent; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
        """)
        self.scroll = scroll

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(24, 12, 24, 24)
        cl.setSpacing(16)

        self._sections = []
        for title_text, blocks in self._get_sections():
            sec = _Section(title_text, blocks)
            self._sections.append((title_text, sec))
            cl.addWidget(sec)

        cl.addStretch()
        scroll.setWidget(content)
        card_layout.addWidget(scroll, 1)

        self._search_input = search
        self._search_input.textChanged.connect(self._filter_sections)

        if self._initial_section:
            QTimer.singleShot(0, self._focus_initial_section)

    def _focus_initial_section(self):
        target = (self._initial_section or "").strip().lower()
        if not target:
            return
        for title, sec in self._sections:
            if target in title.lower():
                self.scroll.ensureWidgetVisible(sec, 120, 120)
                break

    def _filter_sections(self, query):
        q = query.strip().lower()
        for title, sec in self._sections:
            if not q:
                sec.setVisible(True)
            else:
                visible = q in title.lower()
                if not visible:
                    for child in sec.findChildren(QLabel):
                        if q in (child.text() or "").lower():
                            visible = True
                            break
                sec.setVisible(visible)

    def _get_sections(self):
        return [
            ("1. Introduccion", [
                ("Que es una disciplina", "Una disciplina representa un arte marcial o actividad fisica que se imparte en tu academia. Cada disciplina tiene su propio sistema de progresion, niveles, requisitos y configuraciones."),
                ("Disciplina vs Sistema de progresion", "La disciplina es el contenedor general (Karate, BJJ, Kickboxing). El sistema de progresion define como los estudiantes avanzan dentro de esa disciplina (cinturones, niveles, etc.)."),
                ("Que se puede personalizar", "Nombre, icono, color, estado activo/inactivo, sistema de progresion, nombre de niveles (singular/plural), orden de niveles, colores de cinturones, restricciones de edad, requisitos de ascenso, y plantillas predefinidas."),
            ]),
            ("2. General", [
                ("Nombre y preview en vivo", "La pestana General muestra un formulario de identidad (nombre, icono, color, estado) con una vista previa en vivo que se actualiza automaticamente al escribir o seleccionar opciones."),
                ("Vista previa reactiva", "La columna derecha muestra una tarjeta de previsualizacion que reacciona en tiempo real a los cambios en nombre, icono, color de acento y estado activo/inactivo."),
                ("Estado activo/inactivo", "Una disciplina inactiva no desaparece del sistema. Los estudiantes que ya estan asignados conservan su historial. Solo se oculta de las vistas nuevas y no permite nuevas asignaciones."),
                ("Descripcion y enfoque", "Campos opcionales para describir la disciplina y su enfoque de entrenamiento (ej: fuerza, movilidad, resistencia)."),
            ]),
            ("3. Ventanas modales", [
                ("Base unificada MartialArtFormDialog", "Todos los formularios CRUD (disciplina, nivel, requisito, ejercicio) heredan de MartialArtFormDialog, que proporciona shell frameless, sombra, modalidad, arrastre y cierre con Escape."),
                ("Comportamiento", "Mientras una ventana modal este abierta, debe terminarse o cancelarse la operacion. Cancelar no guarda cambios. Guardar aplica los datos y cierra la ventana."),
                ("Arrastre", "Las ventanas frameless pueden arrastrarse desde la barra de titulo personalizada."),
            ]),
            ("4. Sistema de progresion", [
                ("Sistema de progresion (pestana Sistema)", "Define si la disciplina utiliza o no un sistema de progresion. Si usa, elige entre 5 tipos: Cinturones, Camisa, Brazalete, Niveles o Personalizado."),
                ("Cinturones", "Sistema clasico con cinturones de colores. Ejemplo: Karate (blanco, amarillo, naranja, verde, azul, marron, negro)."),
                ("Camisa", "Sistema de camisas de diferentes colores. Ejemplo: algunos estilos de Kung Fu."),
                ("Brazaletes", "Sistema usado en algunos estilos. Ejemplo: Muay Thai con brazaletes de diferentes colores."),
                ("Niveles", "Sistema numerico o por niveles. Ejemplo: sistemas universitarios de artes marciales."),
                ("Personalizado", "Define tu propio sistema con nombres de nivel personalizados."),
                ("Nombres singular/plural", "Los nombres personalizados solo se muestran cuando se selecciona el sistema Personalizado."),
            ]),
            ("5. Crear y editar niveles", [
                ("Nombre del nivel", "El nombre identifica el nivel dentro del sistema de progresion. Debe ser el nombre oficial del cinturon, faja o grado segun el arte marcial."),
                ("Orden", "Numero que define la posicion del nivel en la secuencia de progresion. Debe ser unico por disciplina."),
                ("Color principal", "Color hexadecimal del nivel. Se usa en la barra visual del cinturon y en la vista previa."),
                ("Precolor", "Color de la franja o marca especial del cinturon. Opcional."),
                ("Grados / Stripes", "Numero de grados internos dentro del nivel. Para BJJ: 0-4 stripes. Para otros: 0-10 grados."),
                ("Color de grado", "Color de las franjas de grado. Por defecto blanco."),
            ]),
            ("6. Selector de color (ColorPaletteSelector)", [
                ("Seleccion desde selector", "Haz clic en 'Elegir color' para abrir el selector nativo de color (QColorDialog). Ahi puedes usar los colores basicos, el espectro, HSV/RGB o escribir el codigo hexadecimal."),
                ("Color hexadecimal", "Puedes escribir un color hexadecimal directamente en el campo de texto junto a la vista previa."),
                ("Vista previa", "La muestra grande muestra el color actualmente seleccionado. Cancelar en el selector no cambia el color elegido."),
                ("Selector reutilizable", "El mismo componente se usa en el formulario de disciplina y en el formulario de nivel."),
            ]),
            ("7. Estado y comportamiento del nivel", [
                ("Nivel inicial", "Marca este nivel como el primero de la secuencia de progresion."),
                ("Nivel final", "Senala el nivel superior o ultimo de la progresion ordinaria."),
                ("Nivel activo", "Permite utilizar este nivel en operaciones nuevas. Un nivel inactivo no desaparece del historial."),
                ("Desactivar no elimina", "Desactivar un nivel NO elimina estudiantes asignados ni su historial."),
                ("No duplicar ordenes", "Cada nivel debe tener un orden unico."),
            ]),
            ("8. Restricciones de edad", [
                ("Checkbox de activacion", "Marca 'Este nivel tiene restricciones de edad' para activar los campos de edad."),
                ("Edad minima y maxima", "Edad minima y maxima requerida para acceder al nivel. Valor 0 significa 'Sin limite'."),
                ("Validacion en ascensos", "Al promover un estudiante, se valida automaticamente que cumpla las restricciones de edad del nivel destino."),
            ]),
            ("9. Pestana Reglas", [
                ("Modo de ascenso simplificado", "Dos modos disponibles: Secuencial (solo siguiente nivel por orden) y Permitir saltos (el administrador puede elegir cualquier nivel superior)."),
                ("Secuencial", "Equivale a promotion_mode=sequential, allow_level_skips=False. Solo permite el siguiente nivel inmediato."),
                ("Permitir saltos", "Equivale a promotion_mode=manual, allow_level_skips=True. El administrador puede seleccionar cualquier nivel superior disponible."),
                ("Restricciones de edad", "Se mantienen en esta pestana. Puedes habilitar restricciones de edad por nivel desde una tabla inline."),
                ("Sin UI de asignacion inicial", "La configuracion de asignacion inicial se ha eliminado de la interfaz. Se mantiene first_only como predeterminado."),
                ("Sin UI de reglas personalizadas", "La interfaz de reglas de promocion personalizadas se ha eliminado. Se mantiene el soporte en base de datos para compatibilidad."),
            ]),
            ("10. Pestana Plantillas", [
                ("Filtro automatico", "Las plantillas custom y no_progression estan ocultas. Solo se muestran plantillas relevantes al sistema de progresion seleccionado."),
                ("Vista previa", "Antes de aplicar, puedes previsualizar la estructura completa de niveles que incluye la plantilla."),
                ("Aplicar plantilla", "Reemplaza los niveles actuales por los de la plantilla. Solo disponible si no hay estudiantes con niveles asignados."),
                ("Personalizacion posterior", "Despues de aplicar una plantilla, puedes modificar colores, ordenes y restricciones."),
            ]),
            ("11. Requisitos", [
                ("Tipos", "Tiempo, Tecnico, Fisico, Conducta, Asistencia, Documentacion."),
                ("Creacion", "Selecciona un tipo y escribe la descripcion del requisito. Vista previa en vivo del aspecto final."),
            ]),
            ("12. Flujo recomendado", [
                ("Paso 1-3", "1. Crear disciplina con nombre e icono. 2. Elegir el sistema de progresion. 3. Configurar el modo de ascenso en Reglas."),
                ("Paso 4-6", "4. Crear niveles manualmente o aplicar plantilla. 5. Configurar restricciones de edad. 6. Crear requisitos para niveles clave."),
                ("Paso 7-9", "7. Asignar instructores con permiso de ascenso. 8. Registrar estudiantes de prueba. 9. Realizar ascensos de prueba antes de produccion."),
            ]),
            ("13. Advertencias", [
                ("Cambios con estudiantes activos", "No cambies el orden de niveles ni elimines niveles que tengan estudiantes asignados sin revisar el impacto."),
                ("Saltos de nivel", "Permitir saltos sin intencion clara puede crear inconsistencias en el progreso."),
                ("Revisar edades", "Configurar restricciones de edad sin revisar la composicion de tu academia puede bloquear estudiantes existentes."),
                ("Guardar cambios", "Siempre guarda los cambios antes de navegar a otra seccion."),
            ]),
        ]

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


# ═══════════════════════════════════════════════════════════════
#  5. MartialArtFormDialog base class
# ═══════════════════════════════════════════════════════════════


class MartialArtFormDialog(QDialog):
    """Base class for all martial art form dialogs.

    Provides: frameless shell, draggable header, close button,
    shadow, modality, and Escape-key handling.
    """

    MODAL_MARGIN = 12

    def __init__(self, width: int, height: int, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("MartialArtFormDialog")
        self._shell_w = width
        self._shell_h = height
        self._drag_pos = None
        self.setWindowTitle(title)
        self.setMinimumSize(600, 450)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("QDialog#MartialArtFormDialog { background: transparent; border: none; }")
        self.resize(width, height)

        self._shell = QFrame(self)
        self._shell.setObjectName("MartialArtFormShell")
        self._shell.setGeometry(
            self.MODAL_MARGIN, self.MODAL_MARGIN,
            width - 2 * self.MODAL_MARGIN, height - 2 * self.MODAL_MARGIN,
        )
        self._shell.setStyleSheet(f"""
            QFrame#MartialArtFormShell {{
                background-color: {MA_MODAL_BG};
                border: 1px solid {MA_MODAL_BORDER};
                border-radius: 18px;
            }}
        """)
        _ma_shadow(self._shell, blur=26, offset_y=6, alpha=140)

        shell_lay = QVBoxLayout(self._shell)
        shell_lay.setContentsMargins(0, 0, 0, 0)
        shell_lay.setSpacing(0)

        self._header_frame = QFrame()
        self._header_frame.setObjectName("MartialArtFormHeader")
        self._header_frame.setFixedHeight(56)
        self._header_frame.setStyleSheet(f"""
            QFrame#MartialArtFormHeader {{
                background-color: {MA_MODAL_HEADER};
                border: none;
                border-bottom: 1px solid {MA_MODAL_BORDER};
                border-top-left-radius: 18px;
                border-top-right-radius: 18px;
            }}
        """)
        hdr_layout = QHBoxLayout(self._header_frame)
        hdr_layout.setContentsMargins(20, 0, 20, 0)

        self._header_row = hdr_layout

        self._title_lbl = QLabel(title)
        self._title_lbl.setStyleSheet(
            "color: #F4F4F5; font-size: 16px; font-weight: 700; "
            "border: none; background: transparent; font-family: 'Inter', 'Segoe UI', sans-serif;"
        )
        self._header_row.addWidget(self._title_lbl)
        self._header_row.addStretch()
        self._close_btn = QPushButton("\u2715")
        self._close_btn.setFixedSize(28, 28)
        self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #6B7280;
                border: none; border-radius: 6px; font-size: 13px;
                font-weight: 700; font-family: 'Inter', 'Segoe UI', sans-serif; }
            QPushButton:hover { color: #F4F4F5; background: #1E1E1E; }
        """)
        self._close_btn.clicked.connect(self.reject)
        hdr_layout.addWidget(self._close_btn)
        shell_lay.addWidget(self._header_frame)

        self._content_frame = QWidget()
        self._content_frame.setObjectName("MartialArtFormContent")
        self._content_frame.setStyleSheet(f"""
            QWidget#MartialArtFormContent {{
                background-color: {MA_MODAL_BG};
                border: none;
            }}
        """)
        self._card_layout = QVBoxLayout(self._content_frame)
        self._card_layout.setContentsMargins(24, 16, 24, 16)
        self._card_layout.setSpacing(12)
        shell_lay.addWidget(self._content_frame, 1)

        self._footer_frame = QFrame()
        self._footer_frame.setObjectName("MartialArtFormFooter")
        self._footer_frame.setFixedHeight(64)
        self._footer_frame.setStyleSheet(f"""
            QFrame#MartialArtFormFooter {{
                background-color: {MA_MODAL_HEADER};
                border: none;
                border-top: 1px solid {MA_MODAL_BORDER};
                border-bottom-left-radius: 18px;
                border-bottom-right-radius: 18px;
            }}
        """)
        self._footer_lay = QHBoxLayout(self._footer_frame)
        self._footer_lay.setContentsMargins(20, 0, 20, 0)
        shell_lay.addWidget(self._footer_frame)

    def _set_header_subtitle(self, subtitle: str):
        """Wrap the title in a column with a subtitle below it.

        Increases the header height to 72 px so the subtitle fits.
        """
        self._header_frame.setFixedHeight(72)
        self._header_row.removeWidget(self._title_lbl)
        col_widget = QWidget()
        col_widget.setStyleSheet("background: transparent; border: none;")
        col_lay = QVBoxLayout(col_widget)
        col_lay.setContentsMargins(0, 0, 0, 0)
        col_lay.setSpacing(2)
        col_lay.addWidget(self._title_lbl)
        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet(
            "color: #9CA3AF; font-size: 11px; font-weight: 500; "
            "background: transparent; border: none;"
            " font-family: 'Inter', 'Segoe UI', sans-serif;"
        )
        col_lay.addWidget(sub_lbl)
        self._header_row.insertWidget(0, col_widget, 1)

    def _add_footer_buttons(self, cancel_btn: QPushButton, save_btn: QPushButton):
        """Place Cancel and Save buttons in the fixed footer."""
        self._footer_lay.addWidget(cancel_btn)
        self._footer_lay.addStretch()
        self._footer_lay.addWidget(save_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def resizeEvent(self, event):
        self._shell.setGeometry(
            self.MODAL_MARGIN, self.MODAL_MARGIN,
            self.width() - 2 * self.MODAL_MARGIN,
            self.height() - 2 * self.MODAL_MARGIN,
        )
        super().resizeEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


# ═══════════════════════════════════════════════════════════════
#  6. Discipline exercise widgets
# ═══════════════════════════════════════════════════════════════

def _exercise_media_dir() -> Path:
    base = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppDataLocation
    )
    root = Path(base) if base else Path.home() / "DojoAdmin"
    return root / "media" / "exercises"


def persist_exercise_image(source_path: str) -> str:
    """Copy an exercise image into internal app storage.

    Returns the absolute normalized path of the stored copy. The copy is
    performed here (on save), so canceling the dialog never leaves orphans.
    """
    src = Path(source_path)
    dest_dir = _exercise_media_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)
    ext = src.suffix.lower() or ".png"
    dest = dest_dir / f"{uuid.uuid4().hex}{ext}"
    shutil.copy2(src, dest)
    return str(dest.resolve())


def load_scaled_pixmap(image_path, target_size: QSize):
    """Load an image scaled to target_size keeping aspect ratio, or None."""
    if not image_path:
        return None
    src = Path(image_path)
    if not src.is_file():
        return None
    pm = QPixmap(str(src))
    if pm.isNull():
        return None
    return pm.scaled(
        target_size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )



class DisciplineExerciseCard(QFrame):
    """Compact card for a single discipline exercise with image thumbnail."""
    edit_clicked = pyqtSignal(dict)
    delete_clicked = pyqtSignal(dict)
    toggle_active_clicked = pyqtSignal(dict)

    def __init__(self, exercise: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("DisciplineExerciseCard")
        self.exercise = exercise
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame#DisciplineExerciseCard {{
                background-color: #111111;
                border: 1px solid #252525;
                border-radius: 14px;
            }}
            QFrame#DisciplineExerciseCard:hover {{
                background-color: #151515;
                border-color: #353535;
            }}
        """)
        self.setMinimumHeight(122)

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(14)

        self._thumb_lbl = QLabel()
        self._thumb_lbl.setObjectName("ExerciseCardThumb")
        self._thumb_lbl.setFixedSize(140, 92)
        self._thumb_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thumb_lbl.setStyleSheet(
            "QLabel#ExerciseCardThumb { background: #101010; "
            "border: 1px solid #303030; border-radius: 10px; }"
        )
        root.addWidget(self._thumb_lbl)

        info = QVBoxLayout()
        info.setSpacing(3)

        header = QHBoxLayout()
        header.setSpacing(8)

        name_lbl = QLabel(exercise.get("name", ""))
        name_lbl.setStyleSheet(
            f"color: {MA_TEXT_PRI}; font-size: 13px; font-weight: 700; "
            "background: transparent; border: none; " + _MA_FF
        )
        header.addWidget(name_lbl)
        header.addStretch()

        actions = QHBoxLayout()
        actions.setSpacing(6)
        actions.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        btn_edit = QPushButton()
        btn_edit.setObjectName("DisciplineEditButton")
        btn_edit.setFixedSize(32, 32)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setToolTip("Editar")
        btn_edit.setIcon(QIcon(render_icon_pixmap("lapiz", 15, "#D4D4D8")))
        btn_edit.setIconSize(QSize(15, 15))
        btn_edit.setStyleSheet(f"""
            QPushButton#DisciplineEditButton {{
                background: transparent; border: none; border-radius: 8px;
            }}
            QPushButton#DisciplineEditButton:hover {{ background: #262626; }}
            QPushButton#DisciplineEditButton:pressed {{ background: #383838; }}
        """)
        btn_edit.clicked.connect(lambda: self.edit_clicked.emit(self.exercise))
        actions.addWidget(btn_edit)

        btn_del = QPushButton()
        btn_del.setObjectName("DisciplineDeleteButton")
        btn_del.setFixedSize(32, 32)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setToolTip("Eliminar")
        btn_del.setIcon(QIcon(render_icon_pixmap("basura", 15, "#FB7185")))
        btn_del.setIconSize(QSize(15, 15))
        btn_del.setStyleSheet(f"""
            QPushButton#DisciplineDeleteButton {{
                background: transparent; border: none; border-radius: 8px;
            }}
            QPushButton#DisciplineDeleteButton:hover {{ background: rgba(200,16,46,0.16); }}
            QPushButton#DisciplineDeleteButton:pressed {{ background: rgba(200,16,46,0.30); }}
        """)
        btn_del.clicked.connect(lambda: self.delete_clicked.emit(self.exercise))
        actions.addWidget(btn_del)

        header.addLayout(actions)
        info.addLayout(header)

        meta_parts = []
        if exercise.get("exercise_type"):
            meta_parts.append(exercise["exercise_type"])
        if exercise.get("difficulty"):
            meta_parts.append(exercise["difficulty"])
        if exercise.get("duration_minutes"):
            meta_parts.append(f"{exercise['duration_minutes']} min")
        meta_lbl = QLabel(" \u00b7 ".join(meta_parts))
        meta_lbl.setStyleSheet(
            f"color: {MA_TEXT_MUT}; font-size: 11px; "
            "background: transparent; border: none; " + _MA_FF
        )
        info.addWidget(meta_lbl)

        if exercise.get("description"):
            desc_lbl = QLabel(exercise["description"])
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(
                f"color: {MA_TEXT_SEC}; font-size: 11px; "
                "background: transparent; border: none; " + _MA_FF
            )
            info.addWidget(desc_lbl)

        root.addLayout(info, 1)

        self._refresh_thumbnail(exercise.get("image_path"))

    def _refresh_thumbnail(self, image_path):
        pm = load_scaled_pixmap(image_path, QSize(140, 92))
        if pm is not None:
            self._thumb_lbl.setPixmap(pm)
        else:
            self._thumb_lbl.setPixmap(render_icon_pixmap("ejercicio", 32, "#6B7280"))


class ExerciseImagePicker(QFrame):
    """Image picker with preview for a discipline exercise.

    Holds only a source path until the dialog saves; persist_exercise_image
    copies the file into internal storage on save, never on selection, so
    canceling the dialog leaves no orphan files.
    """

    image_changed = pyqtSignal(object)
    error_raised = pyqtSignal(str)

    _ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
    _MAX_BYTES = 15 * 1024 * 1024

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ExerciseImagePicker")
        self._image_path = None
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"""
            QFrame#ExerciseImagePicker {{
                background-color: {MA_MODAL_CARD};
                border: 1px solid {MA_MODAL_BORDER};
                border-radius: 12px;
            }}
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(14)

        self._thumb = QLabel()
        self._thumb.setObjectName("ExerciseImageThumb")
        self._thumb.setFixedSize(180, 120)
        self._thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thumb.setStyleSheet(
            "QLabel#ExerciseImageThumb { background: #101010; "
            "border: 1px solid #303030; border-radius: 10px; }"
        )
        lay.addWidget(self._thumb)

        right = QVBoxLayout()
        right.setSpacing(10)

        self._empty_lbl = QLabel("Sin imagen\nLa imagen es opcional")
        self._empty_lbl.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self._empty_lbl.setStyleSheet(
            "color: #6B7280; font-size: 12px; font-weight: 600; "
            "background: transparent; border: none; " + _MA_FF
        )
        right.addWidget(self._empty_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self._btn_select = QPushButton("Seleccionar imagen")
        self._btn_select.setFixedHeight(38)
        self._btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_select.setStyleSheet(f"""
            QPushButton {{
                background: {MA_MODAL_INPUT}; color: {MA_TEXT_PRI};
                border: 1px solid {MA_BORDER_HI}; border-radius: 10px;
                font-size: 12px; font-weight: 700; padding: 0 16px; {_MA_FF}
            }}
            QPushButton:hover {{ background: #262626; color: #F4F4F5; }}
        """)
        self._btn_select.clicked.connect(self._choose)
        btn_row.addWidget(self._btn_select)

        self._btn_remove = QPushButton(" Quitar")
        self._btn_remove.setFixedHeight(38)
        self._btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_remove.setToolTip("Quitar imagen")
        self._btn_remove.setIcon(QIcon(render_icon_pixmap("basura", 15, "#FB7185")))
        self._btn_remove.setIconSize(QSize(15, 15))
        self._btn_remove.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: #FB7185;
                border: 1px solid {MA_MODAL_BORDER}; border-radius: 10px;
                font-size: 12px; font-weight: 700; padding: 0 16px; {_MA_FF}
            }}
            QPushButton:hover {{
                background: rgba(200,16,46,0.16); border-color: #FB7185;
            }}
            QPushButton:disabled {{
                color: #52525B; border-color: #262626; background: transparent;
            }}
        """)
        self._btn_remove.clicked.connect(self.clear_image)
        btn_row.addWidget(self._btn_remove)
        btn_row.addStretch()

        right.addLayout(btn_row)
        right.addStretch()

        lay.addLayout(right, 1)
        self._refresh()

    def image_path(self):
        return self._image_path

    def set_image_path(self, path):
        self._image_path = path
        self._refresh()

    def clear_image(self):
        self._image_path = None
        self._refresh()
        self.image_changed.emit(None)

    def _refresh(self):
        pm = load_scaled_pixmap(self._image_path, QSize(180, 120))
        if pm is not None:
            self._thumb.setPixmap(pm)
            self._empty_lbl.setText("Imagen seleccionada")
            self._btn_select.setText("Cambiar imagen")
            self._btn_remove.setEnabled(True)
        else:
            self._thumb.setPixmap(render_icon_pixmap("ejercicio", 36, "#6B7280"))
            self._empty_lbl.setText("Sin imagen\nLa imagen es opcional")
            self._btn_select.setText("Seleccionar imagen")
            self._btn_remove.setEnabled(False)

    def _choose(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar imagen",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.webp);;Todos los archivos (*)",
        )
        if not path:
            return
        self.error_raised.emit("")
        err = self._validate(path)
        if err:
            self.error_raised.emit(err)
            return
        self._image_path = path
        self._refresh()
        self.image_changed.emit(path)

    def _validate(self, path: str):
        src = Path(path)
        if not src.is_file():
            return "El archivo seleccionado no existe."
        if src.suffix.lower() not in self._ALLOWED_EXTS:
            return "Formato no permitido. Usa PNG, JPG, JPEG o WEBP."
        try:
            if src.stat().st_size > self._MAX_BYTES:
                return "La imagen supera el tamaño máximo de 15 MB."
        except OSError:
            return "No se pudo leer el archivo seleccionado."
        if QPixmap(str(src)).isNull():
            return "El archivo no es una imagen válida."
        return None


_EXERCISE_TYPES = [
    "Fuerza", "Movilidad", "Cardio", "Coordinacion",
    "Resistencia", "Tecnica", "Calentamiento", "Recuperacion", "Personalizado",
]
_EXERCISE_DIFFICULTIES = ["Basico", "Intermedio", "Avanzado", "Adaptable"]


class DisciplineExerciseDialog(MartialArtFormDialog):
    """Dialog for creating or editing a discipline exercise.

    Body scrolls inside a transparent QScrollArea; the footer (Cancelar/Crear)
    stays fixed. An optional image can be selected/previewed/replaced/removed;
    the file is copied into internal storage only on save.
    """

    def __init__(self, repo, martial_art_id: int, exercise: dict | None = None, parent=None):
        self.repo = repo
        self.martial_art_id = martial_art_id
        self.exercise = exercise
        self.is_edit = exercise is not None
        title = "Editar ejercicio" if self.is_edit else "Nuevo ejercicio"
        super().__init__(820, 760, title, parent)
        self.setObjectName("DisciplineExerciseDialog")

        self._card_layout.setContentsMargins(30, 20, 30, 18)
        self._card_layout.setSpacing(14)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.viewport().setAutoFillBackground(False)
        scroll.viewport().setStyleSheet("background: transparent; border: none;")
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollArea > QWidget > QWidget {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 7px;
                margin: 6px 1px;
                border: none;
            }

            QScrollBar::handle:vertical {
                background-color: #3A3A3A;
                border-radius: 3px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #4A4A4A;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
                border: none;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }

            QScrollBar:horizontal {
                height: 0px;
                max-height: 0px;
                background: transparent;
                border: none;
            }
        """)

        self._form_widget = QWidget()
        self._form_widget.setObjectName("DisciplineExerciseForm")
        self._form_widget.setStyleSheet(
            "QWidget#DisciplineExerciseForm { background: transparent; border: none; }"
        )
        self._form_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        self._form_lay = QVBoxLayout(self._form_widget)
        self._form_lay.setContentsMargins(0, 0, 4, 0)
        self._form_lay.setSpacing(14)
        scroll.setWidget(self._form_widget)
        self._card_layout.addWidget(scroll)

        self._form_lay.addWidget(_ma_field_label("NOMBRE *"))
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Ej: Sentadilla con peso, Circuito de cardio...")
        self.inp_name.setStyleSheet(MA_FIELD_QSS)
        if self.is_edit:
            self.inp_name.setText(exercise.get("name", ""))
        self._form_lay.addWidget(self.inp_name)

        row1 = QHBoxLayout(); row1.setSpacing(10)
        row1.addWidget(_ma_field_label("TIPO"))
        row1.addWidget(_ma_field_label("DIFICULTAD"))
        self._form_lay.addLayout(row1)

        row2 = QHBoxLayout(); row2.setSpacing(10)
        self.cmb_type = QComboBox()
        self.cmb_type.setStyleSheet(MA_FIELD_QSS)
        self.cmb_type.addItems(_EXERCISE_TYPES)
        if self.is_edit:
            t = exercise.get("exercise_type") or "Personalizado"
            idx = self.cmb_type.findText(t, Qt.MatchFlag.MatchFixedString)
            if idx >= 0:
                self.cmb_type.setCurrentIndex(idx)
        row2.addWidget(self.cmb_type)

        self.cmb_diff = QComboBox()
        self.cmb_diff.setStyleSheet(MA_FIELD_QSS)
        self.cmb_diff.addItems(_EXERCISE_DIFFICULTIES)
        if self.is_edit:
            d = exercise.get("difficulty") or "Basico"
            idx = self.cmb_diff.findText(d, Qt.MatchFlag.MatchFixedString)
            if idx >= 0:
                self.cmb_diff.setCurrentIndex(idx)
        row2.addWidget(self.cmb_diff)
        self._form_lay.addLayout(row2)

        self._form_lay.addWidget(_ma_field_label("DURACIÓN (minutos)"))
        self.spin_duration = QSpinBox()
        self.spin_duration.setRange(0, 999)
        self.spin_duration.setSpecialValueText("Sin límite")
        self.spin_duration.setStyleSheet(MA_SPINBOX_QSS)
        self.spin_duration.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.spin_duration.setFixedHeight(44)
        if self.is_edit and exercise.get("duration_minutes"):
            self.spin_duration.setValue(exercise["duration_minutes"])
        self._form_lay.addWidget(self.spin_duration)

        self.lbl_duration_hint = QLabel(
            "Usa 0 para dejar el ejercicio sin límite de tiempo."
        )
        self.lbl_duration_hint.setStyleSheet(
            "color: #71717A; font-size: 10px; font-weight: 500; "
            "background: transparent; border: none; " + _MA_FF
        )
        self._form_lay.addWidget(self.lbl_duration_hint)

        self._form_lay.addWidget(_ma_field_label("DESCRIPCION"))
        self.inp_desc = QTextEdit()
        self.inp_desc.setPlaceholderText("Describe brevemente este ejercicio...")
        self.inp_desc.setMaximumHeight(90)
        self.inp_desc.setStyleSheet(f"""
            QTextEdit {{ background: {MA_INPUT}; color: {MA_TEXT_PRI}; border: 1.5px solid {MA_BORDER};
                border-radius: 8px; padding: 8px 12px; font-size: 12px; {_MA_FF} }}
            QTextEdit:focus {{ border-color: {MA_BLUE}; }}
        """)
        if self.is_edit:
            self.inp_desc.setPlainText(exercise.get("description") or "")
        self._form_lay.addWidget(self.inp_desc)

        self._form_lay.addWidget(_ma_field_label("IMAGEN DEL EJERCICIO"))
        self.picker = ExerciseImagePicker()
        self._form_lay.addWidget(self.picker)

        self._form_lay.addWidget(_ma_field_label("ESTADO"))
        self.chk_active = QPushButton("Activo" if (not self.is_edit or exercise.get("is_active", True)) else "Inactivo")
        self.chk_active.setCheckable(True)
        self.chk_active.setChecked(not self.is_edit or exercise.get("is_active", True))
        self.chk_active.setFixedHeight(36)
        self.chk_active.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_active_btn()
        self.chk_active.clicked.connect(self._update_active_btn)
        self._form_lay.addWidget(self.chk_active)

        self.lbl_error = QLabel("")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setStyleSheet(f"color: {MA_RED}; font-size: 11px; {_MA_FF}")
        self._form_lay.addWidget(self.lbl_error)

        self._form_lay.addStretch()

        btn_cancel = _ma_secondary_btn("Cancelar", height=42)
        btn_cancel.clicked.connect(self.reject)
        btn_save = _ma_primary_btn("Guardar" if self.is_edit else "Crear", height=42)
        btn_save.clicked.connect(self._save)
        self.inp_name.returnPressed.connect(self._save)
        self._add_footer_buttons(btn_cancel, btn_save)

        self._original_image_path = exercise.get("image_path") if self.is_edit else None
        self._selected_source_path = None
        self._remove_image_requested = False
        self._saved_image_path = self._original_image_path
        if self.is_edit:
            self.picker.set_image_path(self._original_image_path)
        self.picker.image_changed.connect(self._on_image_changed)
        self.picker.error_raised.connect(self.lbl_error.setText)

    def _on_image_changed(self, path):
        if path is None:
            self._remove_image_requested = True
            self._selected_source_path = None
        else:
            self._remove_image_requested = False
            self._selected_source_path = path
        self.lbl_error.setText("")

    def _update_active_btn(self):
        checked = self.chk_active.isChecked()
        self.chk_active.setText("Activo" if checked else "Inactivo")
        if checked:
            self.chk_active.setStyleSheet(f"QPushButton {{ background: rgba(5,46,22,0.5); color: {MA_GREEN}; border: 1px solid #166534; border-radius: 8px; font-size: 12px; font-weight: 800; {_MA_FF} }} QPushButton:hover {{ background: rgba(5,46,22,0.8); }}")
        else:
            self.chk_active.setStyleSheet(f"QPushButton {{ background: {MA_INPUT}; color: {MA_TEXT_MUT}; border: 1px solid {MA_BORDER}; border-radius: 8px; font-size: 12px; font-weight: 700; {_MA_FF} }} QPushButton:hover {{ color: {MA_TEXT_SEC}; border-color: {MA_BORDER_HI}; }}")

    def _save(self):
        name = self.inp_name.text().strip()
        if not name:
            self.lbl_error.setText("El nombre es obligatorio.")
            return
        duration = self.spin_duration.value() if self.spin_duration.value() > 0 else None

        if self.is_edit:
            if self._remove_image_requested:
                final_image_path = None
            elif self._selected_source_path is not None:
                final_image_path = self._selected_source_path
            else:
                final_image_path = self._original_image_path
        else:
            final_image_path = self._selected_source_path

        copied_path = None
        try:
            if final_image_path is not None and final_image_path != self._original_image_path:
                copied_path = persist_exercise_image(final_image_path)
                final_image_path = copied_path
            self._saved_image_path = final_image_path
            data = {
                "name": name,
                "description": self.inp_desc.toPlainText().strip() or None,
                "exercise_type": self.cmb_type.currentText(),
                "difficulty": self.cmb_diff.currentText(),
                "duration_minutes": duration,
                "is_active": self.chk_active.isChecked(),
                "image_path": self._saved_image_path,
            }
            if self.is_edit:
                self.repo.update_discipline_exercise(self.exercise["id"], data)
            else:
                self.repo.create_discipline_exercise(self.martial_art_id, data)
            self.accept()
        except Exception as e:
            if copied_path:
                self._delete_copy(copied_path)
            self.lbl_error.setText(f"Error: {e}")

    def _delete_copy(self, path):
        try:
            p = Path(path)
            if p.is_file():
                p.unlink()
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════
#  7. Requirement widgets
# ═══════════════════════════════════════════════════════════════

_REQUIREMENT_FALLBACK_DESC = "Completa la descripci\u00f3n del requisito..."
_REQUIREMENT_FALLBACK_COLOR = "#3B82F6"


class RequirementVisualCard(QFrame):
    """Unified visual card for belt requirements (live preview + detail list).

    Precedence for values: explicit args > requirement dict > fallbacks.
    All user content is rendered as PlainText (never HTML).
    """

    edit_requested = pyqtSignal(dict)
    delete_requested = pyqtSignal(dict)

    def __init__(
        self,
        requirement: dict | None = None,
        *,
        type_name: str = "",
        description: str = "",
        accent_color: str = "#3B82F6",
        preview: bool = False,
        show_actions: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("RequirementVisualCard")
        self._requirement = requirement or {}
        self._preview = preview
        self._show_actions = show_actions and not preview

        explicit = (
            requirement is None
            or bool(type_name)
            or bool(description)
            or accent_color != _REQUIREMENT_FALLBACK_COLOR
        )
        if explicit:
            self._type_name = (type_name or "").strip() or "Sin tipo"
            self._description = (
                (description or "").strip() or _REQUIREMENT_FALLBACK_DESC
            )
            self._accent_color = valid_hex_color(
                accent_color, _REQUIREMENT_FALLBACK_COLOR
            )
        else:
            self._type_name = (
                (requirement.get("type_name") or "").strip() or "Sin tipo"
            )
            self._description = (
                (requirement.get("requirement") or "").strip()
                or _REQUIREMENT_FALLBACK_DESC
            )
            self._accent_color = valid_hex_color(
                requirement.get("accent_color"), _REQUIREMENT_FALLBACK_COLOR
            )
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────
    def _build_ui(self):
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        hover_qss = ""
        if not self._preview:
            hover_qss = """
                QFrame#RequirementVisualCard:hover {
                    background-color: #191919;
                    border-color: #353535;
                }
            """
        self.setStyleSheet(f"""
            QFrame#RequirementVisualCard {{
                background-color: #151515;
                border: 1px solid #252525;
                border-radius: 13px;
            }}
            {hover_qss}
        """)
        self.setMinimumHeight(126 if self._preview else 112)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 12, 0)
        root.setSpacing(0)

        bar_wrap = QWidget()
        bar_wrap.setFixedWidth(6)
        bar_lay = QVBoxLayout(bar_wrap)
        bar_lay.setContentsMargins(0, 4, 0, 4)
        bar_lay.setSpacing(0)
        self._accent_bar = QFrame()
        self._accent_bar.setObjectName("RequirementAccentBar")
        self._accent_bar.setStyleSheet(
            f"QFrame#RequirementAccentBar {{ background: {self._accent_color}; "
            f"border: none; border-radius: 3px; }}"
        )
        bar_lay.addWidget(self._accent_bar)
        root.addWidget(bar_wrap)

        body = QWidget()
        body.setStyleSheet("background: transparent; border: none;")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(16, 14, 16, 14)
        body_lay.setSpacing(6)

        self._header_lay = QHBoxLayout()
        self._header_lay.setContentsMargins(0, 0, 0, 0)
        self._header_lay.setSpacing(8)
        self._header_lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self._helper_lbl = QLabel("REQUISITO PARA ASCENSO")
        self._helper_lbl.setTextFormat(Qt.TextFormat.PlainText)
        self._helper_lbl.setStyleSheet(self._helper_qss())
        self._header_lay.addWidget(self._helper_lbl)
        self._header_lay.addStretch()

        body_lay.addLayout(self._header_lay)

        self._type_lbl = QLabel(self._type_name)
        self._type_lbl.setTextFormat(Qt.TextFormat.PlainText)
        self._type_lbl.setStyleSheet(
            "color: #F4F4F5; font-size: 14px; font-weight: 800; "
            "background: transparent; border: none; " + _MA_FF
        )
        body_lay.addWidget(self._type_lbl)

        self._desc_lbl = QLabel(self._description)
        self._desc_lbl.setTextFormat(Qt.TextFormat.PlainText)
        self._desc_lbl.setWordWrap(True)
        self._desc_lbl.setStyleSheet(
            "color: #D4D4D8; font-size: 12px; font-weight: 600; "
            "background: transparent; border: none; " + _MA_FF
        )
        body_lay.addWidget(self._desc_lbl)

        root.addWidget(body, 1)

        if self._show_actions:
            self._actions_widget = QWidget()
            self._actions_widget.setFixedSize(74, 34)
            self._actions_widget.setStyleSheet("background: transparent; border: none;")
            actions_lay = QHBoxLayout(self._actions_widget)
            actions_lay.setContentsMargins(0, 0, 0, 0)
            actions_lay.setSpacing(6)
            actions_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._btn_edit = self._action_button(
                "lapiz", "#D4D4D8", "RequirementEditButton",
                "#262626", "#383838", "Editar requisito",
                self.edit_requested.emit,
            )
            self._btn_delete = self._action_button(
                "basura", "#FB7185", "RequirementDeleteButton",
                "rgba(200,16,46,0.16)", "rgba(200,16,46,0.30)",
                "Eliminar requisito", self.delete_requested.emit,
            )
            actions_lay.addWidget(self._btn_edit)
            actions_lay.addWidget(self._btn_delete)
            root.addWidget(
                self._actions_widget, 0,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
            )

            self._actions_opacity = QGraphicsOpacityEffect(self._actions_widget)
            self._actions_widget.setGraphicsEffect(self._actions_opacity)
            self._actions_opacity.setOpacity(0.0)
            self._actions_widget.setEnabled(False)

    def _helper_qss(self) -> str:
        return (
            f"color: {self._accent_color}; font-size: 10px; font-weight: 700; "
            "letter-spacing: 0.8px; background: transparent; border: none; "
            + _MA_FF
        )

    def _action_button(
        self, icon_key, icon_color, object_name, hover_bg, pressed_bg,
        tooltip, slot,
    ):
        btn = QPushButton()
        btn.setObjectName(object_name)
        btn.setFixedSize(34, 34)
        btn.setIconSize(QSize(17, 17))
        btn.setContentsMargins(0, 0, 0, 0)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setToolTip(tooltip)
        btn.setIcon(QIcon(render_icon_pixmap(icon_key, 17, icon_color)))
        btn.setStyleSheet(f"""
            QPushButton#{object_name} {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 0px;
                margin: 0px;
                text-align: center;
            }}
            QPushButton#{object_name}:hover {{ background-color: {hover_bg}; }}
            QPushButton#{object_name}:pressed {{ background-color: {pressed_bg}; }}
        """)
        btn.clicked.connect(lambda _=False: slot(self._requirement))
        return btn

    # ── Hover: reveal/hide actions without relayouting ───────
    def enterEvent(self, event):
        if self._show_actions:
            self._actions_opacity.setOpacity(1.0)
            self._actions_widget.setEnabled(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._show_actions:
            local_position = self.mapFromGlobal(QCursor.pos())
            if not self.rect().contains(local_position):
                self._actions_opacity.setOpacity(0.0)
                self._actions_widget.setEnabled(False)
        super().leaveEvent(event)

    # ── Updaters (in-place, no rebuild) ────────────────────────
    def set_type_name(self, name: str):
        self._type_name = (name or "").strip() or "Sin tipo"
        self._type_lbl.setText(self._type_name)

    def set_description(self, description: str):
        self._description = (
            (description or "").strip() or _REQUIREMENT_FALLBACK_DESC
        )
        self._desc_lbl.setText(self._description)

    def set_accent_color(self, color: str):
        self._accent_color = valid_hex_color(color, _REQUIREMENT_FALLBACK_COLOR)
        self._accent_bar.setStyleSheet(
            f"QFrame#RequirementAccentBar {{ background: {self._accent_color}; "
            f"border: none; border-radius: 3px; }}"
        )
        self._helper_lbl.setStyleSheet(self._helper_qss())

    def set_data(
        self,
        requirement: dict | None = None,
        *,
        type_name: str | None = None,
        description: str | None = None,
        accent_color: str | None = None,
    ):
        if type_name is not None:
            self.set_type_name(type_name)
        elif requirement is not None:
            self.set_type_name(requirement.get("type_name"))
        if description is not None:
            self.set_description(description)
        elif requirement is not None:
            self.set_description(requirement.get("requirement"))
        if accent_color is not None:
            self.set_accent_color(accent_color)
        elif requirement is not None:
            self.set_accent_color(requirement.get("accent_color"))


class RequirementCard(RequirementVisualCard):
    """Detail-list card. Subclass of RequirementVisualCard that re-exports
    the legacy edit_clicked/delete_clicked signals."""

    edit_clicked = pyqtSignal(dict)
    delete_clicked = pyqtSignal(dict)

    def __init__(self, req: dict, parent=None):
        super().__init__(req, show_actions=True, parent=parent)
        self.req = req
        self.edit_requested.connect(self.edit_clicked)
        self.delete_requested.connect(self.delete_clicked)


