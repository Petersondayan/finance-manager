"""Tests for BudgetsView."""
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
from finance_manager.ui.views.budgets_view import BudgetsView


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def mock_budget_service(monkeypatch):
    with patch("finance_manager.ui.views.budgets_view.BudgetService") as mock_bs, \
         patch("finance_manager.ui.views.budgets_view.FinanceRepository") as mock_fr:
        mock_bs.return_value.get_current_budgets.return_value = []
        mock_bs.return_value.check_alerts.return_value = []
        mock_fr.return_value.get_categories.return_value = []
        yield mock_bs.return_value


def test_budgets_view_creates(qapp, mock_budget_service):
    view = BudgetsView()
    assert view is not None


def test_budgets_view_has_table(qapp, mock_budget_service):
    view = BudgetsView()
    assert hasattr(view, "_table")


def test_budgets_view_has_add_button(qapp, mock_budget_service):
    view = BudgetsView()
    assert hasattr(view, "_add_btn")
