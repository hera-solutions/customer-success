"""
Generate a Hera Communication Export PDF from a DynamoDB messages CSV.

Follows the process documented in reporting/pdf-generation-process.md.

Usage:
    python3 generate_communication_pdf.py <input_csv> <output_pdf> \
        --name "Jodi Lee Montoya" --dsp "Merica Delivery Service" --tz Eastern
"""

import argparse
import csv
import os
import re
import sys
from datetime import datetime, timedelta, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


HERA_BLUE = colors.HexColor("#0067bc")
HERA_BLUE_DARK = colors.HexColor("#00509a")
INCOMING_BG = colors.HexColor("#e8f2fb")
ALT_ROW = colors.HexColor("#fafafa")
GREY_DARK = colors.HexColor("#6c757d")
NEAR_BLACK = colors.HexColor("#1c2b3a")
GRID = colors.HexColor("#e2e6ea")

LOGO_PATH = (
    "/Users/johnjm/Library/Mobile Documents/com~apple~CloudDocs/"
    "Hera Solutions/Marketing - Conference/Logos LATEST/"
    "Black Circle Removed/Hera Logo - Horizontal-1.png"
)

HERA_ADDRESS = "4062 Peachtree Rd NE STE A556, Atlanta, GA 30319"
HERA_PHONE = "747.307.0143"
HERA_LEGAL_NAME = "Hera Solutions Inc"


# --------------------------------------------------------------------------- #
# Timezone conversion (manual DST, no pytz)
# --------------------------------------------------------------------------- #

def _second_sunday_march(year: int) -> datetime:
    d = datetime(year, 3, 1, 2, 0)
    while d.weekday() != 6:
        d += timedelta(days=1)
    return d + timedelta(days=7)


def _first_sunday_november(year: int) -> datetime:
    d = datetime(year, 11, 1, 2, 0)
    while d.weekday() != 6:
        d += timedelta(days=1)
    return d


def _is_us_dst(local_naive: datetime) -> bool:
    """Return True if the given local-naive datetime falls inside US DST."""
    start = _second_sunday_march(local_naive.year)
    end = _first_sunday_november(local_naive.year)
    return start <= local_naive < end


def convert_utc(iso_utc: str, tz: str) -> datetime:
    """Convert ISO 8601 UTC timestamp to local datetime (naive) in tz.

    tz is "Eastern" or "Pacific".
    """
    dt = datetime.strptime(iso_utc.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S.%f%z")
    dt_utc = dt.astimezone(timezone.utc).replace(tzinfo=None)
    # Try DST offset first
    offset_dst = {"Eastern": -4, "Pacific": -7}[tz]
    offset_std = {"Eastern": -5, "Pacific": -8}[tz]
    candidate_dst = dt_utc + timedelta(hours=offset_dst)
    if _is_us_dst(candidate_dst):
        return candidate_dst
    return dt_utc + timedelta(hours=offset_std)


def fmt_local(dt: datetime, tz: str) -> str:
    label = "ET" if tz == "Eastern" else "PT"
    hour = dt.hour % 12 or 12
    ampm = "AM" if dt.hour < 12 else "PM"
    return f"{dt.month}/{dt.day}/{dt.year} {hour}:{dt.minute:02d} {ampm} {label}"


# --------------------------------------------------------------------------- #
# Field cleaning
# --------------------------------------------------------------------------- #

def clean_phone(raw: str) -> str:
    """Normalize any stored phone format to (xxx) xxx-xxxx.

    Source data is inconsistent: some rows store "+17605905980", some
    "7605905980", some already "(760) 590-5980". Strip to digits, drop a
    leading US country code, then reformat. If the result is not a standard
    10-digit US number, fall back to the raw value untouched.
    """
    if not raw:
        return ""
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
    return raw.strip().lstrip("'")


def clean_body(text: str) -> str:
    if text is None:
        return ""
    s = text
    # Strip surrounding double-quote wrapping that DynamoDB CSV sometimes adds
    if s.startswith('"') and s.endswith('"') and len(s) >= 2:
        s = s[1:-1]
    # Replace literal "\n" sequences and real newlines with the line-break marker
    # Normalize all line-break sequences (literal "\n" from CSV escaping,
    # CRLF, plain LF) into a single newline character.
    s = s.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\r\n", "\n")
    # Collapse runs of 3+ newlines down to a single blank line
    s = re.sub(r"\n{3,}", "\n\n", s)
    # Collapse spaces/tabs within a line
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s.strip()


def is_incoming(row: dict) -> bool:
    return (row.get("channelType") or "").strip().upper() == "RESPONSE"


# --------------------------------------------------------------------------- #
# PDF building
# --------------------------------------------------------------------------- #

def build_pdf(rows, out_path, associate, dsp, tz):
    page_w, page_h = landscape(letter)  # 11 x 8.5
    margin = 0.5 * inch
    usable = page_w - 2 * margin

    doc = BaseDocTemplate(
        out_path,
        pagesize=landscape(letter),
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
        title=f"{associate} — Communication Export",
        author="Hera Solutions Inc",
    )

    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=NEAR_BLACK,
    )
    body_in = ParagraphStyle("body_in", parent=body, textColor=HERA_BLUE_DARK)
    head_lg = ParagraphStyle(
        "head_lg",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=16,
        textColor=NEAR_BLACK,
    )
    head_sm = ParagraphStyle(
        "head_sm",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        textColor=GREY_DARK,
    )

    # ----- Header band (logo left, title + meta block right) ----- #
    header_height = 1.15 * inch
    logo_w = 1.40 * inch
    logo_h = 0.95 * inch

    def draw_header(c: pdfcanvas.Canvas, _doc):
        c.saveState()
        top = page_h - margin
        # Logo, top-left
        if os.path.exists(LOGO_PATH):
            try:
                c.drawImage(
                    LOGO_PATH,
                    margin,
                    top - logo_h,
                    width=logo_w,
                    height=logo_h,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception:
                pass

        # Text block to the right of the logo
        text_x = margin + logo_w + 0.20 * inch
        # Title
        y = top - 0.30 * inch
        c.setFillColor(NEAR_BLACK)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(text_x, y, "Export of Communications")
        # Associate | DSP
        y -= 16
        c.setFillColor(NEAR_BLACK)
        c.setFont("Helvetica", 11)
        c.drawString(text_x, y, f"{associate}   |   {dsp}")
        # Hera address line
        y -= 14
        c.setFillColor(GREY_DARK)
        c.setFont("Helvetica", 10)
        c.drawString(
            text_x,
            y,
            f"{HERA_LEGAL_NAME}   |   {HERA_ADDRESS}   |   {HERA_PHONE}",
        )
        # Support email
        y -= 13
        c.setFillColor(HERA_BLUE_DARK)
        c.setFont("Helvetica", 10)
        c.drawString(text_x, y, "support@hera.app")

        # Hera Blue rule under the header band
        rule_y = top - header_height + 0.05 * inch
        c.setStrokeColor(HERA_BLUE)
        c.setLineWidth(3)
        c.line(margin, rule_y, page_w - margin, rule_y)

        # Footer
        c.setFillColor(GREY_DARK)
        c.setFont("Helvetica", 8)
        c.drawString(margin, margin - 0.20 * inch, "Powered by Hera Solutions Inc")
        c.drawRightString(
            page_w - margin,
            margin - 0.20 * inch,
            f"Page {c.getPageNumber()}",
        )
        # Thin rule above footer
        c.setStrokeColor(GRID)
        c.setLineWidth(0.5)
        c.line(margin, margin - 0.10 * inch, page_w - margin, margin - 0.10 * inch)
        c.restoreState()

    frame = Frame(
        margin,
        margin,
        usable,
        page_h - 2 * margin - header_height,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )
    template = PageTemplate(id="main", frames=[frame], onPage=draw_header)
    doc.addPageTemplates([template])

    # ----- Table data ----- #
    col_headers = [
        "Sent",
        "Message",
        "Number",
        "SMS Status",
        "Email",
        "Email Status",
    ]
    # Widths (inches) per process doc: 1.35 | rem | 1.05 | 0.9 | 1.85 | 0.9
    fixed = (1.35 + 1.05 + 0.9 + 1.85 + 0.9) * inch
    text_col_w = usable - fixed
    col_widths = [
        1.35 * inch,
        text_col_w,
        1.05 * inch,
        0.9 * inch,
        1.85 * inch,
        0.9 * inch,
    ]

    def message_para(text: str, style: ParagraphStyle) -> Paragraph:
        # Escape XML chars first, then turn real newlines into <br/> so
        # ReportLab renders line breaks instead of collapsing whitespace.
        return Paragraph(_para_escape(text).replace("\n", "<br/>"), style)

    table_data = [col_headers]
    incoming_idx = []
    for i, r in enumerate(rows, start=1):
        if r["incoming"]:
            incoming_idx.append(i)
            table_data.append([
                fmt_local(r["sent_dt"], tz),
                message_para(r["body"], body_in),
                "Incoming",
                "Incoming",
                "Incoming",
                "Incoming",
            ])
        else:
            table_data.append([
                fmt_local(r["sent_dt"], tz),
                message_para(r["body"], body),
                r["number"],
                r["sms_status"],
                r["email"],
                r["email_status"],
            ])

    style_cmds = [
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), HERA_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        # Body
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("VALIGN", (0, 1), (-1, -1), "TOP"),
        ("TEXTCOLOR", (0, 1), (-1, -1), NEAR_BLACK),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, GRID),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ALT_ROW]),
    ]
    for i in incoming_idx:
        style_cmds.append(("BACKGROUND", (0, i), (-1, i), INCOMING_BG))
        style_cmds.append(("TEXTCOLOR", (0, i), (-1, i), HERA_BLUE_DARK))
        style_cmds.append(("FONTNAME", (0, i), (-1, i), "Helvetica-Oblique"))

    # splitInRow=1 lets an oversized message cell break across pages; without it
    # a single row taller than the frame raises a LayoutError.
    table = Table(table_data, colWidths=col_widths, repeatRows=1, splitInRow=1)
    table.setStyle(TableStyle(style_cmds))

    story = [table]
    doc.build(story)


def _para_escape(text: str) -> str:
    """Escape characters that ReportLab Paragraph treats as XML/HTML."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# --------------------------------------------------------------------------- #
# CSV ingestion
# --------------------------------------------------------------------------- #

def load_rows(csv_path: str, tz: str):
    out = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            created = (row.get("createdAt") or "").strip()
            if not created:
                continue
            sent_dt = convert_utc(created, tz)
            incoming = is_incoming(row)
            body = clean_body(row.get("bodyText") or "")
            out.append({
                "sent_iso": created,
                "sent_dt": sent_dt,
                "body": body,
                "number": clean_phone(row.get("destinationNumber") or ""),
                "sms_status": (row.get("smsStatus") or "").strip(),
                "email": (row.get("destinationEmail") or "").strip(),
                "email_status": (row.get("emailStatus") or "").strip(),
                "incoming": incoming,
            })
    out.sort(key=lambda r: r["sent_iso"])
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input_csv")
    p.add_argument("output_pdf")
    p.add_argument("--name", required=True)
    p.add_argument("--dsp", required=True)
    p.add_argument("--tz", choices=["Eastern", "Pacific"], required=True)
    args = p.parse_args()

    rows = load_rows(args.input_csv, args.tz)
    if not rows:
        sys.exit("No rows in input CSV.")
    build_pdf(rows, args.output_pdf, args.name, args.dsp, args.tz)
    print(f"Wrote {args.output_pdf} ({len(rows)} messages).")


if __name__ == "__main__":
    main()
