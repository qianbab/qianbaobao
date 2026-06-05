---
name: s-research-skill
description: Analyze Serenity / @aleabitoreddit source material and apply the derived S_research workflow to industry-chain research. Use when the user asks to study Serenity posts, clean X timeline/browser exports, extract tickers, classify theses, summarize the author's framework, build industry deep-dive reports, benchmark global companies against Chinese companies, or output HTML/PDF research reports with China-company mapping and risk framing.
---

# Serenity Research

Use this skill in two related modes:

1. Turn Serenity / @aleabitoreddit source material into clean, author-only research artifacts.
2. Apply the distilled S_research workflow to industry-chain research reports, including China-company benchmarking and HTML/PDF output.

## Evidence Rules

- Prefer direct `https://x.com/aleabitoreddit/status/...` records.
- Include replies only when the status URL author is `aleabitoreddit`.
- Keep third-party commentary, signal-site sentiment, media coverage, and mirror summaries out of author-only tables.
- Treat browser timeline text as visible-page evidence, not full status-page text. It can include quoted posts, UI labels, metrics, and truncated `Show more` text.
- Do not present ticker frequencies as clean author-text frequencies until quote/UI cleanup has been run.
- For industry reports, separate public facts, source-grounded claims, and analyst inference. For current market/company data, verify with up-to-date sources before drawing conclusions.

## Mode A: Author-Only X Workflow

1. Identify the input type: browser export CSV/JSON, strict X status table, interview notes, or mixed mirror sample.
2. If the input is a browser export, run `scripts/clean_x_export.py` before analysis.
3. Extract tickers, dates, post type, quoted-context flags, and status IDs.
4. Classify each record using `references/taxonomy.md`.
5. For methodology summaries, read `references/serenity-methodology.md` and keep claims separated as `direct_x_status`, `author_attributed_secondary`, or `inference`.
6. For ticker case studies, use `references/case-study-template.md`.

## Mode B: Industry Deep-Dive Workflow

Use this mode when the user asks to analyze an industry such as AI compute, robotics, commercial space, green power, innovative drugs, semiconductors, or similar sectors.

1. Define the architecture migration: what is changing in technology, demand, regulation, or supply-chain structure.
2. Identify the real chokepoints: scarce assets, physical constraints, production capacity, CMC/manufacturing barriers, grid/energy constraints, regulatory approval, or customer adoption bottlenecks.
3. Map the value chain from upstream inputs to end-market revenue.
4. Benchmark global leaders against representative Chinese companies. Read `references/china-company-benchmark.md` for table fields and comparison rules.
5. Convert the thesis into equity-relevant outcomes: who captures margin, who faces commoditization, what milestones validate or break the thesis, and which risks can permanently impair value.
6. When the user asks for a report or PDF, write a source-grounded HTML report first, then use `scripts/build_report_pdf.py` to generate a PDF from a JSON report spec, or adapt the script if the local report format requires it.

## Scripts: X Data

Run from the workspace containing the export:

```bash
python <path-to-skill>/scripts/clean_x_export.py input.csv --out cleaned.csv --ticker-out ticker_frequency.csv
```

The cleaner expects columns such as `x_url`, `posted_at`, `post_type`, and `text`. It writes:

- cleaned rows with `status_id`, `author_text`, `quote_context`, `tickers`, and `needs_detail_fetch`.
- ticker counts based on cleaned `author_text`.

Tag cleaned rows:

```bash
python <path-to-skill>/scripts/tag_ai_compute_chain.py cleaned.csv --out tagged.csv --summary-out layer_summary.csv
```

Fetch fuller status-detail text from a logged-in Edge/Chrome CDP session:

```bash
node <path-to-skill>/scripts/fetch_status_details_cdp.mjs cleaned.csv --out status_details.csv
```

Use detail fetching when many rows have `needs_detail_fetch=yes`, when exact post type matters, or when a ticker case study needs full source text.

## Scripts: Report Output

Build a PDF and optional HTML from a structured JSON report spec:

```bash
python <path-to-skill>/scripts/build_report_pdf.py report_spec.json --html report.html --pdf report.pdf
```

For the expected JSON shape, read `references/report-output-template.md`. The script supports Chinese text, headings, paragraphs, bullet lists, metric blocks, and tables. Prefer this script for repeatable report output instead of rewriting PDF code every time.

Dependencies: `scripts/build_report_pdf.py` requires Python `reportlab`. `scripts/fetch_status_details_cdp.mjs` requires the Node package `playwright` and a browser already exposing a local CDP endpoint.

## Reference Files

- `references/taxonomy.md`: sector and thesis labels for tagging posts.
- `references/serenity-methodology.md`: distilled author framework and caveats.
- `references/case-study-template.md`: structure for ticker-level case studies.
- `references/china-company-benchmark.md`: required fields and quality rules for global-to-China company benchmarking.
- `references/report-output-template.md`: JSON structure and report section checklist for HTML/PDF reports.

## Output Standards

- Always state collection limits: X login state, scroll depth, timeline truncation, quote-context contamination, and lack of API metadata when relevant.
- Use short excerpts only; summarize instead of reproducing long X posts.
- Separate facts from inference. Label inferences explicitly.
- For investment-related output, include risk framing and avoid giving personalized investment advice.
- For industry-chain reports, include representative Chinese companies by value-chain segment, not only headline A-share/H-share names.
- For PDF deliverables, provide the PDF path and the source HTML or JSON path. Verify the PDF exists and has a non-zero size; if a PDF reader is available, verify page count.
