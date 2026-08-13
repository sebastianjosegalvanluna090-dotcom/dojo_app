"""
core/app_logger.py
Persistent logging system for DOJO_ADMIN.

Logs are stored in:
  %LOCALAPPDATA%\\SenshiFightAcademy\\DojoAdmin\\logs

- RotatingFileHandler: 5 MB x 5 copies
- Auto-cleanup of files older than 30 days
- Global exception hook integration
- Safe console duplication (no crash if stdout is None)
"""

import logging
import os
import sys
import traceback
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler


APP_NAME = "DojoAdmin"
COMPANY_NAME = "SenshiFightAcademy"


def resource_path(relative_path):
    """Resolve resource path for both source and PyInstaller frozen builds."""
    if getattr(sys, "frozen", False):
        base_path = getattr(
            sys, "_MEIPASS", os.path.dirname(sys.executable)
        )
    else:
        base_path = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    return os.path.join(base_path, relative_path)


def get_app_data_directory():
    base = os.getenv("LOCALAPPDATA")

    if not base:
        base = os.path.expanduser("~")

    app_dir = os.path.join(base, COMPANY_NAME, APP_NAME)
    os.makedirs(app_dir, exist_ok=True)
    return app_dir


def get_log_directory():
    log_dir = os.path.join(get_app_data_directory(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def cleanup_old_logs(days=30):
    log_dir = get_log_directory()
    cutoff = datetime.now() - timedelta(days=days)

    for file_name in os.listdir(log_dir):
        file_path = os.path.join(log_dir, file_name)

        if not os.path.isfile(file_path):
            continue

        try:
            modified = datetime.fromtimestamp(
                os.path.getmtime(file_path)
            )
            if modified < cutoff:
                os.remove(file_path)
        except Exception:
            pass


def get_logger(name="dojo_admin"):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    log_path = os.path.join(
        get_log_directory(),
        f"dojo_admin_{datetime.now():%Y-%m-%d}.log",
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(threadName)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if sys.stdout is not None:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger.propagate = False
    return logger


def install_global_exception_logging():
    logger = get_logger("global")

    original_hook = sys.excepthook

    def exception_hook(exc_type, exc_value, exc_traceback):
        if exc_type is KeyboardInterrupt:
            original_hook(exc_type, exc_value, exc_traceback)
            return

        logger.critical(
            "UNCAUGHT PYTHON EXCEPTION",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

        if sys.stderr is not None:
            traceback.print_exception(
                exc_type, exc_value, exc_traceback
            )

    sys.excepthook = exception_hook
    cleanup_old_logs()

    logger.info("=" * 70)
    logger.info("DOJO ADMIN iniciado")
    logger.info("Python: %s", sys.version)
    logger.info("Executable: %s", sys.executable)
    logger.info("Frozen: %s", bool(getattr(sys, "frozen", False)))
    logger.info("=" * 70)
