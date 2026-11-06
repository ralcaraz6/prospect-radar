# Roadmap

What I plan to build next, roughly in order. Estimates are honest guesses.

## Done (v0.1)
- [x] Polite fetcher: robots.txt, one request per site, delay between sites, clear User-Agent
- [x] 17 weighted homepage checks written for business owners, and an upside score
- [x] Ranked Markdown report and CSV export
- [x] `--demo` on made-up offline sites, unit tests, CI on every push

## Next: something I can send (~10 h)
- [ ] One-page HTML audit per site, printable to PDF, with the 3 biggest fixes first — 4 h
- [ ] Report language switch: English, Spanish, German — 3 h
- [ ] Estimated effort per fix (quick win / half day / project) to price an offer — 2 h
- [ ] Config file to change weights and turn checks off — 1 h

## Then: better checks (~10 h)
- [ ] Real page weight: sum images, scripts and styles referenced by the homepage — 3 h
- [ ] Oversized images (dimensions and bytes) — 2 h
- [ ] Mobile-unfriendly signals beyond the viewport (fixed widths, tiny fonts) — 2 h
- [ ] Booking or online-ordering presence for local businesses — 1 h
- [ ] Parallel fetching with a per-host limit — 2 h

## Later: keep it running (~8 h)
- [ ] Store audits in SQLite and show what changed since the last run — 4 h
- [ ] `--since` to list sites that got worse or were redesigned — 2 h
- [ ] Recorded-response tests for the web fetcher — 2 h

Out of scope on purpose: security scanning of any kind, and collecting personal data (emails, phone numbers, names).
