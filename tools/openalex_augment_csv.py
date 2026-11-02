#!/usr/bin/env python3
"""Add every field OpenAlex has for each paper to a CSV that has a `doi` column.

Usage:
    python3 tools/openalex_augment_csv.py chi2026_papers.csv
        # -> chi2026_papers_openalex.csv
    python3 tools/openalex_augment_csv.py in.csv -o out.csv

Uses only the Python standard library. Looks DOIs up in batches of 50 with the
OpenAlex works API (https://api.openalex.org). Without a key, requests share a
small free daily budget with everyone on the same IP address. A free personal
key (https://help.openalex.org/api/authentication/) avoids that: pass it with
--api-key or set OPENALEX_API_KEY.

Each original column is kept as is. OpenAlex fields are appended, prefixed
`openalex_`:
  * plain values (title, publication_date, cited_by_count, fwci, ...) get
    their own column;
  * objects are spread one level (openalex_open_access.oa_status, ...); any
    deeper value is written as JSON;
  * lists (authorships, topics, keywords, referenced_works, ...) are written as
    JSON, so nothing is dropped;
  * a few readable extras are added: openalex_abstract (rebuilt from the
    abstract_inverted_index), openalex_author_names, openalex_institutions,
    openalex_topic_names, openalex_keyword_names.
A cell is blank when OpenAlex has no value for that paper, or has no record
for its DOI at all.
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.openalex.org/works"
USER_AGENT = "theory-in-hci openalex_augment_csv/1.0 (research script)"
BATCH = 50
PREFIX = "openalex_"


def fetch_json(url, api_key=None, retries=5):
    delay = 2
    headers = {"User-Agent": USER_AGENT}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 429 and int(e.headers.get("Retry-After") or 0) > 300:
                body = e.read().decode("utf-8", "replace")
                sys.exit(f"OpenAlex daily budget used up: {body}")
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                print(f"  HTTP {e.code}; retrying in {delay}s", file=sys.stderr)
                time.sleep(delay)
                delay *= 2
                continue
            raise


def norm_doi(doi):
    doi = (doi or "").strip().lower()
    for p in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.startswith(p):
            doi = doi[len(p):]
    return doi


def lookup(dois, api_key=None):
    """Return {normalized doi: OpenAlex work} for the DOIs OpenAlex knows."""
    works = {}
    for i in range(0, len(dois), BATCH):
        chunk = dois[i:i + BATCH]
        q = urllib.parse.urlencode({
            "filter": "doi:" + "|".join(chunk), "per-page": BATCH})
        for w in fetch_json(f"{API}?{q}", api_key).get("results", []):
            works[norm_doi(w.get("doi"))] = w
        print(f"  looked up {min(i + BATCH, len(dois))}/{len(dois)}", file=sys.stderr)
        time.sleep(0.2)  # stay well under OpenAlex's rate limit
    return works


def cell(v):
    if v is None or v == [] or v == {}:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (str, int, float)):
        return v
    return json.dumps(v, ensure_ascii=False)


def abstract(inv):
    if not inv:
        return ""
    words = {}
    for word, positions in inv.items():
        for p in positions:
            words[p] = word
    return " ".join(words[p] for p in sorted(words))


def join_unique(names):
    seen = []
    for n in names:
        if n and n not in seen:
            seen.append(n)
    return "; ".join(seen)


def flatten(work):
    row = {}
    for k, v in work.items():
        if isinstance(v, dict) and v:
            for sk, sv in v.items():
                row[f"{PREFIX}{k}.{sk}"] = cell(sv)
        else:
            row[PREFIX + k] = cell(v)
    auths = work.get("authorships") or []
    row[PREFIX + "abstract"] = abstract(work.get("abstract_inverted_index"))
    row[PREFIX + "author_names"] = join_unique(
        (a.get("author") or {}).get("display_name") for a in auths)
    row[PREFIX + "institutions"] = join_unique(
        inst.get("display_name") for a in auths for inst in a.get("institutions") or [])
    row[PREFIX + "topic_names"] = join_unique(
        t.get("display_name") for t in work.get("topics") or [])
    row[PREFIX + "keyword_names"] = join_unique(
        k.get("display_name") for k in work.get("keywords") or [])
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="CSV with a `doi` column")
    ap.add_argument("-o", "--output", help="CSV path (default: <input>_openalex.csv)")
    ap.add_argument("--api-key", default=os.environ.get("OPENALEX_API_KEY"),
                    help="OpenAlex API key (default: $OPENALEX_API_KEY)")
    args = ap.parse_args()
    out = args.output or args.input.rsplit(".", 1)[0] + "_openalex.csv"

    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        base_fields = reader.fieldnames
        rows = list(reader)

    dois = sorted({norm_doi(r["doi"]) for r in rows if r.get("doi")})
    print(f"Looking up {len(dois)} DOIs in OpenAlex", file=sys.stderr)
    works = lookup(dois, args.api_key)

    extra = [flatten(works[norm_doi(r.get("doi"))]) if norm_doi(r.get("doi")) in works
             else {} for r in rows]
    readable = [PREFIX + n for n in ("abstract", "author_names", "institutions",
                                     "topic_names", "keyword_names")]
    oa_fields = readable[:]
    for e in extra:
        for k in e:
            if k not in oa_fields:
                oa_fields.append(k)

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=base_fields + oa_fields, restval="")
        w.writeheader()
        for r, e in zip(rows, extra):
            w.writerow({**r, **e})
    print(f"Matched {len(works)}/{len(dois)} DOIs; wrote {len(rows)} rows, "
          f"{len(base_fields + oa_fields)} columns to {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
