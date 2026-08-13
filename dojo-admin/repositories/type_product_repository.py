from database.connection import db


class TypeProductRepository:

    def get_all(self) -> list:
        with db.cursor() as cur:
            cur.execute("SELECT id, name FROM type_products ORDER BY name")
            return [{"id": r[0], "name": r[1]} for r in cur.fetchall()]

    def create(self, name: str):
        with db.transaction() as cur:
            cur.execute("INSERT INTO type_products (name) VALUES (%s)", (name,))

    def update(self, type_id: int, name: str):
        with db.transaction() as cur:
            cur.execute("UPDATE type_products SET name = %s WHERE id = %s", (name, type_id))

    def delete(self, type_id: int):
        with db.transaction() as cur:
            cur.execute("DELETE FROM type_products WHERE id = %s", (type_id,))
