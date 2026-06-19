import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from services.auth_service import AuthService
from views.login_view import LoginView
from views.dashboard_view import DashboardView
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
    def __init__(self, icon, label, parent=None):
        super().__init__(parent)
        self.setText(f"  {icon}  {label}")
        self.setFixedHeight(44)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._base_style = f"""
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
        """
        self.setStyleSheet(self._base_style)


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Senshi Fight Academy")
        self.setMinimumSize(1100, 680)
        self.setStyleSheet(f"background-color: {BG_MAIN};")

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        sidebar = self._make_sidebar()
        root.addWidget(sidebar)

        # Separador
        sep = QFrame()
        sep.setFixedWidth(1)
        sep.setStyleSheet(f"background-color: {BORDER};")
        root.addWidget(sep)

        # Área de contenido
        self.content_area = QWidget()
        self.content_area.setStyleSheet(f"background-color: {BG_MAIN};")
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout = content_layout
        root.addWidget(self.content_area, 1)

        # Mostrar dashboard por defecto
        self._show_dashboard()
        self.btn_dashboard.setChecked(True)

    def _make_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet(f"background-color: {BG_SIDEBAR};")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(4)

        # Logo
        logo = QLabel("⚔  SENSHI")
        logo.setStyleSheet(f"""
            font-size: 16px; font-weight: 800;
            letter-spacing: 2px; color: {TEXT_PRI};
            padding: 0 8px 16px 8px;
        """)
        layout.addWidget(logo)

        # Separador
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER}; margin-bottom: 8px;")
        layout.addWidget(sep)

        # Botones de navegación
        self.btn_dashboard   = SidebarButton("📊", "Dashboard")
        self.btn_students    = SidebarButton("👥", "Estudiantes")
        self.btn_classes     = SidebarButton("🥋", "Clases")
        self.btn_payments    = SidebarButton("💰", "Pagos")
        self.btn_expenses    = SidebarButton("📉", "Egresos")
        self.btn_belts       = SidebarButton("🏅", "Cinturones")
        self.btn_inventory   = SidebarButton("📦", "Inventario")
        self.btn_reports     = SidebarButton("📈", "Reportes")
        self.btn_settings    = SidebarButton("⚙️",  "Configuración")

        self._nav_buttons = [
            self.btn_dashboard, self.btn_students, self.btn_classes,
            self.btn_payments, self.btn_expenses, self.btn_belts,
            self.btn_inventory, self.btn_reports,
        ]

        for btn in self._nav_buttons:
            btn.clicked.connect(lambda _, b=btn: self._on_nav(b))
            layout.addWidget(btn)

        layout.addStretch()

        # Separador inferior
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background: {BORDER}; margin: 4px 0;")
        layout.addWidget(sep2)

        layout.addWidget(self.btn_settings)

        # Usuario logueado
        user_lbl = QLabel(f"👤  {self.user.get('username', '')}")
        user_lbl.setStyleSheet(f"""
            font-size: 11px; color: {TEXT_MUT};
            padding: 8px 8px 0 8px;
        """)
        layout.addWidget(user_lbl)

        # Cerrar sesión
        btn_logout = QPushButton("Cerrar sesión")
        btn_logout.setFixedHeight(36)
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: #666;
                border: 1px solid {BORDER};
                border-radius: 6px;
                font-size: 11px;
                margin-top: 6px;
            }}
            QPushButton:hover {{
                color: {RED};
                border-color: {RED};
            }}
        """)
        btn_logout.clicked.connect(self._logout)
        layout.addWidget(btn_logout)

        return sidebar

    def _on_nav(self, clicked_btn):
        # Desmarcar todos
        for btn in self._nav_buttons:
            btn.setChecked(False)
        clicked_btn.setChecked(True)

        # Mostrar vista correspondiente
        if clicked_btn == self.btn_dashboard:
            self._show_dashboard()
        else:
            self._show_placeholder(clicked_btn.text().strip())

    def _clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_dashboard(self):
        self._clear_content()
        view = DashboardView(db, self.user)
        self.content_layout.addWidget(view)

    def _show_placeholder(self, name):
        self._clear_content()
        lbl = QLabel(f"{name}\n\nMódulo en desarrollo 🚧")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 18px;")
        self.content_layout.addWidget(lbl)

    def _logout(self):
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