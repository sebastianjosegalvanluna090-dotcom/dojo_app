from database.connection import db


class MembershipCategoryRepository:

    def get_all(self) -> list:
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, name
                FROM membership_categories
                ORDER BY name
            """)
            return [{"id": r[0], "name": r[1]} for r in cur.fetchall()]

    def create(self, name: str):
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO membership_categories (name)
                VALUES (%s)
            """, (name,))

    def update(self, category_id: int, name: str):
        with db.transaction() as cur:
            cur.execute("""
                UPDATE membership_categories
                SET name = %s
                WHERE id = %s
            """, (name, category_id))

    def delete(self, category_id: int):
        with db.transaction() as cur:
            cur.execute("""
                DELETE FROM membership_categories
                WHERE id = %s
            """, (category_id,))
