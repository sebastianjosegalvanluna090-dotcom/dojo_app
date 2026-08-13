"""
Plantilla de Recibo Mejorada — Senshi Fight Academy (PyQt6)
====================================================
Réplica en PyQt6 refinada. Pensada como plantilla:
se le pasa un diccionario `data` con toda la información variable
y construye el widget completo.
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QGraphicsDropShadowEffect, QScrollArea, QSizePolicy
)
from PyQt6.QtGui import QColor, QPixmap, QFont
from PyQt6.QtCore import Qt

CARD_WIDTH = 820

# Colores Base (Inspirados en la vista previa HTML Tailwind)
COLOR_DARK = "#0A0A0A"
COLOR_RED = "#E11D48" 
COLOR_LIGHT = "#F8F9FA"


def make_label(text, style, alignment=None, word_wrap=False, rich=False):
    lbl = QLabel(text)
    lbl.setStyleSheet(style)
    if rich:
        lbl.setTextFormat(Qt.TextFormat.RichText)
    if alignment is not None:
        lbl.setAlignment(alignment)
    lbl.setWordWrap(word_wrap)
    return lbl


class ReceiptWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setObjectName("rc")
        self.setFixedWidth(CARD_WIDTH)
        self.setStyleSheet(f"""
            #rc {{
                background-color: {COLOR_LIGHT};
                border-radius: 24px;
            }}
            * {{
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}
        """)

        # Sombra premium
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 20)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 32) # Padding bottom
        outer.setSpacing(0)

        outer.addWidget(self._build_header())
        outer.addSpacing(-32) # Superponer la tarjeta del cliente
        outer.addWidget(self._build_client_card())
        outer.addSpacing(32)
        outer.addWidget(self._build_table())
        outer.addWidget(self._build_subtotal())
        outer.addSpacing(16)
        outer.addWidget(self._build_observations())
        outer.addSpacing(24)
        outer.addWidget(self._build_footer())

    # ------------------------------------------------------------------ #
    # HEADER NEGRO
    # ------------------------------------------------------------------ #
    def _build_header(self):
        frame = QFrame()
        frame.setObjectName("rcTop")
        frame.setStyleSheet(f"""
            #rcTop {{
                background-color: {COLOR_DARK};
                border-bottom-left-radius: 32px;
                border-bottom-right-radius: 32px;
            }}
        """)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(40, 40, 40, 60) # Amplio padding inferior para la superposición

        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title = make_label("Recibo", "color:#ffffff; font-size:36px; font-weight:900;")
        slogan = make_label(
            "COMPROBANTE OFICIAL DE PAGO",
            "color:#9CA3AF; font-size:11px; font-weight:700; letter-spacing:2px;"
        )
        title_box.addWidget(title)
        title_box.addWidget(slogan)
        title_box.addStretch()

        layout.addLayout(title_box)
        layout.addStretch()

        # Logo placeholder
        logo = QLabel()
        logo.setFixedSize(96, 96)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("background-color:#000000; border: 1px solid #1F1F1F; border-radius:16px;")
        
        logo_path = self.data.get("logo_path")
        if logo_path:
            pix = QPixmap(logo_path).scaled(
                96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            logo.setPixmap(pix)
        else:
            logo.setText("SFA")
            logo.setStyleSheet(f"background-color:#000000; color:{COLOR_RED}; font-size:32px; font-weight:900; font-style:italic; border-radius:16px; border: 1px solid #1F1F1F;")
            
        layout.addWidget(logo)

        return frame

    # ------------------------------------------------------------------ #
    # CARD ROJA CLIENTE
    # ------------------------------------------------------------------ #
    def _build_client_card(self):
        wrapper = QWidget()
        wlayout = QHBoxLayout(wrapper)
        wlayout.setContentsMargins(32, 0, 32, 0)

        card = QFrame()
        card.setObjectName("rcClient")
        card.setStyleSheet(f"""
            #rcClient {{ background-color:{COLOR_RED}; border-radius:20px; }}
            #rcClient QLabel {{ color:#ffffff; }}
        """)
        
        # Sombra sutil para la tarjeta roja
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(136, 19, 55, 100)) # Sombra tono rojo oscuro
        card.setGraphicsEffect(shadow)
        
        clayout = QHBoxLayout(card)
        clayout.setContentsMargins(32, 28, 32, 28)

        # -- lado izquierdo --
        left = QVBoxLayout()
        left.setSpacing(4)
        left.addWidget(make_label(
            "CLIENTE", "font-size:10px; font-weight:700; letter-spacing:1.5px; color: rgba(255,255,255,0.8);"
        ))
        left.addWidget(make_label(
            self.data.get("client_name", ""),
            "font-size:26px; font-weight:800;"
        ))
        left.addSpacing(8)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(16)
        meta_row.addWidget(make_label(
            f"<b>Documento:</b> {self.data.get('client_document', '')}",
            "font-size:12px; font-weight:500;", rich=True
        ))
        meta_row.addWidget(make_label(
            f"<b>Teléfono:</b> {self.data.get('client_phone', '')}",
            "font-size:12px; font-weight:500;", rich=True
        ))
        student_meta = self.data.get("student_meta")
        if student_meta:
            meta_row.addWidget(make_label(student_meta, "font-size:12px; font-weight:500;", rich=True))
        meta_row.addStretch()
        left.addLayout(meta_row)

        clayout.addLayout(left)
        clayout.addStretch()

        # -- lado derecho --
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignmentFlag.AlignRight)
        right.setSpacing(12)
        
        inv_info = make_label(
            f"<b>No. Recibo:</b> {self.data.get('receipt_number', '')}<br>"
            f"<span style='color:rgba(255,255,255,0.8);'><b>Fecha:</b></span> {self.data.get('receipt_date', '')}",
            "font-size:12px;", alignment=Qt.AlignmentFlag.AlignRight, rich=True
        )
        right.addWidget(inv_info)

        total_badge = make_label(
            self.data.get("total", ""),
            f"""
            background-color:{COLOR_DARK}; color:#ffffff;
            padding:6px 20px; border-radius:16px;
            font-size:18px; font-weight:900;
            border: 1px solid #000000;
            """,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        total_badge.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        right.addWidget(total_badge, 0, Qt.AlignmentFlag.AlignRight)

        clayout.addLayout(right)

        wlayout.addWidget(card)
        return wrapper

    # ------------------------------------------------------------------ #
    # TABLA DE ITEMS
    # ------------------------------------------------------------------ #
    def _build_table(self):
        wrapper = QWidget()
        wlayout = QVBoxLayout(wrapper)
        wlayout.setContentsMargins(40, 0, 40, 0)
        wlayout.setSpacing(0)

        # header
        header = QFrame()
        header.setObjectName("tblHeader")
        header.setStyleSheet(f"""
            #tblHeader {{ background-color:{COLOR_DARK}; border-radius:12px; }}
            #tblHeader QLabel {{ color:#ffffff; font-size:10px; font-weight:800; letter-spacing: 1px; padding: 6px 0;}}
        """)
        hlayout = QHBoxLayout(header)
        hlayout.setContentsMargins(20, 4, 20, 4)
        hlayout.addWidget(make_label("DESCRIPCI\u00d3N", ""), 55)
        hlayout.addWidget(make_label("CANT.", "", alignment=Qt.AlignmentFlag.AlignCenter), 12)
        hlayout.addWidget(make_label("VALOR UNIT.", "", alignment=Qt.AlignmentFlag.AlignRight), 16)
        hlayout.addWidget(make_label("TOTAL", "", alignment=Qt.AlignmentFlag.AlignRight), 17)
        wlayout.addWidget(header)
        wlayout.addSpacing(8)

        # filas
        items = self.data.get("items", [])
        for i, item in enumerate(items):
            row = QFrame()
            is_last = (i == len(items) - 1)
            border = "none" if is_last else "1px solid rgba(0,0,0,0.08)"
            row.setStyleSheet(f"border-bottom:{border};")
            rlayout = QHBoxLayout(row)
            rlayout.setContentsMargins(20, 14, 20, 14)

            desc_html = f"<span style='font-weight:600; color:#1F2937; font-size:14px;'>{item.get('description', '')}</span>"
            if item.get("discount"):
                desc_html += f"<br><span style='color:{COLOR_RED}; font-size:10px; font-weight:800; letter-spacing: 0.5px; text-transform: uppercase;'>{item['discount']}</span>"
            desc = make_label(desc_html, "", word_wrap=True, rich=True)
            rlayout.addWidget(desc, 55)

            rlayout.addWidget(make_label(
                str(item.get("qty", "")), "font-size:14px; font-weight:500; color:#4B5563;", alignment=Qt.AlignmentFlag.AlignCenter
            ), 12)
            rlayout.addWidget(make_label(
                item.get("unit_price", ""), "font-size:14px; font-weight:500; color:#4B5563;", alignment=Qt.AlignmentFlag.AlignRight
            ), 16)
            rlayout.addWidget(make_label(
                item.get("amount", ""), "font-size:14px; font-weight:800; color:#111827;", alignment=Qt.AlignmentFlag.AlignRight
            ), 17)

            wlayout.addWidget(row)

        return wrapper

    # ------------------------------------------------------------------ #
    # SUBTOTAL
    # ------------------------------------------------------------------ #
    def _build_subtotal(self):
        wrapper = QWidget()
        wlayout = QHBoxLayout(wrapper)
        wlayout.setContentsMargins(40, 16, 40, 0)
        wlayout.addStretch()

        pill = make_label(
            f"SUBTOTAL: {self.data.get('subtotal', '')}",
            f"""
            border: 2px solid {COLOR_DARK}; padding: 6px 20px;
            border-radius: 14px; font-size: 12px; font-weight: 800;
            color: {COLOR_DARK}; letter-spacing: 0.5px;
            """
        )
        wlayout.addWidget(pill)
        return wrapper

    # ------------------------------------------------------------------ #
    # OBSERVACIONES
    # ------------------------------------------------------------------ #
    def _build_observations(self):
        wrapper = QWidget()
        wlayout = QVBoxLayout(wrapper)
        wlayout.setContentsMargins(40, 0, 40, 0)

        box = QFrame()
        box.setObjectName("rcObs")
        box.setStyleSheet("""
            #rcObs {
                background-color:#ffffff;
                border: 1px dashed #D1D5DB;
                border-radius: 16px;
            }
        """)
        blayout = QVBoxLayout(box)
        blayout.setContentsMargins(20, 20, 20, 20)

        title = make_label(
            "OBSERVACIONES", "font-size:10px; letter-spacing: 1px; font-weight:800; color:#9CA3AF;"
        )
        body = make_label(
            self.data.get("observations", ""),
            "font-size:12px; color:#4B5563; font-weight:500; margin-top: 4px;", word_wrap=True
        )
        body.setMinimumHeight(35)
        blayout.addWidget(title)
        blayout.addWidget(body)

        wlayout.addWidget(box)
        return wrapper

    # ------------------------------------------------------------------ #
    # FOOTER (2 columnas: pago / contacto)
    # ------------------------------------------------------------------ #
    def _build_footer(self):
        wrapper = QWidget()
        wlayout = QHBoxLayout(wrapper)
        wlayout.setContentsMargins(40, 0, 40, 0)
        wlayout.setSpacing(20)

        # -- tarjeta oscura: detalles de pago --
        pay_card = QFrame()
        pay_card.setObjectName("payCard")
        pay_card.setStyleSheet("""
            #payCard { background-color:#161616; border-radius:20px; }
        """)
        
        shadow_pay = QGraphicsDropShadowEffect(pay_card)
        shadow_pay.setBlurRadius(15)
        shadow_pay.setOffset(0, 5)
        shadow_pay.setColor(QColor(0, 0, 0, 40))
        pay_card.setGraphicsEffect(shadow_pay)
        
        players = QVBoxLayout(pay_card)
        players.setContentsMargins(24, 24, 24, 24)
        players.setSpacing(8)

        title = make_label(
            "DETALLES DEL PAGO", "font-size:10px; letter-spacing:1px; font-weight:800; color:#9CA3AF;"
        )
        players.addWidget(title)
        players.addSpacing(4)

        pay_fields = [
            ("Método:", self.data.get("payment_method", ""), "#FFFFFF", False),
            ("Fecha pago:", self.data.get("payment_date", ""), "#FFFFFF", False),
            ("Descuento:", self.data.get("discount", ""), COLOR_RED, False),
            ("separator", "", "", False),
            ("Pagado:", self.data.get("total_paid", ""), "#FFFFFF", True),
            ("Pendiente:", self.data.get("pending_amount", ""), "#34D399", True), # Emerald 400
            ("Cuenta:", self.data.get("destination_account", "")[:20]+"...", "#9CA3AF", False),
        ]
        
        for label, value, val_color, is_bold in pay_fields:
            if label == "separator":
                sep = QFrame()
                sep.setFixedHeight(1)
                sep.setStyleSheet("background-color: rgba(255,255,255,0.1); margin: 4px 0;")
                players.addWidget(sep)
                continue
                
            weight = "800" if is_bold else "600"
            row = make_label(
                f"<table width='100%'><tr><td align='left' style='color:#9CA3AF;'>{label}</td><td align='right' style='color:{val_color}; font-weight:{weight};'>{value}</td></tr></table>",
                "font-size:12px;", rich=True
            )
            players.addWidget(row)

        # -- tarjeta clara: contacto --
        contact_card = QFrame()
        contact_card.setObjectName("contactCard")
        contact_card.setStyleSheet("""
            #contactCard { background-color:#F3F4F6; border: 1px solid #E5E7EB; border-radius:20px; }
        """)
        
        shadow_contact = QGraphicsDropShadowEffect(contact_card)
        shadow_contact.setBlurRadius(10)
        shadow_contact.setOffset(0, 4)
        shadow_contact.setColor(QColor(0, 0, 0, 10))
        contact_card.setGraphicsEffect(shadow_contact)
        
        clayout = QVBoxLayout(contact_card)
        clayout.setContentsMargins(24, 24, 24, 24)
        clayout.setSpacing(6)

        clayout.addWidget(make_label(
            "CONTACTO", "font-size:10px; letter-spacing:1px; font-weight:800; color:#6B7280;"
        ))
        clayout.addWidget(make_label(
            "Senshi Fight Academy", "font-size:14px; font-weight:800; color:#0A0A0A; margin-bottom: 8px;"
        ))

        contact_rows = [
            ("📍", self.data.get("address", "Cra 57 #75-152, BAQ")),
            ("☎",  self.data.get("phone", "301 482 8926")),
            ("✉",  self.data.get("email", "senshiacademycol@gmail...")),
            ("🧾", self.data.get("nit", "NIT: 901570911")),
        ]
        
        for icon, text in contact_rows:
            row = QHBoxLayout()
            row.setSpacing(12)
            icon_lbl = make_label(icon, "font-size:14px; color:#6B7280;")
            icon_lbl.setFixedWidth(20)
            row.addWidget(icon_lbl)
            row.addWidget(make_label(text, "font-size:12px; font-weight:500; color:#374151;"))
            row.addStretch()
            clayout.addLayout(row)

        wlayout.addWidget(pay_card, 1)
        wlayout.addWidget(contact_card, 1)
        return wrapper


class ReceiptWindow(QScrollArea):
    """Ventana contenedora que imita el fondo de previsualización."""

    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Recibo — Senshi Fight Academy")
        self.setStyleSheet("background-color:#111111; border:none;")
        self.setWidgetResizable(True)

        container = QWidget()
        container.setStyleSheet("background-color:#111111;")
        clayout = QVBoxLayout(container)
        clayout.setContentsMargins(20, 50, 20, 50)
        clayout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.receipt = ReceiptWidget(data)
        clayout.addWidget(self.receipt)

        self.setWidget(container)
        self.resize(CARD_WIDTH + 100, 950)


# ---------------------------------------------------------------------- #
# DATOS DE EJEMPLO
# ---------------------------------------------------------------------- #
SAMPLE_DATA = {
    "client_name": "Juan Pérez",
    "client_document": "CC 1234567890",
    "client_phone": "300 123 4567",
    "student_meta": "<b>Categoría:</b> Adulto",
    "receipt_number": "0042",
    "receipt_date": "07/07/2026",
    "total": "$ 250.000",
    "items": [
        {
            "description": "Mensualidad Julio — Muay Thai",
            "qty": "1",
            "unit_price": "$ 200.000",
            "amount": "$ 200.000",
        },
        {
            "description": "Kit de guantes",
            "discount": "Descuento 10%",
            "qty": "1",
            "unit_price": "$ 80.000",
            "amount": "$ 72.000",
        },
    ],
    "subtotal": "$ 272.000",
    "observations": "Pago realizado en efectivo en recepción.\nGracias por su preferencia.",
    "payment_method": "Efectivo",
    "payment_date": "07/07/2026",
    "discount": "$ 22.000",
    "total_paid": "$ 250.000",
    "pending_amount": "$ 0",
    "destination_account": "Bancolombia 000-000000-00",
    # "logo_path": "ruta/a/logo.png",
}


def main():
    app = QApplication(sys.argv)
    window = ReceiptWindow(SAMPLE_DATA)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()