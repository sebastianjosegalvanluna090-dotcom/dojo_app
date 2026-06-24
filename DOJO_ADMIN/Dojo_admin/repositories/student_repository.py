# ─── STUDENT_REPOSITORY ─────────────────────────────────────────────

from database.connection import db
from core.security import hash_password

class StudentRepository:

    def get_all(self, search: str = "", filters: dict = None) -> list:
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            filters = filters or {}

            martial_art_id = filters.get("martial_art_id")

            # Normalizar filtro de arte marcial
            if martial_art_id in ("", "0", 0, None):
                martial_art_id = None
            else:
                martial_art_id = int(martial_art_id)

            params = []
            conditions = []

            # ─────────────────────────────────────────────
            # JOIN dinámico según filtro de arte marcial
            # ─────────────────────────────────────────────
            if martial_art_id is None:
                # Sin filtro: todos los estudiantes, aunque no tengan cinturón
                belt_join = """
                    LEFT JOIN LATERAL (
                        SELECT
                            sb.id_belt
                        FROM students_belts sb
                        JOIN belts bx ON bx.id = sb.id_belt
                        LEFT JOIN martial_arts max ON max.id = bx.id_martial_art
                        WHERE sb.id_student = s.id
                        ORDER BY max.name, bx.orden ASC NULLS LAST, bx.name
                        LIMIT 1
                    ) sb_sel ON TRUE
                """
            else:
                # Con filtro: solo estudiantes que tengan cinturón en ese arte marcial
                belt_join = """
                    JOIN LATERAL (
                        SELECT
                            sb.id_belt
                        FROM students_belts sb
                        JOIN belts bx ON bx.id = sb.id_belt
                        WHERE sb.id_student = s.id
                        AND bx.id_martial_art = %s
                        ORDER BY bx.orden DESC NULLS LAST, bx.grades DESC NULLS LAST, bx.name
                        LIMIT 1
                    ) sb_sel ON TRUE
                """
                params.append(martial_art_id)


            query = f"""
                SELECT
                    s.id,
                    p.first_name || ' ' || p.last_name       AS nombre,
                    COALESCE(td.type_document || ': ' || s.document, '—') AS documento,
                    p.phone,
                    p.email,
                    COALESCE(st.status, 'Sin estado')         AS estado,
                    COALESCE(cat.name,  'Sin categoría')      AS categoria,
                    p.created_at::date                        AS fecha_ingreso,
                    s.id_person,
                    p.first_name,
                    p.last_name,
                    p.birthdate,
                    s.document                                AS doc_numero,
                    s.id_type_document,
                    s.id_status,
                    s.category_id,
                    COALESCE(b.name,      'Sin cinturón')     AS cinturon,
                    COALESCE(b.color,     '#888888')          AS belt_color,
                    COALESCE(b.pre_color, NULL)               AS belt_pre_color,
                    COALESCE(ma.name,     'Sin arte')         AS arte_marcial,
                    COALESCE(b.grades,    0)                  AS belt_grades,
                    COALESCE(b.grade_color, '#FFFFFF')        AS belt_grade_color,
                    b.id_martial_art                          AS belt_ma_id
                FROM students s
                JOIN people p              ON p.id  = s.id_person
                LEFT JOIN type_document td ON td.id = s.id_type_document
                LEFT JOIN status st        ON st.id = s.id_status
                LEFT JOIN categories cat   ON cat.id = s.category_id

                {belt_join}

                LEFT JOIN belts b         ON b.id = sb_sel.id_belt
                LEFT JOIN martial_arts ma ON ma.id = b.id_martial_art
            """

            # ─────────────────────────────────────────────
            # Filtros normales
            # ─────────────────────────────────────────────
            if search:
                conditions.append("""(
                    LOWER(p.first_name || ' ' || p.last_name) LIKE %s
                    OR LOWER(COALESCE(s.document, '')) LIKE %s
                    OR LOWER(COALESCE(p.email, ''))    LIKE %s
                    OR LOWER(COALESCE(p.phone, ''))    LIKE %s
                )""")
                like = f"%{search.lower()}%"
                params += [like, like, like, like]

            if filters.get("id_status"):
                conditions.append("s.id_status = %s")
                params.append(filters["id_status"])

            if filters.get("category_id"):
                conditions.append("s.category_id = %s")
                params.append(filters["category_id"])

            if filters.get("id_type_document"):
                conditions.append("s.id_type_document = %s")
                params.append(filters["id_type_document"])

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            # Si hay filtro por arte marcial, ordenar por cinturón de mayor a menor
            if martial_art_id is not None:
                query += """
                    ORDER BY
                        b.orden DESC NULLS LAST,
                        b.grades DESC NULLS LAST,
                        p.first_name,
                        p.last_name
                """
            else:
                query += """
                    ORDER BY
                        p.first_name,
                        p.last_name
                """

            cur.execute(query, params)
            return cur.fetchall()

        finally:
            cur.close()
            db.release(conn)
            
    def get_filter_options(self) -> dict:
        """Carga todas las opciones para los filtros de búsqueda."""
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, status FROM status ORDER BY status")
            statuses = cur.fetchall()
            cur.execute("SELECT id, name FROM categories ORDER BY name")
            categories = cur.fetchall()
            cur.execute("SELECT id, type_document FROM type_document ORDER BY type_document")
            doc_types = cur.fetchall()
            cur.execute("SELECT id, name FROM martial_arts ORDER BY name")
            martial_arts = cur.fetchall()
            return {
                "statuses": statuses,
                "categories": categories,
                "doc_types": doc_types,
                "martial_arts": martial_arts,
            }
        finally:
            cur.close()
            db.release(conn)

    def get_by_id(self, student_id: int) -> dict | None:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    s.id, p.first_name, p.last_name,
                    p.phone, p.email, p.birthdate,
                    s.document, s.id_type_document,
                    s.id_status, s.category_id, s.id_person,
                    s.joined_date
                FROM students s
                JOIN people p ON p.id = s.id_person
                WHERE s.id = %s
            """, (student_id,))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row[0], "first_name": row[1], "last_name": row[2],
                "phone": row[3], "email": row[4], "birthdate": row[5],
                "document": row[6], "id_type_document": row[7],
                "id_status": row[8], "category_id": row[9],
                "id_person": row[10], "joined_date": row[11],
            }
        finally:
            cur.close()
            db.release(conn)
    
    def _get_student_role_id(self, cur) -> int:
        """
        Busca el rol de estudiante.
        Acepta nombres como: estudiante, student.
        """
        cur.execute("""
            SELECT id
            FROM roles
            WHERE LOWER(name) IN ('estudiante', 'student')
            LIMIT 1
        """)
        row = cur.fetchone()

        if not row:
            raise ValueError("No existe un rol llamado 'Estudiante' o 'Student' en la tabla roles.")

        return row[0]
    
    def get_user_by_student_id(self, student_id: int) -> dict | None:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT u.id, u.username
                FROM users u
                JOIN students s ON s.id_person = u.id_person
                WHERE s.id = %s
                LIMIT 1
            """, (student_id,))
            row = cur.fetchone()

            if not row:
                return None

            return {
                "id": row[0],
                "username": row[1],
            }
        finally:
            cur.close()
            db.release(conn)

    def update_student_user_access(self, student_id: int, username: str = None, password: str = None):
        """
        Actualiza usuario y/o contraseña del estudiante.
        Si password viene vacío, no cambia la contraseña.
        """
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                SELECT u.id
                FROM users u
                JOIN students s ON s.id_person = u.id_person
                WHERE s.id = %s
                LIMIT 1
            """, (student_id,))
            row = cur.fetchone()

            if not row:
                raise ValueError("El estudiante no tiene usuario asociado.")

            user_id = row[0]

            username = (username or "").strip()
            password = (password or "").strip()

            if username:
                cur.execute("""
                    SELECT 1
                    FROM users
                    WHERE username = %s
                    AND id <> %s
                """, (username, user_id))

                if cur.fetchone():
                    raise ValueError("Ese nombre de usuario ya está en uso.")

                cur.execute("""
                    UPDATE users
                    SET username = %s
                    WHERE id = %s
                """, (username, user_id))

            if password:
                cur.execute("""
                    UPDATE users
                    SET password_hash = %s
                    WHERE id = %s
                """, (hash_password(password), user_id))

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cur.close()
            db.release(conn)


    def _username_exists_tx(self, cur, username: str) -> bool:
        cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
        return cur.fetchone() is not None


    def _generate_student_username(self, cur, data: dict) -> str:
        """
        Genera username único para estudiante.
        Prioridad:
        1. username enviado desde el formulario
        2. documento
        3. nombre.apellido
        """
        raw_username = (data.get("username") or "").strip()

        if raw_username:
            base = raw_username.lower().replace(" ", "")
        elif data.get("document"):
            base = str(data.get("document")).strip().lower().replace(" ", "")
        else:
            first = str(data.get("first_name", "")).strip().lower().replace(" ", "")
            last = str(data.get("last_name", "")).strip().lower().replace(" ", "")
            base = f"{first}.{last}".strip(".")

        if not base:
            base = "estudiante"

        username = base
        counter = 1

        while self._username_exists_tx(cur, username):
            counter += 1
            username = f"{base}{counter}"

        return username

    def create(self, data: dict) -> dict:
        """
        Crea:
        1. people
        2. students
        3. users
        4. person_roles como Estudiante

        Retorna el id del estudiante.
        """
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            # 1. Insertar en people
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

            # 2. Insertar en students
            cur.execute("""
                INSERT INTO students (
                    id_person,
                    id_type_document,
                    document,
                    id_status,
                    category_id,
                    joined_date
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                person_id,
                data.get("id_type_document"),
                data.get("document"),
                data.get("id_status"),
                data.get("category_id"),
                data.get("joined_date"),
            ))

            student_id = cur.fetchone()[0]

            # 3. Buscar rol estudiante
            student_role_id = self._get_student_role_id(cur)

            # 4. Generar username
            username = self._generate_student_username(cur, data)

            # 5. Password temporal
            # Si el formulario manda password, usa esa.
            # Si no, usa el documento como contraseña temporal.
            temp_password = data.get("password")

            if not temp_password:
                if data.get("document"):
                    temp_password = str(data.get("document")).strip()
                else:
                    temp_password = f"estudiante{student_id}"

            password_hash = hash_password(temp_password)

            # 6. Crear usuario
            cur.execute("""
                INSERT INTO users (id_person, username, password_hash)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (
                person_id,
                username,
                password_hash,
            ))

            user_id = cur.fetchone()[0]

            # 7. Asignar rol estudiante
            cur.execute("""
                INSERT INTO person_roles (id_person, id_role)
                VALUES (%s, %s)
            """, (
                person_id,
                student_role_id,
            ))

            conn.commit()

            return {
                "student_id": student_id,
                "user_id": user_id,
                "username": username,
                "password": temp_password,
}

        except Exception:
            conn.rollback()
            raise

        finally:
            cur.close()
            db.release(conn)

    def update(self, student_id: int, data: dict):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            # Obtener id_person
            cur.execute("SELECT id_person FROM students WHERE id = %s", (student_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError("Estudiante no encontrado")
            person_id = row[0]

            # Actualizar people
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

            # Actualizar students
            cur.execute("""
                UPDATE students
                SET id_type_document = %s, document = %s,
                    id_status = %s, category_id = %s,
                    joined_date = %s
                WHERE id = %s
            """, (
                data.get("id_type_document"),
                data.get("document"),
                data.get("id_status"),
                data.get("category_id"),
                data.get("joined_date"),
                student_id,
            ))

            # Actualizar usuario si viene username/password
            username = (data.get("username") or "").strip()
            password = (data.get("password") or "").strip()

            if username or password:
                cur.execute("""
                    SELECT u.id
                    FROM users u
                    JOIN students s ON s.id_person = u.id_person
                    WHERE s.id = %s
                    LIMIT 1
                """, (student_id,))
                user_row = cur.fetchone()

                if user_row:
                    user_id = user_row[0]

                    if username:
                        cur.execute("""
                            SELECT 1
                            FROM users
                            WHERE username = %s
                            AND id <> %s
                        """, (username, user_id))

                        if cur.fetchone():
                            raise ValueError("Ese nombre de usuario ya está en uso.")

                        cur.execute("""
                            UPDATE users
                            SET username = %s
                            WHERE id = %s
                        """, (username, user_id))

                    if password:
                        cur.execute("""
                            UPDATE users
                            SET password_hash = %s
                            WHERE id = %s
                        """, (hash_password(password), user_id))

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            db.release(conn)

    def get_type_documents(self) -> list:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, type_document FROM type_document ORDER BY type_document")
            return cur.fetchall()
        finally:
            cur.close()
            db.release(conn)

    def get_statuses(self) -> list:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, status FROM status ORDER BY status")
            return cur.fetchall()
        finally:
            cur.close()
            db.release(conn)

    def get_categories(self) -> list:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM categories ORDER BY name")
            return cur.fetchall()
        finally:
            cur.close()
            db.release(conn)

    def delete(self, student_id: int):
        """Elimina estudiante, usuario y persona asociada."""
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("SELECT id_person FROM students WHERE id = %s", (student_id,))
            row = cur.fetchone()

            if not row:
                raise ValueError("Estudiante no encontrado")

            person_id = row[0]

            # Borrar relaciones primero
            cur.execute("DELETE FROM student_memberships WHERE id_student = %s", (student_id,))
            cur.execute("DELETE FROM students_belts_history WHERE id_student = %s", (student_id,))
            cur.execute("DELETE FROM students_belts WHERE id_student = %s", (student_id,))

            # Borrar usuario y roles
            cur.execute("DELETE FROM users WHERE id_person = %s", (person_id,))
            cur.execute("DELETE FROM person_roles WHERE id_person = %s", (person_id,))

            # Borrar estudiante y persona
            cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
            cur.execute("DELETE FROM people WHERE id = %s", (person_id,))

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cur.close()
            db.release(conn)

    def get_detail(self, student_id: int) -> dict:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    s.id,
                    p.first_name || ' ' || p.last_name     AS nombre,
                    COALESCE(td.type_document, '—')         AS tipo_doc,
                    COALESCE(s.document, '—')               AS documento,
                    COALESCE(p.phone, '—')                  AS telefono,
                    COALESCE(p.email, '—')                  AS email,
                    COALESCE(p.birthdate::text, '—')        AS nacimiento,
                    COALESCE(st.status, '—')                AS estado,
                    p.created_at::date                      AS fecha_ingreso,
                    COALESCE(mp.name, 'Sin membresía')      AS membresia,
                    COALESCE(sm.status, '—')                AS estado_mem,
                    COALESCE(sm.start_date::text, '—')      AS inicio_mem,
                    COALESCE(sm.end_date::text, '—')        AS fin_mem,
                    COALESCE(
                        sm.custom_fee::text,
                        mp.monthly_fee::text,
                        '—'
                    )                                       AS cuota,
                    COALESCE(b.name, 'Sin cinturón')        AS cinturon,
                    COALESCE(ma.name, '—')                  AS arte_marcial,
                    COALESCE(cat.name, 'Sin categoría')     AS categoria
                FROM students s
                JOIN people p              ON p.id  = s.id_person
                LEFT JOIN type_document td ON td.id = s.id_type_document
                LEFT JOIN status st        ON st.id = s.id_status
                LEFT JOIN categories cat   ON cat.id = s.category_id
                LEFT JOIN student_memberships sm
                       ON sm.id_student = s.id AND sm.status = 'activo'
                LEFT JOIN membership_plans mp ON mp.id = sm.id_membership_plan
                LEFT JOIN students_belts bs ON bs.id_student = s.id
                LEFT JOIN belts b           ON b.id = bs.id_belt
                LEFT JOIN martial_arts ma     ON ma.id = b.id_martial_art
                WHERE s.id = %s
                LIMIT 1
            """, (student_id,))
            row = cur.fetchone()
            if not row:
                return {}
            keys = [
                "id", "nombre", "tipo_doc", "documento", "telefono",
                "email", "nacimiento", "estado", "fecha_ingreso",
                "membresia", "estado_mem", "inicio_mem", "fin_mem",
                "cuota", "cinturon", "arte_marcial", "categoria"
            ]
            return dict(zip(keys, row))
        finally:
            cur.close()
            db.release(conn)

    def get_belt_history(self, student_id: int) -> list:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    b.name      AS cinturon,
                    ma.name     AS arte_marcial,
                    sbh.action,
                    sbh.date_changed
                FROM students_belts_history sbh
                JOIN belts b         ON b.id  = sbh.id_belt
                JOIN martial_arts ma ON ma.id = b.id_martial_art
                WHERE sbh.id_student = %s
                ORDER BY sbh.date_changed DESC
            """, (student_id,))
            return cur.fetchall()
        finally:
            cur.close()
            db.release(conn)

    def get_last_classes(self, student_id: int) -> list:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    c.date,
                    COALESCE(sc.name, 'Sin nombre') AS clase,
                    COALESCE(ma.name, '—')           AS arte_marcial
                FROM attendance a
                JOIN classes c       ON c.id  = a.id_class
                LEFT JOIN schedule sc     ON sc.id = c.id_schedule
                LEFT JOIN martial_arts ma ON ma.id = sc.id_martial_art
                WHERE a.id_student = %s
                ORDER BY c.date DESC
                LIMIT 5
            """, (student_id,))
            return cur.fetchall()
        finally:
            cur.close()
            db.release(conn)

    def update_photo(self, student_id: int, photo_path: str):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE people SET photo_path = %s
                WHERE id = (SELECT id_person FROM students WHERE id = %s)
            """, (photo_path, student_id))
            conn.commit()
        finally:
            cur.close()
            db.release(conn)

    def get_photo(self, student_id: int) -> str | None:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT p.photo_path
                FROM students s
                JOIN people p ON p.id = s.id_person
                WHERE s.id = %s
            """, (student_id,))
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            cur.close()
            db.release(conn)