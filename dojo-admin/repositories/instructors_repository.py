"""
repositories/instructors_repository.py
CRUD para instructores (people + instructors).
"""

from database.connection import db


class InstructorsRepository:

    # ── Listado ───────────────────────────────────────────────────────
    def get_all(self, search: str = "", belt_id: int = None) -> list:
        with db.cursor() as cur:
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
                    p.birthdate,
                    COALESCE(i.is_sensei, false)        AS is_sensei
                FROM instructors i
                JOIN people p ON p.id = i.id_person
            """
            params = []
            conditions = []

            if belt_id is not None:
                query += """
                    JOIN instructor_belts ib ON ib.id_instructor = i.id AND ib.id_belt = %s
                """
                params.append(belt_id)

            if search:
                conditions.append("""
                    (LOWER(p.first_name || ' ' || p.last_name) LIKE %s
                    OR LOWER(p.email)  LIKE %s
                    OR LOWER(p.phone)  LIKE %s)
                """)
                like = f"%{search.lower()}%"
                params.extend([like, like, like])

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY p.first_name, p.last_name"
            cur.execute(query, params)
            return cur.fetchall()

    # ── Por ID ────────────────────────────────────────────────────────
    def get_by_id(self, instructor_id: int) -> dict | None:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    i.id, p.first_name, p.last_name,
                    p.phone, p.email, p.birthdate, i.id_person,
                    COALESCE(i.is_sensei, false) AS is_sensei
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
                "id_person": row[6], "is_sensei": row[7],
            }

    # ── Crear ─────────────────────────────────────────────────────────
    def create(self, data: dict) -> int:
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO people (first_name, last_name, phone, email, birthdate)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data["first_name"],
                data["last_name"],
                data.get("phone"),
                data.get("email"),
                data.get("birthdate"),
            ))

            person_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO instructors (id_person, is_sensei)
                VALUES (%s, %s)
                RETURNING id
            """, (
                person_id,
                bool(data.get("is_sensei")),
            ))

            instructor_id = cur.fetchone()[0]

            self._ensure_instructor_role(cur, person_id)

            return instructor_id

    # ── Actualizar ────────────────────────────────────────────────────
    def update(self, instructor_id: int, data: dict):
        with db.transaction() as cur:
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

            if "is_sensei" in data:
                cur.execute("""
                    UPDATE instructors
                    SET is_sensei = %s
                    WHERE id = %s
                """, (
                    bool(data["is_sensei"]),
                    instructor_id,
                ))

    # ── Eliminar ──────────────────────────────────────────────────────
    def delete(self, instructor_id: int):
        """
        Elimina solo el vínculo de instructor.
        No elimina la persona porque puede estar referenciada por users,
        students, pagos, roles u otros módulos.
        """
        with db.transaction() as cur:
            cur.execute(
                "SELECT id_person FROM instructors WHERE id = %s",
                (instructor_id,)
            )
            row = cur.fetchone()

            if not row:
                raise ValueError("Instructor no encontrado")

            person_id = row[0]

            # Verificar si tiene clases asignadas
            cur.execute(
                "SELECT COUNT(*) FROM classes WHERE id_instructor = %s",
                (instructor_id,)
            )
            count = cur.fetchone()[0]

            if count > 0:
                raise ValueError(
                    f"No se puede eliminar: el instructor tiene {count} clase(s) asignada(s)."
                )

            # Eliminar artes marciales asignadas
            cur.execute(
                "DELETE FROM instructor_martial_arts WHERE id_instructor = %s",
                (instructor_id,)
            )

            # Eliminar solo el registro de instructor
            cur.execute(
                "DELETE FROM instructors WHERE id = %s",
                (instructor_id,)
            )

            # Quitar SOLO el rol instructor
            cur.execute("""
                DELETE FROM person_roles pr
                USING roles r
                WHERE pr.id_role = r.id
                AND pr.id_person = %s
                AND LOWER(r.name) = 'instructor'
            """, (person_id,))


    # ── Estadísticas ──────────────────────────────────────────────────
    def get_class_count(self, instructor_id: int) -> int:
        with db.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM classes WHERE id_instructor = %s",
                (instructor_id,)
            )
            return cur.fetchone()[0]

    def get_class_counts_batch(self, instructor_ids: list[int]) -> dict[int, int]:
        """Retorna {id_instructor: count} para todos los IDs dados."""
        if not instructor_ids:
            return {}
        with db.cursor() as cur:
            cur.execute(
                "SELECT id_instructor, COUNT(*) FROM classes WHERE id_instructor = ANY(%s) GROUP BY id_instructor",
                (instructor_ids,)
            )
            return dict(cur.fetchall())

    def get_instructor_martial_arts_batch(self, instructor_ids: list[int]) -> dict[int, list[dict]]:
        """Retorna {id_instructor: [{ma_id, ma_name, can_promote}, ...]}."""
        if not instructor_ids:
            return {}
        with db.cursor() as cur:
            cur.execute("""
                SELECT ima.id_instructor, ma.id, ma.name, ima.can_promote
                FROM instructor_martial_arts ima
                JOIN martial_arts ma ON ma.id = ima.id_martial_art
                WHERE ima.id_instructor = ANY(%s)
                ORDER BY ma.name
            """, (instructor_ids,))
            result: dict[int, list[dict]] = {}
            for row in cur.fetchall():
                id_inst = row[0]
                entry = {"ma_id": row[1], "ma_name": row[2], "can_promote": row[3]}
                result.setdefault(id_inst, []).append(entry)
            return result

    def get_recent_classes(self, instructor_id: int) -> list:
        with db.cursor() as cur:
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

    # ── Validaciones ──────────────────────────────────────────────────
    def email_exists(self, email: str, exclude_person_id: int = None) -> bool:
        with db.cursor() as cur:
            if exclude_person_id:
                cur.execute(
                    "SELECT 1 FROM people WHERE email = %s AND id != %s",
                    (email, exclude_person_id)
                )
            else:
                cur.execute("SELECT 1 FROM people WHERE email = %s", (email,))
            return cur.fetchone() is not None

    def _ensure_instructor_role(self, cur, person_id: int):
        """
        Asegura que la persona tenga el rol instructor en person_roles.
        """
        cur.execute(
            "SELECT id FROM roles WHERE LOWER(name) = 'instructor'"
        )
        row = cur.fetchone()

        if not row:
            raise ValueError("No existe el rol 'instructor' en la tabla roles")

        role_id = row[0]

        cur.execute("""
            SELECT 1
            FROM person_roles
            WHERE id_person = %s
            AND id_role = %s
        """, (person_id, role_id))

        exists = cur.fetchone()

        if not exists:
            cur.execute("""
                INSERT INTO person_roles (id_person, id_role)
                VALUES (%s, %s)
            """, (person_id, role_id))

    def sync_instructor_roles(self):
        """
        Asigna el rol instructor a todas las personas que existen en instructors.
        Útil para corregir instructores creados antes de esta actualización.
        """
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO person_roles (id_person, id_role)
                SELECT i.id_person, r.id
                FROM instructors i
                CROSS JOIN roles r
                WHERE LOWER(r.name) = 'instructor'
                AND NOT EXISTS (
                    SELECT 1
                    FROM person_roles pr
                    WHERE pr.id_person = i.id_person
                        AND pr.id_role = r.id
                )
            """)

    # ── Artes marciales del instructor ────────────────────────────────────
    def get_martial_arts(self) -> list:
        with db.cursor() as cur:
            cur.execute("SELECT id, name FROM martial_arts ORDER BY name")
            return [{"id": r[0], "name": r[1]} for r in cur.fetchall()]

    def get_instructor_martial_arts(self, instructor_id: int) -> list:
        with db.cursor() as cur:
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

    def assign_instructor_martial_art(self, instructor_id: int, martial_art_id: int, can_promote: bool):
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO instructor_martial_arts (id_instructor, id_martial_art, can_promote)
                VALUES (%s, %s, %s)
                ON CONFLICT (id_instructor, id_martial_art)
                DO UPDATE SET can_promote = EXCLUDED.can_promote
            """, (instructor_id, martial_art_id, can_promote))

    def remove_instructor_martial_art(self, ima_id: int):
        with db.transaction() as cur:
            cur.execute("DELETE FROM instructor_martial_arts WHERE id = %s", (ima_id,))

    def get_people_not_instructors(self) -> list:
        with db.cursor() as cur:
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

    def create_from_person(self, person_id: int) -> int:
        """Convierte una persona existente en instructor y le asigna el rol instructor."""
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO instructors (id_person)
                VALUES (%s)
                RETURNING id
            """, (person_id,))

            instructor_id = cur.fetchone()[0]

            self._ensure_instructor_role(cur, person_id)

            return instructor_id

    def create_person_and_instructor(self, data: dict) -> int:
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO people (first_name, last_name, email, phone, birthdate)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data["first_name"],
                data["last_name"],
                data.get("email"),
                data.get("phone"),
                data.get("birthdate")
            ))

            person_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO instructors (id_person)
                VALUES (%s)
                RETURNING id
            """, (person_id,))

            instructor_id = cur.fetchone()[0]

            self._ensure_instructor_role(cur, person_id)

            return instructor_id

    # ── Nombrar Sensei ────────────────────────────────────────────────
    def appoint_sensei(self, instructor_id: int):
        with db.transaction() as cur:
            cur.execute("""
                UPDATE instructors
                SET is_sensei = false
                WHERE is_sensei = true
            """)
            cur.execute("""
                UPDATE instructors
                SET is_sensei = true
                WHERE id = %s
            """, (instructor_id,))

    # ── Opciones para filtro de cinturones ────────────────────────────
    def get_belt_filter_options(self) -> list[dict]:
        with db.cursor() as cur:
            cur.execute("""
                SELECT b.id, b.name, ma.name
                FROM belts b
                JOIN martial_arts ma ON ma.id = b.id_martial_art
                ORDER BY ma.name, b.orden
            """)
            return [{"id": r[0], "name": r[1], "ma_name": r[2]} for r in cur.fetchall()]

    # ── Cinturones batch ──────────────────────────────────────────────
    def get_instructor_belts_batch(self, instructor_ids: list[int]) -> dict[int, list[dict]]:
        if not instructor_ids:
            return {}

        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    ib.id_instructor,
                    ma.id, ma.name,
                    b.id, b.name,
                    b.color, b.pre_color,
                    COALESCE(b.grades, 0),
                    COALESCE(b.grade_color, '#FFFFFF'),
                    b.orden
                FROM instructor_belts ib
                JOIN martial_arts ma ON ma.id = ib.id_martial_art
                JOIN belts b ON b.id = ib.id_belt
                WHERE ib.id_instructor = ANY(%s)
                ORDER BY ib.id_instructor, ma.name, b.orden
            """, (instructor_ids,))

            result = {}
            for r in cur.fetchall():
                instructor_id = r[0]
                item = {
                    "ma_id": r[1], "ma_name": r[2],
                    "belt_id": r[3], "belt_name": r[4],
                    "color": r[5], "pre_color": r[6],
                    "grades": r[7], "grade_color": r[8],
                    "orden": r[9],
                }
                result.setdefault(instructor_id, []).append(item)
            return result

    # ── Cinturones por arte marcial ───────────────────────────────────
    def get_belts_by_martial_art(self, martial_art_id: int) -> list[dict]:
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, name, color, pre_color,
                       COALESCE(grades, 0),
                       COALESCE(grade_color, '#FFFFFF'),
                       orden
                FROM belts
                WHERE id_martial_art = %s
                ORDER BY orden
            """, (martial_art_id,))
            return [
                {
                    "id": r[0], "name": r[1],
                    "color": r[2], "pre_color": r[3],
                    "grades": r[4], "grade_color": r[5],
                    "orden": r[6],
                }
                for r in cur.fetchall()
            ]

    # ── Guardar cinturones del instructor ─────────────────────────────
    def save_instructor_belts(self, instructor_id: int, belts: list[dict]):
        with db.transaction() as cur:
            for item in belts:
                id_martial_art = item.get("id_martial_art")
                id_belt = item.get("id_belt")
                if not id_martial_art or not id_belt:
                    continue
                cur.execute("""
                    INSERT INTO instructor_belts (id_instructor, id_martial_art, id_belt)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id_instructor, id_martial_art)
                    DO UPDATE SET id_belt = EXCLUDED.id_belt, assigned_at = CURRENT_TIMESTAMP
                """, (instructor_id, id_martial_art, id_belt))
