# FSU Research Explorer — v0.1

Ask a question about how research areas connect, see a network, and **click any
claim to see the exact papers behind it.** Not a chatbot that draws charts — an
interface where every number the AI states is traceable to real records.

Built on [OpenAlex](https://openalex.org) publication data for Florida State
University (institution `I103163165`).

## The product problem

Publication databases are effective when someone already knows which paper,
author, or topic to search for. They are much harder to use for exploratory
questions such as:

- Which research areas are becoming more interdisciplinary?
- Where are strong cross-field relationships forming?
- What evidence supports that conclusion?
- Can a user inspect the records instead of trusting an aggregate or AI summary?

The provisional primary user is a university research strategist investigating
cross-disciplinary activity before deciding where to focus outreach or deeper
analysis. That user definition is a design hypothesis until interviews are
completed.

> **Design hypothesis:** AI can make a large research dataset easier to
> interrogate, but users should not have to accept its numerical claims on
> fluency alone. Every generated conclusion should remain visually and
> interactively attached to the evidence that produced it.

That creates the core product loop:

```
question → constrained analysis → observation → clickable claim → network focus → source papers
```

### Why the interface works this way

- **Claims are interactive objects, not a block of prose.** Selecting one
  highlights its relationship and exposes the papers behind it.
- **The network explores; text specifies.** The graph reveals relational
  structure while claim cards communicate exact values.
- **Observation and interpretation have different voices.** Measurements use
  the sans-serif interface voice; interpretive conclusions use a contrasting
  serif voice.
- **The model never owns the numbers.** The agent selects constrained tools,
  while the browser reconstructs visible claims from local, provenance-bearing
  data.

The tradeoff is deliberate: constraining the agent makes the answer less
free-form, but makes unsupported quantitative claims structurally harder to
display.

### Evaluation status

The mechanism is implemented; its effect on user comprehension and calibrated
trust has not been established yet. A counterbalanced 6–8 participant comparison
is prepared using a claim-only control and the full evidence-first interface.
Results will be added only after real sessions are completed.

## Product-design materials

The repository now includes the product story and the materials needed to evaluate it without inventing findings:

- **[Live product-design case study](https://epple3k.github.io/fsu-research-atlas-2/case-study.html)** — problem, hypothesis, design decisions, implementation iteration and evaluation plan.
- **[Case-study copy](docs/CASE_STUDY_COPY.md)** — portable copy for a portfolio CMS.
- **[Evaluation plan](docs/EVALUATION_PLAN.md)** — counterbalanced comparison, moderator script, tasks, measures and analysis.
- **[Session record](docs/SESSION_RECORD.md)** — duplicate once per participant.
- **[Results template](docs/RESULTS_TEMPLATE.md)** and **[fillable CSV](docs/results-template.csv)** — aggregate the study and document the iteration.
- **[Interaction specification](docs/DESIGN_SPEC.md)** — component states, behavioral rules, edge cases and accessibility checklist.

The two test views are `?study=control` (claim-only) and `?study=full` (evidence-first). Results are intentionally not claimed until real sessions are completed.

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
interpreter automatically. The server never invents a claim: it hands the page only field pairs returned
by the constrained analysis tools, and the page builds each clickable claim
from real `network-data.js` edges — so a claim on screen always traces to real
papers.

### Publishing to GitHub Pages, with the real AI

GitHub Pages only serves static files — it cannot run `agent_server.py` (no
Python, no long-lived process). The frontend and backend are hosted
separately; both are set up in this repo to need as few manual steps as
possible.

1. **Deploy `agent_server.py` to Render.** `render.yaml` in this repo is a
   [Render Blueprint](https://render.com/docs/blueprint-spec) — Render reads
   it and configures the build/start commands and `ALLOWED_ORIGIN` itself:

   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Epple3k/fsu-research-atlas-2)

   Click it, sign in (or create a free account) and authorize Render to read
   this repo, then approve the blueprint. The only field you type by hand is
   `ANTHROPIC_API_KEY` — Render prompts for it as a secret because
   `render.yaml` marks it `sync: false`, so it's never written to the repo.

   Once it deploys, copy the service's URL from the Render dashboard (looks
   like `https://fsu-research-atlas-agent.onrender.com`).

   - **Set a spend limit / usage alert in your Anthropic console.** The rate
     limiting and origin check in `agent_server.py` are reasonable guards for
     a small demo, not a substitute for that — a determined caller can still
     hit the endpoint directly.
   - Free instances sleep after inactivity; the first request after a sleep
     can take 30–50s to wake up. The page's "Thinking…" state and its
     45-second request timeout are already sized for this.
   - If you rename the service (or it's already taken), Render appends
     characters to keep the URL unique — always use the exact URL Render
     shows you, not the one guessed above.

2. **Point the page at that URL.** In `web/index.html`, find
   `PRODUCTION_AGENT_BASE` near the top of the script and set it to the
   Render URL from step 1. This is the one edit the file needs before
   publishing — locally it still talks to `http://localhost:8765`
   automatically. Commit and push that change.

3. **Turn on GitHub Pages via the included Action.** `.github/workflows/pages.yml`
   publishes just the `web/` folder as the site root — no `/web/` in the URL,
   and it redeploys on every push to `main`. One manual step: in the repo's
   **Settings → Pages**, set **Build and deployment → Source** to
   **GitHub Actions** (not "Deploy from a branch"). The workflow runs
   automatically after that.

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
| `render.yaml` | Render Blueprint for one-click `agent_server.py` deployment |
| `.github/workflows/pages.yml` | publishes `web/` to GitHub Pages as the site root |

---

## Where to take it next

- Add uncertainty / conflicting-evidence states to claims.
- Let users challenge an interpretation and re-run with changed assumptions.
- Break "field" down to department or author level for finer networks.
- Run the evaluation from the brief: give people a task, measure trust with vs.
  without visible provenance.
