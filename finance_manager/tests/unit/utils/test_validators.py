"""Tests for validation utilities."""

import pytest
from finance_manager.utils.validators import (
    validate_required, validate_positive, validate_range, validate_email,
)


class TestValidateRequired:
    def test_passes_with_value(self):
        validate_required("hello", "field")  # no exception

    def test_raises_on_none(self):
        with pytest.raises(ValueError, match="required"):
            validate_required(None, "field")

    def test_raises_on_empty_string(self):
        with pytest.raises(ValueError, match="required"):
            validate_required("", "field")

    def test_raises_on_whitespace(self):
        with pytest.raises(ValueError, match="required"):
            validate_required("   ", "field")

    def test_passes_with_zero(self):
        validate_required(0, "field")  # 0 is a valid value

    def test_passes_with_false(self):
        validate_required(False, "field")  # False is a valid value


class TestValidatePositive:
    def test_passes_positive(self):
        validate_positive(1.0, "amount")

    def test_raises_on_zero(self):
        with pytest.raises(ValueError, match="positive"):
            validate_positive(0.0, "amount")

    def test_raises_on_negative(self):
        with pytest.raises(ValueError, match="positive"):
            validate_positive(-5.0, "amount")


class TestValidateRange:
    def test_passes_in_range(self):
        validate_range(50.0, 0.0, 100.0, "pct")

    def test_passes_at_min(self):
        validate_range(0.0, 0.0, 100.0, "pct")

    def test_passes_at_max(self):
        validate_range(100.0, 0.0, 100.0, "pct")

    def test_raises_below_min(self):
        with pytest.raises(ValueError, match="between"):
            validate_range(-1.0, 0.0, 100.0, "pct")

    def test_raises_above_max(self):
        with pytest.raises(ValueError, match="between"):
            validate_range(101.0, 0.0, 100.0, "pct")


class TestValidateEmail:
    def test_valid_email(self):
        assert validate_email("user@example.com") is True

    def test_invalid_no_at(self):
        assert validate_email("userexample.com") is False

    def test_invalid_no_domain(self):
        assert validate_email("user@") is False

    def test_invalid_empty(self):
        assert validate_email("") is False
