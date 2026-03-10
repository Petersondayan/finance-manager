"""Tests for GoalsView."""
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
from finance_manager.ui.views.goals_view import GoalsView


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def mock_goal_service(monkeypatch):
    with patch("finance_manager.ui.views.goals_view.GoalService") as mock_gs:
        mock_gs.return_value.get_active_goals.return_value = []
        yield mock_gs.return_value


def test_goals_view_creates(qapp, mock_goal_service):
    view = GoalsView()
    assert view is not None


def test_goals_view_has_add_button(qapp, mock_goal_service):
    view = GoalsView()
    assert hasattr(view, "_add_btn")


def test_goals_view_has_goals_container(qapp, mock_goal_service):
    view = GoalsView()
    assert hasattr(view, "_goals_container")
