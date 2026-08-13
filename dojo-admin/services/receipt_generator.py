import os
import re
import unicodedata
import base64
from datetime import datetime
from pathlib import Path
from html import escape


_WEBENGINE_PAGES_GUARD = []

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = BASE_DIR / "assets" / "templates" / "receipt_template.html"
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


def _find_logo_path() -> Path | None:
    for candidate in _LOGO_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def _build_logo_html() -> str:
    logo_path = _find_logo_path()
    if logo_path is None:
        return "[ Logo ]"

    ext = logo_path.suffix.lower()
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
    }
    mime = mime_map.get(ext, "image/png")

    try:
        data = logo_path.read_bytes()
        b64 = base64.b64encode(data).decode("ascii")
        return f'<img src="data:{mime};base64,{b64}" alt="Logo Senshi">'
    except Exception:
        return "[ Logo ]"


def format_money(value):
    try:
        value = float(value or 0)
    except Exception:
        value = 0
    return "$" + f"{value:,.0f}".replace(",", ".")


def slugify_filename(value: str) -> str:
    value = str(value or "")
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s\-]", "", value)
    value = re.sub(r"[\s]+", "_", value.strip())
    value = re.sub(r"_+", "_", value)
    return value[:80] if value else "recibo"


def build_receipt_number(income_id: int) -> str:
    return f"R-{int(income_id):04d}"


def _extract_student_name(participants: list, income: dict) -> str:
    for p in (participants or []):
        expected = float(p.get("expected_amount", 0) or 0)
        paid = float(p.get("paid_amount", 0) or 0)
        pending = float(p.get("pending_amount", 0) or 0)
        if expected == 0 and paid == 0 and pending == 0:
            return p.get("display_name", "")
    return ""


def _format_date(income_date) -> str:
    if hasattr(income_date, "strftime"):
        return income_date.strftime("%d/%m/%Y")
    return str(income_date)[:10] if income_date else datetime.now().strftime("%d/%m/%Y")


def _escape(value) -> str:
    return escape(str(value or ""))


def _build_items_rows(items: list) -> str:
    rows = []
    for item in items:
        name = _escape(str(item.get("name", ""))[:50])
        qty = item.get("quantity", 1)
        price = float(item.get("unit_price", 0) or 0)
        subtotal = float(item.get("subtotal", 0) or 0)
        discount = float(item.get("discount", 0) or 0)

        discount_html = ""
        if discount > 0:
            discount_html = f' <span class="item-discount">Descuento aplicado: -{format_money(discount)}</span>'

        rows.append(
            "<tr>"
            f"<td>{name}{discount_html}</td>"
            f'<td class="tc">{qty}</td>'
            f'<td class="tr">{format_money(price)}</td>'
            f'<td class="tr">{format_money(subtotal)}</td>'
            "</tr>"
        )

    if not rows:
        rows.append(
            "<tr><td>&mdash;</td><td class=\"tc\">&mdash;</td>"
            "<td class=\"tr\">&mdash;</td><td class=\"tr\">&mdash;</td></tr>"
        )

    return "\n".join(rows)


def _build_observations_body(income: dict) -> str:
    note = income.get("note", "")
    agreement = income.get("agreement_note", "")

    parts = []
    if note:
        parts.append(_escape(note))
    if agreement:
        parts.append(_escape(agreement))

    if not parts:
        return '<div class="rc-obs-text">&mdash;</div>'

    return f'<div class="rc-obs-text">{"".join(f"<p>{p}</p>" for p in parts)}</div>'


def build_receipt_context(income: dict, items: list, participants: list, receipt_number: str = None) -> dict:
    payer_name = _escape(income.get("payer_name", ""))
    payer_doc = _escape(income.get("payer_document", "") or "")
    payer_phone = _escape(income.get("payer_phone", "") or "")

    student_name = _extract_student_name(participants, income)
    student_meta = (
        f'<span><strong>Estudiante:</strong> {_escape(student_name)}</span>'
        if student_name else ""
    )

    income_date = income.get("income_date", "")
    receipt_date = _format_date(income_date)

    total = float(income.get("total", 0) or 0)
    discount = float(income.get("discount", 0) or 0)
    subtotal = float(income.get("subtotal", 0) or 0)
    total_paid = float(income.get("total_paid", 0) or 0)
    pending = float(income.get("pending_amount", 0) or 0)

    payment_method = _escape(income.get("payment_method_name", "") or "—")
    destination_account = _escape(income.get("destination_account_name", "") or "—")

    return {
        "client_name": payer_name,
        "client_document": payer_doc,
        "client_phone": payer_phone,
        "student_meta": student_meta,
        "receipt_number": _escape(receipt_number or ""),
        "receipt_date": receipt_date,
        "total": format_money(total),
        "subtotal": format_money(subtotal),
        "discount": format_money(discount),
        "total_paid": format_money(total_paid),
        "pending_amount": format_money(pending),
        "payment_method": payment_method,
        "payment_date": receipt_date,
        "destination_account": destination_account,
        "items_rows": _build_items_rows(items),
        "observations_body": _build_observations_body(income),
        "logo_html": _build_logo_html(),
    }


def _render_template(template_html: str, context: dict) -> str:
    result = template_html
    for key, value in context.items():
        result = result.replace("{{ " + key + " }}", str(value))
        result = result.replace("{{" + key + "}}", str(value))

    if "{{" in result and "}}" in result:
        print("[ReceiptGenerator] Warning: unresolved placeholders in template")

    return result


def render_receipt_html(income: dict, items: list, participants: list, receipt_number: str = None, preview: bool = False) -> str:
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")

    template_html = TEMPLATE_PATH.read_text(encoding="utf-8")
    context = build_receipt_context(income, items, participants, receipt_number)
    rendered = _render_template(template_html, context)

    if preview:
        preview_css = """
        html, body {
            width: 100%;
            min-height: 100%;
            margin: 0 !important;
            padding: 0 !important;
            overflow-x: hidden !important;
            background: #222 !important;
        }

        body {
            display: flex !important;
            justify-content: center !important;
            align-items: flex-start !important;
            padding: 18px 0 !important;
        }

        .rc {
            width: 700px !important;
            transform: scale(0.68);
            transform-origin: top center;
            margin-bottom: -260px;
        }
        """
        rendered = rendered.replace("</style>", preview_css + "\n</style>")

    return rendered


def _html_to_pdf_qwebengine(html_path: Path, pdf_path: Path) -> bool:
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

        def cleanup_page():
            try:
                if page in _WEBENGINE_PAGES_GUARD:
                    _WEBENGINE_PAGES_GUARD.remove(page)
                page.deleteLater()
            except Exception:
                pass

        QTimer.singleShot(3000, cleanup_page)

        return pdf_path.exists() and pdf_path.stat().st_size > 0

    except Exception as e:
        print(f"[ReceiptGenerator] QWebEngine PDF failed: {e}")
        return False


def _html_to_pdf(html_path: Path, pdf_path: Path) -> bool:
    return _html_to_pdf_qwebengine(html_path, pdf_path)


def prepare_receipt_files(income: dict, items: list, participants: list) -> dict:
    income_id = income.get("id", 0)
    receipt_number = income.get("receipt_number") or build_receipt_number(income_id)

    payer_name = income.get("payer_name", "")
    safe_name = slugify_filename(payer_name)

    income_date = income.get("income_date", "")
    if hasattr(income_date, "strftime"):
        date_str = income_date.strftime("%Y-%m-%d")
    else:
        date_str = str(income_date)[:10] if income_date else datetime.now().strftime("%Y-%m-%d")

    HTML_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    html_filename = f"{receipt_number}_{safe_name}_{date_str}.html"
    pdf_filename = f"{receipt_number}_{safe_name}_{date_str}.pdf"

    html_path = HTML_OUTPUT_DIR / html_filename
    pdf_path = OUTPUT_DIR / pdf_filename

    rendered_html = render_receipt_html(
        income,
        items,
        participants,
        receipt_number=receipt_number,
        preview=False,
    )

    html_path.write_text(rendered_html, encoding="utf-8")

    return {
        "receipt_number": receipt_number,
        "html_path": str(html_path),
        "pdf_path": str(pdf_path),
    }


def generate_receipt(income: dict, items: list, participants: list) -> dict:
    return prepare_receipt_files(income, items, participants)
