# ─── USER_REPOSITORY ─────────────────────────────────────────────

from database.connection import db
from core.security import hash_password

class UserRepository:

    # ── Login ──────────────────────────────────────────────────────────
    def get_by_username(self, username: str):
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, username, password_hash, id_person
                FROM users
                WHERE username = %s
            """, (username,))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id":            row[0],
                "username":      row[1],
                "password_hash": row[2],
                "id_person":     row[3],
            }

    # ── Registro ───────────────────────────────────────────────────────
    def validate_code(self, code: str) -> dict | None:
        with db.cursor() as cur:
            cur.execute("""
                SELECT cu.id, cu.code, cu.id_role, r.name
                FROM codes_users cu
                JOIN roles r ON r.id = cu.id_role
                WHERE cu.code = %s
            """, (code,))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id":        row[0],
                "code":      row[1],
                "id_role":   row[2],
                "role_name": row[3],
            }

    def create_user(self, data: dict) -> int:
        with db.transaction() as cur:

            cur.execute("""
                INSERT INTO people
                    (first_name, last_name, phone, email, birthdate, id_code_users)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data["first_name"],
                data["last_name"],
                data.get("phone"),
                data.get("email"),
                data.get("birthdate"),
                data["id_code_users"],
            ))
            id_person = cur.fetchone()[0]

            password_hash = hash_password(data["password"])
            cur.execute("""
                INSERT INTO users (id_person, username, password_hash)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (id_person, data["username"], password_hash))
            user_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO person_roles (id_person, id_role)
                VALUES (%s, %s)
            """, (id_person, data["id_role"]))

            return user_id

    def username_exists(self, username: str) -> bool:
        with db.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            return cur.fetchone() is not None

    def email_exists(self, email: str) -> bool:
        with db.cursor() as cur:
            cur.execute("SELECT 1 FROM people WHERE email = %s", (email,))
            return cur.fetchone() is not None

    def get_user_roles(self, user_id: int) -> list[str]:
        with db.cursor() as cur:
            cur.execute("""
                SELECT LOWER(r.name)
                FROM person_roles pr
                JOIN roles r ON r.id = pr.id_role
                WHERE pr.id_person = (
                    SELECT id_person FROM users WHERE id = %s
                );
            """, (user_id,))
            return [row[0] for row in cur.fetchall()]
