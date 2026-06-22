"""
config/settings.py
Gestiona la configuración persistente en settings.json.
"""

import json
import os

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_SETTINGS_PATH = os.path.join(_BASE_DIR, "settings.json")

_DEFAULTS = {
    "language": "es",
}


def load() -> dict:
    """Carga settings.json. Si no existe o está corrupto, devuelve defaults."""
    if not os.path.exists(_SETTINGS_PATH):
        return dict(_DEFAULTS)
    try:
        with open(_SETTINGS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        # Mezclar con defaults para claves faltantes
        merged = dict(_DEFAULTS)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(_DEFAULTS)


def save(data: dict):
    """Guarda el diccionario en settings.json."""
    current = load()
    current.update(data)
    try:
        with open(_SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"[settings] Error saving: {e}")


def get(key: str, default=None):
    """Lee un valor individual del archivo."""
    return load().get(key, default)


def set_value(key: str, value):
    """Escribe un valor individual."""
    save({key: value})