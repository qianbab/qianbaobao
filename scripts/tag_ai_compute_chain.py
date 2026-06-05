#!/usr/bin/env python
"""Tag Serenity cleaned X rows with AI compute-chain layers and thesis labels."""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path


LAYER_PATTERNS: dict[str, list[str]] = {
    "photonics": [
        r"\bCPO\b",
        r"photonics?",
        r"optical",
        r"silicon photonics",
        r"\blaser",
        r"\$SIVE\b",
        r"\$AAOI\b",
        r"\$LITE\b",
        r"\$MRVL\b",
        r"\$COHR\b",
        r"\$POET\b",
    ],
    "substrates-materials": [
        r"\bInP\b",
        r"substrate",
        r"\bSOI\b",
        r"\$SOI\b",
        r"\$AXTI\b",
        r"\$IQE\b",
        r"glass core",
        r"\$LPK\b",
        r"wafer",
        r"epiwafer",
    ],
    "memory": [
        r"\bHBM\b",
        r"\bDRAM\b",
        r"\bNAND\b",
        r"memory",
        r"\$MU\b",
        r"\$SNDK\b",
        r"Hynix",
        r"Samsung",
        r"\bSSD\b",
        r"\$EWY\b",
    ],
    "neocloud": [
        r"Neocloud",
        r"GPU cloud",
        r"compute",
        r"hyperscaler",
        r"\$NBIS\b",
        r"\$IREN\b",
        r"\$CRWV\b",
        r"\$WULF\b",
        r"\$CIFR\b",
        r"\$APLD\b",
    ],
    "ai-infra": [
        r"data center",
        r"datacenter",
        r"\$NVDA\b",
        r"Nvidia",
        r"\bGPU\b",
        r"networking",
        r"server",
        r"\$JBL\b",
        r"\$APH\b",
        r"power",
        r"cooling",
        r"Vertiv",
        r"\$VRT\b",
    ],
    "semicap-test": [
        r"test",
        r"burn-in",
        r"semicap",
        r"foundry",
        r"packag",
        r"\$AEHR\b",
        r"\$TER\b",
        r"\$TSM\b",
        r"\$GFS\b",
        r"\$INTC\b",
    ],
    "policy-sovereignty": [
        r"CHIPS Act",
        r"\bDoD\b",
        r"national security",
        r"sovereignty",
        r"EU Chips",
        r"Nasdaq",
        r"redomicil",
        r"funding",
    ],
    "consumer-ai-hardware": [
        r"AI PC",
        r"laptop",
        r"edge",
        r"\$RPI\b",
        r"Raspberry",
        r"physical AI",
        r"\$AEVA\b",
        r"LiDAR",
    ],
    "market-structure": [
        r"gamma",
        r"short squeeze",
        r"dilution",
        r"\bATM\b",
        r"convertible",
        r"financing",
        r"float",
        r"liquidity",
        r"valuation",
    ],
    "self-positioning": [
        r"free research",
        r"paywall",
        r"community",
        r"track record",
        r"followers",
        r"disinformation",
    ],
}


THESIS_PATTERNS: dict[str, list[str]] = {
    "chokepoint": [r"chokepoint", r"bottleneck", r"critical"],
    "architecture-shift": [r"architecture", r"next-generation", r"copper", r"CPO", r"rack scale"],
    "capacity-sold-out": [r"sold out", r"capacity", r"volume ramp", r"production start"],
    "underfollowed-exposure": [r"missed", r"underfollowed", r"not mentioned", r"market.*realize"],
    "policy-catalyst": [r"CHIPS Act", r"\bDoD\b", r"funding", r"Nasdaq", r"EU Chips"],
    "financing-quality": [r"financing", r"dilution", r"\bATM\b", r"convertible", r"stake"],
    "cycle-rotation": [r"cycle", r"supercycle", r"rotation", r"memory.*optical"],
    "management-capital-markets": [r"management", r"listing", r"redomicil", r"M&A"],
    "risk-management": [r"risk", r"position sizing", r"volatility", r"drawdown", r"selling"],
}


def compile_patterns(table: dict[str, list[str]]) -> dict[str, list[re.Pattern[str]]]:
    return {
        label: [re.compile(pattern, re.I) for pattern in patterns]
        for label, patterns in table.items()
    }


LAYER_REGEX = compile_patterns(LAYER_PATTERNS)
THESIS_REGEX = compile_patterns(THESIS_PATTERNS)


def labels_for(text: str, table: dict[str, list[re.Pattern[str]]]) -> list[str]:
    return sorted(
        label
        for label, patterns in table.items()
        if any(pattern.search(text or "") for pattern in patterns)
    )


def primary_ticker(tickers: str) -> str:
    values = [ticker for ticker in (tickers or "").split(";") if ticker]
    return values[0] if values else ""


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cleaned_csv", type=Path)
    parser.add_argument("--out", type=Path, default=Path("serenity_x_author_tagged.csv"))
    parser.add_argument("--summary-out", type=Path, default=Path("serenity_x_author_layer_summary.csv"))
    args = parser.parse_args()

    rows = read_csv(args.cleaned_csv)
    tagged: list[dict[str, str]] = []
    layer_counts: Counter[str] = Counter()
    thesis_counts: Counter[str] = Counter()

    for row in rows:
        text = row.get("author_text", "")
        layer_labels = labels_for(text, LAYER_REGEX)
        thesis_labels = labels_for(text, THESIS_REGEX)
        for label in layer_labels:
            layer_counts[label] += 1
        for label in thesis_labels:
            thesis_counts[label] += 1
        tagged.append(
            {
                **row,
                "primary_ticker": primary_ticker(row.get("tickers", "")),
                "layer_labels": ";".join(layer_labels),
                "thesis_labels": ";".join(thesis_labels),
            }
        )

    fieldnames = list(tagged[0].keys()) if tagged else []
    write_csv(args.out, tagged, fieldnames)

    with args.summary_out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["kind", "label", "count"])
        for label, count in layer_counts.most_common():
            writer.writerow(["layer", label, count])
        for label, count in thesis_counts.most_common():
            writer.writerow(["thesis", label, count])

    print(f"tagged_rows={len(tagged)}")
    print(f"out={args.out}")
    print(f"summary_out={args.summary_out}")


if __name__ == "__main__":
    main()
