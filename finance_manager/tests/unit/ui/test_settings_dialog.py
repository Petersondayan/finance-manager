"""Tests for SettingsDialog."""

from unittest.mock import patch, MagicMock
import pytest


@pytest.fixture()
def mock_config(qapp):
    cfg = MagicMock()
    cfg.currency_symbol = "$"
    cfg.date_format = "%Y-%m-%d"
    cfg.ollama.enabled = True
    cfg.ollama.host = "http://localhost:11434"
    cfg.ollama.model = "llama3.2:3b"
    cfg.ollama.confidence_threshold = 0.8
    cfg.ollama.timeout = 30
    cfg.database.auto_backup = True
    cfg.database.backup_count = 5
    cfg.database.backup_interval_days = 7
    return cfg


def test_settings_dialog_opens(qtbot, mock_config):
    with patch("finance_manager.ui.dialogs.settings_dialog.get_config", return_value=mock_config), \
         patch("finance_manager.ui.dialogs.settings_dialog.get_config_manager"):
        from finance_manager.ui.dialogs.settings_dialog import SettingsDialog
        dlg = SettingsDialog()
        qtbot.addWidget(dlg)
        assert dlg.windowTitle() == "Settings"


def test_settings_dialog_has_three_tabs(qtbot, mock_config):
    with patch("finance_manager.ui.dialogs.settings_dialog.get_config", return_value=mock_config), \
         patch("finance_manager.ui.dialogs.settings_dialog.get_config_manager"):
        from finance_manager.ui.dialogs.settings_dialog import SettingsDialog
        dlg = SettingsDialog()
        qtbot.addWidget(dlg)
        assert dlg._tabs.count() == 3


def test_settings_loads_existing_values(qtbot, mock_config):
    with patch("finance_manager.ui.dialogs.settings_dialog.get_config", return_value=mock_config), \
         patch("finance_manager.ui.dialogs.settings_dialog.get_config_manager"):
        from finance_manager.ui.dialogs.settings_dialog import SettingsDialog
        dlg = SettingsDialog()
        qtbot.addWidget(dlg)
        assert dlg._ollama_host_input.text() == "http://localhost:11434"
        assert dlg._timeout_spin.value() == 30
        assert dlg._backup_count_spin.value() == 5


def test_ai_fields_disabled_when_ai_off(qtbot, mock_config):
    mock_config.ollama.enabled = False
    with patch("finance_manager.ui.dialogs.settings_dialog.get_config", return_value=mock_config), \
         patch("finance_manager.ui.dialogs.settings_dialog.get_config_manager"):
        from finance_manager.ui.dialogs.settings_dialog import SettingsDialog
        dlg = SettingsDialog()
        qtbot.addWidget(dlg)
        assert not dlg._ollama_host_input.isEnabled()
        assert not dlg._ollama_model_input.isEnabled()
