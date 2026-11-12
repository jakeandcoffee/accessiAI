import io
from collections import defaultdict
from collections.abc import Sequence

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

from app.models.scan import Scan
from app.models.violation import Violation


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# Dark theme palette
BG_DARK = colors.Color(0.04, 0.04, 0.08)
BG_CARD = colors.Color(0.08, 0.08, 0.14)
BG_ROW_ALT = colors.Color(0.06, 0.06, 0.11)
BORDER_COLOR = colors.Color(1, 1, 1, 0.08)
TEXT_PRIMARY = colors.Color(0.89, 0.91, 0.94)
TEXT_MUTED = colors.Color(0.55, 0.58, 0.65)
BRAND = colors.Color(0.47, 0.47, 0.95)
BRAND_LIGHT = colors.Color(0.62, 0.62, 1.0)

IMPACT_COLORS = {
    "critical": colors.Color(0.95, 0.28, 0.28),
    "serious": colors.Color(0.95, 0.55, 0.15),
    "moderate": colors.Color(0.95, 0.80, 0.15),
    "minor": colors.Color(0.45, 0.75, 0.45),
}

IMPACT_BG = {
    "critical": colors.Color(0.95, 0.28, 0.28, 0.15),
    "serious": colors.Color(0.95, 0.55, 0.15, 0.12),
    "moderate": colors.Color(0.95, 0.80, 0.15, 0.10),
    "minor": colors.Color(0.45, 0.75, 0.45, 0.10),
}

PHASE_CONFIG = {
    "data-quality": {
        "order": 1,
        "label": "Phase 1 — Data Quality & Measurement",
        "color": colors.Color(0.95, 0.55, 0.15),
        "bg": colors.Color(0.95, 0.55, 0.15, 0.12),
    },
    "accessibility": {
        "order": 2,
        "label": "Phase 2 — Accessibility (WCAG 2.2 AA)",
        "color": colors.Color(0.95, 0.28, 0.28),
        "bg": colors.Color(0.95, 0.28, 0.28, 0.12),
    },
    "geo": {
        "order": 3,
        "label": "Phase 3 — GEO (Generative Engine Optimization)",
        "color": colors.Color(0.68, 0.45, 0.95),
        "bg": colors.Color(0.68, 0.45, 0.95, 0.12),
    },
    "ux-performance": {
        "order": 4,
        "label": "Phase 4 — UX & Performance",
        "color": colors.Color(0.38, 0.58, 0.95),
        "bg": colors.Color(0.38, 0.58, 0.95, 0.12),
    },
    "seo": {
        "order": 5,
        "label": "Phase 5 — SEO & Discoverability",
        "color": colors.Color(0.30, 0.75, 0.45),
        "bg": colors.Color(0.30, 0.75, 0.45, 0.12),
    },
    "baseline": {
        "order": 6,
        "label": "Phase 6 — Baseline & Measurement",
        "color": colors.Color(0.25, 0.75, 0.82),
        "bg": colors.Color(0.25, 0.75, 0.82, 0.12),
    },
}

PHASE_ORDER = ["data-quality", "accessibility", "geo", "ux-performance", "seo", "baseline"]


def _score_color(score: float) -> colors.Color:
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


SECURITY_SEVERITY_COLORS = {
    "critical": colors.Color(0.95, 0.28, 0.28),
    "high": colors.Color(0.96, 0.55, 0.28),
    "medium": colors.Color(0.96, 0.80, 0.28),
    "low": colors.Color(0.28, 0.61, 0.96),
    "info": colors.Color(0.55, 0.56, 0.65),
}

SECURITY_CATEGORY_COLORS = {
    "HTTP Security Headers": colors.Color(0.47, 0.47, 0.95),
    "SSL / TLS": colors.Color(0.30, 0.75, 0.45),
    "Cookie Security": colors.Color(0.95, 0.55, 0.15),
    "Content Security": colors.Color(0.95, 0.28, 0.28),
    "Information Disclosure": colors.Color(0.68, 0.45, 0.95),
}

SECURITY_SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]


def generate_pdf_report(
    scan: Scan,
    violations: Sequence[Violation],
    severity_breakdown: dict[str, int],
    security_results: dict | None = None,
) -> io.BytesIO:
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

    # --- Styles ---
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
    s_phase_heading = ParagraphStyle(
        "PhaseHeading", parent=styles["Heading3"],
        fontSize=12, spaceBefore=18, spaceAfter=8,
    )
    s_body = ParagraphStyle(
        "DarkBody", parent=styles["BodyText"],
        fontSize=9, textColor=TEXT_PRIMARY, leading=13,
    )
    s_body_muted = ParagraphStyle(
        "DarkBodyMuted", parent=s_body,
        textColor=TEXT_MUTED, fontSize=8,
    )
    s_code = ParagraphStyle(
        "DarkCode", parent=s_body,
        fontName="Courier", fontSize=7.5, textColor=TEXT_MUTED, leftIndent=12, leading=10,
    )
    s_label = ParagraphStyle(
        "Label", parent=s_body,
        fontSize=8, textColor=TEXT_MUTED,
    )
    s_value = ParagraphStyle(
        "Value", parent=s_body,
        fontSize=11, textColor=TEXT_PRIMARY, fontName="Helvetica-Bold",
    )
    s_score_big = ParagraphStyle(
        "ScoreBig", parent=s_body,
        fontSize=32, fontName="Helvetica-Bold", alignment=TA_CENTER,
    )
    s_center = ParagraphStyle(
        "Center", parent=s_body,
        alignment=TA_CENTER, fontSize=8, textColor=TEXT_MUTED,
    )
    s_disclaimer = ParagraphStyle(
        "Disclaimer", parent=s_body,
        fontSize=7, textColor=TEXT_MUTED, spaceBefore=20,
    )

    elements = []

    # ── Header ──
    elements.append(Paragraph(
        'Accessi<font color="#9d9dff">AI</font> — Site Audit Report',
        s_title,
    ))
    elements.append(Paragraph(
        f"Generated on {scan.scan_started_at.strftime('%B %d, %Y at %H:%M UTC') if scan.scan_started_at else 'N/A'}",
        s_subtitle,
    ))

    elements.append(HRFlowable(
        width="100%", thickness=0.5,
        color=colors.Color(1, 1, 1, 0.08),
        spaceAfter=16,
    ))

    # ── Summary Cards Row ──
    score = scan.accessibility_score if scan.accessibility_score is not None else 0
    sc = _score_color(score)

    summary_data = [[
        Paragraph(f'<font color="#8b8fa5">Website</font><br/><font size="11"><b>{_esc(scan.website.name)}</b></font>', s_body),
        Paragraph(f'<font color="#8b8fa5">URL</font><br/><font size="9">{_esc(scan.website.url)}</font>', s_body),
        Paragraph(f'<font color="#8b8fa5">Violations</font><br/><font size="14"><b>{scan.total_violations}</b></font>', s_body),
        Paragraph(f'<font color="#8b8fa5">Overall Score</font><br/><font size="18" color="#{sc.hexval()[2:]}"><b>{score:.0f}</b></font><font size="9" color="#8b8fa5"> / 100</font>', s_body),
    ]]

    col_w = page_w / 4
    summary_table = Table(summary_data, colWidths=[col_w] * 4)
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
    if severity_breakdown:
        elements.append(Paragraph("Severity Breakdown", s_heading))
        sev_header = [
            Paragraph('<font color="#8b8fa5"><b>Severity</b></font>', s_body),
            Paragraph('<font color="#8b8fa5"><b>Count</b></font>', s_body),
            Paragraph('<font color="#8b8fa5"><b>Distribution</b></font>', s_body),
        ]
        total_v = sum(severity_breakdown.values()) or 1
        sev_rows = [sev_header]
        for sev in ["critical", "serious", "moderate", "minor"]:
            count = severity_breakdown.get(sev, 0)
            if count == 0:
                continue
            pct = count / total_v * 100
            ic = IMPACT_COLORS.get(sev, TEXT_MUTED)
            hex_c = ic.hexval()[2:]
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

    # ── Phase Summary ──
    grouped: dict[str, list[Violation]] = defaultdict(list)
    for v in violations:
        grouped[v.category or "accessibility"].append(v)

    active_phases = [p for p in PHASE_ORDER if grouped.get(p)]

    if active_phases:
        elements.append(Paragraph("Phase Overview", s_heading))
        phase_header = [
            Paragraph('<font color="#8b8fa5"><b>Phase</b></font>', s_body),
            Paragraph('<font color="#8b8fa5"><b>Issues</b></font>', s_body),
            Paragraph('<font color="#8b8fa5"><b>Critical</b></font>', s_body),
            Paragraph('<font color="#8b8fa5"><b>Serious</b></font>', s_body),
        ]
        phase_rows = [phase_header]
        for cat in active_phases:
            cfg = PHASE_CONFIG.get(cat, {"label": cat, "color": TEXT_MUTED})
            cat_violations = grouped[cat]
            crit = sum(1 for v in cat_violations if v.impact == "critical")
            serious = sum(1 for v in cat_violations if v.impact == "serious")
            hex_c = cfg["color"].hexval()[2:]
            phase_rows.append([
                Paragraph(f'<font color="#{hex_c}"><b>{_esc(cfg["label"])}</b></font>', s_body),
                Paragraph(f'<b>{len(cat_violations)}</b>', s_body),
                Paragraph(f'<font color="{IMPACT_COLORS["critical"].hexval()}">{crit}</font>' if crit else '<font color="#8b8fa5">0</font>', s_body),
                Paragraph(f'<font color="{IMPACT_COLORS["serious"].hexval()}">{serious}</font>' if serious else '<font color="#8b8fa5">0</font>', s_body),
            ])

        phase_table = Table(phase_rows, colWidths=[page_w * 0.5, page_w * 0.17, page_w * 0.17, page_w * 0.16])
        phase_style = [
            ("BACKGROUND", (0, 0), (-1, 0), BG_CARD),
            ("BACKGROUND", (0, 1), (-1, -1), BG_CARD),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, BORDER_COLOR),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ]
        for r in range(2, len(phase_rows), 2):
            phase_style.append(("BACKGROUND", (0, r), (-1, r), BG_ROW_ALT))
        phase_table.setStyle(TableStyle(phase_style))
        elements.append(phase_table)
        elements.append(Spacer(1, 10))

    # ── Violations by Phase ──
    elements.append(Paragraph("Detailed Findings", s_heading))

    for cat in active_phases:
        cfg = PHASE_CONFIG.get(cat, {"label": cat, "color": TEXT_MUTED, "bg": BG_CARD})
        cat_violations = grouped[cat]
        hex_c = cfg["color"].hexval()[2:]

        elements.append(HRFlowable(
            width="100%", thickness=1.5,
            color=cfg["color"],
            spaceBefore=14, spaceAfter=4,
        ))
        phase_title = ParagraphStyle(
            f"Phase_{cat}", parent=s_phase_heading,
            textColor=cfg["color"],
        )
        elements.append(Paragraph(
            f'{_esc(cfg["label"])} <font size="9" color="#8b8fa5">({len(cat_violations)} issues)</font>',
            phase_title,
        ))

        for i, v in enumerate(cat_violations, 1):
            ic = IMPACT_COLORS.get(v.impact, TEXT_MUTED)
            ic_hex = ic.hexval()[2:]

            violation_data = [[
                Paragraph(
                    f'<font size="9"><b>{i}.</b></font> '
                    f'<font size="9"><b>{_esc(v.rule_id)}</b></font>',
                    s_body,
                ),
                Paragraph(
                    f'<font size="8" color="#{ic_hex}"><b> {v.impact.upper()} </b></font>',
                    ParagraphStyle("ImpactBadge", parent=s_body, alignment=TA_RIGHT),
                ),
            ]]
            vt = Table(violation_data, colWidths=[page_w * 0.75, page_w * 0.25])
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

            detail_parts = [
                f'<font color="#e2e8f0">{_esc(v.description)}</font>',
            ]
            if v.wcag_criteria:
                detail_parts.append(f'<br/><font color="#8b8fa5"><b>WCAG:</b> {_esc(v.wcag_criteria)}</font>')
            if v.help_url:
                detail_parts.append(f'<br/><font color="#7878cc"><u>{_esc(v.help_url)}</u></font>')

            detail_data = [[Paragraph("".join(detail_parts), s_body)]]
            dt = Table(detail_data, colWidths=[page_w])
            dt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), BG_ROW_ALT),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("PADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("ROUNDEDCORNERS", [0, 0, 4, 4]),
            ]))
            elements.append(dt)

            if v.affected_elements:
                for el in v.affected_elements[:3]:
                    elements.append(Paragraph(
                        f'<font color="#8b8fa5">Selector:</font> <font color="#9d9dff">{_esc(el.selector)}</font>',
                        s_code,
                    ))
                    elements.append(Paragraph(_esc(el.html), s_code))

            if v.ai_analyses:
                latest = v.ai_analyses[-1]
                elements.append(Spacer(1, 3))
                elements.append(Paragraph(
                    f'<font color="#9d9dff"><b>AI Suggestion:</b></font> {_esc(latest.suggested_fix[:500])}',
                    ParagraphStyle("AISuggestion", parent=s_body, fontSize=8, leftIndent=12, textColor=TEXT_MUTED),
                ))

            elements.append(Spacer(1, 8))

    # ── Security Scan Results ──
    if security_results and security_results.get("status") == "completed":
        elements.append(Spacer(1, 24))
        elements.append(HRFlowable(
            width="100%", thickness=2,
            color=BRAND,
            spaceAfter=8,
        ))
        elements.append(Paragraph(
            '<font color="#9d9dff">Security Scan Results</font>',
            s_heading,
        ))

        sec_score = security_results.get("security_score", 0)
        sec_sc = _score_color(sec_score)
        sec_total = security_results.get("total_findings", 0)

        sec_summary = [[
            Paragraph(f'<font color="#8b8fa5">Security Score</font><br/><font size="18" color="#{sec_sc.hexval()[2:]}"><b>{sec_score}</b></font><font size="9" color="#8b8fa5"> / 100</font>', s_body),
            Paragraph(f'<font color="#8b8fa5">Total Findings</font><br/><font size="14"><b>{sec_total}</b></font>', s_body),
        ]]
        sec_sum_table = Table(sec_summary, colWidths=[page_w / 2, page_w / 2])
        sec_sum_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BG_CARD),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("PADDING", (0, 0), (-1, -1), 12),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ]))
        elements.append(sec_sum_table)
        elements.append(Spacer(1, 12))

        # Security severity breakdown
        sec_findings = security_results.get("findings", [])
        sec_sev_counts: dict[str, int] = {}
        for f in sec_findings:
            sec_sev_counts[f["severity"]] = sec_sev_counts.get(f["severity"], 0) + 1

        if sec_sev_counts:
            elements.append(Paragraph("Security Severity Breakdown", s_heading))
            sec_sev_header = [
                Paragraph('<font color="#8b8fa5"><b>Severity</b></font>', s_body),
                Paragraph('<font color="#8b8fa5"><b>Count</b></font>', s_body),
                Paragraph('<font color="#8b8fa5"><b>Distribution</b></font>', s_body),
            ]
            sec_sev_total = sum(sec_sev_counts.values()) or 1
            sec_sev_rows = [sec_sev_header]
            for sev in SECURITY_SEVERITY_ORDER:
                cnt = sec_sev_counts.get(sev, 0)
                if cnt == 0:
                    continue
                pct = cnt / sec_sev_total * 100
                sc_ = SECURITY_SEVERITY_COLORS.get(sev, TEXT_MUTED)
                hex_c = sc_.hexval()[2:]
                bar = f'<font color="#{hex_c}">{"█" * max(1, int(pct / 3))}</font> <font color="#8b8fa5">{pct:.0f}%</font>'
                sec_sev_rows.append([
                    Paragraph(f'<font color="#{hex_c}"><b>{sev.upper()}</b></font>', s_body),
                    Paragraph(f'<b>{cnt}</b>', s_body),
                    Paragraph(bar, s_body),
                ])
            sec_sev_table = Table(sec_sev_rows, colWidths=[1.5 * inch, 1 * inch, page_w - 2.5 * inch])
            sec_sev_style = [
                ("BACKGROUND", (0, 0), (-1, 0), BG_CARD),
                ("BACKGROUND", (0, 1), (-1, -1), BG_CARD),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, BORDER_COLOR),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROUNDEDCORNERS", [6, 6, 6, 6]),
            ]
            for r in range(2, len(sec_sev_rows), 2):
                sec_sev_style.append(("BACKGROUND", (0, r), (-1, r), BG_ROW_ALT))
            sec_sev_table.setStyle(TableStyle(sec_sev_style))
            elements.append(sec_sev_table)
            elements.append(Spacer(1, 10))

        # Security detailed findings by category
        sec_categories = security_results.get("categories", [])
        if sec_categories:
            elements.append(Paragraph("Security Findings by Category", s_heading))

            for cat_data in sec_categories:
                cat_findings = cat_data.get("findings", [])
                cat_name = cat_data.get("name", "Unknown")
                cat_score = cat_data.get("score", 0)
                cc = SECURITY_CATEGORY_COLORS.get(cat_name, TEXT_MUTED)
                cat_sc = _score_color(cat_score)

                elements.append(HRFlowable(
                    width="100%", thickness=1.5,
                    color=cc,
                    spaceBefore=14, spaceAfter=4,
                ))
                sec_cat_title = ParagraphStyle(
                    f"SecCat_{cat_name}", parent=s_phase_heading,
                    textColor=cc,
                )
                elements.append(Paragraph(
                    f'{_esc(cat_name)} '
                    f'<font size="9" color="#8b8fa5">({len(cat_findings)} issues · Score: </font>'
                    f'<font size="9" color="#{cat_sc.hexval()[2:]}">{cat_score}</font>'
                    f'<font size="9" color="#8b8fa5">)</font>',
                    sec_cat_title,
                ))

                for i, f in enumerate(cat_findings, 1):
                    sc_ = SECURITY_SEVERITY_COLORS.get(f["severity"], TEXT_MUTED)
                    sc_hex = sc_.hexval()[2:]

                    row_data = [[
                        Paragraph(
                            f'<font size="9"><b>{i}.</b></font> '
                            f'<font size="9"><b>{_esc(f["title"])}</b></font>',
                            s_body,
                        ),
                        Paragraph(
                            f'<font size="8" color="#{sc_hex}"><b> {f["severity"].upper()} </b></font>',
                            ParagraphStyle("SecSevBadge", parent=s_body, alignment=TA_RIGHT),
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

                    dt = Table([[Paragraph("".join(detail_parts), s_body)]], colWidths=[page_w])
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
        "Generated by AccessiAI. Automated scans detect many issues but cannot establish complete WCAG compliance or security. "
        "Manual testing, expert review, and professional penetration testing are recommended.",
        s_disclaimer,
    ))

    doc.build(elements, onFirstPage=_on_page, onLaterPages=_on_page)
    buffer.seek(0)
    return buffer


def generate_markdown_report(
    scan: Scan,
    violations: Sequence[Violation],
    severity_breakdown: dict[str, int],
    security_results: dict | None = None,
) -> str:
    lines: list[str] = []
    url = scan.website.url if scan.website else "N/A"
    name = scan.website.name if scan.website else "Unknown"
    started = scan.scan_started_at.strftime("%Y-%m-%d %H:%M UTC") if scan.scan_started_at else "N/A"
    completed = scan.scan_completed_at.strftime("%Y-%m-%d %H:%M UTC") if scan.scan_completed_at else "N/A"

    lines.append("# AccessiAI Report")
    lines.append("")
    lines.append(f"**Website:** {name} ({url})")
    lines.append(f"**Scan Started:** {started}")
    lines.append(f"**Scan Completed:** {completed}")
    lines.append(f"**Accessibility Score:** {round(scan.accessibility_score) if scan.accessibility_score is not None else 'N/A'}/100")
    lines.append(f"**Total Violations:** {scan.total_violations}")
    lines.append("")

    lines.append("## Severity Breakdown")
    lines.append("")
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")
    for sev in ["critical", "serious", "moderate", "minor"]:
        count = severity_breakdown.get(sev, 0)
        if count:
            lines.append(f"| {sev.capitalize()} | {count} |")
    lines.append("")

    lines.append("## Violations")
    lines.append("")
    if not violations:
        lines.append("No violations found.")
    else:
        for i, v in enumerate(violations, 1):
            lines.append(f"### {i}. {v.description}")
            lines.append("")
            lines.append(f"- **Rule:** `{v.rule_id}`")
            lines.append(f"- **Impact:** {v.impact}")
            lines.append(f"- **WCAG:** {v.wcag_criteria}")
            lines.append(f"- **Status:** {v.status}")
            if v.help_url:
                lines.append(f"- **Reference:** {v.help_url}")
            lines.append("")

            if v.affected_elements:
                lines.append("**Affected Elements:**")
                lines.append("")
                for el in v.affected_elements:
                    lines.append(f"- `{el.selector}`")
                    lines.append(f"  ```html")
                    lines.append(f"  {el.html}")
                    lines.append(f"  ```")
                lines.append("")

            if v.ai_analyses:
                for analysis in v.ai_analyses:
                    lines.append("**AI Analysis:**")
                    lines.append("")
                    lines.append(analysis.explanation)
                    lines.append("")
                    if analysis.suggested_fix:
                        lines.append("**Suggested Fix:**")
                        lines.append("")
                        lines.append(analysis.suggested_fix)
                        lines.append("")

            lines.append("---")
            lines.append("")

    if security_results and security_results.get("status") == "completed":
        lines.append("## Security Scan Results")
        lines.append("")
        lines.append(f"**Security Score:** {security_results.get('security_score', 0)}/100")
        lines.append(f"**Total Findings:** {security_results.get('total_findings', 0)}")
        lines.append("")

        for cat in security_results.get("categories", []):
            lines.append(f"### {cat['name']} (Score: {cat['score']}/100)")
            lines.append("")
            if not cat.get("findings"):
                lines.append("No issues found.")
            else:
                for f in cat["findings"]:
                    lines.append(f"- **[{f['severity'].upper()}]** {f['title']}")
                    lines.append(f"  {f['description']}")
                    if f.get("recommendation"):
                        lines.append(f"  *Recommendation:* {f['recommendation']}")
            lines.append("")

    lines.append("---")
    lines.append("*Report generated by AccessiAI. Designed & Built by Jake Huang.*")
    lines.append("")

    return "\n".join(lines)
