# ─── EVENTS_REPOSITORY ─────────────────────────────────────────────

from database.connection import db


class EventsRepository:
    """
    Repository para eventos especiales:
    - torneos
    - exámenes
    - seminarios
    - festivos
    """

    # Contrato usado por MonthlyEventsWidget:
    # 0 id
    # 1 name
    # 2 event_date
    # 3 event_type
    # 4 description
    # 5 color
    # 6 start_time
    # 7 end_time
    # 8 location
    # 9 is_important
    def get_month_events(self, year: int, month: int):
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    id,
                    name,
                    event_date,
                    event_type,
                    description,
                    COALESCE(color, '#3B82F6') AS color,
                    start_time,
                    end_time,
                    location,
                    COALESCE(is_important, false) AS is_important
                FROM events
                WHERE EXTRACT(YEAR FROM event_date) = %s
                  AND EXTRACT(MONTH FROM event_date) = %s
                ORDER BY event_date, start_time NULLS LAST, name;
            """, (year, month))

            return cur.fetchall()

        finally:
            cur.close()
            db.release(conn)

    def get_year_summary(self, year: int):
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    EXTRACT(MONTH FROM event_date)::int AS month,
                    COUNT(*) AS total
                FROM events
                WHERE EXTRACT(YEAR FROM event_date) = %s
                GROUP BY EXTRACT(MONTH FROM event_date)
                ORDER BY month;
            """, (year,))

            rows = cur.fetchall()
            return {int(month): int(total) for month, total in rows}

        finally:
            cur.close()
            db.release(conn)

    def get_by_id(self, event_id: int):
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    id,
                    name,
                    event_date,
                    event_type,
                    description,
                    color,
                    start_time,
                    end_time,
                    location,
                    is_important
                FROM events
                WHERE id = %s;
            """, (event_id,))

            row = cur.fetchone()
            if not row:
                return None

            return {
                "id": row[0],
                "name": row[1],
                "event_date": row[2],
                "event_type": row[3],
                "description": row[4],
                "color": row[5],
                "start_time": row[6],
                "end_time": row[7],
                "location": row[8],
                "is_important": row[9],
            }

        finally:
            cur.close()
            db.release(conn)

    def create(self, data: dict):
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO events (
                    name,
                    event_date,
                    event_type,
                    description,
                    color,
                    start_time,
                    end_time,
                    location,
                    is_important
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                data.get("name"),
                data.get("event_date"),
                data.get("event_type"),
                data.get("description"),
                data.get("color") or "#3B82F6",
                data.get("start_time"),
                data.get("end_time"),
                data.get("location"),
                bool(data.get("is_important")),
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

    def update(self, event_id: int, data: dict):
        conn = db.get_conn()
        try:
            cur = conn.cursor()

            cur.execute("""
                UPDATE events
                SET
                    name = %s,
                    event_date = %s,
                    event_type = %s,
                    description = %s,
                    color = %s,
                    start_time = %s,
                    end_time = %s,
                    location = %s,
                    is_important = %s
                WHERE id = %s;
            """, (
                data.get("name"),
                data.get("event_date"),
                data.get("event_type"),
                data.get("description"),
                data.get("color") or "#3B82F6",
                data.get("start_time"),
                data.get("end_time"),
                data.get("location"),
                bool(data.get("is_important")),
                event_id,
            ))

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cur.close()
            db.release(conn)

    def delete(self, event_id: int):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM events WHERE id = %s;", (event_id,))
            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cur.close()
            db.release(conn)