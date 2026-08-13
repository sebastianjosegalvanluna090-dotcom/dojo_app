from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt


WEAK = "#FF4444"
MEDIUM = "#F59E0B"
STRONG = "#3B82F6"
VERY_STRONG = "#22C55E"
GRAY = "#333333"
TEXT_MUTED = "#888888"


def validate_password(password: str) -> dict:
    return {
        "length": len(password) >= 8,
        "uppercase": any(c.isupper() for c in password),
        "lowercase": any(c.islower() for c in password),
        "number": any(c.isdigit() for c in password),
        "symbol": any(not c.isalnum() for c in password),
    }


REQUIREMENT_KEYS = [
    "auth.req_length",
    "auth.req_uppercase",
    "auth.req_lowercase",
    "auth.req_number",
    "auth.req_symbol",
]


class PasswordStrengthWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._checked = {k: False for k in REQUIREMENT_KEYS}
        self._req_texts_raw = [""] * 5

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(6)

        self._header = QLabel("")
        self._header.setStyleSheet(f"""
            color: {TEXT_MUTED};
            font-size: 11px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self._header)

        self._bar_frame = QHBoxLayout()
        self._bar_frame.setSpacing(0)
        self._bar_frame.setContentsMargins(0, 0, 0, 0)
        self._bar_bg = QFrame()
        self._bar_bg.setFixedHeight(6)
        self._bar_bg.setStyleSheet(f"background-color: {GRAY}; border-radius: 3px; border: none;")
        self._bar_fill = QFrame(self._bar_bg)
        self._bar_fill.setFixedHeight(6)
        self._bar_fill.setGeometry(0, 0, 0, 6)
        self._bar_fill.setStyleSheet(f"background-color: {GRAY}; border-radius: 3px; border: none;")
        layout.addWidget(self._bar_bg)

        self._strength_label = QLabel("")
        self._strength_label.setStyleSheet(f"""
            color: {TEXT_MUTED};
            font-size: 10px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self._strength_label)

        self._req_labels = {}
        for key in REQUIREMENT_KEYS:
            lbl = QLabel("")
            lbl.setStyleSheet(f"""
                color: {TEXT_MUTED};
                font-size: 11px;
                font-weight: 500;
                padding-left: 12px;
                background: transparent;
                border: none;
            """)
            self._req_labels[key] = lbl
            layout.addWidget(lbl)

        self.setVisible(False)

    def set_texts(self, header: str, req_texts: list[str], weak: str, medium: str, strong: str, very_strong: str):
        self._header.setText(header)
        self._strength_texts = [weak, medium, strong, very_strong]
        self._req_texts_raw = req_texts
        for key, text in zip(REQUIREMENT_KEYS, req_texts):
            self._req_labels[key].setText(f"☐  {text}")

    def update_password(self, password: str):
        results = validate_password(password)
        keys = REQUIREMENT_KEYS
        checks = [results["length"], results["uppercase"], results["lowercase"], results["number"], results["symbol"]]
        score = sum(checks)

        self._update_requirements(keys, checks, score)
        self._update_bar(score)

        if password:
            self.setVisible(True)
        else:
            self.setVisible(False)

    def _update_requirements(self, keys, checks, score):
        for i, (key, ok) in enumerate(zip(keys, checks)):
            lbl = self._req_labels[key]
            raw = self._req_texts_raw[i] if i < len(self._req_texts_raw) else ""
            if ok:
                lbl.setText(f"✓  {raw}")
                lbl.setStyleSheet(f"""
                    color: {VERY_STRONG};
                    font-size: 11px;
                    font-weight: 600;
                    padding-left: 12px;
                    background: transparent;
                    border: none;
                """)
            else:
                lbl.setText(f"☐  {raw}")
                lbl.setStyleSheet(f"""
                    color: {TEXT_MUTED};
                    font-size: 11px;
                    font-weight: 500;
                    padding-left: 12px;
                    background: transparent;
                    border: none;
                """)
            self._checked[key] = ok

    def _update_bar(self, score):
        if score <= 1:
            color = WEAK
            label = self._strength_texts[0] if hasattr(self, '_strength_texts') and len(self._strength_texts) > 0 else ""
        elif score <= 3:
            color = MEDIUM
            label = self._strength_texts[1] if hasattr(self, '_strength_texts') and len(self._strength_texts) > 1 else ""
        elif score == 4:
            color = STRONG
            label = self._strength_texts[2] if hasattr(self, '_strength_texts') and len(self._strength_texts) > 2 else ""
        else:
            color = VERY_STRONG
            label = self._strength_texts[3] if hasattr(self, '_strength_texts') and len(self._strength_texts) > 3 else ""

        bw = self._bar_bg.width()
        pct = score / 5.0
        fill_w = max(int(bw * pct), 0) if bw > 0 else 0
        self._bar_fill.setFixedWidth(fill_w)
        self._bar_fill.setStyleSheet(f"background-color: {color}; border-radius: 3px; border: none;")
        self._strength_label.setText(label)
        self._strength_label.setStyleSheet(f"""
            color: {color};
            font-size: 10px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        score = sum(1 for v in self._checked.values() if v)
        self._update_bar(score)

    def is_valid(self) -> bool:
        return all(self._checked.values())
