"""
core/i18n.py
Motor de internacionalización con señal Qt para cambio en caliente.

Uso:
    from core.i18n import tr, i18n
    label.setText(tr("students"))
    i18n.language_changed.connect(my_callback)
    i18n.set_language("en")
"""

import json
import os
from PyQt6.QtCore import QObject, pyqtSignal

# Ruta a la carpeta locales (relativa a este archivo → ../locales)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOCALES_DIR = os.path.join(_BASE_DIR, "locales")

SUPPORTED_LANGUAGES = {
    "es": "Español",
    "en": "English",
    "fr": "Français",
    "ja": "日本語",
}


class I18n(QObject):
    """Singleton que gestiona el idioma activo y emite señales al cambiar."""

    language_changed = pyqtSignal(str)  # emite el código del nuevo idioma

    def __init__(self):
        super().__init__()
        self._lang = "es"
        self._strings: dict = {}
        self._load("es")

    # ── Carga ─────────────────────────────────────────────────────────
    def _load(self, lang: str):
        path = os.path.join(_LOCALES_DIR, f"{lang}.json")
        if not os.path.exists(path):
            print(f"[i18n] Locale file not found: {path}")
            return
        with open(path, encoding="utf-8") as f:
            self._strings = json.load(f)
        self._lang = lang

    # ── API pública ───────────────────────────────────────────────────
    def set_language(self, lang: str):
        """Cambia el idioma y notifica a todos los oyentes."""
        if lang not in SUPPORTED_LANGUAGES:
            print(f"[i18n] Unsupported language: {lang}")
            return
        if lang == self._lang:
            return
        self._load(lang)
        self.language_changed.emit(lang)

    def get(self, key: str, **kwargs) -> str:
        """Devuelve el string traducido. Soporta format kwargs."""
        text = self._strings.get(key, key)  # fallback al key si no existe
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass
        return text

    @property
    def current(self) -> str:
        return self._lang

    @property
    def strings(self) -> dict:
        return self._strings


# Instancia global singleton
i18n = I18n()


def tr(key: str, **kwargs) -> str:
    """Shortcut global: tr('students') → 'Estudiantes' / 'Students' / etc."""
    return i18n.get(key, **kwargs)