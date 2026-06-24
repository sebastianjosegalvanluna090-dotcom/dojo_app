# ─── LOGIN_VIEW ─────────────────────────────────────────────

import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QBrush, QLinearGradient


# ─── PALETA DE COLORES ────────────────────────────────────────────────
BG_DARK       = "#0D0D0D"   # fondo exterior
CARD_BG       = "#161616"   # tarjeta login
BORDER        = "#2A2A2A"   # bordes sutiles
INPUT_BG      = "#1E1E1E"   # fondo inputs
INPUT_BORDER  = "#333333"
INPUT_FOCUS   = "#C8102E"   # rojo Senshi (acento principal)
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

    # ── Ventana ──────────────────────────────────────────────────────
    def _setup_window(self):
        self.setWindowTitle("Senshi Fight Academy")
        self.setFixedSize(420, 560)
        self.setStyleSheet(f"background-color: {BG_DARK};")

    # ── UI principal ─────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = self._make_card()
        root.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    # ── Tarjeta central ──────────────────────────────────────────────
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

        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 180))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 36, 40, 36)
        layout.setSpacing(0)

        # Logo / cabecera
        layout.addWidget(self._make_header())
        layout.addSpacing(28)

        # Separador
        layout.addWidget(self._make_divider())
        layout.addSpacing(24)

        # Campos
        self.input_user = self._make_input("Usuario", False)
        self.input_pass = self._make_input("Contraseña", True)
        layout.addWidget(self._make_field_label("Usuario"))
        layout.addSpacing(6)
        layout.addWidget(self.input_user)
        layout.addSpacing(16)
        layout.addWidget(self._make_field_label("Contraseña"))
        layout.addSpacing(6)
        layout.addWidget(self.input_pass)
        layout.addSpacing(24)

        # Botón
        self.btn_login = self._make_button()
        layout.addWidget(self.btn_login)
        layout.addSpacing(16)

        # Mensaje de estado
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setFixedHeight(20)
        self.lbl_status.setStyleSheet(f"color: {ERROR_COLOR}; font-size: 12px; background: transparent; border: none;")
        layout.addWidget(self.lbl_status)

        layout.addStretch()

        # Footer
        layout.addWidget(self._make_footer())

        # ── Botón registrarse
        btn_register = QPushButton("¿Tienes un código? Regístrate")
        btn_register.setFixedHeight(36)
        btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_register.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_MUTED};
                border: none;
                font-size: 12px;
            }}
            QPushButton:hover {{ color: {BTN_RED}; }}
        """)
        btn_register.clicked.connect(self._open_register)
        layout.addWidget(btn_register)

        return card

    # ── Cabecera ─────────────────────────────────────────────────────
    def _make_header(self):
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Ícono de academia (texto estilizado como logo)
        icon_lbl = QLabel("⚔")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"font-size: 36px; color: {BTN_RED}; background: transparent; border: none;")
        v.addWidget(icon_lbl)

        title = QLabel("SENSHI FIGHT ACADEMY")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 800;
            letter-spacing: 2px;
            color: {TEXT_PRIMARY};
            background: transparent;
            border: none;
        """)
        v.addWidget(title)

        subtitle = QLabel("Sistema de Gestión")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED}; background: transparent; border: none;")
        v.addWidget(subtitle)

        return container

    # ── Separador con acento rojo ─────────────────────────────────────
    def _make_divider(self):
        line = QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet(f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 transparent,
                stop:0.3 {BTN_RED},
                stop:0.7 {BTN_RED},
                stop:1 transparent
            );
            border: none;
            border-radius: 1px;
        """)
        return line

    # ── Label de campo ───────────────────────────────────────────────
    def _make_field_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 1px;
            color: {TEXT_MUTED};
            background: transparent;
            border: none;
        """)
        return lbl

    # ── Input estilizado ─────────────────────────────────────────────
    def _make_input(self, placeholder, is_password):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(44)
        if is_password:
            inp.setEchoMode(QLineEdit.EchoMode.Password)

        base_style = f"""
            QLineEdit {{
                background-color: {INPUT_BG};
                color: {TEXT_PRIMARY};
                border: 1.5px solid {INPUT_BORDER};
                border-radius: 8px;
                padding: 0 14px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {INPUT_FOCUS};
                background-color: #1A1010;
            }}
            QLineEdit::placeholder {{
                color: {TEXT_MUTED};
            }}
        """
        inp.setStyleSheet(base_style)

        # Enter en contraseña → login
        inp.returnPressed.connect(self._do_login)
        return inp

    # ── Botón principal ───────────────────────────────────────────────
    def _make_button(self):
        btn = QPushButton("INGRESAR")
        btn.setFixedHeight(46)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BTN_RED};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{
                background-color: {BTN_RED_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {BTN_RED_PRESS};
            }}
            QPushButton:disabled {{
                background-color: #3A1A1A;
                color: #666666;
            }}
        """)
        btn.clicked.connect(self._do_login)
        return btn

    # ── Footer ────────────────────────────────────────────────────────
    def _make_footer(self):
        lbl = QLabel("v1.0.0  ·  Senshi Fight Academy © 2025")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED}; background: transparent; border: none;")
        return lbl

    # ── Abrir registro ────────────────────────────────────────────────
    def _open_register(self):
        from views.register_view import RegisterView
        self.register = RegisterView(
            on_back=lambda: self.show()
        )
        self.register.show()
        self.hide()

    # ── Lógica de login ───────────────────────────────────────────────
    def _do_login(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text()

        # Validaciones básicas en el cliente
        if not username:
            self._set_status("Ingresa tu usuario.", error=True)
            self.input_user.setFocus()
            return
        if not password:
            self._set_status("Ingresa tu contraseña.", error=True)
            self.input_pass.setFocus()
            return

        # Estado de carga
        self.btn_login.setEnabled(False)
        self.btn_login.setText("Verificando...")
        self._set_status("")

        try:
            user = self.auth_service.login(username, password)
            self._set_status("✓  Acceso concedido", error=False)
            QTimer.singleShot(800, lambda: self._on_login_success(user))

        except ValueError as e:
            self._set_status(str(e), error=True)
            self._shake_inputs()

        finally:
            self.btn_login.setEnabled(True)
            self.btn_login.setText("INGRESAR")

    def _set_status(self, msg, error=True):
        color = ERROR_COLOR if error else SUCCESS_COLOR
        self.lbl_status.setStyleSheet(
            f"color: {color}; font-size: 12px; background: transparent; border: none;"
        )
        self.lbl_status.setText(msg)

    def _shake_inputs(self):
        """Animación sutil de error en los inputs."""
        original_style_u = self.input_user.styleSheet()
        original_style_p = self.input_pass.styleSheet()
        error_border = f"border: 1.5px solid {ERROR_COLOR};"

        for inp in [self.input_user, self.input_pass]:
            current = inp.styleSheet()
            inp.setStyleSheet(current.replace(
                f"border: 1.5px solid {INPUT_BORDER};",
                f"border: 1.5px solid {ERROR_COLOR};"
            ))

        QTimer.singleShot(600, lambda: (
            self.input_user.setStyleSheet(original_style_u),
            self.input_pass.setStyleSheet(original_style_p),
        ))

    def _on_login_success(self, user):
        """
        Llamar aquí a la ventana principal.
        Por ahora imprime el usuario en consola.
        """
        print(f"[LOGIN OK] usuario={user['username']}  id={user['id']}")
        # TODO: abrir MainWindow(user)
        # from views.main_window import MainWindow
        # self.main = MainWindow(user)
        # self.main.show()
        # self.close()