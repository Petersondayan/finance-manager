"""First-run setup dialog shown on initial application launch."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QDialogButtonBox, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ...core.config import get_config, get_config_manager


_CURRENCIES = [
    ("$",   "$ — US Dollar"),
    ("€",   "€ — Euro"),
    ("£",   "£ — British Pound"),
    ("¥",   "¥ — Yen / Yuan"),
    ("₹",   "₹ — Indian Rupee"),
    ("A$",  "A$ — Australian Dollar"),
    ("C$",  "C$ — Canadian Dollar"),
    ("CHF", "CHF — Swiss Franc"),
]


class FirstRunDialog(QDialog):
    """Welcome wizard shown only on the very first launch."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to Finance Manager")
        self.setMinimumWidth(440)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(28, 28, 28, 20)

        # Header
        title = QLabel("Welcome to Personal Finance Manager")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(
            "Let's get you set up in a few seconds.\n"
            "You can change any of these settings later in Edit → Preferences."
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #555; margin-bottom: 8px;")
        layout.addWidget(subtitle)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #ddd;")
        layout.addWidget(line)

        # Currency selection
        currency_row = QHBoxLayout()
        currency_label = QLabel("Currency symbol:")
        currency_label.setMinimumWidth(140)
        currency_row.addWidget(currency_label)

        self._currency_combo = QComboBox()
        self._currency_combo.setEditable(True)
        for symbol, label in _CURRENCIES:
            self._currency_combo.addItem(label, symbol)
        currency_row.addWidget(self._currency_combo, 1)
        layout.addLayout(currency_row)

        hint = QLabel("Not in the list? Type your own symbol in the box above.")
        hint.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(hint)

        layout.addStretch()

        # Buttons — only Get Started, no Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Get Started")
        buttons.accepted.connect(self._on_accept)
        layout.addWidget(buttons)

    def _on_accept(self):
        symbol = (
            self._currency_combo.currentData()
            or self._currency_combo.currentText().strip()
            or "$"
        )
        cfg = get_config()
        cfg.currency_symbol = symbol
        cfg.first_run = False
        get_config_manager().save(cfg)
        self.accept()
