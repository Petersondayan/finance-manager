"""Tests for DashboardView."""
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
from finance_manager.ui.views.dashboard_view import DashboardView


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    return app


@pytest.fixture
def mock_services(monkeypatch):
    with patch("finance_manager.ui.views.dashboard_view.AccountRepository") as mock_ar, \
         patch("finance_manager.ui.views.dashboard_view.TransactionRepository") as mock_tr, \
         patch("finance_manager.ui.views.dashboard_view.BudgetService") as mock_bs, \
         patch("finance_manager.ui.views.dashboard_view.ReportService") as mock_rs:

        mock_ar.return_value.get_summary.return_value = MagicMock(
            total_assets=10000.0, total_liabilities=2000.0, net_worth=8000.0
        )
        mock_tr.return_value.get_by_date_range.return_value = []
        mock_tr.return_value.get_monthly_totals.return_value = (3000.0, 1500.0)
        mock_bs.return_value.get_current_budgets.return_value = []
        mock_rs.return_value.get_spending_trend.return_value = []
        yield


def test_dashboard_view_creates(qapp, mock_services):
    view = DashboardView()
    assert view is not None


def test_dashboard_shows_net_worth(qapp, mock_services):
    view = DashboardView()
    assert hasattr(view, "_net_worth_label")


def test_dashboard_shows_budget_section(qapp, mock_services):
    view = DashboardView()
    assert hasattr(view, "_budget_container")


def test_dashboard_shows_recent_transactions(qapp, mock_services):
    view = DashboardView()
    assert hasattr(view, "_recent_table")
