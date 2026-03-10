"""Dialog for creating a goal."""

from datetime import date

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QDoubleSpinBox, QDateEdit, QDialogButtonBox,
    QLabel,
)
from PyQt6.QtCore import QDate


class GoalDialog(QDialog):
    """Create a new financial goal."""

    GOAL_TYPES = [
        ("Savings", "savings"),
        ("Debt Payoff", "debt_payoff"),
        ("Retirement", "retirement"),
    ]
    STRATEGIES = [("Avalanche (highest balance first)", "avalanche"),
                  ("Snowball (smallest balance first)", "snowball")]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Goal")
        self.setMinimumWidth(420)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(12)

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("e.g., Emergency Fund")
        form.addRow("Goal Name:", self._name_input)

        self._type_combo = QComboBox()
        for label, value in self.GOAL_TYPES:
            self._type_combo.addItem(label, value)
        self._type_combo.currentIndexChanged.connect(self._on_type_changed)
        form.addRow("Goal Type:", self._type_combo)

        self._target_input = QDoubleSpinBox()
        self._target_input.setRange(0.01, 9999999.99)
        self._target_input.setDecimals(2)
        self._target_input.setPrefix("$")
        self._target_input.setValue(1000.0)
        form.addRow("Target Amount:", self._target_input)

        self._deadline_edit = QDateEdit()
        self._deadline_edit.setCalendarPopup(True)
        self._deadline_edit.setDate(QDate.currentDate().addYears(1))
        self._deadline_edit.setDisplayFormat("yyyy-MM-dd")
        form.addRow("Deadline (optional):", self._deadline_edit)

        self._strategy_label = QLabel("Strategy:")
        self._strategy_combo = QComboBox()
        for label, value in self.STRATEGIES:
            self._strategy_combo.addItem(label, value)
        form.addRow(self._strategy_label, self._strategy_combo)

        layout.addLayout(form)
        self._on_type_changed()

        # Inline error label
        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #d32f2f; font-size: 12px;")
        self._error_label.hide()
        layout.addWidget(self._error_label)
        self._name_input.textChanged.connect(lambda: self._error_label.hide())

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_type_changed(self):
        is_debt = self._type_combo.currentData() == "debt_payoff"
        self._strategy_label.setVisible(is_debt)
        self._strategy_combo.setVisible(is_debt)

    def _on_save(self):
        if not self._name_input.text().strip():
            self._error_label.setText("Goal name is required.")
            self._error_label.show()
            self._name_input.setFocus()
            return
        self.accept()

    def get_name(self) -> str:
        return self._name_input.text().strip()

    def get_goal_type(self) -> str:
        return self._type_combo.currentData()

    def get_target_amount(self) -> float:
        return self._target_input.value()

    def get_strategy(self) -> str:
        return self._strategy_combo.currentData()

    def get_deadline(self) -> date:
        qd = self._deadline_edit.date()
        return date(qd.year(), qd.month(), qd.day())
