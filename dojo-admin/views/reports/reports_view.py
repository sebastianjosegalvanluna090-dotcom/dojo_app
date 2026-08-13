from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QStackedWidget,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QGraphicsBlurEffect

from core.i18n import tr

from views.reports.general_report_view import GeneralReportView
from views.reports.finance_report_view import FinanceReportView
from views.reports.classes_report_view import ClassesReportView
from views.reports.students_report_view import StudentsReportView
from views.reports.events_report_view import EventsReportView

BG_MAIN  = "#050505"
BG_CARD  = "#0C0C0C"
BG_HOVER = "#141414"
BORDER   = "#1F1F1F"
RED      = "#E11D48"
TEXT_PRI = "#FAFAFA"
TEXT_SEC = "#A3A3A3"
TEXT_MUT = "#666666"


class ReportsSidebarButton(QPushButton):
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
                font-family: 'Inter';
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


class ReportsView(QWidget):
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

        self.general_view = GeneralReportView()
        self.finance_view = FinanceReportView()
        self.classes_view = ClassesReportView()
        self.students_view = StudentsReportView()
        self.events_view = EventsReportView()

        self.stack.addWidget(self.general_view)
        self.stack.addWidget(self.finance_view)
        self.stack.addWidget(self.classes_view)
        self.stack.addWidget(self.students_view)
        self.stack.addWidget(self.events_view)

        main = QFrame()
        main.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_MAIN};
                border: none;
            }}
        """)
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.stack)
        root.addWidget(main, 1)

        self.btn_general.setChecked(True)
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
        side_layout.setContentsMargins(20, 24, 20, 24)
        side_layout.setSpacing(10)

        title = QLabel(tr("reports.title"))
        title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: 900;
            font-family: 'Inter';
        """)

        subtitle = QLabel(tr("reports.subtitle"))
        subtitle.setStyleSheet("""
            color: #666666;
            font-size: 10px;
            font-weight: 900;
            font-family: 'Inter';
            letter-spacing: 1.4px;
        """)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"""
            background-color: {BORDER};
            border: none;
        """)

        side_layout.addWidget(title)
        side_layout.addWidget(subtitle)
        side_layout.addSpacing(16)
        side_layout.addWidget(sep)
        side_layout.addSpacing(8)

        self.btn_general = ReportsSidebarButton("\U0001f4ca " + tr("reports.general"))
        self.btn_finance = ReportsSidebarButton("\U0001f4b0 " + tr("reports.finance"))
        self.btn_classes = ReportsSidebarButton("\U0001f3eb " + tr("reports.classes"))
        self.btn_students = ReportsSidebarButton("\U0001f393 " + tr("reports.students"))
        self.btn_events = ReportsSidebarButton("\U0001f4c5 " + tr("reports.events"))

        self.btn_general.clicked.connect(lambda: self._switch_view("general"))
        self.btn_finance.clicked.connect(lambda: self._switch_view("finance"))
        self.btn_classes.clicked.connect(lambda: self._switch_view("classes"))
        self.btn_students.clicked.connect(lambda: self._switch_view("students"))
        self.btn_events.clicked.connect(lambda: self._switch_view("events"))

        side_layout.addWidget(self.btn_general)
        side_layout.addWidget(self.btn_finance)
        side_layout.addWidget(self.btn_classes)
        side_layout.addWidget(self.btn_students)
        side_layout.addWidget(self.btn_events)
        side_layout.addStretch()

        return sidebar

    def _switch_view(self, view_name: str):
        self.btn_general.setChecked(view_name == "general")
        self.btn_finance.setChecked(view_name == "finance")
        self.btn_classes.setChecked(view_name == "classes")
        self.btn_students.setChecked(view_name == "students")
        self.btn_events.setChecked(view_name == "events")

        idx = {"general": 0, "finance": 1, "classes": 2,
               "students": 3, "events": 4}.get(view_name, 0)
        self.stack.setCurrentIndex(idx)

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
        self._blur_anim.setBlurRadius(14)
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
