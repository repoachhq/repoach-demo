import pytest

from tally.money import apply_discount, format_amount, parse_amount


@pytest.mark.parametrize(("text", "cents"), [("0", 0), ("12.3", 1230), ("12.34", 1234), (" 7 ", 700)])
def test_parse_amount(text: str, cents: int) -> None:
    assert parse_amount(text) == cents


@pytest.mark.parametrize("text", ["", "-1", "1.234", "abc", "1.x"])
def test_parse_amount_rejects(text: str) -> None:
    with pytest.raises(ValueError):
        parse_amount(text)


def test_format_amount() -> None:
    assert format_amount(1234) == "12.34"
    assert format_amount(5) == "0.05"
    assert format_amount(-250) == "-2.50"


def test_apply_discount() -> None:
    assert apply_discount(1000, 10) == 900
    assert apply_discount(999, 50) == 499
    with pytest.raises(ValueError):
        apply_discount(1000, 101)
