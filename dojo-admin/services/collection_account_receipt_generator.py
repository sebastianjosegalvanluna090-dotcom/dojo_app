import os
import re
import sys
import unicodedata
import base64
from datetime import datetime
from pathlib import Path
from html import escape


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "storage" / "receipts"
HTML_OUTPUT_DIR = OUTPUT_DIR / "html"

_LOGO_CANDIDATES = [
    BASE_DIR / "assets" / "logo.png",
    BASE_DIR / "assets" / "images" / "logo.png",
    BASE_DIR / "assets" / "senshi_logo.png",
    BASE_DIR / "assets" / "logo_senshi.png",
    BASE_DIR / "assets" / "logo.jpg",
    BASE_DIR / "assets" / "logo.jpeg",
    BASE_DIR / "assets" / "logo.svg",
    BASE_DIR / "assets" / "logo.webp",
    BASE_DIR / "assets" / "images" / "logo.jpg",
    BASE_DIR / "assets" / "images" / "logo.jpeg",
    BASE_DIR / "assets" / "images" / "logo.svg",
    BASE_DIR / "assets" / "images" / "logo.webp",
]

_WEBENGINE_PAGES_GUARD = []


def _find_logo_path():
    for candidate in _LOGO_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def _build_logo_html():
    logo_path = _find_logo_path()
    if logo_path is None:
        return ""
    ext = logo_path.suffix.lower()
    mime_map = {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml", ".webp": "image/webp",
    }
    mime = mime_map.get(ext, "image/png")
    try:
        data = logo_path.read_bytes()
        b64 = base64.b64encode(data).decode("ascii")
        return f'<img src="data:{mime};base64,{b64}" alt="Logo" style="height:48px;">'
    except Exception:
        return ""


def format_money(value):
    try:
        value = float(value or 0)
    except Exception:
        value = 0
    return "$" + f"{value:,.0f}".replace(",", ".")


def _format_date(d):
    if hasattr(d, "strftime"):
        return d.strftime("%d/%m/%Y")
    return str(d)[:10] if d else datetime.now().strftime("%d/%m/%Y")


def _escape(value):
    return escape(str(value or ""))


def _slugify(value):
    value = str(value or "")
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s\-]", "", value)
    value = re.sub(r"[\s]+", "_", value.strip())
    value = re.sub(r"_+", "_", value)
    return value[:80] if value else "cuenta"


def build_receipt_number(account_id):
    return f"CC-{int(account_id):04d}"


def _build_items_rows(items):
    rows = []
    for item in items:
        name = _escape(str(item.get("name", ""))[:50])
        desc = _escape(str(item.get("description", ""))[:60])
        qty = item.get("quantity", 1)
        price = float(item.get("unit_price", 0) or 0)
        subtotal = float(item.get("subtotal", 0) or 0)
        discount = float(item.get("discount", 0) or 0)

        desc_html = f'<br><span style="color:#9CA3AF;font-size:12px;">{desc}</span>' if desc else ""
        discount_html = ""
        if discount > 0:
            discount_html = f'<br><span style="color:#C8102E;font-size:12px;">Descuento: -{format_money(discount)}</span>'

        rows.append(
            "<tr>"
            f'<td style="padding:10px 14px;border-bottom:1px solid #E5E7EB;font-size:13px;">{name}{desc_html}{discount_html}</td>'
            f'<td style="padding:10px 14px;border-bottom:1px solid #E5E7EB;text-align:center;font-size:13px;">{qty}</td>'
            f'<td style="padding:10px 14px;border-bottom:1px solid #E5E7EB;text-align:right;font-size:13px;">{format_money(price)}</td>'
            f'<td style="padding:10px 14px;border-bottom:1px solid #E5E7EB;text-align:right;font-size:13px;font-weight:600;">{format_money(subtotal)}</td>'
            "</tr>"
        )

    if not rows:
        rows.append(
            '<tr><td colspan="4" style="padding:14px;text-align:center;color:#9CA3AF;font-size:13px;">Sin conceptos</td></tr>'
        )

    return "\n".join(rows)


def build_collection_account_html(account, items, receipt_number=None):
    client_name = _escape(account.get("client_name", ""))
    client_doc = _escape(account.get("client_document", "") or "")
    client_email = _escape(account.get("client_email", "") or "")
    client_phone = _escape(account.get("client_phone", "") or "")
    account_date = _format_date(account.get("account_date"))
    due_date = _format_date(account.get("due_date"))
    subtotal = float(account.get("subtotal", 0) or 0)
    scholarship_discount = float(account.get("scholarship_discount", 0) or 0)
    total = float(account.get("total", 0) or 0)
    total_paid = float(account.get("total_paid", 0) or 0)
    pending = float(account.get("pending_amount", 0) or 0)
    scholarship_name = _escape(account.get("scholarship_name", "") or "")
    note = _escape(account.get("note", "") or "")
    receipt_num = _escape(receipt_number or build_receipt_number(account.get("id", 0)))

    logo_html = _build_logo_html()
    items_rows = _build_items_rows(items)

    scholarship_section = ""
    if scholarship_name and scholarship_discount > 0:
        scholarship_section = f"""
        <div style="background:#F5F3FF;border:1px solid #DDD6FE;border-radius:8px;padding:12px 16px;margin-bottom:20px;">
            <div style="font-size:13px;font-weight:700;color:#7C3AED;margin-bottom:4px;">🎓 {_escape(account.get('scholarship_name', ''))}</div>
            <div style="font-size:13px;color:#6B7280;">Descuento aplicado: <strong style="color:#7C3AED;">-{format_money(scholarship_discount)}</strong></div>
        </div>"""

    note_section = ""
    if note:
        note_section = f"""
        <div style="margin-bottom:20px;">
            <div style="font-size:11px;font-weight:700;color:#9CA3AF;letter-spacing:1px;margin-bottom:8px;text-transform:uppercase;">Observaciones</div>
            <div style="font-size:13px;color:#374151;line-height:1.5;">{note}</div>
        </div>"""

    pending_style = "color:#DC2626;" if pending > 0 else "color:#16A34A;"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Recibo de Cuenta de Cobro {receipt_num}</title>
<style>
@page {{ size: A4; margin: 12mm; }}
body {{ margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background: #fff; }}
* {{ box-sizing: border-box; }}
</style>
</head>
<body>
<div style="max-width:720px;margin:0 auto;padding:32px;">

<!-- Header -->
<div style="text-align:center;margin-bottom:28px;border-bottom:3px solid #C8102E;padding-bottom:20px;">
    <div style="margin-bottom:12px;">{logo_html}</div>
    <div style="font-size:11px;font-weight:700;color:#9CA3AF;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;">Cuenta de Cobro</div>
    <div style="font-size:22px;font-weight:900;color:#111827;">{receipt_num}</div>
</div>

<!-- Info Row -->
<div style="display:flex;justify-content:space-between;margin-bottom:24px;flex-wrap:wrap;gap:16px;">
    <div>
        <div style="font-size:11px;font-weight:700;color:#9CA3AF;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">Fecha de emisión</div>
        <div style="font-size:14px;font-weight:600;color:#111827;">{account_date}</div>
    </div>
    <div>
        <div style="font-size:11px;font-weight:700;color:#9CA3AF;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">Fecha de vencimiento</div>
        <div style="font-size:14px;font-weight:600;color:#111827;">{due_date}</div>
    </div>
</div>

<!-- Client -->
<div style="background:#F9FAFB;border:1px solid #E5E7EB;border-radius:10px;padding:18px 20px;margin-bottom:24px;">
    <div style="font-size:11px;font-weight:700;color:#9CA3AF;letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;">Datos del Cliente</div>
    <div style="font-size:16px;font-weight:700;color:#111827;margin-bottom:6px;">{client_name}</div>
    <div style="font-size:13px;color:#6B7280;line-height:1.7;">
        {'<div>📄 ' + client_doc + '</div>' if client_doc else ''}
        {'<div>📧 ' + client_email + '</div>' if client_email else ''}
        {'<div>📞 ' + client_phone + '</div>' if client_phone else ''}
        {'<div style="color:#9CA3AF;">Sin datos de contacto</div>' if not client_doc and not client_email and not client_phone else ''}
    </div>
</div>

<!-- Items Table -->
<div style="margin-bottom:24px;">
    <table style="width:100%;border-collapse:collapse;border:1px solid #E5E7EB;border-radius:10px;overflow:hidden;">
        <thead>
            <tr style="background:#F3F4F6;">
                <th style="padding:10px 14px;text-align:left;font-size:11px;font-weight:700;color:#6B7280;text-transform:uppercase;letter-spacing:0.5px;">Concepto</th>
                <th style="padding:10px 14px;text-align:center;font-size:11px;font-weight:700;color:#6B7280;text-transform:uppercase;letter-spacing:0.5px;">Cant.</th>
                <th style="padding:10px 14px;text-align:right;font-size:11px;font-weight:700;color:#6B7280;text-transform:uppercase;letter-spacing:0.5px;">Valor</th>
                <th style="padding:10px 14px;text-align:right;font-size:11px;font-weight:700;color:#6B7280;text-transform:uppercase;letter-spacing:0.5px;">Subtotal</th>
            </tr>
        </thead>
        <tbody>
            {items_rows}
        </tbody>
    </table>
</div>

{scholarship_section}

<!-- Summary -->
<div style="background:#F9FAFB;border:1px solid #E5E7EB;border-radius:10px;padding:18px 20px;margin-bottom:24px;">
    <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
        <span style="font-size:13px;color:#6B7280;">Subtotal</span>
        <span style="font-size:13px;color:#111827;">{format_money(subtotal)}</span>
    </div>
    {'<div style="display:flex;justify-content:space-between;margin-bottom:8px;"><span style="font-size:13px;color:#7C3AED;">Descuento beca</span><span style="font-size:13px;color:#7C3AED;">-' + format_money(scholarship_discount) + '</span></div>' if scholarship_discount > 0 else ''}
    <div style="border-top:2px solid #E5E7EB;margin:10px 0;padding-top:10px;display:flex;justify-content:space-between;">
        <span style="font-size:14px;font-weight:700;color:#111827;">Total</span>
        <span style="font-size:18px;font-weight:900;color:#111827;">{format_money(total)}</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-top:6px;">
        <span style="font-size:13px;color:#6B7280;">Pagado</span>
        <span style="font-size:13px;color:#16A34A;font-weight:600;">{format_money(total_paid)}</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-top:4px;">
        <span style="font-size:13px;color:#6B7280;">Pendiente</span>
        <span style="font-size:14px;font-weight:700;{pending_style}">{format_money(pending)}</span>
    </div>
</div>

{note_section}

<!-- Footer -->
<div style="text-align:center;padding-top:16px;border-top:1px solid #E5E7EB;">
    <div style="font-size:11px;color:#9CA3AF;">Generado el {_format_date(datetime.now())} — Senshi Academy</div>
</div>

</div>
</body>
</html>"""

    return html


def generate_collection_account_receipt(account, items, receipt_number=None):
    account_id = account.get("id", 0)
    receipt_num = receipt_number or build_receipt_number(account_id)
    client_name = account.get("client_name", "")
    safe_name = _slugify(client_name)

    account_date = account.get("account_date", "")
    if hasattr(account_date, "strftime"):
        date_str = account_date.strftime("%Y-%m-%d")
    else:
        date_str = str(account_date)[:10] if account_date else datetime.now().strftime("%Y-%m-%d")

    HTML_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    html_filename = f"{receipt_num}_{safe_name}_{date_str}.html"
    pdf_filename = f"{receipt_num}_{safe_name}_{date_str}.pdf"

    html_path = HTML_OUTPUT_DIR / html_filename
    pdf_path = OUTPUT_DIR / pdf_filename

    html_content = build_collection_account_html(account, items, receipt_number=receipt_num)
    html_path.write_text(html_content, encoding="utf-8")

    pdf_ok = _html_to_pdf(html_path, pdf_path)

    return {
        "receipt_number": receipt_num,
        "html_path": str(html_path),
        "pdf_path": str(pdf_path) if pdf_ok else "",
        "pdf_generated": pdf_ok,
    }


def _html_to_pdf(html_path, pdf_path):
    try:
        from PyQt6.QtCore import QUrl, QEventLoop, QTimer
        from PyQt6.QtWebEngineCore import QWebEnginePage
        from PyQt6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            return False

        page = QWebEnginePage(app)
        _WEBENGINE_PAGES_GUARD.append(page)
        loop = QEventLoop()
        result = {"ok": False}

        def on_load_finished(ok):
            if not ok:
                loop.quit()
                return
            page.printToPdf(str(pdf_path))

        def on_pdf_finished(pdf_path_str, success):
            result["ok"] = success
            loop.quit()

        try:
            page.pdfPrintingFinished.connect(on_pdf_finished)
        except Exception:
            pass

        page.loadFinished.connect(on_load_finished)
        page.load(QUrl.fromLocalFile(str(html_path)))

        QTimer.singleShot(15000, loop.quit)
        loop.exec()

        def cleanup():
            try:
                if page in _WEBENGINE_PAGES_GUARD:
                    _WEBENGINE_PAGES_GUARD.remove(page)
                page.deleteLater()
            except Exception:
                pass

        QTimer.singleShot(3000, cleanup)

        return pdf_path.exists() and pdf_path.stat().st_size > 0

    except Exception as e:
        print(f"[CollectionAccountReceipt] PDF generation failed: {e}")
        return False


def open_file(path):
    path = str(path)
    if not os.path.exists(path):
        return
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        import subprocess
        subprocess.call(["open", path])
    else:
        import subprocess
        subprocess.call(["xdg-open", path])
