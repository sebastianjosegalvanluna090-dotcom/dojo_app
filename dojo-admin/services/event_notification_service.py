"""
services/event_notification_service.py
Servicio de revision y notificacion de eventos proximos.

Responsabilidades:
- Revisar eventos programados cada 60 segundos
- Calcular minutos restantes hasta cada evento
- Emitir signal cuando una notificacion esta lista
- Mantener registro de notificaciones ya enviadas
- Descartar claves antiguas para evitar duplicados
"""

from datetime import datetime, timedelta

from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from core.app_logger import get_logger
from core.debug import debug_log

logger = get_logger("event_notification_service")


class EventNotificationService(QObject):
    """
    Servicio que revisa los eventos programados y emite
    signals cuando hay una notificacion pendiente.

    Signals:
        notification_ready(dict) - emitido cuando hay una nueva notificacion
    """

    notification_ready = pyqtSignal(dict)

    def __init__(self, events_repository, parent=None):
        super().__init__(parent)

        self.events_repository = events_repository
        self.sent_event_notifications = set()
        self._notifications = []
        self._preferences = {}

        self._timer = QTimer(self)
        self._timer.setInterval(60000)
        self._timer.timeout.connect(self.check_notifications)

    def set_preferences(self, preferences):
        self._preferences = dict(preferences)

    def start(self):
        self._timer.start()
        QTimer.singleShot(5000, self.check_notifications)

    def stop(self):
        self._timer.stop()

    def check_notifications(self):
        if not self._preferences.get("events_enabled", True):
            return

        try:
            now = datetime.now()
            today = now.date()

            from_date = today.isoformat()
            to_date = (today + timedelta(days=7)).isoformat()

            events = self.events_repository.get_upcoming_events(
                from_date, to_date,
            )

            events_minutes_before = int(
                self._preferences.get("events_minutes_before", 1440)
            )

            for event in events:
                event_id = event.get("id")
                if event_id is None:
                    continue

                event_date = event.get("event_date")
                start_time = event.get("start_time")

                if event_date is None:
                    continue

                if hasattr(event_date, "date"):
                    event_date_obj = event_date.date()
                else:
                    event_date_obj = event_date

                if hasattr(start_time, "hour"):
                    event_dt = datetime.combine(event_date_obj, start_time)
                elif isinstance(start_time, str) and len(start_time) >= 5:
                    try:
                        from datetime import time as dt_time
                        t = dt_time.fromisoformat(start_time[:5])
                        event_dt = datetime.combine(event_date_obj, t)
                    except Exception:
                        event_dt = datetime.combine(
                            event_date_obj, datetime.min.time()
                        )
                else:
                    event_dt = datetime.combine(
                        event_date_obj, datetime.min.time()
                    )

                minutes_until_event = int(
                    (event_dt - now).total_seconds() / 60
                )

                event_date_iso = (
                    event_date_obj.isoformat()
                    if hasattr(event_date_obj, "isoformat")
                    else str(event_date_obj)
                )

                # Aviso previo
                if (
                    0 < minutes_until_event <= events_minutes_before
                    and minutes_until_event > 0
                ):
                    notification_key = (
                        event_id,
                        event_date_iso,
                        "upcoming",
                        events_minutes_before,
                    )

                    if notification_key not in self.sent_event_notifications:
                        notification = self._build_notification(
                            event=event,
                            notification_type="upcoming",
                            minutes_until=minutes_until_event,
                            notification_key=notification_key,
                        )

                        self.sent_event_notifications.add(notification_key)
                        self._notifications.insert(0, notification)
                        self._notifications = self._notifications[:30]

                        self.notification_ready.emit(notification)

                # Aviso de inicio (-5 a 0 minutos)
                elif (
                    self._preferences.get("events_notify_at_start", True)
                    and -5 <= minutes_until_event <= 0
                ):
                    notification_key = (
                        event_id,
                        event_date_iso,
                        "started",
                    )

                    if notification_key not in self.sent_event_notifications:
                        notification = self._build_notification(
                            event=event,
                            notification_type="started",
                            minutes_until=0,
                            notification_key=notification_key,
                        )

                        self.sent_event_notifications.add(notification_key)
                        self._notifications.insert(0, notification)
                        self._notifications = self._notifications[:30]

                        self.notification_ready.emit(notification)

            self._discard_old_keys(today)

        except Exception:
            logger.exception("Error revisando notificaciones de eventos")

    def _build_notification(
        self, event, notification_type, minutes_until, notification_key,
    ):
        event_name = event.get("name", "Evento")
        location = event.get("location", "")
        start_time = event.get("start_time")
        event_date = event.get("event_date")

        if hasattr(start_time, "strftime"):
            time_text = start_time.strftime("%H:%M")
        elif isinstance(start_time, str):
            time_text = start_time[:5]
        else:
            time_text = ""

        if hasattr(event_date, "strftime"):
            date_text = event_date.strftime("%d/%m/%Y")
        else:
            date_text = str(event_date) if event_date else ""

        if notification_type == "started":
            message = "El evento acaba de comenzar."
        else:
            if minutes_until == 1:
                message = "Comienza en 1 minuto."
            elif minutes_until < 60:
                message = f"Comienza en {minutes_until} minutos."
            elif minutes_until < 1440:
                hours = minutes_until // 60
                message = f"Comienza en {hours} hora(s)."
            else:
                days = minutes_until // 1440
                message = f"Comienza en {days} dia(s)."

        return {
            "key": notification_key,
            "category": "event",
            "type": notification_type,
            "title": event_name,
            "message": message,
            "time": time_text,
            "date": date_text,
            "details": location,
            "minutes_until": minutes_until,
            "show_in_app": bool(
                self._preferences.get("events_in_app", True)
            ),
            "show_windows": bool(
                self._preferences.get("events_windows", True)
            ),
            "created_at": datetime.now(),
        }

    def _discard_old_keys(self, today):
        today_text = today.isoformat()
        self.sent_event_notifications = {
            key
            for key in self.sent_event_notifications
            if key[1] == today_text
            or (
                isinstance(key[1], str)
                and key[1] >= today_text
            )
        }

    def get_notifications(self):
        return list(self._notifications)

    def clear_notifications(self):
        self._notifications.clear()
