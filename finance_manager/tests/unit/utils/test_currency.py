"""Tests for currency utilities."""

from unittest.mock import patch, MagicMock
import pytest
from finance_manager.utils.currency import format_currency, parse_currency


@pytest.fixture(autouse=True)
def mock_config():
    cfg = MagicMock()
    cfg.currency_symbol = "$"
    with patch("finance_manager.utils.currency.get_config", return_value=cfg):
        yield cfg


class TestFormatCurrency:
    def test_positive_amount(self):
        assert format_currency(1234.56) == "$1,234.56"

    def test_zero(self):
        assert format_currency(0.0) == "$0.00"

    def test_negative_amount(self):
        assert format_currency(-500.0) == "-$500.00"

    def test_custom_symbol(self):
        assert format_currency(100.0, symbol="€") == "€100.00"

    def test_large_number_with_commas(self):
        assert format_currency(1_000_000.0) == "$1,000,000.00"

    def test_negative_large_number(self):
        assert format_currency(-9999.99) == "-$9,999.99"


class TestParseCurrency:
    def test_dollar_sign(self):
        assert parse_currency("$1,234.56") == 1234.56

    def test_euro_sign(self):
        assert parse_currency("€500.00") == 500.0

    def test_no_symbol(self):
        assert parse_currency("99.99") == 99.99

    def test_negative(self):
        assert parse_currency("-150.00") == -150.0

    def test_parentheses_negative(self):
        assert parse_currency("(200.00)") == -200.0

    def test_with_commas(self):
        assert parse_currency("1,000,000.00") == 1_000_000.0
