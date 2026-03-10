"""Transaction dialog."""

from typing import List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QDoubleSpinBox, QDialogButtonBox,
    QLabel, QTextEdit, QCheckBox, QDateEdit,
)
from PyQt6.QtCore import QDate

from ...models.transaction import Transaction
from ...models.account import Account


class TransactionDialog(QDialog):
    """Dialog for adding/editing transactions."""
    
    def __init__(self, parent=None, accounts: List[Account] = None, 
                 transaction: Transaction = None):
        super().__init__(parent)
        
        self._accounts = accounts or []
        self._transaction = transaction
        self._is_edit = transaction is not None
        
        self.setWindowTitle("Edit Transaction" if self._is_edit else "Add Transaction")
        self.setMinimumWidth(450)
        
        self._setup_ui()
        
        if self._transaction:
            self._load_transaction()
    
    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Account
        self._account_combo = QComboBox()
        for account in self._accounts:
            self._account_combo.addItem(account.name, account.id)
        form_layout.addRow("Account:", self._account_combo)
        
        # Date
        self._date_input = QDateEdit()
        self._date_input.setCalendarPopup(True)
        self._date_input.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self._date_input)
        
        # Description
        self._description_input = QLineEdit()
        self._description_input.setPlaceholderText("e.g., Grocery shopping at Walmart")
        form_layout.addRow("Description:", self._description_input)
        
        # Amount
        self._amount_input = QDoubleSpinBox()
        self._amount_input.setRange(-999999, 999999)
        self._amount_input.setDecimals(2)
        self._amount_input.setPrefix("$")
        form_layout.addRow("Amount:", self._amount_input)
        
        # Notes
        self._notes_input = QTextEdit()
        self._notes_input.setMaximumHeight(80)
        self._notes_input.setPlaceholderText("Optional notes...")
        form_layout.addRow("Notes:", self._notes_input)
        
        # Is transfer
        self._transfer_check = QCheckBox("This is a transfer")
        form_layout.addRow("", self._transfer_check)
        
        layout.addLayout(form_layout)

        # Inline error label
        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #d32f2f; font-size: 12px;")
        self._error_label.hide()
        layout.addWidget(self._error_label)
        self._description_input.textChanged.connect(lambda: self._error_label.hide())
        self._amount_input.valueChanged.connect(lambda _: self._error_label.hide())

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_save)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_transaction(self):
        """Load transaction data into form."""
        # Account
        index = self._account_combo.findData(self._transaction.account_id)
        if index >= 0:
            self._account_combo.setCurrentIndex(index)
        
        # Date
        self._date_input.setDate(QDate(self._transaction.date.year, 
                                       self._transaction.date.month, 
                                       self._transaction.date.day))
        
        # Description
        self._description_input.setText(self._transaction.description)
        
        # Amount
        self._amount_input.setValue(self._transaction.amount)
        
        # Notes
        if self._transaction.notes:
            self._notes_input.setText(self._transaction.notes)
        
        # Transfer
        self._transfer_check.setChecked(self._transaction.is_transfer)
        
        # Disable account editing for existing transactions
        self._account_combo.setEnabled(False)
    
    def _on_save(self):
        """Handle save button."""
        description = self._description_input.text().strip()
        if not description:
            self._error_label.setText("Description is required.")
            self._error_label.show()
            self._description_input.setFocus()
            return
        if self._amount_input.value() == 0:
            self._error_label.setText("Amount cannot be zero.")
            self._error_label.show()
            self._amount_input.setFocus()
            return
        self.accept()
    
    def get_transaction(self) -> Transaction:
        """Get transaction from form data."""
        return Transaction(
            account_id=self._account_combo.currentData(),
            date=self._date_input.date().toPyDate(),
            amount=self._amount_input.value(),
            description=self._description_input.text().strip(),
            notes=self._notes_input.toPlainText().strip() or None,
            is_transfer=self._transfer_check.isChecked()
        )
