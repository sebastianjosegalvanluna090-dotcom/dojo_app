from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt

from core.i18n import tr

BG_MAIN  = "#050505"
BG_CARD  = "#0C0C0C"
BORDER   = "#1F1F1F"
TEXT_PRI = "#FAFAFA"
TEXT_SEC = "#A3A3A3"


class EventsReportView(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: {BG_MAIN}; border: none; }}
        """)

        container = QWidget()
        container.setStyleSheet(f"background-color: {BG_MAIN};")
        root = QVBoxLayout(container)
        root.setContentsMargins(32, 28, 32, 32)
        root.setSpacing(20)

        title = QLabel(tr("reports.events.title"))
        title.setStyleSheet(f"""
            color: {TEXT_PRI}; font-size: 22px; font-weight: 900;
            font-family: 'Inter'; background: transparent;
        """)
        root.addWidget(title)

        subtitle = QLabel(tr("reports.events.subtitle"))
        subtitle.setStyleSheet(f"""
            color: {TEXT_SEC}; font-size: 13px; font-weight: 600;
            font-family: 'Inter'; background: transparent;
        """)
        root.addWidget(subtitle)
        root.addSpacing(40)

        placeholder = QFrame()
        placeholder.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
        """)
        placeholder.setMinimumHeight(300)
        ph_layout = QVBoxLayout(placeholder)
        ph_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_lbl = QLabel("\U0001f4c5")
        icon_lbl.setStyleSheet("font-size: 48px; background: transparent;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        msg = QLabel(tr("reports.events.coming_soon"))
        msg.setStyleSheet(f"""
            color: {TEXT_SEC}; font-size: 16px; font-weight: 700;
            font-family: 'Inter'; background: transparent;
        """)
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub_msg = QLabel(tr("reports.events.coming_soon_detail"))
        sub_msg.setStyleSheet(f"""
            color: {TEXT_SEC}; font-size: 13px; font-weight: 600;
            font-family: 'Inter'; background: transparent; opacity: 0.6;
        """)
        sub_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ph_layout.addStretch()
        ph_layout.addWidget(icon_lbl)
        ph_layout.addSpacing(12)
        ph_layout.addWidget(msg)
        ph_layout.addSpacing(4)
        ph_layout.addWidget(sub_msg)
        ph_layout.addStretch()

        root.addWidget(placeholder)
        root.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
