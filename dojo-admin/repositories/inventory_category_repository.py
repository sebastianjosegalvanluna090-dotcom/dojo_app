from database.connection import db


class InventoryCategoryRepository:

    def get_all(self) -> list:
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, name
                FROM inventory_categories
                ORDER BY name
            """)
            return [{"id": r[0], "name": r[1]} for r in cur.fetchall()]

    def get_all_with_product_count(self) -> list:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    ic.id,
                    ic.name,
                    COUNT(p.id) AS product_count
                FROM inventory_categories ic
                LEFT JOIN products p ON p.id_inventory_category = ic.id
                GROUP BY ic.id, ic.name
                ORDER BY ic.name
            """)
            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "product_count": r[2],
                }
                for r in cur.fetchall()
            ]

    def create(self, name: str):
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO inventory_categories (name)
                VALUES (%s)
            """, (name,))

    def update(self, category_id: int, name: str):
        with db.transaction() as cur:
            cur.execute("""
                UPDATE inventory_categories
                SET name = %s
                WHERE id = %s
            """, (name, category_id))

    def delete(self, category_id: int):
        with db.transaction() as cur:
            cur.execute("""
                SELECT COUNT(*)
                FROM products
                WHERE id_inventory_category = %s
            """, (category_id,))
            count = cur.fetchone()[0]

            if count > 0:
                raise ValueError("No se puede eliminar una categoría con productos asociados.")

            cur.execute("""
                DELETE FROM inventory_categories
                WHERE id = %s
            """, (category_id,))
