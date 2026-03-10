"""Tests for TransactionService."""

from unittest.mock import MagicMock, call
from datetime import date
import pytest

from finance_manager.models.transaction import Transaction
from finance_manager.models.account import Account
from finance_manager.services.transaction_service import TransactionService


def _make_transaction(id=1, account_id=1, amount=100.0, description="Test"):
    return Transaction(id=id, account_id=account_id, date=date(2026, 3, 1),
                       amount=amount, description=description)


def _make_account(id=1, balance=500.0):
    return Account(id=id, name="Checking", account_type="checking", current_balance=balance)


def _make_svc():
    txn_repo = MagicMock()
    acc_repo = MagicMock()
    acc_repo.get_by_id.return_value = _make_account()
    return TransactionService(transaction_repo=txn_repo, account_repo=acc_repo), txn_repo, acc_repo


class TestCreateTransaction:
    def test_creates_and_updates_balance(self):
        svc, txn_repo, acc_repo = _make_svc()
        txn = _make_transaction(amount=200.0)
        txn_repo.create.return_value = txn

        result = svc.create_transaction(txn)

        txn_repo.create.assert_called_once_with(txn)
        acc_repo.update_balance.assert_called_once_with(1, 700.0)
        assert result is txn

    def test_skips_balance_update_when_disabled(self):
        svc, txn_repo, acc_repo = _make_svc()
        txn = _make_transaction(amount=200.0)
        txn_repo.create.return_value = txn

        svc.create_transaction(txn, update_balance=False)

        acc_repo.update_balance.assert_not_called()


class TestDeleteTransaction:
    def test_returns_false_if_not_found(self):
        svc, txn_repo, acc_repo = _make_svc()
        txn_repo.get_by_id.return_value = None

        assert svc.delete_transaction(999) is False

    def test_deletes_and_reverses_balance(self):
        svc, txn_repo, acc_repo = _make_svc()
        txn = _make_transaction(amount=200.0)
        txn_repo.get_by_id.return_value = txn
        txn_repo.delete.return_value = True

        result = svc.delete_transaction(1)

        txn_repo.delete.assert_called_once_with(1)
        # Balance 500 - 200 (reverse) = 300
        acc_repo.update_balance.assert_called_once_with(1, 300.0)
        assert result is True

    def test_delete_skips_balance_when_disabled(self):
        svc, txn_repo, acc_repo = _make_svc()
        txn = _make_transaction(amount=200.0)
        txn_repo.get_by_id.return_value = txn
        txn_repo.delete.return_value = True

        svc.delete_transaction(1, update_balance=False)
        acc_repo.update_balance.assert_not_called()


class TestGetMonthlySummary:
    def test_summary_structure(self):
        svc, txn_repo, acc_repo = _make_svc()
        txn_repo.get_monthly_totals.return_value = (3000.0, 1500.0)

        result = svc.get_monthly_summary(2026, 3)

        assert result["income"] == 3000.0
        assert result["expenses"] == 1500.0
        assert result["net"] == 1500.0
        assert result["period"] == "2026-03"

    def test_net_can_be_negative(self):
        svc, txn_repo, acc_repo = _make_svc()
        txn_repo.get_monthly_totals.return_value = (1000.0, 2000.0)

        result = svc.get_monthly_summary(2026, 3)
        assert result["net"] == -1000.0


class TestGetSpendingByCategory:
    def test_calculates_percentages(self):
        svc, txn_repo, acc_repo = _make_svc()
        txn_repo.get_total_by_category.return_value = [
            (1, "Food", 600.0),
            (2, "Transport", 400.0),
        ]

        result = svc.get_spending_by_category(date(2026, 3, 1), date(2026, 3, 31))

        assert len(result) == 2
        food = next(r for r in result if r["category_name"] == "Food")
        assert food["percentage"] == 60.0
        transport = next(r for r in result if r["category_name"] == "Transport")
        assert transport["percentage"] == 40.0

    def test_empty_returns_empty_list(self):
        svc, txn_repo, acc_repo = _make_svc()
        txn_repo.get_total_by_category.return_value = []

        result = svc.get_spending_by_category(date(2026, 3, 1), date(2026, 3, 31))
        assert result == []


class TestImportTransactions:
    def test_imports_and_updates_balances(self):
        svc, txn_repo, acc_repo = _make_svc()
        transactions = [
            _make_transaction(id=1, account_id=1, amount=100.0),
            _make_transaction(id=2, account_id=1, amount=200.0),
            _make_transaction(id=3, account_id=2, amount=50.0),
        ]
        txn_repo.create_many.return_value = transactions

        result = svc.import_transactions(transactions)

        assert result["imported_count"] == 3
        assert result["account_totals"][1] == 300.0
        assert result["account_totals"][2] == 50.0
