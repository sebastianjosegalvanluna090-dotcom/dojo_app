import sys
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
from PyQt6.QtWidgets import QApplication
from services.auth_service import AuthService
from views.login_view import LoginView

def main():
    app = QApplication(sys.argv)

    auth_service = AuthService()
    window = LoginView(auth_service)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()