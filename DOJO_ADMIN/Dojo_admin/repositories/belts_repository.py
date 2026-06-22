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
                       pre_color
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
                }
                for r in cur.fetchall()
            ]
        finally:
            cur.close(); db.release(conn)

    def create_belt(self, martial_art_id: int, name: str, orden: int = None, color: str = None, pre_color: str = None):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO belts (name, id_martial_art, orden, color, pre_color)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, martial_art_id, orden, color, pre_color))
            conn.commit()
        except:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    def update_belt(self, belt_id: int, name: str, orden: int = None, color: str = None, pre_color: str = None):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE belts SET name = %s, orden = %s, color = %s, pre_color = %s WHERE id = %s
            """, (name, orden, color, pre_color, belt_id))
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