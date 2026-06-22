"""
views/settings_view.py
Vista de Configuración — selector de idioma + gestión de instructores.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QButtonGroup, QScrollArea,
    QStackedWidget
)
from PyQt6.QtCore import Qt

from core.i18n import i18n, tr, SUPPORTED_LANGUAGES
from config import settings as cfg

# ─── PALETA ───────────────────────────────────────────────────────────
BG_MAIN  = "#0D0D0D"
BG_CARD  = "#161616"
BG_SIDE  = "#111111"
BORDER   = "#2A2A2A"
RED      = "#C8102E"
RED_H    = "#E8152F"
TEXT_PRI = "#F0F0F0"
TEXT_SEC = "#888888"
TEXT_MUT = "#444444"
GREEN    = "#22C55E"

LANG_FLAGS = {
    "es": "🇪🇸",
    "en": "🇬🇧",
    "fr": "🇫🇷",
    "ja": "🇯🇵",
}


def _make_card(accent=None):
    card = QFrame()
    bl = f"border-left: 3px solid {accent};" if accent else ""
    card.setStyleSheet(f"""
        QFrame {{
            background-color: {BG_CARD}; border: 1px solid {BORDER};
            {bl} border-radius: 12px;
        }}
        QFrame * {{ border: none; background: transparent; }}
    """)
    return card


class _NavButton(QPushButton):
    def __init__(self, icon, text, parent=None):
        super().__init__(f"  {icon}  {text}", parent)
        self.setFixedHeight(42)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh_style(False)

    def _refresh_style(self, checked):
        if checked:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1A0A0C; color: {TEXT_PRI};
                    border: none; border-left: 3px solid {RED};
                    border-radius: 8px; text-align: left;
                    padding-left: 10px; font-size: 13px; font-weight: 600;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {TEXT_SEC};
                    border: none; border-radius: 8px; text-align: left;
                    padding-left: 13px; font-size: 13px;
                }}
                QPushButton:hover {{ background: #1A1A1A; color: {TEXT_PRI}; }}
            """)

    def setChecked(self, v):
        super().setChecked(v)
        self._refresh_style(v)


class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        self._status_timer = None
        self._lang_buttons: dict[str, QPushButton] = {}
        self._build_ui()
        i18n.language_changed.connect(self._on_language_changed)

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {BG_MAIN};")
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Panel izquierdo (nav) ─────────────────────────────────────
        nav_panel = QFrame()
        nav_panel.setFixedWidth(200)
        nav_panel.setStyleSheet(f"background-color: {BG_SIDE}; border-right: 1px solid {BORDER};")
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(12, 24, 12, 24)
        nav_layout.setSpacing(4)

        nav_title = QLabel(tr("settings").upper())
        nav_title.setStyleSheet(f"font-size: 10px; font-weight: 700; letter-spacing: 2px; color: {TEXT_MUT}; padding: 0 4px 12px 4px;")
        nav_layout.addWidget(nav_title)

        self.btn_nav_general     = _NavButton("⚙️",  "General")
        self.btn_nav_instructors = _NavButton("🥋", "Instructores")

        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        for btn in [self.btn_nav_general, self.btn_nav_instructors]:
            self._nav_group.addButton(btn)
            nav_layout.addWidget(btn)

        nav_layout.addStretch()
        root.addWidget(nav_panel)

        # ── Panel derecho (stack) ─────────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {BG_MAIN};")
        self.stack.addWidget(self._build_general_page())   # index 0
        self.stack.addWidget(self._build_instructors_page()) # index 1
        root.addWidget(self.stack, 1)

        # Seleccionar General por defecto
        self.btn_nav_general.setChecked(True)
        self.stack.setCurrentIndex(0)

        self.btn_nav_general.clicked.connect(lambda: self._switch(0, self.btn_nav_general))
        self.btn_nav_instructors.clicked.connect(lambda: self._switch(1, self.btn_nav_instructors))

    def _switch(self, index: int, btn: _NavButton):
        for b in [self.btn_nav_general, self.btn_nav_instructors]:
            b.setChecked(False)
        btn.setChecked(True)
        self.stack.setCurrentIndex(index)

    # ── Página General (idioma) ───────────────────────────────────────
    def _build_general_page(self):
        page = QWidget()
        page.setStyleSheet(f"background-color: {BG_MAIN};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        container.setStyleSheet(f"background-color: {BG_MAIN};")
        main = QVBoxLayout(container)
        main.setContentsMargins(40, 32, 40, 32)
        main.setSpacing(24)

        # Header
        hdr = QHBoxLayout()
        self.lbl_title = QLabel("⚙️  General")
        self.lbl_title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {TEXT_PRI};")
        hdr.addWidget(self.lbl_title); hdr.addStretch()
        main.addLayout(hdr)

        sep = QFrame(); sep.setFixedHeight(2)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.4 {RED}, stop:1 transparent); border: none;
        """)
        main.addWidget(sep)

        # Card idioma
        lang_card = _make_card(RED)
        ll = QVBoxLayout(lang_card)
        ll.setContentsMargins(24, 20, 24, 20); ll.setSpacing(16)

        top = QHBoxLayout()
        icon_lbl = QLabel("🌐"); icon_lbl.setStyleSheet("font-size: 20px;"); icon_lbl.setFixedWidth(32)
        tcol = QVBoxLayout(); tcol.setSpacing(2)
        self.lbl_lang_title = QLabel(tr("language"))
        self.lbl_lang_title.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {TEXT_PRI};")
        self.lbl_lang_desc = QLabel(tr("language_desc"))
        self.lbl_lang_desc.setStyleSheet(f"font-size: 12px; color: {TEXT_SEC};")
        tcol.addWidget(self.lbl_lang_title); tcol.addWidget(self.lbl_lang_desc)
        top.addWidget(icon_lbl); top.addLayout(tcol, 1)
        ll.addLayout(top)

        btn_grid = QHBoxLayout(); btn_grid.setSpacing(12)
        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)

        for code, name in SUPPORTED_LANGUAGES.items():
            flag = LANG_FLAGS.get(code, "🌐")
            btn = QPushButton(f"{flag}  {name}")
            btn.setCheckable(True)
            btn.setFixedHeight(48)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._style_lang_btn(btn, active=(code == i18n.current))
            btn.clicked.connect(lambda _, c=code: self._select_language(c))
            self._btn_group.addButton(btn)
            self._lang_buttons[code] = btn
            btn_grid.addWidget(btn)

        ll.addLayout(btn_grid)

        self.lbl_note = QLabel(tr("language_restart_note"))
        self.lbl_note.setStyleSheet(f"font-size: 11px; color: {TEXT_MUT}; font-style: italic;")
        ll.addWidget(self.lbl_note)
        main.addWidget(lang_card)
        main.addStretch()

        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setFixedHeight(28)
        self.lbl_status.setStyleSheet(f"color: {GREEN}; font-size: 13px; font-weight: 600;")
        main.addWidget(self.lbl_status)

        scroll.setWidget(container)
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        return page

    # ── Página Instructores ───────────────────────────────────────────
    def _build_instructors_page(self):
        from views.instructors_view import InstructorsView
        page = InstructorsView()
        return page

    # ── Helpers ───────────────────────────────────────────────────────
    def _style_lang_btn(self, btn: QPushButton, active: bool):
        if active:
            btn.setStyleSheet(f"""
                QPushButton {{ background: {RED}; color: white; border: none;
                    border-radius: 10px; font-size: 14px; font-weight: 700; }}
                QPushButton:hover {{ background: {RED_H}; }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{ background: #1E1E1E; color: {TEXT_SEC};
                    border: 1.5px solid {BORDER}; border-radius: 10px; font-size: 14px; }}
                QPushButton:hover {{ background: #2A2A2A; color: {TEXT_PRI}; border-color: #555; }}
                QPushButton:checked {{ background: {RED}; color: white; border: none; font-weight: 700; }}
            """)

    def _select_language(self, code: str):
        cfg.set_value("language", code)
        i18n.set_language(code)
        for c, btn in self._lang_buttons.items():
            self._style_lang_btn(btn, active=(c == code))
        self._show_status(tr("settings_saved"))

    def _on_language_changed(self, lang: str):
        self.lbl_title.setText("⚙️  General")
        self.lbl_lang_title.setText(tr("language"))
        self.lbl_lang_desc.setText(tr("language_desc"))
        self.lbl_note.setText(tr("language_restart_note"))

    def _show_status(self, msg: str):
        self.lbl_status.setText(msg)
        from PyQt6.QtCore import QTimer
        if self._status_timer:
            self._status_timer.stop()
        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(lambda: self.lbl_status.setText(""))
        self._status_timer.start(2500)