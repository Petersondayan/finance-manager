"""Tests for FirstRunDialog."""

from unittest.mock import patch, MagicMock
import pytest


@pytest.fixture()
def mock_config():
    cfg = MagicMock()
    cfg.currency_symbol = "$"
    cfg.first_run = True
    return cfg


def test_first_run_dialog_opens(qtbot, mock_config):
    with patch("finance_manager.ui.dialogs.first_run_dialog.get_config", return_value=mock_config), \
         patch("finance_manager.ui.dialogs.first_run_dialog.get_config_manager"):
        from finance_manager.ui.dialogs.first_run_dialog import FirstRunDialog
        dlg = FirstRunDialog()
        qtbot.addWidget(dlg)
        assert "Welcome" in dlg.windowTitle()


def test_first_run_has_currency_combo(qtbot, mock_config):
    with patch("finance_manager.ui.dialogs.first_run_dialog.get_config", return_value=mock_config), \
         patch("finance_manager.ui.dialogs.first_run_dialog.get_config_manager"):
        from finance_manager.ui.dialogs.first_run_dialog import FirstRunDialog
        dlg = FirstRunDialog()
        qtbot.addWidget(dlg)
        assert dlg._currency_combo.count() > 0


def test_first_run_accept_saves_config(qtbot, mock_config):
    mock_mgr = MagicMock()
    with patch("finance_manager.ui.dialogs.first_run_dialog.get_config", return_value=mock_config), \
         patch("finance_manager.ui.dialogs.first_run_dialog.get_config_manager", return_value=mock_mgr):
        from finance_manager.ui.dialogs.first_run_dialog import FirstRunDialog
        dlg = FirstRunDialog()
        qtbot.addWidget(dlg)
        dlg._on_accept()
        assert mock_config.first_run is False
        mock_mgr.save.assert_called_once_with(mock_config)
