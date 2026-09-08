"""
agent.py  (optional — the real AI-orchestration layer)

The frontend ships with a deterministic interpreter so the demo runs with no
key. This file is the grown-up version the brief points at: the LLM never
computes numbers itself — it only calls the constrained tools in tools.py, and
every figure it reports is carried by real work IDs (provenance).

Usage:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...
    python agent.py "which areas are becoming more interdisciplinary?"

Model: set MODEL below or via env. Pick a current model id from your console
(see https://docs.claude.com/en/api/overview).
"""

import json
import os
import sys

import tools

MODEL = os.environ.get("MODEL", "claude-sonnet-5")

SYSTEM = """You are a research-exploration agent for Florida State University \
publication data. You help a user understand how research fields connect.

Hard rules:
- You may ONLY state numbers that came back from a tool call. Never estimate or \
invent a figure.
- Prefer to break a question into tool calls, then explain what you found.
- When you make a claim about a specific link between two fields, call \
link_papers so the exact papers are available as evidence.
- Distinguish observations (what the data shows) from conclusions (your \
interpretation). Keep conclusions clearly tentative.
"""


def run(question, path="web/network.json"):
    try:
        import anthropic
    except ImportError:
        sys.exit("Install the SDK first:  pip install anthropic")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Set ANTHROPIC_API_KEY in your environment first.")

    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": question}]
    collected_provenance = []  # every work id any tool surfaced this turn

    while True:
        resp = client.messages.create(
            model=MODEL, max_tokens=1200, system=SYSTEM,
            tools=tools.TOOL_SCHEMA, messages=messages,
        )
        # surface any tool calls
        tool_uses = [b for b in resp.content if b.type == "tool_use"]
        for b in resp.content:
            if b.type == "text" and b.text.strip():
                print("\n" + b.text.strip() + "\n")

        if resp.stop_reason != "tool_use":
            break

        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for tu in tool_uses:
            print(f"  → tool: {tu.name}({json.dumps(tu.input)})")
            result = tools.call(tu.name, tu.input, path=path)
            collected_provenance.extend(result.get("work_ids", []))
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": json.dumps(result)})
        messages.append({"role": "user", "content": results})

    # the punchline: the claims above are all backed by these specific papers
    uniq = list(dict.fromkeys(collected_provenance))
    if uniq:
        print(f"[provenance] {len(uniq)} works underlie the figures above, e.g.:")
        net = json.load(open(path))
        for wid in uniq[:5]:
            w = net["works"].get(wid)
            if w:
                print(f"   {wid}  {w['t'][:70]}  https://openalex.org/{wid}")


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "which research areas are most interconnected?"
    run(q)
