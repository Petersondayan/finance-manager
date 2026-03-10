"""PDF importer."""

import re
from typing import List, Optional
import pdfplumber

from .base_importer import BaseImporter
from ..models.statement_import import ParsedTransaction


class PDFImporter(BaseImporter):
    """Importer for PDF files."""

    _DATE_PATTERN = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
    _AMOUNT_PATTERN = r'-?\$?\d{1,3}(?:,\d{3})*\.\d{2}'

    @property
    def supported_extensions(self) -> List[str]:
        return [".pdf"]

    def parse(self, file_path: str) -> List[ParsedTransaction]:
        """Parse PDF file, trying tables first then plain text."""
        transactions = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if row:
                            txn = self._parse_row(row)
                            if txn:
                                transactions.append(txn)

        # Fallback: parse as plain text when no tables were found
        if not transactions:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        transactions.extend(self._parse_text_lines(text))

        return transactions

    def _parse_row(self, row: List[str]) -> Optional[ParsedTransaction]:
        """Parse a table row into a transaction."""
        date_str = ""
        description = ""
        amount = 0.0

        for cell in row:
            if not cell:
                continue
            cell_str = str(cell).strip()

            if re.search(self._DATE_PATTERN, cell_str) and not date_str:
                date_str = re.search(self._DATE_PATTERN, cell_str).group()
            elif '$' in cell_str or re.match(r'^-?\d+\.\d{2}$', cell_str):
                try:
                    amount = self._clean_amount(cell_str)
                except Exception:
                    pass
            else:
                description = cell_str

        if date_str and description and amount != 0:
            return ParsedTransaction(date=date_str, description=description,
                                     amount=amount, raw_data={"row": row})
        return None

    def _parse_text_lines(self, text: str) -> List[ParsedTransaction]:
        """Parse plain-text lines (e.g. BofA text-layout statements)."""
        transactions = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            date_match = re.search(self._DATE_PATTERN, line)
            amount_match = re.search(self._AMOUNT_PATTERN, line)
            if not date_match or not amount_match:
                continue

            date_str = date_match.group()
            amount_str = amount_match.group()

            # Description is the text between the date and the amount
            start = date_match.end()
            end = amount_match.start()
            description = line[start:end].strip(" -")

            if not description:
                # Fallback: everything before the amount except the date
                description = line[:amount_match.start()].replace(date_str, "").strip(" -")

            if not description:
                continue

            try:
                amount = self._clean_amount(amount_str)
            except Exception:
                continue

            if amount != 0:
                transactions.append(ParsedTransaction(
                    date=date_str,
                    description=description,
                    amount=amount,
                    raw_data={"line": line}
                ))

        return transactions
