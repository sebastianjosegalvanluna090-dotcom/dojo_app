from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QFrame, QDateEdit, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QColor

from repositories.user_repository import UserRepository

# ─── PALETA ───────────────────────────────────────────────────────────
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
YELLOW       = "#EAB308"

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
    QLineEdit, QDateEdit {{
        background-color: {INPUT_BG};
        color: {TEXT_PRI};
        border: 1.5px solid {INPUT_BORDER};
        border-radius: 8px;
        padding: 0 14px;
        font-size: 13px;
        min-height: 40px;
    }}
    QLineEdit:focus, QDateEdit:focus {{
        border: 1.5px solid {RED};
        background-color: #1A1010;
    }}
    QDateEdit::up-button, QDateEdit::down-button {{ width: 0; }}
"""


class RegisterView(QWidget):
    def __init__(self, on_success=None, on_back=None):
        super().__init__()
        self.repo       = UserRepository()
        self.on_success = on_success
        self.on_back    = on_back
        self._code_data = None  # resultado de validate_code

        self.setWindowTitle("Senshi Fight Academy — Registro")
        self.setFixedSize(460, 680)
        self.setStyleSheet(f"background-color: {BG_DARK};")

        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = self._make_card()
        root.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def _make_card(self):
        card = QFrame()
        card.setFixedSize(400, 640)
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
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(12)

        # ── Encabezado
        icon = QLabel("⚔")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(f"font-size: 30px; color: {RED}; background: transparent; border: none;")
        layout.addWidget(icon)

        title = QLabel("CREAR CUENTA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 14px; font-weight: 800;
            letter-spacing: 2px; color: {TEXT_PRI};
            background: transparent; border: none;
        """)
        layout.addWidget(title)

        # ── Separador
        layout.addWidget(self._divider())

        # ── PASO 1: Código de invitación
        lbl_code = self._field_label("CÓDIGO DE INVITACIÓN")
        layout.addWidget(lbl_code)

        code_row = QHBoxLayout()
        code_row.setSpacing(8)
        self.inp_code = QLineEdit()
        self.inp_code.setPlaceholderText("Ej: Kyokushin4life")
        self.inp_code.setStyleSheet(INPUT_STYLE)
        self.inp_code.setFixedHeight(42)

        self.btn_validate = QPushButton("Verificar")
        self.btn_validate.setFixedSize(90, 42)
        self.btn_validate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_validate.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED}; color: white;
                border: none; border-radius: 8px; font-size: 12px; font-weight: 700;
            }}
            QPushButton:hover {{ background-color: #E8152F; }}
        """)
        self.btn_validate.clicked.connect(self._validate_code)
        self.inp_code.returnPressed.connect(self._validate_code)

        code_row.addWidget(self.inp_code)
        code_row.addWidget(self.btn_validate)
        layout.addLayout(code_row)

        # Badge de rol detectado
        self.lbl_role_badge = QLabel("")
        self.lbl_role_badge.setFixedHeight(32)
        self.lbl_role_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_role_badge.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.lbl_role_badge)

        # ── PASO 2: Datos personales (oculto hasta validar código)
        self.form_widget = QWidget()
        self.form_widget.setStyleSheet("background: transparent;")
        form_layout = QVBoxLayout(self.form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(8)

        form_layout.addWidget(self._field_label("NOMBRE"))
        self.inp_first = QLineEdit()
        self.inp_first.setPlaceholderText("Nombre")
        self.inp_first.setStyleSheet(INPUT_STYLE)
        form_layout.addWidget(self.inp_first)

        form_layout.addWidget(self._field_label("APELLIDO"))
        self.inp_last = QLineEdit()
        self.inp_last.setPlaceholderText("Apellido")
        self.inp_last.setStyleSheet(INPUT_STYLE)
        form_layout.addWidget(self.inp_last)

        form_layout.addWidget(self._field_label("EMAIL"))
        self.inp_email = QLineEdit()
        self.inp_email.setPlaceholderText("correo@ejemplo.com")
        self.inp_email.setStyleSheet(INPUT_STYLE)
        form_layout.addWidget(self.inp_email)

        form_layout.addWidget(self._field_label("USUARIO"))
        self.inp_user = QLineEdit()
        self.inp_user.setPlaceholderText("nombre_usuario")
        self.inp_user.setStyleSheet(INPUT_STYLE)
        form_layout.addWidget(self.inp_user)

        form_layout.addWidget(self._field_label("CONTRASEÑA"))
        self.inp_pass = QLineEdit()
        self.inp_pass.setPlaceholderText("Mínimo 6 caracteres")
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_pass.setStyleSheet(INPUT_STYLE)
        self.inp_pass.returnPressed.connect(self._register)
        form_layout.addWidget(self.inp_pass)

        self.form_widget.setVisible(False)
        layout.addWidget(self.form_widget)

        # ── Mensaje de estado
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet(
            f"color: {ERROR_C}; font-size: 12px; background: transparent; border: none;"
        )
        layout.addWidget(self.lbl_status)

        layout.addStretch()

        # ── Botón registrar
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
        layout.addWidget(self.btn_register)

        # ── Volver al login
        btn_back = QPushButton("← Volver al inicio de sesión")
        btn_back.setFixedHeight(36)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUT};
                border: none; font-size: 12px;
            }}
            QPushButton:hover {{ color: {TEXT_PRI}; }}
        """)
        btn_back.clicked.connect(self._go_back)
        layout.addWidget(btn_back)

        return card

    # ── Helpers UI ────────────────────────────────────────────────────
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
        lbl.setStyleSheet(f"""
            font-size: 10px; font-weight: 700;
            letter-spacing: 1px; color: {TEXT_MUT};
            background: transparent; border: none;
        """)
        return lbl

    def _set_status(self, msg, color=None):
        c = color or ERROR_C
        self.lbl_status.setStyleSheet(
            f"color: {c}; font-size: 12px; background: transparent; border: none;"
        )
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
            self._set_status("❌  Código inválido. Verifica e intenta de nuevo.")
            self.lbl_role_badge.setText("")
            self.form_widget.setVisible(False)
            self.btn_register.setVisible(False)
            self._code_data = None
            return

        self._code_data = result
        role_name = result["role_name"]
        color = ROLE_COLORS.get(role_name, RED)
        icon  = ROLE_ICONS.get(role_name, "👤")

        self.lbl_role_badge.setText(f"{icon}  Rol detectado: {role_name.upper()}")
        self.lbl_role_badge.setStyleSheet(f"""
            background-color: transparent;
            color: {color};
            font-size: 13px; font-weight: 700;
            border: 1px solid {color};
            border-radius: 8px;
            padding: 4px 0;
        """)

        self.inp_code.setEnabled(False)
        self.btn_validate.setEnabled(False)
        self.form_widget.setVisible(True)
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

        # Validaciones
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

        # Validar email
        if self.repo.email_exists(email):
            self._set_status("⚠  Este email ya está registrado.")
            return

        # Validar username
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
            user_id = self.repo.create_user(data)
            self._set_status("✓  ¡Cuenta creada exitosamente!", color=SUCCESS_C)

            # Cerrar después de 1.5s
            if self.on_success:
                QTimer.singleShot(1500, lambda: self.on_success(user_id))
            else:
                QTimer.singleShot(1500, self.close)

        except Exception as e:
            self._set_status(f"Error: {str(e)[:100]}")
            self.btn_register.setEnabled(True)
            self.btn_register.setText("CREAR CUENTA")

    def _go_back(self):
        if self.on_back:
            self.on_back()
        else:
            self.close()
