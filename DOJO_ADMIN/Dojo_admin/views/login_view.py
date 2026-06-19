from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel

class LoginView(QWidget):
    def __init__(self, auth_service):
        super().__init__()

        self.auth_service = auth_service

        self.setWindowTitle("Login")

        self.layout = QVBoxLayout()

        self.username = QLineEdit()
        self.username.setPlaceholderText("Usuario")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Contraseña")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn = QPushButton("Ingresar")
        self.label = QLabel("")

        self.btn.clicked.connect(self.login)

        self.layout.addWidget(self.username)
        self.layout.addWidget(self.password)
        self.layout.addWidget(self.btn)
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)

    def login(self):
        try:
            user = self.auth_service.login(
                self.username.text(),
                self.password.text()
            )
            self.label.setText("Login exitoso 🔥")

        except Exception as e:
            self.label.setText(str(e))