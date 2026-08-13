from database.connection import db
from core.security import hash_password, verify_password
from datetime import date


class RecoveryRepository:

    def save_recovery_data(self, user_id: int, birthdate, security_word: str):
        normalized = security_word.strip().lower()
        word_hash = hash_password(normalized)
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO user_security_recovery
                    (id_user, birthdate, security_word_hash)
                VALUES (%s, %s, %s)
                ON CONFLICT (id_user)
                DO UPDATE SET
                    birthdate = EXCLUDED.birthdate,
                    security_word_hash = EXCLUDED.security_word_hash
            """, (user_id, birthdate, word_hash))

    def get_recovery_by_username(self, username: str) -> dict | None:
        with db.cursor() as cur:
            cur.execute("""
                SELECT u.id, usr.birthdate, usr.security_word_hash
                FROM users u
                JOIN user_security_recovery usr ON usr.id_user = u.id
                WHERE u.username = %s
            """, (username,))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "birthdate": row[1],
                "security_word_hash": row[2],
            }

    def verify_birthdate(self, username: str, birthdate) -> bool:
        with db.cursor() as cur:
            cur.execute("""
                SELECT 1
                FROM users u
                JOIN user_security_recovery usr ON usr.id_user = u.id
                WHERE u.username = %s AND usr.birthdate = %s
            """, (username.strip(), birthdate))
            return cur.fetchone() is not None

    def verify_security_word(self, username: str, security_word: str) -> bool:
        with db.cursor() as cur:
            cur.execute("""
                SELECT usr.security_word_hash
                FROM users u
                JOIN user_security_recovery usr ON usr.id_user = u.id
                WHERE u.username = %s
            """, (username.strip(),))
            row = cur.fetchone()
            if not row:
                return False
            normalized = security_word.strip().lower()
            return verify_password(normalized, row[0])

    def reset_password(self, username: str, new_password: str):
        password_hash = hash_password(new_password)
        with db.transaction() as cur:
            cur.execute("""
                UPDATE users
                SET password_hash = %s
                WHERE username = %s
            """, (password_hash, username.strip()))
