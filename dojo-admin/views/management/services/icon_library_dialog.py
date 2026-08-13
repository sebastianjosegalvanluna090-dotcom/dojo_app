from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QWidget,
    QGridLayout,
)
from PyQt6.QtCore import Qt

from core.i18n import tr

SERVICE_ICONS = [
    "🚀", "🎓", "⚡", "🏅", "🥋", "🥊",
    "💪", "🧘", "📋", "🎯", "🛡️", "🔥",
    "⭐", "💳", "📦", "🏆", "👊", "⏱️",
    "🧾", "🎟️", "📚", "🧠", "🦾", "🏋️",
    "🤸", "🩺", "🎥", "📸", "🧃", "🍎",
    "🗓️", "📆", "🔔", "📢", "💎", "🧍",
    "👥", "🧑‍🏫", "📝", "✅", "🔒", "🔑",
    "🎖️", "🥇", "🥈", "🥉", "🛒", "💰",
    "🏷️", "🧦", "🥤", "🧥", "👕", "🎒",
    "📍", "🧪", "🛎️", "🎫", "🧑‍⚕️", "🧑‍💻",
    "🪪", "🗂️",
]

RED    = "#C8102E"
BORDER = "#2A2A2A"


class IconLibraryDialog(QDialog):
    def __init__(self, current_icon="🚀", parent=None):
        super().__init__(parent)
        self.selected_icon = current_icon

        self.setWindowTitle(tr("management.services.icon_library"))
        self.setMinimumSize(600, 560)
        self.resize(600, 560)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #0D0D0D;
                color: #F0F0F0;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        title = QLabel(tr("management.services.icon_library"))
        title.setStyleSheet("color: white; font-size: 20px; font-weight: 900;")
        root.addWidget(title)

        subtitle = QLabel(tr("management.services.icon_library_subtitle"))
        subtitle.setStyleSheet("color: #666666; font-size: 12px; font-weight: 600;")
        root.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent; border: none;")
        grid = QGridLayout(scroll_content)
        grid.setSpacing(8)
        grid.setContentsMargins(0, 0, 0, 0)

        cols = 6
        self._icon_buttons = []
        for idx, icon in enumerate(SERVICE_ICONS):
            btn = QPushButton(icon)
            btn.setFixedSize(54, 54)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=icon: self._select(i))
            btn.mouseDoubleClickEvent = lambda e, i=icon: self._double_click(i)
            self._icon_buttons.append(btn)
            grid.addWidget(btn, idx // cols, idx % cols)

        scroll.setWidget(scroll_content)
        root.addWidget(scroll, 1)

        self._refresh_buttons()

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton(tr("cancel"))
        btn_cancel.setFixedHeight(38)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: #666666;
                border: 1px solid {BORDER}; border-radius: 9px; font-size: 13px;
            }}
            QPushButton:hover {{ color: #F0F0F0; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_use = QPushButton(tr("management.services.use_icon"))
        btn_use.setFixedHeight(38)
        btn_use.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_use.setStyleSheet(f"""
            QPushButton {{
                background: {RED}; color: white;
                border: none; border-radius: 9px; font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background: #E8152F; }}
        """)
        btn_use.clicked.connect(self.accept)

        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_use)
        root.addLayout(btn_row)

    def _select(self, icon):
        self.selected_icon = icon
        self._refresh_buttons()

    def _double_click(self, icon):
        self.selected_icon = icon
        self.accept()

    def _refresh_buttons(self):
        for btn in self._icon_buttons:
            selected = btn.text() == self.selected_icon
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {'#2A0A0C' if selected else '#1A1A1A'};
                    color: white;
                    border: {'2px solid #C8102E' if selected else '1px solid #2A2A2A'};
                    border-radius: 14px;
                    font-size: 24px;
                }}
                QPushButton:hover {{
                    background-color: #222222;
                    border-color: {RED};
                }}
            """)

    def selected(self):
        return self.selected_icon
