from database.connection import db


class StudentRepository:

    def get_all(self, search: str = "") -> list:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            query = """
                SELECT
                    s.id,
                    p.first_name || ' ' || p.last_name   AS nombre,
                    td.type_document || ': ' || s.document AS documento,
                    p.phone,
                    p.email,
                    COALESCE(st.status, 'Sin estado')     AS estado,
                    COALESCE(ma.name,  'Sin arte')        AS arte_marcial,
                    p.created_at::date                    AS fecha_ingreso,
                    s.id_person,
                    p.first_name,
                    p.last_name,
                    p.birthdate,
                    s.document                            AS doc_numero,
                    s.id_type_document,
                    s.id_status,
                    s.category_id
                FROM students s
                JOIN people p         ON p.id  = s.id_person
                LEFT JOIN type_document td ON td.id = s.id_type_document
                LEFT JOIN status st        ON st.id = s.id_status
                LEFT JOIN student_memberships sm
                       ON sm.id_student = s.id
                      AND sm.status = 'activo'
                LEFT JOIN membership_plans mp ON mp.id = sm.id_membership_plan
                LEFT JOIN type_products tp    ON tp.id = mp.id_type_product
                LEFT JOIN martial_arts ma     ON ma.name = tp.name
            """
            params = []
            if search:
                query += """
                    WHERE
                        LOWER(p.first_name || ' ' || p.last_name) LIKE %s
                        OR LOWER(s.document) LIKE %s
                        OR LOWER(p.email)    LIKE %s
                        OR LOWER(p.phone)    LIKE %s
                """
                like = f"%{search.lower()}%"
                params = [like, like, like, like]

            query += " ORDER BY p.first_name, p.last_name"
            cur.execute(query, params)
            return cur.fetchall()
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
                    s.id_status, s.category_id, s.id_person
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
                "id_person": row[10],
            }
        finally:
            cur.close()
            db.release(conn)

    def create(self, data: dict) -> int:
        """Crea person + student en una transacción. Retorna el id del estudiante."""
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            # 1. Insertar en people
            cur.execute("""
                INSERT INTO people (first_name, last_name, phone, email, birthdate)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data["first_name"], data["last_name"],
                data.get("phone"), data.get("email"),
                data.get("birthdate"),
            ))
            person_id = cur.fetchone()[0]

            # 2. Insertar en students
            cur.execute("""
                INSERT INTO students (id_person, id_type_document, document, id_status, category_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                person_id,
                data.get("id_type_document"),
                data.get("document"),
                data.get("id_status"),
                data.get("category_id"),
            ))
            student_id = cur.fetchone()[0]
            conn.commit()
            return student_id
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
                    id_status = %s, category_id = %s
                WHERE id = %s
            """, (
                data.get("id_type_document"),
                data.get("document"),
                data.get("id_status"),
                data.get("category_id"),
                student_id,
            ))
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

    def delete(self, student_id: int):
        """Elimina estudiante y su persona asociada."""
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            # Obtener id_person antes de borrar
            cur.execute("SELECT id_person FROM students WHERE id = %s", (student_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError("Estudiante no encontrado")
            person_id = row[0]

            # Borrar en orden por FK: membresías → cinturones → estudiante → persona
            cur.execute("DELETE FROM student_memberships WHERE id_student = %s", (student_id,))
            cur.execute("DELETE FROM belts_students WHERE students_id = %s", (student_id,))
            cur.execute("DELETE FROM students_belts_history WHERE id_student = %s", (student_id,))
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
        """Retorna detalle completo: membresía activa + cinturón actual."""
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
                    -- Membresía activa
                    COALESCE(mp.name, 'Sin membresía')      AS membresia,
                    COALESCE(sm.status, '—')                AS estado_mem,
                    COALESCE(sm.start_date::text, '—')      AS inicio_mem,
                    COALESCE(sm.end_date::text, '—')        AS fin_mem,
                    COALESCE(
                        sm.custom_fee::text,
                        mp.monthly_fee::text,
                        '—'
                    )                                       AS cuota,
                    -- Cinturón actual (último asignado)
                    COALESCE(b.name, 'Sin cinturón')        AS cinturon,
                    COALESCE(ma.name, '—')                  AS arte_marcial
                FROM students s
                JOIN people p ON p.id = s.id_person
                LEFT JOIN type_document td ON td.id = s.id_type_document
                LEFT JOIN status st        ON st.id = s.id_status
                LEFT JOIN student_memberships sm
                       ON sm.id_student = s.id AND sm.status = 'activo'
                LEFT JOIN membership_plans mp ON mp.id = sm.id_membership_plan
                LEFT JOIN belts_students bs   ON bs.students_id = s.id
                LEFT JOIN belts b             ON b.id = bs.belts_id
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
                "cuota", "cinturon", "arte_marcial"
            ]
            return dict(zip(keys, row))
        finally:
            cur.close()
            db.release(conn)