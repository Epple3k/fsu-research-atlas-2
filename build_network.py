"""
build_network.py

Pure transform logic: given a list of OpenAlex `works` records, produce the
field co-occurrence network that the whole app is built on.

The one idea that makes this project more than a chatbot: every number the
interface can state is backed by the specific work IDs behind it. So an edge
between two fields doesn't just carry a weight -- it carries the list of works
that produced that weight. Click a claim, get the papers.

This file has no network calls, so it can be unit-tested on mock works.
fetch_openalex.py calls build_network() on the works it downloads.
"""

from itertools import combinations
from collections import defaultdict

# How "interdisciplinary" is operationalised for v0.1:
# a work is interdisciplinary if its topics span more than one OpenAlex *field*
# (the 26 top-level buckets, e.g. Physics, Psychology). Each such work draws an
# edge between every pair of fields it touches. Defensible, cheap, and every
# edge is auditable back to real papers.

EARLY = range(2018, 2022)   # 2018-2021
LATE = range(2022, 2027)    # 2022-2026
MAX_PROVENANCE_PER_EDGE = 60  # cap stored work IDs per edge to keep the file small


def _short_id(openalex_url):
    """https://openalex.org/W123 -> W123 ; already-short ids pass through."""
    return openalex_url.rsplit("/", 1)[-1] if openalex_url else openalex_url


def fields_of(work):
    """Distinct (field_id, field_name) pairs appearing in a work's topics."""
    seen = {}
    for topic in work.get("topics") or []:
        field = (topic or {}).get("field") or {}
        fid = _short_id(field.get("id"))
        if fid:
            seen[fid] = field.get("display_name", fid)
    return seen  # {field_id: field_name}


def build_network(works, institution=None, years=None):
    field_names = {}
    field_works = defaultdict(set)          # field -> set(work_id)
    field_interdisc_works = defaultdict(set)
    edge_weight = defaultdict(int)          # (a,b) sorted -> count
    edge_works = defaultdict(list)          # (a,b) sorted -> [work_id,...] (capped)
    # trend accounting: distinct partner fields and work counts per window
    trend = defaultdict(lambda: {"early": 0, "late": 0,
                                 "partners_early": set(), "partners_late": set()})
    works_meta = {}
    used_work_ids = set()

    for w in works:
        wid = _short_id(w.get("id"))
        if not wid:
            continue
        year = w.get("publication_year")
        fields = fields_of(w)
        if not fields:
            continue

        for fid, fname in fields.items():
            field_names[fid] = fname
            field_works[fid].add(wid)
            if year in EARLY:
                trend[fid]["early"] += 1
            elif year in LATE:
                trend[fid]["late"] += 1

        if len(fields) > 1:  # interdisciplinary work -> edges
            fids = sorted(fields)
            for fid in fids:
                field_interdisc_works[fid].add(wid)
            for a, b in combinations(fids, 2):
                key = (a, b)
                edge_weight[key] += 1
                if len(edge_works[key]) < MAX_PROVENANCE_PER_EDGE:
                    edge_works[key].append(wid)
                if year in EARLY:
                    trend[a]["partners_early"].add(b)
                    trend[b]["partners_early"].add(a)
                elif year in LATE:
                    trend[a]["partners_late"].add(b)
                    trend[b]["partners_late"].add(a)
            # only keep metadata for works we can actually cite from an edge
            works_meta[wid] = {"t": (w.get("title") or "Untitled")[:180], "y": year}
            used_work_ids.add(wid)

    # per-window edge weights so the AI can say "+42% since 2022" and prove it
    edge_early = defaultdict(int)
    edge_late = defaultdict(int)
    for w in works:
        year = w.get("publication_year")
        fields = sorted(fields_of(w))
        if len(fields) > 1:
            for a, b in combinations(fields, 2):
                if year in EARLY:
                    edge_early[(a, b)] += 1
                elif year in LATE:
                    edge_late[(a, b)] += 1

    fields_out = [
        {"id": fid, "name": field_names[fid],
         "works": len(field_works[fid]),
         "interdisc_works": len(field_interdisc_works[fid])}
        for fid in sorted(field_names, key=lambda f: -len(field_works[f]))
    ]

    edges_out = []
    for (a, b), weight in edge_weight.items():
        e, l = edge_early[(a, b)], edge_late[(a, b)]
        delta = None if e == 0 else round((l - e) / e * 100)
        edges_out.append({"a": a, "b": b, "weight": weight,
                          "early": e, "late": l, "delta_pct": delta,
                          "work_ids": edge_works[(a, b)]})
    edges_out.sort(key=lambda x: -x["weight"])

    trends_out = {}
    for fid, t in trend.items():
        pe, pl = len(t["partners_early"]), len(t["partners_late"])
        trends_out[fid] = {
            "early": t["early"], "late": t["late"],
            "partners_early": pe, "partners_late": pl,
            "partner_delta": pl - pe,
        }

    return {
        "meta": {"institution": institution or "Unknown",
                 "years": years or "", "work_count": len(works),
                 "interdisc_work_count": len(used_work_ids)},
        "fields": fields_out,
        "edges": edges_out,
        "works": works_meta,
        "trends": trends_out,
    }


def write_outputs(net, outdir="web"):
    """Write network.json (read by the Python tools/agent) and network-data.js
    (read by the browser, so index.html works even opened straight off disk)."""
    import json, os
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "network.json"), "w") as f:
        json.dump(net, f, separators=(",", ":"))
    with open(os.path.join(outdir, "network-data.js"), "w") as f:
        f.write("window.NETWORK = ")
        json.dump(net, f, separators=(",", ":"))
        f.write(";")


if __name__ == "__main__":
    # tiny smoke test on mock works
    mock = [
        {"id": "https://openalex.org/W1", "title": "CS meets Medicine", "publication_year": 2024,
         "topics": [{"field": {"id": "https://openalex.org/fields/17", "display_name": "Computer Science"}},
                    {"field": {"id": "https://openalex.org/fields/27", "display_name": "Medicine"}}]},
        {"id": "https://openalex.org/W2", "title": "Pure physics", "publication_year": 2019,
         "topics": [{"field": {"id": "https://openalex.org/fields/31", "display_name": "Physics and Astronomy"}}]},
        {"id": "https://openalex.org/W3", "title": "CS + Medicine again", "publication_year": 2019,
         "topics": [{"field": {"id": "https://openalex.org/fields/17", "display_name": "Computer Science"}},
                    {"field": {"id": "https://openalex.org/fields/27", "display_name": "Medicine"}}]},
    ]
    import json
    print(json.dumps(build_network(mock, "Test U", "2018-2026"), indent=2))
