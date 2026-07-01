"""Published Anthropic API rates + cost math — the single source of truth for every
dollar figure this skill reports. Rates are USD per million tokens (MTok).

Verification anchor: a real baseline run logged $5.22 on claude-opus-4-8 with
3,194,582 cache-read + 220,523 cache-write + 84,436 output + 26,606 input tokens:
    3.194582*0.50 + 0.220523*6.25 + 0.084436*25 + 0.026606*5 == 5.22
so these rates reproduce measured cost exactly, not by re-derivation.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rate:
    """USD per MTok for each billing bucket."""

    input: float
    output: float
    cache_read: float  # ~0.1x input
    cache_write_5m: float  # ~1.25x input


# Update as Anthropic publishes new rates. Sonnet 5 has a lower intro promo through
# 2026-08-31; standard rates are used here for durability.
RATE_CARD: dict[str, Rate] = {
    "claude-opus-4-8": Rate(input=5.00, output=25.00, cache_read=0.50, cache_write_5m=6.25),
    "claude-opus-4-7": Rate(input=5.00, output=25.00, cache_read=0.50, cache_write_5m=6.25),
    "claude-sonnet-5": Rate(input=3.00, output=15.00, cache_read=0.30, cache_write_5m=3.75),
    "claude-sonnet-4-6": Rate(input=3.00, output=15.00, cache_read=0.30, cache_write_5m=3.75),
    "claude-haiku-4-5": Rate(input=1.00, output=5.00, cache_read=0.10, cache_write_5m=1.25),
}


def cost_usd(
    model: str,
    *,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_read_tokens: int = 0,
    cache_write_tokens: int = 0,
) -> float:
    """Cost of one call from explicit token counts."""
    if model not in RATE_CARD:
        raise KeyError(f"no rate for model {model!r}; add it to RATE_CARD")
    r = RATE_CARD[model]
    return (
        input_tokens * r.input
        + output_tokens * r.output
        + cache_read_tokens * r.cache_read
        + cache_write_tokens * r.cache_write_5m
    ) / 1_000_000


def _field(usage: object, key: str) -> int:
    """Read a token field from an Anthropic response.usage or a plain dict."""
    if isinstance(usage, dict):
        return int(usage.get(key, 0) or 0)
    return int(getattr(usage, key, 0) or 0)


def cost_from_usage(model: str, usage: object) -> float:
    """Cost of one call from an Anthropic ``response.usage`` (or an equivalent dict).

    Handles the current field names: ``input_tokens``, ``output_tokens``,
    ``cache_read_input_tokens``, ``cache_creation_input_tokens``.
    """
    return cost_usd(
        model,
        input_tokens=_field(usage, "input_tokens"),
        output_tokens=_field(usage, "output_tokens"),
        cache_read_tokens=_field(usage, "cache_read_input_tokens"),
        cache_write_tokens=_field(usage, "cache_creation_input_tokens"),
    )
