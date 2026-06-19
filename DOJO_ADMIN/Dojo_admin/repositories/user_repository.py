from database.connection import db

class UserRepository:

    def get_by_username(self, username: str):
        conn = db.get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, username, password_hash, id_person
            FROM users
            WHERE username = %s
        """, (username,))

        row = cursor.fetchone()

        cursor.close()
        db.release(conn)

        if not row:
            return None

        return {
            "id": row[0],
            "username": row[1],
            "password_hash": row[2],
            "id_person": row[3]
        }