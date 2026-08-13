"""
Compat layer para la vista previa del recibo.

IMPORTANTE:
- La plantilla visual real y editable por el usuario vive en:
  assets/templates/receipt_template.py
- Este archivo NO redefine el diseño del recibo.
- Este archivo solo adapta esa plantilla para que funcione dentro de IncomeDialog.
- Tambien asegura que el logo se inyecte en data["logo_path"].
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QScrollArea, QVBoxLayout, QWidget

from core.debug import debug_log


# ----------------------------------------------------------------------
# RUTAS
# ----------------------------------------------------------------------

def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _template_path() -> Path:
    return _project_root() / "assets" / "templates" / "receipt_template.py"


def _fallback_logo_path() -> str:
    root = _project_root()
    candidates = [
        root / "assets" / "logo.png",
        root / "assets" / "logo.jpg",
        root / "assets" / "images" / "logo.png",
        root / "assets" / "images" / "logo.jpg",
        root / "assets" / "senshi_logo.png",
        root / "assets" / "logo_senshi.png",
    ]

    for path in candidates:
        if path.exists() and path.is_file():
            return str(path)

    explicit = Path(
        r"C:\Users\Sebastian Galvan\Documents\DOJO_ADMIN\Dojo_admin\assets\logo.png"
    )
    if explicit.exists() and explicit.is_file():
        return str(explicit)

    return ""


def _with_logo(data: dict | None) -> dict:
    result = dict(data or {})
    if not result.get("logo_path"):
        logo_path = _fallback_logo_path()
        if logo_path:
            result["logo_path"] = logo_path
    return result


def _debug_dir() -> Path:
    d = _project_root() / "storage" / "debug"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ----------------------------------------------------------------------
# CARGA DINAMICA DE LA PLANTILLA ACTUAL
# ----------------------------------------------------------------------

def _load_template_module():
    path = _template_path()
    if not path.exists():
        raise FileNotFoundError(f"No existe la plantilla de recibo: {path}")

    spec = importlib.util.spec_from_file_location("dojo_receipt_template", str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar la plantilla: {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_TEMPLATE_MODULE = _load_template_module()
_TEMPLATE_RECEIPT_WIDGET = _TEMPLATE_MODULE.ReceiptWidget
_TEMPLATE_CARD_WIDTH = int(getattr(_TEMPLATE_MODULE, "CARD_WIDTH", 720))


class ReceiptWidget(_TEMPLATE_RECEIPT_WIDGET):
    """
    Wrapper compatible.

    IncomeDialog/ReceiptPreviewArea pueden seguir importando ReceiptWidget desde
    este archivo, pero el diseno real viene de assets/templates/receipt_template.py.
    """

    def __init__(self, data, parent=None, card_width=None, compact=False):
        super().__init__(_with_logo(data), parent=parent)


class ReceiptPreviewArea(QScrollArea):
    """
    Area de vista previa que usa la plantilla actual del usuario.

    La plantilla se instancia, se captura con grab(), se recorta para eliminar
    espacio blanco interno, se escala al ancho disponible y se centra.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        debug_log("[PreviewFix] ReceiptPreviewArea INIT FROM views/finances/income/receipt_widget.py")

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setStyleSheet("""
            QScrollArea {
                background-color: #101010;
                border: none;
                border-radius: 14px;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #101010;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #3A3A3A;
                border-radius: 4px;
                min-height: 24px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
                border: none;
            }
        """)

        self._container = QWidget()
        self._container.setStyleSheet("background-color:#101010; border:none;")

        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(12, 10, 12, 10)
        self._layout.setSpacing(0)
        self._layout.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )

        self._preview_label = QLabel("Generando vista previa...")
        self._preview_label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        self._preview_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #888888;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        self._layout.addWidget(
            self._preview_label,
            0,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
        )
        self._layout.addStretch()
        self.setWidget(self._container)

        self._last_data = None
        self._render_source_widget = None
        self._last_good_pixmap = QPixmap()
        self._rendering = False

    def set_receipt_data(self, data: dict):
        self._last_data = _with_logo(data)
        self._last_good_pixmap = QPixmap()
        QTimer.singleShot(0, self._render_preview)

    # ------------------------------------------------------------------
    # PARTE 3 — Trim empty borders
    # ------------------------------------------------------------------

    def _trim_empty_borders(self, pixmap: QPixmap) -> QPixmap:
        """
        Recorte seguro SOLO vertical.

        No recorta izquierda ni derecha para evitar cortar el header,
        la card roja, sombras o contenido lateral.

        Solo elimina exceso vertical si existe.
        """
        if pixmap.isNull():
            return pixmap

        img = pixmap.toImage()
        w = img.width()
        h = img.height()

        if w <= 0 or h <= 0:
            return pixmap

        def is_empty_pixel(x, y):
            c = img.pixelColor(x, y)
            return (
                c.alpha() == 0
                or (
                    c.red() >= 248
                    and c.green() >= 248
                    and c.blue() >= 248
                )
            )

        top = 0
        for y in range(h):
            non_empty_count = 0
            for x in range(w):
                if not is_empty_pixel(x, y):
                    non_empty_count += 1
                    if non_empty_count > 8:
                        break
            if non_empty_count > 8:
                top = y
                break

        bottom = h - 1
        for y in range(h - 1, -1, -1):
            non_empty_count = 0
            for x in range(w):
                if not is_empty_pixel(x, y):
                    non_empty_count += 1
                    if non_empty_count > 8:
                        break
            if non_empty_count > 8:
                bottom = y
                break

        if bottom <= top:
            return pixmap

        margin_y = 24
        top = max(0, top - margin_y)
        bottom = min(h - 1, bottom + margin_y)

        debug_log(
            f"[PreviewFix] vertical_crop top={top}, bottom={bottom}, original={w}x{h}"
        )

        return pixmap.copy(0, top, w, bottom - top + 1)

    # ------------------------------------------------------------------
    # Main render flow
    # ------------------------------------------------------------------

    def _render_preview(self):
        debug_log("[PreviewFix] USING NEW PREVIEW RENDER PIPELINE")

        if getattr(self, "_rendering", False):
            return

        data = self._last_data
        if not data:
            return

        self._rendering = True

        try:
            source = ReceiptWidget(data)
            source.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
            source.show()

            if source.layout():
                source.layout().invalidate()
                source.layout().activate()

            app = QApplication.instance()
            if app:
                app.processEvents()

            source.adjustSize()

            size = source.sizeHint()
            if not size.isValid() or size.width() <= 0 or size.height() <= 0:
                size = source.size()
            if not size.isValid() or size.width() <= 0 or size.height() <= 0:
                size = source.minimumSizeHint()

            source.resize(size)

            if source.layout():
                source.layout().activate()

            if app:
                app.processEvents()

            pixmap = source.grab()

            if pixmap.isNull():
                pixmap = QPixmap(source.size())
                pixmap.fill(Qt.GlobalColor.transparent)
                source.render(pixmap)

            if pixmap.isNull() or pixmap.width() <= 0 or pixmap.height() <= 0:
                raise RuntimeError(
                    f"Pixmap invalido. source.size={source.size()}, "
                    f"sizeHint={source.sizeHint()}"
                )

            debug_log(f"[PreviewFix] source={source.width()}x{source.height()}")

            pixmap_original = pixmap
            debug_log(
                f"[PreviewFix] original={pixmap_original.width()}x{pixmap_original.height()}"
            )

            # PARTE 2: save debug original
            try:
                pixmap_original.save(str(_debug_dir() / "preview_original.png"))
            except Exception:
                pass

            # PARTE 3: trim empty borders
            cropped = self._trim_empty_borders(pixmap_original)


            debug_log(
                f"[PreviewFix] cropped={cropped.width()}x{cropped.height()}"
            )

            # PARTE 2: save debug cropped
            try:
                cropped.save(str(_debug_dir() / "preview_cropped.png"))
            except Exception:
                pass

            # PARTE 7: white bg only = cropped size (never viewport)
            pixmap = cropped

            # PARTE 5 + 6: scale conservatively — max 12% upscale, never overflow viewport.
            viewport_width = self.viewport().width()
            if viewport_width <= 0:
                viewport_width = 560

            safe_max_width = max(360, viewport_width - 24)

            # Regla:
            # - Si el pixmap es más ancho que el área, reducirlo.
            # - Si el pixmap ya cabe, NO agrandarlo.
            # Esto evita borrosidad.
            if pixmap.width() > safe_max_width:
                pixmap = pixmap.scaledToWidth(
                    safe_max_width,
                    Qt.TransformationMode.SmoothTransformation,
                )

            # PARTE 2: save debug final
            try:
                pixmap.save(str(_debug_dir() / "preview_final.png"))
            except Exception:
                pass

            debug_log(
                f"[PreviewFix] final={pixmap.width()}x{pixmap.height()}"
            )

            # PARTE 6: center label
            self._preview_label.clear()
            self._preview_label.setPixmap(pixmap)
            self._preview_label.setText("")
            self._preview_label.setFixedWidth(pixmap.width())
            self._preview_label.setFixedHeight(pixmap.height())
            self._preview_label.adjustSize()

            if self._container.layout():
                self._container.layout().invalidate()
                self._container.layout().activate()

            self._last_good_pixmap = pixmap

            self._render_source_widget = source
            QTimer.singleShot(0, self._release_source_widget)

        except Exception as e:
            debug_log(f"[PreviewFix] error: {e}")
            if (
                hasattr(self, "_last_good_pixmap")
                and not self._last_good_pixmap.isNull()
            ):
                self._preview_label.setPixmap(self._last_good_pixmap)
                self._preview_label.setText("")
            else:
                self._preview_label.setPixmap(QPixmap())
                self._preview_label.setText(
                    f"No se pudo cargar la plantilla del recibo.\n{e}"
                )

        finally:
            self._rendering = False

    def _release_source_widget(self):
        if self._render_source_widget is not None:
            try:
                self._render_source_widget.deleteLater()
            except Exception:
                pass
            self._render_source_widget = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._last_data:
            QTimer.singleShot(0, self._render_preview)
