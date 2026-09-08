"""
fetch_openalex.py

Pulls Florida State University works from OpenAlex and writes web/network.json,
the single file the interface reads. Run this once (re-run to refresh).

    python fetch_openalex.py --email you@example.com

The --email puts you in OpenAlex's fast "polite pool". It's free and needs no
key. Uses only the Python standard library.
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

from build_network import build_network

FSU_ID = "I103163165"          # from the institutions?search=Florida State University lookup
BASE = "https://api.openalex.org/works"
# Only pull the fields we actually use -> smaller, faster responses.
SELECT = "id,title,publication_year,topics"


def fetch_works(institution_id, year_range, email, max_works):
    params_filter = f"institutions.id:{institution_id},publication_year:{year_range}"
    cursor = "*"
    got = []
    page = 0
    while cursor and len(got) < max_works:
        params = {
            "filter": params_filter,
            "select": SELECT,
            "per-page": "200",
            "cursor": cursor,
        }
        if email:
            params["mailto"] = email
        url = BASE + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": f"research-explorer ({email or 'anon'})"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.load(resp)
        except Exception as e:
            print(f"\nRequest failed: {e}", file=sys.stderr)
            print("If this is a network error, check your connection and retry.", file=sys.stderr)
            break
        results = data.get("results", [])
        got.extend(results)
        cursor = data.get("meta", {}).get("next_cursor")
        page += 1
        total = data.get("meta", {}).get("count", "?")
        print(f"  page {page}: +{len(results)} works "
              f"({len(got)} collected of {total} total)", flush=True)
        if not results:
            break
        time.sleep(0.1)  # be gentle
    return got[:max_works]


def main():
    ap = argparse.ArgumentParser(description="Pull FSU research data from OpenAlex.")
    ap.add_argument("--email", default=os.environ.get("OPENALEX_EMAIL", ""),
                    help="your email, for OpenAlex's polite pool (recommended)")
    ap.add_argument("--institution", default=FSU_ID, help="OpenAlex institution ID")
    ap.add_argument("--years", default="2018-2026", help="publication year range")
    ap.add_argument("--max-works", type=int, default=8000,
                    help="cap on works to pull (v0.1 default keeps it snappy)")
    ap.add_argument("--out", default="web/network.json")
    ap.add_argument("--name", default="Florida State University")
    args = ap.parse_args()

    if not args.email:
        print("Tip: pass --email you@example.com for faster, more reliable requests.\n")

    print(f"Fetching {args.name} works {args.years} from OpenAlex...")
    works = fetch_works(args.institution, args.years, args.email, args.max_works)
    if not works:
        print("No works fetched -- nothing written.", file=sys.stderr)
        sys.exit(1)

    print(f"\nBuilding field co-occurrence network from {len(works)} works...")
    net = build_network(works, institution=args.name, years=args.years)

    from build_network import write_outputs
    outdir = os.path.dirname(args.out) or "."
    write_outputs(net, outdir)
    kb = os.path.getsize(args.out) // 1024

    print(f"\nWrote {args.out} and network-data.js ({kb} KB)")
    print(f"  {len(net['fields'])} fields, {len(net['edges'])} field-to-field links")
    print(f"  {net['meta']['interdisc_work_count']} interdisciplinary works")
    top = net["edges"][0] if net["edges"] else None
    if top:
        fname = {f["id"]: f["name"] for f in net["fields"]}
        print(f"  strongest link: {fname.get(top['a'])} <-> {fname.get(top['b'])} "
              f"({top['weight']} works)")
    print("\nNext: open web/index.html in a browser.")


if __name__ == "__main__":
    main()
