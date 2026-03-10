"""Integration tests for Categorizer — mocks OllamaClient, tests business logic."""

from unittest.mock import MagicMock, patch
import pytest

from finance_manager.ai.categorizer import Categorizer, CategorizationResult
from finance_manager.models.transaction import Transaction
from datetime import date


def _make_client(response: dict, available: bool = True) -> MagicMock:
    client = MagicMock()
    client.is_available = available
    client.generate_json.return_value = response
    return client


def _make_config(enabled: bool = True, threshold: float = 0.8) -> MagicMock:
    cfg = MagicMock()
    cfg.ollama.enabled = enabled
    cfg.ollama.confidence_threshold = threshold
    return cfg


class TestCategorizerWhenDisabled:
    def test_returns_unknown_when_ai_disabled(self):
        client = _make_client({})
        with patch("finance_manager.ai.categorizer.get_config", return_value=_make_config(enabled=False)):
            cat = Categorizer(client=client)
            result = cat.suggest_category("Coffee shop", -5.0)
        assert result.category_id is None
        assert result.confidence == 0.0
        client.generate_json.assert_not_called()

    def test_returns_unknown_when_ollama_unavailable(self):
        client = _make_client({}, available=False)
        with patch("finance_manager.ai.categorizer.get_config", return_value=_make_config()):
            cat = Categorizer(client=client)
            result = cat.suggest_category("Coffee shop", -5.0)
        assert result.category_id is None
        client.generate_json.assert_not_called()


class TestCategorizerSuggestCategory:
    def test_maps_known_category(self):
        client = _make_client({
            "category": "Groceries",
            "confidence": 0.95,
            "reasoning": "Grocery store purchase",
        })
        with patch("finance_manager.ai.categorizer.get_config", return_value=_make_config()):
            cat = Categorizer(client=client)
            result = cat.suggest_category("Walmart Grocery", -120.0)
        assert result.category_name == "Groceries"
        assert result.confidence == 0.95
        assert result.category_id is not None

    def test_returns_none_id_for_unknown_category(self):
        client = _make_client({
            "category": "CompletlyMadeUpCategory",
            "confidence": 0.5,
            "reasoning": "Unknown",
        })
        with patch("finance_manager.ai.categorizer.get_config", return_value=_make_config()):
            cat = Categorizer(client=client)
            result = cat.suggest_category("Mystery charge", -9.99)
        assert result.category_name == "CompletlyMadeUpCategory"

    def test_handles_client_exception_gracefully(self):
        client = MagicMock()
        client.is_available = True
        client.generate_json.side_effect = ValueError("Bad JSON")
        with patch("finance_manager.ai.categorizer.get_config", return_value=_make_config()):
            cat = Categorizer(client=client)
            result = cat.suggest_category("Something", -10.0)
        assert result.category_id is None
        assert result.confidence == 0.0
        assert "Error" in result.reasoning

    def test_fuzzy_match_partial_name(self):
        # "Food" is contained in "Food & Dining" → fuzzy match should resolve it
        client = _make_client({
            "category": "Food",
            "confidence": 0.7,
            "reasoning": "Food purchase",
        })
        with patch("finance_manager.ai.categorizer.get_config", return_value=_make_config()):
            cat = Categorizer(client=client)
            result = cat.suggest_category("Local market", -30.0)
        assert result.category_id is not None


class TestShouldAutoAccept:
    def test_auto_accept_above_threshold(self):
        client = _make_client({})
        with patch("finance_manager.ai.categorizer.get_config",
                   return_value=_make_config(threshold=0.8)):
            cat = Categorizer(client=client)
            assert cat.should_auto_accept(0.9) is True
            assert cat.should_auto_accept(0.8) is True

    def test_no_auto_accept_below_threshold(self):
        client = _make_client({})
        with patch("finance_manager.ai.categorizer.get_config",
                   return_value=_make_config(threshold=0.8)):
            cat = Categorizer(client=client)
            assert cat.should_auto_accept(0.79) is False


class TestCategorizeBatch:
    def test_batch_returns_one_suggestion_per_transaction(self):
        client = _make_client({
            "category": "Food & Dining",
            "confidence": 0.85,
            "reasoning": "Restaurant",
        })
        with patch("finance_manager.ai.categorizer.get_config", return_value=_make_config()):
            cat = Categorizer(client=client)
            txns = [
                Transaction(account_id=1, date=date(2026, 3, 1),
                            amount=-20.0, description="Pizza place"),
                Transaction(account_id=1, date=date(2026, 3, 2),
                            amount=-15.0, description="Burger joint"),
            ]
            results = cat.categorize_batch(txns)
        assert len(results) == 2
        assert all(r.confidence == 0.85 for r in results)
