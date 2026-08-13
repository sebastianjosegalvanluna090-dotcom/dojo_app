from database.connection import db


class FinancesScholarshipsRepository:

    def _parse(self, r):
        return {
            "id":               r[0],
            "person_id":        r[1],
            "person_name":      r[2] or "",
            "monthly_fee":      float(r[3]) if r[3] else 0.0,
            "start_date":       r[4],
            "end_date":         r[5],
            "status":           r[6] or "active",
            "rate_class":       float(r[7]) if r[7] else 25000.0,
            "rate_deep_clean":  float(r[8]) if r[8] else 50000.0,
            "rate_maintenance": float(r[9]) if r[9] else 25000.0,
            "penalty_per_miss": float(r[10]) if r[10] else 25000.0,
            "notes":            r[11] or "",
            "created_at":       r[12],
        }

    def _q(self, extra=""):
        return f"""
            SELECT
                s.id, s.person_id,
                TRIM(COALESCE(p.first_name,'') || ' ' || COALESCE(p.last_name,'')) AS person_name,
                s.monthly_fee, s.start_date, s.end_date, s.status,
                s.rate_class, s.rate_deep_clean, s.rate_maintenance,
                s.penalty_per_miss, s.notes, s.created_at
            FROM scholarships s
            LEFT JOIN people p ON p.id = s.person_id
            {extra}
        """

    def get_all(self):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute(self._q("ORDER BY s.status, person_name"))
            return [self._parse(r) for r in cur.fetchall()]
        finally:
            cur.close(); db.release(conn)

    def get_active(self):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute(self._q("WHERE s.status = 'active' ORDER BY person_name"))
            return [self._parse(r) for r in cur.fetchall()]
        finally:
            cur.close(); db.release(conn)

    def get_by_person(self, person_id):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                self._q("WHERE s.person_id = %s AND s.status = 'active' ORDER BY s.start_date DESC LIMIT 1"),
                (person_id,)
            )
            r = cur.fetchone()
            return self._parse(r) if r else None
        finally:
            cur.close(); db.release(conn)

    def get_by_id(self, scholarship_id):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute(self._q("WHERE s.id = %s"), (scholarship_id,))
            r = cur.fetchone()
            return self._parse(r) if r else None
        finally:
            cur.close(); db.release(conn)

    def create(self, data):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO scholarships
                    (person_id, monthly_fee, start_date, end_date, status,
                     rate_class, rate_deep_clean, rate_maintenance, penalty_per_miss, notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
            """, (
                data.get("person_id"),
                data.get("monthly_fee", 0),
                data.get("start_date"),
                data.get("end_date"),
                data.get("status", "active"),
                data.get("rate_class", 25000),
                data.get("rate_deep_clean", 50000),
                data.get("rate_maintenance", 25000),
                data.get("penalty_per_miss", 25000),
                data.get("notes", ""),
            ))
            sid = cur.fetchone()[0]
            conn.commit()
            return sid
        except Exception:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    def update(self, scholarship_id, data):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE scholarships SET
                    person_id=%s, monthly_fee=%s, start_date=%s, end_date=%s,
                    status=%s, rate_class=%s, rate_deep_clean=%s,
                    rate_maintenance=%s, penalty_per_miss=%s, notes=%s
                WHERE id=%s
            """, (
                data.get("person_id"),
                data.get("monthly_fee", 0),
                data.get("start_date"),
                data.get("end_date"),
                data.get("status", "active"),
                data.get("rate_class", 25000),
                data.get("rate_deep_clean", 50000),
                data.get("rate_maintenance", 25000),
                data.get("penalty_per_miss", 25000),
                data.get("notes", ""),
                scholarship_id,
            ))
            conn.commit()
        except Exception:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    def terminate(self, scholarship_id):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE scholarships SET status='terminated', end_date=CURRENT_DATE WHERE id=%s",
                (scholarship_id,)
            )
            conn.commit()
        except Exception:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    def calculate_monthly_balance(self, person_id: int, month: int, year: int) -> dict:
        scholarship = self.get_by_person(person_id)
        if not scholarship:
            return {}
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    COALESCE(SUM(CASE WHEN NOT i.penalty THEN i.subtotal ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN i.penalty     THEN i.subtotal ELSE 0 END), 0)
                FROM collection_account_items i
                JOIN collection_accounts ca ON ca.id = i.collection_account_id
                WHERE ca.person_id    = %s
                  AND ca.period_month = %s
                  AND ca.period_year  = %s
                  AND ca.status      != 'cancelled'
            """, (person_id, month, year))
            r = cur.fetchone()
            activities = float(r[0]) if r else 0.0
            penalties  = float(r[1]) if r else 0.0
            net        = activities - penalties
            monthly    = float(scholarship["monthly_fee"])
            balance    = net - monthly
            return {
                "scholarship":  scholarship,
                "activities":   activities,
                "penalties":    penalties,
                "net":          net,
                "monthly_fee":  monthly,
                "balance":      balance,
                "dojo_owes":    max(balance, 0),
                "becado_owes":  max(-balance, 0),
            }
        finally:
            cur.close(); db.release(conn)

    def search_people(self, query=""):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            q = f"%{query.lower()}%"
            cur.execute("""
                SELECT id,
                    TRIM(COALESCE(first_name,'') || ' ' || COALESCE(last_name,'')) AS name,
                    COALESCE(email,''), COALESCE(phone,'')
                FROM people
                WHERE %s = ''
                   OR LOWER(first_name) LIKE %s
                   OR LOWER(last_name)  LIKE %s
                   OR LOWER(email)      LIKE %s
                ORDER BY name LIMIT 30
            """, (query, q, q, q))
            return [{"id": r[0], "name": r[1], "email": r[2], "phone": r[3]}
                    for r in cur.fetchall()]
        finally:
            cur.close(); db.release(conn)
