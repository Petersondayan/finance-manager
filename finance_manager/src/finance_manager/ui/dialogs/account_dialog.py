"""Account dialog."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QDoubleSpinBox, QDialogButtonBox,
    QLabel,
)
from PyQt6.QtCore import Qt

from ...models.account import Account
from ...core.constants import AccountType, ACCOUNT_TYPE_NAMES


class AccountDialog(QDialog):
    """Dialog for adding/editing accounts."""
    
    def __init__(self, parent=None, account: Account = None):
        super().__init__(parent)
        
        self._account = account
        self._is_edit = account is not None
        
        self.setWindowTitle("Edit Account" if self._is_edit else "Add Account")
        self.setMinimumWidth(400)
        
        self._setup_ui()
        
        if self._account:
            self._load_account()
    
    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Name
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("e.g., Primary Checking")
        form_layout.addRow("Account Name:", self._name_input)
        
        # Type
        self._type_combo = QComboBox()
        for acc_type in AccountType:
            self._type_combo.addItem(ACCOUNT_TYPE_NAMES[acc_type], acc_type.value)
        form_layout.addRow("Account Type:", self._type_combo)
        
        # Institution
        self._institution_input = QLineEdit()
        self._institution_input.setPlaceholderText("e.g., Chase Bank (optional)")
        form_layout.addRow("Institution:", self._institution_input)
        
        # Balance
        self._balance_input = QDoubleSpinBox()
        self._balance_input.setRange(-999999999, 999999999)
        self._balance_input.setDecimals(2)
        self._balance_input.setPrefix("$")
        form_layout.addRow("Current Balance:", self._balance_input)
        
        layout.addLayout(form_layout)

        # Inline error label
        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #d32f2f; font-size: 12px;")
        self._error_label.hide()
        layout.addWidget(self._error_label)
        self._name_input.textChanged.connect(lambda: self._error_label.hide())

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_save)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_account(self):
        """Load account data into form."""
        self._name_input.setText(self._account.name)
        self._institution_input.setText(self._account.institution or "")
        self._balance_input.setValue(self._account.current_balance)
        
        # Set type
        index = self._type_combo.findData(self._account.account_type)
        if index >= 0:
            self._type_combo.setCurrentIndex(index)
        
        # Disable type editing for existing accounts
        self._type_combo.setEnabled(False)
    
    def _on_save(self):
        """Handle save button."""
        name = self._name_input.text().strip()
        if not name:
            self._error_label.setText("Account name is required.")
            self._error_label.show()
            self._name_input.setFocus()
            return
        self.accept()
    
    def get_account(self) -> Account:
        """Get account from form data."""
        return Account(
            name=self._name_input.text().strip(),
            account_type=self._type_combo.currentData(),
            institution=self._institution_input.text().strip() or None,
            current_balance=self._balance_input.value()
        )
