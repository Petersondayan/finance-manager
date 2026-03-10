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
         patch("finance_manager.ui.views.dashboard_view.BudgetService") as mock_bs:

        mock_ar.return_value.get_summary.return_value = MagicMock(
            total_assets=10000.0, total_liabilities=2000.0, net_worth=8000.0
        )
        mock_tr.return_value.get_by_date_range.return_value = []
        mock_tr.return_value.get_monthly_totals.return_value = (3000.0, 1500.0)
        mock_bs.return_value.get_current_budgets.return_value = []
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


def test_dashboard_has_insights_card(qtbot, mock_services):
    """Dashboard should have an AI insights generate button."""
    from finance_manager.ui.views.dashboard_view import DashboardView
    with patch("finance_manager.ui.views.dashboard_view.InsightGenerator") as mock_ig, \
         patch("finance_manager.ui.views.dashboard_view.OllamaClient") as mock_oc:
        mock_ig.return_value.get_recent_insights.return_value = []
        mock_oc.return_value.is_available = False
        view = DashboardView()
        qtbot.addWidget(view)
        assert hasattr(view, "_generate_btn")
        assert hasattr(view, "_insight_text")


def test_generate_button_disabled_when_ollama_unavailable(qtbot, mock_services):
    """Generate Insights button should be disabled when Ollama is not available."""
    from finance_manager.ui.views.dashboard_view import DashboardView
    with patch("finance_manager.ui.views.dashboard_view.InsightGenerator") as mock_ig, \
         patch("finance_manager.ui.views.dashboard_view.OllamaClient") as mock_oc:
        mock_ig.return_value.get_recent_insights.return_value = []
        mock_oc.return_value.is_available = False
        view = DashboardView()
        qtbot.addWidget(view)
        view.refresh()
        assert not view._generate_btn.isEnabled()
