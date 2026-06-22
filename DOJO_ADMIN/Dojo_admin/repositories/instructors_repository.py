"""
repositories/instructors_repository.py
CRUD para instructores (people + instructors).
"""

from database.connection import db


class InstructorsRepository:

    # ── Listado ───────────────────────────────────────────────────────
    def get_all(self, search: str = "") -> list:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            query = """
                SELECT
                    i.id,
                    p.first_name || ' ' || p.last_name  AS nombre,
                    COALESCE(p.phone, '—')              AS telefono,
                    COALESCE(p.email, '—')              AS email,
                    p.created_at::date                  AS fecha_registro,
                    i.id_person,
                    p.first_name,
                    p.last_name,
                    p.phone,
                    p.email                             AS email_raw,
                    p.birthdate
                FROM instructors i
                JOIN people p ON p.id = i.id_person
            """
            params = []
            if search:
                query += """
                    WHERE
                        LOWER(p.first_name || ' ' || p.last_name) LIKE %s
                        OR LOWER(p.email)  LIKE %s
                        OR LOWER(p.phone)  LIKE %s
                """
                like = f"%{search.lower()}%"
                params = [like, like, like]

            query += " ORDER BY p.first_name, p.last_name"
            cur.execute(query, params)
            return cur.fetchall()
        finally:
            cur.close()
            db.release(conn)

    # ── Por ID ────────────────────────────────────────────────────────
    def get_by_id(self, instructor_id: int) -> dict | None:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    i.id, p.first_name, p.last_name,
                    p.phone, p.email, p.birthdate, i.id_person
                FROM instructors i
                JOIN people p ON p.id = i.id_person
                WHERE i.id = %s
            """, (instructor_id,))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row[0], "first_name": row[1], "last_name": row[2],
                "phone": row[3], "email": row[4], "birthdate": row[5],
                "id_person": row[6],
            }
        finally:
            cur.close()
            db.release(conn)

    # ── Crear ─────────────────────────────────────────────────────────
    def create(self, data: dict) -> int:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO people (first_name, last_name, phone, email, birthdate)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data["first_name"], data["last_name"],
                data.get("phone"), data.get("email"), data.get("birthdate"),
            ))
            person_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO instructors (id_person)
                VALUES (%s)
                RETURNING id
            """, (person_id,))
            instructor_id = cur.fetchone()[0]
            conn.commit()
            return instructor_id
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            db.release(conn)

    # ── Actualizar ────────────────────────────────────────────────────
    def update(self, instructor_id: int, data: dict):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id_person FROM instructors WHERE id = %s", (instructor_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError("Instructor no encontrado")
            person_id = row[0]

            cur.execute("""
                UPDATE people
                SET first_name = %s, last_name = %s,
                    phone = %s, email = %s, birthdate = %s
                WHERE id = %s
            """, (
                data["first_name"], data["last_name"],
                data.get("phone"), data.get("email"),
                data.get("birthdate"), person_id,
            ))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            db.release(conn)

    # ── Eliminar ──────────────────────────────────────────────────────
    def delete(self, instructor_id: int):
        """Elimina el instructor y su persona. Falla si tiene clases asignadas."""
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id_person FROM instructors WHERE id = %s", (instructor_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError("Instructor no encontrado")
            person_id = row[0]

            # Verificar si tiene clases
            cur.execute("SELECT COUNT(*) FROM classes WHERE id_instructor = %s", (instructor_id,))
            count = cur.fetchone()[0]
            if count > 0:
                raise ValueError(
                    f"No se puede eliminar: el instructor tiene {count} clase(s) asignada(s)."
                )

            cur.execute("DELETE FROM instructors WHERE id = %s", (instructor_id,))
            cur.execute("DELETE FROM people WHERE id = %s", (person_id,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            db.release(conn)

    # ── Estadísticas ──────────────────────────────────────────────────
    def get_class_count(self, instructor_id: int) -> int:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM classes WHERE id_instructor = %s",
                (instructor_id,)
            )
            return cur.fetchone()[0]
        finally:
            cur.close()
            db.release(conn)

    def get_recent_classes(self, instructor_id: int) -> list:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    c.date,
                    COALESCE(sc.name, 'Sin nombre') AS clase,
                    COALESCE(ma.name, '—')           AS arte_marcial
                FROM classes c
                LEFT JOIN schedule sc     ON sc.id = c.id_schedule
                LEFT JOIN martial_arts ma ON ma.id = sc.id_martial_art
                WHERE c.id_instructor = %s
                ORDER BY c.date DESC
                LIMIT 8
            """, (instructor_id,))
            return cur.fetchall()
        finally:
            cur.close()
            db.release(conn)

    # ── Validaciones ──────────────────────────────────────────────────
    def email_exists(self, email: str, exclude_person_id: int = None) -> bool:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            if exclude_person_id:
                cur.execute(
                    "SELECT 1 FROM people WHERE email = %s AND id != %s",
                    (email, exclude_person_id)
                )
            else:
                cur.execute("SELECT 1 FROM people WHERE email = %s", (email,))
            return cur.fetchone() is not None
        finally:
            cur.close()
            db.release(conn)
    # ── Artes marciales del instructor ────────────────────────────────────
    def get_martial_arts(self) -> list:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM martial_arts ORDER BY name")
            return [{"id": r[0], "name": r[1]} for r in cur.fetchall()]
        finally:
            cur.close()
            db.release(conn)

    def get_instructor_martial_arts(self, instructor_id: int) -> list:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT ima.id, ma.id, ma.name, ima.can_promote
                FROM instructor_martial_arts ima
                JOIN martial_arts ma ON ma.id = ima.id_martial_art
                WHERE ima.id_instructor = %s
                ORDER BY ma.name
            """, (instructor_id,))
            return [
                {"id": r[0], "ma_id": r[1], "ma_name": r[2], "can_promote": r[3]}
                for r in cur.fetchall()
            ]
        finally:
            cur.close(); db.release(conn)

    def assign_instructor_martial_art(self, instructor_id: int, martial_art_id: int, can_promote: bool):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO instructor_martial_arts (id_instructor, id_martial_art, can_promote)
                VALUES (%s, %s, %s)
                ON CONFLICT (id_instructor, id_martial_art)
                DO UPDATE SET can_promote = EXCLUDED.can_promote
            """, (instructor_id, martial_art_id, can_promote))
            conn.commit()
        except:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    def remove_instructor_martial_art(self, ima_id: int):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM instructor_martial_arts WHERE id = %s", (ima_id,))
            conn.commit()
        except:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    def get_people_not_instructors(self) -> list:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT p.id, p.first_name || ' ' || p.last_name AS nombre,
                    COALESCE(p.email, '—') AS email,
                    COALESCE(p.phone, '—') AS telefono
                FROM people p
                WHERE p.id NOT IN (
                    SELECT id_person FROM instructors
                )
                ORDER BY p.first_name, p.last_name
            """)
            return [
                {"id": r[0], "nombre": r[1], "email": r[2], "telefono": r[3]}
                for r in cur.fetchall()
            ]
        finally:
            cur.close(); db.release(conn)

    def create_from_person(self, person_id: int) -> int:
        """Convierte una persona existente en instructor."""
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO instructors (id_person)
                VALUES (%s)
                RETURNING id
            """, (person_id,))
            instructor_id = cur.fetchone()[0]
            conn.commit()
            return instructor_id
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close(); db.release(conn)

    def create_person_and_instructor(self, data: dict) -> int:
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            # 1. Crear persona
            cur.execute("""
                INSERT INTO people (first_name, last_name, email, phone, birthdate)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data["first_name"],
                data["last_name"],
                data["email"],
                data["phone"],
                data["birthdate"]
            ))

            person_id = cur.fetchone()[0]

            # 2. Crear instructor
            cur.execute("""
                INSERT INTO instructors (id_person)
                VALUES (%s)
                RETURNING id
            """, (person_id,))

            instructor_id = cur.fetchone()[0]

            conn.commit()
            return instructor_id

        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            db.release(conn)