from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QStackedWidget,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QGraphicsBlurEffect
from PyQt6.QtGui import QColor

from core.i18n import tr

from views.management.inventory.inventory_view import InventoryView
from views.management.memberships.memberships_view import MembershipsView
from views.management.services.services_view import ServicesView

BG_MAIN  = "#0D0D0D"
BG_CARD  = "#161616"
BG_PANEL = "#121212"
BG_HOVER = "#1A1A1A"
BORDER   = "#2A2A2A"
RED      = "#C8102E"
RED_H    = "#E8152F"
TEXT_PRI = "#F0F0F0"
TEXT_SEC = "#888888"
TEXT_MUT = "#666666"


class ManagementSidebarButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(46)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_SEC};
                border: none;
                border-left: 3px solid transparent;
                border-radius: 8px;
                text-align: left;
                padding-left: 14px;
                font-size: 14px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                background-color: {BG_HOVER};
                color: white;
            }}
            QPushButton:checked {{
                background-color: {BG_HOVER};
                color: white;
                border-left: 3px solid {RED};
            }}
        """)


class ManagementView(QWidget):
    def __init__(self):
        super().__init__()
        self._animations = []
        self._blur_effect = None
        self._blur_target_widget = None
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        self.stack = QStackedWidget()

        self.inventory_view = InventoryView(
            blur_on=self._blur_on,
            blur_off=self._blur_off
        )
        self.memberships_view = MembershipsView(
            blur_on=self._blur_on,
            blur_off=self._blur_off
        )
        self.services_view = ServicesView(
            blur_on=self._blur_on,
            blur_off=self._blur_off
        )

        self.stack.addWidget(self.inventory_view)
        self.stack.addWidget(self.memberships_view)
        self.stack.addWidget(self.services_view)

        main = QFrame()
        main.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_MAIN};
                border: none;
            }}
        """)
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.stack)
        root.addWidget(main, 1)

        self.btn_inventory.setChecked(True)
        self.stack.setCurrentIndex(0)

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(256)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_MAIN};
                border: none;
                border-right: 1px solid {BORDER};
            }}
        """)

        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(24, 24, 24, 24)
        side_layout.setSpacing(10)

        title = QLabel(tr("management.title"))
        title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: 900;
        """)

        subtitle = QLabel(tr("management.subtitle"))
        subtitle.setStyleSheet("""
            color: #666666;
            font-size: 10px;
            font-weight: 900;
            letter-spacing: 1.4px;
        """)

        side_layout.addWidget(title)
        side_layout.addWidget(subtitle)
        side_layout.addSpacing(30)

        self.btn_inventory = ManagementSidebarButton("\U0001f4e6 " + tr("management.inventory"))
        self.btn_memberships = ManagementSidebarButton("\U0001f4b3 " + tr("management.memberships"))
        self.btn_services = ManagementSidebarButton("\U0001f680 " + tr("management.services.nav"))

        self.btn_inventory.clicked.connect(lambda: self._switch_view("inventory"))
        self.btn_memberships.clicked.connect(lambda: self._switch_view("memberships"))
        self.btn_services.clicked.connect(lambda: self._switch_view("services"))

        side_layout.addWidget(self.btn_inventory)
        side_layout.addWidget(self.btn_memberships)
        side_layout.addWidget(self.btn_services)
        side_layout.addStretch()

        return sidebar

    def _switch_view(self, view_name: str):
        self.btn_inventory.setChecked(view_name == "inventory")
        self.btn_memberships.setChecked(view_name == "memberships")
        self.btn_services.setChecked(view_name == "services")

        if view_name == "inventory":
            self.stack.setCurrentIndex(0)
        elif view_name == "memberships":
            self.stack.setCurrentIndex(1)
        else:
            self.stack.setCurrentIndex(2)

        self._animate_current_view()

    def _animate_current_view(self):
        widget = self.stack.currentWidget()
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(380)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        def cleanup():
            widget.setGraphicsEffect(None)

        anim.finished.connect(cleanup)
        anim.start()
        self._animations.append(anim)

    def _blur_target(self):
        win = self.window()
        if hasattr(win, "centralWidget") and win.centralWidget():
            return win.centralWidget()
        return win

    def _blur_on(self):
        target = self._blur_target()
        if self._blur_effect is not None:
            return

        self._blur_target_widget = target
        self._blur_effect = QGraphicsBlurEffect(target)
        self._blur_effect.setBlurRadius(0)
        target.setGraphicsEffect(self._blur_effect)

        self._blur_anim = QPropertyAnimation(self._blur_effect, b"blurRadius", self)
        self._blur_anim.setDuration(220)
        self._blur_anim.setStartValue(0)
        self._blur_anim.setEndValue(14)
        self._blur_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._blur_anim.start()

    def _blur_off(self):
        if self._blur_effect is None:
            return

        target = self._blur_target_widget

        self._blur_anim_out = QPropertyAnimation(self._blur_effect, b"blurRadius", self)
        self._blur_anim_out.setDuration(180)
        self._blur_anim_out.setStartValue(self._blur_effect.blurRadius())
        self._blur_anim_out.setEndValue(0)
        self._blur_anim_out.setEasingCurve(QEasingCurve.Type.InCubic)

        def cleanup():
            if target:
                target.setGraphicsEffect(None)
            self._blur_effect = None
            self._blur_target_widget = None

        self._blur_anim_out.finished.connect(cleanup)
        self._blur_anim_out.start()
