"""Import service."""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pathlib import Path

from ..repositories.transaction_repository import TransactionRepository
from ..repositories.account_repository import AccountRepository
from ..models.transaction import Transaction
from ..models.statement_import import StatementImport, ImportResult, ParsedTransaction
from ..importers.registry import ImporterRegistry
from ..core.logging import get_logger
from ..core.constants import FileType

logger = get_logger()


class ImportService:
    """Service for importing transactions from files."""
    
    def __init__(self,
                 transaction_repo: Optional[TransactionRepository] = None,
                 account_repo: Optional[AccountRepository] = None):
        self._transaction_repo = transaction_repo or TransactionRepository()
        self._account_repo = account_repo or AccountRepository()
        self._registry = ImporterRegistry()
    
    def detect_file_type(self, file_path: str) -> Optional[FileType]:
        """Detect file type from extension."""
        ext = Path(file_path).suffix.lower()
        type_map = {
            '.pdf': FileType.PDF,
            '.csv': FileType.CSV,
            '.xlsx': FileType.XLSX,
            '.xls': FileType.XLSX,
            '.docx': FileType.DOCX,
        }
        return type_map.get(ext)
    
    def parse_file(self, file_path: str, file_type: Optional[FileType] = None) -> List[ParsedTransaction]:
        """Parse transactions from file."""
        if file_type is None:
            file_type = self.detect_file_type(file_path)
        
        if file_type is None:
            raise ValueError(f"Cannot detect file type for: {file_path}")
        
        # Get importer
        importer = self._registry.get_importer(file_type)
        if importer is None:
            raise ValueError(f"No importer available for file type: {file_type}")
        
        # Parse file
        logger.info(f"Parsing {file_type.value} file: {file_path}")
        return importer.parse(file_path)
    
    def import_transactions(self, file_path: str, account_id: int,
                           file_type: Optional[FileType] = None,
                           default_category_id: Optional[int] = None) -> ImportResult:
        """Import transactions from file."""
        # Create import record
        import_record = StatementImport(
            filename=Path(file_path).name,
            file_type=file_type.value if file_type else self.detect_file_type(file_path).value,
            account_id=account_id,
            status="pending"
        )
        
        try:
            # Parse file
            parsed = self.parse_file(file_path, file_type)
            import_record.transactions_count = len(parsed)
            import_record.status = "parsed"
            
            # Convert to transactions
            transactions = []
            errors = []
            for p in parsed:
                try:
                    # Parse date
                    if isinstance(p.date, str):
                        txn_date = self._parse_date(p.date)
                    else:
                        txn_date = p.date

                    txn = Transaction(
                        account_id=account_id,
                        date=txn_date,
                        amount=p.amount,
                        description=p.description,
                        category_id=default_category_id,
                        source_file=Path(file_path).name,
                        is_confirmed=False
                    )
                    transactions.append(txn)
                except Exception as e:
                    msg = f"{p.description}: {e}"
                    errors.append(msg)
                    logger.warning(f"Failed to parse transaction: {msg}")

            # Import transactions
            if transactions:
                self._transaction_repo.create_many(transactions)
                import_record.status = "imported"

                # Update account balance
                total_amount = sum(t.amount for t in transactions)
                account = self._account_repo.get_by_id(account_id)
                if account:
                    new_balance = account.current_balance + total_amount
                    self._account_repo.update_balance(account_id, new_balance)

            logger.info(f"Imported {len(transactions)} transactions from {file_path}")

            return ImportResult(
                statement_id=0,  # Would be set from DB
                success_count=len(transactions),
                error_count=len(errors),
                errors=errors
            )
            
        except Exception as e:
            import_record.status = "error"
            import_record.error_message = str(e)
            logger.error(f"Import failed: {e}")
            raise
    
    def _parse_date(self, date_str: str) -> date:
        """Parse date from various formats."""
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%m/%d/%y",   # BofA: 04/18/24
            "%d/%m/%Y",
            "%d/%m/%y",
            "%Y/%m/%d",
            "%m-%d-%Y",
            "%m-%d-%y",
            "%d-%m-%Y",
            "%d-%m-%y",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Cannot parse date: {date_str}")
    
    def validate_import(self, file_path: str, file_type: Optional[FileType] = None) -> Dict[str, Any]:
        """Validate file can be imported."""
        result = {
            "valid": False,
            "file_path": file_path,
            "file_type": None,
            "transaction_count": 0,
            "errors": []
        }
        
        try:
            # Check file exists
            if not Path(file_path).exists():
                result["errors"].append("File not found")
                return result
            
            # Detect type
            detected_type = file_type or self.detect_file_type(file_path)
            if detected_type is None:
                result["errors"].append("Cannot detect file type")
                return result
            
            result["file_type"] = detected_type.value
            
            # Try to parse
            parsed = self.parse_file(file_path, detected_type)
            result["transaction_count"] = len(parsed)
            result["valid"] = True
            
        except Exception as e:
            result["errors"].append(str(e))
        
        return result
