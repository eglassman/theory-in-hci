#!/usr/bin/env python3
"""Write every paper in a DBLP proceedings listing to a CSV file.

Default target is the CHI 2026 main proceedings:
    https://dblp.org/db/conf/chi/chi2026.html

Usage:
    python3 tools/dblp_to_csv.py                      # -> chi2026_papers.csv
    python3 tools/dblp_to_csv.py -o out.csv
    python3 tools/dblp_to_csv.py --url https://dblp.org/db/conf/chi/chi2025.html

Uses only the Python standard library.

How it works: every DBLP table-of-contents page (".../chi2026.html") has an
XML twin (".../chi2026.xml") that lists each entry with its session heading.
The script reads that XML. If the XML can't be read, it falls back to the
DBLP search API (toc:<key>.bht:), which paginates but has no session headings.
"""

import argparse
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

USER_AGENT = "theory-in-hci dblp_to_csv/1.0 (research script)"
FIELDS = ["index", "session", "title", "authors", "pages", "year",
          "doi", "url", "dblp_key"]


def fetch(url, retries=4):
    """GET a URL, backing off politely if DBLP rate-limits (HTTP 429)."""
    delay = 2
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < retries:
                wait = int(e.headers.get("Retry-After") or delay)
                print(f"  HTTP {e.code}; retrying in {wait}s", file=sys.stderr)
                time.sleep(wait)
                delay *= 2
                continue
            raise


def text(el):
    """All text inside an element, including text inside nested tags like <i>."""
    return "".join(el.itertext()).strip() if el is not None else ""


def doi_from(ees):
    for ee in ees:
        if "doi.org/" in ee:
            return ee.split("doi.org/", 1)[1]
    return ""


def papers_from_toc_xml(xml_url):
    """Yield papers, in page order, from a DBLP TOC XML file."""
    root = ET.fromstring(fetch(xml_url))
    session = ""
    for el in root.iter():
        if el.tag in ("h2", "h3"):
            session = text(el)
        elif el.tag == "inproceedings":
            ees = [text(e) for e in el.findall("ee")]
            yield {
                "session": session,
                "title": text(el.find("title")).rstrip("."),
                "authors": "; ".join(text(a) for a in el.findall("author")),
                "pages": text(el.find("pages")),
                "year": text(el.find("year")),
                "doi": doi_from(ees),
                "url": ees[0] if ees else "",
                "dblp_key": el.get("key", ""),
            }


def papers_from_search_api(toc_key, page_size=1000):
    """Yield papers via the DBLP search API, page by page (no session info)."""
    first = 0
    while True:
        q = urllib.parse.urlencode({
            "q": f"toc:{toc_key}.bht:", "format": "json",
            "h": page_size, "f": first})
        data = json.loads(fetch(f"https://dblp.org/search/publ/api?{q}"))
        hits = data["result"]["hits"]
        total = int(hits.get("@total", 0))
        for hit in hits.get("hit", []):
            info = hit["info"]
            if info.get("type") == "Editorship":
                continue  # the proceedings volume itself, not a paper
            authors = info.get("authors", {}).get("author", [])
            if isinstance(authors, dict):
                authors = [authors]
            yield {
                "session": "",
                "title": info.get("title", "").rstrip("."),
                "authors": "; ".join(a["text"] for a in authors),
                "pages": info.get("pages", ""),
                "year": info.get("year", ""),
                "doi": info.get("doi", ""),
                "url": info.get("ee", ""),
                "dblp_key": info.get("key", ""),
            }
        first += page_size
        if first >= total:
            break
        time.sleep(1)  # be gentle with DBLP


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="https://dblp.org/db/conf/chi/chi2026.html",
                    help="DBLP table-of-contents page (default: CHI 2026)")
    ap.add_argument("-o", "--output", help="CSV path (default: <volume>_papers.csv)")
    args = ap.parse_args()

    path = urllib.parse.urlparse(args.url).path        # /db/conf/chi/chi2026.html
    toc_key = path.lstrip("/").rsplit(".", 1)[0]       # db/conf/chi/chi2026
    out = args.output or f"{toc_key.rsplit('/', 1)[-1]}_papers.csv"

    try:
        xml_url = f"https://dblp.org/{toc_key}.xml"
        print(f"Reading {xml_url}", file=sys.stderr)
        papers = list(papers_from_toc_xml(xml_url))
        if not papers:
            raise ValueError("no papers found in TOC XML")
    except Exception as e:
        print(f"TOC XML failed ({e}); using the DBLP search API", file=sys.stderr)
        papers = list(papers_from_search_api(toc_key))

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for i, p in enumerate(papers, 1):
            w.writerow({"index": i, **p})
    print(f"Wrote {len(papers)} papers to {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
