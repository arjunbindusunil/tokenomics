# engine/ — the measurement harness

Four small, dependency-light modules. Together they let you open the black box, prove a
change, and never trade quality for cost by accident. Only the judge needs the Anthropic
SDK (`pip install anthropic`) and an `ANTHROPIC_API_KEY`; the rest is pure Python.

| File | Phase | What it does |
|---|---|---|
| [`rates.py`](rates.py) | 0 | The published Anthropic rate card + `cost_usd` / `cost_from_usage`. Single source of truth for every dollar figure. Reproduces the real $5.22 anchor to the cent. |
| [`observe.py`](observe.py) | 0 | `record()` one telemetry row per API call to JSONL; `summarize()` the bucketed bill and surface **re-read context** — usually the biggest, most-invisible line item. |
| [`judge.py`](judge.py) | 2 | A cheap, **audience-matched** 1–5 rubric judge (small model on purpose). Strict-JSON out, defensive parse: a parse failure is a *measurement* failure, never a score of 0. |
| [`ab.py`](ab.py) | 1–4 | One-variable A/B: baseline vs a single-lever variant, compared on cost + latency + quality. Prints ADOPT / REVIEW / REJECT. |
| [`validate.py`](validate.py) | pre-flight | **Run this first.** Confirms the cost math and the judge parser behave, before you trust any number. `--live` adds one real judge call. |

## The loop

```
python -m engine.validate            # 0. never trust an unvalidated ruler
# 1. instrument your existing pipeline with observe.record(...) on every call
python -c "from engine.observe import summarize; summarize('run.jsonl')"   # see the bill
# 2. stand up judge.judge(artifact, audience=...) as your quality gate
# 3-4. for each lever, in order, run one-variable A/Bs:
#      ab(baseline=..., variant=..., judge_fn=..., n=3)
#      context architecture -> spec -> effort -> model tier -> (maybe) lexical
# 5. ship the winning config; re-run the gate as the workload drifts
```

## Wiring it to *your* pipeline

`observe.record` and `ab` don't know anything about your app — you hand them the `(model,
usage)` of each call and the finished artifact. That's deliberate: the harness is
domain-neutral, so the same four files work whether you're generating articles, answering
questions over a corpus, driving tools, or writing code. The levers change per domain (see
the repo roadmap); the measurement discipline doesn't.

Everything here is a template. Adapt the rubric in `judge.py` to your artifact type, add
your models to `rates.py`, and keep one variable per experiment.
