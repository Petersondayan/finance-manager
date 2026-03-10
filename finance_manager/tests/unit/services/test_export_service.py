"""Tests for ExportService."""
import pytest
import tempfile
from pathlib import Path
from finance_manager.services.export_service import ExportService
from finance_manager.services.report_service import MonthlyReport, AnnualReport


@pytest.fixture
def monthly_report():
    return MonthlyReport(
        period="2026-03",
        starting_balance=5000.0,
        income=3000.0,
        expenses=1500.0,
        net_change=1500.0,
        ending_balance=6500.0,
        top_categories=[{"name": "Groceries", "amount": 400.0}],
        top_transactions=[],
    )


@pytest.fixture
def annual_report():
    return AnnualReport(
        year=2025,
        total_income=36000.0,
        total_expenses=24000.0,
        net_savings=12000.0,
        savings_rate=33.3,
        monthly_breakdown=[{"month": i, "income": 3000.0, "expenses": 2000.0, "net": 1000.0} for i in range(1, 13)],
        category_breakdown=[{"name": "Groceries", "amount": 4800.0}],
    )


def test_export_monthly_to_xlsx(monthly_report):
    svc = ExportService()
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.xlsx"
        svc.export_monthly_xlsx(monthly_report, str(out))
        assert out.exists()
        assert out.stat().st_size > 0


def test_export_monthly_to_pdf(monthly_report):
    svc = ExportService()
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "report.pdf"
        svc.export_monthly_pdf(monthly_report, str(out))
        assert out.exists()
        assert out.stat().st_size > 0


def test_export_annual_to_xlsx(annual_report):
    svc = ExportService()
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "annual.xlsx"
        svc.export_annual_xlsx(annual_report, str(out))
        assert out.exists()
        assert out.stat().st_size > 0


def test_export_annual_to_pdf(annual_report):
    svc = ExportService()
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "annual.pdf"
        svc.export_annual_pdf(annual_report, str(out))
        assert out.exists()
        assert out.stat().st_size > 0
