# ─── EVENTS_VIEW ────────────────────────────────────────────────────

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QStackedWidget, QButtonGroup,
)
from PyQt6.QtCore import Qt
from core.debug import debug_log


BG_MAIN  = "#050505"
BG_CARD  = "#111111"
BORDER   = "#252525"
RED      = "#C8102E"
RED_H    = "#E8152F"
TEXT_PRI = "#F0F0F0"
TEXT_SEC = "#9CA3AF"
TEXT_MUT = "#6B7280"


class EventsView(QWidget):
    """Main container for the social events module."""

    def __init__(self, current_user, parent_window=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.current_user_id = current_user.get("id") if current_user else None
        self.parent_window = parent_window
        self.setObjectName("EventsPage")

        from repositories.social_events_repository import SocialEventsRepository
        self.repo = SocialEventsRepository()

        self._tabs = []
        self._current_tab = 0

        self._build_ui()
        self._build_overlay()
        self._switch_tab(0)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame()
        header.setObjectName("EventsHeader")
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QFrame#EventsHeader {{
                background-color: {BG_MAIN};
                border-bottom: 1px solid {BORDER};
            }}
            QFrame#EventsHeader QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(28, 18, 28, 18)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        lbl_title = QLabel("Eventos")
        lbl_title.setStyleSheet(f"color: {TEXT_PRI}; font-size: 18px; font-weight: 900; font-family: 'Inter','Segoe UI',sans-serif;")
        title_col.addWidget(lbl_title)
        lbl_sub = QLabel("Descubre torneos, seminarios, exámenes y actividades")
        lbl_sub.setStyleSheet(f"color: {TEXT_MUT}; font-size: 11px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif;")
        title_col.addWidget(lbl_sub)
        h_layout.addLayout(title_col)
        h_layout.addStretch()

        if self.repo.is_admin_or_instructor(self.current_user_id):
            self.btn_create_event = QPushButton("Crear evento")
            self.btn_create_event.setFixedHeight(38)
            self.btn_create_event.setMinimumWidth(140)
            self.btn_create_event.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_create_event.setStyleSheet(f"""
                QPushButton {{
                    background-color: {RED};
                    color: white;
                    border: 1px solid {RED_H};
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: 800;
                    font-family: 'Inter','Segoe UI',sans-serif;
                }}
                QPushButton:hover {{ background-color: {RED_H}; }}
            """)
            self.btn_create_event.clicked.connect(lambda: self.open_event_editor())
            h_layout.addWidget(self.btn_create_event)

        root.addWidget(header)

        tabs_frame = QFrame()
        tabs_frame.setFixedHeight(48)
        tabs_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_MAIN};
                border-bottom: 1px solid {BORDER};
            }}
        """)
        tabs_layout = QHBoxLayout(tabs_frame)
        tabs_layout.setContentsMargins(28, 0, 28, 0)
        tabs_layout.setSpacing(4)

        self._tab_group = QButtonGroup(self)
        self._tab_group.setExclusive(True)

        tab_labels = ["Explorar", "Mis eventos", "Calendario"]
        if self.repo.is_admin_or_instructor(self.current_user_id):
            tab_labels.append("Gestión")

        for i, label in enumerate(tab_labels):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFixedHeight(36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {TEXT_MUT};
                    border: none;
                    border-bottom: 2px solid transparent;
                    padding: 0 14px;
                    font-size: 12px;
                    font-weight: 600;
                    font-family: 'Inter','Segoe UI',sans-serif;
                }}
                QPushButton:checked {{
                    color: {TEXT_PRI};
                    border-bottom: 2px solid {RED_H};
                }}
                QPushButton:hover {{
                    color: {TEXT_SEC};
                }}
            """)
            btn.clicked.connect(lambda checked, idx=i: self._switch_tab(idx))
            self._tab_group.addButton(btn, i)
            tabs_layout.addWidget(btn)
            self._tabs.append(btn)

        tabs_layout.addStretch()
        root.addWidget(tabs_frame)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        self._build_pages()

    def _build_overlay(self):
        from views.events.event_widgets import EventsGlassOverlay
        self.glass = EventsGlassOverlay(self)
        self.glass.setGeometry(self.rect())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "glass"):
            self.glass.setGeometry(self.rect())

    def _build_pages(self):
        from views.events.event_explore_view import EventExploreView
        self.explore_view = EventExploreView(
            current_user=self.current_user,
            repo=self.repo,
            parent_view=self,
        )
        self.stack.addWidget(self.explore_view)

        self.my_events_view = EventExploreView(
            current_user=self.current_user,
            repo=self.repo,
            parent_view=self,
            mode="user_events",
        )
        self.stack.addWidget(self.my_events_view)

        from views.events.event_explore_view import EventExploreView
        self.calendar_view = EventExploreView(
            current_user=self.current_user,
            repo=self.repo,
            parent_view=self,
            mode="calendar",
        )
        self.stack.addWidget(self.calendar_view)

        if self.repo.is_admin_or_instructor(self.current_user_id):
            from views.events.event_management_view import EventManagementView
            self.management_view = EventManagementView(
                current_user=self.current_user,
                repo=self.repo,
                parent_view=self,
            )
            self.stack.addWidget(self.management_view)
        else:
            placeholder = QWidget()
            self.stack.addWidget(placeholder)

    def _switch_tab(self, index):
        if index < 0 or index >= len(self._tabs):
            return
        self._current_tab = index
        for i, btn in enumerate(self._tabs):
            btn.setChecked(i == index)
        self.stack.setCurrentIndex(index)

        try:
            page = self.stack.currentWidget()
            if hasattr(page, "refresh"):
                page.refresh()
        except Exception as e:
            debug_log(f"[EventsView] Error cambiando pestaña: {e}")

    def open_event_detail(self, event_id):
        try:
            from views.events.event_detail_view import EventDetailView
            self.detail_view = EventDetailView(
                event_id=event_id,
                current_user=self.current_user,
                repo=self.repo,
                parent_view=self,
            )
            self.stack.addWidget(self.detail_view)
            self.stack.setCurrentWidget(self.detail_view)
            for btn in self._tabs:
                btn.setChecked(False)
        except Exception as e:
            debug_log(f"[EventsView] Error abriendo detalle: {e}")

    def back_to_list(self):
        if hasattr(self, "detail_view"):
            self.stack.removeWidget(self.detail_view)
            self.detail_view.deleteLater()
            del self.detail_view
        self.stack.setCurrentIndex(self._current_tab)
        self._tabs[self._current_tab].setChecked(True)
        page = self.stack.currentWidget()
        if hasattr(page, "refresh"):
            page.refresh()

    def open_event_editor(self, event_id=None):
        from PyQt6.QtWidgets import QDialog
        from views.events.event_editor_dialog import EventEditorDialog

        self.glass.setGeometry(self.rect())
        self.glass.fade_in()
        self.glass.raise_()

        dialog = EventEditorDialog(
            repo=self.repo,
            current_user=self.current_user,
            event_id=event_id,
            parent=self.window(),
        )

        result = QDialog.DialogCode.Rejected

        try:
            result = dialog.exec()
        except Exception as e:
            debug_log(f"[EventsView] Error abriendo editor: {e}")
        finally:
            self.glass.fade_out()

        if result == QDialog.DialogCode.Accepted:
            self.refresh_all_event_views()

    def refresh_all_event_views(self):
        for view_name in (
            "explore_view",
            "my_events_view",
            "calendar_view",
            "management_view",
        ):
            view = getattr(self, view_name, None)
            if view is not None and hasattr(view, "refresh"):
                try:
                    view.refresh()
                except Exception as e:
                    debug_log(f"[EventsView] Error actualizando {view_name}: {e}")

        if hasattr(self, "detail_view") and hasattr(self.detail_view, "_load_event"):
            try:
                self.detail_view._load_event()
            except Exception as e:
                debug_log(f"[EventsView] Error actualizando detalle: {e}")

    def _create_event(self):
        self.open_event_editor()
