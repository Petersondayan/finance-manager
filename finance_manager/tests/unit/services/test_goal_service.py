"""Tests for GoalService."""

from unittest.mock import MagicMock
from datetime import date, timedelta
import pytest

from finance_manager.models.goal import Goal
from finance_manager.services.goal_service import GoalService


def _make_goal(target=1000.0, current=0.0, deadline=None, goal_type="savings"):
    return Goal(id=1, name="Test Goal", goal_type=goal_type,
                target_amount=target, current_amount=current, deadline=deadline)


class TestCreateDebtPayoffGoal:
    def test_invalid_strategy_raises(self):
        repo = MagicMock()
        svc = GoalService(finance_repo=repo)
        with pytest.raises(ValueError, match="Strategy"):
            svc.create_debt_payoff_goal("Debt", 5000.0, strategy="invalid")

    def test_valid_avalanche(self):
        repo = MagicMock()
        repo.create_goal.side_effect = lambda g: g
        svc = GoalService(finance_repo=repo)
        goal = svc.create_debt_payoff_goal("Debt", 5000.0, strategy="avalanche")
        assert goal.strategy == "avalanche"

    def test_valid_snowball(self):
        repo = MagicMock()
        repo.create_goal.side_effect = lambda g: g
        svc = GoalService(finance_repo=repo)
        goal = svc.create_debt_payoff_goal("Debt", 5000.0, strategy="snowball")
        assert goal.strategy == "snowball"


class TestGetProjections:
    def test_zero_contribution_returns_no_date(self):
        repo = MagicMock()
        svc = GoalService(finance_repo=repo)
        goal = _make_goal(target=1000.0, current=0.0)
        proj = svc.get_projections(goal, monthly_contribution=0.0)
        assert proj.estimated_completion_date is None
        assert proj.months_to_complete is None

    def test_calculates_months_to_complete(self):
        repo = MagicMock()
        svc = GoalService(finance_repo=repo)
        goal = _make_goal(target=1200.0, current=0.0)
        proj = svc.get_projections(goal, monthly_contribution=100.0)
        assert proj.months_to_complete == 12

    def test_completion_date_in_future(self):
        repo = MagicMock()
        svc = GoalService(finance_repo=repo)
        goal = _make_goal(target=600.0, current=0.0)
        proj = svc.get_projections(goal, monthly_contribution=100.0)
        assert proj.estimated_completion_date > date.today()

    def test_required_monthly_calculated_with_deadline(self):
        repo = MagicMock()
        svc = GoalService(finance_repo=repo)
        deadline = date.today() + timedelta(days=300)  # ~10 months
        goal = _make_goal(target=1000.0, current=0.0, deadline=deadline)
        proj = svc.get_projections(goal, monthly_contribution=50.0)
        # With 10 months to deadline and $1000 remaining, should need ~$100/month
        assert proj.monthly_contribution_needed > 50.0


class TestCalculateDebtPayoffOrder:
    def _debt(self, target, current):
        return Goal(name="Debt", goal_type="debt_payoff",
                    target_amount=target, current_amount=current)

    def test_snowball_smallest_balance_first(self):
        repo = MagicMock()
        svc = GoalService(finance_repo=repo)
        goals = [
            self._debt(target=3000.0, current=1000.0),  # remaining=2000
            self._debt(target=1500.0, current=1000.0),  # remaining=500
            self._debt(target=2000.0, current=500.0),   # remaining=1500
        ]
        ordered = svc.calculate_debt_payoff_order(goals, strategy="snowball")
        remainders = [g.remaining for g in ordered]
        assert remainders == sorted(remainders)

    def test_avalanche_largest_balance_first(self):
        repo = MagicMock()
        svc = GoalService(finance_repo=repo)
        goals = [
            self._debt(target=3000.0, current=1000.0),  # remaining=2000
            self._debt(target=1500.0, current=1000.0),  # remaining=500
            self._debt(target=2000.0, current=500.0),   # remaining=1500
        ]
        ordered = svc.calculate_debt_payoff_order(goals, strategy="avalanche")
        remainders = [g.remaining for g in ordered]
        assert remainders == sorted(remainders, reverse=True)


class TestAddProgress:
    def test_returns_false_for_missing_goal(self):
        repo = MagicMock()
        repo.get_goal.return_value = None
        svc = GoalService(finance_repo=repo)
        assert svc.add_progress(999, 100.0) is False

    def test_updates_amount(self):
        repo = MagicMock()
        repo.get_goal.return_value = _make_goal(target=1000.0, current=200.0)
        repo.update_goal_progress.return_value = True
        svc = GoalService(finance_repo=repo)
        result = svc.add_progress(1, 300.0)
        repo.update_goal_progress.assert_called_with(1, 500.0)
        assert result is True
