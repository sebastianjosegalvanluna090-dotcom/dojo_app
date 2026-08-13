from database.connection import db


MEMBERSHIP_COLUMNS_SQL = """
    mp.id,
    mp.name,
    COALESCE(mp.plan_type, 'individual') AS plan_type,
    mp.weekly_classes,
    COALESCE(mp.is_unlimited, false) AS is_unlimited,
    mp.monthly_fee,
    COALESCE(mp.discount, 0),
    COALESCE(mp.description, ''),
    COALESCE(mp.benefits, ''),
    COALESCE(mp.group_capacity, 1) AS group_capacity,
    COALESCE(mp.discount_type, 'percent') AS discount_type
"""

PREPAID_COLUMNS_SQL = """
    COALESCE(mp.is_prepaid_months, false) AS is_prepaid_months,
    COALESCE(mp.prepaid_months_count, 1) AS prepaid_months_count
"""

PREPAID_FALLBACK_SQL = """
    false AS is_prepaid_months,
    1 AS prepaid_months_count
"""


class MembershipsRepository:

    @staticmethod
    def _has_column(table_name: str, column_name: str) -> bool:
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

    def get_all(self) -> list:
        has_prepaid = self._has_prepaid_columns()
        prepaid_cols = PREPAID_COLUMNS_SQL if has_prepaid else PREPAID_FALLBACK_SQL
        sql = (
            "SELECT " + MEMBERSHIP_COLUMNS_SQL + ", "
            + prepaid_cols
            + " FROM membership_plans mp"
            + " ORDER BY mp.plan_type, mp.monthly_fee, mp.name"
        )
        with db.cursor() as cur:
            cur.execute(sql)
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "plan_type": row[2],
                    "weekly_classes": row[3],
                    "is_unlimited": bool(row[4]),
                    "monthly_fee": float(row[5]) if row[5] else 0.0,
                    "discount": float(row[6]) if row[6] else 0.0,
                    "description": row[7],
                    "benefits": row[8],
                    "group_capacity": int(row[9]) if row[9] else 1,
                    "discount_type": row[10],
                    "is_prepaid_months": bool(row[11]),
                    "prepaid_months_count": int(row[12]) if row[12] else 1,
                }
                for row in cur.fetchall()
            ]

    def get_by_id(self, plan_id: int) -> dict | None:
        has_prepaid = self._has_prepaid_columns()
        prepaid_cols = PREPAID_COLUMNS_SQL if has_prepaid else PREPAID_FALLBACK_SQL
        sql = (
            "SELECT " + MEMBERSHIP_COLUMNS_SQL + ", "
            + prepaid_cols
            + " FROM membership_plans mp"
            + " WHERE mp.id = %s"
        )
        with db.cursor() as cur:
            cur.execute(sql, (plan_id,))
            row = cur.fetchone()
            if row is None:
                return None
            return {
                "id": row[0],
                "name": row[1],
                "plan_type": row[2],
                "weekly_classes": row[3],
                "is_unlimited": bool(row[4]),
                "monthly_fee": float(row[5]) if row[5] else 0.0,
                "discount": float(row[6]) if row[6] else 0.0,
                "description": row[7],
                "benefits": row[8],
                "group_capacity": int(row[9]) if row[9] else 1,
                "discount_type": row[10],
                "is_prepaid_months": bool(row[11]),
                "prepaid_months_count": int(row[12]) if row[12] else 1,
            }

    def get_membership_categories(self) -> list:
        with db.cursor() as cur:
            cur.execute("SELECT id, name FROM membership_categories ORDER BY name")
            return [{"id": r[0], "name": r[1]} for r in cur.fetchall()]

    def _has_prepaid_columns(self) -> bool:
        return (
            self._has_column("membership_plans", "is_prepaid_months")
            and self._has_column("membership_plans", "prepaid_months_count")
        )

    def create_plan(self, name: str, plan_type: str,
                    weekly_classes, is_unlimited: bool, monthly_fee: float,
                    discount: float,
                    description: str, benefits: str,
                    group_capacity: int = 1,
                    discount_type: str = "percent",
                    is_prepaid_months: bool = False,
                    prepaid_months_count: int = 1) -> int:
        if plan_type != "individual":
            is_prepaid_months = False
            prepaid_months_count = 1
        has_prepaid = self._has_prepaid_columns()
        cols = ("name, plan_type, weekly_classes, is_unlimited, monthly_fee, "
                "discount, discount_by_person, description, benefits, "
                "group_capacity, discount_type")
        vals = "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
        params = [name, plan_type, weekly_classes, is_unlimited, monthly_fee,
                  discount, False, description, benefits, group_capacity,
                  discount_type]
        if has_prepaid:
            cols += ", is_prepaid_months, prepaid_months_count"
            vals += ", %s, %s"
            params.extend([is_prepaid_months, prepaid_months_count])
        sql = "INSERT INTO membership_plans (" + cols + ") VALUES (" + vals + ") RETURNING id"
        with db.transaction() as cur:
            cur.execute(sql, params)
            return cur.fetchone()[0]

    def update_plan(self, plan_id: int, name: str, plan_type: str,
                    weekly_classes, is_unlimited: bool, monthly_fee: float,
                    discount: float,
                    description: str, benefits: str,
                    group_capacity: int = 1,
                    discount_type: str = "percent",
                    is_prepaid_months: bool = False,
                    prepaid_months_count: int = 1):
        if plan_type != "individual":
            is_prepaid_months = False
            prepaid_months_count = 1
        has_prepaid = self._has_prepaid_columns()
        set_clause = ("name = %s, plan_type = %s, weekly_classes = %s, "
                      "is_unlimited = %s, monthly_fee = %s, discount = %s, "
                      "discount_by_person = %s, description = %s, benefits = %s, "
                      "group_capacity = %s, discount_type = %s")
        params = [name, plan_type, weekly_classes, is_unlimited, monthly_fee,
                  discount, False, description, benefits, group_capacity,
                  discount_type]
        if has_prepaid:
            set_clause += ", is_prepaid_months = %s, prepaid_months_count = %s"
            params.extend([is_prepaid_months, prepaid_months_count])
        params.append(plan_id)
        sql = "UPDATE membership_plans SET " + set_clause + " WHERE id = %s"
        with db.transaction() as cur:
            cur.execute(sql, params)

    def delete_plan(self, plan_id: int):
        with db.transaction() as cur:
            cur.execute("DELETE FROM membership_plans WHERE id = %s", (plan_id,))
