from database.connection import db


class ServicesRepository:

    def get_all(self) -> list:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    id,
                    name,
                    COALESCE(description, ''),
                    COALESCE(price, 0),
                    COALESCE(icon, '🚀'),
                    COALESCE(accent_color, '#3B82F6'),
                    COALESCE(is_active, true)
                FROM services
                WHERE is_active = true
                ORDER BY name
            """)
            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "description": r[2],
                    "price": float(r[3]) if r[3] else 0.0,
                    "icon": r[4],
                    "accent_color": r[5],
                    "is_active": bool(r[6]),
                }
                for r in cur.fetchall()
            ]

    def create_service(self, name, description="", price=0, icon="🚀", accent_color="#3B82F6", is_active=True):
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO services (name, description, price, icon, accent_color, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (name, description, price, icon, accent_color, is_active))
            return cur.fetchone()[0]

    def update_service(self, service_id, name, description="", price=0, icon="🚀", accent_color="#3B82F6", is_active=True):
        with db.transaction() as cur:
            cur.execute("""
                UPDATE services
                SET name = %s, description = %s, price = %s, icon = %s,
                    accent_color = %s, is_active = %s
                WHERE id = %s
            """, (name, description, price, icon, accent_color, is_active, service_id))

    def delete_service(self, service_id: int):
        with db.transaction() as cur:
            cur.execute("""
                UPDATE services SET is_active = false WHERE id = %s
            """, (service_id,))
