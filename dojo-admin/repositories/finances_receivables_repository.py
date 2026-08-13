from database.connection import db


class FinancesReceivablesRepository:

    def get_all(self, search=""):
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    fr.id,
                    fr.person_id,
                    fr.debtor_name,
                    fr.source_income_id,
                    fr.original_amount,
                    fr.paid_amount,
                    fr.pending_amount,
                    fr.due_date,
                    fr.status,
                    fr.created_at,
                    COALESCE(payments.payment_count, 0) AS payment_count,
                    COALESCE(payments.total_paid, 0) AS payments_total
                FROM finance_receivables fr
                LEFT JOIN (
                    SELECT receivable_id,
                           COUNT(*) AS payment_count,
                           COALESCE(SUM(amount), 0) AS total_paid
                    FROM finance_receivable_payments
                    GROUP BY receivable_id
                ) payments ON payments.receivable_id = fr.id
                WHERE (%s = '' OR LOWER(fr.debtor_name) LIKE %s)
                ORDER BY fr.created_at DESC
            """, (search, f"%{search}%"))
            return [
                {
                    "id": r[0],
                    "person_id": r[1],
                    "debtor_name": r[2],
                    "source_income_id": r[3],
                    "original_amount": float(r[4]) if r[4] else 0.0,
                    "paid_amount": float(r[5]) if r[5] else 0.0,
                    "pending_amount": float(r[6]) if r[6] else 0.0,
                    "due_date": r[7],
                    "status": r[8],
                    "created_at": r[9],
                    "payment_count": r[10],
                    "payments_total": float(r[11]) if r[11] else 0.0,
                }
                for r in cur.fetchall()
            ]

    def get_by_id(self, receivable_id):
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    id,
                    person_id,
                    debtor_name,
                    source_income_id,
                    source_participant_id,
                    original_amount,
                    paid_amount,
                    pending_amount,
                    due_date,
                    status,
                    created_at
                FROM finance_receivables
                WHERE id = %s
            """, (receivable_id,))
            r = cur.fetchone()
            if not r:
                return None
            return {
                "id": r[0],
                "person_id": r[1],
                "debtor_name": r[2],
                "source_income_id": r[3],
                "source_participant_id": r[4],
                "original_amount": float(r[5]) if r[5] else 0.0,
                "paid_amount": float(r[6]) if r[6] else 0.0,
                "pending_amount": float(r[7]) if r[7] else 0.0,
                "due_date": r[8],
                "status": r[9],
                "created_at": r[10],
            }

    def create_receivable(self, data):
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO finance_receivables (
                    person_id, debtor_name, source_income_id, source_participant_id,
                    original_amount, paid_amount, pending_amount, due_date, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data.get("person_id"),
                data.get("debtor_name"),
                data.get("source_income_id"),
                data.get("source_participant_id"),
                data.get("original_amount", 0),
                data.get("paid_amount", 0),
                data.get("pending_amount", 0),
                data.get("due_date"),
                data.get("status", "open"),
            ))
            return cur.fetchone()[0]

    def get_payments(self, receivable_id):
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, receivable_id, amount, payment_method_id, payment_date, note
                FROM finance_receivable_payments
                WHERE receivable_id = %s
                ORDER BY payment_date
            """, (receivable_id,))
            return [
                {
                    "id": r[0],
                    "receivable_id": r[1],
                    "amount": float(r[2]) if r[2] else 0.0,
                    "payment_method_id": r[3],
                    "payment_date": r[4],
                    "note": r[5] or "",
                }
                for r in cur.fetchall()
            ]

    def register_payment(self, receivable_id, amount, payment_method_id=None, note=""):
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO finance_receivable_payments (receivable_id, amount, payment_method_id, note)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (receivable_id, amount, payment_method_id, note))
            payment_id = cur.fetchone()[0]

            cur.execute("""
                UPDATE finance_receivables
                SET
                    paid_amount = paid_amount + %s,
                    pending_amount = pending_amount - %s,
                    status = CASE
                        WHEN pending_amount - %s <= 0 THEN 'paid'
                        WHEN paid_amount + %s > 0 THEN 'partial'
                        ELSE status
                    END
                WHERE id = %s
            """, (amount, amount, amount, amount, receivable_id))

            return payment_id

    def cancel_receivable(self, receivable_id):
        with db.transaction() as cur:
            cur.execute("""
                UPDATE finance_receivables
                SET status = 'cancelled'
                WHERE id = %s
            """, (receivable_id,))

    def get_by_person(self, person_id: int) -> list:
        """Retorna todas las carteras de una persona, ordenadas por fecha."""
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    id, person_id, debtor_name, source_income_id,
                    original_amount, paid_amount, pending_amount,
                    due_date, status, created_at
                FROM finance_receivables
                WHERE person_id = %s
                ORDER BY created_at DESC
            """, (person_id,))
            return [
                {
                    "id":              r[0],
                    "person_id":       r[1],
                    "debtor_name":     r[2],
                    "source_income_id": r[3],
                    "original_amount": float(r[4]) if r[4] else 0.0,
                    "paid_amount":     float(r[5]) if r[5] else 0.0,
                    "pending_amount":  float(r[6]) if r[6] else 0.0,
                    "due_date":        r[7],
                    "status":          r[8],
                    "created_at":      r[9],
                }
                for r in cur.fetchall()
            ]

    def get_person_contact(self, person_id: int) -> dict:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    COALESCE(p.email, '')    AS email,
                    COALESCE(p.phone, '')    AS phone,
                    COALESCE(
                        td.type_document || ': ' || s.document,
                        p.email,
                        ''
                    )                        AS documento
                FROM people p
                LEFT JOIN students s         ON s.id_person = p.id
                LEFT JOIN type_document td   ON td.id = s.id_type_document
                WHERE p.id = %s
                LIMIT 1
            """, (person_id,))
            r = cur.fetchone()
            if not r:
                return {}
            return {"email": r[0], "phone": r[1], "documento": r[2]}
