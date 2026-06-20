from repositories.user_repository import UserRepository
from core.security import verify_password

class AuthService:

    def __init__(self):
        self.repo = UserRepository()

    def login(self, username: str, password: str):

        user = self.repo.get_by_username(username)

        if not user:
            raise ValueError("Usuario no existe")

        if not verify_password(password, user["password_hash"]):  # password_hash
            raise ValueError("Contraseña incorrecta")

        return user 