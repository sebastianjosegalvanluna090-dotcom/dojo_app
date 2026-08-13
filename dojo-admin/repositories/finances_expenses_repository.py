# _____________finances_expenses_repository.py_____________

from database.connection import db


class FinancesExpensesRepository:

    def get_all(self, search="", expense_type=None):
        with db.cursor() as cur:
            conditions = ["(%s = '' OR LOWER(fe.description) LIKE %s)"]
            params = [search, f"%{search}%"]

            if expense_type in ("fixed", "variable"):
                conditions.append("fe.expense_type = %s")
                params.append(expense_type)

            where = " AND ".join(conditions)
            cur.execute(f"""
                SELECT
                    fe.id,
                    fe.expense_date,
                    fe.description,
                    fe.category_id,
                    fe.subcategory_id,
                    fe.amount,
                    fe.payment_method_id,
                    fe.affects_inventory,
                    fe.expense_type,
                    fe.created_at,
                    COALESCE(fec.name, '') AS category_name,
                    COALESCE(fes.name, '') AS subcategory_name
                FROM finance_expenses fe
                LEFT JOIN finance_expense_categories fec ON fec.id = fe.category_id
                LEFT JOIN finance_expense_subcategories fes ON fes.id = fe.subcategory_id
                WHERE {where}
                ORDER BY fe.expense_date DESC
            """, tuple(params))
            return [
                {
                    "id": r[0],
                    "expense_date": r[1],
                    "description": r[2],
                    "category_id": r[3],
                    "subcategory_id": r[4],
                    "amount": float(r[5]) if r[5] else 0.0,
                    "payment_method_id": r[6],
                    "affects_inventory": bool(r[7]),
                    "expense_type": r[8] or "variable",
                    "created_at": r[9],
                    "category_name": r[10],
                    "subcategory_name": r[11],
                }
                for r in cur.fetchall()
            ]

    def get_categories(self, expense_type=None):
        with db.cursor() as cur:
            if expense_type in ("fixed", "variable"):
                cur.execute("""
                    SELECT id, name, description, expense_type
                    FROM finance_expense_categories
                    WHERE expense_type = %s
                    ORDER BY name
                """, (expense_type,))
            else:
                cur.execute("""
                    SELECT id, name, description, expense_type
                    FROM finance_expense_categories
                    ORDER BY name
                """)
            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "description": r[2] or "",
                    "expense_type": r[3] or "variable",
                }
                for r in cur.fetchall()
            ]

    def get_subcategories(self, category_id):
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, name, description
                FROM finance_expense_subcategories
                WHERE category_id = %s
                ORDER BY name
            """, (category_id,))
            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "description": r[2] or "",
                }
                for r in cur.fetchall()
            ]

    def create_category(self, name, description="", expense_type="variable"):
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO finance_expense_categories (name, description, expense_type)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (name, description, expense_type))
            return cur.fetchone()[0]

    def create_subcategory(self, category_id, name, description=""):
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO finance_expense_subcategories (category_id, name, description)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (category_id, name, description))
            return cur.fetchone()[0]

    def update_category(self, cat_id, name, description="", expense_type="variable"):
        with db.transaction() as cur:
            cur.execute("""
                UPDATE finance_expense_categories
                SET name = %s, description = %s, expense_type = %s
                WHERE id = %s
            """, (name, description, expense_type, cat_id))

    def update_subcategory(self, sub_id, name, description=""):
        with db.transaction() as cur:
            cur.execute("""
                UPDATE finance_expense_subcategories
                SET name = %s, description = %s
                WHERE id = %s
            """, (name, description, sub_id))

    def delete_category(self, cat_id):
        with db.transaction() as cur:
            cur.execute("""
                DELETE FROM finance_expense_categories WHERE id = %s
            """, (cat_id,))

    def delete_subcategory(self, sub_id):
        with db.transaction() as cur:
            cur.execute("""
                DELETE FROM finance_expense_subcategories WHERE id = %s
            """, (sub_id,))

    def create_expense(self, data):
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO finance_expenses (
                    expense_date, description, category_id, subcategory_id,
                    amount, payment_method_id, affects_inventory, expense_type
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data.get("expense_date"),
                data.get("description"),
                data.get("category_id"),
                data.get("subcategory_id"),
                data.get("amount", 0),
                data.get("payment_method_id"),
                bool(data.get("affects_inventory", False)),
                data.get("expense_type", "variable"),
            ))
            expense_id = cur.fetchone()[0]

            if data.get("affects_inventory") and data.get("inventory_items"):
                for item in data["inventory_items"]:
                    cur.execute("""
                        INSERT INTO finance_expense_inventory_items (expense_id, product_id, quantity, unit_cost, total_cost)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        expense_id,
                        item.get("product_id"),
                        item.get("quantity", 1),
                        item.get("unit_cost", 0),
                        item.get("total_cost", 0),
                    ))

                    cur.execute("""
                        UPDATE products SET stock = stock + %s WHERE id = %s
                    """, (item.get("quantity", 1), item.get("product_id")))

            return expense_id

    def get_expense_inventory_items(self, expense_id):
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, expense_id, product_id, quantity, unit_cost, total_cost
                FROM finance_expense_inventory_items
                WHERE expense_id = %s
                ORDER BY id
            """, (expense_id,))
            return [
                {
                    "id": r[0],
                    "expense_id": r[1],
                    "product_id": r[2],
                    "quantity": r[3],
                    "unit_cost": float(r[4]) if r[4] else 0.0,
                    "total_cost": float(r[5]) if r[5] else 0.0,
                }
                for r in cur.fetchall()
            ]

    def delete_expense(self, expense_id):
        with db.transaction() as cur:
            items = self.get_expense_inventory_items(expense_id)
            for item in items:
                cur.execute("""
                    UPDATE products SET stock = stock - %s WHERE id = %s
                """, (item["quantity"], item["product_id"]))

            cur.execute("""
                DELETE FROM finance_expenses WHERE id = %s
            """, (expense_id,))
