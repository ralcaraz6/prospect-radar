"""Turn audits into a ranked Markdown report and a CSV for a spreadsheet or CRM."""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import date

from .checks import Finding, upside


@dataclass
class Audit:
    name: str
    url: str
    findings: list[Finding] | None = None
    error: str = ""

    @property
    def score(self) -> int:
        return upside(self.findings) if self.findings else -1

    @property
    def failed(self) -> list[Finding]:
        return sorted((f for f in self.findings or [] if not f.passed), key=lambda f: -f.weight)


def ranked(audits: list[Audit]) -> list[Audit]:
    return sorted(audits, key=lambda a: -a.score)


def to_markdown(audits: list[Audit], today: date) -> str:
    ok = [a for a in ranked(audits) if a.findings]
    out = [f"# Prospect radar, {today.isoformat()}", "",
           f"{len(ok)} sites audited, ranked by upside (how much a fix is worth to them).", "",
           "| # | Business | Upside | Top issue |", "|---|---|---|---|"]
    for i, a in enumerate(ok, 1):
        top = a.failed[0].message if a.failed else "Nothing major"
        out.append(f"| {i} | {a.name} | {a.score} | {top} |")
    out.append("")
    for a in ok:
        out += [f"## {a.name} ({a.score})", "", a.url, ""]
        out += [f"- {f.message}" for f in a.failed] or ["- No issues found."]
        out.append("")
    errors = [a for a in audits if a.error]
    if errors:
        out += ["## Not audited", ""] + [f"- {a.name}: {a.error}" for a in errors] + [""]
    return "\n".join(out)


def to_csv(audits: list[Audit]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["business", "url", "upside", "issues", "top_issue", "error"])
    for a in ranked(audits):
        w.writerow([a.name, a.url, a.score if a.findings else "", len(a.failed),
                    a.failed[0].id if a.failed else "", a.error])
    return buf.getvalue()
