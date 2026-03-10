"""Tests for Budget and BudgetStatus models."""

import pytest
from finance_manager.models.budget import Budget, BudgetStatus


class TestBudget:
    def test_alert_amount(self):
        b = Budget(category_id=1, monthly_limit=1000.0, period="2026-03", alert_threshold=0.8)
        assert b.alert_amount == 800.0

    def test_alert_amount_custom_threshold(self):
        b = Budget(category_id=1, monthly_limit=500.0, period="2026-03", alert_threshold=0.5)
        assert b.alert_amount == 250.0

    def test_get_status_on_track(self):
        b = Budget(category_id=1, monthly_limit=1000.0, period="2026-03", alert_threshold=0.8)
        assert b.get_status(500.0) == "on_track"

    def test_get_status_warning(self):
        b = Budget(category_id=1, monthly_limit=1000.0, period="2026-03", alert_threshold=0.8)
        assert b.get_status(850.0) == "warning"

    def test_get_status_exceeded(self):
        b = Budget(category_id=1, monthly_limit=1000.0, period="2026-03", alert_threshold=0.8)
        assert b.get_status(1100.0) == "exceeded"

    def test_get_status_exactly_at_limit(self):
        b = Budget(category_id=1, monthly_limit=1000.0, period="2026-03")
        assert b.get_status(1000.0) == "exceeded"

    def test_get_status_zero_limit(self):
        # Zero limit: division guard returns on_track (no budget configured)
        b = Budget(category_id=1, monthly_limit=0.0, period="2026-03")
        assert b.get_status(0.0) == "on_track"


class TestBudgetStatus:
    def _make_status(self, limit: float, spent: float, threshold: float = 0.8) -> BudgetStatus:
        budget = Budget(category_id=1, monthly_limit=limit, period="2026-03",
                        alert_threshold=threshold)
        return BudgetStatus(budget=budget, category_name="Food", spent=spent)

    def test_remaining(self):
        s = self._make_status(1000.0, 400.0)
        assert s.remaining == 600.0

    def test_remaining_negative_when_exceeded(self):
        s = self._make_status(1000.0, 1200.0)
        assert s.remaining == -200.0

    def test_percent_used(self):
        s = self._make_status(1000.0, 750.0)
        assert s.percent_used == 75.0

    def test_percent_used_zero_limit(self):
        s = self._make_status(0.0, 0.0)
        assert s.percent_used == 0.0

    def test_is_on_track(self):
        s = self._make_status(1000.0, 500.0)
        assert s.is_on_track
        assert not s.is_warning
        assert not s.is_exceeded

    def test_is_warning(self):
        s = self._make_status(1000.0, 850.0)
        assert s.is_warning
        assert not s.is_on_track
        assert not s.is_exceeded

    def test_is_exceeded(self):
        s = self._make_status(1000.0, 1050.0)
        assert s.is_exceeded
        assert not s.is_on_track
        assert not s.is_warning
