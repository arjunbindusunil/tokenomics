---
name: tokenomics
description: >-
  Measure-driven cost + quality optimization for any agentic LLM pipeline (content
  generation, RAG/Q&A, tool-use, coding agents). Use when an LLM agent costs more than
  expected or its output quality is inconsistent and you want to know which lever
  actually helps. It instruments the pipeline (Phase 0), then applies the cost levers in
  the order that actually pays off — context architecture, spec+eval, effort, model tier,
  and only maybe lexical — judge-gating every change so you never trade quality for cost.
  Ships a recommended per-pipeline config with before/after receipts, not vibes.
---
<!-- All measured numbers below are real receipts, domain-anonymized. -->

# tokenomics — optimize an agentic LLM pipeline by measuring, not guessing

You are optimizing a target LLM pipeline for **cost and quality at the same time**. The
core discovery this skill encodes: the levers that help are almost never the one people
reach for first (a bigger model). Apply them **in order**, and **prove each step with a
cheap judge** so no cost cut silently costs quality.

## The meta-order (this is the product)

> **context architecture → spec & eval → effort → model tier → (maybe) lexical.**
> Most teams start at "use a bigger model." In the measured data that was **last and least**.

Applying the levers out of order wastes money: you can't tell whether a model swap helped
if you never built the judge, and you can't judge context savings if the context is still a
mess. Go top to bottom. Gate every step.

## How to run it

1. **Phase 0 — open the black box.** Instrument the pipeline before changing anything. Use
   `engine/observe.py` to record per-call `input / output / cache-read / cache-creation`
   tokens, turn count, model, wall time, and cost to a JSONL, then `summarize()` it. The
   number that matters most is **re-read context** (cache-read + cache-write across turns):
   it's usually the biggest line item and the one nobody has measured. Do **not** optimize
   until you can see the bill by bucket.

2. **Build the judge FIRST (Phase 2's tool, built early).** Stand up `engine/judge.py` — a
   cheap, small-model, **audience-matched** 1–5 rubric. Everything downstream is gated on
   it, so it must exist before you touch anything. A parse failure is a *measurement*
   failure, never a score of 0.

3. **Validate the harness.** Run `engine/validate.py`. Instrument bugs (a truncated judge,
   shared scratch paths, a stale read, an unparsed verdict) masquerade as model behavior
   and hand you confidently-wrong conclusions. Confirm a known-good input scores as
   expected and the cost math reproduces **before trusting a single number.**

4. **Walk the levers in order, one variable at a time**, using `engine/ab.py` to compare
   baseline vs a single-variable variant on cost + latency + quality:
   - **Context architecture** — replace big always-on docs re-read every turn with one
     small, self-contained, read-once spec per task (aim ≥30× smaller per-call payload).
     Keep static context byte-identical so it's cache-read, not re-created.
   - **Spec + eval** — when output is weak, tighten the spec, don't upsize the model.
     Encode acceptance as steps the model executes (a length gate; a "list sub-areas,
     dedupe" diversity check; a depth-matches-audience rule), not hopes in the preamble.
   - **Effort** — sweep reasoning effort low→high on the (now cheaper) model; find the
     knee. Effort is a near-free dial that often removes the need for a dearer model.
   - **Model tier** — cheapest model that holds the bar. **Tier within a task:** default
     cheap, add a cheap detector, escalate only the failing cases to a stronger model.
   - **(maybe) lexical** — only after the above, and usually skip: compressing the wording
     of an already-lean spec saves ~nothing and risks nuanced rules. Never compress the
     deliverable when the content *is* the product.
   Gate each step: quality must hold (judge ≥ target) at the new, lower cost.

5. **Ship the config with receipts.** Output the recommended per-pipeline config (model,
   effort, lean-doc shape) plus the before→after cost and quality proof and the projected
   per-operation saving. Then keep the loop: re-run the gate as the workload drifts.

## The rules

The ten operationalized lessons live in [`RULES.md`](RULES.md). The measured receipts that
justify each one live in [`examples/README.md`](examples/README.md). Read both before
advising a change — the point of this skill is that the advice is *measured*, and several
findings contradict popular wisdom.

## Cross-cutting discipline (non-negotiable)

- **Validate the harness before trusting any number.**
- **One variable per experiment**; repeat where variance is real.
- **Never compromise an audience:** if a segment scores low, first check the eval matches
  it, *then* fix the spec. Lift every audience to the same bar.
- **A test artifact that fails for a test reason is a diagnosis, not a content failure** —
  don't "fix" it into something worse.
