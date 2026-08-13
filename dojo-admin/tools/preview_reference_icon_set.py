"""Preview the 12 new reference icons in a 3x4 grid.

Run from the Dojo_admin directory:
    python tools/preview_reference_icon_set.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from views.icon_library import render_icon_pixmap, ICON_DRAWERS

ROWS, COLS = 3, 4
ICON_SIZE = 64
BG_COLOR = "#F2F3F8"
TEXT_COLOR = "#111827"
KEY_COLOR = "#6B7280"

ORDER = [
    "martial-arts-gi",
    "punching-bag",
    "split-shield",
    "sparring-fighters",
    "tied-belt",
    "boxing-glove-outline",
    "jump-rope",
    "katana",
    "anatomical-heart",
    "training-calendar",
    "achievement-medal",
    "training-checklist",
]

LABELS = {
    "martial-arts-gi": "Uniforme de artes marciales",
    "punching-bag": "Saco de boxeo",
    "split-shield": "Escudo de proteccion",
    "sparring-fighters": "Combate y sparring",
    "tied-belt": "Cinturon de graduacion",
    "boxing-glove-outline": "Guante de boxeo",
    "jump-rope": "Cuerda de saltar",
    "katana": "Katana",
    "anatomical-heart": "Corazon y condicion fisica",
    "training-calendar": "Calendario de entrenamiento",
    "achievement-medal": "Medalla de logro",
    "training-checklist": "Lista de requisitos",
}


def main():
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Reference Icon Set Preview — 3x4 Grid")
    window.setStyleSheet(f"background: {BG_COLOR};")

    root = QVBoxLayout(window)
    root.setContentsMargins(24, 24, 24, 24)
    root.setSpacing(16)

    title = QLabel("Iconos de referencia — 12 iconos (3x4)")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 16px; font-weight: bold; font-family: 'Inter', 'Segoe UI', sans-serif; padding-bottom: 8px;")
    root.addWidget(title)

    grid = QGridLayout()
    grid.setSpacing(20)

    for idx, key in enumerate(ORDER):
        row, col = divmod(idx, COLS)

        cell = QVBoxLayout()
        cell.setSpacing(6)
        cell.setContentsMargins(8, 8, 8, 8)

        pixmap = render_icon_pixmap(key, size=ICON_SIZE, color=TEXT_COLOR)
        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(ICON_SIZE + 16, ICON_SIZE + 16)
        icon_label.setStyleSheet(f"""
            background: white;
            border-radius: 12px;
            border: 1px solid #E5E7EB;
        """)
        cell.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

        name_label = QLabel(LABELS.get(key, key))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 12px; font-family: 'Inter', 'Segoe UI', sans-serif; background: transparent;")
        cell.addWidget(name_label)

        key_label = QLabel(key)
        key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        key_label.setStyleSheet(f"color: {KEY_COLOR}; font-size: 10px; font-family: 'Consolas', monospace; background: transparent;")
        cell.addWidget(key_label)

        wrapper = QWidget()
        wrapper.setLayout(cell)
        wrapper.setStyleSheet(f"""
            background: white;
            border-radius: 16px;
            border: 1px solid #E5E7EB;
        """)
        wrapper.setFixedSize(140, 150)
        grid.addWidget(wrapper, row, col)

    root.addLayout(grid)

    sizes_label = QLabel("Sizes: 16px | 20px | 24px | 32px | 48px | 64px")
    sizes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    sizes_label.setStyleSheet(f"color: {KEY_COLOR}; font-size: 11px; font-family: 'Consolas', monospace; padding-top: 12px; background: transparent;")
    root.addWidget(sizes_label)

    size_row = QHBoxLayout()
    size_row.setSpacing(12)
    size_row.setContentsMargins(40, 0, 40, 0)
    for sz in [16, 20, 24, 32, 48, 64]:
        pix = render_icon_pixmap("martial-arts-gi", size=sz, color=TEXT_COLOR)
        lbl = QLabel()
        lbl.setPixmap(pix)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setFixedSize(sz + 8, sz + 8)
        lbl.setStyleSheet(f"background: white; border: 1px solid #E5E7EB; border-radius: 4px;")
        size_row.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        sz_lbl = QLabel(f"{sz}")
        sz_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sz_lbl.setStyleSheet(f"color: {KEY_COLOR}; font-size: 9px; font-family: 'Consolas', monospace; background: transparent;")
        size_row.addWidget(sz_lbl)

    root.addLayout(size_row)

    window.resize(680, 580)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
