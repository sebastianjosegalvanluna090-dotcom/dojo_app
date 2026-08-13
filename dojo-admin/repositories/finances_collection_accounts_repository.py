from database.connection import db


class FinancesCollectionAccountsRepository:

    def _parse_row(self, r):
        return {
            "id":            r[0],
            "person_id":     r[1],
            "person_name":   r[2] or "",
            "concept":       r[3] or "",
            "total_amount":  float(r[4]) if r[4] else 0.0,
            "status":        r[5] or "draft",
            "due_date":      r[6],
            "issued_date":   r[7],
            "notes":         r[8] or "",
            "scholarship_id":r[9],
            "period_month":  r[10],
            "period_year":   r[11],
            "created_at":    r[12],
        }

    def get_all(self, search="", status_filter="all", month=None, year=None):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            where = ["1=1"]; params = []
            if search:
                s = f"%{search.lower()}%"
                where.append("""(
                    LOWER(ca.person_name) LIKE %s
                    OR LOWER(COALESCE(p.first_name,'') || ' ' || COALESCE(p.last_name,'')) LIKE %s
                    OR LOWER(ca.concept) LIKE %s
                )""")
                params += [s, s, s]
            if status_filter and status_filter != "all":
                where.append("ca.status = %s"); params.append(status_filter)
            if month:
                where.append("ca.period_month = %s"); params.append(month)
            if year:
                where.append("ca.period_year = %s"); params.append(year)

            cur.execute(f"""
                SELECT
                    ca.id, ca.person_id,
                    COALESCE(ca.person_name,
                        TRIM(COALESCE(p.first_name,'') || ' ' || COALESCE(p.last_name,'')),
                        '') AS person_name,
                    ca.concept, ca.total_amount, ca.status,
                    ca.due_date, ca.issued_date, ca.notes,
                    ca.scholarship_id, ca.period_month, ca.period_year, ca.created_at,
                    (SELECT COUNT(*) FROM collection_account_items
                     WHERE collection_account_id = ca.id) AS items_count
                FROM collection_accounts ca
                LEFT JOIN people p ON p.id = ca.person_id
                WHERE {" AND ".join(where)}
                ORDER BY ca.issued_date DESC, ca.id DESC
            """, params)
            rows = cur.fetchall()
            result = []
            for r in rows:
                d = self._parse_row(r[:13])
                d["items_count"] = r[13]
                result.append(d)
            return result
        finally:
            cur.close(); db.release(conn)

    def get_by_id(self, account_id):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    ca.id, ca.person_id,
                    COALESCE(ca.person_name,
                        TRIM(COALESCE(p.first_name,'') || ' ' || COALESCE(p.last_name,'')),
                        '') AS person_name,
                    ca.concept, ca.total_amount, ca.status,
                    ca.due_date, ca.issued_date, ca.notes,
                    ca.scholarship_id, ca.period_month, ca.period_year, ca.created_at
                FROM collection_accounts ca
                LEFT JOIN people p ON p.id = ca.person_id
                WHERE ca.id = %s
            """, (account_id,))
            r = cur.fetchone()
            return self._parse_row(r) if r else None
        finally:
            cur.close(); db.release(conn)

    def get_items(self, account_id):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, collection_account_id, activity_type, description,
                       quantity, unit_price, subtotal, activity_date, penalty
                FROM collection_account_items
                WHERE collection_account_id = %s
                ORDER BY penalty, id
            """, (account_id,))
            return [{
                "id":                    r[0],
                "collection_account_id": r[1],
                "activity_type":         r[2] or "otro",
                "description":           r[3] or "",
                "quantity":              float(r[4]) if r[4] else 1.0,
                "unit_price":            float(r[5]) if r[5] else 0.0,
                "subtotal":              float(r[6]) if r[6] else 0.0,
                "activity_date":         r[7],
                "penalty":               bool(r[8]),
            } for r in cur.fetchall()]
        finally:
            cur.close(); db.release(conn)

    def create(self, data):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO collection_accounts
                    (person_id, person_name, concept, total_amount, status,
                     due_date, issued_date, notes, scholarship_id,
                     period_month, period_year)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
            """, (
                data.get("person_id"),
                data.get("person_name", ""),
                data.get("concept", ""),
                data.get("total_amount", 0),
                data.get("status", "draft"),
                data.get("due_date"),
                data.get("issued_date"),
                data.get("notes", ""),
                data.get("scholarship_id"),
                data.get("period_month"),
                data.get("period_year"),
            ))
            account_id = cur.fetchone()[0]
            for item in data.get("items", []):
                cur.execute("""
                    INSERT INTO collection_account_items
                        (collection_account_id, activity_type, description,
                         quantity, unit_price, subtotal, activity_date, penalty)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    account_id,
                    item.get("activity_type", "otro"),
                    item.get("description", ""),
                    item.get("quantity", 1),
                    item.get("unit_price", 0),
                    item.get("subtotal", 0),
                    item.get("activity_date"),
                    item.get("penalty", False),
                ))
            conn.commit()
            return account_id
        except Exception:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    def update(self, account_id, data):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE collection_accounts SET
                    person_id=%s, person_name=%s, concept=%s, total_amount=%s,
                    status=%s, due_date=%s, issued_date=%s, notes=%s,
                    scholarship_id=%s, period_month=%s, period_year=%s
                WHERE id=%s
            """, (
                data.get("person_id"),
                data.get("person_name", ""),
                data.get("concept", ""),
                data.get("total_amount", 0),
                data.get("status", "draft"),
                data.get("due_date"),
                data.get("issued_date"),
                data.get("notes", ""),
                data.get("scholarship_id"),
                data.get("period_month"),
                data.get("period_year"),
                account_id,
            ))
            cur.execute(
                "DELETE FROM collection_account_items WHERE collection_account_id=%s",
                (account_id,)
            )
            for item in data.get("items", []):
                cur.execute("""
                    INSERT INTO collection_account_items
                        (collection_account_id, activity_type, description,
                         quantity, unit_price, subtotal, activity_date, penalty)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    account_id,
                    item.get("activity_type", "otro"),
                    item.get("description", ""),
                    item.get("quantity", 1),
                    item.get("unit_price", 0),
                    item.get("subtotal", 0),
                    item.get("activity_date"),
                    item.get("penalty", False),
                ))
            conn.commit()
        except Exception:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    def update_status(self, account_id: int, status: str):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE collection_accounts SET status=%s WHERE id=%s",
                (status, account_id)
            )
            conn.commit()
        except Exception:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    def delete(self, account_id):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM collection_accounts WHERE id=%s", (account_id,))
            conn.commit()
        except Exception:
            conn.rollback(); raise
        finally:
            cur.close(); db.release(conn)

    def get_by_person(self, person_id: int):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, person_id, person_name, concept, total_amount, status,
                       due_date, issued_date, notes, scholarship_id,
                       period_month, period_year, created_at
                FROM collection_accounts
                WHERE person_id=%s
                ORDER BY issued_date DESC
            """, (person_id,))
            return [self._parse_row(r) for r in cur.fetchall()]
        finally:
            cur.close(); db.release(conn)

    def get_kpis(self):
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    COALESCE(SUM(CASE WHEN status IN ('pending','approved')
                        THEN total_amount ELSE 0 END), 0),
                    COUNT(CASE WHEN status='approved'
                        AND DATE_TRUNC('month',issued_date)=DATE_TRUNC('month',CURRENT_DATE)
                        THEN 1 END),
                    COALESCE(SUM(CASE WHEN status='paid'
                        AND DATE_TRUNC('month',issued_date)=DATE_TRUNC('month',CURRENT_DATE)
                        THEN total_amount ELSE 0 END), 0),
                    (SELECT COUNT(*) FROM scholarships WHERE status='active')
                FROM collection_accounts
            """)
            r = cur.fetchone()
            return {
                "pending_amount":      float(r[0]) if r[0] else 0.0,
                "approved_this_month": int(r[1])   if r[1] else 0,
                "paid_this_month":     float(r[2]) if r[2] else 0.0,
                "active_scholars":     int(r[3])   if r[3] else 0,
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
                    COALESCE(email,''), COALESCE(phone,''), COALESCE(document,'')
                FROM people
                WHERE %s=''
                   OR LOWER(first_name) LIKE %s
                   OR LOWER(last_name)  LIKE %s
                   OR LOWER(email)      LIKE %s
                ORDER BY name LIMIT 30
            """, (query, q, q, q))
            return [{"id": r[0], "name": r[1], "email": r[2], "phone": r[3], "document": r[4]}
                    for r in cur.fetchall()]
        finally:
            cur.close(); db.release(conn)
