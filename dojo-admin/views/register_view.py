from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QFrame, QScrollArea, QDateEdit,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QColor

from core.i18n import tr
from repositories.user_repository import UserRepository
from repositories.recovery_repository import RecoveryRepository
from views.widgets.floating_input import FloatingInput
from views.widgets.password_strength import PasswordStrengthWidget


BG_DARK  = "#0D0D0D"
CARD_BG  = "#161616"
BORDER   = "#2A2A2A"
RED      = "#C8102E"
TEXT_PRI = "#F0F0F0"
TEXT_MUT = "#666666"
ERROR_C  = "#FF4444"
SUCCESS_C = "#22C55E"

ROLE_COLORS = {
    "admin":      "#A855F7",
    "acudent":    "#3B82F6",
    "visit":      "#6B7280",
    "instructor": "#F97316",
    "student":    "#22C55E",
}
ROLE_ICONS = {
    "admin":      "👑",
    "acudent":    "👨‍👧",
    "visit":      "👁️",
    "instructor": "🥋",
    "student":    "🎓",
}


class RegisterView(QWidget):
    def __init__(self, on_success=None, on_back=None):
        super().__init__()
        self.repo      = UserRepository()
        self.recovery  = RecoveryRepository()
        self.on_success = on_success
        self.on_back    = on_back
        self._code_data = None

        self.setWindowTitle(tr("auth.register_title"))
        self.setFixedSize(500, 750)
        self.setStyleSheet(f"background-color: {BG_DARK};")
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setStyleSheet(f"background-color: {BG_DARK};")
        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(40, 36, 40, 36)
        vbox.setSpacing(0)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)

        icon = QLabel("⚔")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(f"font-size: 32px; color: {RED};")
        vbox.addWidget(icon)
        vbox.addSpacing(6)

        title = QLabel(tr("auth.register_title"))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-size: 14px; font-weight: 800; letter-spacing: 2px; color: {TEXT_PRI};")
        vbox.addWidget(title)
        vbox.addSpacing(16)

        vbox.addWidget(self._divider())
        vbox.addSpacing(20)

        vbox.addWidget(self._field_label(tr("auth.invitation_code")))
        vbox.addSpacing(6)

        code_row = QHBoxLayout()
        code_row.setSpacing(8)
        self.inp_code = QLineEdit()
        self.inp_code.setPlaceholderText(tr("auth.code_placeholder"))
        self.inp_code.setStyleSheet(f"""
            QLineEdit {{
                background-color: #1E1E1E; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 12px;
                padding: 0 14px; font-size: 13px;
                min-height: 38px; max-height: 38px;
            }}
            QLineEdit:focus {{ border: 1.5px solid {RED}; background-color: #1A1010; }}
        """)
        self.btn_validate = QPushButton(tr("auth.verify"))
        self.btn_validate.setFixedSize(90, 38)
        self.btn_validate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_validate.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED}; color: white;
                border: none; border-radius: 10px;
                font-size: 12px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: #E8152F; }}
        """)
        self.btn_validate.clicked.connect(self._validate_code)
        self.inp_code.returnPressed.connect(self._validate_code)
        code_row.addWidget(self.inp_code)
        code_row.addWidget(self.btn_validate)
        vbox.addLayout(code_row)
        vbox.addSpacing(10)

        self.lbl_role_badge = QLabel("")
        self.lbl_role_badge.setFixedHeight(36)
        self.lbl_role_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_role_badge.setStyleSheet("background: transparent;")
        vbox.addWidget(self.lbl_role_badge)
        vbox.addSpacing(6)

        self.sep2 = self._divider()
        self.sep2.setVisible(False)
        vbox.addWidget(self.sep2)
        vbox.addSpacing(4)

        self.fields_widget = QWidget()
        self.fields_widget.setStyleSheet("background: transparent;")
        fields_vbox = QVBoxLayout(self.fields_widget)
        fields_vbox.setContentsMargins(0, 0, 0, 0)
        fields_vbox.setSpacing(0)

        self.inp_first = FloatingInput(tr("auth.first_name"))
        self.inp_last  = FloatingInput(tr("auth.last_name"))
        self.inp_email = FloatingInput(tr("auth.email"))
        self.inp_user  = FloatingInput(tr("auth.username"))
        self.inp_birthdate = QDateEdit()
        self.inp_birthdate.setCalendarPopup(True)
        self.inp_birthdate.setDate(QDate(2000, 1, 1))
        self.inp_birthdate.setFixedHeight(44)
        self.inp_birthdate.setStyleSheet(f"""
            QDateEdit {{
                background-color: #1E1E1E; color: {TEXT_PRI};
                border: 1.5px solid {BORDER}; border-radius: 12px;
                padding: 0 14px; font-size: 13px;
            }}
            QDateEdit:focus {{ border-color: {RED}; }}
            QCalendarWidget {{ background-color: {CARD_BG}; color: {TEXT_PRI}; }}
        """)

        self.inp_pass = FloatingInput(tr("auth.password"), password=True)
        self.inp_confirm = FloatingInput(tr("auth.confirm_password"), password=True)
        self.inp_security = FloatingInput(tr("auth.security_word"))

        self.pw_strength = PasswordStrengthWidget()
        self.inp_pass.textChanged.connect(self._on_pass_changed)

        def add_floating(label_text, widget):
            fields_vbox.addWidget(self._field_label(label_text))
            fields_vbox.addSpacing(4)
            fields_vbox.addWidget(widget)
            fields_vbox.addSpacing(12)

        add_floating(tr("auth.first_name"), self.inp_first)
        add_floating(tr("auth.last_name"), self.inp_last)
        add_floating(tr("auth.email"), self.inp_email)
        add_floating(tr("auth.username"), self.inp_user)

        bd_container = QWidget()
        bd_container.setStyleSheet("background: transparent;")
        bd_v = QVBoxLayout(bd_container)
        bd_v.setContentsMargins(0, 0, 0, 0)
        bd_v.setSpacing(0)
        bd_v.addWidget(self._field_label(tr("auth.birthdate")))
        bd_v.addSpacing(5)
        bd_v.addWidget(self.inp_birthdate)
        fields_vbox.addWidget(bd_container)
        fields_vbox.addSpacing(12)

        add_floating(tr("auth.password"), self.inp_pass)
        fields_vbox.addWidget(self.pw_strength)
        fields_vbox.addSpacing(4)
        add_floating(tr("auth.confirm_password"), self.inp_confirm)
        add_floating(tr("auth.security_word"), self.inp_security)

        self.inp_security.line_edit().returnPressed.connect(self._register)

        self.fields_widget.setVisible(False)
        vbox.addWidget(self.fields_widget)

        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet(f"color: {ERROR_C}; font-size: 12px; background: transparent; border: none;")
        vbox.addWidget(self.lbl_status)
        vbox.addSpacing(12)

        self.btn_register = QPushButton(tr("auth.create_account"))
        self.btn_register.setFixedHeight(44)
        self.btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_register.setVisible(False)
        self.btn_register.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED}; color: white;
                border: none; border-radius: 12px;
                font-size: 13px; font-weight: 700; letter-spacing: 1px;
            }}
            QPushButton:hover {{ background-color: #E8152F; }}
            QPushButton:pressed {{ background-color: #A00C24; }}
            QPushButton:disabled {{ background-color: #3A1A1A; color: #666; }}
        """)
        self.btn_register.clicked.connect(self._register)
        vbox.addWidget(self.btn_register)
        vbox.addSpacing(10)

        btn_back = QPushButton("←  " + tr("auth.back_to_login"))
        btn_back.setFixedHeight(36)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_MUT}; border: none; font-size: 12px; }}
            QPushButton:hover {{ color: {TEXT_PRI}; }}
        """)
        btn_back.clicked.connect(self._go_back)
        vbox.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignCenter)

        scroll.setWidget(content)
        root.addWidget(scroll)

    def _on_pass_changed(self, text):
        texts = [
            tr("auth.req_length"),
            tr("auth.req_uppercase"),
            tr("auth.req_lowercase"),
            tr("auth.req_number"),
            tr("auth.req_symbol"),
        ]
        self.pw_strength.set_texts(
            tr("auth.password_requirements"), texts,
            tr("auth.password_weak"), tr("auth.password_medium"),
            tr("auth.password_strong"), tr("auth.password_very_strong"),
        )
        self.pw_strength.update_password(text)

    def _divider(self):
        line = QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 transparent, stop:0.3 {RED},
                stop:0.7 {RED}, stop:1 transparent);
            border: none;
        """)
        return line

    def _field_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 10px; font-weight: 700; letter-spacing: 1px; color: {TEXT_MUT};")
        return lbl

    def _set_status(self, msg, color=None):
        self.lbl_status.setStyleSheet(f"color: {color or ERROR_C}; font-size: 12px; background: transparent; border: none;")
        self.lbl_status.setText(msg)

    def _validate_code(self):
        code = self.inp_code.text().strip()
        if not code:
            self._set_status(tr("auth.code_required"))
            return
        self._set_status("")
        result = self.repo.validate_code(code)
        if not result:
            self._set_status("❌  " + tr("auth.invalid_code"))
            self.lbl_role_badge.setText("")
            self.fields_widget.setVisible(False)
            self.btn_register.setVisible(False)
            self.sep2.setVisible(False)
            self._code_data = None
            return

        self._code_data = result
        role_name = result["role_name"]
        color = ROLE_COLORS.get(role_name, RED)
        icon  = ROLE_ICONS.get(role_name, "👤")

        self.lbl_role_badge.setText(f"{icon}  {tr('auth.role_detected')}: {role_name.upper()}")
        self.lbl_role_badge.setStyleSheet(f"""
            color: {color}; font-size: 13px; font-weight: 700;
            border: 1px solid {color}; border-radius: 8px; padding: 4px 0;
        """)
        self.inp_code.setEnabled(False)
        self.btn_validate.setEnabled(False)
        self.sep2.setVisible(True)
        self.fields_widget.setVisible(True)
        self.btn_register.setVisible(True)
        self.inp_first.setFocus()
        self._set_status("✓  " + tr("auth.code_valid"), color=SUCCESS_C)

    def _register(self):
        if not self._code_data:
            return

        first  = self.inp_first.text().strip()
        last   = self.inp_last.text().strip()
        email  = self.inp_email.text().strip()
        user   = self.inp_user.text().strip()
        pwd    = self.inp_pass.text()
        confirm = self.inp_confirm.text()
        security = self.inp_security.text().strip()

        if not first or not last:
            self._set_status(tr("auth.name_required"))
            return
        if not user:
            self._set_status(tr("auth.username_required"))
            return
        if not pwd:
            self._set_status(tr("auth.password_required"))
            return
        if not self.pw_strength.is_valid():
            self._set_status(tr("auth.password_not_secure"))
            return
        if pwd != confirm:
            self._set_status(tr("auth.passwords_do_not_match"))
            return
        if not email:
            self._set_status(tr("auth.email_required"))
            return
        if not security:
            self._set_status(tr("auth.security_word_required"))
            return

        if self.repo.email_exists(email):
            self._set_status(tr("auth.email_exists"))
            return
        if self.repo.username_exists(user):
            self._set_status(tr("auth.username_exists"))
            return

        self.btn_register.setEnabled(False)
        self.btn_register.setText(tr("auth.registering"))
        self._set_status("")

        try:
            data = {
                "first_name":    first,
                "last_name":     last,
                "email":         email,
                "username":      user,
                "password":      pwd,
                "id_code_users": self._code_data["id"],
                "id_role":       self._code_data["id_role"],
                "phone":         None,
                "birthdate":     self.inp_birthdate.date().toPyDate(),
            }
            user_id = self.repo.create_user(data)
            self.recovery.save_recovery_data(
                user_id=user_id,
                birthdate=self.inp_birthdate.date().toPyDate(),
                security_word=security,
            )
            self._set_status("✓  " + tr("auth.account_created"), color=SUCCESS_C)
            QTimer.singleShot(1200, self._go_back)
        except Exception as e:
            self._set_status(f"Error: {str(e)[:100]}")
            self.btn_register.setEnabled(True)
            self.btn_register.setText(tr("auth.create_account"))

    def _go_back(self):
        if self.on_back:
            self.on_back()
        self.close()
