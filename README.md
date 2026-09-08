# FSU Research Explorer — v0.1

Ask a question about how research areas connect, see a network, and **click any
claim to see the exact papers behind it.** Not a chatbot that draws charts — an
interface where every number the AI states is traceable to real records.

Built on [OpenAlex](https://openalex.org) publication data for Florida State
University (institution `I103163165`).

---

## Run it (2 minutes)

The repo ships with **sample data**, so you can look first:

```bash
cd web
python -m http.server 8000
# open http://localhost:8000
```

Then pull the **real FSU data** (free, no API key):

```bash
python fetch_openalex.py --email you@example.com
```

Reload the page. The sample badge disappears and you're on live OpenAlex data.

> Opening `web/index.html` by double-click works too — it reads `network-data.js`
> directly — but a local server is the reliable path.

### Turn on the real AI (optional)

Without it, the Ask box uses a deterministic keyword interpreter — no key
needed, but it only understands a fixed set of question shapes. To make it
actually understand free-form questions, run the small local API in front of
`agent.py`:

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python agent_server.py
```

Leave that running and reload the page — the header badge flips to "AI agent
connected" and the Ask box calls Claude directly. If the server isn't running
(or goes down mid-session), the page falls back to the deterministic
interpreter automatically. The server never invents a claim: it only ever
hands the page the exact field pairs the model looked up via `tools.py`'s
`link_papers`, and the page builds the actual clickable claim from real
`network-data.js` edges — so a claim on screen always traces to real papers.

### Publishing to GitHub Pages, with the real AI

GitHub Pages only serves static files — it cannot run `agent_server.py` (no
Python, no long-lived process). The frontend and backend have to be hosted
separately:

1. **Deploy `agent_server.py` somewhere that runs a server.** [Render](https://render.com)'s
   free Web Service tier needs no Dockerfile:
   - New → Web Service → connect this repo.
   - Build command: `pip install -r requirements.txt`
   - Start command: `python agent_server.py`
   - Add environment variables:
     - `ANTHROPIC_API_KEY` = your key (as a secret)
     - `ALLOWED_ORIGIN` = `https://<your-username>.github.io` (your exact Pages
       URL — this locks the API to your page so random sites can't spend your
       Anthropic budget through it)
   - Render sets `PORT` for you automatically; the server already reads it.
   - Deploy, then copy the resulting URL (e.g. `https://fsu-research-atlas.onrender.com`).
   - **Set a spend limit / usage alert in your Anthropic console.** The rate
     limiting and origin check in `agent_server.py` are reasonable guards for
     a small demo, not a substitute for that — a determined caller can still
     hit the endpoint directly.
   - Free instances sleep after inactivity; the first request after a sleep
     can take 30–50s to wake up. The page's "Thinking…" state and its
     45-second request timeout are already sized for this.

2. **Point the page at that URL.** In `web/index.html`, find
   `PRODUCTION_AGENT_BASE` near the top of the script and set it to your
   Render URL. This is the one edit the file needs before publishing — locally
   it still talks to `http://localhost:8765` automatically.

3. **Publish `web/` to GitHub Pages.** Pages only serves from a repo's root or
   a `/docs` folder, not an arbitrary subfolder, so either:
   - copy/move `web/`'s contents to `/docs` (or the repo root) and point
     Pages at that, or
   - add a small GitHub Action that publishes the `web/` folder to a
     `gh-pages` branch.

   Then in the repo's Settings → Pages, pick that branch/folder as the source.

Without step 1–2, the static page still works fine on Pages — it just uses the
deterministic interpreter, same as running it locally with no `agent_server.py`.

---

## What v0.1 does

One dataset, one kind of question, one visualization, one interaction loop:

- **Network** — 26 OpenAlex fields as nodes; an arc between two fields is the set
  of papers whose topics span both. Thicker arc = more shared work.
- **Ask** — type a question (or tap a chip). The interpreter turns it into
  *claims*.
- **Click a claim** — the network highlights the exact links involved and the
  **Evidence** panel lists the real papers, each linking out to OpenAlex.

"Becoming more interdisciplinary" is operationalized as a field pair sharing more
papers in 2022–2026 than in 2018–2021 — and every % change traces back to works.

---

## The architecture (why it's more than a chatbot)

```
question → interpret → constrained tools → observations (+ work IDs) → claims → click → evidence
```

- **`build_network.py`** — pure transform: works → field co-occurrence network.
  Every edge stores the work IDs behind it. *This is the spine.*
- **`tools.py`** — the only surface the AI may touch. Each tool returns
  `{observation, data, work_ids}` — never a free-form number. Provenance is
  built in, not bolted on.
- **`agent.py`** *(optional)* — the real LLM layer. The model orchestrates the
  tools via Anthropic tool-use and may only report figures the tools returned.
  Needs `pip install anthropic` and `ANTHROPIC_API_KEY`.
- **`agent_server.py`** *(optional)* — puts `agent.py` behind a tiny local HTTP
  API (`POST /ask`) so the browser can call it. Tracks every `link_papers` call
  the model makes and hands back just those field-id pairs; the page builds the
  actual claim from its own data, so nothing shown can lack real evidence.
- **`web/index.html`** — the interface. Ships with a deterministic interpreter so
  the demo runs offline; calls `agent_server.py` automatically when it's running,
  for open-ended questions.

The frontend visually separates **observations** (data, in the sans face) from
**conclusions** (interpretation, in the serif face) — the distinction your
research question is about.

---

## Files

| File | Role |
|---|---|
| `fetch_openalex.py` | pull FSU works, write `web/network.json` + `network-data.js` |
| `build_network.py` | works → network with per-edge provenance (unit-testable) |
| `tools.py` | constrained, provenance-returning tools |
| `agent.py` | optional LLM orchestration over those tools |
| `agent_server.py` | optional local HTTP API putting `agent.py` behind the Ask box |
| `web/index.html` | the explorer UI |

---

## Where to take it next

- Add uncertainty / conflicting-evidence states to claims.
- Let users challenge an interpretation and re-run with changed assumptions.
- Break "field" down to department or author level for finer networks.
- Run the evaluation from the brief: give people a task, measure trust with vs.
  without visible provenance.
