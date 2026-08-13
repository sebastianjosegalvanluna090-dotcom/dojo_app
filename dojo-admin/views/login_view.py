#login_view.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QBrush, QLinearGradient

from core.i18n import tr
from views.widgets.floating_input import FloatingInput
from views.widgets.password_toggle import PasswordToggleButton


BG_DARK       = "#0D0D0D"
CARD_BG       = "#161616"
BORDER        = "#2A2A2A"
INPUT_BG      = "#1E1E1E"
INPUT_BORDER  = "#333333"
INPUT_FOCUS   = "#C8102E"
TEXT_PRIMARY  = "#F0F0F0"
TEXT_MUTED    = "#666666"
BTN_RED       = "#C8102E"
BTN_RED_HOVER = "#E8152F"
BTN_RED_PRESS = "#A00C24"
ERROR_COLOR   = "#FF4444"
SUCCESS_COLOR = "#22C55E"


class LoginView(QWidget):
    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self._setup_window()
        self._build_ui()

    def _setup_window(self):
        self.setWindowTitle("Senshi Fight Academy")
        self.setFixedSize(420, 580)
        self.setStyleSheet(f"background-color: {BG_DARK};")

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = self._make_card()
        root.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def _make_card(self):
        card = QFrame()
        card.setFixedSize(360, 540)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 180))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 36, 32, 36)
        layout.setSpacing(0)

        layout.addWidget(self._make_header())
        layout.addSpacing(20)

        layout.addWidget(self._make_divider())
        layout.addSpacing(20)

        self.username_input = FloatingInput(tr("auth.username"))
        layout.addWidget(self.username_input)
        layout.addSpacing(8)

        self.password_toggle = PasswordToggleButton()
        self.password_toggle.toggledVisible.connect(self._toggle_password_visibility)
        self.password_input = FloatingInput(tr("auth.password"), password=True, right_widget=self.password_toggle)
        layout.addWidget(self.password_input)
        layout.addSpacing(4)

        self.password_input.line_edit().returnPressed.connect(self._do_login)

        self.btn_forgot = QPushButton(tr("auth.forgot_password"))
        self.btn_forgot.setFixedHeight(28)
        self.btn_forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_forgot.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUTED};
                border: none; font-size: 12px; font-weight: 700;
            }}
            QPushButton:hover {{ color: {BTN_RED}; }}
        """)
        self.btn_forgot.clicked.connect(self._open_forgot_password)
        layout.addWidget(self.btn_forgot, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)

        self.btn_login = self._make_button()
        layout.addWidget(self.btn_login)
        layout.addSpacing(12)

        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setFixedHeight(20)
        self.lbl_status.setStyleSheet(f"color: {ERROR_COLOR}; font-size: 12px; background: transparent; border: none;")
        layout.addWidget(self.lbl_status)

        layout.addStretch()

        layout.addWidget(self._make_footer())

        btn_register = QPushButton(tr("auth.register_link"))
        btn_register.setFixedHeight(36)
        btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_register.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUTED};
                border: none; font-size: 12px;
            }}
            QPushButton:hover {{ color: {BTN_RED}; }}
        """)
        btn_register.clicked.connect(self._open_register)
        layout.addWidget(btn_register)

        return card

    def _toggle_password_visibility(self, visible):
        mode = QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
        self.password_input.setEchoMode(mode)

    def _make_header(self):
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_lbl = QLabel("⚔")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"font-size: 36px; color: {BTN_RED}; background: transparent; border: none;")
        v.addWidget(icon_lbl)

        title = QLabel("SENSHI FIGHT ACADEMY")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 14px; font-weight: 800;
            letter-spacing: 2px; color: {TEXT_PRIMARY};
            background: transparent; border: none;
        """)
        v.addWidget(title)

        subtitle = QLabel(tr("auth.management_system"))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED}; background: transparent; border: none;")
        v.addWidget(subtitle)

        return container

    def _make_divider(self):
        line = QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet(f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 transparent, stop:0.3 {BTN_RED},
                stop:0.7 {BTN_RED}, stop:1 transparent
            );
            border: none; border-radius: 1px;
        """)
        return line

    def _make_button(self):
        btn = QPushButton(tr("auth.login"))
        btn.setFixedHeight(46)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BTN_RED}; color: white;
                border: none; border-radius: 12px;
                font-size: 13px; font-weight: 700;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{ background-color: {BTN_RED_HOVER}; }}
            QPushButton:pressed {{ background-color: {BTN_RED_PRESS}; }}
            QPushButton:disabled {{ background-color: #3A1A1A; color: #666666; }}
        """)
        btn.clicked.connect(self._do_login)
        return btn

    def _make_footer(self):
        lbl = QLabel("v1.0.0  ·  Senshi Fight Academy © 2025")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED}; background: transparent; border: none;")
        return lbl

    def _open_register(self):
        from views.register_view import RegisterView
        self.register = RegisterView(on_back=lambda: self.show())
        self.register.show()
        self.hide()

    def _open_forgot_password(self):
        from views.forgot_password_dialog import ForgotPasswordDialog
        dlg = ForgotPasswordDialog(parent=self)
        dlg.exec()

    def _do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username:
            self._set_status(tr("auth.username_required"), error=True)
            self.username_input.setFocus()
            return
        if not password:
            self._set_status(tr("auth.password_required"), error=True)
            self.password_input.setFocus()
            return

        self.btn_login.setEnabled(False)
        self.btn_login.setText(tr("auth.verifying"))
        self._set_status("")

        try:
            user = self.auth_service.login(username, password)
            self._set_status(tr("auth.access_granted"), error=False)
            QTimer.singleShot(800, lambda: self._on_login_success(user))
        except ValueError as e:
            self._set_status(str(e), error=True)
            self._shake_inputs()
        finally:
            self.btn_login.setEnabled(True)
            self.btn_login.setText(tr("auth.login"))

    def _set_status(self, msg, error=True):
        color = ERROR_COLOR if error else SUCCESS_COLOR
        self.lbl_status.setStyleSheet(
            f"color: {color}; font-size: 12px; background: transparent; border: none;"
        )
        self.lbl_status.setText(msg)

    def _shake_inputs(self):
        self.username_input.set_error(True)
        self.password_input.set_error(True)
        QTimer.singleShot(600, lambda: (
            self.username_input.set_error(False),
            self.password_input.set_error(False),
        ))

    def _on_login_success(self, user):
        print(f"[LOGIN OK] usuario={user['username']}  id={user['id']}")
