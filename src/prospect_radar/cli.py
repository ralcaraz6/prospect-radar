"""prospect-radar: audit a list of business websites and rank them by how much they'd gain from a fix.

  prospect-radar prospects.csv --out report.md
  prospect-radar --demo
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

from .checks import run_checks
from .fetch import FetchError, FixtureFetcher, WebFetcher
from .report import Audit, to_csv, to_markdown

ROOT = Path(__file__).resolve().parents[2]


def load_prospects(path: Path) -> list[tuple[str, str]]:
    with open(path, newline="") as f:
        rows = [(r["name"].strip(), r["url"].strip()) for r in csv.DictReader(f) if r.get("url", "").strip()]
    if not rows:
        raise SystemExit(f"No rows with a url in {path} (columns: name,url)")
    return rows


def audit_all(prospects, fetcher, today: date) -> list[Audit]:
    audits = []
    for name, url in prospects:
        try:
            page = fetcher.get(url)
            audits.append(Audit(name, page.url, run_checks(page, today)))
        except FetchError as e:
            audits.append(Audit(name, url, error=str(e)))
        print(f"  {name}: {'ok' if audits[-1].findings else audits[-1].error}", file=sys.stderr)
    return audits


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="prospect-radar", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("prospects", nargs="?", type=Path, help="CSV with columns name,url")
    p.add_argument("--out", type=Path, help="write the report here (.md or .csv) instead of printing it")
    p.add_argument("--demo", action="store_true", help="audit made-up sample sites, offline")
    args = p.parse_args(argv)

    if args.demo:
        prospects = load_prospects(ROOT / "sample" / "prospects.csv")
        fetcher, today = FixtureFetcher(ROOT / "sample" / "sites"), date(2026, 11, 6)
    elif args.prospects:
        prospects, fetcher, today = load_prospects(args.prospects), WebFetcher(), date.today()
    else:
        p.error("give a prospects CSV or --demo")

    audits = audit_all(prospects, fetcher, today)
    text = to_csv(audits) if args.out and args.out.suffix == ".csv" else to_markdown(audits, today)
    if args.out:
        args.out.write_text(text)
        print(f"Wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
