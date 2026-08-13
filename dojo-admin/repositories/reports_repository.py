# ─── REPORTS_REPOSITORY ──────────────────────────────────────────────
# Consultas para Reportes: General, Finanzas, Clases, Estudiantes

from database.connection import db


class ReportsRepository:

    # ── GENERAL ──────────────────────────────────────────────────────

    def get_general_kpis(self) -> dict:
        with db.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM students")
            total_students = cur.fetchone()[0] or 0

            cur.execute("""
                SELECT COUNT(*) FROM students s
                JOIN status st ON st.id = s.id_status
                WHERE LOWER(st.status) = 'activo'
            """)
            active_students = cur.fetchone()[0] or 0

            cur.execute("SELECT COUNT(*) FROM classes")
            total_classes = cur.fetchone()[0] or 0

            cur.execute("SELECT COUNT(*) FROM attendance")
            total_attendance = cur.fetchone()[0] or 0

            cur.execute("""
                SELECT COALESCE(SUM(total), 0) FROM finance_income
                WHERE EXTRACT(YEAR FROM income_date) = EXTRACT(YEAR FROM CURRENT_DATE)
                  AND EXTRACT(MONTH FROM income_date) = EXTRACT(MONTH FROM CURRENT_DATE)
            """)
            monthly_income = float(cur.fetchone()[0] or 0)

            cur.execute("""
                SELECT COALESCE(SUM(amount), 0) FROM finance_expenses
                WHERE EXTRACT(YEAR FROM expense_date) = EXTRACT(YEAR FROM CURRENT_DATE)
                  AND EXTRACT(MONTH FROM expense_date) = EXTRACT(MONTH FROM CURRENT_DATE)
            """)
            monthly_expenses = float(cur.fetchone()[0] or 0)

            cur.execute("""
                SELECT COUNT(*), COALESCE(SUM(pending_amount), 0)
                FROM finance_receivables WHERE status = 'open'
            """)
            row = cur.fetchone()
            open_receivables_count = row[0] or 0
            open_receivables_amount = float(row[1] or 0)

            cur.execute("SELECT COUNT(*) FROM products WHERE stock <= 5")
            low_stock_count = cur.fetchone()[0] or 0

            return {
                "total_students": total_students,
                "active_students": active_students,
                "total_classes": total_classes,
                "total_attendance": total_attendance,
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "monthly_balance": monthly_income - monthly_expenses,
                "open_receivables_count": open_receivables_count,
                "open_receivables_amount": open_receivables_amount,
                "low_stock_count": low_stock_count,
            }

    def get_general_chart_6m(self) -> list:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    EXTRACT(YEAR FROM cl.date)::int AS yr,
                    EXTRACT(MONTH FROM cl.date)::int AS mo,
                    COUNT(DISTINCT a.id_student) AS total
                FROM attendance a
                JOIN classes cl ON cl.id = a.id_class
                WHERE cl.date >= (CURRENT_DATE - INTERVAL '6 months')
                GROUP BY yr, mo
                ORDER BY yr, mo
            """)
            return [{"year": r[0], "month": r[1], "total": r[2]}
                    for r in cur.fetchall()]

    def get_general_alerts(self) -> dict:
        with db.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*), COALESCE(SUM(pending_amount), 0)
                FROM finance_receivables WHERE status = 'open'
            """)
            row = cur.fetchone()
            open_receivables = {"count": row[0] or 0, "amount": float(row[1] or 0)}

            cur.execute("""
                SELECT id, name, stock FROM products
                WHERE stock <= 5 ORDER BY stock ASC
            """)
            low_stock = [{"id": r[0], "name": r[1], "stock": r[2]}
                        for r in cur.fetchall()]

            cur.execute("""
                SELECT id, name, event_date, event_type, color
                FROM events WHERE event_date >= CURRENT_DATE
                ORDER BY event_date ASC LIMIT 5
            """)
            upcoming_events = [{"id": r[0], "name": r[1], "date": r[2],
                               "type": r[3], "color": r[4]}
                              for r in cur.fetchall()]

            cur.execute("""
                SELECT c.id, c.date, c.status,
                       COALESCE(s.name, '') AS schedule_name,
                       (SELECT COUNT(*) FROM attendance a WHERE a.id_class = c.id) AS attendees,
                       COALESCE(s.capacity, 0) AS capacity
                FROM classes c
                LEFT JOIN schedule s ON s.id = c.id_schedule
                ORDER BY c.date DESC, c.id DESC LIMIT 5
            """)
            recent_classes = [{"id": r[0], "date": r[1], "status": r[2],
                              "schedule_name": r[3], "attendees": r[4],
                              "capacity": r[5]}
                             for r in cur.fetchall()]

            return {
                "open_receivables": open_receivables,
                "low_stock": low_stock,
                "upcoming_events": upcoming_events,
                "recent_classes": recent_classes,
            }

    # ── FINANCE ──────────────────────────────────────────────────────

    def get_finance_summary(self, start_date=None, end_date=None) -> dict:
        with db.cursor() as cur:
            where_inc = ["1=1"]
            where_exp = ["1=1"]
            params_inc = []
            params_exp = []

            if start_date:
                where_inc.append("income_date >= %s")
                params_inc.append(start_date)
                where_exp.append("expense_date >= %s")
                params_exp.append(start_date)
            if end_date:
                where_inc.append("income_date <= %s")
                params_inc.append(end_date)
                where_exp.append("expense_date <= %s")
                params_exp.append(end_date)

            # Ingresos por fuente
            cur.execute(f"""
                SELECT COALESCE(fi2.item_type, 'Otro') AS source,
                       COALESCE(SUM(fi2.subtotal), 0) AS total,
                       COUNT(*) AS count
                FROM finance_income_items fi2
                JOIN finance_income fi ON fi.id = fi2.income_id
                WHERE {' AND '.join(where_inc)}
                GROUP BY fi2.item_type ORDER BY total DESC
            """, params_inc)
            income_by_source = [{"source": r[0], "total": float(r[1]),
                                "count": r[2]} for r in cur.fetchall()]

            # Egresos por categoría
            cur.execute(f"""
                SELECT COALESCE(fec.name, 'Sin categoría') AS category,
                       COALESCE(SUM(fe.amount), 0) AS total,
                       COUNT(*) AS count
                FROM finance_expenses fe
                LEFT JOIN finance_expense_categories fec ON fec.id = fe.category_id
                WHERE {' AND '.join(where_exp)}
                GROUP BY fec.name ORDER BY total DESC
            """, params_exp)
            expenses_by_category = [{"category": r[0], "total": float(r[1]),
                                    "count": r[2]} for r in cur.fetchall()]

            # Totales
            cur.execute(f"""
                SELECT COALESCE(SUM(total), 0) FROM finance_income
                WHERE {' AND '.join(where_inc)}
            """, params_inc)
            total_income = float(cur.fetchone()[0] or 0)

            cur.execute(f"""
                SELECT COALESCE(SUM(amount), 0) FROM finance_expenses
                WHERE {' AND '.join(where_exp)}
            """, params_exp)
            total_expenses = float(cur.fetchone()[0] or 0)

            # Cartera
            where_rec = ["status = 'open'"]
            params_rec = []
            if start_date:
                where_rec.append("created_at >= %s")
                params_rec.append(start_date)
            if end_date:
                where_rec.append("created_at <= %s")
                params_rec.append(end_date)

            cur.execute(f"""
                SELECT COUNT(*), COALESCE(SUM(pending_amount), 0)
                FROM finance_receivables WHERE {' AND '.join(where_rec)}
            """, params_rec)
            row = cur.fetchone()
            receivables_count = row[0] or 0
            receivables_amount = float(row[1] or 0)

            # Cuentas de cobro
            where_cc = ["1=1"]
            params_cc = []
            if start_date:
                where_cc.append("issued_date >= %s")
                params_cc.append(start_date)
            if end_date:
                where_cc.append("issued_date <= %s")
                params_cc.append(end_date)

            cur.execute(f"""
                SELECT COUNT(*), COALESCE(SUM(total_amount), 0)
                FROM collection_accounts WHERE {' AND '.join(where_cc)}
            """, params_cc)
            row_cc = cur.fetchone()
            collection_count = row_cc[0] or 0
            collection_amount = float(row_cc[1] or 0)

            return {
                "total_income": total_income,
                "total_expenses": total_expenses,
                "balance": total_income - total_expenses,
                "income_by_source": income_by_source,
                "expenses_by_category": expenses_by_category,
                "receivables_count": receivables_count,
                "receivables_amount": receivables_amount,
                "collection_count": collection_count,
                "collection_amount": collection_amount,
            }

    def get_finance_vs(self, period_a_start, period_a_end,
                       period_b_start, period_b_end) -> dict:
        """Comparativo VS entre dos períodos."""
        with db.cursor() as cur:
            def _fetch_period(s, e):
                cur.execute("""
                    SELECT COALESCE(SUM(total), 0) FROM finance_income
                    WHERE income_date >= %s AND income_date <= %s
                """, (s, e))
                inc = float(cur.fetchone()[0] or 0)

                cur.execute("""
                    SELECT COALESCE(SUM(amount), 0) FROM finance_expenses
                    WHERE expense_date >= %s AND expense_date <= %s
                """, (s, e))
                exp = float(cur.fetchone()[0] or 0)

                cur.execute("""
                    SELECT COUNT(*), COALESCE(SUM(pending_amount), 0)
                    FROM finance_receivables
                    WHERE status = 'open' AND created_at >= %s AND created_at <= %s
                """, (s, e))
                row = cur.fetchone()
                rec_count = row[0] or 0
                rec_amount = float(row[1] or 0)

                cur.execute("""
                    SELECT COUNT(*), COALESCE(SUM(total_amount), 0)
                    FROM collection_accounts
                    WHERE issued_date >= %s AND issued_date <= %s
                """, (s, e))
                row_cc = cur.fetchone()
                cc_count = row_cc[0] or 0
                cc_amount = float(row_cc[1] or 0)

                return {
                    "income": inc, "expenses": exp, "balance": inc - exp,
                    "receivables_count": rec_count, "receivables_amount": rec_amount,
                    "collection_count": cc_count, "collection_amount": cc_amount,
                }

            a = _fetch_period(period_a_start, period_a_end)
            b = _fetch_period(period_b_start, period_b_end)

            def _pct(new, old):
                if old == 0:
                    return 100.0 if new > 0 else 0.0
                return ((new - old) / abs(old)) * 100

            analysis = {}
            for key in ["income", "expenses", "balance", "receivables_amount", "collection_amount"]:
                analysis[key] = {
                    "period_a": a[key], "period_b": b[key],
                    "change": b[key] - a[key],
                    "pct_change": round(_pct(b[key], a[key]), 1),
                    "trend": "up" if b[key] > a[key] else ("down" if b[key] < a[key] else "same"),
                }

            return {"period_a": a, "period_b": b, "analysis": analysis}

    def get_finance_monthly_series(self, months=6) -> list:
        with db.cursor() as cur:
            cur.execute("""
                SELECT
                    EXTRACT(YEAR FROM income_date)::int AS yr,
                    EXTRACT(MONTH FROM income_date)::int AS mo,
                    COALESCE(SUM(total), 0) AS income
                FROM finance_income
                WHERE income_date >= (CURRENT_DATE - INTERVAL '%s months')
                GROUP BY yr, mo ORDER BY yr, mo
            """, (months,))
            income_rows = {r[1]: {"year": r[0], "month": r[1], "income": float(r[2])}
                          for r in cur.fetchall()}

            cur.execute("""
                SELECT
                    EXTRACT(YEAR FROM expense_date)::int AS yr,
                    EXTRACT(MONTH FROM expense_date)::int AS mo,
                    COALESCE(SUM(amount), 0) AS expenses
                FROM finance_expenses
                WHERE expense_date >= (CURRENT_DATE - INTERVAL '%s months')
                GROUP BY yr, mo ORDER BY yr, mo
            """, (months,))
            expense_rows = {r[1]: {"expenses": float(r[2])} for r in cur.fetchall()}

            all_months = sorted(set(list(income_rows.keys()) + list(expense_rows.keys())))
            result = []
            for mo in all_months:
                inc = income_rows.get(mo, {"year": 2026, "month": mo, "income": 0})
                exp = expense_rows.get(mo, {"expenses": 0})
                result.append({
                    "year": inc["year"], "month": mo,
                    "income": inc["income"],
                    "expenses": exp["expenses"],
                    "balance": inc["income"] - exp["expenses"],
                })
            return result

    # ── CLASSES ──────────────────────────────────────────────────────

    def get_classes_report(self, start_date=None, end_date=None) -> dict:
        with db.cursor() as cur:
            where = ["1=1"]
            params = []
            if start_date:
                where.append("cl.date >= %s")
                params.append(start_date)
            if end_date:
                where.append("cl.date <= %s")
                params.append(end_date)

            where_sql = " AND ".join(where)

            cur.execute(f"""
                SELECT COUNT(*) FROM classes cl WHERE {where_sql}
            """, params)
            total = cur.fetchone()[0] or 0

            cur.execute(f"""
                SELECT COUNT(*) FROM classes cl
                WHERE {where_sql} AND cl.status = 'completed'
            """, params)
            completed = cur.fetchone()[0] or 0

            cur.execute(f"""
                SELECT COUNT(*) FROM classes cl
                WHERE {where_sql} AND cl.status = 'cancelled'
            """, params)
            cancelled = cur.fetchone()[0] or 0

            scheduled = total - completed - cancelled

            # Asistencia promedio
            cur.execute(f"""
                SELECT COALESCE(AVG(cnt), 0) FROM (
                    SELECT COUNT(*) AS cnt
                    FROM attendance a
                    JOIN classes cl ON cl.id = a.id_class
                    WHERE {where_sql}
                    GROUP BY a.id_class
                ) sub
            """, params)
            avg_attendance = float(cur.fetchone()[0] or 0)

            # Por mes
            cur.execute(f"""
                SELECT EXTRACT(YEAR FROM cl.date)::int AS yr,
                       EXTRACT(MONTH FROM cl.date)::int AS mo,
                       COUNT(*) AS cnt
                FROM classes cl WHERE {where_sql}
                GROUP BY yr, mo ORDER BY yr, mo
            """, params)
            monthly = [{"year": r[0], "month": r[1], "count": r[2]}
                      for r in cur.fetchall()]

            # Por arte marcial
            cur.execute(f"""
                SELECT COALESCE(ma.name, 'Sin asignar') AS martial_art,
                       COUNT(DISTINCT cl.id) AS classes_count
                FROM classes cl
                LEFT JOIN schedule s ON s.id = cl.id_schedule
                LEFT JOIN martial_arts ma ON ma.id = s.id_martial_art
                WHERE {where_sql}
                GROUP BY ma.name ORDER BY classes_count DESC
            """, params)
            by_martial_art = [{"martial_art": r[0], "count": r[1]}
                             for r in cur.fetchall()]

            # Por instructor
            cur.execute(f"""
                SELECT COALESCE(
                    p.first_name || ' ' || p.last_name, 'Sin asignar'
                ) AS instructor,
                COUNT(DISTINCT cl.id) AS classes_count
                FROM classes cl
                LEFT JOIN schedule sc ON sc.id = cl.id_schedule
                LEFT JOIN instructors i ON i.id = sc.id_instructor
                LEFT JOIN people p ON p.id = i.id_person
                WHERE {where_sql}
                GROUP BY instructor ORDER BY classes_count DESC
            """, params)
            by_instructor = [{"instructor": r[0], "count": r[1]}
                            for r in cur.fetchall()]

            # Detalle de clases
            cur.execute(f"""
                SELECT cl.id, cl.date, cl.status,
                       COALESCE(s.name, '') AS schedule_name,
                       COALESCE(ma.name, '') AS martial_art,
                       COALESCE(
                           p.first_name || ' ' || p.last_name, '—'
                       ) AS instructor,
                       (SELECT COUNT(*) FROM attendance a WHERE a.id_class = cl.id) AS attendees,
                       COALESCE(s.capacity, 0) AS capacity
                FROM classes cl
                LEFT JOIN schedule s ON s.id = cl.id_schedule
                LEFT JOIN martial_arts ma ON ma.id = s.id_martial_art
                LEFT JOIN instructors i ON i.id = s.id_instructor
                LEFT JOIN people p ON p.id = i.id_person
                WHERE {where_sql}
                ORDER BY cl.date DESC
            """, params)
            detail = [{"id": r[0], "date": r[1], "status": r[2],
                       "schedule_name": r[3], "martial_art": r[4],
                       "instructor": r[5], "attendees": r[6],
                       "capacity": r[7]} for r in cur.fetchall()]

            return {
                "total": total, "completed": completed,
                "cancelled": cancelled, "scheduled": scheduled,
                "avg_attendance": avg_attendance,
                "monthly": monthly,
                "by_martial_art": by_martial_art,
                "by_instructor": by_instructor,
                "detail": detail,
            }

    # ── STUDENTS ─────────────────────────────────────────────────────

    def get_students_report(self, start_date=None, end_date=None) -> dict:
        with db.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM students")
            total = cur.fetchone()[0] or 0

            cur.execute("""
                SELECT COUNT(*) FROM students s
                JOIN status st ON st.id = s.id_status
                WHERE LOWER(st.status) = 'activo'
            """)
            active = cur.fetchone()[0] or 0

            inactive = total - active

            where = ["1=1"]
            params = []
            if start_date:
                where.append("s.joined_date >= %s")
                params.append(start_date)
            if end_date:
                where.append("s.joined_date <= %s")
                params.append(end_date)
            where_sql = " AND ".join(where)

            cur.execute(f"""
                SELECT COUNT(*) FROM students s WHERE {where_sql}
            """, params)
            new_in_period = cur.fetchone()[0] or 0

            # Nuevos por mes
            cur.execute(f"""
                SELECT EXTRACT(YEAR FROM s.joined_date)::int AS yr,
                       EXTRACT(MONTH FROM s.joined_date)::int AS mo,
                       COUNT(*) AS cnt
                FROM students s WHERE {where_sql}
                GROUP BY yr, mo ORDER BY yr, mo
            """, params)
            monthly_new = [{"year": r[0], "month": r[1], "count": r[2]}
                          for r in cur.fetchall()]

            # Por categoría
            cur.execute(f"""
                SELECT COALESCE(c.name, 'Sin categoría') AS category,
                       COUNT(*) AS cnt
                FROM students s
                LEFT JOIN categories c ON c.id = s.category_id
                WHERE {where_sql}
                GROUP BY c.name ORDER BY cnt DESC
            """, params)
            by_category = [{"category": r[0], "count": r[1]}
                          for r in cur.fetchall()]

            # Por arte marcial (via belt)
            cur.execute(f"""
                SELECT COALESCE(ma.name, 'Sin asignar') AS martial_art,
                       COUNT(*) AS cnt
                FROM students s
                LEFT JOIN students_belts sb ON sb.id_student = s.id
                LEFT JOIN belts b ON b.id = sb.id_belt
                LEFT JOIN martial_arts ma ON ma.id = b.id_martial_art
                WHERE {where_sql}
                GROUP BY ma.name ORDER BY cnt DESC
            """, params)
            by_martial_art = [{"martial_art": r[0], "count": r[1]}
                             for r in cur.fetchall()]

            # Estado de membresías (via category plan)
            cur.execute("""
                SELECT COALESCE(c.name, 'Sin categoría') AS category,
                       COUNT(*) AS cnt
                FROM students s
                JOIN status st ON st.id = s.id_status
                LEFT JOIN categories c ON c.id = s.category_id
                WHERE LOWER(st.status) = 'activo'
                GROUP BY c.name ORDER BY cnt DESC
            """)
            membership_status = [{"category": r[0], "count": r[1]}
                                for r in cur.fetchall()]

            # Detalle nuevos en período
            cur.execute(f"""
                SELECT s.id,
                       p.first_name || ' ' || p.last_name AS name,
                       s.joined_date,
                       COALESCE(c.name, '—') AS category,
                       COALESCE(st.status, '—') AS status
                FROM students s
                JOIN people p ON p.id = s.id_person
                LEFT JOIN categories c ON c.id = s.category_id
                LEFT JOIN status st ON st.id = s.id_status
                WHERE {where_sql}
                ORDER BY s.joined_date DESC
            """, params)
            new_students_detail = [
                {"id": r[0], "name": r[1], "joined_date": r[2],
                 "category": r[3], "status": r[4]}
                for r in cur.fetchall()
            ]

            return {
                "total": total, "active": active, "inactive": inactive,
                "new_in_period": new_in_period,
                "monthly_new": monthly_new,
                "by_category": by_category,
                "by_martial_art": by_martial_art,
                "membership_status": membership_status,
                "new_students_detail": new_students_detail,
            }


reports_repo = ReportsRepository()
