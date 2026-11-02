#!/usr/bin/env python3
"""Write every paper in an ACM proceedings volume to a CSV file, via Crossref.

Default target is the CHI 2026 main proceedings
(Proceedings of the 2026 CHI Conference on Human Factors in Computing Systems,
DOI 10.1145/3772318).

Usage:
    python3 tools/crossref_to_csv.py                  # -> chi2026_papers.csv
    python3 tools/crossref_to_csv.py -o out.csv
    python3 tools/crossref_to_csv.py \\
        --container "Proceedings of the 2025 CHI Conference on Human Factors in Computing Systems" \\
        --volume-doi 10.1145/3706598 -o chi2025_papers.csv

Uses only the Python standard library. Useful when dblp.org answers with its
"Making sure you're not a bot!" page (see tools/dblp_to_csv.py). Crossref has
no session headings, so this CSV has none.

How it works: asks the Crossref REST API for every proceedings-article whose
container title is the volume's exact title, paging with a cursor, and keeps
only DOIs under the volume DOI (10.1145/<volume>.<paper>).
"""

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.crossref.org/works"
USER_AGENT = "theory-in-hci crossref_to_csv/1.0 (research script)"
FIELDS = ["index", "title", "authors", "pages", "year", "doi", "url"]
DEFAULT_CONTAINER = ("Proceedings of the 2026 CHI Conference on "
                     "Human Factors in Computing Systems")
DEFAULT_VOLUME_DOI = "10.1145/3772318"


def fetch_json(url, retries=4):
    delay = 2
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                print(f"  HTTP {e.code}; retrying in {delay}s", file=sys.stderr)
                time.sleep(delay)
                delay *= 2
                continue
            raise


def author_name(a):
    if "given" in a or "family" in a:
        return " ".join(p for p in (a.get("given"), a.get("family")) if p)
    return a.get("name", "")


def year_of(item):
    for k in ("published", "published-print", "published-online", "issued"):
        parts = item.get(k, {}).get("date-parts", [[None]])
        if parts and parts[0] and parts[0][0]:
            return str(parts[0][0])
    return ""


def papers(container, volume_doi, mailto=None):
    cursor = "*"
    while True:
        params = {
            "filter": f"type:proceedings-article,container-title:{container}",
            "rows": 1000, "cursor": cursor,
            "select": "DOI,title,author,page,published,issued,URL",
        }
        if mailto:
            params["mailto"] = mailto
        msg = fetch_json(f"{API}?{urllib.parse.urlencode(params)}")["message"]
        items = msg.get("items", [])
        if not items:
            return
        for it in items:
            doi = it.get("DOI", "")
            if volume_doi and not doi.lower().startswith(volume_doi.lower() + "."):
                continue
            yield {
                "title": " ".join((it.get("title") or [""])[0].split()),
                "authors": "; ".join(author_name(a) for a in it.get("author", [])),
                "pages": it.get("page", ""),
                "year": year_of(it),
                "doi": doi,
                "url": f"https://doi.org/{doi}",
            }
        cursor = msg.get("next-cursor")
        if not cursor:
            return
        time.sleep(1)  # be polite


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--container", default=DEFAULT_CONTAINER,
                    help="exact proceedings title in Crossref (default: CHI 2026)")
    ap.add_argument("--volume-doi", default=DEFAULT_VOLUME_DOI,
                    help="keep only DOIs under this volume DOI ('' to keep all)")
    ap.add_argument("--mailto", help="your email, sent to Crossref's polite pool")
    ap.add_argument("-o", "--output", default="chi2026_papers.csv", help="CSV path")
    args = ap.parse_args()

    rows = sorted(papers(args.container, args.volume_doi, args.mailto),
                  key=lambda p: p["doi"])
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for i, p in enumerate(rows, 1):
            w.writerow({"index": i, **p})
    print(f"Wrote {len(rows)} papers to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
