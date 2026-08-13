# repositories/account_repository.py
# Repositorio de cuenta de usuario — lee y actualiza datos del usuario
# activo conectando las tablas users ↔ people.

from database.connection import db
from core.app_logger import get_logger

logger = get_logger("account_repository")

DEFAULT_NOTIFICATION_PREFERENCES = {
    "classes_enabled": True,
    "classes_in_app": True,
    "classes_windows": True,
    "classes_minutes_before": 15,
    "classes_notify_at_start": True,
    "events_enabled": True,
    "events_in_app": True,
    "events_windows": True,
    "events_minutes_before": 1440,
    "events_notify_at_start": True,
}


class AccountRepository:
    """
    Contrato de datos que usa AccountView:

    get_account(user_id) → dict con:
        id, username, is_active, created_at,
        security_pin_enabled, two_factor_sms, two_factor_app (users)
        first_name, last_name, email, phone, birthdate,
        address_line, residence_city, residence_country,
        birth_city, birth_country, neighborhood,
        socioeconomic_stratum, profession, residence_details,
        photo_path, id_document_type, document  (people)

    update_profile(user_id, data) → None
    update_password(user_id, new_hash) → None
    """

    # ─────────────────────────────────────────────────────────────
    # Lectura
    # ─────────────────────────────────────────────────────────────
    def get_account(self, user_id: int) -> dict:
        """
        Retorna todos los datos del usuario y su persona asociada.
        Devuelve un dict vacío si no se encuentra.
        """
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("""
                    SELECT
                        u.id,
                        u.username,
                        u.is_active,
                        u.created_at,
                        u.security_pin_enabled,
                        u.two_factor_sms,
                        u.two_factor_app,
                        p.id          AS person_id,
                        p.first_name,
                        p.last_name,
                        p.email,
                        p.phone,
                        p.birthdate,
                        p.address_line,
                        p.residence_city,
                        p.residence_country,
                        p.birth_city,
                        p.birth_country,
                        p.neighborhood,
                        p.socioeconomic_stratum,
                        p.profession,
                        p.residence_details,
                        p.photo_path,
                        p.id_document_type,
                        p.document
                    FROM users u
                    LEFT JOIN people p ON p.id = u.id_person
                    WHERE u.id = %s
                    LIMIT 1;
                """, (user_id,))
                cols = [
                    "id", "username", "is_active", "created_at",
                    "security_pin_enabled", "two_factor_sms", "two_factor_app",
                    "person_id", "first_name", "last_name", "email",
                    "phone", "birthdate", "address_line",
                    "residence_city", "residence_country",
                    "birth_city", "birth_country", "neighborhood",
                    "socioeconomic_stratum", "profession",
                    "residence_details", "photo_path",
                    "id_document_type", "document",
                ]
            except Exception:
                cur.execute("""
                    SELECT
                        u.id,
                        u.username,
                        u.is_active,
                        u.created_at,
                        p.id          AS person_id,
                        p.first_name,
                        p.last_name,
                        p.email,
                        p.phone,
                        p.birthdate,
                        p.address_line,
                        p.residence_city,
                        p.residence_country,
                        p.birth_city,
                        p.birth_country,
                        p.neighborhood,
                        p.socioeconomic_stratum,
                        p.profession,
                        p.residence_details,
                        p.photo_path
                    FROM users u
                    LEFT JOIN people p ON p.id = u.id_person
                    WHERE u.id = %s
                    LIMIT 1;
                """, (user_id,))
                cols = [
                    "id", "username", "is_active", "created_at",
                    "person_id", "first_name", "last_name", "email",
                    "phone", "birthdate", "address_line",
                    "residence_city", "residence_country",
                    "birth_city", "birth_country", "neighborhood",
                    "socioeconomic_stratum", "profession",
                    "residence_details", "photo_path",
                ]

            row = cur.fetchone()
            if not row:
                return {}

            return dict(zip(cols, row))

        finally:
            cur.close()
            db.release(conn)

    # ─────────────────────────────────────────────────────────────
    # Actualizar perfil (tabla people)
    # ─────────────────────────────────────────────────────────────
    def update_profile(self, user_id: int, data: dict) -> None:
        """
        Actualiza los campos de people para el usuario dado.
        Solo toca las columnas que vienen en data.

        data keys (todos opcionales):
            first_name, last_name, email, phone, birthdate,
            address_line, residence_city, residence_country,
            birth_city, birth_country, neighborhood,
            socioeconomic_stratum, profession, residence_details,
            photo_path
        """
        allowed = {
            "first_name", "last_name", "email", "phone", "birthdate",
            "address_line", "residence_city", "residence_country",
            "birth_city", "birth_country", "neighborhood",
            "socioeconomic_stratum", "profession", "residence_details",
            "photo_path",
        }

        fields = {k: v for k, v in data.items() if k in allowed}
        if not fields:
            return

        set_clause = ", ".join(f"{col} = %s" for col in fields)
        values = list(fields.values())

        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute(f"""
                UPDATE people
                SET {set_clause}
                WHERE id = (
                    SELECT id_person FROM users WHERE id = %s LIMIT 1
                );
            """, values + [user_id])
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            db.release(conn)

    # ─────────────────────────────────────────────────────────────
    # Actualizar contraseña (tabla users)
    # ─────────────────────────────────────────────────────────────
    def update_password(self, user_id: int, new_password_hash: str) -> None:
        """
        Guarda el nuevo hash de contraseña.
        El hashing debe hacerse ANTES de llamar a este método.
        """
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE users
                SET password_hash = %s
                WHERE id = %s;
            """, (new_password_hash, user_id))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            db.release(conn)

    # ─────────────────────────────────────────────────────────────
    # Verificar contraseña actual (para el flujo de cambio)
    # ─────────────────────────────────────────────────────────────
    def get_password_hash(self, user_id: int) -> str | None:
        """
        Devuelve el hash almacenado para verificarlo antes de
        permitir el cambio de contraseña.
        """
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT password_hash
                FROM users
                WHERE id = %s
                LIMIT 1;
            """, (user_id,))
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            cur.close()
            db.release(conn)

    # ─────────────────────────────────────────────────────────────
    # Configuración de seguridad (tabla users)
    # ─────────────────────────────────────────────────────────────
    def update_security_settings(self, user_id: int, data: dict) -> None:
        """
        Actualiza campos de seguridad en users.
        data keys: two_factor_sms, two_factor_app,
                   security_pin_enabled, security_pin_hash (ya hasheado),
                   security_word
        """
        allowed = {
            "two_factor_sms", "two_factor_app",
            "security_pin_enabled", "security_pin_hash", "security_word"
        }
        fields = {k: v for k, v in data.items() if k in allowed}
        if not fields:
            return
        set_clause = ", ".join(f"{col} = %s" for col in fields)
        values = list(fields.values())
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                f"UPDATE users SET {set_clause} WHERE id = %s;",
                values + [user_id]
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            db.release(conn)

    def get_security_word(self, user_id: int) -> str | None:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT security_word FROM users WHERE id = %s LIMIT 1;",
                (user_id,)
            )
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            cur.close()
            db.release(conn)

    def verify_pin(self, user_id: int, pin_hash: str) -> bool:
        conn = db.get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT security_pin_hash FROM users WHERE id = %s LIMIT 1;",
                (user_id,)
            )
            row = cur.fetchone()
            return row[0] == pin_hash if row and row[0] else False
        finally:
            cur.close()
            db.release(conn)

    # ─────────────────────────────────────────────────────────────
    # Preferencias de notificación por usuario
    # ─────────────────────────────────────────────────────────────
    def get_notification_preferences(self, user_id):
        try:
            with db.cursor() as cur:
                cur.execute("""
                    SELECT
                        classes_enabled,
                        classes_in_app,
                        classes_windows,
                        classes_minutes_before,
                        classes_notify_at_start,
                        events_enabled,
                        events_in_app,
                        events_windows,
                        events_minutes_before,
                        events_notify_at_start
                    FROM user_notification_preferences
                    WHERE user_id = %s
                """, (int(user_id),))

                row = cur.fetchone()

                if row is None:
                    return dict(DEFAULT_NOTIFICATION_PREFERENCES)

                return {
                    "classes_enabled": bool(row[0]),
                    "classes_in_app": bool(row[1]),
                    "classes_windows": bool(row[2]),
                    "classes_minutes_before": int(row[3]),
                    "classes_notify_at_start": bool(row[4]),
                    "events_enabled": bool(row[5]),
                    "events_in_app": bool(row[6]),
                    "events_windows": bool(row[7]),
                    "events_minutes_before": int(row[8]),
                    "events_notify_at_start": bool(row[9]),
                }

        except Exception:
            logger.exception(
                "Error cargando preferencias de notificaciones del usuario %s",
                user_id,
            )
            return dict(DEFAULT_NOTIFICATION_PREFERENCES)

    def save_notification_preferences(self, user_id, preferences):
        allowed_class_minutes = {5, 10, 15, 30, 60}
        allowed_event_minutes = {
            15, 30, 60, 180, 720, 1440, 2880, 10080,
        }

        class_minutes = int(
            preferences.get("classes_minutes_before", 15)
        )
        event_minutes = int(
            preferences.get("events_minutes_before", 1440)
        )

        if class_minutes not in allowed_class_minutes:
            raise ValueError("Tiempo de clases invalido")

        if event_minutes not in allowed_event_minutes:
            raise ValueError("Tiempo de eventos invalido")

        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO user_notification_preferences (
                    user_id,
                    classes_enabled,
                    classes_in_app,
                    classes_windows,
                    classes_minutes_before,
                    classes_notify_at_start,
                    events_enabled,
                    events_in_app,
                    events_windows,
                    events_minutes_before,
                    events_notify_at_start,
                    updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id)
                DO UPDATE SET
                    classes_enabled = EXCLUDED.classes_enabled,
                    classes_in_app = EXCLUDED.classes_in_app,
                    classes_windows = EXCLUDED.classes_windows,
                    classes_minutes_before = EXCLUDED.classes_minutes_before,
                    classes_notify_at_start = EXCLUDED.classes_notify_at_start,
                    events_enabled = EXCLUDED.events_enabled,
                    events_in_app = EXCLUDED.events_in_app,
                    events_windows = EXCLUDED.events_windows,
                    events_minutes_before = EXCLUDED.events_minutes_before,
                    events_notify_at_start = EXCLUDED.events_notify_at_start,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                int(user_id),
                bool(preferences.get("classes_enabled", True)),
                bool(preferences.get("classes_in_app", True)),
                bool(preferences.get("classes_windows", True)),
                class_minutes,
                bool(preferences.get("classes_notify_at_start", True)),
                bool(preferences.get("events_enabled", True)),
                bool(preferences.get("events_in_app", True)),
                bool(preferences.get("events_windows", True)),
                event_minutes,
                bool(preferences.get("events_notify_at_start", True)),
            ))

        logger.info(
            "Preferencias de notificaciones guardadas para usuario %s",
            user_id,
        )
        return True
