"""
tools.py

The constrained tool surface the AI is allowed to touch. The AI never sees raw
data and never computes numbers itself -- it calls these, and every result
carries the work IDs behind it. That's what makes a claim clickable later.

Each tool returns a dict shaped like:
    {"observation": <human-readable>, "data": {...}, "work_ids": [...]}
so the caller (agent or UI) can render the number AND jump to the evidence.
"""

import json
from functools import lru_cache


@lru_cache(maxsize=1)
def _net(path="web/network.json"):
    with open(path) as f:
        net = json.load(f)
    net["_fname"] = {f["id"]: f["name"] for f in net["fields"]}
    net["_fid"] = {f["name"].lower(): f["id"] for f in net["fields"]}
    return net


def _resolve_field(name_or_id, net):
    if name_or_id in net["_fname"]:
        return name_or_id
    key = str(name_or_id).lower()
    if key in net["_fid"]:
        return net["_fid"][key]
    # loose contains-match, e.g. "computer" -> "Computer Science"
    for fname, fid in net["_fid"].items():
        if key in fname:
            return fid
    return None


def list_fields(path="web/network.json"):
    """All research fields present, with how many works each has."""
    net = _net(path)
    return {"observation": f"{len(net['fields'])} fields present",
            "data": [{"field": f["name"], "works": f["works"]} for f in net["fields"]],
            "work_ids": []}


def top_collaborations(limit=8, path="web/network.json"):
    """The strongest cross-field links, i.e. which areas most co-occur in work."""
    net = _net(path)
    out = []
    for e in net["edges"][:limit]:
        out.append({"a": net["_fname"][e["a"]], "b": net["_fname"][e["b"]],
                    "weight": e["weight"], "delta_pct": e["delta_pct"],
                    "edge": [e["a"], e["b"]], "work_ids": e["work_ids"]})
    return {"observation": f"top {len(out)} cross-field links by shared works",
            "data": out,
            "work_ids": [wid for e in out for wid in e["work_ids"]]}


def interdisciplinarity_trend(limit=8, path="web/network.json"):
    """Fields whose number of distinct collaborating fields grew the most
    from 2018-2021 to 2022-2026 -- i.e. becoming more interdisciplinary."""
    net = _net(path)
    rows = []
    for fid, t in net["trends"].items():
        rows.append({"field": net["_fname"].get(fid, fid),
                     "id": fid,
                     "partners_early": t["partners_early"],
                     "partners_late": t["partners_late"],
                     "partner_delta": t["partner_delta"]})
    rows.sort(key=lambda r: -r["partner_delta"])
    return {"observation": "change in number of collaborating fields, early vs late window",
            "data": rows[:limit],
            "work_ids": []}


def field_papers(field, limit=25, path="web/network.json"):
    """Interdisciplinary papers that involve a given field, with titles + links."""
    net = _net(path)
    fid = _resolve_field(field, net)
    if not fid:
        return {"observation": f"no field matching '{field}'", "data": [], "work_ids": []}
    ids = []
    for e in net["edges"]:
        if e["a"] == fid or e["b"] == fid:
            ids.extend(e["work_ids"])
    seen, papers = set(), []
    for wid in ids:
        if wid in seen or wid not in net["works"]:
            continue
        seen.add(wid)
        w = net["works"][wid]
        papers.append({"id": wid, "title": w["t"], "year": w["y"],
                       "url": f"https://openalex.org/{wid}"})
        if len(papers) >= limit:
            break
    return {"observation": f"{len(papers)} interdisciplinary papers involving {net['_fname'][fid]}",
            "data": papers,
            "work_ids": [p["id"] for p in papers]}


def link_papers(field_a, field_b, limit=25, path="web/network.json"):
    """The specific papers behind the link between two fields -- the evidence
    a user sees when they click a claim like 'X connects to Y'."""
    net = _net(path)
    a, b = _resolve_field(field_a, net), _resolve_field(field_b, net)
    if not a or not b:
        return {"observation": "one or both fields not found", "data": [], "work_ids": []}
    key = tuple(sorted([a, b]))
    for e in net["edges"]:
        if (e["a"], e["b"]) == key:
            papers = []
            for wid in e["work_ids"][:limit]:
                w = net["works"].get(wid)
                if w:
                    papers.append({"id": wid, "title": w["t"], "year": w["y"],
                                   "url": f"https://openalex.org/{wid}"})
            return {"observation": f"{e['weight']} shared works between "
                                   f"{net['_fname'][a]} and {net['_fname'][b]}",
                    "data": papers, "work_ids": [p["id"] for p in papers]}
    return {"observation": "no direct link between those fields", "data": [], "work_ids": []}


# Schema advertised to the LLM (Anthropic tool-use format). agent.py imports this.
TOOL_SCHEMA = [
    {"name": "list_fields", "description": "List all research fields and their work counts.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "top_collaborations",
     "description": "Strongest cross-field links (which areas most co-occur in the same works).",
     "input_schema": {"type": "object",
                      "properties": {"limit": {"type": "integer", "default": 8}}}},
    {"name": "interdisciplinarity_trend",
     "description": "Which fields gained the most distinct collaborating fields from 2018-2021 to 2022-2026.",
     "input_schema": {"type": "object",
                      "properties": {"limit": {"type": "integer", "default": 8}}}},
    {"name": "field_papers",
     "description": "Interdisciplinary papers involving a named field.",
     "input_schema": {"type": "object",
                      "properties": {"field": {"type": "string"},
                                     "limit": {"type": "integer", "default": 25}},
                      "required": ["field"]}},
    {"name": "link_papers",
     "description": "The specific papers behind the link between two named fields (the evidence for a claim).",
     "input_schema": {"type": "object",
                      "properties": {"field_a": {"type": "string"},
                                     "field_b": {"type": "string"},
                                     "limit": {"type": "integer", "default": 25}},
                      "required": ["field_a", "field_b"]}},
]

DISPATCH = {"list_fields": list_fields, "top_collaborations": top_collaborations,
            "interdisciplinarity_trend": interdisciplinarity_trend,
            "field_papers": field_papers, "link_papers": link_papers}


def call(name, args, path="web/network.json"):
    fn = DISPATCH[name]
    return fn(path=path, **(args or {}))


if __name__ == "__main__":
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else "web/network.json"
    print(json.dumps(top_collaborations(path=p), indent=2)[:1500])
