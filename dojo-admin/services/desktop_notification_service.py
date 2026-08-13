"""
services/desktop_notification_service.py
Servicio completo de notificaciones de escritorio y system tray.

Responsabilidades:
- System tray con menú contextual completo
- Notificaciones de escritorio (show_info, show_warning, show_error)
- Notificaciones de clases (show_class_upcoming, show_class_started)
- Mostrar/ocultar ventana
- Silenciar notificaciones por tiempo determinado
- Soporte para AppUserModelID en Windows
- Preparado para migración futura a Windows Toast nativo
"""

import os
import ctypes

from PyQt6.QtWidgets import (
    QSystemTrayIcon,
    QMenu,
    QApplication,
)
from PyQt6.QtGui import QAction, QIcon, QPixmap, QPainter, QPen, QColor, QFont
from PyQt6.QtCore import QObject, QTimer, Qt

from config import settings as cfg
from core.app_logger import get_logger, get_log_directory, resource_path

logger = get_logger("desktop_notifications")


class DesktopNotificationService(QObject):
    """
    Servicio de notificaciones de escritorio y system tray.

    Expone:
        show_info(title, message)
        show_warning(title, message)
        show_error(title, message)
        show_class_upcoming(class_name, start_time, minutes_until)
        show_class_started(class_name, start_time)
        restore_window()
        hide_window()
        enable_notifications()
        disable_notifications()
        is_enabled() -> bool
        mute_for(hours)
        is_muted() -> bool
    """

    def __init__(self, main_window, icon_path=None):
        super().__init__()

        self.main_window = main_window

        self._notifications_enabled = cfg.get(
            "desktop_notifications", True
        )

        self._minimize_to_tray = cfg.get(
            "minimize_to_tray", True
        )

        self._sound_enabled = cfg.get(
            "notification_sound", True
        )

        self._mute_until = None

        self._native_toaster = None
        self._native_toast_available = False

        self.tray = QSystemTrayIcon(self)

        self.app_icon = self._load_icon(icon_path)
        if self.app_icon and not self.app_icon.isNull():
            self.tray.setIcon(self.app_icon)
            if QApplication.instance():
                QApplication.instance().setWindowIcon(self.app_icon)
            logger.info("Icono del System Tray establecido")
        else:
            logger.error(
                "El icono oficial de DOJO ADMIN es invalido: %s",
                icon_path,
            )

        self.tray.setToolTip("DOJO ADMIN")

        logger.info(
            "System Tray disponible: %s",
            QSystemTrayIcon.isSystemTrayAvailable(),
        )
        logger.info(
            "Mensajes del System Tray soportados: %s",
            QSystemTrayIcon.supportsMessages(),
        )
        logger.info(
            "Icono valido: %s",
            not self.app_icon.isNull(),
        )

        self._build_menu()

        self.tray.messageClicked.connect(
            self.restore_window
        )

        self.tray.activated.connect(self._on_tray_activated)

        self.tray.show()

        self._setup_native_toasts()

    def _load_icon(self, icon_path):
        """Carga el ícono desde la ruta dada, o usa el ícono de la app."""
        if icon_path:
            full_path = resource_path(icon_path)
            if os.path.exists(full_path):
                icon = QIcon(full_path)
                if not icon.isNull():
                    logger.info("Icono cargado: %s", full_path)
                    return icon
                logger.error(
                    "El archivo ICO existe pero QIcon no pudo cargarlo: %s",
                    full_path,
                )

        app_icon = QApplication.instance().windowIcon()
        if app_icon and not app_icon.isNull():
            return app_icon

        fallback = resource_path(
            os.path.join("assets", "Icons", "dojo_admin.ico")
        )

        if os.path.exists(fallback):
            icon = QIcon(fallback)
            if not icon.isNull():
                return icon

        logger.warning("Usando icono fallback (pixmap generado)")
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor("#C8102E"))
        p = QPainter(pixmap)
        p.setPen(QPen(QColor("white"), 2))
        p.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        p.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "DA")
        p.end()
        return QIcon(pixmap)

    def _setup_native_toasts(self):
        """Inicializa Windows Toast nativa si esta disponible."""
        if os.name != "nt":
            return

        try:
            from windows_toasts import WindowsToaster

            self._native_toaster = WindowsToaster("DOJO ADMIN")
            self._native_toast_available = True

            logger.info("Windows Toast nativa inicializada")

        except Exception:
            self._native_toast_available = False

            logger.exception(
                "No se pudo inicializar Windows Toast; "
                "se utilizara QSystemTrayIcon"
            )

        logger.info(
            "Toast nativa disponible: %s",
            self._native_toast_available,
        )

        if not self._native_toast_available:
            logger.warning(
                "Windows continuara mostrando el AppUserModelID. "
                "La identidad debe completarse mediante instalador "
                "y acceso directo del menu Inicio."
            )

    def _show_native_toast(self, title, message):
        """Muestra una Toast nativa de Windows. Retorna True si tuvo exito."""
        if not self._native_toast_available:
            return False

        try:
            from windows_toasts import Toast

            toast = Toast()
            toast.text_fields = [title, message]

            toast.on_activated = lambda _: QTimer.singleShot(
                0, self.restore_window
            )

            self._native_toaster.show_toast(toast)
            return True

        except Exception:
            logger.exception(
                "No se pudo mostrar Windows Toast nativa"
            )
            return False

    def _build_menu(self):
        """Construye el menú contextual del tray."""
        self.menu = QMenu()
        self.menu.setStyleSheet(f"""
            QMenu {{
                background-color: #1A1A1A;
                color: #F0F0F0;
                border: 1px solid #2A2A2A;
                border-radius: 8px;
                padding: 4px;
                font-size: 12px;
                font-family: 'Inter', 'Segoe UI';
            }}
            QMenu::item {{
                padding: 8px 24px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: #2A2A2A;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: #2A2A2A;
                margin: 4px 8px;
            }}
        """)

        self.action_open = QAction("Abrir DOJO ADMIN")
        self.action_open.triggered.connect(
            self.restore_window
        )

        self.action_view_classes = QAction("Ver clases de hoy")
        self.action_view_classes.triggered.connect(
            self._view_today_classes
        )

        self.action_mute = QAction("Silenciar 1 hora")
        self.action_mute.triggered.connect(
            lambda: self.mute_for(1)
        )

        self.action_toggle = QAction("Desactivar notificaciones")
        self.action_toggle.triggered.connect(
            self._toggle_notifications
        )

        self.action_exit = QAction("Salir")
        self.action_exit.triggered.connect(self._exit_from_tray)

        self.action_open_logs = QAction("Abrir carpeta de diagnósticos")
        self.action_open_logs.triggered.connect(self._open_logs)

        self.menu.addAction(self.action_open)
        self.menu.addSeparator()
        self.menu.addAction(self.action_view_classes)
        self.menu.addAction(self.action_mute)
        self.menu.addAction(self.action_toggle)
        self.menu.addSeparator()
        self.menu.addAction(self.action_open_logs)
        self.menu.addSeparator()
        self.menu.addAction(self.action_exit)

        self.tray.setContextMenu(self.menu)

        self._update_menu_state()

    def _update_menu_state(self):
        """Actualiza el texto de los items del menú según el estado."""
        if self._notifications_enabled:
            self.action_toggle.setText("Desactivar notificaciones")
        else:
            self.action_toggle.setText("Activar notificaciones")

        if self.is_muted():
            remaining = self._minutes_until_unmute()
            self.action_mute.setText(
                f"Silenciado ({remaining} min restantes)"
            )
            self.action_mute.setEnabled(False)
        else:
            self.action_mute.setText("Silenciar 1 hora")
            self.action_mute.setEnabled(True)

    def _on_tray_activated(self, reason):
        """Maneja clic en el ícono del tray."""
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
            QSystemTrayIcon.ActivationReason.MiddleClick,
        ):
            self.restore_window()

    def _view_today_classes(self):
        """Navega a la vista de clases y restaura la ventana."""
        self.restore_window()
        if hasattr(self.main_window, "open_classes_module"):
            self.main_window.open_classes_module()

    def _open_logs(self):
        """Abre la carpeta de logs en el explorador."""
        log_directory = get_log_directory()
        try:
            os.startfile(log_directory)
        except Exception:
            logger.exception(
                "No se pudo abrir la carpeta de logs: %s",
                log_directory,
            )

    def _toggle_notifications(self):
        """Alterna el estado de notificaciones."""
        if self._notifications_enabled:
            self.disable_notifications()
        else:
            self.enable_notifications()

    def _exit_from_tray(self):
        """Cierra realmente la aplicación desde el tray."""
        if hasattr(self.main_window, "class_notification_service"):
            self.main_window.class_notification_service.stop()

        self.tray.hide()
        self.main_window._force_exit = True
        self.main_window.close()

        from PyQt6.QtWidgets import QApplication
        QApplication.quit()

    # ── API pública ──────────────────────────────────────────────────

    def show_info(self, title, message):
        """Muestra una notificacion informativa."""
        if not self._should_show():
            return
        final_title = title.strip() if title else "DOJO ADMIN"
        self._show_desktop(final_title, message)

    def show_warning(self, title, message):
        """Muestra una notificacion de advertencia."""
        if not self._should_show():
            return
        final_title = title.strip() if title else "DOJO ADMIN"
        self._show_desktop(final_title, message)

    def show_error(self, title, message):
        """Muestra una notificacion de error."""
        if not self._should_show():
            return
        final_title = title.strip() if title else "DOJO ADMIN"
        self._show_desktop(final_title, message)

    def show_class_upcoming(self, class_name, start_time, minutes_until):
        """Notificacion: proxima clase."""
        if not self._should_show():
            return

        time_text = start_time
        if hasattr(start_time, "strftime"):
            time_text = start_time.strftime("%H:%M")

        if minutes_until == 1:
            when = "Comienza en 1 minuto."
        else:
            when = f"Comienza en {minutes_until} minutos."

        title = "DOJO ADMIN \u00b7 Proxima clase"
        message = (
            f"{class_name}\n"
            f"{when}\n"
            f"Hora: {time_text}"
        )

        self._show_desktop(title, message)

    def show_class_started(self, class_name, start_time):
        """Notificacion: clase iniciada."""
        if not self._should_show():
            return

        time_text = start_time
        if hasattr(start_time, "strftime"):
            time_text = start_time.strftime("%H:%M")

        title = "DOJO ADMIN \u00b7 Clase iniciada"
        message = (
            f"{class_name}\n"
            f"La clase acaba de comenzar.\n"
            f"Hora: {time_text}"
        )

        self._show_desktop(title, message)

    def show_event_upcoming(self, event_name, event_date, start_time, minutes_until):
        """Notificacion: proximo evento."""
        if not self._should_show():
            return

        time_text = start_time
        if hasattr(start_time, "strftime"):
            time_text = start_time.strftime("%H:%M")

        date_text = event_date
        if hasattr(event_date, "strftime"):
            date_text = event_date.strftime("%d/%m/%Y")

        if minutes_until == 1:
            when = "Comienza en 1 minuto."
        elif minutes_until < 60:
            when = f"Comienza en {minutes_until} minutos."
        elif minutes_until < 1440:
            hours = minutes_until // 60
            when = f"Comienza en {hours} hora(s)."
        else:
            days = minutes_until // 1440
            when = f"Comienza en {days} dia(s)."

        title = "DOJO ADMIN \u00b7 Proximo evento"
        message = (
            f"{event_name}\n"
            f"Programado para {date_text} a las {time_text}\n"
            f"{when}"
        )

        self._show_desktop(title, message)

    def show_event_started(self, event_name, start_time):
        """Notificacion: evento iniciado."""
        if not self._should_show():
            return

        time_text = start_time
        if hasattr(start_time, "strftime"):
            time_text = start_time.strftime("%H:%M")

        title = "DOJO ADMIN \u00b7 Evento iniciado"
        message = (
            f"{event_name}\n"
            f"El evento acaba de comenzar.\n"
            f"Hora: {time_text}"
        )

        self._show_desktop(title, message)

    def restore_window(self):
        """Restaura y muestra la ventana principal."""
        self.main_window.showNormal()

        try:
            import ctypes
            hwnd = int(self.main_window.winId())
            ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception:
            logger.debug(
                "ctypes restore falló, usando raise_/activateWindow"
            )
            self.main_window.raise_()
            self.main_window.activateWindow()

    def hide_window(self):
        """Oculta la ventana (minimiza al tray)."""
        self.main_window.hide()

    def enable_notifications(self):
        """Activa las notificaciones de escritorio."""
        self._notifications_enabled = True
        cfg.set_value("desktop_notifications", True)
        self._update_menu_state()

    def disable_notifications(self):
        """Desactiva las notificaciones de escritorio."""
        self._notifications_enabled = False
        cfg.set_value("desktop_notifications", False)
        self._update_menu_state()

    def is_enabled(self):
        """Retorna True si las notificaciones están activadas."""
        return self._notifications_enabled

    def mute_for(self, hours):
        """Silencia las notificaciones por un número de horas."""
        from datetime import datetime, timedelta
        self._mute_until = datetime.now() + timedelta(hours=hours)
        self._update_menu_state()

    def is_muted(self):
        """Retorna True si las notificaciones están silenciadas."""
        if self._mute_until is None:
            return False
        from datetime import datetime
        if datetime.now() < self._mute_until:
            return True
        self._mute_until = None
        return False

    def _minutes_until_unmute(self):
        """Minutos restantes hasta que se desilencie."""
        if self._mute_until is None:
            return 0
        from datetime import datetime
        delta = self._mute_until - datetime.now()
        return max(0, int(delta.total_seconds() / 60))

    def _should_show(self):
        """Determina si se debe mostrar una notificación."""
        if not self._notifications_enabled:
            return False
        if self.is_muted():
            return False
        return True

    def _show_desktop(self, title, message):
        """
        Muestra notificacion de escritorio.
        Intenta Toast nativa primero; si falla, usa QSystemTrayIcon.
        """
        if self._show_native_toast(title, message):
            return

        try:
            if (
                hasattr(self, "app_icon")
                and not self.app_icon.isNull()
            ):
                self.tray.showMessage(
                    title,
                    message,
                    self.app_icon,
                    10000,
                )
            else:
                self.tray.showMessage(
                    title,
                    message,
                    QSystemTrayIcon.MessageIcon.NoIcon,
                    10000,
                )

        except Exception:
            logger.exception(
                "No se pudo mostrar ni la Toast nativa "
                "ni la notificacion de Qt"
            )
