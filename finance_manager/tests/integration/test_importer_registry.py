"""Integration tests for ImporterRegistry."""

import pytest

from finance_manager.importers.registry import ImporterRegistry
from finance_manager.importers.csv_importer import CSVImporter
from finance_manager.importers.xlsx_importer import XLSXImporter
from finance_manager.importers.pdf_importer import PDFImporter
from finance_manager.importers.docx_importer import DOCXImporter
from finance_manager.core.constants import FileType


@pytest.fixture()
def registry():
    return ImporterRegistry()


class TestImporterRegistry:
    def test_returns_csv_importer(self, registry):
        assert isinstance(registry.get_importer(FileType.CSV), CSVImporter)

    def test_returns_xlsx_importer(self, registry):
        assert isinstance(registry.get_importer(FileType.XLSX), XLSXImporter)

    def test_returns_pdf_importer(self, registry):
        assert isinstance(registry.get_importer(FileType.PDF), PDFImporter)

    def test_returns_docx_importer(self, registry):
        assert isinstance(registry.get_importer(FileType.DOCX), DOCXImporter)

    def test_returns_none_for_unknown(self, registry):
        assert registry.get_importer("unknown") is None  # type: ignore

    def test_can_override_importer(self, registry):
        """Custom importer can replace a registered one."""
        custom = CSVImporter()
        registry.register(FileType.CSV, custom)
        assert registry.get_importer(FileType.CSV) is custom
