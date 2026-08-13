from __future__ import annotations

import re
import warnings

from database.connection import db


_REQUIREMENT_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

_DEFAULT_REQUIREMENT_COLOR = "#3B82F6"


def requirement_default_color(type_name: str | None = None) -> str:
    """Type-based accent color used only when a record has no stored color."""
    key = (type_name or "").strip().lower()
    return {
        "tiempo": "#3B82F6",
        "técnico": "#7E22CE", "tecnico": "#7E22CE",
        "físico": "#22C55E", "fisico": "#22C55E",
        "conducta": "#EAB308", "actitud": "#EAB308",
        "sin tipo": "#71717A",
    }.get(key, _DEFAULT_REQUIREMENT_COLOR)


def _normalize_requirement_color(value) -> str:
    if not value:
        return _DEFAULT_REQUIREMENT_COLOR
    candidate = str(value).strip().upper()
    if _REQUIREMENT_COLOR_RE.match(candidate):
        return candidate
    return _DEFAULT_REQUIREMENT_COLOR


class BeltsRepository:

    # ═══════════════════════════════════════════════════════════════════
    # Artes Marciales
    # ═══════════════════════════════════════════════════════════════════

    def _has_column(self, table: str, column: str) -> bool:
        """Check if a column exists in a table (idempotent, cached)."""
        key = f"{table}.{column}"
        if not hasattr(self, "_col_cache"):
            self._col_cache: dict[str, bool] = {}
        if key in self._col_cache:
            return self._col_cache[key]
        try:
            with db.cursor() as cur:
                cur.execute(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.columns "
                    "WHERE table_name = %s AND column_name = %s)",
                    (table, column),
                )
                exists = cur.fetchone()[0]
        except Exception:
            exists = False
        self._col_cache[key] = exists
        return exists

    def _select_martial_arts_columns(self) -> str:
        base = (
            "id, name, icon_key, accent_color, "
            "progression_enabled, progression_system, "
            "progression_label_singular, progression_label_plural, "
            "promotion_mode, allow_level_skips, "
            "initial_assignment_mode, template_key, is_active"
        )
        extras = []
        if self._has_column("martial_arts", "description"):
            extras.append("description")
        if self._has_column("martial_arts", "training_focus"):
            extras.append("training_focus")
        if extras:
            return base + ", " + ", ".join(extras)
        return base

    def _map_martial_art_row(self, r, has_description: bool, has_focus: bool) -> dict:
        d = {
            "id": r[0], "name": r[1], "icon_key": r[2],
            "accent_color": r[3], "progression_enabled": r[4],
            "progression_system": r[5],
            "progression_label_singular": r[6],
            "progression_label_plural": r[7],
            "promotion_mode": r[8], "allow_level_skips": r[9],
            "initial_assignment_mode": r[10],
            "template_key": r[11], "is_active": r[12],
        }
        idx = 13
        if has_description:
            d["description"] = r[idx]; idx += 1
        else:
            d["description"] = None
        if has_focus:
            d["training_focus"] = r[idx]; idx += 1
        else:
            d["training_focus"] = None
        return d

    def get_martial_arts(self) -> list[dict]:
        cols = self._select_martial_arts_columns()
        has_d = self._has_column("martial_arts", "description")
        has_f = self._has_column("martial_arts", "training_focus")
        with db.cursor() as cur:
            cur.execute(f"""
                SELECT {cols}
                FROM martial_arts
                ORDER BY name
            """)
            return [self._map_martial_art_row(r, has_d, has_f) for r in cur.fetchall()]

    def get_martial_arts_full(self) -> list[dict]:
        """Alias for get_martial_arts."""
        return self.get_martial_arts()

    def get_martial_art(self, ma_id: int) -> dict | None:
        cols = self._select_martial_arts_columns()
        has_d = self._has_column("martial_arts", "description")
        has_f = self._has_column("martial_arts", "training_focus")
        with db.cursor() as cur:
            cur.execute(f"""
                SELECT {cols}
                FROM martial_arts
                WHERE id = %s
            """, (ma_id,))
            r = cur.fetchone()
            if not r:
                return None
            return self._map_martial_art_row(r, has_d, has_f)

    def create_martial_art(
        self,
        name: str,
        icon_key: str | None = None,
        accent_color: str = "#C8102E",
    ) -> int:
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO martial_arts (name, icon_key, accent_color)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (name, icon_key, accent_color))
            return cur.fetchone()[0]

    def update_martial_art(
        self,
        ma_id: int,
        name: str,
        icon_key: str | None = None,
        accent_color: str | None = None,
    ) -> None:
        with db.transaction() as cur:
            cur.execute("""
                UPDATE martial_arts
                SET name = %s,
                    icon_key = %s,
                    accent_color = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (name, icon_key, accent_color, ma_id))

    def delete_martial_art(self, ma_id: int) -> None:
        with db.transaction() as cur:
            cur.execute("DELETE FROM martial_arts WHERE id = %s", (ma_id,))

    def get_martial_art_settings(self, ma_id: int) -> dict | None:
        """Alias for get_martial_art."""
        return self.get_martial_art(ma_id)

    def save_martial_art_settings(self, ma_id: int, settings: dict) -> None:
        pm = settings.get("promotion_mode")
        if pm == "Secuencial":
            settings["promotion_mode"] = "sequential"
            settings["allow_level_skips"] = False
        elif pm == "Permitir saltos":
            settings["promotion_mode"] = "manual"
            settings["allow_level_skips"] = True
        has_d = self._has_column("martial_arts", "description")
        has_f = self._has_column("martial_arts", "training_focus")

        set_parts = [
            "name = %s", "icon_key = %s", "accent_color = %s",
            "progression_enabled = %s", "progression_system = %s",
            "progression_label_singular = %s", "progression_label_plural = %s",
            "promotion_mode = %s", "allow_level_skips = %s",
            "initial_assignment_mode = %s", "template_key = %s",
            "is_active = %s", "updated_at = CURRENT_TIMESTAMP",
        ]
        params = [
            settings.get("name"), settings.get("icon_key"),
            settings.get("accent_color", "#C8102E"),
            settings.get("progression_enabled", True),
            settings.get("progression_system", "belt"),
            settings.get("progression_label_singular", "Cinturón"),
            settings.get("progression_label_plural", "Cinturones"),
            settings.get("promotion_mode", "sequential"),
            settings.get("allow_level_skips", False),
            settings.get("initial_assignment_mode", "first_only"),
            settings.get("template_key"), settings.get("is_active", True),
        ]
        if has_d:
            set_parts.append("description = %s")
            params.append(settings.get("description"))
        if has_f:
            set_parts.append("training_focus = %s")
            params.append(settings.get("training_focus"))

        params.append(ma_id)
        with db.transaction() as cur:
            cur.execute(
                f"UPDATE martial_arts SET {', '.join(set_parts)} WHERE id = %s",
                tuple(params),
            )

    def get_martial_art_dependencies(self, ma_id: int) -> dict:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    (SELECT COUNT(*) FROM belts WHERE id_martial_art = %s) AS belts,
                    (SELECT COUNT(*) FROM instructor_martial_arts WHERE id_martial_art = %s) AS instructors,
                    (SELECT COUNT(*) FROM students_belts sb
                     JOIN belts b ON b.id = sb.id_belt
                     WHERE b.id_martial_art = %s) AS students
            """, (ma_id, ma_id, ma_id))
            r = cur.fetchone()
            return {
                "belts": r[0] if r else 0,
                "instructors": r[1] if r else 0,
                "students": r[2] if r else 0,
            }

    # ═══════════════════════════════════════════════════════════════════
    # Cinturones / Niveles
    # ═══════════════════════════════════════════════════════════════════

    def get_belts(self, martial_art_id: int) -> list[dict]:
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, name, orden,
                    COALESCE(color, '#888888'),
                    pre_color,
                    COALESCE(grades, 0),
                    COALESCE(grade_color, '#FFFFFF'),
                    level_type,
                    icon_key,
                    is_initial,
                    is_final,
                    is_active,
                    display_name,
                    minimum_age,
                    maximum_age,
                    age_restriction_note
                FROM belts
                WHERE id_martial_art = %s
                ORDER BY orden ASC NULLS LAST, name
            """, (martial_art_id,))

            return [
                {
                    "id": r[0], "name": r[1], "orden": r[2],
                    "color": r[3], "pre_color": r[4],
                    "grades": r[5], "grade_color": r[6],
                    "level_type": r[7], "icon_key": r[8],
                    "is_initial": r[9], "is_final": r[10],
                    "is_active": r[11], "display_name": r[12],
                    "minimum_age": r[13], "maximum_age": r[14],
                    "age_restriction_note": r[15],
                }
                for r in cur.fetchall()
            ]

    def get_level(self, level_id: int) -> dict | None:
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, name, orden,
                    COALESCE(color, '#888888'),
                    pre_color,
                    COALESCE(grades, 0),
                    COALESCE(grade_color, '#FFFFFF'),
                    level_type, icon_key, is_initial, is_final,
                    is_active, display_name, id_martial_art,
                    minimum_age, maximum_age, age_restriction_note
                FROM belts
                WHERE id = %s
            """, (level_id,))
            r = cur.fetchone()
            if not r:
                return None
            return {
                "id": r[0], "name": r[1], "orden": r[2],
                "color": r[3], "pre_color": r[4],
                "grades": r[5], "grade_color": r[6],
                "level_type": r[7], "icon_key": r[8],
                "is_initial": r[9], "is_final": r[10],
                "is_active": r[11], "display_name": r[12],
                "id_martial_art": r[13],
                "minimum_age": r[14], "maximum_age": r[15],
                "age_restriction_note": r[16],
            }

    def create_belt(
        self,
        martial_art_id: int,
        name: str,
        orden: int | None = None,
        color: str | None = None,
        pre_color: str | None = None,
        grades: int = 0,
        grade_color: str = "#FFFFFF",
        minimum_age: int | None = None,
        maximum_age: int | None = None,
        age_restriction_note: str | None = None,
         is_initial: bool = False,
         is_final: bool = False,
         is_active: bool = True,
         level_type: str | None = None,
         display_name: str | None = None,
         icon_key: str | None = None,
    ) -> int:
        if minimum_age is not None and maximum_age is not None and minimum_age > maximum_age:
            raise ValueError("minimum_age cannot exceed maximum_age")
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO belts
                    (name, id_martial_art, orden, color, pre_color,
                     grades, grade_color,
                     minimum_age, maximum_age, age_restriction_note,
                     is_initial, is_final, is_active,
                     level_type, display_name, icon_key)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (name, martial_art_id, orden, color, pre_color, grades, grade_color,
                  minimum_age, maximum_age, age_restriction_note,
                  is_initial, is_final, is_active,
                  level_type, display_name, icon_key))
            return cur.fetchone()[0]

    def update_belt(
        self,
        belt_id: int,
        name: str,
        orden: int | None = None,
        color: str | None = None,
        pre_color: str | None = None,
        grades: int = 0,
        grade_color: str = "#FFFFFF",
        minimum_age: int | None = None,
        maximum_age: int | None = None,
        age_restriction_note: str | None = None,
        is_initial: bool = False,
        is_final: bool = False,
        is_active: bool = True,
        level_type: str | None = None,
        display_name: str | None = None,
        icon_key: str | None = None,
    ) -> None:
        if minimum_age is not None and maximum_age is not None and minimum_age > maximum_age:
            raise ValueError("minimum_age cannot exceed maximum_age")
        with db.transaction() as cur:
            cur.execute("""
                UPDATE belts
                SET name = %s,
                    orden = %s,
                    color = %s,
                    pre_color = %s,
                    grades = %s,
                    grade_color = %s,
                    minimum_age = %s,
                    maximum_age = %s,
                    age_restriction_note = %s,
                    is_initial = %s,
                    is_final = %s,
                    is_active = %s,
                    level_type = %s,
                    display_name = %s,
                    icon_key = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (name, orden, color, pre_color, grades, grade_color,
                  minimum_age, maximum_age, age_restriction_note,
                  is_initial, is_final, is_active,
                  level_type, display_name, icon_key, belt_id))

    def delete_belt(self, belt_id: int) -> None:
        with db.transaction() as cur:
            cur.execute("DELETE FROM belts WHERE id = %s", (belt_id,))

    def get_level_dependencies(self, level_id: int) -> dict:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    (SELECT COUNT(*) FROM students_belts WHERE id_belt = %s),
                    (SELECT COUNT(*) FROM belt_requirements WHERE belt_id = %s),
                    (SELECT COUNT(*) FROM martial_art_promotion_rules
                        WHERE from_level_id = %s OR to_level_id = %s),
                    (SELECT COUNT(*) FROM martial_art_initial_levels WHERE level_id = %s)
            """, (level_id, level_id, level_id, level_id, level_id))
            r = cur.fetchone()
            return {
                "students": r[0],
                "requirements": r[1],
                "promotion_rules": r[2],
                "initial_assignments": r[3],
            }

    def is_level_order_available(
        self,
        martial_art_id: int,
        orden: int,
        exclude_level_id: int | None = None,
    ) -> bool:
        with db.cursor() as cur:
            if exclude_level_id is not None:
                cur.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM belts
                        WHERE id_martial_art = %s
                          AND orden = %s
                          AND id != %s
                    )
                """, (martial_art_id, orden, exclude_level_id))
            else:
                cur.execute("""
                    SELECT EXISTS(
                        SELECT 1 FROM belts
                        WHERE id_martial_art = %s
                          AND orden = %s
                    )
                """, (martial_art_id, orden))
            return not cur.fetchone()[0]

    def get_next_available_order(self, martial_art_id: int) -> int:
        with db.cursor() as cur:
            cur.execute("""
                SELECT COALESCE(MAX(orden), 0) + 1
                FROM belts
                WHERE id_martial_art = %s
            """, (martial_art_id,))
            return cur.fetchone()[0]

    def get_all_progression_levels(self, martial_art_id: int) -> list[dict]:
        """Alias for get_belts."""
        return self.get_belts(martial_art_id)

    def get_allowed_promotion_levels(
        self,
        martial_art_id: int,
        current_level_id: int | None,
    ) -> list[dict]:
        settings = self.get_martial_art(martial_art_id)
        if not settings:
            return []

        promotion_mode = settings.get("promotion_mode", "sequential")
        allow_skips = settings.get("allow_level_skips", False)
        all_levels = self.get_belts(martial_art_id)

        if not all_levels:
            return []

        all_levels = [lv for lv in all_levels if lv.get("is_active", True)]

        if not all_levels:
            return []

        if current_level_id is None:
            if promotion_mode == "manual" and allow_skips:
                return all_levels
            return [all_levels[0]] if all_levels else []

        current_idx: int | None = None
        for i, lv in enumerate(all_levels):
            if lv["id"] == current_level_id:
                current_idx = i
                break

        if current_idx is None:
            return []

        if promotion_mode == "sequential":
            if current_idx + 1 < len(all_levels):
                return [all_levels[current_idx + 1]]
            return []

        if promotion_mode == "sequential_with_grades":
            current_lv = all_levels[current_idx]
            grades_needed = current_lv.get("grades", 0) or 0
            if grades_needed > 0:
                return []
            if current_idx + 1 < len(all_levels):
                return [all_levels[current_idx + 1]]
            return []

        if promotion_mode == "manual":
            if allow_skips:
                return all_levels[current_idx + 1:]
            return [all_levels[current_idx + 1]] if current_idx + 1 < len(all_levels) else []

        if promotion_mode == "custom_rules":
            rules = self.get_promotion_rules(martial_art_id)
            allowed_ids: set[int] = set()
            for rule in rules:
                if rule.get("from_level_id") == current_level_id and rule.get("is_allowed"):
                    allowed_ids.add(rule["to_level_id"])
            return [lv for lv in all_levels if lv["id"] in allowed_ids]

        return all_levels[current_idx + 1:] if allow_skips and current_idx + 1 < len(all_levels) else (
            [all_levels[current_idx + 1]] if current_idx + 1 < len(all_levels) else []
        )

    def validate_promotion(
        self,
        student_id: int,
        martial_art_id: int,
        destination_level_id: int,
    ) -> tuple[bool, str]:
        with db.cursor() as cur:
            cur.execute("""
                SELECT sb.id_belt
                FROM students_belts sb
                JOIN belts b ON b.id = sb.id_belt
                WHERE sb.id_student = %s AND b.id_martial_art = %s
            """, (student_id, martial_art_id))
            row = cur.fetchone()
            current_level_id = row[0] if row else None

        settings = self.get_martial_art(martial_art_id)
        if not settings:
            return False, "Arte marcial no encontrado."

        if not settings.get("progression_enabled", True):
            return False, "Este arte marcial no tiene progresion habilitada."

        dest = self.get_level(destination_level_id)
        if not dest:
            return False, "Nivel de destino no encontrado."

        if dest.get("id_martial_art") != martial_art_id:
            return False, "El nivel no pertenece a este arte marcial."

        allowed = self.get_allowed_promotion_levels(martial_art_id, current_level_id)
        allowed_ids = {lv["id"] for lv in allowed}
        if destination_level_id not in allowed_ids:
            return False, "Ascenso no permitido segun las reglas configuradas."

        return True, "Ascenso valido."

    # ═══════════════════════════════════════════════════════════════════
    # Reglas de ascenso
    # ═══════════════════════════════════════════════════════════════════

    def get_promotion_rules(self, martial_art_id: int) -> list[dict]:
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, martial_art_id, from_level_id, to_level_id,
                       is_allowed, requires_all_grades, minimum_grade,
                       notes
                FROM martial_art_promotion_rules
                WHERE martial_art_id = %s
                ORDER BY from_level_id NULLS FIRST, to_level_id
            """, (martial_art_id,))
            return [
                {
                    "id": r[0], "martial_art_id": r[1],
                    "from_level_id": r[2], "to_level_id": r[3],
                    "is_allowed": r[4], "requires_all_grades": r[5],
                    "minimum_grade": r[6], "notes": r[7],
                }
                for r in cur.fetchall()
            ]

    def save_promotion_rules(
        self,
        martial_art_id: int,
        rules_list: list[dict],
    ) -> None:
        with db.transaction() as cur:
            cur.execute("""
                DELETE FROM martial_art_promotion_rules
                WHERE martial_art_id = %s
            """, (martial_art_id,))
            for rule in rules_list:
                cur.execute("""
                    INSERT INTO martial_art_promotion_rules
                        (martial_art_id, from_level_id, to_level_id,
                         is_allowed, requires_all_grades, minimum_grade, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    martial_art_id,
                    rule.get("from_level_id"),
                    rule["to_level_id"],
                    rule.get("is_allowed", True),
                    rule.get("requires_all_grades", False),
                    rule.get("minimum_grade"),
                    rule.get("notes"),
                ))

    # ═══════════════════════════════════════════════════════════════════
    # Plantillas de progresion
    # ═══════════════════════════════════════════════════════════════════

    def get_progression_templates(self, system_type: str | None = None) -> list[dict]:
        with db.cursor() as cur:
            base_sql = """
                SELECT id, template_key, name, description,
                       system_type, icon_key, is_builtin, is_active
                FROM progression_templates
                WHERE (is_builtin = true OR is_active = true)
            """
            params: list = []
            if system_type:
                base_sql += " AND system_type = %s"
                params.append(system_type)
            base_sql += " ORDER BY is_builtin DESC, name ASC"
            cur.execute(base_sql, tuple(params))
            return [
                {
                    "id": r[0], "template_key": r[1], "name": r[2],
                    "description": r[3], "system_type": r[4],
                    "icon_key": r[5], "is_builtin": r[6],
                    "is_active": r[7],
                }
                for r in cur.fetchall()
            ]

    def get_template_levels(self, template_id: int) -> list[dict]:
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, template_id, name, orden, color,
                       pre_color, grades, grade_color, icon_key,
                       is_initial, is_final
                FROM progression_template_levels
                WHERE template_id = %s
                ORDER BY orden ASC NULLS LAST, name
            """, (template_id,))
            return [
                {
                    "id": r[0], "template_id": r[1], "name": r[2],
                    "orden": r[3], "color": r[4], "pre_color": r[5],
                    "grades": r[6], "grade_color": r[7],
                    "icon_key": r[8], "is_initial": r[9],
                    "is_final": r[10],
                }
                for r in cur.fetchall()
            ]

    def apply_progression_template(
        self,
        martial_art_id: int,
        template_id: int,
        strategy: str = "append_missing",
    ) -> None:
        with db.cursor() as cur:
            cur.execute("""
                SELECT system_type, template_key
                FROM progression_templates
                WHERE id = %s
            """, (template_id,))
            meta = cur.fetchone()
        if not meta:
            raise ValueError("Plantilla no encontrada.")
        template_system, template_key = meta

        template_levels = self.get_template_levels(template_id)
        is_no_progression = (
            template_system == "none" or template_key == "no_progression"
        )

        if not is_no_progression and not template_levels:
            raise ValueError("La plantilla no tiene niveles.")

        settings = self.get_martial_art(martial_art_id)
        if not settings:
            raise ValueError("Arte marcial no encontrado.")

        if self.has_students_with_levels(martial_art_id):
            raise ValueError(
                "No se puede aplicar la plantilla: "
                "existen estudiantes con niveles asignados."
            )

        with db.transaction() as cur:
            cur.execute("""
                DELETE FROM martial_art_promotion_rules
                WHERE martial_art_id = %s
            """, (martial_art_id,))

            cur.execute("""
                DELETE FROM belts
                WHERE id_martial_art = %s
            """, (martial_art_id,))

            for tl in template_levels:
                cur.execute("""
                    INSERT INTO belts
                        (name, id_martial_art, orden, color, pre_color,
                         grades, grade_color, icon_key, is_initial,
                         is_final, level_type, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, true)
                """, (
                    tl["name"], martial_art_id, tl["orden"],
                    tl["color"], tl["pre_color"], tl["grades"],
                    tl["grade_color"], tl.get("icon_key"),
                    tl.get("is_initial", False),
                    tl.get("is_final", False),
                    template_system,
                ))

            cur.execute("""
                UPDATE martial_arts
                SET progression_enabled = %s,
                    progression_system = %s,
                    template_key = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (
                template_system != "none",
                template_system,
                template_key,
                martial_art_id,
            ))

            if template_levels:
                cur.execute("""
                    SELECT id FROM belts
                    WHERE id_martial_art = %s
                    ORDER BY orden ASC NULLS LAST, name
                """, (martial_art_id,))
                new_ids = [row[0] for row in cur.fetchall()]
                for i, from_id in enumerate(new_ids):
                    if i + 1 < len(new_ids):
                        cur.execute("""
                            INSERT INTO martial_art_promotion_rules
                                (martial_art_id, from_level_id, to_level_id,
                                 is_allowed)
                            VALUES (%s, %s, %s, true)
                        """, (martial_art_id, from_id, new_ids[i + 1]))

    def has_students_with_levels(self, martial_art_id: int) -> bool:
        with db.cursor() as cur:
            cur.execute("""
                SELECT EXISTS(
                    SELECT 1
                    FROM students_belts sb
                    JOIN belts b ON b.id = sb.id_belt
                    WHERE b.id_martial_art = %s
                      AND sb.id_belt IS NOT NULL
                )
            """, (martial_art_id,))
            return cur.fetchone()[0]

    # ═══════════════════════════════════════════════════════════════════
    # Niveles iniciales
    # ═══════════════════════════════════════════════════════════════════

    def _get_initial_levels(self, martial_art_id: int) -> list[dict]:
        with db.cursor() as cur:
            cur.execute("""
                SELECT b.id, b.name, b.orden,
                    COALESCE(b.color, '#888888')
                FROM martial_art_initial_levels mil
                JOIN belts b ON b.id = mil.level_id
                WHERE mil.martial_art_id = %s
                ORDER BY b.orden ASC NULLS LAST, b.name
            """, (martial_art_id,))
            return [
                {
                    "id": r[0], "name": r[1],
                    "orden": r[2], "color": r[3],
                }
                for r in cur.fetchall()
            ]

    # ═══════════════════════════════════════════════════════════════════
    # Requisitos
    # ═══════════════════════════════════════════════════════════════════

    def get_requirements(self, belt_id: int) -> list[dict]:
        has_color = self._has_column("belt_requirements", "accent_color")
        if not has_color:
            warnings.warn(
                "La base de datos necesita la migración de color para requisitos. "
                "Usando color por defecto."
            )
        with db.cursor() as cur:
            if has_color:
                cur.execute("""
                    SELECT br.id, br.requirement, br.id_type_requeriments,
                           tr.type_requirement,
                           COALESCE(br.accent_color, %s)
                    FROM belt_requirements br
                    LEFT JOIN type_requirements tr ON tr.id = br.id_type_requeriments
                    WHERE br.belt_id = %s
                    ORDER BY br.created_at
                """, (_DEFAULT_REQUIREMENT_COLOR, belt_id))
            else:
                cur.execute("""
                    SELECT br.id, br.requirement, br.id_type_requeriments,
                           tr.type_requirement
                    FROM belt_requirements br
                    LEFT JOIN type_requirements tr ON tr.id = br.id_type_requeriments
                    WHERE br.belt_id = %s
                    ORDER BY br.created_at
                """, (belt_id,))
            return [
                {
                    "id": r[0], "requirement": r[1],
                    "id_type": r[2], "type_name": r[3],
                    "accent_color": (
                        r[4] if len(r) > 4 and r[4] else _DEFAULT_REQUIREMENT_COLOR
                    ),
                }
                for r in cur.fetchall()
            ]

    def get_requirement_types(self) -> list:
        with db.cursor() as cur:
            cur.execute(
                "SELECT id, type_requirement FROM type_requirements ORDER BY type_requirement"
            )
            return cur.fetchall()

    def create_requirement(
        self,
        belt_id: int,
        requirement: str,
        tipo_id: int | None = None,
        accent_color: str = "#3B82F6",
    ) -> int:
        if not self._has_column("belt_requirements", "accent_color"):
            raise RuntimeError(
                "La base de datos necesita la migración de color para requisitos."
            )
        normalized = _normalize_requirement_color(accent_color)
        with db.transaction() as cur:
            cur.execute("""
                INSERT INTO belt_requirements
                    (belt_id, requirement, id_type_requeriments, accent_color)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (belt_id, requirement, tipo_id, normalized))
            return cur.fetchone()[0]

    def update_requirement(
        self,
        req_id: int,
        requirement: str,
        tipo_id: int | None = None,
        accent_color: str = "#3B82F6",
    ) -> None:
        if not self._has_column("belt_requirements", "accent_color"):
            raise RuntimeError(
                "La base de datos necesita la migración de color para requisitos."
            )
        normalized = _normalize_requirement_color(accent_color)
        with db.transaction() as cur:
            cur.execute("""
                UPDATE belt_requirements
                SET requirement = %s, id_type_requeriments = %s, accent_color = %s
                WHERE id = %s
            """, (requirement, tipo_id, normalized, req_id))

    def delete_requirement(self, req_id: int) -> None:
        with db.transaction() as cur:
            cur.execute("DELETE FROM belt_requirements WHERE id = %s", (req_id,))

    # ═══════════════════════════════════════════════════════════════════
    # Tipos de requisito (CRUD)
    # ═══════════════════════════════════════════════════════════════════

    def create_requirement_type(self, name: str) -> int:
        trimmed = (name or "").strip()
        if not trimmed:
            raise ValueError("El nombre del tipo no puede estar vacio.")
        with db.cursor() as cur:
            cur.execute(
                "SELECT EXISTS(SELECT 1 FROM type_requirements WHERE LOWER(BTRIM(type_requirement)) = LOWER(BTRIM(%s)))",
                (trimmed,),
            )
            if cur.fetchone()[0]:
                raise ValueError("Ya existe un tipo de requisito con ese nombre.")
        with db.transaction() as cur:
            cur.execute(
                "INSERT INTO type_requirements (type_requirement) VALUES (%s) RETURNING id",
                (trimmed,),
            )
            return cur.fetchone()[0]

    def update_requirement_type(self, type_id: int, name: str) -> None:
        trimmed = (name or "").strip()
        if not trimmed:
            raise ValueError("El nombre del tipo no puede estar vacio.")
        with db.transaction() as cur:
            cur.execute(
                "UPDATE type_requirements SET type_requirement = %s WHERE id = %s",
                (trimmed, type_id),
            )

    def delete_requirement_type(self, type_id: int) -> None:
        with db.transaction() as cur:
            cur.execute("DELETE FROM type_requirements WHERE id = %s", (type_id,))

    def requirement_type_in_use(self, type_id: int) -> bool:
        with db.cursor() as cur:
            cur.execute(
                "SELECT EXISTS(SELECT 1 FROM belt_requirements WHERE id_type_requeriments = %s)",
                (type_id,),
            )
            return cur.fetchone()[0]

    # ═══════════════════════════════════════════════════════════════════
    # Instructores que pueden promover
    # ═══════════════════════════════════════════════════════════════════

    def get_instructors_that_can_promote(self, martial_art_id: int) -> list[dict]:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    i.id,
                    p.first_name || ' ' || p.last_name AS nombre
                FROM instructor_martial_arts ima
                JOIN instructors i  ON i.id  = ima.id_instructor
                JOIN people      p  ON p.id  = i.id_person
                WHERE ima.id_martial_art = %s
                  AND ima.can_promote = TRUE
                ORDER BY p.first_name, p.last_name
            """, (martial_art_id,))
            return [{"id": r[0], "nombre": r[1]} for r in cur.fetchall()]

    # ═══════════════════════════════════════════════════════════════════
    # Estudiantes por arte marcial
    # ═══════════════════════════════════════════════════════════════════

    def get_students_by_martial_art(self, martial_art_id: int) -> list[dict]:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    s.id,
                    p.first_name || ' ' || p.last_name  AS nombre,
                    COALESCE(b.id,    0)                 AS belt_id,
                    COALESCE(b.name, 'Sin cinturón')     AS belt_name,
                    COALESCE(b.color, '#888888')          AS belt_color,
                    COALESCE(b.orden, 0)                  AS belt_orden,
                    COALESCE(b.grades, 0)                 AS belt_grades
                FROM students s
                JOIN people p  ON p.id  = s.id_person
                JOIN status st ON st.id = s.id_status
                    AND LOWER(st.status) IN ('activo', 'active')
                LEFT JOIN students_belts sb ON sb.id_student = s.id
                LEFT JOIN belts b
                    ON b.id = sb.id_belt
                    AND b.id_martial_art = %s
                ORDER BY p.first_name, p.last_name
            """, (martial_art_id,))
            return [
                {
                    "id": r[0], "nombre": r[1],
                    "belt_id": r[2], "belt_name": r[3],
                    "belt_color": r[4], "belt_orden": r[5],
                    "belt_grades": r[6],
                }
                for r in cur.fetchall()
            ]

    # ═══════════════════════════════════════════════════════════════════
    # Ascenso de estudiante
    # ═══════════════════════════════════════════════════════════════════

    def promote_student(
        self,
        student_id: int,
        belt_id: int,
        instructor_id: int,
        martial_art_id: int,
    ) -> None:
        age_ok, age_msg = self.validate_level_age(student_id, belt_id)
        if not age_ok:
            raise ValueError(age_msg)

        with db.transaction() as cur:
            cur.execute("""
                SELECT can_promote FROM instructor_martial_arts
                WHERE id_instructor = %s AND id_martial_art = %s
            """, (instructor_id, martial_art_id))
            row = cur.fetchone()
            if not row or not row[0]:
                raise ValueError(
                    "Este instructor no tiene permiso para promover en este arte marcial."
                )

            cur.execute("""
                SELECT sb.id FROM students_belts sb
                JOIN belts b ON b.id = sb.id_belt
                WHERE sb.id_student = %s AND b.id_martial_art = %s
            """, (student_id, martial_art_id))
            existing = cur.fetchone()
            if existing:
                cur.execute(
                    "UPDATE students_belts SET id_belt = %s WHERE id = %s",
                    (belt_id, existing[0]),
                )
            else:
                cur.execute(
                    "INSERT INTO students_belts (id_student, id_belt) VALUES (%s, %s)",
                    (student_id, belt_id),
                )

            cur.execute("""
                INSERT INTO students_belts_history
                    (id_student, id_belt, action, date_changed)
                VALUES (%s, %s, 'promotion', NOW())
            """, (student_id, belt_id))

    # ═══════════════════════════════════════════════════════════════════
    # Age restrictions per level
    # ═══════════════════════════════════════════════════════════════════

    def get_level_age_rules(self, martial_art_id: int) -> list[dict]:
        with db.cursor() as cur:
            cur.execute("""
                SELECT b.id, b.name, b.orden, COALESCE(b.color, '#888888'),
                       b.minimum_age, b.maximum_age, b.age_restriction_note
                FROM belts b
                WHERE b.id_martial_art = %s
                ORDER BY b.orden ASC NULLS LAST, b.name
            """, (martial_art_id,))
            return [
                {
                    "level_id": r[0], "name": r[1], "orden": r[2],
                    "color": r[3], "minimum_age": r[4],
                    "maximum_age": r[5], "age_restriction_note": r[6],
                }
                for r in cur.fetchall()
            ]

    def save_level_age_rules(
        self,
        martial_art_id: int,
        rules: list[dict],
    ) -> None:
        with db.transaction() as cur:
            for rule in rules:
                level_id = rule["level_id"]
                minimum_age = rule.get("minimum_age")
                maximum_age = rule.get("maximum_age")
                note = rule.get("age_restriction_note")
                if minimum_age is not None:
                    minimum_age = int(minimum_age)
                if maximum_age is not None:
                    maximum_age = int(maximum_age)
                cur.execute("""
                    UPDATE belts
                    SET minimum_age = %s,
                        maximum_age = %s,
                        age_restriction_note = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s AND id_martial_art = %s
                """, (minimum_age, maximum_age, note, level_id, martial_art_id))

    def get_student_age(self, student_id: int) -> int | None:
        with db.cursor() as cur:
            cur.execute("""
                SELECT p.birthdate
                FROM students s
                JOIN people p ON p.id = s.id_person
                WHERE s.id = %s
            """, (student_id,))
            row = cur.fetchone()
            if not row or not row[0]:
                return None
            from datetime import date
            bd = row[0]
            today = date.today()
            age = today.year - bd.year - (
                (today.month, today.day) < (bd.month, bd.day)
            )
            return age

    def validate_level_age(
        self,
        student_id: int,
        level_id: int,
    ) -> tuple[bool, str]:
        age = self.get_student_age(student_id)
        if age is None:
            return True, ""

        with db.cursor() as cur:
            cur.execute("""
                SELECT minimum_age, maximum_age, age_restriction_note
                FROM belts WHERE id = %s
            """, (level_id,))
            row = cur.fetchone()
            if not row:
                return True, ""

        min_age, max_age, note = row[0], row[1], row[2]
        note_suffix = f" ({note})" if note else ""

        if min_age is not None and age < min_age:
            return False, f"Edad minima: {min_age} anios{note_suffix}. Estudiante tiene {age}."
        if max_age is not None and age > max_age:
            return False, f"Edad maxima: {max_age} anios{note_suffix}. Estudiante tiene {age}."
        return True, ""

    # ═══════════════════════════════════════════════════════════════════
    # Discipline exercises
    # ═══════════════════════════════════════════════════════════════════

    def _has_table(self, table: str) -> bool:
        """Check if a table exists (idempotent, cached)."""
        if not hasattr(self, "_tbl_cache"):
            self._tbl_cache: dict[str, bool] = {}
        if table in self._tbl_cache:
            return self._tbl_cache[table]
        try:
            with db.cursor() as cur:
                cur.execute(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.tables "
                    "WHERE table_name = %s)",
                    (table,),
                )
                exists = cur.fetchone()[0]
        except Exception:
            exists = False
        self._tbl_cache[table] = exists
        return exists

    def get_discipline_exercises(
        self,
        martial_art_id: int,
        include_inactive: bool = False,
    ) -> list[dict]:
        if not self._has_table("discipline_exercises"):
            return []
        has_image = self._has_column("discipline_exercises", "image_path")
        if not has_image:
            warnings.warn(
                "La base de datos necesita la migración de imágenes para "
                "ejercicios. image_path será None."
            )
        with db.cursor() as cur:
            where = ""
            if not include_inactive:
                where = "AND is_active = TRUE"
            if has_image:
                cur.execute(f"""
                    SELECT id, martial_art_id, name, description,
                           exercise_type, difficulty, duration_minutes,
                           sort_order, is_active, created_at, updated_at,
                           image_path
                    FROM discipline_exercises
                    WHERE martial_art_id = %s {where}
                    ORDER BY sort_order ASC, name ASC
                """, (martial_art_id,))
            else:
                cur.execute(f"""
                    SELECT id, martial_art_id, name, description,
                           exercise_type, difficulty, duration_minutes,
                           sort_order, is_active, created_at, updated_at
                    FROM discipline_exercises
                    WHERE martial_art_id = %s {where}
                    ORDER BY sort_order ASC, name ASC
                """, (martial_art_id,))
            rows = cur.fetchall()
        return [
            {
                "id": r[0], "martial_art_id": r[1], "name": r[2],
                "description": r[3], "exercise_type": r[4],
                "difficulty": r[5], "duration_minutes": r[6],
                "sort_order": r[7], "is_active": r[8],
                "created_at": r[9], "updated_at": r[10],
                "image_path": r[11] if has_image else None,
            }
            for r in rows
        ]

    def create_discipline_exercise(
        self,
        martial_art_id: int,
        data: dict,
    ) -> int:
        if not self._has_table("discipline_exercises"):
            raise ValueError("La tabla de ejercicios no existe. Ejecute la migracion.")
        name = (data.get("name") or "").strip()
        if not name:
            raise ValueError("El nombre del ejercicio es obligatorio.")
        duration = data.get("duration_minutes")
        if duration is not None:
            duration = int(duration)
            if duration <= 0:
                raise ValueError("La duracion debe ser mayor a cero.")
        sort_order = int(data.get("sort_order") or 0)
        if sort_order < 0:
            sort_order = 0
        image_path = data.get("image_path")
        has_image_col = self._has_column("discipline_exercises", "image_path")
        if image_path is not None:
            if not has_image_col:
                raise RuntimeError(
                    "La base de datos necesita la migración de imágenes para ejercicios."
                )
            image_path = str(image_path).strip() or None
        with db.transaction() as cur:
            if has_image_col:
                cur.execute("""
                    INSERT INTO discipline_exercises
                        (martial_art_id, name, description, exercise_type,
                         difficulty, duration_minutes, sort_order, is_active,
                         image_path)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    martial_art_id,
                    name,
                    data.get("description"),
                    data.get("exercise_type"),
                    data.get("difficulty"),
                    duration,
                    sort_order,
                    data.get("is_active", True),
                    image_path,
                ))
            else:
                cur.execute("""
                    INSERT INTO discipline_exercises
                        (martial_art_id, name, description, exercise_type,
                         difficulty, duration_minutes, sort_order, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    martial_art_id,
                    name,
                    data.get("description"),
                    data.get("exercise_type"),
                    data.get("difficulty"),
                    duration,
                    sort_order,
                    data.get("is_active", True),
                ))
            return cur.fetchone()[0]

    def update_discipline_exercise(
        self,
        exercise_id: int,
        data: dict,
    ) -> None:
        if not self._has_table("discipline_exercises"):
            raise ValueError("La tabla de ejercicios no existe. Ejecute la migracion.")
        name = (data.get("name") or "").strip()
        if not name:
            raise ValueError("El nombre del ejercicio es obligatorio.")
        duration = data.get("duration_minutes")
        if duration is not None:
            duration = int(duration)
            if duration <= 0:
                raise ValueError("La duracion debe ser mayor a cero.")
        sort_order = int(data.get("sort_order") or 0)
        if sort_order < 0:
            sort_order = 0
        has_image_field = "image_path" in data
        image_path = data.get("image_path")
        if has_image_field:
            image_path = str(image_path).strip() if image_path else None
        has_image_col = self._has_column("discipline_exercises", "image_path")
        if has_image_field and image_path is not None and not has_image_col:
            raise RuntimeError(
                "La base de datos necesita la migración de imágenes para ejercicios."
            )
        with db.transaction() as cur:
            if has_image_field and has_image_col:
                cur.execute("""
                    UPDATE discipline_exercises
                    SET name = %s,
                        description = %s,
                        exercise_type = %s,
                        difficulty = %s,
                        duration_minutes = %s,
                        sort_order = %s,
                        is_active = %s,
                        image_path = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (
                    name,
                    data.get("description"),
                    data.get("exercise_type"),
                    data.get("difficulty"),
                    duration,
                    sort_order,
                    data.get("is_active", True),
                    image_path,
                    exercise_id,
                ))
            else:
                cur.execute("""
                    UPDATE discipline_exercises
                    SET name = %s,
                        description = %s,
                        exercise_type = %s,
                        difficulty = %s,
                        duration_minutes = %s,
                        sort_order = %s,
                        is_active = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (
                    name,
                    data.get("description"),
                    data.get("exercise_type"),
                    data.get("difficulty"),
                    duration,
                    sort_order,
                    data.get("is_active", True),
                    exercise_id,
                ))

    def delete_discipline_exercise(self, exercise_id: int) -> None:
        if not self._has_table("discipline_exercises"):
            return
        with db.transaction() as cur:
            cur.execute(
                "DELETE FROM discipline_exercises WHERE id = %s",
                (exercise_id,),
            )

    def set_discipline_exercise_active(
        self,
        exercise_id: int,
        active: bool,
    ) -> None:
        if not self._has_table("discipline_exercises"):
            return
        with db.transaction() as cur:
            cur.execute("""
                UPDATE discipline_exercises
                SET is_active = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (active, exercise_id))

    def get_discipline_summary(self, martial_art_id: int) -> dict:
        has_ex = self._has_table("discipline_exercises")
        with db.cursor() as cur:
            schedule_q = """
                (SELECT COUNT(*) FROM schedule
                 WHERE id_martial_art = %s AND LOWER(status) = 'active')
            """
            exercise_q = """
                (SELECT 0)
            """ if not has_ex else """
                (SELECT COUNT(*) FROM discipline_exercises
                 WHERE martial_art_id = %s AND is_active = TRUE)
            """
            level_q = """
                (SELECT COUNT(*) FROM belts
                 WHERE id_martial_art = %s AND is_active = TRUE)
            """
            if has_ex:
                cur.execute(f"""
                    SELECT {schedule_q}, {exercise_q}, {level_q}
                """, (martial_art_id, martial_art_id, martial_art_id))
            else:
                cur.execute(f"""
                    SELECT {schedule_q}, {exercise_q}, {level_q}
                """, (martial_art_id, martial_art_id))
            r = cur.fetchone()
            return {
                "active_schedule_count": r[0] if r else 0,
                "exercise_count": r[1] if r else 0,
                "level_count": r[2] if r else 0,
            }

    # ═══════════════════════════════════════════════════════════════════
    # Backward-compatible aliases
    # ═══════════════════════════════════════════════════════════════════

    def get_next_belts(
        self, martial_art_id: int, current_orden: int
    ) -> list[dict]:
        """Deprecated: use get_allowed_promotion_levels instead."""
        warnings.warn(
            "get_next_belts is deprecated; use get_allowed_promotion_levels.",
            DeprecationWarning,
            stacklevel=2,
        )
        all_levels = self.get_belts(martial_art_id)
        if current_orden == 0:
            return all_levels
        return [lv for lv in all_levels if (lv.get("orden") or 0) > current_orden]
