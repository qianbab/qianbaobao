# Report Output Template

Use this reference when the user asks S_research to output an industry report as HTML or PDF.

## Report Checklist

Include these sections unless the user narrows the scope:

1. Cover: title, date, method line, and 3-5 key metrics.
2. One-sentence conclusion.
3. Industry phase: what changed and why now.
4. Core bottleneck thesis: what is scarce, hard, or newly valuable.
5. Value-chain map: upstream to end-market.
6. China company benchmark: global leaders vs representative Chinese companies.
7. Priority ranking: most attractive bottleneck exposures first.
8. Valuation/equity translation: who captures margin and what can go wrong.
9. Risks: policy, price war, technology, customer, financing, regulatory, and execution.
10. Sources and disclaimer.

## JSON Spec Shape

`scripts/build_report_pdf.py` expects this shape:

```json
{
  "title": "Industry Chain Deep Dive",
  "subtitle": "Architecture migration -> chokepoint -> supply-chain validation -> equity result",
  "date": "2026-06-06",
  "metrics": [
    {"value": "46", "label": "Example key metric"}
  ],
  "sections": [
    {"type": "note", "text": "One-sentence conclusion."},
    {"type": "h2", "text": "1. Industry Phase"},
    {"type": "p", "text": "Paragraph text."},
    {
      "type": "table",
      "headers": ["Segment", "Global leaders", "China companies", "What to verify"],
      "rows": [
        ["Segment A", "GlobalCo", "ChinaCo", "Orders, margin, qualification"]
      ]
    },
    {"type": "bullets", "items": ["Risk one", "Risk two"]}
  ],
  "sources": [
    "Official source or report URL"
  ],
  "disclaimer": "For research workflow testing only; not investment advice."
}
```

## HTML/PDF Rules

- Write concise table cells. PDF pages become unreadable when cells contain long paragraphs.
- Use source names and URLs in `sources`; avoid uncited market-size or company claims.
- Keep evidence and inference separate in prose.
- When current facts matter, verify with up-to-date sources before writing the report.
- Always verify generated PDF file existence and, when possible, page count.
