# prospect-radar

I build and fix websites and data setups for small businesses. Finding who actually needs help is the slow part: opening fifty sites one by one to see which are slow, not mobile-friendly, untracked or abandoned. `prospect-radar` does that pass for me. Give it a CSV of business websites and it ranks them by **upside**: how much a fix would be worth to them, with each issue written in words a business owner understands.

**Who it's for:** freelancers and small agencies who sell web, SEO or analytics work.
**Built with:** Python 3.11+, standard library only. No API keys, no accounts.

## What it does

```
| # | Business                     | Upside | Top issue                                              |
|---|------------------------------|--------|--------------------------------------------------------|
| 1 | Old Town Bakery (fictional)  | 95     | No mobile viewport: the site is not built for phones.  |
| 2 | Riverside Dental (fictional) | 28     | No usable meta description, so Google writes its own...|
| 3 | Northlight Studio (fictional)| 0      | Nothing major                                          |
```

It fetches each homepage once and checks 17 things that matter to a business, weighted by impact: HTTPS, load time, mobile viewport, title and description, headings, analytics and ad pixel, a contact route and a one-tap phone/email/WhatsApp link, structured data, social preview, a stale copyright year, image alt text, language and favicon. The report is Markdown (ranking plus a section per site) or CSV for a spreadsheet or CRM.

**What it deliberately does not do:** no security probing, and no collecting of emails, phone numbers or names. It only checks whether a contact route exists, never what it contains. It respects `robots.txt`, makes one request per site, waits a second between sites and identifies itself in its User-Agent.

## Run it

Try it offline on made-up sites:

```bash
git clone https://github.com/ralcaraz6/prospect-radar.git
cd prospect-radar
PYTHONPATH=src python3 -m prospect_radar --demo
```

On real sites:

```bash
cp prospects.example.csv prospects.csv     # columns: name,url
PYTHONPATH=src python3 -m prospect_radar prospects.csv --out report.md
PYTHONPATH=src python3 -m prospect_radar prospects.csv --out report.csv
```

`prospects.csv` and generated reports are git-ignored. Or install it with `pip install -e .` and run `prospect-radar --demo`.

## Tests

```bash
python3 -m unittest discover -s tests
```

## Plans

See [ROADMAP.md](ROADMAP.md): per-site one-page audits to send, reports in Spanish and German, real page-weight and image-size checks, re-checks over time.

## License

MIT.
