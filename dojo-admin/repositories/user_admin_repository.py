# ─── USER_ADMIN_REPOSITORY ─────────────────────────────────────────────

import bcrypt
from database.connection import db


class UserAdminRepository:
    """
    Administración de:
    - personas
    - usuarios
    - roles
    - códigos de invitación
    """

    # ─────────────────────────────────────────────────────────────
    # Personas + usuarios + roles
    # ─────────────────────────────────────────────────────────────
    def get_people_users(self, search=""):
        with db.cursor() as cur:
            query = """
                SELECT
                    p.id AS person_id,
                    COALESCE(p.first_name, '') AS first_name,
                    COALESCE(p.last_name, '') AS last_name,
                    COALESCE(p.email, '') AS email,
                    COALESCE(p.phone, '') AS phone,
                    u.id AS user_id,
                    COALESCE(u.username, '') AS username,
                    COALESCE(u.is_active, false) AS is_active,
                    COALESCE(
                        STRING_AGG(DISTINCT r.name, ', ' ORDER BY r.name),
                        ''
                    ) AS roles,
                    COALESCE(
                        ARRAY_AGG(DISTINCT r.id) FILTER (WHERE r.id IS NOT NULL),
                        '{}'
                    ) AS role_ids
                FROM people p
                LEFT JOIN users u ON u.id_person = p.id
                LEFT JOIN person_roles pr ON pr.id_person = p.id
                LEFT JOIN roles r ON r.id = pr.id_role
            """

            params = []
            conditions = []

            if search:
                term = f"%{search}%"
                conditions.append("""
                    (
                        LOWER(COALESCE(p.first_name, '')) LIKE LOWER(%s)
                        OR LOWER(COALESCE(p.last_name, '')) LIKE LOWER(%s)
                        OR LOWER(COALESCE(p.email, '')) LIKE LOWER(%s)
                        OR LOWER(COALESCE(p.phone, '')) LIKE LOWER(%s)
                        OR LOWER(COALESCE(u.username, '')) LIKE LOWER(%s)
                        OR LOWER(COALESCE(r.name, '')) LIKE LOWER(%s)
                    )
                """)
                params.extend([term, term, term, term, term, term])

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += """
                GROUP BY
                    p.id,
                    p.first_name,
                    p.last_name,
                    p.email,
                    p.phone,
                    u.id,
                    u.username,
                    u.is_active
                ORDER BY p.first_name, p.last_name;
            """

            cur.execute(query, params)
            return cur.fetchall()

    def get_person_detail(self, person_id: int):
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    p.id,
                    p.first_name,
                    p.last_name,
                    p.email,
                    p.phone,
                    p.birthdate,
                    u.id AS user_id,
                    u.username,
                    u.is_active
                FROM people p
                LEFT JOIN users u ON u.id_person = p.id
                WHERE p.id = %s;
            """, (person_id,))

            row = cur.fetchone()

            if not row:
                return None

            return {
                "person_id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "phone": row[4],
                "birthdate": row[5],
                "user_id": row[6],
                "username": row[7],
                "is_active": row[8],
            }

    def update_person(self, person_id: int, data: dict):
        with db.transaction() as cur:
            cur.execute("""
                UPDATE people
                SET
                    first_name = %s,
                    last_name = %s,
                    email = %s,
                    phone = %s
                WHERE id = %s;
            """, (
                data.get("first_name"),
                data.get("last_name"),
                data.get("email"),
                data.get("phone"),
                person_id,
            ))

    # ─────────────────────────────────────────────────────────────
    # Usuarios
    # ─────────────────────────────────────────────────────────────
    def set_user_active(self, user_id: int, is_active: bool):
        with db.transaction() as cur:
            cur.execute("""
                UPDATE users
                SET is_active = %s
                WHERE id = %s;
            """, (is_active, user_id))

    def update_username(self, user_id: int, username: str):
        with db.transaction() as cur:
            cur.execute("""
                UPDATE users
                SET username = %s
                WHERE id = %s;
            """, (username, user_id))

    def reset_password(self, user_id: int, new_password: str):
        password_hash = bcrypt.hashpw(
            new_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        with db.transaction() as cur:
            cur.execute("""
                UPDATE users
                SET password_hash = %s
                WHERE id = %s;
            """, (password_hash, user_id))

    # ─────────────────────────────────────────────────────────────
    # Roles
    # ─────────────────────────────────────────────────────────────
    def get_roles(self):
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, name
                FROM roles
                ORDER BY name;
            """)

            return cur.fetchall()

    def _get_role_names_by_ids(self, cur, role_ids):
        """
        Retorna los nombres de roles asociados a una lista de IDs.
        """
        if not role_ids:
            return set()

        cur.execute("""
            SELECT LOWER(name)
            FROM roles
            WHERE id = ANY(%s);
        """, (list(role_ids),))

        return {row[0] for row in cur.fetchall()}


    def _ensure_student_profile(self, cur, person_id: int):
        """
        Si la persona tiene rol Student, asegura que exista en students.
        No crea usuario, no crea cinturón, no crea membresía.
        Solo crea el perfil mínimo para que aparezca en Estudiantes y Asistencia.
        """
        cur.execute("""
            SELECT id
            FROM students
            WHERE id_person = %s;
        """, (person_id,))

        row = cur.fetchone()

        if row:
            return row[0]

        cur.execute("""
            INSERT INTO students (
                id_person,
                id_type_document,
                document,
                category_id,
                id_status,
                joined_date
            )
            VALUES (%s, NULL, NULL, NULL, NULL, CURRENT_DATE)
            ON CONFLICT (id_person) DO NOTHING
            RETURNING id;
        """, (person_id,))

        inserted = cur.fetchone()

        if inserted:
            return inserted[0]

        cur.execute("""
            SELECT id
            FROM students
            WHERE id_person = %s;
        """, (person_id,))

        row = cur.fetchone()
        return row[0] if row else None


    def _ensure_instructor_profile(self, cur, person_id: int):
        """
        Si la persona tiene rol Instructor, asegura que exista en instructors.
        """
        cur.execute("""
            SELECT id
            FROM instructors
            WHERE id_person = %s;
        """, (person_id,))

        row = cur.fetchone()

        if row:
            return row[0]

        cur.execute("""
            INSERT INTO instructors (id_person)
            VALUES (%s)
            ON CONFLICT (id_person) DO NOTHING
            RETURNING id;
        """, (person_id,))

        inserted = cur.fetchone()

        if inserted:
            return inserted[0]

        cur.execute("""
            SELECT id
            FROM instructors
            WHERE id_person = %s;
        """, (person_id,))

        row = cur.fetchone()
        return row[0] if row else None

    def set_person_roles(self, person_id: int, role_ids):
        with db.transaction() as cur:
            role_ids = list(role_ids or [])

            # Obtener nombres de roles antes de guardar
            role_names = self._get_role_names_by_ids(cur, role_ids)

            # Borrar relaciones actuales
            cur.execute("""
                DELETE FROM person_roles
                WHERE id_person = %s;
            """, (person_id,))

            # Insertar nuevas relaciones
            for role_id in role_ids:
                cur.execute("""
                    INSERT INTO person_roles (id_person, id_role)
                    VALUES (%s, %s);
                """, (person_id, role_id))

            # Sincronización funcional:
            # Si tiene rol student/estudiante, crear registro en students
            if "student" in role_names or "estudiante" in role_names:
                self._ensure_student_profile(cur, person_id)

            # Si tiene rol instructor, crear registro en instructors
            if "instructor" in role_names:
                self._ensure_instructor_profile(cur, person_id)

    def create_role(self, name: str):
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO roles (name)
                VALUES (%s)
                RETURNING id;
            """, (name,))

            new_id = cur.fetchone()[0]
            return new_id

    def rename_role(self, role_id: int, name: str):
        with db.transaction() as cur:
            cur.execute("""
                UPDATE roles
                SET name = %s
                WHERE id = %s;
            """, (name, role_id))

    def delete_role(self, role_id: int):
        with db.transaction() as cur:
            cur.execute("""
                DELETE FROM person_roles
                WHERE id_role = %s;
            """, (role_id,))

            cur.execute("""
                DELETE FROM codes_users
                WHERE id_role = %s;
            """, (role_id,))

            cur.execute("""
                DELETE FROM roles
                WHERE id = %s;
            """, (role_id,))

    # ─────────────────────────────────────────────────────────────
    # Códigos de invitación
    # ─────────────────────────────────────────────────────────────
    def get_invite_codes(self):
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    cu.id,
                    cu.code,
                    cu.id_role,
                    r.name AS role_name
                FROM codes_users cu
                JOIN roles r ON r.id = cu.id_role
                ORDER BY r.name, cu.code;
            """)

            return cur.fetchall()

    def create_invite_code(self, code: str, role_id: int):
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO codes_users (code, id_role)
                VALUES (%s, %s)
                RETURNING id;
            """, (code, role_id))

            new_id = cur.fetchone()[0]
            return new_id

    def delete_invite_code(self, code_id: int):
        with db.transaction() as cur:
            cur.execute("""
                DELETE FROM codes_users
                WHERE id = %s;
            """, (code_id,))

    # ─────────────────────────────────────────────────────────────
    # Eliminación profunda de una persona
    # Borra:
    # - asistencias como estudiante
    # - membresías del estudiante
    # - cinturones e historial
    # - clases/schedules si era instructor
    # - relaciones instructor-artes
    # - usuario
    # - roles asignados a la persona
    # - pagos asociados a la persona
    # - persona
    #
    # NO borra registros de roles globales.
    # ─────────────────────────────────────────────────────────────
    def delete_person_deep(self, person_id: int):
        with db.transaction() as cur:
            # ── Buscar estudiante asociado
            cur.execute("""
                SELECT id
                FROM students
                WHERE id_person = %s;
            """, (person_id,))
            student_row = cur.fetchone()
            student_id = student_row[0] if student_row else None

            # ── Buscar instructor asociado
            cur.execute("""
                SELECT id
                FROM instructors
                WHERE id_person = %s;
            """, (person_id,))
            instructor_row = cur.fetchone()
            instructor_id = instructor_row[0] if instructor_row else None

            # ─────────────────────────────────────────────
            # Si la persona es estudiante
            # ─────────────────────────────────────────────
            if student_id is not None:
                # Asistencias del estudiante
                cur.execute("""
                    DELETE FROM attendance
                    WHERE id_student = %s;
                """, (student_id,))

                # Membresías del estudiante
                cur.execute("""
                    DELETE FROM student_memberships
                    WHERE id_student = %s;
                """, (student_id,))

                # Cinturones e historial
                cur.execute("""
                    DELETE FROM students_belts_history
                    WHERE id_student = %s;
                """, (student_id,))

                cur.execute("""
                    DELETE FROM students_belts
                    WHERE id_student = %s;
                """, (student_id,))

                # Registro estudiante
                cur.execute("""
                    DELETE FROM students
                    WHERE id = %s;
                """, (student_id,))

            # ─────────────────────────────────────────────
            # Si la persona es instructor
            # ─────────────────────────────────────────────
            if instructor_id is not None:
                # Horarios del instructor
                cur.execute("""
                    SELECT id
                    FROM schedule
                    WHERE id_instructor = %s;
                """, (instructor_id,))
                schedule_ids = [row[0] for row in cur.fetchall()]

                if schedule_ids:
                    # Asistencias de clases asociadas a esos horarios
                    cur.execute("""
                        DELETE FROM attendance
                        WHERE id_class IN (
                            SELECT id
                            FROM classes
                            WHERE id_schedule = ANY(%s)
                        );
                    """, (schedule_ids,))

                    # Clases asociadas a esos horarios
                    cur.execute("""
                        DELETE FROM classes
                        WHERE id_schedule = ANY(%s);
                    """, (schedule_ids,))

                    # Horarios del instructor
                    cur.execute("""
                        DELETE FROM schedule
                        WHERE id = ANY(%s);
                    """, (schedule_ids,))

                # Clases donde aparezca como instructor directo
                cur.execute("""
                    DELETE FROM attendance
                    WHERE id_class IN (
                        SELECT id
                        FROM classes
                        WHERE id_instructor = %s
                    );
                """, (instructor_id,))

                cur.execute("""
                    DELETE FROM classes
                    WHERE id_instructor = %s;
                """, (instructor_id,))

                # Artes marciales del instructor
                cur.execute("""
                    DELETE FROM instructor_martial_arts
                    WHERE id_instructor = %s;
                """, (instructor_id,))

                # Registro instructor
                cur.execute("""
                    DELETE FROM instructors
                    WHERE id = %s;
                """, (instructor_id,))

            # ─────────────────────────────────────────────
            # Pagos asociados a la persona
            # ─────────────────────────────────────────────
            cur.execute("""
                SELECT id
                FROM payments
                WHERE id_person = %s;
            """, (person_id,))
            payment_ids = [row[0] for row in cur.fetchall()]

            if payment_ids:
                cur.execute("""
                    DELETE FROM payment_items
                    WHERE id_payments = ANY(%s);
                """, (payment_ids,))

                cur.execute("""
                    DELETE FROM payments
                    WHERE id = ANY(%s);
                """, (payment_ids,))

            # ─────────────────────────────────────────────
            # Usuario asociado
            # ─────────────────────────────────────────────
            cur.execute("""
                DELETE FROM users
                WHERE id_person = %s;
            """, (person_id,))

            # ─────────────────────────────────────────────
            # Roles asignados a la persona
            # Esto borra solo la relación persona-rol,
            # NO borra el rol global.
            # ─────────────────────────────────────────────
            cur.execute("""
                DELETE FROM person_roles
                WHERE id_person = %s;
            """, (person_id,))

            # ─────────────────────────────────────────────
            # Finalmente borrar persona
            # ─────────────────────────────────────────────
            cur.execute("""
                DELETE FROM people
                WHERE id = %s;
            """, (person_id,))
