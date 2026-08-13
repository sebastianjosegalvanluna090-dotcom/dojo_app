from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QStackedWidget, QDateEdit, QMessageBox,
    QGraphicsDropShadowEffect, QWidget,
)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QColor

from core.i18n import tr
from views.widgets.floating_input import FloatingInput
from views.widgets.password_strength import PasswordStrengthWidget
from repositories.recovery_repository import RecoveryRepository


BG_DARK = "#0D0D0D"
CARD_BG = "#161616"
BORDER = "#2A2A2A"
TEXT_PRIMARY = "#F0F0F0"
TEXT_MUTED = "#666666"
BTN_RED = "#C8102E"
BTN_RED_HOVER = "#E8152F"
ERROR_COLOR = "#FF4444"
SUCCESS_COLOR = "#22C55E"


class ForgotPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.repo = RecoveryRepository()
        self._username = ""
        self._setup_window()
        self._build_ui()

    def _setup_window(self):
        self.setWindowTitle(tr("auth.recover_password"))
        self.setFixedSize(420, 580)
        self.setStyleSheet(f"background-color: {BG_DARK};")

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setFixedSize(380, 540)
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
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(0)

        icon_lbl = QLabel("🔐")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"font-size: 32px; background: transparent; border: none;")
        layout.addWidget(icon_lbl)
        layout.addSpacing(6)

        title = QLabel(tr("auth.recover_password"))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 16px; font-weight: 800;
            letter-spacing: 1px; color: {TEXT_PRIMARY};
            background: transparent; border: none;
        """)
        layout.addWidget(title)
        layout.addSpacing(6)

        subtitle = QLabel(tr("auth.choose_recovery_method"))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"""
            font-size: 11px; color: {TEXT_MUTED};
            background: transparent; border: none;
        """)
        layout.addWidget(subtitle)
        layout.addSpacing(16)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: transparent;")

        self._page_select = self._build_page_select()
        self._page_birthdate = self._build_page_birthdate()
        self._page_security_word = self._build_page_security_word()
        self._page_help = self._build_page_help()
        self._page_reset = self._build_page_reset()

        self._stack.addWidget(self._page_select)
        self._stack.addWidget(self._page_birthdate)
        self._stack.addWidget(self._page_security_word)
        self._stack.addWidget(self._page_help)
        self._stack.addWidget(self._page_reset)

        layout.addWidget(self._stack)
        layout.addStretch()

        root.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    # ── Page 0: Method selection ──────────────────────────────────
    def _build_page_select(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        v = QVBoxLayout(page)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        self._sel_user = FloatingInput(tr("auth.username"))
        v.addWidget(self._sel_user)
        v.addSpacing(12)

        v.addWidget(self._method_button(tr("auth.birthdate_verification"), "🎂", self._go_birthdate))
        v.addWidget(self._method_button(tr("auth.security_word_verification"), "🔐", self._go_security_word))
        v.addWidget(self._method_button(tr("auth.contact_help"), "🧑‍💻", self._go_help))

        btn_cancel = QPushButton(tr("auth.back_to_login"))
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUTED};
                border: none; font-size: 12px;
            }}
            QPushButton:hover {{ color: {TEXT_PRIMARY}; }}
        """)
        btn_cancel.clicked.connect(self.reject)
        v.addWidget(btn_cancel)
        return page

    def _method_button(self, text, icon, callback):
        btn = QPushButton(f"  {icon}  {text}")
        btn.setFixedHeight(48)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #1A1A1A;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 12px;
                font-size: 13px;
                font-weight: 600;
                text-align: left;
                padding-left: 12px;
            }}
            QPushButton:hover {{
                border-color: {BTN_RED};
                background-color: #221010;
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    # ── Page 1: Birthdate verification ────────────────────────────
    def _build_page_birthdate(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        v = QVBoxLayout(page)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        lbl = QLabel(tr("auth.birthdate_verification"))
        lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent; border: none;")
        v.addWidget(lbl)
        v.addSpacing(4)

        self._bd_user = FloatingInput(tr("auth.username"))
        v.addWidget(self._bd_user)

        self._bd_picker = QDateEdit()
        self._bd_picker.setCalendarPopup(True)
        self._bd_picker.setDate(QDate(2000, 1, 1))
        self._bd_picker.setFixedHeight(44)
        self._bd_picker.setStyleSheet(f"""
            QDateEdit {{
                background-color: #1A1A1A;
                color: {TEXT_PRIMARY};
                border: 1.5px solid {BORDER};
                border-radius: 12px;
                padding: 0 14px;
                font-size: 13px;
            }}
            QDateEdit:focus {{ border-color: {BTN_RED}; }}
            QCalendarWidget {{ background-color: {CARD_BG}; color: {TEXT_PRIMARY}; }}
        """)
        v.addWidget(self._bd_picker)
        v.addSpacing(4)

        self._lbl_bd_status = QLabel("")
        self._lbl_bd_status.setStyleSheet(f"color: {ERROR_COLOR}; font-size: 11px; background: transparent; border: none;")
        v.addWidget(self._lbl_bd_status)

        btn_verify = QPushButton(tr("auth.verify"))
        btn_verify.setFixedHeight(44)
        btn_verify.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_verify.setStyleSheet(f"""
            QPushButton {{
                background-color: {BTN_RED}; color: white;
                border: none; border-radius: 10px;
                font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: {BTN_RED_HOVER}; }}
        """)
        btn_verify.clicked.connect(self._verify_birthdate)
        v.addWidget(btn_verify)

        btn_back = QPushButton("←  " + tr("auth.back_to_login"))
        btn_back.setFixedHeight(36)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_MUTED}; border: none; font-size: 12px; }}
            QPushButton:hover {{ color: {TEXT_PRIMARY}; }}
        """)
        btn_back.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        v.addWidget(btn_back)

        return page

    # ── Page 2: Security word verification ────────────────────────
    def _build_page_security_word(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        v = QVBoxLayout(page)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        lbl = QLabel(tr("auth.security_word_verification"))
        lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent; border: none;")
        v.addWidget(lbl)
        v.addSpacing(4)

        self._sw_user = FloatingInput(tr("auth.username"))
        v.addWidget(self._sw_user)

        self._sw_input = FloatingInput(tr("auth.security_word"))
        v.addWidget(self._sw_input)

        self._lbl_sw_status = QLabel("")
        self._lbl_sw_status.setStyleSheet(f"color: {ERROR_COLOR}; font-size: 11px; background: transparent; border: none;")
        v.addWidget(self._lbl_sw_status)

        btn_verify = QPushButton(tr("auth.verify"))
        btn_verify.setFixedHeight(44)
        btn_verify.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_verify.setStyleSheet(f"""
            QPushButton {{
                background-color: {BTN_RED}; color: white;
                border: none; border-radius: 10px;
                font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: {BTN_RED_HOVER}; }}
        """)
        btn_verify.clicked.connect(self._verify_security_word)
        v.addWidget(btn_verify)

        btn_back = QPushButton("←  " + tr("auth.back_to_login"))
        btn_back.setFixedHeight(36)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_MUTED}; border: none; font-size: 12px; }}
            QPushButton:hover {{ color: {TEXT_PRIMARY}; }}
        """)
        btn_back.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        v.addWidget(btn_back)

        return page

    # ── Page 3: Contact help ──────────────────────────────────────
    def _build_page_help(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        v = QVBoxLayout(page)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        icon = QLabel("🧑‍💻")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 48px; background: transparent; border: none;")
        v.addWidget(icon)
        v.addSpacing(12)

        msg = QLabel(tr("auth.help_message"))
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        msg.setStyleSheet(f"font-size: 13px; color: {TEXT_PRIMARY}; background: transparent; border: none;")
        v.addWidget(msg)

        v.addStretch()

        btn_back = QPushButton(tr("auth.back_to_login"))
        btn_back.setFixedHeight(44)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet(f"""
            QPushButton {{
                background-color: {BTN_RED}; color: white;
                border: none; border-radius: 10px;
                font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: {BTN_RED_HOVER}; }}
        """)
        btn_back.clicked.connect(self.reject)
        v.addWidget(btn_back)

        return page

    # ── Page 4: Reset password ────────────────────────────────────
    def _build_page_reset(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        v = QVBoxLayout(page)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)

        icon = QLabel("🔑")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 32px; background: transparent; border: none;")
        v.addWidget(icon)
        v.addSpacing(4)

        lbl = QLabel(tr("auth.reset_password"))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"font-size: 14px; font-weight: 800; color: {TEXT_PRIMARY}; background: transparent; border: none;")
        v.addWidget(lbl)
        v.addSpacing(8)

        self._reset_pass = FloatingInput(tr("auth.new_password"), password=True)
        v.addWidget(self._reset_pass)

        self._reset_confirm = FloatingInput(tr("auth.confirm_password"), password=True)
        v.addWidget(self._reset_confirm)

        self._pw_strength = PasswordStrengthWidget()
        v.addWidget(self._pw_strength)
        self._reset_pass.textChanged.connect(self._on_reset_pass_changed)

        self._lbl_reset_status = QLabel("")
        self._lbl_reset_status.setStyleSheet(f"color: {ERROR_COLOR}; font-size: 11px; background: transparent; border: none;")
        v.addWidget(self._lbl_reset_status)

        btn_save = QPushButton(tr("auth.reset_password"))
        btn_save.setFixedHeight(44)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {BTN_RED}; color: white;
                border: none; border-radius: 10px;
                font-size: 13px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: {BTN_RED_HOVER}; }}
        """)
        btn_save.clicked.connect(self._do_reset_password)
        v.addWidget(btn_save)

        return page

    # ── Navigation methods ────────────────────────────────────────
    def _go_birthdate(self):
        self._username = self._sel_user.text().strip()
        if not self._username:
            self._sel_user.set_error(tr("auth.username_required"))
            return
        self._sel_user.set_error("")
        self._bd_user.setText(self._username)
        self._stack.setCurrentIndex(1)

    def _go_security_word(self):
        self._username = self._sel_user.text().strip()
        if not self._username:
            self._sel_user.set_error(tr("auth.username_required"))
            return
        self._sel_user.set_error("")
        self._sw_user.setText(self._username)
        self._stack.setCurrentIndex(2)

    def _go_help(self):
        self._stack.setCurrentIndex(3)

    def _verify_birthdate(self):
        username = self._bd_user.text().strip()
        if not username:
            self._lbl_bd_status.setText(tr("auth.username_required"))
            return
        qdate = self._bd_picker.date()
        bd = qdate.toPyDate()
        try:
            ok = self.repo.verify_birthdate(username, bd)
        except Exception:
            ok = False
        if ok:
            self._username = username
            self._stack.setCurrentIndex(4)
        else:
            self._lbl_bd_status.setText(tr("auth.invalid_recovery_data"))

    def _verify_security_word(self):
        username = self._sw_user.text().strip()
        word = self._sw_input.text()
        if not username or not word:
            self._lbl_sw_status.setText(tr("auth.invalid_recovery_data"))
            return
        try:
            ok = self.repo.verify_security_word(username, word)
        except Exception:
            ok = False
        if ok:
            self._username = username
            self._stack.setCurrentIndex(4)
        else:
            self._lbl_sw_status.setText(tr("auth.invalid_recovery_data"))

    def _on_reset_pass_changed(self, text):
        self._pw_strength.update_password(text)

    def _do_reset_password(self):
        pwd = self._reset_pass.text()
        confirm = self._reset_confirm.text()

        if not pwd:
            self._lbl_reset_status.setText(tr("auth.password_required"))
            return
        if not self._pw_strength.is_valid():
            self._lbl_reset_status.setText(tr("auth.password_not_secure"))
            return
        if pwd != confirm:
            self._lbl_reset_status.setText(tr("auth.passwords_do_not_match"))
            return

        try:
            self.repo.reset_password(self._username, pwd)
            QMessageBox.information(self, "", tr("auth.password_updated"))
            self.accept()
        except Exception as e:
            self._lbl_reset_status.setText(f"Error: {str(e)[:80]}")
