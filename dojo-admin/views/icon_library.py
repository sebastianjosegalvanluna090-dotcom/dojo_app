"""Dojo Admin -- Icon library (SVG-based, theme-aware).

Professional icon system loading vector SVGs from ``assets/Icons/outline/``
with support for dark/light themes and user/system icon categories.

Directory structure::

    assets/Icons/outline/
        black/          -- black fill icons (for light theme backgrounds)
            usables/    -- user-facing icons (martial arts, discipline picker)
            sistema/    -- system-only icons (UI chrome, not shown to users)
        light/          -- white fill icons (for dark theme backgrounds)
            usables/
            sistema/

Public API:

    render_icon_pixmap(icon_key, size, color) -> QPixmap
    AppIcon(widget)              -- icon widget
    MartialArtIcon(widget)       -- alias for AppIcon
    VectorIconPainter            -- painting engine
    ICON_DRAWERS                 -- dict of icon keys (compat, values are None)
    VALID_ICON_KEYS / ALL_ICON_KEYS
    normalize_icon_key(value, fallback)
    normalize_martial_art_icon(value, name)
    APP_ICON_LIBRARY / MARTIAL_ART_ICON_LIBRARY / SYSTEM_ICON_LIBRARY
    ICON_SEARCH_ALIASES
    search_icon_library(query, library)
    LEGACY_EMOJI_TO_ICON
    set_icon_theme(mode) / get_icon_theme() / toggle_icon_theme()
    ICON_CATEGORIES
"""
from __future__ import annotations

import re
import unicodedata
import warnings
from pathlib import Path
from typing import Callable

from PyQt6.QtCore import Qt, QRectF, QSize
from PyQt6.QtGui import QPainter, QColor, QPixmap, QPen, QBrush
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QWidget

# ── SVG directories ───────────────────────────────────────────────────────────

_SVG_ROOT: Path = Path(__file__).resolve().parent.parent / "assets" / "Icons" / "outline"

_ICON_THEME: str = "dark"  # default: dark theme -> use light/ (white icons)

_SVG_DIRS: dict[str, dict[str, Path]] = {
    "dark": {
        "usables": _SVG_ROOT / "light" / "usables",
        "sistema": _SVG_ROOT / "light" / "sistema",
    },
    "light": {
        "usables": _SVG_ROOT / "black" / "usables",
        "sistema": _SVG_ROOT / "black" / "sistema",
    },
}


def set_icon_theme(mode: str) -> None:
    """Set icon theme: 'dark' (white icons for dark bg) or 'light' (black icons for light bg)."""
    global _ICON_THEME
    _ICON_THEME = "dark" if mode == "dark" else "light"
    _SVG_CACHE.clear()


def get_icon_theme() -> str:
    return _ICON_THEME


def toggle_icon_theme() -> str:
    new = "light" if _ICON_THEME == "dark" else "dark"
    set_icon_theme(new)
    return new


# ── Renderer cache ────────────────────────────────────────────────────────────

_SVG_CACHE: dict[str, QSvgRenderer] = {}


def _resolve_svg_path(key: str) -> Path | None:
    """Find SVG file: check usables first, then sistema."""
    dirs = _SVG_DIRS[_ICON_THEME]
    for category in ("usables", "sistema"):
        svg_path = dirs[category] / f"{key}.svg"
        if svg_path.exists():
            return svg_path
    return None


def _get_renderer(key: str) -> QSvgRenderer | None:
    if key in _SVG_CACHE:
        return _SVG_CACHE[key]
    svg_path = _resolve_svg_path(key)
    if svg_path is None:
        return None
    renderer = QSvgRenderer(str(svg_path))
    if renderer.isValid():
        _SVG_CACHE[key] = renderer
        return renderer
    return None


_FIXED_BLACK_ATTR_RE = re.compile(
    r'(?i)(fill|stroke)="(?:#000000|#000|black|rgb\(\s*0\s*,\s*0\s*,\s*0\s*\))"'
)
_FIXED_BLACK_STYLE_RE = re.compile(
    r'(?i)(fill|stroke)\s*:\s*(?:#000000|#000|black|rgb\(\s*0\s*,\s*0\s*,\s*0\s*\))'
)
_SHAPE_TAG_RE = re.compile(r"<(path|circle|rect|line|polyline|polygon|ellipse)\b([^>]*?)(/?>)", re.I)
_HAS_COLOR_ATTR_RE = re.compile(r"(?i)(?:fill|stroke|style)\s*=")


def _recolor_svg_bytes(key: str, color: str) -> QSvgRenderer:
    """Load SVG, replace currentColor and hard-coded black with *color*.

    Some SVGs (e.g. lapiz/basura) carry no ``fill``/``stroke`` attribute at
    all, so the SVG default (black) would win. When the whole file has no
    colour attribute anywhere, the target *color* is injected as ``fill`` on
    every shape element instead.
    """
    svg_path = _resolve_svg_path(key)
    if svg_path is None:
        return None
    raw = svg_path.read_text(encoding="utf-8")

    raw = raw.replace("currentColor", color)

    raw = _FIXED_BLACK_ATTR_RE.sub(
        lambda m: f'{m.group(1)}="{color}"',
        raw,
    )
    raw = _FIXED_BLACK_STYLE_RE.sub(
        lambda m: f"{m.group(1)}:{color}",
        raw,
    )

    if not _HAS_COLOR_ATTR_RE.search(raw):
        def _inject_fill(m: re.Match) -> str:
            tag, attrs, closing = m.group(1), m.group(2), m.group(3)
            if _HAS_COLOR_ATTR_RE.search(attrs):
                return m.group(0)
            if attrs:
                return f"<{tag} fill=\"{color}\"{attrs}{closing}"
            return f"<{tag} fill=\"{color}\"{closing}"
        raw = _SHAPE_TAG_RE.sub(_inject_fill, raw)

    renderer = QSvgRenderer()
    renderer.load(raw.encode("utf-8"))
    return renderer if renderer.isValid() else None


# ── Legacy compatibility ──────────────────────────────────────────────────────

LEGACY_EMOJI_TO_ICON: dict[str, str] = {}

VB = 24.0

# ── ICON_DRAWERS (backward compat -- keys only, rendering via SVG) ────────────

ICON_DRAWERS: dict[str, None] = {}

# ── User-facing icons (discipline picker, settings) ──────────────────────────

_USER_KEYS: list[str] = [
    "patada", "meditacion", "combate-fight", "guantes-de-boxeo",
    "golpe-de-frente", "katanas", "golpe-hacia-arriba",
    "muay-thai", "muay-thai-1", "muay-thai-2", "muay-thai-3", "muay-thai-4",
    "pesos", "telefone", "treinamento",
    "boxe", "boxer", "cinto", "definicoes", "jiu-jitsu",
    "judo", "judo1", "karate1", "karate2",
    "karate-nuevo", "kickboxing-nuevo", "judo-olimpico",
    "ejercicio", "extendido", "hacer-subir", "luta-livre", "lutar",
    "mma-nuevo", "mma-nuevo-2", "pilates", "pilates-2",
    "rutina-de-ejercicio", "treinamento-em-artes-marciais",
]

# ── System-only icons (UI chrome, not shown to users) ────────────────────────

_SYSTEM_KEYS: list[str] = [
    "agregar-usuario", "ajustes-deslizadores", "aplicaciones", "basura",
    "busqueda", "cruz", "diseno-fluido", "energia", "estadisticas",
    "hogar", "lapiz", "marcador-de-mapa", "marcador", "reloj",
    "salir-alt", "sobre", "usuario", "usuarios-alt",
    "comentario-info", "paleta",
    "administracion", "ajustes", "cartera", "clases-eventos",
    "configuracion", "cuentas-por-cobrar", "egresos", "eventos",
    "ingresos", "insignia", "instructores", "inventario",
    "camiza", "brazalete", "niveles", "personalizado",
]

# ── All keys combined ─────────────────────────────────────────────────────────

_ALL_KEYS: list[str] = _USER_KEYS + _SYSTEM_KEYS

for _k in _ALL_KEYS:
    ICON_DRAWERS[_k] = None

_PAINTER_REGISTRY = ICON_DRAWERS

ALL_ICON_KEYS: list[str] = list(ICON_DRAWERS.keys())
VALID_ICON_KEYS: frozenset[str] = frozenset(ICON_DRAWERS.keys())

_UNKNOWN_ICON_KEYS: set[str] = set()


def _log_unknown_icon(key: str) -> None:
    if key not in _UNKNOWN_ICON_KEYS:
        _UNKNOWN_ICON_KEYS.add(key)
        warnings.warn("Unknown icon key: {!r}".format(key), stacklevel=3)


def normalize_icon_key(value: str | None, fallback: str = "patada") -> str:
    if value and value in VALID_ICON_KEYS:
        return value
    if value:
        _log_unknown_icon(value)
    return fallback


# ── Libraries for selectors ──────────────────────────────────────────────────

MARTIAL_ART_ICON_LIBRARY: list[dict[str, str]] = [
    {"key": "muay-thai", "label": "Muay Thai", "category": "Combate"},
    {"key": "muay-thai-1", "label": "Muay Thai 1", "category": "Combate"},
    {"key": "muay-thai-2", "label": "Muay Thai 2", "category": "Combate"},
    {"key": "muay-thai-3", "label": "Muay Thai 3", "category": "Combate"},
    {"key": "muay-thai-4", "label": "Muay Thai 4", "category": "Combate"},
    {"key": "combate-fight", "label": "Combate", "category": "Combate"},
    {"key": "patada", "label": "Patada", "category": "Combate"},
    {"key": "golpe-de-frente", "label": "Golpe de frente", "category": "Combate"},
    {"key": "golpe-hacia-arriba", "label": "Golpe hacia arriba", "category": "Combate"},
    {"key": "guantes-de-boxeo", "label": "Guantes de boxeo", "category": "Combate"},
    {"key": "katanas", "label": "Katanas cruzadas", "category": "Armas"},
    {"key": "meditacion", "label": "Meditacion", "category": "Acondicionamiento"},
    {"key": "pesos", "label": "Pesos", "category": "Acondicionamiento"},
    {"key": "treinamento", "label": "Treinamiento", "category": "Entrenamiento"},
    {"key": "telefone", "label": "Telefone", "category": "Utilidades"},
    {"key": "boxe", "label": "Boxe", "category": "Combate"},
    {"key": "boxer", "label": "Boxeador", "category": "Combate"},
    {"key": "cinto", "label": "Cinto", "category": "Progresion"},
    {"key": "definicoes", "label": "Definiciones", "category": "Acondicionamiento"},
    {"key": "jiu-jitsu", "label": "Jiu-Jitsu", "category": "Grappling"},
    {"key": "judo", "label": "Judo", "category": "Grappling"},
    {"key": "judo1", "label": "Judo 2", "category": "Grappling"},
    {"key": "karate1", "label": "Karate", "category": "Artes marciales"},
    {"key": "karate2", "label": "Karate 2", "category": "Artes marciales"},
    {"key": "karate-nuevo", "label": "Karate 4", "category": "Artes marciales"},
    {"key": "kickboxing-nuevo", "label": "Kickboxing 2", "category": "Combate"},
    {"key": "judo-olimpico", "label": "Judo Olimpico", "category": "Grappling"},
    {"key": "ejercicio", "label": "Ejercicio", "category": "Acondicionamiento"},
    {"key": "extendido", "label": "Extendido", "category": "Acondicionamiento"},
    {"key": "hacer-subir", "label": "Hacer subir", "category": "Acondicionamiento"},
    {"key": "luta-livre", "label": "Luta Livre", "category": "Grappling"},
    {"key": "lutar", "label": "Lutar", "category": "Combate"},
    {"key": "mma-nuevo", "label": "MMA Nuevo", "category": "Combate"},
    {"key": "mma-nuevo-2", "label": "MMA Nuevo 2", "category": "Combate"},
    {"key": "pilates", "label": "Pilates", "category": "Acondicionamiento"},
    {"key": "pilates-2", "label": "Pilates 2", "category": "Acondicionamiento"},
    {"key": "rutina-de-ejercicio", "label": "Rutina de ejercicio", "category": "Acondicionamiento"},
    {"key": "treinamento-em-artes-marciais", "label": "Treinamiento en artes marciales", "category": "Entrenamiento"},
]

SYSTEM_ICON_LIBRARY: list[dict[str, str]] = [
    {"key": "agregar-usuario", "label": "Agregar usuario", "category": "Sistema"},
    {"key": "ajustes-deslizadores", "label": "Ajustes deslizadores", "category": "Sistema"},
    {"key": "aplicaciones", "label": "Aplicaciones", "category": "Sistema"},
    {"key": "basura", "label": "Basura", "category": "Sistema"},
    {"key": "busqueda", "label": "Busqueda", "category": "Sistema"},
    {"key": "cruz", "label": "Cruz", "category": "Sistema"},
    {"key": "diseno-fluido", "label": "Diseno fluido", "category": "Sistema"},
    {"key": "energia", "label": "Energia", "category": "Sistema"},
    {"key": "estadisticas", "label": "Estadisticas", "category": "Sistema"},
    {"key": "hogar", "label": "Hogar", "category": "Sistema"},
    {"key": "lapiz", "label": "Lapiz", "category": "Sistema"},
    {"key": "marcador-de-mapa", "label": "Marcador de mapa", "category": "Sistema"},
    {"key": "marcador", "label": "Marcador", "category": "Sistema"},
    {"key": "reloj", "label": "Reloj", "category": "Sistema"},
    {"key": "salir-alt", "label": "Salir", "category": "Sistema"},
    {"key": "sobre", "label": "Sobre", "category": "Sistema"},
    {"key": "usuario", "label": "Usuario", "category": "Sistema"},
    {"key": "usuarios-alt", "label": "Usuarios", "category": "Sistema"},
    {"key": "comentario-info", "label": "Comentario info", "category": "Sistema"},
    {"key": "paleta", "label": "Paleta", "category": "Sistema"},
    {"key": "administracion", "label": "Administracion", "category": "Sistema"},
    {"key": "ajustes", "label": "Ajustes", "category": "Sistema"},
    {"key": "cartera", "label": "Cartera", "category": "Sistema"},
    {"key": "clases-eventos", "label": "Clases y eventos", "category": "Sistema"},
    {"key": "configuracion", "label": "Configuracion", "category": "Sistema"},
    {"key": "cuentas-por-cobrar", "label": "Cuentas por cobrar", "category": "Sistema"},
    {"key": "egresos", "label": "Egresos", "category": "Sistema"},
    {"key": "eventos", "label": "Eventos", "category": "Sistema"},
    {"key": "ingresos", "label": "Ingresos", "category": "Sistema"},
    {"key": "insignia", "label": "Insignia", "category": "Sistema"},
    {"key": "instructores", "label": "Instructores", "category": "Sistema"},
    {"key": "inventario", "label": "Inventario", "category": "Sistema"},
]

APP_ICON_LIBRARY: list[dict[str, str]] = list(MARTIAL_ART_ICON_LIBRARY)

ICON_CATEGORIES: dict[str, str] = {
    "Combate": "Iconos de artes marciales de combate",
    "Grappling": "Iconos de artes marciales de grappling",
    "Artes marciales": "Iconos generales de artes marciales",
    "Acondicionamiento": "Iconos de ejercicios y acondicionamiento",
    "Entrenamiento": "Iconos de entrenamiento",
    "Armas": "Iconos de armas tradicionales",
    "Utilidades": "Iconos de utilidades generales",
    "Progresion": "Iconos de progresion y graduacion",
}


# ── Normalizers ──────────────────────────────────────────────────────────────


def normalize_martial_art_icon(value: str | None, name: str = "") -> str:
    if value and value not in LEGACY_EMOJI_TO_ICON and ord(value[0]) < 0x1F000:
        if value in ICON_DRAWERS:
            return value
    if value and value in LEGACY_EMOJI_TO_ICON:
        return LEGACY_EMOJI_TO_ICON[value]
    if name:
        n = name.strip().lower()
        if "muay" in n or "thai" in n:
            return "muay-thai"
        if "combate" in n or "fight" in n or "pelea" in n:
            return "combate-fight"
        if "patada" in n or "kick" in n:
            return "patada"
        if "golpe" in n and "frente" in n:
            return "golpe-de-frente"
        if "golpe" in n and ("arriba" in n or "up" in n):
            return "golpe-hacia-arriba"
        if "golpe" in n:
            return "golpe-de-frente"
        if "guante" in n or "boxeo" in n or "boxing" in n:
            return "guantes-de-boxeo"
        if "katana" in n or "espada" in n:
            return "katanas"
        if "medita" in n or "mindfulness" in n:
            return "meditacion"
        if "peso" in n or "weight" in n or "fuerza" in n:
            return "pesos"
        if "treinamento" in n or "entrenamiento" in n or "training" in n:
            return "treinamento"
        if "tele" in n or "phone" in n or "fono" in n:
            return "telefone"
        if "box" in n:
            return "boxe"
        if "jiu" in n or "bjj" in n:
            return "jiu-jitsu"
        if "judo" in n:
            return "judo"
        if "karate" in n or "kata" in n:
            return "karate1"
        if "kick" in n and "box" in n:
            return "kickboxing-nuevo"
        if "olimpico" in n or "olympic" in n:
            return "judo-olimpico"
        if "cinto" in n or "belt" in n or "graduacion" in n:
            return "cinto"
        if "definicion" in n or "definition" in n:
            return "definicoes"
    return "patada"


# ── SVG rendering engine ─────────────────────────────────────────────────────


def render_icon_pixmap(icon_key: str, size: int = 24, color: str = "#9CA3AF") -> QPixmap:
    """Render an icon to a QPixmap using SVG files with dynamic color.

    The SVG uses ``currentColor`` placeholders which are replaced with the
    target *color* before rendering -- no QPainter composition needed.
    """
    key = normalize_icon_key(icon_key)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    renderer = _recolor_svg_bytes(key, color)
    if renderer is None:
        return pixmap

    painter = QPainter(pixmap)
    if not painter.isActive():
        return pixmap
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    return pixmap


# ── Painting engine (backward compat) ────────────────────────────────────────


class VectorIconPainter:
    """SVG-based icon painting engine (drop-in replacement)."""

    def __init__(self):
        pass

    def register(self, key: str, painter_fn: Callable | None = None) -> None:
        ICON_DRAWERS[key] = None

    def paint(self, painter: QPainter, rect: QRectF, color: QColor, icon_key: str) -> None:
        key = normalize_icon_key(icon_key)
        renderer = _recolor_svg_bytes(key, color.name())
        if renderer is None:
            return
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        renderer.render(painter, QRectF(rect))
        painter.restore()

    def paint_icon(self, painter: QPainter, icon_key: str, color: QColor, size: int | float | None = None) -> None:
        if size is not None:
            rect = QRectF(0, 0, size, size)
        else:
            rect = QRectF(painter.viewport())
        self.paint(painter, rect, color, icon_key)

    @staticmethod
    def draw_at(icon_key: str, painter: QPainter, rect: QRectF, color: QColor) -> None:
        _DEFAULT_PAINTER.paint(painter, rect, color, icon_key)


_DEFAULT_PAINTER = VectorIconPainter()
ICON_PAINTER = _DEFAULT_PAINTER


# ── Public widgets ───────────────────────────────────────────────────────────


class AppIcon(QWidget):
    """SVG-based icon widget with dynamic color support."""

    def __init__(self, icon_key: str = "patada", size: int = 24, color: str = "#9CA3AF", parent=None):
        super().__init__(parent)
        self._icon_key = normalize_icon_key(icon_key)
        self._color = color
        self.setFixedSize(size, size)

    def set_icon(self, icon_key: str) -> None:
        self._icon_key = normalize_icon_key(icon_key)
        self.update()

    def set_color(self, color: str) -> None:
        self._color = color
        self.update()

    def set_size(self, size: int) -> None:
        self.setFixedSize(size, size)

    def icon_key(self) -> str:
        return self._icon_key

    def color(self) -> str:
        return self._color

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        if not painter.isActive():
            return
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect())
        color = QColor(self._color)
        key = normalize_icon_key(self._icon_key)
        _DEFAULT_PAINTER.paint(painter, rect, color, key)


class MartialArtIcon(AppIcon):
    pass


# ── Search aliases ────────────────────────────────────────────────────────────

ICON_SEARCH_ALIASES: dict[str, set[str]] = {
    "muay-thai": {"muay thai", "thai boxing", "artes marciales tailandesas"},
    "combate-fight": {"combate", "pelea", "sparring", "lucha"},
    "patada": {"patada", "kick", "pierna"},
    "golpe-de-frente": {"golpe", "frente", "straight punch", "puno"},
    "golpe-hacia-arriba": {"golpe arriba", "uppercut", "upper"},
    "guantes-de-boxeo": {"guantes", "boxeo", "boxing gloves"},
    "katanas": {"katana", "espada", "katanas cruzadas", "swords"},
    "meditacion": {"meditacion", "mindfulness", "calma", "zen"},
    "pesos": {"pesos", "pesas", "fuerza", "strength", "weights"},
    "treinamento": {"treinamiento", "entrenamiento", "training"},
    "telefone": {"telefone", "telefono", "phone", "contacto"},
    "boxe": {"boxe", "boxeo", "boxing"},
    "boxer": {"boxer", "boxeador", "peleador"},
    "cinto": {"cinto", "belt", "cinturon", "graduacion"},
    "definicoes": {"definiciones", "definition", "musculacion"},
    "jiu-jitsu": {"jiu-jitsu", "bjj", "grappling", "submission"},
    "judo": {"judo", "grappling", "throw"},
    "judo1": {"judo 2", "judo throw"},
    "karate1": {"karate", "kata", "artes marciales"},
    "karate2": {"karate 2", "karate kata"},
    "karate-nuevo": {"karate 4", "karate nuevo"},
    "kickboxing-nuevo": {"kickboxing 2", "kick boxing 2"},
    "judo-olimpico": {"judo olimpico", "judo olympic", "judo throw olimpico"},
    "ejercicio": {"ejercicio", "exercise", "entrenamiento"},
    "extendido": {"extendido", "stretch", "estiramiento"},
    "hacer-subir": {"hacer subir", "pull up", "dominada"},
    "luta-livre": {"luta livre", "lucha libre", "grappling libre"},
    "lutar": {"lutar", "lucha", "fight", "pelear"},
    "mma-nuevo": {"mma", "mixed martial arts", "artes marciales mixtas"},
    "mma-nuevo-2": {"mma 2", "mixed martial arts 2"},
    "pilates": {"pilates", "pilates exercises"},
    "pilates-2": {"pilates 2", "pilates exercises 2"},
    "rutina-de-ejercicio": {"rutina", "routine", "rutina de ejercicio", "workout"},
    "treinamento-em-artes-marciais": {"treinamiento artes marciales", "martial arts training"},
    # System icons
    "agregar-usuario": {"agregar usuario", "add user", "nuevo usuario"},
    "ajustes-deslizadores": {"ajustes", "sliders", "settings", "configuracion"},
    "aplicaciones": {"aplicaciones", "apps", "grid"},
    "basura": {"basura", "trash", "delete", "eliminar", "borrar"},
    "busqueda": {"busqueda", "search", "buscar", "lupa"},
    "cruz": {"cruz", "close", "cerrar", "cancel"},
    "diseno-fluido": {"diseno fluido", "fluid", "flow"},
    "energia": {"energia", "energy", "power", "fuerza"},
    "estadisticas": {"estadisticas", "stats", "chart", "grafico"},
    "hogar": {"hogar", "home", "inicio"},
    "lapiz": {"lapiz", "edit", "editar", "pencil"},
    "marcador-de-mapa": {"marcador mapa", "map pin", "ubicacion"},
    "marcador": {"marcador", "bookmark", "favorito"},
    "reloj": {"reloj", "clock", "tiempo", "hora"},
    "salir-alt": {"salir", "logout", "exit"},
    "sobre": {"sobre", "mail", "correo", "email"},
    "usuario": {"usuario", "user", "perfil"},
    "usuarios-alt": {"usuarios", "users", "people", "personas"},
    "comentario-info": {"comentario", "comment", "info", "informacion", "mensaje"},
    "paleta": {"paleta", "palette", "color", "colores", "tema"},
}


# ── Search helpers ────────────────────────────────────────────────────────────


def _normalize_search_text(value: str) -> str:
    """Normalize text for accent-insensitive, case-insensitive search."""
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("-", " ")
    text = " ".join(text.split())
    return text


def search_icon_library(
    query: str,
    library: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Search the icon library by key, label, category, keywords, and aliases.

    Returns entries matching *query* (case-insensitive, accent-insensitive).
    Empty query returns the full library in original order.
    """
    if library is None:
        library = APP_ICON_LIBRARY

    q = _normalize_search_text(query)
    if not q:
        return list(library)

    results: list[dict[str, str]] = []
    for entry in library:
        key = entry.get("key", "")
        label = entry.get("label", "")
        category = entry.get("category", "")
        keywords = entry.get("keywords", "")
        aliases = " ".join(ICON_SEARCH_ALIASES.get(key, set()))

        hay = " ".join([key, label, category, keywords, aliases])
        if q in _normalize_search_text(hay):
            results.append(entry)

    return results
