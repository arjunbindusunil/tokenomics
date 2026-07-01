"""Phase 2's tool, built first — a cheap, audience-matched quality judge.

A small model scores an artifact 1-5 against a rubric, judged against the artifact's
intended audience, and returns strict JSON. Cheap enough to run on everything — that is
the entire point: you can only make a pipeline cheaper safely if you can tell, on every
run, whether quality moved.

Two hard-won design rules baked in:
  * The judge uses a SMALL model on purpose. It must be cheaper than what it judges, or
    you can't afford to gate every run. This is the one place a small model is the correct
    default rather than a compromise.
  * A parse failure is a MEASUREMENT failure, never a score of 0. Counting an unparsed
    verdict as "bad content" poisons your averages and fakes you out (a real harness bug
    from the case study). We return ``parse_error`` instead, and callers must skip those.
"""
from __future__ import annotations

import json
from typing import Any

try:
    from anthropic import Anthropic
except ImportError:  # keep the module importable for cost/parse tests without the SDK
    Anthropic = None  # type: ignore[assignment, misc]

# Five audience-relative criteria. "Depth" means mechanism for a technical reader and
# practical consequence for a general one — the rubric adapts to the audience, it does not
# punish non-technical work for being successfully non-technical.
DEFAULT_RUBRIC: list[tuple[str, str]] = [
    ("fit", "pitched to THIS audience's stated level and goal"),
    ("depth", "explains the mechanism (technical) or the real consequence (general) — not a gesture"),
    ("structure", "one clear idea, opened, built, and landed — not a list"),
    ("specificity", "concrete claims, names, examples — not hedged generalities"),
    ("format", "obeys the requested shape/length"),
]

JUDGE_SYSTEM = (
    "You are a strict, fair content evaluator. You grade an artifact ONLY against its "
    "stated audience — never a fixed 'technical' bar. Reply with STRICT JSON and nothing "
    "else."
)


def _build_prompt(artifact: str, audience: str, rubric: list[tuple[str, str]]) -> str:
    lines = "\n".join(f'  "{k}": <1-5>,  // {desc}' for k, desc in rubric)
    return (
        f"AUDIENCE (grade against this reader):\n{audience}\n\n"
        f"ARTIFACT:\n<<<\n{artifact}\n>>>\n\n"
        "Score each criterion 1-5, then give an overall 1-5 and one sentence on the "
        "weakest point. Reply with exactly this JSON shape:\n"
        "{\n"
        f"{lines}\n"
        '  "overall": <1-5>,\n'
        '  "weakest": "<one sentence>"\n'
        "}"
    )


def _parse(text: str) -> dict[str, Any]:
    """Defensive parse: distinguish a bad artifact from a parser choke."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {"parse_error": True, "raw": text[:500]}
    try:
        obj = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {"parse_error": True, "raw": text[:500]}
    if "overall" not in obj:
        return {"parse_error": True, "raw": text[:500]}
    return obj


def judge(
    artifact: str,
    *,
    audience: str,
    rubric: list[tuple[str, str]] | None = None,
    model: str = "claude-haiku-4-5",
    client: Any = None,
) -> dict[str, Any]:
    """Score ``artifact`` for ``audience``. Returns the parsed verdict dict, or
    ``{"parse_error": True, ...}`` if the judge's reply couldn't be parsed."""
    if Anthropic is None and client is None:
        raise RuntimeError("anthropic SDK not installed; pass a client or `pip install anthropic`")
    client = client or Anthropic()
    rubric = rubric or DEFAULT_RUBRIC
    resp = client.messages.create(
        model=model,
        max_tokens=600,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": _build_prompt(artifact, audience, rubric)}],
    )
    text = "".join(getattr(b, "text", "") for b in resp.content if getattr(b, "type", "") == "text")
    verdict = _parse(text)
    verdict["_model"] = model
    verdict["_usage"] = getattr(resp, "usage", None)
    return verdict
