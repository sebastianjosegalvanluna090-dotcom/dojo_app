# core/toast.py — Singleton global de toasts para DOJO_ADMIN
# Uso: from core.toast import toast_manager; toast_manager.show("msg", "success")

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QLabel, QHBoxLayout,
    QGraphicsOpacityEffect,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve

TEXT_PRI = "#FAFAFA"


class Toast(QFrame):
    def __init__(self, message, kind="success", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(62)
        self.setFixedWidth(360)

        color = {
            "success": "#10B981",
            "info":    "#3B82F6",
            "warning": "#F59E0B",
            "error":   "#E11D48",
        }.get(kind, "#10B981")

        icon = {"success": "✓", "info": "i", "warning": "!", "error": "×"}.get(kind, "✓")

        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(14,14,14,235);
                border: 1px solid #222222;
                border-radius: 12px;
            }}
            QLabel {{ background: transparent; border: none; }}
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(14, 10, 14, 10)
        root.setSpacing(10)

        lbl_icon = QLabel(icon)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setFixedSize(28, 28)
        lbl_icon.setStyleSheet(f"""
            QLabel {{
                color: {color}; border: 1px solid {color};
                border-radius: 14px; font-weight: 900; font-size: 13px;
                background: transparent;
            }}
        """)
        lbl_msg = QLabel(message)
        lbl_msg.setWordWrap(True)
        lbl_msg.setStyleSheet(f"color: {TEXT_PRI}; font-size: 12px; font-weight: 600;")

        root.addWidget(lbl_icon)
        root.addWidget(lbl_msg, 1)

        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)

        self._anim_in = QPropertyAnimation(self.effect, b"opacity", self)
        self._anim_in.setDuration(240)
        self._anim_in.setStartValue(0.0)
        self._anim_in.setEndValue(1.0)
        self._anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._anim_out = QPropertyAnimation(self.effect, b"opacity", self)
        self._anim_out.setDuration(260)
        self._anim_out.setStartValue(1.0)
        self._anim_out.setEndValue(0.0)
        self._anim_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self._anim_out.finished.connect(self._finish)

        self._anim_in.start()
        QTimer.singleShot(3000, self._anim_out.start)

    def _finish(self):
        if self.parentWidget() and self.parentWidget().layout():
            self.parentWidget().layout().removeWidget(self)
        self.deleteLater()


class ToastManager:
    """Singleton. Se inicializa una vez en MainWindow, luego cualquier modulo lo importa y usa."""
    _instance = None

    def __init__(self):
        self._layer: QWidget | None = None
        self._layout = None
        self._parent: QWidget | None = None
        self._original_resize = None

    @classmethod
    def instance(cls) -> "ToastManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def attach(self, parent: QWidget):
        """Llamar desde MainWindow._build_ui() pasando self (la ventana principal)."""
        self._parent = parent

        self._layer = QWidget(parent)
        self._layer.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._layer.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._layer.setStyleSheet("background: transparent;")

        self._layout = QVBoxLayout(self._layer)
        self._layout.setContentsMargins(0, 0, 16, 16)
        self._layout.setSpacing(8)
        self._layout.setAlignment(
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight
        )
        self._layout.addStretch()

        self._resize_layer()
        self._layer.raise_()

        # Guardar el resizeEvent original y reemplazarlo
        self._original_resize = parent.resizeEvent
        parent.resizeEvent = self._on_parent_resize

    def _resize_layer(self):
        if self._parent and self._layer:
            self._layer.setGeometry(0, 0, self._parent.width(), self._parent.height())

    def _on_parent_resize(self, event):
        # Llamar al resize original primero
        if self._original_resize:
            self._original_resize(event)
        # Luego actualizar capa
        self._resize_layer()
        if self._layer:
            self._layer.raise_()

    def show(self, message: str, kind: str = "success"):
        """Llamar desde cualquier view: toast_manager.show('Guardado', 'success')"""
        if not self._layer or not self._layout:
            return
        toast = Toast(message, kind, self._layer)
        self._layout.addWidget(toast, 0, Qt.AlignmentFlag.AlignRight)
        self._layer.raise_()


# Acceso global
toast_manager = ToastManager.instance()
