"""Integration tests for CSVImporter — uses real temp files, no mocks."""

import pytest
from pathlib import Path

from finance_manager.importers.csv_importer import CSVImporter


@pytest.fixture()
def importer():
    return CSVImporter()


def write_csv(path: Path, content: str) -> str:
    path.write_text(content, encoding="utf-8")
    return str(path)


class TestCSVImporterCanImport:
    def test_accepts_csv(self, importer):
        assert importer.can_import("bank_statement.csv")

    def test_rejects_pdf(self, importer):
        assert not importer.can_import("bank_statement.pdf")

    def test_rejects_xlsx(self, importer):
        assert not importer.can_import("bank_statement.xlsx")


class TestCSVImporterParse:
    def test_parses_standard_csv(self, importer, tmp_path):
        csv_file = write_csv(tmp_path / "bank.csv", (
            "Date,Description,Amount\n"
            "2026-03-01,Grocery Store,-85.50\n"
            "2026-03-02,Salary Deposit,3000.00\n"
            "2026-03-03,Electric Bill,-120.00\n"
        ))
        result = importer.parse(csv_file)
        assert len(result) == 3
        assert result[0].description == "Grocery Store"
        assert result[0].amount == -85.50
        assert result[1].amount == 3000.00

    def test_parses_transaction_date_column(self, importer, tmp_path):
        csv_file = write_csv(tmp_path / "chase.csv", (
            "Transaction Date,Payee,Amount\n"
            "2026-03-05,Amazon,-45.99\n"
        ))
        result = importer.parse(csv_file)
        assert len(result) == 1
        assert result[0].description == "Amazon"
        assert result[0].amount == -45.99

    def test_parses_amount_with_dollar_sign(self, importer, tmp_path):
        csv_file = write_csv(tmp_path / "bank2.csv", (
            "Date,Description,Amount\n"
            "2026-03-01,Coffee,$4.50\n"
        ))
        result = importer.parse(csv_file)
        assert len(result) == 1
        assert result[0].amount == 4.50

    def test_parses_parentheses_negative(self, importer, tmp_path):
        csv_file = write_csv(tmp_path / "bank3.csv", (
            "Date,Description,Amount\n"
            "2026-03-01,ATM Withdrawal,(200.00)\n"
        ))
        result = importer.parse(csv_file)
        assert len(result) == 1
        assert result[0].amount == -200.00

    def test_skips_malformed_rows(self, importer, tmp_path):
        csv_file = write_csv(tmp_path / "bank4.csv", (
            "Date,Description,Amount\n"
            "2026-03-01,Valid Row,-50.00\n"
            "bad_date,,not_a_number\n"
            "2026-03-03,Another Row,-30.00\n"
        ))
        result = importer.parse(csv_file)
        # Should have at least the two valid rows
        valid = [r for r in result if r.amount in (-50.0, -30.0)]
        assert len(valid) == 2

    def test_empty_csv_returns_empty_list(self, importer, tmp_path):
        csv_file = write_csv(tmp_path / "empty.csv", "Date,Description,Amount\n")
        result = importer.parse(csv_file)
        assert result == []

    def test_raw_data_preserved(self, importer, tmp_path):
        csv_file = write_csv(tmp_path / "bank5.csv", (
            "Date,Description,Amount,Balance\n"
            "2026-03-01,Coffee,-4.50,995.50\n"
        ))
        result = importer.parse(csv_file)
        assert len(result) == 1
        assert "Balance" in result[0].raw_data
