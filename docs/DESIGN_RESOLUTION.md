# Research Atlas: The Crossing Field
## Design resolution · October 2026

### The particular problem

A university can have tens of thousands of publications without having an immediately readable picture of how its research fields intersect. Publication search works when you know an author or paper. It is weaker for *discovery* questions: Which disciplines produce work together? Which intersections are substantial? Which have appeared more often in the later years of the dataset? Can I inspect the actual studies behind the pattern?

The existing Research Explorer was a radial network with 26 fields and 279 relationships. The network was technically connected to real data, but it encouraged an aesthetic reading before an analytical one. It was difficult to compare arc thicknesses, find two named fields, discern the absence of a relationship, or tell where a claim came from without following a separate interaction chain. A conventional dashboard would introduce a different problem: neat rankings without relational context. A chatbot alone would add convenient phrasing without guaranteeing transparent evidence.

**Resolution:** Make the *crossing of two research fields* the primary unit of discovery. Give each crossing a permanent spatial address, make its magnitude visible relative to other crossings, and make the source publications one selection away.

### What is unique about the data

The source is an OpenAlex-derived FSU publication dataset covering 2018–2026. Each work may be assigned to one or more OpenAlex **research fields**; those are not administrative departments, nor do they directly describe interpersonal collaboration. A crossing occurs when a work is assigned to both fields in a pair. A publication assigned to three fields contributes to three pairwise connections. That means pairwise counts cannot be summed to obtain the number of distinct interdisciplinary papers.

The builder records:

- Total works per field
- For every field pair, the count of works assigned to both fields
- Counts in the 2018–2021 and 2022–2026 windows
- The percent difference between the windows where an earlier baseline exists
- Up to 60 supporting work IDs per field pair
- Titles and years for indexed interdisciplinary works

These affordances shaped the visualization. The interface must not imply department-level funding flows, citations between fields, researcher collaboration, statistically established growth, or complete publication evidence when only capped IDs are stored.

### How the form follows the problem

**1. Replace arc soup with a crossing field.** A two-dimensional field-by-field matrix gives every pair an exact lookup address. Each tile means one thing: the number of publications tagged with both fields. Stronger color means a larger count; an uncolored cell means no connection was recorded. Every pair appears symmetrically, so someone looking up either discipline can find it.

**2. Arrange by relationships, not a generic alphabet.** Field order uses co-occurrence weights so stronger neighbors tend to sit closer. Bright blocks then suggest communities of research intersection without inventing a cluster label, an embedding, or a formal community-detection result.

**3. Make the contrast measurable.** "Shared works" and "Window shift" are distinct map modes. The second compares the actual early/later count windows, with negative and positive change encoded separately. The product explicitly discloses that the windows differ in length and are not annualized.

**4. Join macro pattern to micro evidence.** Select a crossing and the same workspace shows its two named fields, exact shared-work count, the two period counts, and real source paper links. Counts come from local data, not an AI response. The source list transparently indicates its 60-ID-per-pair storage cap.

**5. Search what actually exists.** The main field accepts actual field names, paper title fragments, exact two-field queries and questions. Field and title lookup run directly on the indexed data. A paper can be opened directly even when it lies outside the retained 60-ID-per-pair provenance subset. The user is never asked to guess a keyword from a decorative graph.

**6. Do not make AI availability a prerequisite.** The earlier interface could wait indefinitely for a sleeping hosted agent. The atlas opens as soon as the publication file loads. Questions receive an immediate deterministic, evidence-linked reading; the optional agent can refine it if connected. Unsupported numeric claims cannot enter the displayed results.

### Product experience

**Land.** The headline says "Where research crosses." Real data-driven signals immediately expose a strong crossing, a notable shift, and a field with many connections. These are computed from the loaded dataset.

**Scan.** In the crossing field, color and negative space reveal structure more quickly than hundreds of individually drawn links.

**Narrow.** Search a field, select a row or column, type a paper title, or click a signal. The atlas constrains attention without discarding the overall view.

**Inspect.** Select a tile. The evidence inspector shows exact counts and public records, including a clear caveat about the comparison periods.

**Question.** Follow a source to OpenAlex. Use an optional natural-language investigation for additional evidence-backed claims, never replacing the raw record.

### Important design tradeoffs

- **Matrix over network:** Easier comparison, lookup and explicit absences; less visually suggestive of paths longer than one connection. The primary task is direct field-pair evidence, so this is an acceptable limitation.
- **Symmetric duplication:** Each pair appears twice; this improves field-based lookup but must be explained so users do not double-count.
- **Relative intensity:** Uses a logarithmic scale to avoid a single very large crossing washing out all others. Precise figures always remain available in the inspector.
- **Pairwise co-occurrence:** This is a useful proxy for interdisciplinarity, not direct evidence of team collaboration or research impact.
- **Unequal time windows:** The mode surfaces descriptive differences, not annualized growth rates or causal trends.
- **Evidence storage cap:** Up to 60 source IDs are retained per pair; this is not a random or necessarily representative sample of all contributing papers.
- **Search limitation:** Local title matching operates over indexed interdisciplinary works, not all publications in OpenAlex. It does not claim full-text search.

### Validation, not invented findings

The redesigned mechanism is implemented, but no new usability results are claimed. The existing six-to-eight-participant evidence-visibility comparison was prepared for an earlier network layout and should be revised before collecting data with the new interface.

Suggested task-based evaluation:
1. Find a strong crossing between unfamiliar fields without being told which tile to open.
2. Locate a named field and discover its three largest recorded intersections.
3. Identify a crossing that changed between the two windows without incorrectly calling the percent a normalized annual growth rate.
4. Find a publication by title and open its exact OpenAlex record.
5. Explain what an empty intersection means, and what it **does not** mean.
6. Describe the chain of evidence for an AI-supported observation, including the difference between the full count and stored source IDs.

Collect task success, time, misinterpretations, provenance clicks, confidence, and ability to explain counts. In particular, compare first-glance comprehension and accurate source identification against the previous radial graph. Do not equate interface polish with demonstrated understanding.

### The success criterion

A first-time visitor should be able to explain **what a square represents**, find one interesting relation, and open a real supporting paper, without a tour or a model-generated paragraph. The graphics are successful only when they reduce the work required to understand the research landscape.
