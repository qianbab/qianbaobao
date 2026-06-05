#!/usr/bin/env python
"""Build an S_research HTML/PDF report from a structured JSON spec."""

from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def read_spec(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        spec = json.load(f)
    if not spec.get("title"):
        raise ValueError("report spec must include a non-empty title")
    if not isinstance(spec.get("sections", []), list):
        raise ValueError("report spec sections must be a list")
    return spec


def html_report(spec: dict[str, Any]) -> str:
    title = escape(str(spec["title"]))
    subtitle = escape(str(spec.get("subtitle", "")))
    date = escape(str(spec.get("date", "")))
    metrics = spec.get("metrics", [])
    sections = spec.get("sections", [])
    sources = spec.get("sources", [])
    disclaimer = escape(str(spec.get("disclaimer", "For research use only; not investment advice.")))

    metric_html = "\n".join(
        f'<div class="metric"><strong>{escape(str(m.get("value", "")))}</strong><span>{escape(str(m.get("label", "")))}</span></div>'
        for m in metrics
    )
    body_parts = []
    for section in sections:
        kind = section.get("type")
        if kind in {"h2", "h3", "p", "note"}:
            tag = "p" if kind == "note" else kind
            cls = ' class="note"' if kind == "note" else ""
            body_parts.append(f"<{tag}{cls}>{escape(str(section.get('text', '')))}</{tag}>")
        elif kind == "bullets":
            items = section.get("items", [])
            body_parts.append("<ul>" + "".join(f"<li>{escape(str(item))}</li>" for item in items) + "</ul>")
        elif kind == "table":
            headers = section.get("headers", [])
            rows = section.get("rows", [])
            head = "".join(f"<th>{escape(str(h))}</th>" for h in headers)
            row_html = []
            for row in rows:
                row_html.append("<tr>" + "".join(f"<td>{escape(str(cell))}</td>" for cell in row) + "</tr>")
            body_parts.append("<table><tr>" + head + "</tr>" + "".join(row_html) + "</table>")

    source_html = "".join(f"<li>{escape(str(s))}</li>" for s in sources)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    @page {{ size: A4; margin: 17mm 15mm; }}
    :root {{ --ink:#171914; --muted:#5e625c; --paper:#fbfaf5; --line:#d8d0bf; --accent:#31566f; --gold:#9f762b; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; color:var(--ink); background:var(--paper); font-family:"Noto Serif SC","SimSun",Georgia,serif; line-height:1.58; font-size:13.2px; }}
    h1,h2,h3 {{ margin:0; line-height:1.2; page-break-after:avoid; }}
    h1 {{ font-size:30px; margin-bottom:10px; }}
    h2 {{ font-size:21px; margin-top:24px; padding-bottom:6px; border-bottom:2px solid var(--ink); }}
    h3 {{ font-size:16px; margin-top:15px; color:#30342e; }}
    p {{ margin:8px 0; }}
    .cover {{ min-height:210px; padding:22px 24px; border:1px solid var(--line); background:linear-gradient(135deg,#fffdf7,#e9eef5); margin-bottom:18px; }}
    .kicker {{ display:inline-block; color:var(--muted); border:1px solid var(--line); border-radius:999px; padding:4px 9px; font-size:11px; margin-bottom:12px; }}
    .summary {{ display:grid; grid-template-columns:repeat(4,1fr); gap:9px; margin-top:18px; }}
    .metric {{ border:1px solid var(--line); background:#fffdf7; padding:9px; border-radius:6px; }}
    .metric strong {{ display:block; font-family:"Noto Sans SC","Microsoft YaHei",sans-serif; font-size:17px; }}
    .metric span {{ color:var(--muted); font-size:10.8px; }}
    .note {{ color:var(--muted); font-size:12px; border-left:3px solid var(--gold); padding-left:10px; margin:12px 0; }}
    table {{ width:100%; border-collapse:collapse; margin:9px 0 14px; page-break-inside:avoid; background:#fffdf7; }}
    th,td {{ border:1px solid var(--line); padding:7px 8px; vertical-align:top; font-size:12.2px; }}
    th {{ background:#e7ebef; text-align:left; font-family:"Noto Sans SC","Microsoft YaHei",sans-serif; }}
    ul {{ margin:8px 0 8px 18px; padding:0; }}
    li {{ margin:5px 0; }}
    .sources li {{ font-size:11.5px; color:var(--muted); }}
  </style>
</head>
<body>
  <section class="cover">
    <div class="kicker">S_research workflow · {date}</div>
    <h1>{title}</h1>
    <p>{subtitle}</p>
    <div class="summary">{metric_html}</div>
  </section>
  {''.join(body_parts)}
  <h2>主要来源</h2>
  <ul class="sources">{source_html}</ul>
  <p class="note">{disclaimer}</p>
</body>
</html>
"""


def pdf_para(text: Any, style: ParagraphStyle) -> Paragraph:
    safe = escape(str(text)).replace("\n", "<br/>")
    return Paragraph(safe, style)


def on_page_factory(title: str):
    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("STSong-Light", 8)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawString(15 * mm, 10 * mm, title[:45])
        canvas.drawRightString(195 * mm, 10 * mm, str(doc.page))
        canvas.restoreState()

    return on_page


def build_pdf(spec: dict[str, Any], pdf_path: Path) -> None:
    registerFont(UnicodeCIDFont("STSong-Light"))
    title = str(spec["title"])
    doc = BaseDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=16 * mm,
        title=title,
        author="Codex S_research",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="A4", frames=[frame], onPage=on_page_factory(title))])

    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("cn_title", parent=base["Title"], fontName="STSong-Light", fontSize=22, leading=28, alignment=TA_CENTER, spaceAfter=8),
        "subtitle": ParagraphStyle("cn_subtitle", parent=base["BodyText"], fontName="STSong-Light", fontSize=10, leading=14, alignment=TA_CENTER, textColor=colors.HexColor("#5e625c"), spaceAfter=10),
        "h2": ParagraphStyle("cn_h2", parent=base["Heading2"], fontName="STSong-Light", fontSize=15, leading=20, textColor=colors.HexColor("#173651"), spaceBefore=11, spaceAfter=6),
        "h3": ParagraphStyle("cn_h3", parent=base["Heading3"], fontName="STSong-Light", fontSize=12, leading=16, textColor=colors.HexColor("#26343d"), spaceBefore=7, spaceAfter=4),
        "p": ParagraphStyle("cn_p", parent=base["BodyText"], fontName="STSong-Light", fontSize=9.2, leading=13.6, alignment=TA_LEFT, spaceAfter=4),
        "note": ParagraphStyle("cn_note", parent=base["BodyText"], fontName="STSong-Light", fontSize=9, leading=13, leftIndent=8, textColor=colors.HexColor("#5e625c"), spaceAfter=5),
        "li": ParagraphStyle("cn_li", parent=base["BodyText"], fontName="STSong-Light", fontSize=9, leading=13, leftIndent=10, firstLineIndent=-7, spaceAfter=3),
        "cell": ParagraphStyle("cn_cell", parent=base["BodyText"], fontName="STSong-Light", fontSize=6.9, leading=8.8),
        "head": ParagraphStyle("cn_head", parent=base["BodyText"], fontName="STSong-Light", fontSize=7.1, leading=9, textColor=colors.white),
    }

    story = [pdf_para(title, styles["title"])]
    if spec.get("subtitle"):
        story.append(pdf_para(spec["subtitle"], styles["subtitle"]))
    metrics = spec.get("metrics", [])
    if metrics:
        metric_rows = [[pdf_para(f'{m.get("value", "")}: {m.get("label", "")}', styles["cell"]) for m in metrics]]
        story.append(Table(metric_rows, colWidths=[doc.width / len(metrics)] * len(metrics), style=[
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#b9b29f")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffdf7")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(Spacer(1, 8))

    for section in spec.get("sections", []):
        kind = section.get("type")
        if kind in {"h2", "h3", "p", "note"}:
            story.append(pdf_para(section.get("text", ""), styles[kind]))
        elif kind == "bullets":
            for item in section.get("items", []):
                story.append(pdf_para("• " + str(item), styles["li"]))
        elif kind == "table":
            headers = section.get("headers", [])
            rows = section.get("rows", [])
            max_cols = max([len(headers)] + [len(r) for r in rows] + [1])
            normalized_headers = headers + [""] * (max_cols - len(headers))
            table_rows = [[pdf_para(cell, styles["head"]) for cell in normalized_headers]]
            for row in rows:
                normalized = row + [""] * (max_cols - len(row))
                table_rows.append([pdf_para(cell, styles["cell"]) for cell in normalized])
            table = Table(table_rows, colWidths=[doc.width / max_cols] * max_cols, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#31566f")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#b9b29f")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fffdf7")),
            ]))
            story.append(table)
            story.append(Spacer(1, 5))

    sources = spec.get("sources", [])
    if sources:
        story.append(pdf_para("主要来源", styles["h2"]))
        for source in sources:
            story.append(pdf_para("• " + str(source), styles["li"]))
    if spec.get("disclaimer"):
        story.append(pdf_para(spec["disclaimer"], styles["note"]))

    doc.build(story)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="JSON report spec")
    parser.add_argument("--html", type=Path, help="HTML output path")
    parser.add_argument("--pdf", type=Path, help="PDF output path")
    args = parser.parse_args()

    spec = read_spec(args.spec)
    html_path = args.html or args.spec.with_suffix(".html")
    pdf_path = args.pdf or args.spec.with_suffix(".pdf")
    html_path.write_text(html_report(spec), encoding="utf-8")
    build_pdf(spec, pdf_path)
    print(f"HTML: {html_path}")
    print(f"PDF: {pdf_path}")


if __name__ == "__main__":
    main()
