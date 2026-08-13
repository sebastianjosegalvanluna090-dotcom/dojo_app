"""
services/class_notification_service.py
Servicio de revisión y notificación de clases próximas.

Responsabilidades:
- Revisar clases programadas para hoy cada 30 segundos
- Calcular minutos restantes hasta cada clase
- Emitir signal cuando una notificación está lista
- Mantener registro de notificaciones ya enviadas
- Descartar claves antiguas para evitar duplicados

Flujo:
QTimer -> ClassNotificationService.check_notifications()
        -> notification_ready(dict)
        -> MainWindow._on_class_notification()
        -> NotificationPopup + Toast + DesktopNotificationService
"""

from datetime import datetime, timedelta

from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from config import settings as cfg
from core.debug import debug_log


class ClassNotificationService(QObject):
    """
    Servicio que revisa las clases programadas y emite
    signals cuando hay una notificación pendiente.

    Signals:
        notification_ready(dict) - emitido cuando hay una nueva notificación
    """

    notification_ready = pyqtSignal(dict)

    def __init__(self, classes_repo, parent=None):
        super().__init__(parent)

        self.classes_repo = classes_repo
        self.sent_class_notifications = set()
        self._notifications = []
        self._preferences = {}

        self._minutes_before = cfg.get(
            "notification_minutes_before", 15
        )

        self._timer = QTimer(self)
        self._timer.setInterval(30000)
        self._timer.timeout.connect(self.check_notifications)

    def set_preferences(self, preferences):
        self._preferences = dict(preferences)
        self._minutes_before = int(
            preferences.get("classes_minutes_before", 15)
        )

    def start(self):
        """Inicia el timer de revisión de clases."""
        self._timer.start()
        QTimer.singleShot(1200, self.check_notifications)

    def stop(self):
        """Detiene el timer de revisión de clases."""
        self._timer.stop()

    def check_notifications(self):
        """
        Revisa las clases de hoy y emite signals para
        las que requieren notificacion.
        """
        if not self._preferences.get("classes_enabled", True):
            return

        try:
            now = datetime.now()
            today = now.date()
            current_weekday = today.weekday()

            schedules = (
                self.classes_repo.get_schedules_for_day(
                    current_weekday
                )
            )

            current_minute = now.replace(
                second=0,
                microsecond=0,
            )

            for schedule in schedules:
                start_time = schedule.get("start_time")

                if start_time is None:
                    continue

                if isinstance(start_time, str):
                    try:
                        start_time = datetime.strptime(
                            start_time[:5], "%H:%M"
                        ).time()
                    except Exception as e:
                        debug_log(
                            "[ClassNotification] "
                            "Hora invalida para la clase "
                            f"{schedule.get('name')}: {e}"
                        )
                        continue

                class_start = datetime.combine(
                    today, start_time
                )

                seconds_until = (
                    class_start - current_minute
                ).total_seconds()

                minutes_until = int(seconds_until / 60)

                schedule_id = schedule.get("id")

                if schedule_id is None:
                    continue

                if 1 <= minutes_until <= self._minutes_before:
                    notification_key = (
                        today.isoformat(),
                        int(schedule_id),
                        "upcoming",
                    )

                    if (
                        notification_key
                        not in self.sent_class_notifications
                    ):
                        notification = self._build_notification(
                            schedule=schedule,
                            notification_type="upcoming",
                            minutes_until=minutes_until,
                            notification_key=notification_key,
                        )

                        self.sent_class_notifications.add(
                            notification_key
                        )

                        self._notifications.insert(
                            0, notification
                        )
                        self._notifications = (
                            self._notifications[:30]
                        )

                        self.notification_ready.emit(
                            notification
                        )

                elif minutes_until == 0:
                    notification_key = (
                        today.isoformat(),
                        int(schedule_id),
                        "started",
                    )

                    if (
                        notification_key
                        not in self.sent_class_notifications
                    ):
                        notification = self._build_notification(
                            schedule=schedule,
                            notification_type="started",
                            minutes_until=0,
                            notification_key=notification_key,
                        )

                        self.sent_class_notifications.add(
                            notification_key
                        )

                        self._notifications.insert(
                            0, notification
                        )
                        self._notifications = (
                            self._notifications[:30]
                        )

                        self.notification_ready.emit(
                            notification
                        )

            self._discard_old_notification_keys(today)

        except Exception as e:
            debug_log(
                "[ClassNotification] "
                "Error revisando notificaciones "
                f"de clases: {e}"
            )

    def _build_notification(
        self,
        schedule,
        notification_type,
        minutes_until,
        notification_key,
    ):
        """Construye el diccionario de notificación."""
        class_name = schedule.get("name", "Clase")

        instructor = schedule.get(
            "instructor", "Sin instructor"
        )

        location = schedule.get(
            "location", "Sin ubicacion"
        )

        start_time = schedule.get("start_time")

        if hasattr(start_time, "strftime"):
            time_text = start_time.strftime("%H:%M")
        else:
            time_text = str(start_time or "")[:5]

        if notification_type == "started":
            message = "La clase ya comenzo."
        else:
            if minutes_until == 1:
                message = (
                    "La clase comenzara en 1 minuto."
                )
            else:
                message = (
                    f"La clase comenzara en "
                    f"{minutes_until} minutos."
                )

        return {
            "key": notification_key,
            "category": "class",
            "type": notification_type,
            "title": class_name,
            "message": message,
            "time": time_text,
            "minutes_until": minutes_until,
            "details": f"{instructor} · {location}",
            "show_in_app": bool(
                self._preferences.get("classes_in_app", True)
            ),
            "show_windows": bool(
                self._preferences.get("classes_windows", True)
            ),
            "created_at": datetime.now(),
        }

    def _discard_old_notification_keys(self, today):
        """Elimina claves de notificaciones de dias anteriores."""
        today_text = today.isoformat()
        self.sent_class_notifications = {
            key
            for key in self.sent_class_notifications
            if key[0] == today_text
        }

    def get_notifications(self):
        """Retorna la lista actual de notificaciones."""
        return list(self._notifications)

    def clear_notifications(self):
        """Limpia todas las notificaciones."""
        self._notifications.clear()
