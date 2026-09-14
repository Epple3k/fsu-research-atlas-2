# FSU Research Explorer — portfolio case study copy

## Making an AI answer show its work

I designed and built an evidence-first interface for exploring how research fields at Florida State University connect—without asking users to trust a black-box summary.

**Role:** Product design, interaction design, data modeling, frontend and agent architecture  
**Scope:** Independent prototype, 2026  
**Data:** 38,607 FSU works from OpenAlex, spanning 2018–2026  
**Status:** Working product; structured usability evaluation prepared

## The problem

University research is distributed across departments, disciplines and thousands of individual publications. Existing publication databases work well when someone already knows what paper, author or topic to search for. They are much less useful for exploratory questions:

- Which research fields are becoming more interdisciplinary?
- Where are strong cross-field relationships forming?
- What records support that conclusion?
- Can I inspect the evidence instead of accepting an aggregate or AI summary?

Putting a conversational model over the data makes questioning easier, but creates a new problem. A fluent answer can feel authoritative even when the route from source data to conclusion is invisible.

The design problem was not simply: **How can AI answer questions about research?**

It was: **How can an answer remain inspectable after AI makes the dataset easier to ask?**

### Provisional primary user

A university research strategist investigating cross-disciplinary activity before deciding where to focus outreach or further analysis.

This is a design hypothesis until interviews with research-adjacent users are completed. Do not present it as validated research yet.

### Core jobs

1. Identify a relationship worth investigating without scanning thousands of papers.
2. Understand whether a claim describes current volume, change over time or interpretation.
3. Inspect the exact papers behind a conclusion before acting on it.

## Design hypothesis

AI can make a large research dataset easier to interrogate, but users should never have to accept its numerical claims on fluency alone. Every generated conclusion should remain visually and interactively attached to the evidence that produced it.

That hypothesis became the product loop:

**Question → constrained analysis → observation → clickable claim → network focus → source papers**

## The product

FSU Research Explorer maps 26 OpenAlex fields and 279 cross-field relationships across 38,607 FSU research works. A user can ask about collaboration, growth or a particular field. The product turns the analysis into selectable claims. Selecting a claim highlights the corresponding relationship in the network and exposes the exact publications behind it.

The AI is optional. If the hosted agent is unavailable, a deterministic interpreter preserves a useful core experience.

## Four design decisions

### 1. Claims are objects, not prose

Instead of presenting a paragraph as the final answer, the interface decomposes an answer into selectable claims. Selecting one highlights the exact relationship and loads its supporting papers.

**Reason:** preserve the speed of natural-language querying without turning the model into an opaque authority.

**Tradeoff:** the answer feels less conversational, but becomes much easier to inspect and challenge.

### 2. The network explores; text specifies

A ranking communicates exact values but hides relational structure. A network reveals the pattern of relationships but is harder to read precisely. I use the network for orientation and claim cards for specific measurements.

**Tradeoff:** two coordinated representations increase interface complexity, so their selection states must remain synchronized.

### 3. Observation and interpretation use different voices

Measurements use the product's sans-serif interface voice. Interpretive conclusions use a contrasting serif voice.

**Reason:** help users distinguish what the dataset reports from what the system concludes before they consciously parse every label.

**Tradeoff:** typography can reinforce the distinction, but wording and access to evidence still carry the real burden.

### 4. The model never owns the numbers

The agent can only call constrained tools that return observations, field pairs and work IDs. The browser reconstructs visible claims from its own local data before rendering them.

**Reason:** trust needs to be structural. A prompt asking the model not to invent values is not enough.

**Tradeoff:** constraining the agent limits free-form expression, but makes unsupported quantitative claims far harder to display.

## A meaningful implementation iteration

During live testing, the agent answered an open-ended question using real output from the top-collaborations tool, but the UI rendered no clickable evidence. The first server implementation only collected provenance when the model used a direct link lookup. The prose was supported, but the returned edge list was empty.

That was a product failure: a technically correct answer had broken the evidence contract.

I changed the server to capture evidence-backed field pairs from every relevant tool result and kept visible claim construction in the browser. I also raised the model's output budget after tracing a second failure in which tool calls were silently truncated on harder questions.

The goal of those fixes was not to make the AI sound better. It was to make the evidence chain survive different agent behavior.

## Evaluation plan

The working product proves that the mechanism functions. It does not yet prove that visible provenance improves comprehension or calibrated trust.

The prepared evaluation uses two otherwise similar versions:

- **Version A — claim-only control:** participants can read claims and see network context but cannot inspect paper-level evidence.
- **Version B — evidence-first:** participants can select a claim, see the highlighted relationship and inspect each source paper.

Six to eight participants will complete matched investigation tasks in counterbalanced order. The study records:

- task completion;
- correct relationship identification;
- time on task;
- confidence from 1–5;
- trust in the conclusion from 1–5;
- whether the participant attempts to inspect a source;
- where the participant hesitates;
- the participant's explanation for trusting or questioning the result.

The goal is not simply to maximize reported trust. If evidence visibility raises trust indiscriminately, the interface may be creating false confidence. A stronger outcome would be more source inspection, more accurate explanations and clearer reasons for accepting or challenging a claim.

## Current conclusion

The most important outcome is not the network itself. It is a reusable interaction model for keeping machine-generated interpretation connected to inspectable records.

This prototype changed how I think about provenance. It is not merely a backend property or a citation added after an answer. It is a path the user should be able to follow: from question, to claim, to relationship, to source.

## Before publishing final results

Replace the “evaluation prepared” language only after real sessions are completed. Add:

- participant count and relevant backgrounds;
- the exact task and test order;
- completion and accuracy results by condition;
- trust and confidence summaries;
- two or three observed usability failures;
- the interface changes made because of those failures;
- limitations, especially the small convenience sample.

Never turn an example result into a claimed finding.
