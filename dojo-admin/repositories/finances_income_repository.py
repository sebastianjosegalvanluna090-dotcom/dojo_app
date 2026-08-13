from database.connection import db


class FinancesIncomeRepository:

    def _parse_row(self, r):
        return {
            "id": r[0],
            "payer_name": r[1],
            "payer_type": r[2],
            "income_date": r[3],
            "subtotal": float(r[4]) if r[4] else 0.0,
            "discount": float(r[5]) if r[5] else 0.0,
            "total": float(r[6]) if r[6] else 0.0,
            "total_paid": float(r[7]) if r[7] else 0.0,
            "pending_amount": float(r[8]) if r[8] else 0.0,
            "status": r[9],
            "note": r[10] or "",
            "agreement_note": r[11] or "",
            "payer_person_id": r[12],
            "payer_document": r[13] or "",
            "payer_email": r[14] or "",
            "payer_phone": r[15] or "",
            "payment_method_id": r[16],
            "destination_account_id": r[17],
            "receipt_number": r[18] or "" if len(r) > 18 else "",
            "receipt_pdf_path": r[19] or "" if len(r) > 19 else "",
            "receipt_generated_at": r[20] if len(r) > 20 else None,
        }

    def get_all(self, search=""):
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    fi.id,
                    fi.payer_name,
                    fi.payer_type,
                    fi.income_date,
                    fi.subtotal,
                    fi.discount,
                    fi.total,
                    fi.total_paid,
                    fi.pending_amount,
                    fi.status,
                    fi.note,
                    fi.agreement_note,
                    fi.payer_person_id,
                    fi.payer_document,
                    fi.payer_email,
                    fi.payer_phone,
                    fi.payment_method_id,
                    fi.destination_account_id,
                    fi.receipt_number,
                    fi.receipt_pdf_path,
                    fi.receipt_generated_at,
                    COALESCE(items.cnt, 0) AS items_count,
                    COALESCE(participants.cnt, 0) AS participants_count,
                    COALESCE(student_participants.student_names, '') AS student_names,
                    COALESCE(pm.name, '') AS payment_method_name,
                    COALESCE(da.name, '') AS destination_account_name
                FROM finance_income fi
                LEFT JOIN (
                    SELECT income_id, COUNT(*) AS cnt
                    FROM finance_income_items
                    GROUP BY income_id
                ) items ON items.income_id = fi.id
                LEFT JOIN (
                    SELECT income_id, COUNT(*) AS cnt
                    FROM finance_income_participants
                    GROUP BY income_id
                ) participants ON participants.income_id = fi.id
                LEFT JOIN (
                    SELECT
                        income_id,
                        STRING_AGG(display_name, ', ' ORDER BY id) AS student_names
                    FROM finance_income_participants
                    WHERE COALESCE(expected_amount, 0) = 0
                      AND COALESCE(pending_amount, 0) = 0
                    GROUP BY income_id
                ) student_participants ON student_participants.income_id = fi.id
                LEFT JOIN payment_method pm ON pm.id = fi.payment_method_id
                LEFT JOIN destination_account da ON da.id = fi.destination_account_id
                WHERE (%s = '' OR LOWER(fi.payer_name) LIKE %s)
                ORDER BY fi.income_date DESC
            """, (search, f"%{search}%"))
            rows = cur.fetchall()
            result = []
            for r in rows:
                base = self._parse_row(r[:21])
                base["items_count"] = r[21]
                base["participants_count"] = r[22]
                base["student_names"] = r[23] or ""
                base["payment_method_name"] = r[24] or ""
                base["destination_account_name"] = r[25] or ""
                result.append(base)
            return result

    def get_by_id(self, income_id):
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    fi.id,
                    fi.payer_name,
                    fi.payer_type,
                    fi.income_date,
                    fi.subtotal,
                    fi.discount,
                    fi.total,
                    fi.total_paid,
                    fi.pending_amount,
                    fi.status,
                    fi.note,
                    fi.agreement_note,
                    fi.payer_person_id,
                    fi.payer_document,
                    fi.payer_email,
                    fi.payer_phone,
                    fi.payment_method_id,
                    fi.destination_account_id,
                    fi.receipt_number,
                    fi.receipt_pdf_path,
                    fi.receipt_generated_at,
                    COALESCE(pm.name, '') AS payment_method_name,
                    COALESCE(da.name, '') AS destination_account_name
                FROM finance_income fi
                LEFT JOIN payment_method pm ON pm.id = fi.payment_method_id
                LEFT JOIN destination_account da ON da.id = fi.destination_account_id
                WHERE fi.id = %s
            """, (income_id,))
            r = cur.fetchone()
            if not r:
                return None
            base = self._parse_row(r[:21])
            base["payment_method_name"] = r[21] or ""
            base["destination_account_name"] = r[22] or ""
            return base

    def get_income_items(self, income_id):
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, income_id, name, quantity, unit_price, discount, subtotal, item_type, reference_id, details
                FROM finance_income_items
                WHERE income_id = %s
                ORDER BY id
            """, (income_id,))
            return [
                {
                    "id": r[0],
                    "income_id": r[1],
                    "name": r[2],
                    "quantity": r[3],
                    "unit_price": float(r[4]) if r[4] else 0.0,
                    "discount": float(r[5]) if r[5] else 0.0,
                    "subtotal": float(r[6]) if r[6] else 0.0,
                    "item_type": r[7],
                    "reference_id": r[8],
                    "details": r[9] or "",
                }
                for r in cur.fetchall()
            ]

    def get_income_participants(self, income_id):
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, income_id, display_name, expected_amount, paid_amount, pending_amount, due_date, person_id
                FROM finance_income_participants
                WHERE income_id = %s
                ORDER BY id
            """, (income_id,))
            return [
                {
                    "id": r[0],
                    "income_id": r[1],
                    "display_name": r[2],
                    "expected_amount": float(r[3]) if r[3] else 0.0,
                    "paid_amount": float(r[4]) if r[4] else 0.0,
                    "pending_amount": float(r[5]) if r[5] else 0.0,
                    "due_date": r[6],
                    "person_id": r[7],
                }
                for r in cur.fetchall()
            ]

    def create_income(self, data):
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO finance_income (
                    payer_name, payer_type, income_date, subtotal, discount,
                    total, total_paid, pending_amount, status, note, agreement_note,
                    payer_person_id, payer_document, payer_email, payer_phone,
                    payment_method_id, destination_account_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data.get("payer_name"),
                data.get("payer_type"),
                data.get("income_date"),
                data.get("subtotal", 0),
                data.get("discount", 0),
                data.get("total", 0),
                data.get("total_paid", 0),
                data.get("pending_amount", 0),
                data.get("status", "pending"),
                data.get("note", ""),
                data.get("agreement_note", ""),
                data.get("payer_person_id"),
                data.get("payer_document", ""),
                data.get("payer_email", ""),
                data.get("payer_phone", ""),
                data.get("payment_method_id"),
                data.get("destination_account_id"),
            ))
            income_id = cur.fetchone()[0]

            for item in data.get("items", []):
                cur.execute("""
                    INSERT INTO finance_income_items (income_id, name, quantity, unit_price, discount, subtotal, item_type, reference_id, details)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    income_id,
                    item.get("name", ""),
                    item.get("quantity", 1),
                    item.get("unit_price", 0),
                    item.get("discount", 0),
                    item.get("subtotal", 0),
                    item.get("item_type", "other"),
                    item.get("reference_id"),
                    item.get("details", ""),
                ))

            for participant in data.get("participants", []):
                cur.execute("""
                    INSERT INTO finance_income_participants (income_id, display_name, expected_amount, paid_amount, pending_amount, due_date, person_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    income_id,
                    participant.get("display_name"),
                    participant.get("expected_amount", 0),
                    participant.get("paid_amount", 0),
                    participant.get("pending_amount", 0),
                    participant.get("due_date"),
                    participant.get("person_id"),
                ))
                participant_id = cur.fetchone()[0]

                if participant.get("pending_amount", 0) > 0:
                    cur.execute("""
                        INSERT INTO finance_receivables (
                            debtor_name, source_income_id, source_participant_id,
                            original_amount, paid_amount, pending_amount, due_date, status
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        participant.get("display_name"),
                        income_id,
                        participant_id,
                        participant.get("expected_amount", 0),
                        participant.get("paid_amount", 0),
                        participant.get("pending_amount", 0),
                        participant.get("due_date", data.get("income_date")),
                        "open",
                    ))

            for item in data.get("items", []):
                if item.get("item_type") in ("inventory", "inventory_product") and item.get("reference_id"):
                    cur.execute("""
                        UPDATE products SET stock = stock - %s WHERE id = %s
                    """, (item.get("quantity", 1), item.get("reference_id")))

            return income_id

    def update_income(self, income_id, data):
        with db.transaction() as cur:
            cur.execute("""
                UPDATE finance_income SET
                    payer_name = %s,
                    payer_type = %s,
                    income_date = %s,
                    subtotal = %s,
                    discount = %s,
                    total = %s,
                    total_paid = %s,
                    pending_amount = %s,
                    status = %s,
                    note = %s,
                    agreement_note = %s,
                    payer_person_id = %s,
                    payer_document = %s,
                    payer_email = %s,
                    payer_phone = %s,
                    payment_method_id = %s,
                    destination_account_id = %s
                WHERE id = %s
            """, (
                data.get("payer_name"),
                data.get("payer_type"),
                data.get("income_date"),
                data.get("subtotal", 0),
                data.get("discount", 0),
                data.get("total", 0),
                data.get("total_paid", 0),
                data.get("pending_amount", 0),
                data.get("status", "pending"),
                data.get("note", ""),
                data.get("agreement_note", ""),
                data.get("payer_person_id"),
                data.get("payer_document", ""),
                data.get("payer_email", ""),
                data.get("payer_phone", ""),
                data.get("payment_method_id"),
                data.get("destination_account_id"),
                income_id,
            ))

            cur.execute("DELETE FROM finance_income_items WHERE income_id = %s", (income_id,))
            for item in data.get("items", []):
                cur.execute("""
                    INSERT INTO finance_income_items (income_id, name, quantity, unit_price, discount, subtotal, item_type, reference_id, details)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    income_id,
                    item.get("name", ""),
                    item.get("quantity", 1),
                    item.get("unit_price", 0),
                    item.get("discount", 0),
                    item.get("subtotal", 0),
                    item.get("item_type", "other"),
                    item.get("reference_id"),
                    item.get("details", ""),
                ))

            old_participant_ids = []
            cur.execute("SELECT id FROM finance_income_participants WHERE income_id = %s", (income_id,))
            for row in cur.fetchall():
                old_participant_ids.append(row[0])

            cur.execute("DELETE FROM finance_receivables WHERE source_income_id = %s", (income_id,))
            cur.execute("DELETE FROM finance_income_participants WHERE income_id = %s", (income_id,))

            for participant in data.get("participants", []):
                cur.execute("""
                    INSERT INTO finance_income_participants (income_id, display_name, expected_amount, paid_amount, pending_amount, due_date, person_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    income_id,
                    participant.get("display_name"),
                    participant.get("expected_amount", 0),
                    participant.get("paid_amount", 0),
                    participant.get("pending_amount", 0),
                    participant.get("due_date"),
                    participant.get("person_id"),
                ))
                participant_id = cur.fetchone()[0]

                if participant.get("pending_amount", 0) > 0:
                    cur.execute("""
                        INSERT INTO finance_receivables (
                            debtor_name, source_income_id, source_participant_id,
                            original_amount, paid_amount, pending_amount, due_date, status
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        participant.get("display_name"),
                        income_id,
                        participant_id,
                        participant.get("expected_amount", 0),
                        participant.get("paid_amount", 0),
                        participant.get("pending_amount", 0),
                        participant.get("due_date", data.get("income_date")),
                        "open",
                    ))

    def search_people(self, query=""):
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, first_name, last_name, COALESCE(phone, ''), COALESCE(email, '')
                FROM people
                WHERE (%s = ''
                    OR LOWER(first_name) LIKE %s
                    OR LOWER(last_name) LIKE %s
                    OR LOWER(phone) LIKE %s
                    OR LOWER(email) LIKE %s)
                ORDER BY first_name, last_name
                LIMIT 30
            """, (query, f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
            return [
                {
                    "id": r[0],
                    "first_name": r[1],
                    "last_name": r[2],
                    "phone": r[3],
                    "email": r[4],
                    "display_name": f"{r[1]} {r[2]}".strip(),
                }
                for r in cur.fetchall()
            ]

    def get_people_for_income(self):
        with db.cursor() as cur:
            cur.execute("""
                WITH primary_guardian AS (
                    SELECT DISTINCT ON (sg.id_student)
                        sg.id_student,
                        sg.full_name,
                        COALESCE(sg.phone, '') AS phone,
                        COALESCE(sg.email, '') AS email,
                        COALESCE(sg.relationship, '') AS relationship
                    FROM student_guardians sg
                    ORDER BY sg.id_student, sg.is_primary DESC, sg.id ASC
                )
                SELECT
                    p.id AS person_id,
                    s.id AS student_id,
                    TRIM(CONCAT(COALESCE(p.first_name, ''), ' ', COALESCE(p.last_name, ''))) AS name,
                    COALESCE(s.document, '') AS document,
                    COALESCE(p.email, '') AS email,
                    COALESCE(p.phone, '') AS phone,
                    CASE WHEN s.id IS NOT NULL THEN 'student' ELSE 'third_party' END AS payer_type,
                    COALESCE(c.name, '') AS category_name,
                    COALESCE(pg.full_name, '') AS guardian_name,
                    COALESCE(pg.phone, '') AS guardian_phone,
                    COALESCE(pg.email, '') AS guardian_email,
                    COALESCE(pg.relationship, '') AS guardian_relationship
                FROM people p
                LEFT JOIN students s ON s.id_person = p.id
                LEFT JOIN categories c ON c.id = s.category_id
                LEFT JOIN primary_guardian pg ON pg.id_student = s.id
                ORDER BY name
            """)
            return [
                {
                    "id": r[0],
                    "person_id": r[0],
                    "student_id": r[1],
                    "name": r[2],
                    "document": r[3],
                    "email": r[4],
                    "phone": r[5],
                    "payer_type": r[6],
                    "category_name": r[7],
                    "guardian_name": r[8],
                    "guardian_phone": r[9],
                    "guardian_email": r[10],
                    "guardian_relationship": r[11],
                    "is_kid": str(r[7] or "").upper() == "KID",
                }
                for r in cur.fetchall()
            ]

    def get_students_for_income(self):
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    s.id,
                    p.id AS person_id,
                    TRIM(CONCAT(COALESCE(p.first_name, ''), ' ', COALESCE(p.last_name, ''))) AS full_name,
                    COALESCE(s.document, '') AS document,
                    COALESCE(st.status, '') AS status
                FROM students s
                JOIN people p ON p.id = s.id_person
                LEFT JOIN status st ON st.id = s.id_status
                ORDER BY full_name
            """)
            return [
                {
                    "student_id": r[0],
                    "person_id": r[1],
                    "name": r[2],
                    "document": r[3],
                    "status": r[4],
                }
                for r in cur.fetchall()
            ]

    def _has_column(self, table_name: str, column_name: str) -> bool:
        with db.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = %s
                      AND column_name = %s
                )
            """, (table_name, column_name))
            return bool(cur.fetchone()[0])

    def get_membership_plans(self):
        with db.cursor() as cur:
            has_prepaid_cols = (
                self._has_column("membership_plans", "is_prepaid_months")
                and self._has_column("membership_plans", "prepaid_months_count")
            )
            has_discount_cols = (
                self._has_column("membership_plans", "discount")
                and self._has_column("membership_plans", "discount_type")
            )
            if has_prepaid_cols and has_discount_cols:
                cur.execute("""
                    SELECT
                        id,
                        name,
                        monthly_fee,
                        COALESCE(is_prepaid_months, false) AS is_prepaid_months,
                        COALESCE(prepaid_months_count, 1) AS prepaid_months_count,
                        COALESCE(plan_type, 'individual') AS plan_type,
                        COALESCE(discount, 0) AS discount,
                        COALESCE(discount_type, 'amount') AS discount_type
                    FROM membership_plans
                    ORDER BY name
                """)
            elif has_prepaid_cols:
                cur.execute("""
                    SELECT
                        id,
                        name,
                        monthly_fee,
                        COALESCE(is_prepaid_months, false) AS is_prepaid_months,
                        COALESCE(prepaid_months_count, 1) AS prepaid_months_count,
                        COALESCE(plan_type, 'individual') AS plan_type,
                        0 AS discount,
                        'amount' AS discount_type
                    FROM membership_plans
                    ORDER BY name
                """)
            elif has_discount_cols:
                cur.execute("""
                    SELECT
                        id,
                        name,
                        monthly_fee,
                        false AS is_prepaid_months,
                        1 AS prepaid_months_count,
                        COALESCE(plan_type, 'individual') AS plan_type,
                        COALESCE(discount, 0) AS discount,
                        COALESCE(discount_type, 'amount') AS discount_type
                    FROM membership_plans
                    ORDER BY name
                """)
            else:
                cur.execute("""
                    SELECT
                        id,
                        name,
                        monthly_fee,
                        false AS is_prepaid_months,
                        1 AS prepaid_months_count,
                        COALESCE(plan_type, 'individual') AS plan_type,
                        0 AS discount,
                        'amount' AS discount_type
                    FROM membership_plans
                    ORDER BY name
                """)
            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "price": float(r[2]) if r[2] else 0.0,
                    "is_prepaid_months": bool(r[3]),
                    "prepaid_months_count": min(max(int(r[4] or 1), 1), 12),
                    "plan_type": r[5],
                    "discount": float(r[6]) if r[6] else 0.0,
                    "discount_type": r[7] or "amount",
                }
                for r in cur.fetchall()
            ]

    def get_inventory_products(self):
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, name, COALESCE(sale_price, 0), COALESCE(stock, 0)
                FROM products
                WHERE COALESCE(stock, 0) > 0
                ORDER BY name
            """)
            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "price": float(r[2]) if r[2] else 0.0,
                    "stock": r[3],
                }
                for r in cur.fetchall()
            ]

    def get_services(self):
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, name, COALESCE(price, 0)
                FROM services
                WHERE is_active = true
                ORDER BY name
            """)
            return [
                {"id": r[0], "name": r[1], "price": float(r[2]) if r[2] else 0.0}
                for r in cur.fetchall()
            ]

    def get_open_receivables(self, search=""):
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, debtor_name, pending_amount
                FROM finance_receivables
                WHERE status IN ('open', 'partial')
                    AND (%s = '' OR LOWER(debtor_name) LIKE %s)
                ORDER BY debtor_name
                LIMIT 30
            """, (search, f"%{search}%"))
            return [
                {
                    "id": r[0],
                    "debtor_name": r[1],
                    "pending_amount": float(r[2]) if r[2] else 0.0,
                }
                for r in cur.fetchall()
            ]

    def get_payment_methods(self):
        with db.cursor() as cur:
            cur.execute("SELECT id, name FROM payment_method ORDER BY name")
            return [{"id": r[0], "name": r[1]} for r in cur.fetchall()]

    def get_destination_accounts(self):
        with db.cursor() as cur:
            cur.execute("SELECT id, name, COALESCE(account_number, '') FROM destination_account ORDER BY name")
            return [
                {"id": r[0], "name": r[1], "account_number": r[2]}
                for r in cur.fetchall()
            ]

    def delete(self, income_id):
        return self.delete_income(income_id)

    def delete_income(self, income_id):
        with db.transaction() as cur:
            items = self.get_income_items(income_id)
            for item in items:
                if item["item_type"] in ("inventory", "inventory_product") and item["reference_id"]:
                    cur.execute("""
                        UPDATE products SET stock = stock + %s WHERE id = %s
                    """, (item["quantity"], item["reference_id"]))

            cur.execute("""
                DELETE FROM finance_receivables WHERE source_income_id = %s
            """, (income_id,))

            cur.execute("""
                DELETE FROM finance_income WHERE id = %s
            """, (income_id,))

    def update_receipt_info(self, income_id, receipt_number, receipt_pdf_path):
        with db.transaction() as cur:
            cur.execute("""
                UPDATE finance_income SET
                    receipt_number = %s,
                    receipt_pdf_path = %s,
                    receipt_generated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (receipt_number, receipt_pdf_path, income_id))

    def duplicate_income(self, income_id):
        original = self.get_by_id(income_id)
        if not original:
            return None
        items = self.get_income_items(income_id)
        participants = self.get_income_participants(income_id)
        note = original.get("note", "") or ""
        if note:
            note += " "
        note += f"(Duplicado de #{income_id})"
        data = {
            "payer_name": original["payer_name"],
            "payer_type": original["payer_type"],
            "income_date": original["income_date"],
            "subtotal": original["subtotal"],
            "discount": original["discount"],
            "total": original["total"],
            "total_paid": original["total_paid"],
            "pending_amount": original["pending_amount"],
            "status": original["status"],
            "note": note,
            "agreement_note": original.get("agreement_note", ""),
            "payer_person_id": original.get("payer_person_id"),
            "payer_document": original.get("payer_document", ""),
            "payer_email": original.get("payer_email", ""),
            "payer_phone": original.get("payer_phone", ""),
            "payment_method_id": original.get("payment_method_id"),
            "destination_account_id": original.get("destination_account_id"),
            "items": [
                {
                    "name": i["name"],
                    "quantity": i["quantity"],
                    "unit_price": i["unit_price"],
                    "discount": i["discount"],
                    "subtotal": i["subtotal"],
                    "item_type": i["item_type"],
                    "reference_id": i.get("reference_id"),
                    "details": i.get("details", ""),
                }
                for i in items
            ],
            "participants": [
                {
                    "display_name": p["display_name"],
                    "expected_amount": p["expected_amount"],
                    "paid_amount": p["paid_amount"],
                    "pending_amount": p["pending_amount"],
                    "due_date": p.get("due_date"),
                    "person_id": p.get("person_id"),
                }
                for p in participants
            ],
        }
        return self.create_income(data)
