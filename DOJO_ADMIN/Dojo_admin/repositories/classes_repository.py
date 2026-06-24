# ─── CLASSES_REPOSITORY ─────────────────────────────────────────────

from datetime import timedelta
from database.connection import db


class ClassesRepository:
    """
    Repository para:
    - schedule: plantillas recurrentes de clase
    - classes: instancias reales de clase por fecha
    """

    # ─────────────────────────────────────────────────────────────
    # Plantillas semanales para vista semanal
    # Contrato usado por WeeklyCalendarWidget:
    # 0 id
    # 1 name
    # 2 day_of_week
    # 3 start_time
    # 4 end_time
    # 5 capacity
    # 6 location
    # 7 status
    # 8 repeat_type
    # 9 instructor
    # 10 martial_art
    # 11 color
    # 12 id_instructor
    # 13 id_martial_art
    # ─────────────────────────────────────────────────────────────
    def get_week_schedules(self, filters=None):
        filters = filters or {}

        conn = db.get_conn()
        try:
            cur = conn.cursor()

            query = """
                SELECT
                    s.id,
                    s.name,
                    s.day_of_week,
                    s.start_time,
                    s.end_time,
                    s.capacity,
                    s.location,
                    COALESCE(s.status, 'active') AS status,
                    COALESCE(s.repeat_type, 'weekly') AS repeat_type,
                    COALESCE(p.first_name || ' ' || p.last_name, 'Sin instructor') AS instructor,
                    COALESCE(ma.name, 'Sin arte') AS martial_art,
                    COALESCE(s.color, '#3B82F6') AS color,
                    s.id_instructor,
                    s.id_martial_art
                FROM schedule s
                LEFT JOIN instructors i ON i.id = s.id_instructor
                LEFT JOIN people p ON p.id = i.id_person
                LEFT JOIN martial_arts ma ON ma.id = s.id_martial_art
            """

            conditions = []
            params = []

            instructor_id = filters.get("id_instructor")
            if instructor_id is not None:
                conditions.append("s.id_instructor = %s")
                params.append(instructor_id)

            martial_art_id = filters.get("id_martial_art")
            if martial_art_id is not None:
                conditions.append("s.id_martial_art = %s")
                params.append(martial_art_id)

            day_of_week = filters.get("day_of_week")
            if day_of_week is not None:
                conditions.append("s.day_of_week = %s")
                params.append(day_of_week)

            status = filters.get("status")
            if status:
                conditions.append("LOWER(COALESCE(s.status, 'active')) = LOWER(%s)")
                params.append(status)

            # Solo plantillas activas por defecto, a menos que el filtro mande otra cosa
            if not status:
                conditions.append("LOWER(COALESCE(s.status, 'active')) = 'active'")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += """
                ORDER BY
                    s.day_of_week NULLS LAST,
                    s.start_time NULLS LAST,
                    s.name;
            """

            cur.execute(query, params)
            return cur.fetchall()

        finally:
            cur.close()
            db.release(conn)

    # ─────────────────────────────────────────────────────────────
    # Tabla/listado opcional de plantillas
    # ─────────────────────────────────────────────────────────────
    def get_all(self, search="", filters=None):
        filters = filters or {}

        conn = db.get_conn()
        try:
            cur = conn.cursor()

            query = """
                SELECT
                    s.id,
                    s.name,
                    s.day_of_week,
                    s.start_time,
                    s.end_time,
                    s.capacity,
                    s.location,
                    COALESCE(s.status, 'active') AS status,
                    COALESCE(s.repeat_type, 'weekly') AS repeat_type,
                    COALESCE(p.first_name || ' ' || p.last_name, 'Sin instructor') AS instructor,
                    COALESCE(ma.name, 'Sin arte') AS martial_art,
                    COALESCE(s.color, '#3B82F6') AS color,
                    s.id_instructor,
                    s.id_martial_art
                FROM schedule s
                LEFT JOIN instructors i ON i.id = s.id_instructor
                LEFT JOIN people p ON p.id = i.id_person
                LEFT JOIN martial_arts ma ON ma.id = s.id_martial_art
            """

            conditions = []
            params = []

            if search:
                term = f"%{search}%"
                conditions.append("""
                    (
                        LOWER(COALESCE(s.name, '')) LIKE LOWER(%s)
                        OR LOWER(COALESCE(p.first_name || ' ' || p.last_name, '')) LIKE LOWER(%s)
                        OR LOWER(COALESCE(ma.name, '')) LIKE LOWER(%s)
                        OR LOWER(COALESCE(s.location, '')) LIKE LOWER(%s)
                    )
                """)
                params.extend([term, term, term, term])

            if filters.get("day_of_week") is not None:
                conditions.append("s.day_of_week = %s")
                params.append(filters["day_of_week"])

            if filters.get("id_instructor") is not None:
                conditions.append("s.id_instructor = %s")
                params.append(filters["id_instructor"])

            if filters.get("id_martial_art") is not None:
                conditions.append("s.id_martial_art = %s")
                params.append(filters["id_martial_art"])

            if filters.get("status"):
                conditions.append("LOWER(COALESCE(s.status, 'active')) = LOWER(%s)")
                params.append(filters["status"])

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += """
                ORDER BY
                    s.day_of_week NULLS LAST,
                    s.start_time NULLS LAST,
                    s.name;
            """

            cur.execute(query, params)
            return cur.fetchall()

        finally:
            cur.close()
            db.release(conn)

    # ─────────────────────────────────────────────────────────────
    # Obtener plantilla por ID
    # ─────────────────────────────────────────────────────────────
    def get_by_id(self, schedule_id: int):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    id,
                    name,
                    id_martial_art,
                    id_instructor,
                    day_of_week,
                    start_time,
                    end_time,
                    capacity,
                    location,
                    color,
                    status,
                    repeat_type
                FROM schedule
                WHERE id = %s;
            """, (schedule_id,))

            row = cur.fetchone()
            if not row:
                return None

            return {
                "id": row[0],
                "name": row[1],
                "id_martial_art": row[2],
                "id_instructor": row[3],
                "day_of_week": row[4],
                "start_time": row[5],
                "end_time": row[6],
                "capacity": row[7],
                "location": row[8],
                "color": row[9],
                "status": row[10],
                "repeat_type": row[11],
            }

        finally:
            cur.close()
            db.release(conn)

    # ─────────────────────────────────────────────────────────────
    # Crear plantilla
    # ─────────────────────────────────────────────────────────────
    def create_schedule(self, data: dict):
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO schedule (
                    name,
                    id_martial_art,
                    id_instructor,
                    day_of_week,
                    start_time,
                    end_time,
                    capacity,
                    location,
                    color,
                    status,
                    repeat_type
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                data.get("name"),
                data.get("id_martial_art"),
                data.get("id_instructor"),
                data.get("day_of_week"),
                data.get("start_time"),
                data.get("end_time"),
                data.get("capacity"),
                data.get("location"),
                data.get("color") or "#3B82F6",
                data.get("status") or "active",
                data.get("repeat_type") or "weekly",
            ))

            new_id = cur.fetchone()[0]
            conn.commit()
            return new_id

        except Exception:
            conn.rollback()
            raise

        finally:
            cur.close()
            db.release(conn)

    # ─────────────────────────────────────────────────────────────
    # Actualizar plantilla
    # ─────────────────────────────────────────────────────────────
    def update_schedule(self, schedule_id: int, data: dict):
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                UPDATE schedule
                SET
                    name = %s,
                    id_martial_art = %s,
                    id_instructor = %s,
                    day_of_week = %s,
                    start_time = %s,
                    end_time = %s,
                    capacity = %s,
                    location = %s,
                    color = %s,
                    status = %s,
                    repeat_type = %s
                WHERE id = %s;
            """, (
                data.get("name"),
                data.get("id_martial_art"),
                data.get("id_instructor"),
                data.get("day_of_week"),
                data.get("start_time"),
                data.get("end_time"),
                data.get("capacity"),
                data.get("location"),
                data.get("color") or "#3B82F6",
                data.get("status") or "active",
                data.get("repeat_type") or "weekly",
                schedule_id,
            ))

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cur.close()
            db.release(conn)

    # ─────────────────────────────────────────────────────────────
    # Eliminar plantilla y sus clases reales/asistencias
    # ─────────────────────────────────────────────────────────────
    def delete_schedule(self, schedule_id: int):
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                DELETE FROM attendance
                WHERE id_class IN (
                    SELECT id FROM classes WHERE id_schedule = %s
                );
            """, (schedule_id,))

            cur.execute("DELETE FROM classes WHERE id_schedule = %s;", (schedule_id,))
            cur.execute("DELETE FROM schedule WHERE id = %s;", (schedule_id,))

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cur.close()
            db.release(conn)

    # ─────────────────────────────────────────────────────────────
    # Instancias reales por semana
    # ─────────────────────────────────────────────────────────────
    def get_week_classes(self, start_date):
        end_date = start_date + timedelta(days=6)

        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    c.id,
                    c.date,
                    COALESCE(c.status, 'scheduled') AS class_status,
                    c.note,
                    s.id AS schedule_id,
                    s.name,
                    s.day_of_week,
                    s.start_time,
                    s.end_time,
                    COALESCE(s.color, '#3B82F6') AS color,
                    COALESCE(ma.name, 'Sin arte') AS martial_art,
                    COALESCE(p.first_name || ' ' || p.last_name, 'Sin instructor') AS instructor,
                    s.capacity,
                    s.location
                FROM classes c
                JOIN schedule s ON s.id = c.id_schedule
                LEFT JOIN martial_arts ma ON ma.id = s.id_martial_art
                LEFT JOIN instructors i ON i.id = COALESCE(c.id_instructor, s.id_instructor)
                LEFT JOIN people p ON p.id = i.id_person
                WHERE c.date BETWEEN %s AND %s
                ORDER BY c.date, s.start_time;
            """, (start_date, end_date))

            return cur.fetchall()

        finally:
            cur.close()
            db.release(conn)

    def create_class(self, id_schedule: int, class_date, id_instructor=None):
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO classes (
                    id_schedule,
                    id_instructor,
                    date,
                    status
                )
                VALUES (%s, %s, %s, 'scheduled')
                RETURNING id;
            """, (id_schedule, id_instructor, class_date))

            new_id = cur.fetchone()[0]
            conn.commit()
            return new_id

        except Exception:
            conn.rollback()
            raise

        finally:
            cur.close()
            db.release(conn)

    def update_class(self, class_id: int, status: str, note: str = None):
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                UPDATE classes
                SET status = %s,
                    note = %s
                WHERE id = %s;
            """, (status, note, class_id))

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cur.close()
            db.release(conn)

    def delete_class(self, class_id: int):
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("DELETE FROM attendance WHERE id_class = %s;", (class_id,))
            cur.execute("DELETE FROM classes WHERE id = %s;", (class_id,))

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cur.close()
            db.release(conn)

    # ─────────────────────────────────────────────────────────────
    # Opciones para formularios/filtros
    # ─────────────────────────────────────────────────────────────
    def get_filter_options(self):
        return self.get_form_options()

    def get_form_options(self):
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    i.id,
                    COALESCE(p.first_name || ' ' || p.last_name, 'Sin nombre') AS name
                FROM instructors i
                JOIN people p ON p.id = i.id_person
                ORDER BY p.first_name, p.last_name;
            """)
            instructors = cur.fetchall()

            cur.execute("""
                SELECT id, name
                FROM martial_arts
                ORDER BY name;
            """)
            martial_arts = cur.fetchall()

            return {
                "instructors": instructors,
                "martial_arts": martial_arts,
            }

        finally:
            cur.close()
            db.release(conn)

    # ─────────────────────────────────────────────────────────────
    # Obtener o crear instancia real de clase para asistencia
    # schedule = plantilla semanal
    # classes = clase real en una fecha concreta
    # ─────────────────────────────────────────────────────────────
    def get_or_create_class_instance(self, schedule_id: int, class_date, id_instructor=None):
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                SELECT id
                FROM classes
                WHERE id_schedule = %s
                  AND date = %s
                LIMIT 1;
            """, (schedule_id, class_date))

            row = cur.fetchone()

            if row:
                return row[0]

            cur.execute("""
                INSERT INTO classes (
                    id_schedule,
                    id_instructor,
                    date,
                    status
                )
                VALUES (%s, %s, %s, 'scheduled')
                RETURNING id;
            """, (
                schedule_id,
                id_instructor,
                class_date,
            ))

            class_id = cur.fetchone()[0]
            conn.commit()
            return class_id

        except Exception:
            conn.rollback()
            raise

        finally:
            cur.close()
            db.release(conn)

    # ─────────────────────────────────────────────────────────────
    # Estudiantes activos para marcar asistencia
    # Retorna:
    # 0 id_student
    # 1 nombre completo
    # 2 documento
    # ─────────────────────────────────────────────────────────────
    def get_active_students_for_attendance(self):
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    s.id,
                    COALESCE(p.first_name || ' ' || p.last_name, 'Sin nombre') AS full_name,
                    COALESCE(s.document, '') AS document
                FROM students s
                JOIN people p ON p.id = s.id_person
                LEFT JOIN status st ON st.id = s.id_status
                WHERE LOWER(COALESCE(st.status, 'active')) = 'active'
                ORDER BY p.first_name, p.last_name;
            """)

            return cur.fetchall()

        finally:
            cur.close()
            db.release(conn)

    # ─────────────────────────────────────────────────────────────
    # Obtener asistencia actual de una clase real
    # ─────────────────────────────────────────────────────────────
    def get_attendance_student_ids(self, class_id: int):
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                SELECT id_student
                FROM attendance
                WHERE id_class = %s;
            """, (class_id,))

            return {row[0] for row in cur.fetchall()}

        finally:
            cur.close()
            db.release(conn)

    # ─────────────────────────────────────────────────────────────
    # Guardar asistencia
    # Estrategia simple:
    # borrar asistencia previa de esa clase y volver a insertar presentes
    # ─────────────────────────────────────────────────────────────
    def save_attendance(self, class_id: int, present_student_ids):
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                DELETE FROM attendance
                WHERE id_class = %s;
            """, (class_id,))

            for student_id in present_student_ids:
                cur.execute("""
                    INSERT INTO attendance (
                        id_class,
                        id_student
                    )
                    VALUES (%s, %s)
                    ON CONFLICT (id_class, id_student) DO NOTHING;
                """, (
                    class_id,
                    student_id,
                ))

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cur.close()
            db.release(conn)