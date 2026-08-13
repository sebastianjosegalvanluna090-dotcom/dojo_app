# ─── EVENT_EDITOR_DIALOG ────────────────────────────────────────────
import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QComboBox,
    QDateEdit, QTimeEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QFrame, QScrollArea, QFileDialog,
    QWidget, QSplitter, QSizePolicy, QApplication,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QDate, QTime, QTimer, QSize, QRect, QPoint
from PyQt6.QtGui import QColor, QPixmap, QCursor

from core.debug import debug_log
from views.events.event_widgets import (
    BG_MAIN, BG_CARD, BG_CARD2, BG_HOVER, BORDER, BORDER2,
    RED, RED_H, TEXT_PRI, TEXT_SEC, TEXT_MUT, TEXT_DIM,
    GREEN, YELLOW, PURPLE,
    EventStatusBadge, EventLivePreview, format_event_date,
    format_event_time, format_currency,
)

INPUT_STYLE = f"""
    QComboBox, QLineEdit, QDateEdit, QTimeEdit, QSpinBox, QDoubleSpinBox {{
        background-color: #181818; color: {TEXT_PRI};
        border: 1px solid #303030; border-radius: 9px;
        padding: 0 13px; font-size: 11px; font-weight: 600;
        font-family: 'Inter','Segoe UI',sans-serif;
    }}
    QComboBox:hover, QLineEdit:hover, QDateEdit:hover, QTimeEdit:hover,
    QSpinBox:hover, QDoubleSpinBox:hover {{ border-color: #414141; }}
    QComboBox:focus, QLineEdit:focus, QDateEdit:focus, QTimeEdit:focus,
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {RED}; background-color: #1B1B1B;
    }}
    QComboBox::drop-down {{ border: none; width: 22px; }}
    QComboBox QAbstractItemView {{
        background-color: {BG_CARD}; color: {TEXT_SEC};
        border: 1px solid {BORDER}; selection-background-color: {BG_HOVER};
        selection-color: {TEXT_PRI};
    }}
    QSpinBox::up-button, QSpinBox::down-button,
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
        width: 16px; border: none; background: transparent;
    }}
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
        image: none; border-left: 4px solid transparent;
        border-right: 4px solid transparent; border-bottom: 5px solid {TEXT_MUT};
        width: 0; height: 0;
    }}
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
        image: none; border-left: 4px solid transparent;
        border-right: 4px solid transparent; border-top: 5px solid {TEXT_MUT};
        width: 0; height: 0;
    }}
    QCalendarWidget {{
        background-color: {BG_CARD}; color: {TEXT_SEC};
        border: 1px solid {BORDER}; border-radius: 10px;
    }}
"""

TEXTEDIT_STYLE = f"""
    QTextEdit {{
        background-color: #181818; color: {TEXT_PRI};
        border: 1px solid #303030; border-radius: 9px;
        padding: 10px 13px; font-size: 11px; font-weight: 500;
        font-family: 'Inter','Segoe UI',sans-serif;
        selection-background-color: {RED}44;
    }}
    QTextEdit:focus {{ border-color: {RED}; background-color: #1B1B1B; }}
"""


class EventEditorDialog(QDialog):
    def __init__(self, repo, current_user, event_id=None, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.current_user = current_user
        self.current_user_id = current_user.get("id") if current_user else None
        self._event_id = event_id
        self._cover_path = None
        self._is_edit = event_id is not None
        self.saved_event_id = None
        self._drag_pos = None

        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)

        screen = QApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else QRect(0, 0, 1280, 800)
        w = min(1180, max(980, avail.width() - 120))
        h = min(860, max(680, avail.height() - 100))
        self.resize(w, h)

        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(60)
        self._preview_timer.timeout.connect(self._update_live_preview)

        self._build_ui()
        self._connect_preview_signals()
        self._update_live_preview()

        if self._is_edit:
            QTimer.singleShot(100, self._load_event)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(0)

        self.dialog_card = QFrame()
        self.dialog_card.setObjectName("EventEditorCard")
        self.dialog_card.setStyleSheet(f"""
            QFrame#EventEditorCard {{
                background-color: #0D0D0D;
                border: 1px solid #2B2B2B;
                border-radius: 18px;
            }}
            QFrame#EventEditorCard QLabel {{
                background-color: transparent;
                border: none;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self.dialog_card)
        shadow.setBlurRadius(36)
        shadow.setOffset(0, 12)
        shadow.setColor(QColor(0, 0, 0, 200))
        self.dialog_card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.dialog_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        self._build_header(card_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet(f"QSplitter {{ background: transparent; border: none; }} QSplitter::handle {{ background-color: #1A1A1A; }}")

        left = self._build_form_panel()
        right = self._build_preview_panel()

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([680, 400])
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        card_layout.addWidget(splitter, 1)
        root.addWidget(self.dialog_card, 1)

    # ── Header ────────────────────────────────────────────────────

    def _build_header(self, parent):
        header = QFrame()
        self._header = header
        header.setObjectName("EditorHeader")
        header.setFixedHeight(76)
        header.setStyleSheet(f"""
            QFrame#EditorHeader {{
                background-color: #0D0D0D;
                border-bottom: 1px solid #1E1E1E;
                border-top-left-radius: 18px;
                border-top-right-radius: 18px;
            }}
            QFrame#EditorHeader QLabel {{
                background: transparent; border: none;
            }}
        """)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 20, 0)
        layout.setSpacing(12)

        try:
            from app.main import IconLabel
            icon = IconLabel("event", 22, RED_H)
        except Exception:
            icon = QLabel("●")
            icon.setStyleSheet(f"color: {RED_H}; font-size: 22px; background: transparent; border: none;")
        layout.addWidget(icon)

        text_col = QVBoxLayout()
        text_col.setSpacing(0)
        eyebrow = QLabel("EVENTOS")
        eyebrow.setStyleSheet(f"color: {TEXT_MUT}; font-size: 8px; font-weight: 900; letter-spacing: 1.2px; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
        text_col.addWidget(eyebrow)

        self._header_title = QLabel("Crear evento" if not self._is_edit else "Editar evento")
        self._header_title.setStyleSheet(f"color: {TEXT_PRI}; font-size: 15px; font-weight: 800; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
        text_col.addWidget(self._header_title)

        subtitle = "Diseña una publicación para la comunidad" if not self._is_edit else "Actualiza la información de la publicación"
        lbl_sub = QLabel(subtitle)
        lbl_sub.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
        text_col.addWidget(lbl_sub)
        layout.addLayout(text_col, 1)

        self._btn_draft = QPushButton("Guardar borrador")
        self._btn_draft.setFixedHeight(34)
        self._btn_draft.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._btn_draft.setStyleSheet(f"""
            QPushButton {{
                background-color: #1A1A1A; color: {TEXT_SEC};
                border: 1px solid #303030; border-radius: 8px;
                padding: 0 14px; font-size: 10px; font-weight: 700;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QPushButton:hover {{ background-color: #222; color: {TEXT_PRI}; border-color: #414141; }}
        """)
        self._btn_draft.clicked.connect(lambda: self._save(target_status="draft"))
        layout.addWidget(self._btn_draft)

        self._btn_publish = QPushButton("Publicar evento")
        self._btn_publish.setFixedHeight(34)
        self._btn_publish.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._btn_publish.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED}; color: white;
                border: 1px solid {RED_H}; border-radius: 8px;
                padding: 0 16px; font-size: 10px; font-weight: 800;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QPushButton:hover {{ background-color: {RED_H}; }}
        """)
        self._btn_publish.clicked.connect(lambda: self._save(target_status="publish"))
        layout.addWidget(self._btn_publish)

        btn_close = QPushButton()
        btn_close.setFixedSize(32, 32)
        btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUT};
                border: 1px solid transparent; border-radius: 8px;
                font-size: 14px; font-weight: 700;
            }}
            QPushButton:hover {{ color: {RED_H}; background: rgba(200,16,46,0.08); border: 1px solid rgba(200,16,46,0.2); }}
        """)
        btn_close.setText("×")
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close)

        parent.addWidget(header)

    # ── Form panel (left) ─────────────────────────────────────────

    def _build_form_panel(self):
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._error_banner = QLabel("")
        self._error_banner.setWordWrap(True)
        self._error_banner.hide()
        self._error_banner.setStyleSheet(f"""
            background-color: rgba(225, 29, 72, 0.08);
            border: 1px solid rgba(225, 29, 72, 0.28);
            border-radius: 9px;
            color: #FB7185;
            padding: 10px 14px;
            font-size: 11px; font-weight: 600;
            font-family: 'Inter','Segoe UI',sans-serif;
        """)
        layout.addWidget(self._error_banner)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{ background: transparent; width: 6px; }}
            QScrollBar::handle:vertical {{ background: #333; border-radius: 3px; min-height: 30px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

        form = QWidget()
        form.setStyleSheet("background: transparent;")
        self._form_layout = QVBoxLayout(form)
        self._form_layout.setContentsMargins(24, 16, 24, 24)
        self._form_layout.setSpacing(14)

        self._build_info_section()
        self._build_datetime_section()
        self._build_location_section()
        self._build_registration_section()
        self._build_publish_section()
        self._build_appearance_section()

        self._form_layout.addStretch()
        scroll.setWidget(form)
        layout.addWidget(scroll, 1)
        return panel

    # ── Section builders ──────────────────────────────────────────

    def _section(self, title, desc=""):
        frame = QFrame()
        frame.setObjectName("EditorSection")
        frame.setStyleSheet(f"""
            QFrame#EditorSection {{
                background-color: #111111;
                border: 1px solid #252525;
                border-radius: 14px;
            }}
            QFrame#EditorSection QLabel {{
                background: transparent; border: none;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        if title:
            lbl = QLabel(title.upper())
            lbl.setStyleSheet(f"color: {RED_H}; font-size: 8px; font-weight: 900; letter-spacing: 1px; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
            layout.addWidget(lbl)
        if desc:
            lbl_d = QLabel(desc)
            lbl_d.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
            layout.addWidget(lbl_d)
        return frame, layout

    def _field(self, label, widget):
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        if label:
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 600; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
            lay.addWidget(lbl)
        lay.addWidget(widget)
        return w

    def _line(self, placeholder=""):
        w = QLineEdit()
        w.setFixedHeight(42)
        w.setPlaceholderText(placeholder)
        w.setStyleSheet(INPUT_STYLE)
        return w

    def _text(self, lines=4, placeholder=""):
        w = QTextEdit()
        w.setFixedHeight(lines * 24)
        w.setPlaceholderText(placeholder)
        w.setStyleSheet(TEXTEDIT_STYLE)
        return w

    def _combo(self, items):
        cb = QComboBox()
        cb.setFixedHeight(42)
        for label, data in items:
            cb.addItem(label, data)
        cb.setStyleSheet(INPUT_STYLE)
        return cb

    def _spin_int(self, max_val=9999, suffix="", special="Sin límite"):
        sp = QSpinBox()
        sp.setRange(0, max_val)
        sp.setFixedHeight(42)
        if special:
            sp.setSpecialValueText(special)
        if suffix:
            sp.setSuffix(suffix)
        sp.setStyleSheet(INPUT_STYLE)
        return sp

    def _spin_money(self):
        sp = QDoubleSpinBox()
        sp.setRange(0, 99999999)
        sp.setDecimals(0)
        sp.setPrefix("$ ")
        sp.setFixedHeight(42)
        sp.setStyleSheet(INPUT_STYLE)
        return sp

    # ── Section 1: Info ───────────────────────────────────────────

    def _build_info_section(self):
        card, lay = self._section("Información principal", "Cuéntale a la comunidad de qué trata el evento.")

        self._name_edit = self._line("Ej. Seminario de Kickboxing 2026")
        lay.addWidget(self._field("Nombre del evento *", self._name_edit))

        self._type_combo = self._combo([
            ("Torneo", "torneo"), ("Seminario", "seminario"),
            ("Examen", "examen"), ("Clase especial", "clase especial"),
            ("Campeonato", "campeonato"), ("Encuentro", "encuentro"),
            ("Workshop", "workshop"), ("Otro", "otro"),
        ])
        lay.addWidget(self._field("Tipo de evento", self._type_combo))

        self._custom_type_container = QWidget()
        self._custom_type_container.setStyleSheet("background: transparent; border: none;")
        ct_layout = QVBoxLayout(self._custom_type_container)
        ct_layout.setContentsMargins(0, 0, 0, 0)
        ct_layout.setSpacing(4)
        ct_lbl = QLabel("Tipo personalizado *")
        ct_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 600; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
        ct_layout.addWidget(ct_lbl)
        self._custom_type_edit = self._line("Ej. Festival, conferencia, entrenamiento abierto...")
        self._custom_type_edit.setMaxLength(50)
        ct_layout.addWidget(self._custom_type_edit)
        self._custom_type_error = QLabel("")
        self._custom_type_error.setStyleSheet(f"color: #FB7185; font-size: 9px; font-weight: 600; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
        self._custom_type_error.hide()
        ct_layout.addWidget(self._custom_type_error)
        self._custom_type_container.hide()
        lay.addWidget(self._custom_type_container)
        self._type_combo.currentIndexChanged.connect(self._update_custom_type_visibility)

        self._short_desc_edit = self._text(2, "Una frase breve que aparecerá en la tarjeta del evento.")
        sd_row = QHBoxLayout()
        sd_row.setSpacing(8)
        sd_row.addWidget(self._field("Descripción corta", self._short_desc_edit), 1)
        self._short_desc_counter = QLabel("0 / 280")
        self._short_desc_counter.setFixedWidth(60)
        self._short_desc_counter.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 600; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none; padding-top: 18px;")
        sd_row.addWidget(self._short_desc_counter)
        lay.addLayout(sd_row)
        self._short_desc_edit.textChanged.connect(self._update_short_desc_counter)

        self._desc_edit = self._text(6, "Describe el objetivo, actividades y recomendaciones.")
        lay.addWidget(self._field("Descripción", self._desc_edit))

        self._form_layout.addWidget(card)

    # ── Section 2: Date/time ──────────────────────────────────────

    def _build_datetime_section(self):
        card, lay = self._section("Fecha y horario")

        row1 = QHBoxLayout()
        row1.setSpacing(10)
        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDate(QDate.currentDate())
        self._date_edit.setFixedHeight(42)
        self._date_edit.setStyleSheet(INPUT_STYLE)
        row1.addWidget(self._field("Fecha del evento *", self._date_edit))

        self._start_time = QTimeEdit()
        self._start_time.setTime(QTime(9, 0))
        self._start_time.setFixedHeight(42)
        self._start_time.setStyleSheet(INPUT_STYLE)
        row1.addWidget(self._field("Hora inicio", self._start_time))

        self._end_time = QTimeEdit()
        self._end_time.setTime(QTime(17, 0))
        self._end_time.setFixedHeight(42)
        self._end_time.setStyleSheet(INPUT_STYLE)
        row1.addWidget(self._field("Hora fin", self._end_time))
        lay.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self._end_date_edit = QDateEdit()
        self._end_date_edit.setCalendarPopup(True)
        self._end_date_edit.setDate(QDate.currentDate())
        self._end_date_edit.setFixedHeight(42)
        self._end_date_edit.setStyleSheet(INPUT_STYLE)
        row2.addWidget(self._field("Fecha fin", self._end_date_edit))

        self._reg_deadline = QDateEdit()
        self._reg_deadline.setCalendarPopup(True)
        self._reg_deadline.setDate(QDate.currentDate())
        self._reg_deadline.setFixedHeight(42)
        self._reg_deadline.setStyleSheet(INPUT_STYLE)
        row2.addWidget(self._field("Fecha límite inscripción", self._reg_deadline))
        row2.addStretch()
        lay.addLayout(row2)

        self._form_layout.addWidget(card)

    # ── Section 3: Location ───────────────────────────────────────

    def _build_location_section(self):
        card, lay = self._section("Lugar")

        self._location_edit = self._line("Ej. Sede principal")
        lay.addWidget(self._field("Lugar", self._location_edit))

        self._venue_edit = self._line("Nombre del venue o espacio")
        lay.addWidget(self._field("Nombre del venue", self._venue_edit))

        self._address_edit = self._line("Dirección")
        lay.addWidget(self._field("Dirección", self._address_edit))

        row = QHBoxLayout()
        row.setSpacing(10)
        self._city_edit = self._line("Barranquilla")
        row.addWidget(self._field("Ciudad", self._city_edit))
        self._country_edit = self._line("Colombia")
        self._country_edit.setText("Colombia")
        row.addWidget(self._field("País", self._country_edit))
        lay.addLayout(row)

        self._form_layout.addWidget(card)

    # ── Section 4: Registration ───────────────────────────────────

    def _build_registration_section(self):
        card, lay = self._section("Inscripción", "Configura cómo los usuarios pueden inscribirse.")

        self._reg_enabled_check = QCheckBox("Inscripción habilitada")
        self._reg_enabled_check.setObjectName("EditorOptionCard")
        self._reg_enabled_check.setCheckable(True)
        self._reg_enabled_check.setStyleSheet(f"""
            QCheckBox#EditorOptionCard {{
                background-color: #151515;
                border: 1px solid #292929;
                border-radius: 10px;
                padding: 11px 13px;
                color: {TEXT_SEC};
                font-size: 11px; font-weight: 600;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QCheckBox#EditorOptionCard:hover {{ border-color: #3A3A3A; }}
            QCheckBox#EditorOptionCard:checked {{
                background-color: rgba(200, 16, 46, 0.08);
                border-color: rgba(200, 16, 46, 0.45);
                color: {TEXT_PRI};
            }}
        """)
        self._reg_enabled_check.toggled.connect(self._update_registration_fields)
        lay.addWidget(self._reg_enabled_check)

        self._registration_options_container = QWidget()
        self._registration_options_container.setStyleSheet("background: transparent; border: none;")
        ro_layout = QVBoxLayout(self._registration_options_container)
        ro_layout.setContentsMargins(0, 6, 0, 0)
        ro_layout.setSpacing(10)

        row = QHBoxLayout()
        row.setSpacing(10)
        self._capacity_spin = self._spin_int(9999, "", "Sin límite")
        row.addWidget(self._field("Capacidad", self._capacity_spin))
        self._price_spin = self._spin_money()
        row.addWidget(self._field("Precio (COP)", self._price_spin))
        ro_layout.addLayout(row)

        self._form_layout.addWidget(card)

    def _update_registration_fields(self, checked):
        self._registration_options_container.setEnabled(checked)

    # ── Section 5: Publish / visibility ───────────────────────────

    def _build_publish_section(self):
        card, lay = self._section("Publicación y visibilidad")

        row = QHBoxLayout()
        row.setSpacing(10)
        self._status_combo = self._combo([
            ("Borrador", "draft"), ("Publicado", "published"),
            ("Inscripción abierta", "registration_open"),
            ("Inscripción cerrada", "registration_closed"),
            ("En curso", "in_progress"), ("Finalizado", "completed"),
            ("Aplazado", "postponed"),
        ])
        row.addWidget(self._field("Estado", self._status_combo))
        self._visibility_combo = self._combo([
            ("Interno", "internal"), ("Público", "public"), ("Privado", "private"),
        ])
        row.addWidget(self._field("Visibilidad", self._visibility_combo))
        lay.addLayout(row)

        self._featured_check = QCheckBox("Evento destacado")
        self._featured_check.setObjectName("EditorOptionCard")
        self._featured_check.setStyleSheet(f"""
            QCheckBox#EditorOptionCard {{
                background-color: #151515; border: 1px solid #292929;
                border-radius: 10px; padding: 11px 13px;
                color: {TEXT_SEC}; font-size: 11px; font-weight: 600;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QCheckBox#EditorOptionCard:hover {{ border-color: #3A3A3A; }}
            QCheckBox#EditorOptionCard:checked {{
                background-color: rgba(200, 16, 46, 0.08);
                border-color: rgba(200, 16, 46, 0.45); color: {TEXT_PRI};
            }}
        """)
        lay.addWidget(self._featured_check)

        self._important_check = QCheckBox("Evento importante — se resaltará en calendario y notificaciones")
        self._important_check.setObjectName("EditorOptionCard")
        self._important_check.setStyleSheet(f"""
            QCheckBox#EditorOptionCard {{
                background-color: #151515; border: 1px solid #292929;
                border-radius: 10px; padding: 11px 13px;
                color: {TEXT_SEC}; font-size: 11px; font-weight: 600;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QCheckBox#EditorOptionCard:hover {{ border-color: #3A3A3A; }}
            QCheckBox#EditorOptionCard:checked {{
                background-color: rgba(200, 16, 46, 0.08);
                border-color: rgba(200, 16, 46, 0.45); color: {TEXT_PRI};
            }}
        """)
        lay.addWidget(self._important_check)

        self._form_layout.addWidget(card)

    # ── Section 6: Appearance ─────────────────────────────────────

    def _build_appearance_section(self):
        card, lay = self._section("Imagen y apariencia", "Destaca tu evento con una portada y color único.")

        cover_row = QHBoxLayout()
        cover_row.setSpacing(14)

        self._cover_preview = QLabel("Agrega una portada para destacar tu evento")
        self._cover_preview.setFixedSize(220, 124)
        self._cover_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cover_preview.setStyleSheet(f"""
            background-color: #181818; color: {TEXT_MUT};
            border: 1px dashed #303030; border-radius: 10px;
            font-size: 10px; font-weight: 500;
            font-family: 'Inter','Segoe UI',sans-serif;
        """)
        cover_row.addWidget(self._cover_preview)

        cover_btns = QVBoxLayout()
        cover_btns.setSpacing(6)
        btn_select = QPushButton("Seleccionar imagen")
        btn_select.setFixedHeight(34)
        btn_select.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_select.setStyleSheet(f"""
            QPushButton {{
                background-color: #1A1A1A; color: {TEXT_SEC};
                border: 1px solid #303030; border-radius: 8px;
                padding: 0 14px; font-size: 10px; font-weight: 600;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QPushButton:hover {{ background-color: #222; color: {TEXT_PRI}; border-color: #414141; }}
        """)
        btn_select.clicked.connect(self._select_cover)
        cover_btns.addWidget(btn_select)

        btn_clear = QPushButton("Quitar imagen")
        btn_clear.setFixedHeight(30)
        btn_clear.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_clear.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUT};
                border: 1px solid transparent; border-radius: 6px;
                padding: 0 12px; font-size: 10px; font-weight: 500;
                font-family: 'Inter','Segoe UI',sans-serif;
            }}
            QPushButton:hover {{ color: {RED_H}; }}
        """)
        btn_clear.clicked.connect(self._clear_cover)
        cover_btns.addWidget(btn_clear)
        cover_btns.addStretch()
        cover_row.addLayout(cover_btns)
        cover_row.addStretch()
        lay.addLayout(cover_row)

        color_lbl = QLabel("Color del evento")
        color_lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 10px; font-weight: 600; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
        lay.addWidget(color_lbl)

        presets = [
            ("#C8102E", "Rojo"), ("#3B82F6", "Azul"), ("#22C55E", "Verde"),
            ("#A855F7", "Violeta"), ("#F59E0B", "Amarillo"), ("#F97316", "Naranja"),
        ]
        preset_row = QHBoxLayout()
        preset_row.setSpacing(8)
        self._color_preset_buttons = []
        for color_hex, name in presets:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setToolTip(name)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_hex}; border: 2px solid transparent;
                    border-radius: 10px;
                }}
                QPushButton:hover {{ border-color: #FFF; }}
            """)
            btn.clicked.connect(lambda _, c=color_hex: self._set_color(c))
            preset_row.addWidget(btn)
            self._color_preset_buttons.append((btn, color_hex))
        preset_row.addStretch()

        self._color_edit = QLineEdit()
        self._color_edit.setText("#3B82F6")
        self._color_edit.setFixedHeight(34)
        self._color_edit.setMaximumWidth(110)
        self._color_edit.setStyleSheet(INPUT_STYLE)
        self._color_edit.textChanged.connect(self._update_color_preview)
        preset_row.addWidget(self._color_edit)

        self._color_swatch = QFrame()
        self._color_swatch.setFixedSize(34, 34)
        self._color_swatch.setStyleSheet(f"background-color: #3B82F6; border-radius: 10px; border: 2px solid {BORDER};")
        preset_row.addWidget(self._color_swatch)
        preset_row.addStretch()
        lay.addLayout(preset_row)

        self._form_layout.addWidget(card)

    # ── Preview panel (right) ─────────────────────────────────────

    def _build_preview_panel(self):
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        panel.setMinimumWidth(320)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(10)

        lbl = QLabel("VISTA PREVIA")
        lbl.setStyleSheet(f"color: {TEXT_MUT}; font-size: 8px; font-weight: 900; letter-spacing: 1.2px; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
        layout.addWidget(lbl)

        lbl2 = QLabel("Así verá la comunidad tu evento.")
        lbl2.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
        layout.addWidget(lbl2)

        self._preview = EventLivePreview()
        self._preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self._preview)

        tips_card = QFrame()
        tips_card.setStyleSheet(f"""
            QFrame {{ background-color: #111; border: 1px solid #252525; border-radius: 12px; }}
            QFrame QLabel {{ background: transparent; border: none; }}
        """)
        tips_layout = QVBoxLayout(tips_card)
        tips_layout.setContentsMargins(16, 14, 16, 14)
        tips_layout.setSpacing(6)

        tips_title = QLabel("CONSEJOS")
        tips_title.setStyleSheet(f"color: {TEXT_MUT}; font-size: 8px; font-weight: 900; letter-spacing: 1px; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
        tips_layout.addWidget(tips_title)

        for tip in [
            "Usa una portada horizontal de al menos 800×400 px",
            "Escribe un título claro y descriptivo",
            "La descripción corta es lo primero que verán",
        ]:
            t = QLabel(f"• {tip}")
            t.setWordWrap(True)
            t.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; font-weight: 500; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none;")
            tips_layout.addWidget(t)

        layout.addWidget(tips_card)
        layout.addStretch()
        return panel

    # ── Signal connections ────────────────────────────────────────

    def _connect_preview_signals(self):
        signals = [
            (self._name_edit, "textChanged"),
            (self._short_desc_edit, "textChanged"),
            (self._type_combo, "currentIndexChanged"),
            (self._date_edit, "dateChanged"),
            (self._start_time, "timeChanged"),
            (self._location_edit, "textChanged"),
            (self._venue_edit, "textChanged"),
            (self._city_edit, "textChanged"),
            (self._price_spin, "valueChanged"),
            (self._capacity_spin, "valueChanged"),
            (self._status_combo, "currentIndexChanged"),
            (self._featured_check, "toggled"),
            (self._reg_enabled_check, "toggled"),
            (self._color_edit, "textChanged"),
        ]
        for widget, signal_name in signals:
            sig = getattr(widget, signal_name, None)
            if sig is not None:
                try:
                    sig.connect(self._schedule_preview_update)
                except Exception:
                    pass

        if self._custom_type_edit:
            self._custom_type_edit.textChanged.connect(self._schedule_preview_update)

    def _schedule_preview_update(self):
        self._preview_timer.start()

    def _update_live_preview(self):
        data = self._collect_preview_data()
        self._preview.update_event(data)

    def _collect_preview_data(self):
        selected = self._type_combo.currentData() or ""
        if selected == "otro":
            et = self._custom_type_edit.text().strip() or "Otro"
        else:
            et = self._type_combo.currentText() or "Evento"
        return {
            "name": (
                self._name_edit.text().strip()
                or "Nombre del evento"
            ),
            "event_type": et,
            "short_description": (
                self._short_desc_edit.toPlainText().strip()
                or "La descripción breve aparecerá aquí."
            ),
            "event_date": self._date_edit.date().toPyDate(),
            "start_time": self._start_time.time().toPyTime(),
            "location": self._location_edit.text().strip(),
            "venue_name": self._venue_edit.text().strip(),
            "city": self._city_edit.text().strip(),
            "price": self._price_spin.value(),
            "capacity": self._capacity_spin.value() or None,
            "status": self._status_combo.currentData(),
            "is_featured": self._featured_check.isChecked(),
            "registration_enabled": self._reg_enabled_check.isChecked(),
            "cover_image_path": self._cover_path,
            "color": self._validated_color(),
        }

    # ── Helpers ───────────────────────────────────────────────────

    def _validated_color(self):
        v = self._color_edit.text().strip().upper()
        if re.fullmatch(r"#[0-9A-F]{6}", v):
            return v
        return "#3B82F6"

    def _set_color(self, color_hex):
        self._color_edit.setText(color_hex)

    def _update_color_preview(self):
        c = self._validated_color()
        self._color_swatch.setStyleSheet(f"background-color: {c}; border-radius: 10px; border: 2px solid {BORDER};")

    def _update_custom_type_visibility(self):
        is_other = self._type_combo.currentData() == "otro"
        self._custom_type_container.setVisible(is_other)
        if not is_other:
            self._custom_type_error.hide()

    def _update_short_desc_counter(self):
        n = len(self._short_desc_edit.toPlainText())
        color = "#FB7185" if n > 280 else TEXT_MUT
        self._short_desc_counter.setText(f"{n} / 280")
        self._short_desc_counter.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: 600; font-family: 'Inter','Segoe UI',sans-serif; background: transparent; border: none; padding-top: 18px;")

    # ── Cover ─────────────────────────────────────────────────────

    def _select_cover(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar portada", "",
            "Imágenes (*.png *.jpg *.jpeg *.webp)",
        )
        if path:
            try:
                from services.event_media_service import EventMediaService
                svc = EventMediaService()
                saved = svc.save_cover(path)
                if saved:
                    self._cover_path = saved
                    self._load_cover(saved)
                    self._schedule_preview_update()
                else:
                    self._cover_preview.setText("Error al guardar")
            except Exception as e:
                debug_log(f"[EventEditor] Error guardando portada: {e}")

    def _clear_cover(self):
        self._cover_path = None
        self._cover_preview.setPixmap(QPixmap())
        self._cover_preview.setText("Agrega una portada para destacar tu evento")
        self._cover_preview.setStyleSheet(f"""
            background-color: #181818; color: {TEXT_MUT};
            border: 1px dashed #303030; border-radius: 10px;
            font-size: 10px; font-weight: 500;
            font-family: 'Inter','Segoe UI',sans-serif;
        """)
        self._schedule_preview_update()

    def _load_cover(self, path):
        from views.events.event_widgets import load_cover_pixmap
        pix = load_cover_pixmap(path, QSize(210, 118))
        if pix:
            self._cover_preview.setPixmap(pix)
            self._cover_preview.setStyleSheet("border: none; border-radius: 10px;")
        else:
            self._cover_preview.setText("Error al cargar imagen")

    # ── Load event (edit mode) ────────────────────────────────────

    def _load_event(self):
        try:
            ev = self.repo.get_event_detail(self._event_id)
            if not ev:
                return

            self._name_edit.setText(ev.get("name", ""))

            et = (ev.get("event_type") or "").strip().lower()
            known_idx = self._type_combo.findData(et)
            if known_idx >= 0:
                self._type_combo.setCurrentIndex(known_idx)
            elif et:
                self._type_combo.setCurrentIndex(self._type_combo.count() - 1)
                self._custom_type_edit.setText(ev.get("event_type", ""))
            self._update_custom_type_visibility()

            self._short_desc_edit.setPlainText(ev.get("short_description", ""))
            self._desc_edit.setPlainText(ev.get("description", ""))

            ed = ev.get("event_date")
            if ed and hasattr(ed, "year"):
                self._date_edit.setDate(QDate(ed.year, ed.month, ed.day))

            st = ev.get("start_time")
            if st and hasattr(st, "hour"):
                self._start_time.setTime(QTime(st.hour, st.minute))

            et2 = ev.get("end_time")
            if et2 and hasattr(et2, "hour"):
                self._end_time.setTime(QTime(et2.hour, et2.minute))

            ed2 = ev.get("end_date")
            if ed2 and hasattr(ed2, "year"):
                self._end_date_edit.setDate(QDate(ed2.year, ed2.month, ed2.day))

            dl = ev.get("registration_deadline")
            if dl and hasattr(dl, "year"):
                self._reg_deadline.setDate(QDate(dl.year, dl.month, dl.day))

            self._location_edit.setText(ev.get("location", ""))
            self._venue_edit.setText(ev.get("venue_name", ""))
            self._address_edit.setText(ev.get("address", ""))
            self._city_edit.setText(ev.get("city", ""))
            self._country_edit.setText(ev.get("country", ""))

            cap = ev.get("capacity") or 0
            self._capacity_spin.setValue(cap)
            price = ev.get("price") or 0
            self._price_spin.setValue(float(price))

            self._reg_enabled_check.setChecked(bool(ev.get("registration_enabled")))
            self._update_registration_fields(self._reg_enabled_check.isChecked())

            self._featured_check.setChecked(bool(ev.get("is_featured")))
            self._important_check.setChecked(bool(ev.get("is_important")))

            si = self._status_combo.findData(ev.get("status", "draft"))
            if si >= 0:
                self._status_combo.setCurrentIndex(si)

            vis = ev.get("visibility", "internal")
            vi = self._visibility_combo.findData(vis)
            if vi >= 0:
                self._visibility_combo.setCurrentIndex(vi)
            else:
                internal_index = self._visibility_combo.findData("internal")
                if internal_index >= 0:
                    self._visibility_combo.setCurrentIndex(internal_index)

            color = ev.get("color", "#3B82F6")
            self._color_edit.setText(color)
            self._update_color_preview()

            if ev.get("cover_image_path"):
                self._cover_path = ev["cover_image_path"]
                self._load_cover(self._cover_path)

            self._schedule_preview_update()

        except Exception as e:
            debug_log(f"[EventEditor] Error cargando evento: {e}")

    # ── Validation ────────────────────────────────────────────────

    def _validate(self, strict=False):
        errors = []

        name = self._name_edit.text().strip()
        if not name:
            errors.append("El nombre del evento es obligatorio.")
        elif len(name) < 3:
            errors.append("El nombre debe tener al menos 3 caracteres.")

        if self._type_combo.currentData() == "otro":
            ct = self._custom_type_edit.text().strip()
            if not ct or len(ct) < 3:
                errors.append("El tipo personalizado debe tener al menos 3 caracteres.")
                self._custom_type_error.setText("Mínimo 3 caracteres")
                self._custom_type_error.show()
            else:
                self._custom_type_error.hide()

        sd = self._short_desc_edit.toPlainText().strip()
        if strict and not sd:
            errors.append("La descripción corta es obligatoria para publicar.")
        if len(sd) > 280:
            errors.append("La descripción corta no puede superar 280 caracteres.")

        if strict and not self._desc_edit.toPlainText().strip():
            errors.append("La descripción es obligatoria para publicar.")

        if strict and not self._location_edit.text().strip():
            errors.append("El lugar es obligatorio para publicar.")

        start_date = self._date_edit.date().toPyDate()
        end_date = self._end_date_edit.date().toPyDate()
        start_time = self._start_time.time().toPyTime()
        end_time = self._end_time.time().toPyTime()

        if end_date < start_date:
            errors.append(
                "La fecha final no puede ser anterior a la fecha inicial."
            )

        if end_date == start_date and end_time <= start_time:
            errors.append(
                "La hora final debe ser posterior a la hora inicial."
            )

        if strict and not self._reg_enabled_check.isChecked():
            if self._capacity_spin.value() == 0 and self._price_spin.value() > 0:
                errors.append("Configura la inscripción para cobrar por el evento.")

        if self._reg_enabled_check.isChecked():
            dl = self._reg_deadline.date().toPyDate()
            ed = self._date_edit.date().toPyDate()
            if dl > ed:
                errors.append("La fecha límite de inscripción no puede ser posterior al evento.")

        raw_color = self._color_edit.text().strip().upper()
        if not re.fullmatch(r"#[0-9A-F]{6}", raw_color):
            errors.append(
                "El color debe ser un código hexadecimal válido (#RRGGBB)."
            )

        return errors

    def _show_errors(self, errors):
        if errors:
            self._error_banner.setText(" · ".join(errors))
            self._error_banner.show()
        else:
            self._error_banner.hide()

    # ── Save ──────────────────────────────────────────────────────

    def _save(self, target_status=None):
        self._error_banner.hide()
        self._custom_type_error.hide()

        strict = target_status == "publish"
        errors = self._validate(strict=strict)
        if errors:
            self._show_errors(errors)
            return

        name = self._name_edit.text().strip()
        selected_type = self._type_combo.currentData() or ""
        if selected_type == "otro":
            event_type = self._custom_type_edit.text().strip()
        else:
            event_type = selected_type

        dl_val = self._reg_deadline.date().toPyDate()
        ed_val = self._date_edit.date().toPyDate()

        if target_status == "draft":
            status = "draft"
        elif target_status == "publish":
            if self._reg_enabled_check.isChecked():
                status = "registration_open"
            else:
                status = "published"
        else:
            current = self._status_combo.currentData() or "draft"
            advanced = {"in_progress", "completed", "cancelled"}
            if current in advanced and self._is_edit:
                status = current
            else:
                status = "draft"

        data = {
            "name": name,
            "event_type": event_type,
            "short_description": self._short_desc_edit.toPlainText().strip(),
            "description": self._desc_edit.toPlainText().strip(),
            "event_date": ed_val,
            "start_time": self._start_time.time().toPyTime(),
            "end_time": self._end_time.time().toPyTime(),
            "end_date": self._end_date_edit.date().toPyDate(),
            "registration_deadline": dl_val if self._reg_enabled_check.isChecked() else None,
            "location": self._location_edit.text().strip(),
            "venue_name": self._venue_edit.text().strip(),
            "address": self._address_edit.text().strip(),
            "city": self._city_edit.text().strip(),
            "country": self._country_edit.text().strip(),
            "capacity": self._capacity_spin.value() or None,
            "price": self._price_spin.value(),
            "is_featured": self._featured_check.isChecked(),
            "registration_enabled": self._reg_enabled_check.isChecked(),
            "is_important": self._important_check.isChecked(),
            "status": status,
            "visibility": self._visibility_combo.currentData() or "internal",
            "cover_image_path": self._cover_path,
            "color": self._validated_color(),
            "organizer_user_id": self.current_user_id,
        }

        try:
            if self._is_edit:
                ok = self.repo.update_event(self._event_id, data)
                if ok:
                    self.saved_event_id = self._event_id
                    self.accept()
            else:
                new_id = self.repo.create_event(data)
                if new_id is not None:
                    self.saved_event_id = new_id
                    self.accept()
        except Exception as e:
            debug_log(f"[EventEditor] Error guardando: {e}")
            self._show_errors([f"Error al guardar: {e}"])

    # ── Cleanup ───────────────────────────────────────────────────

    def done(self, result):
        try:
            if hasattr(self, "_preview_timer"):
                self._preview_timer.stop()
            if hasattr(self, "dialog_card") and self.dialog_card is not None:
                self.dialog_card.setGraphicsEffect(None)
        except Exception as e:
            debug_log(f"[EventEditor] Error limpiando modal: {e}")
        super().done(result)

    # ── Drag from header ──────────────────────────────────────────

    def _point_is_in_header(self, dialog_point):
        """Return True only when a dialog-local point is inside the header."""
        if not hasattr(self, "_header") or self._header is None:
            return False

        header_point = self._header.mapFrom(
            self,
            dialog_point,
        )
        return self._header.rect().contains(header_point)

    def mousePressEvent(self, event):
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self._point_is_in_header(event.position().toPoint())
        ):
            clicked_widget = self.childAt(event.position().toPoint())
            if not isinstance(clicked_widget, QPushButton):
                self._drag_pos = (
                    event.globalPosition().toPoint()
                    - self.frameGeometry().topLeft()
                )
                event.accept()
                return

        self._drag_pos = None
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self._drag_pos is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            target = event.globalPosition().toPoint() - self._drag_pos

            screen = self.screen() or QApplication.primaryScreen()
            if screen is not None:
                available = screen.availableGeometry()
                max_x = available.right() - self.width() + 1
                max_y = available.bottom() - self.height() + 1
                target.setX(max(available.left(), min(target.x(), max_x)))
                target.setY(max(available.top(), min(target.y(), max_y)))

            self.move(target)
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)
