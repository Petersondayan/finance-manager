"""Integration tests for XLSXImporter — uses real temp XLSX files."""

import pytest
from openpyxl import Workbook

from finance_manager.importers.xlsx_importer import XLSXImporter


@pytest.fixture()
def importer():
    return XLSXImporter()


def write_xlsx(path, rows: list) -> str:
    """Write rows (first row = headers) to an xlsx file."""
    wb = Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    wb.save(str(path))
    return str(path)


class TestXLSXImporterCanImport:
    def test_accepts_xlsx(self, importer):
        assert importer.can_import("statement.xlsx")

    def test_accepts_xls(self, importer):
        assert importer.can_import("statement.xls")

    def test_rejects_csv(self, importer):
        assert not importer.can_import("statement.csv")


class TestXLSXImporterParse:
    def test_parses_standard_xlsx(self, importer, tmp_path):
        xlsx_file = write_xlsx(tmp_path / "bank.xlsx", [
            ["Date", "Description", "Amount"],
            ["2026-03-01", "Grocery Store", -85.50],
            ["2026-03-02", "Salary Deposit", 3000.00],
        ])
        result = importer.parse(xlsx_file)
        assert len(result) == 2
        assert result[0].amount == -85.50
        assert result[1].amount == 3000.00

    def test_parses_description_column(self, importer, tmp_path):
        xlsx_file = write_xlsx(tmp_path / "bank2.xlsx", [
            ["Date", "Desc", "Amount"],
            ["2026-03-01", "Netflix", -15.99],
        ])
        result = importer.parse(xlsx_file)
        assert len(result) == 1
        assert result[0].description == "Netflix"

    def test_empty_xlsx_returns_empty(self, importer, tmp_path):
        xlsx_file = write_xlsx(tmp_path / "empty.xlsx", [
            ["Date", "Description", "Amount"],
        ])
        result = importer.parse(xlsx_file)
        assert result == []

    def test_skips_rows_without_date(self, importer, tmp_path):
        xlsx_file = write_xlsx(tmp_path / "bank3.xlsx", [
            ["Date", "Description", "Amount"],
            [None, "No date row", -10.00],
            ["2026-03-01", "Valid row", -50.00],
        ])
        result = importer.parse(xlsx_file)
        valid = [r for r in result if r.amount == -50.0]
        assert len(valid) == 1
