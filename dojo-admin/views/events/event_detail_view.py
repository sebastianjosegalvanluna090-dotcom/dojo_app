# ─── EVENT_DETAIL_VIEW ──────────────────────────────────────────────

import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QStackedWidget,
    QButtonGroup, QSizePolicy, QGridLayout, QInputDialog,
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QCursor, QPixmap, QPainter, QPainterPath, QColor

from core.debug import debug_log
from views.events.event_widgets import (
    BG_MAIN, BG_CARD, BG_CARD2, BG_HOVER, BORDER, BORDER2,
    RED, RED_H, TEXT_PRI, TEXT_SEC, TEXT_MUT, TEXT_DIM,
    GREEN, YELLOW, PURPLE,
    EventStatusBadge, EventPostCard, ParticipantCard,
    ScheduleItemCard, EmptyState,
    format_event_date, format_event_time, format_currency,
)


# ─── Local visual constants ─────────────────────────────────────────

SURFACE = "#0B0B0B"
SURFACE_2 = "#101010"
SURFACE_3 = "#151515"
BORDER_SOFT = "#232323"
BORDER_HOVER = "#363636"
BLUE = "#3B82F6"
ORANGE = "#F97316"


class ClickableFrame(QFrame):
    """Small accessible frame used by premium information cards."""

    clicked = pyqtSignal()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class CoverLabel(QLabel):
    """Label that keeps a cover image cropped to fill the available area."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._source = QPixmap()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

    def set_source(self, path):
        self._source = QPixmap()
        if path and os.path.isfile(str(path)):
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                self._source = pixmap
        self._render()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._render()

    def _render(self):
        if self._source.isNull() or self.width() <= 0 or self.height() <= 0:
            self.setPixmap(QPixmap())
            return

        scaled = self._source.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )

        x = max(0, (scaled.width() - self.width()) // 2)
        y = max(0, (scaled.height() - self.height()) // 2)
        cropped = scaled.copy(x, y, self.width(), self.height())

        rounded = QPixmap(self.size())
        rounded.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(
            0,
            0,
            float(self.width()),
            float(self.height()),
            18,
            18,
        )
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, cropped)
        painter.end()
        self.setPixmap(rounded)


class EventDetailView(QWidget):
    """Premium full detail view for a single social event."""

    def __init__(self, event_id, current_user, repo, parent_view, parent=None):
        super().__init__(parent)
        self.event_id = int(event_id)
        self.current_user = current_user or {}
        self.current_user_id = self.current_user.get("id")
        self.repo = repo
        self.parent_view = parent_view
        self._event = None
        self._detail_tab = 0
        self._can_manage = False

        self.setObjectName("EventDetailView")
        self.setStyleSheet(f"QWidget#EventDetailView {{ background: {BG_MAIN}; }}")
        self._build_ui()
        QTimer.singleShot(80, self._load_event)

    # ── Root UI ───────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("EventDetailScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll.setStyleSheet(f"""
            QScrollArea#EventDetailScroll {{
                background-color: {BG_MAIN};
                border: none;
            }}
            QScrollArea#EventDetailScroll > QWidget > QWidget {{
                background-color: {BG_MAIN};
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 7px;
                margin: 4px 1px;
            }}
            QScrollBar::handle:vertical {{
                background: #303030;
                border-radius: 3px;
                min-height: 42px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #454545;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)

        self._content = QWidget()
        self._content.setObjectName("EventDetailContent")
        self._content.setStyleSheet(
            f"QWidget#EventDetailContent {{ background: {BG_MAIN}; }}"
        )
        self._layout = QVBoxLayout(self._content)
        self._layout.setContentsMargins(24, 18, 24, 36)
        self._layout.setSpacing(16)

        self._build_header()
        self._build_hero()
        self._build_social_bar()
        self._build_detail_tabs()
        self._build_detail_pages()

        self.scroll.setWidget(self._content)
        root.addWidget(self.scroll, 1)

    # ── Shared visual helpers ─────────────────────────────────────

    def _button_style(self, variant="secondary"):
        if variant == "primary":
            return f"""
                QPushButton {{
                    background-color: {RED};
                    color: white;
                    border: 1px solid {RED_H};
                    border-radius: 10px;
                    padding: 0 16px;
                    font-size: 11px;
                    font-weight: 800;
                    font-family: 'Inter','Segoe UI',sans-serif;
                }}
                QPushButton:hover {{ background-color: {RED_H}; }}
                QPushButton:pressed {{ background-color: #A70D26; }}
                QPushButton:disabled {{
                    background-color: #202020;
                    color: #555555;
                    border-color: #292929;
                }}
            """
        if variant == "ghost":
            return f"""
                QPushButton {{
                    background: transparent;
                    color: {TEXT_SEC};
                    border: 1px solid transparent;
                    border-radius: 9px;
                    padding: 0 12px;
                    font-size: 11px;
                    font-weight: 700;
                    font-family: 'Inter','Segoe UI',sans-serif;
                }}
                QPushButton:hover {{
                    background-color: #171717;
                    color: {TEXT_PRI};
                    border-color: #292929;
                }}
            """
        return f"""
            QPushButton {{
                background-color: #171717;
                color: {TEXT_SEC};
                border: 1px solid #2B2B2B;
                border-radius: 10px;
                padding: 0 14px;
                font-size: 11px;
                font-weight: 700;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QPushButton:hover {{
                background-color: #202020;
                color: {TEXT_PRI};
                border-color: #3A3A3A;
            }}
            QPushButton:pressed {{ background-color: #131313; }}
        """

    def _section_heading(self, eyebrow, title, subtitle=""):
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        eye = QLabel(eyebrow.upper())
        eye.setStyleSheet(f"""
            color: {RED_H};
            font-size: 8px;
            font-weight: 900;
            letter-spacing: 1.2px;
            background: transparent;
            border: none;
        """)
        layout.addWidget(eye)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 17px;
            font-weight: 900;
            background: transparent;
            border: none;
        """)
        layout.addWidget(title_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setWordWrap(True)
            subtitle_label.setStyleSheet(f"""
                color: {TEXT_MUT};
                font-size: 10px;
                font-weight: 500;
                background: transparent;
                border: none;
            """)
            layout.addWidget(subtitle_label)

        return wrapper

    def _make_action_button(self, text, variant="secondary", width=None):
        button = QPushButton(text)
        button.setFixedHeight(38)
        if width:
            button.setMinimumWidth(width)
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        button.setStyleSheet(self._button_style(variant))
        return button

    # ── Compact top bar ───────────────────────────────────────────

    def _build_header(self):
        header = QFrame()
        header.setObjectName("EventDetailHeader")
        header.setFixedHeight(52)
        header.setStyleSheet(f"""
            QFrame#EventDetailHeader {{
                background-color: transparent;
                border: none;
            }}
            QFrame#EventDetailHeader QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._btn_back = self._make_action_button(
            "‹  Volver a eventos",
            "ghost",
            132,
        )
        self._btn_back.clicked.connect(self.parent_view.back_to_list)
        layout.addWidget(self._btn_back)

        separator = QFrame()
        separator.setFixedSize(1, 22)
        separator.setStyleSheet("background: #292929; border: none;")
        layout.addWidget(separator)

        self._header_title = QLabel("Cargando evento...")
        self._header_title.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 11px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self._header_title)
        layout.addStretch()

        self._status_badge_host = QWidget()
        self._status_badge_host.setStyleSheet("background: transparent; border: none;")
        self._status_badge_container = QHBoxLayout(self._status_badge_host)
        self._status_badge_container.setContentsMargins(0, 0, 0, 0)
        self._status_badge_container.setSpacing(6)
        layout.addWidget(self._status_badge_host)

        self._layout.addWidget(header)

    # ── Hero section ──────────────────────────────────────────────

    def _build_hero(self):
        self._hero = QFrame()
        self._hero.setObjectName("EventDetailHero")
        self._hero.setMinimumHeight(330)
        self._hero.setStyleSheet(f"""
            QFrame#EventDetailHero {{
                background-color: {SURFACE};
                border: 1px solid #262626;
                border-radius: 20px;
            }}
            QFrame#EventDetailHero QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        layout = QHBoxLayout(self._hero)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._cover_panel = QFrame()
        self._cover_panel.setObjectName("EventHeroCoverPanel")
        self._cover_panel.setMinimumWidth(430)
        self._cover_panel.setStyleSheet(f"""
            QFrame#EventHeroCoverPanel {{
                background-color: #141414;
                border: none;
                border-top-left-radius: 19px;
                border-bottom-left-radius: 19px;
            }}
        """)
        cover_layout = QVBoxLayout(self._cover_panel)
        cover_layout.setContentsMargins(14, 14, 14, 14)
        cover_layout.setSpacing(0)

        self._cover_label = CoverLabel()
        self._cover_label.setMinimumHeight(300)
        self._cover_label.setStyleSheet("background: transparent; border: none;")
        cover_layout.addWidget(self._cover_label)

        self._cover_placeholder = QFrame(self._cover_label)
        self._cover_placeholder.setObjectName("EventCoverPlaceholder")
        self._cover_placeholder.setStyleSheet(f"""
            QFrame#EventCoverPlaceholder {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #161616,
                    stop:0.55 #1C1013,
                    stop:1 #2B0D14
                );
                border: 1px solid #2C2022;
                border-radius: 17px;
            }}
            QFrame#EventCoverPlaceholder QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        placeholder_layout = QVBoxLayout(self._cover_placeholder)
        placeholder_layout.setContentsMargins(30, 30, 30, 30)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.setSpacing(10)

        placeholder_mark = QLabel("EVENTO")
        placeholder_mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_mark.setStyleSheet(f"""
            color: {RED_H};
            font-size: 10px;
            font-weight: 900;
            letter-spacing: 2px;
        """)
        placeholder_layout.addWidget(placeholder_mark)

        placeholder_title = QLabel("Senshi Fight Academy")
        placeholder_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_title.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 20px;
            font-weight: 900;
        """)
        placeholder_layout.addWidget(placeholder_title)

        placeholder_text = QLabel("La portada del evento aparecerá aquí")
        placeholder_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_text.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 10px;
            font-weight: 500;
        """)
        placeholder_layout.addWidget(placeholder_text)

        self._hero_info = QFrame()
        self._hero_info.setObjectName("EventHeroInfo")
        self._hero_info.setMinimumWidth(400)
        self._hero_info.setStyleSheet(f"""
            QFrame#EventHeroInfo {{
                background-color: #101010;
                border: none;
                border-top-right-radius: 19px;
                border-bottom-right-radius: 19px;
            }}
        """)
        info_layout = QVBoxLayout(self._hero_info)
        info_layout.setContentsMargins(28, 28, 28, 26)
        info_layout.setSpacing(12)

        badge_row = QHBoxLayout()
        badge_row.setSpacing(8)

        self._type_label = QLabel("EVENTO")
        self._type_label.setObjectName("EventTypePill")
        self._type_label.setStyleSheet(f"""
            QLabel#EventTypePill {{
                color: {RED_H};
                background-color: rgba(200, 16, 46, 0.10);
                border: 1px solid rgba(200, 16, 46, 0.32);
                border-radius: 8px;
                padding: 5px 9px;
                font-size: 8px;
                font-weight: 900;
                letter-spacing: 1px;
            }}
        """)
        badge_row.addWidget(self._type_label)

        self._featured_badge = QLabel("DESTACADO")
        self._featured_badge.setObjectName("FeaturedPill")
        self._featured_badge.setStyleSheet(f"""
            QLabel#FeaturedPill {{
                color: #FBBF24;
                background-color: rgba(245, 158, 11, 0.10);
                border: 1px solid rgba(245, 158, 11, 0.30);
                border-radius: 8px;
                padding: 5px 9px;
                font-size: 8px;
                font-weight: 900;
                letter-spacing: 1px;
            }}
        """)
        self._featured_badge.hide()
        badge_row.addWidget(self._featured_badge)
        badge_row.addStretch()
        info_layout.addLayout(badge_row)

        self._event_name = QLabel("Cargando...")
        self._event_name.setWordWrap(True)
        self._event_name.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 28px;
            font-weight: 900;
            letter-spacing: -0.4px;
        """)
        info_layout.addWidget(self._event_name)

        self._short_description = QLabel("")
        self._short_description.setWordWrap(True)
        self._short_description.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 11px;
            font-weight: 500;
        """)
        info_layout.addWidget(self._short_description)

        info_layout.addSpacing(4)

        self._date_label = self._meta_row("FECHA", "—", RED_H)
        info_layout.addWidget(self._date_label)

        self._time_label = self._meta_row("HORARIO", "—", BLUE)
        info_layout.addWidget(self._time_label)

        self._location_label = self._meta_row("LUGAR", "—", PURPLE)
        info_layout.addWidget(self._location_label)

        info_layout.addStretch()

        hero_action_row = QHBoxLayout()
        hero_action_row.setSpacing(9)

        self._register_hero_btn = self._make_action_button(
            "Inscribirme",
            "primary",
            132,
        )
        self._register_hero_btn.clicked.connect(self._register_student)
        hero_action_row.addWidget(self._register_hero_btn)

        self._edit_hero_btn = self._make_action_button(
            "Editar evento",
            "secondary",
            126,
        )
        self._edit_hero_btn.clicked.connect(self._edit_event)
        self._edit_hero_btn.hide()
        hero_action_row.addWidget(self._edit_hero_btn)

        self._share_btn = self._make_action_button("Compartir", "ghost", 94)
        self._share_btn.clicked.connect(self._copy_share_summary)
        hero_action_row.addWidget(self._share_btn)
        hero_action_row.addStretch()
        info_layout.addLayout(hero_action_row)

        layout.addWidget(self._cover_panel, 5)
        layout.addWidget(self._hero_info, 4)
        self._layout.addWidget(self._hero)

    def _meta_row(self, title, value, accent):
        row = QFrame()
        row.setObjectName("HeroMetaRow")
        row.setStyleSheet(f"""
            QFrame#HeroMetaRow {{
                background-color: #151515;
                border: 1px solid #262626;
                border-radius: 10px;
            }}
            QFrame#HeroMetaRow QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(11, 8, 11, 8)
        layout.setSpacing(10)

        accent_dot = QFrame()
        accent_dot.setFixedSize(7, 7)
        accent_dot.setStyleSheet(
            f"background-color: {accent}; border-radius: 3px; border: none;"
        )
        layout.addWidget(accent_dot)

        title_label = QLabel(title)
        title_label.setFixedWidth(58)
        title_label.setStyleSheet(f"""
            color: {TEXT_DIM};
            font-size: 8px;
            font-weight: 900;
            letter-spacing: 0.8px;
        """)
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setWordWrap(True)
        value_label.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 10px;
            font-weight: 700;
        """)
        layout.addWidget(value_label, 1)
        row._value_label = value_label
        return row

    # ── Social action bar ─────────────────────────────────────────

    def _build_social_bar(self):
        self._social_bar = QFrame()
        self._social_bar.setObjectName("EventSocialBar")
        self._social_bar.setStyleSheet(f"""
            QFrame#EventSocialBar {{
                background-color: #101010;
                border: 1px solid #252525;
                border-radius: 14px;
            }}
            QFrame#EventSocialBar QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        layout = QHBoxLayout(self._social_bar)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(8)

        self._follower_btn = self._social_button("Seguir evento")
        self._follower_btn.clicked.connect(self._toggle_follow)
        layout.addWidget(self._follower_btn)

        self._interested_btn = self._social_button("Me interesa")
        self._interested_btn.clicked.connect(
            lambda: self._set_interest("interested")
        )
        layout.addWidget(self._interested_btn)

        self._attending_btn = self._social_button("Asistiré")
        self._attending_btn.clicked.connect(
            lambda: self._set_interest("attending")
        )
        layout.addWidget(self._attending_btn)

        layout.addStretch()

        self._followers_stat = self._stat_chip("0", "seguidores")
        layout.addWidget(self._followers_stat)

        self._registrations_stat = self._stat_chip("0", "inscritos")
        layout.addWidget(self._registrations_stat)

        self._layout.addWidget(self._social_bar)

    def _social_button(self, text):
        button = QPushButton(text)
        button.setCheckable(False)
        button.setFixedHeight(36)
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: #171717;
                color: {TEXT_SEC};
                border: 1px solid #2B2B2B;
                border-radius: 9px;
                padding: 0 13px;
                font-size: 10px;
                font-weight: 700;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QPushButton:hover {{
                background-color: #202020;
                color: {TEXT_PRI};
                border-color: #3B3B3B;
            }}
        """)
        return button

    def _stat_chip(self, value, label):
        chip = QFrame()
        chip.setObjectName("EventStatChip")
        chip.setStyleSheet(f"""
            QFrame#EventStatChip {{
                background-color: #151515;
                border: 1px solid #282828;
                border-radius: 9px;
            }}
            QFrame#EventStatChip QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        layout = QHBoxLayout(chip)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(5)

        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 11px;
            font-weight: 900;
        """)
        layout.addWidget(value_label)

        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 9px;
            font-weight: 600;
        """)
        layout.addWidget(label_widget)
        chip._value_label = value_label
        return chip

    # ── Tabs ──────────────────────────────────────────────────────

    def _build_detail_tabs(self):
        tab_frame = QFrame()
        tab_frame.setObjectName("EventDetailTabs")
        tab_frame.setFixedHeight(54)
        tab_frame.setStyleSheet(f"""
            QFrame#EventDetailTabs {{
                background-color: #0D0D0D;
                border: 1px solid #242424;
                border-radius: 13px;
            }}
        """)
        layout = QHBoxLayout(tab_frame)
        layout.setContentsMargins(7, 7, 7, 7)
        layout.setSpacing(4)

        self._detail_tab_group = QButtonGroup(self)
        self._detail_tab_group.setExclusive(True)

        tabs = [
            ("Información", "Resumen y datos clave"),
            ("Agenda", "Programa del evento"),
            ("Actualizaciones", "Noticias del organizador"),
            ("Participantes", "Personas inscritas"),
        ]
        self._detail_tab_buttons = []

        for index, (label, tooltip) in enumerate(tabs):
            button = QPushButton(label)
            button.setToolTip(tooltip)
            button.setCheckable(True)
            button.setFixedHeight(38)
            button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            button.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {TEXT_MUT};
                    border: 1px solid transparent;
                    border-radius: 9px;
                    padding: 0 16px;
                    font-size: 11px;
                    font-weight: 700;
                    font-family: 'Inter','Segoe UI',sans-serif;
                }}
                QPushButton:hover {{
                    background-color: #161616;
                    color: {TEXT_SEC};
                }}
                QPushButton:checked {{
                    background-color: rgba(200, 16, 46, 0.11);
                    color: {TEXT_PRI};
                    border-color: rgba(200, 16, 46, 0.32);
                }}
            """)
            button.clicked.connect(
                lambda checked, idx=index: self._switch_detail_tab(idx)
            )
            self._detail_tab_group.addButton(button, index)
            self._detail_tab_buttons.append(button)
            layout.addWidget(button)

        layout.addStretch()
        self._layout.addWidget(tab_frame)

    def _switch_detail_tab(self, index):
        if index < 0 or index >= len(self._detail_tab_buttons):
            return
        self._detail_tab = index
        for button_index, button in enumerate(self._detail_tab_buttons):
            button.setChecked(button_index == index)
        self._detail_stack.setCurrentIndex(index)
        self._refresh_tab(index)

    # ── Detail pages ──────────────────────────────────────────────

    def _build_detail_pages(self):
        self._detail_stack = QStackedWidget()
        self._detail_stack.setObjectName("EventDetailStack")
        self._detail_stack.setStyleSheet(
            f"QStackedWidget#EventDetailStack {{ background: transparent; border: none; }}"
        )

        self._info_page = self._build_info_page()
        self._schedule_page = self._build_schedule_page()
        self._posts_page = self._build_posts_page()
        self._participants_page = self._build_participants_page()

        for page in (
            self._info_page,
            self._schedule_page,
            self._posts_page,
            self._participants_page,
        ):
            self._detail_stack.addWidget(page)

        self._layout.addWidget(self._detail_stack)

    # ── Information page ──────────────────────────────────────────

    def _build_info_page(self):
        page = QWidget()
        page.setObjectName("EventInfoPage")
        page.setStyleSheet("QWidget#EventInfoPage { background: transparent; }")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(16)

        main_row = QHBoxLayout()
        main_row.setSpacing(16)

        description_card = QFrame()
        description_card.setObjectName("EventDescriptionCard")
        description_card.setStyleSheet(f"""
            QFrame#EventDescriptionCard {{
                background-color: {SURFACE_2};
                border: 1px solid #252525;
                border-radius: 16px;
            }}
            QFrame#EventDescriptionCard QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        desc_layout = QVBoxLayout(description_card)
        desc_layout.setContentsMargins(22, 20, 22, 20)
        desc_layout.setSpacing(13)
        desc_layout.addWidget(
            self._section_heading(
                "Acerca del evento",
                "Descripción",
                "Información compartida por la organización.",
            )
        )

        self._desc_text = QLabel("Cargando información...")
        self._desc_text.setWordWrap(True)
        self._desc_text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._desc_text.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 12px;
            font-weight: 500;
            line-height: 1.5;
            background: transparent;
            border: none;
        """)
        desc_layout.addWidget(self._desc_text)
        desc_layout.addStretch()
        main_row.addWidget(description_card, 3)

        organizer_card = QFrame()
        organizer_card.setObjectName("EventOrganizerCard")
        organizer_card.setMinimumWidth(280)
        organizer_card.setStyleSheet(f"""
            QFrame#EventOrganizerCard {{
                background-color: {SURFACE_2};
                border: 1px solid #252525;
                border-radius: 16px;
            }}
            QFrame#EventOrganizerCard QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        org_layout = QVBoxLayout(organizer_card)
        org_layout.setContentsMargins(22, 20, 22, 20)
        org_layout.setSpacing(11)
        org_layout.addWidget(
            self._section_heading(
                "Organización",
                "Responsable",
                "Cuenta que administra esta publicación.",
            )
        )

        avatar = QLabel("SF")
        avatar.setFixedSize(48, 48)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                color: white;
                background-color: {RED};
                border: 1px solid {RED_H};
                border-radius: 14px;
                font-size: 12px;
                font-weight: 900;
            }}
        """)
        org_layout.addWidget(avatar)

        self._organizer_name = QLabel("—")
        self._organizer_name.setWordWrap(True)
        self._organizer_name.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 13px;
            font-weight: 800;
        """)
        org_layout.addWidget(self._organizer_name)

        org_caption = QLabel("Organizador del evento")
        org_caption.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 9px;
            font-weight: 600;
        """)
        org_layout.addWidget(org_caption)
        org_layout.addStretch()
        main_row.addWidget(organizer_card, 1)

        layout.addLayout(main_row)

        metrics_grid = QGridLayout()
        metrics_grid.setHorizontalSpacing(12)
        metrics_grid.setVerticalSpacing(12)

        self._detail_location_card = self._info_card(
            "LUGAR",
            "Ubicación",
            "—",
            PURPLE,
        )
        self._detail_capacity_card = self._info_card(
            "CUPOS",
            "Capacidad",
            "—",
            BLUE,
        )
        self._detail_price_card = self._info_card(
            "INSCRIPCIÓN",
            "Precio",
            "—",
            GREEN,
        )
        self._detail_deadline_card = self._info_card(
            "CIERRE",
            "Fecha límite",
            "—",
            ORANGE,
        )

        metrics_grid.addWidget(self._detail_location_card, 0, 0)
        metrics_grid.addWidget(self._detail_capacity_card, 0, 1)
        metrics_grid.addWidget(self._detail_price_card, 0, 2)
        metrics_grid.addWidget(self._detail_deadline_card, 0, 3)
        for column in range(4):
            metrics_grid.setColumnStretch(column, 1)

        layout.addLayout(metrics_grid)

        self._edit_event_btn = self._make_action_button(
            "Editar publicación",
            "secondary",
            150,
        )
        self._edit_event_btn.clicked.connect(self._edit_event)
        self._edit_event_btn.hide()

        info_actions = QHBoxLayout()
        info_actions.addWidget(self._edit_event_btn)
        info_actions.addStretch()
        layout.addLayout(info_actions)
        return page

    def _info_card(self, eyebrow, title, value, accent):
        card = QFrame()
        card.setObjectName("EventInfoMetricCard")
        card.setMinimumHeight(112)
        card.setStyleSheet(f"""
            QFrame#EventInfoMetricCard {{
                background-color: {SURFACE_2};
                border: 1px solid #252525;
                border-radius: 14px;
            }}
            QFrame#EventInfoMetricCard:hover {{
                background-color: #141414;
                border-color: #343434;
            }}
            QFrame#EventInfoMetricCard QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(4)

        accent_bar = QFrame()
        accent_bar.setFixedSize(26, 3)
        accent_bar.setStyleSheet(
            f"background-color: {accent}; border-radius: 1px; border: none;"
        )
        card_layout.addWidget(accent_bar)

        eye = QLabel(eyebrow)
        eye.setStyleSheet(f"""
            color: {TEXT_DIM};
            font-size: 8px;
            font-weight: 900;
            letter-spacing: 0.8px;
        """)
        card_layout.addWidget(eye)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {TEXT_MUT};
            font-size: 9px;
            font-weight: 600;
        """)
        card_layout.addWidget(title_label)

        value_label = QLabel(value or "—")
        value_label.setWordWrap(True)
        value_label.setStyleSheet(f"""
            color: {TEXT_PRI};
            font-size: 12px;
            font-weight: 800;
        """)
        card_layout.addWidget(value_label)
        card_layout.addStretch()
        card._value_label = value_label
        return card

    # ── Reusable content page shell ───────────────────────────────

    def _build_collection_page(self, eyebrow, title, subtitle, button_text):
        page = QWidget()
        page.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(14)

        header_card = QFrame()
        header_card.setObjectName("CollectionHeaderCard")
        header_card.setStyleSheet(f"""
            QFrame#CollectionHeaderCard {{
                background-color: {SURFACE_2};
                border: 1px solid #252525;
                border-radius: 15px;
            }}
            QFrame#CollectionHeaderCard QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(20, 16, 16, 16)
        header_layout.setSpacing(12)
        header_layout.addWidget(self._section_heading(eyebrow, title, subtitle), 1)

        action = self._make_action_button(button_text, "primary", 126)
        header_layout.addWidget(action)
        layout.addWidget(header_card)

        content_card = QFrame()
        content_card.setObjectName("CollectionContentCard")
        content_card.setStyleSheet(f"""
            QFrame#CollectionContentCard {{
                background-color: #0E0E0E;
                border: 1px solid #222222;
                border-radius: 15px;
            }}
        """)
        content_layout = QVBoxLayout(content_card)
        content_layout.setContentsMargins(14, 14, 14, 14)
        content_layout.setSpacing(10)
        layout.addWidget(content_card)
        layout.addStretch()
        return page, action, content_layout

    # ── Schedule page ─────────────────────────────────────────────

    def _build_schedule_page(self):
        page, self._add_schedule_btn, self._schedule_layout = (
            self._build_collection_page(
                "Programa",
                "Agenda del evento",
                "Horarios y actividades organizados cronológicamente.",
                "Agregar actividad",
            )
        )
        self._add_schedule_btn.clicked.connect(self._add_schedule_item)
        return page

    # ── Posts page ────────────────────────────────────────────────

    def _build_posts_page(self):
        page, self._add_post_btn, self._posts_layout = (
            self._build_collection_page(
                "Comunidad",
                "Actualizaciones",
                "Novedades publicadas por la organización del evento.",
                "Nueva publicación",
            )
        )
        self._add_post_btn.clicked.connect(self._add_post)
        return page

    # ── Participants page ─────────────────────────────────────────

    def _build_participants_page(self):
        page, self._register_btn, self._participants_layout = (
            self._build_collection_page(
                "Inscripciones",
                "Participantes",
                "Estudiantes y miembros registrados en este evento.",
                "Inscribir estudiante",
            )
        )
        self._register_btn.clicked.connect(self._register_student)
        return page

    # ── Loading and population ────────────────────────────────────

    def _load_event(self):
        try:
            self._event = self.repo.get_event_detail(
                self.event_id,
                self.current_user_id,
            )
            if not self._event:
                self._show_not_found()
                return

            self._populate_event()
            self._switch_detail_tab(self._detail_tab)
        except Exception as error:
            debug_log(f"[EventDetailView] Error cargando evento: {error}")
            self._header_title.setText("No se pudo cargar el evento")

    def refresh(self):
        self._load_event()

    def _show_not_found(self):
        self._header_title.setText("Evento no encontrado")
        self._event_name.setText("Evento no disponible")
        self._short_description.setText(
            "La publicación fue eliminada, archivada o ya no está disponible."
        )
        self._social_bar.setEnabled(False)

    def _populate_event(self):
        event = self._event
        name = event.get("name") or "Sin nombre"
        self._header_title.setText(name)
        self._event_name.setText(name)

        self._clear_layout(self._status_badge_container)
        self._status_badge_container.addWidget(
            EventStatusBadge(event.get("status") or "draft")
        )

        event_type = event.get("event_type") or "Evento"
        self._type_label.setText(event_type.upper())
        self._featured_badge.setVisible(bool(event.get("is_featured")))

        short_description = (
            event.get("short_description")
            or event.get("description")
            or "Información del evento disponible próximamente."
        )
        self._short_description.setText(short_description)

        date_text = format_event_date(event.get("event_date")) or "Fecha por definir"
        end_date = event.get("end_date")
        if end_date and end_date != event.get("event_date"):
            date_text = f"{date_text} — {format_event_date(end_date)}"
        self._date_label._value_label.setText(date_text)

        start_time = format_event_time(event.get("start_time"))
        end_time = format_event_time(event.get("end_time"))
        if start_time and end_time:
            time_text = f"{start_time} — {end_time}"
        else:
            time_text = start_time or end_time or "Horario por definir"
        self._time_label._value_label.setText(time_text)

        location_parts = [
            event.get("venue_name"),
            event.get("location"),
            event.get("city"),
        ]
        location_text = " · ".join(
            str(part).strip() for part in location_parts if part
        ) or "Ubicación por definir"
        self._location_label._value_label.setText(location_text)

        cover_path = event.get("cover_image_path")
        self._cover_label.set_source(cover_path)
        self._cover_placeholder.setVisible(
            not bool(cover_path and os.path.isfile(str(cover_path)))
        )
        self._sync_cover_placeholder_geometry()

        description = (
            event.get("description")
            or event.get("short_description")
            or "La organización todavía no ha publicado una descripción completa."
        )
        self._desc_text.setText(description)

        full_location = ", ".join(
            str(part).strip()
            for part in (
                event.get("venue_name") or event.get("location"),
                event.get("address"),
                event.get("city"),
                event.get("country"),
            )
            if part
        ) or "—"
        self._detail_location_card._value_label.setText(full_location)

        capacity = event.get("capacity")
        registration_count = int(event.get("registration_count") or 0)
        if capacity:
            capacity_text = f"{registration_count} de {capacity} inscritos"
        else:
            capacity_text = (
                f"{registration_count} inscritos · Sin límite"
                if registration_count
                else "Sin límite"
            )
        self._detail_capacity_card._value_label.setText(capacity_text)

        price = event.get("price") or 0
        self._detail_price_card._value_label.setText(
            "Gratis" if float(price) <= 0 else format_currency(price)
        )

        deadline = event.get("registration_deadline")
        deadline_text = format_event_date(deadline) if deadline else "Sin fecha límite"
        self._detail_deadline_card._value_label.setText(deadline_text)

        organizer = event.get("organizer_name") or "Senshi Fight Academy"
        self._organizer_name.setText(organizer)

        follower_count = int(event.get("follower_count") or 0)
        self._followers_stat._value_label.setText(str(follower_count))
        self._registrations_stat._value_label.setText(str(registration_count))

        is_following = bool(event.get("is_following"))
        self._follower_btn.setText(
            "Siguiendo" if is_following else "Seguir evento"
        )
        self._apply_social_state(
            self._follower_btn,
            is_following,
            RED_H,
        )

        interest = event.get("user_interest")
        self._apply_social_state(
            self._interested_btn,
            interest == "interested",
            YELLOW,
        )
        self._apply_social_state(
            self._attending_btn,
            interest == "attending",
            GREEN,
        )

        self._can_manage = bool(
            self.repo.can_manage_event(self.current_user_id, self.event_id)
        )
        self._edit_event_btn.setVisible(self._can_manage)
        self._edit_hero_btn.setVisible(self._can_manage)
        self._add_schedule_btn.setVisible(self._can_manage)
        self._add_post_btn.setVisible(self._can_manage)

        registration_enabled = bool(event.get("registration_enabled"))
        status = event.get("status") or "draft"
        can_register_status = status in ("published", "registration_open")
        capacity_available = not capacity or registration_count < int(capacity)
        can_register = (
            registration_enabled
            and can_register_status
            and capacity_available
            and self.current_user_id is not None
        )
        self._register_hero_btn.setVisible(registration_enabled)
        self._register_hero_btn.setEnabled(can_register)
        self._register_btn.setVisible(registration_enabled)
        self._register_btn.setEnabled(can_register)

        if registration_enabled and not capacity_available:
            self._register_hero_btn.setText("Cupos agotados")
        elif registration_enabled and status == "registration_closed":
            self._register_hero_btn.setText("Inscripción cerrada")
        else:
            self._register_hero_btn.setText("Inscribirme")

    def _sync_cover_placeholder_geometry(self):
        if hasattr(self, "_cover_placeholder"):
            self._cover_placeholder.setGeometry(self._cover_label.rect())
            self._cover_placeholder.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._sync_cover_placeholder_geometry()

    def _apply_social_state(self, button, active, accent):
        if active:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(200, 16, 46, 0.10);
                    color: {accent};
                    border: 1px solid {accent};
                    border-radius: 9px;
                    padding: 0 13px;
                    font-size: 10px;
                    font-weight: 800;
                    font-family: 'Inter','Segoe UI',sans-serif;
                }}
                QPushButton:hover {{ background-color: rgba(200, 16, 46, 0.16); }}
            """)
        else:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #171717;
                    color: {TEXT_SEC};
                    border: 1px solid #2B2B2B;
                    border-radius: 9px;
                    padding: 0 13px;
                    font-size: 10px;
                    font-weight: 700;
                    font-family: 'Inter','Segoe UI',sans-serif;
                }}
                QPushButton:hover {{
                    background-color: #202020;
                    color: {TEXT_PRI};
                    border-color: #3B3B3B;
                }}
            """)

    # ── Tab loading ───────────────────────────────────────────────

    def _refresh_tab(self, index):
        if index == 1:
            self._load_schedule()
        elif index == 2:
            self._load_posts()
        elif index == 3:
            self._load_participants()

    def _load_schedule(self):
        self._clear_layout(self._schedule_layout)
        try:
            items = self.repo.get_event_schedule(self.event_id)
            if not items:
                self._schedule_layout.addWidget(
                    EmptyState(
                        "calendar",
                        "Sin agenda publicada",
                        "La programación aparecerá aquí cuando sea agregada.",
                    )
                )
                return

            for item in items:
                card = ScheduleItemCard(item, can_edit=self._can_manage)
                self._schedule_layout.addWidget(card)
        except Exception as error:
            debug_log(f"[EventDetailView] Error cargando agenda: {error}")
            self._schedule_layout.addWidget(
                EmptyState(
                    "calendar",
                    "No se pudo cargar la agenda",
                    "Intenta nuevamente en unos momentos.",
                )
            )

    def _load_posts(self):
        self._clear_layout(self._posts_layout)
        try:
            posts = self.repo.get_event_posts(self.event_id)
            if not posts:
                self._posts_layout.addWidget(
                    EmptyState(
                        "event",
                        "Sin actualizaciones",
                        "La organización aún no ha publicado novedades.",
                    )
                )
                return

            for post in posts:
                card = EventPostCard(post, can_edit=self._can_manage)
                self._posts_layout.addWidget(card)
        except Exception as error:
            debug_log(f"[EventDetailView] Error cargando publicaciones: {error}")
            self._posts_layout.addWidget(
                EmptyState(
                    "event",
                    "No se pudieron cargar las actualizaciones",
                    "Intenta nuevamente en unos momentos.",
                )
            )

    def _load_participants(self):
        self._clear_layout(self._participants_layout)
        try:
            participants = self.repo.get_event_participants(self.event_id)
            if not participants:
                self._participants_layout.addWidget(
                    EmptyState(
                        "user",
                        "Sin participantes",
                        "Todavía no se han registrado estudiantes.",
                    )
                )
                return

            for participant in participants:
                self._participants_layout.addWidget(
                    ParticipantCard(participant)
                )
        except Exception as error:
            debug_log(f"[EventDetailView] Error cargando participantes: {error}")
            self._participants_layout.addWidget(
                EmptyState(
                    "user",
                    "No se pudieron cargar los participantes",
                    "Intenta nuevamente en unos momentos.",
                )
            )

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                EventDetailView._clear_layout(child_layout)

    # ── Social actions ────────────────────────────────────────────

    def _toggle_follow(self):
        if not self._event or not self.current_user_id:
            return
        try:
            if self._event.get("is_following", False):
                self.repo.unfollow_event(self.event_id, self.current_user_id)
            else:
                self.repo.follow_event(self.event_id, self.current_user_id)
            self._load_event()
        except Exception as error:
            debug_log(f"[EventDetailView] Error al seguir evento: {error}")

    def _set_interest(self, response):
        if not self._event or not self.current_user_id:
            return
        try:
            current = self._event.get("user_interest")
            if current == response:
                self.repo.clear_interest(self.event_id, self.current_user_id)
            else:
                self.repo.set_interest(
                    self.event_id,
                    self.current_user_id,
                    response,
                )
            self._load_event()
        except Exception as error:
            debug_log(f"[EventDetailView] Error actualizando interés: {error}")

    def _copy_share_summary(self):
        if not self._event:
            return
        name = self._event.get("name") or "Evento"
        date_text = format_event_date(self._event.get("event_date")) or ""
        location = (
            self._event.get("venue_name")
            or self._event.get("location")
            or self._event.get("city")
            or ""
        )
        parts = [name, date_text, location]
        summary = "\n".join(str(part) for part in parts if part)

        try:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(summary)
            self._share_btn.setText("Copiado")
            QTimer.singleShot(2200, lambda: self._share_btn.setText("Compartir"))
        except Exception as error:
            debug_log(f"[EventDetailView] Error copiando evento: {error}")

    # ── Management actions ────────────────────────────────────────

    def _edit_event(self):
        if not self._event:
            return
        self.parent_view.open_event_editor(self.event_id)

    def _add_schedule_item(self):
        if not self._can_manage:
            return

        title, accepted = QInputDialog.getText(
            self,
            "Agregar actividad",
            "Título de la actividad:",
        )
        title = title.strip()
        if not accepted or not title:
            return

        event_date = self._event.get("event_date") if self._event else None
        start_time = self._event.get("start_time") if self._event else None
        starts_at = None
        if event_date:
            if start_time:
                starts_at = datetime.combine(event_date, start_time)
            else:
                starts_at = datetime.combine(event_date, datetime.min.time())

        try:
            self.repo.create_schedule_item(
                self.event_id,
                {
                    "title": title,
                    "description": "",
                    "starts_at": starts_at,
                    "ends_at": None,
                    "location": "",
                    "sort_order": 0,
                },
            )
            self._load_schedule()
        except Exception as error:
            debug_log(f"[EventDetailView] Error creando actividad: {error}")

    def _add_post(self):
        if not self._can_manage:
            return
        try:
            from views.events.event_post_dialog import EventPostDialog
            dialog = EventPostDialog(
                repo=self.repo,
                event_id=self.event_id,
                current_user=self.current_user,
                parent=self.window(),
            )
            if dialog.exec():
                self._load_posts()
        except Exception as error:
            debug_log(f"[EventDetailView] Error abriendo publicación: {error}")

    def _register_student(self):
        if not self._event or not self._event.get("registration_enabled"):
            return
        try:
            from views.events.event_registration_dialog import (
                EventRegistrationDialog,
            )
            dialog = EventRegistrationDialog(
                repo=self.repo,
                event_id=self.event_id,
                current_user=self.current_user,
                parent=self.window(),
            )
            if dialog.exec():
                self._load_participants()
                self._load_event()
        except Exception as error:
            debug_log(f"[EventDetailView] Error abriendo inscripción: {error}")
