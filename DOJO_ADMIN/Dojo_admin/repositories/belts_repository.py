from database.connection import db


class BeltsRepository:

    # ── Artes Marciales ───────────────────────────────────────────────
    def get_martial_arts(self) -> list:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM martial_arts ORDER BY name")
            return [{"id": r[0], "name": r[1]} for r in cur.fetchall()]
        finally:
            cur.close(); db.release(conn)

    def create_martial_art(self, name: str):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO martial_arts (name) VALUES (%s)", (name,))
            conn.commit()
        except:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    def update_martial_art(self, ma_id: int, name: str):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("UPDATE martial_arts SET name = %s WHERE id = %s", (name, ma_id))
            conn.commit()
        except:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    def delete_martial_art(self, ma_id: int):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM martial_arts WHERE id = %s", (ma_id,))
            conn.commit()
        except:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    # ── Cinturones ────────────────────────────────────────────────────
    def get_belts(self, martial_art_id: int) -> list:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, name, orden,
                    COALESCE(color, '#888888'),
                    pre_color,
                    COALESCE(grades, 0),
                    COALESCE(grade_color, '#FFFFFF')
                FROM belts
                WHERE id_martial_art = %s
                ORDER BY orden ASC NULLS LAST, name
            """, (martial_art_id,))

            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "orden": r[2],
                    "color": r[3],
                    "pre_color": r[4],
                    "grades": r[5],
                    "grade_color": r[6],
                }
                for r in cur.fetchall()
            ]
        finally:
            cur.close()
            db.release(conn)

    def create_belt(self, martial_art_id: int, name: str, orden: int = None, color: str = None, pre_color: str = None, grades: int = 0, grade_color: str = "#FFFFFF"):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO belts (name, id_martial_art, orden, color, pre_color, grades, grade_color)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, martial_art_id, orden, color, pre_color, grades, grade_color))
            conn.commit()
        except:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    def update_belt(self, belt_id: int, name: str, orden: int = None, color: str = None, pre_color: str = None, grades: int = 0, grade_color: str = "#FFFFFF"):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE belts
                SET name = %s,
                    orden = %s,
                    color = %s,
                    pre_color = %s,
                    grades = %s,
                    grade_color = %s
                WHERE id = %s
            """, (name, orden, color, pre_color, grades, grade_color, belt_id))
            conn.commit()
        except:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    def delete_belt(self, belt_id: int):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM belts WHERE id = %s", (belt_id,))
            conn.commit()
        except:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    # ── Requisitos ────────────────────────────────────────────────────
    def get_requirements(self, belt_id: int) -> list:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT br.id, br.requirement, br.id_type_requeriments,
                       tr.type_requirement
                FROM belt_requirements br
                LEFT JOIN type_requirements tr ON tr.id = br.id_type_requeriments
                WHERE br.belt_id = %s
                ORDER BY br.created_at
            """, (belt_id,))
            return [
                {"id": r[0], "requirement": r[1],
                 "id_type": r[2], "type_name": r[3]}
                for r in cur.fetchall()
            ]
        finally:
            cur.close(); db.release(conn)

    def get_requirement_types(self) -> list:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, type_requirement FROM type_requirements ORDER BY type_requirement")
            return cur.fetchall()
        finally:
            cur.close(); db.release(conn)

    def create_requirement(self, belt_id: int, requirement: str, tipo_id: int = None):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO belt_requirements (belt_id, requirement, id_type_requeriments)
                VALUES (%s, %s, %s)
            """, (belt_id, requirement, tipo_id))
            conn.commit()
        except:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    def update_requirement(self, req_id: int, requirement: str, tipo_id: int = None):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE belt_requirements
                SET requirement = %s, id_type_requeriments = %s
                WHERE id = %s
            """, (requirement, tipo_id, req_id))
            conn.commit()
        except:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    def delete_requirement(self, req_id: int):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM belt_requirements WHERE id = %s", (req_id,))
            conn.commit()
        except:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)
     
    def get_instructors_that_can_promote(self, martial_art_id: int) -> list:
        """Retorna instructores con permiso can_promote para un arte marcial."""
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    i.id,
                    p.first_name || ' ' || p.last_name AS nombre
                FROM instructor_martial_arts ima
                JOIN instructors i  ON i.id  = ima.id_instructor
                JOIN people      p  ON p.id  = i.id_person
                WHERE ima.id_martial_art = %s
                  AND ima.can_promote = TRUE
                ORDER BY p.first_name, p.last_name
            """, (martial_art_id,))
            return [{"id": r[0], "nombre": r[1]} for r in cur.fetchall()]
        finally:
            cur.close(); db.release(conn)
 
    def get_students_by_martial_art(self, martial_art_id: int) -> list:
            """
            Retorna todos los estudiantes activos con su cinturón actual
            en el arte marcial dado (si tienen uno).
            """
            conn = db.get_conn()
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT
                        s.id,
                        p.first_name || ' ' || p.last_name  AS nombre,
                        COALESCE(b.id,    0)                 AS belt_id,
                        COALESCE(b.name, 'Sin cinturón')     AS belt_name,
                        COALESCE(b.color, '#888888')          AS belt_color,
                        COALESCE(b.orden, 0)                  AS belt_orden,
                        COALESCE(b.grades, 0)                 AS belt_grades
                    FROM students s
                    JOIN people p  ON p.id  = s.id_person
                    JOIN status st ON st.id = s.id_status
                        AND LOWER(st.status) IN ('activo', 'active')
                    LEFT JOIN students_belts sb ON sb.id_student = s.id
                    LEFT JOIN belts b
                        ON b.id = sb.id_belt
                        AND b.id_martial_art = %s
                    ORDER BY p.first_name, p.last_name
                """, (martial_art_id,))
                return [
                    {
                        "id":          r[0],
                        "nombre":      r[1],
                        "belt_id":     r[2],
                        "belt_name":   r[3],
                        "belt_color":  r[4],
                        "belt_orden":  r[5],
                        "belt_grades": r[6],
                    }
                    for r in cur.fetchall()
                ]
            finally:
                cur.close(); db.release(conn)
 
    def get_next_belts(self, martial_art_id: int, current_orden: int) -> list:
        """Cinturones disponibles para ascender (orden > actual)."""
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, name, orden,
                    COALESCE(color, '#888888'),
                    pre_color,
                    COALESCE(grades, 0),
                    COALESCE(grade_color, '#FFFFFF')
                FROM belts
                WHERE id_martial_art = %s
                AND (orden > %s OR %s = 0)
                ORDER BY orden ASC NULLS LAST, name
            """, (martial_art_id, current_orden, current_orden))

            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "orden": r[2],
                    "color": r[3],
                    "pre_color": r[4],
                    "grades": r[5],
                    "grade_color": r[6],
                }
                for r in cur.fetchall()
            ]
        finally:
            cur.close()
            db.release(conn)
 
    def get_next_belts(self, martial_art_id: int, current_orden: int) -> list:
        """Cinturones disponibles para ascender (orden > actual)."""
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, name, orden,
                    COALESCE(color, '#888888'),
                    pre_color,
                    COALESCE(grades, 0),
                    COALESCE(grade_color, '#FFFFFF')
                FROM belts
                WHERE id_martial_art = %s
                ORDER BY orden ASC NULLS LAST, name
            """, (martial_art_id,))
            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "orden": r[2],
                    "color": r[3],
                    "pre_color": r[4],
                    "grades": r[5],
                    "grade_color": r[6],
                }
                for r in cur.fetchall()
            ]
        finally:
            cur.close(); db.release(conn)
 
    def promote_student(self, student_id: int, belt_id: int, instructor_id: int,
                        martial_art_id: int):
        """
        Asciende al estudiante:
        1. Actualiza o inserta en students_belts (cinturón actual)
        2. Inserta en students_belts_history
        Valida que el instructor tenga can_promote en ese arte.
        """
        conn = db.get_conn()
        try:
            cur = conn.cursor()
 
            # Verificar permiso del instructor
            cur.execute("""
                SELECT can_promote FROM instructor_martial_arts
                WHERE id_instructor = %s AND id_martial_art = %s
            """, (instructor_id, martial_art_id))
            row = cur.fetchone()
            if not row or not row[0]:
                raise ValueError("Este instructor no tiene permiso para promover en este arte marcial.")
 
            # Upsert cinturón actual en students_belts
            # Buscar si ya tiene cinturón EN ESTE arte marcial específico
            cur.execute("""
                SELECT sb.id FROM students_belts sb
                JOIN belts b ON b.id = sb.id_belt
                WHERE sb.id_student = %s AND b.id_martial_art = %s
            """, (student_id, martial_art_id))
            existing = cur.fetchone()
            if existing:
                cur.execute("""
                    UPDATE students_belts SET id_belt = %s WHERE id = %s
                """, (belt_id, existing[0]))
            else:
                cur.execute("""
                    INSERT INTO students_belts (id_student, id_belt)
                    VALUES (%s, %s)
                """, (student_id, belt_id))
 
            # Registrar en historial
            cur.execute("""
                INSERT INTO students_belts_history
                    (id_student, id_belt, action, date_changed)
                VALUES (%s, %s, 'promotion', NOW())
            """, (student_id, belt_id))
 
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close(); db.release(conn)