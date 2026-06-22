"""
app/main.py  — punto de entrada principal con soporte i18n en caliente.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt

# ── Cargar idioma guardado ANTES de importar cualquier vista ──────────
from config import settings as cfg
from core.i18n import i18n, tr

_saved_lang = cfg.get("language", "es")
if _saved_lang != "es":
    i18n._load(_saved_lang)   # carga sin emitir señal (no hay vistas aún)

# ── Importaciones de vistas ───────────────────────────────────────────
from services.auth_service import AuthService
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.students_view import StudentsView
from database.connection import db

# ─── PALETA ───────────────────────────────────────────────────────────
BG_SIDEBAR  = "#111111"
BG_MAIN     = "#0D0D0D"
BORDER      = "#2A2A2A"
RED         = "#C8102E"
TEXT_PRI    = "#F0F0F0"
TEXT_MUT    = "#555555"
HOVER_BG    = "#1E1E1E"
ACTIVE_BG   = "#1A0A0C"


class SidebarButton(QPushButton):
    def __init__(self, icon, label_key, parent=None):
        super().__init__(parent)
        self._icon = icon
        self._key  = label_key          # clave i18n
        self._refresh_text()
        self.setFixedHeight(44)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: #888888;
                border: none;
                border-radius: 8px;
                text-align: left;
                padding-left: 12px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {HOVER_BG};
                color: {TEXT_PRI};
            }}
            QPushButton:checked {{
                background-color: {ACTIVE_BG};
                color: {TEXT_PRI};
                border-left: 3px solid {RED};
            }}
        """)

    def _refresh_text(self):
        self.setText(f"  {self._icon}  {tr(self._key)}")

    def retranslate(self):
        self._refresh_text()


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Senshi Fight Academy")
        self.setMinimumSize(1100, 680)
        self.setStyleSheet(f"background-color: {BG_MAIN};")
        self._build_ui()
        # Conectar señal de idioma para actualizar el sidebar en caliente
        i18n.language_changed.connect(self._retranslate_ui)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = self._make_sidebar()
        root.addWidget(sidebar)

        sep = QFrame()
        sep.setFixedWidth(1)
        sep.setStyleSheet(f"background-color: {BORDER};")
        root.addWidget(sep)

        self.content_area = QWidget()
        self.content_area.setStyleSheet(f"background-color: {BG_MAIN};")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.content_area, 1)

        self._show_dashboard()
        self.btn_dashboard.setChecked(True)

    def _make_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet(f"background-color: {BG_SIDEBAR};")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(4)

        self.lbl_logo = QLabel("⚔  SENSHI")
        self.lbl_logo.setStyleSheet(f"""
            font-size: 16px; font-weight: 800;
            letter-spacing: 2px; color: {TEXT_PRI};
            padding: 0 8px 16px 8px;
        """)
        layout.addWidget(self.lbl_logo)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER}; margin-bottom: 8px;")
        layout.addWidget(sep)

        # Botones de navegación — usan claves i18n
        self.btn_dashboard  = SidebarButton("📊", "dashboard")
        self.btn_students   = SidebarButton("👥", "students")
        self.btn_classes    = SidebarButton("🗓️", "classes")
        self.btn_payments   = SidebarButton("💰", "payments")
        self.btn_expenses   = SidebarButton("📉", "expenses")
        self.btn_belts      = SidebarButton("🥋", "martial_arts")
        self.btn_inventory  = SidebarButton("📦", "inventory")
        self.btn_reports    = SidebarButton("📈", "reports")
        self.btn_settings   = SidebarButton("⚙️",  "settings")

        self._nav_buttons = [
            self.btn_dashboard, self.btn_students, self.btn_classes,
            self.btn_payments, self.btn_expenses, self.btn_belts,
            self.btn_inventory, self.btn_reports,
        ]

        for btn in self._nav_buttons:
            btn.clicked.connect(lambda _, b=btn: self._on_nav(b))
            layout.addWidget(btn)

        layout.addStretch()

        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background: {BORDER}; margin: 4px 0;")
        layout.addWidget(sep2)

        self.btn_settings.clicked.connect(lambda: self._on_nav_settings())
        layout.addWidget(self.btn_settings)

        self.lbl_user = QLabel(f"👤  {self.user.get('username', '')}")
        self.lbl_user.setStyleSheet(f"font-size: 11px; color: {TEXT_MUT}; padding: 8px 8px 0 8px;")
        layout.addWidget(self.lbl_user)

        self.btn_logout = QPushButton(tr("logout"))
        self.btn_logout.setFixedHeight(36)
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: #666;
                border: 1px solid {BORDER}; border-radius: 6px;
                font-size: 11px; margin-top: 6px;
            }}
            QPushButton:hover {{ color: {RED}; border-color: {RED}; }}
        """)
        self.btn_logout.clicked.connect(self._logout)
        layout.addWidget(self.btn_logout)

        return sidebar

    # ── Retraducciones en caliente ────────────────────────────────────
    def _retranslate_ui(self, _lang: str):
        """Actualiza todos los textos del sidebar sin reconstruir la UI."""
        for btn in self._nav_buttons + [self.btn_settings]:
            btn.retranslate()
        self.btn_logout.setText(tr("logout"))

    # ── Navegación ────────────────────────────────────────────────────
    def _on_nav(self, clicked_btn):
        for btn in self._nav_buttons:
            btn.setChecked(False)
        self.btn_settings.setChecked(False)
        clicked_btn.setChecked(True)

        if clicked_btn == self.btn_dashboard:
            self._show_dashboard()
        elif clicked_btn == self.btn_students:
            self._show_students()
        elif clicked_btn == self.btn_belts:
            self._show_belts()
        else:
            self._show_placeholder(clicked_btn.text().strip())

    def _on_nav_settings(self):
        for btn in self._nav_buttons:
            btn.setChecked(False)
        self.btn_settings.setChecked(True)
        self._show_settings()

    def _clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_dashboard(self):
        self._clear_content()
        view = DashboardView(db, self.user)
        self.content_layout.addWidget(view)

    def _show_students(self):
        self._clear_content()
        view = StudentsView()
        self.content_layout.addWidget(view)

    def _show_belts(self):
        self._clear_content()
        from views.belts_view import BeltsView
        view = BeltsView()
        self.content_layout.addWidget(view)

    def _show_settings(self):
        self._clear_content()
        from views.settings_view import SettingsView
        view = SettingsView()
        self.content_layout.addWidget(view)

    def _show_placeholder(self, name):
        self._clear_content()
        lbl = QLabel(f"{name}\n\nMódulo en desarrollo 🚧")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 18px;")
        self.content_layout.addWidget(lbl)

    def _logout(self):
        i18n.language_changed.disconnect(self._retranslate_ui)
        from views.login_view import LoginView
        from services.auth_service import AuthService
        self.login = LoginView(AuthService())
        self.login.show()
        self.close()


# ─── ENTRY POINT ──────────────────────────────────────────────────────
def main():
    os.environ["PYTHONIOENCODING"] = "utf-8"
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    auth_service = AuthService()

    def on_login_success(user, login_win):
        window = MainWindow(user)
        window.show()
        login_win.close()

    login = LoginView(auth_service)
    login._on_login_success = lambda user: on_login_success(user, login)
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()  