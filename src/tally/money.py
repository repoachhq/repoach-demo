"""Money arithmetic in integer cents, never floats."""

from __future__ import annotations


def parse_amount(text: str) -> int:
    """Parse ``"12.34"`` into 1234 cents.

    Raises:
        ValueError: when the text is not a non-negative decimal with at most two places.
    """
    whole, _, frac = text.strip().partition(".")
    if not whole.isdigit() or (frac and (not frac.isdigit() or len(frac) > 2)):
        raise ValueError(f"not an amount: {text!r}")
    return int(whole) * 100 + int(frac.ljust(2, "0") or 0)


def format_amount(cents: int) -> str:
    """Format 1234 cents as ``"12.34"``."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"


def apply_discount(cents: int, percent: int) -> int:
    """Return ``cents`` reduced by ``percent`` (0-100), rounded half up."""
    if not 0 <= percent <= 100:
        raise ValueError(f"discount out of range: {percent}")
    return cents - (cents * percent + 50) // 100
