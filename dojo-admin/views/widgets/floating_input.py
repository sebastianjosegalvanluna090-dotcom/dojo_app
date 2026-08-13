from PyQt6.QtWidgets import QWidget, QLineEdit, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QEvent, QTimer, QPoint


CARD_BG = "#161616"
INPUT_FOCUS = "#C8102E"
TEXT_PRIMARY = "#F0F0F0"
ERROR_COLOR = "#FF4444"
SUCCESS_COLOR = "#22C55E"


class FloatingInput(QWidget):
    textChanged = pyqtSignal(str)

    def __init__(self, label_text: str, password: bool = False, parent=None, accent: str = INPUT_FOCUS, right_widget=None):
        super().__init__(parent)
        self._accent = accent
        self._error = False
        self._success = False
        self._right_widget = right_widget

        self.setFixedHeight(68)
        self.setCursor(Qt.CursorShape.IBeamCursor)

        self._input = QLineEdit(self)
        self._input.setGeometry(0, 0, self.width(), 68)
        self._apply_input_style("#333333")
        if password:
            self._input.setEchoMode(QLineEdit.EchoMode.Password)

        self._label = QLabel(label_text, self)
        self._label.setStyleSheet("color: #888888; font-size: 14px; font-weight: 700; background: transparent; border: none; padding: 0;")
        self._label.setGeometry(16, 23, max(self.width() - 32, 72), 20)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self._label_anim = QPropertyAnimation(self._label, b"pos", self)
        self._label_anim.setDuration(200)
        self._label_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._input.textChanged.connect(self._on_text_changed)
        self._input.textChanged.connect(self.textChanged.emit)
        self._input.returnPressed.connect(self._clear_focus)
        self._input.installEventFilter(self)

        if self._right_widget:
            self._right_widget.setParent(self)
            self._right_widget.raise_()
            self._right_widget.move(self.width() - self._right_widget.width() - 18, 16)
            self._right_widget.setCursor(Qt.CursorShape.ArrowCursor)

    def eventFilter(self, obj, event):
        if obj == self._input:
            if event.type() == QEvent.Type.FocusIn:
                QTimer.singleShot(0, self._sync_label_state)
            elif event.type() == QEvent.Type.FocusOut:
                QTimer.singleShot(0, self._sync_label_state)
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        self._input.setFocus()
        super().mousePressEvent(event)

    def _apply_input_style(self, border_color):
        right_padding = "54px" if self._right_widget else "14px"
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                color: {TEXT_PRIMARY};
                border: 2px solid {border_color};
                border-radius: 18px;
                padding: 15px {right_padding} 5px 14px;
                font-size: 14px;
                font-weight: 600;
            }}
            QLineEdit:focus {{
                border-color: {self._accent};
            }}
        """)

    def _clear_focus(self):
        self._input.clearFocus()

    def _on_text_changed(self, text):
        QTimer.singleShot(0, self._sync_label_state)

    def _sync_label_state(self):
        should_float = self._input.hasFocus() or bool(self._input.text().strip())
        if should_float:
            self._float_label()
        else:
            self._unfloat_label()

    def _float_label(self):
        self._label_anim.stop()
        self._label_anim.setStartValue(self._label.pos())
        self._label_anim.setEndValue(QPoint(18, 2))
        self._label_anim.start()
        self._label.setStyleSheet(f"""
            color: {self._accent};
            font-size: 11px;
            font-weight: 900;
            background-color: {CARD_BG};
            border: none;
            padding: 0 7px;
        """)

    def _unfloat_label(self):
        self._label_anim.stop()
        self._label_anim.setStartValue(self._label.pos())
        self._label_anim.setEndValue(QPoint(16, 23))
        self._label_anim.start()
        self._label.setStyleSheet("""
            color: #888888;
            font-size: 14px;
            font-weight: 700;
            background: transparent;
            border: none;
            padding: 0;
        """)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._input.setGeometry(0, 0, self.width(), 68)
        if self._right_widget:
            x = self.width() - self._right_widget.width() - 18
            y = (self.height() - self._right_widget.height()) // 2
            self._right_widget.move(x, y)
            self._right_widget.raise_()
        if self._input.text():
            self._label.setGeometry(18, 2, max(self.width() - 32, 72), 16)
        else:
            self._label.setGeometry(16, 23, max(self.width() - 32, 72), 20)

    def text(self) -> str:
        return self._input.text()

    def setText(self, value: str):
        self._input.setText(value)
        QTimer.singleShot(0, self._sync_label_state)

    def clear(self):
        self._input.clear()
        QTimer.singleShot(0, self._sync_label_state)

    def setFocus(self):
        self._input.setFocus()

    def setEchoMode(self, mode):
        self._input.setEchoMode(mode)

    def line_edit(self) -> QLineEdit:
        return self._input

    def set_error(self, message: str = ""):
        self._error = bool(message)
        self._update_border()

    def set_accent(self, accent: str):
        self._accent = accent
        self._update_border()

    def _update_border(self):
        color = ERROR_COLOR if self._error else (SUCCESS_COLOR if self._success else "#333333")
        if self._input.hasFocus() and not self._error and not self._success:
            color = self._accent
        self._apply_input_style(color)
