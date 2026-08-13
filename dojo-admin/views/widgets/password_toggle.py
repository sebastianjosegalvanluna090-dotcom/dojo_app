from PyQt6.QtWidgets import QPushButton, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, pyqtSignal, QByteArray, QPropertyAnimation, QEasingCurve, QRectF
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer


_EYE_OFF = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"'
    ' fill="none" stroke="{COLOR}" stroke-width="2"'
    ' stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8'
    ' a18.45 18.45 0 0 1 5.06-5.94"/>'
    '<path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8'
    ' a18.5 18.5 0 0 1-2.16 3.19"/>'
    '<line x1="1" y1="1" x2="23" y2="23"/>'
    '<path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"/>'
    '</svg>'
)

_EYE_ON = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"'
    ' fill="none" stroke="{COLOR}" stroke-width="2"'
    ' stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>'
    '<circle cx="12" cy="12" r="3"/>'
    '</svg>'
)


def _build_pixmap(svg_template: str, color: str) -> QPixmap:
    svg = svg_template.replace("{COLOR}", color)
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    pm = QPixmap(24, 24)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    renderer.render(p, QRectF(0, 0, 24, 24))
    p.end()
    return pm


class PasswordToggleButton(QPushButton):
    _pm_hidden = None
    _pm_visible = None
    toggledVisible = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._visible = False
        self.setFixedSize(36, 36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.07);
            }
            QPushButton:pressed {
                background-color: rgba(200, 16, 46, 0.18);
            }
        """)
        self.clicked.connect(self._toggle)

        if PasswordToggleButton._pm_hidden is None:
            PasswordToggleButton._pm_hidden = _build_pixmap(_EYE_OFF, "#9CA3AF")
        if PasswordToggleButton._pm_visible is None:
            PasswordToggleButton._pm_visible = _build_pixmap(_EYE_ON, "#C8102E")

    def _toggle(self):
        self._visible = not self._visible
        self.toggledVisible.emit(self._visible)

        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(0.0)
        self.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(220)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutBack)
        anim.finished.connect(lambda: self.setGraphicsEffect(None))
        self._anim = anim
        anim.start()

    def isVisiblePassword(self) -> bool:
        return self._visible

    def paintEvent(self, event):
        p = QPainter(self)
        if not p.isActive():
            return
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        src = self._pm_visible if self._visible else self._pm_hidden
        x = (self.width() - src.width()) // 2
        y = (self.height() - src.height()) // 2
        p.drawPixmap(x, y, src)
