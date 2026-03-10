"""Tests for ReportsView."""
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
from finance_manager.ui.views.reports_view import ReportsView


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def mock_report_service(monkeypatch):
    with patch("finance_manager.ui.views.reports_view.ReportService") as mock_rs:
        from finance_manager.services.report_service import MonthlyReport, AnnualReport
        mock_rs.return_value.generate_monthly_report.return_value = MonthlyReport(
            period="2026-03", starting_balance=0, income=0, expenses=0,
            net_change=0, ending_balance=0, top_categories=[], top_transactions=[]
        )
        mock_rs.return_value.generate_annual_report.return_value = AnnualReport(
            year=2026, total_income=0, total_expenses=0, net_savings=0,
            savings_rate=0, monthly_breakdown=[], category_breakdown=[]
        )
        yield


def test_reports_view_creates(qapp, mock_report_service):
    view = ReportsView()
    assert view is not None


def test_reports_view_has_period_selector(qapp, mock_report_service):
    view = ReportsView()
    assert hasattr(view, "_month_combo")


def test_reports_view_has_export_buttons(qapp, mock_report_service):
    view = ReportsView()
    assert hasattr(view, "_export_pdf_btn")
    assert hasattr(view, "_export_xlsx_btn")
