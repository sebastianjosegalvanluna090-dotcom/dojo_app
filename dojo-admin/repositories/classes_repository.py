# ─── CLASSES_REPOSITORY ─────────────────────────────────────────────

from datetime import time, timedelta
from database.connection import db


def _to_time(value) -> time | None:
    """Normaliza start_time/end_time a datetime.time.

    Acepta: time, str (HH:mm), None.
    """
    if value is None:
        return None
    if isinstance(value, time):
        return value
    parts = str(value).strip().split(":")
    try:
        return time(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return None


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

        with db.cursor() as cur:
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

    # ─────────────────────────────────────────────────────────────
    # Tabla/listado opcional de plantillas
    # ─────────────────────────────────────────────────────────────
    def get_all(self, search="", filters=None):
        filters = filters or {}

        with db.cursor() as cur:
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

    # ─────────────────────────────────────────────────────────────
    # Obtener plantilla por ID
    # ─────────────────────────────────────────────────────────────
    def get_by_id(self, schedule_id: int):
        with db.cursor() as cur:
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

    # ─────────────────────────────────────────────────────────────
    # Crear plantilla
    # ─────────────────────────────────────────────────────────────
    def create_schedule(self, data: dict):
        with db.transaction() as cur:
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
                _to_time(data.get("start_time")),
                _to_time(data.get("end_time")),
                data.get("capacity"),
                data.get("location"),
                data.get("color") or "#3B82F6",
                data.get("status") or "active",
                data.get("repeat_type") or "weekly",
            ))

            return cur.fetchone()[0]

    # ─────────────────────────────────────────────────────────────
    # Actualizar plantilla
    # ─────────────────────────────────────────────────────────────
    def update_schedule(self, schedule_id: int, data: dict):
        with db.transaction() as cur:
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
                _to_time(data.get("start_time")),
                _to_time(data.get("end_time")),
                data.get("capacity"),
                data.get("location"),
                data.get("color") or "#3B82F6",
                data.get("status") or "active",
                data.get("repeat_type") or "weekly",
                schedule_id,
            ))

    # ─────────────────────────────────────────────────────────────
    # Eliminar plantilla y sus clases reales/asistencias
    # ─────────────────────────────────────────────────────────────
    def delete_schedule(self, schedule_id: int):
        with db.transaction() as cur:
            cur.execute("""
                DELETE FROM attendance
                WHERE id_class IN (
                    SELECT id FROM classes WHERE id_schedule = %s
                );
            """, (schedule_id,))

            cur.execute("DELETE FROM classes WHERE id_schedule = %s;", (schedule_id,))
            cur.execute("DELETE FROM schedule WHERE id = %s;", (schedule_id,))

    # ─────────────────────────────────────────────────────────────
    # Instancias reales por semana
    # ─────────────────────────────────────────────────────────────
    def get_week_classes(self, start_date):
        end_date = start_date + timedelta(days=6)

        with db.cursor() as cur:
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

    def create_class(self, id_schedule: int, class_date, id_instructor=None):
        with db.transaction() as cur:
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

            return cur.fetchone()[0]

    def update_class(self, class_id: int, status: str, note: str = None):
        with db.transaction() as cur:
            cur.execute("""
                UPDATE classes
                SET status = %s,
                    note = %s
                WHERE id = %s;
            """, (status, note, class_id))

    def delete_class(self, class_id: int):
        with db.transaction() as cur:
            cur.execute("DELETE FROM attendance WHERE id_class = %s;", (class_id,))
            cur.execute("DELETE FROM classes WHERE id = %s;", (class_id,))

    # ─────────────────────────────────────────────────────────────
    # Opciones para formularios/filtros
    # ─────────────────────────────────────────────────────────────
    def get_filter_options(self):
        return self.get_form_options()

    def get_form_options(self):
        with db.cursor() as cur:
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

    # ─────────────────────────────────────────────────────────────
    # Obtener o crear instancia real de clase para asistencia
    # schedule = plantilla semanal
    # classes = clase real en una fecha concreta
    # ─────────────────────────────────────────────────────────────
    def get_or_create_class_instance(self, schedule_id: int, class_date, id_instructor=None):
        with db.transaction() as cur:
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

            return cur.fetchone()[0]

    # ─────────────────────────────────────────────────────────────
    # Estudiantes activos para marcar asistencia
    # Retorna:
    # 0 id_student
    # 1 nombre completo
    # 2 documento
    # ─────────────────────────────────────────────────────────────
    def get_active_students_for_attendance(self):
        """
        Retorna todos los estudiantes activos para asistencia.
        No filtra por arte marcial ni por cinturón.
        """
        with db.cursor() as cur:
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
            
    # ─────────────────────────────────────────────────────────────
    # Obtener estudiantes presentes en una clase
    # ─────────────────────────────────────────────────────────────
    def get_attendance_student_ids(self, class_id: int):
        with db.cursor() as cur:
            cur.execute("""
                SELECT id_student
                FROM attendance
                WHERE id_class = %s;
            """, (class_id,))

            return {row[0] for row in cur.fetchall()}

    # ─────────────────────────────────────────────────────────────
    # Obtener asistencia actual de una clase real
    # ─────────────────────────────────────────────────────────────
    def get_class_guest_info(self, class_id: int) -> dict:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    COALESCE(guest_count, 0),
                    COALESCE(guest_names, ''),
                    id_instructor,
                    COALESCE(status, 'scheduled')
                FROM classes
                WHERE id = %s;
            """, (class_id,))

            row = cur.fetchone()

            if not row:
                return {
                    "guest_count": 0,
                    "guest_names": "",
                    "id_instructor": None,
                    "class_status": "scheduled",
                }

            return {
                "guest_count": row[0],
                "guest_names": row[1],
                "id_instructor": row[2],
                "class_status": row[3],
            }

    # ─────────────────────────────────────────────────────────────
    # Verificar rol de usuario
    # ─────────────────────────────────────────────────────────────
    def user_has_role(self, user_id: int | None, role_name: str) -> bool:
        if user_id is None:
            return False

        with db.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM users u
                    JOIN person_roles pr
                        ON pr.id_person = u.id_person
                    JOIN roles r
                        ON r.id = pr.id_role
                    WHERE u.id = %s
                      AND LOWER(TRIM(r.name)) = LOWER(TRIM(%s))
                );
            """, (
                user_id,
                role_name,
            ))

            row = cur.fetchone()
            return bool(row and row[0])

    def is_admin_user(self, user_id: int | None) -> bool:
        return self.user_has_role(user_id, "admin")

    # ─────────────────────────────────────────────────────────────
    # Cupos semanales por estudiante
    # ─────────────────────────────────────────────────────────────
    def get_students_weekly_allowance(
        self,
        student_ids,
        class_date
    ) -> dict:
        """
        Calcula cupos semanales por estudiante.

        Flujo por cada estudiante:
        1. Obtener datos del estudiante (person_id, categoría, nombre).
        2. Si KID/YOUTH → usar nombre del acudiente principal.
        3. Buscar último ingreso de tipo membership en finance_income.
        4. Obtener reference_id → membership_plans.
        5. Contar asistencias de la semana.
        6. Calcular remaining = weekly_classes - used.
        """
        student_ids = list(set(
            int(x)
            for x in student_ids
            if x is not None
        ))

        if not student_ids:
            return {}

        week_start = class_date - timedelta(
            days=class_date.weekday()
        )
        week_end = week_start + timedelta(days=6)

        allowances = {}

        with db.cursor() as cur:

            for student_id in student_ids:

                cur.execute("""
                    SELECT
                        s.id,
                        s.id_person,
                        UPPER(COALESCE(c.name,'')) AS category_name,
                        TRIM(
                            COALESCE(p.first_name,'')
                            || ' ' ||
                            COALESCE(p.last_name,'')
                        ) AS student_name,
                        COALESCE(sg.full_name,'') AS guardian_name
                    FROM students s
                    JOIN people p
                        ON p.id = s.id_person
                    LEFT JOIN categories c
                        ON c.id = s.category_id
                    LEFT JOIN student_guardians sg
                        ON sg.id_student = s.id
                       AND sg.is_primary = TRUE
                    WHERE s.id = %s
                    LIMIT 1
                """, (student_id,))

                info = cur.fetchone()

                if not info:
                    continue

                person_id = info[1]
                category = (info[2] or "").upper()
                student_name = (info[3] or "").strip()
                guardian_name = (info[4] or "").strip()

                if category == "SCHOLARSHIP":
                    allowances[student_id] = {
                        "plan_name": "Scholarship",
                        "weekly_limit": 0,
                        "used_classes": 0,
                        "remaining": None,
                        "is_unlimited": True,
                        "has_membership": True,
                    }
                    continue

                search_name = student_name

                if category in ("KID", "YOUTH") and guardian_name:
                    search_name = guardian_name

                cur.execute("""
                    SELECT
                        fii.reference_id,
                        fii.name,
                        fi.income_date

                    FROM finance_income fi

                    JOIN finance_income_items fii
                        ON fii.income_id = fi.id

                    LEFT JOIN finance_income_participants fip
                        ON fip.income_id = fi.id

                    WHERE LOWER(fii.item_type) = 'membership'

                    AND (
                          fip.person_id = %s
                       OR fi.payer_person_id = %s
                       OR LOWER(fi.payer_name) = LOWER(%s)
                    )

                    AND LOWER(
                        COALESCE(fi.status, '')
                    ) IN (
                        'paid',
                        'partial',
                        'pagado',
                        'parcial'
                    )

                    AND COALESCE(fi.total_paid, 0) > 0

                    AND EXTRACT(MONTH FROM fi.income_date)
                        = EXTRACT(MONTH FROM %s::date)

                    AND EXTRACT(YEAR FROM fi.income_date)
                        = EXTRACT(YEAR FROM %s::date)

                    ORDER BY fi.income_date DESC
                    LIMIT 1
                """, (
                    person_id,
                    person_id,
                    search_name,
                    class_date,
                    class_date,
                ))

                payment = cur.fetchone()

                if not payment:

                    allowances[student_id] = {
                        "plan_name": "Sin mensualidad",
                        "weekly_limit": 0,
                        "used_classes": 0,
                        "remaining": 0,
                        "is_unlimited": False,
                        "has_membership": False,
                    }

                    continue

                plan_id = payment[0]

                cur.execute("""
                    SELECT
                        name,
                        COALESCE(weekly_classes, 0),
                        COALESCE(is_unlimited, false)
                    FROM membership_plans
                    WHERE id = %s
                """, (plan_id,))

                plan = cur.fetchone()

                if not plan:

                    allowances[student_id] = {
                        "plan_name": "Sin mensualidad",
                        "weekly_limit": 0,
                        "used_classes": 0,
                        "remaining": 0,
                        "is_unlimited": False,
                        "has_membership": False,
                    }

                    continue

                plan_name = plan[0]
                weekly_limit = int(plan[1] or 0)
                is_unlimited = bool(plan[2])

                cur.execute("""
                    SELECT COUNT(*)

                    FROM attendance a

                    JOIN classes c
                        ON c.id = a.id_class

                    WHERE a.id_student = %s

                    AND c.date BETWEEN %s AND %s

                    AND LOWER(
                        COALESCE(c.status,'completed')
                    ) NOT IN (
                        'cancelled',
                        'cancelada',
                        'inactive',
                        'inactiva'
                    )
                """, (
                    student_id,
                    week_start,
                    week_end,
                ))

                used_classes = int(
                    cur.fetchone()[0] or 0
                )

                if is_unlimited:
                    remaining = None
                else:
                    remaining = max(
                        0,
                        weekly_limit - used_classes
                    )

                allowances[student_id] = {
                    "plan_name": plan_name,
                    "weekly_limit": weekly_limit,
                    "used_classes": used_classes,
                    "remaining": remaining,
                    "is_unlimited": is_unlimited,
                    "has_membership": True,
                }

        return allowances

    # ─────────────────────────────────────────────────────────────
    # Guardar asistencia (transacción unificada)
    # Actualiza estado, instructor, invitados y asistencia en una sola transacción
    # ─────────────────────────────────────────────────────────────
    def save_attendance(
        self,
        class_id: int,
        class_status: str,
        instructor_id,
        present_student_ids,
        guest_count: int = 0,
        guest_names: str = "",
        admin_overrides=None,
        current_user_id=None,
    ):
        admin_overrides = admin_overrides or {}

        class_status = (
            class_status or "completed"
        ).strip().lower()

        valid_statuses = {
            "completed",
            "cancelled",
            "inactive",
        }

        if class_status not in valid_statuses:
            raise ValueError(
                "Estado de clase no válido."
            )

        present_student_ids = {
            int(student_id)
            for student_id in present_student_ids
        }

        if admin_overrides:
            if not self.is_admin_user(current_user_id):
                raise PermissionError(
                    "El usuario no tiene permiso para "
                    "autorizar asistencias sin cupo."
                )

        with db.transaction() as cur:
            if class_status != "completed":
                instructor_id = None
                guest_count = 0
                guest_names = ""
                present_student_ids = set()
                admin_overrides = {}

            cur.execute("""
                UPDATE classes
                SET status = %s,
                    id_instructor = %s,
                    guest_count = %s,
                    guest_names = %s
                WHERE id = %s;
            """, (
                class_status,
                instructor_id,
                int(guest_count or 0),
                guest_names.strip() or None,
                class_id,
            ))

            cur.execute("""
                DELETE FROM attendance
                WHERE id_class = %s;
            """, (class_id,))

            for student_id in present_student_ids:
                override_reason = admin_overrides.get(
                    student_id
                )

                is_override = bool(override_reason)

                cur.execute("""
                    INSERT INTO attendance (
                        id_class,
                        id_student,
                        status,
                        check_in_time,
                        is_admin_override,
                        override_user_id,
                        override_reason
                    )
                    VALUES (
                        %s,
                        %s,
                        'present',
                        CURRENT_TIMESTAMP,
                        %s,
                        %s,
                        %s
                    );
                """, (
                    class_id,
                    student_id,
                    is_override,
                    current_user_id if is_override else None,
                    override_reason if is_override else None,
                ))

    def get_schedules_for_day(self, day_of_week: int):
        """
        Retorna las clases activas programadas para un día de la semana.

        day_of_week:
            0 = lunes
            1 = martes
            ...
            6 = domingo
        """
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    s.id,
                    COALESCE(s.name, 'Clase') AS class_name,
                    s.start_time,
                    s.end_time,
                    COALESCE(
                        p.first_name || ' ' || p.last_name,
                        'Sin instructor'
                    ) AS instructor_name,
                    COALESCE(s.location, 'Sin ubicación') AS location,
                    COALESCE(s.color, '#C8102E') AS color

                FROM schedule s

                LEFT JOIN instructors i
                    ON i.id = s.id_instructor

                LEFT JOIN people p
                    ON p.id = i.id_person

                WHERE s.day_of_week = %s

                AND LOWER(
                    COALESCE(s.status, 'active')
                ) IN (
                    'active',
                    'activo'
                )

                ORDER BY s.start_time;
            """, (int(day_of_week),))

            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "start_time": row[2],
                    "end_time": row[3],
                    "instructor": row[4],
                    "location": row[5],
                    "color": row[6],
                }
                for row in cur.fetchall()
            ]