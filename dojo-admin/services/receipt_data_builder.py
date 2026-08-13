"""
Convierte datos de ingreso en el formato que espera ReceiptWidget.
"""

from datetime import date, datetime
from pathlib import Path

from core.debug import debug_log

BASE_DIR = Path(__file__).resolve().parents[1]


def format_money(value):
    try:
        value = float(value or 0)
    except Exception:
        value = 0
    return "$ " + f"{value:,.0f}".replace(",", ".")


def format_date(d):
    if isinstance(d, datetime):
        return d.strftime("%d/%m/%Y")
    if isinstance(d, date):
        return d.strftime("%d/%m/%Y")
    if isinstance(d, str):
        try:
            from datetime import datetime as dt
            parsed = dt.strptime(d[:10], "%Y-%m-%d")
            return parsed.strftime("%d/%m/%Y")
        except Exception:
            return d
    return ""


def build_receipt_number(income_id):
    return f"R-{int(income_id or 0):04d}"


def _extract_student_name(participants):
    for p in participants or []:
        expected = float(p.get("expected_amount", 0) or 0)
        paid = float(p.get("paid_amount", 0) or 0)
        pending = float(p.get("pending_amount", 0) or 0)
        if expected == 0 and paid == 0 and pending == 0:
            return p.get("display_name", "")
    return ""


def _find_logo_path():
    candidates = [
        BASE_DIR / "assets" / "logo.jpg",
        BASE_DIR / "assets" / "logo.png",
        BASE_DIR / "assets" / "images" / "logo.jpg",
        BASE_DIR / "assets" / "images" / "logo.png",
        BASE_DIR / "assets" / "senshi_logo.png",
        BASE_DIR / "assets" / "logo_senshi.png",
    ]
    for path in candidates:
        if path.exists() and path.is_file():
            return str(path)
    return ""


def build_receipt_widget_data(
    income: dict,
    items: list,
    participants: list,
    receipt_number: str = None,
) -> dict:
    client_name = income.get("payer_name") or "\u2014"
    client_document = income.get("payer_document") or income.get("client_document") or "\u2014"
    client_phone = income.get("payer_phone") or income.get("client_phone") or "\u2014"

    student_name = _extract_student_name(participants)
    student_meta = f"<b>Estudiante:</b> {student_name}" if student_name else ""

    receipt_num = receipt_number or income.get("receipt_number", "R-BORRADOR")
    income_date = income.get("income_date") or income.get("date")
    receipt_date = format_date(income_date)

    subtotal = sum(float(item.get("subtotal", 0) or 0) for item in items)
    discount = float(income.get("discount", 0) or 0)
    total = max(0, subtotal - discount)
    paid = float(income.get("paid_amount") or income.get("total_paid", 0) or 0)
    pending = max(0, total - paid)

    widget_items = []
    for item in items:
        qty = item.get("quantity", 1)
        unit_price = float(item.get("unit_price", 0) or 0)
        item_total = float(item.get("subtotal", 0) or 0)
        item_discount = float(item.get("discount", 0) or 0)

        desc = item.get("name", "")
        discount_text = ""
        if item_discount > 0:
            discount_text = f"Descuento aplicado: -{format_money(item_discount)}"

        widget_items.append({
            "description": desc,
            "qty": str(qty),
            "unit_price": format_money(unit_price),
            "amount": format_money(item_total),
            "discount": discount_text,
        })

    payment_method = income.get("payment_method") or income.get("payment_method_name", "")
    destination_account = income.get("account_name") or income.get("destination_account_name", "")
    observations = income.get("note", "")

    logo = _find_logo_path()
    debug_log(f"[ReceiptDataBuilder] logo_path={logo}")

    return {
        "client_name": client_name,
        "client_document": client_document,
        "client_phone": client_phone,
        "student_meta": student_meta,
        "receipt_number": receipt_num,
        "receipt_date": receipt_date,
        "total": format_money(total),
        "items": widget_items,
        "subtotal": format_money(subtotal),
        "observations": observations,
        "payment_method": payment_method,
        "payment_date": receipt_date,
        "discount": format_money(discount),
        "total_paid": format_money(paid),
        "pending_amount": format_money(pending),
        "destination_account": destination_account,
        "logo_path": logo,
        "address": "Cra 57 #75-152, Barranquilla",
        "phone": "301 482 8926",
        "email": "senshiacademycol@gmail.com",
        "nit": "NIT: 901570911",
    }
