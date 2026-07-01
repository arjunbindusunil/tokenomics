"""One-variable A/B — the driver for Phases 1-4.

Run a baseline pipeline against a variant that changes EXACTLY ONE lever (leaner context,
tighter spec, higher effort, cheaper model), and compare cost + latency + quality. Quality
comes from the cheap judge, so a cost win that quietly costs quality shows up immediately.

You supply two callables. Each runs your pipeline once and returns:
    (artifact_text, [(model, usage), ...])
i.e. the finished artifact plus the (model, usage) of every API call it made, so cost can
be totalled across a multi-turn agent.

    from engine.ab import ab
    from engine.judge import judge
    report = ab(
        baseline=lambda: run_my_pipeline(context="full-manual"),
        variant=lambda:  run_my_pipeline(context="lean-spec"),
        judge_fn=lambda art: judge(art, audience="an SRE who knows Linux well"),
        n=3,
    )
"""
from __future__ import annotations

import time
from statistics import mean
from typing import Any, Callable

from .rates import cost_from_usage

PipelineFn = Callable[[], tuple[str, list[tuple[str, object]]]]
JudgeFn = Callable[[str], dict[str, Any]]


def _run_once(fn: PipelineFn, judge_fn: JudgeFn) -> dict[str, Any] | None:
    t0 = time.perf_counter()
    artifact, calls = fn()
    wall = time.perf_counter() - t0
    cost = sum(cost_from_usage(model, usage) for model, usage in calls)
    verdict = judge_fn(artifact)
    if verdict.get("parse_error"):
        # measurement failure, not a quality result — drop it, don't score it 0
        return None
    return {"cost_usd": cost, "wall_s": wall, "overall": float(verdict["overall"]), "calls": len(calls)}


def _agg(runs: list[dict[str, Any]]) -> dict[str, float]:
    return {
        "cost_usd": mean(r["cost_usd"] for r in runs),
        "wall_s": mean(r["wall_s"] for r in runs),
        "overall": mean(r["overall"] for r in runs),
        "n": len(runs),
    }


def ab(
    *,
    baseline: PipelineFn,
    variant: PipelineFn,
    judge_fn: JudgeFn,
    n: int = 3,
    quality_floor: float | None = None,
) -> dict[str, Any]:
    """Compare baseline vs a single-variable variant over ``n`` runs each. Prints a table
    and returns the aggregates. If ``quality_floor`` is set, flags whether the variant
    holds it."""
    base_runs = [r for r in (_run_once(baseline, judge_fn) for _ in range(n)) if r]
    var_runs = [r for r in (_run_once(variant, judge_fn) for _ in range(n)) if r]
    if not base_runs or not var_runs:
        raise RuntimeError("too many judge parse failures — validate the harness first")

    b, v = _agg(base_runs), _agg(var_runs)
    cost_delta = (v["cost_usd"] - b["cost_usd"]) / b["cost_usd"] * 100 if b["cost_usd"] else 0.0
    qual_delta = v["overall"] - b["overall"]

    print("\n=== one-variable A/B ===")
    print(f"{'':<10}{'cost $':>10}{'wall s':>10}{'quality':>10}{'runs':>7}")
    print(f"{'baseline':<10}{b['cost_usd']:>10.4f}{b['wall_s']:>10.2f}{b['overall']:>10.2f}{b['n']:>7}")
    print(f"{'variant':<10}{v['cost_usd']:>10.4f}{v['wall_s']:>10.2f}{v['overall']:>10.2f}{v['n']:>7}")
    print(f"  cost {cost_delta:+.1f}%   quality {qual_delta:+.2f}")
    verdict = "ADOPT" if qual_delta >= 0 and cost_delta < 0 else "REVIEW"
    if quality_floor is not None and v["overall"] < quality_floor:
        verdict = "REJECT (below quality floor)"
    print(f"  -> {verdict}\n")

    return {"baseline": b, "variant": v, "cost_delta_pct": cost_delta, "quality_delta": qual_delta, "verdict": verdict}
