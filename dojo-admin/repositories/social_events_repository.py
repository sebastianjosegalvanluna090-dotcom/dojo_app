# ─── SOCIAL_EVENTS_REPOSITORY ───────────────────────────────────────

from database.connection import db
from core.debug import debug_log


def _row_to_dict(row, columns):
    """Convert a database row to a dict."""
    if row is None:
        return None
    return {col: row[i] for i, col in enumerate(columns)}


def _rows_to_dicts(rows, columns):
    """Convert multiple rows to a list of dicts."""
    return [_row_to_dict(r, columns) for r in rows]


_EVENT_COLS = [
    "id", "name", "event_date", "event_type", "description", "color",
    "start_time", "end_time", "location", "is_important",
    "short_description", "organizer_user_id", "martial_art_id",
    "end_date", "venue_name", "address", "city", "country",
    "cover_image_path", "capacity", "registration_deadline",
    "price", "status", "visibility", "is_featured",
    "registration_enabled", "published_at", "updated_at", "created_at",
]

_FOLLOWER_COLS = ["id", "event_id", "user_id", "notifications_enabled", "followed_at"]
_INTEREST_COLS = ["id", "event_id", "user_id", "response", "created_at", "updated_at"]
_REGISTRATION_COLS = [
    "id", "event_id", "user_id", "student_id", "registration_status",
    "payment_status", "notes", "registered_at", "updated_at",
]
_SCHEDULE_COLS = [
    "id", "event_id", "title", "description", "starts_at",
    "ends_at", "location", "sort_order", "created_at", "updated_at",
]
_POST_COLS = [
    "id", "event_id", "author_user_id", "content", "image_path",
    "is_pinned", "created_at", "updated_at",
]

_MAX_LIMIT = 50


def _clamp_limit(limit):
    return min(max(1, int(limit or 12)), _MAX_LIMIT)


class SocialEventsRepository:

    # ── Explore ────────────────────────────────────────────────

    def get_explore_events(
        self, search_text="", event_type=None, martial_art_id=None,
        status=None, date_filter=None, featured_only=False,
        limit=12, offset=0,
    ):
        try:
            where = [
                "e.status IN ('published','registration_open','registration_closed','in_progress','completed')"
            ]
            params = []

            if search_text:
                where.append(
                    "(e.name ILIKE %s OR e.short_description ILIKE %s "
                    "OR e.description ILIKE %s OR e.location ILIKE %s "
                    "OR e.venue_name ILIKE %s OR e.city ILIKE %s "
                    "OR e.event_type ILIKE %s)"
                )
                term = f"%{search_text}%"
                params.extend([term] * 7)

            if event_type:
                where.append("e.event_type = %s")
                params.append(event_type)

            if martial_art_id:
                where.append("e.martial_art_id = %s")
                params.append(int(martial_art_id))

            if status:
                where.append("e.status = %s")
                params.append(status)

            if date_filter == "upcoming":
                where.append("e.event_date >= CURRENT_DATE")
            elif date_filter == "this_month":
                where.append(
                    "EXTRACT(MONTH FROM e.event_date) = EXTRACT(MONTH FROM CURRENT_DATE) "
                    "AND EXTRACT(YEAR FROM e.event_date) = EXTRACT(YEAR FROM CURRENT_DATE)"
                )
            elif date_filter == "registration_open":
                where.append("e.registration_enabled = true AND e.status = 'registration_open'")

            if featured_only:
                where.append("e.is_featured = true")

            where_sql = " AND ".join(where)
            limit = _clamp_limit(limit)
            offset = max(0, int(offset or 0))

            sql = f"""
                SELECT e.id, e.name, e.event_date, e.event_type, e.description,
                       e.color, e.start_time, e.end_time, e.location, e.is_important,
                       e.short_description, e.organizer_user_id, e.martial_art_id,
                       e.end_date, e.venue_name, e.address, e.city, e.country,
                       e.cover_image_path, e.capacity, e.registration_deadline,
                       e.price, e.status, e.visibility, e.is_featured,
                       e.registration_enabled, e.published_at, e.updated_at, e.created_at,
                       COALESCE(reg.cnt, 0) AS registration_count,
                       COALESCE(fol.cnt, 0) AS follower_count
                FROM events e
                LEFT JOIN (
                    SELECT event_id, COUNT(*) AS cnt
                    FROM event_registrations
                    WHERE registration_status NOT IN ('cancelled','rejected')
                    GROUP BY event_id
                ) reg ON reg.event_id = e.id
                LEFT JOIN (
                    SELECT event_id, COUNT(*) AS cnt
                    FROM event_followers
                    GROUP BY event_id
                ) fol ON fol.event_id = e.id
                WHERE {where_sql}
                ORDER BY e.is_featured DESC, e.event_date ASC,
                         e.start_time ASC NULLS LAST, e.created_at DESC
                LIMIT %s OFFSET %s;
            """
            params.extend([limit, offset])

            with db.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

            cols = _EVENT_COLS + ["registration_count", "follower_count"]
            return _rows_to_dicts(rows, cols)

        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error en get_explore_events: {e}")
            return []

    def get_featured_event(self):
        try:
            with db.cursor() as cur:
                cur.execute("""
                    SELECT e.id, e.name, e.event_date, e.event_type, e.description,
                           e.color, e.start_time, e.end_time, e.location, e.is_important,
                           e.short_description, e.organizer_user_id, e.martial_art_id,
                           e.end_date, e.venue_name, e.address, e.city, e.country,
                           e.cover_image_path, e.capacity, e.registration_deadline,
                           e.price, e.status, e.visibility, e.is_featured,
                           e.registration_enabled, e.published_at, e.updated_at, e.created_at,
                           COALESCE(reg.cnt, 0) AS registration_count,
                           COALESCE(fol.cnt, 0) AS follower_count
                    FROM events e
                    LEFT JOIN (
                        SELECT event_id, COUNT(*) AS cnt
                        FROM event_registrations
                        WHERE registration_status NOT IN ('cancelled','rejected')
                        GROUP BY event_id
                    ) reg ON reg.event_id = e.id
                    LEFT JOIN (
                        SELECT event_id, COUNT(*) AS cnt
                        FROM event_followers
                        GROUP BY event_id
                    ) fol ON fol.event_id = e.id
                    WHERE e.is_featured = true
                      AND e.status IN ('published','registration_open','in_progress')
                      AND e.event_date >= CURRENT_DATE
                    ORDER BY e.event_date ASC
                    LIMIT 1;
                """)
                row = cur.fetchone()
            return _row_to_dict(row, _EVENT_COLS + ["registration_count", "follower_count"])
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error en get_featured_event: {e}")
            return None

    # ── Detail ─────────────────────────────────────────────────

    def get_event_detail(self, event_id, current_user_id=None):
        try:
            with db.cursor() as cur:
                cur.execute("""
                    SELECT e.id, e.name, e.event_date, e.event_type, e.description,
                           e.color, e.start_time, e.end_time, e.location, e.is_important,
                           e.short_description, e.organizer_user_id, e.martial_art_id,
                           e.end_date, e.venue_name, e.address, e.city, e.country,
                           e.cover_image_path, e.capacity, e.registration_deadline,
                           e.price, e.status, e.visibility, e.is_featured,
                           e.registration_enabled, e.published_at, e.updated_at, e.created_at,
                           COALESCE(reg.cnt, 0) AS registration_count,
                           COALESCE(fol.cnt, 0) AS follower_count,
                           COALESCE(interes.cnt, 0) AS interest_count,
                           COALESCE(interes.attending_count, 0) AS attending_count,
                           CASE WHEN fol.id IS NOT NULL THEN true ELSE false END AS is_following,
                           ei.response AS user_interest,
                           er.id AS user_registration_id,
                           er.registration_status AS user_registration_status,
                           u.username AS organizer_name
                    FROM events e
                    LEFT JOIN (
                        SELECT event_id, COUNT(*) AS cnt
                        FROM event_registrations
                        WHERE registration_status NOT IN ('cancelled','rejected')
                        GROUP BY event_id
                    ) reg ON reg.event_id = e.id
                    LEFT JOIN (
                        SELECT event_id, COUNT(*) AS cnt
                        FROM event_followers
                        GROUP BY event_id
                    ) fol ON fol.event_id = e.id
                    LEFT JOIN (
                        SELECT event_id,
                               COUNT(*) AS cnt,
                               COUNT(*) FILTER (WHERE response = 'attending') AS attending_count
                        FROM event_interest
                        GROUP BY event_id
                    ) interes ON interes.event_id = e.id
                    LEFT JOIN event_followers fol
                        ON fol.event_id = e.id AND fol.user_id = %s
                    LEFT JOIN event_interest ei
                        ON ei.event_id = e.id AND ei.user_id = %s
                    LEFT JOIN event_registrations er
                        ON er.event_id = e.id AND er.user_id = %s
                        AND er.registration_status NOT IN ('cancelled','rejected')
                    LEFT JOIN users u ON u.id = e.organizer_user_id
                    WHERE e.id = %s;
                """, (current_user_id, current_user_id, current_user_id, event_id))
                row = cur.fetchone()

            if not row:
                return None

            cols = _EVENT_COLS + [
                "registration_count", "follower_count", "interest_count",
                "attending_count", "is_following", "user_interest",
                "user_registration_id", "user_registration_status", "organizer_name",
            ]
            return _row_to_dict(row, cols)

        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error en get_event_detail: {e}")
            return None

    # ── User events ────────────────────────────────────────────

    def get_user_events(self, user_id, filter_type="all"):
        try:
            where = []
            params = [user_id]

            if filter_type == "following":
                where.append("ef.user_id = %s")
                params.append(user_id)
                join_extra = "INNER JOIN event_followers ef ON ef.event_id = e.id"
            elif filter_type == "interested":
                where.append("ei.user_id = %s AND ei.response = 'interested'")
                params.append(user_id)
                join_extra = "INNER JOIN event_interest ei ON ei.event_id = e.id"
            elif filter_type == "attending":
                where.append("ei.user_id = %s AND ei.response = 'attending'")
                params.append(user_id)
                join_extra = "INNER JOIN event_interest ei ON ei.event_id = e.id"
            elif filter_type == "registered":
                where.append("er.user_id = %s AND er.registration_status NOT IN ('cancelled','rejected')")
                params.append(user_id)
                join_extra = "INNER JOIN event_registrations er ON er.event_id = e.id"
            elif filter_type == "organized":
                where.append("e.organizer_user_id = %s")
                params.append(user_id)
                join_extra = ""
            elif filter_type == "past":
                where.append("e.event_date < CURRENT_DATE")
                join_extra = ""
            else:
                join_extra = ""

            where.insert(0, "e.status NOT IN ('draft','archived','cancelled')")
            where_sql = " AND ".join(where)

            sql = f"""
                SELECT DISTINCT e.id, e.name, e.event_date, e.event_type, e.description,
                       e.color, e.start_time, e.end_time, e.location, e.is_important,
                       e.short_description, e.organizer_user_id, e.martial_art_id,
                       e.end_date, e.venue_name, e.address, e.city, e.country,
                       e.cover_image_path, e.capacity, e.registration_deadline,
                       e.price, e.status, e.visibility, e.is_featured,
                       e.registration_enabled, e.published_at, e.updated_at, e.created_at,
                       COALESCE(reg.cnt, 0) AS registration_count,
                       COALESCE(fol.cnt, 0) AS follower_count
                FROM events e
                {join_extra}
                LEFT JOIN (
                    SELECT event_id, COUNT(*) AS cnt
                    FROM event_registrations
                    WHERE registration_status NOT IN ('cancelled','rejected')
                    GROUP BY event_id
                ) reg ON reg.event_id = e.id
                LEFT JOIN (
                    SELECT event_id, COUNT(*) AS cnt
                    FROM event_followers
                    GROUP BY event_id
                ) fol ON fol.event_id = e.id
                WHERE {where_sql}
                ORDER BY e.event_date DESC
                LIMIT 50;
            """
            with db.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()

            cols = _EVENT_COLS + ["registration_count", "follower_count"]
            return _rows_to_dicts(rows, cols)

        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error en get_user_events: {e}")
            return []

    # ── Management ─────────────────────────────────────────────

    def get_managed_events(self, organizer_user_id, status=None):
        try:
            where = ["e.organizer_user_id = %s"]
            params = [organizer_user_id]

            if status:
                where.append("e.status = %s")
                params.append(status)

            where_sql = " AND ".join(where)
            with db.cursor() as cur:
                cur.execute(f"""
                    SELECT e.id, e.name, e.event_date, e.event_type, e.description,
                           e.color, e.start_time, e.end_time, e.location, e.is_important,
                           e.short_description, e.organizer_user_id, e.martial_art_id,
                           e.end_date, e.venue_name, e.address, e.city, e.country,
                           e.cover_image_path, e.capacity, e.registration_deadline,
                           e.price, e.status, e.visibility, e.is_featured,
                           e.registration_enabled, e.published_at, e.updated_at, e.created_at,
                           COALESCE(reg.cnt, 0) AS registration_count,
                           COALESCE(fol.cnt, 0) AS follower_count
                    FROM events e
                    LEFT JOIN (
                        SELECT event_id, COUNT(*) AS cnt
                        FROM event_registrations
                        WHERE registration_status NOT IN ('cancelled','rejected')
                        GROUP BY event_id
                    ) reg ON reg.event_id = e.id
                    LEFT JOIN (
                        SELECT event_id, COUNT(*) AS cnt
                        FROM event_followers
                        GROUP BY event_id
                    ) fol ON fol.event_id = e.id
                    WHERE {where_sql}
                    ORDER BY e.event_date DESC
                    LIMIT 50;
                """, params)
                rows = cur.fetchall()

            cols = _EVENT_COLS + ["registration_count", "follower_count"]
            return _rows_to_dicts(rows, cols)
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error en get_managed_events: {e}")
            return []

    # ── CRUD ───────────────────────────────────────────────────

    def create_event(self, data):
        try:
            with db.transaction() as cur:
                cur.execute("""
                    INSERT INTO events (
                        name, event_date, event_type, description, color,
                        start_time, end_time, location, is_important,
                        short_description, organizer_user_id, martial_art_id,
                        end_date, venue_name, address, city, country,
                        cover_image_path, capacity, registration_deadline,
                        price, status, visibility, is_featured, registration_enabled,
                        published_at
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        CASE WHEN %s IN ('published','registration_open','registration_closed','in_progress')
                             THEN CURRENT_TIMESTAMP ELSE NULL END
                    )
                    RETURNING id;
                """, (
                    data.get("name"), data.get("event_date"), data.get("event_type"),
                    data.get("description"), data.get("color", "#3B82F6"),
                    data.get("start_time"), data.get("end_time"), data.get("location"),
                    bool(data.get("is_important", False)),
                    data.get("short_description"), data.get("organizer_user_id"),
                    data.get("martial_art_id"), data.get("end_date"),
                    data.get("venue_name"), data.get("address"),
                    data.get("city"), data.get("country"),
                    data.get("cover_image_path"), data.get("capacity"),
                    data.get("registration_deadline"),
                    data.get("price", 0), data.get("status", "draft"),
                    data.get("visibility", "internal"),
                    bool(data.get("is_featured", False)),
                    bool(data.get("registration_enabled", False)),
                    data.get("status", "draft"),
                ))
                new_id = cur.fetchone()[0]
                debug_log(f"[SocialEventsRepo] Evento creado: id={new_id}")
                return new_id
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error creando evento: {e}")
            return None

    def update_event(self, event_id, data):
        try:
            with db.transaction() as cur:
                cur.execute("""
                    UPDATE events SET
                        name = %s, event_date = %s, event_type = %s,
                        description = %s, color = %s, start_time = %s,
                        end_time = %s, location = %s, is_important = %s,
                        short_description = %s, martial_art_id = %s,
                        end_date = %s, venue_name = %s, address = %s,
                        city = %s, country = %s, cover_image_path = %s,
                        capacity = %s, registration_deadline = %s,
                        price = %s, status = %s, visibility = %s,
                        is_featured = %s, registration_enabled = %s,
                        updated_at = CURRENT_TIMESTAMP,
                        published_at = CASE
                            WHEN %s IN ('published','registration_open','registration_closed','in_progress')
                            AND published_at IS NULL THEN CURRENT_TIMESTAMP
                            ELSE published_at END
                    WHERE id = %s;
                """, (
                    data.get("name"), data.get("event_date"), data.get("event_type"),
                    data.get("description"), data.get("color", "#3B82F6"),
                    data.get("start_time"), data.get("end_time"), data.get("location"),
                    bool(data.get("is_important", False)),
                    data.get("short_description"), data.get("martial_art_id"),
                    data.get("end_date"), data.get("venue_name"), data.get("address"),
                    data.get("city"), data.get("country"), data.get("cover_image_path"),
                    data.get("capacity"), data.get("registration_deadline"),
                    data.get("price", 0), data.get("status", "draft"),
                    data.get("visibility", "internal"),
                    bool(data.get("is_featured", False)),
                    bool(data.get("registration_enabled", False)),
                    data.get("status", "draft"),
                    event_id,
                ))
                debug_log(f"[SocialEventsRepo] Evento actualizado: id={event_id}")
                return True
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error actualizando evento: {e}")
            return False

    def set_event_status(self, event_id, status, user_id=None):
        try:
            with db.transaction() as cur:
                if status in ("published", "registration_open", "registration_closed", "in_progress"):
                    cur.execute("""
                        UPDATE events SET status = %s, updated_at = CURRENT_TIMESTAMP,
                            published_at = COALESCE(published_at, CURRENT_TIMESTAMP)
                        WHERE id = %s;
                    """, (status, event_id))
                else:
                    cur.execute("""
                        UPDATE events SET status = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s;
                    """, (status, event_id))
                debug_log(f"[SocialEventsRepo] Estado cambiado: event={event_id} -> {status}")
                return True
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error cambiando estado: {e}")
            return False

    def delete_draft_event(self, event_id, user_id):
        try:
            with db.transaction() as cur:
                cur.execute("""
                    DELETE FROM events
                    WHERE id = %s AND status = 'draft' AND organizer_user_id = %s;
                """, (event_id, user_id))
                deleted = cur.rowcount > 0
                if deleted:
                    debug_log(f"[SocialEventsRepo] Borrador eliminado: id={event_id}")
                return deleted
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error eliminando borrador: {e}")
            return False

    # ── Social actions ─────────────────────────────────────────

    def follow_event(self, event_id, user_id):
        try:
            with db.transaction() as cur:
                cur.execute("""
                    INSERT INTO event_followers (event_id, user_id)
                    VALUES (%s, %s)
                    ON CONFLICT (event_id, user_id) DO NOTHING;
                """, (event_id, user_id))
                return True
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error siguiendo evento: {e}")
            return False

    def unfollow_event(self, event_id, user_id):
        try:
            with db.transaction() as cur:
                cur.execute("""
                    DELETE FROM event_followers
                    WHERE event_id = %s AND user_id = %s;
                """, (event_id, user_id))
                return True
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error dejando de seguir: {e}")
            return False

    def set_interest(self, event_id, user_id, response):
        try:
            with db.transaction() as cur:
                cur.execute("""
                    INSERT INTO event_interest (event_id, user_id, response)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (event_id, user_id)
                    DO UPDATE SET response = %s, updated_at = CURRENT_TIMESTAMP;
                """, (event_id, user_id, response, response))
                return True
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error en set_interest: {e}")
            return False

    def clear_interest(self, event_id, user_id):
        try:
            with db.transaction() as cur:
                cur.execute("""
                    DELETE FROM event_interest
                    WHERE event_id = %s AND user_id = %s;
                """, (event_id, user_id))
                return True
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error en clear_interest: {e}")
            return False

    # ── Registrations ──────────────────────────────────────────

    def register_student(self, event_id, user_id, student_id, notes=""):
        try:
            with db.transaction() as cur:
                cur.execute("""
                    INSERT INTO event_registrations
                        (event_id, user_id, student_id, notes)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (event_id, student_id)
                    WHERE student_id IS NOT NULL AND registration_status <> 'cancelled'
                    DO NOTHING
                    RETURNING id;
                """, (event_id, user_id, student_id, notes))
                row = cur.fetchone()
                if row:
                    debug_log(f"[SocialEventsRepo] Inscripción: event={event_id} student={student_id}")
                    return row[0]
                return None
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error inscribiendo: {e}")
            return None

    def cancel_registration(self, registration_id, user_id):
        try:
            with db.transaction() as cur:
                cur.execute("""
                    UPDATE event_registrations
                    SET registration_status = 'cancelled', updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s AND user_id = %s;
                """, (registration_id, user_id))
                debug_log(f"[SocialEventsRepo] Inscripción cancelada: id={registration_id}")
                return True
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error cancelando inscripción: {e}")
            return False

    def get_event_participants(self, event_id):
        try:
            with db.cursor() as cur:
                cur.execute("""
                    SELECT er.id, er.event_id, er.user_id, er.student_id,
                           er.registration_status, er.payment_status,
                           er.notes, er.registered_at, er.updated_at,
                           p.first_name, p.last_name
                    FROM event_registrations er
                    LEFT JOIN students s ON s.id = er.student_id
                    LEFT JOIN people p ON p.id = s.id_person
                    WHERE er.event_id = %s
                    ORDER BY er.registered_at ASC;
                """, (event_id,))
                rows = cur.fetchall()
            return _rows_to_dicts(rows, _REGISTRATION_COLS + ["first_name", "last_name"])
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error en get_event_participants: {e}")
            return []

    def get_available_students_for_user(self, user_id):
        try:
            with db.cursor() as cur:
                cur.execute("""
                    SELECT s.id, p.first_name, p.last_name, s.status
                    FROM students s
                    LEFT JOIN people p ON p.id = s.id_person
                    WHERE s.status = 'active'
                    ORDER BY p.first_name, p.last_name;
                """)
                rows = cur.fetchall()
            return _rows_to_dicts(rows, ["id", "first_name", "last_name", "status"])
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error en get_available_students: {e}")
            return []

    # ── Schedule ───────────────────────────────────────────────

    def get_event_schedule(self, event_id):
        try:
            with db.cursor() as cur:
                cur.execute("""
                    SELECT id, event_id, title, description, starts_at,
                           ends_at, location, sort_order, created_at, updated_at
                    FROM event_schedule_items
                    WHERE event_id = %s
                    ORDER BY starts_at ASC, sort_order ASC;
                """, (event_id,))
                rows = cur.fetchall()
            return _rows_to_dicts(rows, _SCHEDULE_COLS)
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error en get_event_schedule: {e}")
            return []

    def create_schedule_item(self, event_id, data):
        try:
            with db.transaction() as cur:
                cur.execute("""
                    INSERT INTO event_schedule_items
                        (event_id, title, description, starts_at, ends_at, location, sort_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (
                    event_id, data.get("title"), data.get("description"),
                    data.get("starts_at"), data.get("ends_at"),
                    data.get("location"), data.get("sort_order", 0),
                ))
                return cur.fetchone()[0]
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error creando agenda: {e}")
            return None

    def update_schedule_item(self, item_id, data):
        try:
            with db.transaction() as cur:
                cur.execute("""
                    UPDATE event_schedule_items SET
                        title = %s, description = %s, starts_at = %s,
                        ends_at = %s, location = %s, sort_order = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                """, (
                    data.get("title"), data.get("description"),
                    data.get("starts_at"), data.get("ends_at"),
                    data.get("location"), data.get("sort_order", 0),
                    item_id,
                ))
                return True
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error actualizando agenda: {e}")
            return False

    def delete_schedule_item(self, item_id):
        try:
            with db.transaction() as cur:
                cur.execute("DELETE FROM event_schedule_items WHERE id = %s;", (item_id,))
                return True
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error eliminando agenda: {e}")
            return False

    # ── Posts ──────────────────────────────────────────────────

    def get_event_posts(self, event_id):
        try:
            with db.cursor() as cur:
                cur.execute("""
                    SELECT ep.id, ep.event_id, ep.author_user_id, ep.content,
                           ep.image_path, ep.is_pinned, ep.created_at, ep.updated_at,
                           u.username AS author_name
                    FROM event_posts ep
                    LEFT JOIN users u ON u.id = ep.author_user_id
                    WHERE ep.event_id = %s
                    ORDER BY ep.is_pinned DESC, ep.created_at DESC;
                """, (event_id,))
                rows = cur.fetchall()
            return _rows_to_dicts(rows, _POST_COLS + ["author_name"])
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error en get_event_posts: {e}")
            return []

    def create_event_post(self, event_id, author_user_id, content, image_path=None, is_pinned=False):
        try:
            with db.transaction() as cur:
                cur.execute("""
                    INSERT INTO event_posts (event_id, author_user_id, content, image_path, is_pinned)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                """, (event_id, author_user_id, content, image_path, is_pinned))
                post_id = cur.fetchone()[0]
                debug_log(f"[SocialEventsRepo] Post creado: id={post_id} event={event_id}")
                return post_id
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error creando post: {e}")
            return None

    def update_event_post(self, post_id, user_id, data):
        try:
            with db.transaction() as cur:
                cur.execute("""
                    UPDATE event_posts SET
                        content = %s, image_path = %s, is_pinned = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s AND author_user_id = %s;
                """, (
                    data.get("content"), data.get("image_path"),
                    data.get("is_pinned", False), post_id, user_id,
                ))
                return cur.rowcount > 0
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error actualizando post: {e}")
            return False

    def delete_event_post(self, post_id, user_id):
        try:
            with db.transaction() as cur:
                cur.execute("""
                    DELETE FROM event_posts WHERE id = %s AND author_user_id = %s;
                """, (post_id, user_id))
                return cur.rowcount > 0
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error eliminando post: {e}")
            return False

    # ── Statistics ─────────────────────────────────────────────

    def get_event_statistics(self, event_id):
        try:
            stats = {}
            with db.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) FROM event_registrations
                    WHERE event_id = %s AND registration_status NOT IN ('cancelled','rejected');
                """, (event_id,))
                stats["registrations"] = cur.fetchone()[0]

                cur.execute("""
                    SELECT COUNT(*) FROM event_followers WHERE event_id = %s;
                """, (event_id,))
                stats["followers"] = cur.fetchone()[0]

                cur.execute("""
                    SELECT COUNT(*) FROM event_interest
                    WHERE event_id = %s AND response = 'attending';
                """, (event_id,))
                stats["attending"] = cur.fetchone()[0]

                cur.execute("""
                    SELECT COUNT(*) FROM event_interest
                    WHERE event_id = %s AND response = 'interested';
                """, (event_id,))
                stats["interested"] = cur.fetchone()[0]

                cur.execute("""
                    SELECT COUNT(*) FROM event_posts WHERE event_id = %s;
                """, (event_id,))
                stats["posts"] = cur.fetchone()[0]

                cur.execute("""
                    SELECT COUNT(*) FROM event_schedule_items WHERE event_id = %s;
                """, (event_id,))
                stats["schedule_items"] = cur.fetchone()[0]

            return stats
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error en get_event_statistics: {e}")
            return {}

    # ── Permissions ────────────────────────────────────────────

    def get_user_role_names(self, user_id):
        try:
            with db.cursor() as cur:
                cur.execute("""
                    SELECT DISTINCT r.name
                    FROM users u
                    JOIN people p ON p.id = u.id_person
                    JOIN person_roles pr ON pr.id_person = p.id
                    JOIN roles r ON r.id = pr.id_role
                    WHERE u.id = %s;
                """, (user_id,))
                return [row[0] for row in cur.fetchall()]
        except Exception as e:
            debug_log(f"[SocialEventsRepo] Error en get_user_role_names: {e}")
            return []

    def can_manage_event(self, user_id, event_id):
        roles = self.get_user_role_names(user_id)
        if "admin" in roles:
            return True
        try:
            with db.cursor() as cur:
                cur.execute(
                    "SELECT organizer_user_id FROM events WHERE id = %s;",
                    (event_id,),
                )
                row = cur.fetchone()
                return row and row[0] == user_id
        except Exception:
            return False

    def is_admin_or_instructor(self, user_id):
        roles = self.get_user_role_names(user_id)
        return "admin" in roles or "instructor" in roles
