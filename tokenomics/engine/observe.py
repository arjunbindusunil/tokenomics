"""Phase 0 — open the black box.

Record per-call token/cost/turn telemetry to a JSONL file, then summarize where the
money actually goes. The number that matters most is **re-read context**: cache-read +
cache-write summed across every turn. In the measured case study that was more than half
the bill — the agent re-reading a big instruction doc dozens of times — and it was
invisible until instrumented.

Usage:
    from engine.observe import record, summarize
    resp = client.messages.create(...)          # your pipeline call
    record("run.jsonl", model="claude-haiku-4-5", usage=resp.usage, label="write")
    ...
    summarize("run.jsonl")                       # prints the bucketed bill
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .rates import _field, cost_from_usage


def record(
    path: str | Path,
    *,
    model: str,
    usage: object,
    turns: int = 1,
    wall_s: float | None = None,
    label: str = "",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Append one telemetry row for a single API call. Returns the row."""
    row: dict[str, Any] = {
        "label": label,
        "model": model,
        "turns": turns,
        "wall_s": wall_s,
        "input_tokens": _field(usage, "input_tokens"),
        "output_tokens": _field(usage, "output_tokens"),
        "cache_read_tokens": _field(usage, "cache_read_input_tokens"),
        "cache_write_tokens": _field(usage, "cache_creation_input_tokens"),
        "cost_usd": round(cost_from_usage(model, usage), 6),
    }
    if extra:
        row.update(extra)
    with Path(path).open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return row


def load(path: str | Path) -> list[dict[str, Any]]:
    """Read a telemetry JSONL into a list of rows."""
    text = Path(path).read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def summarize(path: str | Path) -> dict[str, Any]:
    """Print and return the bucketed bill: totals per token bucket, per model, and the
    key ratio — how much of the spend is *overhead* (context read/written + input) versus
    the *generation* you actually keep (output)."""
    rows = load(path)
    buckets = ("input", "output", "cache_read", "cache_write")
    tok = {b: sum(r.get(f"{b}_tokens", 0) for r in rows) for b in buckets}
    # cost per bucket needs per-row rates, so sum the per-row cost and split by share
    total_cost = sum(r.get("cost_usd", 0.0) for r in rows)

    # per-model rollup
    per_model: dict[str, dict[str, float]] = {}
    for r in rows:
        m = per_model.setdefault(r["model"], {"cost": 0.0, "calls": 0, "output": 0, "cache_read": 0})
        m["cost"] += r.get("cost_usd", 0.0)
        m["calls"] += 1
        m["output"] += r.get("output_tokens", 0)
        m["cache_read"] += r.get("cache_read_tokens", 0)

    reread = tok["cache_read"] + tok["cache_write"]
    print(f"\n=== bill: {len(rows)} calls, {sum(r.get('turns',1) for r in rows)} turns, ${total_cost:.4f} ===")
    print(f"  input        {tok['input']:>12,} tok")
    print(f"  output       {tok['output']:>12,} tok   <- the words you keep")
    print(f"  cache-read   {tok['cache_read']:>12,} tok   <- context re-read every turn")
    print(f"  cache-write  {tok['cache_write']:>12,} tok")
    print(f"  re-read context (cache-read + cache-write): {reread:,} tok")
    if tok["output"]:
        print(f"  re-read : output token ratio = {reread / tok['output']:.1f}x")
    print("  per model:")
    for m, s in sorted(per_model.items(), key=lambda kv: -kv[1]["cost"]):
        print(f"    {m:<20} {s['calls']:>4} calls  ${s['cost']:.4f}")
    print("  Lever check: if re-read context dominates, fix CONTEXT ARCHITECTURE first")
    print("  (one small read-once spec per task), before touching the model.\n")

    return {"tokens": tok, "reread_tokens": reread, "total_cost_usd": total_cost, "per_model": per_model}
