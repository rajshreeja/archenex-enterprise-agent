"""Boardroom PDF report with complex charts. DejaVu fonts (bundled with matplotlib) render the ₹ symbol."""
from __future__ import annotations

import io
import os
from datetime import datetime
from xml.sax.saxutils import escape

import matplotlib
matplotlib.use("Agg")
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (CondPageBreak, Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

from . import charts, insights
from .detectors import TOOL_VERSION, inr

NAVY, BLUE, GREY, RED = "#1e3a8a", "#2563eb", "#64748b", "#b91c1c"
_FONTS_READY = False


def _fonts():
    global _FONTS_READY
    if _FONTS_READY:
        return
    base = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
    pdfmetrics.registerFont(TTFont("DejaVu", os.path.join(base, "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", os.path.join(base, "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold", italic="DejaVu", boldItalic="DejaVu-Bold")
    _FONTS_READY = True


def build_pdf(meta: dict, findings: list, summary: dict, cfg: dict, fingerprint: str, reviewer: str = "",
              ai_text: str = "", decisions: dict | None = None, audit_head: str = "") -> bytes:
    _fonts()
    ss = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="DejaVu-Bold", fontSize=15, textColor=colors.HexColor(NAVY), spaceAfter=4)
    H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="DejaVu-Bold", fontSize=11, textColor=colors.HexColor(BLUE),
                        spaceBefore=10, spaceAfter=4, keepWithNext=1)
    B = ParagraphStyle("B", parent=ss["Normal"], fontName="DejaVu", fontSize=9, leading=13, spaceAfter=4)
    SM = ParagraphStyle("SM", parent=B, fontSize=7.5, leading=10, textColor=colors.HexColor(GREY))
    MONO = ParagraphStyle("MONO", parent=B, fontName="Courier", fontSize=7.5, leading=10)
    WARN = ParagraphStyle("WARN", parent=B, fontName="DejaVu-Bold", textColor=colors.HexColor(RED))

    def tbl(data, widths, header=True, align_right_from=None):
        t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
        st = [("FONTNAME", (0, 0), (-1, -1), "DejaVu"), ("FONTSIZE", (0, 0), (-1, -1), 8),
              ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
              ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
              ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
        if header:
            st += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                   ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold")]
        if align_right_from is not None:
            st.append(("ALIGN", (align_right_from, 0), (-1, -1), "RIGHT"))
        t.setStyle(TableStyle(st))
        return t

    def cell(txt):
        return Paragraph(escape(str(txt)), ParagraphStyle("c", parent=B, fontSize=8, leading=10, spaceAfter=0))

    def img(buf, w=170, h=66):
        return Image(buf, width=w * mm, height=h * mm) if buf is not None else Spacer(1, 1)

    prim = [f for f in findings if f.tier == "primary"]
    sec = [f for f in findings if f.tier != "primary"]
    story = [Paragraph("ARCHENEX AUDIT DOSSIER", H1),
             Paragraph("Cross-silo financial leakage review - draft for board sub-committee", SM), Spacer(1, 4)]
    if meta["is_demo"]:
        story.append(Paragraph("SYNTHETIC DEMONSTRATION DATA - NOT FINDINGS FOR ANY REAL COMPANY", WARN))
    now = datetime.now().strftime("%d %b %Y, %H:%M")
    story.append(tbl([
        ["Organisation", cell(meta["client"]), "Report date", cell(now)],
        ["Industry", cell(meta["sector"]), "Data basis", cell(meta["data_basis"])],
        ["Source systems", cell(f"{meta['hris']} / {meta['erp']}"), "Engine version", cell(TOOL_VERSION)],
    ], [28 * mm, 66 * mm, 26 * mm, 54 * mm], header=False))

    # 1. headline
    story.append(Paragraph("1. Headline numbers", H2))
    pb = summary["payback_months"]
    hl = [["Measure", "Value", "How it is derived"],
          ["Identified annual leakage", inr(summary["identified_annual"]), "Sum of primary rule findings, scaled from the data window to 12 months"],
          ["Realistically addressable", inr(summary["addressable_annual"]), "Identified × realisation rate per rule (planning assumption)"],
          ["Illustrative valuation lift", inr(summary["valuation_lift"]), f"Addressable × {cfg['ev_ebitda_multiple']:g}x. Only valid if savings are recurring and verified"],
          ["Platform fee (assumed)", inr(summary["fee"]), "Annual subscription used in the payback maths"],
          ["Return on fee", f"{summary['roi_multiple']:.1f}x per year", f"Payback in {pb:.1f} months" if pb != float("inf") else "n/a"],
          ["One-time cash release", inr(summary["one_time_cash_release"] + summary.get("one_time_recovery", 0.0)),
           "Unbilled milestones + recoverable duplicate payments; working capital, not annual savings"]]
    if sec:
        hl.append(["Secondary (not in headline)", inr(summary["secondary_identified"]),
                   "Retention exposure watch-list; planning assumptions"])
    hl = [hl[0]] + [[r[0], r[1], cell(r[2])] for r in hl[1:]]
    story.append(tbl(hl, [48 * mm, 30 * mm, 96 * mm]))

    # 2. insights
    story.append(Paragraph("2. What the data says", H2))
    for it in insights.headline_insights(findings, summary, cfg)[:6]:
        story.append(KeepTogether([Paragraph(f"<b>{escape(it['headline'])}</b>", B),
                                   Paragraph(escape(it["so_what"]) + f" <i>Owner: {escape(it['owner'])}.</i>", SM)]))
    if ai_text:
        story.append(Paragraph("AI-written CFO brief (from aggregated numbers only)", H2))
        for para in ai_text.split("\n\n"):
            story.append(Paragraph(escape(para.replace("\n", " ")), B))

    # 3. findings table + charts
    story.append(Paragraph("3. Findings by audit rule", H2))
    rows = [["Rule", "Flagged", "Window", "Identified / yr", "Real. %", "Addressable / yr"]]
    for f in findings:
        rows.append([cell(f.title), f"{f.rows_flagged:,}", f"{f.window_days}d", inr(f.annualised_inr),
                     f"{cfg['realisation_pct'].get(f.key, 0):g}%", inr(f.addressable(cfg))])
    story.append(tbl(rows, [62 * mm, 18 * mm, 16 * mm, 30 * mm, 15 * mm, 33 * mm], align_right_from=1))
    story.append(Spacer(1, 6))
    if prim:
        story.append(img(charts.mpl_rule_bars(findings, cfg), 170, 71))
        story.append(CondPageBreak(75 * mm))
        story.append(Paragraph("From leakage to net benefit", H2))
        story.append(img(charts.mpl_waterfall(summary), 170, 66))

    story.append(PageBreak())
    story.append(Paragraph("4. Where it concentrates", H2))
    for key, col in (("idle_staging", "cell"), ("duplicate_payments", "vendor"), ("orphaned_saas", "app")):
        f = next((x for x in findings if x.key == key and len(x.evidence)), None)
        if f is not None:
            story.append(KeepTogether([Paragraph(f"<b>{escape(charts.short(f))}</b>: Pareto by {col}", B),
                                       img(charts.mpl_pareto(f, col), 165, 64)]))
    idle = next((x for x in findings if x.key == "idle_staging" and len(x.evidence)), None)
    if idle is not None:
        hm = charts.mpl_heatmap(idle)
        if hm is not None:
            story.append(KeepTogether([Paragraph("<b>Hotspot map</b>: idle-time cost by cell and shift", B), img(hm, 130, 65)]))
    tr = charts.mpl_trend(findings)
    if tr is not None:
        story.append(KeepTogether([Paragraph("<b>Weekly trend</b> by rule", B), img(tr, 165, 64)]))

    # 5. method
    story.append(CondPageBreak(70 * mm))
    story.append(Paragraph("5. Method and limitations", H2))
    for f in findings:
        story.append(KeepTogether([Paragraph(f"<b>{escape(f.title)}</b>", B), Paragraph(escape(f.method), B),
                                   Paragraph("<i>Limitation:</i> " + escape(f.caveat or "None noted."), SM)]))
    story.append(Paragraph("All figures are computed from the files or connectors supplied. Realisation rates are planning "
                           "assumptions until a pilot produces measured recovery. Findings are exceptions for human review, "
                           "not conclusions of wrongdoing, and no payroll, HRIS or ERP data has been altered.", SM))

    story.append(Paragraph("6. Assumptions used", H2))
    arows = [["Assumption", "Value"],
             ["Cost of capital", f"{cfg['cost_of_capital_pct']:g}%"], ["Overtime multiplier", f"{cfg['overtime_multiplier']:g}x"],
             ["Invoice grace period", f"{cfg['invoice_grace_days']} days"], ["SaaS inactivity threshold", f"{cfg['saas_inactive_days']} days"],
             ["Under-utilisation threshold", f"{cfg['low_utilisation_pct']:g}%"], ["Weekly overtime cap", f"{cfg['weekly_ot_cap_hours']:g} h"],
             ["Avoidable downtime reasons", escape(str(cfg["avoidable_reasons"]))],
             ["EV/EBITDA multiple (illustrative)", f"{cfg['ev_ebitda_multiple']:g}x"]]
    story.append(tbl(arows, [70 * mm, 50 * mm]))

    # 7. decisions
    if decisions:
        story.append(Paragraph("7. Decisions recorded", H2))
        drows = [["Action", "Decision"]] + [[cell(k), v] for k, v in list(decisions.items())[:25]]
        story.append(tbl(drows, [130 * mm, 40 * mm]))

    story.append(Paragraph("8. Integrity fingerprint", H2))
    story.append(Paragraph("The SHA-256 fingerprint below is computed over the input-file hashes, the assumptions and the findings. "
                           "If a single figure or assumption is altered, the fingerprint no longer matches. It proves integrity, "
                           "not authorship; it is not a digital signature.", B))
    story.append(Paragraph(fingerprint, MONO))
    if audit_head:
        story.append(Paragraph("Decision audit chain head: " + audit_head, MONO))

    story.append(Paragraph("9. Human review and sign-off", H2))
    story.append(Paragraph("Status: <b>DRAFT - pending human review.</b> This report becomes final only when signed below.", B))
    story.append(tbl([["Prepared / reviewed by", escape(reviewer) if reviewer else "", "Date", ""],
                      ["CFO / approving executive", "", "Date", ""]], [48 * mm, 70 * mm, 14 * mm, 42 * mm], header=False))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("DejaVu", 7)
        canvas.setFillColor(colors.HexColor(GREY))
        canvas.drawString(15 * mm, 9 * mm, f"ArcheNex · {meta['client']} · DRAFT - pending human review")
        canvas.drawRightString(A4[0] - 15 * mm, 9 * mm, f"Page {doc.page}")
        canvas.restoreState()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=14 * mm,
                            bottomMargin=16 * mm, title="ArcheNex Audit Dossier", author="ArcheNex")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()
