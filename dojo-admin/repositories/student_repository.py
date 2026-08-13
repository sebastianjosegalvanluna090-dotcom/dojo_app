# ─── STUDENT_REPOSITORY ─────────────────────────────────────────────

from database.connection import db
from core.security import hash_password

class StudentRepository:

    def get_all(self, search: str = "") -> list:
        """
        Retorna todos los estudiantes con todos sus cinturones como lista JSON.
        Cada registro contiene 'belts' con todos los cinturones del estudiante
        más campos planos de compatibilidad (primer cinturón).
        """
        with db.cursor() as cur:
            query = """
                SELECT
                    s.id,
                    p.first_name || ' ' || p.last_name AS nombre,
                    COALESCE(p.phone, '\u2014') AS telefono,
                    COALESCE(p.email, '\u2014') AS email,
                    s.document,
                    COALESCE(td.type_document, 'Doc') AS type_document,
                    COALESCE(c.name, '\u2014') AS category_name,
                    COALESCE(st.status, '\u2014') AS status_name,
                    COALESCE(
                        json_agg(
                            json_build_object(
                                'belt_id', b.id,
                                'belt_name', b.name,
                                'belt_color', b.color,
                                'color', b.color,
                                'pre_color', b.pre_color,
                                'grades', COALESCE(b.grades, 0),
                                'grade_color', COALESCE(b.grade_color, '#FFFFFF'),
                                'martial_art_id', ma.id,
                                'martial_art', ma.name,
                                'ma_name', ma.name,
                                'orden', b.orden
                            )
                            ORDER BY ma.name, b.orden DESC
                        ) FILTER (WHERE b.id IS NOT NULL),
                        '[]'
                    ) AS belts,
                    COALESCE((SELECT sg2.phone FROM student_guardians sg2 WHERE sg2.id_student = s.id AND sg2.is_primary = TRUE LIMIT 1), '') AS guardian_phone,
                    COALESCE((SELECT sg2.email FROM student_guardians sg2 WHERE sg2.id_student = s.id AND sg2.is_primary = TRUE LIMIT 1), '') AS guardian_email,
                    COALESCE((SELECT sg2.full_name FROM student_guardians sg2 WHERE sg2.id_student = s.id AND sg2.is_primary = TRUE LIMIT 1), '') AS guardian_name
                FROM students s
                JOIN people p ON p.id = s.id_person
                LEFT JOIN categories c ON c.id = s.category_id
                LEFT JOIN status st ON st.id = s.id_status
                LEFT JOIN type_document td ON td.id = s.id_type_document
                LEFT JOIN students_belts sb ON sb.id_student = s.id
                LEFT JOIN belts b ON b.id = sb.id_belt
                LEFT JOIN martial_arts ma ON ma.id = b.id_martial_art
            """

            params = []

            if search:
                query += """
                    WHERE
                        LOWER(p.first_name || ' ' || p.last_name) LIKE %s
                        OR LOWER(COALESCE(p.email, '')) LIKE %s
                        OR LOWER(COALESCE(p.phone, '')) LIKE %s
                        OR LOWER(COALESCE(s.document, '')) LIKE %s
                """
                like = f"%{search.lower()}%"
                params.extend([like, like, like, like])

            query += """
                GROUP BY
                    s.id,
                    p.first_name,
                    p.last_name,
                    p.phone,
                    p.email,
                    s.document,
                    c.name,
                    st.status,
                    td.type_document
                ORDER BY p.first_name, p.last_name
            """

            cur.execute(query, params)
            result = []
            for r in cur.fetchall():
                raw_belts = r[8]
                if isinstance(raw_belts, str):
                    import json
                    try:
                        raw_belts = json.loads(raw_belts)
                    except Exception:
                        raw_belts = []
                belts = raw_belts or []
                first_belt = belts[0] if belts else {}
                result.append({
                    "id":             r[0],
                    "nombre":         r[1],
                    "telefono":       r[2],
                    "phone":          r[2],
                    "email":          r[3],
                    "document":       r[4],
                    "documento":      r[4],
                    "type_document":  r[5] or "Doc",
                    "category_name":  r[6],
                    "status_name":    r[7],
                    "status":         r[7],
                    "estado":         r[7],
                    "guardian_phone": r[9]  or "",
                    "guardian_email": r[10] or "",
                    "guardian_name":  r[11] or "",
                    "belts":          belts,
                    "belt_name":      first_belt.get("belt_name",   "Sin cintur\u00f3n"),
                    "belt_color":     first_belt.get("belt_color",  "#999999"),
                    "color":          first_belt.get("color",       "#999999"),
                    "pre_color":      first_belt.get("pre_color"),
                    "grades":         first_belt.get("grades",      0),
                    "grade_color":    first_belt.get("grade_color", "#FFFFFF"),
                    "orden":          first_belt.get("orden",       0),
                    "martial_art":    first_belt.get("martial_art", "Sin arte"),
                    "ma_name":        first_belt.get("ma_name",     "Sin arte"),
                    "arte_marcial":   first_belt.get("martial_art", "Sin arte"),
                })
            return result
            
    def get_filter_options(self) -> dict:
        """Carga todas las opciones para los filtros de búsqueda."""
        with db.cursor() as cur:
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

    def get_by_id(self, student_id: int) -> dict | None:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    s.id, p.first_name, p.last_name,
                    p.phone, p.email, p.birthdate,
                    s.document, s.id_type_document,
                    s.id_status, s.category_id, s.id_person,
                    s.joined_date,
                    p.address_line, p.residence_city, p.residence_country,
                    p.birth_city, p.birth_country,
                    p.neighborhood, p.socioeconomic_stratum,
                    s.school_name
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
                "address_line": row[12] or "",
                "residence_city": row[13] or "", "residence_country": row[14] or "",
                "birth_city": row[15] or "", "birth_country": row[16] or "",
                "neighborhood": row[17] or "",
                "socioeconomic_stratum": row[18],
                "school_name": row[19] or "",
            }
    
    def get_student_profile_detail(self, student_id: int) -> dict | None:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    s.id,
                    s.id_person,
                    p.first_name,
                    p.last_name,
                    p.phone,
                    p.email,
                    p.birthdate,
                    p.address_line,
                    p.residence_city,
                    p.residence_country,
                    p.birth_city,
                    p.birth_country,
                    s.joined_date,
                    c.name AS category_name,
                    st.status AS status_name,
                    s.document
                FROM students s
                JOIN people p ON p.id = s.id_person
                LEFT JOIN categories c ON c.id = s.category_id
                LEFT JOIN status st ON st.id = s.id_status
                WHERE s.id = %s
            """, (student_id,))

            row = cur.fetchone()
            if not row:
                return None

            return {
                "id": row[0],
                "id_person": row[1],
                "first_name": row[2],
                "last_name": row[3],
                "phone": row[4],
                "email": row[5],
                "birthdate": row[6],
                "address_line": row[7],
                "residence_city": row[8],
                "residence_country": row[9],
                "birth_city": row[10],
                "birth_country": row[11],
                "joined_date": row[12],
                "category_name": row[13],
                "status_name": row[14],
                "document": row[15],
            }

    def get_primary_guardian(self, student_id: int) -> dict | None:
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, full_name, phone, email, relationship, is_primary,
                       document, profession
                FROM student_guardians
                WHERE id_student = %s
                ORDER BY is_primary DESC, id ASC
                LIMIT 1
            """, (student_id,))

            row = cur.fetchone()
            if not row:
                return None

            return {
                "id": row[0],
                "full_name": row[1],
                "phone": row[2],
                "email": row[3],
                "relationship": row[4],
                "is_primary": row[5],
                "document": row[6] or "",
                "profession": row[7] or "",
            }

    def get_primary_emergency_contact(self, student_id: int) -> dict | None:
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, full_name, phone, email, relationship, note, is_primary
                FROM student_emergency_contacts
                WHERE id_student = %s
                ORDER BY is_primary DESC, id ASC
                LIMIT 1
            """, (student_id,))

            row = cur.fetchone()
            if not row:
                return None

            return {
                "id": row[0],
                "full_name": row[1],
                "phone": row[2],
                "email": row[3],
                "relationship": row[4],
                "note": row[5],
                "is_primary": row[6],
            }

    def save_guardian(self, student_id: int, data: dict) -> int:
        with db.transaction() as cur:
            existing = None
            cur.execute("""
                SELECT id FROM student_guardians
                WHERE id_student = %s AND is_primary = TRUE
            """, (student_id,))
            existing = cur.fetchone()

            if existing:
                cur.execute("""
                    UPDATE student_guardians
                    SET full_name = %s, phone = %s, email = %s,
                        relationship = %s, document = %s, profession = %s
                    WHERE id = %s
                """, (
                    data["full_name"], data["phone"],
                    data.get("email"), data["relationship"],
                    data.get("document"), data.get("profession"),
                    existing[0],
                ))
                return existing[0]
            else:
                cur.execute("""
                    INSERT INTO student_guardians
                        (id_student, full_name, phone, email, relationship,
                         is_primary, document, profession)
                    VALUES (%s, %s, %s, %s, %s, TRUE, %s, %s)
                    RETURNING id
                """, (
                    student_id, data["full_name"], data["phone"],
                    data.get("email"), data["relationship"],
                    data.get("document"), data.get("profession"),
                ))
                return cur.fetchone()[0]

    def delete_guardian(self, student_id: int):
        with db.transaction() as cur:
            cur.execute("""
                DELETE FROM student_guardians WHERE id_student = %s
            """, (student_id,))

    def save_emergency_contact(self, student_id: int, data: dict) -> int:
        with db.transaction() as cur:
            existing = None
            cur.execute("""
                SELECT id FROM student_emergency_contacts
                WHERE id_student = %s AND is_primary = TRUE
            """, (student_id,))
            existing = cur.fetchone()

            if existing:
                cur.execute("""
                    UPDATE student_emergency_contacts
                    SET full_name = %s, phone = %s, email = %s,
                        relationship = %s, note = %s
                    WHERE id = %s
                """, (
                    data["full_name"], data["phone"],
                    data.get("email"), data.get("relationship"),
                    data.get("note"), existing[0],
                ))
                return existing[0]
            else:
                cur.execute("""
                    INSERT INTO student_emergency_contacts
                        (id_student, full_name, phone, email, relationship, note, is_primary)
                    VALUES (%s, %s, %s, %s, %s, %s, TRUE)
                    RETURNING id
                """, (
                    student_id, data["full_name"], data["phone"],
                    data.get("email"), data.get("relationship"),
                    data.get("note"),
                ))
                return cur.fetchone()[0]

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
        with db.cursor() as cur:
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

    def update_student_user_access(self, student_id: int, username: str = None, password: str = None):
        """
        Actualiza usuario y/o contraseña del estudiante.
        Si password viene vacío, no cambia la contraseña.
        """
        with db.transaction() as cur:

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

        Si la categoría es KID, además crea usuario acudent para el acudiente.

        Retorna el id del estudiante.
        """
        with db.transaction() as cur:

            # 1. Insertar en people
            cur.execute("""
                INSERT INTO people (
                    first_name, last_name, phone, email, birthdate,
                    address_line, residence_details, residence_city, residence_country,
                    birth_city, birth_country,
                    neighborhood, socioeconomic_stratum, profession
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data["first_name"],
                data["last_name"],
                data.get("phone"),
                data.get("email"),
                data.get("birthdate"),
                data.get("address_line"),
                data.get("residence_details"),
                data.get("residence_city"),
                data.get("residence_country"),
                data.get("birth_city"),
                data.get("birth_country"),
                data.get("neighborhood"),
                data.get("socioeconomic_stratum"),
                data.get("profession"),
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
                    joined_date,
                    school_name
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                person_id,
                data.get("id_type_document"),
                data.get("document"),
                data.get("id_status"),
                data.get("category_id"),
                data.get("joined_date"),
                data.get("school_name"),
            ))

            student_id = cur.fetchone()[0]

            # 3. Buscar rol estudiante
            student_role_id = self._get_student_role_id(cur)

            # 4. Generar username
            username = self._generate_student_username(cur, data)

            # 5. Password temporal
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

            result = {
                "student_id": student_id,
                "user_id": user_id,
                "username": username,
                "password": temp_password,
                "acudent_credentials": None,
            }

            # 8. Guardar guardian si aplica (KID / YOUTH)
            guardian_data = data.get("guardian")
            if guardian_data:
                self._upsert_guardian(cur, student_id, guardian_data)

            # 9. Guardar contacto de emergencia si NO es KID/YOUTH
            emergency_data = data.get("emergency_contact")
            if emergency_data:
                self._upsert_emergency_contact(cur, student_id, emergency_data)

            # 10. Guardar salud
            health_data = data.get("health")
            if health_data:
                self._upsert_health_info(cur, student_id, health_data)

            # 11. Determinar categoría para lógica KID
            category_id = data.get("category_id")
            cat_name = ""
            if category_id:
                cur.execute("SELECT name FROM categories WHERE id = %s", (category_id,))
                cat_row = cur.fetchone()
                if cat_row:
                    cat_name = cat_row[0]

            # 12. KID: crear usuario acudent
            if cat_name.upper() == "KID" and guardian_data:
                acudent = self._create_acudent_user_for_kid(cur, guardian_data)
                if acudent:
                    result["acudent_credentials"] = acudent

            return result

    def _upsert_guardian(self, cur, student_id: int, data: dict):
        cur.execute("""
            SELECT id FROM student_guardians
            WHERE id_student = %s AND is_primary = TRUE
        """, (student_id,))
        existing = cur.fetchone()
        if existing:
            cur.execute("""
                UPDATE student_guardians
                SET full_name = %s, phone = %s, email = %s,
                    relationship = %s, document = %s, profession = %s
                WHERE id = %s
            """, (
                data["full_name"], data["phone"],
                data.get("email"), data.get("relationship"),
                data.get("document"), data.get("profession"),
                existing[0],
            ))
        else:
            cur.execute("""
                INSERT INTO student_guardians
                    (id_student, full_name, phone, email, relationship,
                     is_primary, document, profession)
                VALUES (%s, %s, %s, %s, %s, TRUE, %s, %s)
                RETURNING id
            """, (
                student_id, data["full_name"], data["phone"],
                data.get("email"), data.get("relationship"),
                data.get("document"), data.get("profession"),
            ))

    def _upsert_emergency_contact(self, cur, student_id: int, data: dict):
        cur.execute("""
            SELECT id FROM student_emergency_contacts
            WHERE id_student = %s AND is_primary = TRUE
        """, (student_id,))
        existing = cur.fetchone()
        if existing:
            cur.execute("""
                UPDATE student_emergency_contacts
                SET full_name = %s, phone = %s, email = %s,
                    relationship = %s, note = %s
                WHERE id = %s
            """, (
                data["full_name"], data["phone"],
                data.get("email"), data.get("relationship"),
                data.get("note"), existing[0],
            ))
        else:
            cur.execute("""
                INSERT INTO student_emergency_contacts
                    (id_student, full_name, phone, email, relationship, note, is_primary)
                VALUES (%s, %s, %s, %s, %s, %s, TRUE)
                RETURNING id
            """, (
                student_id, data["full_name"], data["phone"],
                data.get("email"), data.get("relationship"),
                data.get("note"),
            ))

    def _upsert_health_info(self, cur, student_id: int, data: dict):
        cur.execute("""
            INSERT INTO student_health_info
                (id_student, eps, ips, blood_type,
                 allergies, medical_conditions, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id_student)
            DO UPDATE SET
                eps = EXCLUDED.eps,
                ips = EXCLUDED.ips,
                blood_type = EXCLUDED.blood_type,
                allergies = EXCLUDED.allergies,
                medical_conditions = EXCLUDED.medical_conditions,
                notes = EXCLUDED.notes,
                updated_at = CURRENT_TIMESTAMP
        """, (
            student_id,
            data.get("eps", ""),
            data.get("ips", ""),
            data.get("blood_type", ""),
            data.get("allergies", ""),
            data.get("medical_conditions", ""),
            data.get("notes", ""),
        ))

    def update(self, student_id: int, data: dict):
        with db.transaction() as cur:
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
                    phone = %s, email = %s, birthdate = %s,
                    address_line = %s, residence_details = %s, residence_city = %s, residence_country = %s,
                    birth_city = %s, birth_country = %s,
                    neighborhood = %s, socioeconomic_stratum = %s, profession = %s
                WHERE id = %s
            """, (
                data["first_name"], data["last_name"],
                data.get("phone"), data.get("email"),
                data.get("birthdate"),
                data.get("address_line"), data.get("residence_details"), data.get("residence_city"),
                data.get("residence_country"), data.get("birth_city"),
                data.get("birth_country"),
                data.get("neighborhood"), data.get("socioeconomic_stratum"), data.get("profession"),
                person_id,
            ))

            # Actualizar students
            cur.execute("""
                UPDATE students
                SET id_type_document = %s, document = %s,
                    id_status = %s, category_id = %s,
                    joined_date = %s, school_name = %s
                WHERE id = %s
            """, (
                data.get("id_type_document"),
                data.get("document"),
                data.get("id_status"),
                data.get("category_id"),
                data.get("joined_date"),
                data.get("school_name"),
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

    def get_type_documents(self) -> list:
        with db.cursor() as cur:
            cur.execute("SELECT id, type_document FROM type_document ORDER BY type_document")
            return cur.fetchall()

    def get_statuses(self) -> list:
        with db.cursor() as cur:
            cur.execute("SELECT id, status FROM status ORDER BY status")
            return cur.fetchall()

    def get_categories(self) -> list:
        with db.cursor() as cur:
            cur.execute("SELECT id, name FROM categories ORDER BY name")
            return cur.fetchall()

    def get_form_lookups(self) -> dict:
        countries_cities = {
            "Colombia": ["Barranquilla", "Bogotá", "Medellín", "Cali", "Cartagena", "Santa Marta", "Bucaramanga"],
            "Venezuela": ["Caracas", "Maracaibo", "Valencia", "Barquisimeto"],
            "Estados Unidos": ["Miami", "New York", "Orlando", "Los Ángeles"],
            "Argentina": ["Buenos Aires", "Córdoba", "Rosario"],
            "Chile": ["Santiago", "Valparaíso", "Concepción"],
            "Perú": ["Lima", "Arequipa", "Cusco"],
            "Ecuador": ["Quito", "Guayaquil", "Cuenca"],
            "México": ["Ciudad de México", "Guadalajara", "Monterrey"],
            "España": ["Madrid", "Barcelona", "Valencia"],
            "Brasil": ["São Paulo", "Río de Janeiro", "Brasilia"],
        }
        with db.cursor() as cur:
            cur.execute("SELECT id, name FROM categories ORDER BY name")
            categories = cur.fetchall()
            cur.execute("SELECT id, type_document FROM type_document ORDER BY type_document")
            doc_types = cur.fetchall()
            cur.execute("SELECT id, status FROM status ORDER BY status")
            statuses = cur.fetchall()
            cur.execute("SELECT id, name FROM roles ORDER BY name")
            roles = cur.fetchall()
        return {
            "categories": categories,
            "document_types": doc_types,
            "statuses": statuses,
            "roles": roles,
            "countries_cities": countries_cities,
        }

    def get_health_info(self, student_id: int) -> dict | None:
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, eps, ips, blood_type,
                       allergies, medical_conditions, notes
                FROM student_health_info
                WHERE id_student = %s
            """, (student_id,))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "eps": row[1] or "",
                "ips": row[2] or "",
                "blood_type": row[3] or "",
                "allergies": row[4] or "",
                "medical_conditions": row[5] or "",
                "notes": row[6] or "",
            }

    def get_student_documents(self, student_id: int):
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, doc_type, file_path, uploaded_at
                FROM student_documents
                WHERE id_student = %s
                ORDER BY uploaded_at DESC
            """, (student_id,))
            return [
                {
                    "id": r[0],
                    "doc_type": r[1],
                    "file_path": r[2],
                }
                for r in cur.fetchall()
            ]

    def delete(self, student_id: int):
        """Elimina estudiante, usuario y persona asociada."""
        with db.transaction() as cur:

            cur.execute("SELECT id_person FROM students WHERE id = %s", (student_id,))
            row = cur.fetchone()

            if not row:
                raise ValueError("Estudiante no encontrado")

            person_id = row[0]

            # Borrar relaciones primero
            cur.execute("DELETE FROM student_guardians WHERE id_student = %s", (student_id,))
            cur.execute("DELETE FROM student_emergency_contacts WHERE id_student = %s", (student_id,))
            cur.execute("DELETE FROM student_health_info WHERE id_student = %s", (student_id,))
            cur.execute("DELETE FROM student_documents WHERE id_student = %s", (student_id,))
            cur.execute("DELETE FROM student_memberships WHERE id_student = %s", (student_id,))
            cur.execute("DELETE FROM students_belts_history WHERE id_student = %s", (student_id,))
            cur.execute("DELETE FROM students_belts WHERE id_student = %s", (student_id,))

            # Borrar usuario y roles
            cur.execute("DELETE FROM users WHERE id_person = %s", (person_id,))
            cur.execute("DELETE FROM person_roles WHERE id_person = %s", (person_id,))

            # Borrar estudiante y persona
            cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
            cur.execute("DELETE FROM people WHERE id = %s", (person_id,))

    def get_detail(self, student_id: int) -> dict:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    s.id,
                    p.first_name || ' ' || p.last_name     AS nombre,
                    COALESCE(td.type_document, '\u2014')         AS tipo_doc,
                    COALESCE(s.document, '\u2014')               AS documento,
                    COALESCE(p.phone, '\u2014')                  AS telefono,
                    COALESCE(p.email, '\u2014')                  AS email,
                    COALESCE(p.birthdate::text, '\u2014')        AS nacimiento,
                    COALESCE(st.status, '\u2014')                AS estado,
                    p.created_at::date                      AS fecha_ingreso,
                    COALESCE(mp.name, 'Sin membres\u00eda')      AS membresia,
                    COALESCE(sm.status, '\u2014')                AS estado_mem,
                    COALESCE(sm.start_date::text, '\u2014')      AS inicio_mem,
                    COALESCE(sm.end_date::text, '\u2014')        AS fin_mem,
                    COALESCE(
                        sm.custom_fee::text,
                        mp.monthly_fee::text,
                        '\u2014'
                    )                                       AS cuota,
                    COALESCE(b.name, 'Sin cintur\u00f3n')        AS cinturon,
                    COALESCE(ma.name, '\u2014')                  AS arte_marcial,
                    COALESCE(cat.name, 'Sin categor\u00eda')     AS categoria
                FROM students s
                JOIN people p              ON p.id  = s.id_person
                LEFT JOIN type_document td ON td.id = s.id_type_document
                LEFT JOIN status st ON st.id = s.id_status
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

    def get_recent_classes(self, student_id: int, limit: int = 5) -> list:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    c.date,
                    COALESCE(sc.name, 'Clase') AS class_name,
                    COALESCE(ma.name, '\u2014') AS martial_art,
                    COALESCE(a.status, '\u2014') AS attendance_status,
                    a.check_in_time
                FROM attendance a
                JOIN classes c ON c.id = a.id_class
                LEFT JOIN schedule sc ON sc.id = c.id_schedule
                LEFT JOIN martial_arts ma ON ma.id = sc.id_martial_art
                WHERE a.id_student = %s
                ORDER BY c.date DESC, a.check_in_time DESC
                LIMIT %s
            """, (student_id, limit))

            return [
                {
                    "date": r[0],
                    "class_name": r[1],
                    "martial_art": r[2],
                    "status": r[3],
                    "check_in_time": r[4],
                }
                for r in cur.fetchall()
            ]

    def get_current_belts(self, student_id: int) -> list:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    sb.id,
                    b.id,
                    b.name,
                    b.color,
                    b.pre_color,
                    COALESCE(b.grades, 0),
                    COALESCE(b.grade_color, '#FFFFFF'),
                    ma.id,
                    ma.name,
                    b.orden
                FROM students_belts sb
                JOIN belts b ON b.id = sb.id_belt
                JOIN martial_arts ma ON ma.id = b.id_martial_art
                WHERE sb.id_student = %s
                ORDER BY ma.name, b.orden
            """, (student_id,))

            return [
                {
                    "student_belt_id": r[0],
                    "belt_id": r[1],
                    "belt_name": r[2],
                    "color": r[3],
                    "pre_color": r[4],
                    "grades": r[5],
                    "grade_color": r[6],
                    "martial_art_id": r[7],
                    "martial_art": r[8],
                    "orden": r[9],
                }
                for r in cur.fetchall()
            ]

    def get_belt_history(self, student_id: int, limit: int = 10) -> list:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    sbh.date_changed,
                    sbh.action,
                    b.name AS belt_name,
                    ma.name AS martial_art,
                    b.color,
                    b.pre_color,
                    COALESCE(b.grades, 0),
                    COALESCE(b.grade_color, '#FFFFFF')
                FROM students_belts_history sbh
                JOIN belts b ON b.id = sbh.id_belt
                JOIN martial_arts ma ON ma.id = b.id_martial_art
                WHERE sbh.id_student = %s
                ORDER BY sbh.date_changed DESC
                LIMIT %s
            """, (student_id, limit))

            return [
                {
                    "date_changed": r[0],
                    "action": r[1],
                    "belt_name": r[2],
                    "martial_art": r[3],
                    "color": r[4],
                    "pre_color": r[5],
                    "grades": r[6],
                    "grade_color": r[7],
                }
                for r in cur.fetchall()
            ]

    def get_payment_history(self, student_id: int, limit: int = 8) -> list:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    p.id,
                    p.payment_date,
                    p.total,
                    p.total_paid,
                    COALESCE(pm.name, '\u2014') AS payment_method,
                    COALESCE(p.description, '\u2014') AS description,
                    COALESCE(p.note, '\u2014') AS note
                FROM students s
                JOIN payments p ON p.id_person = s.id_person
                LEFT JOIN payment_method pm ON pm.id = p.id_payment_method
                WHERE s.id = %s
                ORDER BY p.payment_date DESC
                LIMIT %s
            """, (student_id, limit))

            return [
                {
                    "id": r[0],
                    "payment_date": r[1],
                    "total": r[2],
                    "total_paid": r[3],
                    "payment_method": r[4],
                    "description": r[5],
                    "note": r[6],
                }
                for r in cur.fetchall()
            ]

    def save_health_info(self, student_id: int, data: dict):
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO student_health_info
                    (id_student, eps, ips, blood_type,
                     allergies, medical_conditions, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id_student)
                DO UPDATE SET
                    eps = EXCLUDED.eps,
                    ips = EXCLUDED.ips,
                    blood_type = EXCLUDED.blood_type,
                    allergies = EXCLUDED.allergies,
                    medical_conditions = EXCLUDED.medical_conditions,
                    notes = EXCLUDED.notes,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                student_id,
                data.get("eps", ""),
                data.get("ips", ""),
                data.get("blood_type", ""),
                data.get("allergies", ""),
                data.get("medical_conditions", ""),
                data.get("notes", ""),
            ))

    def save_student_document(self, student_id: int, doc_type: str, file_path: str):
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO student_documents
                    (id_student, doc_type, file_path)
                VALUES (%s, %s, %s)
                ON CONFLICT ON CONSTRAINT uq_student_doc_type
                DO UPDATE SET
                    file_path = EXCLUDED.file_path,
                    uploaded_at = CURRENT_TIMESTAMP
            """, (
                student_id, doc_type, file_path,
            ))

    def delete_student_document(self, doc_id: int):
        with db.transaction() as cur:
            cur.execute("""
                DELETE FROM student_documents
                WHERE id = %s
            """, (doc_id,))

    def _get_acudent_role_id(self, cur) -> int:
        cur.execute("""
            SELECT id FROM roles WHERE LOWER(name) = 'acudent'
            LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            raise ValueError("No existe un rol llamado 'acudent' en la tabla roles.")
        return row[0]

    def _create_acudent_user_for_kid(self, cur, guardian_data: dict) -> dict | None:
        guardian_name = (guardian_data.get("full_name") or "").strip()
        guardian_document = (guardian_data.get("document") or "").strip()
        if not guardian_name or not guardian_document:
            return None
        parts = guardian_name.split()
        first_name = parts[0]
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        cur.execute("""
            SELECT id FROM people
            WHERE LOWER(TRIM(CONCAT(COALESCE(first_name,''),' ',COALESCE(last_name,'')))) = LOWER(%s)
               OR phone = %s
               OR email = %s
            LIMIT 1
        """, (guardian_name, guardian_data.get("phone", ""), guardian_data.get("email", "")))
        row = cur.fetchone()
        if row:
            guardian_person_id = row[0]
        else:
            cur.execute("""
                INSERT INTO people (first_name, last_name, phone, email)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (first_name, last_name, guardian_data.get("phone", ""), guardian_data.get("email", "")))
            guardian_person_id = cur.fetchone()[0]
        username = self._build_username_from_document(guardian_document)
        password_hash = hash_password(guardian_document)
        cur.execute("""
            INSERT INTO users (id_person, username, password_hash, is_active)
            VALUES (%s, %s, %s, true)
            ON CONFLICT ON CONSTRAINT users_username_key DO NOTHING
        """, (guardian_person_id, username, password_hash))
        role_id = self._get_acudent_role_id(cur)
        cur.execute("""
            INSERT INTO person_roles (id_person, id_role)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (guardian_person_id, role_id))
        return {
            "username": username,
            "password": guardian_document,
        }

    @staticmethod
    def _build_username_from_document(document: str) -> str:
        base = document.strip().lower().replace(" ", "").replace("-", "")
        if not base:
            base = "acudent"
        return f"ac.{base}"

    def get_student_payment_lookup_name(self, student_id: int) -> tuple:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    p.first_name,
                    p.last_name,
                    c.name AS category_name,
                    sg.full_name AS guardian_name
                FROM students s
                JOIN people p ON p.id = s.id_person
                LEFT JOIN categories c ON c.id = s.category_id
                LEFT JOIN student_guardians sg
                    ON sg.id_student = s.id AND sg.is_primary = TRUE
                WHERE s.id = %s
            """, (student_id,))

            row = cur.fetchone()
            if not row:
                return ("", "student")

            first_name = row[0] or ""
            last_name = row[1] or ""
            category_name = (row[2] or "").upper()
            guardian_name = row[3] or ""

            is_minor = category_name in ("KID", "YOUTH")
            if is_minor and guardian_name:
                return (guardian_name, "guardian")

            student_name = f"{first_name} {last_name}".strip()
            return (student_name, "student")

    def get_last_payments_for_student(self, student_id: int, limit: int = 5) -> list:
        lookup_name, source = self.get_student_payment_lookup_name(student_id)
        if not lookup_name:
            return []

        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    fi.id,
                    fi.income_date,
                    COALESCE(fi.subtotal, 0) AS subtotal,
                    COALESCE(fi.discount, 0) AS discount,
                    COALESCE(fi.total, 0) AS total,
                    COALESCE(fi.total_paid, 0) AS total_paid,
                    COALESCE(fi.pending_amount, 0) AS pending_amount,
                    fi.status,
                    COALESCE(fi.note, '') AS note,
                    COALESCE(
                        json_agg(
                            json_build_object(
                                'name', fii.name,
                                'quantity', fii.quantity,
                                'unit_price', fii.unit_price,
                                'subtotal', fii.subtotal,
                                'item_type', fii.item_type
                            )
                            ORDER BY fii.id
                        ) FILTER (WHERE fii.id IS NOT NULL),
                        '[]'::json
                    ) AS items
                FROM finance_income fi
                LEFT JOIN finance_income_items fii
                    ON fii.income_id = fi.id
                WHERE fi.payer_name = %s
                GROUP BY fi.id
                ORDER BY fi.income_date DESC
                LIMIT %s
            """, (lookup_name, limit))

            results = []
            for r in cur.fetchall():
                results.append({
                    "id": r[0],
                    "income_date": r[1],
                    "subtotal": r[2],
                    "discount": r[3],
                    "total": r[4],
                    "total_paid": r[5],
                    "pending_amount": r[6],
                    "status": r[7],
                    "note": r[8] or "",
                    "items": r[9] if isinstance(r[9], list) else [],
                    "lookup_source": source,
                    "lookup_name": lookup_name,
                })

            if results:
                return results

            cur.execute("""
                SELECT
                    fi.id,
                    fi.income_date,
                    COALESCE(fi.subtotal, 0) AS subtotal,
                    COALESCE(fi.discount, 0) AS discount,
                    COALESCE(fi.total, 0) AS total,
                    COALESCE(fi.total_paid, 0) AS total_paid,
                    COALESCE(fi.pending_amount, 0) AS pending_amount,
                    fi.status,
                    COALESCE(fi.note, '') AS note,
                    COALESCE(
                        json_agg(
                            json_build_object(
                                'name', fii.name,
                                'quantity', fii.quantity,
                                'unit_price', fii.unit_price,
                                'subtotal', fii.subtotal,
                                'item_type', fii.item_type
                            )
                            ORDER BY fii.id
                        ) FILTER (WHERE fii.id IS NOT NULL),
                        '[]'::json
                    ) AS items
                FROM finance_income fi
                LEFT JOIN finance_income_items fii
                    ON fii.income_id = fi.id
                WHERE fi.payer_name LIKE %s
                GROUP BY fi.id
                ORDER BY fi.income_date DESC
                LIMIT %s
            """, (f"%{lookup_name}%", limit))

            return [
                {
                    "id": r[0],
                    "income_date": r[1],
                    "subtotal": r[2],
                    "discount": r[3],
                    "total": r[4],
                    "total_paid": r[5],
                    "pending_amount": r[6],
                    "status": r[7],
                    "note": r[8] or "",
                    "items": r[9] if isinstance(r[9], list) else [],
                    "lookup_source": source,
                    "lookup_name": lookup_name,
                }
                for r in cur.fetchall()
            ]

    def update_photo(self, student_id: int, photo_path: str):
        with db.transaction() as cur:
            cur.execute("""
                UPDATE people SET photo_path = %s
                WHERE id = (SELECT id_person FROM students WHERE id = %s)
            """, (photo_path, student_id))

    def get_health_info(self, student_id: int) -> dict:
        with db.cursor() as cur:
            cur.execute("""
                SELECT eps, ips, blood_type, allergies, medical_conditions, notes
                FROM student_health_info
                WHERE id_student = %s
                LIMIT 1
            """, (student_id,))
            row = cur.fetchone()
            if not row:
                return {}
            return {
                "eps": row[0] or "",
                "ips": row[1] or "",
                "blood_type": row[2] or "",
                "allergies": row[3] or "",
                "medical_conditions": row[4] or "",
                "notes": row[5] or "",
            }

    def get_full_profile(self, student_id: int) -> dict:
        """
        Versión extendida de get_student_profile_detail con
        todos los campos del formulario: barrio, estrato,
        profesión, colegio, detalles de residencia, username.
        """
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    s.id,
                    s.id_person,
                    p.first_name,
                    p.last_name,
                    p.phone,
                    p.email,
                    p.birthdate,
                    p.address_line,
                    p.residence_city,
                    p.residence_country,
                    p.birth_city,
                    p.birth_country,
                    s.joined_date,
                    c.name                              AS category_name,
                    st.status                           AS status_name,
                    s.document,
                    td.type_document,
                    p.neighborhood,
                    p.socioeconomic_stratum,
                    p.profession,
                    p.residence_details,
                    s.school_name,
                    u.username
                FROM students s
                JOIN people p ON p.id = s.id_person
                LEFT JOIN categories c ON c.id = s.category_id
                LEFT JOIN status st ON st.id = s.id_status
                LEFT JOIN type_document td ON td.id = s.id_type_document
                LEFT JOIN users u ON u.id_person = p.id
                WHERE s.id = %s
            """, (student_id,))
            row = cur.fetchone()
            if not row:
                return {}
            return {
                "id": row[0],
                "id_person": row[1],
                "first_name": row[2],
                "last_name": row[3],
                "phone": row[4],
                "email": row[5],
                "birthdate": row[6],
                "address_line": row[7],
                "residence_city": row[8],
                "residence_country": row[9],
                "birth_city": row[10],
                "birth_country": row[11],
                "joined_date": row[12],
                "category_name": row[13],
                "status_name": row[14],
                "document": row[15],
                "type_document": row[16] or "",
                "neighborhood": row[17] or "",
                "socioeconomic_stratum": row[18],
                "school_name": row[22] or "",
                "profession": row[19] or "",
                "residence_details": row[20] or "",
                "username": row[22] or "",
            }

    def get_photo(self, student_id: int) -> str | None:
        with db.cursor() as cur:
            cur.execute("""
                SELECT p.photo_path
                FROM students s
                JOIN people p ON p.id = s.id_person
                WHERE s.id = %s
            """, (student_id,))
            row = cur.fetchone()
            return row[0] if row else None
