"""
Global receipt preview renderer.

Uses a hidden, persistent QWebEngineView OUTSIDE of any dialog
to render receipt HTML → QPixmap. This avoids the crash caused
by QWebEngineView living inside IncomeDialog's widget tree.
"""

import os
from pathlib import Path

from PyQt6.QtCore import QObject, QTimer, QUrl, pyqtSignal
from PyQt6.QtGui import QPixmap

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False

from core.debug import debug_log


class ReceiptPreviewRenderer(QObject):
    rendered = pyqtSignal(QPixmap)
    failed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = None
        self._pending_html = None
        self._ready = True

        if WEB_ENGINE_AVAILABLE:
            self.view = QWebEngineView()
            self.view.resize(700, 980)
            self.view.hide()
            self.view.loadFinished.connect(self._on_load_finished)
            debug_log(f"[PREVIEW_RENDERER] QWebEngineView created (hidden, no parent dialog)")

    def render_html(self, html, width=700, height=980):
        if self.view is None:
            self.failed.emit("QWebEngineView no disponible")
            return

        if not self._ready:
            self._pending_html = (html, width, height)
            return

        self._ready = False
        self.view.resize(width, height)

        base_dir = Path(__file__).resolve().parents[1]
        self.view.setHtml(html, QUrl.fromLocalFile(str(base_dir) + "/"))
        debug_log(f"[PREVIEW_RENDERER] render_html called, size={width}x{height}")

    def _on_load_finished(self, ok):
        if not ok:
            self._ready = True
            self.failed.emit("No se pudo cargar el recibo HTML.")
            return

        QTimer.singleShot(300, self._grab)

    def _grab(self):
        try:
            pixmap = self.view.grab()
            self._ready = True
            debug_log(f"[PREVIEW_RENDERER] grab OK, size={pixmap.width()}x{pixmap.height()}")
            self.rendered.emit(pixmap)

            if self._pending_html:
                html, w, h = self._pending_html
                self._pending_html = None
                self.render_html(html, w, h)
        except Exception as e:
            self._ready = True
            self.failed.emit(str(e))


_RECEIPT_PREVIEW_RENDERER = None


def get_receipt_preview_renderer():
    global _RECEIPT_PREVIEW_RENDERER
    if _RECEIPT_PREVIEW_RENDERER is None:
        _RECEIPT_PREVIEW_RENDERER = ReceiptPreviewRenderer()
    return _RECEIPT_PREVIEW_RENDERER
