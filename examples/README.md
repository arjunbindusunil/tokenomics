# examples/ — the receipts

Every rule this skill applies was measured on a real, production agentic content-generation
pipeline (a Claude Code agent authoring long-form spoken-word content), with a quality gate.
The domain is anonymized; **the numbers are real**, and each dollar figure is
`measured tokens × published rate` (see [`../engine/rates.py`](../engine/rates.py)).

Rate card used throughout (USD / MTok):

| Model | Input | Output | Cache-read | Cache-write (5m) |
|---|---|---|---|---|
| Opus 4.8 | $5.00 | $25.00 | $0.50 | $6.25 |
| Sonnet | $3.00 | $15.00 | $0.30 | $3.75 |
| Haiku 4.5 | $1.00 | $5.00 | $0.10 | $1.25 |

## Phase 0 — where the money actually was ($5.22, one script, Opus, 49 turns)

| Bucket | Tokens | Cost |
|---|---:|---:|
| Cache-read | 3,194,582 | $1.60 |
| Cache-write | 220,523 | $1.38 |
| Output | 84,436 | $2.11 |
| Input | 26,606 | $0.13 |
| **Total** | | **$5.22** |

The shipped artifact was ~5,300 of those output tokens ≈ **$0.13**. The other **$5.09** was
overhead — mostly the agent re-reading a ~41,000-token instruction doc on every one of ~49
turns (that's the 3.2M cache-read). **The cost was architectural, not the model.**

## Phase 1 — context architecture (biggest lever, no model change)

- Per-call instruction payload: **~41,000 → ~650–1,270 tokens** (a **32–63×** cut) by
  replacing "read the whole manual every turn" with one small, read-once, per-task spec.
- On a single script, **cache-read fell 2.13M → 0.87M tokens** → `2.13M×$0.50 = $1.07`
  down to `0.87M×$0.50 = $0.44`, **~60% off the cache-read line, from a prompt edit.**

## Phase 2 — quality is a spec knob, not a model knob

Same job, same judge, loose vs tightened spec, on a cheap and an expensive model:

| | Loose spec | Tight spec |
|---|---|---|
| Haiku (cheap) | 3/5 · $0.23 | 4/5 · $0.26 |
| Sonnet (expensive) | 2/5 · $1.13 | 4/5 · $0.82 |

On the loose spec the cheap model **beat** the expensive one (3 vs 2) at a fifth of the cost;
on the tight spec both hit 4/5, so the model choice was worth **nothing**. The spec did all
the work (+1 cheap, +2 dear). Same-listener/topic across the row, so it's a clean A/B.

*Judge design receipt:* a first, technical-biased judge scored a (good) non-technical
artifact low for "lacking technical depth" — a false negative. Making the rubric
**audience-matched** fixed it. Your eval is a prompt, with the same failure modes.

## Phase 3 — effort (near-free) then tiering

Reasoning effort on the same model:

| Effort | Judge |
|---|---:|
| Low | 3/5 |
| Medium | 4/5 |
| High | 5/5 |

Tier within a task (cheap default, escalate only where it measurably fails):

| Job | Cheap (Haiku) | Mid (Sonnet) | Result |
|---|---|---|---|
| Recurring "propose next" | 4/5 @ ~$0.26 | 4/5 @ ~$0.82 | tied → **~3.2× cheaper**, keep Haiku |
| Multi-step planner | 4/5 @ ~$0.09 | 4/5 @ ~$0.25 | tied → **~2.7× cheaper**, keep Haiku |
| Dense interlocking graph | drops links | holds | **escalate this class only** |

**Three tiers, and the flagship runs nothing.** The long-form writer *started* on the
flagship (max effort, full context): **$5.22, 4/5** — the Phase 0 baseline above. The shipped
mid-tier config (high effort + lean spec) beat it at **~$1.01, 5/5**: ~5× cheaper *and* a
point higher. Across everything measured, the flagship was **"not needed anywhere."** Final
routing: Haiku for structured daily work, Sonnet for long-form writing, the top tier for
nothing.

## Phase 4 (myths) — the measured duds

- **Bigger model as a blanket fix:** the least useful lever; ~0.5 pt on jobs that didn't
  need it, at 3–5× cost.
- **Lexical "caveman" compression:** a spec **1,054 → 695 tokens** (~360 saved, rounding
  error against generation) **regressed quality 5/5 → 4/5.** Net worse.
- **Plan→self-check scaffold:** lifts *weak* jobs to 5/5 but adds orchestration turns — a
  *quality* lever, not a *cost* one.
- **Turn count as a cost proxy:** a cheaper model used *more* turns and still cost **~5×
  less**. Measure dollars, not turns.

## Cross-cutting — the harness bugs that faked me out (validate first!)

Five instrument bugs each produced a confident, wrong conclusion before I caught them:

1. **Judge silently truncated its input** → "cheap model is bad at long content" (false;
   the ruler was cut short).
2. **Two parallel runs shared one scratch path** → "model produces garbled output" (false;
   file collision).
3. **Judge JSON parse failure counted as a low score** → poisoned averages with fake zeros.
4. **ID corruption in a multi-item job** → scored artifact A against artifact B's rubric.
5. **Env/enum/UTF-8 mangling** → clean output turned to garbage *after* generation.

None threw an error saying "this result is fake." That's why
[`validate.py`](../engine/validate.py) runs first.
