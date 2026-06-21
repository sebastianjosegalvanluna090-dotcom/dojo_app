from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QFrame, QScrollArea, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

from repositories.user_repository import UserRepository

BG_DARK      = "#0D0D0D"
CARD_BG      = "#161616"
BORDER       = "#2A2A2A"
INPUT_BG     = "#1E1E1E"
INPUT_BORDER = "#333333"
RED          = "#C8102E"
TEXT_PRI     = "#F0F0F0"
TEXT_MUT     = "#666666"
ERROR_C      = "#FF4444"
SUCCESS_C    = "#22C55E"

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

INPUT_STYLE = f"""
    QLineEdit {{
        background-color: {INPUT_BG};
        color: {TEXT_PRI};
        border: 1.5px solid {INPUT_BORDER};
        border-radius: 8px;
        padding: 0 14px;
        font-size: 13px;
        min-height: 38px;
        max-height: 38px;
    }}
    QLineEdit:focus {{
        border: 1.5px solid {RED};
        background-color: #1A1010;
    }}
"""

class RegisterView(QWidget):
    def __init__(self, on_success=None, on_back=None):
        super().__init__()
        self.repo       = UserRepository()
        self.on_success = on_success
        self.on_back    = on_back
        self._code_data = None

        self.setWindowTitle("Senshi Fight Academy — Registro")
        self.setFixedSize(480, 700)
        self.setStyleSheet(f"background-color: {BG_DARK};")
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # Scroll area que ocupa toda la ventana
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

        # ── Ícono y título
        icon = QLabel("⚔")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(f"font-size: 32px; color: {RED};")
        vbox.addWidget(icon)
        vbox.addSpacing(6)

        title = QLabel("CREAR CUENTA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-size: 14px; font-weight: 800; letter-spacing: 2px; color: {TEXT_PRI};")
        vbox.addWidget(title)
        vbox.addSpacing(16)

        # ── Separador
        vbox.addWidget(self._divider())
        vbox.addSpacing(20)

        # ── Código de invitación
        vbox.addWidget(self._field_label("CÓDIGO DE INVITACIÓN"))
        vbox.addSpacing(6)

        code_row = QHBoxLayout()
        code_row.setSpacing(8)
        self.inp_code = QLineEdit()
        self.inp_code.setPlaceholderText("Ej: ABC123")
        self.inp_code.setStyleSheet(INPUT_STYLE)
        self.btn_validate = QPushButton("Verificar")
        self.btn_validate.setFixedSize(90, 38)
        self.btn_validate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_validate.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED}; color: white;
                border: none; border-radius: 8px;
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

        # ── Badge de rol
        self.lbl_role_badge = QLabel("")
        self.lbl_role_badge.setFixedHeight(36)
        self.lbl_role_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_role_badge.setStyleSheet("background: transparent;")
        vbox.addWidget(self.lbl_role_badge)
        vbox.addSpacing(6)

        # ── Separador 2
        self.sep2 = self._divider()
        self.sep2.setVisible(False)
        vbox.addWidget(self.sep2)
        vbox.addSpacing(4)

        # ── Campos del formulario (visibles tras validar código)
        self.fields_widget = QWidget()
        self.fields_widget.setStyleSheet("background: transparent;")
        fields_vbox = QVBoxLayout(self.fields_widget)
        fields_vbox.setContentsMargins(0, 0, 0, 0)
        fields_vbox.setSpacing(0)

        def add_field(label, widget):
            fields_vbox.addWidget(self._field_label(label))
            fields_vbox.addSpacing(5)
            fields_vbox.addWidget(widget)
            fields_vbox.addSpacing(14)

        self.inp_first = QLineEdit(); self.inp_first.setPlaceholderText("Nombre"); self.inp_first.setStyleSheet(INPUT_STYLE)
        self.inp_last  = QLineEdit(); self.inp_last.setPlaceholderText("Apellido"); self.inp_last.setStyleSheet(INPUT_STYLE)
        self.inp_email = QLineEdit(); self.inp_email.setPlaceholderText("correo@ejemplo.com"); self.inp_email.setStyleSheet(INPUT_STYLE)
        self.inp_user  = QLineEdit(); self.inp_user.setPlaceholderText("nombre_usuario"); self.inp_user.setStyleSheet(INPUT_STYLE)
        self.inp_pass  = QLineEdit(); self.inp_pass.setPlaceholderText("Mínimo 6 caracteres")
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pass.setStyleSheet(INPUT_STYLE)
        self.inp_pass.returnPressed.connect(self._register)

        add_field("NOMBRE",     self.inp_first)
        add_field("APELLIDO",   self.inp_last)
        add_field("EMAIL",      self.inp_email)
        add_field("USUARIO",    self.inp_user)
        add_field("CONTRASEÑA", self.inp_pass)

        self.fields_widget.setVisible(False)
        vbox.addWidget(self.fields_widget)

        # ── Estado
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet(f"color: {ERROR_C}; font-size: 12px;")
        vbox.addWidget(self.lbl_status)
        vbox.addSpacing(16)

        # ── Botón crear cuenta
        self.btn_register = QPushButton("CREAR CUENTA")
        self.btn_register.setFixedHeight(44)
        self.btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_register.setVisible(False)
        self.btn_register.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED}; color: white;
                border: none; border-radius: 8px;
                font-size: 13px; font-weight: 700; letter-spacing: 1px;
            }}
            QPushButton:hover {{ background-color: #E8152F; }}
            QPushButton:pressed {{ background-color: #A00C24; }}
            QPushButton:disabled {{ background-color: #3A1A1A; color: #666; }}
        """)
        self.btn_register.clicked.connect(self._register)
        vbox.addWidget(self.btn_register)
        vbox.addSpacing(10)

        # ── Volver
        btn_back = QPushButton("← Volver al inicio de sesión")
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

    # ── Helpers ───────────────────────────────────────────────────────
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
        self.lbl_status.setStyleSheet(f"color: {color or ERROR_C}; font-size: 12px;")
        self.lbl_status.setText(msg)

    # ── Lógica ────────────────────────────────────────────────────────
    def _validate_code(self):
        code = self.inp_code.text().strip()
        if not code:
            self._set_status("Ingresa un código de invitación.")
            return
        self._set_status("")
        result = self.repo.validate_code(code)
        if not result:
            self._set_status("❌  Código inválido.")
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

        self.lbl_role_badge.setText(f"{icon}  Rol detectado: {role_name.upper()}")
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
        self._set_status("✓  Código válido. Completa tus datos.", color=SUCCESS_C)

    def _register(self):
        if not self._code_data:
            return
        first = self.inp_first.text().strip()
        last  = self.inp_last.text().strip()
        email = self.inp_email.text().strip()
        user  = self.inp_user.text().strip()
        pwd   = self.inp_pass.text()

        if not first or not last:
            self._set_status("⚠  Nombre y apellido son obligatorios.")
            return
        if not user:
            self._set_status("⚠  El nombre de usuario es obligatorio.")
            return
        if len(pwd) < 6:
            self._set_status("⚠  La contraseña debe tener al menos 6 caracteres.")
            return
        if not email:
            self._set_status("⚠  El email es obligatorio.")
            return

        # Validar duplicados
        if self.repo.email_exists(email):
            self._set_status("⚠  Este email ya está registrado.")
            return
        if self.repo.username_exists(user):
            self._set_status("⚠  Este usuario ya existe.")
            return

        # Crear usuario
        self.btn_register.setEnabled(False)
        self.btn_register.setText("Registrando...")
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
                "birthdate":     None,
            }
            self.repo.create_user(data)
            self._set_status("✓  ¡Cuenta creada exitosamente!", color=SUCCESS_C)
            QTimer.singleShot(1200, self._go_back)

        except Exception as e:
            self._set_status(f"Error: {str(e)[:100]}")
            self.btn_register.setEnabled(True)
            self.btn_register.setText("CREAR CUENTA")

    def _go_back(self):
        if self.on_back:
            self.on_back()
        self.close()
