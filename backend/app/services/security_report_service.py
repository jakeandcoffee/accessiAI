import io
from collections import defaultdict

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BG_DARK = colors.Color(0.04, 0.04, 0.08)
BG_CARD = colors.Color(0.08, 0.08, 0.14)
BG_ROW_ALT = colors.Color(0.06, 0.06, 0.11)
BORDER_COLOR = colors.Color(1, 1, 1, 0.08)
TEXT_PRIMARY = colors.Color(0.89, 0.91, 0.94)
TEXT_MUTED = colors.Color(0.55, 0.58, 0.65)

SEVERITY_COLORS = {
    "critical": colors.Color(0.95, 0.28, 0.28),
    "high": colors.Color(0.96, 0.55, 0.28),
    "medium": colors.Color(0.96, 0.80, 0.28),
    "low": colors.Color(0.28, 0.61, 0.96),
    "info": colors.Color(0.55, 0.56, 0.65),
}

CATEGORY_COLORS = {
    "http-headers": colors.Color(0.47, 0.47, 0.95),
    "ssl-tls": colors.Color(0.30, 0.75, 0.45),
    "cookies": colors.Color(0.95, 0.55, 0.15),
    "content-security": colors.Color(0.95, 0.28, 0.28),
    "info-disclosure": colors.Color(0.68, 0.45, 0.95),
}

CATEGORY_LABELS = {
    "http-headers": "HTTP Security Headers",
    "ssl-tls": "SSL / TLS",
    "cookies": "Cookie Security",
    "content-security": "Content Security",
    "info-disclosure": "Information Disclosure",
}

SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _score_color(score: int) -> colors.Color:
    if score >= 90:
        return colors.Color(0.20, 0.85, 0.45)
    if score >= 75:
        return colors.Color(0.45, 0.75, 0.45)
    if score >= 50:
        return colors.Color(0.95, 0.80, 0.15)
    return colors.Color(0.95, 0.28, 0.28)


def _on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG_DARK)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.restoreState()


def generate_security_pdf_report(url: str, results: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
    )
    styles = getSampleStyleSheet()
    page_w = A4[0] - 1.2 * inch

    s_title = ParagraphStyle(
        "DarkTitle", parent=styles["Title"],
        fontSize=24, textColor=TEXT_PRIMARY, spaceAfter=4,
    )
    s_subtitle = ParagraphStyle(
        "DarkSubtitle", parent=styles["Normal"],
        fontSize=10, textColor=TEXT_MUTED, spaceAfter=16,
    )
    s_heading = ParagraphStyle(
        "DarkHeading", parent=styles["Heading2"],
        fontSize=14, textColor=TEXT_PRIMARY, spaceBefore=20, spaceAfter=10,
    )
    s_body = ParagraphStyle(
        "DarkBody", parent=styles["BodyText"],
        fontSize=9, textColor=TEXT_PRIMARY, leading=13,
    )
    s_cat_heading = ParagraphStyle(
        "CatHeading", parent=styles["Heading3"],
        fontSize=12, spaceBefore=18, spaceAfter=8,
    )
    s_disclaimer = ParagraphStyle(
        "Disclaimer", parent=s_body,
        fontSize=7, textColor=TEXT_MUTED, spaceBefore=20,
    )

    elements = []

    # ── Header ──
    elements.append(Paragraph(
        'Accessi<font color="#9d9dff">AI</font> — Security Scan Report',
        s_title,
    ))

    scan_date = results.get("scan_started_at", "N/A")
    if scan_date != "N/A":
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(scan_date)
            scan_date = dt.strftime("%B %d, %Y at %H:%M UTC")
        except Exception:
            pass

    elements.append(Paragraph(f"Generated on {scan_date}", s_subtitle))
    elements.append(HRFlowable(
        width="100%", thickness=0.5,
        color=colors.Color(1, 1, 1, 0.08),
        spaceAfter=16,
    ))

    # ── Summary Cards ──
    score = results.get("security_score", 0)
    sc = _score_color(score)
    total = results.get("total_findings", 0)

    summary_data = [[
        Paragraph(f'<font color="#8b8fa5">Target URL</font><br/><font size="9"><b>{_esc(url)}</b></font>', s_body),
        Paragraph(f'<font color="#8b8fa5">Security Score</font><br/><font size="18" color="#{sc.hexval()[2:]}"><b>{score}</b></font><font size="9" color="#8b8fa5"> / 100</font>', s_body),
        Paragraph(f'<font color="#8b8fa5">Findings</font><br/><font size="14"><b>{total}</b></font>', s_body),
    ]]

    col_w = page_w / 3
    summary_table = Table(summary_data, colWidths=[col_w] * 3)
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG_CARD),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("PADDING", (0, 0), (-1, -1), 12),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 16))

    # ── Severity Breakdown ──
    all_findings = results.get("findings", [])
    severity_breakdown: dict[str, int] = {}
    for f in all_findings:
        severity_breakdown[f["severity"]] = severity_breakdown.get(f["severity"], 0) + 1
    if severity_breakdown:
        elements.append(Paragraph("Severity Breakdown", s_heading))
        sev_header = [
            Paragraph('<font color="#8b8fa5"><b>Severity</b></font>', s_body),
            Paragraph('<font color="#8b8fa5"><b>Count</b></font>', s_body),
            Paragraph('<font color="#8b8fa5"><b>Distribution</b></font>', s_body),
        ]
        total_v = sum(severity_breakdown.values()) or 1
        sev_rows = [sev_header]
        for sev in SEVERITY_ORDER:
            count = severity_breakdown.get(sev, 0)
            if count == 0:
                continue
            pct = count / total_v * 100
            sc_ = SEVERITY_COLORS.get(sev, TEXT_MUTED)
            hex_c = sc_.hexval()[2:]
            bar = f'<font color="#{hex_c}">{"█" * max(1, int(pct / 3))}</font> <font color="#8b8fa5">{pct:.0f}%</font>'
            sev_rows.append([
                Paragraph(f'<font color="#{hex_c}"><b>{sev.upper()}</b></font>', s_body),
                Paragraph(f'<b>{count}</b>', s_body),
                Paragraph(bar, s_body),
            ])

        sev_table = Table(sev_rows, colWidths=[1.5 * inch, 1 * inch, page_w - 2.5 * inch])
        sev_style = [
            ("BACKGROUND", (0, 0), (-1, 0), BG_CARD),
            ("BACKGROUND", (0, 1), (-1, -1), BG_CARD),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, BORDER_COLOR),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ]
        for r in range(2, len(sev_rows), 2):
            sev_style.append(("BACKGROUND", (0, r), (-1, r), BG_ROW_ALT))
        sev_table.setStyle(TableStyle(sev_style))
        elements.append(sev_table)
        elements.append(Spacer(1, 10))

    # ── Category Overview ──
    categories = results.get("categories", [])
    if categories:
        elements.append(Paragraph("Category Overview", s_heading))
        cat_header = [
            Paragraph('<font color="#8b8fa5"><b>Category</b></font>', s_body),
            Paragraph('<font color="#8b8fa5"><b>Issues</b></font>', s_body),
            Paragraph('<font color="#8b8fa5"><b>Critical</b></font>', s_body),
            Paragraph('<font color="#8b8fa5"><b>High</b></font>', s_body),
        ]
        cat_rows = [cat_header]

        for cat_data in categories:
            cat_findings = cat_data.get("findings", [])
            cat_name = cat_data.get("name", "Unknown")
            cat_key = next((k for k, v in CATEGORY_LABELS.items() if v == cat_name), "")
            cc = CATEGORY_COLORS.get(cat_key, TEXT_MUTED)
            hex_c = cc.hexval()[2:]
            crit = sum(1 for f in cat_findings if f["severity"] == "critical")
            high = sum(1 for f in cat_findings if f["severity"] == "high")
            crit_hex = SEVERITY_COLORS["critical"].hexval()[2:]
            high_hex = SEVERITY_COLORS["high"].hexval()[2:]

            cat_rows.append([
                Paragraph(f'<font color="#{hex_c}"><b>{_esc(cat_name)}</b></font>', s_body),
                Paragraph(f'<b>{len(cat_findings)}</b>', s_body),
                Paragraph(f'<font color="#{crit_hex}">{crit}</font>' if crit else '<font color="#8b8fa5">0</font>', s_body),
                Paragraph(f'<font color="#{high_hex}">{high}</font>' if high else '<font color="#8b8fa5">0</font>', s_body),
            ])

        cat_table = Table(cat_rows, colWidths=[page_w * 0.45, page_w * 0.18, page_w * 0.18, page_w * 0.19])
        cat_style = [
            ("BACKGROUND", (0, 0), (-1, 0), BG_CARD),
            ("BACKGROUND", (0, 1), (-1, -1), BG_CARD),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, BORDER_COLOR),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ]
        for r in range(2, len(cat_rows), 2):
            cat_style.append(("BACKGROUND", (0, r), (-1, r), BG_ROW_ALT))
        cat_table.setStyle(TableStyle(cat_style))
        elements.append(cat_table)
        elements.append(Spacer(1, 10))

    # ── Detailed Findings by Category ──
    if categories:
        elements.append(Paragraph("Detailed Findings", s_heading))

        for cat_data in categories:
            cat_findings = cat_data.get("findings", [])
            label = cat_data.get("name", "Unknown")
            cat_key = next((k for k, v in CATEGORY_LABELS.items() if v == label), "")
            cc = CATEGORY_COLORS.get(cat_key, TEXT_MUTED)

            elements.append(HRFlowable(
                width="100%", thickness=1.5,
                color=cc,
                spaceBefore=14, spaceAfter=4,
            ))
            cat_title = ParagraphStyle(
                f"Cat_{cat}", parent=s_cat_heading,
                textColor=cc,
            )
            elements.append(Paragraph(
                f'{_esc(label)} <font size="9" color="#8b8fa5">({len(cat_findings)} issues)</font>',
                cat_title,
            ))

            for i, f in enumerate(cat_findings, 1):
                sc_ = SEVERITY_COLORS.get(f["severity"], TEXT_MUTED)
                sc_hex = sc_.hexval()[2:]

                row_data = [[
                    Paragraph(
                        f'<font size="9"><b>{i}.</b></font> '
                        f'<font size="9"><b>{_esc(f["title"])}</b></font>',
                        s_body,
                    ),
                    Paragraph(
                        f'<font size="8" color="#{sc_hex}"><b> {f["severity"].upper()} </b></font>',
                        ParagraphStyle("SevBadge", parent=s_body, alignment=TA_RIGHT),
                    ),
                ]]
                vt = Table(row_data, colWidths=[page_w * 0.75, page_w * 0.25])
                vt.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), BG_CARD),
                    ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                    ("PADDING", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("ROUNDEDCORNERS", [4, 4, 0, 0]),
                ]))
                elements.append(vt)

                detail_parts = [f'<font color="#e2e8f0">{_esc(f["description"])}</font>']
                if f.get("recommendation"):
                    detail_parts.append(f'<br/><font color="#8b8fa5"><b>Fix:</b> {_esc(f["recommendation"])}</font>')
                if f.get("details"):
                    detail_parts.append(f'<br/><font color="#7878cc">{_esc(f["details"][:300])}</font>')

                dt_data = [[Paragraph("".join(detail_parts), s_body)]]
                dt = Table(dt_data, colWidths=[page_w])
                dt.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), BG_ROW_ALT),
                    ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                    ("PADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("ROUNDEDCORNERS", [0, 0, 4, 4]),
                ]))
                elements.append(dt)
                elements.append(Spacer(1, 8))

    # ── Footer ──
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(
        width="100%", thickness=0.5,
        color=BORDER_COLOR,
        spaceAfter=10,
    ))
    elements.append(Paragraph(
        "Generated by AccessiAI. Automated security scans detect common misconfigurations but cannot "
        "guarantee full security. Professional penetration testing is recommended for comprehensive assessment.",
        s_disclaimer,
    ))

    doc.build(elements, onFirstPage=_on_page, onLaterPages=_on_page)
    buffer.seek(0)
    return buffer
