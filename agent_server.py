"""
agent_server.py — the small local API the README's roadmap calls for:
"swap the interpreter for agent.py behind a small API so arbitrary questions
work end-to-end."

This exposes agent.py's real LLM agent (Claude + the constrained tools in
tools.py) over HTTP so web/index.html's Ask box can call it directly. Stdlib
only (http.server) — the only dependency is the `anthropic` package agent.py
already required.

The server never invents the claims shown in the UI: it tracks every
link_papers(field_a, field_b) call the model makes, resolves those to real
field ids, and hands back just that ordered list of pairs plus the model's
prose. The browser builds the actual clickable claims from its own
network-data.js via the exact same mkLink()/EDGE_MAP code path the built-in
deterministic interpreter uses — so a claim can never appear on screen
without a real edge (and real papers) behind it.

Usage (local):
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...
    python agent_server.py
    # in another terminal, from web/:
    python -m http.server 8000

The page checks http://localhost:8765/health on load; if this server isn't
running, the Ask box quietly falls back to the built-in deterministic
interpreter instead of breaking.

Usage (deployed, e.g. behind GitHub Pages — see README):
    Set these env vars on whatever host runs this file. PORT is read
    automatically (Render/Railway/Fly all set it); ALLOWED_ORIGIN should be
    your exact GitHub Pages origin, not "*", once this is public — an
    ANTHROPIC_API_KEY reachable from the whole internet is worth locking down.
        ANTHROPIC_API_KEY=sk-ant-...
        ALLOWED_ORIGIN=https://yourname.github.io
    Start command: python agent_server.py
"""

import json
import os
import re
import sys
import time
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import tools

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", os.environ.get("AGENT_PORT", "8765")))
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")
MAX_TOOL_TURNS = 6
MAX_QUESTION_CHARS = 300

# a public /ask endpoint spends your Anthropic budget on every request, so this
# is a real (if minimal) guard, not just local-dev decoration: per-IP, a fixed
# window of requests per hour. Good enough for a small demo; if this ever gets
# real traffic, put a proper reverse-proxy rate limiter in front of it instead.
RATE_LIMIT = int(os.environ.get("RATE_LIMIT_PER_HOUR", "20"))
_hits = defaultdict(deque)


def _rate_limited(ip):
    now = time.time()
    q = _hits[ip]
    while q and now - q[0] > 3600:
        q.popleft()
    if len(q) >= RATE_LIMIT:
        return True
    q.append(now)
    return False

SYSTEM = """You are a research-exploration agent for Florida State University \
publication data. You help a user understand how research fields connect.

Hard rules:
- You may ONLY state numbers that came back from a tool call. Never estimate or \
invent a figure.
- Whenever your answer references a specific link between two fields, call \
link_papers for that exact pair first, even if you already saw the number via \
top_collaborations or field_papers — that call is what makes the claim \
clickable to real evidence in the interface. Call it for every pair you \
mention, not just one.
- If the question doesn't concern this dataset (cross-field research \
collaboration at FSU, 2018-2026), say so plainly instead of forcing an answer.
- Distinguish observations (what the data shows) from conclusions (your \
interpretation). End your reply in exactly this shape and nothing after it:
OBSERVATION: <one or two plain sentences describing what the data shows>
CONCLUSION: <one tentative sentence of your own reading — omit this whole \
line if you don't have one>
"""


def run_agent(question, path="web/network.json"):
    import anthropic

    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": question}]
    net = tools._net(path)
    seen = set()
    edge_pairs = []  # ordered, deduped [a, b] field-id pairs surfaced via a tool call

    def add_edge(a, b):
        if not a or not b:
            return
        key = tuple(sorted([a, b]))
        if key not in seen:
            seen.add(key)
            edge_pairs.append(list(key))

    text = ""
    for _ in range(MAX_TOOL_TURNS):
        resp = client.messages.create(
            # claude-sonnet-5 runs adaptive thinking by default, which spends
            # tokens from this same budget before any tool call or text is
            # emitted — 800 was low enough that harder questions could hit
            # max_tokens mid-plan (stop_reason "max_tokens", not "tool_use"),
            # silently dropping the tool call before it ever ran
            model=MODEL, max_tokens=4096, system=SYSTEM,
            tools=tools.TOOL_SCHEMA, messages=messages,
        )
        tool_uses = [b for b in resp.content if b.type == "tool_use"]
        text = "".join(b.text for b in resp.content if b.type == "text")
        print(f"[agent_server] turn stop_reason={resp.stop_reason} "
              f"tool_calls={[tu.name for tu in tool_uses]}", file=sys.stderr)
        if resp.stop_reason != "tool_use":
            break

        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for tu in tool_uses:
            result = tools.call(tu.name, tu.input, path=path)
            if tu.name == "link_papers":
                add_edge(tools._resolve_field(tu.input.get("field_a", ""), net),
                          tools._resolve_field(tu.input.get("field_b", ""), net))
            elif tu.name == "top_collaborations":
                # top_collaborations() already returns real, tool-verified edges
                # (field ids + work_ids straight from the network data) — a claim
                # built from these is just as grounded as one from link_papers,
                # so capture them even if the model never separately calls
                # link_papers for the same pair (it often won't, despite being
                # asked to — this makes the guarantee structural, not prompt-reliant)
                for row in result.get("data", []):
                    edge = row.get("edge")
                    if edge and len(edge) == 2:
                        add_edge(edge[0], edge[1])
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": json.dumps(result)})
        messages.append({"role": "user", "content": results})

    print(f"[agent_server] done: {len(edge_pairs)} edge(s) captured, "
          f"final text len={len(text)}", file=sys.stderr)
    return finalize(text, edge_pairs)


def finalize(text, edge_pairs):
    obs = re.search(r"OBSERVATION:\s*(.+)", text)
    con = re.search(r"CONCLUSION:\s*(.+)", text)
    interp = obs.group(1).strip() if obs else (text.strip() or "Here's what the data shows.")
    conclusion = con.group(1).strip() if con else ""
    return {"interp": interp, "conclusion": conclusion, "edgePairs": edge_pairs}


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Vary", "Origin")

    def _json(self, status, obj):
        payload = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"ok": True, "model": MODEL})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/ask":
            self._json(404, {"error": "not found"})
            return
        if _rate_limited(self.client_address[0]):
            self._json(429, {"error": "rate limit exceeded — try again later"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            question = (body.get("question") or "").strip()
            if not question:
                raise ValueError("empty question")
            if len(question) > MAX_QUESTION_CHARS:
                raise ValueError(f"question too long (max {MAX_QUESTION_CHARS} characters)")
        except ValueError as e:
            # a bad request from this client — not a sign the server is down,
            # so the frontend should keep treating the agent as online
            self._json(400, {"error": str(e)})
            return
        try:
            if not os.environ.get("ANTHROPIC_API_KEY"):
                raise RuntimeError("ANTHROPIC_API_KEY is not set on the server")
            self._json(200, run_agent(question))
        except Exception as e:
            self._json(500, {"error": str(e)})

    def log_message(self, fmt, *args):
        sys.stderr.write("[agent_server] " + (fmt % args) + "\n")


if __name__ == "__main__":
    try:
        import anthropic  # noqa: F401 -- fail fast with a clear message
    except ImportError:
        sys.exit("Install the SDK first:  pip install anthropic")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY is not set — /ask will return an error until it is.",
              file=sys.stderr)
    if ALLOWED_ORIGIN == "*":
        print("Warning: ALLOWED_ORIGIN is '*' — fine for local dev, but lock this to your "
              "GitHub Pages origin before deploying publicly (anyone could otherwise spend "
              "your Anthropic budget from any page).", file=sys.stderr)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"agent_server listening on http://{HOST}:{PORT}  (POST /ask, GET /health)")
    server.serve_forever()
