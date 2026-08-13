# ─── EVENT_WIDGETS ──────────────────────────────────────────────────

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QColor, QPixmap, QPainter, QPainterPath

# ── Color palette (matches main.py) ────────────────────────────────
BG_MAIN   = "#050505"
BG_CARD   = "#111111"
BG_CARD2  = "#141414"
BG_HOVER  = "#1A1A1A"
BORDER    = "#252525"
BORDER2   = "#303030"
RED       = "#C8102E"
RED_H     = "#E8152F"
TEXT_PRI  = "#F0F0F0"
TEXT_SEC  = "#9CA3AF"
TEXT_MUT  = "#6B7280"
TEXT_DIM  = "#3D4451"
GREEN     = "#22C55E"
YELLOW    = "#F59E0B"
PURPLE    = "#A855F7"


def format_event_date(d):
    if not d:
        return ""
    months = [
        "enero","febrero","marzo","abril","mayo","junio",
        "julio","agosto","septiembre","octubre","noviembre","diciembre"
    ]
    if hasattr(d, "strftime"):
        return f"{d.day} de {months[d.month - 1]} de {d.year}"
    return str(d)


def format_event_time(t):
    if not t:
        return ""
    if hasattr(t, "strftime"):
        return t.strftime("%H:%M")
    return str(t)[:5]


def format_relative_date(d):
    from datetime import date, timedelta
    if not d:
        return ""
    today = date.today()
    if hasattr(d, "date"):
        d = d.date()
    diff = (d - today).days
    if diff < 0:
        return "Finalizado"
    if diff == 0:
        return "Hoy"
    if diff == 1:
        return "Mañana"
    if diff <= 7:
        return f"Faltan {diff} días"
    return format_event_date(d)


def format_currency(amount):
    if amount is None:
        return "Gratis"
    try:
        val = float(amount)
    except (TypeError, ValueError):
        return "Gratis"
    if val == 0:
        return "Gratis"
    return f"${val:,.0f} COP"


# ── Status helpers ──────────────────────────────────────────────────

STATUS_MAP = {
    "draft":               ("Borrador",       TEXT_MUT,  TEXT_DIM),
    "published":           ("Publicado",       GREEN,     "#0D3320"),
    "registration_open":   ("Inscripci\u00f3n abierta", GREEN, "#0D3320"),
    "registration_closed": ("Inscripci\u00f3n cerrada", YELLOW, "#3D2E00"),
    "in_progress":         ("En curso",        PURPLE,    "#2D1B4E"),
    "completed":           ("Finalizado",      TEXT_MUT,  BG_CARD),
    "cancelled":           ("Cancelado",       "#EF4444", "#3D0D0D"),
    "postponed":           ("Aplazado",        YELLOW,    "#3D2E00"),
    "archived":            ("Archivado",       TEXT_DIM,  BG_CARD),
}


def get_status_style(status):
    return STATUS_MAP.get(status, ("Desconocido", TEXT_MUT, BG_CARD))


# ── EventStatusBadge ────────────────────────────────────────────────

class EventStatusBadge(QLabel):
    def __init__(self, status="draft", parent=None):
        super().__init__(parent)
        self.setObjectName("EventStatusBadge")
        self.set_status(status)

    def set_status(self, status):
        text, color, bg = get_status_style(status)
        self.setText(text.upper())
        self.setStyleSheet(f"""
            QLabel#EventStatusBadge {{
                color: {color};
                background-color: {bg};
                border: 1px solid {color}33;
                border-radius: 6px;
                padding: 3px 8px;
                font-size: 8px;
                font-weight: 900;
                letter-spacing: 0.8px;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
        """)


# ── EventFilterChip ─────────────────────────────────────────────────

class EventFilterChip(QPushButton):
    clicked_filter = pyqtSignal(str)

    def __init__(self, label, filter_key, parent=None):
        super().__init__(label, parent)
        self._filter_key = filter_key
        self._active = False
        self.setFixedHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style()
        self.clicked.connect(lambda: self.clicked_filter.emit(self._filter_key))

    def set_active(self, active):
        self._active = active
        self._update_style()

    def _update_style(self):
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {RED};
                    color: white;
                    border: 1px solid {RED_H};
                    border-radius: 8px;
                    padding: 0 14px;
                    font-size: 11px;
                    font-weight: 700;
                    font-family: 'Inter','Segoe UI',sans-serif;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BG_CARD2};
                    color: {TEXT_SEC};
                    border: 1px solid {BORDER};
                    border-radius: 8px;
                    padding: 0 14px;
                    font-size: 11px;
                    font-weight: 600;
                    font-family: 'Inter','Segoe UI',sans-serif;
                }}
                QPushButton:hover {{
                    background-color: {BG_HOVER};
                    color: {TEXT_PRI};
                    border-color: {BORDER2};
                }}
            """)


# ── EmptyState ──────────────────────────────────────────────────────

class EmptyState(QWidget):
    def __init__(self, icon_name="calendar", title="", subtitle="", action_text="", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        try:
            from app.main import IconLabel
            icon = IconLabel(icon_name, 48, TEXT_DIM)
        except Exception:
            icon = QLabel("\u2022")
            icon.setStyleSheet(f"color: {TEXT_DIM}; font-size: 48px;")

        icon_container = QHBoxLayout()
        icon_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container.addWidget(icon)
        layout.addLayout(icon_container)

        if title:
            lbl = QLabel(title)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"""
                color: {TEXT_SEC};
                font-size: 14px;
                font-weight: 600;
                font-family: 'Inter','Segoe UI',sans-serif;
            """)
            layout.addWidget(lbl)

        if subtitle:
            lbl2 = QLabel(subtitle)
            lbl2.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl2.setWordWrap(True)
            lbl2.setMaximumWidth(400)
            lbl2.setStyleSheet(f"""
                color: {TEXT_MUT};
                font-size: 12px;
                font-weight: 500;
                font-family: 'Inter','Segoe UI',sans-serif;
            """)
            layout.addWidget(lbl2)

        self._action_btn = None
        if action_text:
            self._action_btn = QPushButton(action_text)
            self._action_btn.setFixedHeight(36)
            self._action_btn.setMinimumWidth(160)
            self._action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._action_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {RED};
                    color: white;
                    border: 1px solid {RED_H};
                    border-radius: 8px;
                    font-size: 11px;
                    font-weight: 700;
                    font-family: 'Inter','Segoe UI',sans-serif;
                }}
                QPushButton:hover {{ background-color: {RED_H}; }}
            """)
            btn_row = QHBoxLayout()
            btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_row.addWidget(self._action_btn)
            layout.addLayout(btn_row)

    @property
    def action_button(self):
        return self._action_btn


# ── SkeletonCard ────────────────────────────────────────────────────

class SkeletonCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SkeletonCard")
        self.setMinimumHeight(280)
        self.setStyleSheet(f"""
            QFrame#SkeletonCard {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        cover = QFrame()
        cover.setFixedHeight(140)
        cover.setStyleSheet(f"background-color: #1A1A1A; border-top-left-radius: 14px; border-top-right-radius: 14px;")
        layout.addWidget(cover)

        body = QVBoxLayout()
        body.setContentsMargins(16, 14, 16, 14)
        body.setSpacing(8)

        for h in [14, 10, 10]:
            bar = QFrame()
            bar.setFixedHeight(h)
            bar.setStyleSheet(f"background-color: #1A1A1A; border-radius: 4px;")
            body.addWidget(bar)

        layout.addLayout(body)


# ── EventCard ───────────────────────────────────────────────────────

class EventCard(QFrame):
    clicked = pyqtSignal(int)
    follow_requested = pyqtSignal(int)
    interest_requested = pyqtSignal(int)

    def __init__(self, event_data, parent=None):
        super().__init__(parent)
        self._data = event_data
        self._event_id = event_data.get("id", 0)
        self.setObjectName("SocialEventCard")
        self.setMinimumHeight(320)
        self.setMaximumHeight(380)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._hovered = False
        self._apply_style()
        self._build_ui()

    def _apply_style(self):
        if self._hovered:
            self.setStyleSheet(f"""
                QFrame#SocialEventCard {{
                    background-color: #151515;
                    border: 1px solid {BORDER2};
                    border-radius: 14px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame#SocialEventCard {{
                    background-color: {BG_CARD};
                    border: 1px solid {BORDER};
                    border-radius: 14px;
                }}
            """)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        cover = QFrame()
        cover.setFixedHeight(140)
        cover.setStyleSheet(f"""
            background-color: #1A1A1A;
            border-top-left-radius: 14px;
            border-top-right-radius: 14px;
        """)

        cover_layout = QVBoxLayout(cover)
        cover_layout.setContentsMargins(12, 10, 12, 10)

        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        event_type = self._data.get("event_type", "")
        if event_type:
            type_badge = QLabel(event_type.upper()[:12])
            type_badge.setStyleSheet(f"""
                color: white;
                background-color: {self._data.get('color', RED)}CC;
                border-radius: 5px;
                padding: 2px 7px;
                font-size: 8px;
                font-weight: 900;
                letter-spacing: 0.5px;
                font-family: 'Inter','Segoe UI',sans-serif;
            """)
            top_row.addWidget(type_badge)

        top_row.addStretch()

        status = self._data.get("status", "draft")
        if status:
            badge = EventStatusBadge(status)
            top_row.addWidget(badge)

        cover_layout.addLayout(top_row)
        cover_layout.addStretch()

        layout.addWidget(cover)

        body = QVBoxLayout()
        body.setContentsMargins(16, 12, 16, 14)
        body.setSpacing(5)

        name = self._data.get("name", "Sin nombre")
        lbl_name = QLabel(name)
        lbl_name.setWordWrap(True)
        lbl_name.setMaximumHeight(36)
        lbl_name.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 14px;
            font-weight: 800;
            font-family: 'Inter','Segoe UI',sans-serif;
        """)
        body.addWidget(lbl_name)

        meta = QHBoxLayout()
        meta.setSpacing(6)
        date_text = format_event_date(self._data.get("event_date"))
        if date_text:
            meta.addWidget(self._meta_label(date_text))
        time_text = format_event_time(self._data.get("start_time"))
        if time_text:
            meta.addWidget(self._meta_label(f"\u2022 {time_text}"))
        body.addLayout(meta)

        loc = self._data.get("location") or self._data.get("venue_name") or ""
        if loc:
            body.addWidget(self._meta_label(loc))

        body.addSpacing(4)

        bottom = QHBoxLayout()
        bottom.setSpacing(8)

        rel = format_relative_date(self._data.get("event_date"))
        if rel and rel != "Finalizado":
            bottom.addWidget(self._meta_label(rel, YELLOW))
        elif rel == "Finalizado":
            bottom.addWidget(self._meta_label(rel, TEXT_MUT))

        bottom.addStretch()

        reg_count = self._data.get("registration_count", 0)
        capacity = self._data.get("capacity")
        if capacity:
            bottom.addWidget(self._meta_label(f"{reg_count}/{capacity}", TEXT_SEC))
        elif reg_count:
            bottom.addWidget(self._meta_label(f"{reg_count} inscritos", TEXT_SEC))

        body.addLayout(bottom)
        layout.addLayout(body, 1)

    def _meta_label(self, text, color=None):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            color: {color or TEXT_MUT};
            font-size: 10px;
            font-weight: 500;
            font-family: 'Inter','Segoe UI',sans-serif;
            background: transparent;
            border: none;
        """)
        return lbl

    def enterEvent(self, event):
        self._hovered = True
        self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._apply_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._event_id)
        super().mousePressEvent(event)


# ── FeaturedEventCard ───────────────────────────────────────────────

class FeaturedEventCard(QFrame):
    clicked = pyqtSignal(int)

    def __init__(self, event_data, parent=None):
        super().__init__(parent)
        self._data = event_data
        self._event_id = event_data.get("id", 0)
        self.setObjectName("FeaturedEventCard")
        self.setFixedHeight(300)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hovered = False
        self._apply_style()
        self._build_ui()

    def _apply_style(self):
        border = BORDER2 if self._hovered else BORDER
        self.setStyleSheet(f"""
            QFrame#FeaturedEventCard {{
                background-color: {BG_CARD};
                border: 1px solid {border};
                border-radius: 18px;
            }}
            QFrame#FeaturedEventCard QLabel {{
                background: transparent;
                border: none;
            }}
        """)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        cover = QFrame()
        cover.setStyleSheet("""
            background-color: #1A1A1A;
            border-top-left-radius: 18px;
            border-top-right-radius: 18px;
        """)
        cover.setFixedHeight(160)
        cover_layout = QVBoxLayout(cover)
        cover_layout.setContentsMargins(20, 16, 20, 16)

        featured_badge = QLabel("PR\u00d3XIMO EVENTO DESTACADO")
        featured_badge.setStyleSheet(f"""
            color: {RED_H};
            background-color: rgba(200, 16, 46, 0.15);
            border: 1px solid rgba(200, 16, 46, 0.3);
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 8px;
            font-weight: 900;
            letter-spacing: 1px;
            font-family: 'Inter','Segoe UI',sans-serif;
        """)
        featured_badge.setFixedWidth(featured_badge.sizeHint().width() + 20)
        cover_layout.addWidget(featured_badge)
        cover_layout.addStretch()
        layout.addWidget(cover)

        body = QVBoxLayout()
        body.setContentsMargins(20, 14, 20, 16)
        body.setSpacing(6)

        event_type = self._data.get("event_type", "")
        if event_type:
            lbl_type = QLabel(event_type.upper())
            lbl_type.setStyleSheet(f"""
                color: {self._data.get('color', RED_H)};
                font-size: 9px;
                font-weight: 900;
                letter-spacing: 1px;
            """)
            body.addWidget(lbl_type)

        lbl_name = QLabel(self._data.get("name", ""))
        lbl_name.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 18px;
            font-weight: 900;
        """)
        body.addWidget(lbl_name)

        meta = QHBoxLayout()
        meta.setSpacing(12)
        date_text = format_event_date(self._data.get("event_date"))
        if date_text:
            meta.addWidget(self._lbl(date_text))
        loc = self._data.get("location") or self._data.get("venue_name") or ""
        if loc:
            meta.addWidget(self._lbl(loc))
        rel = format_relative_date(self._data.get("event_date"))
        if rel:
            meta.addWidget(self._lbl(rel, YELLOW))
        meta.addStretch()
        body.addLayout(meta)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        btn_view = QPushButton("Ver evento")
        btn_view.setFixedHeight(34)
        btn_view.setMinimumWidth(120)
        btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_view.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED};
                color: white;
                border: 1px solid {RED_H};
                border-radius: 8px;
                font-size: 11px;
                font-weight: 700;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QPushButton:hover {{ background-color: {RED_H}; }}
        """)
        btn_view.clicked.connect(lambda: self.clicked.emit(self._event_id))
        btn_row.addWidget(btn_view)
        btn_row.addStretch()

        body.addLayout(btn_row)
        layout.addLayout(body, 1)

    def _lbl(self, text, color=None):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {color or TEXT_MUT}; font-size: 10px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
        return lbl

    def enterEvent(self, event):
        self._hovered = True
        self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._apply_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._event_id)
        super().mousePressEvent(event)


# ── ParticipantCard ─────────────────────────────────────────────────

class ParticipantCard(QFrame):
    def __init__(self, participant_data, parent=None):
        super().__init__(parent)
        self._data = participant_data
        self.setObjectName("ParticipantCard")
        self.setFixedHeight(56)
        self.setStyleSheet(f"""
            QFrame#ParticipantCard {{
                background-color: {BG_CARD2};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
            QFrame#ParticipantCard QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(12)

        name = f"{participant_data.get('first_name', '')} {participant_data.get('last_name', '')}".strip()
        initials = "".join(p[0].upper() for p in name.split()[:2]) or "?"

        avatar = QLabel(initials)
        avatar.setFixedSize(34, 34)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background-color: {PURPLE};
            color: white;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 900;
            font-family: 'Inter','Segoe UI',sans-serif;
        """)
        layout.addWidget(avatar)

        info = QVBoxLayout()
        info.setSpacing(1)
        lbl_name = QLabel(name or "Sin nombre")
        lbl_name.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px; font-weight: 700;")
        info.addWidget(lbl_name)

        status = participant_data.get("registration_status", "pending")
        status_text, status_color, _ = get_status_style(status)
        lbl_status = QLabel(status_text)
        lbl_status.setStyleSheet(f"color: {status_color}; font-size: 9px; font-weight: 600;")
        info.addWidget(lbl_status)

        layout.addLayout(info, 1)


# ── ScheduleItemCard ────────────────────────────────────────────────

class ScheduleItemCard(QFrame):
    def __init__(self, item_data, can_edit=False, parent=None):
        super().__init__(parent)
        self._data = item_data
        self.setObjectName("ScheduleItemCard")
        self.setStyleSheet(f"""
            QFrame#ScheduleItemCard {{
                background-color: {BG_CARD2};
                border: 1px solid {BORDER};
                border-left: 3px solid {RED};
                border-radius: 10px;
            }}
            QFrame#ScheduleItemCard QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(14)

        time_col = QVBoxLayout()
        time_col.setSpacing(2)
        time_col.setFixedWidth(60)

        starts = item_data.get("starts_at", "")
        ends = item_data.get("ends_at", "")
        lbl_time = QLabel(format_event_time(starts))
        lbl_time.setStyleSheet(f"color: {RED_H}; font-size: 13px; font-weight: 800;")
        time_col.addWidget(lbl_time)

        if ends:
            lbl_end = QLabel(format_event_time(ends))
            lbl_end.setStyleSheet(f"color: {TEXT_MUT}; font-size: 9px; font-weight: 500;")
            time_col.addWidget(lbl_end)

        layout.addLayout(time_col)

        info = QVBoxLayout()
        info.setSpacing(3)
        lbl_title = QLabel(item_data.get("title", ""))
        lbl_title.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px; font-weight: 700;")
        info.addWidget(lbl_title)

        desc = item_data.get("description", "")
        if desc:
            lbl_desc = QLabel(desc[:100])
            lbl_desc.setWordWrap(True)
            lbl_desc.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 500;")
            info.addWidget(lbl_desc)

        loc = item_data.get("location", "")
        if loc:
            lbl_loc = QLabel(loc)
            lbl_loc.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; font-weight: 500;")
            info.addWidget(lbl_loc)

        layout.addLayout(info, 1)


# ── EventPostCard ───────────────────────────────────────────────────

class EventPostCard(QFrame):
    def __init__(self, post_data, can_edit=False, parent=None):
        super().__init__(parent)
        self._data = post_data
        self.setObjectName("EventPostCard")
        self.setStyleSheet(f"""
            QFrame#EventPostCard {{
                background-color: {BG_CARD2};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
            QFrame#EventPostCard QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(8)

        author = post_data.get("author_name", "Autor")
        lbl_author = QLabel(author)
        lbl_author.setStyleSheet(f"color: {TEXT_PRI}; font-size: 11px; font-weight: 700;")
        header.addWidget(lbl_author)

        if post_data.get("is_pinned"):
            pin = QLabel("FIJADO")
            pin.setStyleSheet(f"""
                color: {YELLOW};
                background-color: rgba(245, 158, 11, 0.10);
                border: 1px solid rgba(245, 158, 11, 0.25);
                border-radius: 5px;
                padding: 2px 6px;
                font-size: 7px;
                font-weight: 900;
                letter-spacing: 0.5px;
            """)
            header.addWidget(pin)

        header.addStretch()

        created = post_data.get("created_at", "")
        if created:
            date_str = created.strftime("%d/%m/%Y %H:%M") if hasattr(created, "strftime") else str(created)[:16]
            lbl_date = QLabel(date_str)
            lbl_date.setStyleSheet(f"color: {TEXT_DIM}; font-size: 9px; font-weight: 500;")
            header.addWidget(lbl_date)

        layout.addLayout(header)

        content = post_data.get("content", "")
        if content:
            lbl_content = QLabel(content)
            lbl_content.setWordWrap(True)
            lbl_content.setStyleSheet(f"""
                color: {TEXT_SEC};
                font-size: 12px;
                font-weight: 500;
                line-height: 1.4;
            """)
            layout.addWidget(lbl_content)


# ── load_cover_pixmap ──────────────────────────────────────────────

def load_cover_pixmap(path, target_size):
    """Load an image from path, scale to target_size (QSize) keeping aspect ratio."""
    if not path:
        return None
    try:
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return None
        return pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
    except Exception:
        return None


# ── EventsGlassOverlay ─────────────────────────────────────────────

class EventsGlassOverlay(QFrame):
    """Dark semi-transparent overlay for EventsView."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EventsGlassOverlay")
        self.setStyleSheet(
            "QFrame#EventsGlassOverlay {"
            "  background-color: rgba(0, 0, 0, 150);"
            "  border: none;"
            "}"
        )
        self.hide()

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._anim_in = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._anim_in.setDuration(180)
        self._anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._anim_out = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._anim_out.setDuration(180)
        self._anim_out.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_out.finished.connect(self._on_fade_out_done)

    def fade_in(self):
        self.show()
        self.raise_()
        self._anim_out.stop()
        self._anim_in.setStartValue(self._opacity_effect.opacity())
        self._anim_in.setEndValue(1.0)
        self._anim_in.start()

    def fade_out(self):
        self._anim_in.stop()
        self._anim_out.setStartValue(self._opacity_effect.opacity())
        self._anim_out.setEndValue(0.0)
        self._anim_out.start()

    def force_hide(self):
        self._anim_in.stop()
        self._anim_out.stop()
        self._opacity_effect.setOpacity(0.0)
        self.hide()

    def _on_fade_out_done(self):
        self.hide()


# ── EventLivePreview ───────────────────────────────────────────────

class EventLivePreview(QFrame):
    """Non-interactive preview card that mirrors EventCard appearance."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EventLivePreview")
        self.setStyleSheet(f"""
            QFrame#EventLivePreview {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
            QFrame#EventLivePreview QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        self.setMinimumWidth(320)
        self.setMaximumWidth(420)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._cover = QFrame()
        self._cover.setFixedHeight(160)
        self._cover.setStyleSheet(f"""
            background-color: #1A1A1A;
            border-top-left-radius: 14px;
            border-top-right-radius: 14px;
        """)
        cover_layout = QVBoxLayout(self._cover)
        cover_layout.setContentsMargins(14, 12, 14, 12)

        self._cover_img = QLabel()
        self._cover_img.setFixedHeight(100)
        self._cover_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cover_img.setStyleSheet(f"""
            background-color: #111;
            border-radius: 8px;
            color: {TEXT_MUT};
            font-size: 9px;
            font-weight: 500;
            font-family: 'Inter','Segoe UI',sans-serif;
        """)
        self._cover_img.setText("Sin portada")
        cover_layout.addWidget(self._cover_img)

        top_row = QHBoxLayout()
        top_row.setSpacing(6)
        self._type_badge = QLabel("")
        self._type_badge.setStyleSheet(f"""
            color: white;
            background-color: {RED}CC;
            border-radius: 5px;
            padding: 2px 7px;
            font-size: 8px;
            font-weight: 900;
            letter-spacing: 0.5px;
            font-family: 'Inter','Segoe UI',sans-serif;
        """)
        self._type_badge.hide()
        top_row.addWidget(self._type_badge)
        top_row.addStretch()
        self._status_badge = EventStatusBadge("draft")
        top_row.addWidget(self._status_badge)
        cover_layout.addLayout(top_row)

        layout.addWidget(self._cover)

        body = QVBoxLayout()
        body.setContentsMargins(16, 14, 16, 14)
        body.setSpacing(5)

        self._name_lbl = QLabel("Nombre del evento")
        self._name_lbl.setWordWrap(True)
        self._name_lbl.setMaximumHeight(40)
        self._name_lbl.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 15px;
            font-weight: 800;
            font-family: 'Inter','Segoe UI',sans-serif;
        """)
        body.addWidget(self._name_lbl)

        self._short_desc_lbl = QLabel("La descripción breve aparecerá aquí.")
        self._short_desc_lbl.setWordWrap(True)
        self._short_desc_lbl.setMaximumHeight(36)
        self._short_desc_lbl.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 11px;
            font-weight: 500;
            font-family: 'Inter','Segoe UI',sans-serif;
        """)
        body.addWidget(self._short_desc_lbl)

        meta = QHBoxLayout()
        meta.setSpacing(8)
        self._date_lbl = QLabel("")
        self._date_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif;")
        meta.addWidget(self._date_lbl)
        self._time_lbl = QLabel("")
        self._time_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif;")
        meta.addWidget(self._time_lbl)
        meta.addStretch()
        body.addLayout(meta)

        loc_row = QHBoxLayout()
        loc_row.setSpacing(8)
        self._loc_lbl = QLabel("")
        self._loc_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif;")
        loc_row.addWidget(self._loc_lbl)
        self._city_lbl = QLabel("")
        self._city_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif;")
        loc_row.addWidget(self._city_lbl)
        loc_row.addStretch()
        body.addLayout(loc_row)

        body.addSpacing(4)

        bottom = QHBoxLayout()
        bottom.setSpacing(8)
        self._price_lbl = QLabel("Gratis")
        self._price_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 700; font-family: 'Inter','Segoe UI',sans-serif;")
        bottom.addWidget(self._price_lbl)
        self._cap_lbl = QLabel("Sin límite")
        self._cap_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif;")
        bottom.addWidget(self._cap_lbl)
        bottom.addStretch()
        body.addLayout(bottom)

        layout.addLayout(body, 1)

    def update_event(self, data):
        """Update all preview labels from a data dict."""
        name = data.get("name", "")
        self._name_lbl.setText(name or "Nombre del evento")

        st = data.get("short_description", "")
        self._short_desc_lbl.setText(st or "La descripción breve aparecerá aquí.")

        ev_type = data.get("event_type", "")
        if ev_type:
            self._type_badge.setText(ev_type.upper()[:14])
            self._type_badge.setStyleSheet(f"""
                color: white;
                background-color: {data.get('color', RED)}CC;
                border-radius: 5px;
                padding: 2px 7px;
                font-size: 8px;
                font-weight: 900;
                letter-spacing: 0.5px;
                font-family: 'Inter','Segoe UI',sans-serif;
            """)
            self._type_badge.show()
        else:
            self._type_badge.hide()

        status = data.get("status", "draft")
        self._status_badge.set_status(status)

        ed = data.get("event_date")
        self._date_lbl.setText(format_event_date(ed) or "")

        start = data.get("start_time")
        self._time_lbl.setText(format_event_time(start) or "")

        loc = data.get("location") or data.get("venue_name") or ""
        self._loc_lbl.setText(loc)
        self._loc_lbl.setVisible(bool(loc))

        city = data.get("city") or ""
        self._city_lbl.setText(city)
        self._city_lbl.setVisible(bool(city))

        price = data.get("price", 0)
        self._price_lbl.setText(format_currency(price))

        cap = data.get("capacity")
        if cap:
            self._cap_lbl.setText(f"{cap} cupos")
        else:
            self._cap_lbl.setText("Sin límite")

        cover_path = data.get("cover_image_path")
        if cover_path:
            from PyQt6.QtCore import QSize
            pix = load_cover_pixmap(cover_path, QSize(360, 100))
            if pix:
                self._cover_img.setPixmap(pix)
                self._cover_img.setStyleSheet(f"""
                    border-radius: 8px;
                    border: none;
                """)
            else:
                self._cover_img.setText("Error al cargar")
        else:
            self._cover_img.setPixmap(QPixmap())
            color = data.get("color", "#3B82F6")
            self._cover_img.setText("Sin portada")
            self._cover_img.setStyleSheet(f"""
                background-color: {color}22;
                border: 1px dashed {color}55;
                border-radius: 8px;
                color: {TEXT_MUT};
                font-size: 9px;
                font-weight: 500;
                font-family: 'Inter','Segoe UI',sans-serif;
            """)
