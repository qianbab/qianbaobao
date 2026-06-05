#!/usr/bin/env python
"""Clean logged-in X browser exports for Serenity author-only research."""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path


AUTHOR = "aleabitoreddit"
STATUS_RE = re.compile(rf"/{AUTHOR}/status/(\d+)", re.I)
TICKER_RE = re.compile(r"\$[A-Za-z][A-Za-z0-9]{0,5}")
METRIC_TOKEN_RE = re.compile(r"^(?:\d+(?:\.\d+)?[KMB]?|\d+,\d+|\d+K|\d+M)$", re.I)


def status_id(url: str) -> str:
    match = STATUS_RE.search(url or "")
    return match.group(1) if match else ""


def split_author_quote(text: str) -> tuple[str, str]:
    text = " ".join((text or "").split())
    for marker in (" Quote ", " Show more Quote "):
        if marker in text:
            left, right = text.split(marker, 1)
            return left.strip(), right.strip()
    return text.strip(), ""


def strip_ui_noise(text: str) -> str:
    tokens = []
    skip = {
        "Pinned",
        "Serenity",
        "@aleabitoreddit",
        "·",
        "Show",
        "more",
        "Translate",
        "post",
        "analytics",
    }
    for token in text.split():
        if token in skip:
            continue
        if METRIC_TOKEN_RE.match(token):
            continue
        tokens.append(token)
    return " ".join(tokens).strip()


def post_type(row: dict[str, str], author_text: str) -> str:
    raw = (row.get("post_type") or "").strip()
    if raw:
        return raw
    return "reply" if "Replying to" in author_text else "original_or_quote"


def clean_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    cleaned = []
    seen = set()
    for row in rows:
        url = row.get("x_url") or row.get("url") or ""
        sid = status_id(url)
        if not sid or sid in seen:
            continue
        seen.add(sid)
        author_text, quote_context = split_author_quote(row.get("text", ""))
        author_text = strip_ui_noise(author_text)
        tickers = sorted({t.upper() for t in TICKER_RE.findall(author_text)})
        cleaned.append(
            {
                "status_id": sid,
                "x_url": f"https://x.com/{AUTHOR}/status/{sid}",
                "posted_at": row.get("posted_at", ""),
                "post_type": post_type(row, author_text),
                "author_text": author_text,
                "quote_context": quote_context,
                "tickers": ";".join(tickers),
                "needs_detail_fetch": "yes" if "Show more" in row.get("text", "") else "no",
            }
        )
    return cleaned


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "status_id",
        "x_url",
        "posted_at",
        "post_type",
        "author_text",
        "quote_context",
        "tickers",
        "needs_detail_fetch",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_ticker_counts(path: Path, rows: list[dict[str, str]]) -> None:
    counts: Counter[str] = Counter()
    for row in rows:
        for ticker in filter(None, row["tickers"].split(";")):
            counts[ticker] += 1
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ticker", "count"])
        for ticker, count in counts.most_common():
            writer.writerow([ticker, count])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--out", type=Path, default=Path("serenity_x_author_cleaned.csv"))
    parser.add_argument("--ticker-out", type=Path, default=Path("serenity_x_author_cleaned_ticker_frequency.csv"))
    args = parser.parse_args()

    rows = clean_rows(read_csv(args.input_csv))
    write_csv(args.out, rows)
    write_ticker_counts(args.ticker_out, rows)
    print(f"cleaned_rows={len(rows)}")
    print(f"out={args.out}")
    print(f"ticker_out={args.ticker_out}")


if __name__ == "__main__":
    main()
