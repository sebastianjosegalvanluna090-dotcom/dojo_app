# ─── ESTUDENTS_VIEW ─────────────────────────────────────────────

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QMessageBox, QDialog,
    QFormLayout, QScrollArea, QSizePolicy, QFileDialog,
    QGraphicsOpacityEffect, QComboBox, QAbstractItemView,
    QGraphicsDropShadowEffect, QGraphicsBlurEffect,
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QEvent,
    QPropertyAnimation, QEasingCurve, QRect, QRectF, QPointF
)
from PyQt6.QtGui import QColor, QPixmap, QPainter, QPainterPath, QFont, QPen
from datetime import date

from repositories.student_repository import StudentRepository
from views.student_form import StudentForm
from core.i18n import tr, trf

# ─── PALETA ───────────────────────────────────────────────────────────
BG_MAIN    = "#0D0D0D"
BG_CARD    = "#161616"
BG_TABLE   = "#121212"
BORDER     = "#2A2A2A"
RED        = "#C8102E"
RED_DARK   = "#7A0A1C"
TEXT_PRI   = "#F0F0F0"
TEXT_SEC   = "#888888"
TEXT_MUT   = "#444444"
GREEN      = "#22C55E"
BLUE       = "#3B82F6"
YELLOW     = "#EAB308"


# ─── Helpers de edad y antigüedad ──────────────────────────────────────
def calculate_age(birthdate):
    if not birthdate:
        return "—"

    today = date.today()
    years = today.year - birthdate.year

    if (today.month, today.day) < (birthdate.month, birthdate.day):
        years -= 1

    return f"{years} años"


def calculate_tenure(joined_date):
    if not joined_date:
        return "—"

    today = date.today()
    months = (today.year - joined_date.year) * 12 + (today.month - joined_date.month)

    if today.day < joined_date.day:
        months -= 1

    months = max(0, months)

    years = months // 12
    rest = months % 12

    if years == 0:
        return f"{rest} mes{'es' if rest != 1 else ''}"

    if rest == 0:
        return f"{years} año{'s' if years != 1 else ''}"

    return f"{years} año{'s' if years != 1 else ''}, {rest} mes{'es' if rest != 1 else ''}"


def format_money(value):
    if value is None:
        return "$0"
    try:
        val = float(value)
        if val == int(val):
            return f"${int(val):,}".replace(",", ".")
        return f"${val:,.2f}".replace(",", ".")
    except (ValueError, TypeError):
        return "$0"


# ─── Widgets visuales premium ────────────────────────────────────────────

class InitialsAvatar(QLabel):
    def __init__(self, name="", size=36, color=BLUE, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parts = [p for p in (name or "").split() if p]
        initials = "".join(p[0].upper() for p in parts[:2]) or "?"
        self.setText(initials)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: #222222;
                color: {color};
                border-radius: {size // 2}px;
                border: 1px solid #333333;
                font-size: {max(11, size // 4)}px;
                font-weight: 900;
            }}
        """)


class StatusBadge(QLabel):
    def __init__(self, status="", parent=None):
        super().__init__(parent)
        s = (status or "—").upper()
        self.setText(s)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if s in ("ACTIVE", "ACTIVO"):
            bg = "#0A2A0A"
            fg = GREEN
            border_c = "rgba(34,197,94,0.35)"
        elif s in ("INACTIVE", "INACTIVO", "RETIRED", "RETIRADO", "Inactive"):
            bg = "#2A0A0A"
            fg = "#FF4444"
            border_c = "rgba(255,68,68,0.35)"
        else:
            bg = "#2A210A"
            fg = YELLOW
            border_c = "rgba(234,179,8,0.35)"

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border_c};
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: 900;
                letter-spacing: 0.8px;
            }}
        """)


class BeltWidget(QWidget):
    def __init__(
        self,
        color="#FFFFFF",
        pre_color=None,
        grades=0,
        grade_color="#FFFFFF",
        martial_art="",
        parent=None
    ):
        super().__init__(parent)
        self.color = color or "#FFFFFF"
        self.pre_color = pre_color
        self.grades = int(grades or 0)
        self.grade_color = grade_color or "#FFFFFF"
        self.martial_art = martial_art or ""
        self.setFixedSize(110, 20)

    def _is_light(self, hex_color):
        try:
            c = QColor(hex_color)
            return (c.red() * 0.299 + c.green() * 0.587 + c.blue() * 0.114) > 180
        except Exception:
            return False

    def _is_bjj(self):
        n = (self.martial_art or "").strip().lower()
        return n in {
            "brazilian jiu-jitsu",
            "bjj",
            "jiu-jitsu brasile\u00f1o",
            "jiu jitsu brasile\u00f1o",
            "brazilian jiu jitsu"
        }

    def _border_color(self):
        light_colors = {
            "#FFFFFF", "#FFD700", "#FF8C00",
            "#FFFF00", "#FFA500", "#FFFACD",
            "#E8E8E8"
        }
        if (self.color or "").upper() in light_colors:
            return "#999999"
        if self._is_light(self.color):
            return "#999999"
        return "#333333"

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(1, 1, -1, -1)

        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 4, 4)

        p.save()
        p.setClipPath(path)

        p.fillPath(path, QColor(self.color))

        if self.pre_color:
            stripe_w = max(7, min(11, rect.width() // 10))
            right_padding = max(10, rect.width() // 10)

            stripe_x = rect.right() - right_padding - stripe_w

            stripe_rect = QRect(
                stripe_x,
                rect.y(),
                stripe_w,
                rect.height()
            )

            p.fillRect(stripe_rect, QColor(self.pre_color))

        elif self._is_bjj():
            tip_w = 38
            tip_rect = QRect(
                rect.right() - tip_w,
                rect.y(),
                tip_w,
                rect.height()
            )

            tip_color = QColor("#111111")
            if not self._is_light(self.color):
                tip_color = QColor(RED)

            p.fillRect(tip_rect, tip_color)

            count = min(max(self.grades, 0), 4)
            stripe_w = 4
            gap = 3
            start_x = tip_rect.right() - 6 - ((stripe_w + gap) * count)

            for i in range(count):
                x = start_x + i * (stripe_w + gap)
                stripe_rect = QRect(
                    x,
                    tip_rect.y() + 2,
                    stripe_w,
                    tip_rect.height() - 4
                )
                p.fillRect(stripe_rect, QColor(self.grade_color or "#FFFFFF"))

        elif self.grades:
            count = min(max(self.grades, 0), 4)
            stripe_w = 4
            gap = 4
            total_w = count * stripe_w + max(0, count - 1) * gap
            start_x = rect.right() - total_w - 8

            for i in range(count):
                x = start_x + i * (stripe_w + gap)
                stripe_rect = QRect(
                    x,
                    rect.y() + 2,
                    stripe_w,
                    rect.height() - 4
                )
                p.fillRect(stripe_rect, QColor(self.grade_color or "#FFFFFF"))

        p.restore()

        p.setPen(QColor(self._border_color()))
        p.drawRoundedRect(QRectF(rect), 4, 4)


class IconLabel(QWidget):
    ICONS = {
        "students": '<circle cx="9" cy="7" r="4"/><polyline points="3 21 3 19 5 15 9 14 13 15 15 19 15 21"/><line x1="16" y1="11" x2="20" y2="11"/><line x1="20" y1="8" x2="23" y2="11"/><line x1="23" y1="11" x2="20" y2="14"/>',
        "phone":    '<rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12.01" y2="18"/>',
        "mail":     '<rect x="2" y="4" width="20" height="16" rx="2"/><polyline points="2 8 12 13 22 8"/>',
        "trash":    '<polyline points="3 6 21 6"/><polyline points="8 6 8 3 16 3 16 6"/><rect x="5" y="6" width="14" height="15" rx="1"/><line x1="10" y1="10" x2="10" y2="17"/><line x1="14" y1="10" x2="14" y2="17"/>',
        "search":   '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
        "eye":      '<ellipse cx="12" cy="12" rx="10" ry="6"/><circle cx="12" cy="12" r="3"/><line x1="12" y1="9" x2="12" y2="15"/><line x1="9" y1="12" x2="15" y2="12"/>',
        "edit":     '<polyline points="14 2 14 8 20 8"/><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="13" y2="17"/>',
    }

    def __init__(self, icon_name: str, size: int = 18, color: str = TEXT_SEC, parent=None):
        super().__init__(parent)
        self._icon_name = icon_name
        self._size = size
        self._color = color
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        import re as _re
        path_data = self.ICONS.get(self._icon_name)
        if not path_data:
            return
        try:
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            scale = self._size / 24.0
            p.scale(scale, scale)
            pen = QPen(QColor(self._color))
            pen.setWidthF(1.8)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            elements = _re.findall(r'<(circle|rect|line|polyline|path|ellipse)\s([^/]+)/?>', path_data)
            for tag, attrs_str in elements:
                attrs = dict(_re.findall(r'(\w+)="([^"]*)"', attrs_str))
                if tag == "circle":
                    cx, cy, r = float(attrs.get("cx", 0)), float(attrs.get("cy", 0)), float(attrs.get("r", 0))
                    p.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))
                elif tag == "ellipse":
                    cx = float(attrs.get("cx", 0))
                    cy = float(attrs.get("cy", 0))
                    rx = float(attrs.get("rx", 0))
                    ry = float(attrs.get("ry", 0))
                    p.drawEllipse(QRectF(cx - rx, cy - ry, rx * 2, ry * 2))
                elif tag == "rect":
                    x, y = float(attrs.get("x", 0)), float(attrs.get("y", 0))
                    w, h = float(attrs.get("width", 0)), float(attrs.get("height", 0))
                    rx = float(attrs.get("rx", 0))
                    rect = QRectF(x, y, w, h)
                    p.drawRoundedRect(rect, rx, rx) if rx > 0 else p.drawRect(rect)
                elif tag == "line":
                    p.drawLine(QPointF(float(attrs.get("x1", 0)), float(attrs.get("y1", 0))),
                               QPointF(float(attrs.get("x2", 0)), float(attrs.get("y2", 0))))
                elif tag == "polyline":
                    pts = _re.findall(r'[\d.]+', attrs.get("points", ""))
                    if len(pts) >= 2 and len(pts) % 2 == 0:
                        path = QPainterPath()
                        path.moveTo(float(pts[0]), float(pts[1]))
                        for i in range(2, len(pts), 2):
                            path.lineTo(float(pts[i]), float(pts[i + 1]))
                        p.drawPath(path)
                elif tag == "path":
                    d = attrs.get("d", "")
                    pts = _re.findall(r'[MLCQZ][\d\s,.\-]+', d, _re.IGNORECASE)
                    path = QPainterPath()
                    for cmd in pts:
                        cmd = cmd.strip()
                        if not cmd:
                            continue
                        letter = cmd[0]
                        nums = [float(x) for x in _re.findall(r'[\d.\-]+', cmd[1:])]
                        if letter in ("M", "m") and len(nums) >= 2:
                            path.moveTo(nums[0], nums[1])
                        elif letter in ("L", "l") and len(nums) >= 2:
                            path.lineTo(nums[0], nums[1])
                        elif letter in ("C", "c") and len(nums) >= 6:
                            path.cubicTo(nums[0], nums[1], nums[2], nums[3], nums[4], nums[5])
                        elif letter in ("Q", "q") and len(nums) >= 4:
                            path.quadTo(nums[0], nums[1], nums[2], nums[3])
                        elif letter in ("Z", "z"):
                            path.closeSubpath()
                    p.drawPath(path)
            p.end()
        except Exception:
            pass


# ─── Worker ───────────────────────────────────────────────────────────
class LoadWorker(QThread):
    done = pyqtSignal(list)

    def __init__(self, repo, search=""):
        super().__init__()
        self.repo = repo
        self.search = search

    def run(self):
        try:
            rows = self.repo.get_all(self.search)
            self.done.emit(rows or [])
        except Exception as e:
            print(f"[StudentsView LoadWorker error] {e}")
            self.done.emit([])

# ─── DETALLE AMPLIADO ─────────────────────────────────────────────────
class StudentDetail(QDialog):
    def __init__(self, student_id, repo, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.repo = repo
        self.setWindowTitle("Detalle del Estudiante")
        self.setMinimumSize(860, 680)
        self.resize(940, 780)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setStyleSheet("background-color: #111111; color: #F0F0F0;")

        # ── Carga de datos ────────────────────────────────────────────
        data          = self.repo.get_full_profile(student_id)
        health        = self.repo.get_health_info(student_id)
        recent_classes = self.repo.get_recent_classes(student_id, 5)
        current_belts  = self.repo.get_current_belts(student_id)
        belt_history   = self.repo.get_belt_history(student_id, 8)
        last_payments  = self.repo.get_last_payments_for_student(student_id, 5)
        guardian       = self.repo.get_primary_guardian(student_id)
        emergency      = self.repo.get_primary_emergency_contact(student_id)
        photo_path     = self.repo.get_photo(student_id)

        age_text      = calculate_age(data.get("birthdate") if data else None)
        tenure_text   = calculate_tenure(data.get("joined_date") if data else None)
        category      = (data.get("category_name") or "").upper() if data else ""
        status_name   = data.get("status_name") or "" if data else ""
        is_minor      = category in ("KID", "YOUTH")
        name          = f"{data.get('first_name') or ''} {data.get('last_name') or ''}".strip() if data else "?"

        # ── Layout raíz ───────────────────────────────────────────────
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: #080808; width: 8px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #333; border-radius: 4px; min-height: 26px; }
            QScrollBar::handle:vertical:hover { background: #444; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
        """)

        container = QWidget()
        container.setStyleSheet("background-color: #111111;")
        body = QVBoxLayout(container)
        body.setContentsMargins(24, 22, 24, 28)
        body.setSpacing(16)
        scroll.setWidget(container)
        root.addWidget(scroll, 1)

        # ── Cabecera premium ──────────────────────────────────────────
        doc_str  = data.get("document") or "—" if data else "—"
        type_doc = data.get("type_document") or ""

        _sn_lower = (status_name or "").lower()
        if "activo" in _sn_lower or "active" in _sn_lower:
            badge_color, badge_bg, badge_dot = GREEN, "#0A2A0A", "●"
        elif "inactivo" in _sn_lower or "inactive" in _sn_lower or "retirado" in _sn_lower:
            badge_color, badge_bg, badge_dot = "#FF4444", "#2A0A0A", "●"
        else:
            badge_color, badge_bg, badge_dot = YELLOW, "#2A210A", "●"

        # Wrapper del header con fondo degradado sutil
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #1C1C1C, stop:1 #111111);
                border: 1px solid #2A2A2A;
                border-radius: 14px;
            }}
            QFrame * {{ background: transparent; border: none; }}
        """)
        hdr_inner = QHBoxLayout(hdr_frame)
        hdr_inner.setContentsMargins(20, 18, 20, 18)
        hdr_inner.setSpacing(18)

        # Foto / avatar
        self.lbl_photo = QLabel()
        self.lbl_photo.setFixedSize(72, 72)
        self.lbl_photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_photo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_photo.setToolTip("Clic para cambiar foto")
        self.lbl_photo.setStyleSheet(
            "background-color: #1A1A1A; color: #C8102E; font-size: 20px; font-weight: 700; border-radius: 36px;"
            " border: 2px solid #333333;"
        )
        self._set_photo(photo_path, name)
        self.lbl_photo.mousePressEvent = lambda _: self._change_photo()

        # Columna de nombre
        name_col = QVBoxLayout()
        name_col.setSpacing(5)

        lbl_name = QLabel(name or "—")
        lbl_name.setStyleSheet(
            "font-size: 20px; font-weight: 800; color: #F5F5F5; letter-spacing: 0.3px;"
        )

        lbl_sub = QLabel(
            f"ID: {data.get('id') if data else '—'}  ·  {type_doc}: {doc_str}  ·  {category}"
        )
        lbl_sub.setStyleSheet("font-size: 11px; color: #555555; font-weight: 600;")

        # Mini-stats en línea
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        for _icon, _val, _col in [
            ("◷", tenure_text, YELLOW),
            ("♦", age_text, BLUE),
        ]:
            _w = QWidget()
            _w.setStyleSheet("background: transparent;")
            _hl = QHBoxLayout(_w)
            _hl.setContentsMargins(0, 0, 0, 0)
            _hl.setSpacing(4)
            _ico = QLabel(_icon)
            _ico.setStyleSheet(f"color: {_col}; font-size: 11px;")
            _val_lbl = QLabel(_val)
            _val_lbl.setStyleSheet(f"color: {_col}; font-size: 11px; font-weight: 700;")
            _hl.addWidget(_ico)
            _hl.addWidget(_val_lbl)
            stats_row.addWidget(_w)
        stats_row.addStretch()

        name_col.addWidget(lbl_name)
        name_col.addWidget(lbl_sub)
        name_col.addLayout(stats_row)

        # Badge de estado
        lbl_badge = QLabel(f"  {badge_dot}  {status_name.capitalize() or '—'}  ")
        lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_badge.setFixedHeight(28)
        lbl_badge.setStyleSheet(f"""
            background-color: {badge_bg}; color: {badge_color};
            border: 1px solid {badge_color}55;
            border-radius: 14px;
            font-size: 11px; font-weight: 700;
            letter-spacing: 0.5px;
        """)

        hdr_inner.addWidget(self.lbl_photo)
        hdr_inner.addLayout(name_col, 1)
        hdr_inner.addWidget(lbl_badge, 0, Qt.AlignmentFlag.AlignTop)
        body.addWidget(hdr_frame)

        # Banner de estado de pago
        body.addWidget(self._payment_status_banner(last_payments, status_name))

        # Línea degradada roja
        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {RED}, stop:0.45 rgba(200,16,46,90), stop:1 transparent);
            border: none;
        """)
        body.addWidget(sep)

        # ── FILA 1: Datos personales + Información académica ─────────
        row1 = QHBoxLayout()
        row1.setSpacing(16)

        # CARD — Datos personales
        c_personal, l_personal = self._card("Datos personales")
        l_personal.addLayout(self._drow("Nombre", name or "—"))
        l_personal.addLayout(self._drow("Email", data.get("email") or "—"))
        l_personal.addLayout(self._drow("Teléfono", data.get("phone") or "—"))
        l_personal.addLayout(self._drow("Edad", age_text, GREEN))
        l_personal.addLayout(self._drow("Nacimiento", str(data.get("birthdate") or "—")))
        l_personal.addLayout(self._drow("Antigüedad", tenure_text, YELLOW))
        if data.get("profession"):
            l_personal.addLayout(self._drow("Profesión", data["profession"]))
        if data.get("username"):
            l_personal.addLayout(self._drow("Usuario", data["username"]))
        l_personal.addWidget(self._mini_sep())
        l_personal.addWidget(self._section_label("DIRECCIÓN"))
        l_personal.addLayout(self._drow("Dirección", data.get("address_line") or "—"))
        if data.get("neighborhood"):
            l_personal.addLayout(self._drow("Barrio", data["neighborhood"]))
        if data.get("socioeconomic_stratum"):
            l_personal.addLayout(self._drow("Estrato", f"Estrato {data['socioeconomic_stratum']}"))
        l_personal.addLayout(self._drow("Ciudad", data.get("residence_city") or "—"))
        l_personal.addLayout(self._drow("País residencia", data.get("residence_country") or "—"))
        l_personal.addLayout(self._drow("Ciudad nacimiento", data.get("birth_city") or "—"))
        l_personal.addLayout(self._drow("País nacimiento", data.get("birth_country") or "—"))
        if data.get("residence_details"):
            l_personal.addLayout(self._drow("Detalles", data["residence_details"]))
        l_personal.addStretch()
        row1.addWidget(c_personal, 1)

        # CARD — Información académica + contacto
        c_acad, l_acad = self._card("Información académica")
        l_acad.addLayout(self._drow("Documento", f"{data.get('type_document') or ''} {doc_str}".strip()))
        l_acad.addLayout(self._drow("Categoría", category or "—"))
        l_acad.addLayout(self._drow("Estado", status_name or "—"))
        l_acad.addLayout(self._drow("Ingreso al dojo", str(data.get("joined_date") or "—")))
        if data.get("school_name"):
            l_acad.addLayout(self._drow("Colegio", data["school_name"]))
        l_acad.addWidget(self._mini_sep())

        if is_minor:
            l_acad.addWidget(self._section_label("ACUDIENTE"))
            l_acad.addLayout(self._drow("Nombre", (guardian or {}).get("full_name") or "—"))
            l_acad.addLayout(self._drow("Teléfono", (guardian or {}).get("phone") or "—"))
            l_acad.addLayout(self._drow("Email", (guardian or {}).get("email") or "—"))
            l_acad.addLayout(self._drow("Parentesco", (guardian or {}).get("relationship") or "—"))
            l_acad.addLayout(self._drow("Documento", (guardian or {}).get("document") or "—"))
            l_acad.addLayout(self._drow("Profesión", (guardian or {}).get("profession") or "—"))
        else:
            l_acad.addWidget(self._section_label("CONTACTO DE EMERGENCIA"))
            l_acad.addLayout(self._drow("Nombre", (emergency or {}).get("full_name") or "—"))
            l_acad.addLayout(self._drow("Teléfono", (emergency or {}).get("phone") or "—"))
            l_acad.addLayout(self._drow("Email", (emergency or {}).get("email") or "—"))
            l_acad.addLayout(self._drow("Parentesco", (emergency or {}).get("relationship") or "—"))
            if (emergency or {}).get("note"):
                l_acad.addLayout(self._drow("Nota", emergency["note"]))

        l_acad.addWidget(self._mini_sep())
        l_acad.addWidget(self._section_label("SALUD"))
        if health:
            if health.get("blood_type"):
                l_acad.addLayout(self._drow("Tipo de sangre", health["blood_type"], RED))
            if health.get("eps"):
                l_acad.addLayout(self._drow("EPS", health["eps"]))
            if health.get("allergies"):
                l_acad.addLayout(self._drow("Alergias", health["allergies"], YELLOW))
            if health.get("medical_conditions"):
                l_acad.addLayout(self._drow("Condiciones", health["medical_conditions"]))
            if health.get("notes"):
                l_acad.addLayout(self._drow("Notas salud", health["notes"]))
            if not any([health.get("blood_type"), health.get("eps"),
                        health.get("allergies"), health.get("medical_conditions")]):
                l_acad.addWidget(self._muted("Sin datos de salud registrados."))
        else:
            l_acad.addWidget(self._muted("Sin datos de salud registrados."))

        l_acad.addStretch()
        row1.addWidget(c_acad, 1)
        body.addLayout(row1)

        # ── FILA 2: Cinturones + Clases recientes ─────────────────────
        row2 = QHBoxLayout()
        row2.setSpacing(16)

        # CARD — Cinturones actuales
        c_belts, l_belts = self._card("Cinturones actuales")
        if current_belts:
            for belt in current_belts:
                l_belts.addWidget(self._belt_row(belt))
        else:
            l_belts.addWidget(self._muted("Sin cinturones registrados."))

        l_belts.addWidget(self._mini_sep())
        l_belts.addWidget(self._section_label("HISTORIAL DE CINTURONES"))

        if belt_history:
            for item in belt_history:
                bh_w = QWidget()
                bh_w.setStyleSheet("background: transparent; border: none;")
                bh_hl = QHBoxLayout(bh_w)
                bh_hl.setContentsMargins(0, 2, 0, 2)
                bh_hl.setSpacing(8)

                mini_bw = BeltWidget(
                    color=item.get("color") or "#999999",
                    pre_color=item.get("pre_color"),
                    grades=item.get("grades") or 0,
                    grade_color=item.get("grade_color") or "#FFFFFF",
                    martial_art=item.get("martial_art") or "",
                )
                mini_bw.setFixedSize(70, 14)
                bh_hl.addWidget(mini_bw)

                txt_col = QVBoxLayout()
                txt_col.setSpacing(0)
                lbl_bh_name = QLabel(f"{item.get('belt_name') or '—'}  ·  {item.get('martial_art') or '—'}")
                lbl_bh_name.setStyleSheet("color: #D1D5DB; font-size: 10px; font-weight: 700; border: none;")
                lbl_bh_date = QLabel(f"{item.get('date_changed') or '—'}  ·  {item.get('action') or '—'}")
                lbl_bh_date.setStyleSheet(f"color: {TEXT_MUT}; font-size: 9px; border: none;")
                txt_col.addWidget(lbl_bh_name)
                txt_col.addWidget(lbl_bh_date)
                bh_hl.addLayout(txt_col, 1)
                l_belts.addWidget(bh_w)
        else:
            l_belts.addWidget(self._muted("Sin historial de cinturones."))

        l_belts.addStretch()
        row2.addWidget(c_belts, 1)

        # CARD — Últimas 5 clases
        c_classes, l_classes = self._card("Últimas 5 clases")
        if recent_classes:
            for cls in recent_classes:
                l_classes.addWidget(self._class_row(cls))
        else:
            l_classes.addWidget(self._muted("Sin clases registradas."))
        l_classes.addStretch()
        row2.addWidget(c_classes, 1)

        body.addLayout(row2)

        # ── FILA 3: Últimos pagos (ancho completo) ────────────────────
        c_pay, l_pay = self._card("Últimos pagos")
        if last_payments:
            for pay in last_payments:
                l_pay.addWidget(self._make_payment_row(pay))
        else:
            l_pay.addWidget(self._muted("Sin pagos registrados."))
        body.addWidget(c_pay)

        # ── Footer fijo ───────────────────────────────────────────────
        footer = QFrame()
        footer.setFixedHeight(62)
        footer.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #181818, stop:1 #111111);
                border-top: 1px solid #272727;
            }
            QFrame * { background: transparent; border: none; }
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(24, 12, 24, 12)
        footer_layout.setSpacing(10)

        btn_edit = QPushButton("✎  Editar estudiante")
        btn_edit.setFixedHeight(38)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet(f"""
            QPushButton {{
                background: #1E1E1E; color: {TEXT_SEC};
                border: 1px solid #333333; border-radius: 8px;
                font-size: 13px; font-weight: 700; padding: 0 18px;
            }}
            QPushButton:hover {{
                color: #F0F0F0; border-color: #555555; background: #252525;
            }}
        """)
        btn_edit.clicked.connect(self._open_edit)

        footer_layout.addWidget(btn_edit)
        footer_layout.addStretch()

        btn_close = QPushButton("  Cerrar  ")
        btn_close.setFixedHeight(38)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #E8152F, stop:1 #C8102E);
                color: white; border: none;
                border-radius: 8px; font-size: 13px;
                font-weight: 800; padding: 0 22px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #FF2040, stop:1 #E8152F);
            }
            QPushButton:pressed { background: #A00C24; }
        """)
        btn_close.clicked.connect(self.reject)

        footer_layout.addWidget(btn_close)
        root.addWidget(footer)

    # ── Helpers visuales ────────────────────────────────────────────────

    def _card(self, title):
        outer = QFrame()
        outer.setStyleSheet(f"""
            QFrame#cardOuter {{
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #1E1E1E, stop:1 #141414);
                border: 1px solid #2E2E2E;
                border-top: 1px solid #3A3A3A;
                border-radius: 12px;
            }}
            QFrame#cardOuter * {{
                background: transparent;
                border: none;
            }}
        """)
        outer.setObjectName("cardOuter")

        layout = QVBoxLayout(outer)
        layout.setContentsMargins(18, 14, 18, 16)
        layout.setSpacing(10)

        # Header con acento rojo
        hdr = QWidget()
        hdr.setObjectName("cardHdr")
        hdr.setStyleSheet("""
            QWidget#cardHdr {
                background: transparent;
                border: none;
                border-bottom: 1px solid #252525;
                padding-bottom: 6px;
            }
        """)
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(0, 0, 0, 8)
        hdr_lay.setSpacing(8)

        accent = QFrame()
        accent.setFixedSize(3, 14)
        accent.setStyleSheet(f"background: {RED}; border-radius: 2px; border: none;")

        lbl = QLabel(title.upper())
        lbl.setStyleSheet(f"""
            color: #BBBBBB;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.2px;
            background: transparent;
            border: none;
        """)

        hdr_lay.addWidget(accent)
        hdr_lay.addWidget(lbl)
        hdr_lay.addStretch()
        layout.addWidget(hdr)

        return outer, layout

    def _drow(self, key, val, val_color=TEXT_PRI):
        row = QHBoxLayout()
        row.setSpacing(8)
        row.setContentsMargins(0, 1, 0, 1)

        k = QLabel(key)
        k.setStyleSheet("""
            color: #666666;
            font-size: 11px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        k.setMinimumWidth(90)

        # Separador punteado
        dots = QFrame()
        dots.setFrameShape(QFrame.Shape.HLine)
        dots.setStyleSheet("border: none; border-top: 1px dotted #2A2A2A; background: transparent;")
        dots.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        dots.setFixedHeight(1)

        display_val = str(val) if val not in (None, "") else "—"
        is_dash = display_val == "—"
        effective_color = "#444444" if is_dash else val_color

        v = QLabel(display_val)
        v.setWordWrap(False)
        v.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        v.setStyleSheet(f"""
            color: {effective_color};
            font-size: 12px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)

        row.addWidget(k)
        row.addWidget(dots, 1)
        row.addWidget(v)
        return row

    def _muted(self, text):
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 12px;
            font-weight: 700;
        """)
        return lbl

    def _mini_sep(self):
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #2A2A2A; border: none;")
        return sep

    def _section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.8px;
            background: transparent;
            border: none;
        """)
        return lbl

    def _belt_row(self, belt: dict):
        """Fila visual con BeltWidget real + nombre + arte marcial."""
        w = QWidget()
        w.setStyleSheet("QWidget { background: transparent; border: none; }")
        hl = QHBoxLayout(w)
        hl.setContentsMargins(0, 4, 0, 4)
        hl.setSpacing(10)

        bw = BeltWidget(
            color=belt.get("color") or belt.get("belt_color") or "#999999",
            pre_color=belt.get("pre_color"),
            grades=belt.get("grades") or 0,
            grade_color=belt.get("grade_color") or "#FFFFFF",
            martial_art=belt.get("martial_art") or "",
        )
        hl.addWidget(bw)

        col = QVBoxLayout()
        col.setSpacing(1)
        lbl_name = QLabel(belt.get("belt_name") or "—")
        lbl_name.setStyleSheet("color: #F0F0F0; font-size: 12px; font-weight: 900; border: none;")
        lbl_art = QLabel(belt.get("martial_art") or "—")
        lbl_art.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 700; border: none;")
        col.addWidget(lbl_name)
        col.addWidget(lbl_art)
        hl.addLayout(col, 1)
        return w

    def _class_row(self, cls: dict):
        """Fila visual para una clase reciente con fecha + nombre + estado."""
        w = QWidget()
        w.setStyleSheet("QWidget { background: transparent; border: none; }")
        hl = QHBoxLayout(w)
        hl.setContentsMargins(0, 3, 0, 3)
        hl.setSpacing(8)

        status = (cls.get("status") or "").lower()
        dot_color = GREEN if status == "present" else (YELLOW if status == "late" else TEXT_MUT)
        dot = QLabel("●")
        dot.setFixedWidth(12)
        dot.setStyleSheet(f"color: {dot_color}; font-size: 10px; border: none;")
        hl.addWidget(dot)

        col = QVBoxLayout()
        col.setSpacing(0)
        lbl_name = QLabel(cls.get("class_name") or "Clase")
        lbl_name.setStyleSheet("color: #D1D5DB; font-size: 12px; font-weight: 700; border: none;")
        lbl_sub = QLabel(f"{cls.get('date') or '—'}  ·  {cls.get('martial_art') or '—'}")
        lbl_sub.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 600; border: none;")
        col.addWidget(lbl_name)
        col.addWidget(lbl_sub)
        hl.addLayout(col, 1)

        check_in = cls.get("check_in_time")
        if check_in:
            t = QLabel(str(check_in)[:5])
            t.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; border: none;")
            hl.addWidget(t)
        return w

    def _payment_status_banner(self, last_payments: list, status_name: str) -> QFrame:
        """
        Determina si el estudiante está al día basándose en el tipo de membresía.
        - 1x semana  → ventana de 7 días
        - 2x semana  → ventana de 14 días  (se asume que paga quincenal)
        - 3x semana  → ventana de 14 días
        - Ilimitado  → ventana de 31 días
        - X3 meses adelantados → ventana de 92 días
        - Sin membresía → ventana de 31 días por defecto
        Fuente real: items del pago que contengan keyword de la membresía.
        """
        from datetime import date as _date, datetime as _datetime

        is_active = "activo" in (status_name or "").lower() or "active" in (status_name or "").lower()

        if not last_payments:
            color, bg, border, icon, msg = (
                RED, "#2A0A0A", "rgba(200,16,46,0.35)",
                "⚠", "Sin pagos registrados"
            )
            return self._build_banner(color, bg, border, icon, msg)

        pay = last_payments[0]
        last_status = (pay.get("status") or "").lower()
        last_date   = pay.get("income_date")
        items       = pay.get("items") or []

        # Calcular delta días desde el último pago
        delta = None
        last_date_str = "—"
        if last_date:
            try:
                if hasattr(last_date, "toordinal"):
                    d = last_date
                else:
                    d = _datetime.strptime(str(last_date)[:10], "%Y-%m-%d").date()
                delta = (_date.today() - d).days
                last_date_str = str(d)
            except Exception:
                delta = None

        # Detectar ventana de validez según nombre del plan en los ítems
        window_days = 31  # default mensual
        item_names = " ".join((it.get("name") or "").lower() for it in items)

        if "3 mes" in item_names or "tres mes" in item_names or "adelantad" in item_names:
            window_days = 92
        elif "1 vez" in item_names or "una vez" in item_names:
            window_days = 8    # 1x semana → 7 días + 1 tolerancia
        elif "2 veces" in item_names or "dos veces" in item_names:
            window_days = 16   # 2x semana → pago quincenal + 1 tolerancia
        elif "3 veces" in item_names or "tres veces" in item_names:
            window_days = 16   # 3x semana → pago quincenal + 1 tolerancia
        elif "libre" in item_names or "ilimitad" in item_names or "grupal" in item_names:
            window_days = 31

        overdue = (delta is not None and delta > window_days)

        if last_status in ("partial", "parcial"):
            color, bg, border, icon, msg = (
                YELLOW, "#2A2A0A", "rgba(234,179,8,0.30)",
                "◑", f"Pago parcial pendiente — {last_date_str}"
            )
        elif is_active and last_status in ("paid", "pagado") and not overdue:
            color, bg, border, icon, msg = (
                GREEN, "#0A2A0A", "rgba(34,197,94,0.30)",
                "✓", f"Al día — último pago: {last_date_str}"
            )
        else:
            if delta is not None:
                color, bg, border, icon, msg = (
                    RED, "#2A0A0A", "rgba(200,16,46,0.35)",
                    "⚠", f"Posible mora — último pago: {last_date_str} ({delta}d)"
                )
            else:
                color, bg, border, icon, msg = (
                    RED, "#2A0A0A", "rgba(200,16,46,0.35)",
                    "⚠", "Sin fecha de pago registrada"
                )

        return self._build_banner(color, bg, border, icon, msg)

    def _build_banner(self, color, bg, border, icon, msg) -> QFrame:
        banner = QFrame()
        banner.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}
            QFrame QLabel {{ background: transparent; border: none; }}
        """)
        bl = QHBoxLayout(banner)
        bl.setContentsMargins(12, 8, 12, 8)
        bl.setSpacing(8)
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 900;")
        lbl_text = QLabel(msg)
        lbl_text.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 700;")
        bl.addWidget(lbl_icon)
        bl.addWidget(lbl_text, 1)
        return banner

    def _set_photo(self, path, name):
        if path:
            pixmap = QPixmap(path).scaled(72, 72, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.lbl_photo.setPixmap(pixmap)
        else:
            initials = "".join(part[0].upper() for part in name.split()[:2] if part)
            self.lbl_photo.setText(initials or "?")
            self.lbl_photo.setStyleSheet(
                "background-color: #1A1A1A; color: #C8102E; font-size: 20px; font-weight: 700; border-radius: 36px;"
            )

    def _change_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar foto", "", "Imágenes (*.png *.jpg *.jpeg)")
        if path:
            self.repo.update_photo(self.student_id, path)
            from_ = self.repo.get_student_profile_detail(self.student_id)
            name_ = f"{from_.get('first_name') or ''} {from_.get('last_name') or ''}".strip() if from_ else "?"
            self._set_photo(path, name_)

    def _make_payment_row(self, pay):
        pay_id = pay.get("id") or "—"
        pay_date = pay.get("income_date") or "—"
        pay_total = format_money(pay.get("total"))
        pay_status = (pay.get("status") or "").lower()
        items = pay.get("items") or []
        paid = pay.get("paid_amount")
        total_val = pay.get("total") or 0

        status_text = {
            "paid": trf("student.detail.status_paid", "Pagado"),
            "partial": trf("student.detail.status_partial", "Parcial"),
            "pending": trf("student.detail.status_pending", "Pendiente"),
        }.get(pay_status, pay_status.capitalize() if pay_status else "—")

        sc = {"paid": GREEN, "partial": YELLOW, "pending": RED}.get(pay_status, TEXT_MUT)
        sbg = {"paid": "#0A2A0A", "partial": "#2A2A0A", "pending": "#2A0A0A"}.get(pay_status, "#1A1A1A")
        sbdr = {"paid": "rgba(34,197,94,0.25)", "partial": "rgba(234,179,8,0.25)", "pending": "rgba(200,16,46,0.25)"}.get(pay_status, "#2A2A2A")

        card = QFrame()
        card.setObjectName("payCard")
        card.setStyleSheet(f"""
            QFrame#payCard {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {sbg}, stop:0.06 {sbg}, stop:0.06 #1A1A1A, stop:1 #161616);
                border: 1px solid #222222;
                border-left: 3px solid {sc};
                border-radius: 8px;
            }}
            QFrame#payCard * {{ background: transparent; border: none; }}
        """)

        rl = QVBoxLayout(card)
        rl.setContentsMargins(14, 10, 14, 10)
        rl.setSpacing(6)

        # Fila superior: id · fecha · badge · total
        top = QHBoxLayout()
        top.setSpacing(8)

        id_lbl = QLabel(f"#{pay_id}")
        id_lbl.setStyleSheet(f"color: #555555; font-size: 10px; font-weight: 700;")

        date_lbl = QLabel(str(pay_date))
        date_lbl.setStyleSheet(f"color: #999999; font-size: 11px; font-weight: 600;")

        badge = QLabel(status_text)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedHeight(20)
        badge.setStyleSheet(f"""
            background-color: {sbg}; color: {sc};
            border: 1px solid {sbdr}; border-radius: 4px;
            font-size: 9px; font-weight: 800; padding: 0 8px;
        """)

        total_lbl = QLabel(str(pay_total))
        total_lbl.setStyleSheet(f"color: #F0F0F0; font-size: 13px; font-weight: 800;")

        top.addWidget(id_lbl)
        top.addWidget(date_lbl)
        top.addStretch()
        top.addWidget(badge)
        top.addSpacing(8)
        top.addWidget(total_lbl)
        rl.addLayout(top)

        # Línea de ítems
        item_texts = []
        for it in items[:4]:
            nm = it.get("name") or ""
            qt = it.get("quantity") or ""
            if nm:
                item_texts.append(f"{qt}× {nm}" if qt else nm)
        remaining = max(0, len(items) - 4)
        if remaining:
            item_texts.append(f"+{remaining} más")
        if item_texts:
            items_lbl = QLabel("  ·  ".join(item_texts))
            items_lbl.setStyleSheet("color: #666666; font-size: 10px; font-weight: 600;")
            rl.addWidget(items_lbl)

        # Pago parcial mostrado
        if pay_status == "partial" and paid is not None and total_val:
            partial_pct = min(100, int((paid / total_val) * 100))
            bar_bg = QFrame()
            bar_bg.setFixedHeight(4)
            bar_bg.setStyleSheet("background: #1A1A1A; border-radius: 2px; border: none;")
            bar_fg = QFrame(bar_bg)
            bar_fg.setFixedHeight(4)
            bar_fg.setStyleSheet(f"background: {YELLOW}; border-radius: 2px; border: none;")
            bar_fg.setGeometry(0, 0, max(8, int(partial_pct * 2.2)), 4)
            rl.addWidget(bar_bg)
            plbl = QLabel(f"Pagado: {pay_total} / Parcial: {format_money(paid)} ({partial_pct}%)")
            plbl.setStyleSheet(f"color: {YELLOW}; font-size: 9px; font-weight: 700;")
            rl.addWidget(plbl)

        return card

    def _open_edit(self):
        from views.student_form import StudentForm

        dlg = StudentForm(self.repo, student_id=self.student_id, parent=self)
        if dlg.exec() == StudentForm.DialogCode.Accepted:
            self.accept()


# ─── PANEL LATERAL PREMIUM ────────────────────────────────────────────

class StudentPreviewPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_data = None

        self.setFixedWidth(288)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 20)
        root.setSpacing(0)

        title = QLabel("VISTA PREVIA")
        title.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 10px;
            font-weight: 900;
            letter-spacing: 1.4px;
            background: transparent;
            border: none;
        """)
        root.addWidget(title)
        root.addSpacing(12)

        self.avatar = InitialsAvatar("", 80, RED)
        self.avatar.setStyleSheet(f"""
            QLabel {{
                background-color: #1A1A1A;
                color: white;
                border-radius: 40px;
                border: 2px solid {RED};
                font-size: 24px;
                font-weight: 900;
            }}
        """)
        avatar_row = QHBoxLayout()
        avatar_row.setContentsMargins(0, 0, 0, 0)
        avatar_row.addStretch()
        avatar_row.addWidget(self.avatar)
        avatar_row.addStretch()
        root.addLayout(avatar_row)
        root.addSpacing(16)

        name_container = QWidget()
        name_container.setFixedWidth(210)
        name_container.setStyleSheet("background: transparent; border: none;")
        name_vl = QVBoxLayout(name_container)
        name_vl.setContentsMargins(0, 0, 0, 0)
        name_vl.setSpacing(0)

        self.lbl_name = QLabel("Selecciona un estudiante")
        self.lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_name.setWordWrap(True)
        self.lbl_name.setFixedWidth(210)
        self.lbl_name.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.lbl_name.setStyleSheet("""
            color: white;
            font-size: 15px;
            font-weight: 900;
            background: transparent;
            border: none;
        """)
        name_vl.addWidget(self.lbl_name)

        name_row = QHBoxLayout()
        name_row.setContentsMargins(0, 0, 0, 0)
        name_row.addStretch()
        name_row.addWidget(name_container)
        name_row.addStretch()
        root.addLayout(name_row)
        root.addSpacing(4)

        self.lbl_id = QLabel("—")
        self.lbl_id.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_id.setFixedWidth(210)
        self.lbl_id.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 11px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        id_row = QHBoxLayout()
        id_row.setContentsMargins(0, 0, 0, 0)
        id_row.addStretch()
        id_row.addWidget(self.lbl_id)
        id_row.addStretch()
        root.addLayout(id_row)
        root.addSpacing(20)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER}; border: none;")
        root.addWidget(sep)

        self.belt_box = QFrame()
        self.belt_box.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                border: 1px solid #222222;
                border-radius: 12px;
            }
            QFrame QLabel {
                background: transparent;
                border: none;
            }
            QFrame QWidget {
                background: transparent;
                border: none;
            }
        """)
        belt_l = QVBoxLayout(self.belt_box)
        belt_l.setContentsMargins(14, 12, 14, 12)
        belt_l.setSpacing(8)

        lbl_belt_title = QLabel("CINTURÓN ACTUAL")
        lbl_belt_title.setStyleSheet("""
            color: #666666;
            font-size: 10px;
            font-weight: 900;
            letter-spacing: 1px;
        """)
        belt_l.addWidget(lbl_belt_title)

        belt_row = QHBoxLayout()
        belt_row.setSpacing(10)
        belt_row.addSpacing(0)
        belt_row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.belt_widget = BeltWidget("#FFFFFF", None, 0, "#FFFFFF", "")
        self.lbl_belt = QLabel("Sin cinturón")
        self.lbl_belt.setStyleSheet("""
            color: white;
            font-size: 12px;
            font-weight: 900;
        """)

        belt_row.addWidget(self.belt_widget)
        belt_row.addWidget(self.lbl_belt, 1)
        belt_l.addLayout(belt_row)

        root.addWidget(self.belt_box)
        root.addSpacing(12)

        self.lbl_contact_title = QLabel("CONTACTO")
        self.lbl_contact_title.setStyleSheet("""
            color: #666666;
            font-size: 10px;
            font-weight: 900;
            letter-spacing: 1px;
        """)
        root.addWidget(self.lbl_contact_title)

        phone_row = QHBoxLayout()
        phone_row.setSpacing(8)
        self._phone_icon = IconLabel("phone", 14, TEXT_SEC)
        self.lbl_phone = QLabel("—")
        self.lbl_phone.setWordWrap(True)
        self.lbl_phone.setStyleSheet("""
            color: #D1D5DB;
            font-size: 13px;
            font-weight: 600;
        """)
        phone_row.addWidget(self._phone_icon)
        phone_row.addWidget(self.lbl_phone, 1)
        phone_w = QWidget()
        phone_w.setStyleSheet("background:transparent;")
        phone_w.setLayout(phone_row)
        root.addWidget(phone_w)

        email_row = QHBoxLayout()
        email_row.setSpacing(8)
        self._email_icon = IconLabel("mail", 14, TEXT_SEC)
        self.lbl_email = QLabel("—")
        self.lbl_email.setWordWrap(True)
        self.lbl_email.setStyleSheet("""
            color: #D1D5DB;
            font-size: 13px;
            font-weight: 600;
        """)
        email_row.addWidget(self._email_icon)
        email_row.addWidget(self.lbl_email, 1)
        email_w = QWidget()
        email_w.setStyleSheet("background:transparent;")
        email_w.setLayout(email_row)
        root.addWidget(email_w)

        root.addStretch()
        root.addSpacing(12)

        self.btn_detail = QPushButton()
        _eye_icon = IconLabel("eye", 15, TEXT_PRI)
        _eye_lbl = QLabel("Ver Perfil Completo")
        _eye_lbl.setStyleSheet("color: white; font-size: 13px; font-weight: 800; background: transparent; border: none;")
        _eye_hl = QHBoxLayout(self.btn_detail)
        _eye_hl.setContentsMargins(0, 0, 0, 0)
        _eye_hl.setSpacing(8)
        _eye_hl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        _eye_hl.addWidget(_eye_icon)
        _eye_hl.addWidget(_eye_lbl)

        self.btn_edit = QPushButton()
        _edit_icon = IconLabel("edit", 14, TEXT_SEC)
        _edit_lbl = QLabel("Editar Datos")
        _edit_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px; font-weight: 800; background: transparent; border: none;")
        _edit_hl = QHBoxLayout(self.btn_edit)
        _edit_hl.setContentsMargins(0, 0, 0, 0)
        _edit_hl.setSpacing(8)
        _edit_hl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        _edit_hl.addWidget(_edit_icon)
        _edit_hl.addWidget(_edit_lbl)

        self.btn_detail.setFixedHeight(40)
        self.btn_edit.setFixedHeight(36)

        self.btn_detail.setStyleSheet(f"""
            QPushButton {{
                background-color: #1A1A1A;
                color: white;
                border: 1px solid {BORDER};
                border-radius: 9px;
                font-size: 13px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                background-color: #222222;
                border-color: #444444;
            }}
        """)

        self.btn_edit.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_SEC};
                border: 1px solid transparent;
                border-radius: 9px;
                font-size: 13px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                color: white;
                border-color: {BORDER};
            }}
        """)

        root.addWidget(self.btn_detail)
        root.addWidget(self.btn_edit)

    def set_student(self, data):
        self.current_data = data or {}

        name = self.current_data.get("nombre") or self.current_data.get("name") or "Estudiante"
        document = self.current_data.get("document") or self.current_data.get("documento") or self.current_data.get("id") or "—"

        category = (
            self.current_data.get("category_name") or
            self.current_data.get("categoria") or ""
        ).lower()

        is_kid = any(k in category for k in ("kid", "niño", "menor", "infant", "child", "junior"))

        guardian_phone = self.current_data.get("guardian_phone") or ""
        guardian_email = self.current_data.get("guardian_email") or ""
        guardian_name  = self.current_data.get("guardian_name")  or ""

        if is_kid and (guardian_phone or guardian_email):
            phone = guardian_phone or "—"
            email = guardian_email or "—"
            label = "CONTACTO ACUDIENTE"
            if guardian_name:
                label = f"CONTACTO \u2014 {guardian_name[:18]}{'…' if len(guardian_name) > 18 else ''}"
            self.lbl_contact_title.setText(label)
        else:
            phone = self.current_data.get("phone") or self.current_data.get("telefono") or "—"
            email = self.current_data.get("email") or self.current_data.get("email_raw") or "—"
            self.lbl_contact_title.setText("CONTACTO")

        belt_name = self.current_data.get("belt_name") or self.current_data.get("cinturon") or "Sin cinturón"
        martial_art = self.current_data.get("martial_art") or self.current_data.get("arte_marcial") or ""
        belt_color = self.current_data.get("belt_color") or self.current_data.get("color") or "#FFFFFF"
        pre_color = self.current_data.get("pre_color")
        grades = self.current_data.get("grades") or 0
        grade_color = self.current_data.get("grade_color") or "#FFFFFF"

        parts = [p for p in name.split() if p]
        initials = "".join(p[0].upper() for p in parts[:2]) or "?"

        self.avatar.setText(initials)
        self.lbl_name.setText(name)
        self.lbl_name.setToolTip(name)

        name_len = len(name)
        if name_len <= 18:
            font_size = 17
        elif name_len <= 26:
            font_size = 15
        elif name_len <= 34:
            font_size = 14
        else:
            font_size = 13

        self.lbl_name.setStyleSheet(f"""
            color: white;
            font-size: {font_size}px;
            font-weight: 900;
            background: transparent;
            border: none;
        """)
        tipo_doc = self.current_data.get("type_document") or "Doc"
        self.lbl_id.setText(f"{tipo_doc}: {document}")
        self.lbl_phone.setText(phone)
        self.lbl_email.setText(email)
        self.lbl_belt.setText(belt_name)

        old = self.belt_widget
        self.belt_widget = BeltWidget(belt_color, pre_color, grades, grade_color, martial_art)

        layout = self.belt_box.layout().itemAt(1).layout()
        layout.replaceWidget(old, self.belt_widget)
        old.deleteLater()


# ─── VISTA PRINCIPAL ──────────────────────────────────────────────────
class StudentsView(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = StudentRepository()
        self._rows = []
        self._display_rows = []
        self._selected_id = None
        self._selected_data = None
        self._worker = None
        self._animations = []
        self._proximity_anims = []
        self._blur_effect = None
        self._blur_target_widget = None
        self._selected_row = -1

        self._build_ui()
        self._load()

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, "table"):
            self._load()

    # ─────────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_MAIN};
                color: {TEXT_PRI};
                font-family: 'Inter';
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(22)

        # Header
        header = QHBoxLayout()
        header.setSpacing(16)

        left = QHBoxLayout()
        left.setSpacing(14)

        icon_container = QWidget()
        icon_container.setFixedSize(48, 48)
        icon_container.setMinimumWidth(48)
        icon_container.setMaximumWidth(48)
        icon_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        icon_container.setStyleSheet("background: transparent;")
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(8, 6, 0, 0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon = IconLabel("students", 28, RED)
        icon.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        icon_layout.addWidget(icon)
        left.addWidget(icon_container)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title = QLabel("Estudiantes")
        title.setStyleSheet("""
            color: white;
            font-size: 25px;
            font-weight: 900;
            background: transparent;
            border: none;
        """)

        subtitle = QLabel("DIRECTORIO DE ESTUDIANTES")
        subtitle.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 10px;
            font-weight: 900;
            letter-spacing: 1.6px;
            background: transparent;
            border: none;
        """)

        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        left.addLayout(title_col)

        header.addLayout(left)
        header.addStretch()

        self.btn_delete = QPushButton()
        self.btn_delete.setFixedHeight(40)
        self.btn_delete.setMinimumWidth(110)
        _del_icon = IconLabel("trash", 16, RED)
        _del_lbl = QLabel("Eliminar")
        _del_lbl.setStyleSheet(f"color: {RED}; font-size: 13px; font-weight: 900; background: transparent; border: none;")
        _del_hl = QHBoxLayout(self.btn_delete)
        _del_hl.setContentsMargins(14, 0, 18, 0)
        _del_hl.setSpacing(8)
        _del_hl.addWidget(_del_icon)
        _del_hl.addWidget(_del_lbl)

        self.btn_new = QPushButton("＋ Nuevo Estudiante")
        self.btn_new.setFixedHeight(40)

        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_delete.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {RED};
                border: 1px solid rgba(200,16,46,0.35);
                border-radius: 9px;
                padding: 0 18px;
                font-size: 13px;
                font-weight: 900;
            }}
            QPushButton:hover {{
                background-color: rgba(200,16,46,0.10);
            }}
        """)

        self.btn_new.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #E8152F,
                    stop:1 {RED}
                );
                color: white;
                border: none;
                border-radius: 9px;
                padding: 0 18px;
                font-size: 13px;
                font-weight: 900;
            }}
            QPushButton:hover {{
                background-color: #E8152F;
            }}
        """)

        self.btn_new.clicked.connect(self._open_create)
        self.btn_delete.clicked.connect(self._delete_selected)

        header.addWidget(self.btn_delete)
        header.addWidget(self.btn_new)

        root.addLayout(header)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)

        search_container = QWidget()
        search_container.setStyleSheet("background: transparent;")
        search_hl = QHBoxLayout(search_container)
        search_hl.setContentsMargins(14, 0, 14, 0)
        search_hl.setSpacing(10)

        _search_icon = IconLabel("search", 16, TEXT_MUT)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre, documento, email...")
        self.search_input.setFixedHeight(46)
        self.search_input.setFrame(False)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                color: {TEXT_PRI};
                border: none;
                font-size: 13px;
                font-weight: 600;
            }}
        """)
        search_hl.addWidget(_search_icon)
        search_hl.addWidget(self.search_input, 1)

        search_wrapper = QFrame()
        search_wrapper.setFixedHeight(46)
        search_wrapper.setStyleSheet(f"""
            QFrame {{
                background-color: #1A1A1A;
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        search_inner = QHBoxLayout(search_wrapper)
        search_inner.setContentsMargins(0, 0, 0, 0)
        search_inner.addWidget(search_container)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["Estado: Todos", "Activos", "Inactivos", "Retirados"])

        self.category_filter = QComboBox()
        self.category_filter.addItems([
            u"Categor\u00eda: Todas",
            "KID",
            "YOUTH",
            "ADULT",
            "SCHOLARSHIP",
        ])

        self.art_filter = QComboBox()
        self.art_filter.addItems(["Arte Marcial: Todos", "Karate Kyokushin", "Brazilian Jiu-Jitsu", "Kick Boxing", "Functional"])

        for combo in (self.status_filter, self.category_filter, self.art_filter):
            combo.setFixedHeight(46)
            combo.setStyleSheet(f"""
                QComboBox {{
                    background-color: #1A1A1A;
                    color: #D1D5DB;
                    border: 1px solid {BORDER};
                    border-radius: 12px;
                    padding: 0 14px;
                    font-size: 13px;
                    font-weight: 700;
                    min-width: 170px;
                }}
                QComboBox:focus {{
                    border-color: {RED};
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 24px;
                }}
                QComboBox QAbstractItemView {{
                    background-color: #1A1A1A;
                    color: {TEXT_PRI};
                    selection-background-color: {RED};
                    border: 1px solid {BORDER};
                }}
            """)

        toolbar.addWidget(search_wrapper, 1)
        toolbar.addWidget(self.status_filter)
        toolbar.addWidget(self.category_filter)
        toolbar.addWidget(self.art_filter)

        root.addLayout(toolbar)

        # Content
        content = QHBoxLayout()
        content.setSpacing(22)

        # Table shell
        self.table_shell = QFrame()
        self.table_shell.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        self.table_shell.setProperty("class", "table-shell")

        table_layout = QVBoxLayout(self.table_shell)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            "Estudiante",
            "Contacto",
            "Estado",
            "Nivel (Cinturón)"
        ])

        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.setMouseTracking(True)
        self.table.cellClicked.connect(self._on_cell_click)
        self.table.viewport().installEventFilter(self)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_CARD};
                border: none;
                border-bottom-left-radius: 16px;
                border-bottom-right-radius: 16px;
                outline: none;
                color: {TEXT_PRI};
                gridline-color: transparent;
                selection-background-color: transparent;
                selection-color: white;
                font-size: 12px;
            }}

            QTableWidget::item {{
                border: none;
                border-bottom: 1px solid #1F1F1F;
                padding: 0px;
                outline: none;
                color: transparent;
            }}

            QTableWidget::item:selected {{
                background-color: #1A1A1A;
                border: none;
                border-bottom: 1px solid #1F1F1F;
            }}

            QTableWidget::item:hover {{
                background-color: #1A1A1A;
                border: none;
            }}

            QHeaderView {{
                background-color: #121212;
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }}

            QHeaderView::section {{
                background-color: #121212;
                color: {TEXT_SEC};
                border: none;
                border-bottom: 1px solid #1F1F1F;
                padding: 14px;
                font-size: 10px;
                font-weight: 900;
                letter-spacing: 1.2px;
            }}

            QHeaderView::section:first {{
                border-top-left-radius: 15px;
            }}

            QHeaderView::section:last {{
                border-top-right-radius: 15px;
            }}

            QTableCornerButton::section {{
                background-color: #121212;
                border: none;
            }}

            QScrollBar:vertical {{
                background: {BG_MAIN};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: #333333;
                border-radius: 4px;
                min-height: 28px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #555555;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """)

        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.cellDoubleClicked.connect(lambda row, col: self._open_detail_selected())
        self.table.verticalScrollBar().setSingleStep(8)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        table_layout.addWidget(self.table)
        content.addWidget(self.table_shell, 1)

        # Preview
        self.preview = StudentPreviewPanel()
        self.preview.btn_detail.clicked.connect(self._open_detail_selected)
        self.preview.btn_edit.clicked.connect(self._open_edit_selected)

        content.addWidget(self.preview)

        root.addLayout(content, 1)

        # Debounce
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._load)

        self.search_input.textChanged.connect(lambda: self._search_timer.start(350))
        self.status_filter.currentIndexChanged.connect(self._apply_filters)
        self.category_filter.currentIndexChanged.connect(self._apply_filters)
        self.art_filter.currentIndexChanged.connect(self._apply_filters)

        self._animate_enter([icon, self.search_input])

    # ─────────────────────────────────────────────
    # Animaciones
    # ─────────────────────────────────────────────
    def _animate_enter(self, widgets):
        self._animations.clear()

        for i, w in enumerate(widgets):
            effect = QGraphicsOpacityEffect(w)
            w.setGraphicsEffect(effect)

            anim = QPropertyAnimation(effect, b"opacity", self)
            anim.setDuration(520)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.setLoopCount(1)

            QTimer.singleShot(i * 120, anim.start)

            self._animations.append(anim)

    def _fade_table_refresh(self):
        effect = QGraphicsOpacityEffect(self.table)
        self.table.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(260)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(lambda: self.table.setGraphicsEffect(None))
        anim.start()

        self._animations.append(anim)

    # ─────────────────────────────────────────────
    # Proximity Glow
    # ─────────────────────────────────────────────
    def eventFilter(self, obj, event):
        if obj is self.table.viewport() and event.type() == QEvent.Type.Leave:
            if self._selected_row >= 0:
                for c in range(self.table.columnCount()):
                    w = self.table.cellWidget(self._selected_row, c)
                    if w:
                        w.setStyleSheet("""
                            QWidget { background: transparent; border: none; }
                            QLabel  { background: transparent; border: none; }
                        """)
                self._selected_row = -1
        return super().eventFilter(obj, event)

    def _animate_shadow(self, shadow, color, blur, x, y):
        if not shadow:
            return

        shadow.setColor(color)
        shadow.setOffset(x, y)

        anim = QPropertyAnimation(shadow, b"blurRadius", self)
        anim.setDuration(220)
        anim.setStartValue(shadow.blurRadius())
        anim.setEndValue(blur)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()

        self._proximity_anims.append(anim)

    # ─────────────────────────────────────────────
    # Row Click Selection
    # ─────────────────────────────────────────────
    def _on_cell_click(self, row, col):
        if self._selected_row >= 0 and self._selected_row != row:
            for c in range(self.table.columnCount()):
                w = self.table.cellWidget(self._selected_row, c)
                if w:
                    w.setStyleSheet("""
                        QWidget { background: transparent; border: none; }
                        QLabel  { background: transparent; border: none; }
                    """)

        self._selected_row = row

        HIGHLIGHT_BG = "rgba(200, 16, 46, 0.12)"
        HIGHLIGHT_BORDER = RED

        for c in range(self.table.columnCount()):
            w = self.table.cellWidget(row, c)
            if not w:
                continue

            if c == 0:
                extra = f"border-left: 3px solid {HIGHLIGHT_BORDER};"
            else:
                extra = "border-left: none;"

            w.setStyleSheet(f"""
                QWidget {{
                    background-color: {HIGHLIGHT_BG};
                    border: none;
                    {extra}
                    border-radius: 0px;
                }}
                QLabel {{
                    background: transparent;
                    border: none;
                }}
            """)

        for c in range(self.table.columnCount()):
            w = self.table.cellWidget(row, c)
            if not w:
                continue
            effect = QGraphicsOpacityEffect(w)
            w.setGraphicsEffect(effect)
            anim = QPropertyAnimation(effect, b"opacity", self)
            anim.setDuration(220)
            anim.setStartValue(0.3)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            _w = w
            anim.finished.connect(lambda ww=_w: ww.setGraphicsEffect(None))
            anim.start()
            self._animations.append(anim)

        self._on_selection_changed()

    # ─────────────────────────────────────────────
    # Blur
    # ─────────────────────────────────────────────
    def _blur_target(self):
        win = self.window()
        if hasattr(win, "centralWidget") and win.centralWidget():
            return win.centralWidget()
        return win

    def _blur_on(self):
        target = self._blur_target()
        if getattr(self, "_blur_effect", None):
            return
        self._blur_target_widget = target
        self._blur_effect = QGraphicsBlurEffect(target)
        self._blur_effect.setBlurRadius(0)
        target.setGraphicsEffect(self._blur_effect)
        self._blur_anim = QPropertyAnimation(self._blur_effect, b"blurRadius", self)
        self._blur_anim.setDuration(220)
        self._blur_anim.setStartValue(0)
        self._blur_anim.setEndValue(14)
        self._blur_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._blur_anim.start()

    def _blur_off(self):
        if not getattr(self, "_blur_effect", None):
            return
        target = getattr(self, "_blur_target_widget", None)
        self._blur_anim_out = QPropertyAnimation(self._blur_effect, b"blurRadius", self)
        self._blur_anim_out.setDuration(180)
        self._blur_anim_out.setStartValue(self._blur_effect.blurRadius())
        self._blur_anim_out.setEndValue(0)
        self._blur_anim_out.setEasingCurve(QEasingCurve.Type.InCubic)

        def cleanup():
            if target:
                target.setGraphicsEffect(None)
            self._blur_effect = None
            self._blur_target_widget = None

        self._blur_anim_out.finished.connect(cleanup)
        self._blur_anim_out.start()

    # ─────────────────────────────────────────────
    # Data
    # ─────────────────────────────────────────────
    def _load(self):
        search = self.search_input.text().strip() if hasattr(self, "search_input") else ""

        self._worker = LoadWorker(self.repo, search)
        self._worker.done.connect(self._on_data_loaded)
        self._worker.start()

    def _on_data_loaded(self, rows):
        self._rows = rows or []
        self._apply_filters()
        self._fade_table_refresh()

    def _apply_filters(self):
        rows = list(self._rows)

        status_text = self.status_filter.currentText() if hasattr(self, "status_filter") else "Estado: Todos"
        category_text = self.category_filter.currentText() if hasattr(self, "category_filter") else "Categor\u00eda: Todas"
        art_text = self.art_filter.currentText() if hasattr(self, "art_filter") else "Arte Marcial: Todos"

        if status_text != "Estado: Todos":
            mapping = {
                "Activos":    ("ACTIVO", "ACTIVE"),
                "Inactivos":  ("INACTIVO", "INACTIVE"),
                "Retirados":  ("RETIRADO", "RETIRED"),
            }
            wanted_vals = mapping.get(status_text, ())
            rows = [
                r for r in rows
                if str(self._get(r, "status_name", "estado", "status")).upper() in wanted_vals
            ]

        if category_text != "Categor\u00eda: Todas":
            wanted = category_text.upper()
            rows = [
                r for r in rows
                if wanted == str(self._get(r, "category_name", "categoria", "category")).upper()
            ]

        if art_text != "Arte Marcial: Todos":
            wanted = art_text.replace("Arte Marcial: ", "").strip().upper()
            rows = [
                r for r in rows
                if self._row_has_martial_art(r, wanted)
            ]

        rows = self._sort_rows_for_active_art_filter(rows)

        self._display_rows = rows
        self._paint_table(rows)

        if self.table.rowCount() > 0:
            self.table.selectRow(0)
        else:
            self._selected_id = None
            self._selected_data = None
            if hasattr(self, "preview"):
                self.preview.set_student({})

    def _current_art_filter_text(self):
        if not hasattr(self, "art_filter"):
            return "Arte Marcial: Todos"
        return self.art_filter.currentText() or "Arte Marcial: Todos"

    def _highest_belt(self, belts):
        def safe_orden(b):
            try:
                return int(b.get("orden") or 0)
            except Exception:
                return 0
        return sorted(belts, key=lambda b: safe_orden(b), reverse=True)[0]

    def _primary_belt_when_all(self, belts):
        return self._highest_belt(belts)

    def _selected_belt_for_current_filter(self, data):
        belts = data.get("belts") or []
        if not belts:
            return None

        art_text = self._current_art_filter_text()

        if art_text == "Arte Marcial: Todos":
            return self._primary_belt_when_all(belts)

        wanted = art_text.replace("Arte Marcial: ", "").strip().upper()

        matching = []
        for belt in belts:
            ma = str(
                belt.get("martial_art") or
                belt.get("ma_name") or
                ""
            ).upper()
            if wanted in ma:
                matching.append(belt)

        if not matching:
            return None

        return self._highest_belt(matching)

    def _sort_rows_for_active_art_filter(self, rows):
        art_text = self._current_art_filter_text()

        if art_text == "Arte Marcial: Todos":
            return sorted(
                rows,
                key=lambda r: str(self._get(r, "nombre", "name")).lower()
            )

        def sort_key(row):
            data = self._row_to_dict(row)
            belt = self._selected_belt_for_current_filter(data) or {}
            orden = belt.get("orden")
            try:
                orden = int(orden or 0)
            except Exception:
                orden = 0
            name = str(
                data.get("nombre") or
                data.get("name") or
                ""
            ).lower()
            return (-orden, name)

        return sorted(rows, key=sort_key)

    def _row_has_martial_art(self, row, wanted):
        data = self._row_to_dict(row)
        belts = data.get("belts") or []
        for belt in belts:
            ma = str(belt.get("martial_art") or belt.get("ma_name") or "").upper()
            if wanted in ma:
                return True
        return False

    def _get(self, row, *keys, default=""):
        if isinstance(row, dict):
            for k in keys:
                if k in row and row[k] not in (None, ""):
                    return row[k]
            return default

        # Fallback para tuplas del repo
        mapping = {
            "id": 0,
            "nombre": 1,
            "name": 1,
            "document": 4,
            "documento": 4,
            "phone": 2,
            "telefono": 2,
            "email": 3,
            "email_raw": 3,
            "type_document": 5,
            "category_name": 6,
            "status_name": 7,
            "estado": 7,
            "status": 7,
            "guardian_phone": 9,
            "guardian_email": 10,
            "guardian_name": 11,
            "belts": 8,
            "cinturon": 8,
            "belt_name": 8,
            "belt_color": 8,
            "color": 8,
            "pre_color": 8,
            "arte_marcial": 8,
            "martial_art": 8,
            "ma_name": 8,
            "grades": 8,
            "grade_color": 8,
        }

        for k in keys:
            idx = mapping.get(k)
            if idx is not None and len(row) > idx:
                return row[idx]

        return default

    def _row_to_dict(self, row):
        if isinstance(row, dict):
            return dict(row)

        return {
            "id":             self._get(row, "id"),
            "nombre":         self._get(row, "nombre"),
            "document":       self._get(row, "document"),
            "phone":          self._get(row, "phone"),
            "email":          self._get(row, "email"),
            "status_name":    self._get(row, "status_name"),
            "category_name":  self._get(row, "category_name"),
            "belts":          self._get(row, "belts", default=[]),
            "cinturon":       self._get(row, "cinturon"),
            "belt_color":     self._get(row, "belt_color"),
            "pre_color":      self._get(row, "pre_color"),
            "arte_marcial":   self._get(row, "arte_marcial"),
            "grades":         self._get(row, "grades"),
            "grade_color":    self._get(row, "grade_color"),
            "guardian_phone": self._get(row, "guardian_phone"),
            "guardian_email": self._get(row, "guardian_email"),
            "guardian_name":  self._get(row, "guardian_name"),
        }

    def _paint_table(self, rows):
        self.table.setRowCount(0)

        for row_data in rows:
            data = self._row_to_dict(row_data)
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setRowHeight(r, 76)

            self.table.setCellWidget(r, 0, self._student_cell(data))
            self.table.setCellWidget(r, 1, self._contact_cell(data))
            self.table.setCellWidget(r, 2, self._status_cell(data))
            self.table.setCellWidget(r, 3, self._belt_cell(data))

            id_item = QTableWidgetItem(str(data.get("id") or ""))
            id_item.setData(Qt.ItemDataRole.UserRole, data)
            id_item.setForeground(QColor("transparent"))
            self.table.setItem(r, 0, id_item)

            for c in range(1, 4):
                self.table.setItem(r, c, QTableWidgetItem(""))

        if rows:
            self.table.selectRow(0)

    # ─────────────────────────────────────────────
    # Cells
    # ─────────────────────────────────────────────
    def _student_cell(self, data):
        w = QWidget()
        w.setStyleSheet("""
            QWidget { background: transparent; border: none; }
            QLabel { background: transparent; border: none; }
        """)

        hl = QHBoxLayout(w)
        hl.setContentsMargins(12, 6, 12, 6)
        hl.setSpacing(12)

        name = data.get("nombre") or data.get("name") or "Estudiante"
        document = data.get("document") or data.get("documento") or data.get("id") or "\u2014"

        avatar = InitialsAvatar(name, 38, BLUE)

        col = QVBoxLayout()
        col.setSpacing(3)

        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: 900;
            background: transparent;
            border: none;
        """)

        col.addWidget(lbl_name)

        hl.addWidget(avatar)
        hl.addLayout(col, 1)
        return w

    def _contact_cell(self, data):
        w = QWidget()
        w.setStyleSheet("""
            QWidget { background: transparent; border: none; }
            QLabel { background: transparent; border: none; }
        """)

        vl = QVBoxLayout(w)
        vl.setContentsMargins(12, 8, 12, 8)
        vl.setSpacing(4)

        category = (data.get("category_name") or "").lower()
        is_kid = any(k in category for k in ("kid", "niño", "menor", "infant", "child", "junior"))

        guardian_phone = data.get("guardian_phone") or ""
        guardian_email = data.get("guardian_email") or ""

        if is_kid and (guardian_phone or guardian_email):
            email = guardian_email or "\u2014"
            phone = guardian_phone or "\u2014"
            guardian_name = data.get("guardian_name") or ""

            lbl_tag = QLabel(
                f"Acudiente{': ' + guardian_name[:16] if guardian_name else ''}"
            )
            lbl_tag.setStyleSheet(f"""
                color: #F97316;
                font-size: 9px;
                font-weight: 800;
                letter-spacing: 0.8px;
                background: transparent;
                border: none;
            """)
            vl.addWidget(lbl_tag)
        else:
            email = data.get("email") or data.get("email_raw") or "\u2014"
            phone = data.get("phone") or data.get("telefono") or "\u2014"

        lbl_email = QLabel(email)
        lbl_phone = QLabel(phone)

        lbl_email.setStyleSheet("""
            color: #D1D5DB;
            font-size: 12px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        lbl_phone.setStyleSheet("""
            color: #666666;
            font-size: 11px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)

        vl.addWidget(lbl_email)
        vl.addWidget(lbl_phone)
        return w

    def _status_cell(self, data):
        w = QWidget()
        w.setStyleSheet("""
            QWidget { background: transparent; border: none; }
            QLabel { background: transparent; border: none; }
        """)

        hl = QHBoxLayout(w)
        hl.setContentsMargins(12, 0, 12, 0)
        hl.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        status = data.get("status_name") or data.get("estado") or data.get("status") or "\u2014"
        badge = StatusBadge(status)

        hl.addWidget(badge)
        hl.addStretch()
        return w

    def _belt_cell(self, data):
        w = QWidget()
        w.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)

        root = QHBoxLayout(w)
        root.setContentsMargins(12, 6, 12, 6)
        root.setSpacing(14)

        belt_data = self._selected_belt_for_current_filter(data)

        if not belt_data:
            belt_widget = BeltWidget("#999999", None, 0, "#FFFFFF", "")

            col = QVBoxLayout()
            col.setSpacing(2)

            lbl_belt = QLabel("Sin cintur\u00f3n")
            lbl_art = QLabel("Sin arte")

            lbl_belt.setStyleSheet("color: white; font-size: 12px; font-weight: 900; border: none;")
            lbl_art.setStyleSheet("color: #666666; font-size: 10px; font-weight: 700; border: none;")

            col.addWidget(lbl_belt)
            col.addWidget(lbl_art)

            root.addWidget(belt_widget)
            root.addLayout(col, 1)

            return w

        belt_widget = BeltWidget(
            belt_data.get("belt_color") or belt_data.get("color") or "#FFFFFF",
            belt_data.get("pre_color"),
            belt_data.get("grades") or 0,
            belt_data.get("grade_color") or "#FFFFFF",
            belt_data.get("martial_art") or belt_data.get("ma_name") or ""
        )

        col = QVBoxLayout()
        col.setSpacing(2)

        lbl_belt = QLabel(belt_data.get("belt_name") or "Sin cintur\u00f3n")
        lbl_art = QLabel(belt_data.get("martial_art") or belt_data.get("ma_name") or "Sin arte")

        lbl_belt.setStyleSheet("color: white; font-size: 12px; font-weight: 900; border: none;")
        lbl_art.setStyleSheet("color: #666666; font-size: 10px; font-weight: 700; border: none;")

        col.addWidget(lbl_belt)
        col.addWidget(lbl_art)

        root.addWidget(belt_widget)
        root.addLayout(col, 1)

        return w

    # ─────────────────────────────────────────────
    # Selection
    # ─────────────────────────────────────────────
    def _on_selection_changed(self):
        row = self.table.currentRow()
        if row < 0:
            return

        item = self.table.item(row, 0)
        if not item:
            return

        data = item.data(Qt.ItemDataRole.UserRole) or {}

        self._selected_data = data
        self._selected_id = data.get("id")

        preview_data = dict(data)
        selected_belt = self._selected_belt_for_current_filter(preview_data)

        if selected_belt:
            preview_data.update({
                "belt_name": selected_belt.get("belt_name"),
                "belt_color": selected_belt.get("belt_color") or selected_belt.get("color"),
                "color": selected_belt.get("color") or selected_belt.get("belt_color"),
                "pre_color": selected_belt.get("pre_color"),
                "grades": selected_belt.get("grades"),
                "grade_color": selected_belt.get("grade_color"),
                "martial_art": selected_belt.get("martial_art") or selected_belt.get("ma_name"),
                "ma_name": selected_belt.get("ma_name") or selected_belt.get("martial_art"),
                "orden": selected_belt.get("orden"),
            })
        else:
            preview_data.update({
                "belt_name": "Sin cintur\u00f3n",
                "belt_color": "#999999",
                "color": "#999999",
                "pre_color": None,
                "grades": 0,
                "grade_color": "#FFFFFF",
                "martial_art": "Sin arte",
                "ma_name": "Sin arte",
                "orden": 0,
            })

        self.preview.set_student(preview_data)

    # ─────────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────────
    def _open_create(self):
        self._blur_on()
        result = None
        try:
            dialog = StudentForm(self.repo, parent=self)
            result = dialog.exec()
        finally:
            self._blur_off()
        if result:
            self._load()

    def _open_edit_selected(self):
        if not self._selected_id:
            QMessageBox.warning(self, "Selecciona un estudiante", "Primero selecciona un estudiante.")
            return

        self._blur_on()
        result = None
        try:
            dialog = StudentForm(self.repo, self._selected_id, parent=self)
            result = dialog.exec()
        finally:
            self._blur_off()
        if result:
            self._load()

    def _open_detail_selected(self):
        if not self._selected_id:
            QMessageBox.warning(self, "Selecciona un estudiante", "Primero selecciona un estudiante.")
            return

        self._blur_on()
        try:
            dialog = StudentDetail(self._selected_id, self.repo, parent=self)
            dialog.exec()
        finally:
            self._blur_off()

    def _delete_selected(self):
        if not self._selected_id:
            QMessageBox.warning(self, "Selecciona un estudiante", "Primero selecciona un estudiante.")
            return

        res = QMessageBox.question(
            self,
            "Eliminar estudiante",
            "¿Seguro que deseas eliminar este estudiante?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if res != QMessageBox.StandardButton.Yes:
            return

        try:
            self.repo.delete(self._selected_id)
            self._selected_id = None
            self._selected_data = None
            self._load()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ─────────────────────────────────────────────
    # Teclado
    # ─────────────────────────────────────────────
    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()

        if modifiers == Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_N:
            self._open_create()
            return

        if modifiers == Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_R:
            self._load()
            return

        if modifiers == Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_F:
            self.search_input.setFocus()
            self.search_input.selectAll()
            return

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._open_detail_selected()
            return

        if key == Qt.Key.Key_E:
            self._open_edit_selected()
            return

        if key == Qt.Key.Key_Delete:
            self._delete_selected()
            return

        if key == Qt.Key.Key_Escape:
            self.table.clearSelection()
            self.preview.set_student({})
            return

        super().keyPressEvent(event)