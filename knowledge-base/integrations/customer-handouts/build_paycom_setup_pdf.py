#!/usr/bin/env python3
"""
Generate a Hera-branded PDF customer handout for the Paycom-side prep work
required before connecting Paycom to Hera.

Content source: paycom-setup-for-hera-integration.md (same folder)
Branding source: ../../../branding/brand-guidelines.md

Output: paycom-setup-for-hera-integration.pdf (same folder)
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ---------- Paths ----------
HERE = Path(__file__).parent
REPO = HERE.parent.parent.parent
LOGO_HORIZONTAL = REPO / "branding" / "logos" / "Hera Logo - Horizontal - No Tag Line-1.png"
FONTS_DIR = REPO / "branding" / "fonts"
OUTPUT_PDF = HERE / "paycom-setup-for-hera-integration.pdf"

# ---------- Hera colors (from branding/brand-guidelines.md) ----------
HERA_BLUE = HexColor("#0067bc")
HERA_BLUE_DARK = HexColor("#00509a")
HERA_BLUE_LIGHT = HexColor("#e8f2fb")
HERA_PINK = HexColor("#f9d2d9")
GREY_DARK = HexColor("#6c757d")
GREY_MID = HexColor("#e2e6ea")
GREY_LIGHT = HexColor("#f7f8fa")
NEAR_BLACK = HexColor("#1c2b3a")

# ---------- Font registration ----------
def register_fonts() -> tuple[str, str, str]:
    """Register Aglet Slab from branding/fonts. Falls back to Helvetica if unavailable."""
    try:
        pdfmetrics.registerFont(TTFont("AgletSlab", str(FONTS_DIR / "agletslab-regular.otf")))
        pdfmetrics.registerFont(TTFont("AgletSlab-Bold", str(FONTS_DIR / "agletslab-bold.otf")))
        pdfmetrics.registerFont(TTFont("AgletSlab-Semibold", str(FONTS_DIR / "agletslab-semibold.otf")))
        return "AgletSlab", "AgletSlab-Bold", "AgletSlab-Semibold"
    except Exception as e:  # pragma: no cover
        print(f"WARNING: could not load Aglet Slab fonts ({e}). Falling back to Helvetica.")
        return "Helvetica", "Helvetica-Bold", "Helvetica-Bold"


REGULAR, BOLD, SEMIBOLD = register_fonts()


# ---------- Paragraph styles ----------
def style(name: str, size: int, font: str = REGULAR, color=NEAR_BLACK,
          leading: float | None = None, space_before: int = 0, space_after: int = 0,
          left_indent: int = 0, alignment=TA_LEFT) -> ParagraphStyle:
    return ParagraphStyle(
        name=name,
        fontName=font,
        fontSize=size,
        leading=leading or size + 4,
        textColor=color,
        spaceBefore=space_before,
        spaceAfter=space_after,
        leftIndent=left_indent,
        alignment=alignment,
    )


TITLE = style("title", 26, BOLD, HERA_BLUE, leading=30, space_after=6)
SUBTITLE = style("subtitle", 12, REGULAR, GREY_DARK, leading=16, space_after=18)
H1 = style("h1", 16, BOLD, HERA_BLUE, leading=20, space_before=18, space_after=8)
H2 = style("h2", 13, SEMIBOLD, HERA_BLUE_DARK, leading=17, space_before=14, space_after=6)
BODY = style("body", 11, REGULAR, NEAR_BLACK, leading=15, space_after=8)
BULLET = style("bullet", 11, REGULAR, NEAR_BLACK, leading=15, left_indent=18, space_after=4)
SUB_BULLET = style("sub_bullet", 10.5, REGULAR, NEAR_BLACK, leading=14, left_indent=36, space_after=3)
CALLOUT = style("callout", 11, SEMIBOLD, HERA_BLUE_DARK, leading=15, space_after=6)
QUOTE = style("quote", 11.5, REGULAR, HERA_BLUE_DARK, leading=16, left_indent=14, space_after=8)
CODE = style("code", 11, BOLD, HERA_BLUE_DARK, leading=15)
FOOTER = style("footer", 8.5, REGULAR, GREY_DARK, leading=10)


# ---------- Page chrome ----------
def draw_header_footer(canvas, doc):
    canvas.saveState()

    # Header band: thin Hera Blue line at top
    canvas.setFillColor(HERA_BLUE)
    canvas.rect(0, LETTER[1] - 0.35 * inch, LETTER[0], 0.35 * inch, stroke=0, fill=1)

    # Logo top-left, sitting just below the band. Width tuned to feel present
    # without crowding the title. Aspect ratio of source PNG is ~2.735:1
    # (640x234 for "Hera Logo - Horizontal - No Tag Line-1.png").
    if LOGO_HORIZONTAL.exists():
        logo_w = 1.95 * inch
        logo_h = logo_w / 2.735
        img = Image(str(LOGO_HORIZONTAL), width=logo_w, height=logo_h)
        img.drawOn(canvas, 0.6 * inch, LETTER[1] - 0.5 * inch - logo_h)

    # Footer rule line
    canvas.setStrokeColor(GREY_MID)
    canvas.setLineWidth(0.5)
    canvas.line(0.6 * inch, 0.55 * inch, LETTER[0] - 0.6 * inch, 0.55 * inch)

    # Footer text
    canvas.setFont(REGULAR, 8.5)
    canvas.setFillColor(GREY_DARK)
    canvas.drawString(0.6 * inch, 0.35 * inch, "Powered by Hera Solutions, Inc.")
    canvas.drawRightString(
        LETTER[0] - 0.6 * inch, 0.35 * inch, f"Page {canvas.getPageNumber()}"
    )

    canvas.restoreState()


# ---------- Helpers ----------
def ip_box(ips: list[str]) -> Table:
    """A boxed display of the IP addresses in a Hera-blue-tinted callout."""
    rows = [[Paragraph(f"<b>{ip}</b>", CODE)] for ip in ips]
    tbl = Table(rows, colWidths=[6.6 * inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HERA_BLUE_LIGHT),
        ("BOX", (0, 0), (-1, -1), 1, HERA_BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return tbl


def step_header(num: int, title: str) -> Table:
    """A full-width Hera Blue bar with the step number and title."""
    label = f'<font color="white"><b>STEP {num}</b></font>'
    head = f'<font color="white"><b>&nbsp;&nbsp;{title}</b></font>'
    p = Paragraph(label + head, ParagraphStyle(
        name=f"step{num}",
        fontName=BOLD,
        fontSize=12,
        leading=16,
        textColor=white,
    ))
    tbl = Table([[p]], colWidths=[6.9 * inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HERA_BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    return tbl


def section_bar(title: str, color=HERA_BLUE_DARK) -> Table:
    p = Paragraph(f'<font color="white"><b>{title}</b></font>',
                  ParagraphStyle(name="sect", fontName=BOLD, fontSize=11, leading=15, textColor=white))
    tbl = Table([[p]], colWidths=[6.9 * inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROUNDEDCORNERS", [3, 3, 3, 3]),
    ]))
    return tbl


def bullet(text: str) -> Paragraph:
    return Paragraph(f"&bull;&nbsp;&nbsp;{text}", BULLET)


def sub_bullet(text: str) -> Paragraph:
    return Paragraph(f"&ndash;&nbsp;&nbsp;{text}", SUB_BULLET)


# ---------- Build the story ----------
def build_story() -> list:
    story: list = []

    # Title block. The larger topMargin already clears the bigger logo —
    # this small spacer just adds breathing room before the title on page 1.
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Paycom Setup for Your Hera Integration", TITLE))
    story.append(Paragraph(
        "What you will do on the Paycom side before we connect Paycom to Hera.",
        SUBTITLE,
    ))

    # Intro
    story.append(Paragraph(
        "This guide is for Hera customers who use Paycom for payroll and want to connect "
        "Paycom to Hera. Three steps must happen on the Paycom side before Hera can "
        "establish the connection. This document walks you through those three steps.",
        BODY,
    ))
    story.append(Spacer(1, 0.1 * inch))

    # Step 1
    story.append(KeepTogether([
        step_header(1, "Request API access from Paycom"),
        Spacer(1, 0.12 * inch),
        Paragraph(
            "Reach out to your Paycom account representative and let them know you would "
            "like to enable API access. When they ask what the access is for, you can say:",
            BODY,
        ),
        Paragraph('"I want a vendor to access my employee data from Paycom."', QUOTE),
        Paragraph(
            "Your Paycom representative will then walk you through their standard approval "
            "process. Expect the following:",
            BODY,
        ),
        bullet("Paycom may ask you to sign an NDA before sharing documentation."),
        bullet(
            "A discovery call will be scheduled with the Paycom Automation team and your "
            "technical resources to talk through what is available and the technical side "
            "of leveraging the API."
        ),
        bullet(
            "You will review and sign a Paycom Proposal and MSA to add API access to your "
            "existing Paycom suite."
        ),
        Spacer(1, 0.08 * inch),
        Paragraph(
            "This step is handled entirely between you and Paycom. Plan for a few business "
            "days. You cannot move to Step 2 until Paycom approves API access.",
            BODY,
        ),
    ]))
    story.append(Spacer(1, 0.18 * inch))

    # Step 2
    story.append(KeepTogether([
        step_header(2, "Receive your Paycom API credentials"),
        Spacer(1, 0.12 * inch),
        Paragraph(
            "Once Paycom approves your API access, your Paycom representative will provide:",
            BODY,
        ),
        bullet("<b>API SID</b> (System ID)"),
        bullet("<b>API Token</b>"),
        bullet("<b>Paycom API Documentation</b>"),
        Spacer(1, 0.04 * inch),
        Paragraph(
            "Keep these in a secure location. You will need both the SID and the Token "
            "in the final connection step in Hera.",
            BODY,
        ),
    ]))
    story.append(Spacer(1, 0.18 * inch))

    # Step 3
    story.append(KeepTogether([
        step_header(3, "Allowlist Hera's IP addresses in Paycom"),
        Spacer(1, 0.12 * inch),
        Paragraph(
            "Paycom only allows API access from specific, pre-approved IP addresses. "
            "Before the connection can succeed, your Paycom representative needs to add "
            "Hera's IP addresses to your allowlist.",
            BODY,
        ),
        Paragraph(
            "Send your Paycom representative the following three IP addresses and ask "
            "them to add all of them:",
            BODY,
        ),
        Spacer(1, 0.06 * inch),
        ip_box(["13.59.40.132", "3.136.219.255", "18.216.194.37"]),
        Spacer(1, 0.1 * inch),
        Paragraph(
            "If any of these IPs are missing, the connection will fail when you try to "
            "complete it in Hera. Confirm directly with your Paycom representative that "
            "all three have been added before moving on.",
            BODY,
        ),
    ]))
    story.append(Spacer(1, 0.25 * inch))

    # Reference link + sign-off. Uses a Hera-hosted share URL so we get a
    # clean, short link with no URL-encoded characters — older HubSpot-hosted
    # URL had %20 spaces that some PDF readers mangled on click.
    link_url = "https://files.hera.run/share/V4qy2ypZ9LTmFCXEofOw"
    ref_style = ParagraphStyle(
        name="reference",
        fontName=REGULAR,
        fontSize=11,
        leading=15,
        textColor=NEAR_BLACK,
        spaceAfter=8,
    )
    signoff_style = ParagraphStyle(
        name="signoff",
        fontName=SEMIBOLD,
        fontSize=11,
        leading=15,
        textColor=HERA_BLUE,
        spaceBefore=10,
    )
    story.append(KeepTogether([
        Paragraph("Reference", H1),
        Paragraph(
            f'For Paycom\'s official process documentation, see the '
            f'<a href="{link_url}" color="#0067bc"><u>Paycom Client API Checklist</u></a>.',
            ref_style,
        ),
        Paragraph("For additional help, reach out to your Hera contact.", signoff_style),
    ]))

    return story


def build_pdf() -> None:
    doc = BaseDocTemplate(
        str(OUTPUT_PDF),
        pagesize=LETTER,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=1.45 * inch,
        bottomMargin=0.75 * inch,
        title="Paycom Setup for Your Hera Integration",
        author="Hera Solutions, Inc.",
        subject="Customer-facing setup guide for Paycom prep work",
    )

    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        id="main",
    )
    page = PageTemplate(id="main", frames=[frame], onPage=draw_header_footer)
    doc.addPageTemplates([page])

    doc.build(build_story())
    print(f"Wrote {OUTPUT_PDF}")


if __name__ == "__main__":
    build_pdf()
