# ─── EVENT_MANAGEMENT_VIEW ──────────────────────────────────────────

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QComboBox,
    QGridLayout, QMenu,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor

from core.debug import debug_log
from views.events.event_widgets import (
    BG_MAIN, BG_CARD, BG_CARD2, BG_HOVER, BORDER, BORDER2,
    RED, RED_H, TEXT_PRI, TEXT_SEC, TEXT_MUT, TEXT_DIM,
    GREEN, YELLOW, PURPLE,
    EventStatusBadge, EventCard, EmptyState,
    format_event_date, format_event_time,
)


class EventManagementView(QWidget):
    """Management view for event organizers and admins."""

    def __init__(self, current_user, repo, parent_view, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.current_user_id = current_user.get("id") if current_user else None
        self.repo = repo
        self.parent_view = parent_view
        self._events = []

        self.setObjectName("EventManagementView")
        self._build_ui()
        QTimer.singleShot(100, self.refresh)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame()
        header.setObjectName("ManagementHeader")
        header.setStyleSheet(f"""
            QFrame#ManagementHeader {{
                background-color: {BG_MAIN};
                border-bottom: 1px solid {BORDER};
            }}
            QFrame#ManagementHeader QLabel {{
                background: transparent; border: none;
            }}
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(28, 18, 28, 18)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        lbl = QLabel("Gestión de eventos")
        lbl.setStyleSheet(f"color: {TEXT_PRI}; font-size: 16px; font-weight: 800; font-family: 'Inter','Segoe UI',sans-serif;")
        title_col.addWidget(lbl)
        lbl2 = QLabel("Administra los eventos que organizas")
        lbl2.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif;")
        title_col.addWidget(lbl2)
        h_layout.addLayout(title_col)
        h_layout.addStretch()

        root.addWidget(header)

        filter_bar = QFrame()
        filter_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_MAIN};
                border-bottom: 1px solid {BORDER};
            }}
        """)
        fb_layout = QHBoxLayout(filter_bar)
        fb_layout.setContentsMargins(28, 8, 28, 8)

        self._status_combo = QComboBox()
        self._status_combo.setFixedHeight(32)
        self._status_combo.setMinimumWidth(160)
        self._status_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {BG_CARD2}; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 0 12px; font-size: 11px; font-weight: 600;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QComboBox:hover {{ border-color: {BORDER2}; }}
            QComboBox::drop-down {{
                border: none; width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {BG_CARD}; color: {TEXT_SEC};
                border: 1px solid {BORDER}; selection-background-color: {BG_HOVER};
                selection-color: {TEXT_PRI};
            }}
        """)
        self._status_combo.addItem("Todos", "all")
        self._status_combo.addItem("Borradores", "draft")
        self._status_combo.addItem("Publicados", "published")
        self._status_combo.addItem("Inscripción abierta", "registration_open")
        self._status_combo.addItem("En curso", "in_progress")
        self._status_combo.addItem("Finalizados", "completed")
        self._status_combo.currentIndexChanged.connect(self._on_status_changed)
        fb_layout.addWidget(self._status_combo)
        fb_layout.addStretch()

        root.addWidget(filter_bar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: {BG_MAIN}; border: none; }}
            QScrollBar:vertical {{ background: transparent; width: 8px; }}
            QScrollBar::handle:vertical {{ background: #333; border-radius: 4px; min-height: 40px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

        content = QWidget()
        content.setStyleSheet(f"background-color: {BG_MAIN};")
        self._grid = QGridLayout(content)
        self._grid.setContentsMargins(28, 16, 28, 16)
        self._grid.setSpacing(16)

        self._empty = None

        scroll.setWidget(content)
        root.addWidget(scroll, 1)

    def _on_status_changed(self, index):
        self.refresh()

    def refresh(self):
        self._clear_grid()
        try:
            status = self._status_combo.currentData()
            if status == "all":
                status = None
            events = self.repo.get_managed_events(self.current_user_id, status=status)
            self._events = events

            if not events:
                self._empty = EmptyState(
                    "event",
                    "Aún no hay eventos para gestionar",
                    "Crea tu primer evento desde el botón \"Crear evento\" ubicado en la parte superior.",
                )
                self._grid.addWidget(self._empty, 0, 0, 1, 3)
                return

            for i, ev in enumerate(events):
                card = self._management_card(ev)
                self._grid.addWidget(card, i // 3, i % 3)

        except Exception as e:
            debug_log(f"[EventManagementView] Error: {e}")

    def _management_card(self, ev):
        card = QFrame()
        card.setObjectName("MgmtCard")
        card.setMinimumHeight(340)
        card.setMaximumHeight(400)
        card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        card.setStyleSheet(f"""
            QFrame#MgmtCard {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
            QFrame#MgmtCard:hover {{
                border-color: {BORDER2};
                background-color: #151515;
            }}
            QFrame#MgmtCard QLabel {{
                background: transparent; border: none;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        cover = QFrame()
        cover.setFixedHeight(140)
        cover.setStyleSheet(f"""
            background-color: #1A1A1A;
            border-top-left-radius: 14px; border-top-right-radius: 14px;
        """)
        cover_layout = QVBoxLayout(cover)
        cover_layout.setContentsMargins(14, 10, 14, 10)

        top = QHBoxLayout()
        top.setSpacing(6)
        badge = EventStatusBadge(ev.get("status", "draft"))
        top.addWidget(badge)
        top.addStretch()

        btn_menu = QPushButton("⋯")
        btn_menu.setFixedSize(28, 28)
        btn_menu.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_menu.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD2}; color: {TEXT_SEC}; border: 1px solid {BORDER};
                border-radius: 7px; font-size: 13px; font-weight: 800;
            }}
            QPushButton:hover {{ background: {BG_HOVER}; color: {TEXT_PRI}; border-color: {BORDER2}; }}
        """)
        menu = QMenu()
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {BG_CARD}; color: {TEXT_SEC};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 16px; border-radius: 4px;
                font-size: 11px; font-weight: 600;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QMenu::item:selected {{
                background-color: {BG_HOVER}; color: {TEXT_PRI};
            }}
        """)
        ev_id = ev.get("id")
        status = ev.get("status", "draft")

        act_view = menu.addAction("Ver detalle")
        act_view.triggered.connect(lambda _, eid=ev_id: self.parent_view.open_event_detail(eid))

        act_edit = menu.addAction("Editar")
        act_edit.triggered.connect(lambda _, eid=ev_id: self._edit_event(eid))

        menu.addSeparator()

        if status == "draft":
            act_pub = menu.addAction("Publicar")
            act_pub.triggered.connect(lambda _, eid=ev_id: self._change_status(eid, "published"))
        elif status in ("published", "registration_closed"):
            act_reg = menu.addAction("Abrir inscripción")
            act_reg.triggered.connect(lambda _, eid=ev_id: self._change_status(eid, "registration_open"))
        elif status == "registration_open":
            act_close = menu.addAction("Cerrar inscripción")
            act_close.triggered.connect(lambda _, eid=ev_id: self._change_status(eid, "registration_closed"))
            act_progress = menu.addAction("Marcar en curso")
            act_progress.triggered.connect(lambda _, eid=ev_id: self._change_status(eid, "in_progress"))

        if status != "completed":
            act_complete = menu.addAction("Finalizar")
            act_complete.triggered.connect(lambda _, eid=ev_id: self._change_status(eid, "completed"))

        if status == "draft":
            menu.addSeparator()
            act_delete = menu.addAction("Eliminar borrador")
            act_delete.triggered.connect(lambda _, eid=ev_id: self._delete_draft(eid))

        btn_menu.setMenu(menu)
        top.addWidget(btn_menu)

        cover_layout.addLayout(top)
        cover_layout.addStretch()
        layout.addWidget(cover)

        body = QVBoxLayout()
        body.setContentsMargins(16, 12, 16, 14)
        body.setSpacing(4)

        ev_type = ev.get("event_type", "")
        if ev_type:
            lbl_type = QLabel(ev_type.upper()[:12])
            lbl_type.setStyleSheet(f"color: {ev.get('color', RED_H)}; font-size: 8px; font-weight: 900; letter-spacing: 0.8px; font-family: 'Inter','Segoe UI',sans-serif;")
            body.addWidget(lbl_type)

        lbl_name = QLabel(ev.get("name", "Sin nombre"))
        lbl_name.setWordWrap(True)
        lbl_name.setMaximumHeight(36)
        lbl_name.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 800; font-family: 'Inter','Segoe UI',sans-serif;")
        body.addWidget(lbl_name)

        meta = QHBoxLayout()
        meta.setSpacing(6)
        date_text = format_event_date(ev.get("event_date"))
        if date_text:
            lbl = QLabel(date_text)
            lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif;")
            meta.addWidget(lbl)
        time_text = format_event_time(ev.get("start_time"))
        if time_text:
            lbl = QLabel(f"\u2022 {time_text}")
            lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif;")
            meta.addWidget(lbl)
        meta.addStretch()
        body.addLayout(meta)

        bottom = QHBoxLayout()
        bottom.setSpacing(8)
        reg = ev.get("registration_count", 0)
        cap = ev.get("capacity")
        if cap:
            lbl = QLabel(f"{reg}/{cap} inscritos")
            lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif;")
            bottom.addWidget(lbl)
        elif reg:
            lbl = QLabel(f"{reg} inscritos")
            lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif;")
            bottom.addWidget(lbl)
        bottom.addStretch()
        body.addLayout(bottom)

        layout.addLayout(body, 1)

        card.mousePressEvent = lambda e, eid=ev_id: self.parent_view.open_event_detail(eid)

        return card

    def _edit_event(self, event_id):
        self.parent_view.open_event_editor(event_id)

    def _change_status(self, event_id, status):
        try:
            self.repo.set_event_status(event_id, status, self.current_user_id)
            self.refresh()
        except Exception as e:
            debug_log(f"[EventManagementView] Error cambiando estado: {e}")

    def _delete_draft(self, event_id):
        try:
            self.repo.delete_draft_event(event_id, self.current_user_id)
            self.refresh()
        except Exception as e:
            debug_log(f"[EventManagementView] Error eliminando: {e}")

    def _clear_grid(self):
        self._events.clear()
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()
