from database.connection import db


class InventoryRepository:

    def get_all(self, search: str = "") -> list:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    p.id,
                    p.name,
                    COALESCE(ic.name, 'Sin categoría') AS category_name,
                    p.id_inventory_category,
                    COALESCE(p.stock, 0),
                    COALESCE(p.cost_price, 0),
                    COALESCE(p.sale_price, 0),
                    COALESCE(p.image_path, '') AS image_path,
                    p.id_type_product
                FROM products p
                LEFT JOIN inventory_categories ic ON ic.id = p.id_inventory_category
                WHERE (%s = '' OR LOWER(p.name) LIKE %s OR LOWER(COALESCE(ic.name, '')) LIKE %s)
                ORDER BY p.name
            """, (search, f"%{search}%", f"%{search}%"))
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "category_name": row[2],
                    "id_inventory_category": row[3],
                    "stock": row[4],
                    "cost_price": float(row[5]) if row[5] else 0.0,
                    "sale_price": float(row[6]) if row[6] else 0.0,
                    "image_path": row[7],
                    "id_type_product": row[8],
                }
                for row in cur.fetchall()
            ]

    def get_inventory_categories(self) -> list:
        with db.cursor() as cur:
            cur.execute("SELECT id, name FROM inventory_categories ORDER BY name")
            return [{"id": r[0], "name": r[1]} for r in cur.fetchall()]

    def get_product_purchase_history(self, product_id: int, limit: int = 10) -> list:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    id,
                    buyer_name,
                    purchase_date,
                    quantity,
                    total_price,
                    note
                FROM product_purchase_history
                WHERE id_product = %s
                ORDER BY purchase_date DESC
                LIMIT %s
            """, (product_id, limit))
            return [
                {
                    "id": r[0],
                    "buyer_name": r[1],
                    "purchase_date": r[2],
                    "quantity": r[3],
                    "total_price": float(r[4]) if r[4] else 0.0,
                    "note": r[5] or "",
                }
                for r in cur.fetchall()
            ]

    def get_type_products(self) -> list:
        with db.cursor() as cur:
            cur.execute("SELECT id, name FROM type_products ORDER BY name")
            return [{"id": r[0], "name": r[1]} for r in cur.fetchall()]

    def create_product(self, id_inventory_category: int, name: str, cost_price: float, sale_price: float, stock: int, image_path: str = "", id_type_product: int = 1) -> int:
        with db.transaction() as cur:
            cur.execute(
                "INSERT INTO products (id_inventory_category, name, cost_price, sale_price, stock, image_path, id_type_product) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (id_inventory_category, name, cost_price, sale_price, stock, image_path, id_type_product)
            )
            return cur.fetchone()[0]

    def update_product(self, product_id: int, id_inventory_category: int, name: str, cost_price: float, sale_price: float, stock: int, image_path: str = "", id_type_product: int = 1):
        with db.transaction() as cur:
            cur.execute(
                "UPDATE products SET id_inventory_category = %s, name = %s, cost_price = %s, sale_price = %s, stock = %s, image_path = %s, id_type_product = %s WHERE id = %s",
                (id_inventory_category, name, cost_price, sale_price, stock, image_path, id_type_product, product_id)
            )

    def delete_product(self, product_id: int):
        with db.transaction() as cur:
            cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
