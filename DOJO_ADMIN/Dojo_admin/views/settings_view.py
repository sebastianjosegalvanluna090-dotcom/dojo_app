# ─────────────────────────────────────────────────────────────
# SETTINGS_VIEW 
# ─────────────────────────────────────────────────────────────

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QButtonGroup, QScrollArea,
    QStackedWidget, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, 
    QRect
)
from PyQt6.QtGui import QColor

from core.i18n import i18n, tr, SUPPORTED_LANGUAGES
from config import settings as cfg


# 🎯 PALETA PREMIUM
BG_MAIN  = "#050505"
BG_CARD  = "#0C0C0C"
BG_SIDE  = "#090909"
BORDER   = "#1F1F1F"
RED      = "#E11D48"
RED_H    = "#F43F5E"
TEXT_PRI = "#FAFAFA"
TEXT_SEC = "#A3A3A3"
TEXT_MUT = "#525252"

LANG_FLAGS = {
    "es": "🇪🇸",
    "en": "🇬🇧",
    "fr": "🇫🇷",
    "ja": "🇯🇵",
}


# ─────────────────────────────────────────────────────────────
# CARD PREMIUM (con sombra)
# ─────────────────────────────────────────────────────────────
def _make_card(accent=None):
    card = QFrame()
    card.setObjectName("PremiumCard")

    bl = f"border-left: 4px solid {accent};" if accent else ""

    card.setStyleSheet(f"""
        QFrame#PremiumCard {{
            background-color: {BG_CARD};
            border: 1px solid {BORDER};
            {bl}
            border-radius: 12px;
        }}

        QFrame#PremiumCard QLabel {{
            background: transparent;
            border: none;
        }}

        QFrame#PremiumCard QWidget {{
            background: transparent;
        }}
    """)

    shadow = QGraphicsDropShadowEffect(card)
    shadow.setBlurRadius(14)
    shadow.setColor(QColor(0, 0, 0, 120))
    shadow.setOffset(0, 3)
    card.setGraphicsEffect(shadow)

    return card


# ─────────────────────────────────────────────────────────────
# BOTÓN NAV
# ─────────────────────────────────────────────────────────────
class _NavButton(QPushButton):
    def __init__(self, icon, text):
        super().__init__(f"  {icon}   {text}")
        self.setFixedHeight(44)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style(False)

    def _update_style(self, active):
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #161011;
                    color: {TEXT_PRI};
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 17px;
                    font-size: 13px;
                    font-weight: 700;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {TEXT_SEC};
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 17px;
                    font-size: 13px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background: #121212;
                    color: {TEXT_PRI};
                }}
            """)

    def setChecked(self, v):
        super().setChecked(v)
        self._update_style(v)


# ─────────────────────────────────────────────────────────────
# MAIN VIEW
# ─────────────────────────────────────────────────────────────
class SettingsView(QWidget):
    def __init__(self):
        super().__init__()

        self._lang_buttons = {}

        self._build_ui()
        i18n.language_changed.connect(self._on_language_changed)

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {BG_MAIN};")

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 🧭 NAV PANEL
        self.nav_panel = QFrame()
        self.nav_panel.setFixedWidth(220)
        self.nav_panel.setStyleSheet(f"""
            background-color: {BG_SIDE};
            border-right: 1px solid {BORDER};
        """)

        nav = self.nav_panel
        nav.setStyleSheet(f"""
            background-color: {BG_SIDE};
            border-right: 1px solid {BORDER};
        """)

        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(14, 28, 14, 28)

        title = QLabel(tr("settings").upper())
        title.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.5px;
        """)

        nav_layout.addWidget(title)
        nav_layout.addSpacing(10)

        self.btn_nav_general = _NavButton("⚙️", "General")
        self.btn_nav_instructors = _NavButton("🥋", "Instructores")
        self.btn_nav_users = _NavButton("👤", "Usuarios y roles")

        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        for b in [self.btn_nav_general, self.btn_nav_instructors, self.btn_nav_users]:
            self._nav_group.addButton(b)
            nav_layout.addWidget(b)

        nav_layout.addStretch()
        root.addWidget(nav)

        # 📄 STACK + ANIMACIÓN

        # Barra lateral animada
        self.nav_indicator = QFrame(self.nav_panel)
        self.nav_indicator.setFixedWidth(3)
        self.nav_indicator.setStyleSheet(f"""
            QFrame {{
                background-color: {RED};
                border-radius: 2px;
            }}
        """)
        self.nav_indicator.hide()

        self.nav_indicator_anim = QPropertyAnimation(self.nav_indicator, b"geometry", self)
        self.nav_indicator_anim.setDuration(220)
        self.nav_indicator_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        QTimer.singleShot(0, lambda: self._move_nav_indicator(self.btn_nav_general, animate=False))
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {BG_MAIN};")
        self.old_index = 0

        self._is_switching = False
        self.anim_current = None
        self.anim_next = None

        self.stack.addWidget(self._build_general_page())
        self.stack.addWidget(self._build_instructors_page())
        self.stack.addWidget(self._build_users_page())

        root.addWidget(self.stack, 1)

        # default
        self.btn_nav_general.setChecked(True)

        self.btn_nav_general.clicked.connect(lambda: self._switch(0, self.btn_nav_general))
        self.btn_nav_instructors.clicked.connect(lambda: self._switch(1, self.btn_nav_instructors))
        self.btn_nav_users.clicked.connect(lambda: self._switch(2, self.btn_nav_users))

    # 🎬 TRANSICIÓN
    def _switch(self, index, btn):
        if self._is_switching:
            return

        if index == self.stack.currentIndex():
            for b in [self.btn_nav_general, self.btn_nav_instructors, self.btn_nav_users]:
                b.setChecked(False)

            btn.setChecked(True)
            self._move_nav_indicator(btn)
            return

        self._is_switching = True

        for b in [self.btn_nav_general, self.btn_nav_instructors, self.btn_nav_users]:
            b.setChecked(False)

        btn.setChecked(True)
        self._move_nav_indicator(btn)

        self.stack.setCurrentIndex(index)
        self.old_index = index

        self._animate_current_page()

        QTimer.singleShot(240, self._unlock_switch)

    def _unlock_switch(self):
        self._is_switching = False

    def _animate_current_page(self):
        page = self.stack.currentWidget()

        if not page:
            return

        start_pos = QPoint(18, 0)
        end_pos = QPoint(0, 0)

        page.move(start_pos)

        self.anim_page = QPropertyAnimation(page, b"pos", self)
        self.anim_page.setDuration(220)
        self.anim_page.setStartValue(start_pos)
        self.anim_page.setEndValue(end_pos)
        self.anim_page.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim_page.start()

    def _move_nav_indicator(self, btn, animate=True):
        if not hasattr(self, "nav_indicator"):
            return

        pos = btn.mapTo(self.nav_panel, QPoint(0, 0))

        target = QRect(
            8,
            pos.y(),
            3,
            btn.height()
        )

        self.nav_indicator.show()
        self.nav_indicator.raise_()

        if not animate:
            self.nav_indicator.setGeometry(target)
            return

        self.nav_indicator_anim.stop()
        self.nav_indicator_anim.setStartValue(self.nav_indicator.geometry())
        self.nav_indicator_anim.setEndValue(target)
        self.nav_indicator_anim.start()

    # ─────────────────────────────────────────────────────────────
    # GENERAL PAGE
    # ─────────────────────────────────────────────────────────────
    def _build_general_page(self):
        page = QWidget()
        page.setStyleSheet(f"background-color: {BG_MAIN};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #080808;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #1F1F1F;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #333333;
            }
        """)

        container = QWidget()
        container.setStyleSheet("background: transparent;")

        main = QVBoxLayout(container)
        main.setContentsMargins(40, 32, 40, 32)
        main.setSpacing(24)

        # Header
        title = QLabel("⚙️  General")
        title.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 22px;
            font-weight: 800;
        """)
        main.addWidget(title)

        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.35 {RED}, stop:1 transparent);
            border: none;
        """)
        main.addWidget(sep)

        # Card idioma
        lang_card = _make_card(RED)
        ll = QVBoxLayout(lang_card)
        ll.setContentsMargins(24, 20, 24, 20)
        ll.setSpacing(16)

        lang_header = QHBoxLayout()

        icon_lbl = QLabel("🌐")
        icon_lbl.setFixedWidth(34)
        icon_lbl.setStyleSheet("font-size: 22px; background: transparent; border: none;")

        text_col = QVBoxLayout()
        text_col.setSpacing(3)

        self.lbl_lang_title = QLabel(tr("language"))
        self.lbl_lang_title.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 15px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)

        self.lbl_lang_desc = QLabel(tr("language_desc"))
        self.lbl_lang_desc.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 12px;
            background: transparent;
            border: none;
        """)

        text_col.addWidget(self.lbl_lang_title)
        text_col.addWidget(self.lbl_lang_desc)

        lang_header.addWidget(icon_lbl)
        lang_header.addLayout(text_col, 1)

        ll.addLayout(lang_header)

        row_container = QWidget()
        row_container.setStyleSheet("background: transparent; border: none;")

        row_layout = QHBoxLayout(row_container)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)

        for code, name in SUPPORTED_LANGUAGES.items():
            flag = LANG_FLAGS.get(code, "")
            btn = QPushButton(f"{flag}  {name}")

            btn.setCheckable(True)
            btn.setFixedHeight(46)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumWidth(150)

            self._style_lang_btn(btn, code == i18n.current)

            btn.clicked.connect(lambda _, c=code: self._select_language(c))

            self._lang_buttons[code] = btn
            self._btn_group.addButton(btn)

            row_layout.addWidget(btn)

        ll.addWidget(row_container)

        self.lbl_note = QLabel(tr("language_restart_note"))
        self.lbl_note.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 11px;
            font-style: italic;
            background: transparent;
            border: none;
        """)
        ll.addWidget(self.lbl_note)

        main.addWidget(lang_card)

        # Card atajos
        main.addWidget(self._build_shortcuts_card())

        main.addStretch()

        scroll.setWidget(container)

        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        return page

    def _build_shortcuts_card(self):
        card = _make_card("#3B82F6")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        top = QHBoxLayout()

        icon_lbl = QLabel("⌨️")
        icon_lbl.setFixedWidth(34)
        icon_lbl.setStyleSheet("font-size: 22px; background: transparent; border: none;")

        tcol = QVBoxLayout()
        tcol.setSpacing(3)

        lbl_title = QLabel("Atajos de Teclado")
        lbl_title.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 15px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)

        lbl_desc = QLabel("Acciones rápidas disponibles en el módulo de estudiantes para agilizar el flujo de trabajo.")
        lbl_desc.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 12px;
            background: transparent;
            border: none;
        """)

        tcol.addWidget(lbl_title)
        tcol.addWidget(lbl_desc)

        top.addWidget(icon_lbl)
        top.addLayout(tcol, 1)

        layout.addLayout(top)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER}; border: none;")
        layout.addWidget(sep)

        shortcuts = [
            ("Ctrl + N", "Crear nuevo estudiante"),
            ("Ctrl + R", "Actualizar lista de estudiantes"),
            ("Ctrl + F", "Enfocar el buscador de la barra superior"),
            ("Enter", "Ver detalle del estudiante seleccionado"),
            ("Ctrl + E", "Editar ficha del estudiante seleccionado"),
            ("Delete", "Eliminar de forma irreversible el registro"),
            ("Esc", "Limpiar selección activa y replegar paneles"),
        ]

        for keys, desc in shortcuts:
            layout.addWidget(self._shortcut_row(keys, desc))

        note = QLabel("Tip: selecciona primero una fila de la grilla para habilitar los atajos contextuales.")
        note.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 11px;
            font-style: italic;
            padding-top: 6px;
            background: transparent;
            border: none;
        """)
        layout.addWidget(note)

        return card


    def _shortcut_row(self, keys, description):
        row = QWidget()
        row.setStyleSheet("background: transparent; border: none;")

        hl = QHBoxLayout(row)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(14)

        key_lbl = QLabel(keys)
        key_lbl.setFixedWidth(98)
        key_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        key_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: #121212;
                color: {TEXT_PRI};
                border: 1px solid #222222;
                border-bottom: 3px solid #1C1C1C;
                border-radius: 6px;
                font-size: 10px;
                font-weight: 800;
                padding: 5px 8px;
            }}
        """)

        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 12px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)

        hl.addWidget(key_lbl)
        hl.addWidget(desc_lbl, 1)

        return row

    # ─────────────────────────────────────────────────────────────
    def _build_instructors_page(self):
        from views.instructors_view import InstructorsView
        return InstructorsView()

    def _build_users_page(self):
        from views.users_admin_view import UsersAdminView
        return UsersAdminView()

    # ─────────────────────────────────────────────────────────────
    def _style_lang_btn(self, btn, active):
        if active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background:{RED};
                    color:white;
                    border:none;
                    border-radius:8px;
                    font-size:13px;
                    font-weight:700;
                }}
                QPushButton:hover {{
                    background:{RED_H};
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background:#111111;
                    color:{TEXT_SEC};
                    border:1px solid {BORDER};
                    border-radius:8px;
                    font-size:13px;
                    font-weight:600;
                }}
                QPushButton:hover {{
                    background:#1A1A1A;
                    color:{TEXT_PRI};
                    border-color:#333;
                }}
            """)


    def _select_language(self, code):
        cfg.set_value("language", code)
        i18n.set_language(code)

        for c, b in self._lang_buttons.items():
            self._style_lang_btn(b, c == code)

    def _on_language_changed(self, _):
        try:
            self.lbl_lang_title.setText(tr("language"))
            self.lbl_lang_desc.setText(tr("language_desc"))
            self.lbl_note.setText(tr("language_restart_note"))
        except Exception:
            pass