#!/usr/bin/env python
"""Build an S_research HTML report and print it to PDF with a browser.

Primary pipeline:
    JSON spec -> high-quality HTML/CSS -> Chromium/Edge/Chrome print-to-PDF

Fallback:
    If no supported browser is available, generate a simpler ReportLab PDF.
"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import tempfile
from html import escape
from pathlib import Path
from typing import Any


def read_spec(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        spec = json.load(f)
    if not spec.get("title"):
        raise ValueError("report spec must include a non-empty title")
    if not isinstance(spec.get("sections", []), list):
        raise ValueError("report spec sections must be a list")
    return spec


def html_escape(value: Any) -> str:
    return escape(str(value if value is not None else ""), quote=True)


def render_sections(sections: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for section in sections:
        kind = section.get("type")
        if kind == "note":
            parts.append(f'<p class="note">{html_escape(section.get("text", ""))}</p>')
        elif kind in {"h2", "h3"}:
            parts.append(f'<{kind}>{html_escape(section.get("text", ""))}</{kind}>')
        elif kind == "p":
            parts.append(f'<p>{html_escape(section.get("text", ""))}</p>')
        elif kind == "bullets":
            items = section.get("items", [])
            lis = "".join(f"<li>{html_escape(item)}</li>" for item in items)
            parts.append(f"<ul>{lis}</ul>")
        elif kind == "table":
            headers = section.get("headers", [])
            rows = section.get("rows", [])
            head = "".join(f"<th>{html_escape(h)}</th>" for h in headers)
            body_rows = []
            for row in rows:
                cells = "".join(f"<td>{html_escape(cell)}</td>" for cell in row)
                body_rows.append(f"<tr>{cells}</tr>")
            parts.append(f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>")
    return "\n".join(parts)


def html_report(spec: dict[str, Any]) -> str:
    title = html_escape(spec["title"])
    subtitle = html_escape(spec.get("subtitle", ""))
    date = html_escape(spec.get("date", ""))
    metrics = spec.get("metrics", [])
    sources = spec.get("sources", [])
    disclaimer = html_escape(spec.get("disclaimer", "For research use only; not investment advice."))

    metric_cards = "\n".join(
        f'<div class="metric"><strong>{html_escape(m.get("value", ""))}</strong><span>{html_escape(m.get("label", ""))}</span></div>'
        for m in metrics
    )
    source_items = "".join(f"<li>{html_escape(source)}</li>" for source in sources)
    sections = render_sections(spec.get("sections", []))

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    @page {{
      size: A4;
      margin: 14mm 14mm 15mm;
    }}

    :root {{
      --ink: #171914;
      --muted: #60665c;
      --paper: #fbfaf4;
      --page: #fffdf7;
      --line: #d8d0bf;
      --line-soft: #e7dfcf;
      --green: #315f42;
      --blue: #31566f;
      --gold: #9f762b;
      --red: #9e3f34;
    }}

    * {{ box-sizing: border-box; }}

    html, body {{
      margin: 0;
      padding: 0;
      color: var(--ink);
      background: var(--paper);
      font-family: "Microsoft YaHei", "微软雅黑", "Noto Sans CJK SC", "PingFang SC", Arial, sans-serif;
      font-size: 13.2px;
      line-height: 1.62;
      letter-spacing: 0;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}

    body {{
      padding: 18px 0 28px;
    }}

    .page {{
      width: min(1040px, calc(100vw - 36px));
      margin: 0 auto;
      background: var(--page);
      border: 1px solid var(--line);
      box-shadow: 0 10px 30px rgba(40, 34, 20, 0.08);
      padding: 30px 34px 34px;
    }}

    .cover {{
      min-height: 260px;
      margin: -30px -34px 24px;
      padding: 30px 34px 32px;
      border-bottom: 1px solid var(--line);
      background:
        linear-gradient(135deg, rgba(255,255,255,0.9), rgba(238, 232, 214, 0.62)),
        radial-gradient(circle at 92% 10%, rgba(49, 86, 111, 0.16), transparent 35%);
    }}

    .kicker {{
      display: inline-flex;
      align-items: center;
      max-width: 100%;
      color: var(--muted);
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 4px 11px;
      font-size: 11px;
      margin-bottom: 16px;
      background: rgba(255,255,255,0.62);
    }}

    h1, h2, h3 {{
      margin: 0;
      line-height: 1.2;
      page-break-after: avoid;
      break-after: avoid;
    }}

    h1 {{
      max-width: 900px;
      font-family: "Microsoft YaHei", "微软雅黑", "Noto Sans CJK SC", sans-serif;
      font-size: 34px;
      font-weight: 800;
      margin-bottom: 14px;
      color: #11150f;
    }}

    .subtitle {{
      max-width: 940px;
      color: #3f443c;
      font-size: 14.2px;
      margin: 0;
    }}

    .summary {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 24px;
    }}

    .metric {{
      min-height: 92px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: rgba(255,253,247,0.92);
      padding: 12px 13px;
      page-break-inside: avoid;
      break-inside: avoid;
    }}

    .metric strong {{
      display: block;
      font-size: 20px;
      line-height: 1.15;
      margin-bottom: 7px;
      color: #17221a;
    }}

    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 11.3px;
      line-height: 1.45;
    }}

    h2 {{
      font-size: 22px;
      margin-top: 26px;
      padding-bottom: 8px;
      border-bottom: 2px solid var(--ink);
      color: #11150f;
    }}

    h3 {{
      font-size: 16px;
      margin-top: 17px;
      color: #29352d;
    }}

    p {{
      margin: 9px 0;
    }}

    .note {{
      color: #4e554d;
      font-size: 12.7px;
      border-left: 4px solid var(--gold);
      padding: 8px 0 8px 12px;
      margin: 14px 0;
      background: rgba(245, 239, 221, 0.45);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 11px 0 16px;
      background: #fffdf7;
      page-break-inside: auto;
      break-inside: auto;
    }}

    tr {{
      page-break-inside: avoid;
      break-inside: avoid;
    }}

    thead {{
      display: table-header-group;
    }}

    th, td {{
      border: 1px solid var(--line-soft);
      padding: 9px 10px;
      vertical-align: top;
      font-size: 12px;
      line-height: 1.52;
      overflow-wrap: anywhere;
    }}

    th {{
      background: #e8dfcb;
      color: #1d211c;
      text-align: left;
      font-weight: 700;
    }}

    tbody tr:nth-child(even) td {{
      background: rgba(244, 240, 226, 0.38);
    }}

    ul {{
      margin: 9px 0 10px 20px;
      padding: 0;
    }}

    li {{
      margin: 5px 0;
    }}

    .sources {{
      color: var(--muted);
      font-size: 11.4px;
      overflow-wrap: anywhere;
    }}

    .sources li {{
      margin: 4px 0;
    }}

    .disclaimer {{
      margin-top: 16px;
      color: var(--muted);
      font-size: 11.8px;
      border-top: 1px solid var(--line);
      padding-top: 12px;
    }}

    @media print {{
      body {{
        padding: 0;
        background: white;
      }}

      .page {{
        width: auto;
        min-height: auto;
        margin: 0;
        padding: 0;
        border: 0;
        box-shadow: none;
        background: white;
      }}

      .cover {{
        margin: 0 0 22px;
        padding: 24px 28px 26px;
        border: 1px solid var(--line);
      }}

      .summary {{
        grid-template-columns: repeat(4, 1fr);
      }}

      h1 {{
        font-size: 31px;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="cover">
      <div class="kicker">S_research workflow · {date}</div>
      <h1>{title}</h1>
      <p class="subtitle">{subtitle}</p>
      <div class="summary">{metric_cards}</div>
    </section>
    {sections}
    <h2>主要来源</h2>
    <ul class="sources">{source_items}</ul>
    <p class="disclaimer">{disclaimer}</p>
  </main>
</body>
</html>
"""


def file_uri(path: Path) -> str:
    return path.resolve().as_uri()


def find_browser() -> str | None:
    candidates: list[str] = []
    if platform.system() == "Windows":
        candidates.extend(
            [
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
        )
    candidates.extend(["msedge", "microsoft-edge", "google-chrome", "chrome", "chromium", "chromium-browser"])
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return str(path)
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def print_pdf_with_browser(html_path: Path, pdf_path: Path) -> bool:
    browser = find_browser()
    if not browser:
        return False

    profile_dir = Path(tempfile.mkdtemp(prefix="s-research-print-"))
    command = [
        browser,
        "--headless",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        f"--user-data-dir={profile_dir}",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={pdf_path.resolve()}",
        file_uri(html_path),
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        return result.returncode == 0 and pdf_path.exists() and pdf_path.stat().st_size > 0
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)


def build_pdf_fallback_reportlab(spec: dict[str, Any], pdf_path: Path) -> None:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.pdfbase.pdfmetrics import registerFont
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle

    def pdf_font() -> str:
        for font_path in [Path("C:/Windows/Fonts/msyh.ttc"), Path("C:/Windows/Fonts/msyh.ttf")]:
            if font_path.exists():
                try:
                    registerFont(TTFont("MicrosoftYaHei", str(font_path)))
                    return "MicrosoftYaHei"
                except Exception:
                    pass
        registerFont(UnicodeCIDFont("STSong-Light"))
        return "STSong-Light"

    def para(text: Any, style: ParagraphStyle) -> Paragraph:
        return Paragraph(html_escape(text).replace("\n", "<br/>"), style)

    font = pdf_font()
    title = str(spec["title"])

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont(font, 8)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawString(15 * mm, 10 * mm, title[:45])
        canvas.drawRightString(195 * mm, 10 * mm, str(doc.page))
        canvas.restoreState()

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
    doc.addPageTemplates([PageTemplate(id="A4", frames=[frame], onPage=on_page)])

    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("title", parent=base["Title"], fontName=font, fontSize=22, leading=28, alignment=TA_CENTER, spaceAfter=8),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName=font, fontSize=15, leading=20, textColor=colors.HexColor("#173651"), spaceBefore=11, spaceAfter=6),
        "h3": ParagraphStyle("h3", parent=base["Heading3"], fontName=font, fontSize=12, leading=16, spaceBefore=7, spaceAfter=4),
        "p": ParagraphStyle("p", parent=base["BodyText"], fontName=font, fontSize=9.2, leading=13.6, alignment=TA_LEFT, spaceAfter=4),
        "note": ParagraphStyle("note", parent=base["BodyText"], fontName=font, fontSize=9, leading=13, leftIndent=8, textColor=colors.HexColor("#5e625c"), spaceAfter=5),
        "li": ParagraphStyle("li", parent=base["BodyText"], fontName=font, fontSize=9, leading=13, leftIndent=10, firstLineIndent=-7, spaceAfter=3),
        "cell": ParagraphStyle("cell", parent=base["BodyText"], fontName=font, fontSize=6.9, leading=8.8),
        "head": ParagraphStyle("head", parent=base["BodyText"], fontName=font, fontSize=7.1, leading=9, textColor=colors.white),
    }

    story = [para(title, styles["title"])]
    if spec.get("subtitle"):
        story.append(para(spec["subtitle"], styles["p"]))
    if spec.get("metrics"):
        metric_row = [[para(f'{m.get("value", "")}: {m.get("label", "")}', styles["cell"]) for m in spec["metrics"]]]
        story.append(Table(metric_row, colWidths=[doc.width / len(metric_row[0])] * len(metric_row[0])))
        story.append(Spacer(1, 8))

    for section in spec.get("sections", []):
        kind = section.get("type")
        if kind in {"h2", "h3", "p", "note"}:
            story.append(para(section.get("text", ""), styles[kind]))
        elif kind == "bullets":
            for item in section.get("items", []):
                story.append(para("- " + str(item), styles["li"]))
        elif kind == "table":
            headers = section.get("headers", [])
            rows = section.get("rows", [])
            max_cols = max([len(headers)] + [len(row) for row in rows] + [1])
            table_rows = [[para(cell, styles["head"]) for cell in headers + [""] * (max_cols - len(headers))]]
            for row in rows:
                table_rows.append([para(cell, styles["cell"]) for cell in row + [""] * (max_cols - len(row))])
            table = Table(table_rows, colWidths=[doc.width / max_cols] * max_cols, repeatRows=1)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#31566f")),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#b9b29f")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            story.append(table)
            story.append(Spacer(1, 5))

    if spec.get("sources"):
        story.append(para("主要来源", styles["h2"]))
        for source in spec["sources"]:
            story.append(para("- " + str(source), styles["li"]))
    if spec.get("disclaimer"):
        story.append(para(spec["disclaimer"], styles["note"]))
    doc.build(story)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="JSON report spec")
    parser.add_argument("--html", type=Path, help="HTML output path")
    parser.add_argument("--pdf", type=Path, help="PDF output path")
    parser.add_argument(
        "--pdf-engine",
        choices=["auto", "browser", "reportlab", "none"],
        default="auto",
        help="PDF engine. Default: auto tries browser first, then ReportLab fallback.",
    )
    args = parser.parse_args()

    spec = read_spec(args.spec)
    html_path = args.html or args.spec.with_suffix(".html")
    pdf_path = args.pdf or args.spec.with_suffix(".pdf")
    html_path.write_text(html_report(spec), encoding="utf-8")

    if args.pdf_engine != "none":
        printed = False
        if args.pdf_engine in {"auto", "browser"}:
            printed = print_pdf_with_browser(html_path, pdf_path)
            if args.pdf_engine == "browser" and not printed:
                raise RuntimeError("Browser PDF generation failed. Install Edge/Chrome or use --pdf-engine reportlab.")
        if not printed and args.pdf_engine in {"auto", "reportlab"}:
            build_pdf_fallback_reportlab(spec, pdf_path)

    print(f"HTML: {html_path}")
    if args.pdf_engine != "none":
        print(f"PDF: {pdf_path}")


if __name__ == "__main__":
    main()
