# ─── EVENT_MEDIA_SERVICE ────────────────────────────────────────────

import os
import uuid
import shutil
from pathlib import Path

from core.debug import debug_log
from core.app_logger import resource_path


_ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
_MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def _get_media_base() -> Path:
    """Return writable media base directory."""
    local = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    base = Path(local) / "SenshiFightAcademy" / "DojoAdmin" / "media" / "events"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _validate_image(filepath: str) -> tuple[bool, str]:
    """Validate file type and size. Returns (ok, error_message)."""
    ext = Path(filepath).suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        return False, f"Tipo de archivo no permitido: {ext}"

    try:
        size = os.path.getsize(filepath)
    except OSError:
        return False, "No se pudo leer el archivo."

    if size > _MAX_SIZE_BYTES:
        mb = size / (1024 * 1024)
        return False, f"Archivo demasiado grande ({mb:.1f} MB). Máximo 10 MB."

    # Reject executables renamed to image extensions
    if size < 200:
        try:
            with open(filepath, "rb") as f:
                header = f.read(4)
            # PE header
            if header[:2] == b"MZ":
                return False, "Archivo ejecutable detectado."
            # ELF header
            if header[:4] == b"\x7fELF":
                return False, "Archivo ejecutable detectado."
        except Exception:
            pass

    return True, ""


class EventMediaService:
    """Handles cover image storage for events."""

    def save_cover(self, source_path: str) -> str | None:
        """Copy an image to media/events. Returns absolute path or None."""
        ok, err = _validate_image(source_path)
        if not ok:
            debug_log(f"[EventMediaService] Validación fallida: {err}")
            return None

        try:
            ext = Path(source_path).suffix.lower()
            filename = f"{uuid.uuid4().hex}{ext}"
            dest = _get_media_base() / filename
            shutil.copy2(source_path, str(dest))
            debug_log(f"[EventMediaService] Portada guardada: {dest}")
            return str(dest)
        except Exception as e:
            debug_log(f"[EventMediaService] Error guardando imagen: {e}")
            return None

    def delete_cover(self, filepath: str) -> bool:
        """Delete a cover image file."""
        if not filepath:
            return False
        try:
            p = Path(filepath)
            if p.exists() and "media/events" in str(p):
                p.unlink()
                debug_log(f"[EventMediaService] Portada eliminada: {filepath}")
                return True
        except Exception as e:
            debug_log(f"[EventMediaService] Error eliminando imagen: {e}")
        return False

    def get_placeholder_path(self) -> str:
        """Return path to placeholder cover image."""
        return str(resource_path("assets/Icons/dojo_admin.ico"))
