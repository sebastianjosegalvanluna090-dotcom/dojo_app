#views/users_admin_view.py


from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox,
    QCheckBox, QScrollArea, QComboBox, QInputDialog,
    QGraphicsDropShadowEffect, QGridLayout, QDialog, QSizePolicy,
    QGraphicsBlurEffect, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor


from repositories.user_admin_repository import UserAdminRepository

# ─── PALETA ───────────────────────────────────────────────────────────
BG_MAIN  = "#050505"
BG_CARD  = "#0C0C0C"
BG_TABLE = "#090909"
BORDER   = "#1F1F1F"
RED      = "#E11D48"
RED_H    = "#F43F5E"
RED_DARK = "#3B0712"
TEXT_PRI = "#FAFAFA"
TEXT_SEC = "#A3A3A3"
TEXT_MUT = "#525252"
GREEN    = "#10B981"
YELLOW   = "#F59E0B"
BLUE     = "#3B82F6"

ROLE_COLORS = {
    "admin":      "#A855F7",
    "acudent":    "#3B82F6",
    "visit":      "#6B7280",
    "instructor": "#F97316",
    "student":    "#10B981",
}


# ─── TOAST ────────────────────────────────────────────────────────────
class ToastNotification(QFrame):
    def __init__(self, message: str, toast_type: str = "success", parent=None):
        super().__init__(parent)

        self.setFixedSize(300, 68)

        color = {
            "success": GREEN,
            "warning": YELLOW,
            "info": BLUE,
            "error": RED,
        }.get(toast_type, GREEN)

        icon = {
            "success": "✅",
            "warning": "⚠️",
            "info": "🔹",
            "error": "⛔",
        }.get(toast_type, "✅")

        self.setWindowOpacity(0.0)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #0E0E0E;
                border: 1px solid {BORDER};
                border-left: 4px solid {color};
                border-radius: 10px;
            }}
            QLabel {{
                color: {TEXT_PRI};
                font-size: 11px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(0, 0, 0, 210))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        lbl_icon = QLabel(icon)
        lbl_icon.setFixedWidth(22)

        lbl_text = QLabel(message)
        lbl_text.setWordWrap(True)

        layout.addWidget(lbl_icon)
        layout.addWidget(lbl_text, 1)

        self.anim = QPropertyAnimation(self, b"windowOpacity", self)
        self.anim.setDuration(280)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(3200)
        self.timer.timeout.connect(self.close_with_fade)

    def show_toast(self):
        self.show()
        self.raise_()

        self.anim.stop()
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

        self.timer.start()

    def close_with_fade(self):
        self.anim.stop()
        self.anim.setStartValue(self.windowOpacity())
        self.anim.setEndValue(0.0)

        try:
            self.anim.finished.disconnect()
        except Exception:
            pass

        self.anim.finished.connect(self.deleteLater)
        self.anim.start()


# ─── CARD CON SOMBRA ──────────────────────────────────────────────────
class PremiumTextDialog(QDialog):
    def __init__(self, title, subtitle, label, placeholder="", accent=RED, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setFixedSize(430, 245)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("PremiumDialogCard")
        card.setStyleSheet(f"""
            QFrame#PremiumDialogCard {{
                background-color: #0C0C0C;
                border: 1px solid #242424;
                border-top: 4px solid {accent};
                border-radius: 14px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(26)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 220))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 18px;
            font-weight: 900;
        """)

        btn_close = QPushButton("×")
        btn_close.setFixedSize(30, 30)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                color: {TEXT_SEC};
                background: transparent;
                border: none;
                font-size: 24px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
            }}
        """)
        btn_close.clicked.connect(self.reject)

        header.addWidget(title_lbl)
        header.addStretch()
        header.addWidget(btn_close)
        layout.addLayout(header)

        desc_lbl = QLabel(subtitle)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 12px;
            font-weight: 600;
        """)
        layout.addWidget(desc_lbl)

        field_lbl = QLabel(label.upper())
        field_lbl.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 9px;
            font-weight: 900;
            letter-spacing: 1.2px;
        """)
        layout.addWidget(field_lbl)

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setFixedHeight(40)
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #121212;
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 12px;
                font-size: 13px;
                font-weight: 700;
            }}
            QLineEdit:focus {{
                border-color: {accent};
            }}
        """)
        self.input.returnPressed.connect(self.accept)
        layout.addWidget(self.input)

        actions = QHBoxLayout()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SEC};
                border: none;
                font-size: 12px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
            }}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("Confirmar")
        btn_ok.setFixedHeight(38)
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 900;
                padding: 0 18px;
            }}
            QPushButton:hover {{
                background-color: {RED_H};
            }}
        """)
        btn_ok.clicked.connect(self.accept)

        actions.addWidget(btn_cancel)
        actions.addStretch()
        actions.addWidget(btn_ok)

        layout.addLayout(actions)

        root.addWidget(card)

        QTimer.singleShot(80, self.input.setFocus)

    def value(self):
        return self.input.text().strip()

class PremiumInviteCodeDialog(QDialog):
    def __init__(self, roles, parent=None):
        super().__init__(parent)

        self.roles = roles or []

        self.setWindowTitle("Nuevo Código")
        self.setFixedSize(460, 310)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("PremiumInviteCard")
        card.setStyleSheet(f"""
            QFrame#PremiumInviteCard {{
                background-color: #0C0C0C;
                border: 1px solid #242424;
                border-top: 4px solid {RED};
                border-radius: 14px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(26)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 220))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()

        title_lbl = QLabel("Nuevo Código de Invitación")
        title_lbl.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 18px;
            font-weight: 900;
        """)

        btn_close = QPushButton("×")
        btn_close.setFixedSize(30, 30)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                color: {TEXT_SEC};
                background: transparent;
                border: none;
                font-size: 24px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
            }}
        """)
        btn_close.clicked.connect(self.reject)

        header.addWidget(title_lbl)
        header.addStretch()
        header.addWidget(btn_close)
        layout.addLayout(header)

        desc = QLabel("Genera un código para permitir el registro de usuarios con un rol específico.")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 12px;
            font-weight: 600;
        """)
        layout.addWidget(desc)

        lbl_role = QLabel("ROL ASIGNADO")
        lbl_role.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 9px;
            font-weight: 900;
            letter-spacing: 1.2px;
        """)
        layout.addWidget(lbl_role)

        self.cmb_role = QComboBox()
        self.cmb_role.setFixedHeight(40)
        self.cmb_role.setStyleSheet(f"""
            QComboBox {{
                background-color: #121212;
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 12px;
                font-size: 13px;
                font-weight: 800;
            }}
            QComboBox:focus {{
                border-color: {RED};
            }}
            QComboBox QAbstractItemView {{
                background-color: #121212;
                color: {TEXT_PRI};
                selection-background-color: {RED};
                border: 1px solid {BORDER};
            }}
        """)

        for role_id, role_name in self.roles:
            self.cmb_role.addItem(role_name.capitalize(), role_id)

        layout.addWidget(self.cmb_role)

        lbl_code = QLabel("CÓDIGO")
        lbl_code.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 9px;
            font-weight: 900;
            letter-spacing: 1.2px;
        """)
        layout.addWidget(lbl_code)

        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("Ej. ACU-2026, ADMIN-ACCESS, INV-001")
        self.input_code.setFixedHeight(40)
        self.input_code.setStyleSheet(f"""
            QLineEdit {{
                background-color: #121212;
                color: {TEXT_PRI};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 0 12px;
                font-size: 13px;
                font-weight: 800;
            }}
            QLineEdit:focus {{
                border-color: {RED};
            }}
        """)
        self.input_code.returnPressed.connect(self.accept)
        layout.addWidget(self.input_code)

        actions = QHBoxLayout()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SEC};
                border: none;
                font-size: 12px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                color: {TEXT_PRI};
            }}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("Crear Código")
        btn_ok.setFixedHeight(38)
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 900;
                padding: 0 18px;
            }}
            QPushButton:hover {{
                background-color: {RED_H};
            }}
        """)
        btn_ok.clicked.connect(self.accept)

        actions.addWidget(btn_cancel)
        actions.addStretch()
        actions.addWidget(btn_ok)

        layout.addLayout(actions)

        root.addWidget(card)

        QTimer.singleShot(80, self.input_code.setFocus)

    def selected_role_id(self):
        return self.cmb_role.currentData()

    def code(self):
        return self.input_code.text().strip()
    
# ─── CARD PREMIUM (con sombra avanzada) ───────────────────────────────
class PremiumCard(QFrame):
    """
    Tarjeta premium con sombra profunda y micro-animación segura.
    La sombra se puede recrear después del blur para evitar errores de QPainter.
    """

    def __init__(self, border_accent=None, parent=None):
        super().__init__(parent)

        self.setObjectName("PremiumCard")
        self.border_accent = border_accent or BORDER

        bl = f"border-left: 4px solid {self.border_accent};" if border_accent else ""

        self.setStyleSheet(f"""
            QFrame#PremiumCard {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                {bl}
                border-radius: 14px;
            }}

            QFrame#PremiumCard QLabel {{
                background: transparent;
                border: none;
            }}

            QFrame#PremiumCard QWidget {{
                background: transparent;
            }}
        """)

        self._shadow = None
        self._pulse_anim = None
        self._apply_shadow()

    def _apply_shadow(self):
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(30)
        self._shadow.setOffset(0, 10)
        self._shadow.setColor(QColor(0, 0, 0, 220))
        self.setGraphicsEffect(self._shadow)

        self._pulse_anim = QPropertyAnimation(self._shadow, b"blurRadius", self)
        self._pulse_anim.setDuration(240)
        self._pulse_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def update_with_animation(self, callback):
        if callback:
            callback()

        if not self._shadow:
            self._apply_shadow()

        self._pulse_anim.stop()
        self._pulse_anim.setStartValue(40)
        self._pulse_anim.setEndValue(30)
        self._pulse_anim.start()



# ─── OVERLAY CON BLUR ESTABLE Y SIN CONFLICTOS QPAINTER ───────────────
class SimpleOverlay(QWidget):
    def __init__(self, parent=None, target_widget=None, effect_widgets=None):
        super().__init__(parent)

        self.target_widget = target_widget
        self.effect_widgets = effect_widgets or []

        self.blur_effect = None
        self.anim_blur = None
        self._active = False

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 145);
            }
        """)

        self.hide()

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity_effect)

        self.anim_opacity = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self.anim_opacity.setDuration(180)
        self.anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _suspend_child_effects(self):
        """
        Quitar efectos antes del blur.
        No se guardan referencias porque Qt puede destruirlas internamente.
        """
        for widget in self.effect_widgets:
            if widget is not None:
                widget.setGraphicsEffect(None)

    def _restore_child_effects(self):
        """
        Recrear sombras nuevas después del blur.
        No reutiliza efectos viejos para evitar:
        RuntimeError: wrapped C/C++ object has been deleted
        """
        for widget in self.effect_widgets:
            if widget is None:
                continue

            if hasattr(widget, "_apply_shadow"):
                widget._apply_shadow()
            elif hasattr(widget, "_restore_shadow"):
                widget._restore_shadow()

    def activate(self):
        try:
            self.anim_opacity.finished.disconnect()
        except Exception:
            pass

        if self.parentWidget():
            self.setGeometry(self.parentWidget().rect())

        self.show()
        self.raise_()

        if self._active:
            self.opacity_effect.setOpacity(1.0)
            return

        self._active = True

        self._suspend_child_effects()

        if self.target_widget:
            self.target_widget.setGraphicsEffect(None)

            self.blur_effect = QGraphicsBlurEffect(self.target_widget)
            self.blur_effect.setBlurRadius(0)
            self.target_widget.setGraphicsEffect(self.blur_effect)

            self.anim_blur = QPropertyAnimation(self.blur_effect, b"blurRadius", self)
            self.anim_blur.setDuration(220)
            self.anim_blur.setStartValue(0)
            self.anim_blur.setEndValue(18)
            self.anim_blur.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.anim_blur.start()

        self.anim_opacity.stop()
        self.anim_opacity.setStartValue(self.opacity_effect.opacity())
        self.anim_opacity.setEndValue(1.0)
        self.anim_opacity.start()

    def deactivate(self):
        if not self._active:
            self.hide()
            self.opacity_effect.setOpacity(0.0)
            return

        self._active = False

        try:
            self.anim_opacity.finished.disconnect()
        except Exception:
            pass

        if self.blur_effect:
            self.anim_blur = QPropertyAnimation(self.blur_effect, b"blurRadius", self)
            self.anim_blur.setDuration(180)
            self.anim_blur.setStartValue(self.blur_effect.blurRadius())
            self.anim_blur.setEndValue(0)
            self.anim_blur.setEasingCurve(QEasingCurve.Type.InCubic)
            self.anim_blur.start()

        self.anim_opacity.stop()
        self.anim_opacity.setStartValue(self.opacity_effect.opacity())
        self.anim_opacity.setEndValue(0.0)

        def finish():
            self.hide()
            self.opacity_effect.setOpacity(0.0)

            if self.target_widget:
                self.target_widget.setGraphicsEffect(None)

            self.blur_effect = None
            self.anim_blur = None

            self._restore_child_effects()

            try:
                self.anim_opacity.finished.disconnect()
            except Exception:
                pass

        self.anim_opacity.finished.connect(finish)
        self.anim_opacity.start()

    def resizeEvent(self, e):
        if self.parentWidget():
            self.setGeometry(self.parentWidget().rect())


# ─── VISTA PRINCIPAL ──────────────────────────────────────────────────
class UsersAdminView(QWidget):
    def __init__(self):
        super().__init__()
        self.repo          = UserAdminRepository()
        self._rows:  list  = []
        self._roles: list  = []
        self._role_checks: dict = {}

        self._build_ui()
        self._load_all()

    def showEvent(self, event):
        super().showEvent(event)

        if hasattr(self, "table"):
            self._load_all()


    # ── UI ────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(f"background-color: {BG_MAIN};")

        # Layout raíz con overlay encima
        self._root_grid = QGridLayout(self)
        self._root_grid.setContentsMargins(0, 0, 0, 0)

        # Scroll contenedor principal
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #080808;
                width: 6px;
            }
            QScrollBar::handle:vertical {
                background: #2A2A2A;
                border-radius: 3px;
                min-height: 15px;
            }
        """)

        main_widget = QWidget()
        main_widget.setStyleSheet(f"background-color: {BG_MAIN};")

        scroll.setWidget(main_widget)
        self._root_grid.addWidget(scroll, 0, 0)

        cl = QVBoxLayout(main_widget)
        cl.setContentsMargins(32, 28, 32, 28)
        cl.setSpacing(18)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("👤  Usuarios y Roles")
        title.setStyleSheet(f"color:{TEXT_PRI}; font-size:22px; font-weight:800;")

        self.btn_new_role = QPushButton("＋ Crear Rol")
        self.btn_new_role.setFixedHeight(36)
        self.btn_new_role.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_role.setStyleSheet(self._btn_sec())
        self.btn_new_role.clicked.connect(self._create_role)

        self.btn_new_code = QPushButton("＋ Código Invitación")
        self.btn_new_code.setFixedHeight(36)
        self.btn_new_code.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_code.setStyleSheet(self._btn_pri())
        self.btn_new_code.clicked.connect(self._create_invite_code)

        hdr.addWidget(title); hdr.addStretch()
        hdr.addWidget(self.btn_new_role); hdr.addWidget(self.btn_new_code)
        cl.addLayout(hdr)

        sep = QFrame(); sep.setFixedHeight(2)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.3 {RED}, stop:1 transparent);
            border:none;
        """)
        cl.addWidget(sep)

        # Toolbar
        tb = QHBoxLayout(); tb.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar por nombre, email, usuario o rol...")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(self._input_style())
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._load_people)
        self.search_input.textChanged.connect(lambda: self._search_timer.start(350))

        btn_ref = QPushButton("↻ Actualizar")
        btn_ref.setFixedHeight(38)
        btn_ref.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ref.setStyleSheet(self._btn_sec())
        btn_ref.clicked.connect(self._load_all)
        tb.addWidget(self.search_input, 1); tb.addWidget(btn_ref)
        cl.addLayout(tb)

        # Contenido dividido: tabla + panel derecho
        # Contenido vertical: tabla arriba + paneles abajo
        content = QVBoxLayout()
        content.setContentsMargins(0, 4, 0, 8)
        content.setSpacing(18)

        self.table = self._make_table()
        self.table.setMinimumHeight(300)

        self.user_card = self._make_user_card()
        self.system_card = self._make_system_card()

        content.addWidget(self.table)
        content.addWidget(self.user_card)
        content.addWidget(self.system_card)

        cl.addLayout(content, 1)

        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet(f"color:{GREEN}; font-size:12px;")
        cl.addWidget(self.lbl_status)

        # Overlay encima de todo (capa 2 en el grid)
        self._main_content_widget = main_widget

        self._overlay = SimpleOverlay(
            self,
            target_widget=self._main_content_widget,
            effect_widgets=[
                self.table,
                self.user_card,
                self.system_card
            ]
        )

        self._root_grid.addWidget(self._overlay, 0, 0)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._overlay.resize(self.width(), self.height())

    # ── Tabla ─────────────────────────────────────────────────────────
    def _make_table(self):
        t = QTableWidget()
        t.setColumnCount(7)
        t.setHorizontalHeaderLabels([
            "ID",
            "Nombre",
            "Email",
            "Usuario",
            "Estado",
            "Roles",
            "Teléfono"
        ])
        h = t.horizontalHeader()
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        h.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        h.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        h.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)

        t.setColumnWidth(0, 60)
        t.setColumnWidth(3, 170)
        t.setColumnWidth(4, 120)
        t.setColumnWidth(5, 150)
        t.setColumnWidth(6, 150)
        t.verticalHeader().setVisible(False)
        t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        t.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        t.setAlternatingRowColors(True)
        t.setShowGrid(False)
        t.setSortingEnabled(False)
        t.setStyleSheet(f"""
            QTableWidget {{
                background-color:{BG_TABLE}; alternate-background-color:#0D0D0D;
                color:{TEXT_PRI}; border:1px solid #181818;;
                border-radius:10px; font-size:13px; outline:none;
            }}
            QHeaderView::section {{
                background-color:{BG_CARD}; color:{TEXT_SEC}; border:none;
                border-bottom:1px solid {BORDER}; padding:10px 12px;
                font-size:11px; font-weight:700; letter-spacing:0.5px;
            }}
            QTableWidget::item {{ padding:10px 12px; border-bottom:1px solid #141414; }}
            QTableWidget::item:selected {{ background-color:{RED_DARK}; color:white; }}
        """)

        def restore_table_shadow():
            table_shadow = QGraphicsDropShadowEffect(t)
            table_shadow.setBlurRadius(22)
            table_shadow.setOffset(0, 6)
            table_shadow.setColor(QColor(0, 0, 0, 180))
            t.setGraphicsEffect(table_shadow)

        t._restore_shadow = restore_table_shadow
        t._restore_shadow()

        t.itemSelectionChanged.connect(self._load_selected_to_panel)
        return t

    # ── Tarjeta Ficha ─────────────────────────────────────────────────
    def _make_user_card(self):
        card = PremiumCard(border_accent=RED)
        card.setMinimumHeight(380)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 18, 18, 18); lay.setSpacing(10)

        lbl = QLabel("FICHA INDIVIDUAL")
        lbl.setStyleSheet(f"color:{TEXT_MUT}; font-size:9px; font-weight:900; letter-spacing:1.5px;")
        lay.addWidget(lbl)

        info_row = QHBoxLayout()
        info_row.setSpacing(24)

        left_info = QVBoxLayout()
        left_info.setSpacing(4)

        self.detail_name = QLabel("Selecciona una persona")
        self.detail_name.setWordWrap(True)
        self.detail_name.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 17px;
            font-weight: 900;
        """)

        self.detail_user = QLabel("Usuario: —")
        self.detail_user.setStyleSheet(f"color:{TEXT_SEC}; font-size:12px;")
        self.detail_user.setWordWrap(True)

        self.detail_email = QLabel("Email: —")
        self.detail_email.setStyleSheet(f"color:{TEXT_SEC}; font-size:12px;")
        self.detail_email.setWordWrap(True)

        left_info.addWidget(self.detail_name)
        left_info.addWidget(self.detail_user)
        left_info.addWidget(self.detail_email)

        self.detail_status = QLabel("Estado: —")
        self.detail_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_status.setFixedHeight(24)
        self.detail_status.setMinimumWidth(120)
        self.detail_status.setStyleSheet(f"""
            color: {TEXT_MUT};
            background-color: #181818;
            border: 1px solid {BORDER};
            border-radius: 12px;
            font-size: 10px;
            font-weight: 900;
        """)

        info_row.addLayout(left_info, 1)
        info_row.addWidget(self.detail_status, 0, Qt.AlignmentFlag.AlignTop)

        lay.addLayout(info_row)

        lay.addWidget(self._sep())

        lbl_r = QLabel("PERMISOS DE ACCESO")
        lbl_r.setStyleSheet(f"color:{TEXT_MUT}; font-size:9px; font-weight:900; letter-spacing:1.5px;")
        lay.addWidget(lbl_r)

        self.roles_container = QWidget()
        self.roles_container.setStyleSheet("background: transparent; border: none;")
        self.roles_container.setMinimumHeight(95)

        self.roles_layout = QGridLayout(self.roles_container)
        self.roles_layout.setContentsMargins(0, 0, 0, 0)
        self.roles_layout.setHorizontalSpacing(22)
        self.roles_layout.setVerticalSpacing(10)

        lay.addWidget(self.roles_container)
        lay.addSpacing(10)

        btn_save = QPushButton("Guardar Roles de Seguridad")

        btn_save.setFixedHeight(38)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(self._btn_pri())
        btn_save.clicked.connect(self._save_roles)
        lay.addWidget(btn_save)
        return card

    # ── Tarjeta Sistema ───────────────────────────────────────────────
    def _make_system_card(self):
        card = PremiumCard(border_accent=BLUE)
        card.setMinimumHeight(250)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 18, 18, 18); lay.setSpacing(10)

        lbl = QLabel("ADMINISTRACIÓN Y SEGURIDAD")
        lbl.setStyleSheet(f"color:{TEXT_MUT}; font-size:9px; font-weight:900; letter-spacing:1.5px;")
        lay.addWidget(lbl)

        btn_toggle = QPushButton("Activar / Desactivar Acceso")
        btn_toggle.setFixedHeight(34)
        btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_toggle.setStyleSheet(self._btn_sec())
        btn_toggle.clicked.connect(self._toggle_user_active)

        btn_reset = QPushButton("Resetear Contraseña")
        btn_reset.setFixedHeight(34)
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.setStyleSheet(self._btn_sec())
        btn_reset.clicked.connect(self._reset_password)

        btn_del = QPushButton("Eliminar Ficha Permanentemente")
        btn_del.setFixedHeight(34)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet(self._btn_danger())
        btn_del.clicked.connect(self._delete_person)

        for b in [btn_toggle, btn_reset, btn_del]:
            lay.addWidget(b)

        lay.addWidget(self._sep())

        lbl_c = QLabel("CÓDIGOS DE INVITACIÓN")
        lbl_c.setStyleSheet(f"color:{TEXT_MUT}; font-size:9px; font-weight:900; letter-spacing:1.5px;")
        lay.addWidget(lbl_c)

        self.cmb_codes = QComboBox()
        self.cmb_codes.setFixedHeight(34)
        self.cmb_codes.setStyleSheet(self._combo_style())
        lay.addWidget(self.cmb_codes)

        btn_del_code = QPushButton("Eliminar Código Seleccionado")
        btn_del_code.setFixedHeight(34)
        btn_del_code.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del_code.setStyleSheet(self._btn_danger())
        btn_del_code.clicked.connect(self._delete_invite_code)
        lay.addWidget(btn_del_code)
        return card

    # ── Carga ─────────────────────────────────────────────────────────
    def _load_all(self):
        self._load_roles()
        self._load_codes()
        self._load_people()

    def _load_people(self):
        try:
            self._rows = self.repo.get_people_users(self.search_input.text().strip())
            self._populate_table()
        except Exception as e:
            self._critical(f"No se pudieron cargar usuarios:\n{e}")

    def _load_roles(self):
        try:
            self._roles = self.repo.get_roles()
            self._build_role_checks()
        except Exception as e:
            self._critical(f"No se pudieron cargar roles:\n{e}")

    def _load_codes(self):
        try:
            self.cmb_codes.clear()
            for code_id, code, _, role_name in self.repo.get_invite_codes():
                self.cmb_codes.addItem(f"🔑 {code}  ·  {role_name}", code_id)
        except Exception as e:
            self._critical(f"No se pudieron cargar códigos:\n{e}")

    def _populate_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)

        for i, row in enumerate(self._rows):
            full_name = f"{row[1] or ''} {row[2] or ''}".strip() or "Sin nombre"
            user_id = row[5]
            is_active = row[7]

            status = "Activo" if is_active else ("Sin usuario" if user_id is None else "Inactivo")

            vals = [
                row[0],
                full_name,
                row[3] or "—",
                row[6] or "—",
                status,
                row[8] or "Sin roles",
                row[4] or "—",
            ]

            self.table.insertRow(i)

            for j, val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

                if j == 4:
                    item.setForeground(QColor(
                        GREEN if status == "Activo" else
                        ("#EF4444" if status == "Inactivo" else YELLOW)
                    ))

                self.table.setItem(i, j, item)

            self.table.setRowHeight(i, 50)

        self.table.blockSignals(False)

        if not self._rows:
            self._clear_panel()

    def _build_role_checks(self):
        while self.roles_layout.count():
            item = self.roles_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._role_checks = {}

        columns = 3

        for idx, (role_id, role_name) in enumerate(self._roles):
            color = ROLE_COLORS.get(role_name.lower(), TEXT_SEC)

            chk = QCheckBox(role_name.capitalize())
            chk.setCursor(Qt.CursorShape.PointingHandCursor)
            chk.setMinimumHeight(26)

            chk.setStyleSheet(f"""
                QCheckBox {{
                    color: {color};
                    font-size: 13px;
                    font-weight: 800;
                    spacing: 10px;
                    background: transparent;
                    border: none;
                }}
                QCheckBox::indicator {{
                    width: 17px;
                    height: 17px;
                    border: 1.5px solid {BORDER};
                    border-radius: 5px;
                    background: #121212;
                }}
                QCheckBox::indicator:hover {{
                    border-color: {color};
                }}
                QCheckBox::indicator:checked {{
                    background: {color};
                    border: 1.5px solid {color};
                }}
            """)

            self._role_checks[role_id] = chk

            row = idx // columns
            col = idx % columns

            self.roles_layout.addWidget(chk, row, col)

        self.roles_container.adjustSize()

    # ── Panel derecho ─────────────────────────────────────────────────
    def _current_row(self):
        r = self.table.currentRow()
        return self._rows[r] if 0 <= r < len(self._rows) else None

    def _load_selected_to_panel(self):
        row = self._current_row()

        if not row:
            self._clear_panel()
            return

        self.user_card.update_with_animation(lambda: self._apply_user_card(row))
        self.system_card.update_with_animation(lambda: None)

    def _apply_user_card(self, row):
        full_name = f"{row[1] or ''} {row[2] or ''}".strip() or "Sin nombre"
        user_id   = row[5]
        username  = row[6] or "—"
        is_active = row[7]
        role_ids  = set(row[9] or [])

        self.detail_name.setText(full_name)
        self.detail_user.setText(f"Usuario: {username}")
        self.detail_email.setText(f"Email: {row[3] or '—'}")

        if user_id is None:
            self.detail_status.setText("PENDIENTE")
            self.detail_status.setStyleSheet("""
                color: #F59E0B;
                background-color: rgba(245, 158, 11, 0.10);
                border: 1px solid rgba(245, 158, 11, 0.25);
                border-radius: 12px;
                font-size: 10px;
                font-weight: 900;
            """)
        elif is_active:
            self.detail_status.setText("ACTIVO")
            self.detail_status.setStyleSheet("""
                color: #10B981;
                background-color: rgba(16, 185, 129, 0.10);
                border: 1px solid rgba(16, 185, 129, 0.25);
                border-radius: 12px;
                font-size: 10px;
                font-weight: 900;
            """)
        else:
            self.detail_status.setText("INACTIVO")
            self.detail_status.setStyleSheet("""
                color: #EF4444;
                background-color: rgba(239, 68, 68, 0.10);
                border: 1px solid rgba(239, 68, 68, 0.25);
                border-radius: 12px;
                font-size: 10px;
                font-weight: 900;
            """)
        for role_id, chk in self._role_checks.items():
            chk.blockSignals(True)
            chk.setChecked(role_id in role_ids)
            chk.blockSignals(False)

    def _clear_panel(self):
        self.detail_name.setText("Selecciona una persona")
        self.detail_user.setText("Usuario: —")
        self.detail_email.setText("Email: —")
        self.detail_status.setText("PENDIENTE")
        self.detail_status.setStyleSheet(f"""
            color: {TEXT_MUT};
            background-color: #181818;
            border: 1px solid {BORDER};
            border-radius: 12px;
            font-size: 10px;
            font-weight: 900;
        """)
        for chk in self._role_checks.values():
            chk.setChecked(False)

    # ── Acciones ──────────────────────────────────────────────────────
    def _save_roles(self):
        row = self._current_row()
        if not row:
            self._toast("Selecciona una persona primero", "warning"); return
        selected = [rid for rid, chk in self._role_checks.items() if chk.isChecked()]
        try:
            self.repo.set_person_roles(row[0], selected)
            self._toast("Roles actualizados correctamente")
            self._load_people()
        except Exception as e:
            self._critical(f"No se pudieron guardar roles:\n{e}")

    def _toggle_user_active(self):
        row = self._current_row()
        if not row:
            self._toast("Selecciona una persona primero", "warning"); return
        if row[5] is None:
            self._toast("Esta persona no tiene usuario asociado", "warning"); return
        try:
            self.repo.set_user_active(row[5], not row[7])
            self._toast("Estado de acceso actualizado")
            self._load_people()
        except Exception as e:
            self._critical(f"No se pudo actualizar usuario:\n{e}")

    def _reset_password(self):
        row = self._current_row()
        if not row:
            self._toast("Selecciona una persona primero", "warning"); return
        if row[5] is None:
            self._toast("Esta persona no tiene usuario asociado", "warning"); return

        self._overlay.activate()
        pwd, ok = QInputDialog.getText(
            self, "Resetear Contraseña",
            "Nueva contraseña temporal (mín. 6 caracteres):",
            QLineEdit.EchoMode.Password
        )
        self._overlay.deactivate()
        if not ok: return
        if len(pwd) < 6:
            self._toast("Contraseña demasiado corta", "warning"); return
        try:
            self.repo.reset_password(row[5], pwd)
            self._toast("Contraseña actualizada correctamente")
        except Exception as e:
            self._critical(f"No se pudo actualizar la contraseña:\n{e}")

    def _create_invite_code(self):
        roles = self.repo.get_roles()

        if not roles:
            self._toast("Primero crea un rol", "warning")
            return

        self._overlay.activate()

        dlg = PremiumInviteCodeDialog(
            roles=roles,
            parent=self
        )

        result = dlg.exec()
        QTimer.singleShot(80, self._overlay.deactivate)

        if result != QDialog.DialogCode.Accepted:
            return

        role_id = dlg.selected_role_id()
        code = dlg.code()

        if not code:
            self._toast("Escribe un código de invitación", "warning")
            return

        try:
            self.repo.create_invite_code(code, role_id)
            self._toast("Código de invitación creado")
            self._load_codes()
        except Exception as e:
            self._critical(f"No se pudo crear el código:\n{e}")

    def _delete_invite_code(self):
        code_id = self.cmb_codes.currentData()
        if code_id is None:
            self._toast("Selecciona un código de la lista", "warning"); return
        self._overlay.activate()
        res = QMessageBox.question(
            self, "Eliminar Código", "¿Eliminar este código de invitación?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        self._overlay.deactivate()
        if res != QMessageBox.StandardButton.Yes: return
        try:
            self.repo.delete_invite_code(code_id)
            self._toast("Código eliminado")
            self._load_codes()
        except Exception as e:
            self._critical(f"No se pudo eliminar el código:\n{e}")

    def _create_role(self):
        self._overlay.activate()

        dlg = PremiumTextDialog(
            title="Nuevo Rol",
            subtitle="Crea un nuevo rol de seguridad para asignarlo a personas registradas.",
            label="Nombre del rol",
            placeholder="Ej. admin, instructor, student",
            accent=RED,
            parent=self
        )

        result = dlg.exec()
        QTimer.singleShot(80, self._overlay.deactivate)

        if result != QDialog.DialogCode.Accepted:
            return

        name = dlg.value().strip().lower()

        if not name:
            self._toast("Escribe un nombre de rol", "warning")
            return

        try:
            self.repo.create_role(name)
            self._toast("Rol creado correctamente")
            self._load_all()
        except Exception as e:
            self._critical(f"No se pudo crear el rol:\n{e}")

    def _delete_person(self):
        row = self._current_row()
        if not row:
            self._toast("Selecciona una persona primero", "warning"); return

        person_id = row[0]
        full_name = f"{row[1] or ''} {row[2] or ''}".strip() or "Sin nombre"
        username  = row[6] or "—"
        roles     = row[8] or "Sin roles"

        self._overlay.activate()
        msg = QMessageBox(self)
        msg.setWindowTitle("Eliminar Persona")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(f"¿Eliminar a {full_name}?")
        msg.setInformativeText(
            "Esta acción eliminará de forma irreversible todo el expediente:\n\n"
            f"• ID Persona: {person_id}\n"
            f"• Usuario: {username}\n"
            f"• Roles: {roles}\n\n"
            "Se eliminarán en cascada: clases, asistencias, membresías,\n"
            "cinturones, historial y pagos relacionados.\n\n"
            "Esta acción NO se puede deshacer."
        )
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Cancel)
        msg.setStyleSheet(self._msgbox_style())
        res = msg.exec()
        self._overlay.deactivate()
        if res != QMessageBox.StandardButton.Yes: return

        self._overlay.activate()
        text, ok = QInputDialog.getText(
            self, "Confirmación de seguridad",
            "Para confirmar, escribe  ELIMINAR :"
        )
        self._overlay.deactivate()
        if not ok: return
        if text.strip().upper() != "ELIMINAR":
            self._toast("Acción cancelada — confirmación incorrecta", "warning"); return

        try:
            self.repo.delete_person_deep(person_id)
            self._toast("Ficha eliminada permanentemente", "warning")
            self.table.clearSelection()
            self.table.setCurrentCell(-1, -1)
            self._clear_panel()
            self._load_all()
        except Exception as e:
            self._critical(f"Error al eliminar:\n{e}")

    # ── Helpers ───────────────────────────────────────────────────────
    def _toast(self, msg: str, kind: str = "success"):
        toast = ToastNotification(msg, kind, self)

        x = max(20, self.width() - 320)
        y = max(20, self.height() - 90)

        toast.setGeometry(x, y, 300, 68)
        toast.show_toast()

    def _critical(self, msg: str):
        self._overlay.activate()
        QMessageBox.critical(self, "Error", msg)
        self._overlay.deactivate()

    def _sep(self):
        f = QFrame(); f.setFixedHeight(1)
        f.setStyleSheet(f"background:{BORDER}; border:none;")
        return f

    def _btn_pri(self):
        return f"""
            QPushButton {{
                background: {RED};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 800;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background: {RED_H};
            }}
            QPushButton:pressed {{
                background: #BE123C;
            }}
        """

    def _btn_sec(self):
        return f"""
            QPushButton {{
                background:#121212; color:{TEXT_SEC}; border:1px solid {BORDER};
                border-radius:8px; font-size:12px; font-weight:700; padding:0 16px;
            }}
            QPushButton:hover {{ color:{TEXT_PRI}; border-color:#444; background:#1E1E1E; }}
        """

    def _btn_danger(self):
        return """
            QPushButton {
                background:transparent; color:#EF4444;
                border:1px solid rgba(239,68,68,0.25);
                border-radius:8px; font-size:12px; font-weight:700; padding:0 16px;
            }
            QPushButton:hover { background:rgba(239,68,68,0.1); border-color:#EF4444; }
        """

    def _input_style(self):
        return f"""
            QLineEdit {{
                background:#121212; color:{TEXT_PRI};
                border:1.5px solid {BORDER}; border-radius:8px;
                padding:0 14px; font-size:13px;
            }}
            QLineEdit:focus {{ border-color:{RED}; }}
        """

    def _combo_style(self):
        return f"""
            QComboBox {{
                background:#121212; color:{TEXT_PRI};
                border:1px solid {BORDER}; border-radius:7px;
                padding:0 12px; font-size:12px;
            }}
            QComboBox::drop-down {{ border:none; width:20px; }}
            QComboBox QAbstractItemView {{
                background:#121212; color:{TEXT_PRI};
                selection-background-color:{RED}; border:1px solid {BORDER};
            }}
        """

    def _msgbox_style(self):
        return f"""
            QMessageBox {{ background:#0C0C0C; color:{TEXT_PRI}; }}
            QLabel {{ color:{TEXT_PRI}; }}
            QPushButton {{
                background:#1F1F1F; color:white; border:1px solid {BORDER};
                border-radius:6px; padding:6px 16px; font-weight:700;
            }}
            QPushButton:hover {{ background:#2F2F2F; }}
        """