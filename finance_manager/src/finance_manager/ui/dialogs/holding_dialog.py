"""Dialog for adding/editing an investment holding."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QDoubleSpinBox, QDialogButtonBox, QMessageBox,
)
from ...models.investment import InvestmentHolding


ASSET_TYPES = [
    ("Stock", "stock"),
    ("ETF", "etf"),
    ("Crypto", "crypto"),
    ("Other", "other"),
]


class HoldingDialog(QDialog):
    """Add or edit an investment holding."""

    def __init__(self, accounts: list, parent=None, holding: InvestmentHolding = None):
        super().__init__(parent)
        self._holding = holding
        self._accounts = accounts  # list of (id, name)
        self.setWindowTitle("Edit Holding" if holding else "Add Holding")
        self.setMinimumWidth(400)
        self._setup_ui()
        if holding:
            self._load_holding()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(12)

        self._account_combo = QComboBox()
        for acc_id, acc_name in self._accounts:
            self._account_combo.addItem(acc_name, acc_id)
        form.addRow("Account:", self._account_combo)

        self._ticker_input = QLineEdit()
        self._ticker_input.setPlaceholderText("e.g., AAPL or Bitcoin")
        form.addRow("Ticker / Name:", self._ticker_input)

        self._type_combo = QComboBox()
        for label, value in ASSET_TYPES:
            self._type_combo.addItem(label, value)
        form.addRow("Asset Type:", self._type_combo)

        self._shares_input = QDoubleSpinBox()
        self._shares_input.setRange(0.000001, 9999999.0)
        self._shares_input.setDecimals(6)
        self._shares_input.setValue(1.0)
        form.addRow("Shares:", self._shares_input)

        self._cost_input = QDoubleSpinBox()
        self._cost_input.setRange(0.01, 99999999.99)
        self._cost_input.setDecimals(2)
        self._cost_input.setPrefix("$")
        self._cost_input.setValue(100.0)
        form.addRow("Total Cost Basis:", self._cost_input)

        self._price_input = QDoubleSpinBox()
        self._price_input.setRange(0.0001, 999999.99)
        self._price_input.setDecimals(4)
        self._price_input.setPrefix("$")
        self._price_input.setValue(100.0)
        form.addRow("Current Price:", self._price_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_holding(self):
        h = self._holding
        idx = self._account_combo.findData(h.account_id)
        if idx >= 0:
            self._account_combo.setCurrentIndex(idx)
        self._ticker_input.setText(h.ticker_or_name)
        idx2 = self._type_combo.findData(h.asset_type)
        if idx2 >= 0:
            self._type_combo.setCurrentIndex(idx2)
        self._shares_input.setValue(h.shares)
        self._cost_input.setValue(h.cost_basis)
        self._price_input.setValue(h.last_price or h.cost_basis / max(h.shares, 0.000001))

    def _on_save(self):
        if not self._ticker_input.text().strip():
            QMessageBox.warning(self, "Validation", "Ticker/Name is required.")
            return
        self.accept()

    def get_account_id(self) -> int:
        return self._account_combo.currentData()

    def get_ticker(self) -> str:
        return self._ticker_input.text().strip()

    def get_asset_type(self) -> str:
        return self._type_combo.currentData()

    def get_shares(self) -> float:
        return self._shares_input.value()

    def get_cost_basis(self) -> float:
        return self._cost_input.value()

    def get_current_price(self) -> float:
        return self._price_input.value()
