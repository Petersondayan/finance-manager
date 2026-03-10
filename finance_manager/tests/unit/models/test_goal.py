"""Tests for Goal and GoalProjection models."""

from datetime import date, timedelta
import pytest
from finance_manager.models.goal import Goal, GoalProjection


class TestGoal:
    def _make_goal(self, target=1000.0, current=0.0, deadline=None):
        return Goal(name="Test", goal_type="savings",
                    target_amount=target, current_amount=current, deadline=deadline)

    def test_remaining(self):
        g = self._make_goal(target=1000.0, current=300.0)
        assert g.remaining == 700.0

    def test_remaining_when_complete(self):
        g = self._make_goal(target=1000.0, current=1000.0)
        assert g.remaining == 0.0

    def test_percent_complete(self):
        g = self._make_goal(target=1000.0, current=250.0)
        assert g.percent_complete == 25.0

    def test_percent_complete_capped_at_100(self):
        g = self._make_goal(target=1000.0, current=1500.0)
        assert g.percent_complete == 100.0

    def test_percent_complete_zero_target(self):
        g = self._make_goal(target=0.0, current=0.0)
        assert g.percent_complete == 0.0

    def test_is_complete_false(self):
        g = self._make_goal(target=1000.0, current=999.0)
        assert not g.is_complete

    def test_is_complete_true(self):
        g = self._make_goal(target=1000.0, current=1000.0)
        assert g.is_complete

    def test_is_complete_exceeded(self):
        g = self._make_goal(target=1000.0, current=1100.0)
        assert g.is_complete

    def test_add_progress(self):
        g = self._make_goal(target=1000.0, current=200.0)
        g.add_progress(300.0)
        assert g.current_amount == 500.0

    def test_is_debt_goal(self):
        g = Goal(name="Debt", goal_type="debt_payoff", target_amount=5000.0)
        assert g.is_debt_goal()

    def test_is_not_debt_goal(self):
        g = Goal(name="Savings", goal_type="savings", target_amount=5000.0)
        assert not g.is_debt_goal()


class TestGoalProjection:
    def test_is_achievable_no_deadline(self):
        g = Goal(name="T", goal_type="savings", target_amount=1000.0)
        proj = GoalProjection(goal=g, estimated_completion_date=date.today(),
                              months_to_complete=1, monthly_contribution_needed=1000.0)
        assert proj.is_achievable

    def test_is_achievable_before_deadline(self):
        deadline = date.today() + timedelta(days=60)
        completion = date.today() + timedelta(days=30)
        g = Goal(name="T", goal_type="savings", target_amount=1000.0, deadline=deadline)
        proj = GoalProjection(goal=g, estimated_completion_date=completion,
                              months_to_complete=1, monthly_contribution_needed=1000.0)
        assert proj.is_achievable

    def test_is_not_achievable_after_deadline(self):
        deadline = date.today() + timedelta(days=10)
        completion = date.today() + timedelta(days=60)
        g = Goal(name="T", goal_type="savings", target_amount=1000.0, deadline=deadline)
        proj = GoalProjection(goal=g, estimated_completion_date=completion,
                              months_to_complete=2, monthly_contribution_needed=500.0)
        assert not proj.is_achievable
