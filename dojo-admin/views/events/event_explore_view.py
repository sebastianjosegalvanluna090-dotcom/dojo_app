# ─── EVENT_EXPLORE_VIEW ─────────────────────────────────────────────

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QLineEdit,
    QComboBox, QGridLayout, QSizePolicy, QSpacerItem,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor

from core.debug import debug_log
from views.events.event_widgets import (
    BG_MAIN, BG_CARD, BG_CARD2, BG_HOVER, BORDER, BORDER2,
    RED, RED_H, TEXT_PRI, TEXT_SEC, TEXT_MUT, TEXT_DIM,
    GREEN, YELLOW, PURPLE,
    EventCard, FeaturedEventCard, EventFilterChip,
    EmptyState, SkeletonCard,
    format_event_date, format_event_time, format_relative_date,
)


class EventExploreView(QWidget):
    """Explore events, user's events, or calendar view."""

    def __init__(self, current_user, repo, parent_view, mode="explore", parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.current_user_id = current_user.get("id") if current_user else None
        self.repo = repo
        self.parent_view = parent_view
        self._mode = mode
        self._events = []
        self._featured = None
        self._current_filter = "all"
        self._offset = 0
        self._limit = 12
        self._loading = False
        self._has_more = True

        self.setObjectName("EventExploreView")
        self._build_ui()

        QTimer.singleShot(100, self.refresh)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        if self._mode == "explore":
            self._build_explore_header(root)
        elif self._mode == "user_events":
            self._build_user_events_header(root)
        elif self._mode == "calendar":
            self._build_calendar(root)
            return

        self._build_filters(root)
        self._build_scroll_area(root)

    # ── Explore header ────────────────────────────────────────────

    def _build_explore_header(self, root):
        header = QFrame()
        header.setObjectName("ExploreHeader")
        header.setStyleSheet(f"""
            QFrame#ExploreHeader {{
                background-color: {BG_MAIN};
                border-bottom: 1px solid {BORDER};
            }}
            QFrame#ExploreHeader QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        layout = QVBoxLayout(header)
        layout.setContentsMargins(28, 20, 28, 16)
        layout.setSpacing(8)

        lbl = QLabel("Descubre eventos")
        lbl.setStyleSheet(f"color: {TEXT_PRI}; font-size: 16px; font-weight: 800; font-family: 'Inter','Segoe UI',sans-serif;")
        layout.addWidget(lbl)

        lbl2 = QLabel("Torneos, seminarios, exámenes y más")
        lbl2.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif;")
        layout.addWidget(lbl2)

        root.addWidget(header)

    # ── User events header ────────────────────────────────────────

    def _build_user_events_header(self, root):
        header = QFrame()
        header.setObjectName("UserEventsHeader")
        header.setStyleSheet(f"""
            QFrame#UserEventsHeader {{
                background-color: {BG_MAIN};
                border-bottom: 1px solid {BORDER};
            }}
            QFrame#UserEventsHeader QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        layout = QVBoxLayout(header)
        layout.setContentsMargins(28, 20, 28, 16)

        lbl = QLabel("Mis eventos")
        lbl.setStyleSheet(f"color: {TEXT_PRI}; font-size: 16px; font-weight: 800; font-family: 'Inter','Segoe UI',sans-serif;")
        layout.addWidget(lbl)

        lbl2 = QLabel("Eventos que sigues, te interesan o en los que participas")
        lbl2.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif;")
        layout.addWidget(lbl2)

        root.addWidget(header)

    # ── Filters ───────────────────────────────────────────────────

    def _build_filters(self, root):
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_MAIN};
                border-bottom: 1px solid {BORDER};
            }}
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(28, 10, 28, 10)
        filter_layout.setSpacing(6)

        if self._mode == "explore":
            self._filters = [
                ("all", "Todos"),
                ("upcoming", "Próximos"),
                ("this_month", "Este mes"),
                ("registration_open", "Inscripción abierta"),
            ]
            self._filter_group = None
            for key, label in self._filters:
                chip = EventFilterChip(label, key)
                chip.clicked_filter.connect(self._on_filter_clicked)
                filter_layout.addWidget(chip)
                if self._filter_group is None:
                    self._filter_group = []
                self._filter_group.append(chip)
        elif self._mode == "user_events":
            self._filters = [
                ("all", "Todos"),
                ("following", "Siguiendo"),
                ("interested", "Interesado"),
                ("attending", "Asistiré"),
                ("registered", "Inscrito"),
                ("organized", "Organizando"),
                ("past", "Pasados"),
            ]
            self._filter_group = []
            for key, label in self._filters:
                chip = EventFilterChip(label, key)
                chip.clicked_filter.connect(self._on_filter_clicked)
                filter_layout.addWidget(chip)
                self._filter_group.append(chip)

        filter_layout.addStretch()
        root.addWidget(filter_frame)

    # ── Scroll area with grid ─────────────────────────────────────

    def _build_scroll_area(self, root):
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {BG_MAIN};
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: #333;
                border-radius: 4px;
                min-height: 40px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)

        self._scroll_content = QWidget()
        self._scroll_content.setStyleSheet(f"background-color: {BG_MAIN};")
        self._scroll_layout = QVBoxLayout(self._scroll_content)
        self._scroll_layout.setContentsMargins(28, 16, 28, 16)
        self._scroll_layout.setSpacing(16)

        self._featured_container = QFrame()
        self._featured_container.setStyleSheet("background: transparent; border: none;")
        self._featured_layout = QVBoxLayout(self._featured_container)
        self._featured_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll_layout.addWidget(self._featured_container)

        self._grid_widget = QWidget()
        self._grid_widget.setStyleSheet("background: transparent; border: none;")
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        self._grid_layout.setSpacing(16)
        self._scroll_layout.addWidget(self._grid_widget)

        self._empty_state = None

        self._load_more_btn = QPushButton("Cargar más")
        self._load_more_btn.setFixedHeight(38)
        self._load_more_btn.setMinimumWidth(160)
        self._load_more_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._load_more_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_CARD2};
                color: {TEXT_SEC};
                border: 1px solid {BORDER};
                border-radius: 10px;
                font-size: 11px;
                font-weight: 700;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QPushButton:hover {{ background-color: {BG_HOVER}; color: {TEXT_PRI}; border-color: {BORDER2}; }}
        """)
        self._load_more_btn.clicked.connect(self._load_more)
        self._load_more_btn.hide()
        load_more_row = QHBoxLayout()
        load_more_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        load_more_row.addWidget(self._load_more_btn)
        self._scroll_layout.addLayout(load_more_row)

        self._skeletons = []
        self.scroll.setWidget(self._scroll_content)
        root.addWidget(self.scroll, 1)

    # ── Calendar mode ─────────────────────────────────────────────

    def _build_calendar(self, root):
        from datetime import date, timedelta
        import calendar as cal_mod

        header = QFrame()
        header.setObjectName("CalendarHeader")
        header.setStyleSheet(f"""
            QFrame#CalendarHeader {{
                background-color: {BG_MAIN};
                border-bottom: 1px solid {BORDER};
            }}
            QFrame#CalendarHeader QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(28, 16, 28, 16)
        h_layout.setSpacing(12)

        lbl = QLabel("Calendario de eventos")
        lbl.setStyleSheet(f"color: {TEXT_PRI}; font-size: 16px; font-weight: 800; font-family: 'Inter','Segoe UI',sans-serif;")
        h_layout.addWidget(lbl)
        h_layout.addStretch()
        root.addWidget(header)

        today = date.today()
        self._cal_year = today.year
        self._cal_month = today.month

        nav_frame = QFrame()
        nav_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_MAIN};
                border-bottom: 1px solid {BORDER};
            }}
            QFrame QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(28, 10, 28, 10)
        nav_layout.setSpacing(16)

        btn_prev = QPushButton("<")
        btn_prev.setFixedSize(30, 30)
        btn_prev.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_prev.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD2}; color: {TEXT_SEC}; border: 1px solid {BORDER};
                border-radius: 8px; font-size: 14px; font-weight: 800;
            }}
            QPushButton:hover {{ background: {BG_HOVER}; color: {TEXT_PRI}; }}
        """)
        btn_prev.clicked.connect(self._cal_prev_month)
        nav_layout.addWidget(btn_prev)

        months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                      "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self._cal_month_label = QLabel(f"{months_es[self._cal_month]} {self._cal_year}")
        self._cal_month_label.setStyleSheet(f"color: {TEXT_PRI}; font-size: 14px; font-weight: 800; font-family: 'Inter','Segoe UI',sans-serif;")
        nav_layout.addWidget(self._cal_month_label)

        btn_next = QPushButton(">")
        btn_next.setFixedSize(30, 30)
        btn_next.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_next.setStyleSheet(btn_prev.styleSheet())
        btn_next.clicked.connect(self._cal_next_month)
        nav_layout.addWidget(btn_next)

        nav_layout.addStretch()
        root.addWidget(nav_frame)

        self._cal_scroll = QScrollArea()
        self._cal_scroll.setWidgetResizable(True)
        self._cal_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._cal_scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: {BG_MAIN}; border: none; }}
            QScrollBar:vertical {{ background: transparent; width: 8px; }}
            QScrollBar::handle:vertical {{ background: #333; border-radius: 4px; min-height: 40px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

        self._cal_content = QWidget()
        self._cal_content.setStyleSheet(f"background-color: {BG_MAIN};")
        self._cal_main_layout = QVBoxLayout(self._cal_content)
        self._cal_main_layout.setContentsMargins(28, 16, 28, 16)
        self._cal_main_layout.setSpacing(12)
        self._cal_scroll.setWidget(self._cal_content)
        root.addWidget(self._cal_scroll, 1)

        self._build_calendar_grid()

    def _build_calendar_grid(self):
        import calendar as cal_mod
        from datetime import date, timedelta

        while self._cal_main_layout.count():
            item = self._cal_main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        days_header = QHBoxLayout()
        days_header.setSpacing(4)
        for d_name in ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]:
            lbl = QLabel(d_name)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 700; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
            days_header.addWidget(lbl)
        self._cal_main_layout.addLayout(days_header)

        try:
            events = self.repo.get_explore_events(
                limit=100, offset=0,
                date_filter=None,
            )
        except Exception:
            events = []

        events_by_date = {}
        for ev in events:
            ed = ev.get("event_date")
            if ed and hasattr(ed, "date"):
                ed = ed.date()
            if ed:
                events_by_date.setdefault(ed, []).append(ev)

        cal = cal_mod.Calendar(firstweekday=0)
        month_days = cal.monthdayscalendar(self._cal_year, self._cal_month)
        today = date.today()

        for week in month_days:
            row = QHBoxLayout()
            row.setSpacing(4)
            for day_num in week:
                cell = QFrame()
                cell.setFixedSize(100, 90)
                is_current_month = day_num != 0
                is_today = is_current_month and day_num == today.day and self._cal_month == today.month and self._cal_year == today.year

                if is_today:
                    border_style = f"border: 1px solid {RED};"
                    bg = "#1A0A0A"
                elif is_current_month:
                    border_style = f"border: 1px solid {BORDER};"
                    bg = BG_CARD
                else:
                    border_style = f"border: 1px solid transparent;"
                    bg = "#0A0A0A"

                cell.setStyleSheet(f"""
                    QFrame {{
                        background-color: {bg};
                        border-radius: 10px;
                        {border_style}
                    }}
                    QFrame QLabel {{
                        background: transparent;
                        border: none;
                    }}
                """)

                cell_layout = QVBoxLayout(cell)
                cell_layout.setContentsMargins(6, 6, 6, 6)
                cell_layout.setSpacing(2)

                if is_current_month:
                    day_lbl = QLabel(str(day_num))
                    day_color = RED if is_today else TEXT_PRI
                    day_weight = "900" if is_today else "700"
                    day_lbl.setStyleSheet(f"color: {day_color}; font-size: 11px; font-weight: {day_weight}; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
                    cell_layout.addWidget(day_lbl)

                    cell_date = date(self._cal_year, self._cal_month, day_num)
                    day_events = events_by_date.get(cell_date, [])
                    max_show = 2
                    for ev in day_events[:max_show]:
                        chip = QFrame()
                        chip.setFixedHeight(16)
                        ev_color = ev.get("color", RED)
                        chip.setStyleSheet(f"background-color: {ev_color}33; border-radius: 4px; border: none;")
                        chip_layout = QHBoxLayout(chip)
                        chip_layout.setContentsMargins(4, 1, 4, 1)
                        name = ev.get("name", "")[:12]
                        name_lbl = QLabel(name)
                        name_lbl.setStyleSheet(f"color: {TEXT_PRI}; font-size: 7px; font-weight: 600; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
                        chip_layout.addWidget(name_lbl)
                        cell_layout.addWidget(chip)

                    if len(day_events) > max_show:
                        more = QLabel(f"+{len(day_events) - max_show}")
                        more.setStyleSheet(f"color: {TEXT_MUT}; font-size: 8px; font-weight: 600; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
                        cell_layout.addWidget(more)

                    cell_layout.addStretch()

                    if day_events:
                        cell.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                        cell.mousePressEvent = lambda e, evs=day_events: self._on_day_click(evs)
                else:
                    cell_layout.addStretch()

                row.addWidget(cell)
            self._cal_main_layout.addLayout(row)

        self._cal_main_layout.addStretch()

    def _on_day_click(self, events):
        if len(events) == 1:
            self.parent_view.open_event_detail(events[0]["id"])
        elif events:
            from views.events.event_widgets import format_event_date
            names = "\n".join(f"• {e.get('name', 'Sin nombre')}" for e in events[:5])
            from PyQt6.QtWidgets import QMessageBox
            box = QMessageBox(self)
            box.setWindowTitle("Eventos del día")
            box.setText(f"{len(events)} eventos:\n\n{names}")
            box.setStyleSheet(f"""
                QMessageBox {{ background-color: {BG_MAIN}; }}
                QLabel {{ color: {TEXT_PRI}; font-size: 12px; font-family: 'Inter','Segoe UI',sans-serif; }}
                QPushButton {{
                    background-color: {RED}; color: white; border: 1px solid {RED_H};
                    border-radius: 6px; padding: 4px 16px; font-size: 11px; font-weight: 700;
                    font-family: 'Inter','Segoe UI',sans-serif;
                }}
            """)
            box.exec()

    def _cal_prev_month(self):
        if self._cal_month == 1:
            self._cal_month = 12
            self._cal_year -= 1
        else:
            self._cal_month -= 1
        months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                      "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self._cal_month_label.setText(f"{months_es[self._cal_month]} {self._cal_year}")
        self._build_calendar_grid()

    def _cal_next_month(self):
        if self._cal_month == 12:
            self._cal_month = 1
            self._cal_year += 1
        else:
            self._cal_month += 1
        months_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                      "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self._cal_month_label.setText(f"{months_es[self._cal_month]} {self._cal_year}")
        self._build_calendar_grid()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    # ── Filter handling ───────────────────────────────────────────

    def _on_filter_clicked(self, filter_key):
        self._current_filter = filter_key
        self._offset = 0
        self._has_more = True
        for chip in (self._filter_group or []):
            chip.set_active(chip._filter_key == filter_key)
        self.refresh()

    # ── Load data ─────────────────────────────────────────────────

    def refresh(self):
        if self._mode == "calendar":
            self._build_calendar_grid()
            return

        self._offset = 0
        self._has_more = True
        self._clear_events()
        self._show_skeletons(4)
        QTimer.singleShot(300, self._fetch_events)

    def _clear_events(self):
        self._events.clear()
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if self._featured_layout.count():
            item = self._featured_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if self._empty_state:
            self._empty_state.deleteLater()
            self._empty_state = None

    def _show_skeletons(self, count=4):
        for sk in self._skeletons:
            sk.deleteLater()
        self._skeletons.clear()
        for i in range(count):
            sk = SkeletonCard()
            self._grid_layout.addWidget(sk, i // 3, i % 3)
            self._skeletons.append(sk)

    def _hide_skeletons(self):
        for sk in self._skeletons:
            sk.deleteLater()
        self._skeletons.clear()

    def _fetch_events(self):
        if self._loading:
            return
        self._loading = True

        try:
            if self._mode == "explore":
                if self._offset == 0:
                    featured = self.repo.get_featured_event()
                    if featured:
                        self._featured = featured
                        card = FeaturedEventCard(featured)
                        card.clicked.connect(self.parent_view.open_event_detail)
                        self._featured_layout.addWidget(card)

                date_filter = None
                status_filter = None
                if self._current_filter == "upcoming":
                    date_filter = "upcoming"
                elif self._current_filter == "this_month":
                    date_filter = "this_month"
                elif self._current_filter == "registration_open":
                    date_filter = "registration_open"

                events = self.repo.get_explore_events(
                    search_text="",
                    event_type=None,
                    martial_art_id=None,
                    status=status_filter,
                    date_filter=date_filter,
                    featured_only=False,
                    limit=self._limit,
                    offset=self._offset,
                )
            elif self._mode == "user_events":
                events = self.repo.get_user_events(
                    self.current_user_id,
                    filter_type=self._current_filter,
                )
            else:
                events = []

            self._hide_skeletons()

            if not events:
                if self._offset == 0:
                    if self._mode == "explore":
                        self._empty_state = EmptyState(
                            icon_name="event",
                            title="No hay eventos disponibles",
                            subtitle="Próximamente se publicarán nuevos eventos",
                        )
                    else:
                        self._empty_state = EmptyState(
                            icon_name="event",
                            title="No tienes eventos",
                            subtitle="Explora eventos y síguelos para verlos aquí",
                        )
                    self._grid_layout.addWidget(self._empty_state, 0, 0, 1, 3)
                self._has_more = False
                self._load_more_btn.hide()
                return

            self._events.extend(events)
            start_idx = len(self._events) - len(events)

            for i, ev in enumerate(events):
                card = EventCard(ev)
                card.clicked.connect(self.parent_view.open_event_detail)
                row = (start_idx + i) // 3
                col = (start_idx + i) % 3
                self._grid_layout.addWidget(card, row, col)

            if self._empty_state:
                self._empty_state.deleteLater()
                self._empty_state = None

            if len(events) >= self._limit:
                self._has_more = True
                self._load_more_btn.show()
            else:
                self._has_more = False
                self._load_more_btn.hide()

        except Exception as e:
            debug_log(f"[EventExploreView] Error cargando eventos: {e}")
            self._hide_skeletons()
        finally:
            self._loading = False

    def _load_more(self):
        if self._loading or not self._has_more:
            return
        self._offset += self._limit
        self._loading = True
        self._load_more_btn.setText("Cargando...")
        QTimer.singleShot(200, self._fetch_events_done)

    def _fetch_events_done(self):
        self._fetch_events()
        self._load_more_btn.setText("Cargar más")
