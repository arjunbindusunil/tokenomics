"""Validate the harness BEFORE trusting any number.

Instrument bugs masquerade as model behavior and produce confidently-wrong conclusions —
in the case study, a judge that silently truncated its input "proved" the cheap model was
bad at long content (it wasn't; the ruler was cut short). Run this first.

Offline checks (no API key needed):
  * cost math reproduces the real $5.22 anchor to the cent;
  * the judge parser distinguishes good JSON, malformed JSON, and a missing score —
    and never turns a parse failure into a score of 0.

Live check (needs ANTHROPIC_API_KEY, opt in with --live):
  * a known-good artifact scores at/above a floor, so you know the judge isn't blind.

    python -m engine.validate           # offline only
    python -m engine.validate --live    # + one real judge call
"""
from __future__ import annotations

import sys

from .judge import _parse
from .rates import cost_from_usage, cost_usd


def check_cost_math() -> None:
    anchor = cost_usd(
        "claude-opus-4-8",
        input_tokens=26_606,
        output_tokens=84_436,
        cache_read_tokens=3_194_582,
        cache_write_tokens=220_523,
    )
    assert abs(anchor - 5.22) < 0.01, f"cost anchor drifted: got {anchor:.4f}, expected ~5.22"
    # and via the usage-dict path
    via_usage = cost_from_usage(
        "claude-haiku-4-5",
        {"input_tokens": 1_000_000, "output_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
    )
    assert abs(via_usage - 1.00) < 1e-9, f"haiku input rate wrong: {via_usage}"
    print("  [ok] cost math reproduces the $5.22 anchor and the rate card")


def check_judge_parser() -> None:
    good = _parse('{"fit":4,"depth":5,"structure":4,"specificity":4,"format":5,"overall":4,"weakest":"x"}')
    assert good.get("overall") == 4 and not good.get("parse_error"), "good JSON misparsed"

    malformed = _parse("here is my verdict: {not json at all")
    assert malformed.get("parse_error"), "malformed JSON must be a parse_error, not a score"

    no_score = _parse('{"weakest":"missing overall"}')
    assert no_score.get("parse_error"), "missing overall must be a parse_error, not a 0"
    print("  [ok] judge parser distinguishes bad content from a parser choke (never scores 0)")


def check_live() -> None:
    from .judge import judge  # imported lazily so offline runs need no SDK

    known_good = (
        "Let's talk about why regression does not give you causation. When you run an "
        "ordinary least squares regression you compute a conditional expectation: the "
        "expected value of Y given X. That is descriptive. Causation is a counterfactual "
        "claim — what Y would have been for this same unit had X been different. Those two "
        "are equal only under unconfoundedness, which you can never test from data alone."
    )
    verdict = judge(known_good, audience="a data scientist who knows statistics well")
    assert not verdict.get("parse_error"), f"live judge returned unparseable: {verdict}"
    assert verdict["overall"] >= 3, f"judge scored a known-good artifact too low: {verdict}"
    print(f"  [ok] live judge scored a known-good artifact {verdict['overall']}/5 (not blind)")


def main() -> int:
    print("validating harness...")
    check_cost_math()
    check_judge_parser()
    if "--live" in sys.argv:
        check_live()
    print("harness OK — safe to trust the numbers.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
