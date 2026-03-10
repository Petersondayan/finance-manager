"""Settings / preferences dialog."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QLineEdit, QComboBox, QCheckBox, QSpinBox,
    QDoubleSpinBox, QDialogButtonBox, QLabel, QGroupBox,
)
from PyQt6.QtCore import Qt

from ...core.config import get_config, get_config_manager


_DATE_FORMATS = [
    ("%Y-%m-%d", "2026-03-10  (ISO)"),
    ("%m/%d/%Y", "03/10/2026  (US)"),
    ("%d/%m/%Y", "10/03/2026  (EU)"),
    ("%d.%m.%Y", "10.03.2026  (DE)"),
    ("%b %d, %Y", "Mar 10, 2026"),
]

_CURRENCY_SYMBOLS = [
    ("$", "$ — US Dollar"),
    ("€", "€ — Euro"),
    ("£", "£ — British Pound"),
    ("¥", "¥ — Yen / Yuan"),
    ("₹", "₹ — Indian Rupee"),
    ("A$", "A$ — Australian Dollar"),
    ("C$", "C$ — Canadian Dollar"),
    ("CHF", "CHF — Swiss Franc"),
]


class SettingsDialog(QDialog):
    """Tabbed preferences dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(480)
        self._config = get_config()
        self._setup_ui()
        self._load_values()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_general_tab(), "General")
        self._tabs.addTab(self._build_ai_tab(), "AI / Ollama")
        self._tabs.addTab(self._build_database_tab(), "Database")
        layout.addWidget(self._tabs)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _build_general_tab(self) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(12)
        form.setContentsMargins(16, 16, 16, 16)

        self._currency_combo = QComboBox()
        for symbol, label in _CURRENCY_SYMBOLS:
            self._currency_combo.addItem(label, symbol)
        # Allow typing a custom symbol
        self._currency_combo.setEditable(True)
        form.addRow("Currency symbol:", self._currency_combo)

        self._date_combo = QComboBox()
        for fmt, label in _DATE_FORMATS:
            self._date_combo.addItem(label, fmt)
        form.addRow("Date format:", self._date_combo)

        return tab

    def _build_ai_tab(self) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(12)
        form.setContentsMargins(16, 16, 16, 16)

        self._ai_enabled_check = QCheckBox("Enable AI categorisation and insights")
        form.addRow("", self._ai_enabled_check)

        self._ollama_host_input = QLineEdit()
        self._ollama_host_input.setPlaceholderText("http://localhost:11434")
        form.addRow("Ollama host:", self._ollama_host_input)

        self._ollama_model_input = QLineEdit()
        self._ollama_model_input.setPlaceholderText("llama3.2:3b")
        form.addRow("Model:", self._ollama_model_input)

        self._confidence_spin = QDoubleSpinBox()
        self._confidence_spin.setRange(0.0, 1.0)
        self._confidence_spin.setSingleStep(0.05)
        self._confidence_spin.setDecimals(2)
        self._confidence_spin.setToolTip(
            "Minimum confidence for auto-accepting AI category suggestions (0–1)"
        )
        form.addRow("Auto-accept threshold:", self._confidence_spin)

        self._timeout_spin = QSpinBox()
        self._timeout_spin.setRange(5, 300)
        self._timeout_spin.setSuffix(" s")
        form.addRow("Request timeout:", self._timeout_spin)

        # Grey out fields when AI disabled
        def _toggle(enabled: bool):
            for w in (self._ollama_host_input, self._ollama_model_input,
                      self._confidence_spin, self._timeout_spin):
                w.setEnabled(enabled)

        self._ai_enabled_check.toggled.connect(_toggle)

        return tab

    def _build_database_tab(self) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(12)
        form.setContentsMargins(16, 16, 16, 16)

        self._backup_check = QCheckBox("Automatic backups")
        form.addRow("", self._backup_check)

        self._backup_count_spin = QSpinBox()
        self._backup_count_spin.setRange(1, 30)
        self._backup_count_spin.setSuffix(" copies")
        form.addRow("Backups to keep:", self._backup_count_spin)

        self._backup_interval_spin = QSpinBox()
        self._backup_interval_spin.setRange(1, 365)
        self._backup_interval_spin.setSuffix(" days")
        form.addRow("Backup interval:", self._backup_interval_spin)

        def _toggle_backup(enabled: bool):
            self._backup_count_spin.setEnabled(enabled)
            self._backup_interval_spin.setEnabled(enabled)

        self._backup_check.toggled.connect(_toggle_backup)

        return tab

    # ------------------------------------------------------------------
    # Load / save
    # ------------------------------------------------------------------

    def _load_values(self):
        cfg = self._config

        # General
        idx = self._currency_combo.findData(cfg.currency_symbol)
        if idx >= 0:
            self._currency_combo.setCurrentIndex(idx)
        else:
            self._currency_combo.setEditText(cfg.currency_symbol)

        idx = self._date_combo.findData(cfg.date_format)
        if idx >= 0:
            self._date_combo.setCurrentIndex(idx)

        # AI
        self._ai_enabled_check.setChecked(cfg.ollama.enabled)
        self._ollama_host_input.setText(cfg.ollama.host)
        self._ollama_model_input.setText(cfg.ollama.model)
        self._confidence_spin.setValue(cfg.ollama.confidence_threshold)
        self._timeout_spin.setValue(cfg.ollama.timeout)
        # Trigger toggle to grey/ungrey dependent fields
        for w in (self._ollama_host_input, self._ollama_model_input,
                  self._confidence_spin, self._timeout_spin):
            w.setEnabled(cfg.ollama.enabled)

        # Database
        self._backup_check.setChecked(cfg.database.auto_backup)
        self._backup_count_spin.setValue(cfg.database.backup_count)
        self._backup_interval_spin.setValue(cfg.database.backup_interval_days)
        self._backup_count_spin.setEnabled(cfg.database.auto_backup)
        self._backup_interval_spin.setEnabled(cfg.database.auto_backup)

    def _on_ok(self):
        cfg = self._config

        # General
        symbol = self._currency_combo.currentData() or self._currency_combo.currentText().strip()
        cfg.currency_symbol = symbol or cfg.currency_symbol
        cfg.date_format = self._date_combo.currentData() or cfg.date_format

        # AI
        cfg.ollama.enabled = self._ai_enabled_check.isChecked()
        host = self._ollama_host_input.text().strip()
        cfg.ollama.host = host or cfg.ollama.host
        model = self._ollama_model_input.text().strip()
        cfg.ollama.model = model or cfg.ollama.model
        cfg.ollama.confidence_threshold = self._confidence_spin.value()
        cfg.ollama.timeout = self._timeout_spin.value()

        # Database
        cfg.database.auto_backup = self._backup_check.isChecked()
        cfg.database.backup_count = self._backup_count_spin.value()
        cfg.database.backup_interval_days = self._backup_interval_spin.value()

        get_config_manager().save(cfg)
        self.accept()
