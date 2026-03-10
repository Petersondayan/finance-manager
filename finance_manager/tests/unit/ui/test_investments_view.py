"""Tests for InvestmentsView."""
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
from finance_manager.ui.views.investments_view import InvestmentsView


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def mock_investment_service(monkeypatch):
    with patch("finance_manager.ui.views.investments_view.InvestmentService") as mock_is, \
         patch("finance_manager.ui.views.investments_view.AccountRepository") as mock_ar, \
         patch("finance_manager.ui.views.investments_view.FinanceRepository") as mock_fr:
        mock_is.return_value.get_portfolio_summary.return_value = MagicMock(
            total_cost_basis=0.0, total_current_value=0.0, total_gain_loss=0.0,
            total_gain_loss_percent=0.0
        )
        mock_is.return_value.get_asset_allocation.return_value = []
        mock_fr.return_value.get_all_holdings.return_value = []
        mock_ar.return_value.get_all.return_value = []
        yield


def test_investments_view_creates(qapp, mock_investment_service):
    view = InvestmentsView()
    assert view is not None


def test_investments_view_has_table(qapp, mock_investment_service):
    view = InvestmentsView()
    assert hasattr(view, "_holdings_table")


def test_investments_view_has_chart(qapp, mock_investment_service):
    view = InvestmentsView()
    assert hasattr(view, "_pie_chart")
