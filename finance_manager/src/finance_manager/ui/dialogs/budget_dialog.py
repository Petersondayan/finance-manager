"""Dialog for adding/editing budgets."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QDoubleSpinBox, QDialogButtonBox, QMessageBox,
)
from ...models.budget import Budget


class BudgetDialog(QDialog):
    """Add or edit a budget."""

    def __init__(self, categories: list, parent=None, budget: Budget = None, category_name: str = ""):
        super().__init__(parent)
        self._budget = budget
        self._categories = categories  # list of (id, name)
        self.setWindowTitle("Edit Budget" if budget else "Add Budget")
        self.setMinimumWidth(360)
        self._setup_ui(category_name)
        if budget:
            self._load_budget()

    def _setup_ui(self, preselected_name: str):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(12)

        self._category_combo = QComboBox()
        for cat_id, cat_name in self._categories:
            self._category_combo.addItem(cat_name, cat_id)
        if preselected_name:
            idx = self._category_combo.findText(preselected_name)
            if idx >= 0:
                self._category_combo.setCurrentIndex(idx)
        form.addRow("Category:", self._category_combo)

        self._limit_input = QDoubleSpinBox()
        self._limit_input.setRange(0.01, 999999.99)
        self._limit_input.setDecimals(2)
        self._limit_input.setPrefix("$")
        self._limit_input.setValue(500.0)
        form.addRow("Monthly Limit:", self._limit_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_budget(self):
        idx = self._category_combo.findData(self._budget.category_id)
        if idx >= 0:
            self._category_combo.setCurrentIndex(idx)
        self._category_combo.setEnabled(False)
        self._limit_input.setValue(self._budget.monthly_limit)

    def _on_save(self):
        if self._limit_input.value() <= 0:
            QMessageBox.warning(self, "Validation", "Monthly limit must be greater than zero.")
            return
        self.accept()

    def get_category_id(self) -> int:
        return self._category_combo.currentData()

    def get_limit(self) -> float:
        return self._limit_input.value()
