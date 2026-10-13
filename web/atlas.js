/* Research Atlas / Crossings
   A question → relationship → source interaction for OpenAlex publication data.
   Every quantitative mark comes from the local network, not generated prose. */
(function () {
  "use strict";

  const params = new URLSearchParams(window.location.search);
  if (params.get("portfolioPreview") === "1") document.body.classList.add("is-portfolio-preview");
  const isControl = params.get("study") === "control";
  const money = n => Number(n || 0).toLocaleString("en-US");
  const escapeHTML = value => String(value ?? "").replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const pairKey = (a, b) => [a, b].sort().join("|");
  const clamp = (x, min, max) => Math.min(max, Math.max(min, x));

  window.initAtlas = function initAtlas(net, onQuestion) {
    const fields = net.fields.slice();
    const edges = net.edges.slice();
    const byId = Object.fromEntries(fields.map(f => [f.id, f]));
    const byPair = new Map(edges.map(e => [pairKey(e.a, e.b), e]));
    const byWork = new Map();
    for (const edge of edges) {
      for (const id of edge.work_ids || []) {
        if (!byWork.has(id)) byWork.set(id, []);
        byWork.get(id).push(edge);
      }
    }
    const works = Object.entries(net.works || {}).map(([id, record]) =>
      ({ id, title: record.t || "Untitled", year: record.y || "", search: (record.t || "").toLowerCase() }));
    const edgeFor = (a, b) => byPair.get(pairKey(a, b));
    const strength = f => edges.reduce((sum, e) =>
      sum + (e.a === f.id || e.b === f.id ? e.weight : 0), 0);

    // Seriate by actual co-occurrence, not alphabet. Adjacent blocks in the
    // matrix reveal strongly interconnected communities without invented labels.
    const remaining = new Set(fields.map(f => f.id));
    const order = [];
    const first = fields.slice().sort((a, b) => strength(b) - strength(a))[0];
    if (first) { order.push(first.id); remaining.delete(first.id); }
    while (remaining.size) {
      const previous = order[order.length - 1];
      const best = [...remaining].sort((a, b) =>
        (edgeFor(previous, b)?.weight || 0) + strength(byId[b]) * .025 -
        ((edgeFor(previous, a)?.weight || 0) + strength(byId[a]) * .025))[0];
      order.push(best); remaining.delete(best);
    }
    const sorted = order.map(id => byId[id]);
    const maxWeight = Math.max(1, ...edges.map(e => e.weight));
    let mode = "volume";
    let selected = null;
    let focusedField = null;
    let morePapers = false;
    let searchTimer = null;

    const grid = document.getElementById("atlas-matrix");
    const focusEl = document.getElementById("atlas-focus");
    const sourcesEl = document.getElementById("atlas-sources");
    const searchEl = document.getElementById("q");
    const searchResults = document.getElementById("search-results");
    const signals = document.getElementById("atlas-signals");
    const status = document.getElementById("atlas-status");
    if (!grid || !focusEl || !sourcesEl) return;

    function updateStatus(s) { if (status) status.textContent = s; }
    function selectionClasses() {
      const key = selected ? pairKey(selected.a, selected.b) : null;
      grid.querySelectorAll(".matrix-cell").forEach(cell => {
        const isSelected = key && cell.dataset.key === key;
        const isField = focusedField && (cell.dataset.a === focusedField || cell.dataset.b === focusedField);
        const hasFocus = Boolean(key || focusedField);
        const isPart = focusedField
          ? isField
          : selected && (cell.dataset.a === selected.a || cell.dataset.a === selected.b ||
            cell.dataset.b === selected.a || cell.dataset.b === selected.b);
        cell.classList.toggle("is-selected", Boolean(isSelected));
        cell.classList.toggle("is-focused", Boolean(isField));
        cell.classList.toggle("is-dimmed", hasFocus && !isPart);
        cell.setAttribute("aria-pressed", isSelected ? "true" : "false");
      });
      grid.querySelectorAll(".matrix-row,.matrix-col").forEach(cell => {
        const active = focusedField === cell.dataset.field ||
          Boolean(selected && (selected.a === cell.dataset.field || selected.b === cell.dataset.field));
        cell.classList.toggle("is-focused", active);
      });
    }

    function renderGrid() {
      grid.replaceChildren();
      grid.style.gridTemplateColumns =
        "var(--row-name) repeat(" + sorted.length + ", var(--cell))";
      grid.style.gridTemplateRows =
        "var(--column-label) repeat(" + sorted.length + ", var(--cell))";
      const fragment = document.createDocumentFragment();
      const corner = document.createElement("div");
      corner.className = "matrix-corner";
      corner.innerHTML = "FIELDS<br>× FIELDS<br><span style='color:#9c8e82;font-weight:400'>select an intersection ↘</span>";
      fragment.appendChild(corner);

      for (const field of sorted) {
        const head = document.createElement("button");
        head.type = "button";
        head.className = "matrix-col";
        head.dataset.field = field.id;
        head.textContent = field.name;
        head.title = "Focus " + field.name;
        head.setAttribute("aria-label", "Focus " + field.name);
        fragment.appendChild(head);
      }

      for (const row of sorted) {
        const label = document.createElement("button");
        label.type = "button";
        label.className = "matrix-row";
        label.dataset.field = row.id;
        label.textContent = row.name;
        label.title = "Focus " + row.name;
        fragment.appendChild(label);

        for (const col of sorted) {
          const cell = document.createElement("button");
          cell.type = "button";
          cell.className = "matrix-cell";
          cell.dataset.a = row.id;
          cell.dataset.b = col.id;
          cell.dataset.key = pairKey(row.id, col.id);
          const e = edgeFor(row.id, col.id);
          if (row.id === col.id) {
            cell.classList.add("is-self");
            cell.disabled = true;
            cell.title = "Same field";
          } else if (!e) {
            cell.disabled = true;
            cell.title = row.name + " × " + col.name + ": no shared papers in this dataset";
          } else {
            cell.classList.add("has-data");
            if (mode === "volume") {
              const alpha = .14 + .86 * Math.log1p(e.weight) / Math.log1p(maxWeight);
              cell.style.setProperty("--strength", alpha.toFixed(3));
            } else if (e.delta_pct == null) {
              cell.classList.add("is-unknown");
            } else {
              const intensity = .2 + .8 * clamp(Math.abs(e.delta_pct) / 250, 0, 1);
              cell.style.setProperty("--strength", intensity.toFixed(3));
              if (e.delta_pct < 0) cell.classList.add("is-negative");
            }
            const period = e.delta_pct == null
              ? " · no comparable earlier baseline"
              : " · " + (e.delta_pct > 0 ? "+" : "") + e.delta_pct + "% between windows";
            cell.title = row.name + " × " + col.name + " · " + money(e.weight) + " shared works" + period;
            cell.setAttribute("aria-label", cell.title);
            cell.setAttribute("aria-pressed", "false");
          }
          fragment.appendChild(cell);
        }
      }
      grid.appendChild(fragment);
      const keyEl = document.getElementById("map-legend-key");
      if (keyEl) {
        keyEl.innerHTML = mode === "volume"
          ? '<em>Color = shared publications</em><div class="swatches"><i style="background:#e8cbc6"></i><i style="background:#cf8e83"></i><i style="background:#a85148"></i><i style="background:#722720"></i></div> fewer → more'
          : '<em>Color = change between two unequal time windows</em><div class="swatches"><i style="background:#42738b"></i><i style="background:#d5c4ba"></i><i style="background:#e49784"></i><i style="background:#832b23"></i></div> lower ← → higher';
      }
      document.querySelectorAll("[data-atlas-mode]").forEach(button => {
        const active = button.dataset.atlasMode === mode;
        button.classList.toggle("is-active", active);
        button.setAttribute("aria-pressed", active ? "true" : "false");
      });
      selectionClasses();
    }

    function setMode(next) {
      mode = next === "change" ? "change" : "volume";
      renderGrid();
      updateStatus(mode === "change"
        ? "Comparing 2018–21 with 2022–26. These windows differ in length."
        : "Showing total shared publications between pairs of fields.");
    }

    function renderSources(edge) {
      if (isControl) {
        sourcesEl.innerHTML = '<h3>Source detail</h3><p>Paper-level sources are hidden in this comparison view. The counts and selection remain available.</p>';
        return;
      }
      if (!edge) {
        sourcesEl.innerHTML = '<h3>Source library</h3><p>Select a crossing to see the papers that constitute its relationship.</p>';
        return;
      }
      const totalStored = (edge.work_ids || []).length;
      const limit = morePapers ? totalStored : Math.min(8, totalStored);
      const a = byId[edge.a], b = byId[edge.b];
      const papers = (edge.work_ids || []).slice(0, limit)
        .map(id => ({ id, ...net.works[id] })).filter(p => p.t);
      sourcesEl.innerHTML = '<h3>Evidence, not just an answer.</h3>' +
        '<p>' + money(edge.weight) + ' works counted for ' + escapeHTML(a.name) + ' × ' +
          escapeHTML(b.name) + '. Showing ' + money(papers.length) +
          ' of ' + money(totalStored) + ' stored source IDs (the stored sample is capped at 60 per crossing).</p>' +
        papers.map(p => '<a class="source-paper" href="https://openalex.org/' +
          encodeURIComponent(p.id) + '" target="_blank" rel="noopener noreferrer">' +
          '<b>' + escapeHTML(p.t) + '</b><small>' + escapeHTML(p.y) +
          ' / OpenAlex record ↗</small></a>').join("") +
        (limit < totalStored
          ? '<button type="button" class="source-more" id="show-more-papers">Show all ' +
            money(totalStored) + ' stored records ↓</button>' : "");
      const more = document.getElementById("show-more-papers");
      if (more) more.addEventListener("click", () => { morePapers = true; renderSources(edge); });
    }

    function selectPair(a, b) {
      const edge = edgeFor(a, b);
      if (!edge) return false;
      selected = edge;
      focusedField = null;
      morePapers = false;
      selectionClasses();
      const A = byId[edge.a], B = byId[edge.b];
      const maxPeriod = Math.max(1, edge.early || 0, edge.late || 0);
      const timelineRow = (label, count, recent) => '<div class="timeline-row">' +
        '<span>' + label + '</span><div class="timeline-track"><div class="timeline-fill" style="width:' +
        (100 * count / maxPeriod).toFixed(1) + '%"></div></div><strong>' +
        money(count) + '</strong></div>';
      const delta = edge.delta_pct == null ? "" :
        '<strong>' + (edge.delta_pct > 0 ? "+" : "") + money(edge.delta_pct) +
        '%</strong> difference between counted windows. ';
      focusEl.innerHTML =
        '<div class="focus-eyebrow">A crossing / inspectable relationship</div>' +
        '<h2>' + escapeHTML(A.name) + ' <span class="crossing-name">×</span> ' +
        escapeHTML(B.name) + '</h2>' +
        '<div class="focus-count"><b>' + money(edge.weight) +
        '</b><span>publications tagged with both fields</span></div>' +
        '<p class="focus-explainer">' + delta +
        'These works bridge two OpenAlex research categories. Select the paper records below to see the evidence for yourself.</p>' +
        '<div class="focus-timeline"><h3>When the crossing appeared</h3>' +
        timelineRow("2018–21", edge.early || 0) + timelineRow("2022–26", edge.late || 0) +
        '<div class="timeline-caveat">Different-length windows; not annualized. A shift is an observation, not evidence of a causal trend.</div></div>';
      renderSources(edge);
      updateStatus("Selected " + A.name + " × " + B.name + ": " + money(edge.weight) + " shared works.");
      return true;
    }

    function focusField(id) {
      const f = byId[id]; if (!f) return;
      focusedField = id; selected = null;
      morePapers = false;
      selectionClasses();
      const related = edges.filter(e => e.a === id || e.b === id)
        .sort((a, b) => b.weight - a.weight);
      focusEl.innerHTML =
        '<div class="focus-eyebrow">Field / navigate its boundaries</div>' +
        '<h2>' + escapeHTML(f.name) + '</h2>' +
        '<div class="focus-count"><b>' + money(related.length) +
        '</b><span>other fields connected through shared publications</span></div>' +
        '<p class="focus-explainer"><strong>' + money(f.works) +
        ' works</strong> in this field across the dataset. Highlighted cells show where its publications cross disciplinary boundaries.</p>' +
        '<div class="partner-list"><h3>Explore its strongest crossings</h3>' +
        related.slice(0, 8).map(e => {
          const other = byId[e.a === id ? e.b : e.a];
          return '<button type="button" class="partner-link" data-partner="' +
            escapeHTML(other.id) + '"><span>' + escapeHTML(other.name) +
            '</span><strong>' + money(e.weight) + ' ↗</strong></button>';
        }).join("") + '</div>';
      focusEl.querySelectorAll("[data-partner]").forEach(button =>
        button.addEventListener("click", () => selectPair(id, button.dataset.partner)));
      renderSources(null);
      updateStatus("Viewing all crossings involving " + f.name);
    }

    function matchFields(query) {
      const q = query.toLowerCase().trim();
      return fields.filter(f => f.name.toLowerCase().includes(q));
    }

    function searchPapers(query, limit = 5) {
      const parts = query.toLowerCase().trim().split(/\s+/).filter(Boolean);
      if (!parts.length) return [];
      const found = [];
      for (const work of works) {
        if (parts.every(p => work.search.includes(p))) {
          found.push(work);
          if (found.length >= limit) break;
        }
      }
      return found;
    }

    function focusWork(work) {
      const connected = byWork.get(work.id) || [];
      if (connected.length) {
        const top = connected.slice().sort((a,b) => b.weight - a.weight)[0];
        selectPair(top.a, top.b);
        // Surface the matched publication at the start of the evidence list.
        const paperLink = [...sourcesEl.querySelectorAll(".source-paper")].find(link =>
          link.getAttribute("href")?.includes(encodeURIComponent(work.id)));
        if (paperLink) paperLink.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
      hideSearch();
    }

    function hideSearch() { searchResults.hidden = true; searchResults.replaceChildren(); }
    function renderSearchResults(q) {
      if (q.trim().length < 2) { hideSearch(); return; }
      const matchingFields = matchFields(q).slice(0, 6);
      const matchingPapers = searchPapers(q, 5);
      const clean = document.createDocumentFragment();
      const group = name => {
        const d = document.createElement("div");
        d.className = "search-group"; d.textContent = name; clean.appendChild(d);
      };
      const result = (label, kind, onSelect) => {
        const b = document.createElement("button");
        b.type = "button"; b.className = "search-hit";
        const name = document.createElement("span"); name.textContent = label;
        const badge = document.createElement("small"); badge.textContent = kind;
        b.append(name, badge); b.addEventListener("click", onSelect); clean.appendChild(b);
      };
      if (matchingFields.length) {
        group("Research fields");
        matchingFields.forEach(f => result(f.name, money(f.works) + " works", () => {
          focusField(f.id); hideSearch();
        }));
      }
      if (matchingPapers.length) {
        group("Papers in the indexed interdisciplinary set");
        matchingPapers.forEach(w => result(w.title, String(w.year || "Paper"), () => focusWork(w)));
      }
      if (!matchingFields.length && !matchingPapers.length) {
        group("No exact match");
        result("Investigate this as a question", "Ask ↗", () => {
          hideSearch(); askQuestion(searchEl.value);
        });
      }
      searchResults.replaceChildren(clean); searchResults.hidden = false;
    }

    function askQuestion(question) {
      hideSearch();
      if (!question.trim()) return;
      const results = document.getElementById("question-results");
      results.hidden = false;
      document.getElementById("question-label").textContent = question;
      onQuestion(question);
      if (!document.body.classList.contains("is-portfolio-preview")) {
        results.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    }

    function submitSearch() {
      const q = searchEl.value.trim(); if (!q) return;
      const qLower = q.toLowerCase();
      // Direct lookup should be immediate and local, including pair names.
      const named = fields.filter(f => f.name.length >= 3 && qLower.includes(f.name.toLowerCase()));
      if (named.length >= 2 && edgeFor(named[0].id, named[1].id)) {
        selectPair(named[0].id, named[1].id); hideSearch(); return;
      }
      const exact = fields.find(f => f.name.toLowerCase() === qLower);
      if (exact) { focusField(exact.id); hideSearch(); return; }
      const hits = matchFields(q);
      if (hits.length === 1 && !/[?!]/.test(q) && q.split(/\s+/).length <= 4) {
        focusField(hits[0].id); hideSearch(); return;
      }
      const paperHits = searchPapers(q, 1);
      if (paperHits.length && q.split(/\s+/).length > 2 && !/[?!]/.test(q)) {
        focusWork(paperHits[0]); return;
      }
      askQuestion(q);
    }

    grid.addEventListener("click", event => {
      const button = event.target.closest("button");
      if (!button) return;
      if (button.dataset.field) focusField(button.dataset.field);
      else if (button.dataset.a && button.dataset.b) selectPair(button.dataset.a, button.dataset.b);
    });
    document.querySelectorAll("[data-atlas-mode]").forEach(button =>
      button.addEventListener("click", () => setMode(button.dataset.atlasMode)));
    searchEl.addEventListener("input", () => {
      window.clearTimeout(searchTimer);
      searchTimer = window.setTimeout(() => renderSearchResults(searchEl.value), 100);
    });
    searchEl.addEventListener("keydown", event => {
      if (event.key === "Enter") { event.preventDefault(); submitSearch(); }
      if (event.key === "Escape") hideSearch();
    });
    document.getElementById("go").addEventListener("click", submitSearch);
    document.addEventListener("click", event => {
      if (!event.target.closest(".ask")) hideSearch();
    });

    function createSignal(eyebrow, title, detail, callback) {
      const button = document.createElement("button");
      button.type = "button"; button.className = "signal";
      button.innerHTML = "<span>" + escapeHTML(eyebrow) + "</span><strong>" +
        escapeHTML(title) + "</strong><small>" + escapeHTML(detail) + " ↗</small>";
      button.addEventListener("click", callback);
      signals.appendChild(button);
    }
    const strong = edges[0];
    const shifts = edges.filter(e => e.delta_pct != null && e.early >= 8 && e.weight >= 20)
      .sort((a,b) => b.delta_pct - a.delta_pct);
    const shifting = shifts[0] || strong;
    const broadest = fields.slice().sort((a,b) =>
      edges.filter(e => e.a === b.id || e.b === b.id).length -
      edges.filter(e => e.a === a.id || e.b === a.id).length)[0];
    if (strong) createSignal("Strongest crossing", byId[strong.a].name + " × " + byId[strong.b].name,
      money(strong.weight) + " shared works", () => {setMode("volume"); selectPair(strong.a,strong.b)});
    if (shifting) createSignal("Notable window shift", byId[shifting.a].name + " × " + byId[shifting.b].name,
      (shifting.delta_pct > 0 ? "+" : "") + money(shifting.delta_pct) + "% / unequal windows",
      () => {setMode("change"); selectPair(shifting.a,shifting.b)});
    if (broadest) createSignal("Broadest reach", broadest.name,
      money(edges.filter(e => e.a === broadest.id || e.b === broadest.id).length) + " connected fields",
      () => focusField(broadest.id));

    const chips = document.getElementById("chips");
    chips.replaceChildren();
    const prompt = (title, handler) => {
      const button = document.createElement("button");
      button.type = "button"; button.className = "chip"; button.textContent = title;
      button.addEventListener("click", handler); chips.appendChild(button);
    };
    prompt("01 / Heaviest crossings", () => { setMode("volume"); if(strong) selectPair(strong.a,strong.b); });
    prompt("02 / What has shifted?", () => { setMode("change"); if(shifting) selectPair(shifting.a,shifting.b); });
    prompt("03 / Explore a field", () => { searchEl.focus(); renderSearchResults("Science"); });
    prompt("04 / Ask a research question", () => {
      searchEl.value = "Which areas are becoming more interdisciplinary?";
      askQuestion(searchEl.value);
    });

    window.atlasSelectClaim = claim => {
      const pair = claim?.edges?.[0];
      if (pair && pair.length === 2) selectPair(pair[0], pair[1]);
    };

    const mapCount = document.getElementById("map-count");
    if (mapCount) mapCount.textContent = money(fields.length) + " fields · " +
      money(edges.length) + " documented connections";
    const m = net.meta || {};
    const meta = document.getElementById("meta");
    if (meta) meta.textContent = money(m.work_count) + " publications · " +
      money(m.interdisc_work_count) + " cross-field works · OpenAlex · " + (m.years || "2018–2026") +
      (m.sample ? " · SAMPLE DATA" : "");
    if (isControl) document.getElementById("atlas-study-note").textContent =
      "Comparison condition: source records intentionally hidden.";
    renderGrid();
    if (strong) selectPair(strong.a, strong.b);
    else if (broadest) focusField(broadest.id);
  };
})();
