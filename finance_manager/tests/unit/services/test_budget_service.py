"""Tests for BudgetService."""

from unittest.mock import MagicMock, patch
from datetime import date
import pytest

from finance_manager.models.budget import Budget, BudgetStatus
from finance_manager.services.budget_service import BudgetService


def _make_repo():
    repo = MagicMock()
    repo.get_budget.return_value = None  # no existing budget by default
    return repo


def _make_budget(id=1, category_id=1, limit=1000.0, period="2026-03"):
    return Budget(id=id, category_id=category_id, monthly_limit=limit, period=period)


class TestCreateBudget:
    def test_creates_when_not_exists(self):
        repo = _make_repo()
        created = _make_budget()
        repo.create_budget.return_value = created
        svc = BudgetService(finance_repo=repo)

        result = svc.create_budget(category_id=1, monthly_limit=1000.0, period="2026-03")

        repo.create_budget.assert_called_once()
        assert result is created

    def test_raises_when_budget_exists(self):
        repo = _make_repo()
        repo.get_budget.return_value = _make_budget()
        svc = BudgetService(finance_repo=repo)

        with pytest.raises(ValueError, match="already exists"):
            svc.create_budget(category_id=1, monthly_limit=500.0, period="2026-03")

    def test_defaults_period_to_current_month(self):
        repo = _make_repo()
        repo.create_budget.return_value = _make_budget()
        svc = BudgetService(finance_repo=repo)

        svc.create_budget(category_id=1, monthly_limit=500.0)

        today = date.today()
        expected_period = f"{today.year:04d}-{today.month:02d}"
        repo.get_budget.assert_called_with(1, expected_period)


class TestCheckAlerts:
    def _make_status(self, spent, limit=1000.0, name="Food"):
        budget = Budget(id=1, category_id=1, monthly_limit=limit, period="2026-03")
        return BudgetStatus(budget=budget, category_name=name, spent=spent)

    def test_no_alerts_on_track(self):
        repo = _make_repo()
        repo.get_budget_status.return_value = [self._make_status(500.0)]
        svc = BudgetService(finance_repo=repo)
        assert svc.check_alerts() == []

    def test_warning_alert(self):
        repo = _make_repo()
        repo.get_budget_status.return_value = [self._make_status(850.0)]
        svc = BudgetService(finance_repo=repo)
        alerts = svc.check_alerts()
        assert len(alerts) == 1
        assert alerts[0]["status"] == "warning"

    def test_exceeded_alert(self):
        repo = _make_repo()
        repo.get_budget_status.return_value = [self._make_status(1100.0)]
        svc = BudgetService(finance_repo=repo)
        alerts = svc.check_alerts()
        assert len(alerts) == 1
        assert alerts[0]["status"] == "exceeded"

    def test_multiple_alerts(self):
        repo = _make_repo()
        repo.get_budget_status.return_value = [
            self._make_status(1100.0, name="Food"),
            self._make_status(850.0, name="Transport"),
            self._make_status(200.0, name="Fun"),
        ]
        svc = BudgetService(finance_repo=repo)
        alerts = svc.check_alerts()
        assert len(alerts) == 2


class TestCopyBudgetsToPeriod:
    def test_copies_all_budgets(self):
        repo = _make_repo()
        repo.get_budgets_for_period.return_value = [
            _make_budget(id=1, category_id=1, limit=500.0),
            _make_budget(id=2, category_id=2, limit=300.0),
        ]
        repo.create_budget.side_effect = lambda b: b
        svc = BudgetService(finance_repo=repo)

        count = svc.copy_budgets_to_period("2026-02", "2026-03")
        assert count == 2

    def test_skips_existing_budgets(self):
        repo = _make_repo()
        repo.get_budgets_for_period.return_value = [
            _make_budget(id=1, category_id=1, limit=500.0),
        ]
        # Simulate existing budget for the target period
        repo.get_budget.return_value = _make_budget()
        svc = BudgetService(finance_repo=repo)

        count = svc.copy_budgets_to_period("2026-02", "2026-03")
        assert count == 0
