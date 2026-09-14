# FSU Research Explorer — interaction and design specification

## Product promise

A user can ask a question about cross-field FSU research, inspect a supported claim, see the corresponding relationship in context and open the exact records behind it.

The product must never display an AI-generated quantitative claim without a corresponding relationship in the local dataset.

## Primary workflow

1. The interface opens with a useful deterministic investigation already rendered.
2. The user enters a question or selects a suggested question.
3. The product attempts the hosted agent.
4. If the agent returns supported field pairs, the browser reconstructs claim cards from local data.
5. If the agent is unavailable or the question cannot be handled, the deterministic interpreter responds.
6. Selecting a claim sets the active state, highlights relevant nodes and edges and loads the supporting papers.
7. Opening a paper launches its OpenAlex record in a new tab.

## Components and required states

| Component | Default | Interactive | Empty / error |
|---|---|---|---|
| Ask input | Placeholder explains supported question | Focus border; Enter submits | Empty submission uses the first example |
| Ask button | Enabled | Shows “Thinking…” in results during request | Falls back to deterministic response |
| Suggested chip | Neutral pill | Hover/focus treatment; click submits | Not applicable |
| Agent badge | Checking | Connected or demo-interpreter state | Offline state remains usable |
| Claim card | Neutral | Hover, selected | Zero-claim explanation |
| Network edge | Base weight and opacity | Preview, selected, dimmed | No matching edge means no claim |
| Network node | Label and radius | Hover, drag, drop target, snap-back | Isolated field still remains visible |
| Evidence panel | Prompt to select a claim | List of linked papers | Explicit no-records message |
| Tooltip | Hidden | Field or edge summary | Hidden on leave |
| Case-study link | Visible in header | Hover/focus underline | Not applicable |

## Study mode

The query parameter controls the comparison condition:

- ?study=full — normal evidence-first interface.
- ?study=control — claims still select and highlight the network, but paper-level evidence and evidence cues are removed.

The control condition must not imply that no evidence exists. It should state that source detail is unavailable in this comparison version.

## Interaction rules

### Claims

- A claim can only be created from a real edge in network data.
- Selecting a claim clears the previous selected state.
- Selected fields and their edge remain visually dominant.
- Hover previews must restore the committed selected state when the pointer leaves.
- In full mode, selecting a claim populates evidence immediately.
- In control mode, selecting a claim does not expose work IDs or paper links.

### Network

- Edge thickness communicates number of shared works.
- Hovering a node previews its connected edges.
- Hovering an edge previews only that relationship.
- Dragging a node updates all connected paths continuously.
- Releasing a node returns it to its seriated home position.
- Beginning a new drag cancels any previous snap-back animation for that node.
- Reduced-motion preferences disable nonessential transitions.

### Agent

- The browser should not render arbitrary numbers from model prose as claim metrics.
- Tool outputs provide field pairs and provenance IDs.
- The local dataset remains the source of visible counts and evidence links.
- Network failure, timeout or a sleeping backend must preserve a useful deterministic experience.
- A 4xx response falls back for that question without permanently marking the server unavailable.
- A server or network failure changes the badge to the offline state.

## Content hierarchy

1. **Observation:** exact relationship, count or time comparison; sans-serif.
2. **Interpretation:** what the observation may mean; serif.
3. **Evidence cue:** action-oriented accent text.
4. **Source record:** paper title, year and OpenAlex ID.

Typography is supportive, not sufficient. Labels must remain understandable without relying only on font family, weight or color.

## Edge cases

- Four results: cards should remain readable without creating an empty evidence region.
- Hundreds of papers: the panel should eventually paginate or virtualize; the current prototype may scroll.
- No direct link: explain that no shared interdisciplinary work appears in the dataset.
- Unknown field term: return the supported question shapes.
- Empty result from the agent: do not show unsupported prose as a final evidence-backed claim.
- Backend cold start: retain the 45-second request timeout and visible thinking state.
- Mobile layout: network appears above the investigation panel; both remain usable.
- Missing data file: show local-server and data-generation instructions.

## Accessibility checklist

- Preserve semantic buttons, inputs, links and headings.
- Add visible keyboard focus wherever hover styling exists.
- Do not communicate evidence state through color alone.
- Keep text contrast at WCAG AA levels.
- Give the network an accessible label and provide textual claims as the usable alternative.
- Verify the workflow at 200% zoom and at 320px width.
- Respect prefers-reduced-motion.
- Ensure external links announce their destination in visible text.

## Known limitations

- Fields are OpenAlex categories, not FSU administrative departments.
- Publication co-occurrence is a proxy for interdisciplinarity, not a complete measure.
- The “since 2022” comparison uses two windows rather than a causal growth model.
- A network is effective for pattern recognition but weak for exact comparison without textual support.
- The primary user and trust effects have not yet been validated through completed sessions.
- Hosted AI availability and latency depend on the backend service.
