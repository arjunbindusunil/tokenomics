# tokenomics — measure-driven token-efficiency for agentic LLM pipelines

> We measured every popular token-saving trick on a real production LLM agent. The #1 reflex — reach for a
> bigger model — was the **least** useful lever. Here's what actually works, packaged as a self-improving skill.

_Domain-anonymized (generic "content generation"), MIT-licensed. Every number below is a real, measured
receipt computed at published Anthropic API rates._

> **This is the advanced tier** — a measurement harness for optimizing a real pipeline. Just want better
> prompts with zero setup? Use **[nail-it](../nail-it/)** instead, and come back here when you want to
> *prove* a cheaper config holds quality.

## What it is
A **measurement-driven optimization harness + playbook** for any agentic LLM pipeline (a Claude Code
agent that authors long-form content, proposals, plans, etc.). It opens the black box, applies the
cost levers in the order that actually pays off, and **judge-gates every change** so you never trade
quality for cost. It ships a *recommended config with proof*, not vibes — and a self-improving loop that
keeps tuning.

## Why it's different from compression skills
Point tools compress words or memory. This is the **diagnostic + playbook** that decides *which* lever,
*in what order*, and *proves* the quality held. The findings (below) are measured with a quality gate on
a real workload — several contradict popular advice.

## The measured lessons (the skill's rules — see RULES.md)
1. **Fix context architecture before the model.** Not re-reading big always-on docs every turn cut
   cache-read ~5× *before any model change* — a ~32–63× smaller per-call payload, read once.
2. **Quality is a prompt-spec knob, not a model knob.** Both a cheap and an expensive model rose to 4/5
   when the *spec* was tightened (from 3/5 and 2/5) — then the cheap model matched the dear one.
3. **The bigger-model reflex is the least useful lever.** It was the *last* thing that helped.
4. **Lexical "caveman" compression is a trap once context is lean** — measured: ~0 savings + a quality
   regression. The win is structural (read-once), not lexical.
5. **A structured plan→self-check scaffold buys high-effort *quality* from a low effort tier — but not
   cost** (the extra orchestration turns offset the saving).
6. **Turn count is a bad cost proxy** — a cheaper model used more turns but cost 5× less.
7. **The eval must match the audience** — a technical judge fails non-technical content (false negative);
   grade each artifact against *its* audience.
8. **Validate your harness first** — instrument bugs (truncated judge, shared scratch paths, a stale
   read) masquerade as model behavior and produce confidently-wrong conclusions.
9. **Tier within a task** — cheap model by default, escalate to a stronger one only where it measurably
   clusters/fails (e.g. dense inputs), with a cheap detector — not blanket.
10. **Encode acceptance as a step the model executes** (a length/diversity gate it self-checks), not a
    hope in the preamble.

> **Meta-order that matters:** architecture → spec/eval → effort → model-tier → (maybe) lexical. Most
> teams start at "bigger model"; in our data that was last and least.

## The engine
- **Isolated rig** — run the real pipeline against a throwaway stack, no production side effects.
- **Observability** — per-call tokens, cache-read/creation, turns, per-model breakdown, cost.
- **Cheap judge gate** — a small-model rubric (1–5) per artifact, *audience-matched*, so downgrades are
  safe.
- **One-variable A/B** — change one lever, measure cost + latency *and* quality vs baseline.
- **Self-improving loop** — keeps proposing/locking configs until quality ≥ bar at min cost.

## Quick start
```bash
pip install anthropic
export ANTHROPIC_API_KEY=...
python -m engine.validate        # prove the harness first (offline; --live adds one judge call)
```
Then open `skill.md` and walk the phased playbook against your own pipeline.

## Roadmap — the same method, other workloads
The method is proven on content generation (this repo). The same engine — rig, observability, cheap judge,
one-variable A/B — transfers to the other big agentic workloads, in rough order of how cleanly each can be
measured:
1. **Content generation** — the core method + rig + judge + one-variable A/B + loop *(done)*.
2. **RAG / Q&A** — retrieval discipline (top-k, rerank-vs-dump, context compression), groundedness eval.
3. **Agentic tool-use** — tool-surface trimming, history compression, turn-bounding.
4. **Coding agents** — cleanest objective eval (tests pass or they don't), so it's last and easiest to trust.

## Files in this repo
- `SKILL.md` — the skill entrypoint: frontmatter/trigger + the phased playbook to run.
- `RULES.md` — the 10 lessons, operationalized, applied in the meta-order.
- `engine/` — the measurement harness (all templates, adapt to your pipeline):
  - `rates.py` — the Anthropic rate card + cost math (reproduces the $5.22 anchor).
  - `observe.py` — Phase 0 per-call telemetry to JSONL + the bucketed-bill summary.
  - `judge.py` — the cheap, audience-matched 1–5 quality judge (defensive parse).
  - `ab.py` — one-variable A/B: baseline vs single-lever variant on cost + quality.
  - `validate.py` — **run first** — proves the harness before you trust a number.
  - `engine/README.md` — how the four wire together + the loop.
- `examples/README.md` — the receipts: every measured before/after, at real rates.
- `LICENSE` — MIT.
